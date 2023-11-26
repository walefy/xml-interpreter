from os import mkdir, path
from shutil import rmtree

import xmltodict
from fastapi import FastAPI, Header, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from crud import insert_nfe
from db.database import init_db
from models.company import Company, CompanyRegistration
from utils import read_all_xml_files, unzip_file
from validations import (
    check_duplicates,
    company_exists,
    compare_cnpj_in_all_files,
    verify_sequence_with_gap
)

app = FastAPI(title='XML Validator', version='1.0.0')


@app.on_event('startup')
async def startup():
    await init_db()


@app.middleware('http')
async def clean_folder(request: Request, call_next):
    dir_name = request.headers.get("cnpj")
    response = await call_next(request)

    if dir_name and path.exists(dir_name):
        rmtree(dir_name)

    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    if exc.status_code == 500:
        if not path.exists('./logs'):
            mkdir('./logs')

        with open('./logs/error_log.txt', 'a') as f:
            f.write(exc.detail + '\n')

        return JSONResponse(
            status_code=exc.status_code,
            content={"message": "Internal server error"},
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.post('/company', status_code=status.HTTP_201_CREATED)
async def register_company(company_registration: CompanyRegistration):
    try:
        if await company_exists(company_registration.cnpj):
            raise HTTPException(status_code=400, detail={
                'message': 'This CNPJ already registered!'
            })

        company = Company(
            fantasy_name=company_registration.fantasy_name,
            name=company_registration.name,
            cnpj=company_registration.cnpj,
            ie=company_registration.ie,
            crt=company_registration.crt,
        )

        await company.insert()

        return {'message': f'Company registered with name: {company.name}!'}

    except HTTPException as http_error:
        raise http_error

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.post('/xml', status_code=status.HTTP_201_CREATED)
async def xml_test(upload_file: UploadFile = None, cnpj: str = Header(...)):
    try:
        if upload_file is None:
            raise HTTPException(status_code=400, detail='xml file not found!')

        if upload_file.filename.endswith('.xml'):
            doc = xmltodict.parse(upload_file.file.read())
            return doc

        if upload_file.filename.endswith('.zip'):
            response_dict = {
                'warnings': [],
            }

            unzip_file(upload_file.file, cnpj)
            xml_file_list = read_all_xml_files(cnpj)

            compare_cnpj_in_all_files(xml_list=xml_file_list, cnpj=cnpj)
            verify_sequence_with_gap(
                xml_list=xml_file_list,
                response_dict=response_dict
            )

            company_exists_result = await company_exists(cnpj)

            if not company_exists_result:
                raise HTTPException(status_code=400, detail={
                    'message': 'Company not registered!'
                })

            await check_duplicates(cnpj, xml_file_list)

            await insert_nfe(cnpj, list_nfe_json=xml_file_list)

            return response_dict

        else:
            raise HTTPException(status_code=400, detail='xml file not found!')

    except HTTPException as http_error:
        raise http_error

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

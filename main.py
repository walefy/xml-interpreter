from fastapi import FastAPI, Header, UploadFile, HTTPException, Request, status
from shutil import rmtree
from os import path
import xmltodict

from utils import unzip_file, read_all_xml_files
from validations import compare_cnpj_in_all_files, check_duplicates
from validations import verify_sequence_with_gap
from validations import company_exists
from db.database import init_db
from crud import insert_nfe
from models.company import CompanyRegistration, Company

app = FastAPI(title='XML Validator', version='1.0.0')


@app.on_event("startup")
async def startup():
    await init_db()


@app.middleware('http')
async def clean_folder(request: Request, call_next):
    dir_name = request.headers.get("cnpj")
    response = await call_next(request)

    if dir_name and path.exists(dir_name):
        rmtree(dir_name)

    return response


@app.post('/company', status_code=status.HTTP_201_CREATED)
async def register_company(company_registration: CompanyRegistration):
    company = Company(
        fantasy_name=company_registration.fantasy_name,
        name=company_registration.name,
        cnpj=company_registration.cnpj,
        ie=company_registration.ie,
        crt=company_registration.crt,
    )

    await company.insert()

    return {'detail': f'Company registered with id: {company.name}!'}


@app.post('/xmltest', status_code=status.HTTP_201_CREATED)
async def xml_test(upload_file: UploadFile = None, cnpj: str = Header(...)):
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

        await company_exists(cnpj)
        await check_duplicates(cnpj, xml_file_list)

        await insert_nfe(cnpj, list_nfe_json=xml_file_list)

        return response_dict

    else:
        raise HTTPException(status_code=400, detail='xml file not found!')

from fastapi import FastAPI, Header, UploadFile, HTTPException, Request
from shutil import rmtree
from os import path
import xmltodict

from utils import unzip_file, read_all_xml_files
from validations import compare_cnpj_in_all_files, verify_sequence
from db import database, test_json


app = FastAPI(title='XML Validator', version='1.0.0')


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.middleware('http')
async def clean_folder(request: Request, call_next):
    dir_name = request.headers.get("cnpj")
    response = await call_next(request)

    if dir_name and path.exists(dir_name):
        rmtree(dir_name)

    return response


@app.get('/test/{json_id}')
async def test(json_id: int):
    query = test_json.select(whereclause=test_json.c.id == json_id)
    result = await database.fetch_one(query)

    if result is None:
        raise HTTPException(status_code=404, detail='not found!')

    return result['my_json']


@app.get('/owner')
async def get_owners():
    query = test_json.select()
    return await database.fetch_all(query)


@app.post('/xmltest')
async def xml_test(upload_file: UploadFile = None, cnpj: str = Header(...)):
    if upload_file is None:
        raise HTTPException(status_code=400, detail='xml file not found!')

    if upload_file.filename.endswith('.xml'):
        doc = xmltodict.parse(upload_file.file.read())
        await database.execute(test_json.insert().values(my_json=doc))
        return doc

    if upload_file.filename.endswith('.zip'):
        unzip_file(upload_file.file, cnpj)
        xml_file_list = read_all_xml_files(cnpj)

        compare_cnpj_in_all_files(xml_list=xml_file_list, cnpj=cnpj)
        verify_sequence(xml_list=xml_file_list)
        return {'detail': 'All CNPJ match!'}

    else:
        raise HTTPException(status_code=400, detail='xml file not found!')

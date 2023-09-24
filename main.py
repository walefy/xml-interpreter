from fastapi import FastAPI, Header, UploadFile, HTTPException
from shutil import rmtree
from os import mkdir, path
import xmltodict
from uuid import uuid4

from utils import unzip_file, read_all_xml_files
from validations import compare_cnpj_in_all_files, verify_sequence
from db import database, owner


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.middleware('http')
async def clean_folder(request, call_next):
    dir_name = request.headers.get("cnpj")
    response = await call_next(request)

    if dir_name and path.exists(dir_name):
        rmtree(dir_name)

    return response


@app.get('/')
async def root():
    query = owner.select()
    return await database.fetch_all(query)


@app.post('/owner')
async def create_owner(name: str = Header(...)):
    query = owner.insert(values={'name': name})
    return await database.execute(query)


@app.post('/xmltest')
async def xml_test(upload_file: UploadFile = None, cnpj: str = Header(...)):
    if upload_file is None:
        raise HTTPException(status_code=400, detail='xml file not found!')

    if upload_file.filename.endswith('.xml'):
        doc = xmltodict.parse(upload_file.file.read())
        return doc

    if upload_file.filename.endswith('.zip'):
        mkdir(cnpj)
        unzip_file(upload_file.file, cnpj)
        xml_file_list = read_all_xml_files(cnpj)

        compare_cnpj_in_all_files(xml_list=xml_file_list, cnpj=cnpj)
        verify_sequence(xml_list=xml_file_list)
        return {'detail': 'All CNPJ match!'}

    else:
        raise HTTPException(status_code=400, detail='xml file not found!')

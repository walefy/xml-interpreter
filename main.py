from fastapi import FastAPI, Header, UploadFile, HTTPException
from shutil import rmtree
from os import mkdir, path
import xmltodict

from utils import unzip_file
from validations import compare_cnpj_in_all_files, verify_sequence

app = FastAPI()


@app.middleware('http')
async def clean_folder(request, call_next):
    dir_name = request.headers.get("cnpj")
    response = await call_next(request)

    if dir_name and path.exists(dir_name):
        rmtree(dir_name)

    return response


@app.get('/')
async def root():
    return {'message': 'Hello World'}


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
        compare_cnpj_in_all_files(folder_name=cnpj, cnpj=cnpj)
        verify_sequence(cnpj)
        return {'detail': 'All CNPJ match!'}

    else:
        raise HTTPException(status_code=400, detail='xml file not found!')

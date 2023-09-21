from fastapi import FastAPI, Header, UploadFile, HTTPException
from os import mkdir, listdir
from shutil import rmtree
import zipfile
import xmltodict

app = FastAPI()


def compare_cnpj(cnpj: str, entry_file_name: str):
    with open(f'{cnpj}/{entry_file_name}', 'r') as file:
        response = xmltodict.parse(file.read())
        list_key = ('nfeProc', 'NFe', 'infNFe', 'emit', 'CNPJ')
        for key in list_key:
            if isinstance(response, dict):
                response = response.get(key, {})
            else:
                rmtree(cnpj)
                raise HTTPException(
                    status_code=400, detail="The xml file is not valid")

        return response == cnpj


def compare_cnpj_in_all_files(folder_name: str, cnpj: str):
    for file_name in listdir(folder_name):
        if file_name.endswith('.xml') and not compare_cnpj(cnpj, file_name):
            rmtree(cnpj)
            raise HTTPException(status_code=400, detail="cnpj dont's match!")
        else:
            rmtree(cnpj)
            raise HTTPException(
                status_code=400, detail="all files must be xml!")


def unzip_file(file, cnpj: str):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(cnpj)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post('/xmltest')
async def xml_test(upload_file: UploadFile = None, cnpj: str = Header(...)):
    if upload_file is None:
        raise HTTPException(status_code=400, detail="xml file not found!")
    if upload_file.filename.endswith('.xml'):
        doc = xmltodict.parse(upload_file.file.read())
        return doc
    if upload_file.filename.endswith('.zip'):
        mkdir(cnpj)
        unzip_file(upload_file.file, cnpj)
        compare_cnpj_in_all_files(folder_name=cnpj, cnpj=cnpj)
        rmtree(cnpj)
        return {"detail": "All cnpj matchs!"}
    else:
        raise HTTPException(status_code=400, detail="xml file not found!")

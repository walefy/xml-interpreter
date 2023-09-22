from fastapi import FastAPI, Header, UploadFile, HTTPException
from os import mkdir, listdir
from shutil import rmtree
import zipfile
import xmltodict

app = FastAPI()


def get_nested_value(list_key: tuple[str, ...], entry_dict: dict):
    response = entry_dict.copy()

    for key in list_key:
        if isinstance(response, dict):
            response = response.get(key, {})
        else:
            raise ValueError(f'Key {key} not found')

    return response

def verify_sequence(folder_name: str):
    sequence_dict = {}
    serie_keys = ('nfeProc', 'NFe', 'infNFe', 'ide')
    missing_invoices = []
    for file_name in listdir(folder_name):
        with open(f'{folder_name}/{file_name}', 'r') as file:
            xml_in_dict = xmltodict.parse(file.read())
            ide = get_nested_value(serie_keys, xml_in_dict)
            serie = ide.get('serie')
            invoice_number = ide.get('nNF')
            if serie not in sequence_dict:
                sequence_dict[serie] = [int(invoice_number)]
            else:
                sequence_dict[serie].append(int(invoice_number))
    for serie in sequence_dict:
        sequence_dict[serie].sort()
        for index in range(len(sequence_dict[serie]) - 1):
            if sequence_dict[serie][index] + 1 != sequence_dict[serie][index + 1]:
                for gap_index in range(sequence_dict[serie][index] + 1, sequence_dict[serie][index + 1]):
                    missing_invoices.append({ 'serie': serie, 'invoice_number': gap_index })
    if len(missing_invoices) > 0:
        rmtree(folder_name)
        raise HTTPException(
            status_code=400, detail={ 'message': 'There are missing invoices!', 'missing_invoices': missing_invoices })

        


def compare_cnpj(cnpj: str, entry_file_name: str):
    with open(f'{cnpj}/{entry_file_name}', 'r') as file:
        list_key = ('nfeProc', 'NFe', 'infNFe', 'emit', 'CNPJ')
        xml_in_dict = xmltodict.parse(file.read())

        try:
            response_cnpj = get_nested_value(list_key, xml_in_dict)
            return response_cnpj == cnpj
        except ValueError:
            rmtree(cnpj)
            raise HTTPException(
                status_code=400, detail=f'The xml file {file} is not valid!')


def compare_cnpj_in_all_files(folder_name: str, cnpj: str):
    errors_file_list = []

    for file_name in listdir(folder_name):
        if not file_name.endswith('.xml'):
            rmtree(cnpj)
            raise HTTPException(
                status_code=400, detail='all files must be xml!')

        if not compare_cnpj(cnpj, file_name):
            errors_file_list.append(file_name)
    if len(errors_file_list) > 0:
        rmtree(cnpj)
        raise HTTPException(
            status_code=400, detail={ 'message': 'The CNPJ is not match!', 'files': errors_file_list })


def unzip_file(file, cnpj: str):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(cnpj)


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
        rmtree(cnpj)
        return {'detail': 'All CNPJ match!'}

    else:
        raise HTTPException(status_code=400, detail='xml file not found!')

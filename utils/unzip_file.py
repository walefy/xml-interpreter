from zipfile import ZipFile


def unzip_file(file, cnpj: str):
    with ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(cnpj)

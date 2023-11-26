from os import mkdir
from zipfile import ZipFile


def unzip_file(file, folder_name: str):
    with ZipFile(file, 'r') as zip_ref:
        mkdir(folder_name)
        zip_ref.extractall(folder_name)

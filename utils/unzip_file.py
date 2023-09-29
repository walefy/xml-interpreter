from zipfile import ZipFile
from os import mkdir


def unzip_file(file, folder_name: str):
    with ZipFile(file, 'r') as zip_ref:
        mkdir(folder_name)
        zip_ref.extractall(folder_name)

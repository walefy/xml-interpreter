from zipfile import ZipFile


def unzip_file(file, folder_name: str):
    with ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(folder_name)

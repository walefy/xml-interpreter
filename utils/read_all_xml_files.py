from os import listdir
from models import Xml
from fastapi import HTTPException
import xmltodict


def read_all_xml_files(folder_name: str) -> list[Xml]:
    xml_file_list = []

    for file_name in listdir(folder_name):
        if not file_name.endswith('.xml'):
            raise HTTPException(
                status_code=400,
                detail='all files must be xml!'
            )

        with open(f'{folder_name}/{file_name}', 'r') as file:
            xml_file_in_dict = xmltodict.parse(file.read())
            xml_file_list.append(Xml(
                source=xml_file_in_dict,
                file_name=file_name
            ))

    return xml_file_list

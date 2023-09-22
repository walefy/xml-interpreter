from fastapi import HTTPException
from os import listdir
import xmltodict

from utils import get_nested_value


def compare_cnpj(cnpj: str, entry_file_name: str):
    with open(f'{cnpj}/{entry_file_name}', 'r') as file:
        list_key = ('nfeProc', 'NFe', 'infNFe', 'emit', 'CNPJ')
        xml_in_dict = xmltodict.parse(file.read())

        try:
            response_cnpj = get_nested_value(list_key, xml_in_dict)
            return response_cnpj == cnpj
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f'The xml file {file} is not valid!'
            )


def compare_cnpj_in_all_files(folder_name: str, cnpj: str):
    errors_file_list = []

    for file_name in listdir(folder_name):
        if not file_name.endswith('.xml'):
            raise HTTPException(
                status_code=400,
                detail='all files must be xml!'
            )

        if not compare_cnpj(cnpj, file_name):
            errors_file_list.append(file_name)

    if len(errors_file_list) > 0:
        detail_cnpj_not_match = {
            'message': 'The CNPJ is not match!',
            'files': errors_file_list
        }

        raise HTTPException(
            status_code=400,
            detail=detail_cnpj_not_match
        )


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
        serie_length = len(sequence_dict[serie])

        for index in range(serie_length - 1):
            correct_next_number = sequence_dict[serie][index] + 1
            real_next_number = sequence_dict[serie][index + 1]

            if correct_next_number != real_next_number:
                for gap_index in range(correct_next_number, real_next_number):
                    missing_invoices.append({
                        'serie': serie,
                        'invoice_number': gap_index
                    })

    if len(missing_invoices) > 0:
        raise HTTPException(
            status_code=400,
            detail={
                'message': 'There are missing invoices!',
                'missing_invoices': missing_invoices
            }
        )


def format_date(date: str):
    date = date.split('T')
    date = date[0].split('-')
    return f'{date[2]}/{date[1]}/{date[0]}'


def format_hour(hour: str):
    hour = hour.split('T')
    hour = hour[1].split('-')
    return f'{hour[0]}'

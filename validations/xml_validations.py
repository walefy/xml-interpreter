from fastapi import HTTPException

from utils import get_nested_value
from models.xml_models import XmlModel
from models.company import Company


def compare_cnpj(cnpj: str, xml_dict: dict, xml_file_name: str):
    list_key = ('nfeProc', 'NFe', 'infNFe', 'emit', 'CNPJ')

    try:
        response_cnpj = get_nested_value(list_key, xml_dict)
        return response_cnpj == cnpj
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f'The xml file {xml_file_name} is not valid!'
        )


def compare_cnpj_in_all_files(xml_list: list[XmlModel], cnpj: str):
    errors_file_list = []

    for xml in xml_list:
        if not compare_cnpj(cnpj, xml.source, xml.file_name):
            errors_file_list.append(xml.file_name)

    if len(errors_file_list) > 0:
        detail_cnpj_not_match = {
            'message': 'The CNPJ is not match!',
            'files': errors_file_list
        }

        raise HTTPException(
            status_code=400,
            detail=detail_cnpj_not_match
        )


def verify_sequence(xml_list: list[XmlModel]):
    sequence_dict = {}
    serie_keys = ('nfeProc', 'NFe', 'infNFe', 'ide')
    missing_invoices = []

    for xml in xml_list:
        ide = get_nested_value(serie_keys, xml.source)
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


async def check_duplicates(cnpj: str, xml_list: list[XmlModel]):
    companies = Company.find({'cnpj': cnpj})

    companies_list = await companies.to_list()

    company = companies_list[0]

    for xml in xml_list:
        for nfe in company.nfes:
            xml_number = int(xml.source['nfeProc']['NFe']['infNFe']['ide']['nNF'])
            xml_serie = int(xml.source['nfeProc']['NFe']['infNFe']['ide']['serie'])
            nfe_number = nfe.number
            nfe_serie = nfe.serie

            if xml_number == nfe_number and xml_serie == nfe_serie:
                raise HTTPException(
                    status_code=400,
                    detail={
                        'message': 'There are duplicated invoices!',
                        'duplicated_invoices': {
                            'number': xml_number,
                            'serie': xml_serie
                        }
                    }
                )

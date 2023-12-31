import unittest
from os import path
from unittest.mock import Mock, patch

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient

from main import app
from models.company import Company
from tests.helpers import init_mock_mongodb_beanie


@pytest_asyncio.fixture(autouse=True)
async def mock_mongodb():
    document_models = [Company]
    await init_mock_mongodb_beanie(document_models)


@pytest_asyncio.fixture(autouse=True)
async def register_company():
    default_company = {
        'name': 'Test Company Inc.',
        'fantasy_name': 'Test Company',
        'cnpj': '40028176000176',
        'ie': '123456789012',
        'crt': 'Simples Nacional'
    }

    async with AsyncClient(app=app, base_url='http://test') as async_client:
        await async_client.post('/company', json=default_company)


@pytest.mark.asyncio
async def test_send_zip_with_invoices():
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        path_to_zip_file = path.join(
            path.dirname(__file__),
            '..',
            'data',
            'minimal_no_gap.zip'
        )

        zip_file = open(path_to_zip_file, 'rb')

        files = {
            'upload_file': zip_file
        }

        headers = {
            'Content-Type': 'multipart/form-data;boundary=boundary',
            'cnpj': '40028176000176'
        }

        response = await async_client.post('/xml', files=files, headers=headers)
        zip_file.close()

    assert response.json() == {'warnings': []}
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_send_zip_file_with_gap():
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        path_to_zip_file = path.join(
            path.dirname(__file__),
            '..',
            'data',
            'minimal_with_gap.zip'
        )

        zip_file = open(path_to_zip_file, 'rb')

        files = {
            'upload_file': zip_file
        }

        headers = {
            'Content-Type': 'multipart/form-data;boundary=boundary',
            'cnpj': '40028176000176'
        }

        response = await async_client.post('/xml', files=files, headers=headers)
        zip_file.close()

    expected_warnings = {
        'warnings': [
            {
                'message': 'There are missing invoices!',
                'missing_invoices': [
                    {'invoice_number': 3, 'serie': 3},
                    {'invoice_number': 4, 'serie': 3},
                    {'invoice_number': 66, 'serie': 2},
                    {'invoice_number': 67, 'serie': 2},
                ]
            },
        ],
    }

    actual_warnings = response.json()
    case = unittest.TestCase()

    case.assertCountEqual(actual_warnings, expected_warnings)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_make_request_without_upload_file():
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        headers = {
            'Content-Type': 'multipart/form-data;boundary=boundary',
            'cnpj': '40028176000176'
        }

        response = await async_client.post('/xml', headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'xml file not found!'}


@pytest.mark.asyncio
async def test_make_request_without_company_registered():
    compare_cnpj_in_all_files = Mock(return_value=None)
    verify_sequence_with_gap = Mock(return_value=None)

    patcher_compare_cnpj = patch(
        'main.compare_cnpj_in_all_files', compare_cnpj_in_all_files)
    patcher_verify_sequence = patch(
        'main.verify_sequence_with_gap', verify_sequence_with_gap)

    patcher_compare_cnpj.start()
    patcher_verify_sequence.start()

    async with AsyncClient(app=app, base_url='http://test') as async_client:
        path_to_zip_file = path.join(
            path.dirname(__file__),
            '..',
            'data',
            'minimal_no_gap.zip'
        )

        zip_file = open(path_to_zip_file, 'rb')

        files = {
            'upload_file': zip_file
        }

        headers = {
            'Content-Type': 'multipart/form-data;boundary=boundary',
            'cnpj': '40028176000177'
        }

        response = await async_client.post('/xml', files=files, headers=headers)
        zip_file.close()

    patcher_compare_cnpj.stop()
    patcher_verify_sequence.stop()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'message': 'Company not registered!'}


@pytest.mark.asyncio
async def test_make_request_with_invalid_file_extension():
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        path_to_zip_file = path.join(
            path.dirname(__file__),
            '..',
            'data',
            'full_no_gap',
            '63.xml'
        )

        zip_file = open(path_to_zip_file, 'rb')

        files = {
            'upload_file': zip_file
        }

        headers = {
            'Content-Type': 'multipart/form-data;boundary=boundary',
            'cnpj': '40028176000176'
        }

        response = await async_client.post('/xml', files=files, headers=headers)
        zip_file.close()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'file must be a zip!'}


@pytest.mark.asyncio
async def test_make_request_with_different_cnpj():
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        path_to_zip_file = path.join(
            path.dirname(__file__),
            '..',
            'data',
            'minimal_no_gap.zip'
        )

        zip_file = open(path_to_zip_file, 'rb')

        files = {
            'upload_file': zip_file
        }

        headers = {
            'Content-Type': 'multipart/form-data;boundary=boundary',
            'cnpj': '40028176000177'
        }

        response = await async_client.post('/xml', files=files, headers=headers)
        zip_file.close()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['message'] == 'The CNPJ is not match!'

    not_match_files_expect = [
        '63.xml',
        '64.xml',
        '65.xml',
        '66.xml'
    ]
    not_match_files_actual = response.json()['files']

    case = unittest.TestCase()
    case.assertCountEqual(not_match_files_actual, not_match_files_expect)

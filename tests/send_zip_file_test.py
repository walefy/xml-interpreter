from httpx import AsyncClient
from fastapi import status
from os import path

import pytest
import pytest_asyncio

from main import app
from tests.helpers import init_mock_mongodb_beanie
from models.company import Company


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

        response = await async_client.post('/xmltest', files=files, headers=headers)
        zip_file.close()

    assert response.json() == {'warnings': []}
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_send_zip_file_with_gap():
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        path_to_zip_file = path.join(
            path.dirname(__file__),
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

        response = await async_client.post('/xmltest', files=files, headers=headers)
        zip_file.close()

    assert response.json() == {
        'warnings': [
            {
                'message': 'There are missing invoices!',
                'missing_invoices': [
                    {'invoice_number': 3, 'serie': '3'},
                    {'invoice_number': 4, 'serie': '3'},
                    {'invoice_number': 66, 'serie': '2'},
                    {'invoice_number': 67, 'serie': '2'},
                ]
            },
        ],
    }
    assert response.status_code == status.HTTP_201_CREATED

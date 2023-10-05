from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from fastapi import status

import pytest
import pytest_asyncio

from main import app
from models.company import Company


@pytest_asyncio.fixture(autouse=True)
async def mock_mongodb():
    client = AsyncMongoMockClient()
    await init_beanie(
        document_models=[Company],
        database=client.get_database(name='test_db')
    )


@pytest.mark.asyncio
async def test_register_company():
    default_company = {
        'name': 'Test Company Inc.',
        'fantasy_name': 'Test Company',
        'cnpj': '12345678901234',
        'ie': '123456789012',
        'crt': 'Simples Nacional'
    }

    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post('/company', json=default_company)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'message': f'Company registered with name: {default_company["name"]}!'
    }


@pytest.mark.asyncio
async def test_register_two_companies_with_same_cnpj():
    default_company = {
        'name': 'Test Company Inc.',
        'fantasy_name': 'Test Company',
        'cnpj': '12345678901234',
        'ie': '123456789012',
        'crt': 'Simples Nacional'
    }

    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post('/company', json=default_company)
        response = await async_client.post('/company', json=default_company)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'message': 'This CNPJ already registered!'
    }


@pytest.mark.asyncio
async def test_register_company_with_invalid_crt():
    default_company = {
        'name': 'Test Company Inc.',
        'fantasy_name': 'Test Company',
        'cnpj': '1234567890123',
        'ie': '123456789012',
        'crt': 'Invalid CRT'
    }

    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post('/company', json=default_company)

    response_status_code = response.status_code
    assert response_status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response_loc = response.json()['detail'][0]['loc']
    expected_loc = ['body', 'crt']
    assert response_loc == expected_loc

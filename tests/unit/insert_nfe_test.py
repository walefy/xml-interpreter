from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from crud import insert_nfe
from models.company import Company
from models.xml_models import XmlModel
from tests.helpers.mock_mongodb_beanie import init_mock_mongodb_beanie


@pytest_asyncio.fixture(autouse=True)
async def mock_mongodb():
    document_models = [Company]
    await init_mock_mongodb_beanie(document_models)


@pytest.mark.asyncio
async def test_insert_nfe_with_multiple_products():
    list_nfe_json = [
        XmlModel(
            source={
                'nfeProc': {
                    'NFe': {
                        'infNFe': {
                            'det': [
                                {'prod': {'xProd': 'Product 1', 'vProd': '10.00'},
                                 'imposto': {}
                                 },
                                {'prod': {'xProd': 'Product 2', 'vProd': '20.00'},
                                 'imposto': {}
                                 },
                            ],
                            'ide': {'nNF': '123', 'serie': '1'},
                        }
                    }
                }
            },
            file_name='file_name'
        )
    ]

    company = Mock()
    company.update = AsyncMock()

    Company.find_one = Mock(return_value=company)

    await insert_nfe('40028176000176', list_nfe_json)

    company.update.assert_called_once()

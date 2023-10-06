from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


async def init_mock_mongodb_beanie(document_models: list = []):
    """
    This function is used to mock MongoDB in tests.

    use it like this:

    ```python
    @pytest_asyncio.fixture(autouse=True)
    def mock_mongodb():
        document_models = [Company]
        await init_mock_mongodb_beanie(document_models)
    ```
    """

    client = AsyncMongoMockClient()
    await init_beanie(
        document_models=document_models,
        database=client.get_database(name='test_db')
    )

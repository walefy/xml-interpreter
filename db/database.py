import os

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from models.company import Company


async def init_db():
    MONGO_USER = os.getenv('MONGO_USER')
    MONGO_PASS = os.getenv('MONGO_PASSWORD')
    MONGO_HOST = os.getenv('MONGO_HOST')
    MONGO_PORT = os.getenv('MONGO_PORT')

    client = AsyncIOMotorClient(
        f'mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}'
    )
    db = client['x_app']

    await init_beanie(database=db, document_models=[Company])
    await Company.get_motor_collection().create_index('cnpj', unique=True)

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models.company import Company


async def init_db():
    client = AsyncIOMotorClient('mongodb://user:pass@localhost:27017')
    db = client['x_app']

    await init_beanie(database=db, document_models=[Company])

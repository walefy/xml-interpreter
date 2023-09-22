import databases
import sqlalchemy
from os import environ
from pydantic import BaseModel

from settings import load_env

load_env()

POSTGRES_USER = environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = environ.get('POSTGRES_PASSWORD')
POSTGRES_SERVER = environ.get('POSTGRES_SERVER')
POSTGRES_DB = environ.get('POSTGRES_DB')

DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}'

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

pet = sqlalchemy.Table(
    "pet",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
)

owner = sqlalchemy.Table(
    "owner",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)


class Pet(BaseModel):
    id: int
    name: str
    description: str


class PetIn(BaseModel):
    name: str
    description: str

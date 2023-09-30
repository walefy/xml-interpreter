import databases
import sqlalchemy
from sqlalchemy.dialects import postgresql
import os

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_SERVER = os.getenv('POSTGRES_SERVER')
POSTGRES_DB = os.getenv('POSTGRES_DB')

DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}'

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

test_json = sqlalchemy.Table(
    'test_json',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('my_json', postgresql.JSONB)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)

metadata.create_all(engine)

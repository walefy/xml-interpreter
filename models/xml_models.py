from pydantic import BaseModel


class Xml(BaseModel):
    source: dict
    file_name: str

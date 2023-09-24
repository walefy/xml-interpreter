from pydantic import BaseModel


class XmlModel(BaseModel):
    source: dict
    file_name: str

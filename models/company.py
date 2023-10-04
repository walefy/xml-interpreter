from pydantic import BaseModel
from typing import Any, Optional
from beanie import Document
from typing import Literal


class Address(BaseModel):
    street: str
    number: str
    complement: Optional[str]
    city: str
    state: str
    country: str
    zip_code: str


class ServiceTax(BaseModel):
    cofins: dict[str, Any] = {}
    pis: dict[str, Any] = {}
    iss: dict[str, Any] = {}


class Tax(BaseModel):
    icms: dict[str, Any] = {}
    cofins: dict[str, Any] = {}
    pis: dict[str, Any] = {}
    ipi: dict[str, Any] = {}


class Product(BaseModel):
    description: str
    price: float
    # tax: Tax | ServiceTax
    tax: dict[str, Any] = {}


class NFE(BaseModel):
    number: int
    serie: int
    products: list[Product]


class Company(Document):
    fantasy_name: str
    name: str
    cnpj: str
    # address: Address
    ie: str
    crt: Literal['Simples Nacional', 'Lucro Presumido', 'Lucro Real']
    nfes: list[NFE] = []


class MissingInvoice(BaseModel):
    number: int
    serie: int


class CompanyRegistration(BaseModel):
    fantasy_name: str
    name: str
    cnpj: str
    ie: str
    crt: str
    with_gap: bool = False
    missing_invoices: list[MissingInvoice] = []
    # address: Address

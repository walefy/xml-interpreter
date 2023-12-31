from typing import Any, Literal, Optional

from beanie import Document
from pydantic import BaseModel


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


class MissingInvoice(BaseModel):
    number: int
    serie: int


class Company(Document):
    fantasy_name: str
    name: str
    cnpj: str
    # address: Address
    with_gap: bool = False
    missing_invoices: list[MissingInvoice] = []
    ie: str
    crt: Literal['Simples Nacional', 'Lucro Presumido', 'Lucro Real']
    nfes: list[NFE] = []


class CompanyRegistration(BaseModel):
    fantasy_name: str
    name: str
    cnpj: str
    ie: str
    crt: Literal['Simples Nacional', 'Lucro Presumido', 'Lucro Real']
    # address: Address

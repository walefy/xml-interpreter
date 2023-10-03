from fastapi import HTTPException
from models.company import Company


async def company_exists(cnpj: str):
    company = Company.find_one({'cnpj': cnpj})

    company_count = await company.count()

    if company_count == 0:
        raise HTTPException(
            status_code=404,
            detail={
                'message': 'Company not found!'
            }
        )

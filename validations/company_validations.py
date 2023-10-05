from models.company import Company


async def company_exists(cnpj: str):
    company = Company.find_one({'cnpj': cnpj})

    company_count = await company.count()

    if company_count == 0:
        return False

    if company_count == 1:
        return True

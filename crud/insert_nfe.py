from models.company import NFE, Company, Product
from models.xml_models import XmlModel


async def insert_nfe(cnpj: str, list_nfe_json: list[XmlModel]):
    company = Company.find_one({'cnpj': cnpj})

    for nfe_json in list_nfe_json:
        nfe_source = nfe_json.source['nfeProc']['NFe']
        products_json = nfe_source['infNFe']['det']
        products = []

        if isinstance(products_json, list):
            for product in products_json:
                product_with_class = Product(
                    description=product['prod']['xProd'],
                    price=product['prod']['vProd'],
                    tax=product['imposto']
                )

                products.append(product_with_class)
        else:
            product_with_class = Product(
                description=products_json['prod']['xProd'],
                price=products_json['prod']['vProd'],
                tax=products_json['imposto']
            )

            products.append(product_with_class)

        nfe = NFE(
            number=nfe_source['infNFe']['ide']['nNF'],
            serie=nfe_source['infNFe']['ide']['serie'],
            products=products
        )

        await company.update({
            '$push': {'nfes': nfe.model_dump()},
        })

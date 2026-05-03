import requests
def organize(datas):
    organized = []

    for item in datas:
        organized.append({
            "id" : str(item.get("cnpj")),
            "tittle": item.get("razaoSocial"),
            "description": str(item),
            "link": "https://pncp.gov.br",
        })

    return organized    
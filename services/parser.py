import requests
def organize(datas):
    organized = []

    for item in datas:
        organized.append({
            "id" : str(item.get("id")),
            "cnpj": item.get("cnpj"),
            "description": item.get("descricao"),
            "titulo": item.get("titulo"),
            "valorTotal": item.get("valor"),
            "orgao": item.get("municipio") + " - " + item.get("estado"),
            "link": item.get("link") or "https://pncp.gov.br",
        })

    return organized    
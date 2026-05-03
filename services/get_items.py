import requests

def buscar_itens(cnpj, ano, numero):
    url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{numero}/itens"

    params = {
        "pagina": 1,
        "tamanhoPagina": 5
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers, params=params, timeout=10)

    if r.status_code != 200:
        return []

    return r.json()
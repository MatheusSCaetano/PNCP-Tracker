import requests

def organize(datas):
    organized = []
    for item in datas:
        municipio = item.get("municipio") or ""
        estado = item.get("estado") or ""
        orgao = f"{municipio} - {estado}" if municipio or estado else "N/A"

        organized.append({
            "id": str(item.get("id")),
            "cnpj": item.get("cnpj"),
            "description": item.get("descricao"),
            "titulo": item.get("titulo"),
            "valorTotal": item.get("valor"),
            "orgao": orgao, 
            "link": item.get("link") or "https://pncp.gov.br",
        })
    return organized
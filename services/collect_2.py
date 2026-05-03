import requests

BASE_URL = "https://pncp.gov.br/api/search/"

def coletar_licitacoes_reais(pagina = 6, tamanho=10):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    params = {
        "tipos_documento": "edital",
        "ordenacao": "-data",
        "pagina": pagina,
        "tam_pagina": tamanho,
        "status": "recebendo_proposta"
    }

    response = requests.get(BASE_URL, headers=headers, params=params, timeout=15)

    print("Status:", response.status_code)
    print("URL:", response.url)

    if response.status_code != 200:
        print("Erro ao buscar dados")
        return []

    data = response.json()

    resultados = data.get("resultados") or data.get("items") or data

    licitacoes = []

    for item in resultados:
        try:
            desc = item.get("description") or "Sem descrição" #item.get("objeto") or 
            tittle = item.get("title") or "Sem Título"
            orgao = item.get("orgao_nome", {})#.get("razao_social", "N/A")
            cnpj_org = item.get("orgao_cnpj") or ""
            municipio = item.get("municipio_nome") or ""
            estado = item.get("uf") or ""
            sequencial_contrato = item.get("numero_sequencial") or ""
            ano_contrato = item.get("ano") or ""
            numero_controle_pncp = item.get("numero_controle_pncp") or ""
            valor = item.get("valor_global")
            link = "https://pncp.gov.br/app/editais/" + str(item.get("id", ""))

            licitacoes.append({
                "id": str(item.get("id")),
                "cnpj": cnpj_org,
                "ano": ano_contrato,
                "numero": sequencial_contrato,  # pode precisar ajustar depois
                "numero_controle": numero_controle_pncp,
                "tittle": tittle,
                "description": desc,
                "org": str(orgao) + str(cnpj_org),
                "municipio": municipio,
                "estado": estado,
                "contrato": f"{sequencial_contrato} - {ano_contrato}",
                "valor": valor,
                "link": link
            })

        except Exception as e:
            print("Erro ao parsear item:", e)

    return licitacoes

def buscar_itens(cnpj, ano, numero):
    url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{numero}/itens"
    print("url:",url)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        r = requests.get(url, headers=headers, timeout=15)

        if r.status_code == 200:
            return r.json()
        else:
            print("Erro itens:", r.status_code, url)
            return []

    except Exception as e:
        print("Erro requisição itens:", e)
        return []
    

def enriquecer_com_itens(lista_editais):
    for edital in lista_editais:

        cnpj = edital.get("cnpj")
        ano = edital.get("ano")
        numero = edital.get("numero")

        if not all([cnpj, ano, numero]):
            edital["itens"] = []
            continue

        itens = buscar_itens(cnpj, ano, numero)

        edital["itens"] = itens

    return lista_editais
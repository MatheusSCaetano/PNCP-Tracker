from flask import Flask,request, jsonify
from services.ai_classifier import classify_licitacao
import requests
from datetime import datetime, timedelta, timezone

BASE_URL = "https://pncp.gov.br/api/search/"

def is_current(data_str, dias=7): 
    if not data_str: 
        return False 

    try:
        dias = int(dias)

        data_str = data_str.replace("Z", "+00:00") 
        data = datetime.fromisoformat(data_str) 

        if data.tzinfo is None: 
            data = data.replace(tzinfo=timezone.utc)

        limite = datetime.now(timezone.utc) - timedelta(days=dias)

        return data >= limite 

    except Exception as e: 
        print("Erro ao converter data:", data_str, e) 
        return False

def coletar_licitacoes_reais(max_paginas=10, tamanho=10, palavras_chave=None, number_days=None):
    number_days = number_days or 7
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    licitacoes = []

    for page in range(1, max_paginas + 1):
        params = {
            "q":  palavras_chave or "software juridico",
            "tipos_documento": "edital",
            "ordenacao": "-data",
            "pagina": page,
            "tam_pagina": tamanho,
            "status": "recebendo_proposta"
        }

        response = requests.get(BASE_URL, headers=headers, params=params, timeout=15)    
        print(f"\n Página {page} - Status:", response.status_code)

        if response.status_code != 200:
            print("Erro ao buscar dados")
            continue

        data = response.json()
        results = data.get("resultados") or data.get("items") or data

        if not results:
            print("Sem mais resultados, parando...")
            break

        if isinstance(data, dict):
            results = data.get("resultados") or data.get("items") or []
        elif isinstance(data, list):
            results = data
        else:
            results = []
        for item in results:
            if not isinstance(item, dict):
                continue
            
            descricao = item.get("description") or "Sem descrição"
            titulo = item.get("title") or "Sem Título"
            print(f"\titulo: {titulo}")
            print(f"descricao: {descricao}")
            texto_analise = f"""
                Título:
                {titulo}

                Descrição:
                {descricao}
            """
            classificacao = classify_licitacao(texto_analise)
            print(classificacao)
            data_pub = item.get("data_publicacao_pncp") or item.get("dataPublicacao")

            if data_pub and not is_current(data_pub, number_days):
                continue 
            
            try:
                desc = item.get("description") or "Sem descrição"
                titulo = item.get("title") or "Sem Título"

                cnpj_org = item.get("orgao_cnpj") or ""
                ano = item.get("ano") or ""
                numero = item.get("numero_sequencial") or ""
                numero_controle = item.get("numero_controle_pncp") or ""

                link = f"https://pncp.gov.br/app/editais/{cnpj_org}/{ano}/{numero}"

                if int(classificacao["score"]) >= 7:
                    print("relevante")
                    licitacoes.append({
                        "id": str(item.get("id")),
                        "cnpj": cnpj_org,
                        "ano": ano,
                        "numero": numero,
                        "numero_controle": numero_controle,
                        "titulo": titulo,
                        "descricao": desc,
                        "municipio": item.get("municipio_nome"),
                        "estado": item.get("uf"),
                        "valor": item.get("valor_global"),
                        "link": link
                    })
                else:
                    print("não relevante")
            except Exception as e:
                print("Erro ao parsear item:", e)

    return licitacoes

def buscar_itens(cnpj, ano, numero):
    url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{numero}/itens"
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

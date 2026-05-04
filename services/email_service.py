import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def montar_link(item):
    cnpj = item.get("orgao_cnpj") or ""
    sequencial_contrato = item.get("numero_sequencial") or ""
    ano_contrato = item.get("ano") or ""
    numero = item.get("numero")  # ou sequencial

    if all([cnpj, ano_contrato, numero]):
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{numero}"
    
    return "Link indisponível"

def send_email(lista):
    print("Entrou no send_email")
    print("Quantidade de itens:", len(lista))
    if not lista:
        print("Lista vazia, não enviando email")
        return

    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    corpo = "\n\n".join([
        f"Título: {item.get('titulo')}\n"
        f"Descrição: {item.get('description')}\n"
        f"Órgão: {item.get("orgao")}\n"
        f"cnpj_org: {item.get("cnpj")}\n"
        f"valorTotal: {item.get("valorTotal")}\n"
        f"Link: {item.get("link")}\n"
        f"{'-'*40}"
        for item in lista
    ])

    #  "id" : str(item.get("id")),
    #         "cnpj": item.get("cnpj"),
    #         "description": item.get("descricao"),
    #         "titulo": item.get("titulo"),
    #         "valorTotal": item.get("valor"),
    #         "orgao": item.get("municipio") + " - " + item.get("estado"),
    #         "link": item.get("link") or "https://pncp.gov.br",
    #     })

    msg = MIMEText(corpo)
    msg["Subject"] = "Novas Licitações Encontradas"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_USER

    try:
        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
        smtp.quit()

        print("Email enviado com sucesso!")

    except Exception as e:
        print("Erro ao enviar email:", e)
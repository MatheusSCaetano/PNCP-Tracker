import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


def send_email(list):
    if not list:
        print("Lista vazia, não enviando email")
        return

    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    corpo = "\n\n".join([
        f"Título: {item.get('titulo')}\n"
        f"Descrição: {item.get('description')}\n"
        f"Órgão: {item.get('orgao')}\n"
        f"cnpj_org: {item.get('cnpj')}\n"
        f"valorTotal: {item.get('valor')}\n"
        f"Link: {item.get('link')}\n"
        f"{'-'*40}"
        for item in list
    ])
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
import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email(lista):
    print("Entrou no send_email")
    print("Quantidade de itens:", len(lista))
    if not lista:
        print("Lista vazia, não enviando email")
        return

    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    corpo = "\n\n".join([
        f"{item.get('tittle')}\n{item.get('link')}"
        for item in lista
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
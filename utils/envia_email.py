import smtplib
import email.message
from flask import current_app

from dotenv import load_dotenv
import os

senha = os.getenv('SENHA_EMAIL')

def enviar_email_relatorio(destinatario, nome_arquivo):  
    load_dotenv()

    if not senha:
        raise ValueError("A variável de ambiente SENHA_EMAIL não foi encontrada. Certifique-se de que está configurada corretamente.")

    msg = email.message.EmailMessage()
    msg['Subject'] = f"{nome_arquivo} das avaliações"
    msg['From'] = "rafaeltestepython@gmail.com"
    msg['To'] = destinatario
    msg.set_content("Segue o arquivo em anexo.")

    if not os.path.exists(nome_arquivo):
        print("Arquivo não encontrado para anexo.")
        return

    with open(nome_arquivo, "rb") as f:
        msg.add_attachment(f.read(), maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=nome_arquivo)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(msg['From'], senha)
            server.send_message(msg)

        os.remove(nome_arquivo)

        return True
    
    except Exception as e:
        return False

def envia_email_recuperacao(token, destinatario):
    load_dotenv()

    if not senha:
        raise ValueError("A variável de ambiente SENHA_EMAIL não foi encontrada. Certifique-se de que está configurada corretamente.")
    
    reset_link = f"{current_app.config['SERVER_NAME']}/reset_senha/{token}"
    msg = email.message.EmailMessage()
    msg['Subject'] = "Redefinição de Senha"
    msg['From'] = "rafaeltestepython@gmail.com"
    msg['To'] = destinatario
    msg.set_content(f"Para redefinir sua senha, clique no link: {reset_link}")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(msg['From'], senha)
            server.send_message(msg)

        return True
    
    except Exception as e:
        return False
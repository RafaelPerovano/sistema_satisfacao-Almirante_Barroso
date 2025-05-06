from itsdangerous import URLSafeTimedSerializer
# from config import SECRET_KEY

import os
from dotenv import load_dotenv

secret_key = os.getenv('SECRET_KEY')
s = URLSafeTimedSerializer(secret_key)

def cria_token_redefinicao_senha(email):
    return s.dumps(email, salt='reset-senha')

def verifica_token_redefinicao_senha(token, expiration=3600):
    try:
        return s.loads(token, salt='reset-senha', max_age=expiration)
    except:
        return None

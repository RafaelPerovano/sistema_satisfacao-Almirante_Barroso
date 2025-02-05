import psycopg2
import os 
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()

url = os.getenv('DATABASE_URL')

if not url:
    raise ValueError("A variável de ambiente DATABASE_URL não foi encontrada. Certifique-se de que está configurada no Render.")

conn = psycopg2.connect(url)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

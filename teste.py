from db import conn, cursor

#cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'avaliacoes'")
#cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
#"CREATE table admin (id SERIAL PRIMARY KEY, nome VARCHAR(100) NOT NULL, email VARCHAR(150) UNIQUE NOT NULL, senha TEXT NOT NULL)"
estrutura_tabela = "select * from admins where usuario='Rafael'"
cursor.execute(estrutura_tabela)
mostrar=cursor.fetchall()
print(mostrar)
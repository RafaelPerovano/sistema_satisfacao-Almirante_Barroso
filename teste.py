from cria_excel import enviar_email

enviar_email("Teste!", "teste", "tcurie.rpgp@gmail.com", "rafaeltestepython@gmail.com")
"""
#cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'avaliacoes'")
#cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")

estrutura_tabela = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'avaliacoes'"
cursor.execute(estrutura_tabela)
mostra = cursor.fetchall()
print(mostra)"
"""
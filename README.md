
# Projeto de Sistema de Avaliação Escolar

Este é um projeto simples de sistema de avaliação escolar feito com Flask e PostgreSQL. A ideia é permitir que diferentes tipos de usuários (como professores, alunos, etc.) façam login e deixem uma avaliação de satisfação sobre a escola ou serviços. O projeto foi desenvolvido com a finalidade de ser aplicado em uma tela touch screen que está instalada na escola para todos e com o intuito de praticar meus conhecimentos sobre as tecnologias utilizadas.

## Tecnologias Utilizadas
- **Backend**: Flask (Python)
- **Banco de Dados**: PostgreSQL
- **Frontend**: HTML, CSS, Bootstrap
- **Manipulação de Planilhas**: openpyxl
- **Gerenciamento de Variáveis de Ambiente**: python-dotenv

## Funcionalidades
- Sistema de login com Flask
- Avaliação com emojis e comentários
- Controle de sessão por tipo de usuário
- Tela de admin (protótipo)
- Geração de relatórios em Excel com base nas avaliações
- Envio de relatórios por email (funcionalidade a ser implementada)

## Como Rodar o Projeto
1. Clone o repositório
2. Crie e ative um ambiente virtual (opcional, mas recomendado):
   ```python -m venv venvsource venv/bin/activate  # ou venv\Scripts\activate no Windows```
3. Instale as dependências:
   ```pip install -r requirements.txt```
4. Configure o banco de dados PostgreSQL:
   - Crie um arquivo `.env` na raiz do projeto e adicione a variável de ambiente `DATABASE_URL` com a URL do seu banco de dados PostgreSQL:
     ```
     DATABASE_URL="url_bd"
     ```
5. Execute o Flask:
   ```python app.py```
   O servidor Flask estará rodando no `http://127.0.0.1:5000/`.

## Estrutura do Projeto
```
/
|-- app.py
|-- db.py
|-- utils/
    |-- cria_excel.py
    |-- envia_email.py
    |-- tokens.py
|-- static/
|   |-- img/
|-- templates/
|   |-- avaliacao.html
|   |-- detalhes_avaliacao.html
|   |-- index.html
|   |-- painel.html
|   |-- termino_avaliacao.html
|-- .env
|-- .gitignore
|-- requirements.txt
|-- README.md
```

## Melhorias Futuras
- Criar relatórios de avaliações para admins
- Implementar a interface do painel de controle
- Implementar o sistema de login com Flask-Login
- Enviar relatórios por email para os administradores

from flask import Flask, request, render_template, redirect, session, url_for, flash, jsonify, send_file
import psycopg2
from db import cursor, conn
from datetime import datetime, timedelta
from utils.cria_excel import cria_excel_tipo
from utils.tokens import cria_token_redefinicao_senha, verifica_token_redefinicao_senha
from utils.envia_email import envia_email_recuperacao
from functools import wraps

import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config.from_pyfile('config.cfg', silent=True)
# app.permanent_session_lifetime = timedelta(minutes=3)

class BaseUser:
    def __init__(self, id, usuario):
        self.id = id
        self.usuario = usuario

    def get_id(self):
        return self.id

    def get_usuario(self):
        return self.usuario

# classe para o modelo de usuário
class User(BaseUser):
    def __init__(self, id, usuario, tipo_usuario, ultima_avaliacao):
        super().__init__(id, usuario)
        self.tipo_usuario = tipo_usuario
        self.ultima_avaliacao = ultima_avaliacao
    
    def is_active(self):
        return True

    def get_id(self):
        return self.id
    
    def get_usuario(self):
        return self.usuario
    
    def get_tipo_usuario(self):
        return self.tipo_usuario
    
    def get_ultima_avaliacao(self):
        return self.ultima_avaliacao
    
# função para carregar o usuário na sessão
def load_user(user_id):
    cursor.execute("SELECT tipo_usuario, usuario, ultima_avaliacao FROM usuarios WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        return User(user_id, user_data[0], user_data[1], user_data[2])
    return None
    
# classe para o modelo de admin
class Admin(BaseUser):
    def __init__(self, id, usuario, email, senha):
        super().__init__(id, usuario)
        self.email = email
        self.senha = senha
    
    def is_active(self):
        return True

    def get_id(self):
        return self.id
    
    def get_usuario(self):
        return self.usuario
    
    def get_email(self):
        return self.email
    
    def get_senha(self):
        return self.senha

def load_user_admin(user_id):
    cursor.execute("SELECT usuario, email, senha FROM admins WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        return Admin(user_id, user_data[0], user_data[1], user_data[2])
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se o usuário na sessão é um admin
        if 'usuario' not in session or 'email' not in session:
            flash("Acesso não permitido! Faça login como admin.", "danger")
            return redirect(url_for("login_admin"))
        return f(*args, **kwargs)
    return decorated_function

# página inicial
@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

# página de login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tipo_usuario = request.form['tipo_usuario']
        usuario = request.form['usuario']

        if usuario != "admin":
            cursor.execute("SELECT u.id, u.usuario, tu.nome AS tipo_usuario, u.ultima_avaliacao FROM usuarios u JOIN tipo_usuario tu ON u.tipo_usuario_id = tu.id WHERE u.usuario = %s", (usuario,))
            user_data = cursor.fetchone()

            if tipo_usuario and usuario:
                # faz o login do usuario
                if user_data:
                    user = User(user_data[0], user_data[1], user_data[2], user_data[3])
                    
                    # armazena as informações do usuário na sessão
                    session['user_id'] = user.id
                    session['tipo_usuario'] = user.tipo_usuario
                    session['usuario'] = user.usuario
                    session['ultima_avaliacao'] = user.ultima_avaliacao
                    
                    avaliou = ja_avaliou()
                    
                    if avaliou == False:
                        return redirect('avaliacao')
                    else:
                        return redirect('login')
                
                # caso o usuário não esteja no bd
                flash("Credenciais inválidas!", "warning")
                return redirect(url_for("login"))
            
            # caso nao seja enviado o tipo de usuario nem o nome de usuario
            flash("Seu usuário e/ou tipo de usuario não pode estar vazio!", "danger")
            return redirect(url_for("login"))

        return redirect(url_for("login_admin"))
    
    return render_template("index.html")

@app.route("/login_admin", methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        if email and senha:
            cursor.execute("SELECT id, usuario, email, senha FROM admins WHERE email = %s", (email,))
            user_data = cursor.fetchone()

            if user_data:
                if senha == user_data[3]:            
                    # faz o login do usuario
                    user = Admin(user_data[0], user_data[1], user_data[2], user_data[3])
                    
                    # armazena as informações do usuário na sessão
                    session['user_id'] = user.id
                    session['usuario'] = user.usuario
                    session['email'] = user.email
                    session['senha'] = user.senha

                    # manda para o painel de admin
                    return redirect(url_for("painel"))

                # caso a senha esteja inorreta
                flash("Senha incorreta!", "warning")
                return redirect(url_for("login_admin"))
            
            # caso o usuário não esteja no bd
            flash("Credenciais inválidas!", "warning")
            return redirect(url_for("login_admin"))
        
        # caso nao seja enviado o tipo de usuario nem o nome de usuario
        flash("Seu usuário e/ou tipo de usuario não pode estar vazio!", "danger")
        return redirect(url_for("login_admin"))
    
    return render_template("login_admin.html")

# página da avaliação
@app.route("/avaliacao", methods=['GET', 'POST'])
def avaliacao():
    if request.method == 'POST':
        dados = request.form

        satisfacao = dados.get("emogi")
        comentarios = dados.get("comentarios")
        data = datetime.now()
        turno = verificar_turno(data.hour)
        data = datetime.now().strftime('%Y-%m-%d')
        id_usuario = session.get('user_id')
        tipo_usuario = session.get('tipo_usuario')

        if satisfacao:
            cursor.execute("INSERT INTO avaliacoes (id_usuario, tipo_usuario, satisfacao, comentarios, turno, data) VALUES (%s, %s, %s, %s, %s, %s)", (id_usuario, tipo_usuario, satisfacao, comentarios, turno, data))
            cursor.execute("UPDATE usuarios SET ultima_avaliacao = %s WHERE usuario = %s", (data, session.get('usuario')))

            # logout do sistema
            session.clear()
    
            return render_template("termino_avaliacao.html")
        
        # caso nao seja enviado o emoji
        flash("Voce precisa selecionar um emogi!", "danger")
        return redirect(url_for("avaliacao"))
    
    return render_template("avaliacao.html")

# página do painel que contém as avaliações
@app.route("/painel", methods=['GET', 'POST'])
@admin_required
def painel():
    tipos_usuario = ['Professor', 'Aluno', 'Pedagogia', 'Terceirizada']
    contagens = {}
    
    cursor.execute("SELECT COUNT(*) FROM avaliacoes")
    n_avaliacoes = cursor.fetchone()[0]

    for tipo in tipos_usuario:
        cursor.execute("SELECT COUNT(*) FROM avaliacoes WHERE tipo_usuario=%s", (tipo,))
        contagens[tipo] = cursor.fetchone()[0]

    porcentagens = {tipo: calcula_porcentagem(contagens[tipo], n_avaliacoes) for tipo in contagens}

    return render_template("painel.html", 
        n_avaliacoes=n_avaliacoes, 
        por_professores=porcentagens['Professor'],  
        por_alunos=porcentagens['Aluno'], 
        por_pedagogia=porcentagens['Pedagogia'], 
        por_terceirizada=porcentagens['Terceirizada']
    )

# página dos detalhes das avaliações
@app.route("/detalhes_avaliacoes/<tipo>")
@admin_required
def detalhes_avaliacoes(tipo):
    cursor.execute("SELECT satisfacao, COUNT(*) FROM avaliacoes WHERE tipo_usuario = %s GROUP BY satisfacao", (tipo,))
    dados = cursor.fetchall()

    cursor.execute("SELECT comentarios from avaliacoes where tipo_usuario = %s", (tipo,))
    comentarios = cursor.fetchall()

    # seleciona os dados mais detalhados das avaliações de acordo com o tipo de usuario
    return render_template("detalhes_avaliacoes.html", dados=dados, tipo_usuario=tipo, comentarios=comentarios)

@app.route("/dados_detalhes_avaliacoes", methods=['GET'])
@admin_required
def dados_detalhes_avaliacoes():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    tipo = request.args.get('tipo')

    dados = detalhes_avaliacoes_data(data_inicio, data_fim, tipo)
    
    return jsonify(dados)

def detalhes_avaliacoes_data(data_inicio, data_fim, tipo):
    if data_inicio and data_fim:
        cursor.execute("SELECT satisfacao::TEXT, COUNT(*) FROM avaliacoes WHERE tipo_usuario = %s AND data BETWEEN %s AND %s GROUP BY satisfacao ORDER BY satisfacao", (tipo, data_inicio, data_fim))
        dados = dict(cursor.fetchall())

        cursor.execute("SELECT comentarios FROM avaliacoes WHERE tipo_usuario = %s AND data BETWEEN %s AND %s AND comentarios IS NOT NULL", (tipo, data_inicio, data_fim))
        comentarios = [row[0] for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT satisfacao::TEXT, COUNT(*) FROM avaliacoes WHERE tipo_usuario = %s GROUP BY satisfacao ORDER BY satisfacao", (tipo,))
        dados = dict(cursor.fetchall())

        cursor.execute("SELECT comentarios FROM avaliacoes WHERE tipo_usuario = %s AND comentarios IS NOT NULL", (tipo,))
        comentarios = [row[0] for row in cursor.fetchall()]

    return {"dados": dados, "comentarios": comentarios, "tipo_usuario": tipo}

@app.route("/dados_avaliacoes", methods=['GET'])
@admin_required
def dados_avaliacoes():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    dados = avaliacoes_data(data_inicio, data_fim)

    return jsonify(dados)

def avaliacoes_data(data_inicio, data_fim):
    tipos_usuario = ['Professor', 'Aluno', 'Pedagogia', 'Terceirizada']
    contagens = {}

    if data_inicio and data_fim:
        cursor.execute("SELECT COUNT(*) FROM avaliacoes WHERE data BETWEEN %s AND %s", (data_inicio, data_fim))
        n_avaliacoes = cursor.fetchone()[0]

        for tipo in tipos_usuario:
            cursor.execute("SELECT COUNT(*) FROM avaliacoes WHERE tipo_usuario=%s AND data BETWEEN %s AND %s", (tipo, data_inicio, data_fim))
            contagens[tipo] = cursor.fetchone()[0]
        
        porcentagens = {tipo: calcula_porcentagem(contagens[tipo], n_avaliacoes) for tipo in contagens}

        dados = {"n_avaliacoes": n_avaliacoes, "porcentagens": porcentagens}

        return dados
    
    cursor.execute("SELECT COUNT(*) FROM avaliacoes")
    n_avaliacoes = cursor.fetchone()[0]

    for tipo in tipos_usuario:
        cursor.execute("SELECT COUNT(*) FROM avaliacoes WHERE tipo_usuario=%s", (tipo,))
        contagens[tipo] = cursor.fetchone()[0]

    porcentagens = {tipo: calcula_porcentagem(contagens[tipo], n_avaliacoes) for tipo in contagens}

    dados = {"n_avaliacoes": n_avaliacoes, "porcentagens": porcentagens}

    return dados

@app.route("/dados_excel_tipo", methods=['POST'])
@admin_required
def dados_excel_tipo():
    data = request.get_json()
    tipo_usuario = str(data.get('tipo_usuario'))
    data_inicio = str(data.get('data_inicio'))
    data_fim = str(data.get('data_fim'))

    gerou_excel = gera_excel(tipo_usuario, data_inicio, data_fim)

    if gerou_excel:
        response = {"status": "success", "message": "Email enviado!"}
    else:
        response = {"status": "danger", "message": "Email não foi enviado!"}

    return jsonify(response)

def gera_excel(tipo_usuario, data_inicio, data_fim):
    if data_inicio and data_fim:
        cursor.execute("SELECT data, satisfacao, comentarios, turno FROM avaliacoes WHERE tipo_usuario = %s AND data BETWEEN %s AND %s ORDER BY data ASC", (tipo_usuario, data_inicio, data_fim))
        avaliacoes = cursor.fetchall()

        cria_excel = cria_excel_tipo(tipo_usuario, data_inicio, data_fim, avaliacoes)
    else:
        cursor.execute("SELECT data, satisfacao, comentarios, turno FROM avaliacoes WHERE tipo_usuario = %s ORDER BY data ASC", (tipo_usuario,))
        avaliacoes = cursor.fetchall()

        cria_excel = cria_excel_tipo(tipo_usuario, data_inicio, data_fim, avaliacoes)
    
    print("CRIA EXCEL:", cria_excel)

    return cria_excel

@app.route("recuperacao_senha", methods=['GET', 'POST'])
def recuperacao_senha():
    if request.method == 'POST':
        email = request.form['email']

        if email:
            cursor.execute("SELECT * FROM admins WHERE email=%s", (email,))
            dados_email = cursor.fetchone()

            if dados_email:
                token = cria_token_redefinicao_senha(email)
                envia_email_recuperacao(token, email)

            flash("Email nao encontrado no sistema! Digite um email válido.", "danger")
            return redirect(url_for("recuperacao_senha"))
        
        flash("Digite um email!", "danger")
        return redirect(url_for("recuperacao_senha"))

    render_template("recuperacao_senha.html")

def ja_avaliou():
    hoje = datetime.now().strftime('%Y-%m-%d')
    ultima_avaliacao = session.get('ultima_avaliacao')
    
    if ultima_avaliacao and hoje == ultima_avaliacao.strftime('%Y-%m-%d'):
        return True
    else:
        return False

def verificar_turno(hora):
    if 6 <= hora < 12:
        return "Manha"
    elif 12 <= hora < 19:
        return "Tarde"
    elif 19 <= hora <= 23:
        return "Noite"
    else:
        return "fora do horario"

def calcula_porcentagem(qnt, total):
    if total == 0:
        return 0
    return round((qnt / total) * 100, 1)

if __name__ == "__main__":
    app.run(debug=True)
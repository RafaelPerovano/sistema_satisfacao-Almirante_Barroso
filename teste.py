from flask import Flask, request, render_template, redirect, jsonify, session, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import psycopg2
from db import cursor, conn

#cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'tipo_usuario'")
#cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
#cursor.execute("insert into usuarios (tipo_usuario_id, usuario) values (1, 'TESTE1.4')")
tipo = 'Professor'
cursor.execute("SELECT comentarios from avaliacoes where tipo_usuario = %s", (tipo,))
mostra = cursor.fetchall()
print(mostra)
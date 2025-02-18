from flask import Flask, request, render_template, redirect, jsonify, session, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import psycopg2
from db import cursor, conn

#cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'avaliacoes'")
#cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
cursor.execute("SELECT * from usuarios")

mostra = cursor.fetchall()
print(mostra)
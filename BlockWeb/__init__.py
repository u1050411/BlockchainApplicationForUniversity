import functools
import secrets
from os.path import abspath, dirname, join

from flask import Flask, session, redirect, url_for
from flask_sock import Sock

from BlockWeb import auth
from BlockchainUniversity import BlockchainUniversity
from CreateMysql import MySqlBloc

app = Flask(__name__)
my_db = MySqlBloc('localhost', 'root', 'root', 'blockchainuniversity')
main = BlockchainUniversity(my_db)
app.secret_key = secrets.token_urlsafe()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Configuració de la conexio
sock = Sock(app)
# Definim la carpeta on guardarem els pdf
BASE_DIR = dirname(dirname(abspath(__file__)))
PATH_RELATIU = join('static', 'fitxers')
PATH_TOTAL = join(BASE_DIR, 'BlockWeb', PATH_RELATIU)
PROFESSOR = "professor"
ESTUDIANT = "estudiant"
BOTH = "both"


import BlockWeb.Login
import BlockWeb.Estudiants
import BlockWeb.Comunicacio
import BlockWeb.Professors




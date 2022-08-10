import functools
import os
import secrets
from datetime import datetime

from requests import request
from BlockchainUniversity import Factoria, Examen, Transaccio
from BlockWeb import auth
from CreateMysql import MySqlBloc
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from os.path import abspath, dirname, join

app = Flask(__name__)
my_db = MySqlBloc('localhost', 'Pau', 'UsuariUdg2022', 'blockchainuniversity')
app.secret_key = secrets.token_urlsafe()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Definim la carpeta on guardarem els pdf
BASE_DIR = dirname(dirname(abspath(__file__)))
WEB_DIR = join(BASE_DIR, 'BlockWeb\\static')
STATIC_DIR = join(BASE_DIR, 'static')
# directori pdf
app.config["PDF_FILES"] = join(STATIC_DIR, 'fitxers')
PROFESSOR = "professor"
ESTUDIANT = "estudiant"


def es_usuari(tipus):
    def decorator_es_usuari(func):
        # Comprovem que hem iniciat sessió
        @functools.wraps(func)
        def wrapper_sessio_iniciada(*args, **kwargs):
            if session:
                if session['tipus'] == tipus:
                    return func(*args, **kwargs)
            return redirect(url_for("login"))
        return wrapper_sessio_iniciada
    return decorator_es_usuari


@app.route('/')
def inici():  # put application's code here
    adreça = '/login'
    if session:
        if session['tipus'] == "estudiant":
            adreça = "/alumne"

        elif session['tipus'] == "professor":
            adreça = '/professor'

    return redirect(adreça)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuari = request.form.get('usuari')
        password = request.form.get('password').encode('utf-8')
        user = Factoria.build_usuari_from_db(my_db, usuari)
        if user is not None:
            if password == user.contrasenya.encode('utf-8'):
                session['id'] = user.id
                session['tipus'] = user.tipus
                session['nom'] = user.nom + " " + user.cognom
                return redirect('/')
    return render_template("login.html")


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("logout.html")


@app.route('/professor')
@es_usuari(tipus=PROFESSOR)
def professor():  # put application's code here
    if session:
        if session['tipus'] != "professor":
            return redirect('/')
    return render_template('professor.html')


@app.route('/seleccionar_alumnes')
@es_usuari(tipus=PROFESSOR)
def seleccionar_alumnes():
    user = Factoria.build_usuari_from_db(my_db, session['id'])
    llista_alumnes = user.llista_alumnes(my_db)
    llista_dades = list()

    for x in llista_alumnes:
        valors = [x.id, x.nif, x.nom, x.cognom]
        llista_dades.append(valors)

    # llista_pdf = user.llista

    data = str(datetime.today())
    avui_format = data[0:10] + "T" + data[11:16]


    return render_template('selecionar_alumnes.html', llista_1=llista_dades, data_avui=avui_format)



@app.route('/enviar_examens', methods=["GET", "POST"])
@es_usuari(tipus=PROFESSOR)
def enviar_examen():  # put application's code here
    if request.method == "POST":
        fitxer = request.files['path_fitxer']
        if fitxer.filename:
            image_name = secure_filename(fitxer.filename)
            images_dir = app.config['PDF_FILES']
            os.makedirs(images_dir, exist_ok=True)
            file_path = os.path.join(images_dir, image_name)
            fitxer.save(file_path)

        datai = request.form.get('data_inici')
        dataf = request.form.get('data_entrega')
        id_examen = my_db.seguent_id_examen()
        professor = Factoria.build_usuari_from_db(my_db, session['id'])
        examen = Examen(id_examen, professor, file_path, datai, dataf, datetime.today())
        for val in request.form.getlist("select_usuaris"):
            alumn = Factoria.build_usuari_from_db(my_db, val)
            examen.afegir_estudiants(alumn)
        my_db.guardar_examen(examen)
        for alumn in examen.estudiants:
            transaccio = Transaccio(professor, alumn, examen)
            my_db.guardar_transaccio(transaccio)
        uni = Factoria.build_universitat_from_db(my_db)
    return render_template("examens_enviats.html")


@app.route('/alumne', methods=["GET", "POST"])
@es_usuari(tipus=ESTUDIANT)
def alumne():  # put application's code here
    return render_template('estudiants.html')



if __name__ == '__main__':
    app.run(debug=True)

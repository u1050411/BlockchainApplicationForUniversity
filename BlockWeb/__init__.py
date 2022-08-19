import functools
import os
import secrets
from datetime import datetime
from os.path import abspath, dirname, join

import simple_websocket
from flask import Flask, request, render_template, session, redirect, url_for
from flask_sock import Sock

from BlockWeb import auth
from BlockchainUniversity import Factoria, Examen, Transaccio, BlockchainUniversity, RespostaExamen, AvaluacioExamen
from CreateMysql import MySqlBloc


app = Flask(__name__)
my_db = MySqlBloc('localhost', 'Pau', 'UsuariUdg2022', 'blockchainuniversity')
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


def es_usuari(tipus):
    def decorator_es_usuari(func):
        # Comprovem que hem iniciat sessió
        @functools.wraps(func)
        def wrapper_sessio_iniciada(*args, **kwargs):
            if session:
                if session['tipus'] == tipus or tipus == BOTH:
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


@app.route('/echo', websocket=True)
def echo():
    print("hola")
    ws = simple_websocket.Server(request.environ)
    try:
        while True:
            data = ws.receive()
            print(data)
    except simple_websocket.ConnectionClosed:
        pass
    return render_template('block_enviat.html', bloc=data)


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
    llista_fitxers = user.llista_pdf(my_db)
    llista_pdf = list()
    for x in llista_fitxers:
        valors = [x.id_document, x.data_creacio, x.nom_fitxer]
        llista_pdf.append(valors)
    data = str(datetime.today())
    avui_format = data[0:10] + "T" + data[11:16]

    return render_template('selecionar_alumnes.html', llista_1=llista_dades, llista_2=llista_pdf, data_avui=avui_format)


@app.route('/alumne', methods=["GET", "POST"])
@es_usuari(tipus=ESTUDIANT)
def alumne():  # put application's code here
    return render_template('estudiant.html')


@app.route('/triar_examens')
@es_usuari(tipus=ESTUDIANT)
def triar_examens():
    user = Factoria.build_usuari_from_db(my_db, session['id'])
    llista = user.importar_examens(my_db)
    llista_examens = list()
    for x in llista:
        (id_document, id_professor, data_inici, data_final) = x
        profe = Factoria.build_usuari_from_db(my_db, id_professor)
        valors = [id_document, profe.nom, profe.cognom, data_inici, data_final]
        llista_examens.append(valors)
    return render_template('triar_examens.html', llista=llista_examens, tipus=session['tipus'])


@app.route('/triar_resposta')
@es_usuari(tipus=PROFESSOR)
def triar_resposta():
    user = Factoria.build_usuari_from_db(my_db, session['id'])
    llista = user.importar_examens(my_db)
    llista_examens = list()
    for x in llista:
        if x.nota is None or x.nota == 0:
            nom_assignatura = Factoria.build_examen_from_db(my_db, x.examen.id_document).assignatura.nom
            estudiant = Factoria.build_usuari_from_db(my_db, x.usuari.id)
            valors = [x.id_document, nom_assignatura, estudiant.nom, estudiant.cognom, x.data_creacio]
            llista_examens.append(valors)
    return render_template('triar_resposta.html', llista=llista_examens, tipus=session['tipus'])


@app.route('/veure_resposta', methods=["GET", "POST"])
@es_usuari(tipus=PROFESSOR)
def veure_resposta():
    id_resposta = request.form.get('resposta')
    resposta = Factoria.build_id_resposta_alumne_from_db(my_db, id_resposta)
    if resposta is None:
        redirect('error404.html')
    session['id_resposta'] = id_resposta
    pdf = resposta.pdf
    nom_total = join(PATH_TOTAL, 'veure_resposta.pdf')
    nom_relatiu = join(PATH_RELATIU, 'veure_resposta.pdf')
    Factoria.guardar_fitxer(nom_total, pdf)
    estudiant = Factoria.build_usuari_from_db(my_db, resposta.usuari.id)
    missatge = "Aquest es la resposta del alumne" + " " + resposta.usuari.nom + " " + resposta.usuari.cognom
    return render_template('veure_resposta.html', fitxer=nom_relatiu, missatge=missatge, opcio=1)


@app.route('/pujar_avaluacio', methods=["GET", "POST"])
@es_usuari(tipus=PROFESSOR)
def pujar_avaluacio():
    missatge = "Aquesta es la Resposta del alumne : "
    user = Factoria.build_usuari_from_db(my_db, session['id'])
    nom = user.nom + " " + user.cognom
    tipus = session['tipus']
    if request.method == 'POST':
        missatge = "Pots triar un altre avaluacio o entregar aquesta : "
        # Mira si el request es correcte
        if 'path_fitxer' not in request.files:
            missatge = "No ha anat be, torna-ho a intentar"
        pdf = request.files['path_fitxer']
        # Mira si el usari ha triat un fitxer
        if pdf.filename == '':
            missatge = "No has triat un fitxer, torna-ho a intentar"
        # pdf_nom = secure_filename(pdf.filename)
        os.makedirs(PATH_TOTAL, exist_ok=True)
        pdf.save(join(PATH_TOTAL, 'avaluacio.pdf'))
        nom_relatu = join(PATH_RELATIU, 'avaluacio.pdf')
        return render_template('veure_resposta.html', fitxer=nom_relatu, hora="", missatge=missatge, opcio=2)
    return render_template('pujar_avaluacio.html', nom=nom, tipus=tipus, missatge=missatge)


@app.route('/entregar_avaluacio', methods=["GET", "POST"])
@es_usuari(tipus=PROFESSOR)
def entregar_avaluacio():
    nota = request.form.get('nota')
    profe = Factoria.build_usuari_from_db(my_db, session['id'])
    id_resposta = session['id_resposta']
    resposta = Factoria.build_id_resposta_alumne_from_db(my_db, id_resposta)
    nom_fitxer_avaluacio = join(PATH_TOTAL, 'avaluacio.pdf')
    pdf = Factoria.recuperar_fitxer(nom_fitxer_avaluacio)
    estudiant = resposta.usuari
    id_avaluacio = my_db.seguent_id_avaluacio()
    avaluacio = AvaluacioExamen(resposta, profe, resposta.usuari, pdf, nota)
    avaluacio.id_document = id_avaluacio
    my_db.guardar_avaluacio_examen(avaluacio)
    avaluacio = Factoria.build_avaluacio_from_db(my_db, id_avaluacio)
    transaccio = Transaccio(profe, estudiant, avaluacio)
    my_db.guardar_transaccio(transaccio)
    main.minat()
    pdf_avaluacio = avaluacio.pdf
    pdf_resposta = resposta.pdf
    nom_total_avaluacio = join(PATH_TOTAL, 'avaluacio.pdf')
    nom_relatiu_avaluacio = join(PATH_RELATIU, 'avaluacio.pdf')
    nom_total_resposta = join(PATH_TOTAL, 'veure_resposta.pdf')
    nom_relatiu_resposta = join(PATH_RELATIU, 'veure_resposta.pdf')
    Factoria.guardar_fitxer(nom_total_avaluacio, pdf_avaluacio)
    Factoria.guardar_fitxer(nom_total_resposta, pdf_resposta)
    return render_template('resposta_evaluacio.html', fitxer_avaluacio=nom_relatiu_avaluacio,
                           fitxer_resposta=nom_relatiu_resposta, nota=nota)


@app.route('/pujar_pdf', methods=["GET", "POST"])
@es_usuari(tipus=ESTUDIANT)
def pujar_pdf():
    missatge = "L'hora limit per entregar l'examen es : "
    user = Factoria.build_usuari_from_db(my_db, session['id'])
    nom = user.nom + " " + user.cognom
    tipus = session['tipus']
    if request.method == 'POST':
        missatge = "Pots triar agafar un altre resposta o entregar aquesta : "
        # Mira si el request es correcte
        if 'path_fitxer' not in request.files:
            missatge = "No ha anat be, torna-ho a intentar"
        pdf = request.files['path_fitxer']
        # Mira si el usari ha triat un fitxer
        if pdf.filename == '':
            missatge = "No has triat un fitxer, torna-ho a intentar"
        # pdf_nom = secure_filename(pdf.filename)
        os.makedirs(PATH_TOTAL, exist_ok=True)
        pdf.save(join(PATH_TOTAL, 'pdf_pujat.pdf'))
        nom_relatu = join(PATH_RELATIU, 'pdf_pujat.pdf')
        return render_template('veure_examen.html', fitxer=nom_relatu, hora="", missatge=missatge)
    return render_template('pujar_pdf.html', nom=nom, tipus=tipus, missatge=missatge)


@app.route('/entregar_resposta', methods=["GET", "POST"])
@es_usuari(tipus=ESTUDIANT)
def entregar_resposta():
    user = Factoria.build_usuari_from_db(my_db, session['id'])
    id_examen = session['examen']
    examen = Factoria.build_examen_from_db(my_db, id_examen, True)
    profe = examen.usuari
    nom_fitxer = join(PATH_TOTAL, 'pdf_pujat.pdf')
    pdf = Factoria.recuperar_fitxer(nom_fitxer)
    id_resposta = my_db.seguent_id_resposta()
    resposta = RespostaExamen(id_resposta, examen, user, pdf)
    session['id_resposta'] = id_resposta
    my_db.guardar_resposta_examen(resposta)
    transaccio = Transaccio(user, profe, resposta)
    my_db.guardar_transaccio(transaccio)
    main.minat()
    pdf_examen = examen.pdf
    pdf_resposta = resposta.pdf
    nom_total_examen = join(PATH_TOTAL, 'veure_examen.pdf')
    nom_relatiu_examen = join(PATH_RELATIU, 'veure_examen.pdf')
    nom_total_resposta = join(PATH_TOTAL, 'veure_resposta.pdf')
    nom_relatiu_resposta = join(PATH_RELATIU, 'veure_resposta.pdf')
    Factoria.guardar_fitxer(nom_total_examen, pdf_examen)
    Factoria.guardar_fitxer(nom_total_resposta, pdf_resposta)
    return render_template('examen_resposta.html', fitxer_examen=nom_relatiu_examen,
                           fitxer_resposta=nom_relatiu_resposta)


@app.route('/veure_examen', methods=["GET", "POST"])
@es_usuari(tipus=ESTUDIANT)
def veure_examen():
    id_examen = request.form.get('examen')
    examen = Factoria.build_examen_from_db(my_db, id_examen, True)
    if examen is None:
        redirect('error404.html')
    session['examen'] = id_examen
    hora_limit = examen.data_final
    pdf = examen.pdf
    nom_total = join(PATH_TOTAL, 'veure_examen.pdf')
    nom_relatu = join(PATH_RELATIU, 'veure_examen.pdf')
    Factoria.guardar_fitxer(nom_total, pdf)
    missatge = "L'hora limit per entregar l'examen es : "
    return render_template('veure_examen.html', fitxer=nom_relatu, hora=hora_limit, missatge=missatge)


@app.route('/enviar_examens', methods=["GET", "POST"])
@es_usuari(tipus=BOTH)
def enviar_examen():  # put application's code here
    if request.method == "POST":
        id_pdf = request.form.get('path_fitxer')
        pdf = Factoria.build_pdf_from_db(my_db, id_pdf)
        datai = request.form.get('data_inici')
        dataf = request.form.get('data_entrega')
        id_examen = my_db.seguent_id_examen()
        profe = Factoria.build_usuari_from_db(my_db, session['id'])
        assignatura = profe.get_assignatura(my_db)
        examen = Examen(id_examen, profe, pdf.pdf, datai, dataf, datetime.today(), assignatura)
        for val in request.form.getlist("select_usuaris"):
            alumn = Factoria.build_usuari_from_db(my_db, val)
            examen.afegir_estudiants(alumn)
        my_db.guardar_examen(examen)
        for alumn in examen.estudiants:
            transaccio = Transaccio(profe, alumn, examen)
            my_db.guardar_transaccio(transaccio)
        main.minat()
    return render_template("examens_enviats.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)

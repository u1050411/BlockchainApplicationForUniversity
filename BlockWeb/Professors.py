import os
from datetime import datetime
from os.path import join

from flask import request, render_template, session, redirect
from fpdf import FPDF

from BlockWeb import PROFESSOR, app, PATH_TOTAL, PATH_RELATIU, main, my_db, Login
from BlockchainUniversity import Factoria, Transaccio, AvaluacioExamen


@app.route('/professor')
@Login.es_usuari(tipus=PROFESSOR)
def professor():  # put application's code here
    return render_template('professor.html')


@app.route('/seleccionar_alumnes')
@Login.es_usuari(tipus=PROFESSOR)
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



@app.route('/triar_resposta')
@Login.es_usuari(tipus=PROFESSOR)
def triar_resposta():
    user = Factoria.build_usuari_from_db(my_db, session['id'])
    llista = user.importar_respostes_examen(my_db)
    llista_examens = list()
    for x in llista:
        if x.nota is None or x.nota == 0:
            nom_assignatura = Factoria.build_examen_from_db(my_db, x.examen.id_document).assignatura.nom
            estudiant = Factoria.build_usuari_from_db(my_db, x.usuari.id)
            valors = [x.id_document, nom_assignatura, estudiant.nom, estudiant.cognom, x.data_creacio]
            llista_examens.append(valors)
    return render_template('triar_resposta.html', llista=llista_examens, tipus=session['tipus'])


@app.route('/veure_resposta', methods=["GET", "POST"])
@Login.es_usuari(tipus=PROFESSOR)
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
@Login.es_usuari(tipus=PROFESSOR)
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
@Login.es_usuari(tipus=PROFESSOR)
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


def escriure_cadena(cadena_bloc):
    nom_fitxer_txt = join(PATH_TOTAL, 'cadena.txt')
    nom_fitxer_pdf = join(PATH_TOTAL, 'cadena.pdf')
    with open(nom_fitxer_txt, 'w') as temp_file:
        for blocs in cadena_bloc:
            text = str(blocs.data_bloc)+"  "+str(blocs.hash_bloc_anterior)
            temp_file.write("%s\n" % text)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)
    f = open(nom_fitxer_txt, "r")
    for x in f:
        pdf.cell(200, 10, txt=x, ln=1, align='C')
    pdf.output(nom_fitxer_pdf)


@app.route('/veure_cadena')
def veure_cadena():
    cadena_bloc = Factoria.build_cadena_blocs(my_db)
    escriure_cadena(cadena_bloc)
    nom_relatu = join(PATH_RELATIU, 'cadena.pdf')
    missatge = "Aquesta es la cadena de BlockchainUniversity : "
    hora_limit = datetime.now()
    return render_template('veure_examen.html', fitxer=nom_relatu, hora=hora_limit, missatge=missatge)

@app.route('/veure_cadena_usuari')
def veure_cadena_usuari():
    usuari = Factoria.build_usuari_from_db(my_db, session['id'])
    cadena_bloc = Factoria.build_cadena_blocs_usuari(my_db, usuari)
    escriure_cadena(cadena_bloc)
    nom_relatu = join(PATH_RELATIU, 'cadena.pdf')
    missatge = "Aquesta es la cadena de BlockchainUniversity : "
    hora_limit = datetime.now()
    return render_template('veure_examen.html', fitxer=nom_relatu, hora=hora_limit, missatge=missatge)
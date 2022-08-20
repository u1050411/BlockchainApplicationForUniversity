import os
from datetime import datetime
from os.path import join

from flask import request, render_template, session, redirect

from BlockWeb import ESTUDIANT, BOTH, app, PATH_TOTAL, PATH_RELATIU, main, my_db, Login
from BlockchainUniversity import Factoria, Examen, Transaccio, RespostaExamen


@app.route('/')
def inici():  # put application's code here
    adreça = '/login'
    if session:
        if session['tipus'] == "estudiant":
            adreça = "/alumne"

        elif session['tipus'] == "professor":
            adreça = '/professor'

    return redirect(adreça)



@app.route('/alumne', methods=["GET", "POST"])
@Login.es_usuari(tipus=ESTUDIANT)
def alumne():  # put application's code here
    return render_template('estudiant.html')


@app.route('/triar_examens')
@Login.es_usuari(tipus=ESTUDIANT)
def triar_examens():
    user = Factoria.build_usuari_from_db(my_db, session['id_paquet'])
    llista = user.importar_examens(my_db)
    llista_examens = list()
    for x in llista:
        (id_document, id_professor, data_inici, data_final) = x
        profe = Factoria.build_usuari_from_db(my_db, id_professor)
        valors = [id_document, profe.nom, profe.cognom, data_inici, data_final]
        llista_examens.append(valors)
    return render_template('triar_examens.html', llista=llista_examens, tipus=session['tipus'])


@app.route('/pujar_pdf', methods=["GET", "POST"])
@Login.es_usuari(tipus=ESTUDIANT)
def pujar_pdf():
    missatge = "L'hora limit per entregar l'examen es : "
    user = Factoria.build_usuari_from_db(my_db, session['id_paquet'])
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
@Login.es_usuari(tipus=ESTUDIANT)
def entregar_resposta():
    user = Factoria.build_usuari_from_db(my_db, session['id_paquet'])
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
@Login.es_usuari(tipus=ESTUDIANT)
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
@Login.es_usuari(tipus=BOTH)
def enviar_examen():  # put application's code here
    if request.method == "POST":
        id_pdf = request.form.get('path_fitxer')
        pdf = Factoria.build_pdf_from_db(my_db, id_pdf)
        datai = request.form.get('data_inici')
        dataf = request.form.get('data_entrega')
        id_examen = my_db.seguent_id_examen()
        profe = Factoria.build_usuari_from_db(my_db, session['id_paquet'])
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

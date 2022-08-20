import functools
import json

import simple_websocket
from flask import request, render_template, session, redirect, url_for

from BlockWeb import BOTH, app, my_db
from BlockchainUniversity import Factoria, Bloc


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
#
# @app.route('/echo', websocket=True)
# def echo():
#     print("hola")
#     ws = simple_websocket.Server(request.environ)
#     try:
#         data = json.loads(ws.receive())
#         bloc = Bloc.crear_json(data)
#         hash = bloc.hash_bloc_anterior
#         Comunicacio.send()
#     except simple_websocket.ConnectionClosed:
#         pass
#     return render_template("login.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuari = request.form.get('usuari')
        password = request.form.get('password').encode('utf-8')
        user = Factoria.build_usuari_from_db(my_db, usuari)
        if user is not None:
            if password == user.contrasenya.encode('utf-8'):
                session['id_paquet'] = user.id_paquet
                session['tipus'] = user.tipus
                session['nom'] = user.nom + " " + user.cognom
                return redirect('/')
    return render_template("login.html")


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("logout.html")
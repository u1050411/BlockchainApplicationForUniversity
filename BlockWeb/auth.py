import bcrypt
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_session import Session

from BlockchainUniversity import Factoria
from . import my_db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuari = request.form.get('usuari')
        password = request.form.get('password').encode('utf-8')
        user = Factoria.build_usuari_from_db(my_db, usuari)
        if user is not None:

            if bcrypt.hashpw(password, user.contrasenya.encode('utf-8')) == user.contrasenya.encode('utf-8'):
                session['id'] = user.id
                return render_template("protected.html")
            else:
                return render_template("login.html", error="Error : Usuari o Password no trovat")
        else:
            return render_template("login.html", error="Error : Usuari  no trovat")
    else:
        return render_template("login.html", error="")


@auth.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("login.html")
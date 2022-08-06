import bcrypt
from flask import Blueprint, render_template, redirect, url_for, request, flash, session


from BlockchainUniversity import Factoria


@redirect.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuari = request.form.get('usuari')
        password = request.form.get('password').encode('utf-8')
        user = Factoria.build_usuari_from_db(main.my_db, usuari)
        if user is not None:

            if bcrypt.hashpw(password, user.contrasenya.encode('utf-8')) == user.contrasenya.encode('utf-8'):
                session['id'] = user.id
                return render_template("index.html", uni=main.name_udg)

    else:
        return render_template("login.html")


@redirect.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("login.html")
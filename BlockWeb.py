from pandas._libs import json

from BlockchainUniversity import Factoria
from CreateMysql import MySqlBloc
from flask import Flask, request, render_template

from Test import CreacioTaulaTest

app = Flask(__name__)
my_db = MySqlBloc('localhost', 'Pau', 'UsuariUdg2022', 'blockchainuniversity')


@app.route('/')
def inici():  # put application's code here
    name_udg = "udg dels rosals"
    return render_template("home.html", name=name_udg)


@app.route('/professor')
def professor():  # put application's code here
    return render_template('professor.html')

@app.route('/enviar_examens', methods=["GET", "POST"])
def enviar_examen():  # put application's code here
    if request.method =="POST":
        for val in request.form.getlist("select_usuaris"):
            print(val)
    return render_template("examens_enviats.html")

@app.route('/seleccionar alumnes')
def seleccionar_alumnes():
    user = Factoria.build_usuari_from_db(my_db, 2000256)
    llista_alumnes = user.llista_alumnes(my_db)
    llista_dades = list()
    for x in llista_alumnes:
        valors = [x.id, x.nif, x.nom, x.cognom]
        llista_dades.append(valors)
    return render_template("selecionar_alumnes.html", llista=llista_dades)


@app.route('/alumne', methods=["GET", "POST"])
def alumne():  # put application's code here
    return render_template('estudiants.html')


if __name__ == '__main__':
    app.run(debug=True)

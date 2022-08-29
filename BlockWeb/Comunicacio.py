import collections
import json
import simple_websocket
from flask import request, render_template
from BlockWeb import my_db, app
from BlockchainUniversity import Paquet, Factoria, Missatge
from CreateMysql import MySqlBloc


@app.route('/echo', websocket=True)
def echo():
    ws = simple_websocket.Server(request.environ)
    try:
        data = ws.receive()
        data_json = json.loads(data)
        missatge = Missatge.crear_json(data_json)
        if missatge.rebut(my_db):
            paquet = missatge.paquet
            paquet.ws = ws
            paquet.repartiment()
    except simple_websocket.ConnectionClosed:
        print("Emissio erronea")
    return render_template("login.html")


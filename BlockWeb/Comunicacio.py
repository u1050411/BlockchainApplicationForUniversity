import collections
import json
import simple_websocket
from flask import request, render_template
from BlockWeb import my_db, app
from BlockchainUniversity import Paquet


@app.route('/echo', websocket=True)
def echo():
    ws = simple_websocket.Server(request.environ)
    try:
        data = ws.receive()
        data_json = json.loads(data)
        paquet = Paquet.crear_json(data_json, my_db)
        paquet.ws = ws
        paquet.repartiment()
    except simple_websocket.ConnectionClosed:
        print("Emissio erronea")
    return render_template("login.html")



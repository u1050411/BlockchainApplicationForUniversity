import simple_websocket
import time
import json
from BlockchainUniversity import Factoria, Bloc
from flask import request, render_template, session, redirect
from CreateMysql import MySqlBloc
from BlockWeb import my_db, app


@app.route('/echo', websocket=True)
def echo():
    print("hola")
    ws = simple_websocket.Server(request.environ)
    try:
        data = json.loads(ws.receive())
        bloc = Bloc.crear_json(data)
        hash = bloc.hash_bloc_anterior
        send()

    except simple_websocket.ConnectionClosed:
        pass
    return render_template("login.html")


@app.route('/proves')
def proves():
    ws = simple_websocket.Client('ws://192.168.50.28:5005/echo')
    my_db = MySqlBloc('localhost', 'root', 'root', 'blockchainuniversity')
    bloc = Factoria.build_bloc_from_db(my_db, 6)
    json = Factoria.to_json(bloc)
    try:
        print("comenzar")
        data = json
        ws.send(data)
        print(f' {data}')
        time.sleep(0.5)
        data2 = ws.receive()
        ws.send("rebut")
        print("acabar")

    except (KeyboardInterrupt, EOFError, simple_websocket.ConnectionClosed):
        ws.close()
        return render_template("login.html")


def send(data):
    ws = simple_websocket.Client('ws://192.168.50.28:5005/echo')
    try:
        ws.send(data)
        data = ws.receive()
    except (KeyboardInterrupt, EOFError, simple_websocket.ConnectionClosed):
        ws.close()
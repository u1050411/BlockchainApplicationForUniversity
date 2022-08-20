import collections

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
        paquet = Paquet.crear_json(data)
        paquet.ws = ws
        paquet.repartiment()

    except simple_websocket.ConnectionClosed:
        print("Conexio tancada")
    return render_template("login.html")


@app.route('/proves')
def proves():
    ws = simple_websocket.Client('ws://192.168.50.27:5005/echo')
    my_db = MySqlBloc('localhost', 'root', 'root', 'blockchainuniversity')
    bloc = Factoria.build_bloc_from_db(my_db, my_db.id_ultim_bloc())
    id_ultim_bloc = my_db.id_ultim_bloc()
    try:
        print("comenzar")
        paquet = Paquet(1,id_ultim_bloc, bloc, ws)
        resultat = paquet.repartiment()
        print (resultat)

    except (KeyboardInterrupt, EOFError, simple_websocket.ConnectionClosed):
        ws.close()
        return render_template("login.html")


class Paquet:

    def __init__(self, id_paquet=None, dada=None, bloc=None, ws=None):
        self.id_paquet = id_paquet
        self.dada = dada
        self.bloc = bloc
        self.ws = ws

    def to_dict(self):
        return collections.OrderedDict({
            'id_paquet': self.id_paquet,
            'dada': self.dada,
            'bloc': Factoria.to_json(self.bloc)})

    @classmethod
    def crear_json(cls, dada):
        paquet_json = json.loads(dada)
        id_paquet = paquet_json['id_paquet']
        dada = paquet_json['dada']
        bloc = Bloc.crear_json(paquet_json['bloc'])
        return cls(id_paquet, dada, bloc)


    def repartiment(self):
        try:
            if self.id_paquet == 1:
                self.ws.send(Factoria.to_json(self))
                paquet = self.ws.receive()
                return paquet.repartiment(2)
        except (KeyboardInterrupt, EOFError, simple_websocket.ConnectionClosed):
            self.ws.close()

        if self.id_paquet == 2:
            num_blocs = my_db.id_ultim_bloc()
            if self.dada == num_blocs:
                meu_bloc = Factoria.build_bloc_from_db(my_db, num_blocs)
                return self.bloc.hash_bloc_anterior == meu_bloc.calcular_hash()
            else:
                return False




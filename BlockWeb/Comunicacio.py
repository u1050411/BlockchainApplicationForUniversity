import collections

import simple_websocket
import time
import json
from BlockchainUniversity import Factoria, Bloc
from flask import request, render_template, session, redirect
from CreateMysql import MySqlBloc
from BlockWeb import my_db, app


import asyncio
from contextlib import suppress


@app.route('/echo', websocket=True)
def echo():
    print("hola")
    ws = simple_websocket.Server(request.environ)
    try:
        print("##########1###########")
        data = ws.receive(15)
        data_json = json.loads(data)
        paquet = Paquet.crear_json(data_json)
        paquet.ws = ws
        paquet.repartiment()
        print("##########2###########")

    except simple_websocket.ConnectionClosed:
        print("Conexio tancada")
    return render_template("login.html")


@app.route('/proves')
def proves():
    # ws = simple_websocket.Client('ws://192.168.50.27:5005/echo')
    my_db = MySqlBloc('localhost', 'root', 'root', 'blockchainuniversity')
    bloc = Factoria.build_bloc_from_db(my_db, my_db.id_ultim_bloc())
    id_ultim_bloc = my_db.id_ultim_bloc()
    Paquet.confirmar_enviament(bloc.id,bloc.hash_bloc_anterior)












class Paquet:

    def __init__(self, dada=None, num_blocs=None, hash=None, ip=None):
        self.pas = 1
        self.num_blocs = num_blocs
        self.dada = dada
        self.hash = hash
        self.ws = simple_websocket.Client(f'ws://"+{ip}+"/echo')

    def to_dict(self):
        return collections.OrderedDict({
            'pas': self.pas,
            'num_blocs': self.num_blocs,
            'dada': self.dada,
            'hash': Factoria.to_json(self.hash)})

    @classmethod
    def crear_json(cls, paquet_json):
        id_paquet = paquet_json['pas']
        num_blocs = paquet_json['num_blocs']
        dada = paquet_json['dada']
        bloc = Bloc.crear_json(paquet_json['hash'])
        return cls(id_paquet, dada, bloc, num_blocs)

    def resposta(self):
        self.ws.send(Factoria.to_json(self))
        data = self.ws.receive(15)
        data_json = json.loads(data)
        paquet = Paquet.crear_json(data_json)
        self.pas = paquet.pas
        self.dada = paquet.dada
        self.repartiment()

    def repartiment(self):
        try:
            if self.pas == 1:# es un paquet inici de repartiment blocs
                print("**1**")
                self.pas = 2 # indiquem que es un paquet que hem enviat nosaltres
                self.ws.send(Factoria.to_json(self))
                self.resposta()

            elif self.pas == 2:# es paquet que hem rebut per confirmar blocs
                print("**2**")
                num_blocs = my_db.id_ultim_bloc()
                if self.dada == num_blocs:
                    meu_bloc = Factoria.build_bloc_from_db(my_db, num_blocs)
                    self.dada = self.hash.hash_bloc_anterior == meu_bloc.calcular_hash()
                    self.pas = 3
                    self.ws.send(Factoria.to_json(self))
                    self.resposta()
                else:
                    self.dada = False
                    self.pas = 3
                    self.num_blocs = num_blocs
                    self.ws.send(Factoria.to_json(self))
                    self.resposta()

            elif self.pas == 3:# Tenim la resposta si les dugues cadenes son correctes
                return self

        except (KeyboardInterrupt, EOFError, simple_websocket.ConnectionClosed):
            self.ws.close()

    @classmethod
    def confirmar_enviament(self):
        llista = Factoria.build_universitats_from_id_db(my_db)
        confirmacions = list

        for universitat in llista:
            id_bloc = universitat.id
            ip_universitat = universitat.ip
            has_anterior = universitat.calcular_hash()
            paquet = Paquet(id_bloc, id_bloc, has_anterior, ip_universitat)
            paquet.repartiment()
            confirmacions.append([universitat, paquet])
        if confirmacions:
            self.qui_es_mes_gran(confirmacions)


    # Retorna qui es la cadena mes llarga correcte
    def qui_es_mes_gran(self, confirmacions):
        llista = list
        for x in confirmacions:
            if x.dada:
                x = llista.pop(x.num_blocs)
                if x is None:
                    x = 1
                else:
                    x = x + 1
            llista.insert(x.num_blocs, x)
        llista.sort(reverse=True)
        print(llista)


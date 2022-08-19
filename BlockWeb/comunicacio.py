import simple_websocket

from BlockWeb import app
from BlockchainUniversity import Factoria, Bloc
from flask import json, request
from CreateMysql import MySqlBloc


def send():
    ws = simple_websocket.Client('ws://192.168.50.28:5005/echo')
    my_db = MySqlBloc('localhost', 'root', 'root', 'blockchainuniversity')
    bloc = Factoria.build_bloc_from_db(my_db, 1)
    try:
        data = bloc
        ws.send(data)
        print(f' {data}')
    except (KeyboardInterrupt, EOFError, simple_websocket.ConnectionClosed):
        ws.close()

import simple_websocket

from BlockchainUniversity import Factoria
from CreateMysql import MySqlBloc


def main():
    ws = simple_websocket.Client('ws://192.168.50.28:5005/echo')
    my_db = MySqlBloc('localhost', 'root', 'root', 'blockchainuniversity')
    bloc = Factoria.build_bloc_from_db(my_db, 1)
    try:
        data = bloc
        ws.send(data)
        print(f' {data}')
    except (KeyboardInterrupt, EOFError, simple_websocket.ConnectionClosed):
        ws.close()


if __name__ == '__main__':
    main()

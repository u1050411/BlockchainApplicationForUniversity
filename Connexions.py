import json
import socket
import socketserver
import sys
from pprint import pprint
import SocketServer

SERVER_IP = '127.0.0.1'  # Nom del Servidor o el seu ip
SERVER_PORT = 50007         # El port que utiliza el servidor
BUFFER_SIZE = 1


class Connexions:

    def __init__(self):
        self.ip = SERVER_IP
        self.port = SERVER_PORT

    def servidor(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((HOST, PORT))
            sock.sendall(bytes(data + "\n"))

            received = str(sock.recv(1024))
        finally:
            # shut down
            sock.close()

        print("Sent:     {}".format(data))
        print("Received: {}".format(received))
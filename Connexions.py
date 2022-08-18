import socket

HOST = '127.0.0.1'  # Nom del Servidor o el seu ip
PORT = 50007         # El port que utiliza el servidor
BUFFER_SIZE = 1


class Connexions:

    def test_server_socket(self):
        data = []
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            while 1:  # Accept connections from multiple clients
                print('Listening for client...')
                conn, addr = s.accept()
                print('Connection address:', addr)
                while 1:  # Accept multiple messages from each client
                    buffer = conn.recv(1)
                    buffer = buffer.decode()
                    if buffer == ";":
                        conn.close()
                        print("Received all the data")
                        for x in data:
                            print(x)
                        break
                    elif buffer:
                        print("received data: ", buffer)
                        data.append(buffer)
                    else:
                        break

        self.test_server_socket()

    def conexio_client(self, dada, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, PORT))
            s.sendall(dada)
            data = s.recv(1024)
        print('Received', repr(data))
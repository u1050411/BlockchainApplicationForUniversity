import mysql.connector


class MySqlBloc:

    def __init__(self):
        self.miConexion = mysql.connector.connect(host='localhost', user='root', passwd='root')
        self.miCursor = self.miConexion.cursor()

    def create_schema(self):
        self.miCursor.execute("CREATE DATABASE blockchainuniversity2")
        self.miConexion = mysql.connector.connect(host='localhost', user='root', passwd='root', db='blockchainuniversity')
        self.miCursor = self.miConexion.cursor()

    def afegir_schema(self, nom):
        self.miConexion = mysql.connector.connect(host='localhost', user='root', passwd='root', db=nom)
        self.miCursor = self.miConexion.cursor()

    def create_tables(self):
        line = ("CREATE TABLE `usuari` ("
                "`id` int NOT NULL,"
                "`public_key` varchar(45) DEFAULT NULL,"
                "`nom` varchar(45) DEFAULT NULL,"
                "PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")

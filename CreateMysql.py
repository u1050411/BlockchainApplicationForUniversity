import mysql.connector
from Crypto.PublicKey import RSA


class MySqlBloc:

    def __init__(self):
        self.miConexio = mysql.connector.connect(host='localhost', user='root', passwd='root')
        self.miCursor = self.miConexio.cursor()

    def create_schema(self, nom):
        line = "CREATE DATABASE " + nom
        self.miCursor.execute(line)
        self.miConexio = mysql.connector.connect(host='localhost', user='root', passwd='root', db=nom)
        self.miCursor = self.miConexio.cursor()

    def afegir_schema(self, nom):
        self.miConexio = mysql.connector.connect(host='localhost', user='root', passwd='root', db=nom)
        self.miCursor = self.miConexio.cursor()

    def executar_sql(self, columnes, dades):
        self.miCursor.execute(columnes, dades)
        self.miConexio.commit()

    def select_sql(self, sql):
        self.miCursor.execute(sql)

    def exportar_sql(self, sql):
        self.miCursor.execute(sql)
        self.miConexio.commit()

    def importar_sql(self, sql):
        self.miCursor.execute(sql)

    def tancar(self):
        self.miCursor.close()
        self.miConexio.close()

    # Retorna si existeix la dada a la db
    def existeix(self, taula, columna, dada):
        sql = f'select {columna} from {taula} where {columna} = {dada} LIMIT 1'
        self.afegir_schema('blockchainuniversity')
        self.select_sql(sql)
        return self.miCursor.fetchone() is not None

    def clau_privada(self, id_usuari):
        sql = f'select private_key from private_key where id_usuari = {id_usuari} LIMIT 1'
        self.importar_sql(sql)
        clau_string = self.miCursor.fetchone()[0]
        return RSA.importKey(clau_string)

    def clau_publica(self, id_usuari):
        sql = f'select public_key from public_key where id_usuari = {id_usuari} LIMIT 1'
        self.importar_sql(sql)
        clau_string = self.miCursor.fetchone()[0]
        return RSA.importKey(clau_string)


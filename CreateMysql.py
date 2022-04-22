import mysql.connector


class MySqlBloc:

    def __init__(self):
        self.miConexio = mysql.connector.connect(host='localhost', user='root', passwd='root')
        self.miCursor = self.miConexio.cursor()

    def create_schema(self, nom):
        line = "CREATE DATABASE "+nom
        self.miCursor.execute(line)
        self.miConexio = mysql.connector.connect(host='localhost', user='root', passwd='root', db=nom)
        self.miCursor = self.miConexio.cursor()

    def afegir_schema(self, nom):
        self.miConexio = mysql.connector.connect(host='localhost', user='root', passwd='root', db=nom)
        self.miCursor = self.miConexio.cursor()

    # def executar_sql(self, columnes, dades):
    #     self.miCursor.execute(columnes, dades)
    #     self.miConexio.commit()

    def exportar_sql(self, sql):
        self.miCursor.execute(sql)
        self.miConexio.commit()

    def importar_sql(self, sql):
        self.miCursor.execute(sql)

    def tancar(self):
        self.miCursor.close()
        self.miConexio.close()

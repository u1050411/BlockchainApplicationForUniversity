import base64
from datetime import datetime

import mysql.connector
from Crypto.PublicKey import RSA
from mysql.connector import errorcode

# from BlockchainUniversity import Usuari

UTF_8 = 'utf8'
ESTUDIANT = 'estudiant'
PROFESSOR = 'professor'


class MySqlBloc:

    def __init__(self, ip=None, usuari=None, password=None):
        try:
            self._conexio = mysql.connector.connect(host=ip, user=usuari, passwd=password)
            self._cursor = self._conexio.cursor()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Hi ha un error en l'intent de conexio")
            else:
                print(err)
            exit(1)

    @property
    def conexio(self):
        return self._conexio

    @property
    def schema(self):
        sql = f'SELECT DATABASE() FROM DUAL'
        return self.importar_sql(sql)[0]

    @conexio.setter
    def conexio(self, conexio):
        self._conexio = conexio

    @property
    def cursor(self):
        return self._cursor

    @conexio.setter
    def cursor(self, cursor):
        self._cursor = cursor

    def afegir_schema(self, schema):
        try:
            self.conexio.database = schema
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database no existeix")
            else:
                print(err)
            exit(1)

    def crear_schema(self, schema):
        if not self.existeix(schema, None, None, None):
            try:
                line = "CREATE DATABASE " + schema
                self._cursor.execute(line)
                self.afegir_schema(schema)
            except mysql.connector.Error as err:
                print("Error al crear la base de dades : {}".format(err))
                exit(1)

    def select_sql(self, sql):
        try:
            self._cursor.execute(sql)
        except mysql.connector.Error as err:
            print("Error Mysql : {}".format(err))
            exit(1)

    def exportar_sql(self, sql):
        try:
            self._cursor.execute(sql)
            self._conexio.commit()
        except mysql.connector.Error as err:
            print("Error Mysql : {}".format(err))
            exit(1)

    def importar_llista_sql(self, sql):
        try:
            self._cursor.execute(sql)
        except mysql.connector.Error as err:
            print("Error Mysql : {}".format(err))
            exit(1)
        return self._cursor.fetchall()

    def importar_estudiants_examen(self, id_document):
        sql = f'select `id_estudiant` from `estudiant_examen` where `id_document` = {id_document}'
        return self.importar_llista_sql(sql)

    def importar_respostes(self, id_document):
        sql = f'select id_resposta, data_creacio, id_usuari, pdf  ' \
               f'from `resposta_examen` where `id_document` = {id_document}'
        return self.importar_llista_sql(sql)

    def importar_sql(self, sql):
        llista = self.importar_llista_sql(sql)
        return llista[0]

    def importar_usuari(self, id_usuari):
        sql = f'select * from usuari where id = {id_usuari} LIMIT 1'
        return self.importar_sql(sql)

    def importar_examen(self, id_document):
        sql = f'select `id_document`, `id_professor`, `data_examen`, `data_inici`, `data_final`, `pdf`, `nota`  ' \
              f'from `examen` where `id_document` = {id_document} LIMIT 1'
        return self.importar_sql(sql)

    def esborrar_schema(self, schema):
        if self.existeix(schema, None, None, None):
            sql = f"DROP DATABASE `{schema}`"
            self.exportar_sql(sql)

    def tancar(self):
        try:
            self._cursor.close()
            self._conexio.close()
        except mysql.connector.Error as err:
            print(err)
            exit(1)

    # Retorna si existeix la dada
    def existeix(self, schema, taula, columna, dada):
        if taula is None:
            sql = f"SHOW DATABASES like '{schema}'"
        else:
            self.afegir_schema(schema)
            if columna is None:
                sql = f"SHOW TABLES like '{taula}'"
            elif dada is None:
                sql = f"SHOW COLUMNS FROM {taula} WHERE Field = '{columna}'"
            else:
                sql = f"select `{columna}` from `{taula}` where `{columna}` = '{dada}' LIMIT 1"
        self.select_sql(sql)
        return self._cursor.fetchone() is not None

    def existeix_usuari(self, id_usuari):
        return self.existeix(self.schema, 'usuari', 'id', id_usuari)

    def existeix_examen(self, id_document):
        return self.existeix('BlockchainUniversity', 'examen', 'id_document', id_document)

    def seguent_id_examen(self):
        sql = f"select Max(`id_document`) from `examen`"
        num_maxim = self.importar_sql(sql)[0]
        # id_document, tipus = self.dades_num(num_maxim)
        return num_maxim + 1

    def seguent_id_resposta(self, id_document):
        sql = f"select Max(`id_resposta`) from `resposta_examen` where `id_document` = {id_document}"
        num_maxim = self.importar_sql(sql)[0]
        if num_maxim is None:
            id_document = 0
        else:
            id_document, tipus = self.dades_num(num_maxim)
        return id_document + 1

    def clau_privada(self, id_usuari):
        sql = f'select `private_key` from `blockchainuniversity`.`private_key` where `id_usuari` = {id_usuari} LIMIT 1'
        clau_string = self.importar_sql(sql)
        return RSA.importKey(clau_string[0])

    def clau_publica(self, id_usuari):
        sql = f'select `public_key` from `blockchainuniversity`.`public_key` where `id_usuari` = {id_usuari} LIMIT 1'
        clau_string = self.importar_sql(sql)
        return RSA.importKey(clau_string[0])

    # Aquest Metode es per fer mes facils els test - No anira codi final
    def guardar_clau_privada(self, id_usuari, private_key):
        sql = f'INSERT INTO private_key (`id_usuari`, `private_key`) VALUES({id_usuari}, "{private_key}")'
        self.exportar_sql(sql)

    def guardar_clau_publica(self, id_usuari, public_key):
        sql = f'INSERT INTO public_key (`id_usuari`, `public_key`) VALUES({id_usuari}, "{public_key}")'
        self.exportar_sql(sql)

    def guardar_usuari(self, id_usuari, nif, nom, cognom):
        sql = f'INSERT INTO usuari (`id`, `nif`, `nom`, `cognom`) VALUES({id_usuari}, "{nif}", "{nom}", "{cognom}")'
        self.exportar_sql(sql)
        key = RSA.generate(1024)
        private_key = key.exportKey('PEM').decode('ascii')
        public_key = key.publickey()
        string_key = public_key.exportKey('PEM').decode('ascii')
        sql = f'INSERT INTO private_key (`id_usuari`, `private_key`) VALUES({id_usuari}, "{private_key}")'
        self.exportar_sql(sql)
        sql = f'INSERT INTO public_key (`id_usuari`, `public_key`) VALUES({id_usuari}, "{string_key}")'
        self.exportar_sql(sql)

    @staticmethod
    def dades_num(num_document):
        num_document = str(num_document)
        id_document = int(num_document[0:-4])
        id_tipus = int(num_document[-4:])
        return [id_document, id_tipus]

    @staticmethod
    def recuperar_fitxer(nom_fitxer):
        pdf_file = open(nom_fitxer, "rb")
        save_pdf = base64.b64encode(pdf_file.read())
        pdf_file.close()
        return save_pdf

    def guardar_examen(self, examen):
        id_document, id_tipus = self.dades_num(examen.id_document)
        if id_tipus == 1:
            id_usuari = examen.professor.id
            data_examen = examen.data_creacio
            data_inici = examen.data_inicial
            data_final = examen.data_final
            save_pdf = examen.pdf
            estudiants = examen.estudiants

            sql = f'INSERT INTO examen (`id_document`, `id_professor`, `data_examen`, `data_inici`, `data_final`, ' \
                  f'`pdf`) VALUES({id_document}, {id_usuari}, "{data_examen}", "{data_inici}", "{data_final}", ' \
                  f'"{save_pdf}")'
            self.exportar_sql(sql)

            for estudiant in estudiants:
                sql = f'INSERT INTO estudiant_examen (`id_document`, `id_estudiant`) ' \
                      f'VALUES({id_document}, "{estudiant.id}")'
                self.exportar_sql(sql)

    def guardar_resposta_examen(self, id_document, resposta):
        document, tipus = self.dades_num(id_document)
        if tipus == 1:
            sql = f'INSERT INTO resposta_examen (`id_document`, `id_resposta`, `data_creacio`, `id_usuari`, `pdf`) ' \
                  f'VALUES({id_document}, {resposta.id_resposta}, "{resposta.data_creacio}", ' \
                  f'"{resposta.usuari.id}","{resposta.pdf}")'
            self.exportar_sql(sql)


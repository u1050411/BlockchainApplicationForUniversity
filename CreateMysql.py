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
               f'from `resposta_examen` where `id_examen` = {id_document}'
        return self.importar_llista_sql(sql)

    def importar_resposta(self, id_document, id_resposta):
        sql = f'select id_resposta, data_creacio, id_usuari, pdf  from `resposta_examen` ' \
              f'where `id_examen` = {id_document} and `id_resposta` = {id_resposta}'
        return self.importar_llista_sql(sql)

    def importar_sql(self, sql):
        llista = self.importar_llista_sql(sql)
        return llista[0]

    def importar_usuari(self, id_usuari):
        sql = f'select * from usuari where id = {id_usuari} LIMIT 1'
        return self.importar_sql(sql)

    # def importar_usuari2(self, id_usuari):
    #     sql = f'select `usuari`  from `usuari_json` where id = {id_usuari} LIMIT 1'
    #     return self.importar_sql(sql)[0]

    def importar_examen(self, id_document):
        sql = f'select `id_document`, `id_professor`, `data_examen`, `data_inici`, `data_final`, `pdf` ' \
              f'from `examen` where `id_document` = {id_document} LIMIT 1'
        return self.importar_sql(sql)

    def importar_transaccions(self):
        sql = f'select MIN(id_transaccio), id_emissor, id_receptor, clau, document, data_creacio from `transaccio` ' \
              f'LIMIT 1'
        return self.importar_sql(sql)

    # def importar_transaccio(self):
    #     sql = f'select `id_document`, `id_professor`, `data_examen`, `data_inici`, `data_final`, `pdf` ' \
    #           f'from `examen` where `id_document` = {id_document} LIMIT 1'
    #     return self.importar_sql(sql)

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

    def seguent_id(self, taula, columna):
        sql = f"select Max(`{columna}`) from `{taula}`"
        num_maxim = self.importar_sql(sql)[0]
        if num_maxim is None:
            id_document = 0
        else:
            id_document = num_maxim + 1
        return id_document

    def seguent_id_examen(self):
        return self.seguent_id("examen", "id_document")

    def seguent_id_resposta(self):
        return self.seguent_id("resposta_examen", "id_resposta")

    def seguent_id_bloc(self):
        return self.seguent_id("bloc", "id_bloc")

    def clau_privada(self, id_usuari):
        sql = f'select `private_key` from `blockchainuniversity`.`private_key` where `id_usuari` = {id_usuari} LIMIT 1'
        clau_string = self.importar_sql(sql)
        return RSA.importKey(clau_string[0])

    # def clau_publica(self, id_usuari):
    #     sql = f'select `public_key` from `blockchainuniversity`.`public_key` where `id_usuari` = {id_usuari} LIMIT 1'
    #     clau_string = self.importar_sql(sql)
    #     return RSA.importKey(clau_string[0])

    # Aquest Metode es per fer mes facils els test - No anira codi final
    def guardar_clau_privada(self, id_usuari, private_key):
        private = private_key.exportKey('PEM').decode('ascii')
        sql = f'INSERT INTO private_key (`id_usuari`, `private_key`) VALUES({id_usuari}, "{private}")'
        self.exportar_sql(sql)

    # def guardar_clau_publica(self, id_usuari, public_key):
    #     sql = f'INSERT INTO public_key (`id_usuari`, `public_key`) VALUES({id_usuari}, "{public_key}")'
    #     self.exportar_sql(sql)

    def guardar_usuari(self, usuari):
        sql = f'INSERT INTO usuari (`id`, `tipus`, `nif`, `nom`, `cognom`, `public_key`) VALUES({usuari.id}, ' \
              f'"{usuari.tipus}", "{usuari.nif}", "{usuari.nom}", "{usuari.cognom}", "{usuari.str_publickey()}")'
        self.exportar_sql(sql)

    def guardar_bloc(self, id_bloc, time, id_emissor, id_receptor, id_document, transaccio, hash_block):
        sql = f'INSERT INTO usuari (`id_bloc`, `time`, `id_emissor`, `id_receptor`,`id_document`, `transaccio`, ' \
              f'`hash`) VALUES({id_bloc}, "{time}", "{id_emissor}", "{id_receptor}",{id_document}, "{transaccio}", ' \
              f'"{hash_block}")'
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
        id_document = examen.id_document
        id_usuari = examen.usuari.id
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

    def guardar_resposta_examen(self, resposta):
        sql = f'INSERT INTO resposta_examen (`id_examen`, `id_resposta`, `data_creacio`, `id_usuari`, `pdf`) ' \
              f'VALUES({resposta.id_examen}, {resposta.id_document}, "{resposta.data_creacio}", ' \
              f'"{resposta.usuari.id}","{resposta.pdf}")'
        self.exportar_sql(sql)

    def guardar_transaccio(self, transaccio):
        sql = f'INSERT INTO transaccio (`id_emissor`, `id_receptor`, `clau`, `document`, `data_creacio`) ' \
              f'VALUES({transaccio.emissor.id}, {transaccio.receptor.id},"{transaccio.clau}", ' \
              f'"{transaccio.document}", "{transaccio.data_creacio}")'
        self.exportar_sql(sql)

    # def guardar_trans(self, transaccio):
    #     sql = f'INSERT INTO trans_prova (`transaccio`) ' \
    #           f'VALUES({transaccio})'
    #     self.exportar_sql(sql)

    # f'VALUES({transaccio.emissor.id}, {transaccio.receptor.id},"{transaccio.clau}", "", ' \




import base64
from datetime import datetime

import mysql.connector
from Crypto.PublicKey import RSA
from mysql.connector import errorcode, cursor

# from BlockchainUniversity import Usuari
from BlockchainUniversity import Factoria

UTF_8 = 'utf8'
ESTUDIANT = 'estudiant'
PROFESSOR = 'professor'


class MySqlBloc:

    def __init__(self, ip=None, usuari=None, password=None, db=None):
        try:
            self._conexio = mysql.connector.connect(host=ip, user=usuari, passwd=password, database=db)
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

    def crear_taules_inicials(self):
        sqls = ["CREATE TABLE if not exists `usuari` ("
                "`id`  varchar(8) NOT NULL,"
                "`tipus` varchar(9) NOT NULL,"
                "`nif` varchar(9) NOT NULL,"
                "`nom` varchar(45) DEFAULT NULL,"
                "`cognom` varchar(100) DEFAULT NULL,"
                "`public_key` longtext NULL,"
                "`contrasenya` longtext NULL,"
                "`email` varchar(45) DEFAULT NULL,"
                "PRIMARY KEY (`id`)) ",

                "CREATE TABLE if not exists `private_key` ("
                "`id_usuari`  varchar(8) NOT NULL,"
                "`private_key` longtext NULL,"
                "PRIMARY KEY (`id_usuari`))",

                "CREATE TABLE if not exists `transaccio` ("
                "`id_transaccio` INT NOT NULL AUTO_INCREMENT,"
                "`id_emissor` varchar(8) NOT NULL,"
                "`id_receptor` varchar(8) NOT NULL,"
                "`document` JSON NOT NULL ,"
                "`id_document` INT NOT NULL ,"
                "`data_creacio` DATETIME NOT NULL ,"
                "PRIMARY KEY(`id_transaccio`))",

                "CREATE TABLE if not exists `examen` ("
                "`id_document` INT NOT NULL AUTO_INCREMENT,"
                "`id_professor`  varchar(8) NOT NULL,"
                "`data_examen` DATETIME NOT NULL,"
                "`data_inici` DATETIME NULL,"
                "`data_final` DATETIME NULL,"
                "`pdf` LONGBLOB  NULL,"
                "PRIMARY KEY (`id_document`))",

                "CREATE TABLE if not exists `estudiant_examen` ("
                "`id_document` INT NOT NULL,"
                "`id_estudiant`  varchar(8) NOT NULL,"
                "`nota` INT NULL,"
                "PRIMARY KEY (`id_document`, `id_estudiant`))",

                "CREATE TABLE if not exists `estudiants_professor` ("
                "`id_professor`  varchar(8) NOT NULL,"
                "`id_estudiant`  varchar(8) NOT NULL,"
                "`nota` INT NULL,"
                "PRIMARY KEY (`id_professor`, `id_estudiant`))",

                "CREATE TABLE if not exists `resposta_examen` ("
                "`id_resposta` INT NOT NULL AUTO_INCREMENT,"
                "`id_examen` INT NOT NULL,"
                "`data_creacio` DATETIME NOT NULL,"
                "`id_usuari` varchar(8) NOT NULL,"
                "`pdf` LONGBLOB  NULL,"
                "PRIMARY KEY (`id_resposta`))",

                "CREATE TABLE if not exists `bloc` ("
                "`id_bloc` INT NOT NULL AUTO_INCREMENT,"
                "`data_bloc` DATETIME NOT NULL,"
                # "`id_emissor` INT NOT NULL,"
                # "`id_receptor` INT NOT NULL,"
                # "`id_document` INT NOT NULL,"
                "`transaccio` JSON  NOT NULL,"
                "`hash_bloc_anterior` LONGBLOB  NOT NULL,"
                "PRIMARY KEY (`id_bloc`))",

                "CREATE TABLE if not exists `Universitat` ("
                "`id` INT NOT NULL AUTO_INCREMENT,"
                "`nom` TEXT NOT NULL,"
                "`private_key` longtext NULL,"
                "`public_key` longtext NULL,"
                "PRIMARY KEY (`id`))",
                ]

        for sql in sqls:
            self.exportar_sql(sql)

    def borrar_dades_taula(self, schema, taula):
        sql = f'TRUNCATE TABLE {schema}.{taula}'
        self.select_sql(sql)

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

    def exportar_sql(self, sql, values=None):
        try:
            self._cursor.execute(sql, values)
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

    def importar_llista_enter_sql(self, sql):
        try:
            self._cursor.execute(sql)
            llista = list()
            punter = self._cursor.fetchone()
            while None != punter:
                llista.append(punter[0])
                punter = self._cursor.fetchone()
            return llista

        except mysql.connector.Error as err:
            print("Error Mysql : {}".format(err))
            exit(1)
        return self._cursor.fetchall()


    def importar_estudiants_examen(self, id_document):
        sql = f'select `id_estudiant` from `estudiant_examen` where `id_document` = {id_document}'
        return self.importar_llista_sql(sql)

    def importar_estudiants_examen(self, id_document):
        sql = f'select `id_estudiant` from `estudiant_examen` where `id_document` = {id_document}'
        return self.importar_llista_sql(sql)

    def importar_estudiants_professor(self, professor):
        sql = f'select id from `usuari` where `id` in (select id_estudiant from estudiants_professor where id_professor = "{professor.id}");'
        return self.importar_llista_enter_sql(sql)

    def importar_respostes(self, id_document):
        sql = f'select id_resposta, data_creacio, id_usuari, pdf  ' \
              f'from `resposta_examen` where `id_examen` = {id_document}'
        return self.importar_llista_sql(sql)

    def importar_resposta(self, id_document, id_resposta):
        sql = f'select id_resposta, data_creacio, id_usuari, pdf  from `resposta_examen` ' \
              f'where `id_examen` = {id_document} and `id_resposta` = {id_resposta}'
        return self.importar_llista_sql(sql)

    def importar_sql(self, sql):
        try:
            self._cursor.execute(sql)
        except mysql.connector.Error as err:
            print("Error Mysql : {}".format(err))
            exit(1)
        return self._cursor.fetchone()

    def importar_usuari(self, id_usuari):
        sql = f'select `id`,`tipus`,`nif`,`nom`,`cognom`,`public_key`,`contrasenya` , `email` ' \
              f'from usuari where id = "{id_usuari}" LIMIT 1'
        return self.importar_sql(sql)

    def importar_examen(self, id_document):
        sql = f'select `id_document`, `id_professor`, `data_examen`, `data_inici`, `data_final`, `pdf` ' \
              f'from `examen` where `id_document` = {id_document} LIMIT 1'
        return self.importar_sql(sql)

    def importar_transaccions(self):
        sql = f'select id_transaccio, id_emissor, id_receptor, document, id_document, data_creacio from `transaccio` ' \
              f'LIMIT 1'
        return self.importar_sql(sql)

    def importar_universitat(self):
        sql = f'select * from universitat LIMIT 1'
        return self.importar_sql(sql)

    def importar_bloc(self, id_bloc):
        sql = f'select id_bloc, data_transaccio, id_emissor, id_receptor, id_document, transaccio, hash_bloc_anterior ' \
              f'from `bloc` where `id_bloc` = {id_bloc} LIMIT 1'
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
        return self.existeix(self.schema, 'examen', 'id_document', id_document)

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
        sql = f'select `private_key` from `private_key` where `id_usuari` = "{id_usuari}" LIMIT 1'
        clau_string = self.importar_sql(sql)
        return RSA.importKey(clau_string[0])

    def guardar_clau_privada(self, id_usuari, private_key):
        private = private_key.exportKey('PEM').decode('ascii')
        sql = "INSERT INTO private_key(id_usuari, private_key) VALUES (%s, %s)"
        dades = (id_usuari, private)
        self.exportar_sql(sql, dades)

    def guardar_universitat(self, universitat):
        private = universitat.private_key.exportKey('PEM').decode('ascii')
        public = universitat.public_key.exportKey('PEM').decode('ascii')
        nom = universitat.nom
        sql = "INSERT INTO universitat(nom, public_key, private_key) VALUES (%s, %s, %s)"
        dades = (nom, public, private)
        self.exportar_sql(sql, dades)

    def guardar_usuari(self, usuari):
        sql = "INSERT INTO usuari(id, tipus, nif, nom, cognom, public_key, contrasenya, email) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        dades = (usuari.id, usuari.tipus, usuari.nif, usuari.nom, usuari.cognom, usuari.str_publickey(),
                 usuari.contrasenya, usuari.email)
        self.exportar_sql(sql, dades)

    def guardar_estudiants_professor(self, professor, estudiant):
        sql = "INSERT INTO estudiants_professor(id_professor, id_estudiant) VALUES (%s, %s)"
        dades = (professor.id, estudiant.id)
        self.exportar_sql(sql, dades)

    def guardar_bloc(self, bloc):
        ultim = self.ultim_bloc()
        if ultim is None:
            id = 0
        else:
            id = ultim.id_bloc
        sql = "INSERT INTO bloc (`id_bloc`,`data_bloc`, `transaccio`,`hash_bloc_anterior`) VALUES (%s, %s, %s, %s)"
        dades = (id, bloc.data_bloc, Factoria.to_json(bloc.transaccio), bloc.hash_bloc_anterior)
        self.exportar_sql(sql, dades)


    def ultim_bloc(self):
        sql = "SELECT MAX(id_bloc) FROM bloc"
        id_bloc = self.importar_sql(sql)[0]
        if id_bloc is None:
            return None
        return self.importar_bloc(id_bloc)

    @staticmethod
    def dades_num(num_document):
        num_document = str(num_document)
        id_document = int(num_document[0:-4])
        id_tipus = int(num_document[-4:])
        return [id_document, id_tipus]

    def guardar_examen(self, examen):
        id_document = examen.id_document
        id_usuari = examen.usuari.id
        data_examen = examen.data_creacio
        data_inici = examen.data_inicial
        data_final = examen.data_final
        save_pdf = examen.pdf
        estudiants = examen.estudiants

        sql = "INSERT INTO examen(id_document, id_professor, data_examen, data_inici, data_final, pdf) " \
              "VALUES (%s, %s, %s, %s, %s, %s)"
        dades = (id_document, id_usuari, data_examen, data_inici, data_final, save_pdf)
        self.exportar_sql(sql, dades)

        for estudiant in estudiants:
            sql = "INSERT INTO estudiant_examen(id_document, id_estudiant) VALUES (%s, %s)"
            dades = (id_document, estudiant.id)
            self.exportar_sql(sql, dades)

    def guardar_resposta_examen(self, resposta):
        sql = "INSERT INTO resposta_examen(id_examen, id_resposta, data_creacio, id_usuari, pdf) " \
              "VALUES (%s, %s, %s, %s, %s)"
        dades = (resposta.id_examen, resposta.id_document, resposta.data_creacio, resposta.usuari.id, resposta.pdf)
        self.exportar_sql(sql, dades)

    def guardar_transaccio(self, transaccio):
        encrip_to_json = Factoria.to_json(transaccio.document)
        sql = "INSERT INTO transaccio(id_emissor, id_receptor, document, id_document, data_creacio) " \
              "VALUES (%s, %s, %s, %s, %s)"
        dades = (transaccio.emissor.id, transaccio.receptor.id, encrip_to_json,
                 transaccio.id_document, transaccio.data_creacio,)
        self.exportar_sql(sql, dades)

import mysql.connector
from Crypto.PublicKey import RSA
from mysql.connector import errorcode


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

                "CREATE TABLE if not exists `pdf` ("
                "`id_pdf` INT NOT NULL,"
                "`data_creacio` DATETIME NOT NULL,"
                "`id_usuari` varchar(8) NOT NULL,"
                "`nom_fitxer` varchar(200) NOT NULL,"
                "`pdf` LONGBLOB  NULL,"
                "PRIMARY KEY (`id_pdf`))",

                "CREATE TABLE if not exists `examen` ("
                "`id_document` INT NOT NULL AUTO_INCREMENT,"
                "`id_professor`  varchar(8) NOT NULL,"
                "`id_assignatura`  INT NOT NULL,"
                "`data_examen` DATETIME NOT NULL,"
                "`data_inici` DATETIME NULL,"
                "`data_final` DATETIME NULL,"
                "`pdf` LONGBLOB  NULL,"
                "PRIMARY KEY (`id_document`))",

                "CREATE TABLE if not exists `hash_bloc_usuari` ("
                "`id_bloc` INT NOT NULL,"
                "`id_emissor`  varchar(8) NOT NULL,"
                "`hash_bloc` LONGBLOB  NULL,"
                "PRIMARY KEY (`id_bloc`))",

                "CREATE TABLE if not exists `estudiant_examen` ("
                "`id_document` INT NOT NULL,"
                "`id_estudiant`  varchar(8) NOT NULL,"
                "`nota` float(4,2) NULL,"
                "PRIMARY KEY (`id_document`, `id_estudiant`))",

                "CREATE TABLE if not exists `assignatura` ("
                "`id_assignatura` INT NOT NULL AUTO_INCREMENT,"
                "`nom`  varchar(50) NOT NULL,"
                "`id_professor` varchar(8) NOT NULL,"
                "PRIMARY KEY (`id_assignatura`))",

                "CREATE TABLE if not exists `estudiants_assignatura` ("
                "`id_assignatura`  varchar(8) NOT NULL,"
                "`id_estudiant`  varchar(8) NOT NULL,"
                "`nota` float(4,2) NULL,"
                "PRIMARY KEY (`id_assignatura`, `id_estudiant`))",

                "CREATE TABLE if not exists `resposta_examen` ("
                "`id_resposta` INT NOT NULL AUTO_INCREMENT,"
                "`examen` INT NOT NULL,"
                "`data_creacio` DATETIME NOT NULL,"
                "`id_usuari` varchar(8) NOT NULL,"
                "`pdf` LONGBLOB  NULL,"
                "`nota` INT NULL,"
                "PRIMARY KEY (`id_resposta`))",

                "CREATE TABLE if not exists avaluacio_examen ("
                "`id_avaluacio` INT NOT NULL AUTO_INCREMENT,"
                "`id_resposta` INT NOT NULL,"
                "`id_professor` varchar(8) NOT NULL,"
                "`id_estudiant` varchar(8) NOT NULL,"
                "`pdf` LONGBLOB  NULL,"
                "`nota` float(4,2) NULL,"
                "PRIMARY KEY (`id_avaluacio`))",

                "CREATE TABLE if not exists `bloc` ("
                "`id_bloc` INT NOT NULL AUTO_INCREMENT,"
                "`data_bloc` DATETIME NOT NULL,"
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

    # def importar_estudiants_examen(self, id_document: object) -> object:
    #     sql = f'select `id_estudiant` from `estudiant_examen` where `id_document` = {id_document}'
    #     return self.importar_llista_sql(sql)

    def importar_estudiants_professor(self, professor):
        sql = f'select id_estudiant from `estudiants_assignatura` where `id_assignatura` in (select id_assignatura from assignatura ' \
              f'where id_professor = "{professor.id}")'
        return self.importar_llista_enter_sql(sql)

    def importar_examens_estudiant(self, usuari):
        sql = f'select `id_document`, `id_professor`, `data_inici`, `data_final`' \
              f'from `examen` where `id_document` in (select `id_document` from `estudiant_examen` ' \
              f'where `id_estudiant` = "{usuari.id}")'
        return self.importar_llista_sql(sql)

    def importar_examens_professor(self, professor):
        sql = f'select `id_document`, `id_professor`, `data_examen`, `data_inici`, `data_final`, `pdf` ' \
              f'from `examen` where `id_professor` = "{professor.id}"'
        return self.importar_llista_enter_sql(sql)

    def importar_id_respostes_professor(self, professor):
        sql = f'SELECT id_resposta FROM blockchainuniversity.resposta_examen where  examen in ' \
              f'(SELECT id_document FROM blockchainuniversity.examen where id_assignatura in ' \
              f'(SELECT id_assignatura FROM blockchainuniversity.assignatura where id_professor= "{professor.id}"))'
        return self.importar_llista_enter_sql(sql)

    def importar_respostes(self, id_document):
        sql = f'select id_resposta, data_creacio, id_usuari, pdf  ' \
              f'from `resposta_examen` where `examen` = {id_document}'
        return self.importar_llista_sql(sql)

    def importar_pdf(self, id_pdf):
        sql = f'select id_pdf, data_creacio, id_usuari, pdf, nom_fitxer ' \
              f'from `pdf` where `id_pdf` ={id_pdf}'
        return self.importar_sql(sql)

    def importar_pdf_usuari(self, usuari):
        sql = f'select id_pdf from pdf where `id_usuari` = "{usuari.id}"'
        return self.importar_llista_sql(sql)

    def importar_resposta(self, id_document, id_resposta):
        sql = f'select id_resposta, data_creacio, id_usuari, pdf  from `resposta_examen` ' \
              f'where `examen` = {id_document} and `id_resposta` = {id_resposta}'
        return self.importar_llista_sql(sql)

    def importar_resposta(self, id_resposta):
        sql = f'select id_resposta, examen, data_creacio, id_usuari, pdf, nota  from `resposta_examen` ' \
              f'where `id_resposta` = {id_resposta}'
        return self.importar_llista_sql(sql)

    def importar_avaluacio(self, id_avaluacio):
        sql = f'select id_avaluacio, id_resposta, id_professor, id_estudiant, pdf, nota  from `avaluacio_examen` ' \
              f'where `id_avaluacio` = {id_avaluacio}'
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
        sql = f'select `id_document`, `id_professor`, `data_examen`, `data_inici`, `data_final`, `pdf`, `id_assignatura` ' \
              f'from `examen` where `id_document` = {id_document} LIMIT 1'
        return self.importar_sql(sql)

    def importar_transaccions(self):
        sql = f'select id_transaccio, id_emissor, id_receptor, document, id_document, data_creacio from `transaccio` ' \
              f'LIMIT 1'
        return self.importar_sql(sql)

    def importar_universitat(self):
        sql = f'select * from universitat LIMIT 1'
        return self.importar_sql(sql)

    def importar_assignatura(self, id_assign):
        sql = f'select * from assignatura where `id_assignatura` = {id_assign} LIMIT 1'
        return self.importar_sql(sql)

    def importar_assignatura_professor(self, professor):
        sql = f'select * from assignatura where `id_professor` = "{professor.id}" LIMIT 1'
        return self.importar_sql(sql)

    def importar_bloc(self, id_bloc):
        sql = f'select id_bloc, data_bloc, transaccio, hash_bloc_anterior ' \
              f'from `bloc` where `id_bloc` = {id_bloc} LIMIT 1'
        return self.importar_sql(sql)

    def esborrar_schema(self, schema):
        if self.existeix(schema, None, None, None):
            sql = f"DROP DATABASE `{schema}`"
            self.exportar_sql(sql)

    def esborrar_taula(self, taula):
        if self.existeix(self.schema, taula, None, None):
            sql = f'TRUNCATE TABLE `{self.schema}`.{taula}'
            self.exportar_sql(sql)

    def esborrar_dada(self, taula, columna, dada):
        if self.existeix(self.schema, taula, columna, dada):
            sql = f"DELETE FROM `{self.schema}`.`{taula}` WHERE `{columna}` = {dada}"
            self.exportar_sql(sql)

    def esborrar_transaccio(self, id_transac):
        self.esborrar_dada("transaccio", "id_transaccio", id_transac)

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

    def existeix_resposta(self, id_resposta):
        return self.existeix(self.schema, 'resposta_examen', 'id_resposta', id_resposta)

    def existeix_avaluacio(self, id_avaluacio):
        return self.existeix(self.schema, 'avaluacio_examen', 'id_avaluacio', id_avaluacio)

    def existeix_resposta_alumne(self, id_examen, id_usuari):
        sql = f"select `id_usuari` from `resposta_examen` where `examen` = '{id_examen}' " \
              f"and `id_usuari` = '{id_usuari}' LIMIT 1"
        self.select_sql(sql)
        return self._cursor.fetchone() is not None

    def existeix_examen_alumne(self, id_document, id_estudiant):
        sql = f"select `id_estudiant` from `estudiant_examen` where `id_document` = '{id_document}' " \
              f"and `id_estudiant` = '{id_estudiant}' LIMIT 1"
        self.select_sql(sql)
        return self._cursor.fetchone() is not None

    def existeix_alumnes_examen(self, id_usuari):
        return self.existeix(self.schema, 'usuari', 'id', id_usuari)

    #
    # def existeix_transaccio(self, id_transac):
    #     return self.existeix(self.schema, 'transaccio', 'id_transaccio', id_transac)

    def existeix_alguna_transaccio(self):
        num = self.seguent_id('transaccio', 'id_transaccio')
        return num != 1

    def seguent_id(self, taula, columna):
        sql = f"select Max(`{columna}`) from `{taula}`"
        num_maxim = self.importar_sql(sql)[0]
        if num_maxim is None:
            id_document = 1
        else:
            id_document = num_maxim + 1
        return id_document

    def seguent_id_examen(self):
        return self.seguent_id("examen", "id_document")

    def seguent_id_resposta(self):
        return self.seguent_id("resposta_examen", "id_resposta")

    def seguent_id_avaluacio(self):
        return self.seguent_id("avaluacio_examen", "id_avaluacio")

    def seguent_id_bloc(self):
        return self.seguent_id("bloc", "id_bloc")

    def seguent_id_pdf(self):
        return self.seguent_id("pdf", "id_pdf")

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
        id = universitat.id
        if id == 1:
            private = universitat.private_key.exportKey('PEM').decode('ascii')
        else:
            private = None
        public = universitat.public_key.exportKey('PEM').decode('ascii')
        nom = universitat.nom
        sql = "INSERT INTO universitat(id, nom, public_key, private_key) VALUES (%s, %s, %s, %s)"
        dades = (id, nom, public, private)
        self.exportar_sql(sql, dades)

    def guardar_assignatura(self, assignatura):
        sql = "INSERT INTO assignatura(nom, id_professor) " \
              "VALUES (%s, %s)"
        dades = (assignatura.nom, assignatura.professor.id)
        self.exportar_sql(sql, dades)

    def guardar_usuari(self, usuari):
        sql = "INSERT INTO usuari(id, tipus, nif, nom, cognom, public_key, contrasenya, email) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        dades = (usuari.id, usuari.tipus, usuari.nif, usuari.nom, usuari.cognom, usuari.str_publickey(),
                 usuari.contrasenya, usuari.email)
        self.exportar_sql(sql, dades)

    def guardar_estudiants_assignatura(self, assignatura, estudiant):
        sql = "INSERT INTO estudiants_assignatura(id_assignatura, id_estudiant) VALUES (%s, %s)"
        dades = (assignatura.id, estudiant.id)
        self.exportar_sql(sql, dades)

    def guardar_bloc_dades(self, bloc):
        sql = "INSERT INTO bloc (`id_bloc`,`transaccio`,`data_bloc`,`hash_bloc_anterior`) VALUES (%s, %s, %s, %s)"
        dades = (bloc.id, bloc.transaccio, bloc.data_bloc, bloc.hash_bloc_anterior)
        self.exportar_sql(sql, dades)

    def guardar_bloc_usuari(self, bloc, emissor):
        sql = "INSERT INTO hash_bloc_usuari (`id_bloc`,`id_emissor`,`hash_bloc`) VALUES (%s, %s, %s)"
        dades = (bloc.id, emissor.id, bloc.hash_bloc_anterior)
        self.exportar_sql(sql, dades)

    def guardar_bloc(self, bloc, emissor):
        self.guardar_bloc_usuari(bloc, emissor)
        self.guardar_bloc_dades(bloc)

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
        id_assignatura = examen.assignatura.id

        sql_update = 'UPDATE examen SET id_document = %s, id_professor=%s, data_examen=%s, data_inici=%s, data_final=%s' \
                     ', pdf=%s , id_assignatura=%s WHERE `id_document` = %s'
        dades_update = (
        id_document, id_usuari, data_examen, data_inici, data_final, save_pdf, id_assignatura, id_document)

        sql = "INSERT INTO examen(id_document, id_professor, data_examen, data_inici, data_final, pdf, id_assignatura) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        dades = (id_document, id_usuari, data_examen, data_inici, data_final, save_pdf, id_assignatura)

        if self.existeix_examen(id_document):
            self.exportar_sql(sql_update, dades_update)
        else:
            self.exportar_sql(sql, dades)

        for estudiant in estudiants:
            if not self.existeix_examen_alumne(id_document, estudiant.id):
                sql = "INSERT INTO estudiant_examen(id_document, id_estudiant) VALUES (%s, %s)"
                dades = (id_document, estudiant.id)
                self.exportar_sql(sql, dades)

    def guardar_pdf(self, classe_pdf):
        sql = "INSERT INTO pdf(id_pdf, data_creacio, id_usuari, nom_fitxer, pdf) " \
              "VALUES (%s, %s, %s, %s, %s)"
        dades = (
            classe_pdf.id_document, classe_pdf.data_creacio, classe_pdf.usuari.id, classe_pdf.nom_fitxer,
            classe_pdf.pdf)
        self.exportar_sql(sql, dades)

    def guardar_resposta_examen(self, resposta):
        sql_update = 'UPDATE resposta_examen SET examen = %s, data_creacio=%s, id_usuari=%s, ' \
                     'pdf=%s  WHERE  examen=%s and id_usuari=%s'
        dades_update = (resposta.examen.id_document, resposta.data_creacio, resposta.usuari.id,
                        resposta.pdf, resposta.examen, resposta.usuari.id)

        sql = "INSERT INTO resposta_examen(examen, id_resposta, data_creacio, id_usuari, pdf) " \
              "VALUES (%s, %s, %s, %s, %s)"
        dades = (resposta.examen.id_document, resposta.id_document, resposta.data_creacio, resposta.usuari.id, resposta.pdf)

        if self.existeix_resposta_alumne(resposta.examen, resposta.usuari.id):
            self.exportar_sql(sql_update, dades_update)
        else:
            self.exportar_sql(sql, dades)

    def guardar_avaluacio_examen(self, avaluacio):
        sql_update = 'UPDATE avaluacio_examen SET id_avaluacio = %s, id_resposta=%s, id_professor=%s, id_estudiant=%s, ' \
                     'pdf=%s, nota=%s  WHERE  id_avaluacio=%s'
        dades_update = (avaluacio.id_document, avaluacio.resposta.id_document, avaluacio.usuari.id, avaluacio.estudiant.id,
                        avaluacio.pdf, avaluacio.nota, avaluacio.id_document)

        sql = "INSERT INTO avaluacio_examen(id_resposta, id_professor, id_estudiant, pdf, nota) " \
              "VALUES (%s, %s, %s, %s, %s)"
        dades = (avaluacio.resposta.id_document, avaluacio.usuari.id, avaluacio.estudiant.id,
                        avaluacio.pdf, avaluacio.nota)
        if self.existeix_avaluacio(avaluacio.id_document):
            self.exportar_sql(sql_update, dades_update)
        else:
            self.exportar_sql(sql, dades)

    def guardar_transaccio(self, transaccio):
        sql = "INSERT INTO transaccio(id_emissor, id_receptor, document, id_document, data_creacio) " \
              "VALUES (%s, %s, %s, %s, %s)"
        dades = (transaccio.emissor.id, transaccio.receptor.id, transaccio.document,
                 transaccio.id_document, transaccio.data_creacio,)
        self.exportar_sql(sql, dades)

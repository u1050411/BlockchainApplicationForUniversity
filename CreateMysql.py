import base64

import mysql.connector
from Crypto.PublicKey import RSA
from mysql.connector import errorcode


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

    def importar_sql(self, sql):
        try:
            self._cursor.execute(sql)
        except mysql.connector.Error as err:
            print("Error Mysql : {}".format(err))
            exit(1)
        return self._cursor.fetchall()[0]

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
                # sql = f"select {columna} from {taula} where {columna} = {dada} LIMIT 1"
                sql = f"select `{columna}` from `{taula}` where `{columna}` = '{dada}' LIMIT 1"
        self.select_sql(sql)
        return self._cursor.fetchone() is not None

    def clau_privada(self, id_usuari):
        sql = f'select `private_key` from `blockchainuniversity`.`private_key` where `id_usuari` = {id_usuari} LIMIT 1'
        clau_string = self.importar_sql(sql)
        return RSA.importKey(clau_string[0])

    def clau_publica(self, id_usuari):
        sql = f'select `public_key` from `blockchainuniversity`.`public_key` where `id_usuari` = {id_usuari} LIMIT 1'
        clau_string = self.importar_sql(sql)
        return RSA.importKey(clau_string[0])

    def guardar_usuari(self, id_usuari, nif,  nom, cognom):
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

    def guardar_document(self, num_document, nom_fitxer):
        pdf_file = open(nom_fitxer, "rb")
        save_pdf = base64.b64encode(pdf_file.read())
        pdf_file.close()
        num_document = str(num_document)
        id_document = int(num_document[0:-8])
        id_tipus = int(num_document[-8:-4])
        versio = int(num_document[-4:])
        id_usuari = 1050412
        sql = f'INSERT INTO documents (`id_document`, `id_tipus`, `versio`, `id_usuari`, `pdf`) VALUES({id_document}, ' \
              f'{id_tipus}, {versio}, {id_usuari}, "{save_pdf}") '
        self.exportar_sql(sql)

    def crear_taules(self):
        sqls = ["CREATE TABLE if not exists `usuari` ("
                "`id` int NOT NULL,"
                "`nif` varchar(9) NOT NULL,"
                "`nom` varchar(45) DEFAULT NULL,"
                "`cognom` varchar(100) DEFAULT NULL,"
                "PRIMARY KEY (`id`, `nif`)) ",

                "CREATE TABLE if not exists `private_key` ("
                "`id_usuari` INT NOT NULL,"
                "`private_key` longtext NULL,"
                "PRIMARY KEY (`id_usuari`))",

                "CREATE TABLE if not exists `public_key` ("
                "`id_usuari` INT NOT NULL,"
                "`public_key` longtext NULL,"
                "PRIMARY KEY (`id_usuari`))",

                "CREATE TABLE if not exists `transaccio` ("
                "`id` INT NOT NULL,"
                "`id_emisor` INT NOT NULL,"
                "`id_receptor` INT NOT NULL,"
                "`id_document` INT NOT NULL,"
                "`data` DATETIME NOT NULL,"
                "PRIMARY KEY(`id`, `id_emisor`, `id_receptor`, `id_document`, `data`))",

                "CREATE TABLE if not exists `documents` ("
                "`id_document` INT NOT NULL,"
                "`id_tipus` INT NOT NULL,"
                "`versio` INT NOT NULL,"
                "`id_usuari` INT NULL,"
                "`pdf` LONGBLOB  NULL,"
                "PRIMARY KEY (`id_document`, `id_tipus`, `versio`))",

                "CREATE TABLE if not exists `examen` ("
                "`id` INT NOT NULL,"
                "`datai` DATETIME NULL,"
                "`dataf` DATETIME NULL,"
                "`id_document` INT NULL,"
                "`id_professor` INT NULL,"
                "PRIMARY KEY (`id`))",

                "CREATE TABLE if not exists `examen_alumne` ("
                "`id_examen` INT NOT NULL,"
                "`id_estudiant` INT NOT NULL,"
                "PRIMARY KEY (`id_examen`,`id_estudiant`))",

                "CREATE TABLE if not exists `tipus_document` ("
                "`id` INT NOT NULL,"
                "`id_estudiant` INT NULL,"
                "PRIMARY KEY (`id`))"]

        for sql in sqls:
            self.exportar_sql(sql)

    def crear_usuaris(self):
        usuaris = [[1050411, '40373747T', 'Pau', 'de Jesus Bras'],
                   [1050402, '40373946E', 'Pere', 'de la Rosa'],
                   [1050403, '40332506M', 'Cristina', 'Sabari Vidal'],
                   [2050404, '40332507Y', 'Albert', 'Marti Sabari'],
                   [2000256, '40332508Y', 'Teodor Maria', 'Jove Lagunas']]

        for id_usuari, nif, nom, cognom in usuaris:
            self.guardar_usuari(id_usuari, nif, nom, cognom)

    def crear_documents(self):
        documents = [[100010001, f'C:/Users/u1050/PycharmProjects/'
                                 f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'],
                     [100020001, f'C:/Users/u1050/PycharmProjects/'
                                 f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'],
                     [100030001, f'C:/Users/u1050/PycharmProjects/'
                                 f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'],
                     [100040001, f'C:/Users/u1050/PycharmProjects/'
                                 f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf']]

        for num_document, pdf in documents:
            self.guardar_document(num_document, pdf)

    @staticmethod
    def crear_schema_dades(mydb, schema):
        mydb.esborrar_schema(schema)
        mydb.crear_schema(schema)
        mydb.crear_taules()
        mydb.crear_usuaris()


import mysql.connector
from Crypto.PublicKey import RSA


class MySqlBloc:

    def __init__(self):
        self._conexio = mysql.connector.connect(host='localhost', user='root', passwd='root')
        self._cursor = self._conexio.cursor()

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

    def crear_schema(self, schema):
        if not self.existeix(schema, None, None, None):
            line = "CREATE DATABASE " + schema
            self._cursor.execute(line)
            self._conexio = mysql.connector.connect(host='localhost', user='root', passwd='root', db=schema)
            self._cursor = self._conexio.cursor()

    def afegir_schema(self, schema):
        self._conexio = mysql.connector.connect(host='localhost', user='root', passwd='root', db=schema)
        self._cursor = self._conexio.cursor()

    def executar_sql(self, columnes, dades):
        self._cursor.execute(columnes, dades)
        self._conexio.commit()

    def select_sql(self, sql):
        self._cursor.execute(sql)

    def exportar_sql(self, sql):
        self._cursor.execute(sql)
        self._conexio.commit()

    def importar_sql(self, sql):
        self._cursor.execute(sql)
        return self._cursor.fetchall()[0]

    def esborrar_schema(self, schema):
        if self.existeix(schema, None, None, None):
            sql = f"DROP DATABASE `{schema}`"
            self.exportar_sql(sql)

    def tancar(self):
        self._cursor.close()
        self._conexio.close()

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
                sql = f"select {columna} from {taula} where {columna} = {dada} LIMIT 1"
        self.select_sql(sql)
        return self._cursor.fetchone() is not None

    def clau_privada(self, id_usuari):
        sql = f'select `private_key` from `blockchainuniversity`.`private_key` where `id_usuari` = {id_usuari} LIMIT 1'
        self._cursor.execute(sql)
        clau_string = self._cursor.fetchone()[0]
        return RSA.importKey(clau_string)

    def clau_publica(self, id_usuari):
        sql = f'select `public_key` from `blockchainuniversity`.`public_key` where `id_usuari` = {id_usuari} LIMIT 1'
        self._cursor.execute(sql)
        clau_string = self._cursor.fetchone()[0]
        return RSA.importKey(clau_string)

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


class CreacioInicial(MySqlBloc):

    def __init__(self, schema):
        super().__init__()
        if self.existeix(schema, None, None, None):
            self.esborrar_schema(schema)
        self.crear_schema(schema)
        self.crear_schema_dades()

    def crear_taules(self):
        sql = ("CREATE TABLE `usuari` ("
               "`id` int NOT NULL,"
               "`nif` varchar(8) NOT NULL,"
               "`nom` varchar(45) DEFAULT NULL,"
               "`cognom` varchar(100) DEFAULT NULL,"
               "PRIMARY KEY (`id`, `nif`)) ")

        self.exportar_sql(sql)
        sql = ("CREATE TABLE `documents` ("
               "`id` INT NOT NULL,"
               "`id_tipus` INT NULL,"
               "`id_usuari` INT NULL,"
               "`pdf` BINARY(64) NULL,"
               "PRIMARY KEY (`id`))")
        self.exportar_sql(sql)
        sql = ("CREATE TABLE `private_key` ("
               "`id_usuari` INT NOT NULL,"
               "`private_key` longtext NULL,"
               "PRIMARY KEY (`id_usuari`))")
        self.exportar_sql(sql)
        sql = ("CREATE TABLE `public_key` ("
               "`id_usuari` INT NOT NULL,"
               "`public_key` longtext NULL,"
               "PRIMARY KEY (`id_usuari`))")
        self.exportar_sql(sql)
        sql = ("CREATE TABLE `examen` ("
               "`id` INT NOT NULL,"
               "`datai` DATETIME NULL,"
               "`dataf` DATETIME NULL,"
               "`id_document` INT NULL,"
               "`id_professor` INT NULL,"
               "PRIMARY KEY (`id`))")
        self.exportar_sql(sql)
        sql = ("CREATE TABLE `examen_alumne` ("
               "`id_examen` INT NOT NULL,"
               "`id_estudiant` INT NOT NULL,"
               "PRIMARY KEY (`id_examen`,`id_estudiant`))")
        self.exportar_sql(sql)
        sql = ("CREATE TABLE `tipus_document` ("
               "`id` INT NOT NULL,"
               "`id_estudiant` INT NULL,"
               "PRIMARY KEY (`id`))")
        self.exportar_sql(sql)

    def crear_usuaris(self):
        id_usuari = 1050411
        nif = '40373947T'
        nom = 'Pau'
        cognom = 'de Jesus Bras'
        self.guardar_usuari(id_usuari, nom)
        id_usuari = 1050402
        nif = '40373946E'
        nom = 'Pere'
        cognom = 'de la Rosa'
        self.guardar_usuari(id_usuari, nom)
        id_usuari = 1050403
        nif = '40332506M'
        nom = 'Joan'
        cognom = 'Bras Dos Santos'
        self.guardar_usuari(id_usuari, nom)

    def crear_schema_dades(self):
        self.crear_taules()
        self.crear_usuaris()
        self.tancar()

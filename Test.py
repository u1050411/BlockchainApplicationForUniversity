import unittest

import mysql.connector
from Crypto.PublicKey import RSA

from CreateMysql import MySqlBloc
from BlockchainUniversity import Usuari, Universitat, Estudiant, Transaccio, Professor, TransaccioProfessor, Bloc, \
    BlockchainUniversity


class TestUsuaris(unittest.TestCase):

    def test_creation(self):
        udg = Universitat("Universitat de Girona")
        print(udg.nom)
        print(udg.identity)
        print(udg.private_key)

class TestUniversitat(unittest.TestCase):
    pass


class TestTransaction(unittest.TestCase):

    def test_creation(self):
        emissor = Estudiant('Pau')
        transaccio = Transaccio(emissor, 'DocumentEncriptat', 'idDocument')
        self.assertEqual(transaccio.emissor, emissor)
        self.assertEqual(transaccio.document, 'DocumentEncriptat')
        self.assertEqual(transaccio.nota, 0)
        self.assertEqual(transaccio.id_document, 'Hash')

    def test_posarNota(self):
        cua = []
        estudiant = Estudiant('Pau')
        professor = Professor('Teo')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
        cua.append(t1)
        t2 = TransaccioProfessor(professor, 'DocumentEncriptat', 'Hash', 10)
        cua.append(t2)
        for x in cua:
            x.display_transaccio()
            print('--------------')

    @staticmethod
    def test_sign_transaction():
        estudiant = Estudiant('Pau')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
        t1.sign_transaction()

    def test_to_Json(self):
        estudiant = Estudiant('Pau')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
        x = t1.to_json()
        # jtrans = json.loads(t1.to_json())
        # print(json.dumps(jtrans, indent=4))
        print(x)


class TestBloc(unittest.TestCase):

    def test_blocInicial(self):
        estudiant = Estudiant('Pau')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
        bloc_prova = Bloc(0, '0', t1)

        self.assertEqual(bloc_prova.index, 0)
        self.assertEqual(bloc_prova.transaccio, t1)
        self.assertEqual(bloc_prova.hash_bloc_anterior, '0')

    def test_calcular_Hash(self):
        estudiant = Estudiant('Albert')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
        bloc_prova = Bloc(0, '0', t1)
        hash_anterior = bloc_prova.calcular_hash()
        print(hash_anterior)


class TestBlockchainUniversity(unittest.TestCase):

    def test_crear_genesis_bloc(self):
        bloc_chain = BlockchainUniversity()
        bloc = bloc_chain.ultim_bloc
        self.assertEqual(bloc.index, 0)
        self.assertEqual(bloc.transaccio, [])
        self.assertEqual(bloc.hash_bloc_anterior, '0')

    def test_minat(self):
        bloc_chain = BlockchainUniversity()
        estudiant = Estudiant('Pau')
        professor = Professor('Teo')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
        bloc_chain.afegir_nova_transaccio(t1)
        t2 = TransaccioProfessor(professor, 'DocumentEncriptat', 'idDocument', 10)
        bloc_chain.afegir_nova_transaccio(t2)

        for x in bloc_chain.transaccio_noconfirmades:
            y = 0
            if x is not None:
                print(bloc_chain.minat())
            y += y
            x = []


class TestMysql(unittest.TestCase):

    Mydb = MySqlBloc()

    def test_drop_schema(self, nom_schema):
        sql = f"DROP DATABASE `{nom_schema}`"
        TestMysql.Mydb.exportar_sql(sql)
        TestMysql.Mydb.tancar()

    def test_create_schema(self, nom_schema):
        TestMysql.Mydb.create_schema(nom_schema)
        TestMysql.Mydb.tancar()

    def test_my_create_table(self, nom_schema):
        TestMysql.Mydb.afegir_schema(nom_schema)
        line = ("CREATE TABLE `usuari` ("
                "`id` int NOT NULL,"
                "`public_key` varchar(45) DEFAULT NULL,"
                "`nom` varchar(45) DEFAULT NULL,"
                "PRIMARY KEY (`id`)) ")
        TestMysql.Mydb.exportar_sql(line)
        line = ("CREATE TABLE `documents` ("
                "`id` INT NOT NULL,"
                "`id_tipus` INT NULL,"
                "`id_usuari` INT NULL,"
                "`pdf` BINARY(64) NULL,"
                "PRIMARY KEY (`id`))")
        TestMysql.Mydb.exportar_sql(line)
        line = ("CREATE TABLE `private_key` ("
                "`id_usuari` INT NOT NULL,"
                "`private_key` longtext NULL,"
                "PRIMARY KEY (`id_usuari`))")
        TestMysql.Mydb.exportar_sql(line)
        line = ("CREATE TABLE `public_key` ("
                "`id_usuari` INT NOT NULL,"
                "`public_key` longtext NULL,"
                "PRIMARY KEY (`id_usuari`))")
        TestMysql.Mydb.exportar_sql(line)
        TestMysql.Mydb.tancar()

    def test_create_usuari(self, nom_schema, id_usuari, nom):
        TestMysql.Mydb.afegir_schema(nom_schema)
        sql = f'INSERT INTO usuari (`id`, `nom`) VALUES({id_usuari}, "{nom}")'
        TestMysql.Mydb.exportar_sql(sql)
        key = RSA.generate(1024)
        private_key = key.exportKey('PEM').decode('ascii')
        public_key = key.publickey()
        string_key = public_key.exportKey('PEM').decode('ascii')
        sql = f'INSERT INTO private_key (`id_usuari`, `private_key`) VALUES({id_usuari}, "{private_key}")'
        TestMysql.Mydb.exportar_sql(sql)
        sql = f'INSERT INTO public_key (`id_usuari`, `public_key`) VALUES({id_usuari}, "{string_key}")'
        TestMysql.Mydb.exportar_sql(sql)
        
    def test_create_usuaris(self, nom_schema):
        id_usuari = 1050411
        nom = 'Pau'
        self.test_create_usuari(nom_schema, id_usuari, nom)
        id_usuari = 1050401
        nom = 'Pere'
        self.test_create_usuari(nom_schema, id_usuari, nom)
        id_usuari = 1050402
        nom = 'Joan'
        self.test_create_usuari(nom_schema, id_usuari, nom)
    
    def test_create_blockChain_all(self, nom_schema):
        if TestMysql.Mydb.existeix(nom_schema, "", "", ""):
            self.test_drop_schema(nom_schema)
        self.test_create_schema(nom_schema)
        self.test_my_create_table(nom_schema)
        self.test_create_usuaris(nom_schema)

    def test_existeix(self):
        self.assertEqual(TestMysql.Mydb.existeix('private_key', 'id_usuari', 1050404), True)
        self.assertEqual(TestMysql.Mydb.existeix('private_key', 'id_usuari', 5050404), False)

    def test_clau_(self):
        id_usuari = 1050411
        TestMysql.Mydb.afegir_schema('blockchainuniversity')
        privat_key = TestMysql.Mydb.clau_privada(id_usuari)
        public_key = TestMysql.Mydb.clau_publica(id_usuari)
        self.assertTrue(privat_key.public_key(), public_key)
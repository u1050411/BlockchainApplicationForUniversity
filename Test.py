import unittest

import mysql.connector
from CreateMysql import MySqlBloc
from BlockchainUniversity import Usuari, Universitat, Estudiant, Transaccio, Professor, TransaccioProfessor, Bloc, \
    BlockchainUniversity


class TestUsuaris(unittest.TestCase):

    def test_creation(self):
        udg = Universitat("Universitat de Girona")
        print(udg.nom)
        print(udg.identity)
        print(udg.private_key)

    def test_mysql(self):
        print
        "Resultados de mysql.connector:"
        miConexion = mysql.connector.connect(host='localhost', user='root', passwd='root', db='blockchainuniversity')
        cur = miConexion.cursor()
        cur.execute("SELECT id, nom FROM usuari")
        for (id, nom) in cur:
            print("{}, {} ".format(
                id, nom))
        cur.close()
        miConexion.close()


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

    def test_create_schema(self):
        mydb = MySqlBloc()
        mydb.create_schema('blockchainuniversity2')
        mydb.tancar()

    def test_my_create_table(self):
        mydb = MySqlBloc()
        mydb.afegir_schema('blockchainuniversity2')
        line = ("CREATE TABLE `usuari` ("
                "`id` int NOT NULL,"
                "`public_key` varchar(45) DEFAULT NULL,"
                "`nom` varchar(45) DEFAULT NULL,"
                "PRIMARY KEY (`id`)) ")
        mydb.executar_sql(line)
        line = ("CREATE TABLE `documents` ("
                "`id` INT NOT NULL,"
                "`id_tipus` INT NULL,"
                "`id_usuari` INT NULL,"
                "`pdf` BINARY(64) NULL,"
                "PRIMARY KEY (`id`))")
        mydb.executar_sql(line)
        line = ("CREATE TABLE `private_key` ("
                "`id_usuari` INT NOT NULL,"
                "`key` BINARY(128) NULL,"
                "PRIMARY KEY (`id_usuari`))")
        mydb.executar_sql(line)
        line = ("CREATE TABLE `public_key` ("
                "`id_usuari` INT NOT NULL,"
                "`key` BINARY(128) NULL,"
                "PRIMARY KEY (`id_usuari`))")
        mydb.executar_sql(line)
        mydb.tancar()

    def test_create_usuari(self):
        mydb = MySqlBloc()
        mydb.afegir_schema('blockchainuniversity')
        line = "INSERT INTO usuari (`id`, `nom`) VALUES ('1050412', 'Pere')"
        mydb.executar_sql(line)
        line = "INSERT INTO usuari (`id`, `nom`) VALUES ('1050412', 'Pere')"
        mydb.executar_sql(line)
        line = "INSERT INTO usuari (`id`, `nom`) VALUES ('1050413', 'Joan')"
        mydb.executar_sql(line)

    def test_drop_schema(self):
        mydb = MySqlBloc()
        mydb.executar_sql("DROP DATABASE `blockchainuniversity2`")
        mydb.tancar()


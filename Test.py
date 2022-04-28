import unittest
from random import Random

from Crypto.PublicKey import RSA

from BlockchainUniversity import Universitat, Estudiant, Transaccio, Professor, TransaccioExamen, Bloc,  Examen, Usuari, Factoria
from CreateMysql import MySqlBloc


class TestFactoria(unittest.TestCase):

    def test_factoria(self):
        schema = 'blockchainuniversity'
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, schema)
        my_db.afegir_schema(schema)
        estudiant = Factoria.build_usuari_from_db(my_db, 1050402, 'estudiant')
        self.assertEqual(estudiant.id, 1050402)
        self.assertEqual(estudiant.nom, 'Pere')
        professor = Factoria.build_usuari_from_db(my_db, 2000256, 'professor')
        self.assertEqual(professor.id, 2000256)
        self.assertEqual(professor.nom, 'Teodor Maria')


class TestUsuaris(unittest.TestCase):

    def test_creation(self):
        public_key = RSA.generate(1024).publickey()
        estudiant = Estudiant(1050406, '40332505G', 'Marta', "Rodriguez", public_key)
        self.assertEqual(estudiant.id, 1050406)
        self.assertEqual(estudiant.nif, '40332505G')
        self.assertEqual(estudiant.nom, 'Marta')
        self.assertEqual(estudiant.cognom, 'Rodriguez')
        self.assertEqual(estudiant.public_key, public_key)


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
        t2 = TransaccioExamen(professor, 'DocumentEncriptat', 'Hash', 10)
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
        pass
    # bloc_chain = BlockchainUniversity()
    # bloc = bloc_chain.ultim_bloc
    # self.assertEqual(bloc.index, 0)
    # self.assertEqual(bloc.transaccio, [])
    # self.assertEqual(bloc.hash_bloc_anterior, '0')

    # def test_minat(self):
    #     bloc_chain = BlockchainUniversity()
    #     estudiant = Estudiant('Pau')
    #     professor = Professor('Teo')
    #     t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
    #     bloc_chain.afegir_nova_transaccio(t1)
    #     t2 = TransaccioExamen(professor, 'DocumentEncriptat', 'idDocument', 10)
    #     bloc_chain.afegir_nova_transaccio(t2)
    #
    #     for x in bloc_chain.transaccio_noconfirmades:
    #         y = 0
    #         if x is not None:
    #             print(bloc_chain.minat())
    #         y += y
    #         x = []


class TestMysql(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = 'blockchainuniversity'

    def tearDown(self):
        self.my_db.tancar()

    def test_afegir(self):
        self.my_db.afegir_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), True)

    def test_esborrar_schema(self):
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
        self.my_db.esborrar_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), False)

    def test_crear_schema(self):
        self.my_db.crear_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), True)

    def test_exportar_sql(self):
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
        sql = "CREATE TABLE `TaulaProva` (" \
              "`id` int NOT NULL,"\
              "`nif` varchar(9) NOT NULL," \
              "`nom` varchar(45) DEFAULT NULL,"\
              "`cognom` varchar(100) DEFAULT NULL,"\
              "PRIMARY KEY (`id`, `nif`)) "
        self.my_db.afegir_schema(self.schema)
        self.my_db.exportar_sql(sql)
        self.assertEqual(self.my_db.existeix(self.schema, 'TaulaProva', None, None), True)

    def test_crear_taules(self):
        schema = self.schema
        self.my_db.esborrar_schema(schema)
        self.my_db.crear_schema(schema)
        self.my_db.afegir_schema(schema)
        self.my_db.crear_taules()
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', None, None), True)

    def test_crear_usuaris(self):
        self.test_crear_taules()
        self.my_db.afegir_schema(self.schema)
        self.my_db.crear_usuaris()
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1050403'), True)

    def test_existeix(self):
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), True)
        self.assertEqual(self.my_db.existeix('noSchema', None, None, None), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', None, None), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'no_Taula', None, None), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'nom', None), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'no_Columna', None), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1050403'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1070401'), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'private_key', 'id_usuari', '1050403'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'public_key', 'id_usuari', '1050403'), True)

    def test_guardar_usuari(self):
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
        id_usuari = 1050404
        nif = '40373944C'
        nom = 'Pablo'
        cognom = 'Gutierrez'
        self.my_db.afegir_schema(self.schema)
        self.my_db.guardar_usuari(id_usuari, nif, nom, cognom)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1050411'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'nom', 'Pere'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'private_key', 'id_usuari', '1050411'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'public_key', 'id_usuari', '1050411'), True)

    def test_clau(self):
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
        id_usuari = 1050402
        self.my_db.afegir_schema(self.schema)
        privat_key = self.my_db.clau_privada(id_usuari)
        public_key = self.my_db.clau_publica(id_usuari)
        self.assertTrue(privat_key.public_key(), public_key)


class TestExamen(unittest.TestCase):

    def test_creacio_examen(self):
        MySqlBloc.crear_schema_dades(self.mydb, self.schema)
        examen = Examen()




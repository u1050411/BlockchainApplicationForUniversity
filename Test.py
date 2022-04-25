import unittest

from BlockchainUniversity import Universitat, Estudiant, Transaccio, Professor, TransaccioProfessor, Bloc, \
    BlockchainUniversity, Examen, Factoria
from CreateMysql import MySqlBloc, CreacioInicial


class TestFactoria(unittest.TestCase):

    def test_factoria(self):
        CreacioInicial('blockchainuniversity')
        usuari = Factoria.usuari('1050402')
        self.assertEqual(usuari.id_usuari, 1050402)
        self.assertEqual(usuari.nom, 'Pere')


class TestUsuaris(unittest.TestCase):

    def test_creation(self):
        estudiant = Estudiant.crear_usuari(1050411, 'Pau', None)


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

    def setUp(self):
        self.mydb = MySqlBloc()

    def tearDown(self):
        self.mydb.tancar()

    def test_esborrar_schema(self):
        CreacioInicial('blockchainuniversity')
        self.mydb.esborrar_schema('BlockchainUniversity')
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', None, None, None), False)

    def test_crear_schema(self):
        self.mydb.crear_schema('BlockchainUniversity')
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', None, None, None), True)

    def test_existeix(self):
        CreacioInicial('blockchainuniversity')
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', None, None, None), True)
        self.assertEqual(self.mydb.existeix('noSchema', None, None, None), False)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'usuari', None, None), True)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'no_Taula', None, None), False)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'usuari', 'nom', None), True)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'usuari', 'no_Columna', None), False)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'usuari', 'id', '1050403'), True)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'usuari', 'id', '1070401'), False)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'private_key', 'id_usuari', '1050403'), True)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'public_key', 'id_usuari', '1050403'), True)

    def test_guardar_usuari(self):
        CreacioInicial('blockchainuniversity')
        id_usuari = 1050404
        nif = '40373944C'
        nom = 'Pablo'
        cognom = 'Gutierrez'
        self.mydb.afegir_schema('BlockchainUniversity')
        self.mydb.guardar_usuari(id_usuari, nif, nom, cognom)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'usuari', 'id', '1050411'), True)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'usuari', 'nom', 'Pere'), True)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'private_key', 'id_usuari', '1050411'), True)
        self.assertEqual(self.mydb.existeix('BlockchainUniversity', 'public_key', 'id_usuari', '1050411'), True)

    def test_clau(self):
        CreacioInicial('blockchainuniversity')
        id_usuari = 1050402
        self.mydb.afegir_schema('blockchainuniversity')
        privat_key = self.mydb.clau_privada(id_usuari)
        public_key = self.mydb.clau_publica(id_usuari)
        self.assertTrue(privat_key.public_key(), public_key)


class Test_examen:

    def test_creacio_examen(self):
        mydb = CreacioInicial('blockchainuniversity')
        mydb.crear_schema_dades()
        examen = Examen()




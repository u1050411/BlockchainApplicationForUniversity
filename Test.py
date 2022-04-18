import unittest

from pandas.io import json

from BlockchainUniversity import Usuari, Universitat, Estudiant, Transaccio, Professor, TransaccioProfessor, Bloc


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
        transaccio = Transaccio(emissor, 'DocumentEncriptat', 'Hash')
        self.assertEqual(transaccio.emissor, emissor)
        self.assertEqual(transaccio.document, 'DocumentEncriptat')
        self.assertEqual(transaccio.nota, 0)
        self.assertEqual(transaccio.id_document, 'Hash')

    def test_posarNota(self):
        cua = []
        estudiant = Estudiant('Pau')
        professor = Professor('Teo')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'Hash')
        cua.append(t1)
        t2 = TransaccioProfessor(professor, 'DocumentEncriptat', 'Hash', 10)
        cua.append(t2)
        for x in cua:
            x.display_transaccio()
            print('--------------')

    def test_to_Json(self):
        estudiant = Estudiant('Pau')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'Hash')
        x= t1.to_json()
        # jtrans = json.loads(t1.to_json())
        # print(json.dumps(jtrans, indent=4))
        print(x)


class TestBloc(unittest.TestCase):

    def test_blocInicial(self):
        estudiant = Estudiant('Pau')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'Hash')
        blockinicial = Bloc('0', '0', t1)
        blockinicial.previous_block_hash = None

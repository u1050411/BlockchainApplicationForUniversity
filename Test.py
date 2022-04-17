import unittest

from BlockchainUniversity import Usuari


class TestUniversitat(unittest.TestCase):

    def test_creation(self):
        udg = Usuari("Universitat de Girona")
        print(udg.nom)
        print(udg.identity)
        print(udg.private_key)


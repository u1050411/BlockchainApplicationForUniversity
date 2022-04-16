import unittest

from BlockchainUniversity import Universitat


class TestUniversitat(unittest.TestCase):

    def test_creation(self):
        udg = Universitat(self)
        print(udg.nom)
        print(udg.identity)
        print(udg.private_key)


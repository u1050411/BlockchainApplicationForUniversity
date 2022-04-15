import unittest

from Client import Client
from Transaction import Transaction


class TestTransaction(unittest.TestCase):

    def test_creation(self):
        transaction = Transaction(1, 2, 3)
        self.assertEqual(transaction.sender, 1)  # add assertion here
        self.assertEqual(transaction.recipient, 2)  # add assertion here
        self.assertEqual(transaction.value, 3)  # add assertion here


if __name__ == '__main__':
    unittest.main()


class TestClient(unittest.TestCase):
    def test_creation(self):
        dinesh = Client()
        print(dinesh.identity)
        print(dinesh.private_key)
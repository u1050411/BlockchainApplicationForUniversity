import unittest

from Client import Client
from Transaction import Transaction


class TestTransaction(unittest.TestCase):
    if __name__ == '__main__':
        unittest.main()

    def test_creation(self):
        remitent = Client()
        receptor = Client()
        transaction = Transaction(remitent, receptor.private_key, 3)
        self.assertEqual(transaction.sender, remitent)  # add assertion here
        self.assertEqual(transaction.recipient, receptor.private_key)  # add assertion here
        self.assertEqual(transaction.value, 3)  # add assertion here

    def test_creacioCuaTransaction(self):
        transactions = []
        dinesh = Client()
        ramesh = Client()
        eli = Client()
        vijay = Client()

        t1 = Transaction(
            dinesh,
            ramesh.identity,
            15.0
        )
        t1.sign_transaction()
        transactions.append(t1)
        t2 = Transaction(
            dinesh,
            eli.identity,
            6.0
        )
        t2.sign_transaction()
        transactions.append(t2)
        t3 = Transaction(
            ramesh,
            vijay.identity,
            2.0
        )
        t3.sign_transaction()
        transactions.append(t3)
        t4 = Transaction(
            eli,
            ramesh.identity,
            4.0
        )
        t4.sign_transaction()
        transactions.append(t4)
        t5 = Transaction(
            vijay,
            eli.identity,
            7.0
        )
        t5.sign_transaction()
        transactions.append(t5)
        t6 = Transaction(
            ramesh,
            eli.identity,
            3.0
        )
        t6.sign_transaction()
        transactions.append(t6)
        t7 = Transaction(
            eli,
            dinesh.identity,
            8.0
        )
        t7.sign_transaction()
        transactions.append(t7)
        t8 = Transaction(
            eli,
            ramesh.identity,
            1.0
        )
        t8.sign_transaction()
        transactions.append(t8)
        t9 = Transaction(
            vijay,
            dinesh.identity,
            5.0
        )
        t9.sign_transaction()
        transactions.append(t9)
        t10 = Transaction(
            vijay,
            ramesh.identity,
            3.0
        )
        t10.sign_transaction()
        transactions.append(t10)

    # for x in transactions:
    #     pass

    # display_transaction(transaction)
    # print('--------------')


class TestClient(unittest.TestCase):
    def test_creation(self):
        dinesh = Client()
        print(dinesh.identity)
        print(dinesh.private_key)

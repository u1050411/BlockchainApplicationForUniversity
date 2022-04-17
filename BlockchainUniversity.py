import binascii
from datetime import datetime
from typing import List, Any

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from matplotlib import collections


class Usuari:

    def __init__(self, nom):
        self._nom = nom
        random_seed = Random.new().read
        self._private_key = RSA.generate(1024, random_seed)  # Creacio de la clau privada
        self._public_key = self._private_key.publickey()  # Creacio de la clau publica que es part de la clau privada
        self._signer = PKCS1_v1_5.new(self._private_key)  # Signatura

    @property  # retorna clau publica
    def identity(self):
        return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')

    @property  # retorna clau privada
    def private_key(self):
        return self._private_key

    @property
    def nom(self):
        return self._nom

    @nom.setter
    def nom(self, nom):
        self._nom = nom

    @private_key.setter  # fiquem clau
    def private_key(self, key):
        self._private_key = key
        self._public_key = self._private_key.publickey()


class Universitat(Usuari):
    pass


class Professors(Usuari):
    pass


class Estudiants(Usuari):
    pass


class Transaccio:

    def __init__(self, emissor, document, id_document):
        self.emissor = emissor
        self.document = document
        self.id_document = id_document
        self.nota = 0
        self.time = datetime.datetime.now()

    def to_dict(self):
        return collections.OrderedDict({
            'Emissor': self.emissor.identity,
            'ID Document': self.id_document,
            'Document': self.document,
            'Nota': self.nota,
            'Data': self.time})

    def display_transaction(transaccio):
        trans = transaccio.to_dict()
        print("sender: " + trans['Emissor'])
        print('-----')
        print("recipient: " + trans['ID Document'])
        print('-----')
        print("value: " + str(trans['Document']))
        print('-----')
        print("time: " + str(trans['Nota']))
        print('-----')
        print("time: " + str(trans['Data']))
        print('-----')

    def sign_transaction(self):
        private_key = self.emissor.private_key
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')


class TransaccioProfessor(Transaccio):

    def __init__(self, emissor, document, id_document, nota):
        self.emissor = emissor
        self.document = document
        self.id_document = id_document
        self.nota = nota
        self.time = datetime.datetime.now()

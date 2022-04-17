import binascii
import datetime
import collections
from hashlib import sha256

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from pandas._libs import json


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


class Professor(Usuari):
    pass


class Estudiant(Usuari):
    pass


class Transaccio:
    # Classe on guardem les dades de les transaccions
    def __init__(self, emissor, document, id_document):
        self._emissor = emissor
        self._document = document
        self._id_document = id_document
        self._nota = 0
        self._time = datetime.datetime.now()

    @property
    def emissor(self):
        return self._emissor

    @property
    def document(self):
        return self._document

    @property
    def id_document(self):
        return self._id_document

    @property
    def nota(self):
        return self._nota

    @property
    def time(self):
        return self._time

    @emissor.setter
    def emissor(self, emissor):
        self._emissor = emissor

    @document.setter
    def document(self, document):
        self._document = document

    @document.setter
    def id_document(self, id_document):
        self._id_document = id_document

    @nota.setter
    def nota(self, nota):
        self._nota = nota

    @time.setter
    def time(self, time):
        self._time = time

    def to_dict(self):
        return collections.OrderedDict({
            'Emissor': self.emissor.identity,
            'ID Document': self.id_document,
            'Document': self.document,
            'Nota': self.nota,
            'Data': self.time})

    def display_transaccio(self):
        trans = self.to_dict()
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

    def __init__(self, emissors, document, id_document, nota, emissor):
        super().__init__(emissor, document, id_document)
        self.nota = nota


class Bloc:
    # Classe creació del bloc

    def __init__(self, index, previous_block_hash, transaccio):
        self._index = index
        self._timestamp = datetime.datetime.now()
        self._previous_block_hash = previous_block_hash
        self._transaccio = transaccio
        self._nonce = 0

    @property
    def index(self):
        return self._index

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def previous_block_hash(self):
        return self._previous_block_hash

    @property
    def transaccio(self):
        return self._transaccio

    @property
    def nonce(self):
        return self._nonce

    @index.setter
    def nota(self, index):
        self._index = index

    @previous_block_hash.setter
    def previous_block_hash(self, previous_block_hash):
        self._previous_block_hash = previous_block_hash

    @transaccio.setter
    def transaccio(self, transaccio):
        self._transaccio = transaccio

    @nonce.setter
    def transaccio(self, nonce):
        self._nonce = nonce

    def bloc_hash(self):
        # Converteix el bloc en una cadena json i retorna el hash
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return 256(block_string.encode()).hexdigest()



import binascii
import datetime
import collections
import hashlib
from hashlib import sha256

from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from pandas.io import json

UTF_8 = 'utf8'


class Usuari:

    def __init__(self, nom):
        self.nom = nom
        random_seed = Random.new().read
        self._private_key = None  # Creacio de la clau privada
        self._public_key = None  # Creacio de la clau publica que es part de la clau privada
        self._signer = None  # Signatura
        self.private_key = RSA.generate(1024, random_seed)

    def sign(self, data):
        h = SHA.new(data)
        return binascii.hexlify(self._signer.sign(h)).decode('ascii')

    @property  # retorna clau publica
    def identity(self):
        return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')

    @property  # retorna clau privada
    def private_key(self):
        return self._private_key

    @private_key.setter  # fiquem clau
    def private_key(self, key):
        self._private_key = key  # Creacio de la clau privada
        self._public_key = self._private_key.publickey()  # Creacio de la clau publica que es part de la clau privada
        self._signer = PKCS1_v1_5.new(self._private_key)  # Signatura


class Universitat(Usuari):
    pass


class Professor(Usuari):
    pass


class Estudiant(Usuari):
    pass


class Transaccio:
    # Classe on guardem les dades de les transaccions
    def __init__(self, emissor, document, id_document):
        self.emissor = emissor
        self.document = document
        self.id_document = id_document
        self._nota = 0
        self._time = datetime.datetime.now()

    @property
    def nota(self):
        return self._nota

    @property
    def time(self):
        return self._time

    @nota.setter
    def nota(self, nota):
        self._nota = nota

    @time.setter
    def time(self, time):
        self._time = time

    # canviar a estructura json

    def to_dict(self):
        return collections.OrderedDict({
            'Emissor': self.emissor.identity,
            'ID Document': self.id_document,
            'Document': self.document,
            'Nota': self.nota,
            'Data': self.time})

    def display_transaccio(self):
        print(f"""sender: {self.emissor.identity} 
-----
recipient: {self.id_document}
-----
value: {self.document}
-----
nota: {self.nota}
-----
time: {self.time}
-----
""")

    # Mètode que el emissor signa la transaccio

    def sign_transaction(self):
        # return self.emissor.sign(str(self.to_dict()).encode('utf8'))
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return self.emissor.sign(block_string.encode(UTF_8))

    def to_json(self):
        return json.dumps(self.__dict__)


class TransaccioProfessor(Transaccio):

    def __init__(self, emissor, document, id_document, nota):
        super().__init__(emissor, document, id_document)
        self.nota = nota


class Bloc:
    # Classe creació del bloc

    def __init__(self, index, previous_block_hash, transaccio):
        self._index = index
        self._timestamp = datetime.datetime.now()
        self._previous_block_hash = previous_block_hash
        self._transaccio = transaccio
        self.nonce = 0

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

    def bloc_hash(self):
        # Converteix el bloc en una cadena json i retorna el hash
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

import binascii

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class Universitat:

    def __init__(self):
        # self.nom = nom
        random_seed = Random.new().read
        self._private_key = RSA.generate(1024, random_seed)  # Creacio de la clau privada
        self._public_key = self._private_key.publickey()  # Creacio de la clau publica que es part de la clau privada
        self._signer = PKCS1_v1_5.new(self._private_key)  # Signatura

    @property  # get public key
    def identity(self):
        return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')

    @property  # get private key
    def private_key(self):
        return self._private_key
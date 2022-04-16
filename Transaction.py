import binascii
import collections
import datetime

from Crypto.Hash import SHA
# Define una les variables que guardarem en el blockchain
from Crypto.Signature import PKCS1_v1_5



class Transaction:

    def __init__(self, sender, recipient, value):
        self.sender = sender
        self.recipient = recipient
        self.value = value
        self.time = datetime.datetime.now()

    # Creem blocks de la cadena

    def to_dict(self):
        if self.sender == "Genesis":  # Per tradicció al primer block es anonim i li diem genesis
            identity = "Genesis"
        else:
            identity = self.sender.identity

        return collections.OrderedDict({
            'sender': identity,
            'recipient': self.recipient,
            'value': self.value,
            'time': self.time})

    def display_transaction(self):
        # for transaction in transactions:
        dictat = self.to_dict()
        print("sender: " + dictat['sender'])
        print('-----')
        print("recipient: " + dictat['recipient'])
        print('-----')
        print("value: " + str(dictat['value']))
        print('-----')
        print("time: " + str(dictat['time']))
        print('-----')

    def sign_transaction(self):
        private_key = self.sender._private_key
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')

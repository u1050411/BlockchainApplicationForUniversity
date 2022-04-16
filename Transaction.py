import datetime

# Define una les variables que guardarem en el blockchain
from matplotlib import collections


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


def display_transaction(transaction):
    # for transaction in transactions:
    dictat = transaction.to_dict()
    print("sender: " + dictat['sender'])
    print('-----')
    print("recipient: " + dictat['recipient'])
    print('-----')
    print("value: " + str(dictat['value']))
    print('-----')
    print("time: " + str(dictat['time']))
    print('-----')

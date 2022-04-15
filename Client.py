# import libraries
import hashlib
import random
import string
import json
import binascii
import numpy as np
import pandas as pd
# import pylab as pl
import matplotlib
import matplotlib.pyplot as plt
import logging
import datetime
import collections

#  PKI Requereix les seguents llibreries.

import crypto
import crypto.Random
import self as self
from crypto.Hash import SHA
from crypto.PublicKey import RSA
from crypto.Signature import PKCS1_v1_5

# Creem la clase publica que sera la identitat del client . En el nostre cas identitat de les universitats.

class Client:

    def __init__(self):
        random = crypto.Random.new().read
        self._private_key = RSA.generate(1024, random)
        self._public_key = self._private_key.publickey()
        self._signer = PKCS1_v1_5.new(self._private_key)

    @property
    def identity(self):
        return
binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')

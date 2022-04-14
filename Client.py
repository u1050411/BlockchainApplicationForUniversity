# import libraries
import hashlib
import random
import string
import json
import binascii
import numpy as np
import pandas as pd
#   import pylab as pl
import logging
import datetime
import collections

#  PKI Requereix les seguents llibreries.

import Crypto
import Crypto.Random
import self as self
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

self._private_key = RSA.generate(1024, random)
self._public_key = self._private_key.publickey()

# Creem la clase publica que sera la identitat del client . En el nostre cas identitat de les universitats.
@property
   def identity(self):
      return
binascii.hexlify(self._public_key.exportKey(format='DER'))
.decode('ascii')
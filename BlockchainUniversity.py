import ast
import base64
import binascii
import collections
import hashlib
import json
from datetime import datetime

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from cryptography.fernet import Fernet
from matplotlib.font_manager import _json_decode

UTF_8 = 'utf8'
ESTUDIANT = 'estudiant'
PROFESSOR = 'professor'
USUARI = 'usuari'


class Factoria:

    def __init__(self):
        pass

    @staticmethod
    def build_universitat_from_db(my_db):
        universiat_db = my_db.importar_universitat()
        if universiat_db is not None:
            id_universitat, nom, private_key_str, public_key_str = universiat_db
            public_key = RSA.importKey(public_key_str)
            private_key = RSA.importKey(private_key_str)
            return Universitat(nom, private_key, public_key)
        return None

    @staticmethod
    def build_usuari_from_db(my_db, id_usuari):
        if my_db.existeix_usuari(id_usuari):
            usuari_db = my_db.importar_usuari(id_usuari)
            if usuari_db is not None:
                id_us, tipus, nif, nom, cognom, public_key_str = usuari_db
                public_key = RSA.importKey(public_key_str)
                if tipus == ESTUDIANT:
                    estudiant = Estudiant(id_usuari, nif, nom, cognom, public_key)
                    return estudiant
                elif tipus == PROFESSOR:
                    professor = Professor(id_usuari, nif, nom, cognom, public_key)
                    return professor
        return None

    @staticmethod
    def build_examen_from_db(my_db, id_document, per_estudiant=None):
        if my_db.existeix_examen(id_document):
            id_document, id_professor, data_examen, data_inicial, data_final, pdf = my_db.importar_examen(id_document)
            professor = Factoria.build_usuari_from_db(my_db, id_professor)
            examen = Examen(id_document, professor, pdf, data_inicial, data_final)
            if per_estudiant == None:
                estudiants = my_db.importar_estudiants_examen(id_document)
                if estudiants is not None:
                    for id_estudiant in estudiants:
                        estudiant = Factoria.build_usuari_from_db(my_db, id_estudiant[0])
                        examen.estudiants.append(estudiant)
                    respostes = my_db.importar_respostes(id_document)
                    for sql_resposta in respostes:
                        id_resposta, data_creacio, id_usuari, pdf = sql_resposta
                        usuari = Factoria.build_usuari_from_db(my_db, id_usuari)
                        if usuari.tipus == PROFESSOR:
                            examen.evaluacioExamen = EvaluacioExamen(id_resposta, id_document, usuari, pdf)
                            examen.evaluacioExamen.data_creacio = data_creacio
                        elif usuari.tipus == ESTUDIANT:
                            resposta = RespostaExamen(id_resposta, id_document, usuari, pdf)
                            resposta.data_creacio = data_creacio
                            examen.respostes.append(resposta)
            return examen
        return None

    @staticmethod
    def build_transaccio_from_db(my_db):
        trans_db = my_db.importar_transaccions()
        (id_trans, emissor, receptor, dada_json, id_document, data_creacio) = trans_db
        emissor = Factoria.build_usuari_from_db(my_db, emissor)
        receptor = Factoria.build_usuari_from_db(my_db, receptor)
        dada = Encriptador.crear_json(dada_json)
        transaccio = Transaccio.crear_mysql(id_trans, emissor, receptor, dada, id_document, data_creacio)
        return transaccio

    @staticmethod
    def build_resposta_examen_from_db(my_db, id_document, id_resposta):
        resposta_importar = my_db.importar_resposta(id_document, id_resposta)
        (id_resposta, time, id_usuari, pdf) = resposta_importar[0]
        usuari = Factoria.build_usuari_from_db(my_db, id_usuari)
        if usuari.tipus == ESTUDIANT:
            resposta = RespostaExamen(id_resposta, id_document, usuari, pdf)
        if usuari.tipus == PROFESSOR:
            resposta = EvaluacioExamen(id_resposta, id_document, usuari, pdf)
        return resposta

    @staticmethod
    def build_resposta_alumne_from_db(my_db, id_document, id_resposta):
        resposta = Factoria.build_resposta_examen_from_db(my_db, id_document, id_resposta)
        if resposta.usuari.tipus != ESTUDIANT:
            raise ValueError('Amb aquest id no hi ha una resposta')
        return resposta

    @staticmethod
    def build_evaluacio_examen_from_db(my_db, id_examen, id_resposta):
        resposta = Factoria.build_resposta_examen_from_db(my_db, id_examen, id_resposta)
        if resposta.usuari.tipus != PROFESSOR:
            raise ValueError('Amb aquest id no hi ha una evaluacio')
        return resposta


class Encriptador:

    def __init__(self, dada=None, public_key=None):
        if dada is None:
            self.clau = None
            self.dada = None
        else:
            key_simetric = Fernet.generate_key()
            encriptar_clau = PKCS1_OAEP.new(public_key)
            self.clau = encriptar_clau.encrypt(key_simetric)
            data_json = dada.to_json()
            dada_byte = data_json.encode("utf-8")
            encriptador = Fernet(key_simetric)
            self.dada = encriptador.encrypt(dada_byte)

    @staticmethod
    def crear_json(dada_json):
        encript_json = json.loads(dada_json)
        clau = encript_json['clau']
        dada = encript_json['dada']
        dada_encriptat = Encriptador()
        dada_encriptat.dada = dada
        dada_encriptat.clau = clau
        return dada_encriptat

    def get_dada(self, private_key):
        desencriptador = PKCS1_OAEP.new(private_key)
        clau_simetrica = desencriptador.decrypt(self.clau)
        key_simetric = Fernet(clau_simetrica)
        dada_desencriptada = key_simetric.decrypt(self.dada).decode()
        return dada_desencriptada

    def to_dict(self):
        return collections.OrderedDict({
            'clau': self.clau,
            'dada': self.dada
        })

    def to_json(self):
        rest = self.to_dict()
        return json.dumps(rest, default=str)

    @staticmethod
    def crear_json(j_son):
        nou = Encriptador()
        nou.clau = ast.literal_eval(json.loads(j_son)['clau'])
        nou.dada = ast.literal_eval(json.loads(j_son)['dada'])
        return nou

    @staticmethod
    def desencriptar(origen_encript, public_key):
        clau_dada = origen_encript['clau']
        retorn_encriptat = origen_encript['dada']
        desencriptador = PKCS1_OAEP.new(public_key)
        clau_simetrica = desencriptador.decrypt(clau_dada)
        key_simetric = Fernet(clau_simetrica)
        dada_desencriptada = key_simetric.decrypt(retorn_encriptat).decode()
        return dada_desencriptada


class Usuari:

    def __init__(self, id_usuari=None, nif=None, nom=None, cognom=None, public_key=None):
        self.id = id_usuari
        self.nif = nif
        self.nom = nom
        self.cognom = cognom
        self.tipus = USUARI
        self.public_key = public_key

    def to_dict(self):
        return collections.OrderedDict({
            'id': self.id,
            'nif': self.nif,
            'nom': self.nom,
            'cognom': self.cognom,
            'tipus': self.tipus,
            'public_key': self.str_publickey()})

    @staticmethod
    def crear_json(usuari_json):
        usuari = json.loads(usuari_json)
        id_usuari = usuari['id']
        nif = usuari['nif']
        nom = usuari['nom']
        cognom = usuari['cognom']
        tipus = usuari['tipus']
        public_key = RSA.importKey(usuari['public_key'])
        if tipus == ESTUDIANT:
            usuari = Estudiant(id_usuari, nif, nom, cognom, public_key)
        if tipus == PROFESSOR:
            usuari = Professor(id_usuari, nif, nom, cognom, public_key)
        return usuari

    # @staticmethod
    # def create_json(usuari_json):
    #     usuari = json.loads(usuari_json)
    #     id_usuari = usuari_json['id']
    #     nif = usuari_json['nif']
    #     nom = usuari_json['nom']
    #     cognom = usuari_json['cognom']
    #     tipus = usuari_json['tipus']
    #     public_key = RSA.importKey(usuari_json['public_key'])
    #     if tipus == ESTUDIANT:
    #         usuari = Estudiant(id_usuari, nif, nom, cognom, public_key)
    #     if tipus == PROFESSOR:
    #         usuari = Professor(id_usuari, nif, nom, cognom, public_key)
    #     return usuari

    def to_json(self):
        rest = self.to_dict()
        return json.dumps(rest, default=str)

    def str_publickey(self):
        return self.public_key.exportKey('PEM').decode('ascii')

    # def sign(self, data):
    #     h = SHA1.new(data)
    #     return binascii.hexlify(self._signatura.sign(h)).decode('ascii')


class Professor(Usuari):
    def __init__(self, id_usuari=None, nif=None, nom=None, cognom=None, public_key=None):
        super(Professor, self).__init__(id_usuari, nif, nom, cognom, public_key)
        self.tipus = PROFESSOR


class Estudiant(Usuari):
    def __init__(self, id_usuari=None, nif=None, nom=None, cognom=None, public_key=None):
        super(Estudiant, self).__init__(id_usuari, nif, nom, cognom, public_key)
        self.tipus = ESTUDIANT


class Document:
    def __init__(self, id_document=None, tipus=None, usuari=None, pdf=None, data_creacio=None):
        self.id_document = id_document
        self.data_creacio = datetime.now().isoformat()
        if data_creacio is not None:
            self.data_creacio = data_creacio
        self.tipus = tipus
        self.usuari = usuari
        self.pdf = pdf

    def to_dict(self):
        return collections.OrderedDict({
            'id_document': "Usuari",  # self.id_document,
            'data_creacio': self.data_creacio,
            'id_tipus': self.tipus,
            'usuari': self.usuari.to_json(),
            'pdf': self.pdf})

    def to_json(self):
        rest = self.to_dict()
        return json.dumps(rest, indent=4, sort_keys=True, default=str)


class Examen(Document):

    def __init__(self, id_document=None, professor=None, pdf=None, data_inicial=None, data_final=None,
                 data_creacio=None):
        super(Examen, self).__init__(id_document, 1, professor, pdf, data_creacio)
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.evaluacioExamen = None
        self.estudiants = []
        self.respostes = []

    @classmethod
    def create_json(cls, dades_json=None):
        dades = json.loads(dades_json)
        id_examen = dades['id_document']
        data_creacio = dades['data_creacio']
        data_inicial = dades['data_inicial']
        data_final = dades['data_final']
        professor = Usuari.crear_json(dades['professor'])
        pdf = ast.literal_eval(dades['pdf'])
        return cls(id_examen, professor, pdf, data_inicial, data_final, data_creacio)

    def afegir_estudiants(self, estudiant):
        self.estudiants.append(estudiant)

    @property
    def id_document_blockchain(self):
        return str(self.id_document) + "0001"

    def to_dict(self):
        llista_json = []
        for x in self.estudiants:
            estudiant_json = x.to_json()
            llista_json.append(estudiant_json)
        return collections.OrderedDict({
            'id_document': self.id_document,
            'data_creacio': self.data_creacio,
            'data_inicial': self.data_inicial,
            'data_final': self.data_final,
            'id_tipus': self.tipus,
            'professor': self.usuari.to_json(),
            'pdf': self.pdf,
            'estudiants': [llista_json]
        })


class RespostaExamen(Document):

    def __init__(self, id_resposta, id_examen=None, estudiant=None, pdf=None):
        if estudiant.tipus != ESTUDIANT:
            raise ValueError('Solament els estudiants poden crear respostes')
        super(RespostaExamen, self).__init__(id_resposta, 2, estudiant, pdf)
        self.id_examen = id_examen

    @property
    def id_document_blockchain(self):
        return str(self.id_document) + "0002"

    def to_dict(self):
        return collections.OrderedDict({
            'id_resposta': self.id_document,
            'id_examen': self.id_examen,
            'data_creacio': self.data_creacio,
            'id_tipus': self.tipus,
            'estudiant': self.usuari.to_json(),
            'pdf': self.pdf
        })


class EvaluacioExamen(Document):

    def __init__(self, id_resposta, id_examen=None, professor=None, pdf=None):
        try:
            if professor.tipus != PROFESSOR:
                raise ValueError('Solament els professors poden crear evaluacion')
        except ValueError:
            print(ValueError)
        super(EvaluacioExamen, self).__init__(id_resposta, 3, professor, pdf)
        self.id_examen = id_examen

    def to_dict(self):
        return collections.OrderedDict({
            'id_resposta': self.id_document,
            'id_examen': self.id_examen,
            'data_creacio': self.data_creacio,
            'id_tipus': self.tipus,
            'professor': self.usuari.to_json(),
            'pdf': self.pdf
        })


class Universitat:
    def __init__(self, nom, private_key, public_key):
        self.nom = nom
        self._private_key = private_key  # Creació de la clau privada
        self._public_key = public_key  # Creació de la clau pública que és part de la clau privada

    @property
    def private_key(self):
        return self._private_key

    @property
    def public_key(self):
        return self._public_key


class Transaccio:

    # Classe on guardem les dades de les transaccions
    def __init__(self, emissor=None, receptor=None, document=None):
        self.id_transaccio = 0
        self.emissor = emissor
        self.receptor = receptor
        self.id_document = 0
        self.data_creacio = datetime.now().isoformat()
        if document is not None:
            self.document = Encriptador(document, emissor.public_key)
            self.id_document = document.id_document_blockchain
        else:
            self.document = None
            self.id_document = 0

    @classmethod
    def crear_json(cls, dada):
        trans_json = json.loads(dada)
        id_transaccio = trans_json['id_transaccio']
        emissor = Usuari.crear_json(trans_json['emissor'])
        receptor = Usuari.crear_json(trans_json['receptor'])
        id_document = trans_json['id_document']
        data_creacio = trans_json['data_creacio']
        dada = Encriptador.crear_json(trans_json['document'])
        return cls.crear_mysql(id_transaccio, emissor, receptor, dada, id_document, data_creacio)

    @classmethod
    def crear_mysql(cls, id_trans=None, emissor=None, receptor=None, dada=None, id_document=None, data_creacio=None):
        trans = cls(emissor, receptor, None)
        trans.id_transaccio = id_trans
        trans.id_document = id_document
        trans.document = dada
        trans.data_creacio = data_creacio
        return trans

    def sign(self, data):
        h = SHA1.new(data)
        return binascii.hexlify(self._signatura.sign(h)).decode('ascii')

    def to_dict(self):
        return collections.OrderedDict({
            'id_transaccio': self.id_transaccio,
            'emissor': self.emissor.to_json(),
            'receptor': self.receptor.to_json(),
            'id_document': self.id_document,
            'document': self.document.to_json(),
            'data_creacio': self.data_creacio})

    def to_json(self):
        rest = self.to_dict()
        return json.dumps(rest, default=str)

    def sign_transaction(self):
        # return self.emissor.sign(str(self.to_dict()).encode('utf8'))
        block_json = self.to_json()
        return self.emissor.sign(block_json.encode(UTF_8))

    # def encriptar(self, public_key):
    #     key_simetric = Fernet.generate_key()
    #     encriptar_clau = PKCS1_OAEP.new(public_key)
    #     clau_simetrica = encriptar_clau.encrypt(key_simetric)
    #     examen_byte = self.to_json().encode("utf-8")
    #     encriptador = Fernet(key_simetric)
    #     document = encriptador.encrypt(examen_byte)
    #     retorn = {'clau': clau_simetrica, 'document': document}
    #     return retorn
    #
    # @staticmethod
    # def desencriptar(examen_encript, public_key):
    #     clau_examen = examen_encript['clau']
    #     examen_encriptat = examen_encript['document']
    #     desencriptador = PKCS1_OAEP.new(public_key)
    #     clau_simetrica = desencriptador.decrypt(clau_examen)
    #     key_simetric = Fernet(clau_simetrica)
    #     examen = key_simetric.decrypt(examen_encriptat).decode()
    #     return examen


# class TransaccioExamen(Transaccio):
#
#     def __init__(self, emissor=None, receptor=None, examen=None):
#         super().__init__(emissor, receptor, examen)


class Bloc:
    # Classe creació del bloc

    def __init__(self, index=None, trans=None, hash_bloc_anterior=None, universitat_public_key=None):
        self._index = index
        self.data_transaccio = trans.data_creacio
        self.id_emissor = trans.emissor.id
        self.id_receptor = trans.receptor.id
        self.id_document = trans.id_document
        self.transaccions = Encriptador(trans, universitat_public_key)
        self.hash_bloc_anterior = hash_bloc_anterior
        self.nonce = 0

    @property
    def index(self):
        return self._index

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def previous_block_hash(self):
        return self.hash_bloc_anterior

    @property
    def transaccio(self):
        return self._transaccio

    def to_dict(self):
        return collections.OrderedDict({
            'index': self._index,
            'timestamp': self.timestamp,
            'id_emissor': self.emissor.id,
            'id_receptor': self.receptor.id,
            'id_document': self.document.id,
            'transaccions': self.transaccions,
            'hash_bloc_anterior': self.hash_bloc_anterior})

    def calcular_hash(self):
        # Converteix el bloc en una cadena json i retorna el hash
        block_string = json.dumps(self.__dict__, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def guardar_bloc(self, my_db):
        id_bloc = self.timestamp
        timestamp = self.timestamp
        id_emissor = self.transaccio.emissor.id
        id_receptor = self.transaccio.receptor.id
        id_doc = self.transaccio.document.id_document_blockchain()
        transaccio = self.transaccio
        hash_bloc = self.calcular_hash()
        my_db.guardar_bloc(id_bloc, timestamp, id_emissor, id_receptor, id_doc, transaccio, hash_bloc)


class BlockchainUniversity:
    # Dificultat del hash
    dificultat = 2

    def __init__(self):
        self.transaccio_noconfirmades = []
        self.cadena = []
        self.crear_genesis_bloc()

    def crear_genesis_bloc(self):
        """
       Creacio del bloc Inicial.
        """
        emissor = Usuari("Genesis")
        receptor = Usuari("Genesis")
        document = Document("Genesis")
        transaccio = Transaccio(emissor, receptor, document)
        genesis_bloc = Bloc(0, transaccio, 0)
        genesis_bloc.hash = genesis_bloc.calcular_hash()
        self.cadena.append(genesis_bloc)

    @property
    def ultim_bloc(self):
        return self.cadena[-1]

    def afegir_bloc(self, bloc, hash_prova):
        """
        Una funció que afegeix el bloc a la cadena després de la verificació.
         La verificació inclou:
         * Block apunti al block anterior
         * Que hash_prova satisfà la dificultat prevista
        """
        hash_anterior = self.ultim_bloc.hash

        if hash_anterior != bloc.hash_bloc_anterior:
            return False

        if not self.es_prova_valida(bloc, hash_prova):
            return False

        bloc.hash = hash_prova
        self.cadena.append(bloc)
        return True

    @staticmethod
    def es_prova_valida(bloc, hash_bloc):
        """
        Comprovem si el hash del bloc és vàlid i satisfà els criteris de dificultat
        """
        return (hash_bloc.startswith('0' * BlockchainUniversity.dificultat) and
                hash_bloc == bloc.hash_correcte)

    @staticmethod
    def hash_correcte(bloc, bloc_hash):
        """
        Funció que prova diferents valors de nonce per obtenir un hash
        que compleix els nostres criteris de dificultat.
        """
        bloc.nonce = 0

        hash_calculat = bloc.calcular_hash()
        while not hash_calculat.startswith('0' * BlockchainUniversity.dificultat):
            bloc.nonce += 1
            hash_calculat = bloc.calcular_hash()

        return hash_calculat

    def afegir_nova_transaccio(self, transaccio):
        self.transaccio_noconfirmades.append(transaccio)

    def minat(self):
        """
    Aquesta funció serveix com a interfície per afegir la transacció pendent a la cadena de blocs afegint-les al bloc
         i esbrinar el hash.
        """
        if not self.transaccio_noconfirmades:
            return False

        ultim_bloc = self.ultim_bloc
        index = ultim_bloc.index + 1
        transactions = self.transaccio_noconfirmades
        hash_anterior = ultim_bloc.calcular_hash()
        new_bloc = Bloc(index, hash_anterior, transactions, )
        hash_actual = self.hash_correcte
        self.afegir_bloc(new_bloc, hash_actual)
        self.transaccio_noconfirmades = []
        return new_bloc.index

# class FitxersPdf:
#     OUTPUT_DIR = Path('data')
#
#
#     def llegirPdf(self):
# # read the binary signature
# with open(signature_file_name, 'rb') as f:
#     read_signature = f.read()

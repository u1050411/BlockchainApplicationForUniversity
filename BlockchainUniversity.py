import binascii
import collections
import hashlib
import json
from datetime import datetime

from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA

from CreateMysql import MySqlBloc

# from pandas.io import json

UTF_8 = 'utf8'
ESTUDIANT = 'estudiant'
PROFESSOR = 'professor'


class Factoria:

    def __init__(self):
        pass

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
    def build_examen_from_db(my_db, id_document):
        if my_db.existeix_examen(id_document):
            id_document, id_professor, data_examen, data_inicial, data_final, pdf = my_db.importar_examen(id_document)
            professor = Factoria.build_usuari_from_db(my_db, id_professor)
            examen = Examen(id_document, professor, pdf, data_inicial, data_final)
            estudiants = my_db.importar_estudiants_examen(id_document)
            if estudiants is not None:
                for id_estudiant in estudiants:
                    estudiant = Factoria.build_usuari_from_db(my_db, id_estudiant[0])
                    examen.estudiants.append(estudiant)
                respostes = my_db.importar_respostes(id_document)
                for sql_resposta in respostes:
                    id_resposta, data_creacio, id_usuari, pdf = sql_resposta
                    usuari = Factoria.build_usuari_from_db(my_db, id_estudiant)
                    resposta = RespostaExamen(id_resposta, id_document, usuari, pdf)
                    resposta.data_creacio = data_creacio
                    examen.respostes.append(resposta)
            return examen
        return None

    @staticmethod
    def build_resposta_examen_from_db(my_db, id_document, id_resposta):
        resposta_importar = my_db.importar_resposta(id_document, id_resposta)
        (id_resposta, time, id_usuari, pdf) = resposta_importar[0]
        usuari = Factoria.build_usuari_from_db(my_db, id_usuari)
        resposta = RespostaExamen(id_resposta, id_document, usuari, pdf)
        return resposta


class Usuari:

    def __init__(self, id_usuari=None, nif=None, nom=None, cognom=None, public_key=None):
        self.id = id_usuari
        self.nif = nif
        self.nom = nom
        self.cognom = cognom
        self.tipus = "Usuari"
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
    def create_json(usuari_json):
        id_usuari = usuari_json['id']
        nif = usuari_json['nif']
        nom = usuari_json['nom']
        cognom = usuari_json['cognom']
        tipus = usuari_json['tipus']
        public_key = RSA.importKey(usuari_json['public_key'])
        if tipus == ESTUDIANT:
            usuari = Estudiant(id_usuari, nif, nom, cognom, public_key)
        if tipus == PROFESSOR:
            usuari = Professor(id_usuari, nif, nom, cognom, public_key)
        return usuari

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
    def __init__(self, id_document=None, id_tipus=None, usuari=None, pdf=None):
        self.id_document = id_document
        self.data_creacio = datetime.now().isoformat()
        self.id_tipus = id_tipus
        self.usuari = usuari
        self.pdf = pdf

    @property
    def id_document_blockchain(self):
        pass

    def to_dict(self):
        return collections.OrderedDict({
            'id_document': "Usuari",  # self.id_document,
            'data_creacio': self.data_creacio,
            'id_tipus': self.id_tipus,
            'usuari': self.usuari.to_json(),
            'pdf': self.pdf})

    def to_json(self):
        rest = self.to_dict()
        return json.dumps(rest, default=str)


class Examen(Document):

    def __init__(self, id_document=None, professor=None, pdf=None, data_inicial=None, data_final=None):
        super(Examen, self).__init__(id_document, 1, professor, pdf, )
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.estudiants = []
        self.respostes = []

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
            'id_tipus': self.id_tipus,
            'usuari': self.usuari.to_json(),
            'pdf': self.pdf,
            'estudiants': [llista_json]
        })


class RespostaExamen(Document):

    def __init__(self, id_resposta, id_examen=None, usuari=None, pdf=None):
        super(RespostaExamen, self).__init__(id_resposta, 2, usuari, pdf, )
        self.id_examen = id_examen

    @property
    def id_document_blockchain(self):
        return str(self.id_resposta) + "0002"

    def to_dict(self):
        return collections.OrderedDict({
            'id_resposta': self.id_document,
            'id_examen': self.id_examen,
            'data_creacio': self.data_creacio,
            'id_tipus': self.id_tipus,
            'usuari': self.usuari.to_json(),
            'pdf': self.pdf
        })


class Universitat:
    def __init__(self, nom, private_key, public_key):
        self.nom = nom
        self._private_key = private_key  # Creació de la clau privada
        self._public_key = public_key  # Creació de la clau pública que és part de la clau privada


class Transaccio:

    # Classe on guardem les dades de les transaccions
    def __init__(self, emissor=None, receptor=None, document=None):
        self.id = 0
        self.emissor = emissor
        self.receptor = receptor
        self.document = document
        self._data_creacio = datetime.now().isoformat()

    def sign(self, data):
        h = SHA1.new(data)
        return binascii.hexlify(self._signatura.sign(h)).decode('ascii')

    @property
    def data_creacio(self):
        return self._data_creacio

    @data_creacio.setter
    def data(self, data_creacio):
        self._data_creacio = data_creacio

    # canviar a estructura json

    def to_dict(self):
        return collections.OrderedDict({
            'Emissor': self.emissor.to_json(),
            'Receptor': self.receptor.to_json(),
            'Document': self.document.id_document(),
            'Data': self.time})

    def display_transaccio(self):
        print(f"""sender: {self.emissor.id} 
-----
receptor: {self.receptor.id}
-----
value: {self.document.id_document()}
-----
time: {self.time}
-----
""")

    # Mètode que el emissor signa la transaccio

    def sign_transaction(self):
        # return self.emissor.sign(str(self.to_dict()).encode('utf8'))
        block_json = self.to_json()
        return self.emissor.sign(block_json.encode(UTF_8))

    def to_json(self):
        return json.dumps(self.to_dict, sort_keys=True, default=str)


# class TransaccioExamen(Transaccio):
#
#     def __init__(self, emissor=None, receptor=None, examen=None):
#         super().__init__(emissor, receptor, examen)


class Bloc:
    # Classe creació del bloc

    def __init__(self, index=None, trans=None, hash_bloc_anterior=None, ):
        self._index = index
        self._timestamp = datetime.now().isoformat()
        self.transaccions = trans
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

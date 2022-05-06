import binascii
import collections
import hashlib
import json
from datetime import datetime

from Crypto.Hash import SHA1

from CreateMysql import MySqlBloc

# from pandas.io import json

UTF_8 = 'utf8'
ESTUDIANT = 'estudiant'
PROFESSOR = 'professor'


class Factoria:

    def __init__(self):
        pass

    @staticmethod
    def build_usuari_from_db(my_db, id_usuari, tipus):
        if my_db.existeix('BlockchainUniversity', 'usuari', 'id', id_usuari):
            sql = f'select * from usuari where id = {id_usuari} LIMIT 1'
            usuari = (my_db.importar_sql(sql))
            nif = usuari[1]
            nom = usuari[2]
            cognom = usuari[3]
            public_key = my_db.clau_publica(id_usuari)
            if tipus == ESTUDIANT:
                estudiant = Estudiant(id_usuari, nif, nom, cognom, public_key)
                return estudiant
            elif tipus == PROFESSOR:
                professor = Professor(id_usuari, nif, nom, cognom, public_key)
                return professor
        return None

    @staticmethod
    def build_examen_from_db(my_db, num_document):
        id_document = MySqlBloc.dades_num(num_document)[0]
        if my_db.existeix('BlockchainUniversity', 'examen', 'id_document', id_document):
            sql = f'select `id_document`, `professor`, `data_examen`, `data_inicial`, `data_final`, `pdf`, `nota`  ' \
                  f'from `examen` where `id_document` = {id_document} LIMIT 1'
            id_document, professor, data_examen, data_inicial, data_final, pdf, nota = my_db.importar_sql(sql)
            id_examen, tipus = my_db.dades_num(id_document)
            if tipus == 1:
                examen = Examen(id_document, professor, pdf, data_inicial, data_final)
                sqlu = f'select `id_estudiant` from `estudiant_examen` where `id_document` = {id_document}'
                estudiants = my_db.importar_llista_sql(sqlu)
                if estudiants is not None:
                    for id_estudiant in estudiants:
                        estudiant = Factoria.build_usuari_from_db(my_db, id_estudiant, ESTUDIANT)
                        examen.estudiants.append(estudiant)

                    sqlr = f'select id_resposta, data_creacio, id_usuari, pdf  ' \
                           f'from `resposta_examen` where `id_document` = {id_document}'
                    respostes = my_db.importar_llista_sql(sqlr)
                    for sql_resposta in respostes:
                        id_resposta, data_creacio, id_usuari, pdf = sql_resposta
                        num_tipus = id_usuari[0]
                        if num_tipus == 2:
                            tipus = PROFESSOR
                        else:
                            tipus = ESTUDIANT
                        usuari = Factoria.build_usuari_from_db(my_db, id_estudiant, tipus)
                        resposta = RespostaExamen(id_resposta, usuari, pdf)
                        resposta.data_creacio = data_creacio
                        examen.respostes.append(resposta)
            return examen
        return None


class Usuari:

    def __init__(self, id_usuari=None, nif=None, nom=None, cognom=None, public_key=None):
        self.id = id_usuari
        self.nif = nif
        self.nom = nom
        self.cognom = cognom
        self.public_key = public_key

    # def sign(self, data):
    #     h = SHA1.new(data)
    #     return binascii.hexlify(self._signatura.sign(h)).decode('ascii')


class Professor(Usuari):
    pass


class Estudiant(Usuari):
    pass


class Universitat:
    def __init__(self, nom, private_key, public_key):
        self.nom = nom
        self._private_key = private_key  # Creació de la clau privada
        self._public_key = public_key  # Creació de la clau pública que és part de la clau privada


class Transaccio:

    # Classe on guardem les dades de les transaccions
    def __init__(self, emissor=None, receptor=None, document=None):
        self.emissor = emissor
        self.receptor = receptor
        self.document = document
        self._time = datetime.now().isoformat()

    def sign(self, data):
        h = SHA1.new(data)
        return binascii.hexlify(self._signatura.sign(h)).decode('ascii')

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        self._time = time

    # canviar a estructura json

    def to_dict(self):
        return collections.OrderedDict({
            'Emissor': self.emissor.id,
            'Receptor': self.receptor.id,
            'Document': self.document.numdoc(),
            'Data': self.time})

    def display_transaccio(self):
        print(f"""sender: {self.emissor.id} 
-----
receptor: {self.receptor.id}
-----
value: {self.document.numdoc()}
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
        return json.dumps(self.__dict__, sort_keys=True, default=str)


class TransaccioExamen(Transaccio):

    def __init__(self, emissor=None, receptor=None, document=None):
        super().__init__(emissor, receptor, document)


class Bloc:
    # Classe creació del bloc

    def __init__(self, index=None, hash_bloc_anterior=None, transaccio=None):
        self._index = index
        self._timestamp = datetime.now().isoformat()
        self.hash_bloc_anterior = hash_bloc_anterior
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
        return self.hash_bloc_anterior

    @property
    def transaccio(self):
        return self._transaccio

    def calcular_hash(self):
        # Converteix el bloc en una cadena json i retorna el hash
        block_string = json.dumps(self.__dict__, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()


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
        genesis_bloc = Bloc(0, '0', [])
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


class Document:
    def __init__(self, id_document=None, id_tipus=None, usuari=None, pdf=None):
        self.id_document = id_document
        self.id_tipus = id_tipus
        self.usuari = usuari
        self.pdf = pdf


class Examen(Document):

    def __init__(self, id_document=None, professor=None, pdf=None, data_inicial=None, data_final=None):
        self.id_document = id_document
        self.data_creacio = datetime.now().isoformat()
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.professor = professor
        self.estudiants = []
        self.respostes = []
        self.pdf = pdf
        self.nota = 0

    def afegir_estudiants(self, estudiant):
        self.estudiants.append(estudiant)

    @staticmethod
    def seguent_numero(my_db):
        sql = f"select Max(`id_document`) from `examen`"
        num_maxim = my_db.importar_sql(sql)[0]
        id_document, tipus = my_db.dades_num(num_maxim)
        return id_document + 1

    # sembla que no fa falta
    # def afegir_resposta(self, resposta_examen):
    #     self.respostes.append(resposta_examen)


class RespostaExamen:

    def __init__(self, id_resposta=None, usuari=None, pdf=None):
        self.id_resposta = id_resposta
        self.usuari = usuari
        self.data_creacio = datetime.now().isoformat()
        self.pdf = pdf


    @staticmethod
    def seguent_numero(my_db, id_document):
        sql = f"select Max(`id_resposta`) from `resposta_examen` where `id_document` = {id_document}"
        num_maxim = my_db.importar_sql(sql)[0]
        if num_maxim is None:
            id_document = 0
        else:
            id_document, tipus = my_db.dades_num(num_maxim)
        return id_document + 1

# class FitxersPdf:
#     OUTPUT_DIR = Path('data')
#
#
#     def llegirPdf(self):
# # read the binary signature
# with open(signature_file_name, 'rb') as f:
#     read_signature = f.read()

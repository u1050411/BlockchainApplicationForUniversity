import ast
import base64
import binascii
import collections
import hashlib
import json
from datetime import datetime

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA1, SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from cryptography.fernet import Fernet
from Crypto.Hash import SHA
from cryptography.hazmat.primitives.hashes import SHA256

UTF_8 = 'utf8'
ESTUDIANT = 'estudiant'
PROFESSOR = 'professor'
USUARI = 'usuari'


class Factoria:

    def __init__(self):
        pass

    @staticmethod
    def to_json(dada):
        dades = dada
        rest = dades.to_dict()
        return json.dumps(rest, indent=4, sort_keys=True, default=str)

    @staticmethod
    def recuperar_fitxer(nom_fitxer):
        pdf_file = open(nom_fitxer, "rb")
        save_pdf = base64.b64encode(pdf_file.read())
        pdf_file.close()
        return save_pdf

    @staticmethod
    def guardar_fitxer(nom_directory, pdf):
        pdf_file = base64.b64decode(pdf, validate=True)
        with open(nom_directory, "wb") as f:
            f.write(pdf_file)

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
    def build_assignatura_from_db(my_db, id_assignatura):
        assignatura_db = my_db.importar_assignatura(id_assignatura)
        if assignatura_db is not None:
            id_assignatura, nom, id_professor = assignatura_db
            professor = Factoria.build_usuari_from_db(my_db, id_professor)
            return Assignatura(id_assignatura, nom, professor)

        return None

    @staticmethod
    def build_usuari_from_db(my_db, id_usuari):
        if my_db.existeix_usuari(id_usuari):
            usuari_db = my_db.importar_usuari(id_usuari)
            if usuari_db is not None:
                id_us, tipus, nif, nom, cognom, public_key_str, contrasenya, email = usuari_db
                public_key = RSA.importKey(public_key_str)
                if tipus == ESTUDIANT:
                    estudiant = Estudiant(id_usuari, nif, nom, cognom, public_key, contrasenya, email)
                    return estudiant
                elif tipus == PROFESSOR:
                    professor = Professor(id_usuari, nif, nom, cognom, public_key, contrasenya, email)
                    return professor
        return None

    @staticmethod
    def build_pdf_from_db(my_db, id_pdf):
        id_pdf, data_creacio, id_usuari, pdf, nom_fitxer = my_db.importar_pdf(id_pdf)
        usuari = Factoria.build_usuari_from_db(my_db, id_usuari)
        classe_pdf = Pdf.crear_mysql(id_pdf, nom_fitxer, usuari, pdf, data_creacio)
        return classe_pdf

    @staticmethod
    def build_examen_from_db(my_db, id_document, per_estudiant=None):
        if my_db.existeix_examen(id_document):
            id_document, id_professor, data_examen, data_inicial, data_final, pdf, id_assignatura = my_db.importar_examen(id_document)
            professor = Factoria.build_usuari_from_db(my_db, id_professor)
            assignatura = Factoria.build_assignatura_from_db(my_db, id_assignatura)
            examen = Examen(id_document, professor, pdf, data_inicial, data_final, assignatura)
            if per_estudiant is None:
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
    def build_bloc_from_db(my_db, id_bloc):
        bloc_db = my_db.importar_bloc(id_bloc)
        (id_bloc, data_transaccio, id_emissor, id_receptor, id_document, transaccio_encriptat, hash_bloc) = bloc_db
        uni = Factoria.build_universitat_from_db(my_db)
        transaccio_json = Encriptador.crear_json(transaccio_encriptat)
        transaccio = Transaccio.crear_json(transaccio_json.desencriptar(uni.private_key))
        bloc = Bloc(transaccio, "asfassdfsadfsa", uni.public_key)
        bloc.id_bloc = id_bloc
        return bloc

    @staticmethod
    def build_ultim_bloc_from_db(my_db):
        (id_bloc, data, transaccio, hash_anterior) = my_db.ultim_bloc()
        bloc = Bloc.crear_msql(id_bloc, data, transaccio, hash_anterior)
        return bloc

    @staticmethod
    def build_transaccio_from_db(my_db):
        trans_db = my_db.importar_transaccions()
        (id_trans, emissor, receptor, dada_json, id_document, data_creacio) = trans_db
        emissor = Factoria.build_usuari_from_db(my_db, emissor)
        receptor = Factoria.build_usuari_from_db(my_db, receptor)
        dada = Document.crear_json(dada_json)
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
            self.nom = None
            self.clau = None
            self.dada = None
            self.sign = None
        else:
            key_simetric = Fernet.generate_key()
            encriptar_clau = PKCS1_OAEP.new(public_key)
            self.clau = encriptar_clau.encrypt(key_simetric)
            data_json = Factoria.to_json(dada)
            dada_byte = data_json.encode("utf-8")
            encriptador = Fernet(key_simetric)
            self.dada = encriptador.encrypt(dada_byte)
            self.sign = None
            self.nom = None

    def signar(self, private_key=None):
        h = SHA.new(self.dada)
        signer = PKCS1_PSS.new(private_key)
        self.sign = signer.sign(h)

    def verificar_sign(self, public_key=None):
        h = SHA.new(self.dada)
        verifier = PKCS1_PSS.new(public_key)
        return verifier.verify(h, self.sign)

    # @staticmethod
    # def crear_json(dada_json):
    #     encript_json = json.loads(dada_json)
    #     clau = encript_json['clau']
    #     dada = encript_json['dada']
    #     dada_encriptat = Encriptador()
    #     dada_encriptat.dada = dada
    #     dada_encriptat.clau = clau
    #     return dada_encriptat

    # def get_dada(self, private_key):
    #     desencriptador = PKCS1_OAEP.new(private_key)
    #     clau_simetrica = desencriptador.decrypt(self.clau)
    #     key_simetric = Fernet(clau_simetrica)
    #     dada_desencriptada = key_simetric.decrypt(self.dada).decode()
    #     return dada_desencriptada

    def to_dict(self):
        return collections.OrderedDict({
            'clau': self.clau,
            'dada': self.dada,
            'sign': self.sign,
            'nom': self.nom
        })

    @staticmethod
    def crear_json(j_son):
        nou = Encriptador()
        nou.clau = ast.literal_eval(json.loads(j_son)['clau'])
        nou.dada = ast.literal_eval(json.loads(j_son)['dada'])
        nou.sign = ast.literal_eval(json.loads(j_son)['sign'])
        nou.nom = json.loads(j_son)['nom']
        return nou

    def desencriptar(self, privat_key):
        desencriptador = PKCS1_OAEP.new(privat_key)
        clau_simetrica = desencriptador.decrypt(self.clau)
        key_simetric = Fernet(clau_simetrica)
        dada_desencriptada = key_simetric.decrypt(self.dada).decode()
        return dada_desencriptada



class Assignatura:
    def __init__(self, id_assignatura=0, nom=None, professor=None):
        self.id = id_assignatura
        self.nom = nom
        self.professor = professor
        self.alumnes = list()

    def afegir_alumnes(self, alumne):
        self.alumnes.append(alumne)


class Usuari:

    def __init__(self, id_usuari=None, nif=None, nom=None, cognom=None, public_key=None, contrasenya=None, email=None):
        self.id = id_usuari
        self.nif = nif
        self.nom = nom
        self.cognom = cognom
        self.contrasenya = contrasenya
        self.email = email
        self.tipus = USUARI
        self.public_key = public_key


    def to_dict(self):
        return collections.OrderedDict({
            'id': self.id,
            'nif': self.nif,
            'nom': self.nom,
            'cognom': self.cognom,
            'tipus': self.tipus,
            'public_key': self.str_publickey(),
            'contrasenya': self.contrasenya,
            'email': self.email

        })

    @staticmethod
    def crear_json(usuari_json):
        usuari = json.loads(usuari_json)
        id_usuari = usuari['id']
        nif = usuari['nif']
        nom = usuari['nom']
        cognom = usuari['cognom']
        tipus = usuari['tipus']
        contrasenya = usuari['contrasenya']
        email = usuari['email']
        public_key = RSA.importKey(usuari['public_key'])
        if tipus == ESTUDIANT:
            usuari = Estudiant(id_usuari, nif, nom, cognom, public_key, contrasenya)
        if tipus == PROFESSOR:
            usuari = Professor(id_usuari, nif, nom, cognom, public_key, contrasenya)
        return usuari

    def llista_pdf(self, my_db):
        llista = my_db.importar_pdf_usuari(self)
        llista_pdfs = list()
        for x in llista:
            id_int = x[0]
            classe_pdf = Factoria.build_pdf_from_db(my_db, id_int)
            llista_pdfs.append(classe_pdf)
        return llista_pdfs

    def importar_examens(self, my_db):
        pass

    def to_json(self):
        rest = self.to_dict()
        return json.dumps(rest, default=str)

    def str_publickey(self):
        return self.public_key.exportKey('PEM').decode('ascii')


class Professor(Usuari):
    def __init__(self, id_usuari=None, nif=None, nom=None, cognom=None, public_key=None, contrasenya=None, email=None):
        super(Professor, self).__init__(id_usuari, nif, nom, cognom, public_key, contrasenya, email)
        self.tipus = PROFESSOR

    def llista_alumnes(self, my_db):
        llista = my_db.importar_estudiants_professor(self)
        llista_alumnes = list()
        for x in llista:
            estudiant = Factoria.build_usuari_from_db(my_db, x)
            llista_alumnes.append(estudiant)
        return llista_alumnes

    def llista_examens(self, my_db):
        llista = my_db.importar_examens_professor(self)
        llista_examens = list()
        for x in llista:
            llista_examens.append(x)
        return llista_examens

    def importar_examens(self, my_db):
        return my_db.importar_examens_professor(self)

    def get_assignatura(self, my_db):
        id_assignatura = my_db.importar_assignatura_professor(self)
        assignatura = Factoria.build_assignatura_from_db(my_db, id_assignatura[0])
        return assignatura


class Estudiant(Usuari):
    def __init__(self, id_usuari=None, nif=None, nom=None, cognom=None, public_key=None, contrasenya=None, email=None):
        super(Estudiant, self).__init__(id_usuari, nif, nom, cognom, public_key, contrasenya, email)
        self.tipus = ESTUDIANT

    def importar_examens(self, my_db):
        return my_db.importar_examens_estudiant(self)


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
            'usuari': Factoria.to_json(self.usuari),
            'pdf': self.pdf})

    @property
    def id_document_blockchain(self):
        return str(self.id_document) + "0000"

    @classmethod
    def crear_json(cls, dades_json=None):
        trans_json = json.loads(dades_json)
        if (trans_json['id_tipus']) == 0:
            return Pdf.crear_json(dades_json)
        if (trans_json['id_tipus']) == 1:
            return Examen.crear_json(dades_json)
        if (trans_json['id_tipus']) == 2:
            return RespostaExamen.crear_json(dades_json)



class Pdf(Document):

    def __init__(self, id_document=None, nom_fitxer=None, usuari=None, pdf=None):
        super(Pdf, self).__init__(id_document, 0, usuari, pdf)
        self.nom_fitxer = nom_fitxer

    @property
    def id_document_blockchain(self):
        return str(self.id_document) + "0000"

    @classmethod
    def crear_mysql(cls, id_document=None, nom_fitxer=None, usuari=None, pdf=None, data_creacio=None):
        classe_pdf = cls(id_document, nom_fitxer, usuari, pdf)
        if classe_pdf:
            classe_pdf.data_creacio = data_creacio
        return classe_pdf

    @classmethod
    def crear_json(cls, dades_json=None):
        dades = json.loads(dades_json)
        id_examen = dades['id_document']
        data_creacio = dades['data_creacio']
        data_inicial = dades['data_inicial']
        data_final = dades['data_final']
        professor = Usuari.crear_json(dades['professor'])
        pdf = ast.literal_eval(dades['pdf'])
        return cls(id_examen, professor, pdf, data_inicial, data_final, data_creacio)


class Examen(Document):

    def __init__(self, id_document=None, professor=None, pdf=None, data_inicial=None, data_final=None,
                 data_creacio=None, assignatura=None):
        super(Examen, self).__init__(id_document, 1, professor, pdf, data_creacio)
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.evaluacioExamen = None
        self.estudiants = []
        self.respostes = []
        self.assignatura = assignatura

    @classmethod
    def crear_json(cls, dades_json=None):
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
        return int(str(self.id_document) + "0001")

    def to_dict(self):
        llista_json = []
        for x in self.estudiants:
            estudiant_json = Factoria.to_json(x)
            llista_json.append(estudiant_json)
        return collections.OrderedDict({
            'id_document': self.id_document,
            'data_creacio': self.data_creacio,
            'data_inicial': self.data_inicial,
            'data_final': self.data_final,
            'id_tipus': self.tipus,
            'professor': Factoria.to_json(self.usuari),
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
            'estudiant': Factoria.to_json(self.usuari),
            'pdf': self.pdf
        })

    @classmethod
    def crear_json(cls, dades_json=None):
        dades = json.loads(dades_json)
        id_resposta = dades['id_resposta']
        id_examen = dades['id_examen']
        data_creacio = dades['data_creacio']
        id_tipus = dades['id_tipus']
        estudiant = Usuari.crear_json(dades['estudiant'])
        pdf = ast.literal_eval(dades['pdf'])
        resposta = cls(id_resposta, id_examen, estudiant, pdf)
        resposta.data_creacio = data_creacio
        resposta.tipus = id_tipus
        return resposta


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
            'professor': Factoria.to_json(self.usuari),
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
        self.id_document = document.id_document_blockchain
        self.data_creacio = datetime.now().isoformat()
        self.document = Factoria.to_json(document)

    @classmethod
    def crear_json(cls, dada):
        trans_json = json.loads(dada)
        id_transaccio = trans_json['id_transaccio']
        emissor = Usuari.crear_json(trans_json['emissor'])
        receptor = Usuari.crear_json(trans_json['receptor'])
        id_document = trans_json['id_document']
        data_creacio = trans_json['data_creacio']
        dada = Document.crear_json(trans_json['document'])
        return cls.crear_mysql(id_transaccio, emissor, receptor, dada, id_document, data_creacio)

    @classmethod
    def crear_mysql(cls, id_trans=None, emissor=None, receptor=None, dada=None, id_document=None, data_creacio=None):
        trans = cls(emissor, receptor, dada)
        trans.id_transaccio = id_trans
        trans.id_document = id_document
        trans.data_creacio = data_creacio
        return trans

    # def sign(self, data):
    #     h = SHA1.new(data)
    #     return binascii.hexlify(self._signatura.sign(h)).decode('ascii')

    def to_dict(self):
        return collections.OrderedDict({
            'id_transaccio': self.id_transaccio,
            'emissor': Factoria.to_json(self.emissor),
            'receptor': Factoria.to_json(self.receptor),
            'id_document': self.id_document,
            'document': self.document,
            'data_creacio': self.data_creacio})

    # def to_json(self):
    #     rest = self.to_dict()
    #     return json.dumps(rest, default=str)

    # def sign_transaction(self):
    #     # return self.emissor.sign(str(self.to_dict()).encode('utf8'))
    #     block_json = Factoria.to_json(self)
    #     return self.emissor.sign(block_json.encode(UTF_8))


class Bloc:
    # Classe creació del bloc
    def __init__(self, id=None, trans=None, hash_bloc_anterior=None, my_db=None):
        if trans:
            self.id = id
            self.data_bloc = datetime.now().isoformat()
            uni = Factoria.build_universitat_from_db(my_db)
            self.transaccio = Encriptador(trans, uni.public_key)
            self.transaccio.signar(uni.private_key)
            self.transaccio.nom = uni.nom
            self.transaccio = Factoria.to_json(self.transaccio)
            self.hash_bloc_anterior = hash_bloc_anterior
        else:
            self.id = 0
            self.data_bloc = None
            self.transaccio = None
            self.hash_bloc_anterior = None

    @classmethod
    def crear_json(cls, bloc_json):
        new_bloc = cls()
        new_bloc.id = bloc_json['id']
        new_bloc.data_bloc = ['data_bloc']
        new_bloc.transaccio = bloc_json['transaccions']
        new_bloc.hash_bloc_anterior = bloc_json['hash_bloc_anterior']
        return new_bloc

    @classmethod
    def crear_msql(cls, id_bloc, data_bloc, transaccio, hash_anterior):
        new_bloc= cls()
        new_bloc.id = id_bloc
        new_bloc.data_bloc = data_bloc
        new_bloc.transaccio = transaccio
        new_bloc.hash_bloc_anterior = hash_anterior
        return new_bloc

    def to_dict(self):
        return collections.OrderedDict({
            'id': self.id,
            'transaccions': self.transaccio,
            'data_bloc':  self.data_bloc,
            'hash_bloc_anterior': self.hash_bloc_anterior})


    def calcular_hash(self):
        # Converteix el bloc en una cadena json i retorna el hash
        block_string = Factoria.to_json(self)
        return hashlib.sha256(block_string.encode()).hexdigest()


class BlockchainUniversity:

    def __init__(self, my_db):
        self.my_db = my_db

    def crear_genesis_bloc(self):
        """
       Creacio del bloc Inicial.
        """
        public_key = RSA.generate(1024).publickey()
        genesis = Estudiant('Genesis', 'Genesis', 'Genesis', "Genesis", public_key, "Genesis")
        pdf = base64.b64encode("Genesis".encode())
        doc = Document(0, 0, genesis, pdf)
        transaccio = Transaccio(genesis, genesis, doc)
        genesis_bloc = Bloc(0, transaccio, 0, self.my_db)
        genesis_bloc.hash = genesis_bloc.calcular_hash()
        genesis_bloc.data_bloc = datetime.now().isoformat()
        self.my_db.guardar_bloc_dades(genesis_bloc)

    def afegir_bloc_extern(self, bloc):
        """
        Una funció que afegeix el bloc a la cadena després de la verificació.
         La verificació inclou:
         * Block apunti al block anterior
         * Que vingui de una font valida
        """
        bloc = bloc.crear_json(bloc)
        ultim_bloc = self.my_db.ultim_bloc()
        if bloc.transaccio.verificar:
            if bloc.hash_bloc_anterior == ultim_bloc.calcular_hash():
                if bloc.id == ultim_bloc.id + 1:
                    self.my_db.guardar_bloc_dades(bloc)
                    return False
        return False

    def afegir_nova_transaccio(self, transaccio):
        self.transaccio_noconfirmades.append(transaccio)


    def minat(self):
        """
    Aquesta funció serveix com a interfície per afegir la transacció pendent a la cadena de blocs afegint-les al bloc
         i esbrinar el hash.
        """
        if self.my_db.existeix_alguna_transaccio():
            transaccio = Factoria.build_transaccio_from_db(self.my_db)
            if transaccio:
                emissor = transaccio.emissor
                ultim_bloc = Factoria.build_ultim_bloc_from_db(self.my_db)
                index = ultim_bloc.id + 1
                hash_anterior = ultim_bloc.calcular_hash()
                new_bloc = Bloc(index, transaccio, hash_anterior, self.my_db)

                self.my_db.guardar_bloc(new_bloc, emissor)
                self.my_db.esborrar_transaccio(transaccio.id_transaccio)
                return self.minat()






import ast
import base64
import collections
import hashlib
import json
from datetime import datetime
import simple_websocket

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from cryptography.fernet import Fernet
from collections import Counter

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
        return Factoria.build_universitat_from_id_db(my_db, 1)

    @staticmethod
    def build_universitat_from_db_ip(my_db, ip):
        my_db.importar_universitat_ip(ip)
        return Factoria.build_universitat_from_id_db(my_db, 1)

    @staticmethod
    def build_all_universitat_from_db(my_db):
        universiat_db = my_db.importar_universitats()
        llista = list()
        global id_universitat
        for x in universiat_db:
            id_universitat, nom, ip, private_key_str, public_key_str = x
            if id_universitat != 1:
                public_key = RSA.importKey(public_key_str)
                llista.append(Universitat(nom, None, public_key, id_universitat, ip))
        return llista

    @staticmethod
    def build_universitat_from_id_db(my_db, id):
        universiat_db = my_db.importar_universitat_id(id)
        if universiat_db is not None:
            id_universitat, nom, ip, private_key_str, public_key_str = universiat_db
            public_key = RSA.importKey(public_key_str)
            private_key = RSA.importKey(private_key_str)
            return Universitat(nom, private_key, public_key, id_universitat, ip)
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
            id_document, id_professor, data_examen, data_inicial, data_final, pdf, id_assignatura = my_db.importar_examen(
                id_document)
            professor = Factoria.build_usuari_from_db(my_db, id_professor)
            assignatura = Factoria.build_assignatura_from_db(my_db, id_assignatura)
            examen = Examen(id_document, professor, pdf, data_inicial, data_final, data_examen, assignatura)
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
                            examen.avaluacioExamen = AvaluacioExamen(id_resposta, id_document, usuari, pdf)
                            examen.avaluacioExamen.data_creacio = data_creacio
                        elif usuari.tipus == ESTUDIANT:
                            resposta = RespostaExamen(id_resposta, id_document, usuari, pdf)
                            resposta.data_creacio = data_creacio
                            examen.respostes.append(resposta)
            return examen
        return None

    @staticmethod
    def build_bloc_from_db(my_db, id_bloc):
        bloc_db = my_db.importar_bloc(id_bloc)
        (id_bloc, data_bloc, transaccio, signatura, hash_anterior) = bloc_db
        bloc = Bloc.crear_msql(id_bloc, data_bloc, transaccio, signatura, hash_anterior)
        return bloc

    @staticmethod
    def build_ultim_bloc_from_db(my_db):
        (id_bloc, data, transaccio, signar, hash_anterior) = my_db.ultim_bloc()
        if id_bloc:
            bloc = Bloc.crear_msql(id_bloc, data, transaccio, signar, hash_anterior)
            return bloc
        else:
            return None

    @staticmethod
    def build_cadena_blocs(my_db):
        cadena_id = my_db.importar_cadena_blocs_desc()
        cadena = list()
        for id_bloc in cadena_id:
            bloc = Factoria.build_bloc_from_db(my_db, id_bloc)
            cadena.append(bloc)
        return cadena


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
    def build_id_resposta_alumne_from_db(my_db, id_resposta):
        resposta_importar = my_db.importar_resposta(id_resposta)
        (id_resposta, id_document, time, id_usuari, pdf, nota) = resposta_importar[0]
        usuari = Factoria.build_usuari_from_db(my_db, id_usuari)
        examen = Factoria.build_examen_from_db(my_db, id_document)
        return RespostaExamen(id_resposta, examen, usuari, pdf, nota)

    @staticmethod
    def build_avaluacio_from_db(my_db, id_avaluacio):
        avaluacio_importar = my_db.importar_avaluacio(id_avaluacio)
        (id_avaluacio, id_resposta, id_professor, id_estudiant, pdf, nota) = avaluacio_importar[0]
        resposta = Factoria.build_id_resposta_alumne_from_db(my_db, id_resposta)
        professor = Factoria.build_usuari_from_db(my_db, id_professor)
        estudiant = Factoria.build_usuari_from_db(my_db, id_estudiant)
        return AvaluacioExamen(resposta, professor, estudiant, pdf, nota, id_avaluacio)


@staticmethod
def build_avaluacio_examen_from_db(my_db, id_examen, id_resposta):
    resposta = Factoria.build_resposta_examen_from_db(my_db, id_examen, id_resposta)
    if resposta.usuari.tipus != PROFESSOR:
        raise ValueError('Amb aquest id no hi ha una avaluacio')
    return resposta


class Encriptador:

    def __init__(self, dada=None, public_key=None):
        if dada is None:
            # self.nom = None
            self.clau = None
            self.dada = None
            # self.sign = None
        else:
            key_simetric = Fernet.generate_key()
            encriptar_clau = PKCS1_OAEP.new(public_key)
            self.clau = encriptar_clau.encrypt(key_simetric)
            data_json = Factoria.to_json(dada)
            dada_byte = data_json.encode("utf-8")
            encriptador = Fernet(key_simetric)
            self.dada = encriptador.encrypt(dada_byte)
            # self.sign = None
            # self.nom = None

    @staticmethod
    def signar(dada, private_key=None):
        h = SHA.new(dada)
        h1 = SHA.new(dada)
        public_key = private_key.publickey()
        signer = PKCS1_PSS.new(private_key)
        verifier2 = PKCS1_PSS.new(public_key)
        signature = signer.sign(h)
        if verifier2.verify(h1, signature):
            print("Verificado")
        return signature

    @staticmethod
    def verificar_sign(dada, signatura, public_key=None):
        h = SHA.new(dada)
        verifier = PKCS1_PSS.new(public_key)
        return verifier.verify(h, signatura)

    def to_dict(self):
        return collections.OrderedDict({
            'clau': self.clau,
            'resposta': self.dada
            # 'sign': self.sign,
            # 'nom': self.nom
        })

    @staticmethod
    def crear_json(j_son):
        nou = Encriptador()
        nou.clau = ast.literal_eval(json.loads(j_son)['clau'])
        nou.dada = ast.literal_eval(json.loads(j_son)['resposta'])
        # nou.sign = ast.literal_eval(json.loads(j_son)['sign'])
        # nou.nom = json.loads(j_son)['nom']
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

    # Importa les respostes que han enviat els alumnes de la seva asignatura
    def importar_examens(self, my_db):
        llista_id = my_db.importar_id_respostes_professor(self)
        llista = list()
        for x in llista_id:
            resposta = Factoria.build_id_resposta_alumne_from_db(my_db, x)
            llista.append(resposta)
        return llista

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
        if (trans_json['id_tipus']) == 3:
            return AvaluacioExamen.crear_json(dades_json)


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
        data_creacio = datetime.strptime(dades['data_creacio'], '%y-%m-%d %H:%M:%S')
        data_inicial = datetime.strptime(dades['data_inicial'], '%Y-%m-%d %H:%M:%S')
        data_final = datetime.strptime(dades['data_final'], '%Y-%m-%d %H:%M:%S')
        professor = Usuari.crear_json(dades['professor'])
        pdf = ast.literal_eval(dades['pdf'])
        return cls(id_examen, professor, pdf, data_inicial, data_final, data_creacio)


class Examen(Document):

    def __init__(self, id_document=None, professor=None, pdf=None, data_inicial=None, data_final=None,
                 data_creacio=None, assignatura=None):
        super(Examen, self).__init__(id_document, 1, professor, pdf, data_creacio)
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.avaluacioExamen = None
        self.estudiants = []
        self.respostes = []
        self.assignatura = assignatura

    @classmethod
    def crear_json(cls, dades_json=None):
        dades = json.loads(dades_json)
        id_examen = dades['id_document']
        data_creacio = dades['data_creacio'],
        data_inicial = dades['data_inicial'],
        data_final = dades['data_inicial'],
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

    def __init__(self, id_resposta, examen=None, estudiant=None, pdf=None, nota=0):
        super(RespostaExamen, self).__init__(id_resposta, 2, estudiant, pdf)
        self.examen = examen
        self.nota = nota

    @property
    def id_document_blockchain(self):
        return str(self.id_document) + "0002"

    def to_dict(self):
        return collections.OrderedDict({
            'id_resposta': self.id_document,
            'examen': Factoria.to_json(self.examen),
            'data_creacio': self.data_creacio,
            'id_tipus': self.tipus,
            'estudiant': Factoria.to_json(self.usuari),
            'pdf': self.pdf
        })

    @classmethod
    def crear_json(cls, dades_json=None):
        dades = json.loads(dades_json)
        id_resposta = dades['id_resposta']
        id_examen = Examen.crear_json(dades['examen'])
        data_creacio = dades['data_creacio'],
        id_tipus = dades['id_tipus']
        estudiant = Usuari.crear_json(dades['estudiant'])
        pdf = ast.literal_eval(dades['pdf'])
        resposta = cls(id_resposta, id_examen, estudiant, pdf)
        resposta.data_creacio = data_creacio
        resposta.tipus = id_tipus
        return resposta


class AvaluacioExamen(Document):

    def __init__(self, resposta=None, professor=None, estudiant=None, pdf=None, nota=None, id_avaluacio=0):
        super(AvaluacioExamen, self).__init__(id_avaluacio, 3, professor, pdf)
        self.resposta = resposta
        self.estudiant = estudiant
        if nota is None:
            self.nota = 0
        else:
            self.nota = nota

    def to_dict(self):
        return collections.OrderedDict({
            'id_avaluacio': self.id_document,
            'resposta': Factoria.to_json(self.resposta),
            'id_tipus': self.tipus,
            'data_creacio': self.data_creacio,
            'professor': Factoria.to_json(self.usuari),
            'estudiant': Factoria.to_json(self.estudiant),
            'pdf': self.pdf,
            'nota': self.nota
        })

    @property
    def id_document_blockchain(self):
        return str(self.id_document) + "0003"

    @classmethod
    def crear_json(cls, dades_json=None):
        dades = json.loads(dades_json)
        id_avaluacio = dades['id_avaluacio']
        resposta = RespostaExamen.crear_json(dades['resposta'])
        id_tipus = dades['id_tipus']
        data_creacio = dades['data_creacio']
        professor = Usuari.crear_json(dades['professor'])
        estudiant = Usuari.crear_json(dades['estudiant'])
        pdf = ast.literal_eval(dades['pdf'])
        nota = dades['nota']
        avaluacio = cls(resposta, professor, estudiant, pdf, nota, id_avaluacio)
        avaluacio.data_creacio = data_creacio
        avaluacio.tipus = id_tipus
        return avaluacio


class Universitat:

    def __init__(self, nom=None, private_key=None, public_key=None, id=None, ip=None):
        self.id = id
        self.nom = nom
        self.ip = ip
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
    def __init__(self, emissor=None, receptor=None, document=None, hash_anterior=None):
        self.id_transaccio = 0
        self.emissor = emissor
        self.receptor = receptor
        self.id_document = document.id_document_blockchain
        self.data_creacio = datetime.now().isoformat()
        self.document = Factoria.to_json(document)
        self.hash_anterior = hash_anterior

    @classmethod
    def crear_json(cls, dada):
        trans_json = json.loads(dada)
        id_transaccio = trans_json['id_transaccio']
        emissor = Usuari.crear_json(trans_json['emissor'])
        receptor = Usuari.crear_json(trans_json['receptor'])
        id_document = trans_json['id_document']
        data_creacio = trans_json['data_creacio']
        dada = Document.crear_json(trans_json['document'])
        hash_anterior = trans_json['hash_anterior']
        return cls.crear_mysql(id_transaccio, emissor, receptor, dada, id_document, data_creacio, hash_anterior)

    @classmethod
    def crear_mysql(cls, id_trans=None, emissor=None, receptor=None, dada=None, id_document=None,
                    data_creacio=None, hash_anterior=None):
        trans = cls(emissor, receptor, dada)
        trans.id_transaccio = id_trans
        trans.id_document = id_document
        trans.data_creacio = data_creacio
        trans.hash_anterior = hash_anterior
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
            'data_creacio': self.data_creacio,
            'hash_anterior': self.hash_anterior})


class Bloc:
    def __init__(self, id=None, trans=None, my_db=None, hash_bloc_anterior=None):
        if trans:
            self.id = id
            self.data_bloc = datetime.now().isoformat()
            uni = Factoria.build_universitat_from_db(my_db)
            transaccio_json = Factoria.to_json(Encriptador(trans, uni.public_key))
            self.transaccio = str.encode(transaccio_json)
            self.signatura = Encriptador.signar(self.transaccio, uni.private_key)
            self.hash_bloc_anterior = hash_bloc_anterior
        else:
            self.id = 0
            self.data_bloc = None
            self.transaccio = None
            self.signatura = None
            self.hash_bloc_anterior = None

    def verificar_bloc(self, my_db, ip):
        id_universitat, nom, ip, private_key_str, public_key_str = my_db.importar_universitat_ip(ip)
        uni = Factoria.build_universitat_from_db_ip(my_db, ip)
        return Encriptador.verificar_sign(self.transaccio, self.signatura, uni.public_key)

    @classmethod
    def crear_json(cls, dada):
        new_bloc = cls()
        bloc_json = json.loads(dada)
        new_bloc.id = bloc_json['id']
        new_bloc.data_bloc = bloc_json['data_bloc']
        new_bloc.transaccio = ast.literal_eval(bloc_json['transaccions'])
        new_bloc.signatura = ast.literal_eval(bloc_json['signatura'])
        new_bloc.hash_bloc_anterior = bloc_json['hash_bloc_anterior']
        return new_bloc

    @classmethod
    def crear_msql(cls, id_bloc, data_bloc, transaccio, signatura, hash_anterior):
        new_bloc = cls()
        new_bloc.id = id_bloc
        new_bloc.data_bloc = data_bloc
        new_bloc.transaccio = transaccio
        new_bloc.signatura = signatura
        new_bloc.hash_bloc_anterior = hash_anterior
        return new_bloc

    def to_dict(self):
        return collections.OrderedDict({
            'id': self.id,
            'transaccions': self.transaccio,
            'data_bloc': self.data_bloc,
            'signatura': self.signatura,
            'hash_bloc_anterior': self.hash_bloc_anterior})

    def calcular_hash(self):
        return hashlib.sha256(self.transaccio).hexdigest()


class BlockchainUniversity:

    def __init__(self, my_db):
        self.my_db = my_db

    def crear_genesis_bloc(self):
        """
       Creacio del hash_anterior Inicial.
        """
        public_key = RSA.generate(1024).publickey()
        genesis = Estudiant('Genesis', 'Genesis', 'Genesis', "Genesis", public_key, "Genesis")
        pdf = base64.b64encode("Genesis".encode())
        doc = Document(0, 0, genesis, pdf)
        transaccio = Transaccio(genesis, genesis, doc, 0)
        genesis_bloc = Bloc(1, transaccio, self.my_db, 0)
        genesis_bloc.data_bloc = datetime.now().isoformat()
        resultat = Paquet.confirmar_enviament(genesis_bloc, self.my_db)
        if resultat:
            print(genesis_bloc.calcular_hash())
            self.my_db.guardar_bloc_dades(genesis_bloc)
        return resultat

    @staticmethod
    def afegir_bloc_extern(my_db=None, bloc_json=None, ip=None):
        """
        Una funció que afegeix el hash_anterior a la cadena després de la verificació.
         La verificació inclou:
         * Block apunti al block anterior
         * Que vingui de una font valida
        """
        bloc = Bloc.crear_json(bloc_json)
        if bloc.verificar_bloc(my_db, ip):
            if my_db.existeix_bloc_genesis():
                ultim_bloc = Factoria.build_ultim_bloc_from_db(my_db)
                if bloc.verificar_bloc(my_db, ip):
                    if bloc.hash_bloc_anterior == ultim_bloc.calcular_hash():
                        if bloc.id == ultim_bloc.id + 1:
                            my_db.guardar_bloc_dades(bloc)
                            return True
            elif bloc.id == 1:
                bloc.id = 1
                my_db.guardar_bloc_dades(bloc)
                return True
        return False

    def minat(self):
        """
    Aquesta funció serveix com a interfície per afegir la transacció pendent a la cadena de blocs afegint-les al hash_anterior
         i esbrinar el hash_anterior.b'\x1d\xfd\xd2W\x0e\xe2xE`\xb3\xe2;\xbd\xbfM\x05C\x1b\xb9\x08\x16\x8ej<D\x00O\xd1\xaf\x1fdzR\x03\xfb\xc4\xf4\x19\xe1\x1e\xb3\xfd\xa7\xc5\x18\xf5nM\x85\xa8F\xaeI\xf4\xd8\xc2-\xef\x87\xb2\x1a1I\xb24}R\x9e9\x97\xb4\xda\xb6\xa0\xcd\xe1\x97_\xd3\x87f\x86R\xe9\x18\x06\xd4\x1de\xc8ze\x17\xf0\x80\xcb\xa6\xeahkN\xda\xbb\xa64,\xdf\xd8\xf0b\xdcP\x03\xbe\x163x\xce\xb8@&>^Y\xe4\xda\xa8b'
        """
        if self.my_db.existeix_alguna_transaccio():
            transaccio = Factoria.build_transaccio_from_db(self.my_db)
            if transaccio:
                if self.my_db.existeix_bloc_genesis():
                    ultim_bloc = Factoria.build_ultim_bloc_from_db(self.my_db)
                    if ultim_bloc:
                        index = ultim_bloc.id + 1
                        new_bloc = Bloc(index, transaccio, self.my_db, ultim_bloc.calcular_hash())
                        resultat = Paquet.confirmar_enviament(new_bloc, self.my_db)
                        if resultat:
                            self.my_db.guardar_bloc(new_bloc)
                            self.my_db.esborrar_transaccio(transaccio.id_transaccio)
                            return self.minat()
                else:
                    self.crear_genesis_bloc()
                    return self.minat()

    # Mirem que la cadena sigui correcta
    def comprovar_cadena_propia(self):
        ultim_bloc = self.my_db.id_ultim_bloc()
        bloc = Factoria.build_bloc_from_db(self.my_db, ultim_bloc)
        ok = True
        while ok and bloc.id > 1:
            bloc_anterior = Factoria.build_bloc_from_db(self.my_db, (bloc.id - 1))
            if bloc_anterior:
                ok = (bloc.hash_bloc_anterior.decode() == bloc_anterior.calcular_hash())
            else:
                ok = False
            bloc = bloc_anterior
        return bloc.id == 1

    def comprovar_cadena(self, cadena):
        if not cadena:
            return False
        else:
            id_cadena = 1
            bloc = cadena[0]
            ok = bloc is not None
            while ok and bloc.id > 1:
                bloc_anterior = cadena[id_cadena]
                if bloc_anterior:
                    ok = (bloc.hash_bloc_anterior.decode() == bloc_anterior.calcular_hash())
                    id_cadena += 1
                    bloc = bloc_anterior
                else:
                    ok = False
                    print("La cadena de blocs es incorrecta")
            return bloc.id == 1

    def canviar_cadena(self, cadena):
        if self.comprovar_cadena(cadena):
            self.my_db.esborrar_taula('bloc')
            for bloc in cadena:
                self.my_db.guardar_bloc_dades(bloc)
            return True
        return False


class Paquet:

    def __init__(self, bloc=None, ip=None, my_db=None):
        self.pas = 1
        self.my_db = None
        if bloc is not None:
            self.num_blocs = bloc.id
            self.dada = bloc.id
            self.hash_anterior = bloc.hash_bloc_anterior
            try:
                http = f'ws://{ip}:5005/echo'
                self.ws = simple_websocket.Client(http)
                self.my_db = my_db
            except (KeyboardInterrupt, EOFError, simple_websocket.ConnectionClosed):
                self.ws.close()

    def to_dict(self):
        return collections.OrderedDict({
            'pas': self.pas,
            'num_blocs': self.num_blocs,
            'dada': self.dada,
            'hash_anterior': self.hash_anterior,
        })

    @classmethod
    def crear_json(cls, paquet_json, my_db):
        paquet = cls()
        paquet.pas = paquet_json['pas']
        paquet.num_blocs = paquet_json['num_blocs']
        paquet.dada = paquet_json['dada']
        paquet.hash_anterior = paquet_json['hash_anterior']
        paquet.my_db = my_db
        return paquet

    def resposta(self):
        try:
            data = self.ws.receive()
        except (KeyboardInterrupt, EOFError, simple_websocket.ConnectionClosed):
            self.dada = False
            return self
            self.ws.close()
        if data:
            data_json = json.loads(data)
            missatge = Missatge.crear_json(data_json)
            paquet_json = missatge.rebut(self.my_db)
            paquet = Paquet.crear_json(paquet_json, self.my_db)
            self.pas = paquet.pas
            self.dada = paquet.dada
            self.num_blocs = paquet.num_blocs
            self.hash_anterior = self.hash_anterior
            self.repartiment()
        else:
            self.ws.close()


    def repartiment(self):
        try:
            if self.pas == 1:  # es un paquet inici de repartiment blocs
                self.pas = 2  # indiquem que es un paquet que hem enviat nosaltres
                self.ws.send(Factoria.to_json(Missatge(self)))
                self.resposta()

            elif self.pas == 2:  # es paquet que hem rebut per confirmar blocs
                if self.dada == 1:
                    self.dada = True
                    num_blocs = 0
                else:
                    num_blocs = self.my_db.id_ultim_bloc()
                    if self.dada == (num_blocs + 1):
                        meu_bloc = Factoria.build_bloc_from_db(self.my_db, num_blocs)
                        self.dada = (self.hash_anterior == meu_bloc.calcular_hash())
                        self.num_blocs = num_blocs
                        self.pas = 3
                        self.ws.send(Factoria.to_json(Missatge(self)))
                    else:
                        self.dada = False
                self.pas = 3
                self.num_blocs = num_blocs
                self.ws.send(Factoria.to_json(self))
                self.resposta()

            elif self.pas == 3:  # Tenim la resposta si les dugues cadenes son correctes
                return self

            elif self.pas == 4:  # Enviem el bloc i diem que es correcte per ells
                self.pas = 5
                self.num_blocs = Factoria.build_universitat_from_db(self.my_db).ip
                self.ws.send(Factoria.to_json(Missatge(self)))

            elif self.pas == 5:  # rebem un bloc ja confirmat.
                BlockchainUniversity.afegir_bloc_extern(self.my_db, self.dada, self.num_blocs)
                self.ws.close()

            elif self.pas == 6:  # demanem que ens passi tota la cadena
                self.ws.send(Factoria.to_json(self))
                self.resposta()

            elif self.pas == 7:  # rebem una peticio de tota la cadena
                cadena = Factoria.build_cadena_blocs(self.my_db)
                self.pas = 8
                self.dada = bytes(cadena)
                self.ws.send(Factoria.to_json(self))
                self.resposta()

            elif self.pas == 8:  # rebem tota la cadena
                cadena = self.dada.decode()
                self.dada = BlockchainUniversity.canviar_cadena(cadena)
                return self

        except (KeyboardInterrupt, EOFError, simple_websocket.ConnectionClosed):
            self.dada = False
            return self
            self.ws.close()

    @staticmethod
    def confirmar_enviament(bloc, my_db):
        llista = Factoria.build_all_universitat_from_db(my_db)
        paquets = list()
        for universitat in llista:
            ip_universitat = universitat.ip
            paquet = Paquet(bloc, ip_universitat, my_db)
            paquet.repartiment()
            paquets.append(paquet)
        if paquets:
            # això es un for on extreiem el numblocs i despres counter es diu quin es valor mes comu
            resultat = Counter([x.num_blocs for x in paquets if x.dada]).most_common()
            if resultat:
                mes_comu, quantitat = resultat.pop(0)
                if (len(paquets) / 2) <= quantitat:
                    if mes_comu == (bloc.id - 1) :
                        for paquet_confirmat in paquets:
                            if paquet_confirmat.dada:
                                paquet_confirmat.dada = Factoria.to_json(bloc)
                                paquet_confirmat.pas = 4
                                paquet_confirmat.repartiment()
                        return True
                    else:
                        paquet_demanar_cadena = [z for z in paquets if z.num_blocs == mes_comu]
                        paquet_demanar_cadena.pas = 6
                        paquet_demanar_cadena.repartiment()
                else:
                    return False
            else:
                return False

    @staticmethod
    def llista_blocs_blockchain(my_db):
        llista = my_db.importar_blocs()
        llista_blocs = list()
        for x in llista:
            llista_blocs.append(Factoria.build_bloc_from_db(x['id']))
        return llista_blocs

    @staticmethod
    def llista_hash_blockchain(my_db):
        llista = my_db.importar_blocs()
        llista_hash = list()
        for x in llista:
            llista_hash.append(Factoria.build_bloc_from_db(x['id']).hash_bloc_anterior)
        return llista_hash


class Missatge:
    def __init__(self, paquet):
        if paquet:
            uni = Factoria.build_universitat_from_db(paquet.my_db)
            public_key = uni.public_key
            self.public_key_export = public_key.exportKey('PEM')
            self.paquet_code = Factoria.to_json(paquet).encode('utf-8', 'replace')
            self.signatura = Encriptador.signar(self.paquet_code, uni.private_key)
            print(Encriptador.verificar_sign(self.paquet_code, self.signatura, uni.public_key))
            self.ip = uni.ip
        else:
            self.public_key_export = 0
            self.paquet_code = 0
            self.signatura = 0
            self.ip = 0

    def rebut(self, my_db):
            public_key = RSA.importKey(ast.literal_eval(self.public_key_export))
            paquet_code = ast.literal_eval(self.paquet_code)
            signatura = ast.literal_eval(self.signatura)
            if Encriptador.verificar_sign(paquet_code, signatura, public_key):
                paquet_json = paquet_code.decode('utf-8', 'replace')
                return json.loads(paquet_json)
            else:
                return False

    def to_dict(self):
        return collections.OrderedDict({
            'public_key_export': self.public_key_export,
            'paquet_code': self.paquet_code,
            'signatura': self.signatura,
            'ip': self.ip,
        })

    @classmethod
    def crear_json(cls, missatge_json):
        missatge = cls(None)
        missatge.public_key_export = missatge_json['public_key_export']
        missatge.paquet_code = missatge_json['paquet_code']
        missatge.signatura = missatge_json['signatura']
        missatge.ip = missatge_json['ip']
        return missatge



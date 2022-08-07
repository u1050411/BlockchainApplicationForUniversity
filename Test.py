import socket
import unittest
import ast

from Crypto.PublicKey import RSA

from BlockchainUniversity import Estudiant, Transaccio, Professor, Examen, Factoria, RespostaExamen, EvaluacioExamen, \
    Bloc, Universitat, Encriptador, Document, BlockchainUniversity
from CreateMysql import MySqlBloc

UTF_8 = 'utf8'
ESTUDIANT = 'estudiant'
PROFESSOR = 'professor'
SCHEMA = 'blockchainuniversity2'


class CreacioTaulaTest:

    def __init__(self, my_db, schema):
        self.my_db = my_db
        self.schema = schema

    def crear_schema_dades(self):
        self.my_db.esborrar_schema(self.schema)
        self.my_db.crear_schema(self.schema)
        self.my_db.afegir_schema(self.schema)
        self.my_db.crear_taules_inicials()
        self.crear_universitat()
        self.crear_usuaris()
        self.crear_examens()
        self.crear_respostes()
        self.crear_evaluacio()
        self.crear_transaccions()
        self.crear_universitat()

    def crear_universitat(self):
        private_key = RSA.generate(1024)
        public_key = private_key.publickey()
        uni = Universitat("Universitat de Girona", private_key, public_key)
        self.my_db.guardar_universitat(uni)

    def crear_usuaris(self):
        usuaris = [['u1050411', '40373747T', ESTUDIANT, 'Pau', 'de Jesus Bras', 'password1', 'u1050411@campus.udg.edu'],
                   ['u1050402', '40373946E', ESTUDIANT, 'Pere', 'de la Rosa', 'password2', 'u1050411@campus.udg.edu'],
                   ['u1050403', '40332506M', ESTUDIANT, 'Cristina', 'Sabari Vidal', 'password3',
                    'u1050411@campus.udg.edu'],
                   ['u1050404', '40372506P', ESTUDIANT, 'Diaz', 'Marti Sanchez', 'password4',
                    'u1050411@campus.udg.edu'],
                   ['u2050404', '40332507Y', PROFESSOR, 'Albert', 'Marti Sabari', 'password5',
                    'u1050411@campus.udg.edu'],
                   ['u2000256', '40332508Y', PROFESSOR, 'Teodor Maria', 'Jove Lagunas', 'password6',
                    'u1050411@campus.udg.edu']]

        for id_usuari, nif, tipus, nom, cognom, contrasenya, email in usuaris:
            key = RSA.generate(1024)
            private_key = key.exportKey('PEM').decode('ascii')
            sql = f'INSERT INTO private_key (`id_usuari`, `private_key`) VALUES("{id_usuari}", "{private_key}")'
            self.my_db.exportar_sql(sql)
            public_key = key.publickey()
            if tipus == ESTUDIANT:
                usuari = Estudiant(id_usuari, nif, nom, cognom, public_key, contrasenya, email)
            elif tipus == PROFESSOR:
                usuari = Professor(id_usuari, nif, nom, cognom, public_key, contrasenya, email)
            self.my_db.guardar_usuari(usuari)

        self.my_db.guardar_estudiants_professor(Factoria.build_usuari_from_db(self.my_db, 'u2000256'),
                                                Factoria.build_usuari_from_db(self.my_db, 'u1050411'))
        self.my_db.guardar_estudiants_professor(Factoria.build_usuari_from_db(self.my_db, 'u2000256'),
                                                Factoria.build_usuari_from_db(self.my_db, 'u1050402'))
        self.my_db.guardar_estudiants_professor(Factoria.build_usuari_from_db(self.my_db, 'u2000256'),
                                                Factoria.build_usuari_from_db(self.my_db, 'u1050404'))
        self.my_db.guardar_estudiants_professor(Factoria.build_usuari_from_db(self.my_db, 'u2050404'),
                                                Factoria.build_usuari_from_db(self.my_db, 'u1050403'))
        self.my_db.guardar_estudiants_professor(Factoria.build_usuari_from_db(self.my_db, 'u2050404'),
                                                Factoria.build_usuari_from_db(self.my_db, 'u1050411'))

    def crear_examens(self):
        examens = [[1, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                       f'pdf_minimo.pdf', 'u2050404', '2022-10-01T13:00', '2022-10-01T14:00'],
                   [2, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity'
                       f'/pdf/Examen_2020-21-_26-03_primer_parcial.pdf', 'u2000256', '2022-10-01T12:00'
                       , '2022-10-01T13:00'],
                   [3, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                       f'pdf_minimo.pdf', 'u2000256', '2022-10-01T13:00', '2022-10-01T14:00'],
                   [4, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity'
                       f'/pdf/Examen_2020-21-_26-03_primer_parcial.pdf', 'u2050404', '2022-10-01T12:00'
                       , '2022-10-01T13:00']
                   ]

        for id_document, nom_fitxer, id_professor, data_inicial, data_final in examens:
            pdf = Factoria.recuperar_fitxer(nom_fitxer)
            professor = Factoria.build_usuari_from_db(self.my_db, id_professor)
            examen = Examen(id_document, professor, pdf, data_inicial, data_final)
            estudiant = Factoria.build_usuari_from_db(self.my_db, 'u1050402')
            examen.afegir_estudiants(estudiant)
            self.my_db.guardar_examen(examen)

    def crear_respostes(self):

        respostes = [[1, 1, 'u1050402', f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                                     f'Examen_2021_20_10_01_primer_parcial-solucio.pdf'],
                     [2, 2, 'u1050403', f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                                     f'Examen_2020-21-_26-03_primer_parcial.pdf']]

        for id_resposta, id_examen, id_usuari, nom_fitxer in respostes:
            pdf = Factoria.recuperar_fitxer(nom_fitxer)
            estudiant = Factoria.build_usuari_from_db(self.my_db, id_usuari)
            resposta = RespostaExamen(id_resposta, id_examen, estudiant, pdf)
            self.my_db.guardar_resposta_examen(resposta)

    def crear_evaluacio(self):

        respostes = [[3, 1, 'u2000256', f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                                     f'Examen_2021_20_10_01_primer_parcial-solucio.pdf'],
                     [4, 2, 'u2050404', f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                                     f'Examen_2020-21-_26-03_primer_parcial.pdf']]

        for id_resposta, id_examen, id_usuari, nom_fitxer in respostes:
            pdf = Factoria.recuperar_fitxer(nom_fitxer)
            professor = Factoria.build_usuari_from_db(self.my_db, id_usuari)
            resposta = EvaluacioExamen(id_resposta, id_examen, professor, pdf)
            self.my_db.guardar_resposta_examen(resposta)

    def crear_transaccions(self):
        receptor = Factoria.build_usuari_from_db(self.my_db, 'u1050402')
        emissor = Factoria.build_usuari_from_db(self.my_db, 'u2050404')
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        transaccio_inicial = Transaccio(emissor, receptor, examen)
        self.my_db.guardar_transaccio(transaccio_inicial)
        emissor2 = receptor
        receptor2 = emissor
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf' \
                     f'/Examen_2021_20_10_01_primer_parcial-solucio.pdf'
        pdf = Factoria.recuperar_fitxer(nom_fitxer)
        resposta = RespostaExamen(1, 1, emissor2, pdf)
        transaccio2 = Transaccio(emissor2, receptor2, resposta)
        self.my_db.guardar_transaccio(transaccio2)


class TestUsuaris(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_dades()

    def test_creation(self):
        public_key = RSA.generate(1024).publickey()
        estudiant = Estudiant('u1050406', '40332505G', 'Marta', "Rodriguez", public_key, "password7")
        self.assertEqual(estudiant.id, 'u1050406')
        self.assertEqual(estudiant.nif, '40332505G')
        self.assertEqual(estudiant.nom, 'Marta')
        self.assertEqual(estudiant.cognom, 'Rodriguez')
        self.assertEqual(estudiant.public_key, public_key)


class TestProfessors(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_dades()

    def test_llista_alumnes(self):
        professor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        llista_alumnes = professor.llista_alumnes(self.my_db)
        print(llista_alumnes)

    def test_llista_examens(self):
        professor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        llista_alumnes = professor.llista_examens(self.my_db)
        print(llista_alumnes)


class TestUniversitat(unittest.TestCase):
    pass


class TestMysql(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)

    def tearDown(self):
        self.my_db.tancar()

    def test_afegir(self):
        self.my_db.afegir_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), True)

    def test_esborrar_schema(self):
        self.test.crear_schema_dades()
        self.my_db.esborrar_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), False)

    def test_crear_schema(self):
        self.my_db.crear_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), True)

    def test_exportar_sql(self):
        self.test.crear_schema_dades()
        sql = "CREATE TABLE if not exists `TaulaProva` (" \
              "`id` int NOT NULL," \
              "`nif` varchar(9) NOT NULL," \
              "`nom` varchar(45) DEFAULT NULL," \
              "`cognom` varchar(100) DEFAULT NULL," \
              "PRIMARY KEY (`id`, `nif`)) "
        self.my_db.exportar_sql(sql)
        self.assertEqual(self.my_db.existeix(self.schema, 'TaulaProva', None, None), True)

    def test_crear_taules(self):
        schema = self.schema
        self.my_db.esborrar_schema(schema)
        self.my_db.crear_schema(schema)
        self.my_db.crear_taules_inicials()
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', None, None), True)

    def test_retorn_schema(self):
        self.my_db.afegir_schema(self.schema)
        schema = self.my_db.schema
        self.assertEqual(self.schema, schema)

    def test_crear_usuaris(self):
        self.my_db.esborrar_schema(self.schema)
        self.my_db.crear_schema(self.schema)
        self.my_db.crear_taules_inicials()
        self.test.crear_usuaris()
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', 'u1050403'), True)

    def test_afegir_alumne_professor(self):
        self.test.crear_schema_dades()
        self.my_db.guardar_estudiants_professor(Factoria.build_usuari_from_db(self.my_db, 'u2000256'),
                                                Factoria.build_usuari_from_db(self.my_db, 'u1050403'))

    def test_llista_estudiant_professor(self):
        self.test.crear_schema_dades()
        llista = self.my_db.importar_estudiants_professor(Factoria.build_usuari_from_db(self.my_db, 'u2000256'))
        self.assertEqual(llista[0], 'u1050402')
        self.assertEqual(llista[1], 'u1050404')
        self.assertEqual(llista[2], 'u1050411')

    def test_crear_examens(self):
        self.my_db.esborrar_schema(self.schema)
        self.my_db.crear_schema(self.schema)
        self.test_crear_usuaris()
        self.test.crear_examens()

    def test_existeix(self):
        self.test.crear_schema_dades()
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), True)
        self.assertEqual(self.my_db.existeix('noSchema', None, None, None), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', None, None), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'no_Taula', None, None), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'nom', None), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'no_Columna', None), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', 'u1050403'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', 'u1070401'), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'private_key', 'id_usuari', 'u1050403'), True)

    def test_guardar_usuari(self):
        self.test.crear_schema_dades()
        id_usuari = 'u1050704'
        nif = '40373944C'
        nom = 'Pablo'
        cognom = 'Gutierrez'
        password = 'password9'
        email = 'u1050704@campus.udg.edu'
        key = RSA.generate(1024)
        public_key = key.publickey()
        estudiant = Estudiant(id_usuari, nif, nom, cognom, public_key, password)
        self.my_db.guardar_usuari(estudiant)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', 'u1050411'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'nom', 'Pere'), True)

    def test_clau(self):
        self.test.crear_schema_dades()
        id_usuari = 1050702
        privat_key = RSA.generate(1024)
        public_key = privat_key.publickey()
        self.my_db.guardar_clau_privada(id_usuari, privat_key)
        privat_guardat = self.my_db.clau_privada(id_usuari)
        self.assertTrue(privat_guardat.public_key(), public_key)

    def test_seguent_numero(self):
        self.test.crear_schema_dades()
        num_maxim = self.my_db.seguent_id_examen()
        self.assertIsNotNone(num_maxim)

    def test_guardar_resposta(self):
        self.test.crear_schema_dades()
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = Factoria.recuperar_fitxer(nom_fitxer)
        estudiant = Factoria.build_usuari_from_db(self.my_db, 'u1050411')
        id_resposta = self.my_db.seguent_id_resposta()
        resposta = RespostaExamen(id_resposta, 1, estudiant, pdf)
        self.my_db.guardar_resposta_examen(resposta)


class TestFactoria(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.esborrar_schema(SCHEMA)
        self.test = CreacioTaulaTest(self.my_db, SCHEMA)
        self.test.crear_schema_dades()

    def test_usuari(self):
        estudiant = Factoria.build_usuari_from_db(self.my_db, 'u1050402')
        self.assertEqual(estudiant.id, 'u1050402')
        self.assertEqual(estudiant.nom, 'Pere')
        professor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        self.assertEqual(professor.id, 'u2000256')
        self.assertEqual(professor.nom, 'Teodor Maria')

    def test_examen(self):
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        self.assertEqual(examen.id_document, 1)
        self.assertEqual(examen.usuari.id, 'u2050404')

    def test_to_json(self):
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        exament_print = examen.to_dict()
        print(exament_print)
        examen_json = Factoria.to_json(examen)
        print(examen_json)

    def test_resposta(self):
        resposta = Factoria.build_resposta_alumne_from_db(self.my_db, 1, 1)
        self.assertEqual(resposta.id_document, 1)
        self.assertEqual(resposta.id_examen, 1)
        self.assertEqual(resposta.usuari.id, 'u1050402')
        self.assertEqual(resposta.usuari.tipus, ESTUDIANT)

    def test_evaluacio(self):
        resposta = Factoria.build_evaluacio_examen_from_db(self.my_db, 1, 3)
        self.assertEqual(resposta.id_document, 3)
        self.assertEqual(resposta.id_examen, 1)
        self.assertEqual(resposta.usuari.id, 'u2000256')
        self.assertEqual(resposta.usuari.tipus, PROFESSOR)

    def test_transaccio(self):
        receptor = Factoria.build_usuari_from_db(self.my_db, 'u1050402')
        emissor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        transaccio_inicial = Transaccio(emissor, receptor, examen)
        self.my_db.guardar_transaccio(transaccio_inicial)
        self.my_db.borrar_dades_taula(self.my_db.schema, "transaccio")
        self.my_db.guardar_transaccio(transaccio_inicial)
        transaccio_guardat = Factoria.build_transaccio_from_db(self.my_db)
        self.assertEqual(transaccio_inicial.emissor.id, transaccio_guardat.emissor.id)
        self.assertEqual(transaccio_inicial.receptor.id, transaccio_guardat.receptor.id)

    # def test_bloc(self):
    #     transaccio = Factoria.build_transaccio_from_db(self.my_db)
    #     uni = Factoria.build_universitat_from_db(self.my_db)
    #     bloc = Bloc(transaccio, "41b8e84497b3d73038a397e8b5e100", uni.public_key)
    #     self.my_db.guardar_bloc(bloc)
    #     bloc_final = Factoria.build_bloc_from_db(self.my_db, 1)
    #     transaccio_final = Transaccio.crear_json(bloc_final.transaccio.desencriptar(uni.private_key))
    #     self.assertEqual(transaccio_final.emissor.id, transaccio.emissor.id)


class TestExamen(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.esborrar_schema(SCHEMA)
        self.test = CreacioTaulaTest(self.my_db, SCHEMA)
        self.test.crear_schema_dades()

    def test_creacio_examen(self):
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = Factoria.recuperar_fitxer(nom_fitxer)
        professor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        examen = Examen(1111, professor, pdf, '00000000', '00000000')

        estudiant1 = Factoria.build_usuari_from_db(self.my_db, 'u1050411')
        examen.estudiants.append(estudiant1)
        estudiant2 = Factoria.build_usuari_from_db(self.my_db, 'u1050402')
        examen.estudiants.append(estudiant2)
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = Factoria.recuperar_fitxer(nom_fitxer)
        estudiant = Factoria.build_usuari_from_db(self.my_db, 'u1050411')
        resposta = RespostaExamen(1, 1, estudiant, pdf)
        examen.respostes.append(resposta)
        self.assertEqual(examen.estudiants[0], estudiant1)
        self.assertEqual(examen.pdf, pdf)
        self.assertEqual(examen.usuari, professor)

    def test_seguent_numero(self):
        num_document = self.my_db.seguent_id_examen()
        self.assertIsNotNone(num_document)


class TestRespostaExamen(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.test = CreacioTaulaTest(self.my_db, SCHEMA)
        self.test.crear_schema_dades()

    def test_creacio_resposta_examen(self):
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = Factoria.recuperar_fitxer(nom_fitxer)
        estudiant = Factoria.build_usuari_from_db(self.my_db, 'u1050411')
        resposta = RespostaExamen(1, 1, estudiant, pdf)
        self.assertEqual(resposta.id_document, 1)
        self.assertEqual(resposta.id_examen, 1)
        self.assertEqual(resposta.usuari, estudiant)
        self.assertEqual(resposta.pdf, pdf)

    def test_seguent_numero(self):
        num_document = self.my_db.seguent_id_resposta()
        self.assertIsNotNone(num_document)


class TestEvaluacioExamen(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.esborrar_schema(SCHEMA)
        self.test = CreacioTaulaTest(self.my_db, SCHEMA)
        self.test.crear_schema_dades()

    def test_creacio_resposta_examen(self):
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = Factoria.recuperar_fitxer(nom_fitxer)
        estudiant = Factoria.build_usuari_from_db(self.my_db, 'u1050411')
        resposta = EvaluacioExamen(1, 1, estudiant, pdf)
        self.assertEqual(resposta.id_document, 1)
        self.assertEqual(resposta.id_examen, 1)
        self.assertEqual(resposta.usuari, estudiant)
        self.assertEqual(resposta.pdf, pdf)

    def test_to_json(self):
        evaluacio = Factoria.build_evaluacio_examen_from_db(self.my_db, 1, 3)
        evaluacio_print = evaluacio.to_dict()
        print(evaluacio_print)
        evaluacio_json = Factoria.to_json(evaluacio)
        print(evaluacio_json)


class TestEncriptador(unittest.TestCase):
    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.esborrar_schema(SCHEMA)
        self.test = CreacioTaulaTest(self.my_db, SCHEMA)
        self.test.crear_schema_dades()

    def test_encriptar_desencriptar(self):
        emissor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        examen_encriptar = Encriptador(examen, emissor.public_key)
        examen_resultat = examen_encriptar.desencriptar(self.my_db.clau_privada(emissor.id))
        examen_final = Examen.create_json(examen_resultat)
        self.assertEqual(examen.id_document, examen_final.id_document)
        self.assertEqual(examen.usuari.id, examen_final.usuari.id)
        self.assertEqual(examen.pdf, examen_final.pdf)
        self.assertEqual(examen.data_creacio, examen_final.data_creacio)

    def test_signar_verificar(self):
        private_key = RSA.generate(1024)
        public_key = private_key.publickey()

        dada = Encriptador.signar("Hola".encode("utf8"), private_key)
        self.assertEqual(Encriptador.verificar_sign(dada,public_key), True)


class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.my_db.esborrar_schema(self.schema)
        self.my_db.crear_schema(self.schema)
        self.my_db.afegir_schema(self.schema)
        self.my_db.crear_taules_inicials()
        self.test.crear_universitat()
        self.test.crear_usuaris()
        self.test.crear_examens()
        self.test.crear_respostes()
        self.test.crear_evaluacio()

    @property
    def crear_transaccio(self):
        receptor = Factoria.build_usuari_from_db(self.my_db, 'u1050402')
        emissor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        transaccio = Transaccio(emissor, receptor, examen)
        return receptor, emissor, examen, transaccio

    def test_creation(self):
        (receptor, emissor, examen, transaccio) = self.crear_transaccio
        self.assertEqual(transaccio.emissor, emissor)
        self.assertEqual(transaccio.receptor, receptor)

    def test_guardar(self):
        (receptor, emissor, examen, transaccio_inicial) = self.crear_transaccio
        self.my_db.guardar_transaccio(transaccio_inicial)
        transaccio = Factoria.build_transaccio_from_db(self.my_db)
        self.assertEqual(transaccio.emissor.id, emissor.id)
        self.assertEqual(transaccio.receptor.id, receptor.id)
        self.assertEqual(transaccio.document.dada, transaccio_inicial.document.dada)
        self.assertEqual(transaccio.document.clau, transaccio_inicial.document.clau)

    # def test_to_json(self):
    #     (receptor, emissor, examen, transaccio) = self.crear_transaccio
    #     trans_json = transaccio.to_json()
    #     print(trans_json)

    def test_encriptar_desencriptar(self):
        (receptor, emissor, examen, transaccio_inicial) = self.crear_transaccio
        uni = Factoria.build_universitat_from_db(self.my_db)
        transaccio_encriptat = Encriptador(transaccio_inicial, uni.public_key)
        transaccio_json = transaccio_encriptat.desencriptar(uni.private_key)
        transaccio_final = Transaccio.crear_json(transaccio_json)
        self.assertEqual(transaccio_inicial.emissor.id, transaccio_final.emissor.id)
        self.assertEqual(transaccio_inicial.id_document, transaccio_final.id_document)
        self.assertEqual(transaccio_inicial.document.dada, transaccio_final.document.dada)
        self.assertEqual(transaccio_inicial.document.clau, transaccio_final.document.clau)


class TestBloc(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_dades()

    def test_crear(self):
        transaccio = Factoria.build_transaccio_from_db(self.my_db)
        uni = Factoria.build_universitat_from_db(self.my_db)
        bloc = Bloc(transaccio, "41b8e84497b3d73038a397e8b5e100", uni.public_key)
        return bloc
#
#     def test_guardar(self):
#         bloc = self.test_crear()
#         self.my_db.guardar_bloc(bloc)
#
#     def test_calcular_Hash(self):
#         bloc = self.test_crear()
#         self.assertEqual(bloc.calcular_hash(), bloc.calcular_hash())
#
#
#     # def test_importar_ultim_bloc(self):
#     #     self.test_guardar()
#     #     num_bloc = self.my_db.id_ultim_bloc()
#     #     bloc = Factoria.build_bloc_from_db(self.my_db, num_bloc)
#     #     self.assertEqual(bloc.calcular_hash(), bloc.calcular_hash())
#
#
# class TestBlockchainUniversity(unittest.TestCase):
#
#     def setUp(self):
#         self.my_db = MySqlBloc('localhost', 'root', 'root')
#         self.schema = SCHEMA
#         self.test = CreacioTaulaTest(self.my_db, self.schema)
#         self.test.crear_schema_dades()
#
#     def test_crear_genesis_bloc(self):
#         bloc_chain = BlockchainUniversity(self.my_db)
#         bloc_chain.crear_genesis_bloc()
#         bloc_genesis = Factoria.build_bloc_from_db(self.my_db, 1)
#
#         self.assertEqual(bloc_genesis.index, 0)
#         self.assertEqual(bloc_genesis.hash_bloc_anterior, "asfassdfsadfsa")
#         self.assertEqual(bloc_genesis.id_document, '00000')


# class TestConexions(unittest.TestCase):
#
#     def test_conexio_servidor(self):
#         HOST = ''  # Symbolic name meaning all available interfaces
#         PORT = 50007  # Arbitrary non-privileged port
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.bind((HOST, PORT))
#             s.listen(1)
#             conn, addr = s.accept()
#             with conn:
#                 print('Connected by', addr)
#                 while True:
#                     data = conn.recv(1024)
#                     if not data: break
#                     conn.sendall(data)

# def test_conexio_client(self):
#     HOST = '192.168.50.26'  # The remote host
#     PORT = 50007  # The same port as used by the server
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((HOST, PORT))
#         s.sendall(b'Hello, world udg')
#         data = s.recv(1024)
#     print('Received', repr(data))

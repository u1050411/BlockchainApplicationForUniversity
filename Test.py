import unittest
from socket import socket

from Crypto.PublicKey import RSA
from BlockchainUniversity import Estudiant, Transaccio, Professor, Examen, Factoria, RespostaExamen, AvaluacioExamen, \
    Bloc, Universitat, Encriptador, BlockchainUniversity, Pdf, Assignatura
from Connexions import Connexions
from CreateMysql import MySqlBloc

UTF_8 = 'utf8'
ESTUDIANT = 'estudiant'
PROFESSOR = 'professor'
SCHEMA = 'blockchainuniversity'


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
        self.crear_assignatures()
        self.crear_pdf()
        self.crear_examens()
        self.crear_respostes()
        self.crear_avaluacio()
        self.crear_transaccions()
        self.crear_universitat()
        self.crear_genesis_bloc()

    def crear_schema_inicial(self):
        self.my_db.esborrar_schema(self.schema)
        self.my_db.crear_schema(self.schema)
        self.my_db.afegir_schema(self.schema)
        self.my_db.crear_taules_inicials()
        self.crear_universitat()
        self.crear_usuaris()
        self.crear_assignatures()
        self.crear_pdf()
        self.crear_genesis_bloc()

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

    def crear_assignatures(self):

        assignatures = [['Sistemes operatius', 'u2000256'], ['Computadors', 'u2050404']]

        for nom, id_professor in assignatures:
            professor = Factoria.build_usuari_from_db(self.my_db, id_professor)
            assignatura = Assignatura(0, nom, professor)
            self.my_db.guardar_assignatura(assignatura)

        self.my_db.guardar_estudiants_assignatura(Factoria.build_assignatura_from_db(self.my_db, 1),
                                                  Factoria.build_usuari_from_db(self.my_db, 'u1050411'))
        self.my_db.guardar_estudiants_assignatura(Factoria.build_assignatura_from_db(self.my_db, 1),
                                                  Factoria.build_usuari_from_db(self.my_db, 'u1050402'))
        self.my_db.guardar_estudiants_assignatura(Factoria.build_assignatura_from_db(self.my_db, 1),
                                                  Factoria.build_usuari_from_db(self.my_db, 'u1050404'))
        self.my_db.guardar_estudiants_assignatura(Factoria.build_assignatura_from_db(self.my_db, 2),
                                                  Factoria.build_usuari_from_db(self.my_db, 'u1050403'))
        self.my_db.guardar_estudiants_assignatura(Factoria.build_assignatura_from_db(self.my_db, 2),
                                                  Factoria.build_usuari_from_db(self.my_db, 'u1050411'))

    def crear_pdf(self):
        pdfs = [[1, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                    f'Examen_2021_20_10_01_primer_parcial-solucio.pdf', 'Examen_2021_20_10_01_primer_parcial-solucio.pdf',
                 'u2000256', '2022-10-01T13:00'],
                [2, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity'
                    f'/pdf/Examen_2020-21-_26-03_primer_parcial.pdf', 'Examen_2020-21-_26-03_primer_parcial.pdf',
                 'u2000256', '2022-10-01T12:00'],
                [3, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                    f'Examen_2021_20_10_01_primer_parcial-solucio.pdf',
                 'Examen_2021_20_10_01_primer_parcial-solucio.pdf', 'u2050404', '2022-10-01T13:00'],
                [4, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity'
                    f'/pdf/Examen_2020-21-_26-03_primer_parcial.pdf', 'Examen_2020-21-_26-03_primer_parcial.pdf',
                 'u2050404', '2022-10-01T12:00']]

        for id_pdf, path_fitxer, nom_fitxer, id_usuari, data_creacio in pdfs:
            pdf = Factoria.recuperar_fitxer(path_fitxer)
            usuari = Factoria.build_usuari_from_db(self.my_db, id_usuari)
            classe_pdf = Pdf(id_pdf, nom_fitxer, usuari, pdf)
            self.my_db.guardar_pdf(classe_pdf)

    def crear_examens(self):
        examens = [[1, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                       f'pdf_minimo.pdf', 'u2050404', '2022-10-01T13:00', '2022-10-01T14:00', 2],
                   [2, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity'
                       f'/pdf/Examen_2020-21-_26-03_primer_parcial.pdf', 'u2000256', '2022-10-01T12:00'
                       , '2022-10-01T13:00', 1],
                   [3, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                       f'pdf_minimo.pdf', 'u2000256', '2022-10-01T13:00', '2022-10-01T14:00', 1],
                   [4, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity'
                       f'/pdf/Examen_2020-21-_26-03_primer_parcial.pdf', 'u2050404', '2022-10-01T12:00'
                       , '2022-10-01T13:00', 2]
                   ]

        for id_document, nom_fitxer, id_professor, data_inicial, data_final, id_assignatura in examens:
            pdf = Factoria.recuperar_fitxer(nom_fitxer)
            professor = Factoria.build_usuari_from_db(self.my_db, id_professor)
            assignatura = Factoria.build_assignatura_from_db(self.my_db, id_assignatura)
            examen = Examen(id_document, professor, pdf, data_inicial, data_final, None, assignatura)
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
            examen = Factoria.build_examen_from_db(self.my_db, id_examen, True)
            resposta = RespostaExamen(id_resposta, examen, estudiant, pdf)
            self.my_db.guardar_resposta_examen(resposta)

    def crear_avaluacio(self):

        respostes = [[1, 1, 'u2000256', f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                                        f'Examen_2021_20_10_01_primer_parcial-solucio.pdf', 'u1050411',8],
                     [2, 2, 'u2050404', f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                                        f'Examen_2020-21-_26-03_primer_parcial.pdf', 'u1050402',4]]

        for id_resposta, id_examen, id_professor, nom_fitxer, estudiant, nota in respostes:
            pdf = Factoria.recuperar_fitxer(nom_fitxer)
            professor = Factoria.build_usuari_from_db(self.my_db, id_professor)
            resposta = Factoria.build_id_resposta_alumne_from_db(self.my_db, id_resposta)
            estudiant = Factoria.build_usuari_from_db(self.my_db, estudiant)
            avaluacio_examen = AvaluacioExamen(resposta, professor, estudiant, pdf)
            self.my_db.guardar_avaluacio_examen(avaluacio_examen)

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
        resposta = RespostaExamen(1, examen, emissor2, pdf,7)
        transaccio2 = Transaccio(emissor2, receptor2, resposta)
        self.my_db.guardar_transaccio(transaccio2)

    def crear_genesis_bloc(self):
        bloc_chain = BlockchainUniversity(self.my_db)
        bloc_chain.crear_genesis_bloc()


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

    def test_llista_pdf(self):
        professor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        llista = professor.llista_pdf(self.my_db)
        print(llista)


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

    def test_esborrar_transaccio(self):
        self.test.crear_schema_dades()
        self.my_db.esborrar_transaccio(1)
        self.my_db.esborrar_transaccio(2)
        self.assertEqual(self.my_db.importar_transaccions(), None)

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

    def test_llista_estudiant_professor(self):
        self.test.crear_schema_dades()
        llista = self.my_db.importar_estudiants_professor(Factoria.build_usuari_from_db(self.my_db, 'u2000256'))
        self.assertEqual(llista[0], 'u1050402')
        self.assertEqual(llista[1], 'u1050404')
        self.assertEqual(llista[2], 'u1050411')

    def test_crear_examens(self):
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.my_db.esborrar_schema(self.schema)
        self.my_db.crear_schema(self.schema)
        self.my_db.afegir_schema(self.schema)
        self.my_db.crear_taules_inicials()
        self.test.crear_universitat()
        self.test.crear_usuaris()
        self.test.crear_assignatures()
        self.test.crear_pdf()
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
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        resposta = RespostaExamen(id_resposta, examen, estudiant, pdf, 9)
        self.my_db.guardar_resposta_examen(resposta)

    def test_guardar_bloc(self):
        self.test.crear_schema_dades()
        transactions = Factoria.build_transaccio_from_db(self.my_db)
        emissor = transactions.emissor
        ultim_bloc = Factoria.build_ultim_bloc_from_db((self.my_db))
        index = ultim_bloc.id + 1
        hash_anterior = ultim_bloc.calcular_hash()
        new_bloc = Bloc(index, transactions, hash_anterior, self.my_db)
        self.my_db.guardar_bloc(new_bloc, emissor)


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

    def test_pdf(self):
        path_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                      f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        nom_fitxer = 'GEINF DOC1 full de TFG_V2.pdf'
        pdf = Factoria.recuperar_fitxer(path_fitxer)
        professor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        id = 10
        pdfs = Pdf(id, nom_fitxer, professor, pdf)
        self.my_db.guardar_pdf(pdfs)
        pdf2 = Factoria.build_pdf_from_db(self.my_db, 10)
        nom_fitxer2 = 'fitxer_guardat.pdf'
        path_fitxer2 = f"C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/"
        Factoria.guardar_fitxer(path_fitxer, pdf2.pdf)

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
        resposta = Factoria.build_id_resposta_alumne_from_db(self.my_db, 1)
        self.assertEqual(resposta.id_document, 1)
        self.assertEqual(resposta.examen.id_document, 1)
        self.assertEqual(resposta.usuari.id, 'u1050402')
        self.assertEqual(resposta.usuari.tipus, ESTUDIANT)

    def test_avaluacio(self):
        resposta = Factoria.build_avaluacio_from_db(self.my_db, 1)
        self.assertEqual(resposta.id_document, 1)
        self.assertEqual(resposta.resposta.id_document, 1)
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


class TestPdf(unittest.TestCase):
    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.esborrar_schema(SCHEMA)
        self.test = CreacioTaulaTest(self.my_db, SCHEMA)
        self.test.crear_schema_dades()

    def test_creacio_pdf(self):
        path_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                      f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        nom_fitxer = 'GEINF DOC1 full de TFG_V2.pdf'
        pdf = Factoria.recuperar_fitxer(path_fitxer)
        professor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        id = self.my_db.seguent_id_pdf() + 1
        pdfs = Pdf(id, nom_fitxer, professor, pdf)
        self.my_db.guardar_pdf(pdfs)
        self.assertEqual(pdfs.id_document, id)
        self.assertEqual(pdfs.pdf, pdf)
        self.assertEqual(pdfs.usuari, professor)


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
        examen = Factoria.build_examen_from_db(self.my_db, 1, True)
        resposta = RespostaExamen(1, examen, estudiant, pdf)
        self.assertEqual(resposta.id_document, 1)
        self.assertEqual(resposta.examen.id_document, 1)
        self.assertEqual(resposta.usuari, estudiant)
        self.assertEqual(resposta.pdf, pdf)

    def test_seguent_numero(self):
        num_document = self.my_db.seguent_id_resposta()
        self.assertIsNotNone(num_document)


class TestavaluacioExamen(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.esborrar_schema(SCHEMA)
        self.test = CreacioTaulaTest(self.my_db, SCHEMA)
        self.test.crear_schema_dades()

    def test_creacio_resposta_examen(self):
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = Factoria.recuperar_fitxer(nom_fitxer)
        professor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        estudiant = Factoria.build_usuari_from_db(self.my_db, 'u1050411')
        resposta = Factoria.build_id_resposta_alumne_from_db(self.my_db, 1)
        avaluacio = AvaluacioExamen(resposta, professor, estudiant, pdf, 7, 1)
        self.assertEqual(avaluacio.id_document, 1)
        self.assertEqual(avaluacio.resposta, resposta)
        self.assertEqual(avaluacio.estudiant, estudiant)
        self.assertEqual(avaluacio.usuari, professor)
        self.assertEqual(avaluacio.pdf, pdf)

    def test_to_json(self):
        avaluacio = Factoria.build_avaluacio_from_db(self.my_db, 1)
        avaluacio_json = Factoria.to_json(avaluacio)
        avaluacio2 = AvaluacioExamen.crear_json(avaluacio_json)
        self.assertEqual(avaluacio.id_document, avaluacio2.id_document)
        self.assertEqual(avaluacio.resposta.id_document, avaluacio2.resposta.id_document)
        self.assertEqual(avaluacio.estudiant.id,  avaluacio2.estudiant.id)
        self.assertEqual(avaluacio.usuari.id, avaluacio2.usuari.id)
        self.assertEqual(avaluacio.pdf, avaluacio2.pdf)


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
        examen_final = Examen.crear_json(examen_resultat)
        self.assertEqual(examen.id_document, examen_final.id_document)
        self.assertEqual(examen.usuari.id, examen_final.usuari.id)
        self.assertEqual(examen.pdf, examen_final.pdf)

    def test_signar_verificar(self):
        emissor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        examen_encriptar = Encriptador(examen, emissor.public_key)
        examen_encriptar.signar(self.my_db.clau_privada(emissor.id))
        self.assertTrue(examen_encriptar.verificar_sign(emissor.public_key))
        examen_resultat = examen_encriptar.desencriptar(self.my_db.clau_privada(emissor.id))
        examen_final = Examen.crear_json(examen_resultat)
        self.assertEqual(examen.id_document, examen_final.id_document)
        self.assertEqual(examen.usuari.id, examen_final.usuari.id)
        self.assertEqual(examen.pdf, examen_final.pdf)


class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.esborrar_schema(SCHEMA)
        self.test = CreacioTaulaTest(self.my_db, SCHEMA)
        self.test.crear_schema_dades()

    @property
    def crear_transaccio(self):
        receptor = Factoria.build_usuari_from_db(self.my_db, 'u1050402')
        emissor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        transaccio = Transaccio(emissor, receptor, examen)
        return receptor, emissor, examen, transaccio

    def test_guardar(self):
        self.my_db.esborrar_taula('transaccio')
        (receptor, emissor, examen, transaccio_inicial) = self.crear_transaccio
        self.my_db.guardar_transaccio(transaccio_inicial)
        transaccio = Factoria.build_transaccio_from_db(self.my_db)
        self.assertEqual(transaccio.emissor.id, emissor.id)
        self.assertEqual(transaccio.receptor.id, receptor.id)
        self.assertEqual(transaccio.id_document, transaccio_inicial.id_document)


    def test_encriptar_desencriptar(self):
        (receptor, emissor, examen, transaccio_inicial) = self.crear_transaccio
        uni = Factoria.build_universitat_from_db(self.my_db)
        transaccio_encriptat = Encriptador(transaccio_inicial, uni.public_key)
        transaccio_json = transaccio_encriptat.desencriptar(uni.private_key)
        transaccio_final = Transaccio.crear_json(transaccio_json)
        self.assertEqual(transaccio_inicial.emissor.id, transaccio_final.emissor.id)
        self.assertEqual(transaccio_inicial.id_document, transaccio_final.id_document)


class TestBloc(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_dades()

    def test_crear(self):
        transaccio = Factoria.build_transaccio_from_db(self.my_db)
        bloc = Bloc(0, transaccio, "41b8e84497b3d73038a397e8b5e100", self.my_db)
        uni = Factoria.build_universitat_from_db(self.my_db)
        Encriptador_json = Encriptador.crear_json(bloc.transaccio)
        transaccio_json = Encriptador_json.desencriptar(uni.private_key)
        transaccio_final = Transaccio.crear_json(transaccio_json)
        self.assertEqual(transaccio.emissor.id, transaccio_final.emissor.id)


class TestBlockchainUniversity(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_dades()

    def test_crear_genesis_bloc(self):
        if self.my_db.ultim_bloc() is None:
            bloc_chain = BlockchainUniversity(self.my_db)
            bloc_chain.crear_genesis_bloc()
        self.assertIsNotNone(self.my_db.ultim_bloc())

    def test_minat(self):
        self.test_crear_genesis_bloc()
        bloc_chain = BlockchainUniversity(self.my_db)
        bloc_chain.minat()


class TestInicial(unittest.TestCase):

    def test_inicial(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_inicial()

class TestConexions(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.connexio = Connexions()


    def test_connexio_servidor(self):
        connexio = Connexions()
        connexio.test_server_socket()

    def test_conexio_client(self):
        ip = '192.168.50.26'  # The remote host
        usuari = Factoria.build_usuari_from_db(self.my_db, 'u1050411')
        dada = Factoria.to_json(usuari)
        self.connexio.conexio_client(dada, ip)
#
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
#
# def test_conexio_client(self):
#     HOST = '192.168.50.26'  # The remote host
#     PORT = 50007  # The same port as used by the server
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((HOST, PORT))
#         s.sendall(b'Hello, world udg')
#         data = s.recv(1024)
#     print('Received', repr(data))

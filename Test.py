import unittest

from Crypto.PublicKey import RSA

from BlockchainUniversity import Estudiant, Transaccio, Professor, Examen, Factoria, RespostaExamen, EvaluacioExamen, \
    Bloc, Universitat, Encriptador, Document
from CreateMysql import MySqlBloc

UTF_8 = 'utf8'
ESTUDIANT = 'estudiant'
PROFESSOR = 'professor'


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

    def crear_universitat(self):
        private_key = RSA.generate(1024)
        public_key = private_key.publickey()
        uni = Universitat("Universitat de Girona", private_key, public_key)
        self.my_db.guardar_universitat(uni)

    def crear_usuaris(self):
        usuaris = [[1050411, '40373747T', ESTUDIANT, 'Pau', 'de Jesus Bras'],
                   [1050402, '40373946E', ESTUDIANT, 'Pere', 'de la Rosa'],
                   [1050403, '40332506M', ESTUDIANT, 'Cristina', 'Sabari Vidal'],
                   [2050404, '40332507Y', PROFESSOR, 'Albert', 'Marti Sabari'],
                   [2000256, '40332508Y', PROFESSOR, 'Teodor Maria', 'Jove Lagunas']]

        for id_usuari, nif, tipus, nom, cognom in usuaris:
            key = RSA.generate(1024)
            private_key = key.exportKey('PEM').decode('ascii')
            sql = f'INSERT INTO private_key (`id_usuari`, `private_key`) VALUES({id_usuari}, "{private_key}")'
            self.my_db.exportar_sql(sql)
            public_key = key.publickey()
            if tipus == ESTUDIANT:
                usuari = Estudiant(id_usuari, nif, nom, cognom, public_key)
            elif tipus == PROFESSOR:
                usuari = Professor(id_usuari, nif, nom, cognom, public_key)
            self.my_db.guardar_usuari(usuari)

    def crear_examens(self):
        examens = [[1, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                       f'pdf_minimo.pdf', 2050404, '2022-10-01T13:00', '2022-10-01T14:00'],
                   [2, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity'
                       f'/pdf/Examen_2020-21-_26-03_primer_parcial.pdf', 2000256, '2022-10-01T12:00'
                       , '2022-10-01T13:00']]

        for id_document, nom_fitxer, id_professor, data_inicial, data_final in examens:
            pdf = self.my_db.recuperar_fitxer(nom_fitxer)
            professor = Factoria.build_usuari_from_db(self.my_db, id_professor)
            examen = Examen(id_document, professor, pdf, data_inicial, data_final)
            estudiant = Factoria.build_usuari_from_db(self.my_db, '1050402')
            examen.afegir_estudiants(estudiant)
            self.my_db.guardar_examen(examen)

    def crear_respostes(self):

        respostes = [[1, 1, 1050402, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                      f'Examen_2021_20_10_01_primer_parcial-solucio.pdf'],
                     [2, 2, 1050403, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                      f'Examen_2020-21-_26-03_primer_parcial.pdf']]

        for id_resposta, id_examen, id_usuari,  nom_fitxer in respostes:
            pdf = self.my_db.recuperar_fitxer(nom_fitxer)
            estudiant = Factoria.build_usuari_from_db(self.my_db, id_usuari)
            resposta = RespostaExamen(id_resposta, id_examen, estudiant, pdf)
            self.my_db.guardar_resposta_examen(resposta)

    def crear_evaluacio(self):

        respostes = [[3, 1, 2000256, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                      f'Examen_2021_20_10_01_primer_parcial-solucio.pdf'],
                     [4, 2, 2050404, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                      f'Examen_2020-21-_26-03_primer_parcial.pdf']]

        for id_resposta, id_examen, id_usuari,  nom_fitxer in respostes:
            pdf = self.my_db.recuperar_fitxer(nom_fitxer)
            professor = Factoria.build_usuari_from_db(self.my_db, id_usuari)
            resposta = EvaluacioExamen(id_resposta, id_examen, professor, pdf)
            self.my_db.guardar_resposta_examen(resposta)

    def crear_transaccions(self):
        receptor = Factoria.build_usuari_from_db(self.my_db, 1050402)
        emissor = Factoria.build_usuari_from_db(self.my_db, 2000256)
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        transaccio_inicial = Transaccio(emissor, receptor, examen)
        tr = transaccio_inicial.document.to_json
        self.my_db.guardar_transaccio(transaccio_inicial)
        emissor2 = receptor
        receptor2 = emissor
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf' \
                     f'/Examen_2021_20_10_01_primer_parcial-solucio.pdf'
        pdf = self.my_db.recuperar_fitxer(nom_fitxer)
        resposta = RespostaExamen(1, 1, emissor2, pdf)
        transaccio2 = Transaccio(emissor2, receptor2, resposta)
        self.my_db.guardar_transaccio(transaccio2)


class TestUsuaris(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = 'blockchainuniversity'
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_dades()

    def test_creation(self):
        public_key = RSA.generate(1024).publickey()
        estudiant = Estudiant(1050406, '40332505G', 'Marta', "Rodriguez", public_key)
        self.assertEqual(estudiant.id, 1050406)
        self.assertEqual(estudiant.nif, '40332505G')
        self.assertEqual(estudiant.nom, 'Marta')
        self.assertEqual(estudiant.cognom, 'Rodriguez')
        self.assertEqual(estudiant.public_key, public_key)


class TestUniversitat(unittest.TestCase):
    pass


class TestMysql(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = 'blockchainuniversity'
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
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1050403'), True)

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
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1050403'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1070401'), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'private_key', 'id_usuari', '1050403'), True)

    def test_guardar_usuari(self):
        self.test.crear_schema_dades()
        id_usuari = 1050404
        nif = '40373944C'
        nom = 'Pablo'
        cognom = 'Gutierrez'
        key = RSA.generate(1024)
        public_key = key.publickey()
        estudiant = Estudiant(id_usuari, nif, nom, cognom, public_key)
        self.my_db.guardar_usuari(estudiant)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1050411'), True)
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
        pdf = self.my_db.recuperar_fitxer(nom_fitxer)
        estudiant = Factoria.build_usuari_from_db(self.my_db, 1050411)
        id_resposta = self.my_db.seguent_id_resposta()
        resposta = RespostaExamen(id_resposta, 1, estudiant, pdf)
        self.my_db.guardar_resposta_examen(resposta)


class TestFactoria(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.esborrar_schema('blockchainuniversity')
        self.test = CreacioTaulaTest(self.my_db, 'blockchainuniversity')
        self.test.crear_schema_dades()

    def test_usuari(self):
        estudiant = Factoria.build_usuari_from_db(self.my_db, 1050402)
        self.assertEqual(estudiant.id, 1050402)
        self.assertEqual(estudiant.nom, 'Pere')
        professor = Factoria.build_usuari_from_db(self.my_db, 2000256)
        self.assertEqual(professor.id, 2000256)
        self.assertEqual(professor.nom, 'Teodor Maria')

    def test_examen(self):
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        self.assertEqual(examen.id_document, 1)
        self.assertEqual(examen.usuari.id, 2050404)

    def test_resposta(self):
        resposta = Factoria.build_resposta_alumne_from_db(self.my_db, 1, 1)
        self.assertEqual(resposta.id_document, 1)
        self.assertEqual(resposta.id_examen, 1)
        self.assertEqual(resposta.usuari.id, 1050402)
        self.assertEqual(resposta.usuari.tipus, ESTUDIANT)

    def test_evaluacio(self):
        resposta = Factoria.build_evaluacio_examen_from_db(self.my_db, 1, 3)
        self.assertEqual(resposta.id_document, 3)
        self.assertEqual(resposta.id_examen, 1)
        self.assertEqual(resposta.usuari.id, 2000256)
        self.assertEqual(resposta.usuari.tipus, PROFESSOR)

    def test_transaccio(self):
        receptor = Factoria.build_usuari_from_db(self.my_db, 1050402)
        emissor = Factoria.build_usuari_from_db(self.my_db, 2000256)
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        transaccio_inicial = Transaccio(emissor, receptor, examen)
        self.my_db.guardar_transaccio(transaccio_inicial)
        self.my_db.borrar_dades_taula(self.my_db.schema, "transaccio")
        self.my_db.guardar_transaccio(transaccio_inicial)
        transaccio_guardat = Factoria.build_transaccio_from_db(self.my_db)
        self.assertEqual(transaccio_inicial.emissor.id, transaccio_guardat.emissor.id)
        self.assertEqual(transaccio_inicial.receptor.id, transaccio_guardat.receptor.id)


class TestExamen(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.esborrar_schema('blockchainuniversity')
        self.test = CreacioTaulaTest(self.my_db, 'blockchainuniversity')
        self.test.crear_schema_dades()

    def test_creacio_examen(self):
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = MySqlBloc.recuperar_fitxer(nom_fitxer)
        professor = Factoria.build_usuari_from_db(self.my_db, 2000256)
        examen = Examen(1111, professor, pdf, '00000000', '00000000')

        estudiant1 = Factoria.build_usuari_from_db(self.my_db, 1050411)
        examen.estudiants.append(estudiant1)
        estudiant2 = Factoria.build_usuari_from_db(self.my_db, 1050402)
        examen.estudiants.append(estudiant2)
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = MySqlBloc.recuperar_fitxer(nom_fitxer)
        estudiant = Factoria.build_usuari_from_db(self.my_db, 1050411)
        resposta = RespostaExamen(1, 1, estudiant, pdf)
        examen.respostes.append(resposta)
        self.assertEqual(examen.estudiants[0], estudiant1)
        self.assertEqual(examen.pdf, pdf)
        self.assertEqual(examen.usuari, professor)

    def test_seguent_numero(self):
        num_document = self.my_db.seguent_id_examen()
        self.assertIsNotNone(num_document)

    def test_to_json(self):
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        exament_print = examen.to_dict()
        print(exament_print)
        examen_json = examen.to_json()
        print(examen_json)

    # def test_encript(self):
    #     privat_key = RSA.generate(1024)
    #     public_key = privat_key.publickey()
    #     examen = Factoria.build_examen_from_db(self.my_db, 1)
    #     examen_encript = examen.encriptar(public_key)
    #     examen_j_son = examen.desencriptar(examen_encript, privat_key)
    #     self.assertEqual(examen.to_json(), examen_j_son)


class TestRespostaExamen(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.test = CreacioTaulaTest(self.my_db, 'blockchainuniversity')
        self.test.crear_schema_dades()

    def test_creacio_resposta_examen(self):
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = MySqlBloc.recuperar_fitxer(nom_fitxer)
        estudiant = Factoria.build_usuari_from_db(self.my_db, 1050411)
        resposta = RespostaExamen(1, 1, estudiant, pdf)
        self.assertEqual(resposta.id_document, 1)
        self.assertEqual(resposta.id_examen, 1)
        self.assertEqual(resposta.usuari, estudiant)
        self.assertEqual(resposta.pdf, pdf)

    def test_seguent_numero(self):
        num_document = self.my_db.seguent_id_resposta()
        self.assertIsNotNone(num_document)

    def test_to_json(self):
        resposta = Factoria.build_resposta_examen_from_db(self.my_db, 1,  1)
        resposta_print = resposta.to_dict()
        print(resposta_print)
        examen_json = resposta.to_json()
        print(examen_json)


class TestEvaluacioExamen(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.esborrar_schema('blockchainuniversity')
        self.test = CreacioTaulaTest(self.my_db, 'blockchainuniversity')
        self.test.crear_schema_dades()

    def test_creacio_resposta_examen(self):
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = MySqlBloc.recuperar_fitxer(nom_fitxer)
        estudiant = Factoria.build_usuari_from_db(self.my_db, 1050411)
        resposta = EvaluacioExamen(1, 1, estudiant, pdf)
        self.assertEqual(resposta.id_document, 1)
        self.assertEqual(resposta.id_examen, 1)
        self.assertEqual(resposta.usuari, estudiant)
        self.assertEqual(resposta.pdf, pdf)

    def test_to_json(self):
        evaluacio = Factoria.build_evaluacio_examen_from_db(self.my_db, 1, 3)
        evaluacio_print = evaluacio.to_dict()
        print(evaluacio_print)
        evaluacio_json = evaluacio.to_json()
        print(evaluacio_json)


class TestEncriptador(unittest.TestCase):
    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.esborrar_schema('blockchainuniversity')
        self.test = CreacioTaulaTest(self.my_db, 'blockchainuniversity')
        self.test.crear_schema_dades()

    def test_encriptar_desencriptar(self):
        emissor = Factoria.build_usuari_from_db(self.my_db, 2000256)
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        examen_encriptar = Encriptador(examen, emissor.public_key)
        examen_resultat = examen_encriptar.get_dada(self.my_db.clau_privada(emissor.id))
        examen_final = Examen.create_json(examen_resultat)
        self.assertEqual(examen.id_document, examen_final.id_document)
        self.assertEqual(examen.usuari.id, examen_final.usuari.id)
        self.assertEqual(examen.pdf, examen_final.pdf)
        self.assertEqual(examen.data_creacio, examen_final.data_creacio)


class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = 'blockchainuniversity'
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.my_db.esborrar_schema(self.schema)
        self.my_db.crear_schema(self.schema)
        self.my_db.afegir_schema(self.schema)
        self.my_db.crear_taules_inicials()
        self.test.crear_usuaris()
        self.test.crear_examens()
        self.test.crear_respostes()
        self.test.crear_evaluacio()

    @property
    def crear_transaccio(self):
        receptor = Factoria.build_usuari_from_db(self.my_db, 1050402)
        emissor = Factoria.build_usuari_from_db(self.my_db, 2000256)
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

    def test_to_json(self):
        (receptor, emissor, examen, transaccio) = self.crear_transaccio
        trans_json = transaccio.to_json()
        print(trans_json)

    def test_encriptar(self):
        pass
        # (receptor, emissor, examen, transaccio) = self.crear_transaccio
        # uni = Factoria.build_universitat_from_db(self.my_db)
        # encriptat = Encriptador(transaccio, uni.public_key)
        # transaccio_resultat = encriptat.get_dada(uni.private_key)
        # examen_final = Transaccio..create_json(examen_resultat)
        # self.assertEqual(examen.id_document, examen_final.id_document)
        # self.assertEqual(examen.usuari.id, examen_final.usuari.id)
        # self.assertEqual(examen.pdf, examen_final.pdf)
        # self.assertEqual(examen.data_creacio, examen_final.data_creacio)



class TestBloc(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = 'blockchainuniversity'
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_dades()

    def test_crear(self):
        pass
        # transaccio = Factoria.build_transaccio_from_db(self.my_db)
        # bloc = Bloc(1, transaccio, "")
        # self.my_db.guardar_bloc(bloc)


    # self.assertEqual(bloc_prova.index, 0)
    # self.assertEqual(bloc_prova.transaccio, t1)
    # self.assertEqual(bloc_prova.hash_bloc_anterior, '0')

    # Revisar dona un hash diferent cada cop
    # def test_calcular_Hash(self):
    #     key = RSA.generate(1024)
    #     public_key = key.publickey()
    #     receptor = Factoria.build_usuari_from_db(self.my_db, 1050402)
    #     emissor = Factoria.build_usuari_from_db(self.my_db, 2000256)
    #     examen = Factoria.build_examen_from_db(self.my_db, 1)
    #     examen_encriptar = examen.encriptar(public_key)
    #     transaccio = Transaccio(emissor, receptor, examen_encriptar)
    #     bloc_prova = Bloc(0, '0', transaccio)
    #     hash_anterior = bloc_prova.calcular_hash()
    #     print(hash_anterior)
    #     # self.assertEqual(hash_anterior, '62a1420789f37ee5ddfb6524170c3cf0f5a7083f007e85bcd119bf814befef5a')

class TestBlockchainUniversity(unittest.TestCase):
    pass

    # def test_crear_genesis_bloc(self):
    #     bloc_chain = BlockchainUniversity()
    #     bloc = bloc_chain.ultim_bloc
    #     self.assertEqual(bloc.index, 0)
    #     self.assertEqual(bloc.transaccio, [])
    #     self.assertEqual(bloc.hash_bloc_anterior, '0')
    #
    # def test_minat(self):
    #     bloc_chain = BlockchainUniversity()
    #     estudiant = Estudiant('Pau')
    #     professor = Professor('Teo')
    #     t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
    #     bloc_chain.afegir_nova_transaccio(t1)
    #     t2 = TransaccioExamen(professor, 'DocumentEncriptat', 'idDocument', 10)
    #     bloc_chain.afegir_nova_transaccio(t2)
    #
    #     for x in bloc_chain.transaccio_noconfirmades:
    #         y = 0
    #         if x is not None:
    #             print(bloc_chain.minat())
    #         y += y
    #         x = []

    # def test_llegir_pdf(self):
    #     nom_fitxer = f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
    #     pdf_file = open(nom_fitxer, "rb")
    #     my_db = MySqlBloc('localhost', 'root', 'root')
    #     my_db.crear_schema_dades(my_db, 'blockchainuniversity')
    #     id_document = 1
    #     id_tipus = 1
    #     versio = 1
    #     id_usuari = 1050412
    #     save_pdf = base64.b64encode(pdf_file.read())
    #     pdf_file.close()
    #     sql = f'INSERT INTO documents (`id_document`, `id_tipus`, `versio`, `id_usuari`, `pdf`) VALUES({id_document}, ' \
    #           f'{id_tipus}, {versio}, {id_usuari}, "{save_pdf}") '
    #     my_db.exportar_sql(sql)

    # def test_print_pdf(self, pdffile, printer_name):
    #     # acroread = r'C:\Program Files (x86)\Adobe\Reader 11.0\Reader\AcroRd32.exe'
    #     acrobat = r'C:\Program Files (x86)\Adobe\Acrobat 11.0\Acrobat\Acrobat.exe'
    #
    #     # '"%s"'is to wrap double quotes around paths
    #     # as subprocess will use list2cmdline internally if we pass it a list
    #     # which escapes double quotes and Adobe Reader doesn't like that
    #
    #     cmd = '"{}" /N /T "{}" "{}"'.format(acrobat, pdffile, printer_name)
    #
    #     proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     stdout, stderr = proc.communicate()
    #     exit_code = proc.wait()

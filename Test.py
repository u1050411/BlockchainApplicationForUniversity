import base64
import datetime
import subprocess
import unittest
from random import Random

from Crypto.PublicKey import RSA

from BlockchainUniversity import Universitat, Estudiant, Transaccio, Professor,  Bloc, Examen, Usuari, \
    Factoria, RespostaExamen
from CreateMysql import MySqlBloc
from PyPDF2 import PdfFileMerger, PdfFileReader

UTF_8 = 'utf8'
ESTUDIANT = 'estudiant'
PROFESSOR = 'professor'


class TestUsuaris(unittest.TestCase):

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


class TestTransaction(unittest.TestCase):

    def test_creation(self):
        schema = 'blockchainuniversity'
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, schema)
        my_db.afegir_schema(schema)
        receptor = Factoria.build_usuari_from_db(my_db, 1050402, ESTUDIANT)
        emissor = Factoria.build_usuari_from_db(my_db, 2000256, PROFESSOR)
        transaccio = Transaccio(emissor, receptor, 'idDocument')
        self.assertEqual(transaccio.emissor, emissor)
        self.assertEqual(transaccio.document, 'DocumentEncriptat')
        self.assertEqual(transaccio.nota, 0)
        self.assertEqual(transaccio.id_document, 'Hash')

    # def test_posarNota(self):
    #     cua = []
    #     estudiant = Estudiant('Pau')
    #     professor = Professor('Teo')
    #     t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
    #     cua.append(t1)
    #     t2 = TransaccioExamen(professor, 'DocumentEncriptat', 'Hash', 10)
    #     cua.append(t2)
    #     for x in cua:
    #         x.display_transaccio()
    #         print('--------------')
    #
    # @staticmethod
    # def test_sign_transaction():
    #     estudiant = Estudiant('Pau')
    #     t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
    #     t1.sign_transaction()

    def test_to_Json(self):
        estudiant = Estudiant('Pau')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
        x = t1.to_json()
        # jtrans = json.loads(t1.to_json())
        # print(json.dumps(jtrans, indent=4))
        print(x)


class TestBloc(unittest.TestCase):

    def test_blocInicial(self):
        estudiant = Estudiant('Pau')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
        bloc_prova = Bloc(0, '0', t1)

        self.assertEqual(bloc_prova.index, 0)
        self.assertEqual(bloc_prova.transaccio, t1)
        self.assertEqual(bloc_prova.hash_bloc_anterior, '0')

    #Revisar dona un hash diferent cada cop
    # def test_calcular_Hash(self):
    #     estudiant = Estudiant('Albert')
    #     t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
    #     bloc_prova = Bloc(0, '0', t1)
    #     hash_anterior = bloc_prova.calcular_hash()
    #     print(hash_anterior)
    #     # self.assertEqual(hash_anterior, '62a1420789f37ee5ddfb6524170c3cf0f5a7083f007e85bcd119bf814befef5a')


class TestBlockchainUniversity(unittest.TestCase):

    def test_crear_genesis_bloc(self):
        pass
    # bloc_chain = BlockchainUniversity()
    # bloc = bloc_chain.ultim_bloc
    # self.assertEqual(bloc.index, 0)
    # self.assertEqual(bloc.transaccio, [])
    # self.assertEqual(bloc.hash_bloc_anterior, '0')

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


class TestMysql(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = 'blockchainuniversity'

    def tearDown(self):
        self.my_db.tancar()

    @classmethod
    def crear_schema_test(cls, my_db, schema):
        my_db.esborrar_schema(schema)
        my_db.crear_schema(schema)
        cls.crear_taules()
        cls.crear_usuaris()
        cls.crear_examens()

    def crear_schema_dades(self):
        self.my_db.esborrar_schema(self.schema)
        self.my_db.crear_schema(self.schema)
        self.crear_taules()
        self.crear_usuaris()
        self.crear_examens()

    def crear_taules(self):
        sqls = ["CREATE TABLE if not exists `usuari` ("
                "`id` int NOT NULL,"
                "`nif` varchar(9) NOT NULL,"
                "`nom` varchar(45) DEFAULT NULL,"
                "`cognom` varchar(100) DEFAULT NULL,"
                "PRIMARY KEY (`id`, `nif`)) ",

                "CREATE TABLE if not exists `private_key` ("
                "`id_usuari` INT NOT NULL,"
                "`private_key` longtext NULL,"
                "PRIMARY KEY (`id_usuari`))",

                "CREATE TABLE if not exists `public_key` ("
                "`id_usuari` INT NOT NULL,"
                "`public_key` longtext NULL,"
                "PRIMARY KEY (`id_usuari`))",

                "CREATE TABLE if not exists `transaccio` ("
                "`id` INT NOT NULL,"
                "`id_emisor` INT NOT NULL,"
                "`id_receptor` INT NOT NULL,"
                "`id_document` INT NOT NULL,"
                "`data` DATETIME NOT NULL,"
                "PRIMARY KEY(`id`, `id_emisor`, `id_receptor`, `id_document`, `data`))",

                # "CREATE TABLE if not exists `document` ("
                # "`id_document` INT NOT NULL,"
                # "PRIMARY KEY (`id_document`))",

                "CREATE TABLE if not exists `examen` ("
                "`id_document` INT NOT NULL,"
                "`id_professor` INT NOT NULL,"
                "`nota` INT NULL,"
                "`data_examen` DATETIME NOT NULL,"
                "`data_inici` DATETIME NULL,"
                "`data_final` DATETIME NULL,"
                "`pdf` LONGBLOB  NULL,"
                "PRIMARY KEY (`id_document`))",

                "CREATE TABLE if not exists `estudiant_examen` ("
                "`id_document` INT NOT NULL,"
                "`id_estudiant` INT NOT NULL,"
                "PRIMARY KEY (`id_document`, `id_estudiant`))",

                "CREATE TABLE if not exists `resposta_examen` ("
                "`id_document` INT NOT NULL,"
                "`id_resposta` INT NOT NULL,"
                "`data_creacio` DATETIME NOT NULL,"
                "`id_usuari` INT NOT NULL,"
                "`pdf` LONGBLOB  NULL,"
                "PRIMARY KEY (`id_document`, `id_resposta`))"]

        for sql in sqls:
            self.my_db.exportar_sql(sql)

    def crear_usuaris(self):
        usuaris = [[1050411, '40373747T', 'Pau', 'de Jesus Bras'],
                   [1050402, '40373946E', 'Pere', 'de la Rosa'],
                   [1050403, '40332506M', 'Cristina', 'Sabari Vidal'],
                   [2050404, '40332507Y', 'Albert', 'Marti Sabari'],
                   [2000256, '40332508Y', 'Teodor Maria', 'Jove Lagunas']]

        for id_usuari, nif, nom, cognom in usuaris:
            self.my_db.guardar_usuari(id_usuari, nif, nom, cognom)

    def crear_examens(self):
        examens = [[10001, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity'
                           f'/pdf/GEINF DOC1 full de TFG_V2.pdf', 2050404, '2022-10-01T13:00', '2022-10-01T14:00'],
                   [20001, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity'
                           f'/pdf/GEINF DOC1 full de TFG_V2.pdf', 2000256, '2022-10-01T12:00', '2022-10-01T13:00'],
                   [30001, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity'
                           f'/pdf/GEINF DOC1 full de TFG_V2.pdf', 2000256, '2022-10-01T12:00', '2022-10-01T13:00'],
                   [40001, f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity'
                           f'/pdf/GEINF DOC1 full de TFG_V2.pdf', 2050404, '2022-10-01T13:00', '2022-10-01T14:00']]

        for id_document, nom_fitxer, id_professor, data_inicial, data_final in examens:
            pdf = self.my_db.recuperar_fitxer(nom_fitxer)
            professor = Factoria.build_usuari_from_db(self.my_db, id_professor, PROFESSOR)
            examen = Examen(id_document, professor, pdf, data_inicial, data_final)
            self.my_db.guardar_examen(examen)

    def test_afegir(self):
        self.my_db.afegir_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), True)

    def test_esborrar_schema(self):
        self.crear_schema_dades()
        self.my_db.esborrar_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), False)

    def test_crear_schema(self):
        self.my_db.crear_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), True)

    def test_exportar_sql(self):
        self.crear_schema_dades()
        sql = "CREATE TABLE if not exists `TaulaProva` (" \
              "`id` int NOT NULL,"\
              "`nif` varchar(9) NOT NULL," \
              "`nom` varchar(45) DEFAULT NULL,"\
              "`cognom` varchar(100) DEFAULT NULL,"\
              "PRIMARY KEY (`id`, `nif`)) "
        self.my_db.exportar_sql(sql)
        self.assertEqual(self.my_db.existeix(self.schema, 'TaulaProva', None, None), True)

    def test_crear_taules(self):
        schema = self.schema
        self.my_db.esborrar_schema(schema)
        self.my_db.crear_schema(schema)
        self.crear_taules()
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', None, None), True)

    def test_retorn_schema(self):
        self.my_db.afegir_schema(self.schema)
        schema = self.my_db.schema
        self.assertEqual(self.schema, schema)

    def test_crear_usuaris(self):
        self.test_crear_taules()
        self.crear_usuaris()
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1050403'), True)

    def test_crear_examens(self):
        self.my_db.esborrar_schema(self.schema)
        self.my_db.crear_schema(self.schema)
        self.crear_taules()
        self.crear_usuaris()
        self.crear_examens()

    def test_existeix(self):
        self.crear_schema_dades()
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), True)
        self.assertEqual(self.my_db.existeix('noSchema', None, None, None), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', None, None), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'no_Taula', None, None), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'nom', None), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'no_Columna', None), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1050403'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1070401'), False)
        self.assertEqual(self.my_db.existeix(self.schema, 'private_key', 'id_usuari', '1050403'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'public_key', 'id_usuari', '1050403'), True)

    def test_guardar_usuari(self):
        self.crear_schema_dades()
        id_usuari = 1050404
        nif = '40373944C'
        nom = 'Pablo'
        cognom = 'Gutierrez'
        self.my_db.guardar_usuari(id_usuari, nif, nom, cognom)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1050411'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'nom', 'Pere'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'private_key', 'id_usuari', '1050411'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'public_key', 'id_usuari', '1050411'), True)

    def test_clau(self):
        self.crear_schema_dades()
        id_usuari = 1050402
        privat_key = self.my_db.clau_privada(id_usuari)
        public_key = self.my_db.clau_publica(id_usuari)
        self.assertTrue(privat_key.public_key(), public_key)

    def test_seguent_numero(self):
        self.crear_schema_dades()
        num_maxim = self.my_db.seguent_id_examen()
        self.assertIsNotNone(num_maxim)

    def test_guardar_resposta(self):
        self.crear_schema_dades()
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = self.my_db.recuperar_fitxer(nom_fitxer)
        estudiant = Factoria.build_usuari_from_db(self.my_db, 1050411, ESTUDIANT)
        id_resposta = self.my_db.seguent_id_resposta(100001)
        resposta = RespostaExamen(id_resposta, estudiant, pdf)
        self.my_db.guardar_resposta_examen(10001, resposta)


class TestFactoria(unittest.TestCase):

    def setUp(self):
        my_db = MySqlBloc('localhost', 'root', 'root')
        TestMysql.crear_schema_test(my_db, 'blockchainuniversity')

    # def tearDown(self):
    #     self.my_db.tancar()

    def test_usuari(self):

        # my_db.crear_schema_dades(my_db, schema)
        estudiant = Factoria.build_usuari_from_db(my_db, 1050402, ESTUDIANT)
        self.assertEqual(estudiant.id, 1050402)
        self.assertEqual(estudiant.nom, 'Pere')
        professor = Factoria.build_usuari_from_db(my_db, 2000256, PROFESSOR)
        self.assertEqual(professor.id, 2000256)
        self.assertEqual(professor.nom, 'Teodor Maria')

    def test_examen(self):
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, 'blockchainuniversity')
        examen = Factoria.build_examen_from_db(my_db, 10001)
        self.assertEqual(examen.id_document, 10001)
        self.assertEqual(examen.professor.id, 2050404)


class TestExamen(unittest.TestCase):

    def test_creacio_examen(self):
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, 'blockchainuniversity')
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = MySqlBloc.recuperar_fitxer(nom_fitxer)
        professor = Factoria.build_usuari_from_db(my_db, 2000256, PROFESSOR)
        examen = Examen(10001, professor, pdf, '00000000', '00000000')
        estudiant1 = Factoria.build_usuari_from_db(my_db, 1050411, ESTUDIANT)
        examen.estudiants.append(estudiant1)
        estudiant2 = Factoria.build_usuari_from_db(my_db, 1050402, ESTUDIANT)
        examen.estudiants.append(estudiant2)
        self.assertEqual(examen.estudiants[0], estudiant1)
        self.assertEqual(examen.pdf, pdf)
        self.assertEqual(examen.professor, professor)

    def test_seguent_numero(self):
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, 'blockchainuniversity')
        num_document = my_db.seguent_id_examen()
        self.assertIsNotNone(num_document)


class TestRespostaExamen(unittest.TestCase):

    def test_creacio_resposta_examen(self):
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, 'blockchainuniversity')
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = MySqlBloc.recuperar_fitxer(nom_fitxer)
        estudiant1 = Factoria.build_usuari_from_db(my_db, 1050411, ESTUDIANT)
        resposta = RespostaExamen(100001, estudiant1, pdf)
        self.assertEqual(resposta.id_resposta, 100001)
        self.assertEqual(resposta.usuari, estudiant1)
        self.assertEqual(resposta.pdf, pdf)

    def test_seguent_numero(self):
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, 'blockchainuniversity')
        num_document = my_db.seguent_id_resposta(100001)
        self.assertIsNotNone(num_document)









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
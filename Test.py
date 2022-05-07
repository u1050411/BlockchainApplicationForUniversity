import base64
import subprocess
import unittest
from random import Random

from Crypto.PublicKey import RSA

from BlockchainUniversity import Universitat, Estudiant, Transaccio, Professor, TransaccioExamen, Bloc, Examen, Usuari, \
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
        # self.assertEqual(transaccio.emissor, emissor)
        # self.assertEqual(transaccio.document, 'DocumentEncriptat')
        # self.assertEqual(transaccio.nota, 0)
        # self.assertEqual(transaccio.id_document, 'Hash')

    def test_posarNota(self):
        cua = []
        estudiant = Estudiant('Pau')
        professor = Professor('Teo')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
        cua.append(t1)
        t2 = TransaccioExamen(professor, 'DocumentEncriptat', 'Hash', 10)
        cua.append(t2)
        for x in cua:
            x.display_transaccio()
            print('--------------')

    @staticmethod
    def test_sign_transaction():
        estudiant = Estudiant('Pau')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
        t1.sign_transaction()

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

    def test_calcular_Hash(self):
        estudiant = Estudiant('Albert')
        t1 = Transaccio(estudiant, 'DocumentEncriptat', 'idDocument')
        bloc_prova = Bloc(0, '0', t1)
        hash_anterior = bloc_prova.calcular_hash()
        print(hash_anterior)


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

    def test_afegir(self):
        self.my_db.afegir_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), True)

    def test_esborrar_schema(self):
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
        self.my_db.esborrar_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), False)

    def test_crear_schema(self):
        self.my_db.crear_schema(self.schema)
        self.assertEqual(self.my_db.existeix(self.schema, None, None, None), True)

    def test_exportar_sql(self):
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
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
        self.my_db.crear_taules()
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', None, None), True)

    def test_crear_usuaris(self):
        self.test_crear_taules()
        self.my_db.crear_usuaris()
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', '1050403'), True)

    def test_crear_examens(self):
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
        self.my_db.crear_examens()

    def test_existeix(self):
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
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
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
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
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
        id_usuari = 1050402
        privat_key = self.my_db.clau_privada(id_usuari)
        public_key = self.my_db.clau_publica(id_usuari)
        self.assertTrue(privat_key.public_key(), public_key)

    def test_seguent_numero(self):
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
        num_maxim = self.my_db.numero_maxim_document('examen', 'id_document')
        print(num_maxim)

    def test_guardar_resposta(self):
        MySqlBloc.crear_schema_dades(self.my_db, self.schema)
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = self.my_db.recuperar_fitxer(nom_fitxer)
        estudiant = Factoria.build_usuari_from_db(self.my_db, 1050411, ESTUDIANT)
        id_resposta = RespostaExamen.seguent_numero(self.my_db, 100001)
        resposta = RespostaExamen(id_resposta, estudiant, pdf)

        self.my_db.guardar_resposta_examen(10001, resposta)


class TestFactoria(unittest.TestCase):

    def test_usuari(self):
        schema = 'blockchainuniversity'
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, schema)
        estudiant = Factoria.build_usuari_from_db(my_db, 1050402, ESTUDIANT)
        self.assertEqual(estudiant.id, 1050402)
        self.assertEqual(estudiant.nom, 'Pere')
        professor = Factoria.build_usuari_from_db(my_db, 2000256, PROFESSOR)
        self.assertEqual(professor.id, 2000256)
        self.assertEqual(professor.nom, 'Teodor Maria')

    def test_examen(self):
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, 'blockchainuniversity')
        examen = Factoria.build_examen_from_db(my_db, 10000)
        self.assertEqual(examen.id_document, 10000)


class TestExamen(unittest.TestCase):

    def test_creacio_examen(self):
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, 'blockchainuniversity')
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = MySqlBloc.recuperar_fitxer(nom_fitxer)
        professor = Factoria.build_usuari_from_db(self.my_db, 2000256, PROFESSOR)
        examen = Examen(10001, professor, pdf, '00000000', '00000000')
        estudiant1 = Factoria.build_usuari_from_db(self.my_db, 1050411, ESTUDIANT)
        examen.estudiants.append(estudiant1)
        estudiant2 = Factoria.build_usuari_from_db(self.my_db, 1050402, ESTUDIANT)
        examen.estudiants.append(estudiant2)
        self.my_db.guardar_examen(examen)

    def test_seguent_numero(self):
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, 'blockchainuniversity')
        num_document = Examen.seguent_numero(my_db)
        print(num_document)


class TestRespostaExamen(unittest.TestCase):

    def test_creacio_resposta_examen(self):
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, 'blockchainuniversity')
        nom_fitxer = f'C:/Users/u1050/PycharmProjects/' \
                     f'BlockchainApplicationForUniversity/pdf/GEINF DOC1 full de TFG_V2.pdf'
        pdf = MySqlBloc.recuperar_fitxer(nom_fitxer)
        estudiant1 = Factoria.build_usuari_from_db(my_db, 1050411, ESTUDIANT)
        RespostaExamen(100001, estudiant1, pdf)

    def test_seguent_numero(self):
        my_db = MySqlBloc('localhost', 'root', 'root')
        my_db.crear_schema_dades(my_db, 'blockchainuniversity')
        num_document = RespostaExamen.seguent_numero(my_db, 100001)
        print(num_document)


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








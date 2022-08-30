import hashlib
import json
import unittest

from Crypto.PublicKey import RSA

from BlockWeb.Comunicacio import Paquet
from BlockchainUniversity import Estudiant, Transaccio, Professor, Examen, Factoria, RespostaExamen, AvaluacioExamen, \
    Bloc, Universitat, Encriptador, BlockchainUniversity, Pdf, Assignatura
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


    def crear_schema_inicial(self):
        self.my_db.esborrar_schema(self.schema)
        self.my_db.crear_schema(self.schema)
        self.my_db.afegir_schema(self.schema)
        self.my_db.crear_taules_inicials()
        self.crear_universitat()
        self.crear_usuaris()
        self.crear_assignatures()
        self.crear_pdf()
        # self.crear_genesis_bloc()

    def crear_universitat(self):
        univ = [{"id": 1,"ip": "192.168.50.25", "nom": "Universitat de Girona",
          "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIICWwIBAAKBgQDWYgDCSOewWQPyr673t9bsMIiLjykjryY8qxz4QHHv+b5l2PeB\n5aZjziAcDEWrcaFnfgH7TrB09QRwdRCs7GWISM3+oTcdQ6nAw/SpWK1hRbeI/y+P\nhtOJBe2Z5bzIXjNU4BMCGtpvI8jKGR7cVEtOhlebl01ehSNO2JzEsAOQVwIDAQAB\nAoGAC1pyLUWMkLXWHUKHIuC5ql54MU9OlpUObg4Uqj9JwEXa6HWaEEKVpIctlZM/\nFwNmPmgip5aVGN7U8lqMLtDLRMZNNuS+r2cIqeCLlTPyKSmnw+/IkpBfRAkGHaUK\n7on/+cxB1ASy8yNqAPQxmAH4N1mdn9TW7aGQSyZsSxkN32ECQQDmcHqT+ss5CpGJ\nVWRpFy2hL25mOng+Rq77IsFOZeL41Fqfc+K2P297gl1SS0j3viBCjkDtOfmuQ8Uk\n3CZcNQVnAkEA7imVvGz7Dpbl+EnaSDLJSKR6mmUgvUL85hSRO4IAtpsmJ3G9aUv+\nGkQZxYLV75IBFVc241zl32HZ0OBBNL7XkQJAPaKOFrB41Lvv61Sss7MgYEFofO1c\npgOP39oO7CIyUC20Q3vigq566gUXYuCCFsmCpWqZERp1nte/jjlYBUelNwJAE0zd\nbJKsWcdSxac+gEFVXISvxtlRKOVH12FtT5Q+eI3kLqgiAGl/IyPHruDmc26ylccm\nlJBPtKWaYDn8LskUcQJAc0GeTF3/EiClAMrNTnCbM7FKr7we+fGtnyuQxbLABSkk\nsb2OnhzJLzm+BkOU9AoeZoxGsoa5iBrMapkYr517yw==\n-----END RSA PRIVATE KEY-----",
          "public_key": "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDWYgDCSOewWQPyr673t9bsMIiL\njykjryY8qxz4QHHv+b5l2PeB5aZjziAcDEWrcaFnfgH7TrB09QRwdRCs7GWISM3+\noTcdQ6nAw/SpWK1hRbeI/y+PhtOJBe2Z5bzIXjNU4BMCGtpvI8jKGR7cVEtOhleb\nl01ehSNO2JzEsAOQVwIDAQAB\n-----END PUBLIC KEY-----"},
         # {"id": 3, "ip": "192.168.50.28", "nom": "Universitat Politecnica Catalunya",
         #  "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIICWwIBAAKBgQCchauIJX8B/mlEc+HjYTz9TgymwPJ589ntbaoO44AIES7l1CT5\nL1mE44f5W8VBtIK6xE+y5E0mkNlnKt02nsHuxwjYj1olsZ66mTqjtrdizAPv/otA\nQtU93fX9sQLH0QoPRz554CmyjapbtobaYI6xcqRwxIu/FG04TJ0KRt4EZQIDAQAB\nAoGABFVFzReVcm8u59u50BGNkck629TxZ+nilkpkz+1OMPfIAuNo5wZMcqIMtINs\n+XQvWE9KxSRbDgT3JJfqfT9PSN6K4NxkjraGbj3Nsv9m1C1LxJNNxPhUoukv/5ZR\no7zJf+bmX/6UsQvewNFS/gVtLIvtEQbpvDFrTCxIv07nfUMCQQC5l2nApGbeXnOS\n8li4iwkwObr1AsLKeSEVG6aY0b4lxgm1dvV0AQlwpiPVw16hSdXoonMZk2k2U8/H\nE00XyLhDAkEA1+cN6tQuHT0JbdSz35CMjoUgx3L50pt2Bxr/EraKMcIY5n/zlpqj\naxLhYtfsLInYhP8wialRX3ZTF0dWe6/6NwJALI8tBeKzDBrTVum24YAIUbrap27l\nQ+W3SrEb278oDzuwIxCPuC1zjcdl/THuK31lzXgLeI2LCk8vKNX6gYZgrwJAQg1M\nMrWrTgKoadOTHCiK9+c+ugYw6//nwhC+TKlP6h0ppQssKL0ylcV28tiARrf9Z+Ly\npIsKfBwlG5AVo02ZTQJAWLk056zopXHRjy2wVSk+mrxrX9fmSGQndKo32x0Gq9dG\njzCvS/H2iyojw9GzB4jSxLVMTVYXcvlj4RSWMAXA1A==\n-----END RSA PRIVATE KEY-----",
         #  "public_key": "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCchauIJX8B/mlEc+HjYTz9Tgym\nwPJ589ntbaoO44AIES7l1CT5L1mE44f5W8VBtIK6xE+y5E0mkNlnKt02nsHuxwjY\nj1olsZ66mTqjtrdizAPv/otAQtU93fX9sQLH0QoPRz554CmyjapbtobaYI6xcqRw\nxIu/FG04TJ0KRt4EZQIDAQAB\n-----END PUBLIC KEY-----"},
         {"id": 2, "ip": "192.168.50.27", "nom": "Universitat Rovira i Virgili",
          "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIICXAIBAAKBgQCWY6jFMVyA2FolRbB91q1EeUVwxX6Hma4sMXlyqgsLHJ5QU7Ke\nAXTU7IMzsOpTfn+xE6l86w0R+5ZWu1BsC1z6XxE8ZgWbMSzR9Bs6aMGd4rAHca4w\nJ8nMUWyCvjoehm+/WYtw3e8d5YvkQY9PMUCe4Vpfg2lRReDO/qwScS9+uwIDAQAB\nAoGAAxN5xcLLNhV2zpFc2U4VUDO80GAxxNtHXT8L0WUaAbmtoU389s9n0N0fl+ST\n/m41dW1GB7iVFVuUiSSesf8PgUV+oobVcFfKt2AzoGBQYKKDh1D4BovB+hQihzFu\n+no4XOmGk7KPWUhK2mThJ4OvPwg3HYUt7iKVlgQSMUoAMMkCQQDDSc3f4uemWaHg\nkNdK7jS4by9JbJqFZVj0FcFoUwnnqnk6GLJuNvhxEKhG1JyZ8Xi/xfZIuur7Ch0c\nG8hDVFyJAkEAxSSG+X15uo6YpmYWW0VWFqW1+TYfjwEUhmC3/DU0qnNSLOn218qC\nhxNPILlJG+P4r9OsfbjwRJb8biAemaoYIwJBAIJUCfIlgwVQgijVYOjfyg1gHkW5\nFfJ6bYAP2NBfwpd5/IdaHhJR20HRpQwILi7KqRQK8E8fd1xsJnswy1irv0kCQCvN\nFtQd5crmXdIywmra9+qmPM03EkHyqn3ExXwa0i3A25QxE3AUhXW/e4g4wp6YwytF\nq4Bvc6q5pTJOnp3jpeMCQDP2LV5cfP9WuPzMW5Fkc1nScFVme35PaVkgUQ4zO02B\nWgCMViwfHSnIrrtSICT1MoLHH4UqdtHavHAIcwZlGfM=\n-----END RSA PRIVATE KEY-----",
          "public_key": "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCWY6jFMVyA2FolRbB91q1EeUVw\nxX6Hma4sMXlyqgsLHJ5QU7KeAXTU7IMzsOpTfn+xE6l86w0R+5ZWu1BsC1z6XxE8\nZgWbMSzR9Bs6aMGd4rAHca4wJ8nMUWyCvjoehm+/WYtw3e8d5YvkQY9PMUCe4Vpf\ng2lRReDO/qwScS9+uwIDAQAB\n-----END PUBLIC KEY-----"}
        ]

        for y in univ:
            x = json.dumps(y, indent=4, sort_keys=True, default=str)
            id = json.loads(x)['id']
            nom = json.loads(x)['nom']
            ip = json.loads(x)['ip']
            if id == 1:
                private = RSA.importKey(json.loads(x)['private_key'])
            else:
                private = None
            public = RSA.importKey(json.loads(x)['public_key'])
            uni = Universitat(nom, private, public, id, ip)
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
            key = RSA.generate(1024, randfunc=None, e=65537)
            private_key = key.exportKey('PEM').decode('ascii')
            sql = f'INSERT INTO private_key (`id_usuari`, `private_key`) VALUES("{id_usuari}", "{private_key}")'
            self.my_db.exportar_sql(sql)
            public_key = key.publickey()
            usuari = None
            if tipus == ESTUDIANT:
                usuari = Estudiant(id_usuari, nif, nom, cognom, public_key, contrasenya, email)
            elif tipus == PROFESSOR:
                usuari = Professor(id_usuari, nif, nom, cognom, public_key, contrasenya, email)
            self.my_db.guardar_usuari(usuari)

    def crear_assignatures(self):

        assignatures = [[1, 'Sistemes operatius', 'u2000256'], [2, 'Computadors', 'u2050404']]

        for id_assig, nom, id_professor in assignatures:
            professor = Factoria.build_usuari_from_db(self.my_db, id_professor)
            assignatura = Assignatura(id_assig, nom, professor)
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

        avaluacions = [[1, 1, 1, 'u2000256', f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                                        f'Examen_2021_20_10_01_primer_parcial-solucio.pdf', 'u1050411',8],
                     [2, 2, 2, 'u2050404', f'C:/Users/u1050/PycharmProjects/BlockchainApplicationForUniversity/pdf/'
                                        f'Examen_2020-21-_26-03_primer_parcial.pdf', 'u1050402',4]]

        for id_avaluacio, id_resposta, id_examen, id_professor, nom_fitxer, estudiant, nota in avaluacions:
            pdf = Factoria.recuperar_fitxer(nom_fitxer)
            professor = Factoria.build_usuari_from_db(self.my_db, id_professor)
            resposta = Factoria.build_id_resposta_alumne_from_db(self.my_db, id_resposta)
            estudiant = Factoria.build_usuari_from_db(self.my_db, estudiant)
            avaluacio_examen = AvaluacioExamen(resposta, professor, estudiant, pdf, nota, id_avaluacio)
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

    def crear_bloc(self):
        transaccio = Factoria.build_transaccio_from_db(self.my_db)
        bloc = Bloc(0, transaccio, self.my_db)
        self.my_db.guardar_bloc_dades(bloc)



class TestUsuaris(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_dades()


    def test_creation(self):
        public_key = RSA.generate(1024, randfunc=None, e=65537).publickey()
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
        key = RSA.generate(1024, randfunc=None, e=65537)
        public_key = key.publickey()
        estudiant = Estudiant(id_usuari, nif, nom, cognom, public_key, password)
        self.my_db.guardar_usuari(estudiant)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'id', 'u1050411'), True)
        self.assertEqual(self.my_db.existeix(self.schema, 'usuari', 'nom', 'Pere'), True)

    def test_clau(self):
        self.test.crear_schema_dades()
        id_usuari = 1050702
        privat_key = RSA.generate(1024, randfunc=None, e=65537)
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
        self.test.crear_transaccions()
        self.test.crear_bloc()
        ultim_bloc = Factoria.build_ultim_bloc_from_db((self.my_db))
        transactions = Factoria.build_transaccio_from_db(self.my_db)
        emissor = transactions.emissor
        index = ultim_bloc.id + 1
        new_bloc = Bloc(index, transactions, self.my_db)
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
        self.test.crear_transaccions()
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
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_dades()


    def test_encriptar_desencriptar(self):
        universitat = Factoria.build_universitat_from_db(self.my_db)
        receptor = Factoria.build_usuari_from_db(self.my_db, 'u1050402')
        emissor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        transaccio = Transaccio(emissor, receptor, examen, "0")
        transaccio_encriptar = Encriptador(transaccio, universitat.public_key)
        transaccio_byte = str.encode(Factoria.to_json(transaccio_encriptar))
        transaccio_json = transaccio_byte.decode()
        encriptat = Encriptador.crear_json(transaccio_json)
        transaccio2 = Transaccio.crear_json(encriptat.desencriptar(universitat.private_key))
        self.assertEqual(transaccio.id_transaccio, transaccio2.id_transaccio)


    def test_signar_verificar(self):
        universitat = Factoria.build_universitat_from_db(self.my_db)
        receptor = Factoria.build_usuari_from_db(self.my_db, 'u1050402')
        emissor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        transaccio = Transaccio(emissor, receptor, examen, "0")
        transaccio_encriptar = Encriptador(transaccio, universitat.public_key)
        transaccio_json = str.encode(Factoria.to_json(transaccio_encriptar))
        signatura = Encriptador.signar(transaccio_json,universitat.private_key)
        validacio = Encriptador.verificar_sign(transaccio_json, signatura, universitat.public_key)
        self.assertTrue(Encriptador.verificar_sign(transaccio_json, signatura, universitat.public_key))


class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_dades()

    @property
    def crear_transaccio(self):
        receptor = Factoria.build_usuari_from_db(self.my_db, 'u1050402')
        emissor = Factoria.build_usuari_from_db(self.my_db, 'u2000256')
        examen = Factoria.build_examen_from_db(self.my_db, 1)
        transaccio = Transaccio(emissor, receptor, examen, '01')
        return receptor, emissor, examen, transaccio

    def test_guardar(self):
        self.my_db.esborrar_taula('transaccio')
        (receptor, emissor, examen, transaccio_inicial) = self.crear_transaccio
        self.my_db.guardar_transaccio(transaccio_inicial)
        transaccio = Factoria.build_transaccio_from_db(self.my_db)
        self.assertEqual(transaccio.emissor.id, emissor.id)
        self.assertEqual(transaccio.receptor.id, receptor.id)
        self.assertEqual(transaccio.id_document, transaccio_inicial.id_document)


class TestBloc(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        # self.test = CreacioTaulaTest(self.my_db, self.schema)
        # self.test.crear_schema_dades()

    def test_crear(self):
        transaccio = Factoria.build_transaccio_from_db(self.my_db)
        bloc = Bloc(0, transaccio, self.my_db)
        uni = Factoria.build_universitat_from_db(self.my_db)
        Encriptador_json = Encriptador.crear_json(bloc.transaccio)
        transaccio_json = Encriptador_json.desencriptar(uni.private_key)
        transaccio_final = Transaccio.crear_json(transaccio_json)

        self.assertEqual(transaccio.emissor.id, transaccio_final.emissor.id)

    def test_to_json(self):
        bloc = Factoria.build_bloc_from_db(self.my_db, 1)
        bloc_json = Factoria.to_json(bloc)
        bloc2 = Bloc.crear_json(bloc_json)
        self.assertEqual(bloc.id, bloc2.id)


class TestPaquet(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA

    def test_to_json(self):
        bloc = Factoria.build_bloc_from_db(self.my_db, self.my_db.id_ultim_bloc())
        id_ultim_bloc = self.my_db.id_ultim_bloc()
        paquet = Paquet(bloc, '192.168.50.27:5005')
        paquet_json = Factoria.to_json(paquet)
        paquet2 = Paquet.crear_json(paquet_json)
        self.assertEqual(paquet.pas, paquet2.pas)




class TestBlockchainUniversity(unittest.TestCase):

    def setUp(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.my_db.afegir_schema(SCHEMA)
        # self.test = TestInicial()
        # self.test.test_inicial()


    def test_crear_genesis_bloc(self):
        resultat = False
        if self.my_db.ultim_bloc() is None:
            genesis = BlockchainUniversity(self.my_db)
            resultat = genesis.crear_genesis_bloc()
        return resultat

    def test_comprovar_cadena(self):
        main = BlockchainUniversity(self.my_db)
        self.assertEqual(main.comprovar_cadena_propia(), True)

    def test_to_minat(self):
        if self.my_db.existeix_alguna_transaccio():
            transaccio = Factoria.build_transaccio_from_db(self.my_db)
            if transaccio:
                if self.my_db.existeix_bloc_genesis():
                    ultim_bloc = Factoria.build_ultim_bloc_from_db(self.my_db)
                    if ultim_bloc:
                        index = ultim_bloc.id + 1
                        new_bloc = Bloc(index, transaccio, self.my_db,
                                        Encriptador.calcular_hash(ultim_bloc))
                        hash_bloc = hashlib.sha256(str.encode(Factoria.to_json(new_bloc))).hexdigest()
                        print("************1**************")
                        print(hash_bloc)
                        resultat = Paquet.confirmar_enviament(new_bloc, self.my_db)
                        if resultat:
                            self.my_db.guardar_bloc(new_bloc, transaccio.emissor)
                            self.my_db.esborrar_transaccio(transaccio.id_transaccio)
                            bloc_seguretat = Factoria.build_bloc_from_db(self.my_db, new_bloc.id)
                            hash_bloc_seguretat = hashlib.sha256(str.encode(Factoria.to_json(new_bloc))).hexdigest()
                            print(hash_bloc_seguretat)
                            print("************2**************")

                else:
                    self.crear_genesis_bloc()


    def test_Cadena_blocs(self):
        cadena = Factoria.build_cadena_blocs(self.my_db)
        retorn = False
        if cadena:
            retorn =BlockchainUniversity.comprovar_cadena(cadena)
        self.assertTrue(retorn)


class TestInicial(unittest.TestCase):

    def test_inicial(self):
        self.my_db = MySqlBloc('localhost', 'root', 'root')
        self.schema = SCHEMA
        self.test = CreacioTaulaTest(self.my_db, self.schema)
        self.test.crear_schema_inicial()

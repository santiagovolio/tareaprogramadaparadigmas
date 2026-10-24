"""
Casos de prueba minimos
"""

import unittest

from lexico import analizar_lexico, mensaje_error_lexico, ERROR
from main import procesar, ACEPTADA, RECHAZADA, ERROR_LEXICO

CASOS = [
    ("yo veo un gato grande.", ACEPTADA, None),
    ("la rata busca algo.", ACEPTADA, None),
    ("el perro persigue la rata veloz.", ACEPTADA, None),
    ("una mesa quiere el raton.", ACEPTADA, None),
    ("yo ve el gato.", RECHAZADA, "se esperaba VERBO1"),
    ("un rata busca algo.", RECHAZADA, "se esperaba SUST_M"),
    ("el gato ve.", RECHAZADA, "se esperaba INDEF, ART_M o ART_F"),
    ("el gato ve algo", RECHAZADA, "se esperaba PUNTO"),
    ("el gato ve algo. yo veo algo.", RECHAZADA, "se esperaba EOF"),
    ("el Gato ve algo.", ERROR_LEXICO, "Error lexico en 1:4"),
    ("el gato, ve algo.", ERROR_LEXICO, "caracter no reconocido ','"),
    ("", RECHAZADA, "se esperaba PRONOMBRE, ART_M o ART_F"),
]


class TestCasosMinimos(unittest.TestCase):
    def test_casos_enunciado(self):
        for n, (entrada, esperado, fragmento) in enumerate(CASOS, start=1):
            with self.subTest(caso=n, entrada=entrada):
                resultado, mensajes = procesar(entrada, mostrar=False)
                self.assertEqual(resultado, esperado)
                if fragmento is not None:
                    self.assertIn(fragmento, " ".join(mensajes))


class TestLexico(unittest.TestCase):
    def test_salida_sugerida(self):
        tokens, errores = analizar_lexico("yo veo un gato grande.")
        self.assertEqual(errores, [])
        self.assertEqual([str(t) for t in tokens], [
            "(yo, PRONOMBRE, 1:1)",
            "(veo, VERBO1, 1:4)",
            "(un, ART_M, 1:8)",
            "(gato, SUST_M, 1:11)",
            "(grande, ADJ, 1:16)",
            "(., PUNTO, 1:22)",
            "(EOF, EOF, 1:23)",
        ])

    def test_linea_y_columna_multilinea(self):
        tokens, _ = analizar_lexico("la rata\n\tbusca algo.")
        pos = [(t.lexema, t.linea, t.columna) for t in tokens]
        self.assertEqual(pos, [("la", 1, 1), ("rata", 1, 4), ("busca", 2, 2),
                               ("algo", 2, 8), (".", 2, 12), ("", 2, 13)])

    def test_palabra_no_reservada(self):
        tokens, errores = analizar_lexico("gatito")
        self.assertEqual(tokens[0].categoria, ERROR)
        self.assertEqual(errores[0].lexema, "gatito")

    def test_tilde(self):
        _, errores = analizar_lexico("el ratón ve algo.")
        self.assertEqual([(e.lexema, e.columna) for e in errores],
                         [("rat", 4), ("ó", 7), ("n", 8)])

    def test_reporta_todos_los_errores(self):
        _, errores = analizar_lexico("el Gato, ve algo!")
        self.assertEqual([(e.lexema, e.columna) for e in errores],
                         [("G", 4), ("ato", 5), (",", 8), ("!", 17)])

    def test_mensajes_error_lexico(self):
        _, errores = analizar_lexico("Gato gatito")
        self.assertEqual([mensaje_error_lexico(e) for e in errores], [
            "Error lexico en 1:1: caracter no reconocido 'G' (mayuscula).",
            "Error lexico en 1:2: palabra no reconocida 'ato'.",
            "Error lexico en 1:6: palabra no reconocida 'gatito'.",
        ])


class TestSintactico(unittest.TestCase):
    def test_mensaje_formato_enunciado(self):
        _, mensajes = procesar("yo un gato.", mostrar=False)
        self.assertEqual(mensajes[0],
                         "Error sintactico en 1:4: se esperaba VERBO1 pero se encontro ART_M ('un').")


if __name__ == "__main__":
    unittest.main(verbosity=2)

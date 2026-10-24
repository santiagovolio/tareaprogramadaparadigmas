from lexico import (PRONOMBRE, ART_M, ART_F, SUST_M, SUST_F, ADJ,
                    VERBO1, VERBO3, INDEF, PUNTO, EOF)

EPSILON = "ε"  # simbolo de la produccion vacia en la traza
ANCHO_ETIQUETA = 10


class ErrorSintactico(Exception):
    """Error en el formato: Error sintactico en L:C: se esperaba X pero se encontro Y ('lex')."""

    def __init__(self, esperadas, token):
        self.esperadas = esperadas
        self.token = token
        super().__init__(self.mensaje())

    def mensaje(self):
        t = self.token
        if t.categoria == EOF:
            encontrado = "EOF (fin de entrada)"
        else:
            encontrado = t.categoria + " ('" + t.lexema + "')"
        return "Error sintactico en " + str(t.linea) + ":" + str(t.columna) + \
            ": se esperaba " + formatear_esperadas(self.esperadas) + \
            " pero se encontro " + encontrado + "."


def formatear_esperadas(esperadas):
    """['INDEF','ART_M','ART_F'] -> 'INDEF, ART_M o ART_F'."""
    if len(esperadas) == 1:
        return esperadas[0]
    return ", ".join(esperadas[:-1]) + " o " + esperadas[-1]


class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = tokens  # lista de tokens; nunca el texto original
        self.pos = 0          # posicion actual
        self.nivel = 0        # profundidad para la traza
        self.traza = []       # lineas de la salida (arbol de derivacion)

    def token_actual(self):
        return self.tokens[self.pos]

    def lookahead(self):
        return self.tokens[self.pos].categoria

    def consumir(self, esperada):
        """match: consume el token esperado o reporta error."""
        if self.lookahead() == esperada:
            tok = self.tokens[self.pos]
            if esperada != EOF:
                self.pos += 1
            return tok
        self.error_sintactico([esperada])

    def error_sintactico(self, esperadas):
        raise ErrorSintactico(esperadas, self.token_actual())

    def _nodo(self, etiqueta):
        self.traza.append("  " * self.nivel + etiqueta)

    def _hoja(self, etiqueta, valor):
        self.traza.append("  " * self.nivel + etiqueta.ljust(ANCHO_ETIQUETA) + " -> " + valor)

    # -- punto de entrada -----------------------------------------------------
    def analizar(self):
        self.oracion()
        return self.traza

    def oracion(self):

        self._nodo("oracion")
        self.nivel += 1
        if self.lookahead() == PRONOMBRE:
            self._hoja("pronombre", self.consumir(PRONOMBRE).lexema)
            self.verbo1()
            self.objeto()
            self._hoja("punto", self.consumir(PUNTO).lexema)
        elif self.lookahead() in (ART_M, ART_F):
            self.sintagma()
            self.verbo3()
            self.objeto()
            self._hoja("punto", self.consumir(PUNTO).lexema)
        else:
            self.error_sintactico([PRONOMBRE, ART_M, ART_F])
        self.consumir(EOF)
        self.nivel -= 1

    def objeto(self):

        if self.lookahead() == INDEF:
            self._hoja("objeto", self.consumir(INDEF).lexema)
        elif self.lookahead() in (ART_M, ART_F):
            self._nodo("objeto")
            self.nivel += 1
            self.sintagma()
            self.nivel -= 1
        else:
            self.error_sintactico([INDEF, ART_M, ART_F])

    def sintagma(self):

        self._nodo("sintagma")
        self.nivel += 1
        if self.lookahead() == ART_M:
            self.art_m()
            self.sust_m()
            self.adj_op()
        elif self.lookahead() == ART_F:
            self.art_f()
            self.sust_f()
            self.adj_op()
        else:
            self.error_sintactico([ART_M, ART_F])
        self.nivel -= 1

    def art_m(self):

        self._hoja("art_m", self.consumir(ART_M).lexema)

    def art_f(self):

        self._hoja("art_f", self.consumir(ART_F).lexema)

    def sust_m(self):

        self._hoja("sust_m", self.consumir(SUST_M).lexema)

    def sust_f(self):

        self._hoja("sust_f", self.consumir(SUST_F).lexema)

    def adj_op(self):

        if self.lookahead() == ADJ:
            self._hoja("adj_op", self.consumir(ADJ).lexema)
        else:
            self._hoja("adj_op", EPSILON)  

    def verbo1(self):

        self._hoja("verbo1", self.consumir(VERBO1).lexema)

    def verbo3(self):
        self._hoja("verbo3", self.consumir(VERBO3).lexema)


def analizar_sintactico(tokens):
    """
    Devuelve (aceptada, traza, mensaje_error).
    traza contiene la derivacion completa o parcial (hasta el error).
    """
    parser = AnalizadorSintactico(tokens)
    try:
        parser.analizar()
        return True, parser.traza, None
    except ErrorSintactico as e:
        return False, parser.traza, e.mensaje()

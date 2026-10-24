
# Modulo del
# Analizador lexico.
# Lee el texto fuente UN caracter a la vez, con un indice 

PRONOMBRE = "PRONOMBRE"
ART_M = "ART_M"
ART_F = "ART_F"
SUST_M = "SUST_M"
SUST_F = "SUST_F"
ADJ = "ADJ"
VERBO1 = "VERBO1"
VERBO3 = "VERBO3"
INDEF = "INDEF"
PUNTO = "PUNTO"
EOF = "EOF"
ERROR = "ERROR"


# Tabla de palabras reservadas: lexema -> categoria

PALABRAS_RESERVADAS = {
    "yo": PRONOMBRE,
    "el": ART_M, "un": ART_M,
    "la": ART_F, "una": ART_F,
    "gato": SUST_M, "perro": SUST_M, "raton": SUST_M,
    "rata": SUST_F, "mesa": SUST_F, "alfombra": SUST_F,
    "grande": ADJ, "feliz": ADJ, "veloz": ADJ,
    "veo": VERBO1, "quiero": VERBO1, "busco": VERBO1,
    "ve": VERBO3, "quiere": VERBO3, "busca": VERBO3, "persigue": VERBO3,
    "algo": INDEF,
}

# Blancos: separan tokens y se descartan.
ESPACIO = " "
TABULADOR = "\t"
SALTO_LINEA = "\n"


class Token:
    """Token producido por el analizador lexico."""

    def __init__(self, lexema, categoria, linea, columna):
        self.lexema = lexema
        self.categoria = categoria
        self.linea = linea
        self.columna = columna

    def lexema_visible(self):
        """Representacion del lexema para la salida (EOF no tiene lexema)."""
        if self.categoria == EOF:
            return "EOF"
        return self.lexema

    def __str__(self):
        # Formato sugerido: (yo, PRONOMBRE, 1:1)
        return "(" + self.lexema_visible() + ", " + self.categoria + ", " + \
            str(self.linea) + ":" + str(self.columna) + ")"

    __repr__ = __str__


def es_letra_minuscula(c):
    """Alfabeto valido de palabras: letras minusculas a-z."""
    return "a" <= c <= "z"


def es_letra_mayuscula(c):
    return "A" <= c <= "Z"


def es_no_ascii(c):
    """Letras con tilde, n con virgulilla, dieresis, etc. (fuera de ASCII)."""
    return ord(c) > 127


def clasificar(lexema):
    """
    Busca el lexema en la tabla de palabras reservadas.
    Si no esta, el token es ERROR.
    """
    if lexema in PALABRAS_RESERVADAS:
        return PALABRAS_RESERVADAS[lexema]
    return ERROR


def motivo_caracter(c):
    """Detalle opcional para el mensaje de un caracter no reconocido."""
    if es_letra_mayuscula(c):
        return "mayuscula"
    if es_no_ascii(c):
        return "tilde/caracter no ASCII"
    return None



# Analizador lexico

class AnalizadorLexico:
    def __init__(self, texto):
        self.texto = texto
        self.i = 0          # indice (puntero) sobre el texto
        self.linea = 1
        self.col = 1
        self.tokens = []


    def peek(self):
        """Devuelve el caracter actual sin consumirlo (None al final)."""
        if self.i < len(self.texto):
            return self.texto[self.i]
        return None

    def avanzar(self):
        """Consume un caracter (que no es salto de linea) y avanza la columna."""
        c = self.texto[self.i]
        self.i += 1
        self.col += 1
        return c
    
    def analizar(self):
        while self.peek() is not None:
            c = self.peek()

            if c == ESPACIO or c == TABULADOR:
                self.avanzar()

            elif c == SALTO_LINEA:
                self.linea += 1
                self.col = 1
                self.i += 1

            elif es_letra_minuscula(c):
                self.leer_palabra()

            elif c == ".":
                self.tokens.append(Token(".", PUNTO, self.linea, self.col))
                self.avanzar()

            else:
                self.tokens.append(Token(c, ERROR, self.linea, self.col))
                self.avanzar()

        self.tokens.append(Token("", EOF, self.linea, self.col))
        return self.tokens

    def leer_palabra(self):
        """3) acumular el lexema (secuencia maximal de letras a-z) y 4) clasificarlo."""
        col_ini = self.col
        lexema = ""
        while self.peek() is not None and es_letra_minuscula(self.peek()):
            lexema += self.avanzar()
        self.tokens.append(Token(lexema, clasificar(lexema), self.linea, col_ini))



# Interfaz del modulo
def analizar_lexico(texto):
    """Devuelve (tokens, errores). errores = lista de tokens ERROR."""
    tokens = AnalizadorLexico(texto).analizar()
    errores = [t for t in tokens if t.categoria == ERROR]
    return tokens, errores


def mensaje_error_lexico(token):
    """Error lexico en 1:4: caracter no reconocido 'G' (mayuscula)."""
    if es_letra_minuscula(token.lexema[0]):
        detalle = "palabra no reconocida '" + token.lexema + "'"
    else:
        detalle = "caracter no reconocido '" + token.lexema + "'"
        motivo = motivo_caracter(token.lexema)
        if motivo is not None:
            detalle += " (" + motivo + ")"
    return "Error lexico en " + str(token.linea) + ":" + str(token.columna) + \
        ": " + detalle + "."

# Tarea Programada 1 - Analizador Lexico y Sintactico

ULEAD - Paradigmas de Programacion - IIIC 2026

Implementacion en Python de un analizador lexico (Etapa 1) y un analizador sintactico de descenso recursivo predictivo (Etapa 2) para el lenguaje definido en el enunciado.

## Estructura del proyecto

```
tarea1_analizador/
├── README.md
├── lexico.py
├── sintactico.py
├── main.py
└── pruebas.py
```

| Archivo | Contenido |
|---|---|
| `lexico.py` | Modulo del analizador lexico (Etapa 1). Categorias, tabla de palabras reservadas, clase `Token`, clase `AnalizadorLexico`. |
| `sintactico.py` | Modulo del analizador sintactico (Etapa 2). Clase `AnalizadorSintactico` con una funcion por no terminal. |
| `main.py` | Programa principal: ejecuta la Etapa 1 y, si no hay errores lexicos, la Etapa 2. |
| `pruebas.py` | Los 12 casos de prueba minimos del enunciado y pruebas unitarias adicionales. |
| `README.md` | Este archivo. |

Los analizadores lexico y sintactico estan en modulos separados (`lexico.py` y `sintactico.py`).

## Requisitos

- Python 3.8 o superior.
- No requiere librerias externas (solo la biblioteca estandar: `argparse`, `sys`, `unittest`).

## Instrucciones de ejecucion

Desde la carpeta del proyecto (`tarea1_analizador/`):

```bash
# 1. Analizar una oracion pasada como argumento (entre comillas)
python main.py "yo veo un gato grande."

# 2. Analizar el contenido de un archivo de texto (UTF-8)
python main.py -f entrada.txt

# 3. Modo interactivo (pide la oracion por teclado)
python main.py

# 4. Entrada vacia
python main.py ""

# 5. Ejecutar los 12 casos de prueba minimos del enunciado
python main.py --pruebas

# 6. Ejecutar las pruebas unitarias
python -m unittest pruebas -v
```

En Linux/macOS puede ser necesario usar `python3` en lugar de `python`.

Codigo de salida del programa: `0` = ACEPTADA, `1` = RECHAZADA, `2` = ERROR LEXICO.

## Gramatica implementada

```
<oracion>  -> yo <verbo1> <objeto> .
            | <sintagma> <verbo3> <objeto> .
<objeto>   -> algo | <sintagma>
<sintagma> -> <art_m> <sust_m> <adj_op>
            | <art_f> <sust_f> <adj_op>
<art_m>    -> el | un
<art_f>    -> la | una
<sust_m>   -> gato | perro | raton
<sust_f>   -> rata | mesa | alfombra
<adj_op>   -> grande | feliz | veloz | ε
<verbo1>   -> veo | quiero | busco
<verbo3>   -> ve | quiere | busca | persigue
```

## Categorias de tokens

| Categoria | Lexemas |
|---|---|
| PRONOMBRE | yo |
| ART_M | el, un |
| ART_F | la, una |
| SUST_M | gato, perro, raton |
| SUST_F | rata, mesa, alfombra |
| ADJ | grande, feliz, veloz |
| VERBO1 | veo, quiero, busco |
| VERBO3 | ve, quiere, busca, persigue |
| INDEF | algo |
| PUNTO | . |
| EOF | (fin de entrada, se agrega al final) |
| ERROR | cualquier caracter o palabra no reconocida |

## Etapa 1 - Analizador lexico (`lexico.py`)

- Lee el texto **un caracter a la vez** con un indice `i` sobre el texto y **1 caracter de lookahead** (`peek()`). `avanzar()` consume el caracter y avanza la columna; el salto de linea se trata aparte (linea++, columna = 1), igual que en el pseudocodigo del enunciado.
- Ciclo clasico en `analizar()`: saltar blancos -> decidir por el primer caracter -> acumular el lexema (`leer_palabra()`) -> clasificar el lexema (`clasificar()`).
- Blancos (espacio, tabulador, salto de linea) separan tokens y se descartan. El salto de linea incrementa la linea y reinicia la columna en 1.
- Una palabra es una secuencia maximal de letras, acumulada caracter por caracter. Al terminar se busca en la tabla `PALABRAS_RESERVADAS` para asignar la categoria.
- Alfabeto de palabras: solo letras minusculas `a`-`z`. Si la palabra no esta en la tabla (por ejemplo `gatito`) el token es `ERROR`.
- Las mayusculas y letras con tilde no pertenecen al alfabeto: cada una produce un token `ERROR` de un caracter (por ejemplo `Gato` -> `G` (ERROR, 1:4) y `ato` (ERROR, 1:5)). El mensaje indica el motivo (`mayuscula` o `tilde/caracter no ASCII`).
- `.` produce un token `PUNTO`.
- Cualquier otro caracter produce un token `ERROR` de un caracter y el analisis continua.
- Al final se agrega el token `EOF`.
- Si hay al menos un token `ERROR`, se informan todos (lexema, linea y columna) y **no se ejecuta la etapa 2**.
- No se usan expresiones regulares, `split()`, `strip()`, `tokenize()` ni generadores de analizadores.

Salida (formato sugerido en el enunciado):

```
(yo, PRONOMBRE, 1:1)
(veo, VERBO1, 1:4)
(un, ART_M, 1:8)
(gato, SUST_M, 1:11)
(grande, ADJ, 1:16)
(., PUNTO, 1:22)
(EOF, EOF, 1:23)
```

## Etapa 2 - Analizador sintactico (`sintactico.py`)

- Descenso recursivo **predictivo**: consume **unicamente la lista de tokens** (nunca el texto original).
- **Una funcion por cada no terminal**: `oracion`, `objeto`, `sintagma`, `art_m`, `art_f`, `sust_m`, `sust_f`, `adj_op`, `verbo1`, `verbo3`.
- Usa **un token de lookahead** (`lookahead()`) y la funcion `consumir(categoria)` (*match*), que consume el token esperado o reporta error.
- **Sin backtracking**: cada alternativa se elige solo mirando el lookahead (`PRONOMBRE` vs `ART_M`/`ART_F` en `oracion`; `INDEF` vs `ART_M`/`ART_F` en `objeto`; `ART_M` vs `ART_F` en `sintagma`; `ADJ` vs ε en `adj_op`).
- Al final de `oracion` se exige `EOF`.
- Se detiene en el primer error (no hay recuperacion).

Salida cuando la oracion es aceptada (`python main.py "la rata busca algo."`):

```
=== Etapa 2: Analisis sintactico ===
oracion
  sintagma
    art_f      -> la
    sust_f     -> rata
    adj_op     -> ε
  verbo3     -> busca
  objeto     -> algo
  punto      -> .

Resultado: ACEPTADA
```

Salida cuando hay error sintactico (`python main.py "el gato ve."`):

```
=== Etapa 2: Analisis sintactico ===
Traza (parcial, hasta el error):
oracion
  sintagma
    art_m      -> el
    sust_m     -> gato
    adj_op     -> ε
  verbo3     -> ve

Fallo: RECHAZADA
Error sintactico en 1:11: se esperaba INDEF, ART_M o ART_F pero se encontro PUNTO ('.').
```

Salida cuando hay error lexico (`python main.py "el Gato, ve algo."`):

```
Se encontraron 3 error(es) lexico(s):
Error lexico en 1:4: caracter no reconocido 'G' (mayuscula).
Error lexico en 1:5: palabra no reconocida 'ato'.
Error lexico en 1:8: caracter no reconocido ','.
No se ejecuta la etapa 2.

Resultado: ERROR LEXICO
```

## Casos de prueba minimos

Resultado de `python main.py --pruebas`:

| # | Entrada | Resultado esperado | Mensaje obtenido |
|---|---|---|---|
| 1 | `yo veo un gato grande.` | ACEPTADA | - |
| 2 | `la rata busca algo.` | ACEPTADA | - |
| 3 | `el perro persigue la rata veloz.` | ACEPTADA | - |
| 4 | `una mesa quiere el raton.` | ACEPTADA | - |
| 5 | `yo ve el gato.` | RECHAZADA (se esperaba VERBO1) | Error sintactico en 1:4: se esperaba VERBO1 pero se encontro VERBO3 ('ve'). |
| 6 | `un rata busca algo.` | RECHAZADA (se esperaba SUST_M) | Error sintactico en 1:4: se esperaba SUST_M pero se encontro SUST_F ('rata'). |
| 7 | `el gato ve.` | RECHAZADA (se esperaba INDEF, ART_M o ART_F) | Error sintactico en 1:11: se esperaba INDEF, ART_M o ART_F pero se encontro PUNTO ('.'). |
| 8 | `el gato ve algo` | RECHAZADA (falta PUNTO) | Error sintactico en 1:16: se esperaba PUNTO pero se encontro EOF (fin de entrada). |
| 9 | `el gato ve algo. yo veo algo.` | RECHAZADA (sobra texto, se esperaba EOF) | Error sintactico en 1:18: se esperaba EOF pero se encontro PRONOMBRE ('yo'). |
| 10 | `el Gato ve algo.` | Error lexico en 1:4 (mayuscula), no se ejecuta la etapa 2 | Error lexico en 1:4: caracter no reconocido 'G' (mayuscula). |
| 11 | `el gato, ve algo.` | Error lexico: caracter , | Error lexico en 1:8: caracter no reconocido ','. |
| 12 | (entrada vacia) | RECHAZADA (se esperaba PRONOMBRE, ART_M o ART_F) | Error sintactico en 1:1: se esperaba PRONOMBRE, ART_M o ART_F pero se encontro EOF (fin de entrada). |

Los 12 casos producen el resultado esperado (12/12).

"""
Programa principal: ejecuta la Etapa 1 (lexico) y, si no hay errores lexicos,
la Etapa 2 (sintactico).

Uso:
    python main.py "yo veo un gato grande."     # oracion como argumento
    python main.py -f entrada.txt                # oracion desde archivo
    python main.py                               # modo interactivo
    python main.py --pruebas                     # corre los 12 casos minimos
"""

import argparse
import sys

from lexico import analizar_lexico, mensaje_error_lexico
from sintactico import analizar_sintactico

ACEPTADA = "ACEPTADA"
RECHAZADA = "RECHAZADA"
ERROR_LEXICO = "ERROR LEXICO"


def procesar(texto, mostrar=True):
    """
    Ejecuta ambas etapas sobre el texto.
    Devuelve (resultado, mensajes) donde resultado es ACEPTADA, RECHAZADA o
    ERROR LEXICO y mensajes es la lista de mensajes de error.
    """
    salida = []

    # ---------------- Etapa 1 ----------------
    tokens, errores = analizar_lexico(texto)
    salida.append("=== Etapa 1: Analisis lexico ===")
    for t in tokens:
        salida.append(str(t))

    if errores:
        mensajes = [mensaje_error_lexico(t) for t in errores]
        salida.append("")
        salida.append("Se encontraron " + str(len(errores)) + " error(es) lexico(s):")
        salida.extend(mensajes)
        salida.append("No se ejecuta la etapa 2.")
        salida.append("")
        salida.append("Resultado: " + ERROR_LEXICO)
        if mostrar:
            print("\n".join(salida))
        return ERROR_LEXICO, mensajes

    # ---------------- Etapa 2 ----------------
    aceptada, traza, error = analizar_sintactico(tokens)
    salida.append("")
    salida.append("=== Etapa 2: Analisis sintactico ===")
    if aceptada:
        salida.extend(traza)
        salida.append("")
        salida.append("Resultado: " + ACEPTADA)
        resultado, mensajes = ACEPTADA, []
    else:
        if traza:
            salida.append("Traza (parcial, hasta el error):")
            salida.extend(traza)
            salida.append("")
        salida.append("Fallo: " + RECHAZADA)
        salida.append(error)
        resultado, mensajes = RECHAZADA, [error]

    if mostrar:
        print("\n".join(salida))
    return resultado, mensajes


def correr_pruebas():
    from pruebas import CASOS
    total_ok = 0
    for n, (entrada, esperado, fragmento) in enumerate(CASOS, start=1):
        resultado, mensajes = procesar(entrada, mostrar=False)
        detalle = mensajes[0] if mensajes else ""
        ok = resultado == esperado and (fragmento is None or fragmento in " ".join(mensajes))
        total_ok += ok
        visible = entrada if entrada != "" else "(entrada vacia)"
        print(str(n).rjust(2) + ". [" + ("OK" if ok else "FALLO") + "] " +
              repr(visible) + " -> " + resultado)
        if detalle:
            print("      " + detalle)
    print("")
    print(str(total_ok) + "/" + str(len(CASOS)) + " casos con el resultado esperado.")
    return 0 if total_ok == len(CASOS) else 1


def main():
    # Asegura que el simbolo epsilon se imprima bien en consolas Windows.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    ap =argparse.ArgumentParser(description="Analizador lexico y sintactico - Tarea Programada 1")
    ap.add_argument("oracion", nargs="?", help="oracion a analizar (entre comillas)")
    ap.add_argument("-f", "--archivo", help="leer la oracion desde un archivo de texto")
    ap.add_argument("--pruebas", action="store_true", help="ejecutar los 12 casos de prueba minimos")
    args = ap.parse_args()

    if args.pruebas:
        return correr_pruebas()

    if args.archivo is not None:
        with open(args.archivo, encoding="utf-8") as fh:
            texto = fh.read()
    elif args.oracion is not None:
        texto = args.oracion
    else:
        texto = input("Ingrese la oracion: ")

    print("Entrada: " + repr(texto))
    print("")
    resultado, _ = procesar(texto)
    return {ACEPTADA: 0, RECHAZADA: 1, ERROR_LEXICO: 2}[resultado]


if __name__ == "__main__":
    sys.exit(main())

import sys

NEIGHBORS = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]


def main():
    if len(sys.argv) != 3:
        sys.stderr.write(
            "Uso: python3 vida.py <archivo_estado_inicial> <generaciones>\n"
        )
        return 1

    try:
        generaciones = int(sys.argv[2])
    except ValueError:
        sys.stderr.write("Error: las generaciones deben ser un entero.\n")
        return 1

    if generaciones < 0:
        sys.stderr.write("Error: las generaciones no pueden ser negativas.\n")
        return 1

    try:
        with open(sys.argv[1], "r") as f:
            lineas = [line.strip("\r\n") for line in f]
    except OSError as e:
        sys.stderr.write("Error: no se pudo leer el archivo: {}\n".format(e))
        return 1

    if not lineas:
        return 0

    alto = len(lineas)
    ancho = len(lineas[0])

    if any(len(linea) != ancho for linea in lineas):
        sys.stderr.write("Error: la grilla debe ser rectangular.\n")
        return 1

    grilla = [list(linea) for linea in lineas]

    for _ in range(generaciones):
        nueva_grilla = [["."] * ancho for _ in range(alto)]

        for r in range(alto):
            for c in range(ancho):
                vecinas = 0

                for dr, dc in NEIGHBORS:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < alto and 0 <= nc < ancho and grilla[nr][nc] == "#":
                        vecinas += 1

                if grilla[r][c] == "#":
                    nueva_grilla[r][c] = "#" if vecinas in (2, 3) else "."
                else:
                    nueva_grilla[r][c] = "#" if vecinas == 3 else "."

        grilla = nueva_grilla

    sys.stdout.write("\n".join("".join(fila) for fila in grilla) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

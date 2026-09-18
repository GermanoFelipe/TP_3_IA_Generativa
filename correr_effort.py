"""Compara el efecto de `reasoning_effort` en el slot 1 (Ejercicio 1, criterio 1.5).

Manda **el mismo prompt** al slot 1 con effort `low` y con effort `high` y deja
un log `.md` por corrida, para poder comparar los `reasoning_tokens` de cada
nivel.

Por que hace falta: la primera medicion se hizo con el prompt "explicame en 2
lineas que es la recursividad", que no obliga al modelo a razonar nada, y las
dos corridas dieron `reasoning=0`. Con un prompt que si requiere varios pasos
encadenados, si el modelo devuelve tokens de razonamiento la diferencia entre
niveles tiene que verse.

Reusa `test_slot` de `smoke_test.py` sin modificarlo, de modo que el log que
produce es identico al de las demas corridas del Ejercicio 1.

Uso: python correr_effort.py
"""

import os

from dotenv import load_dotenv

load_dotenv()

from smoke_test import test_slot  # noqa: E402
from usage import format_usage  # noqa: E402

# Un problema de varios pasos encadenados: hay que aplicar inclusion-exclusion
# sobre cuatro conjuntos, o contar a mano. No se resuelve recuperando un dato.
PROMPT = (
    "Cuantos enteros entre 1 y 10000 inclusive no son divisibles ni por 2, "
    "ni por 3, ni por 5, ni por 7? Resolvelo sin escribir ni ejecutar codigo. "
    "Mostra el planteo y termina con el numero final."
)


def main():
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Falta OPENROUTER_API_KEY. Copia .env.example a .env y cargala.")
        return 1

    resultados = {}
    for nivel in ("low", "high"):
        print(f"\n===== slot 1 con reasoning_effort = {nivel} =====")
        _, usages = test_slot(
            "1", [PROMPT], reasoning={"effort": nivel}, suffix=f"-effort-{nivel}"
        )
        resultados[nivel] = usages[0]

    print("\n===== COMPARACION =====")
    for nivel, u in resultados.items():
        print(f"  {nivel:5} -> {format_usage(u)}")

    r_low = (resultados["low"].get("completion_tokens_details") or {}).get(
        "reasoning_tokens", 0
    ) or 0
    r_high = (resultados["high"].get("completion_tokens_details") or {}).get(
        "reasoning_tokens", 0
    ) or 0
    print(f"\n  reasoning low={r_low}  high={r_high}")
    if r_low == 0 and r_high == 0:
        print("  HALLAZGO: el modelo no devuelve reasoning_tokens en ningun nivel.")
    else:
        print(f"  El effort alto uso {r_high - r_low:+d} tokens de razonamiento.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

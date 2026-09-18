"""Corrida no interactiva del Ejercicio 2 contra el slot 4 (DeepSeek).

Reusa exactamente el mismo camino de codigo que `chat.py` (build_messages ->
send_chat -> logger) sin modificarlo: el log `.md` que produce es identico al
que genera el chat interactivo.

Motivo de existir: la consola de Windows no permite pegar de forma fiable un
prompt de ~7000 caracteres en una sola linea (se cuelga o duplica la entrada),
y el prompt del Ejercicio 2 necesita ese tamaño para superar el umbral de
~1024 tokens que pide el cache por prefijo de DeepSeek. Mandarlo desde un
archivo garantiza que las distintas corridas usen un prefijo byte a byte
identico, que es la condicion para que haya cache hit.

Cada invocacion abre una conversacion nueva (log nuevo, historial vacio),
igual que `/switch` en `chat.py`.

Uso: python correr_vida.py [ruta_al_prompt]
"""

import os
import sys

from dotenv import load_dotenv

from chat import build_messages, render_content
from logger import append_turn, init_log, new_log_path
from models import get_slot
from openrouter_client import OpenRouterError, send_chat
from usage import format_usage

load_dotenv()

PROMPT_POR_DEFECTO = os.path.join("prompts", "prompt_vida_v2.txt")


def main():
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Falta OPENROUTER_API_KEY. Copia .env.example a .env y cargala.")
        return 1

    ruta = sys.argv[1] if len(sys.argv) > 1 else PROMPT_POR_DEFECTO
    with open(ruta, encoding="utf-8") as f:
        prompt = f.read().rstrip("\n")

    slot = get_slot("4")
    log_path = new_log_path(slot.key, slot.model_id)
    init_log(log_path, slot.key, slot.model_id)

    print(f"Log    : {log_path}")
    print(f"Prompt : {len(prompt)} caracteres desde {ruta}")
    print(f"Modelo : {slot.model_id}")
    print("Enviando (la respuesta no es streaming, puede tardar)...")

    append_turn(log_path, "user", prompt)
    messages = build_messages(slot, [], prompt)

    try:
        content, usage = send_chat(slot.model_id, messages)
    except OpenRouterError as e:
        print(f"Error: {e}")
        return 1

    rendered = render_content(content, None)
    print(f"\n{slot.label}>\n{rendered}\n")
    print(format_usage(usage))
    append_turn(log_path, "assistant", rendered, usage=usage)
    return 0


if __name__ == "__main__":
    sys.exit(main())

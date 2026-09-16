"""Corridas de prueba no interactivas contra los 4 slots, una por modelo
(mas una extra de slot 1 con effort distinto). Generan los logs .md que
prueban que cada modelo es usable desde la interfaz. Reusa el mismo camino
de codigo que chat.py (build_messages, send_chat, logger)."""

import os

from chat import STRUCTURED_SCHEMA, build_messages, render_content
from dotenv import load_dotenv
from logger import append_turn, init_log, new_log_path
from models import get_slot
from openrouter_client import send_chat
from usage import format_usage

load_dotenv()


def run_turn(slot, log_path, history, user_text, reasoning=None, response_format=None):
    append_turn(log_path, "user", user_text)
    messages = build_messages(slot, history, user_text)
    content, usage = send_chat(
        slot.model_id, messages, reasoning=reasoning, response_format=response_format
    )
    rendered = render_content(content, response_format)
    print(f"[{slot.label}] {rendered[:200]}")
    print(format_usage(usage))
    append_turn(log_path, "assistant", rendered, usage=usage)
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": content})
    return usage


def test_slot(key, questions, reasoning=None, suffix=""):
    slot = get_slot(key)
    log_path = new_log_path(slot.key + suffix, slot.model_id)
    init_log(log_path, slot.key, slot.model_id)
    print(f"\n=== slot {slot.key}{suffix} -> {log_path} ===")
    response_format = STRUCTURED_SCHEMA if slot.supports_structured_output else None
    history = []
    usages = []
    for q in questions:
        usages.append(
            run_turn(slot, log_path, history, q, reasoning=reasoning, response_format=response_format)
        )
    return log_path, usages


if __name__ == "__main__":
    assert os.environ.get("OPENROUTER_API_KEY"), "Falta OPENROUTER_API_KEY"

    # Slot 1: mismo prompt con dos efforts distintos, para comparar.
    test_slot("1", ["Explicame en 2 lineas que es la recursividad."], reasoning={"effort": "low"}, suffix="-low")
    test_slot("1", ["Explicame en 2 lineas que es la recursividad."], reasoning={"effort": "high"}, suffix="-high")

    # Slot 2: dos turnos con el mismo contexto estatico -> el 2do deberia
    # mostrar cached_tokens > 0.
    _, usages2 = test_slot(
        "2",
        [
            "Segun el manual, que se hace primero cuando falla un sistema en produccion?",
            "Y que politica hay sobre secretos en el repositorio?",
        ],
    )
    print("cache_discount / cached_tokens turno 2:", usages2[1].get("prompt_tokens_details"))

    # Slot 3: salida estructurada.
    test_slot("3", ["Dame 3 tips para escribir mejores tests unitarios."])

    # Slot 4: el barato.
    test_slot("4", ["En una linea, que es OpenRouter?"])

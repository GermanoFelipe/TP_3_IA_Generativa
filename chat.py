"""Interfaz de chat en terminal para los 4 modelos del Ejercicio 1.

Uso: python chat.py
Comandos dentro de una conversacion: /switch (cambia de modelo, arranca
conversacion nueva), /exit (termina el programa).
"""

import json
import os
import sys

from dotenv import load_dotenv

from logger import append_turn, init_log, new_log_path
from models import SLOTS, get_slot
from openrouter_client import OpenRouterError, send_chat
from static_context import SUPPORT_CONTEXT
from usage import format_usage

load_dotenv()

STRUCTURED_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "respuesta_estructurada",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "respuesta": {"type": "string"},
                "puntos_clave": {"type": "array", "items": {"type": "string"}},
                "confianza": {"type": "string", "enum": ["baja", "media", "alta"]},
            },
            "required": ["respuesta", "puntos_clave", "confianza"],
            "additionalProperties": False,
        },
    },
}

EFFORT_LEVELS = ["low", "medium", "high"]


def choose_slot():
    print("\nModelos disponibles:")
    for slot in SLOTS:
        print(f"  {slot.key}. {slot.label} - {slot.capability}")
    while True:
        choice = input("Elegi un slot (1-4, o /exit): ").strip()
        if choice == "/exit":
            return None
        try:
            return get_slot(choice)
        except KeyError:
            print("Opcion invalida.")


def choose_effort():
    print(f"Niveles de reasoning_effort: {', '.join(EFFORT_LEVELS)}")
    choice = input("Effort (enter = medium): ").strip().lower()
    return choice if choice in EFFORT_LEVELS else "medium"


def build_messages(slot, history, user_text):
    messages = []
    if slot.supports_cache:
        messages.append(
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": SUPPORT_CONTEXT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
            }
        )
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})
    return messages


def render_content(content, response_format):
    if not response_format:
        return content
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return content
    return json.dumps(parsed, indent=2, ensure_ascii=False)


def run_conversation(slot):
    """Corre una conversacion interactiva para un slot. Devuelve 'switch' o 'exit'."""
    reasoning = {"effort": choose_effort()} if slot.supports_effort else None
    response_format = STRUCTURED_SCHEMA if slot.supports_structured_output else None

    log_path = new_log_path(slot.key, slot.model_id)
    init_log(log_path, slot.key, slot.model_id)
    print(f"\nLog: {log_path}")
    print("Escribi tu mensaje ('/switch' cambia de modelo, '/exit' termina).\n")

    history = []
    while True:
        user_text = input("vos> ").strip()
        if not user_text:
            continue
        if user_text == "/exit":
            return "exit"
        if user_text == "/switch":
            return "switch"

        append_turn(log_path, "user", user_text)
        messages = build_messages(slot, history, user_text)

        try:
            content, usage = send_chat(
                slot.model_id,
                messages,
                reasoning=reasoning,
                response_format=response_format,
            )
        except OpenRouterError as e:
            print(f"Error: {e}\n")
            continue

        rendered = render_content(content, response_format)
        print(f"\n{slot.label}> {rendered}\n")
        print(format_usage(usage))
        append_turn(log_path, "assistant", rendered, usage=usage)

        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": content})


def main():
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Falta OPENROUTER_API_KEY. Copia .env.example a .env y cargala.")
        sys.exit(1)

    while True:
        slot = choose_slot()
        if slot is None:
            break
        result = run_conversation(slot)
        if result == "exit":
            break


if __name__ == "__main__":
    main()

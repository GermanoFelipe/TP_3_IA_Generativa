# SPEC — Ejercicio 1: interfaz de chat con 4 modelos via OpenRouter

Mision de referencia: `missions/prompting/mission.md` del repo
`austral-ing-ai/talksmith-ing`. Este documento cubre solo el **Ejercicio 1**
("una interfaz de chat, cuatro modelos").

## Objetivo

Una interfaz de chat en terminal que sirve 4 modelos via OpenRouter, cada
uno ejercitando una capacidad distinta de la clase de prompting, mostrando
el `usage` de cada respuesta y dejando un log `.md` por conversacion.

## Los 4 slots

| Slot | Modelo | Capacidad | Como se implementa |
|---|---|---|---|
| 1 | `openai/gpt-5.6-luna` | Effort configurable | Se pregunta el nivel (`low`/`medium`/`high`) al elegir el slot y se manda en `reasoning: {effort}` |
| 2 | `anthropic/claude-haiku-4.5` | Prompt caching explicito | Cada request incluye un system prompt estatico (`static_context.py`, ~17.000 caracteres / ~4800 tokens) como bloque de contenido con `cache_control: {type: ephemeral}` |
| 3 | `google/gemini-3.7-flash` | Salidas estructuradas | Se manda `response_format: {type: json_schema, json_schema: {...}}` con un schema fijo (`respuesta`, `puntos_clave[]`, `confianza`) |
| 4 | `deepseek/deepseek-v4-flash-0731` | El escalon barato | Chat simple, sin parametros extra |

IDs verificados contra el catalogo de OpenRouter el 2026-09-16 (todos
respondieron correctamente en las corridas de prueba).

## Por que el contexto estatico del slot 2 es tan largo

Claude Haiku 4.5 no cachea prompts por debajo de **4096 tokens** (a
diferencia de Haiku 3.5, que cachea desde 2048). El primer intento con un
contexto de ~2000 tokens no genero ningun cache hit ni cache write. Se
amplio `static_context.py` a ~4800 tokens para cruzar ese umbral con margen;
el segundo turno de una conversacion muestra `cached_tokens > 0` y el costo
de entrada de ese turno cae a una fraccion del turno anterior. Fuente:
`https://openrouter.ai/docs/features/prompt-caching`.

## Arquitectura

- `models.py` — config de los 4 slots (`ModelSlot`: id, capacidades).
- `openrouter_client.py` — POST a `/api/v1/chat/completions`, devuelve
  `(contenido, usage)`. Unico modulo que hace red.
- `usage.py` — formatea el dict `usage` de OpenRouter a una linea legible y
  detecta cache hits. Sin dependencias externas, 100% testeable.
- `logger.py` — crea y escribe los logs `.md` (`logs/slotN_<modelo>_<ts>.md`).
- `static_context.py` — el system prompt estatico del slot 2.
- `chat.py` — CLI interactivo: elegir slot, chatear, `/switch` (nueva
  conversacion) y `/exit`.
- `smoke_test.py` — corridas no interactivas usadas para generar los logs
  de prueba de la entrega, reusando `build_messages`/`send_chat`/`logger`.

## Requisitos cubiertos

- Usage despues de cada respuesta: prompt, completion, reasoning, cached
  tokens y costo en USD (`usage.py::format_usage`).
- Cambiar de modelo (`/switch`) inicia conversacion nueva (nuevo log, nuevo
  `history`).
- Log `.md` por conversacion con rol, mensaje y usage por turno.
- Los 4 modelos son de 4 proveedores distintos (test `test_models.py`).

## Testing

`pytest` sobre `usage.py`, `logger.py` y `models.py` (sin red). Las llamadas
reales a la API se validaron con `smoke_test.py` contra la cuenta real de
OpenRouter (ver `logs/`), no con mocks, porque el objetivo del ejercicio es
justamente verificar el comportamiento real de reasoning/caching/structured
output de cada proveedor.

## Fuera de alcance de este documento

Ejercicio 2 (`vida.py`), Ejercicio 3 (informe de costos) y la entrega final
al repo del grupo.

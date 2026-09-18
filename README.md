# TP 3 — Mision "el prompt minimo"

IA Generativa TP3

Interfaz de chat en terminal que sirve 4 modelos via OpenRouter, y el uso de
esa interfaz para resolver el juego de la vida de Conway en **un solo prompt**,
midiendo tokens y gasto de cada intento.

Integrantes: Felipe Germano, Franco Pitter, Federico Hanashiro, Francisco
Zizzi.

## Setup

Requiere Python 3.10 o superior.

```bash
python -m pip install -r requirements.txt
cp .env.example .env    # completar OPENROUTER_API_KEY
```

## Correr

```bash
python chat.py            # chat interactivo, los 4 slots
python correr_vida.py     # Ejercicio 2: manda un prompt de prompts/ al slot 4
python correr_effort.py   # slot 1 con effort low y high, para comparar
```

En `chat.py`: `/switch` cambia de modelo e inicia conversacion nueva, `/exit`
termina. Cada conversacion deja un log `.md` en `logs/`.

## Testear

Son **dos suites distintas** y se invocan distinto:

```bash
python -m pytest        # 13 tests del proyecto (usage, logger, models)
python test_vida.py     # 9 tests de la catedra contra vida.py
```

`test_vida.py` no se corre con pytest: el archivo de la catedra hace
`sys.argv.pop(1)` durante el import, asi que si se lo invoca como
`python -m pytest test_vida.py` se auto-apunta a si mismo y los 9 casos
fallan. Por eso `pytest.ini` declara `testpaths = tests`: `python -m pytest`
a secas no lo recoge y no hay conflicto. Detalle en `SPEC.md`.

## Los 4 modelos

| Slot | Modelo | Capacidad que ejercita |
|---|---|---|
| 1 | `openai/gpt-5.6-luna` | Effort configurable (`reasoning_effort`) |
| 2 | `anthropic/claude-haiku-4.5` | Prompt caching explicito (`cache_control`) |
| 3 | `google/gemini-3.7-flash` | Salidas estructuradas (JSON Schema) |
| 4 | `deepseek/deepseek-v4-flash-0731` | El escalon barato |

## Donde esta cada entregable

| Lo que pide el enunciado | Donde |
|---|---|
| Codigo de la interfaz (Ejercicio 1) | `chat.py`, `models.py`, `openrouter_client.py`, `usage.py`, `logger.py`, `static_context.py` |
| Un log de prueba por cada uno de los 4 modelos | `logs/slot1-low_*`, `logs/slot2_*`, `logs/slot3_*`, `logs/slot4_*_20260916_*` |
| Logs del chat que genero Conway (ganadora + quemados) | Los 9 archivos `logs/slot4_*` del 17/09 y 18/09 |
| El script `vida.py` | `vida.py` |
| Tests de la catedra, en verde | `test_vida.py` (9/9) |
| Informe del Ejercicio 3 | `INFORME_EJERCICIO_3.md` |
| El prompt que genero el entregable | `prompts/prompt_vida_v1_ganador.txt` |

La conversacion ganadora es
`logs/slot4_deepseek_deepseek-v4-flash-0731_20260918_171450_906651.md`: **un
solo turno de usuario**, los 9 tests en verde, y el codigo de su bloque
coincide byte a byte con el `vida.py` entregado (2186 caracteres los dos).

El prompt que la produjo esta en `prompts/prompt_vida_v1_ganador.txt`.
`prompts/prompt_vida_v2.txt` es una version optimizada posterior que consigue
los mismos 9 tests con 96% menos razonamiento, y sostiene el hallazgo 4.1 del
informe; no genero el entregable.

## Resultados

- **1 prompt** en la conversacion ganadora.
- **9/9** tests de la catedra en verde.
- **`cached_tokens = 1792`** en la conversacion ganadora: el caching que pide
  la consigna quedo demostrado.
- **$0.042728** de gasto sumando los 16 logs entregados, reconciliado contra
  `GET /api/v1/auth/key` en el informe.
- El razonamiento fue el **95,1 %** de los tokens de salida del Ejercicio 2:
  el hallazgo principal de la mision.

## Documentacion

- **`SPEC.md`** — que se construyo y por que: diseño de los 4 slots, como se
  envian los prompts, y las decisiones que ya estan tomadas.
- **`INFORME_EJERCICIO_3.md`** — el trabajo previo obligatorio, la tabla de
  tokens y costos de los 14 intentos, la reconciliacion del gasto y los
  hallazgos.
- **`CLAUDE.md`** — instrucciones para trabajar en este repo con un agente.

## Nota sobre `vida.py`

`vida.py` entra al repo **tal cual salio del chat**, sin editarlo a mano: es la
regla de la consigna y se verifica comparando el archivo contra el bloque de
codigo de su log. Las convenciones de codigo del resto del repo no aplican a
ese archivo.

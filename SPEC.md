# SPEC — Mision "el prompt minimo"

Mision de referencia: `missions/prompting/mission.md` del repo
`austral-ing-ai/talksmith-ing`. Este documento cubre los tres ejercicios:
la interfaz de chat (Ejercicio 1), la generacion de `vida.py` (Ejercicio 2)
y el informe de costos (Ejercicio 3).

## Como se corren los tests (leer antes que nada)

Son **dos suites distintas** y se invocan distinto:

```bash
python -m pytest        # 13 tests del proyecto (usage, logger, models)
python test_vida.py     # 9 tests de la catedra contra vida.py
```

`test_vida.py` **no se corre con pytest**. El archivo de la catedra hace
`sys.argv.pop(1)` durante el import para resolver contra que script correr,
asi que bajo `python -m pytest test_vida.py` se auto-apunta a si mismo y los
9 casos fallan. No es un bug del codigo: es el contrato de ese archivo, que
esta pensado para ejecutarse directo. `pytest.ini` declara
`testpaths = tests`, de modo que `python -m pytest` a secas no lo recoge y no
hay conflicto.

## Ejercicio 1 — Objetivo

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

## El efecto del effort (slot 1)

La primera medicion comparo `low` contra `high` con el prompt "explicame en 2
lineas que es la recursividad" y dio **`reasoning=0` en los dos niveles**: ese
prompt no tiene nada que razonar, asi que el modelo no gasta presupuesto de
pensamiento y la diferencia queda en el ruido.

`correr_effort.py` repite la comparacion con un problema de varios pasos
encadenados (inclusion-exclusion sobre cuatro conjuntos) y ahi el efecto si se
ve, con el mismo prompt en ambos niveles:

| Corrida | Razonamiento | Costo |
|---|---:|---:|
| `slot1-effort-low` | 309 | $0.001122 |
| `slot1-effort-high` | 415 | $0.001151 |

`reasoning_effort` es un **presupuesto maximo, no una cuota obligatoria**: si
la tarea no lo necesita, subir el nivel no cambia nada. Si se rehace esta
medicion, hay que usar una tarea cuya dificultad supere lo que el nivel bajo
resuelve, o el resultado vuelve a ser cero. Detalle en el hallazgo 4.3 del
informe.

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
- `correr_vida.py` — lo mismo que `smoke_test.py` pero para el Ejercicio 2:
  manda el prompt de `prompts/` al slot 4 por el mismo camino de codigo que
  `chat.py`, sin modificarlo. Ver "Ejercicio 2" mas abajo.
- `correr_effort.py` — manda el mismo prompt al slot 1 con effort `low` y
  `high` para comparar sus `reasoning_tokens`. Reusa `test_slot` de
  `smoke_test.py`. Ver "El efecto del effort" mas abajo.
- `prompts/` — los dos prompts del Ejercicio 2, cada uno en una sola linea.

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

## Ejercicio 2 — `vida.py` en 1 prompt

El target (el juego de la vida de Conway) se pidio siempre al slot 4
(`deepseek/deepseek-v4-flash-0731`) a traves del camino de codigo de la
interfaz del Ejercicio 1.

### Como se envia el prompt

`chat.py` lee la entrada con `input()`, que devuelve **una sola linea**. Un
prompt multilinea pegado en la consola se fragmenta en tantos prompts como
renglones tenga y quema la corrida: el log `20260917_172958` tiene 6 turnos
de usuario que son los renglones sueltos de un unico contrato.

Por eso los prompts del Ejercicio 2 estan escritos en **una sola linea**, y
se envian con `correr_vida.py` en lugar de pegarlos a mano: la consola de
Windows no pega de forma fiable un texto de ese tamaño. `correr_vida.py`
importa `build_messages`, `send_chat` y el `logger` de la interfaz sin
modificarlos, asi que el log `.md` que produce es identico al del chat
interactivo. Es el mismo patron que `smoke_test.py`.

### Cual prompt genero el `vida.py` entregado

`prompts/` tiene dos archivos y **no son intercambiables**:

| Archivo | Tamaño | Genero el entregable |
|---|---:|---|
| `prompt_vida_v1_ganador.txt` | 7.264 chars | **SI** — es el turno `## user` del log ganador, extraido textualmente |
| `prompt_vida_v2.txt` | 5.923 chars | No — version optimizada posterior |

El `vida.py` del repo salio del **v1**. El v2 elimina los ejemplos dibujados
como grillas y consigue el mismo resultado en los tests con 96% menos
razonamiento, pero se corrio despues: se conserva como evidencia del
hallazgo 4.1 del informe, no como el prompt del entregable.

Si en el futuro se regenera `vida.py`, hay que actualizar **los dos**: el
codigo y el archivo de prompt que lo produjo, para que sigan correspondiendose
con el log.

### Por que el prompt tiene ese tamaño

Dos restricciones opuestas lo fijan:

- **Piso:** el cache por prefijo de DeepSeek necesita mas de 1.024 tokens
  para activarse. El prompt mide ~1.550 tokens.
- **Techo:** los ejemplos few-shot dibujados como grillas ASCII hacen que el
  modelo los simule celda por celda en su cadena de pensamiento. Una version
  previa que incluia el glider (10x10, 4 generaciones) consumio **60.619
  tokens de razonamiento**; describiendo los mismos casos en prosa bajo a
  **2.578**, con identico resultado en los tests. Ver `INFORME_EJERCICIO_3.md`,
  hallazgo 4.1.

Por eso el prompt transmite el contrato completo y las trampas conocidas en
prosa, y no dibuja ninguna grilla.

### Regla que no se negocia

`vida.py` entra al repo **tal cual salio del chat**. Se extrae del bloque de
codigo del log ganador con una expresion regular, nunca a mano. La
verificacion es que el archivo y el bloque del log coincidan byte a byte
(hoy: 2186 caracteres los dos). Si los tests fallan, lo que se reescribe es
el prompt y se abre una conversacion nueva; nunca se corrige el codigo.

## Ejercicio 3 — el informe

`INFORME_EJERCICIO_3.md` contiene el trabajo previo obligatorio (que es un
router, el mapa de los 7 proveedores y la comparacion de parametros
soportados), la tabla de tokens y costos de todos los intentos, y los
hallazgos. Sus numeros salen de los logs de `logs/` y son reconciliables
contra ellos.

## Donde vive `test_vida.py`

En la raiz, al lado de `vida.py`. El script de la catedra busca `vida.py`
en su propio directorio cuando se lo invoca sin argumentos
(`Path(__file__).parent / "vida.py"`), asi que dentro de `tests/` no lo
encontraba y los 9 casos daban error. Ademas `pytest.ini` apunta
`testpaths = tests`, con lo cual `python -m pytest` lo recogia y mostraba 9
tests en rojo. Con el archivo en la raiz las tres invocaciones quedan en
verde:

```bash
python -m pytest            # 13 tests del proyecto
python test_vida.py         # 9 tests de la catedra
python test_vida.py ruta/a/vida.py
```

El archivo de la catedra no se modifico: solo cambio de ubicacion.

# CLAUDE.md

Guia para trabajar en este repo (mision `talksmith-ing`, ejercicio de
prompting con OpenRouter).

## Que es esto

Interfaz de chat en terminal (`chat.py`) que sirve 4 modelos via OpenRouter,
cada uno ejercitando una capacidad distinta (effort, caching, salidas
estructuradas, modelo barato). Ver `SPEC.md` para el diseño completo del
Ejercicio 1.

`vida.py` (Ejercicio 2) es la unica excepcion a todo lo de abajo: ese
archivo sale tal cual del chat con el modelo, sin tocarlo a mano y sin las
convenciones de este documento.

**No edites `vida.py`. Nunca. Por ningun motivo.** Ni para arreglar un test,
ni para reformatearlo, ni para agregarle un comentario. Tiene que coincidir
byte a byte con el bloque de codigo del log ganador
(`logs/slot4_..._20260918_171450_906651.md`), y la catedra lo verifica
comparando los dos textos. Si `vida.py` deja de coincidir con su log, el
Ejercicio 2 vale cero.

Ojo con los formateadores automaticos: una pasada de Black sobre este
archivo ya rompio esa coincidencia una vez (le saco el shebang y reformateo
`NEIGHBORS`). Si tu editor formatea al guardar, excluilo.

Si los tests fallan, lo que se reescribe es **el prompt**, y se abre una
conversacion nueva con `correr_vida.py`. El codigo no se toca.

`prompts/` tiene dos archivos y no son intercambiables: el `vida.py`
entregado salio de **`prompt_vida_v1_ganador.txt`** (7.264 chars, el turno
`user` del log ganador). `prompt_vida_v2.txt` (5.923 chars) es la version
optimizada posterior que sostiene el hallazgo 4.1 del informe. Si regeneras
`vida.py`, actualiza tambien el archivo de prompt que lo produjo.

## Setup

```bash
python -m pip install -r requirements.txt
cp .env.example .env   # completar OPENROUTER_API_KEY
```

## Correr

```bash
python chat.py            # chat interactivo, los 4 slots
python correr_vida.py     # Ejercicio 2: manda prompts/prompt_vida_v2.txt al slot 4
```

## Testear

```bash
python -m pytest          # 13 tests del proyecto (sin red)
python test_vida.py       # 9 tests de la catedra contra vida.py
```

Los tests de `tests/` cubren `usage.py`, `logger.py` y `models.py`: la parte
sin red del proyecto. No hay tests con mocks del cliente HTTP — la
verificacion de que las llamadas reales a OpenRouter funcionan (usage,
reasoning, cache hits, structured output) se hace con `smoke_test.py`
contra la API real y sus logs quedan en `logs/` como evidencia.

`test_vida.py` es de la catedra y va **en la raiz**, al lado de `vida.py`:
sin argumentos lo busca en su propio directorio. No lo muevas a `tests/` ni
lo edites.

## Convenciones de codigo

- Python estandar + `requests` y `python-dotenv` como unicas dependencias
  externas. No se agregan frameworks sin necesidad concreta.
- Modulos chicos con una responsabilidad cada uno: `openrouter_client.py`
  es el unico lugar que hace red, `usage.py` y `logger.py` son funciones
  puras testeables sin red.
- Texto de cara al usuario (prompts del CLI, mensajes de error) en
  espanol, sin tildes en el codigo fuente para evitar problemas de
  encoding en la consola de Windows; los logs `.md` si llevan tildes
  normales porque se escriben con `encoding="utf-8"` explicito.
- Secretos (la API key de OpenRouter) solo en `.env`, nunca hardcodeados ni
  commiteados. `.env.example` documenta la variable con valor vacio.

## Decisiones que ya se tomaron (no las re-discutas sin razon nueva)

- CLI en terminal, no interfaz web: el enunciado no pide que sea "linda" y
  una CLI cubre el requisito con menos superficie de codigo.
- El contexto estatico del slot 2 (`static_context.py`) tiene ~4800 tokens
  a proposito: Claude Haiku 4.5 no cachea por debajo de 4096 tokens. Si se
  edita ese archivo, no lo achiques por debajo de ese umbral o el cache
  hit deja de verse.
- El schema estructurado del slot 3 es generico (`respuesta`,
  `puntos_clave`, `confianza`) porque el ejercicio pide demostrar la
  capacidad, no un caso de uso especifico.
- El prompt del Ejercicio 2 va en **una sola linea**: `chat.py` lee con
  `input()`, que devuelve una linea, asi que un prompt multilinea se
  fragmenta en varios prompts y quema la corrida.
- Ese prompt **no dibuja grillas ASCII** como ejemplos, y describe los casos
  en prosa. Una version con el glider (10x10, 4 generaciones) hizo que el
  modelo lo simulara a mano: 60.619 tokens de razonamiento contra 2.578, con
  el mismo resultado en los tests. No vuelvas a meter grillas.
- Pero el prompt tampoco puede achicarse por debajo de ~1.024 tokens: es el
  umbral del cache por prefijo de DeepSeek. Hoy mide ~1.550.
- El slot 4 no manda el parametro `reasoning` (`supports_effort=False`), pero
  DeepSeek razona igual por defecto: todas las respuestas traen
  `reasoning_tokens > 0`.

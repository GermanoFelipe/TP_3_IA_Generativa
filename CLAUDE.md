# CLAUDE.md

Guia para trabajar en este repo (mision `talksmith-ing`, ejercicio de
prompting con OpenRouter).

## Que es esto

Interfaz de chat en terminal (`chat.py`) que sirve 4 modelos via OpenRouter,
cada uno ejercitando una capacidad distinta (effort, caching, salidas
estructuradas, modelo barato). Ver `SPEC.md` para el diseño completo del
Ejercicio 1.

`vida.py` (Ejercicio 2, cuando exista) es la unica excepcion a todo lo de
abajo: ese archivo sale tal cual del chat con el modelo, sin tocarlo a mano
y sin las convenciones de este documento.

## Setup

```bash
python -m pip install -r requirements.txt
cp .env.example .env   # completar OPENROUTER_API_KEY
```

## Correr

```bash
python chat.py
```

## Testear

```bash
python -m pytest
```

Los tests (`tests/`) cubren `usage.py`, `logger.py` y `models.py`: la parte
sin red del proyecto. No hay tests con mocks del cliente HTTP — la
verificacion de que las llamadas reales a OpenRouter funcionan (usage,
reasoning, cache hits, structured output) se hace con `smoke_test.py`
contra la API real y sus logs quedan en `logs/` como evidencia.

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

# Informe — Misión "el prompt mínimo"

Ejercicio 3 (la cuenta final), precedido del trabajo previo obligatorio.
Todos los números salen de los logs `.md` de `logs/` y son reconciliables
contra ellos.

---

## 0. Trabajo previo (obligatorio)

### 0.1 ¿Qué hace un router de modelos?

Un router recibe el pedido sin que el cliente elija modelo y lo despacha al
que mejor resuelve esa tarea según la demanda reciente del mercado, con
fallback automático a otro proveedor si el elegido se cae o se satura.
Resuelve dos problemas: **no tener que reelegir modelo cada vez que sale uno
nuevo o cambia el precio**, y **no quedarse sin servicio cuando un proveedor
falla**.

El Auto Router de OpenRouter (`openrouter/auto`) decide en base a lo que el
mercado de OpenRouter usó para tareas parecidas en los últimos 7 días.

### 0.2 Mapa de modelos: el más avanzado de cada proveedor

Precios por millón de tokens y ventana de contexto tomados de
`GET https://openrouter.ai/api/v1/models` el 2026-09-18. La posición en
benchmarks es la del **Artificial Analysis Intelligence Index** que publica
`openrouter.ai/rankings` (datos hasta 2026-09-17).

| Proveedor | Modelo insignia | Entrada $/M | Salida $/M | Ventana | Posición en benchmarks |
|---|---|---:|---:|---:|---|
| Anthropic | `claude-fable-5.1` | 10.00 | 50.00 | 1.000.000 | **#1** del Intelligence Index (53.4) |
| Qwen | `qwen3.8-max-0902` | 2.00 | 6.00 | 1.000.000 | **#2** (53.4, como "Qwen3.8 Max") |
| OpenAI | `gpt-5.5-pro` | 30.00 | 180.00 | 1.050.000 | **#3** de la familia (GPT-6 Astra, 52.8) |
| Grok (xAI) | `grok-4.6` | 2.00 | 6.00 | 500.000 | **#9** (44.4, "Grok 4.6 high") |
| Kimi (Moonshot) | `kimi-k3` | 1.95 | 10.92 | 1.048.576 | **#10** (43.8, "Kimi K3 max") |
| Gemini (Google) | `gemini-3.1-pro-preview` | 2.00 | 12.00 | 1.048.576 | Fuera del top 10 del índice; **#1 en τ²-Bench Airline** (80.6%) con Gemini 3.7 Flash |
| DeepSeek | `deepseek-v4-pro` | 1.60 | 3.20 | 1.048.576 | Fuera del top 10 del índice, pero **#2 y #5 en volumen** de tokens procesados |

Dato relevante para esta misión: en el ranking **por uso real**,
`GPT-5.6 Luna` (nuestro slot 1) es **#1** con 15,8 T de tokens semanales y
`DeepSeek V4 Flash 0731` (nuestro slot 4) es **#5** con 10,6 T. O sea que el
"escalón barato" del ejercicio no es un modelo marginal: es de los más
usados del mercado.

### 0.3 Parámetros soportados: no todos aceptan lo mismo

Comparación de las fichas de los cuatro modelos del Ejercicio 1
(campo `supported_parameters` de la API):

| Parámetro | GPT-5.6 Luna | Claude Haiku 4.5 | Gemini 3.7 Flash | DeepSeek V4 Flash |
|---|:--:|:--:|:--:|:--:|
| `reasoning` / `reasoning_effort` | ✅ / ✅ | ✅ / ❌ | ✅ / ✅ | ✅ / ✅ |
| `structured_outputs` | ✅ | ✅ | ✅ | ✅ |
| `temperature` | ❌ | ✅ | ✅ | ✅ |
| `top_k` | ❌ | ✅ | ❌ | ✅ |
| `seed` | ✅ | ❌ | ✅ | ✅ |
| `logit_bias` / `logprobs` | ❌ | ❌ | ❌ | ✅ |
| `frequency_penalty` | ❌ | ❌ | ❌ | ✅ |

Hallazgos de la comparación:

- **GPT-5.6 Luna no acepta `temperature` ni `top_k`.** Es un razonador puro:
  las perillas de sampling clásicas no están disponibles y el único control
  de "cuánto pensar" es `reasoning_effort`.
- **Claude Haiku 4.5 acepta `reasoning` pero no `reasoning_effort`.** Usa
  presupuesto de pensamiento por `max_tokens`, no por nivel.
- **DeepSeek V4 Flash es el más completo en perillas de sampling**: es el
  único de los cuatro con `logit_bias`, `logprobs` y `frequency_penalty`.
- Los cuatro soportan salidas estructuradas, así que el slot 3 podría
  haberse implementado con cualquiera.

### 0.4 Precios de cache de los cuatro slots

| Modelo | Entrada $/M | Lectura de cache $/M | Escritura de cache |
|---|---:|---:|---|
| `deepseek/deepseek-v4-flash-0731` | 0.060 | **0.012** (5× más barato) | gratis (automático) |
| `anthropic/claude-haiku-4.5` | 1.000 | **0.100** (10× más barato) | 1.250 (se paga) |
| `openai/gpt-5.6-luna` | 0.200 | **0.020** (10× más barato) | 0.250 |
| `google/gemini-3.7-flash` | 0.750 | **0.075** (10× más barato) | 0.042 |

Esto explica la diferencia de diseño entre el slot 2 y el slot 4: en
Anthropic **escribir** el cache cuesta más que el prompt normal, así que hay
que marcar explícitamente qué bloque vale la pena cachear con
`cache_control`. En DeepSeek la escritura es gratis y el cache es automático
por prefijo, así que se activa solamente con el diseño del prompt.

---

## 1. Metodología del Ejercicio 2

El target (Conway) se pidió siempre al slot 4
(`deepseek/deepseek-v4-flash-0731`), a través de la interfaz del Ejercicio 1.
El `vida.py` entregado se extrajo **textualmente** del bloque de código del
log ganador con una expresión regular, sin edición manual: el archivo y el
log coinciden byte a byte (2186 caracteres).

**Nota metodológica 1 — cómo se enviaron los prompts.** Las corridas del
18/09 se lanzaron con `correr_vida.py`, que importa y reutiliza el mismo
camino de código que `chat.py` (`build_messages` → `send_chat` → `logger`) sin
modificarlo, de modo que el log `.md` resultante es idéntico al del chat
interactivo. El motivo es concreto: la consola de Windows no pega de forma
fiable un prompt de ~7.000 caracteres en una sola línea. Los intentos
`20260917_172958` (6 turnos) y `20260918_163813` son la evidencia de ese
problema: el `input()` de `chat.py` lee una línea por vez, así que un pegado
multilínea se fragmenta en varios prompts y quema la corrida. Se sigue el
mismo patrón que `smoke_test.py`, que generó los logs de prueba del
Ejercicio 1.

**Nota metodológica 2 — el razonamiento.** La consigna pide el slot 4 "con el
razonamiento activado". `chat.py` sólo envía el parámetro `reasoning` para
los slots con `supports_effort=True`, y el slot 4 está configurado con
`False`, así que el parámetro **no se envía explícitamente**. Sin embargo el
razonamiento está activo: todas las respuestas devuelven
`reasoning_tokens > 0` (entre 80 y 60.619 según la corrida), porque DeepSeek
razona por defecto. Activarlo de forma explícita habría requerido modificar
`models.py`, que pertenece al Ejercicio 1.

**Nota metodológica 3 — llamadas abortadas.** Además de las corridas de la
tabla, **6 llamadas nunca devolvieron respuesta** y se cortaron por timeout
del cliente. No tienen usage asociado ni aparecen en el gasto de los logs;
sus archivos se descartaron por no contener ningún dato auditable. Se
detallan en el hallazgo 4.2.

**Nota metodológica 4 — corridas solapadas y marcas de tiempo.** La
conversación ganadora se inició a las 17:14:50 y su respuesta recién llegó a
las 17:36, después de más de 20 minutos generando. Mientras tanto se lanzaron
otras corridas en paralelo, que terminaron antes: por eso las fechas de
modificación de los archivos `20260918_172415`, `20260918_172551` y
`20260918_172844` son **anteriores** a la del log ganador, aunque sus
conversaciones empezaron **después**. El nombre de cada archivo lleva la
marca de tiempo de inicio de la conversación, no la de su última escritura.

**Nota metodológica 5 — cuál prompt produjo el `vida.py` entregado.** El
directorio `prompts/` contiene dos archivos, y no son intercambiables:

| Archivo | Tamaño | Glider | Corresponde a |
|---|---:|:--:|---|
| `prompt_vida_v1_ganador.txt` | 7.264 chars | sí | **La conversación ganadora** (fila 11). Extraído textualmente del turno `## user` de su log |
| `prompt_vida_v2.txt` | 5.923 chars | no | Las corridas optimizadas posteriores (filas 12 a 14) |

El `vida.py` entregado salió del **v1**. El v2 es la versión optimizada que
se probó después y que sostiene el hallazgo 4.1; se conserva porque es la
evidencia de la mejora, no porque haya generado el entregable.

---

## 2. Tokens por intento y totales

Cada fila es un turno de rol `user` con su respuesta. La columna **#u** es la
cantidad total de turnos de usuario de esa conversación.

| # | Log (`logs/slot4_…`) | #u | Turno | Entrada | Salida | Razonam. | Cacheados | Costo USD | Estado |
|---|---|:--:|:--:|---:|---:|---:|---:|---:|---|
| 1 | `20260917_172503` | 2 | 1 | 101 | 380 | 189 | 0 | 0.000137 | Quemado (fragmentación) |
| 2 | `20260917_172958` | 6 | 1 | 392 | 250 | 247 | 0 | 0.000044 | Quemado (6 prompts) |
| 3 | `20260917_172958` | 6 | 2 | 392 | 250 | 247 | 0 | 0.000044 | ″ |
| 4 | `20260917_172958` | 6 | 3 | 392 | 250 | 247 | 0 | 0.000044 | ″ |
| 5 | `20260917_172958` | 6 | 4 | 526 | 241 | 192 | 0 | 0.000047 | ″ |
| 6 | `20260917_172958` | 6 | 5 | 392 | 250 | 247 | 0 | 0.000044 | ″ |
| 7 | `20260917_173315` | 2 | 1 | 392 | 250 | 247 | 0 | 0.000044 | 2 prompts |
| 8 | `20260917_173315` | 2 | 2 | 546 | 6308 | 5738 | 0 | 0.002198 | 2 prompts (dio código) |
| 9 | `20260918_163813` | 1 | 1 | 84 | 107 | 80 | 0 | 0.000042 | Nulo (pegado fallido) |
| 10 | `20260918_164800` | 1 | 1 | 2004 | 5503 | 4999 | 0 | 0.002031 | 1 prompt |
| 11 | **`20260918_171450`** | **1** | **1** | **2123** | **61237** | **60619** | **1792** | **0.021008** | **🏆 GANADORA** |
| 12 | `20260918_172415` | 1 | 1 | 1553 | 3382 | 2578 | 0 | 0.001455 | 1 prompt (optimizado) |
| 13 | `20260918_172551` | 1 | 1 | 1553 | 2966 | 2181 | 0 | 0.000717 | 1 prompt (optimizado) |
| 14 | `20260918_172844` | 1 | 1 | 1575 | 3981 | 3370 | 0 | 0.001153 | 1 prompt (optimizado) |
| | **TOTALES** | | | **12.025** | **85.355** | **81.181** | **1.792** | **0.029008** | 14 llamadas en 9 conversaciones |

La conversación ganadora (fila 11) tiene **un solo turno de usuario**, los
**9 tests de `test_vida.py` pasan** contra el `vida.py` que salió de ella, y
su usage muestra **1.792 tokens cacheados**.

---

## 3. La cuenta final

### 3.1 Entrada y salida

- **Entrada total:** 12.025 tokens
- **Salida total:** 85.355 tokens
- **Relación salida/entrada:** 7,1 a 1

La salida domina el gasto por dos motivos: la salida cuesta el doble que la
entrada ($0,12 contra $0,06 por millón) y el razonamiento se factura dentro
de la salida.

### 3.2 Tokens de pensamiento y qué se facturó por ellos

- **Razonamiento total:** 81.181 tokens, el **95,1 %** de toda la salida.
- OpenRouter los reporta en `completion_tokens_details.reasoning_tokens` y
  los **incluye dentro de `completion_tokens`**: no son un renglón aparte, se
  facturan al precio de salida.
- Traducido a dinero: 81.181 × $0,12/M ≈ **$0,0097**, o sea que **el
  pensamiento explica alrededor de un tercio del gasto total** de la misión.

**Hallazgo.** La corrida ganadora gastó **60.619 tokens de razonamiento para
producir 618 tokens de código**: 98 tokens pensados por cada token escrito.
Ver el hallazgo 4.1 para la causa y la corrección.

A diferencia de lo que anticipa la consigna para la serie `o` de OpenAI,
DeepSeek **sí devuelve** los tokens de razonamiento, así que fueron medibles
en todas las corridas.

### 3.3 Tokens cacheados y ahorro

- **Tokens cacheados:** 1.792, todos en la corrida ganadora.
- **Precio de lectura de cache:** $0,012/M contra $0,060/M de entrada normal
  (5× más barato).
- **Ahorro obtenido:** 1.792 × ($0,060 − $0,012)/M = **$0,000086**.

El ahorro es minúsculo en términos absolutos, y ese es en sí mismo el
resultado: **con prompts de ~2.000 tokens el cache es irrelevante frente al
costo del razonamiento**. Los 1.792 tokens cacheados ahorraron $0,000086,
mientras que los 60.619 tokens de razonamiento de esa misma llamada costaron
unos $0,0073 — es decir, **85 veces más de lo que el cache llegó a ahorrar**.
El cache recién rendiría con un prefijo estático de decenas de miles de
tokens.

**Hallazgo.** El cache de DeepSeek resultó **intermitente**: el mismo prefijo
de 2.123 tokens dio `cached=0` en sus primeras llamadas y `cached=1792`
recién en la cuarta, mientras que el prefijo optimizado de 1.553 tokens no
cacheó en ninguna de sus cuatro llamadas pese a superar el umbral de 1.024
tokens. Los `prompt_tokens` del mismo archivo de prompt variaron entre 1.553
y 1.575 según la llamada, lo que sugiere que OpenRouter rutea a instancias
distintas del proveedor y que el cache de prefijo es por instancia.

### 3.4 Gasto total contra el dashboard

| Fuente | Monto |
|---|---:|
| Suma de los logs del Ejercicio 2 (14 llamadas) | **$0,029008** |
| Ejercicio 1 — slot 1, dos corridas de effort | $0,000122 |
| Ejercicio 1 — slot 2, con cache hit | $0,009009 |
| Ejercicio 1 — slot 3, salida estructurada | $0,002171 |
| Ejercicio 1 — slot 4, log de prueba | $0,000145 |
| **Total atribuible a esta misión** | **$0,040455** |
| **Dashboard de OpenRouter (`openrouter.ai/activity`)** | **$0,075618 (via `auth/key`)** |

Dato lateral que confirma la premisa del ejercicio: el slot 2 (Claude Haiku
4.5) costó **$0,009009 en dos turnos**, más que las 14 llamadas del
Ejercicio 2 contra el slot 4 juntas descontando la ganadora. El "escalón
barato" no es una metáfora.

La cuenta de OpenRouter es de la cátedra y no tenemos acceso a su panel de
actividad, así que el contraste se hizo contra la fuente equivalente que sí
expone la API: `GET /api/v1/auth/key`, que devuelve el gasto acumulado **de
la key del grupo** (la key tiene un límite propio de $1, independiente del
crédito de la cuenta).

| Fuente | Monto |
|---|---:|
| Suma de todos los logs entregados | $0,040455 |
| **`usage` reportado por la API para la key** | **$0,075618** |
| **Diferencia sin registrar en logs** | **$0,035163** |

### Por qué no cierran, desglosado por día

`auth/key` también informa `usage_daily`, lo que permite ubicar la
diferencia:

| Día | Suma de los logs | Gasto real de la key | Diferencia |
|---|---:|---:|---:|
| 16/09 — Ejercicio 1 | $0,011447 | — | — |
| 17/09 — Ejercicio 2, primeros intentos | $0,002602 | — | — |
| 16 y 17/09 combinados | $0,014049 | $0,024807 | **$0,010758** |
| 18/09 — Ejercicio 2, corridas finales | $0,026406 | $0,050812 | **$0,024406** |
| **Total** | **$0,040455** | **$0,075618** | **$0,035163** |

**La diferencia del 18/09 ($0,024406) son las 6 llamadas abortadas.** Se
cortaron por timeout del lado del cliente, pero el modelo siguió generando
del lado del servidor y esos tokens se facturaron. Como el cliente nunca
recibió la respuesta, `logger.py` nunca escribió el turno del assistant y no
quedó ningún usage registrado. La magnitud es coherente: una sola llamada
completada con ese mismo prompt costó $0,021008, así que seis llamadas que
razonaron hasta cortarse explican holgadamente esos $0,0244.

**La diferencia del 16 y 17/09 ($0,010758) es anterior a estas corridas.**
Corresponde a pruebas que no quedaron en `logs/`. Una de ellas está
documentada en `SPEC.md`: un primer intento del slot 2 con un contexto
estático de ~2.000 tokens que no generó ningún cache hit, y que motivó
ampliar `static_context.py` a ~4.800 tokens. Ese intento no fue conservado.

**Conclusión del contraste.** Los logs capturan el **53,5 %** del gasto real.
No es un error de contabilidad del informe sino una limitación del
instrumento: `logger.py` escribe el usage **después** de recibir la
respuesta, de modo que toda llamada que no vuelve queda facturada pero
invisible. Para auditar el gasto con precisión habría que registrar el turno
del assistant con un marcador de error cuando la llamada falla, o consultar
`auth/key` antes y después de cada corrida.

### 3.5 Conclusión

**Sacar del prompt el ejemplo few-shot del glider.** Esa única grilla de
10×10 simulada 4 generaciones hizo que el modelo recorriera 1.600
evaluaciones de celda dentro de su cadena de pensamiento: el prompt con
glider consumió 60.619 tokens de razonamiento y $0,021, y el mismo prompt con
los ejemplos descritos en prosa consumió 2.578 y $0,0015 — **96 % menos
razonamiento y 93 % menos costo, con los mismos 9 tests en verde**.

**Fijar `reasoning_effort: "low"` en el slot 4.** El catálogo confirma que el
modelo lo acepta, y `chat.py` hoy no lo manda porque el slot está declarado
con `supports_effort=False`. Siendo el razonamiento el 95 % de la salida
facturada, es la perilla con mayor impacto por línea de código cambiada.

**No optimizar para el cache a esta escala.** Con prefijos de ~2.000 tokens
el ahorro medido fue de $0,000086, dos órdenes de magnitud menos que lo que
cuesta el razonamiento de una sola llamada; el esfuerzo de diseño rinde mucho
más puesto en acortar la cadena de pensamiento que en alargar el prefijo
estático.

---

## 4. Hallazgos

### 4.1 Un ejemplo few-shot puede costar 14 veces el precio de la tarea

Comparación directa de las dos versiones del mismo prompt, ambas con 1 solo
turno y ambas con los 9 tests en verde:

| | Con el glider (fila 11) | En prosa (fila 12) | Diferencia |
|---|---:|---:|---:|
| Entrada | 2.123 | 1.553 | −27 % |
| Razonamiento | 60.619 | 2.578 | **−96 %** |
| Costo | $0,021008 | $0,001455 | **−93 %** |
| Tiempo de respuesta | > 10 min | 66 s | **−89 %** |
| Tests en verde | 9/9 | 9/9 | igual |

La lección es contraintuitiva: el ejemplo del glider parecía el más valioso
por ser el patrón más complejo, pero **describir los casos en prosa transmite
el mismo contrato sin invitar al modelo a simularlos**. El prompt no perdió
ni un test.

### 4.2 El endpoint del slot 4 es intermitente

De 21 llamadas realizadas contra `deepseek/deepseek-v4-flash-0731`, **6
nunca devolvieron respuesta** (28 %), quedando colgadas indefinidamente. El
`timeout=120` de `openrouter_client.py` no las cortó, presumiblemente porque
OpenRouter envía bytes de keepalive que reinician el contador de lectura de
`requests`. Las llamadas colgadas no siguen ningún patrón de tamaño: se
colgaron tanto prompts de 6.801 caracteres como de 5.923, y el mismo prompt
de 5.923 respondió en 66 s en un intento y nunca en otro.

Un diagnóstico con un prompt mínimo ("Responde únicamente con la palabra OK")
respondió en **2,0 segundos**, lo que descarta que el problema sea de
conectividad o de credenciales.

La misma inestabilidad se observa en los logs del 17/09: de 8 turnos, 6
devolvieron literalmente `"yes"` con un usage idéntico
(`392/250/247`) y uno devolvió un JSON en portugués sobre una "lead" de
ventas, contenido que no corresponde a ninguna pregunta formulada. Sólo 1 de
esos 8 turnos produjo el código pedido.

### 4.3 La interfaz de chat no admite prompts multilínea

`chat.py` lee la entrada con `input()`, que devuelve una sola línea. Pegar un
prompt multilínea lo fragmenta en tantos prompts como renglones tenga, y cada
fragmento cuenta como un turno de usuario. Ése es el origen del intento
quemado `20260917_172958`, cuyos 6 turnos son los renglones sueltos de un
único contrato.

**Corrección sugerida** (fuera del alcance de este ejercicio, porque
`chat.py` pertenece al Ejercicio 1): leer la entrada hasta un delimitador
explícito, por ejemplo una línea con `.` sola, en lugar de hasta el primer
salto de línea.

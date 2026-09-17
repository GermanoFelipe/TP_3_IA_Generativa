# Informe de Auditoría y Métricas - Ejercicio 3

## 1. Métricas por Intento y Acumulado

| Intento / Archivo de Log | Estado | Prompt Tokens | Completion Tokens | Reasoning Tokens | Cached Tokens | Gasto (USD) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `logs/slot4_deepseek_deepseek-v4-flash-0731_20260917_172503_594881.md` | Quemado (fragmentación en shell) | 101 | 380 | 189 | 0 | $0.000137 |
| `logs/slot4_deepseek_deepseek-v4-flash-0731_20260917_172958_281346.md` | Quemado (corte por tope de salida) | 2.090 | 1.241 | 1.180 | 0 | $0.000223 |
| `logs/slot4_deepseek_deepseek-v4-flash-0731_20260917_173315_880958.md` (P1) | Ganadora (prompt base) | 392 | 250 | 247 | 0 | $0.000044 |
| `logs/slot4_deepseek_deepseek-v4-flash-0731_20260917_173315_880958.md` (P2) | Ganadora (código final, 9/9 verdes) | 546 | 6.308 | 5.738 | 0 | $0.002198 |
| **Totales Acumulados** | — | **3.129** | **8.179** | **7.354** | **0** | **$0.002602** |

---

## 2. Análisis de Auditoría y Hallazgos

* **Tokens de razonamiento y facturación:** El modelo `deepseek/deepseek-v4-flash-0731` necesitó 5.738 tokens de reasoning para derivar la solución antes de escribir los 570 tokens de Python puro. OpenRouter reporta estos tokens en `completion_tokens_details.reasoning_tokens` y los factura dentro del importe estándar de `completion_tokens`.
* **Caché de prefijo:** En las llamadas locales se registró `cached=0`. Esto ocurre porque el mecanismo de caché por prefijo de DeepSeek requiere superar un umbral mínimo de tokens repetidos (habitualmente 1.024 tokens) o que la réplica interna del proveedor en OpenRouter mantenga el estado caliente entre solicitudes consecutivas.
* **Gasto total:** La resolución completa de Conway requirió apenas **$0.0026 USD** en total entre los intentos descartados y la conversación ganadora, confirmando la rentabilidad del Slot 4.

---

## 3. Conclusión

Para alcanzar el target estrictamente en 1 prompt y reducir costos, se debe suprimir el límite de `max_tokens` restrictivo en el cliente HTTP e implementar un presupuesto acotado de pensamiento mediante `reasoning: {"effort": "low"}`. Adicionalmente, incorporar lectura multilínea por delimitador en la interfaz evita fragmentaciones accidentales en la terminal y envía la especificación completa en una sola llamada.
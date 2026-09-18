# Conversacion - slot 1 - openai/gpt-5.6-luna

Iniciada: 2026-09-18T19:18:50.542353

## user

Cuantos enteros entre 1 y 10000 inclusive no son divisibles ni por 2, ni por 3, ni por 5, ni por 7? Resolvelo sin escribir ni ejecutar codigo. Mostra el planteo y termina con el numero final.

## assistant

Aplicamos el **principio de inclusión-exclusión**.

Queremos contar los enteros entre \(1\) y \(10000\) que no sean divisibles por \(2,3,5\) ni \(7\).

### 1. Múltiplos de cada número

\[
\left\lfloor\frac{10000}{2}\right\rfloor+
\left\lfloor\frac{10000}{3}\right\rfloor+
\left\lfloor\frac{10000}{5}\right\rfloor+
\left\lfloor\frac{10000}{7}\right\rfloor
\]

\[
=5000+3333+2000+1428=11761
\]

### 2. Restamos las intersecciones de a dos

Los mínimos comunes múltiplos son:

\[
6,10,14,15,21,35
\]

Por lo tanto:

\[
\left\lfloor\frac{10000}{6}\right\rfloor+
\left\lfloor\frac{10000}{10}\right\rfloor+
\left\lfloor\frac{10000}{14}\right\rfloor+
\left\lfloor\frac{10000}{15}\right\rfloor+
\left\lfloor\frac{10000}{21}\right\rfloor+
\left\lfloor\frac{10000}{35}\right\rfloor
\]

\[
=1666+1000+714+666+476+285=4807
\]

### 3. Sumamos las intersecciones de a tres

\[
\operatorname{mcm}(2,3,5)=30,\quad
\operatorname{mcm}(2,3,7)=42,
\]
\[
\operatorname{mcm}(2,5,7)=70,\quad
\operatorname{mcm}(3,5,7)=105
\]

Entonces:

\[
\left\lfloor\frac{10000}{30}\right\rfloor+
\left\lfloor\frac{10000}{42}\right\rfloor+
\left\lfloor\frac{10000}{70}\right\rfloor+
\left\lfloor\frac{10000}{105}\right\rfloor
\]

\[
=333+238+142+95=808
\]

### 4. Restamos la intersección de los cuatro

\[
\operatorname{mcm}(2,3,5,7)=210
\]

\[
\left\lfloor\frac{10000}{210}\right\rfloor=47
\]

Por inclusión-exclusión, la cantidad buscada es:

\[
10000-11761+4807-808+47
\]

\[
\boxed{2285}
\]

[usage] prompt=62 completion=925 reasoning=309 cached=0 cost=$0.001122


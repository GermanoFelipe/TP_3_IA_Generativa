# Conversacion - slot 2 - anthropic/claude-haiku-4.5

Iniciada: 2026-09-16T17:29:55.507322

## user

Segun el manual, que se hace primero cuando falla un sistema en produccion?

## assistant

Según la sección 10 "Incidentes en produccion", **lo primero es contener el impacto** antes de investigar la causa raiz con calma.

Esto significa:

1. **Revertir el último deploy** si el timing coincide con la falla
2. **Deshabilitar la funcionalidad afectada** si hay un feature flag disponible

Solo después de contener el daño se investiga qué pasó realmente. La lógica es clara: mientras investigas, los usuarios siguen sin servicio o con servicio degradado, así que lo prioritario es que vuelva a funcionar rápido, aunque sea de forma parcial.

Una vez estabilizado, se hace un post-mortem documentado que responde: qué pasó, por qué pasó, qué se hizo para mitigarlo, y qué cambio concreto se va a hacer para que no vuelva a ocurrir.

[usage] prompt=4841 completion=226 reasoning=0 cached=0 cost=$0.007175

## user

Y que politica hay sobre secretos en el repositorio?

## assistant

Según la sección 8 "Seguridad", la política es tajante:

**Ningún secreto se hardcodea en el código fuente ni se sube al repositorio**, ni siquiera en un commit temprano que después se revierte. Una vez que un secreto llegó al historial de git, **se lo considera comprometido y hay que rotarlo**.

Los secretos deben vivir en:
- **Variables de entorno**, o
- **Un gestor de secretos**

El repositorio solo contiene un archivo de ejemplo (`.env.example`) con las claves vacías, para que quien clone el proyecto sepa qué variables necesita configurar.

Esto aplica a API keys, contraseñas, tokens de acceso y cualquier credencial. La razón es que aunque elimines un commit después, la información sigue en el historial y cualquiera con acceso al repositorio puede recuperarla.

[usage] prompt=5083 completion=217 reasoning=0 cached=4815 cost=$0.001834


---
mode: agent
description: Incorpora una fuente nueva al framework (configuración + contrato), sin escribir código
---

Vamos a incorporar una fuente nueva. Datos de partida: ${input:fuente:nombre, dominio, origen SQL o landing y clave de negocio}

Sigue estos pasos en orden y no te saltes ninguno:

1. Lee `AGENTS.md`, `docs/convenciones.md` y `config/fuentes/<dominio>.yml`.
2. Si te falta la clave de negocio, el significado de alguna columna o los valores permitidos de un campo categórico, **pregunta antes de seguir**.
3. Crea el contrato `contracts/silver/<fuente>.yml` partiendo de `templates/contrato/contrato.yml`. Propón la política de rechazo y justifícala en una línea.
4. Añade la fuente a `config/fuentes/<dominio>.yml` apuntando a ese contrato.
   Para SQL declara conexión, esquema, tabla y proyección; los nombres de servidor/base pertenecen al entorno.
   Usa extracción completa primero. No añadas exportaciones a CSV ni defectos artificiales al DataFrame.
5. No crees notebooks: `nb_10_bronze_ingesta` y `nb_20_silver_estandarizar` son genéricos y sirven para cualquier fuente.
6. Ejecuta `python scripts/agente_lint.py` sobre el contrato y el fichero de fuentes (valida el esquema, las referencias cruzadas y regenera el catálogo). No sigas hasta que no dé errores.
7. Termina con un resumen: ficheros tocados, decisiones que has tomado y dudas abiertas para el propietario del dato.

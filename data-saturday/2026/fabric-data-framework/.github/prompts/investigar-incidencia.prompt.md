---
mode: agent
description: Ayuda a diagnosticar una carga fallida o que no reconcilia
---

Hay una incidencia en una carga: ${input:incidencia:tabla, batch_id y lo que se ha observado}

1. Sigue `docs/runbooks/carga-fallida.md`.
2. Usa las consultas de `sql/ops/` con los valores de esta incidencia; si necesitas una nueva, créala en `sql/ops/` y pásale `python scripts/agente_lint.py`.
3. Con los resultados que te pase, distingue entre problema de datos de origen, contrato demasiado estricto o bug del framework.
4. Si es un bug del framework, escribe primero el test que lo reproduce en `tests/unit/` y después la corrección. Pasa `python scripts/agente_lint.py` sobre ambos ficheros y `pytest`.
5. Nunca propongas relajar un contrato como solución sin indicar que necesita aprobación del propietario.

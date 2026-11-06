---
mode: agent
description: Revisa los cambios de la rama actual contra la checklist del proyecto
---

Revisa los cambios de esta rama respecto a `main` (`git diff main...HEAD`).

1. Ejecuta `python scripts/agente_lint.py` sobre los ficheros modificados (`git diff --name-only main...HEAD`). Lo que encuentre son incumplimientos automáticos: lístalos primero, con fichero y línea.
2. Aplica `docs/checklist-revision.md` punto por punto. Para cada uno: cumple / no cumple / no aplica, con la evidencia (fichero y línea).
3. Señala especialmente lo que los linters no pueden ver: métricas que no están en el glosario, contratos modificados sin aviso, funciones sin test y reglas silenciadas (`# noqa`, `# fwk: ignore`, `# type: ignore`) sin un motivo convincente.
4. No reescribas el código: propón el cambio mínimo para cada problema.
5. Termina con un veredicto: **aprobar**, **aprobar con cambios menores** o **pedir cambios**.

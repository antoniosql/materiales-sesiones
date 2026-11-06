# Instrucciones para GitHub Copilot

Las instrucciones del proyecto están en `AGENTS.md`, y en los `AGENTS.md` de `fabric/ingenieria/` y `fabric/analitica/`. Síguelas.

Copilot no ejecuta los linters por sí solo después de cada edición, así que hazlo tú:

- Después de crear o modificar ficheros, ejecuta en la terminal `python scripts/agente_lint.py <ficheros que has tocado>` y corrige lo que indique antes de seguir.
- Antes de dar la tarea por terminada: `pre-commit run --all-files` y `pytest`.

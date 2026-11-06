---
mode: agent
description: Crea una tabla gold nueva respetando contrato, glosario, plantillas y tests
---

Necesitamos una tabla gold nueva: ${input:peticion:qué tabla, con qué grano y para qué informe}

1. Lee `AGENTS.md`, `fabric/ingenieria/AGENTS.md`, `docs/convenciones.md` y **`docs/glosario.md`**.
2. Identifica cada métrica de la petición en el glosario. Si alguna no está definida, **para y pregunta**: no inventes la definición.
3. Crea el contrato `contracts/gold/<tabla>.yml` (gold usa `politica_rechazo: fallar` salvo que se justifique otra cosa).
4. Implementa el cálculo como función pura en `src/datafwk/gold/<tabla>.py` y su test en `tests/unit/test_<tabla>.py` con un caso normal, uno con cancelados o nulos y uno vacío.
5. Crea el notebook `fabric/ingenieria/nb_30_gold_<proposito>.Notebook/` copiando `templates/notebook/`, con un `logicalId` nuevo.
6. Ejecuta `python scripts/agente_lint.py` sobre todos los ficheros que has creado o modificado y corrige lo que indique. Después, `pytest`.
7. Revisa tu trabajo contra `docs/checklist-revision.md` y lista los puntos que no cumples y por qué.

# AGENTS.md — reglas para asistentes de código

Este repositorio sigue un framework de ingeniería de datos y analítica en Microsoft Fabric.
Antes de escribir nada, lee `docs/convenciones.md` y `docs/glosario.md`.
Las carpetas `fabric/ingenieria/` y `fabric/analitica/` tienen su propio AGENTS.md con reglas adicionales.

## Mapa del repositorio
- `fabric/<workspace>/` — items de Fabric sincronizados por Git. Una carpeta por workspace: `datos`, `ingenieria`, `analitica`
- `src/datafwk/` — librería común. Toda la lógica vive aquí, nunca en los notebooks
- `config/fuentes/<dominio>.yml` — fuentes declaradas; `config/entornos/` — nombres por entorno
- `contracts/<capa>/<tabla>.yml` — contrato de cada tabla de silver y gold
- `schemas/` — JSON Schema de contratos, fuentes y entornos
- `sql/` — consultas Spark SQL versionadas
- `templates/` — punto de partida obligatorio para notebooks, contratos y tests
- `docs/` — convenciones, glosario de negocio, checklist de revisión, ADR, runbooks

## Reglas no negociables
1. Toda tabla nueva necesita su contrato en `contracts/` ANTES que el notebook o el código que la genera.
2. Los notebooks se crean copiando `templates/notebook/`; nunca desde cero. Cada item nuevo en `fabric/` lleva su `.platform` con un `logicalId` GUID nuevo y único.
3. Nunca rutas `abfss://` escritas a mano: usa `datafwk.rutas` o `datafwk.arranque`.
4. Nunca credenciales, IDs de workspace ni nombres de entorno en el código: van en `config/entornos/` y `fabric/*/parameter.yml`.
5. Toda función de transformación nueva es una función pura en `src/datafwk/` y lleva test en `tests/unit/`.
6. Si una definición de negocio (un KPI, un estado, una regla) no está en `docs/glosario.md` ni en un contrato, PREGUNTA. No la inventes.
7. `docs/catalogo.md` no se edita: se regenera con `python scripts/generar_catalogo.py`. Esta sección de linters tampoco: se regenera con `python scripts/sincronizar_agents.py`.
8. No cambies un contrato existente sin decirlo explícitamente en tu respuesta: un cambio de contrato es un cambio para quien consume la tabla.
9. No silencies un linter (`# noqa`, `# fwk: ignore`, `# type: ignore`) sin el motivo en la misma línea y sin decirlo en tu respuesta.

<!-- inicio: sección generada por scripts/sincronizar_agents.py, no editar a mano -->
## Linters: lo que se comprueba automáticamente

Después de crear o modificar ficheros, ejecuta `python scripts/agente_lint.py <ficheros>` y corrige lo que indique **antes de seguir** (en Claude Code se ejecuta solo tras cada edición). Corrige solo lo que puede corregirse sin decidir nada (formato, imports, estilo SQL); si lo hace, vuelve a leer el fichero.

### Reglas del framework

| Regla | Qué detecta |
|---|---|
| FW001 | ruta abfss:// escrita a mano: usa datafwk.rutas o datafwk.arranque |
| FW002 | instalación de paquetes en un notebook: las dependencias van en el Environment |
| FW003 | collect()/toPandas() sin limit(): puede traer la tabla entera al driver |
| FW004 | nombre de notebook fuera de convención: nb_\<nn>_\<capa>_\<propósito> (10 bronze 20 silver 30 gold 90 ops) |
| FW005 | .platform incoherente con su carpeta (tipo o displayName) |
| FW006 | logicalId inválido o repetido |
| FW007 | la celda de parámetros debe declarar entorno = "dev" y workspace_datos |
| FW008 | nombre de lakehouse fuera de convención: lh_\<nombre> |
| FW009 | demasiada lógica en el notebook (más de 25 líneas): muévela a src/datafwk/ |
| FW010 | GUID escrito en el código: los IDs van en config/entornos/ o en parameter.yml |

FW009 cuenta las líneas de código fuera de la celda de parámetros (máximo 25). Una excepción solo con motivo en la misma línea: `# fwk: ignore FW003 -- tabla de 12 filas`.

### Convenciones que imponen los linters y no son evidentes

- **Python:** Ruff con las reglas de `pyproject.toml` y líneas de 120. En `src/`, mypy estricto: todas las funciones con tipos completos y sin `Any` implícito.
- **Notebooks de Fabric:** se revisan con Ruff pero no se formatean. `spark`, `notebookutils` y `display` existen sin importarlos. `print()` solo en notebooks y `scripts/`; en `src/` se devuelven resultados.
- **Contratos, fuentes, modelos y entornos:** cumplen su JSON Schema de `schemas/`. Nombres en snake_case, tipos de Spark SQL (`decimal(p,s)` para importes) y `descripcion` en cada columna. Un texto con comas va entre comillas: sin ellas YAML lo parte en dos claves.
- **SQL** (Spark SQL, `.sqlfluff`): palabras clave en MAYÚSCULAS, funciones e identificadores en minúsculas, alias con `AS`, columnas cualificadas cuando hay alias y parámetros como `:nombre`.
- **Workflows de GitHub Actions:** actions fijadas por SHA con la versión en un comentario, `permissions` mínimos por job, `persist-credentials: false` y nunca `${{ }}` dentro de `run:` (se pasa por `env:`).
- **Terraform:** formateado con `terraform fmt`; toda variable y todo output con `description`, y las variables con `type`.
- **Secretos:** ninguno en el repositorio, tampoco en notebooks, ejemplos ni tests. Los valores de ejemplo se escriben como marcadores `<nombre>`.
<!-- fin: sección generada -->

## Antes de dar una tarea por terminada
- `pre-commit run --all-files` sin errores y `pytest` en verde
- Si has tocado `fabric/analitica/` y estás en Windows: `pwsh ./scripts/analizar_modelos.ps1` y `pwsh ./scripts/inspeccionar_informes.ps1`
- Revisa tu propio trabajo contra `docs/checklist-revision.md` y di qué puntos no has podido cumplir

## Tareas frecuentes
Hay prompts versionados en `.github/prompts/`: `nueva-fuente`, `nueva-tabla-gold`, `revisar-pr`, `investigar-incidencia`. Úsalos.

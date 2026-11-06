# Plantilla · Framework de ingeniería de datos y analítica en Microsoft Fabric

Repositorio plantilla para proyectos de datos en Fabric y Python preparados para trabajar con IA Generativa.
Es la versión "proyecto real" del framework del workshop *75 años de proyectos de datos en un framework*
(Data Saturday Madrid 2026).

> La IA amplifica lo que encuentra en el repositorio. Si encuentra convenciones, las sigue.
> Si encuentra caos, lo multiplica. Los linters son lo que convierte las convenciones en algo que se cumple.

## Las siete piezas

La rama evolutiva incorpora generación greenfield, lectura SQL directa, ventanas incrementales confirmadas,
cuarentena versionada, revalidación y activación SCD2 sobre una dimensión tipo1.
El [recorrido de cuatro horas](docs/runbooks/workshop-evolutivo.md) explica los comandos, notebooks y checkpoints de [templates/workshop](templates/workshop/README.md). Para validar también almacenamiento y recuperación local:
`pytest --delta` (Java 17; en Windows requiere además las bibliotecas nativas de Hadoop).

| # | Pieza | Dónde |
|---|---|---|
| 1 | Convenciones | `docs/convenciones.md` |
| 2 | Estructura del repositorio | este README · `docs/adr/0001-estructura-del-repositorio.md` |
| 3 | Librería común | `src/datafwk/` |
| 4 | Metadatos | `config/` · `schemas/` |
| 5 | Contratos de datos y calidad | `contracts/` · `docs/catalogo.md` (generado) · `calidad/` |
| 6 | Testing, linters y CI/CD | `tests/` · `.pre-commit-config.yaml` · `.github/workflows/` · `infra/` |
| 7 | Capa de IA | `AGENTS.md` (jerárquico) · `.github/prompts/` · `templates/` · `docs/glosario.md` · `docs/checklist-revision.md` |

## Estructura

```
├── AGENTS.md / CLAUDE.md          reglas para asistentes; la sección de linters se genera desde los linters
├── fabric/                        items de Fabric, UNA CARPETA POR WORKSPACE
│   ├── datos/                     lakehouses bronze/silver/gold · sin código
│   ├── ingenieria/                notebooks, pipelines, Environment · AGENTS.md · parameter.yml
│   └── analitica/                 modelos semánticos (TMDL) e informes (PBIR) · AGENTS.md · parameter.yml
├── src/datafwk/                   librería: arranque, config, rutas, estandarizar, calidad, auditoría, carga
├── config/entornos/               nombres de workspace y lakehouse por entorno
├── config/fuentes/<dominio>.yml   fuentes declaradas: añadir una fuente no requiere código
├── config/modelos/<modelo>.yml   modelo gold, atributos tipo1/SCD2 y proyección actual
├── contracts/{silver,gold}/       contrato por tabla: tipos, nulos, valores, reglas, propietario
├── schemas/                       JSON Schema de contratos, fuentes y entornos (editor + linters)
├── sql/                           consultas Spark SQL versionadas (operación, gold)
├── calidad/                       reglas de Best Practice Analyzer y Fab Inspector
├── templates/                     notebook, contrato y test de partida
├── tests/{unit,contracts,integration}/
├── scripts/                       linter del framework, contratos, catálogo, despliegue, BPA, Fab Inspector
├── infra/                         Terraform: workspaces, capacidades y permisos
├── docs/                          convenciones, glosario, checklist, catálogo, ADR, runbooks
├── .github/                       CI/CD, Dependabot, zizmor, prompts, instrucciones y entorno de Copilot, CODEOWNERS
├── .claude/                       hook que pasa los linters tras cada edición + comandos (envoltorios de los prompts)
├── .vscode/                       esquemas YAML, formateo al guardar y extensiones recomendadas
└── .pre-commit-config.yaml · .yamllint.yml · .sqlfluff · .tflint.hcl · .gitleaks.toml
```

## Flujo de trabajo

```
rama feat/…  ──►  workspace de feature (branch out, conectado a Git)
     │
     ▼ commit  →  pre-commit: linters sobre los ficheros modificados
     ▼ PR      →  CI: linters sobre todo el repo · tests · secretos · BPA/Fab Inspector · revisión (CODEOWNERS)
main ──►  deploy.yml  →  DEV  →  TEST  (+ tests de integración)
     └─►  deploy-prod.yml (manual, con aprobación)  →  PROD
```

- **Solo los workspaces de feature se conectan a Git.** Dev, Test y Prod los despliega `fabric-cicd`; nadie los edita a mano.
- En cada despliegue: (1) `config/` y `contracts/` se publican en `lh_bronze/Files/_framework/`, (2) el wheel de `datafwk` se publica en el Environment `env_fwk`, (3) se despliegan los items de los tres workspaces en orden datos → ingeniería → analítica.
- Los notebooks reciben solo `entorno` y `workspace_datos` (sustituidos por `parameter.yml`) y leen todo lo demás con `datafwk.arranque.cargar_contexto`.

## Primeros pasos

1. **Crear el repo** desde esta plantilla (`git init` si partes de la carpeta) y abrirlo en el devcontainer. Sin devcontainer: Python 3.11, Java 17, Terraform, tflint y `pip install -e ".[dev]"`
2. **Activar los linters:** `pre-commit install` (el devcontainer ya lo hace). Desde ese momento cada commit pasa por ellos
3. **Renombrar** `proyecto` en `config/entornos/*.yml`, `fabric/*/parameter.yml` y `infra/ejemplo.tfvars`
4. **Infra:** `cd infra && terraform init && terraform apply -var-file=<entorno>.tfvars`. Haz commit de `.terraform.lock.hcl`
5. **GitHub Environments** `dev`, `test`, `prod` con las vars `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `WS_DATOS_ID`, `WS_ING_ID`, `WS_ANA_ID`, `ENV_FWK_ID` (federated credential OIDC en el service principal). `prod` con revisores obligatorios
6. **Protección de `main`:** PR obligatorio y checks requeridos (ver [Checks obligatorios](#checks-obligatorios-para-hacer-merge))
7. **En Fabric (dev):** crear el Environment `env_fwk` en el workspace de ingeniería, conectar el workspace de feature a `fabric/ingenieria`, adjuntar `env_fwk` a los notebooks y hacer commit desde el workspace (así el formato Git del Environment y de los pipelines lo genera Fabric, no nosotros)
8. **Sustituir** el dominio de ejemplo `ventas` por el primero real: `config/fuentes/`, `contracts/`, `docs/glosario.md`

---

## Calidad y linters

### El proceso: los mismos linters en cada momento

| Momento | Qué se ejecuta | Sobre qué | Quién lo dispara |
|---|---|---|---|
| **0 · Mientras el agente escribe** | Los linters del tipo de fichero que acaba de tocar | Ese fichero | El agente de IA: automático en Claude Code, por instrucción en Copilot (ver abajo) |
| **1 · Al escribir** | Ruff, mypy, esquemas YAML, SQLFluff, Terraform, Actions | El fichero abierto | VS Code, con las extensiones recomendadas en `.vscode/` |
| **2 · Al hacer commit** | Todos los linters de `.pre-commit-config.yaml` | Solo los ficheros del commit | `pre-commit`, automáticamente en `git commit` |
| **3 · En el PR** | Todos los linters + tests + secretos en todo el historial + BPA y Fab Inspector si hay modelos o informes | Todo el repositorio | GitHub Actions (`ci.yml`) |

La configuración de cada herramienta está en un solo sitio y la usan todos los momentos, así que **lo que pasa en local pasa en CI**.
El momento 2 es una red rápida; el que manda es el 3: un commit hecho desde el workspace de Fabric o con `--no-verify`
no pasa por pre-commit, pero no llega a `main` sin pasar por CI.

**Cuando pre-commit falla al hacer commit:**
1. Los hooks que arreglan solos (Ruff, `sqlfluff-fix`, finales de línea) ya han modificado los ficheros: revisa el cambio con `git diff`
2. Corrige a mano lo que quede (el mensaje dice fichero, línea y regla)
3. `git add` de nuevo y repite el commit

### Los agentes de IA usan los mismos linters

Un agente que genera código sin pasar por los linters entrega trabajo que el CI rechazará después.
El objetivo es que corrija **mientras escribe**, no en el PR. Hay tres piezas:

**1. Instrucciones generadas, no escritas a mano.** La sección *Linters* de `AGENTS.md` la genera
`scripts/sincronizar_agents.py`: las reglas FW salen del propio `scripts/lint_framework.py`, y el resto son
solo las convenciones que el agente no puede deducir (estilo SQL, notebooks sin formatear, esquemas de
contratos, workflows...). Un hook de pre-commit y un test fallan si `AGENTS.md` no está al día: las
instrucciones nunca se desfasan de lo que se comprueba. No se copian las reglas de Ruff a `AGENTS.md`:
son cientos, el agente ya las conoce y gastarían contexto.

**2. Un linter pensado para el agente: `scripts/agente_lint.py`.** Recibe los ficheros que el agente acaba
de tocar y, según su tipo, aplica las herramientas que corresponden con la misma configuración que pre-commit:

| Fichero | Corrige solo | Comprueba |
|---|---|---|
| `src/**/*.py` | `ruff --fix`, `ruff format` | Ruff, mypy, reglas FW |
| `scripts/**/*.py` | `ruff --fix`, `ruff format` | Ruff, reglas FW |
| Notebooks de `fabric/` | `ruff --fix` (sin formatear) | Ruff, reglas FW |
| `.platform` | — | Reglas FW (nombre, `logicalId`) |
| Contratos | Regenera el catálogo | yamllint, JSON Schema, referencias cruzadas |
| Fuentes y entornos | — | yamllint, JSON Schema, referencias cruzadas |
| Workflows | — | yamllint, actionlint, zizmor |
| SQL | `sqlfluff fix` | SQLFluff |
| Terraform | `terraform fmt` | — (validate y tflint, en pre-commit) |

Solo corrige solo lo que no requiere decidir nada (formato, imports, estilo). Lo demás lo devuelve como
error, con fichero, línea y regla, para que el agente lo arregle. Tarda entre 0,1 y 3 segundos por fichero.

**3. Cómo lo usa cada agente:**

| Agente | Cómo llega a los linters |
|---|---|
| **Claude Code** | **Automático.** El hook `PostToolUse` de `.claude/settings.json` ejecuta `agente_lint.py` tras cada edición. Si hay errores, Claude los recibe y los corrige antes de seguir; si el script ha corregido algo solo, se le avisa para que vuelva a leer el fichero |
| **Copilot en VS Code** (modo agente) | Por instrucción: `.github/copilot-instructions.md` y `AGENTS.md` le piden ejecutar `agente_lint.py` tras cada cambio. Además ve los diagnósticos de las extensiones recomendadas (Ruff, YAML con esquemas, SQLFluff) en el panel de problemas |
| **Copilot coding agent** (en GitHub) | Igual que en VS Code, con el entorno preparado por `.github/workflows/copilot-setup-steps.yml`: dependencias, linters y hooks de pre-commit ya instalados |
| **Cualquier otro** (Codex, Cursor...) | `AGENTS.md` y los prompts de `.github/prompts/`, que terminan siempre ejecutando `agente_lint.py` |

En todos los casos la red final es la misma: el CI del PR. Las instrucciones hacen que el agente acierte
más a la primera; el CI garantiza que lo que no acierta no llega a `main`.

**Para desactivar el hook** puntualmente en Claude Code (por ejemplo, en una refactorización grande que
dejará el código roto varios pasos): `/hooks` en la sesión, o un `.claude/settings.local.json` personal,
que no se sube al repositorio.

### Qué revisa cada herramienta

| Herramienta | Qué revisa | Ficheros | Configuración | Ejecutarlo a mano |
|---|---|---|---|---|
| **gitleaks** | Secretos: claves, tokens, cadenas de conexión con contraseña | Todo (en CI, todo el historial) | `.gitleaks.toml` | `pre-commit run gitleaks --all-files` |
| **Ruff** | Errores, imports, estilo, seguridad (reglas de bandit), `print` fuera de sitio y formato | `*.py`, notebooks incluidos | `pyproject.toml` · `[tool.ruff]` | `ruff check . --fix` · `ruff format .` |
| **mypy** | Tipos, en modo estricto | `src/` (la librería) | `pyproject.toml` · `[tool.mypy]` | `mypy` |
| **Linter del framework** | Las reglas de `AGENTS.md` (FW001–FW010, abajo) | `fabric/`, `src/`, `scripts/` | `scripts/lint_framework.py` | `python scripts/lint_framework.py` |
| **Contratos y catálogo** | Fuente → contrato existe, claves coinciden, catálogo al día | `contracts/`, `config/`, `docs/catalogo.md` | `scripts/` | `python scripts/validar_contratos.py` · `python scripts/generar_catalogo.py` |
| **yamllint** | Sintaxis y estilo de todos los YAML | `*.yml` | `.yamllint.yml` | `yamllint -s .` |
| **check-jsonschema** | Estructura de contratos, fuentes y entornos: campos obligatorios, tipos, `snake_case` | `contracts/`, `config/` | `schemas/*.schema.json` | `check-jsonschema --schemafile schemas/contrato.schema.json contracts/*/*.yml` |
| **SQLFluff** | Errores y estilo de SQL (dialecto Spark SQL) | `sql/**/*.sql` | `.sqlfluff` | `sqlfluff lint sql/` · `sqlfluff fix sql/` |
| **actionlint** | Sintaxis, expresiones y scripts de los workflows | `.github/workflows/` | — | `actionlint` |
| **zizmor** | Seguridad de los workflows: permisos, inyecciones, credenciales, actions sin fijar | `.github/` | `.github/zizmor.yml` | `zizmor --offline .github` |
| **Terraform + tflint** | Formato, validez contra el provider y malas prácticas | `infra/` | `.tflint.hcl` | `terraform -chdir=infra fmt` · `terraform -chdir=infra validate` · `tflint --chdir=infra --config "$PWD/.tflint.hcl"` |
| **Best Practice Analyzer** | Buenas prácticas de modelos semánticos: reglas de Microsoft + las del framework | `fabric/**/*.SemanticModel` | `calidad/bpa/reglas-proyecto.json` | `pwsh ./scripts/analizar_modelos.ps1` (Windows) |
| **Fab Inspector** | Buenas prácticas de informes: visuales, páginas, filtros | `fabric/**/*.Report` | `calidad/fab-inspector/` | `pwsh ./scripts/inspeccionar_informes.ps1` (Windows) |

Todo de una vez, igual que CI: `pre-commit run --all-files` y después `pytest`.

### Reglas del framework (FW001–FW010)

Son las reglas de `AGENTS.md` que se pueden comprobar con código. Un asistente de IA sigue `AGENTS.md` casi siempre; este linter cubre el "casi".

| Regla | Qué detecta | Por qué |
|---|---|---|
| FW001 | Una ruta `abfss://` escrita a mano fuera de `datafwk.rutas`/`arranque` | Las rutas cambian por entorno: escritas a mano, el notebook de Dev escribe en Prod |
| FW002 | `%pip install` o `!pip` en un notebook | Las dependencias van en el Environment `env_fwk`, versionadas |
| FW003 | `collect()` o `toPandas()` sin `limit()` en un notebook | Trae la tabla entera al driver |
| FW004 | Notebook que no sigue `nb_<nn>_<capa>_<propósito>` (10 bronze, 20 silver, 30 gold, 90 ops) | El nombre dice qué hace y en qué capa |
| FW005 | `.platform` cuyo tipo o `displayName` no coincide con la carpeta | Fabric crea un item duplicado al sincronizar |
| FW006 | `logicalId` a ceros, inválido o repetido | Típico al copiar un item: Fabric confunde los dos |
| FW007 | Celda de parámetros sin `entorno = "dev"` y `workspace_datos` | Sin ellos, `parameter.yml` no puede cambiar el entorno al desplegar |
| FW008 | Lakehouse que no se llama `lh_<nombre>` | Convención de nombres |
| FW009 | Más de 25 líneas de código en un notebook | La lógica va a `src/datafwk/`, donde tiene tests |
| FW010 | Un GUID en el código de un notebook | Los IDs van en `config/entornos/` o `parameter.yml` |

Para una excepción justificada, en la propia línea: `df.collect()  # fwk: ignore FW003 -- tabla de 12 filas`.
Las reglas nuevas se añaden en `scripts/lint_framework.py` con su test en `tests/unit/test_lint_framework.py`.

### Los que se activan con el contenido

- **SQLFluff** solo revisa ficheros `.sql`. Hoy revisa las consultas de `sql/ops/`; cuando haya transformaciones gold en SQL, van a `sql/gold/` y quedan cubiertas sin tocar nada. Si se añade un Warehouse, su SQL va en `sql/warehouse/` con su propio `.sqlfluff` con `dialect = tsql`.
- **Best Practice Analyzer** y **Fab Inspector** no corren en pre-commit: necesitan Windows y tardan. En CI, el job `detectar` busca carpetas `*.SemanticModel` y `*.Report` y solo entonces lanza los jobs de Windows. Mientras no haya modelos ni informes aparecen como *skipped*.
- **Cuándo ejecutarlos a mano:** antes de abrir un PR que toque `fabric/analitica/`. En Windows, `pwsh ./scripts/analizar_modelos.ps1` y `pwsh ./scripts/inspeccionar_informes.ps1`. Descargan lo que necesitan en `.herramientas/` (ignorado por Git), verificando la huella SHA256.
- **Severidades de BPA:** 3 (error) bloquea el PR; 2 (aviso) y 1 (información) se muestran pero no bloquean.

### Checks obligatorios para hacer merge

En *Settings → Branches → main*: exigir PR y estos checks. Un job que no se ejecuta por su condición (*skipped*) cuenta como superado, así que los de modelos e informes pueden ser obligatorios desde el primer día.

- `Linters (pre-commit)`
- `Tests`
- `Secretos (gitleaks, historial completo)`
- `Modelos semánticos (Best Practice Analyzer)`
- `Informes (Fab Inspector)`

### Decisiones que conviene conocer

| Decisión | Motivo |
|---|---|
| Los notebooks pasan `ruff check` pero **no** `ruff format` | Fabric reescribe el fichero en cada sincronización: formatearlo produciría cambios fantasma en cada commit desde el workspace |
| mypy estricto **solo** en `src/` | La librería la usan todos los notebooks: un error de tipos ahí se propaga. En scripts y tests no compensa |
| zizmor en modo `--offline` en pre-commit | No necesita token. La auditoría completa, que consulta GitHub, se lanza a mano: `GH_TOKEN=$(gh auth token) zizmor .github` |
| gitleaks del historial completo **solo en CI** | En local revisa lo que vas a commitear; en CI, todo lo que ha existido alguna vez |
| Actions fijadas por **SHA** y hooks por versión | Evita que un cambio en una herramienta externa rompa el CI o introduzca código no revisado. Dependabot propone las actualizaciones de actions y de Python cada mes |
| `templates/` excluido de los linters | Contiene marcadores `<...>` que no son código válido a propósito |
| La sección de linters de `AGENTS.md` se **genera** | Unas instrucciones escritas a mano se desfasan de la configuración real en semanas |
| El hook de Claude Code revisa **un fichero** tras cada edición, no todo el repo | Respuesta en segundos; la revisión completa la hacen pre-commit y CI |

### Mantenimiento

- **Una vez al mes:** `pre-commit autoupdate`, `pre-commit run --all-files` y PR con el resultado. Revisar y aprobar los PR de Dependabot
- **Al añadir una regla de negocio comprobable:** al linter del framework (con test) y `python scripts/sincronizar_agents.py`, que la lleva a `AGENTS.md`
- **Al cambiar la configuración de un linter** de forma que afecte a cómo se escribe el código: actualizar `CONVENCIONES` en `scripts/sincronizar_agents.py` y regenerar
- **Al adoptar BPA y Fab Inspector:** revisar las reglas que fallan en el primer modelo real y decidir cuáles se desactivan, en lugar de ignorar el job

---

## Comandos

```bash
pre-commit run --all-files               # todos los linters, como CI
pytest                                   # tests unitarios y de contratos (integración excluida)
python scripts/agente_lint.py FICHEROS   # lo que ejecuta el agente: corrige lo seguro y lista el resto
python scripts/lint_framework.py         # solo las reglas del framework
python scripts/sincronizar_agents.py     # regenera la sección de linters de AGENTS.md
python scripts/generar_catalogo.py       # regenera docs/catalogo.md
```

## Antes de usarlo en un cliente: verificar

Fabric cambia cada mes. Comprobar contra la documentación vigente:
- Formato `parameter.yml` y API de `fabric-cicd` (`scripts/desplegar.py`)
- Endpoints de la API de Environments para publicar librerías (`scripts/publicar_libreria.py`)
- Soporte de Git para Environments con librerías personalizadas y para Data Pipelines con referencias entre workspaces
- Nombre del zip de la CLI en la release de Fab Inspector (`scripts/inspeccionar_informes.ps1`) y su huella
- Formato de los prompt files de Copilot (`mode:` en el frontmatter)

El Terraform está validado con `terraform validate` y `tflint` contra el provider `microsoft/fabric` 1.14.0.

"""Genera en AGENTS.md la sección de linters a partir de las reglas reales de los linters.

Así las instrucciones del agente no se desfasan de lo que de verdad se comprueba: las reglas FW
salen de scripts/lint_framework.py y el resto de este fichero, que cambia junto a la configuración.

Uso: python scripts/sincronizar_agents.py [--comprobar]
Con --comprobar (pre-commit y CI) falla si AGENTS.md no está al día.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from scripts.lint_framework import MAX_LINEAS_CODIGO_NOTEBOOK, REGLAS  # noqa: E402

AGENTS = RAIZ / "AGENTS.md"
INICIO = "<!-- inicio: sección generada por scripts/sincronizar_agents.py, no editar a mano -->"
FIN = "<!-- fin: sección generada -->"

CONVENCIONES = [
    "**Python:** Ruff con las reglas de `pyproject.toml` y líneas de 120. En `src/`, mypy estricto: "
    "todas las funciones con tipos completos y sin `Any` implícito.",
    "**Notebooks de Fabric:** se revisan con Ruff pero no se formatean. `spark`, `notebookutils` y `display` "
    "existen sin importarlos. `print()` solo en notebooks y `scripts/`; en `src/` se devuelven resultados.",
    "**Contratos, fuentes, modelos y entornos:** cumplen su JSON Schema de `schemas/`. Nombres en snake_case, tipos de "
    "Spark SQL (`decimal(p,s)` para importes) y `descripcion` en cada columna. Un texto con comas va entre "
    "comillas: sin ellas YAML lo parte en dos claves.",
    "**SQL** (Spark SQL, `.sqlfluff`): palabras clave en MAYÚSCULAS, funciones e identificadores en minúsculas, "
    "alias con `AS`, columnas cualificadas cuando hay alias y parámetros como `:nombre`.",
    "**Workflows de GitHub Actions:** actions fijadas por SHA con la versión en un comentario, `permissions` "
    "mínimos por job, `persist-credentials: false` y nunca `${{ }}` dentro de `run:` (se pasa por `env:`).",
    "**Terraform:** formateado con `terraform fmt`; toda variable y todo output con `description`, y las "
    "variables con `type`.",
    "**Secretos:** ninguno en el repositorio, tampoco en notebooks, ejemplos ni tests. Los valores de ejemplo "
    "se escriben como marcadores `<nombre>`.",
]


def generar_seccion() -> str:
    lineas = [
        INICIO,
        "## Linters: lo que se comprueba automáticamente",
        "",
        "Después de crear o modificar ficheros, ejecuta `python scripts/agente_lint.py <ficheros>` y corrige lo que "
        "indique **antes de seguir** (en Claude Code se ejecuta solo tras cada edición). Corrige solo lo que puede "
        "corregirse sin decidir nada (formato, imports, estilo SQL); si lo hace, vuelve a leer el fichero.",
        "",
        "### Reglas del framework",
        "",
        "| Regla | Qué detecta |",
        "|---|---|",
        # '\<' para que GitHub no interprete <nn> o <nombre> como etiquetas HTML
        *[f"| {codigo} | {texto.replace('<', chr(92) + '<')} |" for codigo, texto in REGLAS.items()],
        "",
        f"FW009 cuenta las líneas de código fuera de la celda de parámetros (máximo {MAX_LINEAS_CODIGO_NOTEBOOK}). "
        "Una excepción solo con motivo en la misma línea: `# fwk: ignore FW003 -- tabla de 12 filas`.",
        "",
        "### Convenciones que imponen los linters y no son evidentes",
        "",
        *[f"- {c}" for c in CONVENCIONES],
        FIN,
    ]
    return "\n".join(lineas)


def sincronizar(texto: str) -> str:
    if INICIO not in texto or FIN not in texto:
        raise SystemExit(f"AGENTS.md no tiene los marcadores de la sección generada:\n{INICIO}\n{FIN}")
    antes, resto = texto.split(INICIO, 1)
    _, despues = resto.split(FIN, 1)
    return antes + generar_seccion() + despues


if __name__ == "__main__":
    actual = AGENTS.read_text(encoding="utf-8")
    nuevo = sincronizar(actual)
    if "--comprobar" in sys.argv:
        if actual != nuevo:
            print("AGENTS.md no está al día con los linters: ejecuta python scripts/sincronizar_agents.py")
            sys.exit(1)
        print("AGENTS.md al día")
    else:
        AGENTS.write_text(nuevo, encoding="utf-8")
        print("Sección de linters de AGENTS.md regenerada")

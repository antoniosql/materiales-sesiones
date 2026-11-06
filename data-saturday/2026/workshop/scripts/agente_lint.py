"""Linter para agentes de IA: revisa, y corrige lo que se puede corregir solo, los ficheros que acaba de tocar.

Uso:
    python scripts/agente_lint.py RUTA [RUTA ...]   # Copilot, Codex, cualquier agente o persona
    python scripts/agente_lint.py --hook-claude     # hook PostToolUse de Claude Code (lee el evento por stdin)

Usa las mismas herramientas y configuración que pre-commit, pero solo sobre esos ficheros y con
mensajes pensados para que el agente corrija en el momento, no en el PR.

Códigos de salida: 0 sin problemas · 1 con problemas (modo CLI) · 2 con problemas (modo hook:
Claude Code entrega la salida de error al agente para que la corrija).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

ESQUEMAS = {
    "contracts/": "schemas/contrato.schema.json",
    "config/fuentes/": "schemas/fuentes.schema.json",
    "config/entornos/": "schemas/entorno.schema.json",
    "config/modelos/": "schemas/modelo.schema.json",
}
EXCLUIDOS = ("templates/", ".git/", ".herramientas/")
INSTALAR = "pip install -e '.[dev]'"


@dataclass(frozen=True)
class Paso:
    nombre: str
    comando: tuple[str, ...] = ()
    corrige: bool = False  # autocorrección: no reporta errores, solo cambia el fichero
    funcion: Callable[[], list[str]] | None = None


@dataclass
class Resultado:
    ruta: str
    errores: list[str]
    avisos: list[str]
    modificado: bool


# --------------------------------------------------------------------------- pasos internos


def _framework(rel: str) -> Callable[[], list[str]]:
    def revisar_framework() -> list[str]:
        from scripts.lint_framework import revisar

        return [str(h) for h in revisar(RAIZ, [RAIZ / rel])]

    return revisar_framework


def _contratos() -> list[str]:
    from scripts.validar_contratos import validar

    return validar(RAIZ)


def _catalogo() -> list[str]:
    from scripts.generar_catalogo import DESTINO, generar

    contenido = generar(RAIZ)
    if not DESTINO.exists() or DESTINO.read_text(encoding="utf-8") != contenido:
        DESTINO.write_text(contenido, encoding="utf-8")
    return []


# --------------------------------------------------------------------------- qué revisar en cada fichero


def planificar(rel: str) -> list[Paso]:
    """Pasos para un fichero (ruta relativa a la raíz, con '/'). Lista vacía si no hay nada que revisar."""
    if rel.startswith(EXCLUIDOS):
        return []
    ruta = PurePosixPath(rel)
    pasos: list[Paso] = []

    if ruta.suffix == ".py":
        pasos.append(Paso("ruff --fix", ("ruff", "check", "--fix", "--quiet", rel), corrige=True))
        if not rel.startswith("fabric/"):  # Fabric reescribe los notebooks: no se formatean
            pasos.append(Paso("ruff format", ("ruff", "format", "--quiet", rel), corrige=True))
        pasos.append(Paso("ruff", ("ruff", "check", "--output-format", "concise", rel)))
        if rel.startswith("src/"):
            pasos.append(Paso("mypy", ("mypy",)))  # toda la librería, con la configuración de pyproject.toml

    if rel.startswith(("fabric/", "src/", "scripts/")) and (ruta.suffix == ".py" or ruta.name == ".platform"):
        pasos.append(Paso("framework", funcion=_framework(rel)))

    if ruta.suffix in (".yml", ".yaml"):
        pasos.append(Paso("yamllint", ("yamllint", "-s", "-f", "parsable", rel)))
        for prefijo, esquema in ESQUEMAS.items():
            if rel.startswith(prefijo):
                pasos.append(Paso("esquema", ("check-jsonschema", "--schemafile", esquema, rel)))
        if rel.startswith(("contracts/", "config/")):
            pasos.append(Paso("contratos", funcion=_contratos))
        if rel.startswith("contracts/"):
            pasos.append(Paso("catálogo", corrige=True, funcion=_catalogo))
        if rel.startswith(".github/workflows/"):
            pasos.append(Paso("actionlint", ("actionlint", rel)))
            pasos.append(Paso("zizmor", ("zizmor", "--offline", "--quiet", rel)))

    if ruta.suffix == ".sql":
        pasos.append(Paso("sqlfluff fix", ("sqlfluff", "fix", "--quiet", rel), corrige=True))
        pasos.append(Paso("sqlfluff", ("sqlfluff", "lint", rel)))

    if ruta.suffix == ".tf":
        pasos.append(Paso("terraform fmt", ("terraform", "fmt", rel), corrige=True))

    return pasos


# --------------------------------------------------------------------------- ejecución


def _huella(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest() if ruta.exists() else ""


def revisar_fichero(rel: str) -> Resultado:
    ruta = RAIZ / rel
    antes = _huella(ruta)
    errores: list[str] = []
    avisos: list[str] = []
    for paso in planificar(rel):
        if paso.funcion is not None:
            salida = paso.funcion()
            if salida and not paso.corrige:
                errores.append(f"[{paso.nombre}]\n" + "\n".join(salida))
            continue
        if shutil.which(paso.comando[0]) is None:
            avisos.append(f"{paso.comando[0]} no está instalado: no se ha revisado '{paso.nombre}' ({INSTALAR})")
            continue
        proceso = subprocess.run(paso.comando, cwd=RAIZ, capture_output=True, text=True, timeout=180, check=False)  # noqa: S603
        if proceso.returncode != 0 and not paso.corrige:
            texto = (proceso.stdout + proceso.stderr).strip()
            errores.append(f"[{paso.nombre}]\n{texto}")
    return Resultado(rel, errores, avisos, modificado=antes != _huella(ruta))


def _relativa(ruta: str) -> str | None:
    absoluta = (RAIZ / ruta).resolve() if not Path(ruta).is_absolute() else Path(ruta).resolve()
    try:
        rel = absoluta.relative_to(RAIZ.resolve()).as_posix()
    except ValueError:
        return None  # fuera del repositorio
    return rel if absoluta.is_file() else None


def informe(resultados: list[Resultado]) -> tuple[str, str]:
    """(texto de errores para el agente, texto informativo)."""
    errores, info = [], []
    for r in resultados:
        if r.errores:
            errores.append(f"## {r.ruta}\n" + "\n\n".join(r.errores))
        if r.modificado:
            info.append(
                f"{r.ruta}: corregido automáticamente (formato, imports o estilo). Vuelve a leerlo antes de editarlo."
            )
        info += [f"{r.ruta}: {a}" for a in r.avisos]
    texto_errores = ""
    if errores:
        texto_errores = (
            "Los linters del proyecto han encontrado problemas en lo que acabas de escribir. "
            "Corrígelos ahora, antes de seguir con la tarea. Las reglas FW están explicadas en AGENTS.md; "
            "no silencies una regla sin justificarlo en la misma línea.\n\n" + "\n\n".join(errores)
        )
    return texto_errores, "\n".join(info)


def main(argv: list[str]) -> int:
    modo_hook = "--hook-claude" in argv
    if modo_hook:
        evento = json.load(sys.stdin)
        candidatas = [evento.get("tool_input", {}).get("file_path", "")]
    else:
        candidatas = [a for a in argv if not a.startswith("--")]

    rutas = [rel for c in candidatas if c and (rel := _relativa(c)) and planificar(rel)]
    resultados = [revisar_fichero(rel) for rel in rutas]
    texto_errores, texto_info = informe(resultados)

    if modo_hook:
        if texto_errores:
            print(f"{texto_errores}\n\n{texto_info}".strip(), file=sys.stderr)
            return 2
        if texto_info:  # sin errores, pero el agente debe saber que el fichero ha cambiado
            contexto = {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": texto_info}}
            print(json.dumps(contexto, ensure_ascii=False))
        return 0

    for texto in (texto_info, texto_errores):
        if texto:
            print(texto)
    if not texto_errores:
        print(f"Sin problemas en {len(resultados)} fichero(s) revisado(s).")
    return 1 if texto_errores else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Linter de las reglas del framework: convierte AGENTS.md en comprobaciones automáticas.

Uso:
    python scripts/lint_framework.py            # revisa todo el repositorio
    python scripts/lint_framework.py RUTA ...   # revisa solo esos ficheros (lo usa pre-commit)

Para ignorar una regla en una línea concreta, con justificación:
    df.collect()  # fwk: ignore FW003 -- tabla de 12 filas de parámetros
"""

from __future__ import annotations

import json
import re
import sys
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# Únicos ficheros autorizados a construir rutas de OneLake (y el propio linter, que las busca)
RUTAS_PERMITIDAS = {"src/datafwk/rutas.py", "src/datafwk/arranque.py", "scripts/lint_framework.py"}
CARPETAS_REVISADAS = ("fabric", "src", "scripts")
MAX_LINEAS_CODIGO_NOTEBOOK = 25
CAPA_POR_PREFIJO = {"10": "bronze", "20": "silver", "30": "gold", "90": "ops"}

RE_NOTEBOOK = re.compile(r"^nb_(\d{2})_([a-z]+)_[a-z0-9_]+$")
RE_LAKEHOUSE = re.compile(r"^lh_[a-z0-9_]+$")
RE_GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
RE_IGNORAR = re.compile(r"#\s*fwk:\s*ignore\s+((?:FW\d{3}[\s,]*)+)")
RE_SEPARADOR_CELDA = re.compile(r"^# (CELL|PARAMETERS CELL|MARKDOWN|METADATA) \*+$")

REGLAS = {
    "FW001": "ruta abfss:// escrita a mano: usa datafwk.rutas o datafwk.arranque",
    "FW002": "instalación de paquetes en un notebook: las dependencias van en el Environment",
    "FW003": "collect()/toPandas() sin limit(): puede traer la tabla entera al driver",
    "FW004": "nombre de notebook fuera de convención: nb_<nn>_<capa>_<propósito> (10 bronze 20 silver 30 gold 90 ops)",
    "FW005": ".platform incoherente con su carpeta (tipo o displayName)",
    "FW006": "logicalId inválido o repetido",
    "FW007": 'la celda de parámetros debe declarar entorno = "dev" y workspace_datos',
    "FW008": "nombre de lakehouse fuera de convención: lh_<nombre>",
    "FW009": f"demasiada lógica en el notebook (más de {MAX_LINEAS_CODIGO_NOTEBOOK} líneas): muévela a src/datafwk/",
    "FW010": "GUID escrito en el código: los IDs van en config/entornos/ o en parameter.yml",
}


@dataclass(frozen=True)
class Hallazgo:
    ruta: str
    linea: int
    regla: str
    detalle: str = ""

    def __str__(self) -> str:
        extra = f" ({self.detalle})" if self.detalle else ""
        return f"{self.ruta}:{self.linea}: {self.regla} {REGLAS[self.regla]}{extra}"


def _relativa(ruta: Path, raiz: Path) -> str:
    return ruta.resolve().relative_to(raiz.resolve()).as_posix()


def _ignoradas(linea: str) -> set[str]:
    m = RE_IGNORAR.search(linea)
    return set(re.findall(r"FW\d{3}", m.group(1))) if m else set()


def _es_comentario(linea: str) -> bool:
    return linea.lstrip().startswith("#")


# --------------------------------------------------------------------------- código Python


def revisar_python(ruta: Path, raiz: Path) -> Iterator[Hallazgo]:
    rel = _relativa(ruta, raiz)
    es_notebook = ruta.name == "notebook-content.py"
    for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), start=1):
        ignorar = _ignoradas(linea)
        if "abfss://" in linea and rel not in RUTAS_PERMITIDAS and "FW001" not in ignorar:
            yield Hallazgo(rel, n, "FW001")
        if not es_notebook or _es_comentario(linea):
            continue
        codigo = linea.strip()
        if re.match(r"^[%!]\s*pip\b", codigo) and "FW002" not in ignorar:
            yield Hallazgo(rel, n, "FW002")
        if re.search(r"\.(collect|toPandas)\(\)", codigo) and ".limit(" not in codigo and "FW003" not in ignorar:
            yield Hallazgo(rel, n, "FW003")
        if RE_GUID.search(codigo) and "FW010" not in ignorar:
            yield Hallazgo(rel, n, "FW010")


# --------------------------------------------------------------------------- notebooks


def _celdas(texto: str) -> list[tuple[str, list[str]]]:
    celdas: list[tuple[str, list[str]]] = []
    for linea in texto.splitlines():
        m = RE_SEPARADOR_CELDA.match(linea)
        if m:
            celdas.append((m.group(1), []))
        elif celdas:
            celdas[-1][1].append(linea)
    return celdas


def revisar_notebook(carpeta: Path, raiz: Path) -> Iterator[Hallazgo]:
    rel = _relativa(carpeta, raiz)
    nombre = carpeta.name.removesuffix(".Notebook")
    m = RE_NOTEBOOK.match(nombre)
    if not m:
        yield Hallazgo(rel, 1, "FW004", nombre)
    elif CAPA_POR_PREFIJO.get(m.group(1)) != m.group(2):
        yield Hallazgo(rel, 1, "FW004", f"el prefijo {m.group(1)} no corresponde a la capa '{m.group(2)}'")

    contenido = carpeta / "notebook-content.py"
    if not contenido.exists():
        return
    celdas = _celdas(contenido.read_text(encoding="utf-8"))
    parametros = "\n".join(linea for tipo, lineas in celdas if tipo == "PARAMETERS CELL" for linea in lineas)
    if not re.search(r'^entorno = "dev"', parametros, re.M) or not re.search(r"^workspace_datos = ", parametros, re.M):
        yield Hallazgo(_relativa(contenido, raiz), 1, "FW007")

    codigo = [
        linea
        for tipo, lineas in celdas
        if tipo == "CELL"
        for linea in lineas
        if linea.strip() and not _es_comentario(linea)
    ]
    if len(codigo) > MAX_LINEAS_CODIGO_NOTEBOOK:
        yield Hallazgo(_relativa(contenido, raiz), 1, "FW009", f"{len(codigo)} líneas")


# --------------------------------------------------------------------------- items de Fabric


def revisar_platform(ruta: Path, raiz: Path, vistos: dict[str, str]) -> Iterator[Hallazgo]:
    rel = _relativa(ruta, raiz)
    carpeta = ruta.parent.name
    nombre, _, tipo = carpeta.rpartition(".")
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        meta, config = datos["metadata"], datos["config"]
    except (json.JSONDecodeError, KeyError) as exc:
        yield Hallazgo(rel, 1, "FW005", f"no se puede leer: {exc}")
        return
    if meta.get("type") != tipo or meta.get("displayName") != nombre:
        yield Hallazgo(rel, 1, "FW005", f"carpeta {carpeta}, metadata {meta.get('displayName')}.{meta.get('type')}")
    if tipo == "Lakehouse" and not RE_LAKEHOUSE.match(nombre):
        yield Hallazgo(rel, 1, "FW008", nombre)

    logical_id = str(config.get("logicalId", ""))
    try:
        valido = uuid.UUID(logical_id).int != 0
    except ValueError:
        valido = False
    if not valido:
        yield Hallazgo(rel, 1, "FW006", f"'{logical_id}'")
    elif logical_id in vistos:
        yield Hallazgo(rel, 1, "FW006", f"repetido en {vistos[logical_id]}")
    else:
        vistos[logical_id] = rel


# --------------------------------------------------------------------------- orquestación


def revisar(raiz: Path = RAIZ, rutas: list[Path] | None = None) -> list[Hallazgo]:
    raiz = raiz.resolve()
    if rutas:
        objetivos = {p.resolve() for p in rutas}
        # Un fichero de un item de Fabric implica revisar el item entero y la unicidad global de logicalId
        if any("fabric" in p.parts for p in objetivos):
            objetivos |= {p.resolve() for p in (raiz / "fabric").rglob("*")}
    else:
        objetivos = {p.resolve() for carpeta in CARPETAS_REVISADAS for p in (raiz / carpeta).rglob("*")}

    hallazgos: list[Hallazgo] = []
    vistos: dict[str, str] = {}
    for ruta in sorted(objetivos):
        if not ruta.is_file() or "__pycache__" in ruta.parts:
            continue
        if ruta.suffix == ".py":
            hallazgos += revisar_python(ruta, raiz)
        if ruta.name == ".platform":
            hallazgos += revisar_platform(ruta, raiz, vistos)
            if ruta.parent.name.endswith(".Notebook"):
                hallazgos += revisar_notebook(ruta.parent, raiz)
    return hallazgos


if __name__ == "__main__":
    argumentos = [Path(a) for a in sys.argv[1:]]
    encontrados = revisar(RAIZ, argumentos or None)
    for h in encontrados:
        print(h)
    print(f"{len(encontrados)} incumplimientos del framework" if encontrados else "Framework: sin incumplimientos")
    sys.exit(1 if encontrados else 0)

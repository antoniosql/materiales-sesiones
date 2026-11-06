"""Tests del linter del framework sobre un repositorio mínimo construido en tmp_path."""

import json
import uuid
from pathlib import Path

import pytest

from scripts.lint_framework import revisar

PARAMETROS = 'entorno = "dev"\nworkspace_datos = "proyecto-datos-dev"\n'


def _notebook(raiz: Path, nombre: str, codigo: str = "x = 1\n", parametros: str = PARAMETROS, logical_id=None):
    carpeta = raiz / "fabric" / "ingenieria" / f"{nombre}.Notebook"
    carpeta.mkdir(parents=True)
    plataforma = {
        "metadata": {"type": "Notebook", "displayName": nombre},
        "config": {"version": "2.0", "logicalId": logical_id or str(uuid.uuid4())},
    }
    (carpeta / ".platform").write_text(json.dumps(plataforma), encoding="utf-8")
    contenido = (
        "# Fabric notebook source\n\n"
        f"# PARAMETERS CELL ********************\n\n{parametros}\n"
        f"# CELL ********************\n\n{codigo}"
    )
    (carpeta / "notebook-content.py").write_text(contenido, encoding="utf-8")
    return carpeta


def _reglas(raiz: Path) -> list[str]:
    return sorted(h.regla for h in revisar(raiz))


@pytest.fixture
def raiz(tmp_path):
    (tmp_path / "src").mkdir()
    return tmp_path


def test_notebook_correcto_no_tiene_hallazgos(raiz):
    _notebook(raiz, "nb_20_silver_estandarizar")
    assert _reglas(raiz) == []


@pytest.mark.parametrize(
    ("codigo", "regla"),
    [
        ('df = spark.read.load("abfss://ws@onelake.dfs.fabric.microsoft.com/lh.Lakehouse/Tables/t")\n', "FW001"),
        ("%pip install requests\n", "FW002"),
        ("filas = df.collect()\n", "FW003"),
        ("pdf = df.toPandas()\n", "FW003"),
        ('workspace_id = "0b1c2d3e-4f50-6172-8394-a5b6c7d8e9f0"\n', "FW010"),
    ],
)
def test_reglas_de_codigo_en_notebooks(raiz, codigo, regla):
    _notebook(raiz, "nb_20_silver_estandarizar", codigo)
    assert _reglas(raiz) == [regla]


def test_collect_con_limit_esta_permitido(raiz):
    _notebook(raiz, "nb_20_silver_estandarizar", "muestra = df.limit(10).collect()\n")
    assert _reglas(raiz) == []


def test_ignorar_regla_en_una_linea(raiz):
    _notebook(raiz, "nb_20_silver_estandarizar", "p = df.collect()  # fwk: ignore FW003 -- 12 filas\n")
    assert _reglas(raiz) == []


@pytest.mark.parametrize("nombre", ["Notebook1", "nb_20_gold_ventas", "nb_15_silver_x"])
def test_nombres_de_notebook_fuera_de_convencion(raiz, nombre):
    _notebook(raiz, nombre)
    assert "FW004" in _reglas(raiz)


def test_parametros_obligatorios(raiz):
    _notebook(raiz, "nb_10_bronze_ingesta", parametros='fuente = "x"\n')
    assert _reglas(raiz) == ["FW007"]


def test_demasiada_logica_en_el_notebook(raiz):
    _notebook(raiz, "nb_30_gold_ventas", "".join(f"x{i} = {i}\n" for i in range(30)))
    assert _reglas(raiz) == ["FW009"]


def test_platform_incoherente_con_la_carpeta(raiz):
    carpeta = _notebook(raiz, "nb_10_bronze_ingesta")
    datos = json.loads((carpeta / ".platform").read_text())
    datos["metadata"]["displayName"] = "otro_nombre"
    (carpeta / ".platform").write_text(json.dumps(datos))
    assert _reglas(raiz) == ["FW005"]


def test_logical_id_repetido_y_a_ceros(raiz):
    repetido = str(uuid.uuid4())
    _notebook(raiz, "nb_10_bronze_ingesta", logical_id=repetido)
    _notebook(raiz, "nb_20_silver_estandarizar", logical_id=repetido)
    _notebook(raiz, "nb_30_gold_ventas", logical_id="00000000-0000-0000-0000-000000000000")
    assert _reglas(raiz) == ["FW006", "FW006"]


def test_lakehouse_fuera_de_convencion(raiz):
    carpeta = raiz / "fabric" / "datos" / "Bronze.Lakehouse"
    carpeta.mkdir(parents=True)
    plataforma = {
        "metadata": {"type": "Lakehouse", "displayName": "Bronze"},
        "config": {"logicalId": str(uuid.uuid4())},
    }
    (carpeta / ".platform").write_text(json.dumps(plataforma))
    assert _reglas(raiz) == ["FW008"]


def test_rutas_abfss_solo_en_los_modulos_autorizados(raiz):
    (raiz / "src" / "datafwk").mkdir()
    (raiz / "src" / "datafwk" / "rutas.py").write_text('BASE = "abfss://{ws}@onelake"\n')
    (raiz / "src" / "datafwk" / "otro.py").write_text('BASE = "abfss://{ws}@onelake"\n')
    assert [h.ruta for h in revisar(raiz)] == ["src/datafwk/otro.py"]


def test_el_repositorio_cumple_el_framework():
    assert [str(h) for h in revisar()] == []

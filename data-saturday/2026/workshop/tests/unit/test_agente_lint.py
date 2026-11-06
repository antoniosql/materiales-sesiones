"""Tests del linter para agentes: qué se revisa en cada fichero y cómo responde al hook de Claude Code."""

import io
import json
import shutil

import pytest

from scripts import agente_lint
from scripts.agente_lint import main, planificar


def _nombres(rel: str) -> list[str]:
    return [p.nombre for p in planificar(rel)]


@pytest.mark.parametrize(
    ("rel", "esperado"),
    [
        ("src/datafwk/rutas.py", ["ruff --fix", "ruff format", "ruff", "mypy", "framework"]),
        ("scripts/desplegar.py", ["ruff --fix", "ruff format", "ruff", "framework"]),
        ("tests/unit/test_x.py", ["ruff --fix", "ruff format", "ruff"]),
        (
            "fabric/ingenieria/nb_10_bronze_ingesta.Notebook/notebook-content.py",
            ["ruff --fix", "ruff", "framework"],  # sin formatear: Fabric reescribe los notebooks
        ),
        ("fabric/ingenieria/nb_10_bronze_ingesta.Notebook/.platform", ["framework"]),
        ("contracts/silver/pedidos.yml", ["yamllint", "esquema", "contratos", "catálogo"]),
        ("config/fuentes/ventas.yml", ["yamllint", "esquema", "contratos"]),
        (".github/workflows/ci.yml", ["yamllint", "actionlint", "zizmor"]),
        ("sql/ops/reconciliacion.sql", ["sqlfluff fix", "sqlfluff"]),
        ("infra/main.tf", ["terraform fmt"]),
        ("templates/test/test_plantilla.py", []),
        ("README.md", []),
    ],
)
def test_planificar(rel, esperado):
    assert _nombres(rel) == esperado


def test_cada_contrato_usa_su_esquema():
    comando = next(p.comando for p in planificar("contracts/gold/fact_x.yml") if p.nombre == "esquema")
    assert "schemas/contrato.schema.json" in comando


def test_fichero_fuera_del_repositorio_se_ignora(tmp_path, monkeypatch, capsys):
    fuera = tmp_path / "fuera.py"
    fuera.write_text("x = y\n")
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"tool_input": {"file_path": str(fuera)}})))
    assert main(["--hook-claude"]) == 0


@pytest.fixture
def repo(tmp_path, monkeypatch):
    if shutil.which("ruff") is None:
        pytest.skip("ruff no está instalado")
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\nline-length = 120\n")
    (tmp_path / "pkg").mkdir()
    monkeypatch.setattr(agente_lint, "RAIZ", tmp_path)
    return tmp_path


def test_hook_devuelve_errores_al_agente(repo, monkeypatch, capsys):
    fichero = repo / "pkg" / "malo.py"
    fichero.write_text("def f():\n    return valor_inexistente\n")
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"tool_input": {"file_path": str(fichero)}})))
    assert main(["--hook-claude"]) == 2
    error = capsys.readouterr().err
    assert "F821" in error
    assert "Corrígelos ahora" in error


def test_hook_avisa_cuando_corrige_solo(repo, monkeypatch, capsys):
    fichero = repo / "pkg" / "feo.py"
    fichero.write_text("import os\nx=1\n")  # import sin usar y formato: ambos se corrigen solos
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"tool_input": {"file_path": str(fichero)}})))
    assert main(["--hook-claude"]) == 0
    salida = json.loads(capsys.readouterr().out)
    assert "Vuelve a leerlo" in salida["hookSpecificOutput"]["additionalContext"]
    assert fichero.read_text() == "x = 1\n"


def test_modo_cli_falla_con_errores(repo, capsys):
    fichero = repo / "pkg" / "malo.py"
    fichero.write_text("y = z\n")
    assert main([str(fichero)]) == 1
    assert "F821" in capsys.readouterr().out

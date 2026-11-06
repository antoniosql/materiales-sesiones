"""AGENTS.md describe exactamente las reglas que comprueban los linters."""

from scripts.lint_framework import REGLAS
from scripts.sincronizar_agents import AGENTS, sincronizar


def test_agents_al_dia():
    actual = AGENTS.read_text(encoding="utf-8")
    assert actual == sincronizar(actual), "ejecuta python scripts/sincronizar_agents.py"


def test_todas_las_reglas_fw_estan_documentadas():
    texto = AGENTS.read_text(encoding="utf-8")
    assert all(f"| {codigo} |" in texto for codigo in REGLAS)

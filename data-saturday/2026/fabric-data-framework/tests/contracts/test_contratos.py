"""Los contratos y la configuración del repositorio son válidos y el catálogo está al día."""

from scripts.generar_catalogo import DESTINO, generar
from scripts.validar_contratos import validar


def test_contratos_y_fuentes_validos():
    assert validar() == []


def test_catalogo_al_dia():
    assert DESTINO.read_text(encoding="utf-8") == generar(), "ejecuta python scripts/generar_catalogo.py"

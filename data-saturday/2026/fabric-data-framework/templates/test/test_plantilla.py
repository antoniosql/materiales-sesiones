"""Copiar a tests/unit/test_<modulo>.py. Un test por comportamiento, con nombre que lo explique."""

import pytest

# from datafwk.<modulo> import <funcion>

pytestmark = pytest.mark.spark  # quitar si la función no usa Spark


def test_<comportamiento_esperado>(spark):
    df = spark.createDataFrame(
        [("<valor>",)],
        ["<columna>"],
    )
    resultado = df  # <funcion>(df)
    assert resultado.count() == 1


def test_<caso_limite_o_error>(spark):
    ...

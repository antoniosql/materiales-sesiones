"""Las plantillas, una vez rellenas, cumplen los esquemas y las referencias cruzadas.

templates/ está fuera de los linters porque contiene marcadores: este test evita que se desfase.
"""

import json
import re
from pathlib import Path

import jsonschema
import pytest
import yaml

from scripts.validar_contratos import validar

RAIZ = Path(__file__).resolve().parents[2]
VALORES = {
    "dominio": "dominio",
    "fuente": "entidad",
    "tabla": "entidad",
    "dimension": "dim_entidad",
    "atributo": "categoria",
    "expresion_sql": "importe_algo >= 0",
}
GOLD_TIPO1 = {
    "contrato/dimension-tipo1.yml": "contracts/gold/dim_entidad.yml",
    "modelo/modelo-tipo1.yml": "config/modelos/dim_entidad.yml",
}
GOLD_SCD2 = {
    "contrato/dimension-scd2.yml": "contracts/gold/dim_entidad.yml",
    "contrato/dimension-actual.yml": "contracts/gold/dim_entidad_actual.yml",
    "modelo/modelo-scd2.yml": "config/modelos/dim_entidad.yml",
}


def rellenar(texto: str) -> str:
    sin_comentarios = re.sub(r"(?m)^\s*#.*$|\s+#.*$", "", texto)
    return re.sub(
        r"<([^<>\n]*)>",
        lambda m: VALORES.get(
            m[1], m[1].replace("-", "_") if re.fullmatch(r"[a-z0-9_-]+", m[1]) else "Texto de la plantilla"
        ),
        sin_comentarios,
    )


def esquema_de(destino: str) -> dict:
    tipo = {"contracts": "contrato", "fuentes": "fuentes", "modelos": "modelo"}
    nombre = tipo[destino.split("/")[0]] if destino.startswith("contracts") else tipo[destino.split("/")[1]]
    return json.loads((RAIZ / f"schemas/{nombre}.schema.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("fuente", "gold"),
    [("fuente/fuentes-ficheros.yml", GOLD_TIPO1), ("fuente/fuentes-sql.yml", GOLD_SCD2)],
)
def test_plantillas_rellenas_son_validas(tmp_path, fuente, gold):
    ficheros = {
        "contrato/contrato.yml": "contracts/silver/entidad.yml",
        fuente: "config/fuentes/dominio.yml",
        **gold,
    }
    for origen, destino in ficheros.items():
        texto = rellenar((RAIZ / "templates" / origen).read_text(encoding="utf-8"))
        jsonschema.validate(yaml.safe_load(texto), esquema_de(destino))
        salida = tmp_path / destino
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(texto, encoding="utf-8")
    assert validar(tmp_path) == []

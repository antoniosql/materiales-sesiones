from pathlib import Path

import pytest
import yaml

from datafwk.arranque import cargar_contexto, raiz_configuracion

ENTORNO = {
    "nombre": "dev",
    "workspace_datos": "proyecto-datos-dev",
    "lakehouses": {"bronze": "lh_bronze", "silver": "lh_silver", "gold": "lh_gold"},
}
FUENTES = {
    "dominio": "negocio",
    "fuentes": {
        "entidades": {
            "formato": "csv",
            "ruta_landing": "landing/negocio/entidades/",
            "clave_negocio": ["id_entidad"],
            "contrato": "contracts/silver/entidades.yml",
        }
    },
}
COLUMNAS = {"id_entidad": {"tipo": "string", "nulo": False}, "ciudad": {"tipo": "string"}}


def contrato(tabla: str, capa: str, clave: str, **extra: object) -> dict:
    base = {"tabla": tabla, "capa": capa, "dominio": "negocio", "propietario": "@equipo", "descripcion": "Prueba"}
    return {**base, "clave": [clave], "columnas": {**COLUMNAS, clave: {"tipo": "string", "nulo": False}}, **extra}


@pytest.fixture
def proyecto(tmp_path: Path) -> Path:
    ficheros = {
        "config/entornos/dev.yml": ENTORNO,
        "config/fuentes/negocio.yml": FUENTES,
        "config/modelos/dim_entidad.yml": {
            "modelo": "dim_entidad",
            "dominio": "negocio",
            "origen": "entidades",
            "contrato": "contracts/gold/dim_entidad.yml",
            "clave_negocio": ["id_entidad"],
            "columnas": ["id_entidad", "ciudad"],
            "historificacion": {
                "tipo": "scd2",
                "columnas": ["ciudad"],
                "columnas_tipo1": [],
                "vigencia": "observacion",
            },
            "tabla_actual": "dim_entidad_actual",
            "contrato_actual": "contracts/gold/dim_entidad_actual.yml",
        },
        "contracts/silver/entidades.yml": contrato("entidades", "silver", "id_entidad"),
        "contracts/gold/dim_entidad.yml": contrato("dim_entidad", "gold", "id_version", clave_negocio=["id_entidad"]),
        "contracts/gold/dim_entidad_actual.yml": contrato("dim_entidad_actual", "gold", "id_entidad"),
    }
    for relativa, datos in ficheros.items():
        ruta = tmp_path / relativa
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(yaml.safe_dump(datos), encoding="utf-8")
    return tmp_path


def test_raiz_configuracion_en_onelake():
    assert raiz_configuracion("proyecto-datos-test") == (
        "abfss://proyecto-datos-test@onelake.dfs.fabric.microsoft.com/lh_bronze.Lakehouse/Files/_framework"
    )


def test_contexto_desde_una_carpeta_local(proyecto):
    ctx = cargar_contexto("dev", "proyecto-datos-dev", "negocio", raiz=str(proyecto))
    assert ctx.entorno.nombre == "dev"
    assert set(ctx.fuentes) == {"entidades"}
    contrato_fuente = ctx.contrato("entidades")
    assert contrato_fuente.clave == ("id_entidad",)
    assert contrato_fuente.politica_rechazo == "cuarentena"


def test_contexto_carga_modelo_y_ambos_contratos_desde_lector(proyecto):
    def lector(ruta):
        return (proyecto / ruta.removeprefix("config-publicada/")).read_text(encoding="utf-8")

    ctx = cargar_contexto("dev", "<workspace>", "negocio", raiz="config-publicada", lector=lector)
    assert ctx.modelo("dim_entidad").columnas_scd2 == ("ciudad",)
    assert ctx.contrato_modelo("dim_entidad").clave == ("id_version",)
    assert ctx.contrato_modelo("dim_entidad", actual=True).clave == ("id_entidad",)

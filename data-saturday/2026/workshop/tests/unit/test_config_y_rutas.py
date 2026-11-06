import pytest

from datafwk import rutas
from datafwk.auditoria import Ejecucion
from datafwk.config import Entorno, cargar_fuentes
from datafwk.errores import ConfiguracionInvalida

ENTORNO = Entorno.desde_dict(
    {
        "nombre": "dev",
        "workspace_datos": "proyecto-datos-dev",
        "lakehouses": {"bronze": "lh_bronze", "silver": "lh_silver", "gold": "lh_gold"},
    }
)


def test_rutas_de_tabla_y_ficheros():
    assert rutas.tabla(ENTORNO, "silver", "pedidos") == (
        "abfss://proyecto-datos-dev@onelake.dfs.fabric.microsoft.com/lh_silver.Lakehouse/Tables/pedidos"
    )
    assert rutas.ficheros(ENTORNO, "bronze", "/landing/ventas/").endswith("lh_bronze.Lakehouse/Files/landing/ventas")
    assert rutas.cuarentena(ENTORNO, "silver", "pedidos").endswith("/Tables/_cuarentena_pedidos")


def test_rutas_con_esquema():
    con_esquema = Entorno(**{**ENTORNO.__dict__, "esquema": "dbo"})
    assert rutas.tabla(con_esquema, "gold", "fact_x").endswith("lh_gold.Lakehouse/Tables/dbo/fact_x")


def test_capa_desconocida():
    with pytest.raises(ConfiguracionInvalida):
        rutas.tabla(ENTORNO, "platino", "x")


def test_modo_de_carga_invalido():
    fuente = {"formato": "csv", "ruta_landing": "x", "clave_negocio": ["id"], "contrato": "c.yml"}
    with pytest.raises(ConfiguracionInvalida, match="modo_carga"):
        cargar_fuentes({"dominio": "d", "fuentes": {"f": {**fuente, "modo_carga": "upsert"}}})


def test_ejecucion_que_no_reconcilia():
    from datetime import datetime, timezone

    e = Ejecucion("b", "dev", "silver", "f", "t", datetime.now(timezone.utc), filas_leidas=10, filas_escritas=8)
    assert e.cerrar().estado == "no_reconcilia"

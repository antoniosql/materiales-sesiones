"""Casos de aceptación de configuración y extracción evolutiva."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from datafwk.config import ConexionSql, Extraccion, Modelo, OrigenSql, cargar_fuentes
from datafwk.errores import ConfiguracionInvalida
from datafwk.incremental import Intervalo, planificar
from datafwk.origenes.archivos import aplicar_ventana
from datafwk.origenes.sql import consulta

AHORA = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)


def fuente_sql():
    return cargar_fuentes(
        {
            "dominio": "negocio",
            "fuentes": {
                "clientes": {
                    "clave_negocio": ["id_cliente"],
                    "contrato": "contracts/silver/clientes.yml",
                    "origen_sql": {
                        "conexion": "origen",
                        "esquema": "negocio",
                        "tabla": "entidad",
                        "columnas": {"id_origen": "id_cliente", "city": "ciudad", "updated_at": "fecha_cambio"},
                    },
                    "extraccion": {"modo": "completa", "columna_marca": "updated_at"},
                }
            },
        }
    )["clientes"]


def test_completa_siembra_limite_y_incremental_solapa():
    completa = planificar(Extraccion(), AHORA)
    assert completa.desde is None
    assert completa.hasta == AHORA - timedelta(seconds=5)
    incremental = planificar(
        Extraccion(modo="incremental", columna_marca="updated_at"), AHORA + timedelta(minutes=1), completa.hasta
    )
    assert incremental.desde == AHORA - timedelta(seconds=10)
    assert incremental.hasta == AHORA + timedelta(seconds=55)


def test_incremental_sin_baseline_y_marca_futura_fallan():
    with pytest.raises(ConfiguracionInvalida, match="completa"):
        planificar(Extraccion(modo="incremental", columna_marca="updated_at"), AHORA)
    with pytest.raises(ConfiguracionInvalida, match="futuro"):
        planificar(Extraccion(), AHORA, AHORA + timedelta(seconds=1))


def test_sql_completa_e_incremental_filtran_en_origen():
    fuente = fuente_sql()
    texto = consulta(fuente, planificar(fuente.extraccion, AHORA))
    assert "FROM [negocio].[entidad] WHERE [updated_at] <=" in texto
    assert "[id_origen] AS [id_cliente]" in texto
    assert " >= " not in texto
    fuente = replace(fuente, extraccion=replace(fuente.extraccion, modo="incremental"))
    assert "[updated_at] >=" in consulta(fuente, planificar(fuente.extraccion, AHORA, AHORA - timedelta(minutes=1)))


@pytest.mark.parametrize(
    ("campo", "valor"), [("tabla", "x]; DROP TABLE x"), ("esquema", "dbo.x"), ("columnas", {"city": "_batch_id"})]
)
def test_sql_no_acepta_identificadores_inyectados(campo, valor):
    datos = {"conexion": "origen", "esquema": "negocio", "tabla": "entidad", "columnas": {"city": "ciudad"}}
    datos[campo] = valor
    with pytest.raises(ConfiguracionInvalida):
        OrigenSql.desde_dict(datos)


def test_conexion_no_acepta_opciones_jdbc_inyectadas():
    with pytest.raises(ConfiguracionInvalida):
        ConexionSql.desde_dict({"servidor": "server;password=x", "base": "base"})


def test_modelo_exige_clasificar_todos_los_atributos():
    with pytest.raises(ConfiguracionInvalida, match="clasificar"):
        Modelo.desde_dict(
            {
                "modelo": "dim_cliente",
                "dominio": "negocio",
                "origen": "clientes",
                "contrato": "contracts/gold/dim_cliente.yml",
                "clave_negocio": ["id_cliente"],
                "columnas": ["id_cliente", "ciudad", "nombre"],
                "historificacion": {"tipo": "scd2", "columnas": ["ciudad"]},
            }
        )


@pytest.mark.spark
def test_ventana_csv_limites_y_marcas_invalidas(spark):
    def instante(n):
        return datetime(2026, 1, 1, 0, 0, n, tzinfo=timezone.utc)

    intervalo = Intervalo(instante(5), instante(10), instante(15))
    df = spark.createDataFrame([(str(n), instante(n).isoformat()) for n in [4, 5, 10, 11]], "id string, marca string")
    resultado = aplicar_ventana(df, Extraccion("incremental", "marca"), intervalo)
    assert {fila.id for fila in resultado.limit(10).collect()} == {"5", "10"}
    assert aplicar_ventana(df, Extraccion(), intervalo) is df
    for marca in (None, "no es fecha"):
        with pytest.raises(ConfiguracionInvalida, match="inválidas"):
            aplicar_ventana(
                spark.createDataFrame([(marca,)], "marca string"), Extraccion(columna_marca="marca"), intervalo
            )
    with pytest.raises(ConfiguracionInvalida, match="No existe"):
        aplicar_ventana(df, Extraccion(columna_marca="ausente"), intervalo)

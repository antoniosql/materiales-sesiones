import csv
import io
import json
import shutil
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import jsonschema
import pytest
import yaml

from datafwk.calidad import aplicar_contrato
from datafwk.config import Extraccion, cargar_contrato, cargar_fuentes
from datafwk.datos_laboratorio import NULO, cambiar_ciudad, candidatos_calidad, defectos
from datafwk.errores import ConfiguracionInvalida
from datafwk.incremental import Intervalo
from datafwk.origenes.archivos import aplicar_ventana
from scripts._entorno_local import leer, obligatorio
from scripts.crear_proyecto import crear
from scripts.exportar_datos import celda, escribir_partes, linea
from scripts.laboratorio import checkpoint, configurar
from scripts.modificar_csv import leer_csv, modificar, preparar, verificar

RAIZ = Path(__file__).resolve().parents[2]


def test_mutaciones_puras_idempotentes_y_claves():
    filas = [{"id_linea_devolucion": str(i), "importe_reembolso": "12.30", "motivo": "válido"} for i in range(5)]
    ids = candidatos_calidad(filas)
    cambios = defectos(filas, ids)
    assert cambios == defectos(cambios, ids)
    assert cambios[4] == filas[4]
    assert filas[0]["importe_reembolso"] == "12.30"
    assert cambios[1]["importe_reembolso"] == NULO
    with pytest.raises(ValueError, match="cuatro"):
        candidatos_calidad(filas[:3])
    with pytest.raises(ValueError, match="distintas"):
        defectos(filas, ["1"] * 4)
    with pytest.raises(ValueError, match="Faltan"):
        defectos(filas, ["1", "2", "3", "9"])
    clientes = [{"id_cliente": "1", "ciudad": "A", "fecha_cambio": "ayer"}]
    assert cambiar_ciudad(clientes, "1", "B", "hoy")[0]["fecha_cambio"] == "hoy"
    assert clientes[0]["ciudad"] == "A"
    with pytest.raises(ValueError, match="exactamente"):
        cambiar_ciudad(clientes, "2", "B", "hoy")


def test_csv_preserva_null_vacio_comillas_saltos_y_decimal(tmp_path):
    valores = [None, "", 'a,"b"\nc', Decimal("123456789123456.78")]
    assert next(csv.reader(io.StringIO(linea(valores).decode()))) == [NULO, "", 'a,"b"\nc', "123456789123456.78"]
    with pytest.raises(ValueError, match="Colisión"):
        celda(NULO)
    resultado = escribir_partes(tmp_path, "tabla", ["texto"], [("a" * 450000,), ("b" * 450000,)])
    assert resultado["filas"] == 2
    assert len(resultado["partes"]) == 2


def test_env_no_expande_secretos_y_config_publica_no_los_copia(tmp_path):
    fichero = tmp_path / ".env"
    fichero.write_text('PROYECTO=demo\nENTORNO=dev\nSECRETO="${NO_EXPANDIR}"\n', encoding="utf-8")
    datos = leer(fichero)
    assert datos["SECRETO"] == "${NO_EXPANDIR}"
    with pytest.raises(ValueError, match="Completa"):
        obligatorio(datos, "WS_ING_ID")
    (tmp_path / "config/entornos").mkdir(parents=True)
    (tmp_path / "fabric/ingenieria").mkdir(parents=True)
    shutil.copy2(RAIZ / "fabric/ingenieria/parameter.yml", tmp_path / "fabric/ingenieria/parameter.yml")
    configurar(datos, tmp_path)
    assert "SECRETO" not in (tmp_path / "config/entornos/dev.yml").read_text()
    assert "demo-datos-dev" in (tmp_path / "fabric/ingenieria/parameter.yml").read_text()


def test_checkpoint_csv_cumple_schema_y_evoluciona(tmp_path):
    shutil.copytree(RAIZ / "templates", tmp_path / "templates")
    checkpoint("base", tmp_path)
    schema = json.loads((RAIZ / "schemas/fuentes.schema.json").read_text())
    for paso in ("base", "incremental"):
        checkpoint(paso, tmp_path)
        datos = yaml.safe_load((tmp_path / "config/fuentes/crm.yml").read_text())
        jsonschema.validate(datos, schema)
        fuente = cargar_fuentes(datos)["clientes_crm"]
        assert fuente.formato == "csv"
        assert fuente.extraccion.columna_marca == "fecha_cambio"
    checkpoint("calidad", tmp_path)
    assert yaml.safe_load((tmp_path / "contracts/silver/lineas_devolucion.yml").read_text())["version"] == 2


def test_generador_incluye_ejemplo_alumno_excluye_privados_y_mutaciones(tmp_path):
    origen = tmp_path / "base"
    origen.mkdir()
    for nombre in (".env.alumno.example", ".env.alumno", ".env.instructor", ".env.instructor.example"):
        (origen / nombre).write_text("marcador", encoding="utf-8")
    (origen / "data/laboratorio").mkdir(parents=True)
    (origen / "data/laboratorio/ejemplo.csv").write_text("mutado", encoding="utf-8")
    destino = tmp_path / "nuevo"
    assert crear(destino, "demo", origen) == 1
    assert (destino / ".env.alumno.example").is_file()


def test_volcado_real_preparacion_mutacion_y_restauracion(tmp_path):
    shutil.copytree(RAIZ / "data/original", tmp_path / "original")
    escenario = preparar(tmp_path)
    ruta = tmp_path / "laboratorio/lineas_devolucion.csv"
    inicial = ruta.read_bytes()
    modificar(tmp_path, "defectos")
    assert ruta.read_bytes() != inicial
    modificar(tmp_path, "ciudad", "Barcelona")
    modificar(tmp_path, "restaurar")
    assert ruta.read_bytes() == inicial
    clientes = leer_csv(tmp_path / "laboratorio/clientes_crm.csv")
    cliente = next(f for f in clientes if f["id_cliente"] == escenario["cliente"])
    assert cliente["ciudad"] == escenario["ciudad_original"]
    verificar(tmp_path)


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


@pytest.mark.spark
def test_csv_real_cuatro_defectos_y_contratos_q1_q2(spark, tmp_path):
    from scripts.modificar_csv import guardar_csv, originales

    manifiesto = json.loads((RAIZ / "data/original/manifest.json").read_text(encoding="utf-8"))
    filas = originales(RAIZ / "data", manifiesto)["lineas_devolucion"]
    ruta = tmp_path / "devoluciones.csv"
    guardar_csv(ruta, defectos(filas, candidatos_calidad(filas)))
    df = spark.read.options(header="true", nullValue=NULO, multiLine="true", escape='"').csv(str(ruta))
    for checkpoint_nombre, esperado in [("01_base", (387, 10)), ("02_calidad", (358, 39))]:
        contrato = cargar_contrato(
            str(RAIZ / "templates/workshop" / checkpoint_nombre / "contracts/silver/lineas_devolucion.yml")
        )
        aceptadas, rechazadas = aplicar_contrato(df, contrato)
        assert (aceptadas.count(), rechazadas.count()) == esperado

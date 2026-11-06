from pathlib import Path

from datafwk.arranque import cargar_contexto, raiz_configuracion

REPO = Path(__file__).resolve().parents[2]


def test_raiz_configuracion_en_onelake():
    assert raiz_configuracion("proyecto-datos-test") == (
        "abfss://proyecto-datos-test@onelake.dfs.fabric.microsoft.com/lh_bronze.Lakehouse/Files/_framework"
    )


def test_contexto_desde_la_configuracion_del_repo():
    ctx = cargar_contexto("dev", "proyecto-datos-dev", "ventas", raiz=str(REPO))
    assert ctx.entorno.nombre == "dev"
    assert set(ctx.fuentes) == {"pedidos", "clientes"}
    contrato = ctx.contrato("pedidos")
    assert contrato.clave == ("id_pedido",)
    assert contrato.politica_rechazo == "cuarentena"


def test_contexto_carga_modelo_y_ambos_contratos_desde_lector():
    def lector(ruta):
        relativa = ruta.removeprefix("config-publicada/")
        for base in (REPO / "templates/workshop/05_scd2", REPO / "templates/workshop/01_base", REPO):
            if (base / relativa).is_file():
                return (base / relativa).read_text(encoding="utf-8")
        raise FileNotFoundError(ruta)

    ctx = cargar_contexto("dev", "<workspace>", "crm", raiz="config-publicada", lector=lector)
    assert ctx.modelo("dim_cliente").columnas_scd2 == ("ciudad",)
    assert ctx.contrato_modelo("dim_cliente").clave == ("id_version",)
    assert ctx.contrato_modelo("dim_cliente", actual=True).clave == ("id_cliente",)

"""Única fuente de rutas de OneLake. Ningún notebook escribe una ruta abfss:// a mano."""

from __future__ import annotations

from datafwk.config import CAPAS, Entorno
from datafwk.errores import ConfiguracionInvalida

_ONELAKE = "abfss://{workspace}@onelake.dfs.fabric.microsoft.com/{lakehouse}.Lakehouse"


def raiz_lakehouse(entorno: Entorno, capa: str) -> str:
    if capa not in CAPAS:
        raise ConfiguracionInvalida(f"capa '{capa}' no es una de {CAPAS}")
    return _ONELAKE.format(workspace=entorno.workspace_datos, lakehouse=entorno.lakehouses[capa])


def tabla(entorno: Entorno, capa: str, nombre: str) -> str:
    prefijo = f"Tables/{entorno.esquema}" if entorno.esquema else "Tables"
    return f"{raiz_lakehouse(entorno, capa)}/{prefijo}/{nombre}"


def ficheros(entorno: Entorno, capa: str, ruta_relativa: str) -> str:
    return f"{raiz_lakehouse(entorno, capa)}/Files/{ruta_relativa.strip('/')}"


def configuracion(entorno: Entorno, ruta_relativa: str) -> str:
    """Ruta de un fichero de config/ o contracts/ publicado por el pipeline de despliegue."""
    return ficheros(entorno, "bronze", f"{entorno.ruta_config}/{ruta_relativa}")


def cuarentena(entorno: Entorno, capa: str, nombre_tabla: str) -> str:
    return tabla(entorno, capa, f"_cuarentena_{nombre_tabla}")


def auditoria(entorno: Entorno) -> str:
    return tabla(entorno, "silver", "fwk_ejecuciones")

"""Arranque de un notebook: de dos parámetros (entorno y workspace) a toda la configuración.

Los notebooks solo reciben 'entorno' y 'workspace_datos' (fabric-cicd los sustituye por entorno
con parameter.yml). Todo lo demás se lee de la configuración publicada en OneLake.
"""

from __future__ import annotations

from dataclasses import dataclass

from datafwk.config import Contrato, Entorno, Fuente, Lector, Modelo, cargar_contrato, cargar_fuentes, cargar_yaml

LAKEHOUSE_CONFIG = "lh_bronze"
CARPETA_CONFIG = "_framework"


def raiz_configuracion(workspace_datos: str) -> str:
    return (
        f"abfss://{workspace_datos}@onelake.dfs.fabric.microsoft.com/"
        f"{LAKEHOUSE_CONFIG}.Lakehouse/Files/{CARPETA_CONFIG}"
    )


@dataclass(frozen=True)
class Contexto:
    raiz: str
    entorno: Entorno
    fuentes: dict[str, Fuente]
    lector: Lector | None = None

    def fuente(self, nombre: str) -> Fuente:
        return self.fuentes[nombre]

    def contrato(self, nombre_fuente: str) -> Contrato:
        return cargar_contrato(f"{self.raiz}/{self.fuentes[nombre_fuente].contrato}", self.lector)

    def modelo(self, nombre: str) -> Modelo:
        from datafwk.config import identificador

        return Modelo.desde_dict(cargar_yaml(f"{self.raiz}/config/modelos/{identificador(nombre)}.yml", self.lector))

    def contrato_modelo(self, nombre: str, *, actual: bool = False) -> Contrato:
        from datafwk.errores import ConfiguracionInvalida

        modelo = self.modelo(nombre)
        ruta = modelo.contrato_actual if actual else modelo.contrato
        if ruta is None:
            raise ConfiguracionInvalida("el modelo no declara contrato_actual")
        return cargar_contrato(f"{self.raiz}/{ruta}", self.lector)


def cargar_contexto(
    entorno: str,
    workspace_datos: str,
    dominio: str,
    raiz: str | None = None,
    lector: Lector | None = None,
) -> Contexto:
    """'raiz' permite apuntar a la carpeta del repositorio para ejecutar en local."""
    raiz = (raiz or raiz_configuracion(workspace_datos)).rstrip("/")
    cfg_entorno = Entorno.desde_dict(cargar_yaml(f"{raiz}/config/entornos/{entorno}.yml", lector))
    fuentes = cargar_fuentes(cargar_yaml(f"{raiz}/config/fuentes/{dominio}.yml", lector))
    return Contexto(raiz=raiz, entorno=cfg_entorno, fuentes=fuentes, lector=lector)

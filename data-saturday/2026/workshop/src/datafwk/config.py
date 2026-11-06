"""Carga y validación de la configuración: entornos, fuentes y contratos.

En Fabric la configuración no vive en el workspace: el pipeline de despliegue la publica en
OneLake (Files/_framework/ del lakehouse de bronze) y los notebooks la leen desde ahí.
En local se lee del propio repositorio.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from datafwk.errores import ConfiguracionInvalida

Lector = Callable[[str], str]

CAPAS = ("bronze", "silver", "gold")
MODOS_CARGA = ("append", "overwrite", "merge")
POLITICAS_RECHAZO = ("cuarentena", "fallar")


def identificador(valor: str) -> str:
    """Identificador técnico seguro para rutas, columnas y SQL generado."""
    if not re.fullmatch(r"_?[a-z][a-z0-9_]*", valor):
        raise ConfiguracionInvalida(f"identificador inválido: {valor!r}")
    return valor


@dataclass(frozen=True)
class ConexionSql:
    servidor: str
    base: str

    @classmethod
    def desde_dict(cls, datos: dict[str, Any]) -> ConexionSql:
        servidor = str(_obligatorio(datos, "servidor", "conexión SQL"))
        base = str(_obligatorio(datos, "base", "conexión SQL"))
        if not re.fullmatch(r"[a-zA-Z0-9.-]+", servidor) or not re.fullmatch(r"[a-zA-Z0-9_-]+", base):
            raise ConfiguracionInvalida("servidor/base SQL inválidos; no se admiten cadenas de conexión libres")
        return cls(servidor, base)

    @property
    def url(self) -> str:
        return f"jdbc:sqlserver://{self.servidor}:1433;database={self.base};encrypt=true;trustServerCertificate=false"


@dataclass(frozen=True)
class OrigenSql:
    conexion: str
    esquema: str
    tabla: str
    columnas: dict[str, str]

    @classmethod
    def desde_dict(cls, datos: dict[str, Any]) -> OrigenSql:
        columnas = dict(_obligatorio(datos, "columnas", "origen SQL"))
        for origen, destino in columnas.items():
            identificador(origen)
            identificador(destino)
            if destino.startswith("_"):
                raise ConfiguracionInvalida("SQL: los destinos con prefijo _ están reservados al framework")
        if len(set(columnas.values())) != len(columnas):
            raise ConfiguracionInvalida("SQL: dos columnas tienen el mismo destino")
        return cls(
            identificador(str(_obligatorio(datos, "conexion", "SQL"))),
            identificador(str(_obligatorio(datos, "esquema", "SQL"))),
            identificador(str(_obligatorio(datos, "tabla", "SQL"))),
            columnas,
        )


@dataclass(frozen=True)
class Extraccion:
    modo: str = "completa"
    columna_marca: str | None = None
    solape_segundos: int = 5
    estabilizacion_segundos: int = 5
    borrados: str = "no_detectar"

    @classmethod
    def desde_dict(cls, datos: dict[str, Any]) -> Extraccion:
        resultado = cls(**datos)
        if resultado.modo not in ("completa", "incremental"):
            raise ConfiguracionInvalida("extraccion.modo debe ser completa o incremental")
        if resultado.modo == "incremental" and not resultado.columna_marca:
            raise ConfiguracionInvalida("incremental necesita columna_marca")
        if resultado.columna_marca:
            identificador(resultado.columna_marca)
        if resultado.solape_segundos < 0 or resultado.estabilizacion_segundos < 0:
            raise ConfiguracionInvalida("los márgenes de extracción no pueden ser negativos")
        if resultado.borrados != "no_detectar":
            raise ConfiguracionInvalida("la marca temporal no detecta borrados físicos")
        return resultado


def _lector_por_defecto(ruta: str) -> str:
    try:
        import notebookutils  # solo existe en Fabric

        return str(notebookutils.fs.head(ruta, 10_000_000))
    except ImportError:
        return Path(ruta).read_text(encoding="utf-8")


def cargar_yaml(ruta: str, lector: Lector | None = None) -> dict[str, Any]:
    contenido = (lector or _lector_por_defecto)(ruta)
    datos = yaml.safe_load(contenido) or {}
    if not isinstance(datos, dict):
        raise ConfiguracionInvalida(f"{ruta}: se esperaba un diccionario YAML")
    return datos


def _obligatorio(datos: dict[str, Any], clave: str, contexto: str) -> Any:
    if clave not in datos or datos[clave] in (None, ""):
        raise ConfiguracionInvalida(f"{contexto}: falta '{clave}'")
    return datos[clave]


# --------------------------------------------------------------------------- entorno


@dataclass(frozen=True)
class Entorno:
    nombre: str
    workspace_datos: str
    lakehouses: dict[str, str]
    esquema: str | None = None
    ruta_config: str = "_framework"
    conexiones_sql: dict[str, ConexionSql] = field(default_factory=dict)

    @classmethod
    def desde_dict(cls, datos: dict[str, Any]) -> Entorno:
        ctx = "entorno"
        lakehouses = _obligatorio(datos, "lakehouses", ctx)
        faltan = [c for c in CAPAS if c not in lakehouses]
        if faltan:
            raise ConfiguracionInvalida(f"{ctx}: faltan lakehouses para las capas {faltan}")
        return cls(
            nombre=_obligatorio(datos, "nombre", ctx),
            workspace_datos=_obligatorio(datos, "workspace_datos", ctx),
            lakehouses=dict(lakehouses),
            esquema=datos.get("esquema"),
            ruta_config=datos.get("ruta_config", "_framework"),
            conexiones_sql={k: ConexionSql.desde_dict(v) for k, v in datos.get("conexiones_sql", {}).items()},
        )


# --------------------------------------------------------------------------- fuentes


@dataclass(frozen=True)
class Fuente:
    nombre: str
    dominio: str
    formato: str
    ruta_landing: str
    tabla_bronze: str
    tabla_silver: str
    clave_negocio: tuple[str, ...]
    contrato: str
    modo_carga: str = "merge"
    opciones_lectura: dict[str, str] = field(default_factory=dict)
    origen_sql: OrigenSql | None = None
    extraccion: Extraccion = field(default_factory=Extraccion)

    @property
    def identidad(self) -> str:
        return f"{self.dominio}.{self.nombre}"


def cargar_fuentes(datos: dict[str, Any]) -> dict[str, Fuente]:
    dominio = _obligatorio(datos, "dominio", "fuentes")
    resultado: dict[str, Fuente] = {}
    for nombre, cfg in (_obligatorio(datos, "fuentes", f"dominio {dominio}") or {}).items():
        ctx = f"fuente {dominio}.{nombre}"
        modo = cfg.get("modo_carga", "merge")
        if modo not in MODOS_CARGA:
            raise ConfiguracionInvalida(f"{ctx}: modo_carga '{modo}' no es uno de {MODOS_CARGA}")
        clave = tuple(_obligatorio(cfg, "clave_negocio", ctx))
        origen = OrigenSql.desde_dict(cfg["origen_sql"]) if "origen_sql" in cfg else None
        extraccion = Extraccion.desde_dict(cfg.get("extraccion", {}))
        if extraccion.modo == "incremental" and (modo != "merge" or (origen is None and cfg.get("formato") != "csv")):
            raise ConfiguracionInvalida(f"{ctx}: incremental requiere SQL o CSV y modo_carga merge")
        if origen and extraccion.columna_marca and extraccion.columna_marca not in origen.columnas:
            raise ConfiguracionInvalida(f"{ctx}: columna_marca debe estar en las columnas SQL proyectadas")
        if origen and not set(clave).issubset(origen.columnas.values()):
            raise ConfiguracionInvalida(f"{ctx}: la proyección SQL no incluye la clave")
        resultado[nombre] = Fuente(
            nombre=nombre,
            dominio=dominio,
            formato="sql" if origen else _obligatorio(cfg, "formato", ctx),
            ruta_landing="" if origen else _obligatorio(cfg, "ruta_landing", ctx),
            tabla_bronze=cfg.get("tabla_bronze", nombre),
            tabla_silver=cfg.get("tabla_silver", nombre),
            clave_negocio=clave,
            contrato=_obligatorio(cfg, "contrato", ctx),
            modo_carga=modo,
            opciones_lectura={k: str(v) for k, v in (cfg.get("opciones_lectura") or {}).items()},
            origen_sql=origen,
            extraccion=extraccion,
        )
    return resultado


# --------------------------------------------------------------------------- contratos


@dataclass(frozen=True)
class Columna:
    nombre: str
    tipo: str
    nulo: bool = True
    valores: tuple[Any, ...] | None = None
    descripcion: str = ""


@dataclass(frozen=True)
class Regla:
    nombre: str
    expresion: str
    descripcion: str = ""


@dataclass(frozen=True)
class Contrato:
    tabla: str
    capa: str
    dominio: str
    propietario: str
    descripcion: str
    clave: tuple[str, ...]
    columnas: tuple[Columna, ...]
    reglas: tuple[Regla, ...] = ()
    politica_rechazo: str = "cuarentena"
    version: int = 1
    clave_negocio: tuple[str, ...] = ()

    @property
    def nombres_columnas(self) -> tuple[str, ...]:
        return tuple(c.nombre for c in self.columnas)

    @classmethod
    def desde_dict(cls, datos: dict[str, Any]) -> Contrato:
        tabla = _obligatorio(datos, "tabla", "contrato")
        ctx = f"contrato {tabla}"
        capa = _obligatorio(datos, "capa", ctx)
        if capa not in CAPAS:
            raise ConfiguracionInvalida(f"{ctx}: capa '{capa}' no es una de {CAPAS}")
        politica = datos.get("politica_rechazo", "cuarentena")
        if politica not in POLITICAS_RECHAZO:
            raise ConfiguracionInvalida(f"{ctx}: politica_rechazo '{politica}' no es una de {POLITICAS_RECHAZO}")

        columnas = []
        for nombre, cfg in (_obligatorio(datos, "columnas", ctx) or {}).items():
            valores = cfg.get("valores")
            columnas.append(
                Columna(
                    nombre=nombre,
                    tipo=_obligatorio(cfg, "tipo", f"{ctx}.{nombre}"),
                    nulo=bool(cfg.get("nulo", True)),
                    valores=tuple(valores) if valores else None,
                    descripcion=cfg.get("descripcion", ""),
                )
            )
        reglas = tuple(
            Regla(
                nombre=_obligatorio(r, "nombre", f"{ctx}.reglas"),
                expresion=_obligatorio(r, "expresion", f"{ctx}.reglas"),
                descripcion=r.get("descripcion", ""),
            )
            for r in datos.get("reglas") or []
        )
        clave = tuple(_obligatorio(datos, "clave", ctx))
        desconocidas = [c for c in clave if c not in {col.nombre for col in columnas}]
        if desconocidas:
            raise ConfiguracionInvalida(f"{ctx}: la clave usa columnas que no están en el contrato: {desconocidas}")
        version = datos.get("version", 1)
        if not isinstance(version, int) or isinstance(version, bool) or version < 1:
            raise ConfiguracionInvalida(f"{ctx}: version debe ser un entero positivo")
        clave_negocio = tuple(datos.get("clave_negocio", ()))
        if not set(clave_negocio).issubset({col.nombre for col in columnas}):
            raise ConfiguracionInvalida(f"{ctx}: clave_negocio no existe en las columnas")

        return cls(
            tabla=tabla,
            capa=capa,
            dominio=_obligatorio(datos, "dominio", ctx),
            propietario=_obligatorio(datos, "propietario", ctx),
            descripcion=_obligatorio(datos, "descripcion", ctx),
            clave=clave,
            columnas=tuple(columnas),
            reglas=reglas,
            politica_rechazo=politica,
            version=version,
            clave_negocio=clave_negocio,
        )


def cargar_contrato(ruta: str, lector: Lector | None = None) -> Contrato:
    return Contrato.desde_dict(cargar_yaml(ruta, lector))


@dataclass(frozen=True)
class Modelo:
    modelo: str
    dominio: str
    origen: str
    contrato: str
    clave_negocio: tuple[str, ...]
    columnas: tuple[str, ...]
    tipo: str = "tipo1"
    columnas_scd2: tuple[str, ...] = ()
    columnas_tipo1: tuple[str, ...] = ()
    tabla_actual: str | None = None
    contrato_actual: str | None = None

    @classmethod
    def desde_dict(cls, datos: dict[str, Any]) -> Modelo:
        historia = datos.get("historificacion", {})
        resultado = cls(
            modelo=identificador(str(_obligatorio(datos, "modelo", "modelo"))),
            dominio=identificador(str(_obligatorio(datos, "dominio", "modelo"))),
            origen=identificador(str(_obligatorio(datos, "origen", "modelo"))),
            contrato=str(_obligatorio(datos, "contrato", "modelo")),
            clave_negocio=tuple(_obligatorio(datos, "clave_negocio", "modelo")),
            columnas=tuple(_obligatorio(datos, "columnas", "modelo")),
            tipo=historia.get("tipo", "tipo1"),
            columnas_scd2=tuple(historia.get("columnas", ())),
            columnas_tipo1=tuple(historia.get("columnas_tipo1", ())),
            tabla_actual=datos.get("tabla_actual"),
            contrato_actual=datos.get("contrato_actual"),
        )
        for columna in (*resultado.columnas, *resultado.clave_negocio):
            identificador(columna)
        if not set(resultado.clave_negocio).issubset(resultado.columnas):
            raise ConfiguracionInvalida("modelo: clave_negocio ausente en columnas")
        if len(set(resultado.columnas)) != len(resultado.columnas):
            raise ConfiguracionInvalida("modelo: columnas repetidas")
        if resultado.tipo not in ("tipo1", "scd2"):
            raise ConfiguracionInvalida("modelo: tipo de historificación desconocido")
        if historia.get("vigencia", "observacion") != "observacion":
            raise ConfiguracionInvalida("solo se admite historia por observación")
        if resultado.tipo == "scd2":
            historicas, tipo1, claves = map(
                set, (resultado.columnas_scd2, resultado.columnas_tipo1, resultado.clave_negocio)
            )
            if not historicas or historicas & tipo1 or (historicas | tipo1) & claves:
                raise ConfiguracionInvalida("modelo: atributos SCD2/tipo1 vacíos o solapados")
            if historicas | tipo1 | claves != set(resultado.columnas):
                raise ConfiguracionInvalida("modelo: hay atributos sin clasificar")
            if not resultado.tabla_actual or not resultado.contrato_actual:
                raise ConfiguracionInvalida("SCD2 necesita tabla_actual y contrato_actual")
            identificador(resultado.tabla_actual)
            if resultado.tabla_actual == resultado.modelo:
                raise ConfiguracionInvalida("la proyección actual y la histórica deben ser distintas")
        return resultado

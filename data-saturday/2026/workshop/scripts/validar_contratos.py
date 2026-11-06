"""Valida todos los contratos y la configuración de fuentes. Lo ejecutan pre-commit y CI.

Comprueba que cada contrato se puede cargar, que cada fuente apunta a un contrato que existe
y que la clave de negocio de la fuente coincide con la clave del contrato.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from datafwk.config import Contrato, Modelo, cargar_fuentes, cargar_yaml  # noqa: E402 -- añade src antes del import
from datafwk.errores import ConfiguracionInvalida  # noqa: E402


def validar(raiz: Path = RAIZ) -> list[str]:
    errores: list[str] = []
    contratos: dict[str, Contrato] = {}
    fuentes_por_tabla = {}

    for ruta in sorted((raiz / "contracts").rglob("*.yml")):
        relativa = ruta.relative_to(raiz).as_posix()
        try:
            contrato = Contrato.desde_dict(cargar_yaml(str(ruta)))
        except ConfiguracionInvalida as exc:
            errores.append(f"{relativa}: {exc}")
            continue
        if contrato.capa != ruta.parent.name:
            errores.append(f"{relativa}: capa '{contrato.capa}' no coincide con la carpeta '{ruta.parent.name}'")
        if contrato.tabla != ruta.stem:
            errores.append(f"{relativa}: tabla '{contrato.tabla}' no coincide con el nombre del fichero")
        contratos[relativa] = contrato

    for ruta in sorted((raiz / "config" / "fuentes").glob("*.yml")):
        relativa = ruta.relative_to(raiz).as_posix()
        try:
            fuentes = cargar_fuentes(cargar_yaml(str(ruta)))
        except ConfiguracionInvalida as exc:
            errores.append(f"{relativa}: {exc}")
            continue
        for fuente in fuentes.values():
            fuentes_por_tabla[(fuente.dominio, fuente.tabla_silver)] = fuente
            contrato = contratos.get(fuente.contrato)
            if contrato is None:
                aviso = f"la fuente '{fuente.nombre}' apunta a un contrato inexistente: {fuente.contrato}"
                errores.append(f"{relativa}: {aviso}")
            elif tuple(fuente.clave_negocio) != contrato.clave:
                errores.append(f"{relativa}: la clave de '{fuente.nombre}' no coincide con la de su contrato")
            elif fuente.tabla_silver != contrato.tabla or contrato.capa != "silver":
                errores.append(f"{relativa}: tabla_silver/capa no coincide con el contrato")

    for ruta in sorted((raiz / "config" / "modelos").glob("*.yml")):
        relativa = ruta.relative_to(raiz).as_posix()
        try:
            modelo = Modelo.desde_dict(cargar_yaml(str(ruta)))
        except ConfiguracionInvalida as exc:
            errores.append(f"{relativa}: {exc}")
            continue
        fuente = fuentes_por_tabla.get((modelo.dominio, modelo.origen))
        contrato = contratos.get(modelo.contrato)
        if fuente is None:
            errores.append(f"{relativa}: origen silver no declarado como fuente")
        else:
            entrada = contratos.get(fuente.contrato)
            if entrada and not set(modelo.columnas).issubset(entrada.nombres_columnas):
                errores.append(f"{relativa}: columnas ausentes en el contrato silver")
            if modelo.clave_negocio != fuente.clave_negocio:
                errores.append(f"{relativa}: clave_negocio distinta de la fuente silver")
        if modelo.modelo != ruta.stem:
            errores.append(f"{relativa}: modelo y nombre de fichero no coinciden")
        if contrato is None or contrato.capa != "gold" or contrato.tabla != modelo.modelo:
            errores.append(f"{relativa}: contrato gold ausente o incorrecto")
            continue
        esperadas = set(modelo.columnas)
        if modelo.tipo == "scd2":
            esperadas |= {"id_version", "vigente_desde", "vigente_hasta", "es_actual", "_hash_scd2", "_batch_id"}
            if contrato.clave != ("id_version",) or contrato.clave_negocio != modelo.clave_negocio:
                errores.append(f"{relativa}: SCD2 exige clave id_version y clave_negocio explícita")
            actual = contratos.get(modelo.contrato_actual or "")
            if (
                actual is None
                or actual.capa != "gold"
                or actual.tabla != modelo.tabla_actual
                or actual.clave != modelo.clave_negocio
                or set(actual.nombres_columnas) != set(modelo.columnas)
            ):
                errores.append(f"{relativa}: contrato de proyección actual ausente o incompatible")
        elif contrato.clave != modelo.clave_negocio:
            errores.append(f"{relativa}: clave tipo1 distinta de la clave de negocio")
        if set(contrato.nombres_columnas) != esperadas:
            errores.append(f"{relativa}: columnas gold distintas de la salida declarada")

    return errores


if __name__ == "__main__":
    encontrados = validar()
    for e in encontrados:
        print(f"ERROR {e}")
    print(f"{len(encontrados)} errores" if encontrados else "Contratos y fuentes válidos")
    sys.exit(1 if encontrados else 0)

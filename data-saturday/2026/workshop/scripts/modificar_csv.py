"""Prepara, modifica o restaura los dos CSV de trabajo; conserva data/original intacto."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from datafwk.datos_laboratorio import NULO, cambiar_ciudad, candidatos_calidad, defectos

MAPAS = {
    "clientes_crm": ("crm.customer", {"customer_id": "id_cliente", "city": "ciudad", "updated_at": "fecha_cambio"}),
    "lineas_devolucion": (
        "returns.return_line",
        {"return_line_id": "id_linea_devolucion", "refund_amount": "importe_reembolso", "return_reason": "motivo"},
    ),
}


def leer_csv(ruta):
    with ruta.open(encoding="utf-8", newline="") as fichero:
        return list(csv.DictReader(fichero))


def guardar_csv(ruta, filas):
    temporal = ruta.with_suffix(".tmp")
    with temporal.open("w", encoding="utf-8", newline="") as fichero:
        escritor = csv.DictWriter(fichero, fieldnames=list(filas[0]), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)
    temporal.replace(ruta)


def verificar(raiz):
    manifiesto = json.loads((raiz / "original/manifest.json").read_text(encoding="utf-8"))
    for grupo in ("sql", "cosmos"):
        for nombre, entrada in manifiesto[grupo].items():
            total = 0
            for parte in entrada["partes"]:
                ruta = raiz / "original" / parte["ruta"]
                if hashlib.sha256(ruta.read_bytes()).hexdigest() != parte["sha256"]:
                    raise ValueError(f"El volcado original ha cambiado: {ruta}")
                filas = leer_csv(ruta)
                if len(filas) != parte["filas"]:
                    raise ValueError(f"Recuento incoherente: {ruta}")
                if grupo == "cosmos" and any(json.loads(f["documento_json"])["id"] != f["id"] for f in filas):
                    raise ValueError(f"JSON incoherente: {nombre}")
                total += len(filas)
            if total != entrada["filas"]:
                raise ValueError(f"Recuento total incoherente: {nombre}")
    return manifiesto


def originales(raiz, manifiesto):
    resultado = {}
    for nombre, (tabla, mapa) in MAPAS.items():
        resultado[nombre] = [
            {destino: fila[origen] for origen, destino in mapa.items()}
            for parte in manifiesto["sql"][tabla]["partes"]
            for fila in leer_csv(raiz / "original" / parte["ruta"])
        ]
    return resultado


def preparar(raiz):
    manifiesto = verificar(raiz)
    destino = raiz / "laboratorio"
    if destino.exists():
        raise ValueError("Ya existe data/laboratorio; usa restaurar para recuperar los datos sin borrar estado Delta")
    tablas = originales(raiz, manifiesto)
    clientes = sorted(tablas["clientes_crm"], key=lambda f: f["id_cliente"])
    cliente = next(f for f in clientes if f["ciudad"] not in (NULO, "", "Barcelona", "Valencia"))
    escenario = {
        "cliente": cliente["id_cliente"],
        "ciudad_original": cliente["ciudad"],
        "devoluciones": candidatos_calidad(tablas["lineas_devolucion"]),
        "filas": {nombre: len(filas) for nombre, filas in tablas.items()},
    }
    destino.mkdir(parents=True)
    for nombre, filas in tablas.items():
        guardar_csv(destino / f"{nombre}.csv", filas)
    (destino / "escenario.json").write_text(
        json.dumps(escenario, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return escenario


def modificar(raiz, accion, ciudad=None):
    manifiesto = verificar(raiz)
    destino = raiz / "laboratorio"
    escenario = json.loads((destino / "escenario.json").read_text(encoding="utf-8"))
    instante = datetime.now(timezone.utc).isoformat()
    if accion == "defectos":
        ruta = destino / "lineas_devolucion.csv"
        guardar_csv(ruta, defectos(leer_csv(ruta), escenario["devoluciones"]))
    elif accion == "ciudad":
        if not ciudad or ciudad == NULO:
            raise ValueError("Indica --valor con una ciudad no vacía")
        ruta = destino / "clientes_crm.csv"
        guardar_csv(ruta, cambiar_ciudad(leer_csv(ruta), escenario["cliente"], ciudad, instante))
    elif accion == "restaurar":
        tablas = originales(raiz, manifiesto)
        tablas["clientes_crm"] = cambiar_ciudad(
            tablas["clientes_crm"], escenario["cliente"], escenario["ciudad_original"], instante
        )
        for nombre, filas in tablas.items():
            guardar_csv(destino / f"{nombre}.csv", filas)
    return escenario


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accion", choices=["preparar", "verificar", "defectos", "ciudad", "restaurar"])
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--valor")
    args = parser.parse_args()
    if args.accion == "verificar":
        verificar(args.data)
        print("Volcado íntegro: hashes, recuentos y documentos JSON correctos.")
    else:
        escenario = preparar(args.data) if args.accion == "preparar" else modificar(args.data, args.accion, args.valor)
        print(json.dumps(escenario, ensure_ascii=False, indent=2))
        print("CSV locales listos. Publica datos y espera al menos 6 segundos antes de ejecutar bronze.")


if __name__ == "__main__":
    main()

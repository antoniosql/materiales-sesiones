"""Volcado de lectura SQL/Cosmos a CSV UTF-8, con manifiesto y partes menores de 1 MiB."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import struct
import subprocess
import time
from datetime import date, datetime, timezone
from pathlib import Path

from scripts._entorno_local import leer, obligatorio

NULO = "\\N"


def celda(valor):
    if valor is None:
        return NULO
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    if isinstance(valor, bytes):
        return "0x" + valor.hex()
    resultado = str(valor)
    if resultado == NULO:
        raise ValueError("Colisión con el marcador NULL; no se exporta de forma ambigua")
    return resultado


def linea(valores):
    salida = io.StringIO(newline="")
    csv.writer(salida, lineterminator="\n").writerow([celda(v) for v in valores])
    return salida.getvalue().encode("utf-8")


def escribir_partes(raiz, relativa, columnas, filas):
    carpeta = raiz / relativa
    carpeta.mkdir(parents=True)
    cabecera = linea(columnas)
    partes, bloque, cantidad, total = [], bytearray(cabecera), 0, 0

    def guardar():
        nombre = carpeta / f"part-{len(partes) + 1:04d}.csv"
        nombre.write_bytes(bloque)
        partes.append(
            {
                "ruta": nombre.relative_to(raiz).as_posix(),
                "filas": cantidad,
                "sha256": hashlib.sha256(bloque).hexdigest(),
            }
        )

    for fila in filas:
        registro = linea(fila)
        if len(registro) + len(cabecera) > 900_000:
            raise ValueError(f"Una fila supera el tamaño permitido: {relativa}")
        if len(bloque) + len(registro) > 900_000:
            guardar()
            bloque, cantidad = bytearray(cabecera), 0
        bloque.extend(registro)
        cantidad += 1
        total += 1
    guardar()
    return {"columnas": columnas, "filas": total, "partes": partes}


def exportar_sql(datos, raiz):
    import mssql_python
    from azure.identity import AzureCliCredential

    cadena = datos.get("SQL_SOURCE_CONNECTION_STRING") or (
        f"Server={obligatorio(datos, 'SQL_SOURCE_SERVER')};"
        f"Database={obligatorio(datos, 'SQL_SOURCE_DATABASE')};Encrypt=yes;TrustServerCertificate=no;"
    )
    token = (
        AzureCliCredential(tenant_id=obligatorio(datos, "AZURE_TENANT_ID"))
        .get_token("https://database.windows.net/.default")
        .token.encode("utf-16-le")
    )
    conexion = None
    for intento in range(8):
        try:
            conexion = mssql_python.connect(
                cadena, attrs_before={1256: struct.pack("<I", len(token)) + token}, timeout=60
            )
            break
        except mssql_python.OperationalError:
            if intento == 7:
                raise RuntimeError(
                    "SQL no accesible tras reintentos; comprueba estado, permisos Entra y firewall"
                ) from None
            print(f"SQL no disponible; reintento {intento + 1}/8", flush=True)
            time.sleep(15)
    tablas = {}
    with conexion:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT s.name,t.name FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id "
            "WHERE t.is_ms_shipped=0 ORDER BY s.name,t.name"
        )
        nombres = list(cursor.fetchall())
        for esquema, tabla in nombres:
            if esquema == "app" or (esquema, tabla) == ("lab", "identity_ground_truth"):
                continue

            def seguro(valor):
                return "[" + valor.replace("]", "]]") + "]"

            cursor.execute(f"SELECT * FROM {seguro(esquema)}.{seguro(tabla)}")  # noqa: S608 -- nombres del catálogo, delimitados y escapados
            columnas = [c[0] for c in cursor.description]

            def filas():
                while lote := cursor.fetchmany(500):
                    yield from lote

            tablas[f"{esquema}.{tabla}"] = escribir_partes(raiz, f"sql/{esquema}/{tabla}", columnas, filas())
            print(f"SQL {esquema}.{tabla}: {tablas[f'{esquema}.{tabla}']['filas']}", flush=True)
    return tablas


def exportar_cosmos(datos, raiz):
    from azure.cosmos import CosmosClient

    clave = datos.get("COSMOS_SOURCE_READONLY_KEY")
    if not clave:
        az = shutil.which("az")
        if not az:
            raise RuntimeError("Instala Azure CLI para obtener la clave de solo lectura")
        resultado = subprocess.run(  # noqa: S603 -- Azure CLI localizado, argumentos separados y sin shell
            [
                az,
                "cosmosdb",
                "keys",
                "list",
                "--subscription",
                obligatorio(datos, "AZURE_SUBSCRIPTION_ID"),
                "-g",
                obligatorio(datos, "AZURE_RESOURCE_GROUP"),
                "-n",
                obligatorio(datos, "COSMOS_SOURCE_ACCOUNT"),
                "--type",
                "read-only-keys",
                "--query",
                "primaryReadonlyMasterKey",
                "-o",
                "tsv",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        clave = resultado.stdout.strip()
    contenedores = {}
    with CosmosClient(obligatorio(datos, "COSMOS_SOURCE_ENDPOINT"), credential=clave) as cliente:
        base = cliente.get_database_client(obligatorio(datos, "COSMOS_SOURCE_DATABASE"))
        for propiedades in base.list_containers():
            nombre = propiedades["id"]
            contenedor = base.get_container_client(nombre)
            rutas_pk = propiedades["partitionKey"]["paths"]

            def filas(contenedor=contenedor):
                for pagina in contenedor.read_all_items(max_item_count=100).by_page():
                    for documento in pagina:
                        yield (documento["id"], json.dumps(documento, ensure_ascii=False, separators=(",", ":")))
                    time.sleep(0.1)

            entrada = escribir_partes(raiz, f"cosmos/{nombre}", ["id", "documento_json"], filas())
            entrada["partition_key_paths"] = rutas_pk
            contenedores[nombre] = entrada
            print(f"Cosmos {nombre}: {entrada['filas']}", flush=True)
    return contenedores


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--destino", type=Path, default=Path("data/original"))
    args = parser.parse_args()
    if args.destino.exists():
        raise SystemExit("El destino ya existe; usa una carpeta nueva para no alterar el volcado")
    datos = leer(args.env_file)
    args.destino.mkdir(parents=True)
    manifiesto = {
        "inicio_utc": datetime.now(timezone.utc).isoformat(),
        "null": NULO,
        "exclusiones_sql": ["app.* (autenticación y sesiones)", "lab.identity_ground_truth (solución)"],
        "sql_database": obligatorio(datos, "SQL_SOURCE_DATABASE"),
        "cosmos_database": obligatorio(datos, "COSMOS_SOURCE_DATABASE"),
    }
    manifiesto["sql"] = exportar_sql(datos, args.destino)
    manifiesto["cosmos"] = exportar_cosmos(datos, args.destino)
    manifiesto["fin_utc"] = datetime.now(timezone.utc).isoformat()
    (args.destino / "manifest.json").write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Volcado terminado; manifest.json acredita que ambas exportaciones finalizaron.")


if __name__ == "__main__":
    main()

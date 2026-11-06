# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # nb_10_bronze_ingesta
# SQL o landing → bronze para una fuente declarada en `config/fuentes/<dominio>.yml`.
# 
# Este notebook **no contiene lógica**: toda vive en la librería `datafwk`, instalada en el Environment `env_fwk`.
# Bronze es append-only: guarda lo que llegó, como llegó, con `_ingested_at`, `_source` y `_batch_id`.

# PARAMETERS CELL ********************

# entorno y workspace_datos los sustituye fabric-cicd en cada entorno (ver parameter.yml)
entorno = "dev"
workspace_datos = "proyecto-datos-dev"
dominio = "ventas"
fuente = "pedidos"
batch_id = ""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from datafwk.arranque import cargar_contexto
from datafwk.ingesta import a_bronze

ctx = cargar_contexto(entorno, workspace_datos, dominio)
ejecucion = a_bronze(spark, ctx.fuente(fuente), ctx.entorno, batch_id or None)
print(f"{ejecucion.estado}: {ejecucion.filas_escritas} filas en bronze.{ejecucion.tabla} (batch {ejecucion.batch_id})")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# El batch_id es la salida del notebook: el pipeline se lo pasa a nb_20_silver_estandarizar
notebookutils.notebook.exit(ejecucion.batch_id)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

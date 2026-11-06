# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # nb_20_silver_estandarizar
# Bronze → silver: snake_case, contrato de datos, deduplicación por clave y carga según `modo_carga`.
# 
# Los rechazos quedan en `fwk_cuarentena` con dato bruto, motivos y versión del contrato.
# Reconciliación: leídas = claves aceptadas + rechazadas + observaciones consolidadas.

# PARAMETERS CELL ********************

entorno = "dev"
workspace_datos = "proyecto-datos-dev"
dominio = "ventas"
fuente = "pedidos"
batch_id = ""   # obligatorio: salida de bronze; para cambiar reglas usa nb_90_ops_revalidar

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from datafwk.arranque import cargar_contexto
from datafwk.silver import a_silver

ctx = cargar_contexto(entorno, workspace_datos, dominio)
ejecucion = a_silver(spark, ctx.fuente(fuente), ctx.contrato(fuente), ctx.entorno, batch_id or None)
print(
    f"{ejecucion.estado}: {ejecucion.filas_escritas} válidas, {ejecucion.filas_rechazadas} a cuarentena "
    f"en silver.{ejecucion.tabla}"
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

if ejecucion.estado not in ("ok", "reutilizado"):
    raise RuntimeError(f"La ejecución terminó en estado '{ejecucion.estado}'. Revisa fwk_ejecuciones.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

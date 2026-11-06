# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # nb_30_gold_dimension
# Publica el modelo configurado desde el lote silver confirmado.
#
# Contrato de salida: declarado en config/fuentes/ o config/modelos/.

# PARAMETERS CELL ********************

entorno = "dev"
workspace_datos = "proyecto-datos-dev"
dominio = "<dominio>"
fuente = "<fuente>"
modelo = "<modelo>"
batch_id = ""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from datafwk.arranque import cargar_contexto
from datafwk.gold import a_gold

ctx = cargar_contexto(entorno, workspace_datos, dominio)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

cfg = ctx.modelo(modelo)
actual = ctx.contrato_modelo(modelo, actual=True) if cfg.tipo == "scd2" else None
ejecucion = a_gold(spark, cfg, ctx.fuente(fuente), ctx.contrato_modelo(modelo), ctx.entorno, batch_id, actual)
print(ejecucion.estado)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

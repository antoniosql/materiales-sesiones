# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # nb_90_ops_revalidar
# Reevalua el estado actual de bronze con el contrato publicado, sin avanzar la marca.
#
# Contrato de salida: declarado en config/fuentes/ o config/modelos/.

# PARAMETERS CELL ********************

entorno = "dev"
workspace_datos = "proyecto-datos-dev"
dominio = "<dominio>"
fuente = "<fuente>"
batch_id = ""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from datafwk.arranque import cargar_contexto
from datafwk.silver import a_silver

ctx = cargar_contexto(entorno, workspace_datos, dominio)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

ejecucion = a_silver(spark, ctx.fuente(fuente), ctx.contrato(fuente), ctx.entorno, batch_id, revalidar=True)
print(ejecucion.estado)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

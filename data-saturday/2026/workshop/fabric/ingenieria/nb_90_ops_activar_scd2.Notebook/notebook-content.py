# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # nb_90_ops_activar_scd2
# Convierte explicitamente una dimension tipo1 en SCD2 desde el instante de activacion.
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

ejecucion = a_gold(spark, ctx.modelo(modelo), ctx.fuente(fuente), ctx.contrato_modelo(modelo),
                   ctx.entorno, batch_id, ctx.contrato_modelo(modelo, actual=True), activar_scd2=True)
print(ejecucion.estado)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

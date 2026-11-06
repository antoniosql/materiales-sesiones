# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # nb_NN_capa_proposito
# <Qué hace este notebook en una frase. Qué tabla lee y qué tabla escribe.>
#
# Contrato de salida: `contracts/<capa>/<tabla>.yml`

# PARAMETERS CELL ********************

entorno = "dev"
workspace_datos = "proyecto-datos-dev"
dominio = "<dominio>"
batch_id = ""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from datafwk.arranque import cargar_contexto

ctx = cargar_contexto(entorno, workspace_datos, dominio)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# <Llamada a la función de src/datafwk/ que hace el trabajo. Sin lógica aquí.>

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

"""datafwk: librería común del framework de ingeniería de datos y analítica en Microsoft Fabric.

Reglas de diseño:
- Las transformaciones son funciones puras sobre DataFrames: se prueban en local con Spark.
- La E/S (lectura de landing, escritura Delta, auditoría) está aislada en ingesta.py, silver.py y escritura.py.
- Ninguna ruta se escribe a mano: todas salen de rutas.py a partir de la configuración del entorno.
"""

__version__ = "0.3.0"

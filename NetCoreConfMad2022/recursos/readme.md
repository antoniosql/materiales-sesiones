# Recursos complementarios — NetCoreConf Madrid 2022

Material de apoyo de la sesión [**Segmentando mis clientes con ML.NET y Python**](../README.md). Son las demos extendidas que no caben en el tiempo de la charla: la consulta de origen, la conexión a la base de datos, el análisis RFM completo y la visualización final.

| Fichero | Descripción |
| --- | --- |
| `Consulta SQL AdevntureWorksDW17.sql` | Consulta T-SQL sobre **AdventureWorksDW2017** que extrae las ventas por cliente utilizadas como origen del análisis |
| `SQL Azure pyodbc.ipynb` | Cómo conectar desde Python a **Azure SQL / SQL Server** con `pyodbc` y cargar el resultado en un `DataFrame` |
| `Demo_Calculo_RFM_y_clustering.ipynb` | Demo centrada en el cálculo de **RFM** (recencia, frecuencia, importe) y el clustering con K-Means |
| `Demostración_Completa_Analisis_RFM_y_predicción.ipynb` | Versión ampliada: análisis RFM, segmentación y modelo de **predicción** sobre los segmentos obtenidos |
| `AdventureWorksDW2017 Machine Learning.ipynb` | Recorrido general de machine learning sobre el data warehouse de ejemplo |
| `RFM.pbix` | Informe de **Power BI** con la visualización de los segmentos RFM resultantes |

## Orden sugerido

1. `Consulta SQL AdevntureWorksDW17.sql` — entender el origen de datos.
2. `SQL Azure pyodbc.ipynb` — establecer la conexión desde Python.
3. `Demo_Calculo_RFM_y_clustering.ipynb` — construir el modelo RFM y los clusters.
4. `Demostración_Completa_Analisis_RFM_y_predicción.ipynb` — añadir la capa predictiva.
5. `RFM.pbix` — comunicar el resultado a negocio.

## Requisitos

- Acceso a una instancia con **AdventureWorksDW2017** (SQL Server local o Azure SQL) y el driver **ODBC Driver for SQL Server**.
- Python con `pyodbc`, `pandas`, `scikit-learn` y `matplotlib`.
- **Power BI Desktop** para `RFM.pbix`.

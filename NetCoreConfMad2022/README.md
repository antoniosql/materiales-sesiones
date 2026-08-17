# NetCoreConf Madrid 2022 — Segmentando mis clientes con ML.NET y Python

Materiales de la sesión **"Segmentando mis clientes con ML.NET y Python"** impartida en **NetCoreConf Madrid 2022**.

La sesión recorre un caso clásico de analítica de cliente: partir de las ventas de **AdventureWorksDW2017**, calcular un modelo **RFM** (Recencia, Frecuencia, Valor Monetario) y segmentar la base de clientes con **K-Means**, comparando dos implementaciones equivalentes: **ML.NET** (.NET) y **scikit-learn** (Python).

## Contenido

| Fichero | Descripción |
| --- | --- |
| `Segmentando mis clientes con ML.NET y Python.pdf` | Presentación de la sesión |
| `RFM AdventureWorksDW17 KMeans ML_NET.ipynb` | Cálculo de RFM y clustering K-Means con **ML.NET** (notebook .NET Interactive / C#) |
| `RFM AdventureWorksDW17 KMeans Python.ipynb` | El mismo ejercicio con **Python**: pandas + scikit-learn |
| `recursos/` | Material complementario y demos extendidas ([ver detalle](recursos/readme.md)) |
| `LICENSE` | Licencia del material |

## Cómo seguir la sesión

1. Revisar la presentación PDF para el contexto: qué es RFM y por qué segmentar clientes.
2. Ejecutar el notebook de **Python** para ver el pipeline completo (consulta → RFM → escalado → K-Means → interpretación de clusters).
3. Ejecutar el notebook de **ML.NET** para comparar cómo se resuelve lo mismo dentro del ecosistema .NET.
4. Profundizar con el material de [`recursos/`](recursos/): conexión a Azure SQL, análisis RFM completo con predicción y el informe de Power BI.

## Requisitos

- **Datos:** base de datos de ejemplo **AdventureWorksDW2017** (SQL Server o Azure SQL). La consulta de origen está en [`recursos/Consulta SQL AdevntureWorksDW17.sql`](recursos/).
- **Python:** `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `pyodbc`.
- **ML.NET:** .NET SDK con [.NET Interactive](https://github.com/dotnet/interactive) para ejecutar los notebooks de C#.
- **Power BI Desktop** para abrir `recursos/RFM.pbix`.

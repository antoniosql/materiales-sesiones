# Power BI Days Bilbao 2024 — Fabric Data Science

Materiales de la sesión **"Fabric Data Science"** impartida por Antonio Soto en el **Power BI Days de Bilbao**, junio de 2024.

La sesión recorre las capacidades de ciencia de datos e IA dentro de **Microsoft Fabric**: desde entrenar modelos sin escribir código con AutoML hasta consumir los servicios de IA preentrenados directamente sobre el lakehouse.

## Contenido

| Fichero | Descripción |
| --- | --- |
| `Power BI Days Bilbao 24 - Fabric Data Science - Antonio Soto.pdf` | Presentación de la sesión |
| `AutoML Fabric.ipynb` | Entrenamiento automatizado de modelos en Fabric con **FLAML/AutoML** y seguimiento de experimentos en MLflow |
| `Demo Churn clientes.ipynb` | Caso de **abandono de clientes (churn)**: preparación de datos, entrenamiento, evaluación y registro del modelo |
| `Prebuilt AI Services SynapseML.ipynb` | Uso de los **Prebuilt AI Services** de Fabric (análisis de sentimiento, traducción, extracción de entidades…) a través de **SynapseML** |
| `Prebuilt AI Services API REST.ipynb` | Los mismos servicios de IA consumidos directamente mediante la **API REST** |

## Requisitos

- Un **workspace de Microsoft Fabric** con capacidad asignada y un **Lakehouse** al que adjuntar los notebooks.
- Los notebooks se ejecutan sobre el runtime de Spark de Fabric; no están pensados para ejecutarse en local.
- Para los Prebuilt AI Services, la capacidad debe tener habilitados los servicios de IA del tenant.

## Orden sugerido

1. `AutoML Fabric.ipynb` — la vía rápida para obtener un modelo baseline.
2. `Demo Churn clientes.ipynb` — el caso de negocio completo de principio a fin.
3. `Prebuilt AI Services SynapseML.ipynb` y `Prebuilt AI Services API REST.ipynb` — IA lista para usar, en sus dos formas de consumo.

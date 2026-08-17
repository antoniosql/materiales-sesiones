# PyCon ES 2020 — Interpretabilidad de modelos de Machine Learning

Materiales de la sesión **"Interpretando modelos de Machine Learning con Python"**, impartida en la **PyConES 2020**.

Un modelo con buena métrica no sirve de nada si nadie entiende por qué decide lo que decide. La sesión aborda cómo abrir la caja negra usando [**InterpretML**](https://interpret.ml/), la librería de interpretabilidad de Microsoft Research.

## Contenido

| Fichero | Descripción |
| --- | --- |
| `PyConEs2020 Intepretando ML.pdf` | Presentación de la sesión |
| `Interpretabilidad_de_Modelos_con_Interpret.ipynb` | Notebook con la demo completa |

## Recorrido del notebook

1. **¿Por qué necesitamos interpretar modelos?** — motivación: confianza, regulación, depuración y sesgos.
2. **¿Por qué Interpret?** — modelos *glassbox* y explicaciones *blackbox* bajo una única API.
3. **Instalación y carga de paquetes** — `pip install interpret`.
4. **Carga del dataset y transformaciones básicas** — conjunto [Adult (UCI)](https://archive.ics.uci.edu/ml/datasets/Adult), con codificación de variables categóricas.
5. **Pipeline y entrenamiento del clasificador** — se muestra que un sistema *blackbox* incluye también el preprocesado, no solo el estimador.
6. **Evaluación del rendimiento** y **explicaciones globales y locales** del modelo, visualizadas con el dashboard interactivo de Interpret.

## Requisitos

```bash
pip install interpret pandas scikit-learn
```

El notebook está preparado para ejecutarse en Jupyter o en Google Colab.

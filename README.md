# Materiales de sesiones

Repositorio con los **materiales de las sesiones, charlas y talleres** impartidos por [Antonio Soto](https://github.com/antoniosql): presentaciones, notebooks, código de las demos y datos de ejemplo.

Cada carpeta corresponde a una sesión o evento y es autocontenida: incluye su propio README con el detalle del contenido, los requisitos y cómo reproducir las demos.

## Sesiones

| Sesión | Tema | Stack | Material |
| --- | --- | --- | --- |
| [Tenerife Summer Sessions 2026](tenerife-summer-sessions-2026/) | App inteligente de retail multicanal con datos, scoring e IA | Microsoft Fabric, PySpark, Great Expectations, Data Agent | Notebooks medallion, modelo semántico, app Rayfin, presentación |
| [MAF Workshop](maf-workshop/) | De cero a héroe con Microsoft Agent Framework: agentes, tools, MCP, RAG y orquestación multiagente | Microsoft Agent Framework, Python, GitHub Models, MCP | 6 laboratorios en notebook, base de conocimiento, datos y slides |
| [FraSoHome Agents Foundry](frasohome-agents-foundry/) | Diseño y construcción de sistemas multiagente sobre un caso retail real | Microsoft Foundry Agent Service, Python SDK | Guías portal/notebook/código, base de conocimiento, datos sintéticos |
| [AgentCamp Ponferrada](agentcamp-ponferrada/) | Sesión de agentes de IA · 🚧 *pendiente de publicar* | Python | — |
| [Data Cleaning — Caso FraSoHome](datacleaning/) | Ciclo completo de calidad del dato: ingesta → perfilado → limpieza → integración → features → ML-ready | Python, pandas, scikit-learn | 6 notebooks + 11 CSV con errores intencionales |
| [Power BI Days](pbidays/) | Recursos de las distintas ediciones de Power BI Days | Microsoft Fabric, SynapseML | [Bilbao 2024 — Fabric Data Science](pbidays/bilbao2024/) |
| [NetCoreConf Madrid 2022](NetCoreConfMad2022/) | Segmentando mis clientes con ML.NET y Python | ML.NET, Python, scikit-learn, Power BI | Notebooks RFM + K-Means, consulta SQL, informe PBIX, presentación |
| [PyCon ES 2020](PyConES2020/) | Interpretabilidad de modelos de Machine Learning | Python, InterpretML | Notebook de la demo y presentación |
| [NetCoreConf 2020 Virtual](NetCoreConf-2020-Virtual/) | Power BI Embedded desde una app propia | Python, Flask, MSAL, Power BI REST API | Aplicación Flask completa y scripts de configuración de Azure AD |

## El caso FraSoHome

Varias de las sesiones más recientes comparten el mismo hilo conductor: **FraSoHome**, una cadena **ficticia** de retail de hogar y decoración que vende en tienda física y online, con datos repartidos entre CRM, e-commerce, POS, devoluciones, pagos, catálogo y stock.

Los datos son sintéticos e incluyen **errores intencionales** (nulos, duplicados, formatos heterogéneos, claves huérfanas, anomalías) para poder trabajar de forma realista la calidad del dato. El caso se aborda desde ángulos distintos según la sesión:

- [`datacleaning/`](datacleaning/) — la limpieza y preparación del dato con pandas.
- [`tenerife-summer-sessions-2026/`](tenerife-summer-sessions-2026/) — el mismo caso llevado a una arquitectura medallion en Microsoft Fabric.
- [`frasohome-agents-foundry/`](frasohome-agents-foundry/) — agentes de IA que razonan sobre esos datos y sobre las políticas internas.

## Cómo usar el repositorio

1. Entra en la carpeta de la sesión que te interese.
2. Lee su `README.md`: describe el contenido, los requisitos y el orden recomendado.
3. Cada sesión tiene sus propias dependencias; conviene crear un entorno virtual por carpeta.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Carpetas enlazadas con `git subtree`

[`maf-workshop/`](maf-workshop/) se mantiene en su propio repositorio ([antoniosql/maf-workshop](https://github.com/antoniosql/maf-workshop)) y aquí se incorpora como **subtree**. Para traer los cambios publicados en origen:

```powershell
git subtree pull --prefix=maf-workshop https://github.com/antoniosql/maf-workshop main --squash
```

Y para enviar hacia el repositorio original los cambios hechos desde aquí:

```powershell
git subtree push --prefix=maf-workshop https://github.com/antoniosql/maf-workshop main
```

> ℹ️ Los materiales se publican tal y como se usaron en cada evento. Las versiones de librerías y servicios pueden haber cambiado desde entonces, especialmente en las sesiones más antiguas.

# Reglas para modelos semánticos e informes (workspace de analítica)

- Modelos en formato TMDL (`sm_<dominio>.SemanticModel/`), informes en PBIR (`rpt_<nombre>.Report/`).
- Los modelos leen SOLO de tablas gold (`fact_*`, `dim_*`) en modo Direct Lake. Nunca de silver.
- Nombres visibles para negocio en español y con espacios (`Ventas netas`); nombres técnicos de columnas, en snake_case.
- Cada medida lleva `description` y su definición coincide con `docs/glosario.md`. Si el glosario no la define, PREGUNTA.
- Medidas en una tabla `_Medidas`; carpetas de visualización por área de negocio.
- No crees medidas implícitas: desactiva el resumen por defecto de las columnas numéricas.

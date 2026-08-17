# Taxonomía de catálogo y reglas de SKU - FraSoHome

Fuente: `FS-KB-06_Taxonomia_Catalogo_y_Reglas_SKU_v1.2.docx`.

## 1. Objetivo

Unificar categorías, subcategorías y nomenclatura de producto para mejorar búsqueda, reporting y consistencia entre ERP, POS y E-commerce.

## 2. Estructura de categorías

## 3. Regla de naming (título comercial)

Formato recomendado:

NOMBRE_BASE + ' - ' + MATERIAL + ' - ' + COLOR + ' (' + MEDIDAS + ')'

- Ejemplo: 'Sofá Liria - Tela - Gris (220x95 cm)'.
- Evitar abreviaturas internas en el título comercial.
- Las dimensiones deben ir en cm: ancho x fondo x alto si aplica.
## 4. Estructura de SKU (ID producto)

Formato SKU FraSoHome:

## FSH-FFF-CCC-NNNN

- FSH: prefijo fijo.
- FFF: familia (MUE, DEC, EXT).
- CCC: categoría (3 letras).
- NNNN: secuencial numérico.
## 5. Atributos mínimos por producto

- Material principal
- Color principal
- Dimensiones
- Peso (kg)
- Indicador de voluminoso (Sí/No)
- Coste estándar (ERP)
- Precio recomendado (PVP)
- Estado: Activo / Descatalogado
## Tablas extraídas

### Tabla 1

| ID documento | FS-KB-06 |
| --- | --- |
| Título | Taxonomía de catálogo y reglas de naming de SKU |
| Versión | 1.2 |
| Estado | VIGENTE |
| Área propietaria | Producto + E-commerce |
| Aprobado por | Head of Product |
| Vigente desde | 01/12/2025 |
| Última revisión | 08/02/2026 |
| Sensibilidad | Uso interno |

### Tabla 2

| Familia | Categoría | Subcategorías (ejemplos) |
| --- | --- | --- |
| MUEBLES | Sofás | Chaise longue, Sofá 2 plazas, Sofá 3 plazas |
| MUEBLES | Mesas | Comedor, Centro, Auxiliar, Escritorio |
| MUEBLES | Sillas | Comedor, Oficina, Taburetes |
| MUEBLES | Dormitorio | Camas, Cabeceros, Mesitas, Armarios |
| DECORACION | Iluminación | Lámparas techo, Lámparas pie, Apliques |
| DECORACION | Textil | Cojines, Alfombras, Cortinas |
| DECORACION | Pared | Cuadros, Espejos, Relojes |
| EXTERIOR | Jardín | Mesas exterior, Sillas exterior, Tumbonas |

### Tabla 3

| Ejemplo SKU | Interpretación |
| --- | --- |
| FSH-MUE-SOF-0123 | Muebles / Sofás / secuencia 0123 |
| FSH-DEC-ILU-0456 | Decoración / Iluminación / secuencia 0456 |

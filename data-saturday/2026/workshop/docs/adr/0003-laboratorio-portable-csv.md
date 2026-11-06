# 0003 · Laboratorio portable con Fabric propio y CSV

Estado: aceptado por petición del organizador. Sustituye el requisito anterior de no utilizar CSV en la sesión.

Cada alumno aporta su propio tenant y capacidad activa de Fabric. No se ofrece ejecución guiada sin capacidad ni una
base compartida. SQL y Cosmos se exportan una vez en lectura; la edición de alumnos contiene datos de negocio sintéticos,
sin tablas de autenticación ni sesiones y sin la solución de identidad. El manifiesto declara las exclusiones.

`data/original` es inmutable. Las demos de cuatro horas usan las proyecciones CRM y devoluciones de `data/laboratorio`.
Los errores se introducen en esos CSV de origen, antes de publicarlos en landing; no en el procesamiento Spark.
El volcado Cosmos conserva cada documento JSON completo en una celda, con sus arrays y objetos anidados.

El lector CSV aplica una ventana UTC sobre `fecha_cambio`; comparte marcas, lotes y reintentos con SQL.
Lee el archivo completo y filtra filas: demuestra semántica incremental, no ahorro de lectura física ni CDC.
Solo silver confirmado avanza la marca. No detecta borrados físicos ni cambios intermedios o tardíos fuera del solape.

Los contratos existentes se reutilizan sin cambiar reglas de negocio. Los checkpoints docentes Q2/Q3/Q4 y SCD2
siguen siendo cambios de contrato explícitos que el participante aplica durante la demo.
El despliegue docente publica lakehouses y notebooks sin eliminar huérfanos ni sobrescribir el Environment manual.

Los ficheros dotenv cumplimentados quedan fuera de Git y del generador greenfield. Solo el ejemplo del alumno se copia.
Los datos públicos de entorno se proyectan a YAML; las contraseñas nunca se publican en OneLake ni en parámetros.

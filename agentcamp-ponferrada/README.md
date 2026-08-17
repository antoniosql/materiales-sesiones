# AgentCamp Ponferrada

Carpeta reservada para los materiales de la sesión impartida en **AgentCamp Ponferrada**.

## Estado

🚧 **Pendiente de contenido.** Por ahora la carpeta solo incluye la configuración base del proyecto:

- `.gitignore` — plantilla estándar de Python (entornos virtuales, `__pycache__`, notebooks, cachés de herramientas, ficheros `.env`).

## Qué se publicará aquí

Cuando el material esté disponible, esta carpeta contendrá lo habitual en las sesiones de este repositorio:

- Notebooks y código fuente de las demos.
- Datos de ejemplo necesarios para reproducirlas.
- La presentación utilizada en la sesión.
- Instrucciones de preparación del entorno.

## Cómo preparar el entorno (Python)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Nota: `requirements.txt` se añadirá junto con el resto del material.

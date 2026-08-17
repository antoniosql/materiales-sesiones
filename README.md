# 🤖 Workshop: Construyendo Agentes Inteligentes con Microsoft Agent Framework

Bienvenido al repositorio del taller práctico **"De Cero a Héroe con Microsoft Agent Framework"**.

En esta sesión, no vamos a hacer "Hello Worlds" aburridos. Vamos a trabajar en patrones que puedan ser de utilidad en el mundo empresarial para modernizar stacks tecnológicos utilizando Inteligencia Artificial Generativa

## 🎯 Objetivo del Taller

Aprenderás a construir, orquestar y desplegar sistemas multi-agente capaces de razonar, usar herramientas y tomar decisiones sobre datos empresariales.

Pasaremos por todas las fases:
1.  **Single Agent:** Tu primer bot sarcástico.
2.  **Tools & MCP:** Conectando el agente al mundo real (Clima, SQL, APIs).
3.  **RAG:** "Chat with your Data" (Manuales de empleados, políticas).
4.  **Orquestación Multi-Agente:** Creando un equipo de agentes autónomos.

---

## 🛠️ Requisitos Previos (Setup)

Para aprovechar las 4 horas de taller, es **imprescindible** que traigas tu equipo configurado con lo siguiente.

### 1. Software Necesario
Asegúrate de tener instalado:

* **[Visual Studio Code](https://code.visualstudio.com/):** Nuestro editor de código (IDE).
    * *Recomendado:* Instala la extensión de Python y Jupyter.
* **[Python 3.10 o superior](https://www.python.org/downloads/):** El lenguaje que usaremos para los scripts.
* **[Git](https://git-scm.com/downloads):** Para clonar este repositorio.
* **[Cuenta en GitHub](https://github.com/):** Necesaria para acceder a los modelos y al código.

---

### 2. 🔑 Acceso a Modelos (GitHub Models)
En este taller utilizaremos GitHub Models, que nos permite acceder a modelos potentes como GPT-4o, Phi-3 o Llama-3 directamente desde el SDK de Azure AI usando tu cuenta de GitHub (gratuito para desarrollo/pruebas).

#### Pasos para obtener tu Token de Desarrollo (PAT)
Sigue estos pasos para generar el Personal Access Token (PAT) que utilizarás para autenticar el acceso a los modelos de inferencia:

1. Inicia sesión en tu cuenta de GitHub.
2. Ve a Settings (Configuración) (generalmente accesible desde tu foto de perfil).
3. Desplázate al final del menú lateral izquierdo y haz clic en Developer settings (Configuración de desarrollador).
4. Haz clic en Personal access tokens (Tokens de acceso personal) > Tokens (classic).
5. Haz clic en el botón Generate new token > Generate new token (classic).

🛠️ Configuración del Token

* **Note:** Asígnale un nombre descriptivo, por ejemplo: DataSaturday.
* **Expiration:** Selecciona "No expiration" o "30 days" (para la duración del taller).
* **Select scopes:** No es necesario marcar scopes de repo o admin estrictamente para la inferencia, pero se recomienda marcar read:user para asegurar la autenticación básica.

Haz clic en Generate token.

### ⚠️ ¡ADVERTENCIA IMPORTANTE!

Copia el token (comienza por ghp_...) inmediatamente y guárdalo en un lugar seguro (ej. Bloc de notas). No podrás volver a verlo una vez que cierres la página.
Este token es tu contraseña de desarrollador para la API. Trátalo con máxima seguridad y nunca lo subas directamente a GitHub.

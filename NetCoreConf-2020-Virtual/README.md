# NetCoreConf 2020 Virtual — Power BI Embedded con Python y Flask

Materiales de la sesión de **NetCoreConf 2020 Virtual**: cómo embeber informes de Power BI en una aplicación web propia usando **Python + Flask** y el escenario *app owns data* (autenticación con **Service Principal**).

## Qué demuestra la demo

Una aplicación Flask mínima que:

1. Se autentica contra Azure AD con **MSAL** (Service Principal o Master User).
2. Solicita a la **API REST de Power BI** el *embed token* y la *embed URL* del informe.
3. Renderiza el informe en el navegador con el **Power BI JavaScript SDK** (`powerbi.js`).

## Contenido

```text
NetCoreConf-2020-Virtual/
├── Crear Azure AD App.ps1        # Script para registrar la aplicación en Azure AD
├── Pasos Previos.txt             # Checklist de configuración previa (workspace, permisos, API)
├── requirements.txt              # flask, requests, msal
└── powerbiembedding/
    ├── app.py                    # Aplicación Flask: `/` sirve la página y `/getembedinfo` devuelve token + URL
    ├── config.py                 # Configuración: tenant, workspace, informe, credenciales
    ├── aadservice.py             # Obtención del token de Azure AD (MSAL)
    ├── pbiembedservice.py        # Llamadas a la API REST de Power BI (embed token / embed URL)
    ├── templates/index.html      # Contenedor del informe embebido
    └── static/                   # CSS, JS (Bootstrap, jQuery, Power BI SDK) e imágenes
```

## Pasos previos

Referencia oficial: [Embed Power BI content with service principal](https://docs.microsoft.com/en-us/power-bi/developer/embedded/embed-service-principal).

1. Ejecutar `Crear Azure AD App.ps1` para registrar la aplicación en Azure AD.
2. Crear el workspace en Power BI y asignarle el Service Principal y el grupo de seguridad.
3. En el **portal de administración de Power BI**, habilitar la opción de *acceso a API para service principals*.
4. Incluir el grupo de seguridad en esa opción de administración.

## Configuración

Rellenar los valores de `powerbiembedding/config.py`:

| Campo | Descripción |
| --- | --- |
| `AUTHENTICATION_MODE` | `ServicePrincipal` o `MasterUser` |
| `WORKSPACE_ID` | Id del workspace que contiene el informe |
| `REPORT_ID` | Id del informe a embeber |
| `TENANT_ID` | Id del tenant de Azure AD (solo Service Principal) |
| `CLIENT_ID` | Application Id de la app de Azure AD |
| `CLIENT_SECRET` | Secreto de la app (solo Service Principal) |

> ⚠️ No subas secretos reales al repositorio: `config.py` se publica con los valores vacíos a propósito.

## Ejecución

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd powerbiembedding
python app.py
```

La aplicación queda disponible en `http://localhost:5000`.

"""Carga de parámetros (.env) y del escenario (config/escenario.yaml)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]


class ConfigError(RuntimeError):
    pass


def _env(name: str, default: str | None = None, required: bool = False) -> str | None:
    value = os.environ.get(name, default)
    if isinstance(value, str):
        value = value.strip().strip('"').strip("'")
        if value == "":
            value = default
    if required and not value:
        raise ConfigError(f"Falta {name} en .env")
    return value


def _path(value: str | None) -> Path | None:
    if not value:
        return None
    p = Path(value).expanduser()
    return p if p.is_absolute() else (ROOT / p)


@dataclass
class Settings:
    tenant_id: str
    tenant_domain: str
    sp_host: str
    admin_upn: str
    client_id: str
    client_secret: str | None
    cert_thumbprint: str | None
    cert_pem_key_path: Path | None
    case_data_dir: Path | None
    case_kb_dir: Path | None
    output_dir: Path
    state_dir: Path
    usage_location: str
    finanzas_group_alias: str
    label_apply_method: str
    dominio_column_mode: str
    purview_endpoint: str
    purview_api_version: str
    purview_domain_id: str | None
    copilot_chat_endpoint: str
    workiq_scope: str | None
    timezone: str
    pp_environment_id: str | None
    agent_schema_name: str
    agent_display_name: str
    agent_solution: str
    agent_template_file: Path | None
    auth_mode: str = "app"
    dry_run: bool = False
    raw: dict = field(default_factory=dict)

    @property
    def authority(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}"

    @property
    def has_certificate(self) -> bool:
        return bool(self.cert_thumbprint and self.cert_pem_key_path)

    def env(self, name: str, default: str | None = None) -> str | None:
        return _env(name, default)

    @property
    def docs_dir(self) -> Path:
        """Documentos que se suben. Por defecto, los versionados en el repo (documentos/).
        En dry-run, `semdebt documents` escribe en output/dry-run/docs para no tocar el repo."""
        if self.dry_run:
            return self.output_dir / "docs"
        return _path(_env("DOCS_DIR")) or (ROOT / "documentos")

    def doc(self, name: str) -> Path:
        """Ruta de un documento: docs_dir y, si no está (dry-run), el del repo."""
        p = self.docs_dir / name
        return p if p.exists() else ROOT / "documentos" / name

    @property
    def reports_dir(self) -> Path:
        return self.output_dir / "evaluaciones"


def load_settings(env_file: str | None = None, dry_run: bool = False, need_tenant: bool = True) -> Settings:
    env_path = Path(env_file) if env_file else ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)
    elif not dry_run and need_tenant:
        raise ConfigError(f"No encuentro {env_path}. Copia .env.example a .env y rellénalo.")

    req = not dry_run and need_tenant
    s = Settings(
        tenant_id=_env("TENANT_ID", "dry-run-tenant", required=req),
        tenant_domain=_env("TENANT_DOMAIN", "frasohome.onmicrosoft.com", required=req),
        sp_host=_env("SP_HOST", "frasohome.sharepoint.com", required=req),
        admin_upn=_env("ADMIN_UPN", "admin@frasohome.onmicrosoft.com", required=req),
        client_id=_env("CLIENT_ID", "dry-run-client", required=req and (_env("AUTH_MODE", "app") or "app").lower() == "app"),
        client_secret=_env("CLIENT_SECRET"),
        cert_thumbprint=_env("CERT_THUMBPRINT"),
        cert_pem_key_path=_path(_env("CERT_PEM_KEY_PATH")),
        case_data_dir=_path(_env("CASE_DATA_DIR")),
        case_kb_dir=_path(_env("CASE_KB_DIR")),
        output_dir=_path(_env("OUTPUT_DIR", "output")),
        state_dir=_path(_env("STATE_DIR", "state")),
        usage_location=_env("USAGE_LOCATION", "ES"),
        finanzas_group_alias=_env("FINANZAS_GROUP_ALIAS", "FS-Finanzas"),
        label_apply_method=(_env("LABEL_APPLY_METHOD", "graph") or "graph").lower(),
        dominio_column_mode=(_env("DOMINIO_COLUMN_MODE", "taxonomy") or "taxonomy").lower(),
        purview_endpoint=(_env("PURVIEW_ENDPOINT", "https://api.purview-service.microsoft.com") or "").rstrip("/"),
        purview_api_version=_env("PURVIEW_API_VERSION", "2026-03-20-preview"),
        purview_domain_id=_env("PURVIEW_DOMAIN_ID"),
        copilot_chat_endpoint=(_env("COPILOT_CHAT_ENDPOINT", "graph") or "graph").lower(),
        workiq_scope=_env("WORKIQ_SCOPE"),
        timezone=_env("TIMEZONE", "Europe/Madrid"),
        pp_environment_id=_env("PP_ENVIRONMENT_ID"),
        agent_schema_name=_env("AGENT_SCHEMA_NAME", "fs_asistenteComercial"),
        agent_display_name=_env("AGENT_DISPLAY_NAME", "Asistente Comercial FraSoHome"),
        agent_solution=_env("AGENT_SOLUTION", "FraSoHomeDemos"),
        agent_template_file=_path(_env("AGENT_TEMPLATE_FILE", "copilot-studio/asistente-comercial.template.yaml")),
        auth_mode=(_env("AUTH_MODE", "app") or "app").lower(),
        dry_run=dry_run,
    )
    if req and s.auth_mode == "app" and not (s.client_secret or s.has_certificate):
        raise ConfigError("Configura CLIENT_SECRET o CERT_THUMBPRINT + CERT_PEM_KEY_PATH en .env")
    for opt, allowed in (("label_apply_method", {"graph", "manual"}),
                         ("dominio_column_mode", {"taxonomy", "choice"}),
                         ("copilot_chat_endpoint", {"graph", "workiq"}),
                         ("auth_mode", {"app", "delegated"})):
        if getattr(s, opt) not in allowed:
            raise ConfigError(f"{opt.upper()} debe ser uno de {sorted(allowed)}")
    if dry_run:   # el dry-run nunca toca el estado ni las salidas reales
        s.output_dir, s.state_dir = s.output_dir / "dry-run", s.state_dir / "dry-run"
    s.output_dir.mkdir(parents=True, exist_ok=True)
    s.state_dir.mkdir(parents=True, exist_ok=True)
    return s


def load_scenario() -> dict:
    with open(ROOT / "config" / "escenario.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def persona_upn(settings: Settings, scenario: dict, key: str) -> str:
    if key == "admin":
        return settings.admin_upn
    p = scenario["personas"][key]
    return settings.env(p["upn_env"]) or f"{key}@{settings.tenant_domain}"

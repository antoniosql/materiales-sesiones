"""Parámetros (.env) y escenario (config/escenario.yaml)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]


@dataclass
class Settings:
    tenant_id: str
    tenant_domain: str
    admin_upn: str
    graph_client_id: str
    graph_login: str
    subscription_id: str
    resource_group: str
    location: str
    name_suffix: str
    deploy_foundry: bool
    foundry_project_endpoint: str
    foundry_project_name: str
    foundry_model: str
    foundry_model_version: str
    foundry_model_capacity: int
    foundry_shared_identity_id: str
    foundry_agent_identity_id: str
    copilot_agent_identity_id: str
    triage_poll_seconds: int
    usage_location: str
    demo_user_password: str
    ca_states: dict[str, str]
    case_data_dir: Path
    buzon_json: Path
    state_dir: Path
    escenario: dict = field(default_factory=dict)

    def upn(self, alias: str) -> str:
        return f"{alias}@{self.tenant_domain}"


def _ruta(valor: str, defecto: str) -> Path:
    p = Path(valor or defecto)
    return p if p.is_absolute() else RAIZ / p


def cargar(env_file: str | None = None) -> Settings:
    load_dotenv(env_file or RAIZ / ".env", override=False)
    e = os.environ.get
    with open(RAIZ / "config" / "escenario.yaml", encoding="utf-8") as f:
        escenario = yaml.safe_load(f)
    return Settings(
        tenant_id=e("TENANT_ID", ""),
        tenant_domain=e("TENANT_DOMAIN", ""),
        admin_upn=e("ADMIN_UPN", ""),
        graph_client_id=e("GRAPH_CLIENT_ID", "14d82eec-204b-4c2f-b7e8-296a70dab67e"),
        graph_login=e("GRAPH_LOGIN", "device"),
        subscription_id=e("SUBSCRIPTION_ID", ""),
        resource_group=e("RESOURCE_GROUP", "rg-frasohome-agents"),
        location=e("LOCATION", "swedencentral"),
        name_suffix=e("NAME_SUFFIX", ""),
        deploy_foundry=e("DEPLOY_FOUNDRY", "true").lower() == "true",
        foundry_project_endpoint=e("FOUNDRY_PROJECT_ENDPOINT", ""),
        foundry_project_name=e("FOUNDRY_PROJECT_NAME", "fs-agentes-prj"),
        foundry_model=e("FOUNDRY_MODEL", "gpt-4.1-mini"),
        foundry_model_version=e("FOUNDRY_MODEL_VERSION", "2025-04-14"),
        foundry_model_capacity=int(e("FOUNDRY_MODEL_CAPACITY", "30")),
        foundry_shared_identity_id=e("FOUNDRY_SHARED_IDENTITY_ID", ""),
        foundry_agent_identity_id=e("FOUNDRY_AGENT_IDENTITY_ID", ""),
        copilot_agent_identity_id=e("COPILOT_AGENT_IDENTITY_ID", ""),
        triage_poll_seconds=int(e("TRIAGE_POLL_SECONDS", "60")),
        usage_location=e("USAGE_LOCATION", "ES"),
        demo_user_password=e("DEMO_USER_PASSWORD", ""),
        ca_states={"CA-AG-01": e("CA_AG_01_STATE", "enabled"),
                   "CA-AG-02": e("CA_AG_02_STATE", "enabledForReportingButNotEnforced")},
        case_data_dir=_ruta(e("CASE_DATA_DIR", ""), "datos/caso"),
        buzon_json=_ruta(e("BUZON_JSON", ""), "datos/buzon/correos.json"),
        state_dir=_ruta(e("STATE_DIR", ""), "state"),
        escenario=escenario,
    )

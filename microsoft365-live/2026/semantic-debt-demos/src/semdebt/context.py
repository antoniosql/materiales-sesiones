"""Contexto compartido por todos los pasos."""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property

from . import auth
from .config import Settings, load_scenario, load_settings, persona_upn
from .http import GRAPH, GRAPH_BETA, Api
from .state import State


@dataclass
class Ctx:
    settings: Settings
    scenario: dict
    state: State
    pending: list[str] = field(default_factory=list)   # pasos manuales que quedan

    @classmethod
    def build(cls, env_file: str | None = None, dry_run: bool = False, need_tenant: bool = True) -> "Ctx":
        s = load_settings(env_file, dry_run=dry_run, need_tenant=need_tenant)
        return cls(settings=s, scenario=load_scenario(), state=State(s.state_dir / "deployed.json"))

    @cached_property
    def graph(self) -> Api:
        return Api(lambda: auth.app_token(self.settings), GRAPH, self.settings.dry_run)

    @cached_property
    def graph_beta(self) -> Api:
        return Api(lambda: auth.app_token(self.settings), GRAPH_BETA, self.settings.dry_run)

    def upn(self, key: str) -> str:
        return persona_upn(self.settings, self.scenario, key)

    def todo(self, text: str) -> None:
        self.pending.append(text)

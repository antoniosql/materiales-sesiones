"""Contexto común de los comandos: configuración, estado, credencial y resolución de nombres."""

from __future__ import annotations

from dataclasses import dataclass

from agentid.auth import Credencial
from agentid.config import Settings
from agentid.graph import Graph
from agentid.state import Estado


@dataclass
class Ctx:
    s: Settings
    estado: Estado
    credencial: Credencial

    @classmethod
    def crear(cls, s: Settings) -> "Ctx":
        return cls(s=s, estado=Estado(s.state_dir), credencial=Credencial(s))

    def graph(self, *scopes: str) -> Graph:
        return Graph(self.credencial, list(scopes))

    @property
    def esc(self) -> dict:
        return self.s.escenario

    # ---- resolución de personas y grupos -------------------------------------------------
    def usuario_id(self, clave: str) -> str:
        g = self.graph("User.ReadWrite.All")
        if clave == "admin":
            return g.get(f"users/{self.s.admin_upn}?$select=id")["id"]
        guardado = self.estado.id(f"usuario:{clave}")
        if guardado:
            return guardado
        alias = self.esc["personas"][clave]["alias"]
        return g.get(f"users/{self.s.upn(alias)}?$select=id")["id"]

    def grupo_id(self, clave: str) -> str:
        guardado = self.estado.id(f"grupo:{clave}")
        if guardado:
            return guardado
        alias = self.esc["grupos"][clave]["alias"]
        g = self.graph("Group.ReadWrite.All")
        res = g.get(f"groups?$filter=mailNickname eq '{alias}'&$select=id")["value"]
        if not res:
            raise RuntimeError(f"No existe el grupo {alias}: ejecuta `agentid personas`.")
        return res[0]["id"]

    def principal(self, ref: str) -> tuple[str, str]:
        """'marta' → ('users', id) · 'grupo:tiendas' → ('groups', id) · 'admin' → ('users', id)."""
        if ref.startswith("grupo:"):
            return "groups", self.grupo_id(ref.split(":", 1)[1])
        return "users", self.usuario_id(ref)

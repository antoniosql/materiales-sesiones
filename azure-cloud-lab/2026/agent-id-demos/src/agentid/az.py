"""Llamadas a Azure CLI y azd (ARM, ACR, Container Apps, RBAC, Storage)."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


class AzError(RuntimeError):
    pass


def _exe(nombre: str) -> str:
    ruta = shutil.which(nombre) or shutil.which(f"{nombre}.cmd")
    if not ruta:
        raise AzError(f"No encuentro «{nombre}» en el PATH.")
    return ruta


def az(*args: str, salida_json: bool = True, comprobar: bool = True) -> Any:
    cmd = [_exe("az"), *args]
    if salida_json:
        cmd += ["--output", "json"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        if not comprobar:
            return None
        raise AzError(f"az {' '.join(args[:4])}… → {r.stderr.strip()[:800]}")
    if not salida_json or not r.stdout.strip():
        return r.stdout.strip()
    return json.loads(r.stdout)


def azd(*args: str) -> str:
    r = subprocess.run([_exe("azd"), *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise AzError(f"azd {' '.join(args[:4])}… → {(r.stderr or r.stdout).strip()[:800]}")
    return r.stdout.strip()


def ambito_contenedor(storage_id: str, contenedor: str) -> str:
    return f"{storage_id}/blobServices/default/containers/{contenedor}"


def _asignaciones(principal_id: str, rol: str, ambito: str) -> list[dict]:
    # Se filtra en local: `--assignee` obliga a az a resolver el principal en Graph y con
    # identidades de agente recién creadas puede fallar.
    todas = az("role", "assignment", "list", "--scope", ambito) or []
    return [a for a in todas if a.get("principalId") == principal_id and a.get("roleDefinitionName") == rol
            and a.get("scope", "").lower() == ambito.lower()]


def asignar_rol(principal_id: str, rol: str, ambito: str) -> dict:
    existentes = _asignaciones(principal_id, rol, ambito)
    if existentes:
        return existentes[0]
    return az("role", "assignment", "create", "--assignee-object-id", principal_id,
              "--assignee-principal-type", "ServicePrincipal", "--role", rol, "--scope", ambito)


def quitar_rol(principal_id: str, rol: str, ambito: str) -> bool:
    existentes = _asignaciones(principal_id, rol, ambito)
    for a in existentes:
        az("role", "assignment", "delete", "--ids", a["id"], salida_json=False)
    return bool(existentes)


def comando_rol(principal_id: str, rol: str, ambito: str) -> str:
    return (f'az role assignment create \\\n  --assignee-object-id "{principal_id}" \\\n'
            f'  --assignee-principal-type ServicePrincipal \\\n  --role "{rol}" \\\n  --scope "{ambito}"')

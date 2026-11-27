#!/usr/bin/env bash
# Prepara el entorno de las demos (macOS / Linux): .venv, dependencias, .env y Git.
# Uso: ./setup.sh [--sin-pruebas] [--sin-git]
set -euo pipefail
cd "$(dirname "$0")"
SIN_PRUEBAS=0; SIN_GIT=0
for a in "$@"; do case "$a" in --sin-pruebas) SIN_PRUEBAS=1;; --sin-git) SIN_GIT=1;; esac; done

PY=$(command -v python3 || command -v python) || { echo "No encuentro Python 3.10+"; exit 1; }
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || { echo "Hace falta Python 3.10+"; exit 1; }

[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/python -m pip install --upgrade pip --quiet
.venv/bin/python -m pip install -e '.[foundry,dev]' --quiet
echo "✔ dependencias instaladas en .venv"

[ -f .env ] || { cp .env.example .env; echo "✔ .env creado desde .env.example"; }
grep -E '^(TENANT_ID|SUBSCRIPTION_ID|NAME_SUFFIX)=\s*$' .env >/dev/null && echo "⚠ rellena TENANT_ID, SUBSCRIPTION_ID y NAME_SUFFIX en .env" || true

[ -d .vscode ] || { mkdir .vscode && cp config/vscode/*.json .vscode/ && sed -i.bak 's#.venv/Scripts/python.exe#.venv/bin/python#' .vscode/settings.json && rm -f .vscode/settings.json.bak; echo "✔ .vscode creado"; }

if [ "$SIN_GIT" -eq 0 ] && [ ! -d .git ] && command -v git >/dev/null; then
  git init -b main >/dev/null && git add . && git commit -qm 'Demos de Entra Agent ID · Azure Cloud Lab 2026 (FraSoHome)' \
    && echo "✔ repositorio Git inicializado" || echo "⚠ git init hecho, commit pendiente"
fi

command -v az >/dev/null && echo "✔ Azure CLI" || echo "⚠ instala Azure CLI"
command -v azd >/dev/null && echo "✔ azd" || echo "⚠ azd no instalado (solo para la conexión MCP de Foundry)"

[ "$SIN_PRUEBAS" -eq 1 ] || .venv/bin/python -m pytest -q
echo -e "\nSiguiente: source .venv/bin/activate && agentid check"

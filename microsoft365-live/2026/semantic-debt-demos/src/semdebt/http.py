"""Cliente HTTP mínimo con reintentos (429/5xx) y modo dry-run."""
from __future__ import annotations

import itertools
import json
import logging
import time
from typing import Callable
from urllib.parse import quote

import requests

log = logging.getLogger(__name__)

GRAPH = "https://graph.microsoft.com/v1.0"
GRAPH_BETA = "https://graph.microsoft.com/beta"


class ApiError(RuntimeError):
    def __init__(self, method: str, url: str, status: int, body: str):
        super().__init__(f"{method} {url} -> {status}: {body[:800]}")
        self.status = status
        self.body = body


class Api:
    """Envuelve requests con token, reintentos y dry-run.

    En dry-run no se llama a nada: los GET devuelven None (no existe) y los POST
    devuelven un objeto con id ficticio, para poder recorrer el flujo completo.
    """

    _ids = itertools.count(1)

    def __init__(self, token_provider: Callable[[], str], base: str = GRAPH, dry_run: bool = False,
                 extra_headers: dict | None = None):
        self.token_provider = token_provider
        self.base = base.rstrip("/")
        self.dry_run = dry_run
        self.session = requests.Session()
        self.extra_headers = extra_headers or {}

    def url(self, path: str) -> str:
        return path if path.startswith("http") else f"{self.base}/{path.lstrip('/')}"

    def request(self, method: str, path: str, *, json_body=None, data=None, headers=None,
                ok_404: bool = False, retries: int = 6, raw: bool = False):
        url = self.url(path)
        if self.dry_run:
            shown = json.dumps(json_body, ensure_ascii=False)[:300] if json_body is not None else ""
            log.info("[dry-run] %s %s %s", method, url, shown)
            if method == "GET":
                return None
            n = next(self._ids)
            return {"id": f"dry-{n}", "webUrl": f"https://dry.run/{n}", "value": [], "messages": []}
        hdrs = {"Authorization": f"Bearer {self.token_provider()}", **self.extra_headers, **(headers or {})}
        if json_body is not None:
            hdrs.setdefault("Content-Type", "application/json")
        for attempt in range(retries):
            resp = self.session.request(method, url, headers=hdrs,
                                        data=json.dumps(json_body) if json_body is not None else data,
                                        timeout=120)
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                wait = int(resp.headers.get("Retry-After", 2 ** attempt * 2))
                log.warning("%s %s -> %s; reintento en %ss", method, url, resp.status_code, wait)
                time.sleep(min(wait, 60))
                continue
            if resp.status_code == 404 and ok_404:
                return None
            if resp.status_code >= 400:
                raise ApiError(method, url, resp.status_code, resp.text)
            if raw:
                return resp
            if not resp.content:
                return {}
            try:
                return resp.json()
            except ValueError:
                return {"_text": resp.text}
        raise ApiError(method, url, -1, "reintentos agotados")

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, body=None, **kw):
        return self.request("POST", path, json_body=body if body is not None else {}, **kw)

    def patch(self, path, body, **kw):
        return self.request("PATCH", path, json_body=body, **kw)

    def put(self, path, body=None, **kw):
        return self.request("PUT", path, json_body=body, **kw)

    def delete(self, path, **kw):
        return self.request("DELETE", path, **kw)

    def get_all(self, path) -> list[dict]:
        items, url = [], path
        while url:
            page = self.get(url)
            if not page:
                break
            items.extend(page.get("value", []))
            url = page.get("@odata.nextLink")
        return items


def q(value: str) -> str:
    """Escapa comillas simples para filtros OData."""
    return value.replace("'", "''")


def path_segment(value: str) -> str:
    return quote(value, safe="")

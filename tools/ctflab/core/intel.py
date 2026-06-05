"""
core/intel.py — extração automática de inteligência das respostas.

Toda vez que o recon faz uma requisição bem-sucedida, esse módulo
tenta extrair endpoints, campos e tokens da resposta e salva no
Session.ctx automaticamente.

Assim os outros módulos têm defaults úteis sem o usuário precisar
redigitar o que acabou de ver na tela.
"""

from __future__ import annotations

import json
import re
from typing import Any

from .session import Session

# ── padrões para extração ─────────────────────────────────────

# "POST /login", "GET /api/flag", etc (em texto/JSON)
_ENDPOINT_RE = re.compile(
    r'\b(GET|POST|PUT|PATCH|DELETE)\s+(/[\w/\-\.{}:?=&]*)',
    re.IGNORECASE,
)

# paths em HTML: href="/admin", action="/submit", fetch('/api/token')
_HTML_PATH_RE = re.compile(
    r'(?:href|action|src|data-url|fetch|axios\.(?:get|post)|url)\s*[=:(]\s*["\']'
    r'(/[^"\'>\s]{2,})["\']',
    re.IGNORECASE,
)

# campos de corpo: {"username": ..., "password": ...}
_FIELD_RE = re.compile(r'"([\w_]+)"\s*:', re.IGNORECASE)

# tokens/valores base64-like
_B64_RE = re.compile(r'[A-Za-z0-9+/]{20,}={0,2}')

# flags CTF — padrão comum + variações
_FLAG_RE = re.compile(r'(?:CTF|FLAG|HTB|picoCTF|DUCTF)\{[^}]+\}', re.IGNORECASE)

# cookies interessantes no cabeçalho Set-Cookie
_COOKIE_RE = re.compile(r'([^=;\s]+)=([^;]{4,})', re.IGNORECASE)


def _flatten_values(obj: Any) -> list[str]:
    """Extrai todos os valores string de um dict/list aninhado."""
    out: list[str] = []
    if isinstance(obj, dict):
        for v in obj.values():
            out.extend(_flatten_values(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(_flatten_values(v))
    elif isinstance(obj, str):
        out.append(obj)
    return out


def _extract_fields_from_description(text: str) -> list[str]:
    """
    Extrai nomes de campos de descrições como:
    'body: {"code": "...", "user": "..."}  → ...'
    """
    found: list[str] = []
    for match in re.finditer(r'\{[^}]+\}', text):
        try:
            obj = json.loads(match.group())
            found.extend(obj.keys())
        except Exception:
            pass
    if not found:
        found = _FIELD_RE.findall(text)
    return found


def analyze(session: Session, body: str, status: int, headers: dict | None = None) -> dict[str, Any]:
    """
    Analisa o corpo de uma resposta HTTP e atualiza session.ctx
    com o que foi descoberto.

    Retorna um dict com o que foi extraído (para exibição).
    """
    if not body.strip():
        return {}

    discovered: dict[str, Any] = {}

    try:
        data = json.loads(body)
    except Exception:
        data = {}

    all_strings = _flatten_values(data) + [body]

    # ── colheita de palavras para wordlist dinâmica ──────────
    discovered_words = set(session.recall("discovered_words", "").split(","))
    # adiciona strings curtas/médias que podem ser cupons/tokens
    for s_val in all_strings:
        if isinstance(s_val, str) and 3 < len(s_val) < 64:
            # limpa lixo comum de HTML/JSON
            if not any(c in s_val for c in "{}[]<>"):
                discovered_words.add(s_val.strip())
    
    if discovered_words:
        session.remember("discovered_words", ",".join(filter(None, discovered_words)))

    # ── endpoints em texto/JSON ───────────────────────────────
    endpoints: list[dict] = []
    seen_paths: set[str] = set()

    for s in all_strings:
        for m in _ENDPOINT_RE.finditer(s):
            method, path = m.group(1).upper(), m.group(2)
            if path in seen_paths:
                continue
            seen_paths.add(path)
            entry = {"method": method, "path": path, "fields": [], "source": "text"}
            entry["fields"] = _extract_fields_from_description(s)
            endpoints.append(entry)

    # ── endpoints em HTML ─────────────────────────────────────
    for m in _HTML_PATH_RE.finditer(body):
        path = m.group(1).split("?")[0]  # tira query string
        if path in seen_paths or len(path) < 2:
            continue
        seen_paths.add(path)
        endpoints.append({"method": "?", "path": path, "fields": [], "source": "html"})

    if endpoints:
        discovered["endpoints"] = endpoints
        for ep in endpoints:
            if ep["method"] == "POST":
                session.remember("path", ep["path"])
                if ep["fields"]:
                    session.remember("last_fields", json.dumps(ep["fields"]))
                break
        if not session.ctx.get("path"):
            session.remember("path", endpoints[0]["path"])

    # ── flags ─────────────────────────────────────────────────
    for s_val in all_strings:
        for m in _FLAG_RE.finditer(s_val):
            session.flag(m.group())
            discovered.setdefault("flags", []).append(m.group())

    # ── tokens base64 ─────────────────────────────────────────
    for s_val in all_strings:
        for m in _B64_RE.finditer(s_val):
            candidate = m.group()
            if "/" not in candidate and len(candidate) > 20:
                session.remember("token", candidate)
                discovered.setdefault("tokens", []).append(candidate)
                break

    # ── cookies do cabeçalho Set-Cookie ──────────────────────
    if headers:
        set_cookie = headers.get("set-cookie", "")
        if set_cookie:
            for m in _COOKIE_RE.finditer(set_cookie):
                name, val = m.group(1), m.group(2)
                session.remember(f"cookie_{name}", val)
                discovered.setdefault("cookies", []).append(f"{name}={val[:40]}")

    return discovered

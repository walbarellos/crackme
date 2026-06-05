#!/usr/bin/env python3
"""
CTFLab v2.1 — framework modular de pentest / CTF

Uso:
    python3 main.py
    python3 main.py --target http://exemplo.ctf:8080
    python3 main.py --load sessao.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from ctflab.core.session import Session
from ctflab.core import plugin as plugin_loader
from ctflab.cli.ui import ask, banner, console

import ctflab.modules.recon     as recon
import ctflab.modules.sqli      as sqli
import ctflab.modules.forge     as forge
import ctflab.modules.traversal as traversal
import ctflab.modules.race      as race
import ctflab.modules.idor      as idor
import ctflab.modules.utils     as utils


# ── menu principal ────────────────────────────────────────────

def build_menu(session: Session) -> dict:
    options: dict[str, tuple[str, object]] = {
        "1": ("Reconhecimento",   recon.run),
        "2": ("SQL Injection",    sqli.run),
        "3": ("Forge de Token",   forge.run),
        "4": ("Path Traversal",   traversal.run),
        "5": ("Race / Brute",     race.run),
        "6": ("IDOR / Tampering", idor.run),
        "7": ("Utilitários",      utils.run),
    }

    plugins = plugin_loader.discover()
    for i, mod in enumerate(plugins, start=8):
        options[str(i)] = (
            f"{mod.PLUGIN_NAME} [dim](plugin)[/dim]",
            mod.run,
        )

    options["0"] = ("Sair", None)
    return options


# ── loop principal ────────────────────────────────────────────

def main_loop(session: Session) -> None:
    """Loop principal com controle correto de saída."""
    from rich.table import Table

    banner(session)

    while True:
        console.rule()
        options = build_menu(session)

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="info")
        table.add_column()
        for key, (desc, _) in options.items():
            table.add_row(key, desc)
        console.print(table)
        console.print()

        op = ask("módulo")

        if op == "0":
            console.print("\n[dim]saindo...[/dim]\n")
            break

        entry = options.get(op)
        if entry is None:
            console.print("[fail]opção inválida[/fail]")
            continue

        _, handler = entry
        if handler is None:
            break

        try:
            handler(session, console)
        except KeyboardInterrupt:
            console.print("\n[warn]interrompido[/warn]")
        except Exception as exc:
            console.print(f"[fail]erro inesperado: {exc}[/fail]")


# ── CLI args ──────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="CTFLab v2.1 — framework de pentest / CTF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--target", "-t",
        default="http://localhost:1337",
        help="URL alvo (default: http://localhost:1337)",
    )
    p.add_argument(
        "--load", "-l",
        default=None,
        metavar="FILE",
        help="Carrega sessão exportada de um arquivo JSON",
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Timeout HTTP em segundos (default: 10)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.load:
        try:
            session = Session.load(args.load)
            console.print(f"[ok]sessão carregada: {args.load}[/ok]")
        except Exception as exc:
            console.print(f"[fail]erro ao carregar sessão: {exc}[/fail]")
            sys.exit(1)
    else:
        session = Session(target=args.target, timeout=args.timeout)

    try:
        main_loop(session)
    except KeyboardInterrupt:
        console.print("\n\n[dim]Ctrl+C — saindo[/dim]\n")

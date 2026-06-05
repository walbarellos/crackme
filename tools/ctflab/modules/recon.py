"""modules/recon.py"""

from __future__ import annotations

from rich.console import Console

from ctflab.core import http as H, payloads as P
from ctflab.core.session import Session
from ctflab.cli.menu import run_menu
from ctflab.cli.ui import ask, askctx, ask_json_interactive, ask_params, ask_int, show_response, scan_table


def _get_root(s: Session, c: Console) -> None:
    r = H.get(s, "/")
    show_response(r, s.history[-1].elapsed, s)


def _get_custom(s: Session, c: Console) -> None:
    path   = askctx(s, "path", "path", "/")
    params = ask_params()
    r = H.get(s, path, params or None)
    show_response(r, s.history[-1].elapsed, s)


def _post_json(s: Session, c: Console) -> None:
    path    = askctx(s, "path", "path", "/")
    payload = ask_json_interactive(c)
    if payload is not None:
        r = H.post(s, path, payload)
        show_response(r, s.history[-1].elapsed, s)


def _post_form(s: Session, c: Console) -> None:
    path   = askctx(s, "path", "path", "/")
    params = ask_params("campos (ex: user=admin&pass=123)")
    r = H.post(s, path, params, form=True)
    show_response(r, s.history[-1].elapsed, s)


from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

def _fuzz_dirs(s: Session, c: Console) -> None:
    """
    Fuzz de diretórios — testa lista de paths comuns contra o alvo de forma assíncrona.
    """
    wordlist = P.load("paths")
    extra_raw = ask("wordlist extra separada por vírgula (enter = pular)", "")
    if extra_raw:
        for p in extra_raw.split(","):
            p = p.strip()
            if p and p not in wordlist:
                wordlist.append(p)

    c.print(f"\n[warn]preparando {len(wordlist)} requisições assíncronas...[/warn]\n")

    # Executa o fuzzing via core/http.py (asyncio)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=c,
    ) as progress:
        task = progress.add_task("fuzzing caminhos", total=1)
        # O H.fuzz atual é síncrono por fora mas usa asyncio.run internamente.
        # Para mostrar progresso real, o ideal seria o H.fuzz aceitar callback,
        # mas como ele é extremamente rápido (gather), vamos apenas sinalizar início/fim.
        results_raw = H.fuzz(s, wordlist)
        progress.update(task, advance=1, description="concluído")

    table = scan_table(
        "Directory Fuzzing Results",
        ["path", "status", "tamanho", "snippet"],
    )

    hits = 0
    for path, code, size, text in results_raw:
        snippet = text.replace("\n", " ")
        
        if code == 200:
            style = "ok"
            s.remember("path", path)
        elif code in (301, 302, 307):
            style = "warn"
        elif code == 403:
            style = "info"
        elif code == 500:
            style = "fail"
        else:
            style = "dim"

        table.add_row(
            path,
            f"[{style}]{code}[/{style}]",
            str(size),
            snippet,
        )
        hits += 1
        s.note(f"dir [{code}]: {path}")

    c.print(table)
    c.print(f"\n[ok]{hits} caminho(s) interessante(s) encontrado(s)[/ok]")


def _headers_inspect(s: Session, c: Console) -> None:
    """Mostra os headers completos da resposta — útil para descobrir tech stack."""
    path = askctx(s, "path", "path", "/")
    r    = H.get(s, path)

    c.print(f"\n[info]Headers de {path}:[/info]")
    for k, v in r.headers.items():
        c.print(f"  [warn]{k}[/warn]: {v}")

    # dicas de fingerprint
    server  = r.headers.get("server", "")
    powered = r.headers.get("x-powered-by", "")
    if server:
        c.print(f"\n[info]Stack detectado:[/info] [ok]{server}[/ok]")
    if powered:
        c.print(f"[info]Powered by:[/info] [ok]{powered}[/ok]")
    c.print()


_OPTIONS = {
    "1": ("GET / — explorar endpoints",   _get_root),
    "2": ("GET customizado",              _get_custom),
    "3": ("POST com JSON",                _post_json),
    "4": ("POST como form-data",          _post_form),
    "5": ("fuzz de diretórios",           _fuzz_dirs),
    "6": ("inspecionar headers",          _headers_inspect),
    "0": ("voltar",                       None),
}


def run(session: Session, console: Console) -> None:
    run_menu("RECONHECIMENTO", _OPTIONS, session, console)

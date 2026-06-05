"""
core/http.py — camada HTTP isolada.

Todas as funções recebem Session explicitamente.
Retry com backoff exponencial. Toggle SSL. Form-data e JSON.
Last-byte synchronization para race conditions precisas.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from .session import RequestRecord, Session

# ── constantes ────────────────────────────────────────────────

_DEFAULT_RETRY = 2
_BACKOFF_BASE  = 0.3   # segundos


# ── fábrica de cliente ────────────────────────────────────────

def _make_client(session: Session) -> httpx.Client:
    return httpx.Client(
        base_url=session.target,
        headers={"Content-Type": "application/json", **session.headers},
        timeout=session.timeout,
        follow_redirects=True,
        verify=session.ssl,
    )


def _make_async_client(session: Session) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=session.target,
        headers={"Content-Type": "application/json", **session.headers},
        timeout=session.timeout,
        follow_redirects=True,
        verify=session.ssl,
    )


# ── registro ──────────────────────────────────────────────────

def _record(
    session: Session,
    method: str,
    path: str,
    payload: Any,
    r: httpx.Response,
    elapsed: float,
) -> RequestRecord:
    rec = RequestRecord(
        method=method,
        url=session.target.rstrip("/") + path,
        payload=payload,
        status=r.status_code,
        body=r.text,
        elapsed=elapsed,
    )
    session.add_record(rec)
    return rec


# ── GET / POST síncronos com retry ────────────────────────────

def get(
    session: Session,
    path: str = "/",
    params: dict | None = None,
    retries: int = _DEFAULT_RETRY,
) -> httpx.Response:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with _make_client(session) as c:
                start   = time.perf_counter()
                r       = c.get(path, params=params or {})
                elapsed = time.perf_counter() - start
            _record(session, "GET", path, params, r, elapsed)
            return r
        except httpx.RequestError as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(_BACKOFF_BASE * (2 ** attempt))
    raise last_exc  # type: ignore[misc]


def post(
    session: Session,
    path: str,
    payload: Any,
    form: bool = False,
    retries: int = _DEFAULT_RETRY,
) -> httpx.Response:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with _make_client(session) as c:
                start   = time.perf_counter()
                r       = c.post(
                    path,
                    data=payload if form else None,
                    json=None if form else payload,
                )
                elapsed = time.perf_counter() - start
            _record(session, "POST", path, payload, r, elapsed)
            return r
        except httpx.RequestError as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(_BACKOFF_BASE * (2 ** attempt))
    raise last_exc  # type: ignore[misc]


# ── disparo simultâneo assíncrono ─────────────────────────────

async def _gather_fuzz(
    session: Session,
    wordlist: list[str],
) -> list[tuple[str, int, int, str]]:
    """
    Fuzzing assíncrono de diretórios.
    Retorna lista de (path, status, size, preview).
    """
    interesting = {200, 204, 301, 302, 307, 401, 403, 405, 500}
    results = []

    async with _make_async_client(session) as c:
        # cria tasks para todos os caminhos
        tasks = []
        for path in wordlist:
            if not path.startswith("/"):
                path = "/" + path
            tasks.append(c.get(path))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    for path, r in zip(wordlist, responses):
        if isinstance(r, Exception):
            continue
        if r.status_code in interesting:
            results.append((path, r.status_code, len(r.content), r.text[:55]))
    
    return results


def fuzz(session: Session, wordlist: list[str]) -> list[tuple[str, int, int, str]]:
    """Executa o fuzzing assíncrono e retorna os resultados interessantes."""
    return asyncio.run(_gather_fuzz(session, wordlist))


async def _gather_normal(
    session: Session,
    path: str,
    payload: Any,
    n: int,
) -> list[tuple[int, str]]:
    """Disparo simultâneo simples via asyncio.gather."""
    async with _make_async_client(session) as c:
        tasks     = [c.post(path, json=payload) for _ in range(n)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    results: list[tuple[int, str]] = []
    for r in responses:
        if isinstance(r, Exception):
            results.append((-1, str(r)))
        else:
            results.append((r.status_code, r.text))
    return results


async def _gather_synchronized(
    session: Session,
    path: str,
    payload: Any,
    n: int,
) -> list[tuple[int, str]]:
    """
    Last-byte synchronization: prepara n coroutines e as libera
    ao mesmo tempo via asyncio.Event.

    Reduz jitter de rede — mais eficaz contra race conditions com
    janelas pequenas (ex: verificação de uso de cupom antes de UPDATE).
    """
    gate = asyncio.Event()

    async def worker(client: httpx.AsyncClient) -> tuple[int, str]:
        await gate.wait()
        try:
            r = await client.post(path, json=payload)
            return r.status_code, r.text
        except Exception as exc:
            return -1, str(exc)

    async with _make_async_client(session) as c:
        tasks = [asyncio.create_task(worker(c)) for _ in range(n)]
        # aguarda um tick para todas chegarem no await gate.wait()
        await asyncio.sleep(0.05)
        gate.set()  # libera todas simultaneamente
        results = await asyncio.gather(*tasks)

    return list(results)


def race(
    session: Session,
    path: str,
    payload: Any,
    n: int = 10,
    synchronized: bool = False,
) -> list[tuple[int, str]]:
    """
    Dispara n requisições simultâneas e retorna lista (status, body).

    synchronized=True usa last-byte sync — mais preciso para janelas
    de race condition muito pequenas.
    """
    if synchronized:
        return asyncio.run(_gather_synchronized(session, path, payload, n))
    return asyncio.run(_gather_normal(session, path, payload, n))

"""
core/session.py — estado da sessão de pentest.

Session é injetada explicitamente em todo módulo e função.
Nunca existe como global — isso permite múltiplas sessões,
testes unitários e futura paralelização.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RequestRecord:
    """Registro imutável de uma requisição + resposta."""

    method:    str
    url:       str
    payload:   Any
    status:    int
    body:      str
    elapsed:   float
    timestamp: str = field(default_factory=lambda: time.strftime("%H:%M:%S"))

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "method":    self.method,
            "url":       self.url,
            "payload":   self.payload,
            "status":    self.status,
            "elapsed":   round(self.elapsed, 4),
            "body":      self.body[:2000],
        }


@dataclass
class Session:
    """
    Fonte única de verdade da sessão de pentest.

    Não é singleton. Crie uma instância por contexto.
    """

    target:  str          = "http://localhost:1337"
    timeout: float        = 10.0
    ssl:     bool         = False    # False = ignora cert inválido (CTF)
    headers: dict         = field(default_factory=dict)
    history: list         = field(default_factory=list)   # list[RequestRecord]
    notes:   list[str]    = field(default_factory=list)
    flags:   list[str]    = field(default_factory=list)
    # contexto descoberto durante a sessão — alimenta defaults dos módulos
    ctx:     dict         = field(default_factory=dict)

    # ── mutações ──────────────────────────────────────────────

    def set_header(self, key: str, value: str) -> None:
        self.headers[key] = value

    def remove_header(self, key: str) -> None:
        self.headers.pop(key, None)

    def add_record(self, rec: RequestRecord) -> None:
        self.history.append(rec)

    def note(self, text: str) -> None:
        ts = time.strftime("%H:%M:%S")
        self.notes.append(f"[{ts}] {text}")

    def flag(self, value: str) -> None:
        if value not in self.flags:
            self.flags.append(value)
            self.note(f"FLAG: {value}")

    # ── contexto descoberto ───────────────────────────────────

    def remember(self, key: str, value: str) -> None:
        """Guarda um valor de contexto (path, campo, token...)."""
        self.ctx[key] = value

    def recall(self, key: str, fallback: str = "") -> str:
        """Retorna valor de contexto ou fallback."""
        return self.ctx.get(key, fallback)

    # ── persistência ──────────────────────────────────────────

    def export(self, path: str | Path = "ctflab_session.json") -> Path:
        p = Path(path)
        data = {
            "target":  self.target,
            "flags":   self.flags,
            "notes":   self.notes,
            "ctx":     self.ctx,
            "history": [r.to_dict() for r in self.history],
        }
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return p

    @classmethod
    def load(cls, path: str | Path) -> "Session":
        data = json.loads(Path(path).read_text())
        s = cls(target=data.get("target", "http://localhost:1337"))
        s.notes = data.get("notes", [])
        s.flags = data.get("flags", [])
        s.ctx   = data.get("ctx", {})
        # history é reconstruída parcialmente (só leitura)
        for r in data.get("history", []):
            s.history.append(RequestRecord(
                method=r["method"], url=r["url"],
                payload=r["payload"], status=r["status"],
                body=r["body"], elapsed=r["elapsed"],
                timestamp=r["timestamp"],
            ))
        return s

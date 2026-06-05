#!/usr/bin/env python3
"""
=== crackme_one - servidor ===
Você NÃO deve editar este arquivo.
Interaja com ele via HTTP: http://localhost:1337
"""

import hashlib
import base64
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

SECRET_TOKEN = base64.b64encode(b"unlock_me").decode()
FLAG_PARTS = [
    67,
    84,
    70,
    123,
    114,
    51,
    118,
    51,
    114,
    115,
    51,
    95,
    100,
    48,
    110,
    116,
    95,
    115,
    116,
    48,
    112,
    125,
]


def check_password(password: str) -> bool:
    h = hashlib.md5(password.encode()).hexdigest()
    return h == "0cc175b9c0f1b6a831c399e269772661"


def get_flag(token: str) -> str:
    if token != SECRET_TOKEN:
        return None
    return "".join(chr(c) for c in FLAG_PARTS)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silencia logs do servidor

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)

        # GET /  — lista os endpoints disponíveis
        if parsed.path == "/":
            self.send_json(
                200,
                {
                    "endpoints": {
                        "POST /login": 'body: {"password": "..."}  → retorna token se senha correta',
                        "POST /flag": 'body: {"token": "..."}     → retorna flag se token correto',
                    }
                },
            )

        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
        except Exception:
            self.send_json(400, {"error": "invalid json"})
            return

        parsed = urlparse(self.path)

        # POST /login
        if parsed.path == "/login":
            password = data.get("password", "")
            if check_password(password):
                token = base64.b64encode(password.encode()).decode()
                self.send_json(200, {"token": token})
            else:
                self.send_json(401, {"error": "wrong password"})

        # POST /flag
        elif parsed.path == "/flag":
            token = data.get("token", "")
            flag = get_flag(token)
            if flag:
                self.send_json(200, {"flag": flag})
            else:
                self.send_json(403, {"error": "invalid token"})

        else:
            self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    print("=== crackme_one ===")
    print("servidor rodando em http://localhost:1337")
    print("GET / para ver os endpoints disponíveis")
    print("Ctrl+C para parar\n")
    HTTPServer(("localhost", 1337), Handler).serve_forever()

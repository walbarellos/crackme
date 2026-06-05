#!/usr/bin/env python3
"""
=== crackme_four - servidor ===
Você NÃO deve editar este arquivo.
Rode: python3 server4.py
Interaja via HTTP: http://localhost:1337
"""
import json
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

FLAG = "CTF{jwt_f4k3d_l1k3_4_b0ss}"

USERS = {
    "guest": "guest123",
}

def make_token(username, role):
    payload = json.dumps({"username": username, "role": role})
    return base64.b64encode(payload.encode()).decode()

def read_token(token):
    try:
        payload = base64.b64decode(token).decode()
        return json.loads(payload)
    except Exception:
        return None

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if urlparse(self.path).path == "/":
            self.send_json(200, {
                "endpoints": {
                    "POST /login": "body: {\"username\": \"...\", \"password\": \"...\"} → retorna token",
                    "POST /flag":  "body: {\"token\": \"...\"} → retorna flag se role for admin",
                },
                "dica": "existe um usuario: guest / guest123"
            })
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        try:
            data = json.loads(body)
        except Exception:
            self.send_json(400, {"error": "invalid json"})
            return

        path = urlparse(self.path).path

        if path == "/login":
            username = data.get("username", "")
            password = data.get("password", "")
            if USERS.get(username) == password:
                token = make_token(username, "guest")
                self.send_json(200, {"token": token})
            else:
                self.send_json(401, {"error": "wrong credentials"})

        elif path == "/flag":
            token = data.get("token", "")
            payload = read_token(token)
            if not payload:
                self.send_json(400, {"error": "invalid token"})
                return
            if payload.get("role") == "admin":
                self.send_json(200, {"flag": FLAG})
            else:
                self.send_json(403, {"error": "not admin"})

        else:
            self.send_json(404, {"error": "not found"})

if __name__ == "__main__":
    print("=== crackme_four ===")
    print("servidor rodando em http://localhost:1337")
    print("GET / para ver os endpoints")
    print("Ctrl+C para parar\n")
    HTTPServer(("localhost", 1337), Handler).serve_forever()

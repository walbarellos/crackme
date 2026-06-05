#!/usr/bin/env python3
"""
=== crackme_three - servidor ===
Você NÃO deve editar este arquivo.
Rode: python3 server3.py
Interaja via HTTP: http://localhost:1337
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

FLAG = "CTF{p4th_tr4v3rs4l_1s_fun}"

BASE_DIR = "/tmp/ctf_files"

def init_files():
    os.makedirs(f"{BASE_DIR}/public", exist_ok=True)
    os.makedirs(f"{BASE_DIR}/private", exist_ok=True)
    with open(f"{BASE_DIR}/public/readme.txt", "w") as f:
        f.write("bem vindo ao sistema de arquivos publico.")
    with open(f"{BASE_DIR}/public/welcome.txt", "w") as f:
        f.write("aqui voce pode ler arquivos publicos.")
    with open(f"{BASE_DIR}/private/flag.txt", "w") as f:
        f.write(FLAG)

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
        path = urlparse(self.path).path

        if path == "/":
            self.send_json(200, {
                "endpoints": {
                    "GET /file?name=public/readme.txt": "le um arquivo da pasta public",
                }
            })
            return

        if path == "/file":
            qs = parse_qs(urlparse(self.path).query)
            name = qs.get("name", [""])[0]

            if not name:
                self.send_json(400, {"error": "missing name"})
                return

            # monta o caminho completo
            full_path = os.path.join(BASE_DIR, name)

            # so permite arquivos dentro de /public... sera que funciona?
            if not full_path.startswith(f"{BASE_DIR}/public"):
                self.send_json(403, {"error": "access denied"})
                return

            if not os.path.isfile(full_path):
                self.send_json(404, {"error": "file not found"})
                return

            with open(full_path) as f:
                content = f.read()

            self.send_json(200, {"content": content})
            return

        self.send_json(404, {"error": "not found"})

if __name__ == "__main__":
    init_files()
    print("=== crackme_three ===")
    print("servidor rodando em http://localhost:1337")
    print("GET / para ver os endpoints")
    print("Ctrl+C para parar\n")
    HTTPServer(("localhost", 1337), Handler).serve_forever()

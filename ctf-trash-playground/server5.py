#!/usr/bin/env python3
"""
=== crackme_five - servidor ===
Você NÃO deve editar este arquivo.
Rode: python3 server5.py
Interaja via HTTP: http://localhost:1337
"""
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from socketserver import ThreadingMixIn

FLAG = "CTF{r4c3_c0nd1t10n_w1ns}"

used_codes = set()
redemptions = []

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

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
                    "POST /redeem": "body: {\"code\": \"...\"} → resgata um cupom de desconto",
                },
                "cupons_validos": ["DESCONTO10", "FRETE_GRATIS"],
                "dica": "cada cupom so pode ser usado uma vez... ou pode?"
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

        if path == "/redeem":
            code = data.get("code", "")

            if code not in ["DESCONTO10", "FRETE_GRATIS"]:
                self.send_json(400, {"error": "cupom invalido"})
                return

            if code in used_codes:
                self.send_json(400, {"error": "cupom ja utilizado"})
                return

            # simula processamento demorado
            time.sleep(0.5)

            used_codes.add(code)
            redemptions.append(code)

            if len(redemptions) >= 5:
                self.send_json(200, {"message": "cupom aplicado!", "flag": FLAG})
            else:
                self.send_json(200, {"message": f"cupom aplicado! ({len(redemptions)}/5 usos registrados)"})

        else:
            self.send_json(404, {"error": "not found"})

if __name__ == "__main__":
    print("=== crackme_five ===")
    print("servidor rodando em http://localhost:1337")
    print("GET / para ver os endpoints")
    print("Ctrl+C para parar\n")
    ThreadedHTTPServer(("localhost", 1337), Handler).serve_forever()

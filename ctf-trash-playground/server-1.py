#!/usr/bin/env python3
"""
=== crackme_two - servidor ===
Você NÃO deve editar este arquivo.
Rode: python3 server2.py
Interaja via HTTP: http://localhost:1337
"""

import json
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

FLAG_PARTS = [67, 84, 70, 123, 115, 113, 108, 95, 119, 104, 52, 116, 95, 115, 113, 108, 125]


def init_db():
    con = sqlite3.connect(":memory:")
    cur = con.cursor()
    cur.execute("CREATE TABLE users (username TEXT, password TEXT, role TEXT)")
    cur.execute("INSERT INTO users VALUES ('admin', 'supersecret123', 'admin')")
    cur.execute("INSERT INTO users VALUES ('alice', 'alice123', 'user')")
    cur.execute("INSERT INTO users VALUES ('bob',   'bob123',   'user')")
    con.commit()
    return con


DB = init_db()


def query_user(username, password):
    cur = DB.cursor()
    # junta direto na query... nao tem problema ne? :)
    sql = f"SELECT role FROM users WHERE username = '{username}' AND password = '{password}'"
    cur.execute(sql)
    return cur.fetchone()


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
            self.send_json(
                200,
                {
                    "endpoints": {
                        "POST /login": 'body: {"username": "...", "password": "..."} → retorna role se credenciais corretas',
                        "POST /flag": 'body: {"role": "..."} → retorna flag se role for admin',
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

        path = urlparse(self.path).path

        if path == "/login":
            username = data.get("username", "")
            password = data.get("password", "")
            row = query_user(username, password)
            if row:
                self.send_json(200, {"role": row[0]})
            else:
                self.send_json(401, {"error": "wrong credentials"})

        elif path == "/flag":
            role = data.get("role", "")
            if role == "admin":
                flag = "".join(chr(c) for c in FLAG_PARTS)
                self.send_json(200, {"flag": flag})
            else:
                self.send_json(403, {"error": "not admin"})

        else:
            self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    print("=== crackme_two ===")
    print("servidor rodando em http://localhost:1337")
    print("GET / para ver os endpoints")
    print("Ctrl+C para parar\n")
    HTTPServer(("localhost", 1337), Handler).serve_forever()

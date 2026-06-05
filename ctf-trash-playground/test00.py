import time

import requests


class ApiLab:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def get(self, path="/"):
        start = time.time()

        r = requests.get(f"{self.base_url}{path}")

        elapsed = time.time() - start

        return {"status": r.status_code, "body": r.text, "time": elapsed}

    def post(self, path, payload):
        start = time.time()

        r = requests.post(f"{self.base_url}{path}", json=payload)

        elapsed = time.time() - start

        return {"status": r.status_code, "body": r.text, "time": elapsed}

    def show(self, result):
        print("-" * 50)
        print("Status:", result["status"])
        print("Tempo :", round(result["time"], 3), "s")
        print("Body  :", result["body"])
        print("-" * 50)


lab = ApiLab("http://localhost:1337")

while True:
    print()
    print("1 - GET /")
    print("2 - POST /redeem")
    print("0 - sair")

    op = input("> ")

    if op == "1":
        lab.show(lab.get("/"))

    elif op == "2":
        cupom = input("Cupom: ")

        result = lab.post("/redeem", {"code": cupom})

        lab.show(result)

    elif op == "0":
        break

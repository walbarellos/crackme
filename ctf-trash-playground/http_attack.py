import requests

# GET simples
r = requests.get("http://localhost:1337/")
print(r.json())  # resposta em JSON

# POST com JSON no body
r = requests.post(
    "http://localhost:1337/login", json={"password": "0cc175b9c0f1b6a831c399e269772661"}
)
print(r.status_code)  # código HTTP (200, 401, 403...)
print(r.json())  # resposta

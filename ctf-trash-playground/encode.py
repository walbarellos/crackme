import base64
import json

payload = {"username": "guest", "role": "admin"}

texto = json.dumps(payload)
b64 = base64.b64encode(texto.encode()).decode()

print(b64)

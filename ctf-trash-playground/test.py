import requests

r = requests.post("http://localhost:1337/flag", json={"role": "admin"})

print(r.status_code)
print(r.json())

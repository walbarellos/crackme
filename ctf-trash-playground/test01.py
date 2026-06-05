import threading
import requests


def disparar():
    r = requests.post("http://localhost:1337/redeem", json={"code": "DESCONTO10"})
    print(r.json())


# cria 10 threads que rodam a mesma função ao mesmo tempo
threads = []
for i in range(10):
    t = threading.Thread(target=disparar)
    threads.append(t)

# dispara todas ao mesmo tempo
for t in threads:
    t.start()

# espera todas terminarem
for t in threads:
    t.join()

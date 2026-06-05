import hashlib
import base64

# ==============================================
#   WELCOME TO: crackme_zero
#   Objetivo: encontre a flag no formato CTF{...}
#   Dica: nem tudo que parece seguro, é seguro.
# ==============================================

SECRET = base64.b64encode(b"unlock_me").decode()


def check_password(password: str) -> bool:
    h = hashlib.md5(password.encode()).hexdigest()
    return h == "0cc175b9c0f1b6a831c399e269772661"


def get_flag(token: str) -> str:
    if token != SECRET:
        return "acesso negado."

    parts = [
        67,
        84,
        70,
        123,
        114,
        51,
        118,
        51,
        114,
        115,
        51,
        95,
        100,
        48,
        110,
        116,
        95,
        115,
        116,
        48,
        112,
        125,
    ]
    return "".join(chr(c) for c in parts)


def main():
    print("=== crackme_zero ===")
    password = input("senha: ")

    if not check_password(password):
        print("senha errada.")
        return

    print("senha correta! gerando token...")
    token = base64.b64encode(password.encode()).decode()
    print(f"token: {token}")
    print(get_flag(token))


if __name__ == "__main__":
    main()

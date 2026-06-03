#!/usr/bin/env python3
import sys

def generate_key(name):
    acc = 0
    for i, c in enumerate(name):
        acc += ord(c) * (i + 1)
    return acc % 9973

if len(sys.argv) != 2:
    print("Uso: python3 keygen.py <usuario>")
    sys.exit(1)

user = sys.argv[1]
expected = generate_key(user)
key_val = (expected * 1337) % 99991

# A formatação no C verifica um input de 9 chars onde [4] é '-',
# concatena as duas metades e passa no atoi().
# Portanto, a key_val deve ser formatada como XXXX-XXXX (completando com zeros)
val_str = str(key_val).zfill(8)
final_key = f"{val_str[:4]}-{val_str[4:]}"

print(f"[*] Usuário : {user}")
print(f"[*] Internal: {expected}")
print(f"[+] Keygerada: {final_key}")

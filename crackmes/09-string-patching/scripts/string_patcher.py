#!/usr/bin/env python3
import sys

if len(sys.argv) != 2:
    print("Uso: python3 string_patcher.py <binario>")
    sys.exit(1)

binary = sys.argv[1]

# Strings exatamente do tamanho do código C original (incluindo null byte)
old_str = b">> ACESSO NEGADO. SAIA.        \0"
new_str = b">> ACESSO CONCEDIDO. BEM-VINDO.\0"

if len(old_str) != len(new_str):
    print("[-] Erro: Strings devem ter o mesmo tamanho para não quebrar o ELF!")
    sys.exit(1)

with open(binary, 'rb') as f:
    data = f.read()

if old_str in data:
    data = data.replace(old_str, new_str)
    with open(binary, 'wb') as f:
        f.write(data)
    print(f"[+] String de falha substituída pela string de sucesso!")
else:
    print("[-] String original não encontrada. O binário já está patcheado?")

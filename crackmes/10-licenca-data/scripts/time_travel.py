#!/usr/bin/env python3
import sys

if len(sys.argv) != 2:
    print("Uso: python3 time_travel.py <binario>")
    sys.exit(1)

binary = sys.argv[1]

# 2024 - 1900 = 124 -> 0x7c. O GCC frequentemente emite mov dword ptr [X], 0x7c
# Vamos buscar o padrão que move o ano de 124 para a struct tm.
# Em 32-bits little-endian: 7c 00 00 00
# Vamos substituir por 199 (2099 - 1900): c7 00 00 00
old_year_bytes = b"\x7c\x00\x00\x00"
new_year_bytes = b"\xc7\x00\x00\x00"

with open(binary, 'rb') as f:
    data = f.read()

# Substitui as ocorrências do ano.
# Atenção: em um binário grande, buscar "7c 00 00 00" diretamente pode dar
# colisão com outras coisas. Num crackme didático curto, costuma funcionar.
# A melhor abordagem manual é achar o offset via objdump/r2.
if old_year_bytes in data:
    count = data.count(old_year_bytes)
    data = data.replace(old_year_bytes, new_year_bytes)
    with open(binary, 'wb') as f:
        f.write(data)
    print(f"[+] Substituições feitas: {count}")
    print("[+] Ano de expiração movido para 2099!")
else:
    print("[-] Padrão do ano 2024 não encontrado.")

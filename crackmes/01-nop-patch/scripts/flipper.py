#!/usr/bin/env python3
import sys

if len(sys.argv) != 4:
    print("Uso: python3 flipper.py <binario> <offset_hex> <novos_bytes_hex>")
    print("Exemplo: python3 flipper.py ../challenge 0x4011fa 9090")
    sys.exit(1)

binary = sys.argv[1]
offset = int(sys.argv[2], 16)
new_bytes = bytes.fromhex(sys.argv[3])

with open(binary, 'rb+') as f:
    f.seek(offset)
    f.write(new_bytes)

print(f"[+] Patch aplicado em {hex(offset)} com sucesso!")

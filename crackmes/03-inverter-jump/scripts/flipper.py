#!/usr/bin/env python3
import sys

if len(sys.argv) != 4:
    print("Uso: python3 flipper.py <binario> <offset_hex> <novo_byte_hex>")
    print("Exemplo: python3 flipper.py ../challenge 0x4012c3 75")
    sys.exit(1)

binary = sys.argv[1]
offset = int(sys.argv[2], 16)
new_bytes = bytes.fromhex(sys.argv[3])

with open(binary, 'rb+') as f:
    f.seek(offset)
    f.write(new_bytes)

print(f"[+] Byte substituído em {hex(offset)} para {new_bytes.hex()}")

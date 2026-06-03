#!/usr/bin/env python3
import sys
import struct

if len(sys.argv) != 4:
    print("Uso: python3 endian_patch.py <binario> <offset_hex> <nova_senha_int>")
    print("Exemplo: python3 endian_patch.py ../challenge 0x401236 1337")
    sys.exit(1)

binary = sys.argv[1]
offset = int(sys.argv[2], 16)
new_pin = int(sys.argv[3])

# Converte o inteiro para 4 bytes little-endian
patch_bytes = struct.pack('<i', new_pin)

with open(binary, 'rb+') as f:
    f.seek(offset)
    f.write(patch_bytes)

print(f"[+] Patch de 4 bytes injetado em {hex(offset)}: {patch_bytes.hex(' ')}")
print(f"[+] O novo PIN agora é {new_pin}")

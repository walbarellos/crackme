#!/usr/bin/env python3
import sys

if len(sys.argv) != 2:
    print("Uso: python3 pattern_patcher.py <binario>")
    sys.exit(1)

binary = sys.argv[1]

# Assinatura: mov eax, 0 ; leave ; ret
pattern = b"\xb8\x00\x00\x00\x00\xc9\xc3"
# Patch: mov eax, 1 ; leave ; ret
patch = b"\xb8\x01\x00\x00\x00\xc9\xc3"

with open(binary, 'rb') as f:
    data = f.read()

index = data.find(pattern)
if index != -1:
    print(f"[*] Assinatura encontrada no offset: {hex(index)}")
    data = data[:index] + patch + data[index + len(pattern):]
    
    with open(binary, 'wb') as f:
        f.write(data)
    print("[+] Patch aplicado com sucesso!")
else:
    print("[-] Assinatura não encontrada.")

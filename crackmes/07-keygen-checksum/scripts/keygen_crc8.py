#!/usr/bin/env python3
import sys

MAGIC = 0xDE

def crc8(value):
    crc = 0
    for i in range(3, -1, -1):
        byte = (value >> (i * 8)) & 0xFF
        for bit in range(7, -1, -1):
            if (crc ^ byte) & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
            byte = (byte << 1) & 0xFF
    return crc

def generate_full_license(prod_code_hex):
    prod = int(prod_code_hex, 16)
    expected = crc8(prod) ^ MAGIC
    return f"{prod:08X}:{expected:02X}"

if len(sys.argv) != 2:
    print("Uso: python3 keygen_crc8.py <PRODCODE_EM_HEX>")
    print("Exemplo: python3 keygen_crc8.py 4F2A1B3C")
    sys.exit(1)

prod = sys.argv[1]
print(f"[+] Licença gerada: {generate_full_license(prod)}")

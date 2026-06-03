#!/usr/bin/env python3
import sys
import struct

if len(sys.argv) != 3:
    print("Uso: python3 calc_offset.py <endereco_do_call> <endereco_da_funcao_alvo>")
    print("Exemplo: python3 calc_offset.py 0x4012d1 0x401204")
    sys.exit(1)

call_addr = int(sys.argv[1], 16)
target_addr = int(sys.argv[2], 16)

# Instrução CALL tem 5 bytes, a base de cálculo é o endereço seguinte
next_instr = call_addr + 5
offset = target_addr - next_instr

# Offset formatado como 32 bits com sinal (little endian)
patch_bytes = struct.pack('<i', offset)

print(f"[*] Call Address : {hex(call_addr)}")
print(f"[*] Target       : {hex(target_addr)}")
print(f"[*] Next Instr   : {hex(next_instr)}")
print(f"[*] Offset Decimal: {offset}")
print(f"[+] Bytes para patch: e8 {patch_bytes.hex(' ')}")

#!/usr/bin/env python3
"""
decode.py — Decodificador de valores para RE
Você dá um valor, ele mostra TODAS as interpretações possíveis.
A ideia: você vê 0x7C no binário e não sabe o que é.
Esse script expande o valor e faz você pensar no que faz sentido.
"""

import sys
import struct
import string
import datetime

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
BLUE    = "\033[94m"

def hr():
    print(f"{DIM}{'─' * 60}{RESET}")

def decode_value(raw):
    """Tenta interpretar um valor como decimal, hex, string, data, etc."""
    
    # Normaliza o input
    raw = raw.strip()
    
    results = {}
    
    # Tenta parsear como hex (com ou sem 0x)
    val_hex = None
    val_dec = None
    val_bytes = None
    
    try:
        if raw.startswith("0x") or raw.startswith("0X"):
            val_hex = int(raw, 16)
            val_dec = val_hex
        elif all(c in "0123456789abcdefABCDEF" for c in raw) and any(c in "abcdefABCDEF" for c in raw):
            val_hex = int(raw, 16)
            val_dec = val_hex
        else:
            val_dec = int(raw)
            val_hex = val_dec
    except ValueError:
        # Pode ser string de bytes como "7c 00 00 00"
        if " " in raw or raw.replace(" ", "").replace(":", "").replace("\\x", ""):
            try:
                clean = raw.replace(" ", "").replace(":", "").replace("\\x", "")
                val_bytes = bytes.fromhex(clean)
                val_dec = int.from_bytes(val_bytes, "little")
                val_hex = val_dec
            except:
                pass
    
    if val_dec is None:
        print(f"{RED}Não foi possível interpretar: {raw!r}{RESET}")
        return
    
    print(f"\n{BOLD}{BLUE}══ Analisando: {raw} ══{RESET}\n")
    
    # ── REPRESENTAÇÕES NUMÉRICAS ──
    print(f"{YELLOW}Representações numéricas:{RESET}")
    print(f"  Decimal:     {CYAN}{val_dec}{RESET}  ({val_dec:,})")
    print(f"  Hexadecimal: {CYAN}0x{val_hex:X}{RESET}  (0x{val_hex:x})")
    if val_dec < 256:
        print(f"  Binário:     {CYAN}{val_dec:08b}{RESET}")
    elif val_dec < 65536:
        print(f"  Binário:     {CYAN}{val_dec:016b}{RESET}")
    
    # Bytes little-endian / big-endian
    for size, fmt_le, fmt_be in [(4, '<I', '>I'), (8, '<Q', '>Q')]:
        try:
            le = struct.pack(fmt_le, val_dec & (0xFFFFFFFF if size==4 else 0xFFFFFFFFFFFFFFFF))
            be = struct.pack(fmt_be, val_dec & (0xFFFFFFFF if size==4 else 0xFFFFFFFFFFFFFFFF))
            print(f"  LE {size*8}-bit:    {CYAN}{le.hex(' ')}{RESET}")
            print(f"  BE {size*8}-bit:    {CYAN}{be.hex(' ')}{RESET}")
            break
        except (struct.error, OverflowError):
            continue
    
    hr()
    
    # ── INTERPRETAÇÃO COMO CARACTERE ──
    print(f"{YELLOW}Como caractere ASCII:{RESET}")
    if 32 <= val_dec <= 126:
        print(f"  {GREEN}'{chr(val_dec)}'{RESET}  — caractere imprimível")
    elif val_dec < 32:
        ctrl = {0: "NUL", 9: "TAB", 10: "LF (\\n)", 13: "CR (\\r)", 27: "ESC"}
        name = ctrl.get(val_dec, f"ctrl-{val_dec}")
        print(f"  {DIM}Caractere de controle: {name}{RESET}")
    else:
        print(f"  {DIM}Fora do range ASCII imprimível{RESET}")
    
    # Tenta interpretar como string de 4 bytes
    try:
        raw_bytes = struct.pack('<I', val_dec & 0xFFFFFFFF)
        s = "".join(chr(b) if 32 <= b <= 126 else "." for b in raw_bytes)
        print(f"  Como 4 bytes: {CYAN}'{s}'{RESET}  {DIM}(little-endian: {raw_bytes.hex(' ')}){RESET}")
    except:
        pass
    
    hr()
    
    # ── INTERPRETAÇÃO COMO DATA ──
    print(f"{YELLOW}Interpretações de data/tempo:{RESET}")
    
    # Ano (struct tm): anos desde 1900
    if 0 <= val_dec <= 300:
        ano = val_dec + 1900
        print(f"  {GREEN}struct tm.tm_year:{RESET} {ano}  {DIM}(val + 1900){RESET}")
    
    # Timestamp Unix
    if 1000000000 <= val_dec <= 2147483647:
        try:
            dt = datetime.datetime.utcfromtimestamp(val_dec)
            print(f"  {GREEN}Unix timestamp:{RESET} {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        except:
            pass
    
    # Ano como decimal direto
    if 1990 <= val_dec <= 2100:
        print(f"  {GREEN}Possível ano direto:{RESET} {val_dec}")
    
    # Hex que parece data YYYYMMDD
    hex_str = f"{val_dec:08X}"
    if len(hex_str) == 8:
        try:
            y = int(hex_str[:4], 16)
            m = int(hex_str[4:6], 16)
            d = int(hex_str[6:8], 16)
            if 2000 <= y <= 2030 and 1 <= m <= 12 and 1 <= d <= 31:
                print(f"  {GREEN}Possível data (BCD hex):{RESET} {y:04d}-{m:02d}-{d:02d}")
        except:
            pass
    
    hr()
    
    # ── CONSTANTES CONHECIDAS ──
    print(f"{YELLOW}Constantes conhecidas em RE:{RESET}")
    
    known = {
        0x7F454C46: "Magic ELF: \\x7fELF",
        0x5A4D:     "Magic PE: MZ (Windows)",
        0xDEADBEEF: "Marcador debug/canary clássico",
        0xCAFEBABE: "Magic Java bytecode / Mach-O fat",
        0x90909090: "4x NOP sled",
        0xCCCCCCCC: "Padrão de memoria não-inicializada (MSVC debug)",
        0x41414141: "'AAAA' — padding de fuzzing",
        0x61616161: "'aaaa' — padding de fuzzing",
        0x539:      "1337 (leet)",
        0x1337:     "1337 (leet) hex",
        0xDEAD:     "0xDEAD — marcador",
        0xBEEF:     "0xBEEF — marcador",
        0x7C:       "124 → struct tm year = 2024",
        0x7D:       "125 → struct tm year = 2025",
        0x4:        "4 — comum em checksums CRC",
        0x07:       "Polinômio CRC-8 simples",
        0x1DB7:     "7607 — primo?",
        0x26EF:     "9967 — primo próximo de 9973",
    }
    
    if val_dec in known:
        print(f"  {GREEN}RECONHECIDA:{RESET} {known[val_dec]}")
    else:
        # Verifica se é primo (para valores pequenos)
        if 2 <= val_dec <= 100000:
            is_prime = all(val_dec % i != 0 for i in range(2, int(val_dec**0.5)+1))
            if is_prime:
                print(f"  {CYAN}É número primo{RESET}  {DIM}(comum em algoritmos de keygen como módulo){RESET}")
        
        # Potência de 2?
        if val_dec > 0 and (val_dec & (val_dec - 1)) == 0:
            exp = val_dec.bit_length() - 1
            print(f"  {CYAN}É potência de 2:{RESET} 2^{exp}")
        
        # Múltiplo de constantes comuns
        for factor, name in [(1337, "1337"), (1000, "1000"), (256, "256"), (100, "100")]:
            if val_dec > 0 and val_dec % factor == 0:
                print(f"  {DIM}Múltiplo de {name}:{RESET} {val_dec} = {name} × {val_dec//factor}")
    
    hr()
    
    # ── OPERAÇÕES XOR REVERSAS ──
    print(f"{YELLOW}Se isso for resultado de XOR:{RESET}")
    print(f"  {DIM}Se resultado = original XOR {val_hex:#x}, então:{RESET}")
    for key in [0x42, 0xFF, 0xAA, 0x55, 0x13, 0x37, 0xDE, 0xAD]:
        original = val_dec ^ key
        if 32 <= original <= 126:
            print(f"  {GREEN}original XOR 0x{key:02X} = '{chr(original)}'{RESET}  (ASCII {original})")
    
    print()
    
    # ── PERGUNTA SOCRÁTICA ──
    print(f"{BOLD}Com isso em mente:{RESET}")
    
    if 0 <= val_dec <= 300:
        print(f"  → Você viu esse valor numa instrução 'mov' antes de uma comparação de data?")
        print(f"    Se sim: pode ser um ano em struct tm ({val_dec + 1900})")
    
    if val_dec > 1000000000:
        print(f"  → Você viu isso em contexto de time()? Pode ser um timestamp.")
    
    print(f"  → Esse valor aparece em algum 'cmp' no disassembly?")
    print(f"  → Aparece em 'strings' do binário?")
    print(f"  → Se for chave XOR, qual byte resultado faz sentido como ASCII?")
    print()


def main():
    if len(sys.argv) < 2:
        print(f"""
{BOLD}decode.py{RESET} — Expande um valor em todas suas interpretações possíveis

{BOLD}Uso:{RESET}
  python3 decode.py <valor>
  
  Aceita:
    Decimal:   python3 decode.py 1337
    Hex:       python3 decode.py 0x539
    Hex puro:  python3 decode.py 539
    Bytes LE:  python3 decode.py "7c 00 00 00"

{BOLD}Para qué:{RESET}
  Quando você encontra uma constante no disassembly e não sabe o que é.
  O script mostra todas as interpretações e faz perguntas que ajudam
  você a decidir qual faz sentido no contexto.
""")
        sys.exit(0)
    
    value = " ".join(sys.argv[1:])
    decode_value(value)


if __name__ == "__main__":
    main()

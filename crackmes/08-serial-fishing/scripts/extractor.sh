#!/bin/bash
# Um script para extrair as partes da serial que estão soltas no rodata

if [ ! -f "../challenge" ]; then
    echo "[-] Compile o challenge primeiro (make)"
    exit 1
fi

echo "[*] Extraindo strings do binário..."
# Procuramos por strings imprimíveis de pelo menos 3 caracteres
# e fazemos um grep para filtrar possíveis pedaços
strings ../challenge | grep -E "CR4|L4B|202|S3R|I4L"

echo "[+] As peças estão soltas na memória. Cabe a você juntá-las!"

#!/bin/bash
# reset_all.sh - Limpa e recompila todos os desafios do CrackLab

for dir in crackmes/*; do
    if [ -d "$dir" ] && [ -f "$dir/Makefile" ]; then
        echo "[*] Recompilando $dir..."
        make -C "$dir" clean > /dev/null 2>&1
        make -C "$dir" > /dev/null 2>&1
    fi
done
echo "[+] Todos os desafios foram restaurados para o estado original."

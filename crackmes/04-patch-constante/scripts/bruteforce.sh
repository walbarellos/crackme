#!/bin/bash
# Um script simples para forçar a entrada de PINs

for i in $(seq -w 0000 9999); do
    result=$(echo "$i" | ../challenge 2>/dev/null)
    if echo "$result" | grep -q "aberto"; then
        echo "[+] PIN ENCONTRADO: $i"
        break
    fi
done

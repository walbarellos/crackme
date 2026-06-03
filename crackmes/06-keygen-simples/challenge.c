/*
 * CRACKLAB #06 — Keygen Simples
 *
 * Valida uma chave de produto baseada no nome do usuário.
 * Algoritmo: soma os bytes do nome × posição, mod 9973 (primo).
 * Formato da chave: XXXX-XXXX (8 dígitos, separados por hífen)
 *
 * gcc -O0 -g -no-pie -fno-stack-protector -o challenge challenge.c
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define KEY_LEN 8

/* Valida se a string só tem dígitos no formato XXXX-XXXX */
static int parse_key(const char *raw, int *out) {
    char buf[16];
    if (strlen(raw) != 9) return 0;
    if (raw[4] != '-')    return 0;

    /* copia sem o hífen */
    memcpy(buf,     raw,     4);
    memcpy(buf + 4, raw + 5, 4);
    buf[8] = '\0';

    for (int i = 0; i < KEY_LEN; i++) {
        if (buf[i] < '0' || buf[i] > '9') return 0;
    }

    *out = atoi(buf);
    return 1;
}

/* Gera a chave esperada para um dado nome */
unsigned int generate_key(const char *name) {
    unsigned int acc = 0;
    int len = (int)strlen(name);
    for (int i = 0; i < len; i++) {
        acc += (unsigned char)name[i] * (i + 1);
    }
    return acc % 9973;
}

int main(void) {
    char name[64];
    char raw_key[32];
    int  provided;

    puts("╔══════════════════════════════════════╗");
    puts("║   ATIVADOR DE SOFTWARE v1.0          ║");
    puts("║   Insira seu nome e chave de produto ║");
    puts("╚══════════════════════════════════════╝");

    printf("\nNome de usuário: ");
    if (!fgets(name, sizeof(name), stdin)) exit(1);
    /* remove newline */
    name[strcspn(name, "\n")] = '\0';

    if (strlen(name) == 0) {
        puts("Nome não pode ser vazio.");
        exit(1);
    }

    printf("Chave (XXXX-XXXX): ");
    if (!fgets(raw_key, sizeof(raw_key), stdin)) exit(1);
    raw_key[strcspn(raw_key, "\n")] = '\0';

    if (!parse_key(raw_key, &provided)) {
        puts("\n  ✗ Formato inválido. Use XXXX-XXXX (8 dígitos).");
        exit(1);
    }

    unsigned int expected = generate_key(name);

    /* a chave fornecida deve ser os últimos 4 dígitos do valor gerado,
       formatados como YYYY-ZZZZ onde YYYY=expected>>2 e ZZZZ=expected */
    unsigned int key_val = (expected * 1337) % 99991;

    if ((unsigned int)provided == key_val) {
        puts("\n  ╔════════════════════════════════════╗");
        puts("  ║  ✓ CHAVE VÁLIDA                    ║");
        puts("  ║  Software ativado com sucesso.     ║");
        puts("  ║  FLAG{keygen_reversed}             ║");
        puts("  ╚════════════════════════════════════╝");
    } else {
        printf("\n  ✗ Chave inválida para o usuário '%s'.\n", name);
        exit(1);
    }

    return 0;
}

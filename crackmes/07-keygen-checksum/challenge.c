/*
 * CRACKLAB #07 — Keygen com Checksum
 *
 * Sistema de licença com dois campos: código de produto (PROD) e
 * checksum de verificação (CHECK). O CHECK deve ser o CRC-8 simples
 * do PROD XOR com uma constante mágica.
 *
 * Formato: PRODCODE:CHECKSUM  (ex: 4F2A1B3C:A7)
 * PRODCODE = 8 hex chars, CHECKSUM = 2 hex chars
 *
 * gcc -O0 -g -no-pie -fno-stack-protector -o challenge challenge.c
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAGIC 0xDE

/* CRC-8 simples (polinômio 0x07) */
static unsigned char crc8(unsigned int value) {
    unsigned char crc = 0;
    for (int i = 3; i >= 0; i--) {
        unsigned char byte = (value >> (i * 8)) & 0xFF;
        for (int bit = 7; bit >= 0; bit--) {
            if ((crc ^ byte) & 0x80)
                crc = (crc << 1) ^ 0x07;
            else
                crc <<= 1;
            byte <<= 1;
        }
    }
    return crc;
}

/* Calcula o checksum esperado para um dado código */
static unsigned char expected_checksum(unsigned int prod) {
    return crc8(prod) ^ MAGIC;
}

int main(void) {
    char input[32];
    unsigned int prod_code;
    unsigned int check_provided;

    puts("╔══════════════════════════════════════╗");
    puts("║   SISTEMA DE LICENÇA CORPORATIVA     ║");
    puts("║   formato: PRODCODE:CHECKSUM         ║");
    puts("║   exemplo: 4F2A1B3C:A7              ║");
    puts("╚══════════════════════════════════════╝");

    printf("\nLicença: ");
    if (!fgets(input, sizeof(input), stdin)) exit(1);
    input[strcspn(input, "\n")] = '\0';

    /* Valida o formato */
    if (strlen(input) != 11 || input[8] != ':') {
        puts("\n  ✗ Formato inválido. Use PRODCODE:CHECKSUM.");
        exit(1);
    }

    /* Parse */
    char prod_str[9]  = {0};
    char check_str[3] = {0};
    memcpy(prod_str,  input,      8);
    memcpy(check_str, input + 9,  2);

    /* Converte hex */
    char *endp;
    prod_code      = (unsigned int)strtoul(prod_str,  &endp, 16);
    if (*endp != '\0') { puts("  ✗ PRODCODE inválido."); exit(1); }

    check_provided = (unsigned int)strtoul(check_str, &endp, 16);
    if (*endp != '\0') { puts("  ✗ CHECKSUM inválido."); exit(1); }

    unsigned char expected = expected_checksum(prod_code);

    if ((unsigned char)check_provided == expected) {
        puts("\n  ╔════════════════════════════════════╗");
        puts("  ║  ✓ LICENÇA VÁLIDA                  ║");
        puts("  ║  Módulo corporativo desbloqueado.  ║");
        puts("  ║  FLAG{checksum_is_just_math}       ║");
        puts("  ╚════════════════════════════════════╝");
    } else {
        printf("\n  ✗ Checksum inválido. Esperado: %02X, recebido: %02X\n",
               expected, (unsigned char)check_provided);
        puts("  Licença rejeitada.");
        exit(1);
    }

    return 0;
}

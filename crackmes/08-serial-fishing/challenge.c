/*
 * CRACKLAB #08 — Serial Fishing
 *
 * A serial está em algum lugar no binário.
 * strings, xxd, grep — você decide.
 *
 * O programa compara a entrada com uma string hardcoded usando strcmp
 * direto — sem hash, sem transformação, sem nada. A resposta está
 * literalmente escrita no ELF.
 *
 * gcc -O0 -g -no-pie -fno-stack-protector -o challenge challenge.c
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* Dividida em partes pra dificultar um grep ingênuo */
static const char S1[] = "CR4CK";
static const char S2[] = "L4B-";
static const char S3[] = "2026";
static const char S4[] = "-S3R";
static const char S5[] = "I4L";

int main(void) {
    char input[64];
    char serial[32];

    /* Monta a serial em runtime — mas continua no .rodata em pedaços */
    snprintf(serial, sizeof(serial), "%s%s%s%s%s", S1, S2, S3, S4, S5);

    puts("╔══════════════════════════════════════╗");
    puts("║   REGISTRO DE SOFTWARE v3.0          ║");
    puts("╚══════════════════════════════════════╝");

    printf("\nSerial de registro: ");
    if (!fgets(input, sizeof(input), stdin)) exit(1);
    input[strcspn(input, "\n")] = '\0';

    if (strcmp(input, serial) == 0) {
        puts("\n  ╔════════════════════════════════════╗");
        puts("  ║  ✓ SERIAL VÁLIDA                   ║");
        puts("  ║  Produto registrado com sucesso.   ║");
        puts("  ║  FLAG{strings_reveal_secrets}      ║");
        puts("  ╚════════════════════════════════════╝");
    } else {
        puts("\n  ✗ Serial inválida.");
        puts("  Dica: a resposta já está no binário.");
        exit(1);
    }

    return 0;
}

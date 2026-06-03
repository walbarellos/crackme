/*
 * CRACKLAB #01 — NOP Patch
 *
 * O programa valida uma licença simples.
 * is_valid_key() retorna 1 (válida) ou 0 (inválida).
 * O main usa o retorno para decidir qual mensagem exibir.
 *
 * Objetivo: fazer aparecer "Licença válida!" sem conhecer a licença correta.
 * Técnica: substituir o jump condicional por dois NOPs (0x90 0x90).
 *
 * Compilação:
 *   make
 * ou:
 *   gcc -O0 -fno-stack-protector -no-pie -m64 -o challenge challenge.c
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define VALID_KEY "CR4CKL4B-K3Y"

int is_valid_key(const char *key) {
    if (strcmp(key, VALID_KEY) == 0)
        return 1;
    return 0;
}

int main(void) {
    char input[64];

    puts("╔══════════════════════════════════════╗");
    puts("║   ATIVADOR DE SOFTWARE v1.0          ║");
    puts("╚══════════════════════════════════════╝");

    printf("\nLicença: ");
    if (!fgets(input, sizeof(input), stdin)) exit(1);
    input[strcspn(input, "\n")] = '\0';

    if (is_valid_key(input)) {
        puts("\n  ╔════════════════════════════════════╗");
        puts("  ║  ✓ Licença válida! Software ativado.║");
        puts("  ║  FLAG{nop_the_jump}                ║");
        puts("  ╚════════════════════════════════════╝");
    } else {
        puts("\n  ╔════════════════════════════════════╗");
        puts("  ║  ✗ Licença inválida.               ║");
        puts("  ╚════════════════════════════════════╝");
        exit(1);
    }

    return 0;
}

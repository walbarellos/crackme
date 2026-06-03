/*
 * CRACKLAB #09 — String Patching
 *
 * O programa sempre imprime "ACESSO NEGADO". Você não vai mudar
 * a lógica — vai mudar o que está escrito no binário.
 *
 * As strings de sucesso e falha estão no .rodata. O objetivo é
 * localizar os bytes da mensagem de negação e sobrescrevê-los
 * com a mensagem de sucesso — sem tocar em nenhuma instrução.
 *
 * gcc -O0 -g -no-pie -fno-stack-protector -o challenge challenge.c
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* Ambas têm exatamente o mesmo comprimento — 32 bytes com padding */
static const char MSG_DENIED[]  = ">> ACESSO NEGADO. SAIA.        \0";
static const char MSG_GRANTED[] = ">> ACESSO CONCEDIDO. BEM-VINDO.\0";

int main(void) {
    char user[32];

    puts("╔══════════════════════════════════════╗");
    puts("║   TERMINAL SEGURO — AUTENTICADOR     ║");
    puts("╚══════════════════════════════════════╝");

    printf("\nIdentificador: ");
    if (!fgets(user, sizeof(user), stdin)) exit(1);
    user[strcspn(user, "\n")] = '\0';

    /* A lógica sempre nega — mas a string pode mudar */
    (void)user;
    puts(MSG_DENIED);

    if (0) {
        /* Esse bloco nunca executa, mas garante que MSG_GRANTED
           fique no binário (referenciada, não otimizada) */
        puts(MSG_GRANTED);
        puts("FLAG{patch_the_string_not_the_logic}");
    }

    return 0;
}

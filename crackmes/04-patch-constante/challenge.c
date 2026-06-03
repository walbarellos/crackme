#include <stdio.h>
#include <stdlib.h>

#define MAX_TRIES   3
#define SECRET_PIN  7291

int main() {
    int pin;
    int tries = 0;

    puts("╔══════════════════════════════════╗");
    puts("║     COFRE DIGITAL v2.0           ║");
    puts("╚══════════════════════════════════╝");

    while (tries < MAX_TRIES) {
        printf("\nSenha (%d tentativa(s) restante(s)): ", MAX_TRIES - tries);
        if (scanf("%d", &pin) != 1) {
            puts("Entrada invalida.");
            exit(1);
        }

        if (pin == SECRET_PIN) {
            puts("\n  ✓ Cofre aberto. Bem-vindo.");
            puts("  > Conteudo: FLAG{patch_the_constant}");
            puts("╚══════════════════════════════════╝");
            return 0;
        }

        tries++;
        if (tries < MAX_TRIES)
            puts("  ✗ Senha incorreta.");
    }

    puts("\n  ✗ Cofre bloqueado. Muitas tentativas.");
    puts("╚══════════════════════════════════╝");
    exit(1);
}

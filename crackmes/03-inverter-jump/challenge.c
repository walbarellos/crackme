#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CODE_LEN 8

// Codigo de ativacao: soma dos digitos deve ser 42
int validate_code(const char *code) {
    if (strlen(code) != CODE_LEN)
        return 0;

    int sum = 0;
    for (int i = 0; i < CODE_LEN; i++) {
        if (code[i] < '0' || code[i] > '9')
            return 0;
        sum += code[i] - '0';
    }

    return (sum != 42) ? 0 : 1;
}

int main() {
    char code[32];

    puts("=========================================");
    puts("   SISTEMA DE ATIVACAO v1.0              ");
    puts("=========================================");
    printf("Insira o codigo de ativacao (8 digitos): ");
    scanf("%31s", code);

    if (validate_code(code)) {
        puts("");
        puts("  [OK] Codigo valido. Sistema ativado.   ");
        puts("=========================================");
    } else {
        puts("");
        puts("  [X]  Codigo invalido. Tente novamente. ");
        puts("=========================================");
        exit(1);
    }

    return 0;
}

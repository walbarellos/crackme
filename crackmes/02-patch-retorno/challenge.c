#include <stdio.h>
#include <string.h>

int is_premium_user(const char *username) {
    // Lista de usuários premium hardcoded
    const char *premium[] = { "admin", "root", "vip" };
    for (int i = 0; i < 3; i++) {
        if (strcmp(username, premium[i]) == 0)
            return 1;
    }
    return 0;
}

void show_premium_content() {
    puts("=================================");
    puts("  BEM-VINDO AO CONTEUDO PREMIUM  ");
    puts("=================================");
    puts("  > Video 1: Introducao secreta  ");
    puts("  > Video 2: Tecnica avancada    ");
    puts("  > Video 3: Conteudo exclusivo  ");
    puts("=================================");
}

void show_free_content() {
    puts("=================================");
    puts("       CONTA GRATUITA            ");
    puts("=================================");
    puts("  Acesso negado ao conteudo      ");
    puts("  premium. Faca upgrade!         ");
    puts("=================================");
}

int main() {
    char username[64];
    printf("Usuario: ");
    scanf("%63s", username);

    if (is_premium_user(username)) {
        show_premium_content();
    } else {
        show_free_content();
    }

    return 0;
}

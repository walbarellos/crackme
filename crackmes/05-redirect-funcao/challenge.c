#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void access_denied() {
    puts("\n  ╔══════════════════════════════════╗");
    puts("  ║  ACESSO NEGADO                   ║");
    puts("  ║  Credenciais invalidas.           ║");
    puts("  ╚══════════════════════════════════╝");
    exit(1);
}

void access_granted() {
    puts("\n  ╔══════════════════════════════════╗");
    puts("  ║  ACESSO AUTORIZADO               ║");
    puts("  ║  Bem-vindo, operador.             ║");
    puts("  ║  > sistema online                 ║");
    puts("  ║  > logs: /var/log/ops.log         ║");
    puts("  ║  > FLAG{redirect_the_call}        ║");
    puts("  ╚══════════════════════════════════╝");
}

void authenticate(const char *user, const char *pass) {
    if (strcmp(user, "admin") == 0 && strcmp(pass, "s3cr3t_p4ss") == 0) {
        access_granted();
    } else {
        access_denied();
    }
}

int main() {
    char user[32], pass[32];

    puts("╔══════════════════════════════════╗");
    puts("║   TERMINAL DE ACESSO REMOTO      ║");
    puts("╚══════════════════════════════════╝");

    printf("Usuario: ");
    scanf("%31s", user);
    printf("Senha:   ");
    scanf("%31s", pass);

    authenticate(user, pass);
    return 0;
}

/*
 * CRACKLAB #10 — Licença com Data de Expiração
 *
 * O software verifica se a data atual é anterior à data de expiração
 * hardcoded no binário. Se passou, nega o acesso.
 *
 * A data de expiração está em .rodata como string + comparação com
 * time(). Duas abordagens: patchear a data, ou patchear o jump de
 * comparação.
 *
 * gcc -O0 -g -no-pie -fno-stack-protector -o challenge challenge.c
 */

#include <stdio.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>

/* Data de expiração hardcoded: 2024-01-01 00:00:00 UTC (já expirado) */
#define EXPIRY_YEAR  2024
#define EXPIRY_MONTH 1
#define EXPIRY_DAY   1

static time_t get_expiry(void) {
    struct tm t = {0};
    t.tm_year = EXPIRY_YEAR - 1900;
    t.tm_mon  = EXPIRY_MONTH - 1;
    t.tm_mday = EXPIRY_DAY;
    t.tm_hour = 0;
    t.tm_min  = 0;
    t.tm_sec  = 0;
    return timegm(&t);
}

int main(void) {
    puts("╔══════════════════════════════════════╗");
    puts("║   LICENSA PRO v4.2 — TRIAL           ║");
    puts("╚══════════════════════════════════════╝");

    time_t now    = time(NULL);
    time_t expiry = get_expiry();

    struct tm *exp_tm = gmtime(&expiry);
    printf("\n  Expiração: %04d-%02d-%02d\n",
           exp_tm->tm_year + 1900,
           exp_tm->tm_mon  + 1,
           exp_tm->tm_mday);

    struct tm *now_tm = gmtime(&now);
    printf("  Hoje:      %04d-%02d-%02d\n",
           now_tm->tm_year + 1900,
           now_tm->tm_mon  + 1,
           now_tm->tm_mday);

    if (now >= expiry) {
        puts("\n  ╔════════════════════════════════════╗");
        puts("  ║  ✗ LICENÇA EXPIRADA                ║");
        puts("  ║  Contate o suporte para renovar.   ║");
        puts("  ╚════════════════════════════════════╝");
        exit(1);
    }

    puts("\n  ╔════════════════════════════════════╗");
    puts("  ║  ✓ LICENÇA VÁLIDA                  ║");
    puts("  ║  Bem-vindo ao LicensaPRO.          ║");
    puts("  ║  FLAG{time_is_just_a_number}       ║");
    puts("  ╚════════════════════════════════════╝");

    return 0;
}

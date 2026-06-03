# #10 — Licença com Data de Expiração

**Nível:** Intermediário  
**Técnica:** Patchear constante de data ou inverter comparação temporal  
**Ferramentas:** objdump, radare2, python3, dd

---

## A história

Trial expirado. Data de expiração: 2024-01-01.

```
$ ./challenge
╔══════════════════════════════════════╗
║   LICENSA PRO v4.2 — TRIAL           ║
╚══════════════════════════════════════╝

  Expiração: 2024-01-01
  Hoje:      2026-06-02

  ╔════════════════════════════════════╗
  ║  ✗ LICENÇA EXPIRADA                ║
  ║  Contate o suporte para renovar.   ║
  ╚════════════════════════════════════╝
```

O software compara `time(NULL)` com um timestamp de expiração hardcoded.  
Como hoje já é 2026, a licença está vencida há dois anos.

Seu objetivo: fazer o software acreditar que ainda está dentro do prazo.

---

## O que você sabe

O código calcula o timestamp de expiração assim:

```c
#define EXPIRY_YEAR  2024
#define EXPIRY_MONTH 1
#define EXPIRY_DAY   1
```

Esses valores são usados em `get_expiry()` para construir um `struct tm`  
e converter para `time_t` via `timegm()`.

O programa verifica: `if (now >= expiry)` → expirado.

Duas abordagens válidas:
1. **Patchear a data** — trocar 2024 por 2099 no binário
2. **Inverter o salto** — trocar `jge` por `jl` na comparação

---

## Dica

> Abre o disassembly de `get_expiry()`.  
> Os valores `EXPIRY_YEAR - 1900`, `EXPIRY_MONTH - 1` e `EXPIRY_DAY`  
> são atribuídos como constantes ao `struct tm`.  
> Onde você vê `124` (= 2024 - 1900) no disassembly?

---

## Solução

### Abordagem 1 — Patchear o ano de expiração

O compilador vai gerar algo assim em `get_expiry`:

```asm
mov dword ptr [rbp - 0x30], 0x7c   ; 0x7c = 124 = 2024 - 1900
mov dword ptr [rbp - 0x2c], 0x0    ; mês 0 = janeiro
mov dword ptr [rbp - 0x28], 0x1    ; dia 1
```

Você quer mudar `0x7c` (124) para `0xBF` (191 = 2099 - 1900).

```bash
objdump -d ./challenge | grep -B2 -A10 "<get_expiry>"
```

Localiza a instrução com `7c 00 00 00` (little-endian de 124):

```
401196:  c7 45 d0 7c 00 00 00   mov DWORD PTR [rbp-0x30], 0x7c
```

O offset no arquivo do valor `7c` é `0x401199` (3 bytes após o início da instrução).

**Com radare2:**
```
r2 -w ./challenge
s 0x401199
wx bf 00 00 00    ; 191 = 2099 - 1900
q
```

**Com python3:**
```python
binary = bytearray(open('./challenge', 'rb').read())
# localiza os bytes da constante 124 em little-endian no contexto correto
# c7 45 d0 7c 00 00 00
old = bytes([0xc7, 0x45, 0xd0, 0x7c, 0x00, 0x00, 0x00])
new = bytes([0xc7, 0x45, 0xd0, 0xbf, 0x00, 0x00, 0x00])
idx = binary.find(old)
if idx != -1:
    binary[idx:idx+7] = new
    open('./challenge', 'wb').write(binary)
    print(f"Expiração movida pra 2099, offset 0x{idx:x}")
```

---

### Abordagem 2 — Inverter a comparação temporal

O main tem:
```c
if (now >= expiry) { /* expirado */ exit(1); }
```

No disassembly:
```asm
cmp  rax, rdx       ; now vs expiry
jge  0x...          ; se now >= expiry → bloco de expirado
```

Trocar `jge` (opcode `7d`) por `jl` (opcode `7c`) inverte a lógica:
- Agora `now >= expiry` → **não pula** → cai no bloco de válido ✓
- `now < expiry` → pula → bloco de expirado (comportamento nunca ativado)

```bash
objdump -d ./challenge | grep "jge\|jl" | head -10
```

Localiza o endereço e:
```
r2 -w ./challenge
s <endereço do jge>
wx 7c
q
```

---

### Tabela comparativa

| Abordagem | O que muda | Rastro no binário |
|-----------|-----------|-------------------|
| Patchear ano | Constante em `.text` (get_expiry) | Valor numérico alterado |
| Inverter jge→jl | Opcode do salto em main | Um byte de instrução |
| NOP no exit(1) | Remove o exit do bloco expirado | 5 NOPs visíveis |

A inversão do salto é a mais cirúrgica — um byte, sem alterar dados.

---

## Por que o timestamp funciona assim

```
2024-01-01 00:00:00 UTC
  → struct tm: tm_year=124, tm_mon=0, tm_mday=1
  → timegm() → Unix timestamp: 1704067200

time(NULL) em 2026-06-02
  → timestamp: ~1748822400

1748822400 >= 1704067200  →  true  →  expirado
```

Patchear `tm_year` de 124 para 191 (2099):
```
timegm(2099-01-01) = 4070908800

time(NULL) = 1748822400 < 4070908800  →  false  →  válido ✓
```

---

## Variações pra explorar

**Variação 1 — fake o time() com LD_PRELOAD**  
Sem tocar no binário, intercepta `time()` em runtime:
```c
// fake_time.c
#include <time.h>
time_t time(time_t *t) {
    time_t fake = 1000000000; // 2001 — antes da expiração
    if (t) *t = fake;
    return fake;
}
```
```bash
gcc -shared -fPIC -o fake_time.so fake_time.c
LD_PRELOAD=./fake_time.so ./challenge
```
Funciona sem modificar um byte do binário. Mas não persiste.

**Variação 2 — date spoofing com libfaketime**  
```bash
faketime '2020-01-01 00:00:00' ./challenge
```
Ainda mais simples — se você tiver o `libfaketime` instalado.

**Pergunta:** se o servidor validasse a licença remotamente (enviando o timestamp pro backend),  
qual das abordagens acima ainda funcionaria? Qual exigiria algo diferente?

---

## Próximo desafio

**#11 — Licença Baseada em Hardware**  
A licença agora depende do hardware: CPUID ou endereço MAC como seed.  
Falsificar a identidade da máquina é um problema diferente.

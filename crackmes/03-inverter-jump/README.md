# #03 — Inverter Jump

**Nível:** Iniciante  
**Técnica:** Inverter jump condicional  
**Ferramentas:** radare2, objdump, xxd + dd

---

## A história

Sistema de ativação. Código de 8 dígitos.  
Você não tem o código. E não precisa ter.

```
$ ./challenge
=========================================
   SISTEMA DE ATIVACAO v1.0
=========================================
Insira o codigo de ativacao (8 digitos): 12345678

  [X]  Codigo invalido. Tente novamente.
=========================================
```

Objetivo: fazer aparecer `[OK] Codigo valido. Sistema ativado.`  
com qualquer entrada.

---

## O que você sabe

Existe uma função `validate_code()`.  
Ela retorna `1` ou `0`.  
O `main` usa esse retorno pra decidir o caminho.

No desafio #02 você aprendeu a mentir dentro da função.  
Desta vez, a função está **certa** — ela valida direito.  
O problema está em **quem interpreta o resultado**.

---

## Dica

> Abre o disassembly do `main`.  
> Procura o `call validate_code`.  
> O que vem logo depois?  
> Se o resultado é `0` (inválido), o programa pula pra onde?  
> E se você fizesse ele pular pro lado errado?

---

## Solução

### 1. Localiza o ponto de decisão no main

```bash
objdump -d ./challenge | grep -A 10 "call.*validate_code"
```

Você vai ver:

```asm
4012bc:  call  4011b6 <validate_code>
4012c1:  test  %eax, %eax          ; eax = retorno (0 ou 1)
4012c3:  je    4012f4               ; se 0 (invalido) → pula pro erro
4012c5:  ...                        ; senão → conteúdo válido
```

O `je` em `0x4012c3` é o portão.  
Se `validate_code` retorna `0`, o zero flag é setado, e `je` pula pro bloco de erro.  
Se retorna `1`, não pula — cai no bloco de sucesso.

### 2. A inversão

`je` (opcode `74`) pula quando igual a zero.  
`jne` (opcode `75`) pula quando **diferente** de zero.

Trocar `74` por `75` inverte a lógica inteira:
- Código inválido (retorna 0) → **não pula** → cai no sucesso ✓  
- Código válido (retorna 1) → pula → vai pro erro

Uma troca de um byte. Lógica espelhada.

### 3. Confirma o byte no endereço

```bash
objdump -d ./challenge | grep "4012c3"
```

Resultado esperado:
```
4012c3:  74 2f   je  4012f4
```

`74` = je. `2f` = offset do salto (decimal 47).  
Você só vai mexer no `74`.

### 4. O patch

**Com radare2:**
```
r2 -w ./challenge
s 0x4012c3
wx 75
q
```

**Com xxd + dd (sem radare2):**
```bash
# Descobre o offset no arquivo (endereço virtual → offset no arquivo)
# Com no-pie, endereço virtual == offset. Mas confirma:
objdump -d ./challenge | grep "4012c3"

# Patch direto com printf e dd
printf '\x75' | dd of=./challenge bs=1 seek=$((0x4012c3)) conv=notrunc 2>/dev/null
```

### 5. Verifica

```bash
objdump -d ./challenge | grep "4012c3"
```

Deve mostrar agora:
```
4012c3:  75 2f   jne  4012f4
```

### 6. Roda

```bash
./challenge
Insira o codigo de ativacao (8 digitos): 00000000

  [OK] Codigo valido. Sistema ativado.
```

---

## Por que funciona

```
antes do patch:

validate_code("00000000") → retorna 0
test eax, eax             → ZF = 1 (eax é zero)
je  0x4012f4              → ZF=1, pula → ERRO


depois do patch:

validate_code("00000000") → retorna 0
test eax, eax             → ZF = 1
jne 0x4012f4              → ZF=1, NÃO pula → SUCESSO ✓
```

A função continua funcionando perfeitamente.  
Você só trocou quem o portão deixa passar.

---

## Tabela de jumps condicionais — cola rápida

| Instrução | Opcode | Pula quando |
|-----------|--------|-------------|
| `je`  | `74` | igual / zero |
| `jne` | `75` | diferente / não-zero |
| `jl`  | `7C` | menor (signed) |
| `jge` | `7D` | maior ou igual (signed) |
| `jle` | `7E` | menor ou igual (signed) |
| `jg`  | `7F` | maior (signed) |

Cada par é separado por 1 bit. `je` ↔ `jne` é literalmente `74` ↔ `75`.

---

## Variações pra explorar

**Alternativa 1 — patch na função**  
Em `validate_code`, o resultado final é calculado por `sete` em `0x401245`.  
`sete` seta `al` para 1 se ZF=1 (se soma == 42).  
Trocar por `setne` (`0f 95`) inverte: retorna 1 pra qualquer soma que **não** seja 42.

**Alternativa 2 — NOP no exit**  
O bloco de erro chama `exit(1)` em `0x401326`.  
NOP o call. O programa não termina mais no erro — cai no return normal.  
Mas o output ainda mostra `[X]`. Funciona, mas fica feio.

**Pergunta:** qual dessas três abordagens (je→jne, patch na função, NOP no exit)  
deixaria menos rastro numa análise forense do binário?

---

## Próximo desafio

**#04 — Patch de Constante**  
O programa compara sua entrada com um número fixo.  
Esse número está gravado em algum lugar.  
Você pode mudar o número em vez de mudar a lógica.

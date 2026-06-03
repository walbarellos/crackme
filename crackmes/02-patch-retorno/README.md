# #02 — Patch de Retorno

**Nível:** Iniciante  
**Técnica:** Forçar retorno de função  
**Ferramentas:** radare2, objdump, gdb (qualquer uma)

---

## A história

Você encontrou um player de cursos online.  
Tem conteúdo premium. Tem conteúdo gratuito.  
E tem uma função que decide qual você merece ver.

```
$ ./challenge
Usuario: hacker
=================================
       CONTA GRATUITA
=================================
  Acesso negado ao conteudo
  premium. Faca upgrade!
=================================
```

Seu objetivo: ver o conteúdo premium.  
Qualquer usuário. Qualquer senha. Não importa.

---

## O que você sabe

O binário chama uma função pra decidir se você é premium ou não.  
Essa função retorna `1` (premium) ou `0` (não premium).  
Tudo depende do que ela retorna.

E se ela **sempre** retornasse `1`?

---

## Dica

> Antes de ler a solução, tenta responder:  
> Como uma função comunica seu resultado pra quem a chamou?  
> Em x86-64, qual registrador carrega esse valor de volta?

Pensa nisso. Abre o disassembly. Procura a função `is_premium_user`.  
Olha as últimas instruções antes do `ret`.

---

## Solução

### 1. Localiza a função

```bash
objdump -d ./challenge | grep -A 2 "<is_premium_user>"
```

Ou no radare2:
```
r2 -A ./challenge
s sym.is_premium_user
pdf
```

Você vai ver algo assim no final da função:

```asm
401196:  is_premium_user:
  ...
  4011fe:  mov $0x0,%eax     ; return 0  ← caminho de "não premium"
  401203:  leave
  401204:  ret

  ; (dentro do loop, quando encontra match:)
  4011ed:  mov $0x1,%eax     ; return 1  ← só chega aqui com usuário válido
  4011f2:  jmp 401203
```

### 2. Entende o problema

Em x86-64, o valor de retorno de uma função fica em `eax`.  
Antes de retornar, a função faz `mov $0x0, %eax` (coloca 0 em eax).  
Quem chamou lê esse valor e decide o caminho.

Se você forçar `eax = 1` logo antes do `ret`, a função sempre diz "é premium".

### 3. O patch

O endereço do `mov $0x0, %eax` final é `0x4011fe`.  
Você vai sobrescrever essa instrução por `mov $0x1, %eax`.

Em bytes:
```
mov $0x0, %eax  →  b8 00 00 00 00   (5 bytes)
mov $0x1, %eax  →  b8 01 00 00 00   (5 bytes)
```

Mesmo tamanho. Só o segundo byte muda: `00` → `01`.

No radare2:
```
r2 -w ./challenge
s 0x4011fe
wx b8 01 00 00 00
q
```

### 4. Verifica

```bash
objdump -d ./challenge | grep -A 5 "4011fe"
```

Deve mostrar:
```asm
4011fe:  mov $0x1,%eax
```

### 5. Roda

```bash
./challenge
Usuario: qualquercoisa
=================================
  BEM-VINDO AO CONTEUDO PREMIUM
=================================
```

---

## Por que funciona

```
antes do patch:

is_premium_user("hacker")
  → loop não encontra match
  → mov eax, 0      ← você patcheou isso
  → ret
  → main lê eax = 0 → show_free_content()


depois do patch:

is_premium_user("hacker")
  → loop não encontra match
  → mov eax, 1      ← agora sempre retorna 1
  → ret
  → main lê eax = 1 → show_premium_content()
```

Você não tocou no `main`. Não tocou no loop. Não precisou entender o algoritmo.  
Só ensinou a função a mentir sobre o resultado.

---

## Variações pra explorar

**Alternativa 1 — patch mais agressivo**  
Substituir o início inteiro da função por:
```asm
mov eax, 1
ret
```
A função nem executa — já retorna na primeira instrução.

**Alternativa 2 — patch no main**  
Em vez de mexer na função, inverte o `je` no `main` (endereço `0x401327`):
```
je  →  jne
```
Mesma técnica do desafio #01, diferente ponto de aplicação.

**Pergunta:** qual das três abordagens é mais "cirúrgica"? Qual deixa menos rastro?

---

## Próximo desafio

**#03 — Inverter Jump**  
Desta vez a lógica está certa, mas a condição está errada.  
Ou está?

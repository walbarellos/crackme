# #08 — Serial Fishing

**Nível:** Iniciante  
**Técnica:** Localizar string hardcoded no binário  
**Ferramentas:** strings, xxd, grep, radare2

---

## A história

Software de registro. Uma serial. Você não tem.

```
$ ./challenge
╔══════════════════════════════════════╗
║   REGISTRO DE SOFTWARE v3.0          ║
╚══════════════════════════════════════╝

Serial de registro: QUALQUER-COISA

  ✗ Serial inválida.
  Dica: a resposta já está no binário.
```

O binário compara sua entrada com uma string fixa usando `strcmp`.  
Sem hash. Sem criptografia. A resposta está literalmente escrita no ELF.

Seu objetivo: encontrar a serial e registrar o software.

---

## O que você sabe

A serial foi dividida em partes no código-fonte:
```c
static const char S1[] = "CR4CK";
static const char S2[] = "L4B-";
...
```

Essas strings vivem no `.rodata` do binário.  
Separadas na fonte, mas juntas na memória quando o programa roda.  
E individualmente visíveis com `strings`.

---

## Dica

> Antes de qualquer disassembly, tente a ferramenta mais simples:
> ```bash
> strings ./challenge | grep -E "^[A-Z0-9]{4,}"
> ```
> O que você vê? Consegue montar a serial com os pedaços?

---

## Solução

### Abordagem 1 — strings (o caminho direto)

```bash
strings ./challenge
```

Você vai ver os fragmentos individuais em `.rodata`:
```
CR4CK
L4B-
2026
-S3R
I4L
```

A serial montada é a concatenação: `CR4CKL4B-2026-S3RI4L`

```bash
./challenge
Serial de registro: CR4CKL4B-2026-S3RI4L

  ╔════════════════════════════════════╗
  ║  ✓ SERIAL VÁLIDA                   ║
  ║  Produto registrado com sucesso.   ║
  ║  FLAG{strings_reveal_secrets}      ║
  ╚════════════════════════════════════╝
```

---

### Abordagem 2 — xxd + grep

```bash
xxd ./challenge | grep -i "4352 344b"   # "CR4K" em hex
```

Localiza os bytes exatos das strings no arquivo binário.  
Útil quando `strings` filtra coisas curtas demais.

---

### Abordagem 3 — radare2 / gdb (watchpoint no strcmp)

```bash
r2 -d ./challenge
db sym.imp.strcmp
dc
# quando parar, inspeciona os argumentos:
dr rdi
ps @ rdi   # primeiro argumento: sua entrada
ps @ rsi   # segundo argumento: a serial correta
```

Esse método funciona **mesmo se a serial for montada em runtime** — você vê a string já construída em memória no momento da comparação.

---

## Por que funciona

Strings literais em C ficam na seção `.rodata` do ELF — somente leitura, mas não cifradas.  
Qualquer ferramenta que leia o arquivo binário pode encontrá-las.

O desafio dividiu a serial em fragmentos para dificultar um `grep` ingênuo direto no binário — mas os fragmentos continuam visíveis individualmente. A proteção real exigiria XOR ou hash.

---

## Variações pra explorar

**Variação 1 — watchpoint no strcmp**  
Em vez de `strings`, use o GDB pra interceptar o `strcmp` e ler os argumentos em runtime.  
Mesmo resultado, diferente vetor.

**Variação 2 — patch do strcmp**  
NOP o `strcmp` e force `eax = 0` pra a comparação "sempre acertar".  
Técnica dos desafios 01-03, aplicada aqui como alternativa.

**Pergunta:** se a serial fosse gerada como `SHA256(nome_do_usuário)` em vez de hardcoded,  
qual dessas abordagens ainda funcionaria? Qual não funcionaria mais?

---

## Próximo desafio

**#09 — String Patching**  
Desta vez a lógica não é o alvo.  
O programa sempre nega — mas a mensagem pode mudar.

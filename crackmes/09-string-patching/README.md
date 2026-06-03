# #09 — String Patching

**Nível:** Iniciante-Intermediário  
**Técnica:** Localizar e sobrescrever string no .rodata  
**Ferramentas:** xxd, radare2, dd, python3

---

## A história

Terminal seguro. Autenticador. Que sempre nega.

```
$ ./challenge
╔══════════════════════════════════════╗
║   TERMINAL SEGURO — AUTENTICADOR     ║
╚══════════════════════════════════════╝

Identificador: qualquer

>> ACESSO NEGADO. SAIA.
```

Não tem validação. Não tem comparação. O programa **sempre** imprime a mensagem de negação.  
Você não pode mudar a lógica — a lógica não tem nada a mudar.

Mas a string que ele imprime existe no binário.  
E existe outra string logo ao lado.

Seu objetivo: fazer o terminal imprimir `>> ACESSO CONCEDIDO. BEM-VINDO.`

---

## O que você sabe

No código-fonte:
```c
static const char MSG_DENIED[]  = ">> ACESSO NEGADO. SAIA.        \0";
static const char MSG_GRANTED[] = ">> ACESSO CONCEDIDO. BEM-VINDO.\0";
```

Ambas têm exatamente **32 bytes** (com padding nulo).  
Mesmo comprimento — você pode sobrescrever uma pela outra sem deslocar nada.

---

## Dica

> Usa `strings -o ./challenge` pra ver as strings com os offsets no arquivo.  
> Procura `ACESSO NEGADO`.  
> Agora acha `ACESSO CONCEDIDO` no mesmo arquivo.  
> O que você precisaria copiar de onde pra onde?

---

## Solução

### 1. Localiza as strings no arquivo

```bash
strings -o ./challenge | grep "ACESSO"
```

Resultado (offsets no arquivo):
```
  4096  >> ACESSO NEGADO. SAIA.
  4128  >> ACESSO CONCEDIDO. BEM-VINDO.
```

Ou com `xxd`:
```bash
xxd ./challenge | grep -i "4143455353"  # "ACESS" em ASCII/hex
```

### 2. Confirma os offsets com radare2

```
r2 ./challenge
iz    # lista todas as strings em .rodata com seus endereços
```

Você vai ver os dois endereços:
```
0x00402000  >> ACESSO NEGADO. SAIA.
0x00402020  >> ACESSO CONCEDIDO. BEM-VINDO.
```

### 3. O patch — sobrescreve DENIED com GRANTED

Os bytes de `>> ACESSO CONCEDIDO. BEM-VINDO.\0` têm 32 bytes.  
Você quer escrevê-los no offset de `>> ACESSO NEGADO. SAIA.        \0`.

**Com radare2:**
```
r2 -w ./challenge
s 0x402000
w >> ACESSO CONCEDIDO. BEM-VINDO.
q
```

**Com python3 + dd:**
```python
python3 - << 'EOF'
import subprocess, struct

binary = bytearray(open('./challenge', 'rb').read())

old = b'>> ACESSO NEGADO. SAIA.        \x00'
new = b'>> ACESSO CONCEDIDO. BEM-VINDO.\x00'

idx = binary.find(old)
if idx == -1:
    print("String não encontrada")
else:
    binary[idx:idx+len(new)] = new
    open('./challenge', 'wb').write(binary)
    print(f"Patcheado em offset 0x{idx:x}")
EOF
```

### 4. Verifica

```bash
strings ./challenge | grep "ACESSO"
# Deve mostrar "ACESSO CONCEDIDO" no lugar de "ACESSO NEGADO"
```

### 5. Roda

```bash
./challenge
Identificador: qualquer

>> ACESSO CONCEDIDO. BEM-VINDO.
FLAG{patch_the_string_not_the_logic}
```

---

## Por que funciona

```
antes do patch:

.rodata:
  offset 0x2000: ">> ACESSO NEGADO. SAIA.        \0"  ← main imprime isso
  offset 0x2020: ">> ACESSO CONCEDIDO. BEM-VINDO.\0"  ← nunca executado

depois do patch:

.rodata:
  offset 0x2000: ">> ACESSO CONCEDIDO. BEM-VINDO.\0"  ← main imprime isso agora
  offset 0x2020: ">> ACESSO CONCEDIDO. BEM-VINDO.\0"  ← inalterado
```

Você não tocou em nenhuma instrução. Nenhum byte de código.  
Só substituiu dados. A lógica é a mesma — o que ela imprime mudou.

---

## Por que o tamanho importa

Strings em `.rodata` são contíguas. Se a nova string fosse **maior**, ela invadiria a próxima.  
Se fosse **menor**, sobraria lixo do texto anterior até o próximo `\0`.

Por isso ambas têm 32 bytes com padding — você pode fazer a troca 1:1 sem efeitos colaterais.

Em binários reais, você precisa checar se há espaço antes de patchear qualquer string.  
Strings sem padding são as mais frágeis de alterar.

---

## Variações pra explorar

**Variação 1 — redirecionar o ponteiro da string no .rodata**  
Em vez de sobrescrever `MSG_DENIED`, encontra no disassembly onde o endereço de `MSG_DENIED`  
é carregado (`lea rdi, [rip + offset]`) e troca o offset pra apontar pra `MSG_GRANTED`.  
Mais cirúrgico — a string original fica intacta.

**Variação 2 — injetar nova string no padding do binário**  
ELFs têm áreas de padding entre seções. Você pode escrever uma string nova lá  
e redirecionar o ponteiro pra ela. Útil quando não há espaço na string original.

**Pergunta:** se `MSG_DENIED` e `MSG_GRANTED` tivessem comprimentos diferentes,  
qual das duas abordagens (sobrescrever bytes vs redirecionar ponteiro) ainda funcionaria?

---

## Próximo desafio

**#10 — Licença com Data de Expiração**  
O software sabe que dia é hoje. E sabe que sua licença venceu.  
Mas ele confia no que está escrito — e o que está escrito pode mudar.

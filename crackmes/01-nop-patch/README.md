# #01 — NOP Patch

**Nível:** Iniciante  
**Técnica:** Substituir instrução por NOP (0x90)  
**Ferramentas:** radare2, objdump, xxd + dd

---

## A história

Ativador de software. Licença desconhecida.

```
$ ./challenge
╔══════════════════════════════════════╗
║   ATIVADOR DE SOFTWARE v1.0          ║
╚══════════════════════════════════════╝

Licença: abc123

  ╔════════════════════════════════════╗
  ║  ✗ Licença inválida.              ║
  ╚════════════════════════════════════╝
```

Seu objetivo: fazer aparecer `✓ Licença válida! Software ativado.`  
com qualquer entrada.

---

## O que você sabe

O binário chama `is_valid_key()` pra validar a licença.  
Essa função retorna `1` (válida) ou `0` (inválida).  
O `main` usa esse retorno pra decidir qual mensagem exibir.

E se você apagasse a instrução que decide?

---

## Dica

> Abre o disassembly do `main`.  
> Procura o padrão `call sym.is_valid_key` seguido de `test eax, eax`.  
> O que vem logo depois?  
> E o que acontece se você substituir essa instrução por NOPs?

---

## Conceito: NOP (0x90)

NOP é uma instrução x86 que não faz absolutamente nada.  
O processador avança sem executar nenhuma operação.  
Um byte. Zero efeito. Ocupa espaço, não age.

Substituir instruções por NOPs é a forma mais básica de patch — você não muda o tamanho do binário, não desloca nada, só "apaga" o comportamento daquele byte.

---

## Solução

### 1. Abre no radare2

```bash
r2 -A ./challenge
s main
pdf
```

### 2. Localiza o padrão crítico

```asm
call sym.is_valid_key   ; chama a validação
test eax, eax           ; checa se retornou 0
je   0x...              ; [opcode: 74 xx] se 0, pula pro bloco de erro
```

O `je` é o portão — ele decide qual caminho seguir.

### 3. Pega o endereço exato do `je`

```
pdf~je
```

### 4. Patcha com dois NOPs

```
s <endereço do je>
wx 9090
```

### 5. Verifica o patch

```
pd 2 @ <endereço>   ; deve mostrar: nop; nop
```

### 6. Salva e roda

```bash
oo+
q
./challenge
```

---

## Por que funciona

```
antes do patch:

is_valid_key("abc123") → retorna 0
test eax, eax          → ZF = 1
je  0x...              → ZF=1, pula → bloco de erro ✗

depois do patch:

is_valid_key("abc123") → retorna 0
test eax, eax          → ZF = 1
nop; nop               → não pula, segue em frente → bloco de sucesso ✓
```

O `je` ocupa 2 bytes. Dois NOPs também. Troca 1:1 sem deslocar nada.

---

## Alternativas de patch

| Método | Opcode | Efeito |
|--------|--------|--------|
| NOP NOP | `90 90` | Apaga o jump |
| Trocar `je` por `jne` | `75 xx` | Inverte a lógica |
| Trocar `je` por `jmp` | `EB xx` | Jump incondicional |

O opcode original do `je` é `74 xx` onde `xx` é o offset do salto.

---

## Próximo desafio

**#02 — Patch de Retorno**  
Desta vez, o jump não é o alvo.  
A própria função precisa aprender a mentir.

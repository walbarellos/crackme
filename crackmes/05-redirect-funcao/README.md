# #05 — Redirect de Função

**Nível:** Iniciante-Intermediário  
**Técnica:** Redirecionar um `call` para outra função  
**Ferramentas:** objdump, radare2, python3

---

## A história

Terminal de acesso remoto. Usuário e senha desconhecidos.

```
$ ./challenge
╔══════════════════════════════════╗
║   TERMINAL DE ACESSO REMOTO      ║
╚══════════════════════════════════╝
Usuario: hacker
Senha:   qualquer

  ╔══════════════════════════════════╗
  ║  ACESSO NEGADO                   ║
  ║  Credenciais invalidas.           ║
  ╚══════════════════════════════════╝
```

Você sabe que existe uma função `access_granted()` em algum lugar no binário.  
Ela nunca é chamada com suas credenciais.

Mas e se você mudasse **quem** é chamado?

---

## O que você sabe

O binário tem duas funções:
- `access_denied()` → chamada quando credenciais são inválidas
- `access_granted()` → chamada quando são válidas

A instrução `call` em x86-64 não guarda o endereço absoluto do destino.  
Ela guarda um **offset relativo** — a distância entre a próxima instrução e o destino.

Trocar esse offset redireciona a chamada para qualquer função que você quiser.

---

## Dica

> Abre o disassembly e procura as duas funções: `access_denied` e `access_granted`.  
> Anota os endereços de cada uma.  
> Agora procura onde `access_denied` é chamada dentro de `authenticate`.  
> O que você precisaria mudar pra esse `call` ir parar em `access_granted`?

---

## Solução

### 1. Mapeia as funções

```bash
objdump -d ./challenge | grep -E "<access_denied>|<access_granted>|<authenticate>"
```

Resultado:
```
4011b6 <access_denied>
401204 <access_granted>
401278 <authenticate>
```

### 2. Encontra os call sites dentro de authenticate

```bash
objdump -d ./challenge | grep -A 5 "<authenticate>:" | grep call
```

Ou mais direto:
```bash
objdump -d ./challenge | grep "call.*access"
```

Você vai ver:
```asm
4012c5:  e8 3a ff ff ff   call  401204 <access_granted>   ← caminho válido
4012d1:  e8 e0 fe ff ff   call  4011b6 <access_denied>    ← seu alvo
```

### 3. Entende o encoding do call

A instrução `call` relativa usa 5 bytes:
```
e8 [offset de 4 bytes em little-endian]
```

O offset é calculado assim:
```
offset = endereço_destino - endereço_da_próxima_instrução
```

A próxima instrução após o `call` em `0x4012d1` é `0x4012d6` (0x4012d1 + 5).

Para redirecionar para `access_granted` em `0x401204`:
```python
offset = 0x401204 - 0x4012d6 = -0xd2
```

Em little-endian com sinal (32 bits): `2e ff ff ff`

Portanto o novo `call` fica:
```
e8 2e ff ff ff   →   call 401204 <access_granted>
```

### 4. Calcula o offset com python

```python
python3 -c "
import struct
call_addr  = 0x4012d1
next_instr = call_addr + 5
target     = 0x401204
offset     = target - next_instr
b = struct.pack('<i', offset)
print(f'patch bytes: e8 {b.hex()}')
"
# patch bytes: e8 2effffff
```

### 5. Aplica o patch

**Com radare2:**
```
r2 -w ./challenge
s 0x4012d1
wx e8 2e ff ff ff
q
```

**Com dd:**
```bash
printf '\xe8\x2e\xff\xff\xff' | dd of=./challenge bs=1 seek=$((0x4012d1)) conv=notrunc 2>/dev/null
```

### 6. Verifica

```bash
objdump -d ./challenge | grep "4012d1"
```

Deve mostrar:
```asm
4012d1:  e8 2e ff ff ff   call  401204 <access_granted>
```

Agora **ambos** os caminhos em `authenticate` chamam `access_granted`.

### 7. Roda

```bash
./challenge
Usuario: qualquer
Senha:   qualquer

  ╔══════════════════════════════════╗
  ║  ACESSO AUTORIZADO               ║
  ║  Bem-vindo, operador.             ║
  ║  > FLAG{redirect_the_call}        ║
  ╚══════════════════════════════════╝
```

---

## Por que funciona

```
antes do patch:

authenticate("hacker", "wrong")
  → strcmp falha
  → call 0x4011b6   ← access_denied


depois do patch:

authenticate("hacker", "wrong")
  → strcmp falha
  → call 0x401204   ← access_granted  ✓
```

O `call` relativo em x86-64 não sabe o nome da função.  
Ele só sabe a distância. Você trocou a distância.

---

## A matemática do call relativo

```
instrução call em 0x4012d1:
  e8 [offset]

CPU executa assim:
  RIP = 0x4012d1 + 5 = 0x4012d6   (avança pro próximo)
  RIP = RIP + offset_signed        (aplica o salto)

para ir a 0x401204:
  offset = 0x401204 - 0x4012d6 = -0xD2

-0xD2 em i32 little-endian = 2E FF FF FF
```

Isso vale pra qualquer `call` relativo no x86-64.  
Guarda esse cálculo — vai usar muito.

---

## Variações pra explorar

**Variação 1 — redirecionar o call de authenticate no main**  
Em vez de mexer dentro de `authenticate`, redireciona o próprio `call authenticate`  
no `main` (endereço `0x40137f`) direto pra `access_granted`.  
A função `authenticate` nem executa.

**Variação 2 — NOP no call de access_denied**  
5 NOPs (`90 90 90 90 90`) no lugar do `call access_denied`.  
O programa não chama nenhuma das duas e retorna normalmente.  
Funciona, mas o output fica estranho. Por quê?

**Pergunta:** se o binário tivesse PIE ativado (endereços aleatorizados a cada execução),  
esse patch ainda funcionaria? O que mudaria no cálculo?

---

## Próximo desafio

**#06 — Keygen Simples**  
Chega de patchear.  
Desta vez você vai entender o algoritmo e gerar uma licença válida do zero.

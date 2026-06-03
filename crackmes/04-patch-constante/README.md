# #04 — Patch de Constante

**Nível:** Iniciante  
**Técnica:** Localizar e modificar constante hardcoded  
**Ferramentas:** objdump, radare2, xxd, strings

---

## A história

Cofre digital. Três tentativas. PIN desconhecido.

```
$ ./challenge
╔══════════════════════════════════╗
║     COFRE DIGITAL v2.0           ║
╚══════════════════════════════════╝

Senha (3 tentativa(s) restante(s)): 1234
  ✗ Senha incorreta.

Senha (2 tentativa(s) restante(s)): 9999
  ✗ Senha incorreta.

Senha (1 tentativa(s) restante(s)): 0000

  ✗ Cofre bloqueado. Muitas tentativas.
```

Desta vez não tem função pra patchear.  
Não tem jump pra inverter.  
A senha está gravada em algum lugar dentro do binário.

Seu objetivo: descobrir ou alterar essa constante.

---

## O que você sabe

O binário compara sua entrada com um valor fixo.  
Esse valor foi definido em tempo de compilação.  
Ele está no disassembly, esperando ser encontrado.

Duas abordagens possíveis:
1. **Ler** a constante → descobrir a senha → entrar normalmente
2. **Trocar** a constante → mudar o que o binário aceita como válido

Ambas são válidas. Uma é mais elegante.

---

## Dica

> Abre o disassembly do `main`.  
> Procura uma instrução `cmp` comparando um registrador com um número.  
> Esse número é a senha — mas em qual base está?

---

## Solução

### Abordagem 1 — Ler a constante (a mais rápida)

```bash
objdump -d ./challenge | grep "cmp"
```

Você vai encontrar:

```asm
401235:  cmp  $0x1c7b, %eax
```

`0x1c7b` em decimal:

```bash
python3 -c "print(0x1c7b)"
# 7291
```

Pronto. A senha é `7291`. Sem tocar no binário.

```
$ ./challenge
Senha (3 tentativa(s) restante(s)): 7291

  ✓ Cofre aberto. Bem-vindo.
  > Conteudo: FLAG{patch_the_constant}
```

---

### Abordagem 2 — Trocar a constante (o patch)

E se você quisesse que `1234` fosse a senha válida?

`1234` em hex = `0x4d2`  
Em little-endian 4 bytes: `d2 04 00 00`

O `cmp` em `0x401235` tem o encoding:
```
3d 7b 1c 00 00   →   cmp $0x1c7b, %eax
```

Os 4 bytes após `3d` são a constante em little-endian: `7b 1c 00 00`.  
Você quer trocar por `d2 04 00 00` (1234 em little-endian).

**Com radare2:**
```
r2 -w ./challenge
s 0x401236
wx d2 04 00 00
q
```

**Com dd:**
```bash
printf '\xd2\x04\x00\x00' | dd of=./challenge bs=1 seek=$((0x401236)) conv=notrunc 2>/dev/null
```

Verifica:
```bash
objdump -d ./challenge | grep "cmp.*%eax"
# 401235:  cmp  $0x4d2, %eax
```

Agora `1234` abre o cofre.

---

## Por que o número aparece "estranho" no disassembly

O processador armazena inteiros em **little-endian** — o byte menos significativo primeiro.

`7291` em hex é `0x00001C7B`.  
Na memória (e no binário): `7B 1C 00 00`.  
No disassembly o objdump já converte pra você: mostra `$0x1c7b`.

Mas se você abrir o binário em hex bruto com `xxd`:
```bash
xxd ./challenge | grep -A 1 "1c7b"
```

Vai ver os bytes na ordem inversa. Isso vai importar muito nos próximos desafios.

---

## Bônus — strings

Antes de qualquer disassembly, tente sempre:

```bash
strings ./challenge
```

Em binários simples, constantes de texto aparecem em claro.  
PINs numéricos não aparecem (são inteiros, não strings), mas senhas em texto puro sim.  
Guardar esse hábito vai economizar tempo nos desafios futuros.

---

## Variações pra explorar

**Variação 1 — mudar o número de tentativas**  
O loop compara `tries` com `$0x2` em `0x401274`:
```asm
401274:  cmpl  $0x2, -0x4(%rbp)
```
Troca `02` por `63` (99 tentativas). Agora você tem tempo de sobra pra brutar.

**Variação 2 — brutar direto**  
São 4 dígitos. 10.000 combinações.  
Escreve um script que testa tudo:
```bash
for i in $(seq 0 9999); do
    result=$(echo "$i" | ./challenge 2>/dev/null)
    if echo "$result" | grep -q "Cofre aberto"; then
        echo "PIN: $i"
        break
    fi
done
```
Funciona, mas é lento e deixa rastro. O patch é mais elegante.

**Pergunta:** qual das abordagens (ler, patchear, brutar) você usaria  
se o binário verificasse a integridade de si mesmo?

---

## Próximo desafio

**#05 — Redirect de Função**  
O programa chama a função certa.  
Mas e se você fizesse ele chamar outra?

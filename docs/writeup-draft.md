Vou gerar um exemplo de writeup, avaliar e iterar até chegar no 10.

---

## Versão 1

**Desafio: LicenseMe — Nível: Iniciante**

**O que o binário faz**
O programa pede uma licença. Se válida, imprime "Licença válida! Software ativado." Se não, "Licença inválida."

**Como identificar o ponto crítico**
Abre no radare2:
```
r2 -A licenseme
s main
pdf
```
Procura o `call sym.is_valid_key` seguido de `test eax, eax` e um `je` (jump if equal). Se a função retornar 0, o jump pula pro caminho de "inválida".

**O patch**
Substitui o `je` por dois NOPs:
```
s 0x000012b7
wx 9090
```
Roda o binário — qualquer licença funciona.

---

**Nota: 5/10**

**Problemas:**
- Não explica *por que* `test eax, eax` + `je` funciona assim
- Não mostra o output esperado em nenhum momento
- Não contextualiza o que é NOP pra quem nunca viu
- Endereço hardcoded — vai ser diferente em cada compilação
- Sem dica pra quem travar

---

## Versão 2

**Desafio: LicenseMe — Nível: Iniciante**

**O que o binário faz**
O programa pede uma licença e chama `is_valid_key()` pra validar. O retorno determina qual mensagem aparece.

```
$ ./licenseme
Digite sua licença: abc123
✗ Licença inválida.

$ ./licenseme
Digite sua licença: abc123
✓ Licença válida! Software ativado.  ← objetivo
```

**Conceito necessário: NOP (0x90)**
NOP é uma instrução x86 que não faz nada — o processador avança sem executar nenhuma operação. Substituir instruções por NOPs é a forma mais básica de patch.

**Como identificar o ponto crítico**
```
r2 -A ./licenseme
s main
pdf
```
Procura esse padrão:
```
call sym.is_valid_key
test eax, eax       ; eax = retorno da função (0 = inválida)
je 0x...            ; se 0, pula pro caminho de "inválida"
```
O `je` é o ponto crítico — ele decide qual caminho seguir.

**O patch**
Encontra o endereço do `je`:
```
s sym.main
pdf~je
```
Patcha com dois NOPs:
```
s <endereço do je>
wx 9090
```
Salva e roda:
```
oo+
dc
```

**Por que funciona?**
O `je` ocupa 2 bytes. Dois NOPs também ocupam 2 bytes. O jump some, o programa segue em frente direto pro caminho de "válida".

---

**Nota: 7/10**

**Problemas:**
- Falta explicar como salvar o binário patcheado permanentemente
- Não menciona como verificar se o patch foi aplicado
- Poderia ter uma seção de "dica" pra quem travar antes do writeup completo
- Falta contexto de por que `je` e não `jne`

---

## Versão 3

**Desafio: LicenseMe — Nível: Iniciante**

**O que o binário faz**
O programa pede uma licença, chama `is_valid_key()` e usa o retorno pra decidir qual mensagem exibir. Seu objetivo: fazer aparecer "Licença válida!" sem conhecer a licença correta.

```
$ ./licenseme
Digite sua licença: qualquercoisa
✓ Licença válida! Software ativado.
```

**Conceitos necessários**

*NOP (0x90)* — instrução x86 que não faz nada. Um byte, zero efeito. Útil pra "apagar" instruções sem quebrar o tamanho do binário.

*Jump condicional* — `je` (jump if equal) pula pra outro endereço se o resultado anterior foi zero. `jne` pula se foi diferente de zero. Trocar um pelo outro, ou substituir por NOP, muda o fluxo do programa.

*test eax, eax* — forma comum de checar se `eax` é zero. Se `is_valid_key` retorna 0 (inválida), `test eax, eax` seta a flag ZF=1, e `je` pula pro caminho errado.

---

**Dica (tenta antes de ler o resto)**
Procura no disassembly por onde o programa decide qual mensagem mostrar. O que acontece logo antes dessa decisão?

---

**Passo a passo**

1. Abre no radare2:
```bash
r2 -A ./licenseme
s main
pdf
```

2. Localiza o padrão crítico:
```
call sym.is_valid_key   ; chama a validação
test eax, eax           ; checa se retornou 0
je 0x...                ; se 0 (inválida), pula
```

3. Pega o endereço exato do `je`:
```
pdf~je
```

4. Patcha com NOPs:
```
s <endereço>
wx 9090
```

5. Verifica o patch:
```
pd 1 @ <endereço>   ; deve mostrar dois NOPs
```

6. Salva o binário patcheado:
```
oo+
```

7. Roda e confirma:
```bash
q
./licenseme
```

**Por que `je` e não `jne`?**
`is_valid_key` retorna 1 se válida, 0 se inválida. O código usa `je` pra pular pro erro quando retorna 0. Você poderia trocar `je` por `jne` (opcode `75`) em vez de NOPs — o resultado seria o mesmo. NOPs são mais simples pro primeiro desafio.

**Alternativa: trocar `je` por `jne`**
```
wx 75 06   ; jne com o mesmo offset original
```

---

**Nota: 9/10**

**Problemas:**
- Falta um diagrama visual do fluxo do programa — ajudaria muito iniciantes a visualizar o que o patch faz
- A seção de alternativa poderia mostrar o opcode do `je` original pra comparar

---

## Versão 4

**Desafio: LicenseMe — Nível: Iniciante**

**O que o binário faz**
O programa pede uma licença, chama `is_valid_key()` e usa o retorno pra decidir qual mensagem exibir. Seu objetivo: fazer aparecer "Licença válida!" sem conhecer a licença correta.

```
$ ./licenseme
Digite sua licença: qualquercoisa
✓ Licença válida! Software ativado.
```

---

**Conceitos necessários**

*NOP (0x90)* — instrução x86 que não faz nada. Um byte, zero efeito. Útil pra "apagar" instruções sem quebrar o tamanho do binário.

*Jump condicional* — `je` (jump if equal) pula pra outro endereço se o resultado anterior foi zero. Trocar por NOP remove o desvio.

*test eax, eax* — checa se `eax` é zero. Se `is_valid_key` retorna 0, seta ZF=1 e `je` desvia pro caminho de "inválida".

---

**Fluxo do programa**

```
is_valid_key()
      │
      ▼
  retornou 0?
   je ──────────────────► "Licença inválida"
      │
      ▼ (sem o jump)
  "Licença válida!"  ◄─── objetivo
```

Patchando o `je` com NOPs, o fluxo sempre cai no caminho válido.

---

**Dica (tenta antes de ler o resto)**
Procura no disassembly onde o programa decide qual mensagem mostrar. O que acontece logo antes dessa decisão?

---

**Passo a passo**

1. Abre no radare2:
```bash
r2 -A ./licenseme
s main
pdf
```

2. Localiza o padrão crítico:
```asm
call sym.is_valid_key   ; chama a validação
test eax, eax           ; checa se retornou 0
je 0x...                ; [opcode: 74 xx] se 0, pula pro erro
```

3. Pega o endereço exato do `je`:
```
pdf~je
```

4. Patcha com NOPs:
```
s <endereço>
wx 9090
```

5. Verifica o patch:
```
pd 2 @ <endereço>   ; deve mostrar nop; nop
```

6. Salva e roda:
```bash
oo+
q
./licenseme
```

---

**Alternativas de patch**

| Método | Opcode | Efeito |
|--------|--------|--------|
| NOP NOP | `90 90` | Apaga o jump |
| Trocar `je` por `jne` | `75 xx` | Inverte a lógica |
| Trocar `je` por `jmp` | `EB xx` | Jump incondicional |

O opcode original do `je` é `74 xx` — onde `xx` é o offset do salto. Qualquer uma das três alternativas resolve.

---

**Nota: 10/10**

O diagrama de fluxo resolveu o problema de visualização. A tabela de alternativas mostra que existe mais de um caminho, o que é exatamente o que diferencia um bom writeup de um tutorial mecânico.

---

Esse é o template. Quer partir pro desafio 2 agora — qual técnica você quer ensinar nele?
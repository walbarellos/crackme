# RE Toolkit — Andaimes Cognitivos

Scripts que te fazem **pensar**, não que resolvem por você.

A diferença entre isso e os scripts da pasta `/scripts` de cada crackme:

| Scripts originais | Este toolkit |
|-------------------|--------------|
| Executam a solução | Estruturam seu raciocínio |
| Você roda, ele resolve | Você pensa, ele guia |
| Funcionam para UM desafio | Funcionam para QUALQUER binário |
| Você aprende a usar o script | Você aprende a técnica |

---

## Scripts

### `think.py` — Andaime socrático

O principal. Guia você por módulos de análise com perguntas socráticas.

```bash
python3 think.py <binário> <modo>

Modos:
  --recon       Reconhecimento inicial (file, strings, nm)
  --flow        Fluxo de controle (onde está a decisão?)
  --algo        Análise de algoritmo (lendo de trás pra frente)
  --patch       Planejamento de patch (o quê, onde, quais bytes)
  --keygen      Estrutura para implementar keygen
  --bruteforce  Estratégia de enumeração inteligente
```

**Fluxo típico:**
```
--recon → --flow → --algo → --patch
                          → --keygen
                          → --bruteforce
```

---

### `patterns.py` — Vocabulário de padrões assembly

Menu interativo com os padrões mais comuns em crackmes.
Para cada padrão: o que é, o que significa, e as perguntas que você
**deveria estar fazendo** ao ver ele.

```bash
# Menu interativo
python3 patterns.py

# Padrão específico direto
python3 patterns.py retorno-funcao
python3 patterns.py strcmp-pattern
python3 patterns.py loop-acumulador
python3 patterns.py time-check
python3 patterns.py anti-debug-ptrace
python3 patterns.py xor-decode
```

---

### `hypothesis.py` — Framework de investigação

Estrutura o raciocínio científico: observação → hipótese → teste → conclusão.
Salva um log que você pode revisar, exportar como Markdown, e usar como writeup.

```bash
python3 hypothesis.py crackme-01
python3 hypothesis.py keygen-simples

# Dentro do prompt:
# [o] nova observação
# [h] nova hipótese
# [r] resultado de um teste
# [c] conclusão
# [l] ver log completo
# [e] exportar como .md
```

Logs ficam em `~/.re_investigations/`.

---

### `decode.py` — Expande constantes

Você encontra `0x7C` no disassembly e não sabe o que é.
O script mostra **todas** as interpretações possíveis e faz perguntas
contextuais para te ajudar a decidir qual faz sentido.

```bash
python3 decode.py 0x7C        # → 124, 'struct tm year = 2024', ...
python3 decode.py 1337        # → 0x539, primo, leet, ...
python3 decode.py "7c 00 00 00"  # → bytes little-endian
python3 decode.py 0xDEADBEEF  # → marcador conhecido
```

---

## Filosofia

Esses scripts implementam o **template de pensamento de engenharia reversa**:

```
1. OBSERVAR    — o que eu vejo no binário?
2. INFERIR     — o que isso provavelmente significa?
3. HIPOTETIZAR — se eu estiver certo, o que deveria acontecer quando eu testar X?
4. TESTAR      — executar o teste específico
5. CONCLUIR    — confirmar ou revisar a hipótese
```

O erro que o Gemini e outros LLMs fazem é pular direto para o passo 4
sem passar pelos passos 1–3. Isso resolve o exercício mas não constrói
a intuição.

Esses scripts **forçam os passos 1–3** antes de qualquer ação.

---

## Progressão recomendada por desafio

**Nível 1 (NOP/patch):**
```
think.py --recon → think.py --flow → think.py --patch
```

**Nível 2 (keygen):**
```
think.py --recon → think.py --flow → think.py --algo → think.py --keygen
patterns.py loop-acumulador
decode.py <constantes que você achar>
```

**Qualquer nível com hipóteses não óbvias:**
```
hypothesis.py <nome-do-desafio>
```

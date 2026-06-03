#!/usr/bin/env python3
"""
think.py — Andaime socrático para RE
Faz você pensar. Não resolve nada por você.
"""

import subprocess
import sys
import os
import shutil

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
MAGENTA= "\033[95m"

def hr(char="─", color=DIM):
    w = shutil.get_terminal_size((80, 24)).columns
    print(f"{color}{char * w}{RESET}")

def ask(prompt, choices=None):
    print(f"\n{CYAN}?{RESET} {BOLD}{prompt}{RESET}")
    if choices:
        for i, c in enumerate(choices, 1):
            print(f"  {DIM}{i}.{RESET} {c}")
        while True:
            r = input(f"\n{DIM}>{RESET} ").strip()
            if r.isdigit() and 1 <= int(r) <= len(choices):
                return int(r), choices[int(r)-1]
            if r.lower() in [c.lower() for c in choices]:
                idx = [c.lower() for c in choices].index(r.lower())
                return idx+1, choices[idx]
            print(f"  {RED}Digite o número ou a opção.{RESET}")
    else:
        return input(f"{DIM}>{RESET} ").strip()

def reveal(text, label="Dica"):
    print(f"\n{DIM}[pressione Enter para ver {label}]{RESET}")
    input()
    hr("·", YELLOW)
    print(f"{YELLOW}{text}{RESET}")
    hr("·", YELLOW)

def section(title):
    print(f"\n{BOLD}{BLUE}{'━'*4} {title} {'━'*4}{RESET}")

# ─────────────────────────────────────────────
# MÓDULO 1 — Reconhecimento inicial
# ─────────────────────────────────────────────

def recon(binary):
    section("RECONHECIMENTO — O que você está olhando?")

    print(f"""
{DIM}Antes de abrir qualquer disassembly, um bom reverseiro responde
três perguntas básicas sobre o alvo.{RESET}
""")

    # Pergunta 1: tipo de arquivo
    print(f"{BOLD}1. O que é esse arquivo?{RESET}")
    print(f"   {DIM}Execute:{RESET}  file {binary}")
    print(f"   {DIM}Depois:{RESET}   readelf -h {binary} 2>/dev/null | head -20\n")

    ans = ask("O que você viu? O binário é:")
    possible = ["ELF 64-bit", "ELF 32-bit", "não é ELF / outro formato", "não sei ler a saída ainda"]
    n, choice = ask("O binário é:", possible)
    
    if n == 4:
        reveal("""O campo 'Class' do readelf diz:
  ELF64 → binário de 64 bits (registradores rax, rdi, rsi...)
  ELF32 → binário de 32 bits (registradores eax, edi, esi...)
  
O campo 'Type' diz:
  EXEC → endereços fixos (mais fácil pra patch estático)
  DYN  → PIE — base randômica (precisa de ASLR off ou calcular delta)
  
Isso importa porque o offset que você acha no objdump pode não ser
o endereço real em execução se o binário for PIE.""", "explicação")
    
    # Pergunta 2: stripped?
    section("")
    print(f"{BOLD}2. O binário tem símbolos (nomes de função)?{RESET}")
    print(f"   {DIM}Execute:{RESET}  nm {binary} 2>/dev/null | grep -i 'valid\\|check\\|auth\\|key\\|main'")
    print(f"   {DIM}Ou:{RESET}       file {binary} | grep -o 'stripped\\|not stripped'\n")

    n, choice = ask("O que você encontrou:", [
        "Tem nomes de função visíveis (ex: is_valid_key, check_license)",
        "Stripped — sem símbolos",
        "Não sei interpretar a saída"
    ])
    
    if n == 1:
        print(f"\n  {GREEN}✓ Ótimo.{RESET} Nomes visíveis são um mapa. Quais funções aparecem que parecem")
        print(f"  relevantes para a validação? Anote-as.")
        ans = ask("Qual função você acha que faz a validação principal?")
        print(f"\n  {DIM}Interessante. Guarde esse nome — vamos usá-lo daqui a pouco.{RESET}")
    
    elif n == 2:
        reveal("""Stripped = sem nomes de função. Estratégia:
  
  1. Acha o main via entry point:
     objdump -d {bin} | grep '<_start>' -A 10
     O último 'call' antes do hlt geralmente é main.
  
  2. Procura por padrões de comportamento:
     strings {bin} | grep -i 'válid\\|invalid\\|licença\\|chave'
     As strings de output são sua âncora — localize-as no disassembly.
  
  3. No radare2: aaf + s main + pdf já nomeia heurísticas.""", "estratégia para stripped")
    
    elif n == 3:
        reveal("""nm lista símbolos do binário.
  'T' = função definida no texto (código)
  'U' = função usada mas definida em lib externa (ex: printf, strcmp)
  
  Se 'nm' não retornar nada útil, tente:
    readelf -s {binary}
  
  Se ambos derem vazio → stripped. Veja dica acima.""", "interpretação do nm")

    # Pergunta 3: strings
    section("")
    print(f"{BOLD}3. Quais strings interessantes existem no binário?{RESET}")
    print(f"   {DIM}Execute:{RESET}  strings {binary}\n")
    
    print(f"  {DIM}O que procurar:{RESET}")
    print(f"    • Mensagens de sucesso/falha")
    print(f"    • Constantes que parecem chaves/tokens")
    print(f"    • Nomes de função de sistema (strcmp, atoi, time, ...)")
    print(f"    • Strings de formato (%d, %s, ...)")
    
    ans = ask("Que strings chamaram sua atenção? (descreva ou liste)")
    
    print(f"\n  {DIM}Guarde essas strings. Elas são:{RESET}")
    print(f"    {GREEN}a){RESET} Âncoras para achar o ponto crítico no disassembly")
    print(f"    {GREEN}b){RESET} Evidência do comportamento esperado")
    print(f"    {GREEN}c){RESET} Às vezes, a própria resposta está aqui (serial fishing)")

    print(f"\n{GREEN}✓ Reconhecimento concluído.{RESET}")
    print(f"  {DIM}Próximo passo:{RESET} use {CYAN}python3 think.py {binary} --flow{RESET} para mapear o fluxo.")


# ─────────────────────────────────────────────
# MÓDULO 2 — Mapeamento de fluxo
# ─────────────────────────────────────────────

def flow(binary):
    section("FLUXO DE CONTROLE — Onde está a decisão?")
    
    print(f"""
{DIM}Todo crackme tem um ponto de decisão — o lugar onde o programa
decide "sim" ou "não". Seu trabalho é achar esse ponto.{RESET}
""")
    
    print(f"{BOLD}Ferramenta:{RESET} objdump ou radare2\n")
    print(f"  {DIM}objdump:{RESET}  objdump -d -M intel {binary} | less")
    print(f"  {DIM}r2:{RESET}       r2 -A {binary}  →  s main  →  pdf\n")

    # Pergunta sobre o tipo de check
    n, tipo = ask("Qual é o tipo de verificação do desafio que você está analisando:", [
        "Compara input com valor hardcoded (strcmp, ==)",
        "Função retorna 0 ou 1 (válido/inválido)",
        "Cálculo/algoritmo — gera valor esperado e compara",
        "Ainda não sei — preciso olhar primeiro"
    ])

    if n == 4:
        print(f"\n  {CYAN}Ótimo ponto de partida.{RESET} Abra o disassembly e procure por:")
        print(f"""
    {YELLOW}Padrão 1 — Retorno de função:{RESET}
      call  <alguma_funcao>
      test  eax, eax        ← checa se retornou 0
      je/jne <endereço>     ← ← ← AQUI está a decisão

    {YELLOW}Padrão 2 — Comparação direta:{RESET}
      cmp   eax, <valor>    ← compara com constante
      je/jne <endereço>

    {YELLOW}Padrão 3 — strcmp:{RESET}
      call  strcmp@plt
      test  eax, eax
      jne   <falha>         ← se não iguais, pula pro erro
""")
        ans = ask("Você encontrou algum desses padrões? O que viu?")
        print(f"\n  {DIM}Descreva a instrução exata e o endereço. Isso é sua âncora.{RESET}")
        
    elif n == 1:
        print(f"\n  {CYAN}strcmp retorna 0 se as strings são iguais.{RESET}")
        print(f"""
    No disassembly você vai ver:
      call  strcmp@plt
      test  eax, eax    ← eax == 0 significa "iguais"
      jne   <falha>     ← se diferente de zero (≠ iguais), vai pro erro
    
    {BOLD}Pergunta:{RESET} se você quer forçar o caminho de sucesso, qual instrução você tocaria?
    
    Pense: o que 'jne' faz? O que acontece se você trocar por 'je'? 
    Por 'jmp'? Por dois NOPs?
    
    {DIM}Não existe uma única resposta — cada abordagem tem trade-offs.{RESET}
""")

    elif n == 2:
        print(f"""
    {CYAN}Função de validação com retorno 0/1.{RESET}
    
    Você tem duas estratégias principais:
    
    {YELLOW}A) Patch no jump (main){RESET}
       Acha o 'test eax, eax' + 'je/jne' depois do call.
       Pergunta: o jump vai pro sucesso ou pro fracasso?
       → Se vai pro fracasso: NOP o jump = sempre sucesso
       → Se vai pro sucesso: inverte para 'jmp' incondicional
    
    {YELLOW}B) Patch na função (retorno){RESET}
       Força a função a sempre retornar 1.
       Padrão: 'mov eax, 0' no epílogo → troca por 'mov eax, 1'
       
    {BOLD}Qual você prefere explorar? Por quê?{RESET}
""")
        ans = ask("Sua escolha e raciocínio:")
        print(f"\n  {DIM}Boa análise. Agora encontre o endereço exato no disassembly{RESET}")
        print(f"  {DIM}e use {CYAN}python3 think.py {binary} --patch{RESET} para o próximo passo.{RESET}")

    elif n == 3:
        print(f"""
    {CYAN}Algoritmo de validação.{RESET}
    
    Aqui a abordagem muda — você precisa entender o algoritmo,
    não só patchear um jump.
    
    {BOLD}Mapa mental para algoritmos:{RESET}
    
    1. Onde está o input?  (scanf, fgets, atoi...)
    2. O que é feito com ele?  (loop? operação aritmética? hash?)
    3. O que é o "esperado"?  (hardcoded? calculado a partir de algo?)
    4. Onde é a comparação final?  (cmp, test, strcmp)
    
    {DIM}Comece do final (comparação) e vá voltando para entender
    de onde vem cada operando. É engenharia reversa no sentido literal.{RESET}
    
    Use {CYAN}python3 think.py {binary} --algo{RESET} para análise de algoritmo guiada.
""")

    print(f"\n{GREEN}✓ Mapeamento concluído.{RESET}")


# ─────────────────────────────────────────────
# MÓDULO 3 — Análise de algoritmo
# ─────────────────────────────────────────────

def algo(binary):
    section("ANÁLISE DE ALGORITMO — Lendo de trás pra frente")
    
    print(f"""
{DIM}A técnica de engenharia reversa de algoritmos começa no resultado
e vai voltando até o input. É como ler uma receita de bolo
descobrindo os ingredientes a partir do prato pronto.{RESET}
""")

    hr()
    print(f"\n{BOLD}PASSO 1 — Ache a comparação final{RESET}")
    print(f"""
  No disassembly, procure o ponto onde o programa decide "válido/inválido".
  Vai ter um padrão como:
  
    cmp   eax, edx        ← compara dois valores calculados
    je    <sucesso>
  
  ou:
    call  strcmp
    test  eax, eax
    jne   <falha>
  
  {DIM}Antes de continuar, anote:{RESET}
    • Endereço da comparação: _______________
    • Operandos sendo comparados: ___ vs ___
""")
    input(f"  {DIM}[Enter quando anotou]{RESET} ")
    
    print(f"\n{BOLD}PASSO 2 — Rastreie cada operando de volta{RESET}")
    print(f"""
  Para cada operando da comparação, faça a pergunta:
  
    {CYAN}"De onde esse valor veio?"{RESET}
  
  Suba o código linha por linha e responda:
    • É resultado de uma função? → Entre na função e repita.
    • É lido de uma variável? → De onde essa variável foi preenchida?
    • É calculado inline? → Qual operação? Loop ou sequencial?
    • É o próprio input? → Como o input chegou aqui?
  
  {YELLOW}Dica:{RESET} desenhe num papel. Setas. Caixas. O disassembly é um grafo.
""")
    n, _ = ask("Qual dos operandos é mais fácil de rastrear:", [
        "O esperado (gerado pelo programa)",
        "O fornecido (vem do usuário)",
        "Não consigo distinguir qual é qual ainda"
    ])
    
    if n == 3:
        reveal("""Para distinguir operando do input vs operando gerado:

  O do INPUT vem de:
    scanf / fgets / argv → geralmente acaba em rdi/rsi passado como arg
    Vai aparecer na call como parâmetro.
  
  O GERADO pelo programa:
    É calculado internamente — vai ter uma sequência de instruções
    acumulando um valor antes da comparação.
    Frequentemente em eax/rax no momento da comparação.

  Truque rápido: coloque um breakpoint na comparação com gdb:
    gdb ./challenge
    b *<endereço_da_cmp>
    run
    (insira qualquer input)
    info registers
    
  Os valores de eax e edx ali são o que está sendo comparado.
  Um deles vai ser o seu input (ou derivado). O outro é o esperado.""", "como distinguir operandos")

    print(f"\n{BOLD}PASSO 3 — Reconstrua em pseudocódigo{RESET}")
    print(f"""
  Traduza o que você viu para pseudocódigo de alto nível:
  
  {DIM}Exemplo:{RESET}
    {YELLOW}Assembly que você viu:{RESET}
      imul eax, [name_len]
      add  eax, 0x539
      xor  eax, ebx
    
    {YELLOW}Seu pseudocódigo:{RESET}
      resultado = entrada * comprimento_do_nome
      resultado = resultado + 1337
      resultado = resultado XOR <algo>
  
  Escreva o pseudocódigo do que você viu:
""")
    ans = ask("Seu pseudocódigo (pode ser aproximado):")
    
    print(f"\n  {DIM}Bom. Agora a pergunta crítica:{RESET}")
    print(f"""
  {BOLD}Esse algoritmo é reversível?{RESET}
  
  • {GREEN}XOR{RESET} → sim, reversível (XOR consigo mesmo desfaz)
  • {GREEN}Adição/subtração{RESET} → sim, reversível
  • {GREEN}Multiplicação{RESET} → sim SE o módulo for primo e o fator for coprime
  • {YELLOW}Módulo (%)${RESET} → não reversível diretamente — mas você pode enumerar
  • {RED}Hash (CRC, MD5...){RESET} → não reversível — precisa de outra abordagem
""")
    n, _ = ask("O algoritmo que você mapeou parece:", [
        "Reversível — posso calcular o input correto matematicamente",
        "Parcialmente reversível — módulo envolvido, preciso enumerar",
        "Não reversível — preciso de outra abordagem (patch no jump)",
        "Ainda não tenho certeza"
    ])
    
    if n == 1:
        print(f"\n  {CYAN}Perfeito.{RESET} Inverta cada operação na ordem contrária.")
        print(f"  Use {CYAN}python3 think.py {binary} --keygen{RESET} para guia de implementação.")
    elif n == 2:
        print(f"\n  {YELLOW}Módulo:{RESET} o espaço de possibilidades é finito.")
        print(f"  Qual o range do resultado? (ex: % 9973 → 0 a 9972)")
        print(f"  Você pode iterar todos e checar qual passa na validação.")
        print(f"  Use {CYAN}python3 think.py {binary} --bruteforce{RESET} para estratégia de enumeração.")
    elif n == 3:
        print(f"\n  {DIM}Faz sentido. Patch no jump é mais simples quando o algo é opaco.{RESET}")
        print(f"  Use {CYAN}python3 think.py {binary} --flow{RESET} para voltar ao mapeamento de fluxo.")
    elif n == 4:
        print(f"\n  {DIM}Normal. Tente colocar breakpoints e observar os valores em runtime.{RESET}")
        print(f"  {DIM}gdb + info registers depois de cada instrução é seu melhor amigo aqui.{RESET}")


# ─────────────────────────────────────────────
# MÓDULO 4 — Guia de patch
# ─────────────────────────────────────────────

def patch_guide(binary):
    section("PATCH — Qual modificação e onde?")
    
    print(f"""
{DIM}Antes de escrever um único byte, você precisa responder
três perguntas. Scripts que patcheiam sem você responder essas
perguntas são muletas — aqui você vai entender o que está fazendo.{RESET}
""")

    print(f"{BOLD}Pergunta 1 — O que você quer mudar no comportamento?{RESET}")
    n, objetivo = ask("Meu objetivo é:", [
        "Ignorar a verificação completamente (não me importa o como)",
        "Forçar sempre retorno de sucesso",
        "Inverter a lógica (falha vira sucesso)",
        "Mudar um valor hardcoded (constante, ano, PIN)",
        "Redirecionar execução para outra função"
    ])
    
    print(f"\n{BOLD}Pergunta 2 — Onde no binário está esse ponto?{RESET}")
    print(f"""
  {DIM}Você precisa do offset ESTÁTICO no arquivo (não o endereço virtual).{RESET}
  
  Se você tem o endereço virtual do r2/objdump:
    • Binário não-PIE: offset no arquivo ≈ endereço virtual − base
    • Base típica: 0x400000 (verifique com readelf -l {binary} | grep LOAD)
    
  Ou use o r2 diretamente:
    s <endereço>
    px 8          ← mostra os bytes atuais nesse ponto
    
  O offset para o flipper.py é o valor que o r2 mostra após 's':
    0x4012c3 → offset = 0x4012c3 - 0x400000 = 0x12c3 (se base = 0x400000)
""")
    offset = ask("Qual o offset (em hex) do ponto que você quer patchear?")
    
    print(f"\n{BOLD}Pergunta 3 — Quais bytes você vai escrever?{RESET}")
    
    tabela = {
        1: ("NOP patch", "9090", "dois NOPs — apaga 2 bytes de instrução"),
        2: ("Forçar retorno 1", "b8 01 00 00 00 c3", "mov eax, 1; ret"),
        3: ("je → jne", "75 XX", "inverte o jump condicional (XX = offset original)"),
        4: ("je → jmp", "eb XX", "torna o jump incondicional"),
        5: ("Outro", None, "você vai calcular")
    }
    
    print(f"\n  {DIM}Referência de opcodes comuns:{RESET}")
    for k, (nome, opcode, desc) in tabela.items():
        op_str = f"{CYAN}{opcode}{RESET}" if opcode else f"{DIM}(calcular){RESET}"
        print(f"    {k}. {nome:25s} {op_str:30s} {DIM}{desc}{RESET}")
    
    n, _ = ask("Qual categoria de patch você vai fazer:", list(tabela.values().__class__(tabela[i][0] for i in tabela)))
    
    print(f"""
  {BOLD}Antes de aplicar:{RESET}
  
  {YELLOW}1. Faça backup:{RESET}
     cp {binary} {binary}.bak
  
  {YELLOW}2. Verifique os bytes atuais:{RESET}
     python3 -c "
     f = open('{binary}','rb')
     f.seek({offset if offset else 'SEU_OFFSET'})
     print(f.read(4).hex(' '))
     f.close()
     "
  
  {YELLOW}3. Confirme que o byte atual faz sentido:{RESET}
     74 = je, 75 = jne, 90 = nop, eb = jmp curto, e8 = call
  
  {DIM}Se o byte atual não é o que você esperava, você está no offset errado.{RESET}
""")
    
    ans = ask("O byte atual confere com o que você esperava? (s/n)")
    if ans.lower() == 'n':
        reveal("""O offset pode estar errado. Possíveis causas:

  1. PIE: o binário foi compilado com PIE (endereços variáveis).
     O endereço virtual que o r2 mostra NÃO é o offset no arquivo.
     Use: r2 -n {binary} e busque pela sequência de bytes com '/x BYTES'.
  
  2. Você calculou o offset virtual, não o físico.
     No r2: seek para o endereço → 'pv' mostra o offset físico.
  
  3. O binário foi recompilado e os endereços mudaram.
     Use strings e padrões de byte para re-localizar.

  Estratégia robusta (independente de endereço):
    Python: data.find(b'\\x74\\xXX') onde XX é o offset do jump.
    Isso acha a instrução pelos bytes, não pelo endereço.""", "diagnóstico de offset errado")
    else:
        print(f"\n  {GREEN}✓ Offset confirmado.{RESET}")
        print(f"  Agora use o {CYAN}flipper.py{RESET} da pasta do desafio ou escreva seus bytes com Python:")
        print(f"""
  {DIM}Python direto:{RESET}
    python3 -c "
    with open('{binary}', 'rb+') as f:
        f.seek(SEU_OFFSET)
        f.write(bytes.fromhex('SEUS_BYTES'))
    print('patch aplicado')
    "
""")
    
    print(f"\n{BOLD}Depois do patch:{RESET}")
    print(f"  1. Rode o binário e verifique o comportamento")
    print(f"  2. Abra no r2/objdump e confirme que os bytes mudaram")
    print(f"  3. Se algo quebrou — {CYAN}cp {binary}.bak {binary}{RESET} para restaurar")


# ─────────────────────────────────────────────
# MÓDULO 5 — Estratégia de keygen
# ─────────────────────────────────────────────

def keygen_guide(binary):
    section("KEYGEN — Implementando o inverso do algoritmo")
    
    print(f"""
{DIM}Um keygen não copia o código do challenge — ele INVERTE o algoritmo.
Vamos estruturar isso em partes antes de escrever qualquer linha.{RESET}
""")

    print(f"{BOLD}FRAMEWORK para keygen:{RESET}")
    print(f"""
  {CYAN}INPUT  →  [TRANSFORMAÇÃO]  →  OUTPUT_ESPERADO{RESET}
  
  O seu keygen faz:
  
  {CYAN}OUTPUT_DESEJADO  →  [TRANSFORMAÇÃO INVERSA]  →  INPUT_VÁLIDO{RESET}
""")

    print(f"{BOLD}Passo 1 — Liste cada transformação em ordem{RESET}")
    print(f"""
  Escreva o pipeline de transformação que você viu no disassembly.
  Exemplo:
    T1: acc = 0
    T2: para cada char c no nome: acc += c * posição
    T3: acc = acc % 9973
    T4: key_val = (acc * 1337) % 99991
    T5: comparação: key_val == input_inteiro
""")
    ans = ask("Escreva seu pipeline (pode ser aproximado):")
    
    print(f"""
  {BOLD}Passo 2 — Identifique onde está o input do usuário{RESET}
  
  No pipeline acima:
    • O INPUT é o que o usuário digita (a chave)
    • O DADO é o que alimenta o algoritmo (nome, hardware ID, data...)
  
  Pergunta chave: {CYAN}O algoritmo usa o INPUT para gerar o ESPERADO,
  ou usa o DADO para gerar o ESPERADO e compara com o INPUT?{RESET}
  
  {YELLOW}Caso A:{RESET} esperado = f(nome) → você recalcula esperado dado o nome
  {YELLOW}Caso B:{RESET} válido = (input == f(constante)) → você calcula f(constante)
  {YELLOW}Caso C:{RESET} válido = g(input, nome) == 0 → você resolve a equação para input
""")
    
    n, caso = ask("Qual caso descreve seu algoritmo:", [
        "Caso A — keygen simples: dado → esperado",
        "Caso B — serial único: apenas calcula a constante",
        "Caso C — equação a resolver",
        "Não consigo categorizar ainda"
    ])
    
    if n == 1:
        print(f"""
    {CYAN}Caso A — Keygen clássico{RESET}
    
    Estrutura do keygen.py:
    
    def gerar_chave(nome):
        # reimplemente o algoritmo do challenge aqui
        acc = 0
        for i, c in enumerate(nome):
            acc += ord(c) * (i + 1)
        acc = acc % 9973
        key_val = (acc * 1337) % 99991
        return formatar(key_val)  # ex: f"{{key_val//10000:04d}}-{{key_val%10000:04d}}"
    
    {BOLD}ARMADILHA mais comum:{RESET}
    Tipos. Python usa inteiros arbitrários. C usa int32 (overflow silencioso).
    
    {YELLOW}Se o challenge usa 'unsigned int', adicione:{RESET}
        acc = acc & 0xFFFFFFFF  # força 32 bits como C unsigned int faria
    
    {YELLOW}Se usa 'int' (com sinal):{RESET}
        if acc > 0x7FFFFFFF: acc -= 0x100000000  # simula overflow com sinal
    
    {DIM}Diferença de 1 bit aqui faz o keygen gerar chaves erradas para
    valores altos — difícil de debugar sem saber isso.{RESET}
""")
    
    elif n == 2:
        print(f"""
    {CYAN}Caso B — Serial único{RESET}
    
    Rode o algoritmo uma vez e anote o resultado.
    O serial é fixo — não depende de input variável.
    
    {DIM}Mas verifique: o binário usa time(), getenv(), ou lê hardware?
    Se sim, pode não ser tão fixo quanto parece.{RESET}
""")
    
    elif n == 3:
        print(f"""
    {CYAN}Caso C — Equação a resolver{RESET}
    
    Técnicas:
    
    {YELLOW}Se for linear{RESET} (ax + b = c): resolva algebricamente.
    {YELLOW}Se envolver módulo{RESET}: use aritmética modular inversa.
      inverse = pow(a, -1, modulo)  # Python 3.8+
    {YELLOW}Se for complexo{RESET}: enumeração pode ser viável se o espaço for pequeno.
      for i in range(10000):
          if validar(i): print(i); break
""")
    
    print(f"""
  {BOLD}Passo 3 — Valide o keygen{RESET}
  
  Antes de considerar completo:
  
  {YELLOW}Teste de sanidade:{RESET}
    $ python3 seu_keygen.py alice
    $ echo "alice" | ./challenge  # depois insere a chave gerada
  
  {YELLOW}Teste com nomes diferentes:{RESET}
    bob, carol, 123, string_vazia (se o challenge aceitar)
  
  {YELLOW}Teste de edge cases:{RESET}
    nome com 1 char, nome muito longo, chars especiais
  
  Se algum falhar → volte ao pipeline e revise o tipo de dado.
""")


# ─────────────────────────────────────────────
# MÓDULO 6 — Estratégia de bruteforce inteligente
# ─────────────────────────────────────────────

def bruteforce_guide(binary):
    section("ENUMERAÇÃO — Quando bruteforce é legítimo (e quando não é)")
    
    print(f"""
{DIM}Bruteforce cego é a última opção. Bruteforce inteligente é uma técnica.
A diferença está em entender o espaço de busca antes de iterar.{RESET}
""")

    print(f"{BOLD}Pergunta 1 — Qual é o espaço de busca?{RESET}")
    n, espaco = ask("O que você está tentando descobrir:", [
        "PIN numérico (0000–9999 ou similar)",
        "Chave alfanumérica de tamanho fixo",
        "Valor inteiro com range conhecido",
        "String sem restrições conhecidas"
    ])
    
    if n == 1:
        tamanho = ask("Quantos dígitos? (ex: 4, 6, 8)")
        try:
            t = int(tamanho)
            espaco_total = 10**t
            print(f"\n  {CYAN}Espaço total:{RESET} {espaco_total:,} possibilidades")
            if espaco_total <= 10000:
                print(f"  {GREEN}✓ Factível — pode enumerar em segundos com Python{RESET}")
            elif espaco_total <= 1000000:
                print(f"  {YELLOW}⚠ Médio — enumeração possível mas pode demorar se cada teste for lento{RESET}")
            else:
                print(f"  {RED}✗ Grande — considere outra abordagem ou otimize o teste{RESET}")
        except:
            pass
    
    elif n == 4:
        print(f"""
  {RED}Cuidado.{RESET} Strings sem restrições = espaço enorme.
  
  Antes de iterar, tente:
  1. Strings no binário (strings {binary}) — pode estar hardcoded
  2. Análise do algoritmo — talvez tenha mais restrições que parecem
  3. Patch no jump em vez de descobrir a senha
""")

    print(f"""
{BOLD}Pergunta 2 — Como medir o sucesso?{RESET}

  O programa retorna código de saída diferente em sucesso/falha?
  
    {DIM}Teste:{RESET}
    echo "1234" | ./challenge; echo "Exit: $?"
    
  Se retornar 0 em sucesso e 1 (ou outro) em falha → fácil de automatizar.
  
  Se só muda a mensagem de output → você precisa capturar stdout.
""")

    ans = ask("O binário usa exit code diferente para sucesso/falha? (s/n/não sei)")
    
    print(f"""
{BOLD}Template de enumeração inteligente:{RESET}

  {DIM}Para PIN numérico de 4 dígitos:{RESET}
  
  import subprocess
  
  for i in range(10000):
      pin = f"{{i:04d}}"
      result = subprocess.run(
          ["./challenge"],
          input=pin + "\\n",
          capture_output=True,
          text=True,
          timeout=1
      )
      # Opção A: exit code
      if result.returncode == 0:
          print(f"[+] PIN: {{pin}}")
          break
      # Opção B: palavra no output
      if "válid" in result.stdout.lower() or "flag" in result.stdout.lower():
          print(f"[+] PIN: {{pin}}")
          print(result.stdout)
          break

{YELLOW}OTIMIZAÇÕES:{RESET}
  • Adicione timeout para não travar em PINs que o programa espera input adicional
  • Use threading se o teste for CPU-bound
  • Prefira re.search() a 'in' para matches mais precisos

{BOLD}Mas antes de rodar:{RESET}
  Tem certeza que bruteforce é necessário?
  O mesmo PIN está hardcoded como constante no binário?
  
    objdump -d -M intel ./challenge | grep -A2 "cmp.*eax"
  
  Isso pode te dar o valor diretamente sem iterar.
""")


# ─────────────────────────────────────────────
# DISPATCH PRINCIPAL
# ─────────────────────────────────────────────

MODOS = {
    "--recon":       (recon,           "Reconhecimento inicial do binário"),
    "--flow":        (flow,            "Mapeamento de fluxo de controle"),
    "--algo":        (algo,            "Análise guiada de algoritmo"),
    "--patch":       (patch_guide,     "Guia de patch (o que, onde, como)"),
    "--keygen":      (keygen_guide,    "Estrutura para implementar keygen"),
    "--bruteforce":  (bruteforce_guide,"Estratégia de enumeração inteligente"),
}

def usage():
    print(f"""
{BOLD}think.py{RESET} — andaime socrático para engenharia reversa

{BOLD}Uso:{RESET}
  python3 think.py <binário> <modo>

{BOLD}Modos:{RESET}""")
    for flag, (_, desc) in MODOS.items():
        print(f"  {CYAN}{flag:20s}{RESET} {desc}")
    
    print(f"""
{BOLD}Fluxo típico:{RESET}
  1. {CYAN}--recon{RESET}     → entender o que você tem
  2. {CYAN}--flow{RESET}      → achar onde está a decisão
  3. {CYAN}--algo{RESET}      → se precisar entender o algoritmo
  4. {CYAN}--patch{RESET}     → planejar a modificação
  ou {CYAN}--keygen{RESET}    → se for reverter o algoritmo
  ou {CYAN}--bruteforce{RESET}→ se for enumerar
""")
    sys.exit(0)

def main():
    if len(sys.argv) < 3:
        usage()
    
    binary = sys.argv[1]
    mode   = sys.argv[2]
    
    if not os.path.exists(binary):
        print(f"{RED}[!] Binário não encontrado: {binary}{RESET}")
        sys.exit(1)
    
    if mode not in MODOS:
        print(f"{RED}[!] Modo desconhecido: {mode}{RESET}")
        usage()
    
    hr("═", BOLD)
    print(f"{BOLD}{BLUE}  CRACKLAB — THINK.PY{RESET}  {DIM}andaime socrático{RESET}")
    print(f"  {DIM}Alvo:{RESET} {CYAN}{binary}{RESET}")
    hr("═", BOLD)
    
    fn, _ = MODOS[mode]
    try:
        fn(binary)
    except KeyboardInterrupt:
        print(f"\n\n{DIM}[saindo]{RESET}")
    
    print()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
patterns.py — Reconhecimento de padrões em assembly x86-64
Mostra o que um padrão SIGNIFICA e o que você deveria pensar ao ver ele.
Não executa nada, não patcha nada. Só expande seu vocabulário de RE.
"""

import sys
import shutil

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"

def hr(char="─", color=DIM):
    w = min(shutil.get_terminal_size((80, 24)).columns, 90)
    print(f"{color}{char * w}{RESET}")

def pattern_card(name, opcodes, meaning, questions, analogia=None, variants=None):
    hr("━", BOLD)
    print(f"\n  {BOLD}{BLUE}{name}{RESET}\n")
    
    print(f"  {YELLOW}Padrão assembly:{RESET}")
    for line in opcodes:
        print(f"    {CYAN}{line}{RESET}")
    
    print(f"\n  {YELLOW}O que significa:{RESET}")
    print(f"    {meaning}")
    
    if analogia:
        print(f"\n  {YELLOW}Analogia:{RESET}")
        print(f"    {DIM}{analogia}{RESET}")
    
    if variants:
        print(f"\n  {YELLOW}Variantes comuns:{RESET}")
        for v in variants:
            print(f"    {DIM}• {v}{RESET}")
    
    print(f"\n  {YELLOW}Quando você vê isso, pergunte:{RESET}")
    for q in questions:
        print(f"    {GREEN}→{RESET} {q}")
    
    print()


PATTERNS = {

"retorno-funcao": lambda: pattern_card(
    "RETORNO DE FUNÇÃO + DECISÃO",
    [
        "call  sym.is_valid_key    ; chama a função",
        "test  eax, eax            ; eax & eax — seta flags",
        "je    0x4012f0             ; pula se eax == 0 (ZF=1)",
    ],
    """A função retornou em eax. 'test eax, eax' é a forma idiomática de checar
    se eax é zero. Se for zero (ZF=1), 'je' pula. Se não for zero, continua.
    
    Em C isso é equivalente a:
      if (!is_valid_key(input)) { /* falha */ }""",
    [
        "O que significa retorno 0? Falha ou sucesso?",
        "O jump vai pro caminho bom ou ruim?",
        "Patchar o jump — ou forçar a função a retornar 1?",
        "Existe outra saída da função além desta?",
    ],
    analogia="É uma pergunta de sim/não. O 'test' é o árbitro, o 'je' é a porteira.",
    variants=[
        "test eax, eax + jne  (inverte: pula se NÃO zero)",
        "cmp eax, 0 + je      (equivalente mas menos idiomático)",
        "or eax, eax + je     (menos comum, mesmo efeito)",
    ]
),

"cmp-constante": lambda: pattern_card(
    "COMPARAÇÃO COM CONSTANTE HARDCODED",
    [
        "cmp   eax, 0x539          ; compara eax com 1337",
        "jne   0x401350             ; pula se diferentes",
    ],
    """O programa compara o resultado calculado com um valor fixo gravado no código.
    
    Esse valor (0x539 = 1337 decimal) é exatamente o que o input processado
    deve resultar para ser considerado válido.
    
    Em C: if (calculado != 1337) { /* falha */ }""",
    [
        "Qual é o valor decimal dessa constante?",
        "Esse valor é o resultado final ou uma etapa intermediária?",
        "Como o valor em eax foi calculado?",
        "Posso patchear a constante, o jump, ou reverter o cálculo?",
        "Esse valor aparece em strings? É um número especial (primo, potência de 2)?",
    ],
    analogia="É um cadeado com combinação. Você pode abrir (achar a combo) ou arrombar (patchear o cadeado).",
    variants=[
        "cmp eax, edx  (comparando dois registradores calculados)",
        "cmp DWORD PTR [rbp-0x8], 0x1  (comparando variável na stack)",
        "cmp al, 0x41  (comparando um byte — pode ser char 'A')",
    ]
),

"strcmp-pattern": lambda: pattern_card(
    "STRCMP — COMPARAÇÃO DE STRINGS",
    [
        "lea   rdi, [rbp-0x40]    ; 1º arg: string do usuário",
        "lea   rsi, [rip+0x2e4]   ; 2º arg: string esperada (ou addr)",
        "call  strcmp@plt          ; retorna 0 se iguais",
        "test  eax, eax",
        "jne   0x401388            ; pula se strings diferentes",
    ],
    """strcmp(s1, s2) retorna 0 se as strings são idênticas.
    Se diferente de zero → strings diferentes → geralmente vai pro caminho de falha.
    
    'lea rsi, [rip+0x2e4]' é um endereço relativo ao instruction pointer.
    Esse endereço aponta para onde a string esperada está armazenada na memória.""",
    [
        "Qual é o conteúdo do endereço que rsi aponta?",
        "A string esperada está em .rodata? Aparece em 'strings ./challenge'?",
        "É comparação direta ou há transformação do input antes?",
        "Posso pegar a string esperada direto de rodata?",
    ],
    analogia="É como comparar dois papéis. Se são iguais, passa. Mas você pode ver o papel de referência.",
    variants=[
        "strncmp (compara só n chars)",
        "strcasecmp (ignora maiúsculas/minúsculas)",
        "memcmp (compara bytes raw — pode ter null no meio)",
    ]
),

"loop-acumulador": lambda: pattern_card(
    "LOOP DE ACUMULAÇÃO",
    [
        "xor   eax, eax            ; acc = 0",
        "mov   ecx, 0x0            ; i = 0",
        ".loop:",
        "  movzx edx, BYTE [rdi+rcx]  ; d = nome[i]",
        "  imul  edx, ecx             ; d *= i",
        "  add   eax, edx             ; acc += d",
        "  inc   ecx                  ; i++",
        "  cmp   ecx, rbx             ; i < len?",
        "  jl    .loop                ; se sim, continua",
    ],
    """Um loop clássico de geração de hash/checksum.
    Pega cada byte do input, faz uma operação (aqui: byte * posição),
    acumula em eax.
    
    Em C: for (int i = 0; i < len; i++) acc += input[i] * i;""",
    [
        "Qual operação é feita com cada byte? (imul, xor, add...)",
        "O índice começa em 0 ou 1?",
        "Tem algum fator adicional além da posição?",
        "Tem 'mod' (remainder) depois do loop? (shr, idiv, imul com constante mágica)",
        "O loop usa o comprimento da string como limite?",
    ],
    analogia="É uma receita: pega cada ingrediente, processa, junta. Você precisa saber a receita para reproduzir.",
    variants=[
        "XOR acumulado (cada byte XOR'd com o anterior)",
        "Soma simples (sem fator de posição)",
        "CRC (mais complexo — bit a bit com polinômio)",
        "Bernstein hash: hash = hash * 33 + c",
    ]
),

"epílogo-retorno": lambda: pattern_card(
    "EPÍLOGO DE FUNÇÃO COM RETORNO",
    [
        "mov   eax, 0x0            ; retorna 0 (falha)",
        "leave                      ; restaura rbp/rsp",
        "ret                        ; volta pro chamador",
        "---",
        "mov   eax, 0x1            ; retorna 1 (sucesso)",
        "leave",
        "ret",
    ],
    """Toda função tem um ou mais pontos de saída (ret).
    O valor de retorno vai em eax (int, pointer truncado).
    
    'leave' é equivalente a: mov rsp, rbp; pop rbp
    Isso restaura o stack frame da função.
    
    Se você patchear 'mov eax, 0' por 'mov eax, 1' aqui,
    a função SEMPRE retornará sucesso.""",
    [
        "A função tem múltiplos pontos de ret?",
        "Todos os caminhos de falha passam por 'mov eax, 0'?",
        "Seria melhor patchear o retorno ou o jump no chamador?",
        "O padrão tem LEAVE ou apenas POP RBP?",
    ],
    analogia="O 'ret' é a saída da loja. Você pode mudar o que o funcionário entrega ao sair.",
    variants=[
        "xor eax, eax  (equivalente a mov eax, 0 — 2 bytes menor)",
        "pop rbp; ret  (sem leave — funções simples)",
        "retq  (Intel syntax — mesmo que ret em 64-bit)",
    ]
),

"time-check": lambda: pattern_card(
    "VERIFICAÇÃO DE DATA/TEMPO",
    [
        "call  time@plt             ; time(NULL) → timestamp Unix",
        "call  localtime@plt        ; converte para struct tm",
        "mov   eax, DWORD [rax+0x14] ; tm_year (offset 0x14 = 20)",
        "add   eax, 0x76c           ; + 1900 → ano real",
        "cmp   eax, 0x7e8           ; compara com 2024 (hardcoded)",
        "jg    0x401450              ; se após 2024, falha",
    ],
    """O programa pega a data atual e compara com uma data limite hardcoded.
    
    struct tm armazena ano como: anos desde 1900.
    Então 2024 - 1900 = 124 = 0x7C é o que fica no binário.
    
    tm_year está no offset 20 (0x14) da struct tm no Linux x86-64.""",
    [
        "Qual é a data limite? (converta hex → decimal → + 1900)",
        "O check usa >, >=, == ou combinação?",
        "Posso patchear a data limite no binário?",
        "Posso usar 'faketime' para enganar o programa sem patchear?",
        "Outros campos de tm são verificados também? (mês, dia)",
    ],
    analogia="O programa olha o relógio na parede. Você pode mudar o relógio ou cobrir o relógio.",
    variants=[
        "gettimeofday (microsegundos — mais preciso)",
        "clock_gettime (nanosegundos)",
        "comparação de timestamp Unix diretamente (sem localtime)",
    ]
),

"anti-debug-ptrace": lambda: pattern_card(
    "ANTI-DEBUG — ptrace",
    [
        "mov   edi, 0x0             ; PTRACE_TRACEME = 0",
        "call  ptrace@plt",
        "cmp   eax, 0xffffffffffffffff  ; retornou -1?",
        "je    0x401520              ; se sim → debugger detectado",
    ],
    """ptrace(PTRACE_TRACEME, ...) retorna -1 se já há um debugger attachado.
    Um processo só pode ter um tracer por vez — se o GDB já está tracing,
    a chamada ptrace falha.
    
    É um dos anti-debug mais comuns em Linux.""",
    [
        "O programa termina ao detectar debugger ou apenas muda comportamento?",
        "Posso NOP o bloco inteiro (do call ao je)?",
        "Posso patchear o 'je' para nunca pular?",
        "Posso usar LD_PRELOAD para interceptar ptrace e retornar 0?",
        "gdb tem opção para bypass ptrace? (sim: 'catch syscall ptrace')",
    ],
    analogia="O programa pergunta 'alguém está me observando?' Se a resposta for não-padrão, ele sabe.",
    variants=[
        "Verificação de /proc/self/status (TracerPid)",
        "Timing check (execução mais lenta com debugger)",
        "SIGTRAP — envia sinal pra si mesmo e vê se é interceptado",
    ]
),

"xor-decode": lambda: pattern_card(
    "STRING XOR — DECODIFICAÇÃO EM RUNTIME",
    [
        "lea   rdi, [rip+0x1f2]    ; endereço dos bytes cifrados",
        "mov   al, BYTE [rdi+rcx]  ; byte cifrado",
        "xor   al, 0x42            ; XOR com chave 0x42",
        "mov   BYTE [rdi+rcx], al  ; escreve decodificado",
        "inc   rcx",
        "cmp   rcx, 0xe            ; até o fim da string",
        "jl    .decode_loop",
    ],
    """Strings cifradas com XOR são comuns em malware e proteções.
    A string real não aparece em 'strings' do binário — só os bytes cifrados.
    
    XOR é reversível: byte XOR key XOR key = byte.
    A chave pode ser constante (0x42) ou derivada da posição.""",
    [
        "Qual é a chave XOR? (constante no código ou calculada?)",
        "Qual é o comprimento da string cifrada?",
        "Posso rodar o loop manualmente em Python para ver a string?",
        "A string decodificada é a comparação ou uma mensagem?",
        "Breakpoint depois do loop mostra a string decodificada em memória?",
    ],
    analogia="É uma cifra de substituição. Cada letra foi trocada pela letra + 42 posições. Desfazer é só subtrair.",
    variants=[
        "XOR com chave crescente (key = i % base_key)",
        "XOR com chave derivada do timestamp ou hardware",
        "ROT13 / César (adição simples, não XOR)",
    ]
),

}

def menu():
    print(f"""
{BOLD}{BLUE}  patterns.py — Vocabulário de padrões assembly{RESET}
  {DIM}Aprenda a ler o que o disassembly está dizendo{RESET}
""")
    hr()
    
    items = list(PATTERNS.items())
    nomes = {
        "retorno-funcao":    "Retorno de função + decisão  (test eax + je/jne)",
        "cmp-constante":     "Comparação com constante     (cmp eax, 0x539)",
        "strcmp-pattern":    "Comparação de strings        (strcmp + test)",
        "loop-acumulador":   "Loop de acumulação           (keygen/hash)",
        "epílogo-retorno":   "Epílogo de função            (mov eax,0; leave; ret)",
        "time-check":        "Verificação de data          (time + struct tm)",
        "anti-debug-ptrace": "Anti-debug ptrace            (ptrace PTRACE_TRACEME)",
        "xor-decode":        "String XOR cifrada           (decodificação em runtime)",
    }
    
    print(f"  {BOLD}Padrões disponíveis:{RESET}\n")
    for i, (k, _) in enumerate(items, 1):
        print(f"    {CYAN}{i:2}.{RESET} {nomes.get(k, k)}")
    
    print(f"    {CYAN} a.{RESET} {BOLD}Todos{RESET}")
    print(f"    {CYAN} q.{RESET} Sair\n")
    
    while True:
        escolha = input(f"  {DIM}>{RESET} ").strip().lower()
        
        if escolha == 'q':
            break
        elif escolha == 'a':
            for k, fn in items:
                fn()
                input(f"  {DIM}[Enter para próximo]{RESET} ")
        elif escolha.isdigit() and 1 <= int(escolha) <= len(items):
            k, fn = items[int(escolha)-1]
            fn()
            print(f"\n  {DIM}[Enter para voltar ao menu]{RESET}")
            input()
            menu()
            return
        else:
            # permite busca por nome parcial
            matches = [(k, fn) for k, fn in items if escolha in k]
            if matches:
                matches[0][1]()
            else:
                print(f"  {RED}Opção inválida.{RESET}")
    
    print(f"\n  {DIM}Saindo.{RESET}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        key = sys.argv[1].lstrip("-")
        if key in PATTERNS:
            PATTERNS[key]()
        else:
            print(f"{RED}Padrão não encontrado: {key}{RESET}")
            print(f"Disponíveis: {', '.join(PATTERNS.keys())}")
    else:
        menu()

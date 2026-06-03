**Trilha completa — do NOP ao impossível**

---

### 🟢 Nível 1 — Fundamentos de patch

| # | Técnica | Linguagem | O click |
|---|---------|-----------|---------|
| 1 | NOP patch | C | dois bytes apagam uma decisão |
| 2 | Patch de retorno | C | forçar `mov eax, 1; ret` numa função inteira |
| 3 | Inverter jump | C | `je` → `jne`, lógica espelhada |
| 4 | Patch de constante | C | trocar valor hardcoded na memória |
| 5 | Redirect de função | C | redirecionar call pra outra função |

---

### 🟡 Nível 2 — Engenharia reversa de lógica

| # | Técnica | Linguagem | O click |
|---|---------|-----------|---------|
| 6 | Keygen simples | C++ | reverter algoritmo aritmético |
| 7 | Keygen com checksum | C++ | entender validação por soma/hash |
| 8 | Serial fishing | C | achar a serial hardcoded no binário |
| 9 | String patching | C | modificar mensagens no binário |
| 10 | Comparação de tempo | C | licença com data de expiração hardcoded |
| 11 | Licença baseada em hardware | C | CPUID/MAC como seed da validação |

---

### 🟠 Nível 3 — Proteções ativas

| # | Técnica | Linguagem | O click |
|---|---------|-----------|---------|
| 12 | Anti-debug ptrace | C | programa detecta debugger via ptrace |
| 13 | Anti-debug timing | C | mede tempo entre instruções pra detectar stepping |
| 14 | Anti-debug SIGTRAP | C | sinaliza pra si mesmo e verifica handler |
| 15 | Checksum do próprio binário | C | programa verifica se foi modificado |
| 16 | Checksum de seção específica | C++ | só verifica `.text`, não o binário inteiro |
| 17 | Stack canary manual | C | proteção customizada contra tampering |
| 18 | Processo sentinela | C | processo filho monitora o pai |

---

### 🔴 Nível 4 — Ofuscação

| # | Técnica | Linguagem | O click |
|---|---------|-----------|---------|
| 19 | XOR string simples | C | strings criptografadas com chave fixa |
| 20 | XOR com chave dinâmica | C++ | chave gerada em runtime |
| 21 | ROT / Caesar encoding | C | ofuscação trivial mas não óbvia |
| 22 | Base64 customizado | C++ | tabela de encoding diferente do padrão |
| 23 | Strings em heap fragmentadas | C | string montada em pedaços no runtime |
| 24 | Ofuscação de fluxo com junk code | C | código inútil pra confundir o disassembly |
| 25 | Opaque predicates | C++ | condições que sempre são true/false mas parecem complexas |

---

### 🔴 Nível 5 — Empacotamento e carregamento

| # | Técnica | Linguagem | O click |
|---|---------|-----------|---------|
| 26 | UPX pack/unpack | C | descomprimir e reconstruir o binário |
| 27 | Packer customizado simples | C | stub que descomprime o payload em memória |
| 28 | Self-modifying code | C | binário que reescreve a si mesmo em runtime |
| 29 | Código em dados | C | shellcode escondido em seção `.data` |
| 30 | Payload cifrado em recurso | C++ | binário carrega e decifra outro binário |

---

### ⚫ Nível 6 — Virtualização e VM

| # | Técnica | Linguagem | O click |
|---|---------|-----------|---------|
| 31 | Dispatcher simples | C++ | switch gigante que executa opcodes |
| 32 | VM com registradores virtuais | C++ | registradores próprios, stack própria |
| 33 | VM com bytecode ofuscado | C++ | opcodes embaralhados, mapeamento não óbvio |
| 34 | VM com handlers cifrados | C++ | handlers decifrados em runtime |
| 35 | VM dentro de VM | C++ | dois níveis de interpretação |

---

### ⚫ Nível 7 — Boss final

| # | Técnica | Linguagem | O click |
|---|---------|-----------|---------|
| 36 | Licença com criptografia assimétrica leve | C++ | RSA/ECC simples implementado na mão |
| 37 | Proteção polimórfica | C | código que muda a cada execução |
| 38 | Anti-tamper com rede | C++ | binário reporta hash pra servidor, servidor valida |
| 39 | Keygen impossível por design | C++ | você percebe que é impossível e aprende por quê |
| 40 | Desafio combinado | C++ | todas as técnicas juntas num binário só |

---

**39 técnicas novas. O #39 é o mais honesto — ensinar quando algo não tem solução também é aprender.**

Por onde quer começar?
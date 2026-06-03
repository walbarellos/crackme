#!/usr/bin/env python3
"""
hypothesis.py — Framework de hipóteses para RE
Estrutura o raciocínio científico: observação → hipótese → teste → conclusão.
Salva um log de investigação que você pode revisar depois.
"""

import sys
import os
import json
import datetime

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
BLUE    = "\033[94m"

LOG_DIR = os.path.expanduser("~/.re_investigations")

def hr(char="─"):
    print(f"{DIM}{char * 70}{RESET}")

def ts():
    return datetime.datetime.now().strftime("%H:%M:%S")

def load_log(target):
    os.makedirs(LOG_DIR, exist_ok=True)
    safe = target.replace("/", "_").replace(".", "_")
    path = os.path.join(LOG_DIR, f"{safe}.json")
    if os.path.exists(path):
        with open(path) as f:
            return path, json.load(f)
    return path, {"target": target, "observations": [], "hypotheses": [], "conclusions": []}

def save_log(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_observation(log, path):
    print(f"\n{CYAN}O que você OBSERVOU?{RESET}")
    print(f"{DIM}(comportamento do binário, bytes no disassembly, output inesperado...){RESET}")
    obs = input(f"{DIM}>{RESET} ").strip()
    if obs:
        log["observations"].append({"time": ts(), "text": obs})
        save_log(path, log)
        print(f"\n{GREEN}✓ Observação registrada.{RESET}")
        
        print(f"\n{DIM}Com base nisso, o que VOCÊ INFERE?{RESET}")
        print(f"{DIM}(não precisa ser certo — é uma hipótese de trabalho){RESET}")
        inf = input(f"{DIM}>{RESET} ").strip()
        if inf:
            add_hypothesis(log, path, prefill=inf, from_obs=obs)

def add_hypothesis(log, path, prefill=None, from_obs=None):
    if not prefill:
        print(f"\n{CYAN}Qual é sua HIPÓTESE?{RESET}")
        print(f"{DIM}Complete: 'Acredito que ___ porque ___ e posso testar fazendo ___'{RESET}")
        h = input(f"{DIM}>{RESET} ").strip()
    else:
        h = prefill
    
    if not h:
        return
    
    print(f"\n{CYAN}Como você vai TESTAR essa hipótese?{RESET}")
    print(f"{DIM}(comando específico, breakpoint, modificação, experimento...){RESET}")
    test = input(f"{DIM}>{RESET} ").strip()
    
    print(f"\n{CYAN}O que confirmaria OU refutaria essa hipótese?{RESET}")
    expected = input(f"{DIM}>{RESET} ").strip()
    
    entry = {
        "time": ts(),
        "hypothesis": h,
        "test": test,
        "expected": expected,
        "result": None,
        "status": "pendente",
        "from_observation": from_obs
    }
    log["hypotheses"].append(entry)
    save_log(path, log)
    
    idx = len(log["hypotheses"]) - 1
    print(f"\n{GREEN}✓ Hipótese #{idx+1} registrada.{RESET}")
    print(f"{DIM}Execute o teste e use 'resultado' para registrar o que aconteceu.{RESET}")

def record_result(log, path):
    pending = [(i, h) for i, h in enumerate(log["hypotheses"]) if h["status"] == "pendente"]
    
    if not pending:
        print(f"\n{YELLOW}Nenhuma hipótese pendente.{RESET}")
        return
    
    print(f"\n{CYAN}Hipóteses pendentes:{RESET}\n")
    for i, h in pending:
        print(f"  {BOLD}#{i+1}{RESET} {h['hypothesis']}")
        print(f"      {DIM}Teste: {h['test']}{RESET}")
    
    print(f"\nQual hipótese você quer registrar o resultado? (número)")
    n = input(f"{DIM}>{RESET} ").strip()
    
    try:
        idx = int(n) - 1
        h = log["hypotheses"][idx]
    except:
        print(f"{RED}Índice inválido.{RESET}")
        return
    
    print(f"\n{CYAN}O que aconteceu quando você testou?{RESET}")
    result = input(f"{DIM}>{RESET} ").strip()
    
    print(f"\n{CYAN}A hipótese foi:{RESET}")
    print(f"  1. {GREEN}Confirmada{RESET}")
    print(f"  2. {RED}Refutada{RESET}")
    print(f"  3. {YELLOW}Parcialmente confirmada — ajustar hipótese{RESET}")
    
    status_map = {"1": "confirmada", "2": "refutada", "3": "parcial"}
    s = input(f"{DIM}>{RESET} ").strip()
    status = status_map.get(s, "indeterminado")
    
    h["result"] = result
    h["status"] = status
    save_log(path, log)
    
    if status == "confirmada":
        print(f"\n{GREEN}✓ Hipótese confirmada!{RESET}")
        print(f"{DIM}Anote a conclusão com 'conclusão'.{RESET}")
    elif status == "refutada":
        print(f"\n{RED}✗ Hipótese refutada.{RESET}")
        print(f"\n{DIM}O que isso te diz? O que você AGORA acha que está acontecendo?{RESET}")
        nova = input(f"{DIM}>{RESET} ").strip()
        if nova:
            print(f"\n{DIM}Essa é uma nova hipótese. Registrando...{RESET}")
            add_hypothesis(log, path, prefill=nova)
    elif status == "parcial":
        print(f"\n{YELLOW}Parcial.{RESET} O que precisa ser ajustado na hipótese?")
        ajuste = input(f"{DIM}>{RESET} ").strip()
        if ajuste:
            add_hypothesis(log, path, prefill=ajuste)

def add_conclusion(log, path):
    print(f"\n{CYAN}Qual é sua CONCLUSÃO sobre esse aspecto do desafio?{RESET}")
    c = input(f"{DIM}>{RESET} ").strip()
    if c:
        log["conclusions"].append({"time": ts(), "text": c})
        save_log(path, log)
        print(f"\n{GREEN}✓ Conclusão registrada.{RESET}")

def show_log(log):
    print(f"\n{BOLD}{BLUE}══ INVESTIGAÇÃO: {log['target']} ══{RESET}\n")
    
    if log["observations"]:
        print(f"{YELLOW}OBSERVAÇÕES:{RESET}")
        for o in log["observations"]:
            print(f"  {DIM}[{o['time']}]{RESET} {o['text']}")
    
    if log["hypotheses"]:
        print(f"\n{YELLOW}HIPÓTESES:{RESET}")
        status_icons = {"pendente": f"{YELLOW}⏳{RESET}", "confirmada": f"{GREEN}✓{RESET}", 
                       "refutada": f"{RED}✗{RESET}", "parcial": f"{YELLOW}~{RESET}"}
        for i, h in enumerate(log["hypotheses"], 1):
            icon = status_icons.get(h["status"], "?")
            print(f"\n  {icon} {BOLD}#{i}{RESET} {h['hypothesis']}")
            print(f"     {DIM}Teste:{RESET}    {h['test']}")
            if h['result']:
                print(f"     {DIM}Resultado:{RESET} {h['result']}")
    
    if log["conclusions"]:
        print(f"\n{YELLOW}CONCLUSÕES:{RESET}")
        for c in log["conclusions"]:
            print(f"  {DIM}[{c['time']}]{RESET} {GREEN}{c['text']}{RESET}")
    
    h_total = len(log["hypotheses"])
    h_conf  = sum(1 for h in log["hypotheses"] if h["status"] == "confirmada")
    h_ref   = sum(1 for h in log["hypotheses"] if h["status"] == "refutada")
    
    print(f"\n{DIM}── Resumo: {h_total} hipóteses | {h_conf} confirmadas | {h_ref} refutadas ──{RESET}")

def export_log(log, path):
    export_path = path.replace(".json", "_notes.md")
    lines = [
        f"# Investigação: {log['target']}",
        "",
    ]
    
    if log["observations"]:
        lines += ["## Observações", ""]
        for o in log["observations"]:
            lines.append(f"- `[{o['time']}]` {o['text']}")
        lines.append("")
    
    if log["hypotheses"]:
        lines += ["## Hipóteses", ""]
        for i, h in enumerate(log["hypotheses"], 1):
            status = {"confirmada": "✓", "refutada": "✗", "parcial": "~", "pendente": "⏳"}.get(h["status"], "?")
            lines.append(f"### {status} Hipótese {i}")
            lines.append(f"**Hipótese:** {h['hypothesis']}")
            lines.append(f"**Teste:** {h['test']}")
            if h.get("expected"):
                lines.append(f"**Esperado:** {h['expected']}")
            if h.get("result"):
                lines.append(f"**Resultado:** {h['result']}")
            lines.append("")
    
    if log["conclusions"]:
        lines += ["## Conclusões", ""]
        for c in log["conclusions"]:
            lines.append(f"- {c['text']}")
    
    with open(export_path, "w") as f:
        f.write("\n".join(lines))
    
    print(f"\n{GREEN}✓ Exportado para:{RESET} {export_path}")

def main():
    if len(sys.argv) < 2:
        print(f"""
{BOLD}hypothesis.py{RESET} — Framework de investigação para RE

{BOLD}Uso:{RESET}
  python3 hypothesis.py <nome-do-alvo>

  O nome pode ser o binário, desafio, ou qualquer identificador.
  O log fica salvo em ~/.re_investigations/

{BOLD}Comandos interativos:{RESET}
  o  observação  — registra algo que você viu
  h  hipotese    — cria uma hipótese formal
  r  resultado   — registra resultado de um teste
  c  conclusao   — registra conclusão
  l  log         — mostra todo o log
  e  exportar    — exporta como Markdown
  q  sair
""")
        sys.exit(0)
    
    target = sys.argv[1]
    path, log = load_log(target)
    
    print(f"\n{BOLD}{BLUE}  hypothesis.py — Investigação: {target}{RESET}")
    
    if log["hypotheses"] or log["observations"]:
        print(f"  {DIM}Sessão existente carregada.{RESET}")
        show_log(log)
    else:
        print(f"  {DIM}Nova investigação iniciada.{RESET}")
        print(f"""
  {DIM}Use esse script para estruturar seu raciocínio enquanto analisa.
  A ideia: antes de executar qualquer ferramenta ou fazer qualquer patch,
  formule uma hipótese. Teste. Registre o resultado. Repita.
  
  Reversers experientes pensam assim — eles não ficam tentando
  coisas aleatórias. Cada ação tem uma hipótese por trás.{RESET}
""")
    
    cmds = {
        "o": ("observação", lambda: add_observation(log, path)),
        "obs": ("observação", lambda: add_observation(log, path)),
        "h": ("hipótese", lambda: add_hypothesis(log, path)),
        "hip": ("hipótese", lambda: add_hypothesis(log, path)),
        "r": ("resultado", lambda: record_result(log, path)),
        "res": ("resultado", lambda: record_result(log, path)),
        "c": ("conclusão", lambda: add_conclusion(log, path)),
        "con": ("conclusão", lambda: add_conclusion(log, path)),
        "l": ("log", lambda: show_log(log)),
        "log": ("log", lambda: show_log(log)),
        "e": ("exportar", lambda: export_log(log, path)),
        "exp": ("exportar", lambda: export_log(log, path)),
    }
    
    print(f"  {DIM}[o] observação  [h] hipótese  [r] resultado  [c] conclusão  [l] log  [e] exportar  [q] sair{RESET}\n")
    
    while True:
        try:
            cmd = input(f"{CYAN}inv{RESET}{DIM}>{RESET} ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        
        if cmd in ("q", "quit", "exit", "sair"):
            break
        elif cmd in cmds:
            cmds[cmd][1]()
        elif cmd == "":
            continue
        else:
            print(f"  {DIM}Comandos: {', '.join(sorted(set(cmds.keys())))}. 'q' para sair.{RESET}")
    
    print(f"\n{DIM}Investigação salva em {path}{RESET}")

if __name__ == "__main__":
    main()

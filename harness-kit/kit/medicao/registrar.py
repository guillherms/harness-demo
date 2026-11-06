"""Registra eventos da execução ativa em ~/.harness/runs/<id>/log.jsonl.

Como hook (lê o evento do stdin): PostToolUse, SubagentStop, Stop, UserPromptSubmit.
Como CLI (marcos que hook não enxerga):
    python registrar.py marcar review REPROVADO
    python registrar.py marcar fase inicio aplicacao

Nunca bloqueia nada: qualquer erro aqui é ignorado (sai com 0).
Não grava conteúdo de prompts nem de arquivos, só metadados.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RUNS = Path.home() / ".harness" / "runs"


def gravar(evento: dict):
    ativo = RUNS / "active.json"
    if not ativo.exists():
        return
    historia = json.loads(ativo.read_text(encoding="utf-8"))["historia"]
    pasta = RUNS / historia
    pasta.mkdir(parents=True, exist_ok=True)
    evento = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **evento}
    with open(pasta / "log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")


def alvo(entrada: dict) -> str:
    for chave in ("file_path", "path", "pattern"):
        if entrada.get(chave):
            return str(entrada[chave])
    if entrada.get("command"):
        return str(entrada["command"])[:120]
    return ""


def do_hook():
    p = json.load(sys.stdin)
    nome = p.get("hook_event_name", "")
    ev = {"evento": nome, "sessao": p.get("session_id", ""), "transcript": p.get("transcript_path", "")}
    if nome == "PostToolUse":
        ev["ferramenta"] = p.get("tool_name", "")
        ev["alvo"] = alvo(p.get("tool_input") or {})
    if p.get("agent_transcript_path"):  # transcript do subagent, se a versão enviar
        ev["transcript_subagent"] = p["agent_transcript_path"]
    gravar(ev)


if __name__ == "__main__":
    try:
        if len(sys.argv) > 2 and sys.argv[1] == "marcar":
            gravar({"evento": "marco", "tipo": sys.argv[2], "valor": " ".join(sys.argv[3:])})
        else:
            do_hook()
    except Exception:
        pass
    sys.exit(0)

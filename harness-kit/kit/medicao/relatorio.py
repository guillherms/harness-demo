"""Resumo de uma execução: python relatorio.py <id> [--json]

Lê ~/.harness/runs/<id>/log.jsonl e os transcripts referenciados nele (para
somar tokens). Grava também resumo.json na pasta da execução.
"""
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

RUNS = Path.home() / ".harness" / "runs"


def tokens(transcripts: set[str]) -> dict:
    total, vistos = Counter(), set()
    for t in transcripts:
        arq = Path(t).expanduser()
        if not arq.exists():
            continue
        for linha in arq.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                msg = json.loads(linha).get("message") or {}
            except json.JSONDecodeError:
                continue
            uso, mid = msg.get("usage"), msg.get("id")
            if not uso or (mid and mid in vistos):  # a mesma mensagem pode repetir
                continue
            vistos.add(mid)
            for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
                total[k] += uso.get(k) or 0
    return dict(total)


def resumir(historia: str) -> dict:
    log = RUNS / historia / "log.jsonl"
    eventos = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
    ferramentas = [e for e in eventos if e["evento"] == "PostToolUse"]
    por_tipo = Counter(e["ferramenta"] for e in ferramentas)
    marcos = [e for e in eventos if e["evento"] == "marco"]
    ini = datetime.fromisoformat(eventos[0]["ts"])
    fim = datetime.fromisoformat(eventos[-1]["ts"])
    transcripts = {e[k] for e in eventos for k in ("transcript", "transcript_subagent") if e.get(k)}
    tk = tokens(transcripts)
    return {
        "historia": historia,
        "minutos": round((fim - ini).total_seconds() / 60, 1),
        "tokens_entrada": tk.get("input_tokens", 0) + tk.get("cache_read_input_tokens", 0)
                          + tk.get("cache_creation_input_tokens", 0),
        "tokens_saida": tk.get("output_tokens", 0),
        "chamadas_ferramenta": len(ferramentas),
        "arquivos_lidos": len({e["alvo"] for e in ferramentas if e["ferramenta"] == "Read"}),
        "leituras": por_tipo.get("Read", 0),
        "buscas": por_tipo.get("Grep", 0) + por_tipo.get("Glob", 0),
        "edicoes": sum(por_tipo.get(f, 0) for f in ("Edit", "Write", "MultiEdit")),
        "comandos": por_tipo.get("Bash", 0),
        "chamadas_mcp": sum(n for f, n in por_tipo.items() if f.startswith("mcp__")),
        "subagents_concluidos": sum(1 for e in eventos if e["evento"] == "SubagentStop"),
        "falhas_sensor": sum(1 for m in marcos if m["tipo"] == "sensores" and m["valor"].startswith("falha")),
        "rodadas_review": sum(1 for m in marcos if m["tipo"] == "review"),
        "reprovacoes_review": sum(1 for m in marcos if m["tipo"] == "review" and m["valor"].startswith("REPROVADO")),
        "intervencoes_humanas": max(0, sum(1 for e in eventos if e["evento"] == "UserPromptSubmit") - 1),
    }


def texto(r: dict) -> str:
    return "\n".join([
        f"História {r['historia']}  |  {r['minutos']} min",
        f"Tokens: {r['tokens_entrada']:,} entrada / {r['tokens_saida']:,} saída",
        f"Ferramentas: {r['chamadas_ferramenta']} (leituras {r['leituras']}, buscas {r['buscas']}, "
        f"edições {r['edicoes']}, comandos {r['comandos']}, MCP {r['chamadas_mcp']})",
        f"Arquivos distintos lidos: {r['arquivos_lidos']}",
        f"Review: {r['rodadas_review']} rodada(s), {r['reprovacoes_review']} reprovação(ões)  |  "
        f"falhas de sensor: {r['falhas_sensor']}",
        f"Intervenções humanas: {r['intervencoes_humanas']}",
    ])


if __name__ == "__main__":
    r = resumir(sys.argv[1])
    (RUNS / sys.argv[1] / "resumo.json").write_text(json.dumps(r, indent=2), encoding="utf-8")
    print(json.dumps(r, indent=2) if "--json" in sys.argv else texto(r))

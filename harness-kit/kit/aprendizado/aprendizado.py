"""Ciclo de aprendizado: acha o que se repete entre execuções.

    python aprendizado.py analisar [--min 2]
    python aprendizado.py aplicar --categoria testes --onde AGENTS.md --descricao "..."

analisar: lê os apontamentos de review e as falhas de sensor de TODAS as
execuções em ~/.harness/runs/ e agrupa por categoria. Só mostra o que se
repetiu (>= --min ocorrências) DEPOIS da última vez que aquela categoria foi
tratada. A máquina agrupa; quem sugere onde registrar é o orquestrador; quem
decide é o humano.

aplicar: registra que um aprendizado virou regra (vale como linha de corte).
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

HARNESS = Path.home() / ".harness"
RUNS = HARNESS / "runs"
APLICADOS = HARNESS / "aprendizado.jsonl"


def eventos():
    for log in RUNS.glob("*/log.jsonl"):
        for linha in log.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(linha)
            except json.JSONDecodeError:
                continue
            if e.get("evento") != "marco":
                continue
            if e["tipo"] == "apontamento":
                cat, _, resumo = e["valor"].partition(" ")
                yield e["ts"], log.parent.name, cat, resumo
            elif e["tipo"] == "sensores" and e["valor"].startswith("falha"):
                for sensor in e["valor"].split(" ", 1)[1].split(","):
                    yield e["ts"], log.parent.name, f"sensor:{sensor.strip()}", ""


def ultimo_aplicado():
    corte = {}
    if APLICADOS.exists():
        for linha in APLICADOS.read_text(encoding="utf-8").splitlines():
            a = json.loads(linha)
            corte[a["categoria"]] = max(corte.get(a["categoria"], ""), a["ts"])
    return corte


def analisar(minimo):
    corte = ultimo_aplicado()
    grupos = defaultdict(list)
    for ts, historia, cat, resumo in eventos():
        if ts > corte.get(cat, ""):
            grupos[cat].append((ts, historia, resumo))
    repetidos = {c: v for c, v in grupos.items() if len(v) >= minimo}
    if not repetidos:
        print("Nada recorrente.")
        return
    for cat, itens in sorted(repetidos.items(), key=lambda x: -len(x[1])):
        historias = sorted({h for _, h, _ in itens})
        reincidente = " (REINCIDENTE: já foi tratado antes)" if cat in corte else ""
        print(f"{cat}: {len(itens)}x em {len(historias)} história(s) {historias}{reincidente}")
        for _, h, resumo in sorted(itens)[-3:]:
            if resumo:
                print(f"  - [{h}] {resumo}")


def aplicar(categoria, onde, descricao):
    from datetime import datetime, timezone
    APLICADOS.parent.mkdir(parents=True, exist_ok=True)
    with open(APLICADOS, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "categoria": categoria, "onde": onde, "descricao": descricao},
                           ensure_ascii=False) + "\n")
    print(f"Registrado: {categoria} → {onde}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analisar")
    a.add_argument("--min", type=int, default=2)
    b = sub.add_parser("aplicar")
    b.add_argument("--categoria", required=True)
    b.add_argument("--onde", required=True)
    b.add_argument("--descricao", required=True)
    args = p.parse_args()
    if args.cmd == "analisar":
        analisar(args.min)
    else:
        aplicar(args.categoria, args.onde, args.descricao)

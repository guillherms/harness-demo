"""Hook Stop/SubagentStop: roda os sensores dos repos da execução ativa.

Cada repo declara seus sensores em .harness/sensores.json (o repo é dono dos
próprios comandos). Só roda o sensor se algum arquivo alterado casar com ele.

Exit 0 = pode encerrar | Exit 2 = sensor falhou, o agente precisa continuar
(o stderr, já resumido, volta para o agente).
"""
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

RUNS = Path.home() / ".harness" / "runs"
MAX_TENTATIVAS = 3   # depois disso libera e escala para o humano
LINHAS_LOG = 40      # só o final do log entra no contexto do agente


def arquivos_alterados(repo):
    saida = subprocess.run(["git", "-C", repo, "status", "--porcelain", "--untracked-files=all"],
                           capture_output=True, text=True).stdout
    return [linha[3:].strip().strip('"') for linha in saida.splitlines() if linha.strip()]


def resumo(texto):
    linhas = texto.strip().splitlines()
    corte = linhas[-LINHAS_LOG:]
    prefixo = [f"... ({len(linhas) - LINHAS_LOG} linhas omitidas)"] if len(linhas) > LINHAS_LOG else []
    return "\n".join(prefixo + corte)


def marcar_medicao(valor):
    try:  # medição é opcional: se a pasta não existir, segue sem registrar
        sys.path.insert(0, str(Path(__file__).parent.parent / "medicao"))
        import registrar
        registrar.gravar({"evento": "marco", "tipo": "sensores", "valor": valor})
    except Exception:
        pass


def main():
    ativo = RUNS / "active.json"
    if not ativo.exists():
        sys.exit(0)
    run = json.loads(ativo.read_text(encoding="utf-8"))
    pasta_run = RUNS / run["historia"]
    pasta_run.mkdir(parents=True, exist_ok=True)

    resultados, falhas = [], []
    for repo in run["repos"]:
        config = Path(repo) / ".harness" / "sensores.json"
        if not config.exists():
            continue
        alterados = arquivos_alterados(repo)
        for s in json.loads(config.read_text(encoding="utf-8"))["sensores"]:
            if not any(fnmatch.fnmatch(a, p) for a in alterados for p in s["quando"]):
                continue
            r = subprocess.run(s["comando"], cwd=repo, shell=True, capture_output=True, text=True)
            ok = r.returncode == 0
            resultados.append({"repo": Path(repo).name, "sensor": s["nome"], "ok": ok})
            if not ok:
                falhas.append(f"[{Path(repo).name}] {s['nome']} falhou "
                              f"({s['comando']}):\n{resumo(r.stdout + r.stderr)}")

    # Registro para o review e para a medição
    (pasta_run / "sensores.json").write_text(json.dumps(resultados, indent=2), encoding="utf-8")

    nomes_falha = sorted({r["sensor"] for r in resultados if not r["ok"]})
    marcar_medicao("ok" if not falhas else "falha " + ",".join(nomes_falha))

    contador = pasta_run / "tentativas_sensores"
    if not falhas:
        contador.unlink(missing_ok=True)
        sys.exit(0)

    tentativas = int(contador.read_text()) + 1 if contador.exists() else 1
    contador.write_text(str(tentativas))
    if tentativas > MAX_TENTATIVAS:
        contador.unlink()
        print(f"Sensores falharam {MAX_TENTATIVAS} vezes. Pare e reporte ao usuário.", file=sys.stderr)
        sys.exit(0)

    print(f"Sensores falharam (tentativa {tentativas}/{MAX_TENTATIVAS}). "
          "Corrija antes de encerrar:\n\n" + "\n\n".join(falhas), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()

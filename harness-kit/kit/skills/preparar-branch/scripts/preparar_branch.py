"""Prepara, verifica e encerra a branch feature/<id> de uma história.

preparar  --historia PROJ-101 --repos C:/dev/app C:/dev/gateway
verificar
commit    --mensagem "PROJ-101: título"
encerrar

É o ÚNICO caminho de escrita no git do fluxo: as permissões do Claude negam
git commit/push/switch direto, então branch e commit passam sempre por aqui.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

RUN_FILE = Path.home() / ".harness" / "runs" / "active.json"
BASE = "develop"


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        falhar(f"[{Path(repo).name}] git {' '.join(args)}: {r.stderr.strip()}")
    return r


def falhar(msg):
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(1)


def branch_atual(repo):
    return git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def preparar(historia, repos):
    alvo = f"feature/{historia}"
    for repo in repos:  # 1ª passada: só checa, não altera nada
        if not Path(repo).exists():
            falhar(f"repo não encontrado: {repo}")
        if git(repo, "status", "--porcelain").stdout.strip():
            falhar(f"[{Path(repo).name}] há alterações não commitadas. Resolva antes.")
    for repo in repos:
        git(repo, "fetch", "origin")
        if git(repo, "rev-parse", "--verify", alvo, check=False).returncode == 0:
            git(repo, "switch", alvo)
        elif git(repo, "rev-parse", "--verify", f"origin/{alvo}", check=False).returncode == 0:
            git(repo, "switch", "--track", f"origin/{alvo}")
        else:
            git(repo, "switch", BASE)
            git(repo, "pull", "--ff-only")
            git(repo, "switch", "-c", alvo)
        print(f"[{Path(repo).name}] na branch {alvo}")
    RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
    RUN_FILE.write_text(json.dumps({"historia": historia, "repos": repos}, indent=2), encoding="utf-8")


def verificar():
    if not RUN_FILE.exists():
        falhar("nenhuma execução ativa. Rode 'preparar' primeiro.")
    run = json.loads(RUN_FILE.read_text(encoding="utf-8"))
    alvo = f"feature/{run['historia']}"
    for repo in run["repos"]:
        atual = branch_atual(repo)
        if atual != alvo:
            falhar(f"[{Path(repo).name}] está em '{atual}', esperado '{alvo}'.")
    print(f"OK: todos os repos em {alvo}")


def commit(mensagem):
    verificar()  # nunca commita fora da branch da história
    run = json.loads(RUN_FILE.read_text(encoding="utf-8"))
    for repo in run["repos"]:
        if not git(repo, "status", "--porcelain").stdout.strip():
            print(f"[{Path(repo).name}] sem alterações, nada a commitar")
            continue
        git(repo, "add", "-A")
        git(repo, "commit", "-m", mensagem)
        print(f"[{Path(repo).name}] commit feito")


def encerrar():
    RUN_FILE.unlink(missing_ok=True)
    print("Execução encerrada.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    prep = sub.add_parser("preparar")
    prep.add_argument("--historia", required=True)
    prep.add_argument("--repos", nargs="+", required=True)
    sub.add_parser("verificar")
    com = sub.add_parser("commit")
    com.add_argument("--mensagem", required=True)
    sub.add_parser("encerrar")
    a = p.parse_args()
    if a.cmd == "preparar":
        preparar(a.historia, a.repos)
    elif a.cmd == "verificar":
        verificar()
    elif a.cmd == "commit":
        commit(a.mensagem)
    else:
        encerrar()

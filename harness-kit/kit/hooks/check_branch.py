"""PreToolUse hook: bloqueia Edit/Write fora da branch feature/<id> da execução ativa.

Lê a execução ativa em ~/.harness/runs/active.json (gravado pelo preparar-branch):
    {"historia": "PROJ-101", "repos": ["C:/dev/aplicacao-java", "C:/dev/gateway-padrao"]}

Exit 0 = libera | Exit 2 = bloqueia (a mensagem no stderr volta para o agente).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RUN_FILE = Path.home() / ".harness" / "runs" / "active.json"


def norm(p) -> str:
    # Windows: ignora maiúsculas/minúsculas e normaliza as barras
    return os.path.normcase(str(Path(p).resolve()))


def git(cwd: Path, *args) -> str:
    return subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def repo_e_branch(arquivo: Path):
    pasta = arquivo.parent
    while not pasta.exists():  # Write de arquivo novo em pasta que ainda não existe
        pasta = pasta.parent
    try:
        return git(pasta, "rev-parse", "--show-toplevel"), git(pasta, "rev-parse", "--abbrev-ref", "HEAD")
    except subprocess.CalledProcessError:
        return None, None  # fora de um repo git


def bloquear(msg: str):
    print(msg, file=sys.stderr)
    sys.exit(2)


def main():
    if not RUN_FILE.exists():
        sys.exit(0)  # sem execução ativa: não atrapalha o trabalho manual

    try:
        run = json.loads(RUN_FILE.read_text(encoding="utf-8"))
        esperado = f"feature/{run['historia']}"
        repos = {norm(r) for r in run["repos"]}
    except (json.JSONDecodeError, KeyError):
        bloquear(f"Bloqueado: {RUN_FILE} inválido. Rode preparar-branch de novo.")

    payload = json.load(sys.stdin)
    caminho = payload.get("tool_input", {}).get("file_path")
    if not caminho:
        sys.exit(0)

    arquivo = Path(caminho)
    if not arquivo.is_absolute():
        arquivo = Path(payload.get("cwd", ".")) / arquivo

    raiz, branch = repo_e_branch(arquivo)
    if raiz is None or norm(raiz) not in repos:
        sys.exit(0)  # não é repo da história

    if branch != esperado:
        bloquear(
            f"Bloqueado: o repo '{Path(raiz).name}' está na branch '{branch}', "
            f"mas a história exige '{esperado}'. Não edite nada: pare e peça "
            f"para rodar preparar-branch."
        )
    sys.exit(0)


if __name__ == "__main__":
    main()

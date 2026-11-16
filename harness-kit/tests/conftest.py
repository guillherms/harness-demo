"""Fixtures comuns.

Os scripts do kit leem Path.home() no import, então cada teste roda o script
como subprocess com HOME/USERPROFILE apontando para uma pasta temporária:
nada toca o ~/.harness de verdade.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
KIT = RAIZ / "kit"

SCRIPTS = {
    "check_branch": KIT / "hooks" / "check_branch.py",
    "sensores": KIT / "sensores" / "rodar_sensores.py",
    "validar_spec": KIT / "contratos" / "validar_spec.py",
    "preparar_branch": KIT / "skills" / "preparar-branch" / "scripts" / "preparar_branch.py",
    "pre_commit": KIT / "githooks" / "pre_commit.py",
    "registrar": KIT / "medicao" / "registrar.py",
    "relatorio": KIT / "medicao" / "relatorio.py",
    "aprendizado": KIT / "aprendizado" / "aprendizado.py",
    "endpoints": KIT / "mcp" / "endpoints.py",
    "sync": RAIZ / "sync.py",
}


@pytest.fixture
def home(tmp_path, monkeypatch):
    """HOME falso, aplicado ao processo de teste (herdado pelos subprocess)."""
    h = tmp_path / "home"
    h.mkdir()
    for var in ("HOME", "USERPROFILE"):
        monkeypatch.setenv(var, str(h))
    monkeypatch.setenv("PYTHONIOENCODING", "utf-8")
    return h


@pytest.fixture
def runs(home):
    r = home / ".harness" / "runs"
    r.mkdir(parents=True)
    return r


@pytest.fixture
def rodar():
    def _rodar(nome, *args, stdin=None, cwd=None):
        entrada = json.dumps(stdin) if isinstance(stdin, dict) else stdin
        return subprocess.run([sys.executable, str(SCRIPTS[nome]), *map(str, args)],
                              input=entrada, capture_output=True, text=True,
                              encoding="utf-8", cwd=cwd, env=os.environ.copy())
    return _rodar


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, check=check)


@pytest.fixture
def repo_git(tmp_path, home):
    """Cria um repo com remote bare `origin`, branch develop publicada e um commit."""
    def _criar(nome):
        remoto = tmp_path / "remotes" / f"{nome}.git"
        subprocess.run(["git", "init", "-q", "--bare", str(remoto)], check=True)
        repo = tmp_path / nome
        subprocess.run(["git", "init", "-q", "-b", "develop", str(repo)], check=True)
        git(repo, "config", "user.email", "teste@exemplo.com")
        git(repo, "config", "user.name", "Teste")
        git(repo, "config", "core.autocrlf", "false")
        (repo / "README.md").write_text("inicial\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "inicial")
        git(repo, "remote", "add", "origin", str(remoto))
        git(repo, "push", "-q", "-u", "origin", "develop")
        return repo
    return _criar


def ativar(runs, historia, repos):
    (runs / "active.json").write_text(
        json.dumps({"historia": historia, "repos": [str(r) for r in repos]}), encoding="utf-8")

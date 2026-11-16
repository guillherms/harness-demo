"""check_branch (hook PreToolUse), preparar_branch e pre-commit."""
import json
import subprocess

from conftest import ativar, git


def payload(arquivo, cwd="."):
    return {"hook_event_name": "PreToolUse", "tool_name": "Edit", "cwd": str(cwd),
            "tool_input": {"file_path": str(arquivo)}}


# ---------- check_branch ----------

def test_sem_execucao_ativa_libera(rodar, home, repo_git):
    app = repo_git("app")
    r = rodar("check_branch", stdin=payload(app / "README.md"))
    assert r.returncode == 0


def test_branch_errada_bloqueia(rodar, runs, repo_git):
    app = repo_git("app")
    ativar(runs, "PROJ-1", [app])
    r = rodar("check_branch", stdin=payload(app / "README.md"))
    assert r.returncode == 2
    assert "feature/PROJ-1" in r.stderr


def test_branch_certa_libera(rodar, runs, repo_git):
    app = repo_git("app")
    git(app, "switch", "-q", "-c", "feature/PROJ-1")
    ativar(runs, "PROJ-1", [app])
    assert rodar("check_branch", stdin=payload(app / "README.md")).returncode == 0


def test_arquivo_novo_em_pasta_inexistente(rodar, runs, repo_git):
    app = repo_git("app")
    ativar(runs, "PROJ-1", [app])
    r = rodar("check_branch", stdin=payload(app / "src" / "novo" / "X.java"))
    assert r.returncode == 2  # achou o repo subindo as pastas, e a branch está errada


def test_caminho_relativo_usa_cwd(rodar, runs, repo_git):
    app = repo_git("app")
    ativar(runs, "PROJ-1", [app])
    r = rodar("check_branch", stdin=payload("README.md", cwd=app))
    assert r.returncode == 2


def test_repo_fora_da_historia_libera(rodar, runs, repo_git):
    app, outro = repo_git("app"), repo_git("outro")
    ativar(runs, "PROJ-1", [app])
    assert rodar("check_branch", stdin=payload(outro / "README.md")).returncode == 0


# ---------- preparar_branch ----------

def test_preparar_cria_branch_nos_repos(rodar, runs, repo_git):
    app, gw = repo_git("app"), repo_git("gw")
    r = rodar("preparar_branch", "preparar", "--historia", "PROJ-1", "--repos", app, gw)
    assert r.returncode == 0, r.stderr
    for repo in (app, gw):
        assert git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() == "feature/PROJ-1"
    ativo = json.loads((runs / "active.json").read_text(encoding="utf-8"))
    assert ativo["historia"] == "PROJ-1" and len(ativo["repos"]) == 2


def test_preparar_retoma_branch_existente(rodar, runs, repo_git):
    app = repo_git("app")
    rodar("preparar_branch", "preparar", "--historia", "PROJ-1", "--repos", app)
    git(app, "switch", "-q", "develop")
    r = rodar("preparar_branch", "preparar", "--historia", "PROJ-1", "--repos", app)
    assert r.returncode == 0, r.stderr
    assert git(app, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() == "feature/PROJ-1"


def test_preparar_com_repo_sujo_nao_altera_nenhum(rodar, runs, repo_git):
    app, gw = repo_git("app"), repo_git("gw")
    (gw / "sujo.txt").write_text("x", encoding="utf-8")
    r = rodar("preparar_branch", "preparar", "--historia", "PROJ-1", "--repos", app, gw)
    assert r.returncode == 1 and "não commitadas" in r.stderr
    assert git(app, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() == "develop"
    assert not (runs / "active.json").exists()


def test_verificar(rodar, runs, repo_git):
    app = repo_git("app")
    assert rodar("preparar_branch", "verificar").returncode == 1  # sem execução ativa
    rodar("preparar_branch", "preparar", "--historia", "PROJ-1", "--repos", app)
    assert rodar("preparar_branch", "verificar").returncode == 0
    git(app, "switch", "-q", "develop")
    r = rodar("preparar_branch", "verificar")
    assert r.returncode == 1 and "esperado 'feature/PROJ-1'" in r.stderr


def test_commit_so_em_repo_com_mudanca(rodar, runs, repo_git):
    app, gw = repo_git("app"), repo_git("gw")
    rodar("preparar_branch", "preparar", "--historia", "PROJ-1", "--repos", app, gw)
    (app / "Novo.java").write_text("class Novo {}", encoding="utf-8")
    r = rodar("preparar_branch", "commit", "--mensagem", "PROJ-1: teste")
    assert r.returncode == 0, r.stderr
    assert git(app, "log", "-1", "--format=%s").stdout.strip() == "PROJ-1: teste"
    assert git(gw, "log", "-1", "--format=%s").stdout.strip() == "inicial"


def test_commit_fora_da_branch_falha(rodar, runs, repo_git):
    app = repo_git("app")
    rodar("preparar_branch", "preparar", "--historia", "PROJ-1", "--repos", app)
    git(app, "switch", "-q", "develop")
    (app / "x.txt").write_text("x", encoding="utf-8")
    assert rodar("preparar_branch", "commit", "--mensagem", "m").returncode == 1


def test_encerrar_apaga_execucao(rodar, runs, repo_git):
    app = repo_git("app")
    rodar("preparar_branch", "preparar", "--historia", "PROJ-1", "--repos", app)
    assert rodar("preparar_branch", "encerrar").returncode == 0
    assert not (runs / "active.json").exists()


# ---------- pre-commit (instalado pelo sync) ----------

def test_pre_commit_bloqueia_fora_da_branch(rodar, runs, repo_git):
    gw = repo_git("gw")
    assert rodar("sync", "--repo", gw, "--perfil", "gateway").returncode == 0
    ativar(runs, "PROJ-1", [gw])
    (gw / "x.txt").write_text("x", encoding="utf-8")
    git(gw, "add", "-A")
    r = git(gw, "commit", "-m", "fora", check=False)
    assert r.returncode != 0 and "Commit bloqueado" in r.stderr

    git(gw, "switch", "-q", "-c", "feature/PROJ-1")
    assert git(gw, "commit", "-q", "-m", "dentro", check=False).returncode == 0


def test_pre_commit_sem_execucao_ativa_libera(rodar, home, repo_git):
    gw = repo_git("gw")
    rodar("sync", "--repo", gw, "--perfil", "gateway")
    (gw / "x.txt").write_text("x", encoding="utf-8")
    git(gw, "add", "-A")
    assert git(gw, "commit", "-q", "-m", "manual", check=False).returncode == 0

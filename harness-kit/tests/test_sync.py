"""sync.py: o que cada perfil instala e se é seguro rodar de novo."""
import filecmp

import pytest

from conftest import RAIZ


def iguais(a, b):
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files:
        return False
    return all(iguais(a / d, b / d) for d in cmp.common_dirs)


@pytest.mark.parametrize("perfil", ["aplicacao", "bff"])
def test_perfil_com_agente(rodar, home, repo_git, perfil):
    repo = repo_git("app")
    r = rodar("sync", "--repo", repo, "--perfil", perfil)
    assert r.returncode == 0, r.stderr
    for caminho in (".claude/agents/review.md", ".claude/skills/code-review/SKILL.md",
                    ".claude/contratos/checklist-endpoint.md", ".claude/settings.json",
                    ".agents/skills/desenvolver-historia/SKILL.md", ".agents/HARNESS-KIT.md",
                    "AGENTS.md", "CLAUDE.md", ".mcp.json", ".harness/project.yaml",
                    ".harness/sensores.json", ".harness/kit-version",
                    "docs/patterns/paginacao.md", ".git/hooks/pre-commit"):
        assert (repo / caminho).exists(), caminho
    assert iguais(repo / ".claude" / "skills", repo / ".agents" / "skills")
    assert iguais(RAIZ / "kit" / "skills", repo / ".claude" / "skills")
    assert ".claude/settings.local.json" in (repo / ".gitignore").read_text(encoding="utf-8")


def test_perfil_gateway(rodar, home, repo_git):
    repo = repo_git("gw")
    assert rodar("sync", "--repo", repo, "--perfil", "gateway").returncode == 0
    assert (repo / ".git" / "hooks" / "pre-commit").exists()
    assert "Gateway" in (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert not (repo / ".claude").exists() and not (repo / ".agents").exists()


def test_rodar_de_novo_nao_sobrescreve_o_que_e_do_repo(rodar, home, repo_git):
    repo = repo_git("app")
    rodar("sync", "--repo", repo, "--perfil", "aplicacao")
    (repo / "AGENTS.md").write_text("meu AGENTS", encoding="utf-8")
    (repo / "docs" / "patterns" / "testes.md").write_text("meu padrão", encoding="utf-8")
    (repo / ".claude" / "agents" / "review.md").write_text("editado à mão", encoding="utf-8")

    r = rodar("sync", "--repo", repo, "--perfil", "aplicacao")
    assert r.returncode == 0
    assert (repo / "AGENTS.md").read_text(encoding="utf-8") == "meu AGENTS"
    assert (repo / "docs" / "patterns" / "testes.md").read_text(encoding="utf-8") == "meu padrão"
    # o que vem do kit volta a ser a versão do kit
    assert (repo / ".claude" / "agents" / "review.md").read_text(encoding="utf-8") != "editado à mão"
    assert "settings.json já existe" in r.stdout


def test_recusa_pasta_que_nao_e_repo(rodar, home, tmp_path):
    r = rodar("sync", "--repo", tmp_path, "--perfil", "aplicacao")
    assert r.returncode != 0 and "não é a raiz de um repo git" in r.stderr

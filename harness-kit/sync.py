"""Instala/atualiza o harness em um repo.

    python sync.py --repo C:/dev/aplicacao-java --perfil aplicacao
    python sync.py --repo C:/dev/gateway-padrao --perfil gateway

- O que vem de kit/ é SOBRESCRITO (o kit é a fonte da verdade).
- O que vem de templates/ só é criado se NÃO existir (depois o repo é dono).
"""
import argparse
import shutil
import stat
import sys
from pathlib import Path

KIT = Path(__file__).parent / "kit"
TEMPLATES = Path(__file__).parent / "templates"
VERSION = (Path(__file__).parent / "VERSION").read_text().strip()

# Pastas que cada ferramenta lê. Confirme os caminhos do Devin e adicione aqui.
DESTINOS_AGENTE = [".claude"]

PERFIS = {
    "aplicacao": {"agente": True, "agents_md": "AGENTS.md", "project": "project-aplicacao.yaml", "sensores": "sensores-aplicacao.json"},
    "bff": {"agente": True, "agents_md": "AGENTS.md", "project": "project-bff.yaml", "sensores": "sensores-aplicacao.json"},
    "gateway": {"agente": False, "agents_md": "AGENTS-gateway.md", "project": "project-gateway.yaml", "sensores": "sensores-gateway.json"},
}


def copiar_dir(origem: Path, destino: Path):
    for item in origem.iterdir():  # sobrescreve só o que o kit traz
        alvo = destino / item.name
        if item.is_dir():
            shutil.rmtree(alvo, ignore_errors=True)
            shutil.copytree(item, alvo)
        else:
            destino.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, alvo)


def criar_se_faltar(origem: Path, destino: Path):
    if destino.exists():
        print(f"  mantido (já existe): {destino.name}")
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)
    print(f"  criado a partir do template: {destino}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--perfil", required=True, choices=PERFIS)
    a = p.parse_args()

    repo, perfil = Path(a.repo).resolve(), PERFIS[a.perfil]
    if not (repo / ".git").is_dir():
        sys.exit(f"ERRO: {repo} não é a raiz de um repo git.")
    print(f"harness-kit {VERSION} → {repo} ({a.perfil})")

    if perfil["agente"]:
        for pasta in DESTINOS_AGENTE:
            base = repo / pasta
            for parte in ("skills", "agents", "hooks", "sensores", "contratos", "mcp", "medicao", "aprendizado"):
                copiar_dir(KIT / parte, base / parte)
            settings = base / "settings.json"
            if settings.exists():
                print(f"  ATENÇÃO: {settings} já existe. Junte à mão os hooks de kit/settings.json.")
            else:
                shutil.copy2(KIT / "settings.json", settings)
            (base / "HARNESS-KIT.md").write_text(
                f"Arquivos de skills/, agents/, hooks/, sensores/, contratos/, mcp/, medicao/ e aprendizado/ vêm do harness-kit {VERSION}.\n"
                "Não edite aqui: edite no kit e rode o sync de novo.\n", encoding="utf-8")
        criar_se_faltar_texto(repo / "CLAUDE.md", "@AGENTS.md\n")
        criar_se_faltar(KIT / "mcp" / "mcp.json", repo / ".mcp.json")
        criar_se_faltar(TEMPLATES / "mcp-config.json", repo / ".harness" / "mcp.json")
        garantir_gitignore(repo, ".claude/settings.local.json")

    criar_se_faltar(TEMPLATES / perfil["agents_md"], repo / "AGENTS.md")
    criar_se_faltar(TEMPLATES / perfil["project"], repo / ".harness" / "project.yaml")
    criar_se_faltar(TEMPLATES / "sensores" / perfil["sensores"], repo / ".harness" / "sensores.json")

    hooks = repo / ".git" / "hooks"
    copiar_dir(KIT / "githooks", hooks)
    (hooks / "pre-commit").chmod((hooks / "pre-commit").stat().st_mode | stat.S_IEXEC)

    (repo / ".harness").mkdir(exist_ok=True)
    (repo / ".harness" / "kit-version").write_text(VERSION + "\n", encoding="utf-8")
    print("OK")


def criar_se_faltar_texto(destino: Path, conteudo: str):
    if not destino.exists():
        destino.write_text(conteudo, encoding="utf-8")
        print(f"  criado: {destino.name}")


def garantir_gitignore(repo: Path, linha: str):
    gi = repo / ".gitignore"
    atual = gi.read_text(encoding="utf-8") if gi.exists() else ""
    if linha not in atual.splitlines():
        gi.write_text(atual + ("" if atual.endswith("\n") or not atual else "\n") + linha + "\n", encoding="utf-8")
        print(f"  .gitignore: adicionado {linha}")


if __name__ == "__main__":
    main()

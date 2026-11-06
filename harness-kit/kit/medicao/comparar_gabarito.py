"""Compara o que o harness alterou com o que foi entregue de verdade.

    python comparar_gabarito.py --repo C:/dev/aplicacao-java \
        --base <commit antes da entrega> --gabarito <commit/branch entregue> \
        --harness <branch gerada pelo harness>

Cobertura: dos arquivos do gabarito, quantos o harness também alterou.
Precisão: dos arquivos que o harness alterou, quantos estão no gabarito.
"""
import argparse
import subprocess


def arquivos(repo, base, ref):
    out = subprocess.run(["git", "-C", repo, "diff", "--name-only", f"{base}..{ref}"],
                         capture_output=True, text=True, check=True).stdout
    return {l.strip() for l in out.splitlines() if l.strip()}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for a in ("--repo", "--base", "--gabarito", "--harness"):
        p.add_argument(a, required=True)
    a = p.parse_args()
    g, h = arquivos(a.repo, a.base, a.gabarito), arquivos(a.repo, a.base, a.harness)
    comuns = g & h
    print(f"Cobertura: {len(comuns)}/{len(g)} ({len(comuns) / len(g):.0%})" if g else "Gabarito vazio")
    print(f"Precisão:  {len(comuns)}/{len(h)} ({len(comuns) / len(h):.0%})" if h else "Harness não alterou nada")
    if g - h:
        print("Faltou alterar:\n  " + "\n  ".join(sorted(g - h)))
    if h - g:
        print("Alterou a mais:\n  " + "\n  ".join(sorted(h - g)))

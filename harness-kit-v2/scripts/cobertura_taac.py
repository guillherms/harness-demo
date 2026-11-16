"""Confere se todo critério de aceite (CA) da spec tem pelo menos um cenário no TAAC.

Uso:
    python cobertura_taac.py <spec.md> <pasta das features> --historia <id>

- Lê os CAs da seção "## Critérios de aceite" da spec (linhas com **CA1**, CA2: ...).
- Procura nas features (*.feature, recursivo) tags no formato @<id>-CA<n>
  em cenários, outlines ou na feature inteira.
- Saída 0 = todos os CAs cobertos; 1 = falta algum (lista quais).

Confere só a EXISTÊNCIA do cenário com a tag. Se o cenário testa de verdade o critério,
quem confere é o revisor.
"""
import argparse
import os
import re
import sys


def cas_da_spec(caminho):
    with open(caminho, encoding="utf-8") as f:
        texto = f.read()
    secao = re.search(r"^##\s*Crit[ée]rios de aceite\s*$(.*?)(?=^##\s|\Z)", texto,
                      re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not secao:
        sys.exit("[ERRO] seção '## Critérios de aceite' não encontrada na spec.")
    return sorted({int(n) for n in re.findall(r"\bCA(\d+)\b", secao.group(1))})


def tags_das_features(pasta, historia):
    padrao = re.compile(rf"@{re.escape(historia)}-CA(\d+)\b", re.IGNORECASE)
    cobertos = {}
    for raiz, _, arquivos in os.walk(pasta):
        for nome in arquivos:
            if not nome.endswith(".feature"):
                continue
            caminho = os.path.join(raiz, nome)
            with open(caminho, encoding="utf-8") as f:
                for i, linha in enumerate(f, 1):
                    if linha.strip().startswith("@"):
                        for n in padrao.findall(linha):
                            cobertos.setdefault(int(n), []).append(f"{os.path.relpath(caminho, pasta)}:{i}")
    return cobertos


def main():
    p = argparse.ArgumentParser()
    p.add_argument("spec")
    p.add_argument("features")
    p.add_argument("--historia", required=True, help="ID da história (prefixo das tags)")
    a = p.parse_args()

    cas = cas_da_spec(a.spec)
    if not cas:
        sys.exit("[ERRO] nenhum CA numerado na seção de critérios de aceite.")
    cobertos = tags_das_features(a.features, a.historia)

    faltando = [n for n in cas if n not in cobertos]
    extras = sorted(set(cobertos) - set(cas))
    for n in cas:
        if n in cobertos:
            print(f"OK      CA{n}  ->  {', '.join(cobertos[n])}")
        else:
            print(f"FALTA   CA{n}  (nenhum cenário com @{a.historia}-CA{n})")
    if extras:
        print(f"\nAviso: tags para CAs que não existem na spec: {', '.join(f'CA{n}' for n in extras)}")
    print(f"\n{len(cas) - len(faltando)}/{len(cas)} critérios cobertos")
    sys.exit(1 if faltando else 0)


if __name__ == "__main__":
    main()

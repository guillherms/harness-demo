"""Lista as rotas da aplicação que ainda não existem no BFF, comparando os contratos OpenAPI.

Uso:
    python diff_contratos.py --app gateway.yaml --bff gateway-bff.yaml --filtro "app-1"
    python diff_contratos.py ... --mapa mapa.yaml     # equivalências de rota app -> bff
    python diff_contratos.py ... --json               # saída em JSON (para o orquestrador)

--filtro    texto ou regex procurado na integração da rota (ex.: parte da URI da aplicação 1).
            Só as rotas da aplicação cuja integração bate com o filtro entram na comparação.
--filtro-bff  idem, para o contrato do BFF (opcional; padrão: todas as rotas do BFF).
--mapa      YAML com equivalências quando o BFF não espelha o path 1:1, ex.:
                "GET /pessoas": "GET /bff/pessoas"
                "GET /pessoas/{id}": "GET /bff/pessoas/{pessoaId}"

Como uma rota da app casa com uma do BFF (nesta ordem):
  1. entrada no --mapa
  2. mesmo operationId nos dois contratos
  3. mesmo método + path (ignorando o nome dos parâmetros: {id} == {pessoaId})
"""
import argparse
import json
import re
import sys

import yaml

METODOS = {"get", "post", "put", "patch", "delete", "head", "options"}
CHAVES_INTEGRACAO = ("x-amazon-apigateway-integration", "integration", "integrations")


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f)  # YAML também lê JSON


def texto_integracao(op):
    """Junta tudo que estiver na integração (uri, Fn::Sub, stage variables...) num texto só."""
    for chave in CHAVES_INTEGRACAO:
        if chave in op:
            return json.dumps(op[chave], ensure_ascii=False)
    return ""


def normalizar(path):
    return re.sub(r"\{[^}]+\}", "{}", path.rstrip("/") or "/")


def rotas(contrato, filtro=None):
    regex = re.compile(filtro) if filtro else None
    incluidas, ignoradas = [], 0
    for path, item in (contrato.get("paths") or {}).items():
        for metodo, op in (item or {}).items():
            if metodo.lower() not in METODOS or not isinstance(op, dict):
                continue
            if regex and not regex.search(texto_integracao(op)):
                ignoradas += 1
                continue
            incluidas.append({
                "rota": f"{metodo.upper()} {path}",
                "chave": f"{metodo.upper()} {normalizar(path)}",
                "operationId": op.get("operationId"),
                "resumo": op.get("summary", ""),
            })
    return incluidas, ignoradas


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--app", required=True, help="contrato OpenAPI do gateway da aplicação")
    p.add_argument("--bff", required=True, help="contrato OpenAPI do gateway do BFF")
    p.add_argument("--filtro", required=True, help="texto/regex da integração da aplicação 1")
    p.add_argument("--filtro-bff", help="texto/regex da integração no contrato do BFF")
    p.add_argument("--mapa", help="YAML de equivalências 'METODO /app' -> 'METODO /bff'")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    app, ignoradas = rotas(carregar(a.app), a.filtro)
    bff, _ = rotas(carregar(a.bff), a.filtro_bff)
    mapa = {}
    if a.mapa:
        bruto = carregar(a.mapa) or {}
        mapa = {k.split(" ", 1)[0].upper() + " " + normalizar(k.split(" ", 1)[1]):
                v.split(" ", 1)[0].upper() + " " + normalizar(v.split(" ", 1)[1])
                for k, v in bruto.items()}

    chaves_bff = {r["chave"] for r in bff}
    ops_bff = {r["operationId"] for r in bff if r["operationId"]}

    faltando, existentes = [], []
    for r in app:
        if r["chave"] in mapa:
            achou = mapa[r["chave"]] in chaves_bff
        elif r["operationId"] and r["operationId"] in ops_bff:
            achou = True
        else:
            achou = r["chave"] in chaves_bff
        (existentes if achou else faltando).append(r)

    if a.json:
        print(json.dumps({"faltando_no_bff": faltando, "ja_existem": existentes,
                          "ignoradas_outras_integracoes": ignoradas}, ensure_ascii=False, indent=2))
    else:
        print(f"Rotas da aplicação (filtro '{a.filtro}'): {len(app)}  |  ignoradas (outras integrações): {ignoradas}")
        print(f"\nFALTANDO NO BFF ({len(faltando)})")
        for r in faltando:
            print(f"  {r['rota']:<35} {r['resumo']}")
        print(f"\nJÁ EXISTEM NO BFF ({len(existentes)})")
        for r in existentes:
            print(f"  {r['rota']}")
    sys.exit(0)


if __name__ == "__main__":
    main()

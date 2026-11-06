"""Valida a spec do api-owner: schema + regras que schema não expressa.

Uso direto:   python validar_spec.py <spec.json> [--pronta]
Como hook:    PostToolUse em Write; só age em ~/.harness/runs/<id>/spec.json

--pronta: exige pendencias vazia (gate antes de seguir para o código).
Depende de `jsonschema` (já vem junto com o openapi-spec-validator).
"""
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA = json.loads((Path(__file__).parent / "spec.schema.json").read_text(encoding="utf-8"))


def validar(spec: dict, pronta: bool) -> list[str]:
    erros = [f"{'/'.join(map(str, e.path)) or '(raiz)'}: {e.message}"
             for e in Draft202012Validator(SCHEMA).iter_errors(spec)]
    if erros:
        return erros  # regras semânticas só fazem sentido com a estrutura certa

    vistos = set()
    for i, ep in enumerate(spec["endpoints"]):
        chave = (ep["metodo"], ep["path"])
        if chave in vistos:
            erros.append(f"endpoints/{i}: {ep['metodo']} {ep['path']} duplicado")
        vistos.add(chave)

        no_path = set(re.findall(r"\{(\w+)\}", ep["path"]))
        declarados = {c["nome"] for c in ep["request"].get("path_params", [])}
        if no_path != declarados:
            erros.append(f"endpoints/{i}: path_params {sorted(declarados)} não batem "
                         f"com o path {ep['path']} {sorted(no_path)}")

        if ep["metodo"] in ("GET", "DELETE") and ep["request"].get("body"):
            erros.append(f"endpoints/{i}: {ep['metodo']} não deve ter body")

    if pronta and spec["pendencias"]:
        erros.append(f"há {len(spec['pendencias'])} pendência(s): resolva com o usuário antes do código")
    return erros


def main():
    if len(sys.argv) > 1:  # uso direto
        caminho, pronta, modo_hook = Path(sys.argv[1]), "--pronta" in sys.argv, False
    else:  # hook PostToolUse
        payload = json.load(sys.stdin)
        arq = payload.get("tool_input", {}).get("file_path", "")
        runs = (Path.home() / ".harness" / "runs").resolve()
        caminho = Path(arq).resolve() if arq else None
        if not caminho or caminho.name != "spec.json" or runs not in caminho.parents:
            sys.exit(0)
        pronta, modo_hook = False, True

    try:
        spec = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"spec.json não é JSON válido: {e}", file=sys.stderr)
        sys.exit(2 if modo_hook else 1)

    erros = validar(spec, pronta)
    if erros:
        print("Spec inválida. Corrija:\n- " + "\n- ".join(erros[:15]), file=sys.stderr)
        sys.exit(2 if modo_hook else 1)
    print("Spec válida.")


if __name__ == "__main__":
    main()

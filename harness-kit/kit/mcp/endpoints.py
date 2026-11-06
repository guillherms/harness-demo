"""Lógica pura (sem MCP): endpoints do código Java × rotas do contrato OpenAPI.

Separado do servidor de propósito: se o MCP não for liberado no ambiente, o
mesmo código roda como script:
    python endpoints.py listar [repo]
    python endpoints.py comparar <contrato.yaml> [repo]

Limitação conhecida: leitura por regex. Paths montados com constantes ou
anotações quebradas em várias linhas não são resolvidos (aparecem como '?').
"""
import json
import re
import sys
from pathlib import Path

VERBOS = {"GetMapping": "GET", "PostMapping": "POST", "PutMapping": "PUT",
          "PatchMapping": "PATCH", "DeleteMapping": "DELETE"}
RE_CLASSE = re.compile(r"@(?:Rest)?Controller\b")
RE_MAPPING = re.compile(r"@(GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|RequestMapping)\s*(\(([^)]*)\))?")
RE_PATH = re.compile(r'(?:value\s*=\s*|path\s*=\s*)?\{?\s*"([^"]*)"')
RE_METODO = re.compile(r"RequestMethod\.(\w+)")
RE_CLASSE_NOME = re.compile(r"\bclass\s+(\w+)")


def _config(repo: Path) -> dict:
    arq = repo / ".harness" / "mcp.json"
    padrao = {"marcador_padrao": "entrypoint", "fonte": "src/main/java"}
    return {**padrao, **json.loads(arq.read_text(encoding="utf-8"))} if arq.exists() else padrao


def _path_de(args: str | None) -> str:
    if not args:
        return ""
    m = RE_PATH.search(args)
    return m.group(1) if m else "?"


def _juntar(base: str, sub: str) -> str:
    p = "/" + "/".join(x.strip("/") for x in (base, sub) if x and x.strip("/"))
    return p if p != "" else "/"


def listar(repo: str = ".") -> list[dict]:
    raiz = Path(repo).resolve()
    cfg = _config(raiz)
    achados = []
    for arq in sorted((raiz / cfg["fonte"]).rglob("*.java")):
        texto = arq.read_text(encoding="utf-8", errors="ignore")
        if not RE_CLASSE.search(texto):
            continue
        m_classe = RE_CLASSE_NOME.search(texto)
        corpo_ini = m_classe.start() if m_classe else 0
        base = ""
        for m in RE_MAPPING.finditer(texto[:corpo_ini]):  # @RequestMapping da classe
            if m.group(1) == "RequestMapping":
                base = _path_de(m.group(3))
        rel = arq.relative_to(raiz).as_posix()
        padrao = "padrao" if cfg["marcador_padrao"] in rel else "legado"
        for m in RE_MAPPING.finditer(texto, corpo_ini):
            anot, args = m.group(1), m.group(3)
            if anot == "RequestMapping":
                metodos = RE_METODO.findall(args or "") or ["ANY"]
            else:
                metodos = [VERBOS[anot]]
            for metodo in metodos:
                achados.append({
                    "metodo": metodo,
                    "path": _juntar(base, _path_de(args)),
                    "classe": m_classe.group(1) if m_classe else "?",
                    "arquivo": rel,
                    "linha": texto.count("\n", 0, m.start()) + 1,
                    "padrao": padrao,
                })
    return achados


def rotas_contrato(contrato: str) -> list[tuple[str, str]]:
    texto = Path(contrato).read_text(encoding="utf-8")
    if contrato.endswith(".json"):
        doc = json.loads(texto)
    else:
        import yaml  # PyYAML
        doc = yaml.safe_load(texto)
    verbos = {"get", "post", "put", "patch", "delete"}
    return sorted((v.upper(), p) for p, ops in (doc.get("paths") or {}).items()
                  for v in (ops or {}) if v in verbos)


def _chave(metodo: str, path: str, prefixo: str = "") -> tuple[str, str]:
    if prefixo and path.startswith(prefixo):
        path = path[len(prefixo):] or "/"
    return metodo, re.sub(r"\{[^}]+\}", "{}", path.rstrip("/") or "/")


def comparar(contrato: str, repo: str = ".", prefixo_contrato: str = "") -> dict:
    codigo = {_chave(e["metodo"], e["path"]): e for e in listar(repo)}
    contrato_ = {_chave(m, p, prefixo_contrato): (m, p) for m, p in rotas_contrato(contrato)}
    return {
        "so_no_contrato": sorted(f"{m} {p}" for k, (m, p) in contrato_.items() if k not in codigo),
        "so_no_codigo": sorted(f"{e['metodo']} {e['path']}" for k, e in codigo.items() if k not in contrato_),
        "em_ambos": len(set(codigo) & set(contrato_)),
    }


def tabela(endpoints: list[dict]) -> str:
    if not endpoints:
        return "Nenhum endpoint encontrado."
    return "\n".join(f"{e['metodo']:<6} {e['path']:<40} {e['classe']:<28} {e['padrao']:<7} {e['arquivo']}:{e['linha']}"
                     for e in endpoints)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "listar"
    if cmd == "listar":
        print(tabela(listar(sys.argv[2] if len(sys.argv) > 2 else ".")))
    elif cmd == "comparar":
        print(json.dumps(comparar(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "."), indent=2, ensure_ascii=False))

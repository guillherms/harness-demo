"""Servidor MCP local do harness (stdio).

Não precisa publicar nem rodar à mão: o Claude Code/Devin inicia este processo
quando a sessão abre, a partir do .mcp.json, e encerra quando ela fecha.
Requer: pip install mcp pyyaml
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
try:  # mcp 2.x (FastMCP foi renomeado para MCPServer)
    from mcp.server.mcpserver import MCPServer as Servidor
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as Servidor

import endpoints as ep  # noqa: E402

mcp = Servidor("harness")


@mcp.tool()
def listar_endpoints(repo: str = ".", filtro: str = "") -> str:
    """Lista os endpoints REST do repo Java: método, path, classe, se segue o
    padrão atual ou é legado, e arquivo:linha. Use ANTES de abrir controllers.
    `filtro` restringe por trecho do path (ex.: "/arquivos")."""
    itens = [e for e in ep.listar(repo) if filtro in e["path"]]
    return ep.tabela(itens)


@mcp.tool()
def endpoint_modelo(repo: str = ".", metodo: str = "GET") -> str:
    """Sugere um endpoint que segue o padrão atual, para usar como modelo ao
    criar um novo. Nunca devolve endpoint legado."""
    padrao = [e for e in ep.listar(repo) if e["padrao"] == "padrao"]
    mesmos = [e for e in padrao if e["metodo"] == metodo.upper()] or padrao
    return ep.tabela(mesmos[:3]) if mesmos else "Nenhum endpoint no padrão encontrado."


@mcp.tool()
def comparar_contrato(caminho_contrato: str, repo: str = ".", prefixo_contrato: str = "") -> str:
    """Compara as rotas do contrato OpenAPI do gateway com os endpoints do
    código. Mostra o que existe só de um lado. `prefixo_contrato` remove um
    prefixo do contrato que não existe no código (ex.: "/v1")."""
    r = ep.comparar(caminho_contrato, repo, prefixo_contrato)
    linhas = [f"Em ambos: {r['em_ambos']}"]
    linhas += ["Só no contrato:"] + [f"  {x}" for x in r["so_no_contrato"]]
    linhas += ["Só no código:"] + [f"  {x}" for x in r["so_no_codigo"]]
    return "\n".join(linhas)


if __name__ == "__main__":
    mcp.run()

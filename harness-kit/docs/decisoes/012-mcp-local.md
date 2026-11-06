# 012 — MCP local de endpoints (experimental)

**Decisão:** um servidor MCP local (`kit/mcp/harness_mcp.py`) com três
ferramentas: `listar_endpoints`, `endpoint_modelo` e `comparar_contrato`.

**Problema que resolve:** no brownfield, o agente acha endpoints fazendo grep e
abrindo controllers. Isso gasta contexto, varia a cada execução e pode usar um
endpoint legado como modelo. A ferramenta devolve uma tabela curta, sempre
igual, que já separa padrão de legado e aponta arquivo:linha.

**Como roda:** stdio. O Claude Code/Devin inicia o processo ao abrir a sessão,
a partir do `.mcp.json`, e encerra ao fechar. Nada é publicado.

**Desenho:** a lógica (`endpoints.py`) é separada do servidor. Se o pacote
`mcp` não for liberado no trabalho, a mesma lógica roda como script:
`python .claude/mcp/endpoints.py listar`.

**Status:** experimental. O valor deve ser confirmado com medição (ponto 5).
Para remover: apagar `kit/mcp/`, o `.mcp.json` do repo, `enabledMcpjsonServers`
e `mcp__harness` no settings, e as ferramentas `mcp__harness__*` dos agentes.

**Limitação:** leitura por regex. Paths montados com constantes ou anotações em
várias linhas aparecem como `?`. Legado × padrão é definido por um marcador no
caminho do arquivo (`.harness/mcp.json`, padrão `entrypoint`).

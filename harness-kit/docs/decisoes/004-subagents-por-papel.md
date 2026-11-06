# 004 — Subagents por papel: api-owner, codigo, review

**Decisão:** três subagents. "api owner" é o termo do time para quem altera APIs.

**Por quê:** contrato OpenAPI e código Java têm regras, ferramentas e validações
diferentes; separar evita um contexto carregando as regras dos dois repos.
Review read-only valida antes do commit.

**Regras:** uma spec só, extraída uma vez e passada a todos; todo o
human-in-the-loop acontece no orquestrador, antes de delegar (subagent não
conversa com o usuário); execução sequencial; review com no máximo 3 rodadas.

**Os mesmos agentes servem o par BFF:** o que muda é o AGENTS.md lido.

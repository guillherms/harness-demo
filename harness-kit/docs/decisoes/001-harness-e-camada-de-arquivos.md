# 001 — O harness é uma camada de arquivos, não um runtime

**Decisão:** não construir Execution Engine, LLM Gateway, Orchestrator, Policy
Engine ou Observability próprios. O harness é o conjunto de arquivos que Claude
Code e Devin já consomem: AGENTS.md, skills, subagents, hooks, settings e MCP.

**Por quê:** essas camadas já existem nas ferramentas (loop do agente, chamada
ao modelo, subagents, permissões, hooks, logs). Reimplementá-las seria refazer
o Claude Code de forma pior, além de esbarrar em aprovação de provedor de LLM.

**Quando revisar:** se for preciso rodar o fluxo headless (CI, Agent SDK).

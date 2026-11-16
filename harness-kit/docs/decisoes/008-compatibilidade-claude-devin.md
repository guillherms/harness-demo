# 008 — Compatível com Claude e Devin

**Decisão:** skills e agentes escritos uma vez, em formato neutro; o `sync.py`
sabe onde cada ferramenta lê. Lógica de hooks em scripts Python chamados por
hooks finos. Git hook nativo como garantia comum.

**Por quê:** no trabalho são usados Claude e Devin Desktop, no Windows. Formatos
de hook e suporte a subagents diferem entre as ferramentas.

**Skills em duas pastas:** não existe diretório de skills que os dois leiam.
O Claude Code lê `.claude/skills`; o Devin lê `.agents/skills` (padrão aberto
Agent Skills). O `sync.py` copia `kit/skills` para as duas (`DESTINOS_SKILLS`).
A fonte da verdade é o kit; as duas pastas no repo são cópias.

- **Por que não symlink:** no Git em Windows exige modo desenvolvedor e
  `core.symlinks`; quem clona sem isso recebe um arquivo de texto no lugar da
  pasta e a skill some sem erro aparente.
- **Por que não Gradle:** a v0 (`harness-agentes`) sincronizava com
  `gradle/sync-skills.gradle`. Com o kit como fonte, o `sync.py` já faz a cópia
  e vale para repos Maven e para os gateways também.

**Regras para a skill ser portável:**
- Frontmatter da skill só com `name` e `description`.
- Não depender de nome exato de ferramenta MCP: referenciar o servidor.
- Recurso que só um lado tem vira caminho alternativo, não pré-requisito. Ex.:
  sem subagents, o próprio agente segue a skill `code-review` julgando só pelo
  diff, spec e AGENTS.md.

**Pendente:** confirmar os caminhos e o suporte a subagents/hooks do Devin.

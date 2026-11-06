# 008 — Compatível com Claude e Devin

**Decisão:** skills e agentes escritos uma vez, em formato neutro; o `sync.py`
sabe onde cada ferramenta lê. Lógica de hooks em scripts Python chamados por
hooks finos. Git hook nativo como garantia comum.

**Por quê:** no trabalho são usados Claude e Devin Desktop, no Windows. Formatos
de hook e suporte a subagents diferem entre as ferramentas.

**Pendente:** confirmar os caminhos e o suporte a subagents/hooks do Devin.

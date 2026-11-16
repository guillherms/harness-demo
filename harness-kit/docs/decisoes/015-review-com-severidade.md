# 015 — Review com categoria e severidade

**Decisão:** os critérios de revisão saem do subagent e viram a skill
`code-review`; o subagent `review` só define quem revisa e com quais
ferramentas. Cada apontamento tem **categoria** (para o ciclo de aprendizado)
e **severidade** (BLOQUEANTE, IMPORTANTE, SUGESTÃO). APROVADO = zero
BLOQUEANTES.

**Por quê:**
- Categoria sozinha (0.7.0) não dizia o que impede o merge: qualquer
  apontamento reprovava, e o loop podia travar por gosto do revisor.
- Severidade com **regra citada obrigatória** (item da spec ou do AGENTS.md)
  torna o critério objetivo; sem regra, é SUGESTÃO.
- Skill separada funciona no Devin, que pode não ter subagents.
- Veio da v0 (`harness-agentes`), junto com escopo = diff e descartados que
  não voltam.

**Formato:** `- [categoria] [B1] arquivo:linha: problema → mudança (Regra: ...)`.
A categoria continua sendo o primeiro token, então `aprendizado.py` não muda.

**Loop:** só BLOQUEANTES voltam automaticamente ao `codigo` (máx. 3 rodadas).
IMPORTANTES e SUGESTÕES são mostrados ao usuário na aprovação: ele escolhe o
que corrigir e o que descartar (com motivo).

# 007 — Garantia de branch em três camadas

**Decisão:** `preparar-branch` no início, hook PreToolUse em Edit/Write durante
e git pre-commit no final.

**Por quê:** o risco é o agente alterar tudo na branch errada e só descobrir no
commit. Falhar **antes de editar** é mais barato. O PreToolUse pega na primeira
edição; o git hook é a rede que vale para qualquer ferramenta.

**Quem cuida da branch:** o orquestrador, não o agente de código, porque o
primeiro a editar é o api-owner (no gateway) e a branch precisa existir nos dois
repos. Subagents não executam git.

**Limitações:** o PreToolUse não cobre escrita via shell; uma execução ativa por
máquina.

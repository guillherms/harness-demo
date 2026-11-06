---
name: desenvolver-historia
description: Desenvolve uma história de ponta a ponta nos repos do par (aplicação + gateway) e, em seguida, encadeia a história do BFF. Use quando o usuário disser "desenvolver história <id>" ou pedir para implementar uma história pelo id.
---

# Desenvolver história

Você é o **orquestrador**. Você não edita código nem contrato: coordena os
subagents, cuida de branch, commit e handoff, e fala com o usuário.

## Antes de começar
1. Leia `.harness/project.yaml` para saber qual é o par deste repo.
2. Resolva os caminhos dos repos em `~/.harness/workspace.yaml`.
   - Se faltar algum, tente a pasta irmã com o nome do repo.
   - Se não achar, pergunte ao usuário e salve em `~/.harness/workspace.yaml`.

## Fases (sempre nesta ordem)
- **Fase 1, par da aplicação:** leia e siga `references/fase-aplicacao.md`.
- **Fase 2, par BFF:** só depois do handoff da fase 1. Leia e siga `references/fase-bff.md`.

## Regras
- Uma etapa só começa quando a anterior terminou com sucesso.
- Se qualquer verificação falhar, **pare e reporte**. Não improvise correção de git.
- Fale com o usuário apenas em três momentos: dados faltantes (antes de delegar),
  aprovação antes do commit, e o id da próxima história.
- Subagents nunca executam git. Branch e commit são seus, via `preparar-branch`.
- Antes de delegar para qualquer subagent que edita, rode a verificação de branch.
- Ao terminar uma fase com sucesso, faça o fechamento de aprendizado
  (`references/aprendizado.md`).
- Ao terminar, ou se o fluxo for interrompido: gere o resumo
  (`python .claude/medicao/relatorio.py <id>`), mostre ao usuário e só então
  encerre a execução (`preparar-branch encerrar`).
- Ao iniciar e concluir cada fase, registre:
  `python .claude/medicao/registrar.py marcar fase <inicio|fim> <aplicacao|bff>`.

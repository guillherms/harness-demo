---
name: preparar-branch
description: Prepara, verifica ou encerra a branch feature/<id> de uma história em um ou mais repos. Use antes de qualquer alteração de uma história, antes de cada etapa que edita arquivos e ao final do fluxo.
---

# Preparar branch

Sempre use o script. Comandos git de escrita estão bloqueados nas permissões:
branch e commit só passam por aqui.

- Preparar (cria ou faz checkout da branch e registra a execução ativa):
  `python .claude/skills/preparar-branch/scripts/preparar_branch.py preparar --historia <id> --repos <caminho> <caminho>`
- Verificar (antes de cada etapa que edita):
  `python .claude/skills/preparar-branch/scripts/preparar_branch.py verificar`
- Commit (só depois da aprovação do usuário; commita em todos os repos da execução):
  `python .claude/skills/preparar-branch/scripts/preparar_branch.py commit --mensagem "<id>: <título>"`
- Encerrar (ao final ou se o fluxo for interrompido):
  `python .claude/skills/preparar-branch/scripts/preparar_branch.py encerrar`

Se o script sair com erro, pare e mostre a mensagem ao usuário.

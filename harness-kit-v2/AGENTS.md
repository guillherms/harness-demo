# harness-kit

Este repo é o **workspace** do harness: ele roda de fora e trabalha nos repos do time.
Os repos alvo ficam em `local.yaml` (apelido → caminho). Leia esse arquivo primeiro.

## Pontos de entrada
- "desenvolver história(s) <ids> no <apelido>" → `.claude/skills/desenvolver-historias/SKILL.md`
- "desenvolver par <id-app> <id-bff>" → `.claude/skills/desenvolver-par/SKILL.md`
- "extrair referência <nome> de <apelido>" → `.claude/skills/extrair-referencia/SKILL.md`

## Regras gerais
- As regras de cada repo estão em `<repo>/.harness/constitution.md`. Ao mexer num repo, siga a constitution DELE.
- Tudo que o harness gera fica em `execucoes/<id>/` e `progress/<apelido>.md`, aqui no workspace.
- Infra só no LocalStack. Nunca toque a AWS real.
- Não edite o `AGENTS.md` dos repos alvo.

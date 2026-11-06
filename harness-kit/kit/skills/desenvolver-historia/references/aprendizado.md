# Fechamento: ciclo de aprendizado

Rode no fim de cada história, antes do relatório:
`python .claude/aprendizado/aprendizado.py analisar`

Se sair "Nada recorrente", siga. Se houver itens, para cada um proponha ao
usuário **onde** registrar, usando a regra: **o lugar mais determinístico que
resolve**.

| O que se repete | Onde registrar | Exemplo |
|---|---|---|
| Algo que máquina consegue checar | Sensor: regra ArchUnit, lint, teste | "domain importando Spring" → regra ArchUnit |
| Convenção do repo que o agente esquece | `AGENTS.md` ou `docs/patterns/` do repo | "DTO de resposta termina em Response" |
| Erro de processo do agente | Skill ou agente, **no harness-kit** | "codigo não rodou listar_endpoints antes" |
| Critério de julgamento | Checklist do `review.md`, **no harness-kit** | "teste precisa cobrir cada erro da spec" |
| Falha de sensor recorrente | O que faltou para o agente acertar antes | sensor de testes falha sempre → padrão de teste no AGENTS.md |

Para cada sugestão, mostre: o padrão observado (com os exemplos), o destino e o
texto exato proposto (uma ou duas linhas). **Não edite nada.** A mudança é feita
fora da branch da história, para não misturar com a entrega.

Se o usuário aprovar, registre:
`python .claude/aprendizado/aprendizado.py aplicar --categoria <cat> --onde <destino> --descricao "<regra>"`

Item marcado REINCIDENTE: a regra anterior não resolveu. Proponha um destino
mais determinístico do que o anterior (ex.: de AGENTS.md para sensor).

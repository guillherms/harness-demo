# Plan — história <id>

> Só para histórias complexas. Curto: decisões e tasks, não tutorial.

## Decisões técnicas
| Decisão | Escolha | Por quê / referência |
|---|---|---|
| <ex.: acesso ao banco> | <igual ao projeto X> | `.harness/referencias/banco.md` |

## Riscos / dúvidas para o humano
- <...>

## Tasks (em ordem; cada uma roda num subagent novo)
<!-- T1 é sempre o TAAC: os cenários viram o alvo das próximas tasks. -->
| # | Objetivo | Repo / área | Depende de | Pronto quando |
|---|---|---|---|---|
| T1 | Escrever as features do TAAC, 1 cenário por CA, com tags `@<id>-CA<n>` | `<repo>` testes | — | `cobertura_taac.py` passa (os cenários podem falhar) |
| T2 | <ex.: mapear o banco (datasource, entidade, migration)> | `<repo>` | T1 | build passa |
| T3 | <ex.: leitura do S3 + parser, com testes unitários> | `<repo>` | T2 | testes unitários passam |
| T4 | <ex.: listener ligando tudo, com testes unitários> | `<repo>` | T3 | build + TAAC verdes |

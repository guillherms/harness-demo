# Roteiro de evals

## 1. Montar o conjunto (uma vez)
Escolha de 3 a 5 histórias **já entregues**, variando o tipo:
criar endpoint, alterar endpoint, uma que mexeu em legado, uma do BFF.

Registre em `evals/historias.md`:

| História | Repo | Commit base (antes) | Gabarito (entregue) | Tipo |
|---|---|---|---|---|
| PROJ-101 | aplicacao-java | `abc123` | `def456` | criar |

- **Base:** o commit da develop imediatamente antes da entrega.
- **Gabarito:** o commit (ou branch) que foi para a develop com a entrega.

## 2. Rodar um cenário
Para cada história:
1. `git switch --detach <base>` na aplicação e no gateway.
2. Rode o fluxo normalmente: `desenvolver história <id>`. O `preparar-branch`
   cria a `feature/<id>` a partir dali (ajuste para não puxar a develop atual).
3. Responda as pendências como você responderia na época.
4. No fim, anote o resumo (`relatorio.py <id>`) e rode:
   `python .claude/medicao/comparar_gabarito.py --repo <repo> --base <base> --gabarito <gabarito> --harness feature/<id>`
5. Renomeie a pasta `~/.harness/runs/<id>` para `<id>-<cenario>` e apague a
   branch, para rodar o próximo cenário do zero.

## 3. Cenários sugeridos para o case
| Cenário | O que muda |
|---|---|
| A. sem harness | só o texto da história como prompt, sem skills/agentes |
| B. harness | kit completo, sem MCP |
| C. harness + MCP | kit completo |

## 4. Registrar
Preencha `docs/case/resultados.md`. Olhe primeiro: cobertura/precisão
(acertou?), intervenções humanas (quanto precisou de você?), depois tokens e
arquivos lidos (quanto custou?).

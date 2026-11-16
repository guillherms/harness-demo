---
name: desenvolver-par
description: Desenvolve um par de histórias ligadas — primeiro a da aplicação (+ gateway), depois a do BFF (+ gateway BFF) — usando o diff dos contratos como handoff. Use quando o usuário pedir "desenvolver par <id-app> <id-bff>".
---

# Desenvolver par (aplicação → BFF)

## 1. História da aplicação
Rode a skill `desenvolver-historias` para `<id-app>` no repo `aplicacao`.
Ela é complexa por definição (altera o satélite `gateway`): o contrato no gateway vem antes do código.

## 2. Handoff calculado (não escrito por agente)
Com os caminhos do `local.yaml` e o filtro de integração da constitution da aplicação, rode:
```
python scripts/diff_contratos.py --app <gateway>/<contrato> --bff <gateway_bff>/<contrato> \
  --filtro "<filtro da aplicação>" [--mapa <mapa.yaml>] --json > execucoes/<id-bff>/handoff.json
```
(Use a branch `feature/<id-app>` do gateway, onde estão as rotas novas.)

## 3. OK humano
Mostre a lista "faltando no BFF". O usuário confirma quais rotas entram na história do BFF
(o BFF nem sempre espelha 1:1; equivalências vão para um `--mapa`).

## 4. História do BFF
Rode `desenvolver-historias` para `<id-bff>` no repo `bff` (satélite `gateway_bff`).
O `spec-writer` recebe também `execucoes/<id-bff>/handoff.json` como entrada.
O BFF não tem regra de negócio: replica as rotas seguindo o padrão do BFF.

## 5. Fechar
Rode o diff de novo: "faltando no BFF" deve estar vazio para as rotas confirmadas.

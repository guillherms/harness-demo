# AGENTS.md

<!-- Template. Substitua cada TODO pelo que vale no repositório. -->
<!-- Mantenha curto (~150 linhas no máximo). Detalhes vão em docs/ e são apontados daqui. -->

## Visão geral
TODO: 2-3 linhas. Que sistema é este, quem consome, onde roda.

## Comandos
- Build: TODO
- Testes unitários: TODO
- TAAC: TODO
- Rode testes unitários e TAAC antes de considerar uma tarefa pronta.

## Arquitetura
TODO: regras verificáveis de como ESTE repo aplica clean arch. Exemplos de formato:
- Camadas: TODO (ex: adapter/in → application → domain ← adapter/out)
- Controller nunca acessa repository: sempre via use case.
- domain/ não depende de Spring.
Detalhes: docs/arquitetura.md

## Mapa do projeto
- TODO/pasta: o que fica aqui
- TODO/pasta: o que fica aqui
- TODO: onde fica o contrato OpenAPI

## Referências e legado
- Endpoints de referência (use estes como exemplo, não outros):
  - simples: TODO
  - paginado: TODO
  - com integração externa: TODO
- Código legado anterior ao padrão atual (não use como exemplo): TODO
  O repositório adotou clean arch com o tempo; parte dos endpoints antigos não segue o padrão.
- Não refatore código fora do escopo da tarefa sem pedido explícito.

## Testes
- Unitários: TODO (framework e padrão)
- TAAC: modelo em docs/testes/taac.md
- Specs de história: specs/<id-da-historia>.md

# Aplicação Java

<!-- Template do harness-kit. Substitua cada <placeholder> pelo que vale neste repo. -->
<!-- Mantenha curto (~150 linhas no máximo). Detalhes vão em docs/ e são apontados daqui. -->

## Visão geral
<o que a aplicação faz, quem consome, onde roda, em 2-3 linhas>

## Comandos
- Build: `<comando>`
- Testes unitários: `<comando>`
- TAAC: `<comando>`
- Rode testes unitários e TAAC antes de considerar uma tarefa pronta.

## Arquitetura
Regras verificáveis de como ESTE repo aplica clean arch. Exemplos de formato:
- Camadas: `<ex: entrypoint → application → domain ← infrastructure>`
- Controller nunca acessa repository: sempre via use case.
- `domain/` não depende de Spring.
Detalhes: `docs/arquitetura.md`

## Mapa do projeto
- `<pasta>`: o que fica aqui
- `<pasta>`: o que fica aqui
- Contrato OpenAPI: no repo de gateway do par (veja `.harness/project.yaml`).

## Referências e legado
- Endpoints de referência (use estes como exemplo, não outros):
  - simples: `<caminho>`
  - paginado: `<caminho>`
  - com integração externa: `<caminho>`
- Código legado anterior ao padrão atual (não use como exemplo): `<pacote legado>`
- Não refatore código fora do escopo da tarefa sem pedido explícito.

## Padrões (leia só quando a tarefa pedir)
- Criar/alterar endpoint: `docs/patterns/endpoint.md`
- Paginação: `docs/patterns/paginacao.md`
- Testes unitários e TAAC: `docs/patterns/testes.md`

## Harness
- Este repo tem par: veja `.harness/project.yaml`.
- Histórias são desenvolvidas pela skill `desenvolver-historia`.

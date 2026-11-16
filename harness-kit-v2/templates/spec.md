# Spec — história <id>: <título curto>

> Só comportamento e regra de negócio. A estrutura vem do código de referência do repo.

## Objetivo
<1-2 frases>

## Critérios de aceite
<!-- COPIADOS da história, sem reescrever. Cada um vira cenário no TAAC com a tag @<id>-CA<n>. -->
- **CA1**: <texto do critério>
- **CA2**: <texto do critério>

## Gatilho / entrada
- <mensagem na fila X (tópico, filtro, payload de exemplo) | rota HTTP | ...>

## Regras e validações
- <campo X obrigatório; se faltar → ...>

## Efeitos
- <lê arquivo do bucket Y | grava na tabela Z | publica em W ...>

## Erros e idempotência
- Mensagem/requisição repetida: <...>
- Erro de negócio: <...>
- Erro técnico: <retry / DLQ / status HTTP>

## Cenários (base dos testes unitários e do TAAC)
1. **Dado** <contexto> **quando** <ação> **então** <resultado>  (CA1)
2. ...

## Dependências
### Entregável (vai no código/PR)
- <ex.: migration da tabela Z, entidade, config do datasource>
### Ambiente local (só para testar)
- <ex.: fila, bucket com arquivo de exemplo, seed> → detalhado no `infra.yaml`
### Não suportado pelo harness
<!-- Tudo que o harness não sabe montar sozinho ou que é decisão técnica: banco não mapeado,
     API externa sem mock, recurso AWS fora de SNS/SQS/S3... Se houver algo aqui, o fluxo PARA no OK humano. -->
- <item> → <o que você sugere / referência possível>

## Lacunas (perguntas para o humano)
- [ ] <o que a história não diz>

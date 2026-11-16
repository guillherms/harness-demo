---
name: spec-historia
description: Lê uma história (via MCP) e escreve a spec (regra + critérios de aceite com ID) e o infra.yaml do teste local, apontando o que o harness não suporta. Use na etapa de spec de qualquer história.
---

# Spec da história

## Leia (só isso)
1. `<repo>/.harness/constitution.md`
2. A história, pela ferramenta MCP indicada na constitution
3. O código de referência e o teste dele (caminhos na constitution) — para entender o padrão, não para copiar regra
4. `progress/<apelido>.md`, se existir
5. `execucoes/<id>/handoff.json`, se existir (histórias de BFF)

## Escreva
- `execucoes/<id>/spec.md` a partir de `templates/spec.md`
- `execucoes/<id>/infra.yaml` a partir de `templates/infra.yaml` (remova seções que a história não usa)
- arquivos de exemplo em `execucoes/<id>/amostras/` quando a história precisar (ex.: o arquivo que vai no S3),
  seguindo o layout descrito na história; se o layout não estiver descrito, vira lacuna

## Regras
- **Critérios de aceite: copie da história sem reescrever** e numere CA1, CA2…
- Spec descreve comportamento e regra, não estrutura.
- Use nomes (fila, bucket, tabela, rota) que estão **na história**. Se não estiverem, siga o padrão da constitution e marque como lacuna.
- Classifique cada dependência: **entregável** (vai no PR: migration, entidade), **ambiente local** (fila, bucket, seed) ou **não suportado**.
- **Não suportado** = tudo que o `infra.yaml` não cobre (só SNS, SQS, S3) ou que é decisão técnica:
  banco não mapeado no repo, API externa sem mock, outro serviço AWS. Liste na spec e em `nao_suportado` no `infra.yaml`.
  Se a constitution lista uma referência que resolve (ex.: banco do projeto X), cite-a como sugestão.
- Cenários de teste local no `infra.yaml`: pelo menos 1 caminho feliz, 1 barrado pelo filtro (se houver filtro) e 1 de DLQ (se houver DLQ).
- **Não invente regra.** O que faltar vai em "Lacunas", como pergunta objetiva.
- Não escreva código.

## Entregue
Resposta curta: caminhos dos arquivos, lista de lacunas e lista de não suportados.

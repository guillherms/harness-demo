---
name: extrair-referencia
description: Extrai uma única vez, de um repo de referência, o padrão de algo (ex.: como mapear o banco) para um resumo curto que os agentes leem no lugar do repo inteiro. Use quando o usuário pedir "extrair referência <nome> de <repo>".
---

# Extrair referência

Objetivo: os agentes nunca exploram o repo de referência por conta própria. Eles leem este resumo.

## Passos
1. Resolva o caminho do repo de origem em `local.yaml` (`referencias:` ou `repos:`).
2. Encontre os arquivos que compõem o padrão pedido (ex.: banco → config do datasource, entidade, repository, migration, config de teste).
3. Escreva `<repo alvo>/.harness/referencias/<nome>.md` a partir de `templates/referencia.md`:
   - **trechos curtos**, só o que define o padrão (nada de arquivos inteiros);
   - como isso roda localmente / em teste no repo de origem;
   - cuidados (dialeto, schema, credenciais locais).
4. Registre a referência na tabela "Referências externas" da constitution do repo alvo.
5. Mostre o resumo ao usuário para conferência antes de dar como pronto.

## Nunca
- Copiar segredos, senhas ou URLs reais de ambiente. Use placeholders.
- Alterar o repo de origem (é só leitura).

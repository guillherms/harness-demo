# Fluxo: criar endpoint

## 1. Validar o contexto
Leia `references/checklist-criar-endpoint.md` e marque cada item da spec:
- ✅ encontrado: cite o trecho da história que sustenta
- 🟡 inferido: diga de onde veio (default do checklist, padrão do módulo)
- ❌ faltando

Se você não consegue citar um trecho, o item não é ✅.

## 2. Perguntar o que falta
Pergunte todos os 🟡 e ❌ de uma vez, numa lista curta. Não pergunte o que já
está ✅. Não avance com ❌ em item obrigatório.

## 3. Confirmar a spec
Mostre a spec completa e espere o ok. A partir daqui ela é a fonte de verdade;
não volte ao texto da história.

## 4. Escolher a referência
Use os endpoints de referência listados no AGENTS.md, escolhendo pela variação
que a spec indica (simples, paginado, com integração externa...). Leia:
- o endpoint de referência escolhido;
- os arquivos que você vai alterar (entidade existente, repository, registro da
  rota, contrato OpenAPI).

Não use outros endpoints do repositório como exemplo: parte deles é legado fora
do padrão. Se precisar ler algo fora dessa lista, diga o que e por quê antes.

Se a spec tem paginação, leia também `references/paginacao.md`.

## 5. Gerar
Siga a arquitetura do AGENTS.md e a estrutura da referência. Atualize o contrato
OpenAPI. Não refatore código existente que não faz parte da história.

## 6. Testes
- Testes unitários seguindo o padrão do AGENTS.md: um cenário por regra de
  negócio e por erro listado na spec.
- TAAC seguindo o modelo do repositório (o AGENTS.md aponta o documento).

Volte para o passo 6 do SKILL.md.

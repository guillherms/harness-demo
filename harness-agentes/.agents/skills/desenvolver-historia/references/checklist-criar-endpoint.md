# Checklist: criar endpoint

Legenda: [obrigatório] precisa estar ✅ ou confirmado pelo usuário ·
[condicional] obrigatório só na condição indicada ·
[inferível] tem default; marque 🟡 e confirme

## Identificação
- Método HTTP [obrigatório]
- Path da rota [obrigatório]
- Módulo/domínio onde vive [obrigatório]

## Entrada
- Path params: nome e tipo [obrigatório se a rota tiver]
- Query params: nome, tipo, obrigatoriedade, default [condicional: se a história mencionar filtros]
- Body: campos, tipos, validações [condicional: POST/PUT/PATCH]

## Paginação
- Tem paginação? [obrigatório se for GET de lista]
- Se sim: ver `references/paginacao.md`

## Dados
- Entidade: existente ou nova? [obrigatório]
- Integração externa: qual serviço e contrato [condicional: se houver]

## Saída
- Status de sucesso [inferível: GET 200, POST 201, PUT/PATCH 200, DELETE 204]
- Campos do response [obrigatório]
- Erros de negócio: cenário → status [obrigatório]

## Regras de negócio
- Lista de regras, cada uma verificável por um teste [obrigatório]
  Regra vaga ("validar o cliente") é ❌: pergunte o critério.

## Contrato e testes
- Atualizar contrato OpenAPI [inferível: sim]
- Cenários de TAAC [inferível: derivar das regras e dos erros]

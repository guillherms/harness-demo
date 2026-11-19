# Checklist: integração com API

> Aplica-se a histórias que **chamam** uma API externa ou interna (HTTP/REST).
> Somar com: `base.md` + checklist do gatilho (ex.: `listener-sqs.md`, `endpoint.md`).

## Como usar
Mesmo fluxo do `listener-sqs.md`: descobrir → confirmar → perguntar o que falta.
Status: `DESCOBERTO` | `DECIDIDO` | `PENDENTE` | `N/A` (com justificativa).

**Gate:** nenhum item `PENDENTE` antes de implementar.

---

## Contrato

### API-01: Contrato
- **Pergunta:** qual endpoint, método, request e response? Existe OpenAPI/Swagger ou exemplo real?
- **Onde procurar:** contratos no repo do gateway, clients já existentes no projeto, história.
- **Por que importa:** sem contrato, o agente inventa campos.

### API-02: Natureza da operação
- **Pergunta:** a chamada é só **leitura** (consulta) ou **altera estado** do outro lado?
- **Por que importa:** retry de leitura é seguro. Retry de escrita pode duplicar no sistema de destino, e aí é preciso idempotência do lado da API (ex.: idempotency key).

### API-03: Lote × unitário
- **Pergunta:** a API aceita lote? Qual o tamanho máximo do lote? Quantas chamadas por execução (ex.: 5 a 10)?
- **Padrão sugerido:** preferir lote quando existir; reduz tempo e falhas parciais.

### API-04: Mapeamento
- **Pergunta:** como cada campo da resposta mapeia para o domínio/tabelas? O que fazer com campo nulo ou registro não encontrado?
- **Por que importa:** "não encontrado" quase sempre é decisão de negócio, não técnica.

## Desempenho e resiliência

### API-05: SLO de latência
- **Pergunta:** qual a latência p99 da API? Quem é o time dono?
- **Onde procurar:** documentação da API, APM/observabilidade, time dono.
- **Por que importa:** é o número que alimenta o cálculo de timeout (e o SQS-04).

### API-06: Timeout do client
- **Pergunta:** qual o connect timeout e o read timeout?
- **Regra:** derivar do SLO (ex.: p99 × 2), **nunca** usar o padrão da biblioteca.
- **Checagem:** `chamadas × timeout × (1 + retries)` cabe no tempo do gatilho (visibility timeout, timeout do endpoint)?

### API-07: Retry
- **Pergunta:** quantas tentativas, com qual backoff, e em quais erros?
- **Padrão sugerido:** 1 ou 2 retries com backoff exponencial, **só** em timeout, 5xx e 429. Nunca em 4xx de negócio.

### API-08: Rate limit / throttling
- **Pergunta:** existe limite por client-id/consumidor? A API retorna 429? Tem header `Retry-After`?
- **Por que importa:** para APIs críticas e muito usadas, o seu retry não pode virar carga extra.

### API-09: API degradada ou fora
- **Pergunta:** se a API estiver lenta ou fora, o que o fluxo faz? Desiste rápido e reprocessa depois (fila/DLQ)? Usa circuit breaker?
- **Padrão sugerido:** em fluxo assíncrono e de baixo volume, desistir rápido e deixar o reprocessamento para depois, sem insistir numa API crítica.

### API-10: Paralelismo
- **Pergunta:** as chamadas precisam ser paralelas?
- **Padrão sugerido:** **sequencial**. Paralelizar só com medição que justifique, com concorrência limitada (ex.: `Semaphore(3)`), e respeitando o API-08.

## Segurança e operação

### API-11: Autenticação
- **Pergunta:** como autentica (OAuth2 client credentials, mTLS, API key)? O token é cacheado e renovado? De onde vêm as credenciais (Secrets Manager, variáveis)?
- **Onde procurar:** clients existentes no projeto que chamam a mesma API ou o mesmo provedor de identidade.
- **Gate:** nenhuma credencial hardcoded.

### API-12: Dados sensíveis
- **Pergunta:** request ou response trafegam dados sensíveis (CPF/CNPJ, dados bancários)? O que **não** pode ir para o log?

### API-13: Observabilidade
- **Pergunta:** logar duração, status HTTP e correlation id de cada chamada? Propagar o correlation id para a API?

### API-14: Configuração externalizada
- **Pergunta:** URL base, timeouts, retries e tamanho de lote estão no `application.yml` por ambiente?

## Teste

### API-15: Mock
- **Pergunta:** como mockar a API localmente e no teste (WireMock, MockServer, mock do LocalStack)? O mock reproduz a **latência real** e os erros (timeout, 5xx, 429)?

### API-16: Cenários de aceite (TAAC)
- **Mínimo obrigatório:**
  - resposta de sucesso → mapeia e segue o fluxo;
  - registro não encontrado / resposta vazia → comportamento decidido no API-04;
  - timeout → retry conforme o API-07 e, esgotado, falha técnica;
  - 5xx → idem;
  - 429 → respeita o backoff / `Retry-After`;
  - 4xx de negócio → **não** faz retry.

---

## Template de resposta (vai na spec)

| ID | Status | Resposta | Fonte |
|---|---|---|---|
| API-01 | DESCOBERTO | ... | `gateway/openapi.yaml` |
| API-05 | PENDENTE | — | — |
| ... | | | |

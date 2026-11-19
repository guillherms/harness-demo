# BMAD, SDD, OpenSpec e o harness: resumo

## 1. BMAD + SDD
- Juntar os dois inteiros é cerimônia em dobro. A *story file* do BMAD já é, na prática, uma spec.
- O que aproveitar de cada um:
  - **BMAD-lite (antes):** só para demanda nova ou grande. O agente consulta a base de conhecimento (Obsidian/LeanIX, modelo de dados, mapa de repos), descobre onde mexer e gera as histórias.
  - **SDD-lite (durante):** uma spec curta por história, sem quebrar em tasks.
  - **Execução:** implementa → agente revisor → gates determinísticos (cobertura de 90%, TAAC).
- **Um artefato só:** a história recebe uma seção técnica e vira a spec.
- Quanto mais contexto o harness entrega, menor a spec precisa ser.

## 2. Panorama de frameworks
| Framework | Ideia | Para o meu contexto |
|---|---|---|
| Spec Kit (GitHub) | constitution → specify → clarify → plan → tasks → analyze → implement | Pesado; serve para greenfield/feature grande |
| OpenSpec | explore → propose → apply → archive, com specs vivas por delta | Mais próximo do "SDD lite"; bom para brownfield |
| GSD | Meta-prompting + context engineering, focado em Claude Code | Referência |
| Superpowers | Pacote de skills: do brainstorm ao TDD, funciona em vários agentes | Referência de skills bem feitas |
| Tessl | .spec.md ligados a testes | A ideia conversa com o TAAC |
| Kiro (AWS) | IDE própria com spec em 3 fases | Descartado (prende na ferramenta) |

## 3. Spec Kit × OpenSpec
| Spec Kit | OpenSpec |
|---|---|
| constitution | sem comando próprio (no meu caso: AGENTS.md) |
| clarify | explore |
| specify + plan + tasks | propose (proposal, specs delta, design, tasks) |
| analyze (antes de codar) | verify (depois de codar) |
| implement | apply |
| — | sync / archive → spec viva |

- Unidade de trabalho: o Spec Kit pensa **por feature**, o OpenSpec **por mudança**.
- A sacada do OpenSpec: `specs/` guarda a verdade atual, cada mudança descreve só o delta (ADDED/MODIFIED/REMOVED) e o archive incorpora esse delta à spec principal.

### Quando usar cada um
- **Spec Kit:** greenfield, feature grande, muita decisão de arquitetura, requisito ambíguo, necessidade de processo auditável.
- **OpenSpec:** brownfield, mudanças frequentes, quando a spec precisa servir de memória do sistema.
- **Nenhum:** demanda já definida e mudança que segue um padrão → AGENTS.md + skill + história bem escrita.

## 4. Meu SDD lite
| Etapa | Implementação |
|---|---|
| constitution | AGENTS.md de cada repo |
| clarify | Checklist de decisões + human-in-the-loop só para o que falta |
| specify + plan | Um artefato só (delta + seção técnica + fases, se precisar) |
| implement | Executa direto, sem quebrar em tasks |
| verify | Agente revisor + hooks (cobertura de 90%, TAAC) |
| archive | Consolida o delta na spec viva, que vira base de conhecimento |

O que veio de cada um: a disciplina de gates do Spec Kit e a spec viva do OpenSpec. Tasks e checklist de QA saem dos dois.

## 5. Caso real: listener SQS → S3 → parse → API → 3 tabelas
Tem decisão demais para ir só com a história, mas não justifica o Spec Kit completo.

**Decisões que a spec precisa fechar:**
1. Mensagem: o que vem no payload (chave do S3?) e qual message attribute do fanout do SNS faz a fila receber.
2. **Visibility timeout × tempo de processamento** (maior risco: a mensagem volta para a fila e é processada em paralelo).
3. **Idempotência** (o SQS reentrega): como detectar um arquivo já processado (chave + etag, constraint única).
4. **Falha parcial / retry / DLQ:** quantas tentativas, o que acontece com o que já foi gravado.
5. Erro de negócio (arquivo inválido → DLQ/erro) × erro técnico (API fora → volta para a fila).
6. Parse: layout e o que fazer com linha inválida (rejeitar o arquivo ou só a linha).
7. API: contrato, chamada por registro ou em lote, timeout e retry.
8. Tabelas: relacionamentos, chaves, ordem de inserção (FKs), transação ou lote.

**Fases (dentro da spec, não viram tasks):**
0. Listener: segue o padrão do kit.
1. S3 + parse.
2. API + mapeamento.
3. Persistência nas 3 tabelas + idempotência.

Cada fase passa pelo agente revisor antes da próxima.

**No harness:**
- Chamado de modelagem das 3 tabelas (skill do .ldm) sai **no dia 1**, porque tem prazo externo.
- O agente de infra local pede fila + bucket no LocalStack, mock da API e as tabelas no H2.
- A spec referencia o modelo de dados do harness em vez de redescrever as tabelas.
- TAAC: mensagem válida, arquivo inválido, API fora, mensagem duplicada, timeout.

## 6. Lição: "perguntar o que falta" não basta
O agente só detecta uma lacuna que ele **sabe que deveria existir**. No teste, o fluxo não perguntou sobre o visibility timeout nem sobre falha parcial. Um clarify genérico tem o mesmo problema.

**Solução: checklist de decisões por tipo de mudança**, separada das skills:

```
checklists/
  base.md            # vale para toda história; fallback
  listener-sqs.md
  endpoint.md
  integracao-s3.md
  nova-tabela.md
  regra-negocio.md
```

**Fluxo:**
1. Classificar a história (pode ter vários tipos).
2. Juntar a base com as checklists dos tipos.
3. Para cada item, **tentar descobrir no código/config primeiro** (application.yml, padrão dos outros listeners) e só pedir confirmação.
4. Perguntar só o que não conseguiu descobrir.
5. **Gate determinístico:** script/hook que bloqueia o implement se algum item estiver sem resposta.

**Checklist base:** onde a mudança mora (repo/camada/classe); qual comportamento atual muda e quais fluxos são impactados; critérios de aceite como exemplos (dado/quando/então); comportamento em erro; como testar localmente.

**Checklist de regra de negócio** (as respostas vêm da história ou do PO, o agente quase nunca descobre sozinho):
- Exemplos concretos com valores: um que passa, um que falha e um caso de borda.
- Limites: `>=` ou `>`, arredondamento, datas e fuso.
- Conflito com regras existentes (o agente busca no código e mostra).
- Vigência: só para registros novos ou também retroativa?
- **Gate: sem exemplos com valores, não implementa.** Os exemplos viram direto os cenários do TAAC.

**Evolução:**
- Toda lacuna revelada por code review ou incidente vira item da checklist do tipo (aprendizado a partir dos PRs).
- Um tipo de história que aparece pela 3ª vez vira skill própria.

## 7. Decisões técnicas do caso (timeout, API, paralelismo)
**Contexto:** cerca de 2 mensagens por dia, CNAB de até 1000 linhas, 5 a 10 requisições à API (em lote). A API é crítica e muito usada.

**Visibility timeout:**
- Fórmula: `requisições × latência p99 × (1 + retries) + overhead`.
- Regra: o resultado precisa ser **menor que metade do visibility timeout**.
- Com requisições sub-segundo e retries limitados, **30s é ok**. Se a latência for alta, subir para 2–3 min, o que não custa nada com 2 mensagens por dia.
- Pegar o p99 real com o time dono da API ou no APM antes de fechar.

**API crítica:**
- Timeout do client derivado do SLO (ex.: p99 × 2), nunca o padrão da biblioteca.
- 1 ou 2 retries com backoff, só em timeout, 5xx e 429. Nunca em 4xx de negócio.
- Respeitar rate limit e 429. Se a API estiver degradada, desistir rápido e deixar a mensagem voltar para a fila ou ir para a DLQ, sem somar carga.
- Como é só leitura, o retry é seguro do lado dela. A idempotência fica no insert.

**Paralelismo (Java 21):**
- Começar **sequencial**. Paralelizar só se a medição justificar.
- Se precisar: virtual threads (`newVirtualThreadPerTaskExecutor`) + `Semaphore` para limitar a concorrência (ex.: 3).
- Cuidados: pinning com `synchronized` no Java 21; `StructuredTaskScope` ainda é preview; não ligar `spring.threads.virtual.enabled` só por causa de uma história.

## 8. Rodada já feita sem checklist
- **Não jogar fora.** As lacunas são pontuais e o parse, o mapeamento e as entidades devem ser aproveitáveis.
- Rodar as checklists como **review** do código existente. Para cada item, responder se o código trata, não trata ou trata implicitamente.
- Decidir o que ficou em aberto e corrigir só o delta.
- Refazer só a camada de persistência, se a idempotência ou a transação exigirem mudança estrutural.
- O antes/depois serve de **case para a apresentação**.

## 9. Estrutura do harness: classificar, não quebrar
- A história **não é quebrada**. Ela continua com uma spec só e sem tasks. O que acontece é ela ser **classificada** em tipos de mudança.
- Cada tipo traz:
  - **Checklist** = o que decidir antes de codar
  - **Skill** = como fazer (só quando há procedimento repetitivo a automatizar)
- **AGENTS.md** = regras gerais do repo.

**Fluxo do `desenvolver-historia`:**
1. Busca a história via MCP.
2. Lê o **catálogo** e propõe os tipos, com justificativa.
3. **Dev confirma a classificação** (human-in-the-loop barato que evita a falha mais cara).
4. Carrega `base` + as checklists e skills dos tipos confirmados (progressive disclosure).
5. Descobre o que dá, pergunta o resto, e o gate confere se sobrou algo `PENDENTE`.
6. Spec única com fases → implementa → revisor + hooks → archive na spec viva.
7. Se nenhum tipo do catálogo cobrir a história, o agente avisa, e isso vira entrada para criar um tipo novo.

**Catálogo** (dentro da skill, não no AGENTS.md):

| Tipo | Sinais na história | Checklist | Skill |
|---|---|---|---|
| listener-sqs | fila, SQS, mensagem, listener, SNS | listener-sqs.md | — |
| integracao-api | consultar API, chamar serviço | integracao-api.md | — |
| integracao-s3 | bucket, S3, arquivo | integracao-s3.md | — |
| nova-tabela | tabela nova, coluna, modelo de dados | nova-tabela.md | alterar-ldm |
| endpoint | criar rota, novo endpoint, contrato | endpoint.md | criar-endpoint |
| regra-negocio | regra, cálculo, validação | regra-negocio.md | — |

**Estrutura de pastas:**
```
harness-kit/
  skills/
    desenvolver-historia/
      SKILL.md        ← passo 1 lê o catálogo
      catalogo.md
  checklists/
    base.md
    listener-sqs.md     (feito, 16 itens)
    integracao-api.md   (feito, 16 itens)
    integracao-s3.md
    nova-tabela.md
    regra-negocio.md
```

## 10. AGENTS.md como índice (ponteiros)
- O AGENTS.md é carregado em **toda** sessão, então tudo que fica nele gasta token sempre.
- Ele deve dizer **onde** está cada coisa e **quando** usar, sem guardar o conteúdo.
- O que entra no AGENTS.md do projeto:
  ```markdown
  ## Desenvolvimento de histórias
  Para "desenvolver história <id>", use a skill `desenvolver-historia`
  do harness-kit. Não implemente histórias sem ela.
  ```
- Teste: se uma seção só é útil em um tipo de tarefa, ela deveria virar ponteiro.
- Vira critério na skill que avalia AGENTS.md (nota 0–10): "conteúdo que deveria ser ponteiro".
- Pendente: testar se o Devin encontra a skill a partir do ponteiro.

## 11. Argumento para o time
- A ferramenta depende do tipo de demanda: não existe um SDD que sirva para tudo.
- Um framework de SDD só organiza etapas, enquanto o harness guarda o conhecimento de domínio do time e aprende com os reviews.
- Dá para chamar de "SDD lite" dentro do harness-kit, sem Spec Kit nem LangGraph.

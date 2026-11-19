# Checklist: listener SQS

> Aplica-se a histórias que consomem mensagens de uma fila SQS.
> Somar com: `base.md` + checklists das integrações do fluxo (ex.: `integracao-api.md`).

## Como usar
Para cada item:
1. **Descobrir primeiro:** procure nos lugares indicados em "Onde procurar".
2. Se encontrou → status `DESCOBERTO`, citando o arquivo/linha, e peça confirmação ao dev.
3. Se não encontrou → status `PENDENTE` e pergunte ao dev.
4. Resposta do dev → status `DECIDIDO`.

**Gate:** a spec só segue para implementação se nenhum item estiver `PENDENTE`.
Item que não se aplica → `N/A` com justificativa de uma linha.

Use o mesmo checklist como **review** de código existente: para cada item, responda se o código trata o ponto, não trata ou trata implicitamente (usou o padrão sem decidir).

---

## Mensagem

### SQS-01: Contrato da mensagem
- **Pergunta:** quais campos vêm no payload? Existe exemplo real? O que é obrigatório?
- **Onde procurar:** história, outros listeners do repo, DTOs de mensagem existentes.
- **Por que importa:** sem contrato, o agente inventa o DTO.

### SQS-02: Origem e filtro
- **Pergunta:** a mensagem vem de um tópico SNS (fanout)? Qual message attribute / filter policy faz esta fila receber a mensagem? A mensagem chega crua (raw delivery) ou embrulhada no envelope do SNS?
- **Onde procurar:** Terraform/IaC da fila e da subscription, outros listeners.
- **Por que importa:** o envelope do SNS muda o parse do payload. Um filtro errado faz a fila não receber nada.

### SQS-03: Mensagem inválida
- **Pergunta:** o que fazer com payload malformado ou com campo obrigatório faltando?
- **Padrão sugerido:** não reprocessar; logar e mandar para a DLQ/erro.

## Tempo e concorrência

### SQS-04: Tempo máximo de processamento × visibility timeout
- **Pergunta:** qual o pior caso de tempo (incluindo retries das integrações)? Qual o visibility timeout configurado?
- **Regra:** `tempo máximo com retries < visibility timeout / 2`.
- **Onde procurar:** `application.yml`, IaC da fila, SLO das APIs chamadas (ver `integracao-api.md`).
- **Por que importa:** se estourar, a mensagem volta para a fila e é processada **em paralelo** com a primeira execução.

### SQS-05: Volumetria
- **Pergunta:** quantas mensagens por dia/hora? Existe pico? Qual o tamanho do que cada mensagem dispara (ex.: arquivo com N linhas)?
- **Por que importa:** define timeout, concorrência do listener e se vale paralelizar.

### SQS-06: Concorrência do listener
- **Pergunta:** quantas mensagens o listener consome em paralelo (max concurrent / batch size)? Duas mensagens simultâneas podem conflitar (ex.: mesmo arquivo, mesmo cliente)?
- **Onde procurar:** configuração do listener (Spring Cloud AWS), outros listeners.

### SQS-07: Paralelismo interno
- **Pergunta:** o processamento de uma mensagem precisa paralelizar algo?
- **Padrão sugerido:** **não**. Comece sequencial e só paralelize com medição que justifique e com concorrência limitada.

## Confiabilidade

### SQS-08: Idempotência
- **Pergunta:** como detectar que esta mensagem/arquivo já foi processado? Qual a chave (ex.: id da mensagem de negócio, chave S3 + etag)?
- **Opções:** tabela de controle, constraint única, upsert.
- **Por que importa:** o SQS entrega **pelo menos uma vez**. Duplicata vai acontecer.
- **Gate:** item obrigatório; não aceita `N/A`.

### SQS-09: Erro de negócio × erro técnico
- **Pergunta:** quais erros são de negócio (reprocessar não resolve) e quais são técnicos (reprocessar pode resolver)?
- **Padrão sugerido:**
  - negócio (arquivo inválido, regra violada) → registrar o erro, confirmar a mensagem (ack) ou mandar direto para a DLQ;
  - técnico (timeout, 5xx, banco fora) → lançar exceção e deixar a mensagem voltar para a fila.

### SQS-10: Retry e DLQ
- **Pergunta:** qual o `maxReceiveCount`? Existe DLQ configurada? Quem monitora a DLQ e como reprocessar?
- **Onde procurar:** IaC da fila, redrive policy.

### SQS-11: Falha parcial
- **Pergunta:** se falhar no meio (ex.: lote 7 de 10), o que acontece com o que já foi gravado? O reprocessamento retoma ou refaz?
- **Opções:** transação única; commit por lote + idempotência por lote; tabela de status.
- **Por que importa:** é aqui que nascem dados duplicados ou pela metade.

### SQS-12: Modo de ack
- **Pergunta:** a mensagem é confirmada automaticamente ao fim do método ou manualmente? Uma exceção engolida (catch sem rethrow) confirma a mensagem sem processar?
- **Onde procurar:** configuração do listener, outros listeners.

## Operação

### SQS-13: Observabilidade
- **Pergunta:** quais logs mínimos (início, fim, id da mensagem, chave de negócio, duração)? Há correlation id vindo da mensagem? Alguma métrica/alarme?
- **Onde procurar:** padrão de log dos outros listeners.

### SQS-14: Configuração externalizada
- **Pergunta:** nome/URL da fila, timeouts e limites estão no `application.yml` por ambiente, e não hardcoded?

## Teste

### SQS-15: Teste local
- **Pergunta:** quais recursos são necessários no LocalStack (fila, DLQ, tópico, bucket)? Quais dependências precisam de mock?
- **Ação:** gerar a lista de requisitos e acionar a skill de infra LocalStack.

### SQS-16: Cenários de aceite (TAAC)
- **Mínimo obrigatório:**
  - mensagem válida → processa e grava;
  - mensagem inválida → erro/DLQ sem reprocessar;
  - **mensagem duplicada** → não duplica dados;
  - falha técnica de dependência → mensagem volta para a fila;
  - falha no meio do processamento → reprocessamento não duplica nem deixa dados pela metade.

---

## Template de resposta (vai na spec)

| ID | Status | Resposta | Fonte |
|---|---|---|---|
| SQS-01 | DESCOBERTO | ... | `src/.../MensagemDTO.java` |
| SQS-04 | PENDENTE | — | — |
| ... | | | |

# Squad agêntica: harness-kit ampliado

Resumo da conversa de 13/11/2026 (projeto "harness engineering").

## 1. Contexto

- A liderança pediu uma solução **reaproveitável pelo time**, chamada de "squad agêntica". A visão deles é pegar umas 10 histórias e deixar que agentes orquestrem o desenvolvimento delas de forma automática.
- O time gosta de SDD e de LangGraph. Eu não quero usar LangGraph e prefiro um **SDD lite**, porque discordo de algumas etapas (como quebrar em várias tasks) e tenho limite de tokens por mês.
- A ideia é seguir no **harness-kit**, mas ampliar para orquestrar **qualquer repo do time**, e não só o meu problema.
- O produto tem **N microserviços com desenhos diferentes**. Só o meu tem a codependência de 4 repos (app + gateway + BFF + gateway-bff). Na entrega atual existe também um **5º repo de listeners SQS**.

## 2. O que "squad agêntica" significa na prática

Agentes especializados em papéis (spec, dev, review, validação) coordenados por um orquestrador. O "squad" é a metáfora, e o que importa de verdade é o **harness** em volta deles:

- papéis e fronteiras (o que cada agente **não** faz);
- topologia (orquestrador com subagentes);
- handoff por arquivos (spec, relatório de review), e não por conversa;
- ferramentas e permissões por papel;
- gates de qualidade e critério de parada (com limite de iterações);
- pontos de human-in-the-loop;
- observabilidade.

Ressalva: só faz sentido separar em vários agentes quando há motivo real. Exemplos: o contexto não cabe numa sessão só, os papéis precisam de permissões diferentes, ou a revisão precisa ser independente.

## 3. Analogia da cozinha (modelo de brigada)

| Cozinha | Harness |
|---|---|
| Cozinha inteira | Produto (N microserviços) |
| Chef que recebe a comanda | Orquestrador: lê a história e identifica o microserviço |
| Praça (doce, salgado) | Microserviço |
| Ficha técnica do prato | Manifesto do microserviço |
| Funções da brigada (cortar, montar, conferir) | Papéis genéricos: api-owner, código, review |

**Uma brigada só, N fichas.** Nada de montar uma squad por microserviço.

## 4. Arquitetura do kit ampliado (3 camadas)

1. **Motor genérico (no kit):** o orquestrador tem fases que valem para qualquer história: entender → spec lite → implementar → sensores → review → entregar. Ele não sabe nada de stack.
2. **Ficha técnica por microserviço (em cada repo):** `AGENTS.md` e `.harness/project.yaml`, com stack, comandos de build e teste, regras de arquitetura e o que é proibido.
   - **Padrão:** 1 história = 1 repo, sem encadeamento.
   - **Exceção declarada:** uma seção opcional de encadeamento. Hoje só o meu microserviço usa (gateway → app → review → BFF).
3. **Receitas por tipo de história:** criar endpoint, editar endpoint, bugfix, novo listener, ajuste de tela etc. O orquestrador classifica a história e carrega só a receita certa (progressive disclosure). O fluxo atual dos 4 repos vira **uma receita**.

## 5. SDD lite

Etapas que ficam:

- **Specify:** transforma a `historia.md` numa spec curta.
- **Clarify:** o agente lista o que está ambíguo e pergunta só o que falta.

Etapas que saem:

- **Constitution:** o `AGENTS.md` já cumpre esse papel.
- **Plan:** vira uma seção de "arquivos afetados" dentro da própria spec.
- **Tasks e analyze:** ritual demais para o tamanho das histórias.

Ponto-chave: escrever os **critérios de aceite como cenários executáveis**. Exemplo: "attributes X + body Y → efeito Z". Esses cenários viram os testes, então a spec e o teste são a mesma coisa.

A spec aprovada por mim é o **checkpoint humano mais barato** de todo o fluxo.

## 6. Orquestração sem LangGraph

- Para **uma** história, a própria sessão do Claude Code ou do Devin é o orquestrador, usando skill + subagentes.
- Para **várias** histórias, um script Python fino resolve: pega a fila de histórias, cria um git worktree por história e roda cada uma em modo headless (`claude -p`). É um loop, não um grafo.

## 7. Como apresentar para a liderança (em degraus)

O gargalo em brownfield é a **revisão humana** e a qualidade do contexto, não a quantidade de agentes. Dez histórias em paralelo geram dez PRs para revisar e consomem a cota de tokens dez vezes mais rápido.

1. Uma história de ponta a ponta em qualquer repo.
2. Uma fila de histórias em sequência, com aprovação na spec.
3. Paralelo com worktrees, **só depois de medir** custo e taxa de aprovação nos degraus 1 e 2 (usando o sistema de medição do kit).

Sugestão de vitrine: a receita **"novo listener"**. A estrutura se repete e só a regra de negócio varia, então deve ter alta taxa de acerto e baixo custo de token.

## 8. Caso concreto: repo de listeners SQS

**Cenário:** um tópico SNS faz fanout para cerca de 5 filas SQS. Cada assinatura tem uma filter policy por message attribute. A aplicação tem um listener por fila, e cada um aplica uma regra diferente. A infra (filas, DLQ, assinaturas) fica num **repo de Terraform separado**.

**Amarração implícita:** são três peças que precisam bater:

1. quem publica define os attributes;
2. a filter policy da assinatura decide qual fila recebe;
3. o listener aplica a regra.

Se um attribute mudar, a mensagem **simplesmente não chega** na fila. Não aparece erro nenhum.

**Receita "novo listener":**

1. Infra (no repo de Terraform): fila, DLQ e assinatura com filter policy, seguindo o padrão das filas existentes.
2. Listener: esqueleto copiado do padrão + a regra de negócio da história.
3. Sensores determinísticos:
   - **Teste da filter policy:** confere se os attributes de exemplo casam com a fila certa e **não casam com as outras**. Pode ser Python puro, sem AWS.
   - **Teste do handler:** usa uma mensagem no formato real. É preciso checar se a assinatura usa raw message delivery, porque isso define se o listener recebe ou não o envelope do SNS.
   - **Teste integrado no LocalStack:** sobe tópico, fila e assinatura, publica os cenários da spec e confere o efeito.

**Atenção:** no LocalStack, a filter policy deve ser **lida do repo de Terraform** (pelo caminho local, como já é feito com o gateway), e não copiada para dentro da aplicação. Se for copiada, o teste local continua passando mesmo quando a policy real diverge.

## 9. Fluxo proposto

1. **Refino (SDD lite):** a `historia.md` vira a spec com cenários de mensagem. O agente faz o clarify e **eu aprovo a spec**.
2. **Desenvolvimento:** o agente implementa e fica em loop com os testes unitários e o script do LocalStack até tudo passar.
3. **Review:** o agente de review (só leitura) revisa junto comigo, no **human-in-the-loop**.
4. **Revalidação:** o script roda de novo depois dos ajustes, e aí sai o PR.

Decisões por trás dessa ordem:

- **A validação vem antes do review.** Assim ninguém gasta tempo revisando código que não funciona.
- **O validador é um script, não um agente.** É determinístico e custa zero token. O agente só entra para interpretar e corrigir uma falha.

## 10. Em aberto

- Quais tipos de história são mais comuns no time? A resposta define quais receitas fazer primeiro.
- O que cada listener produz no final: grava no DynamoDB, publica em outra fila, chama uma API? Isso define o que o script consegue conferir como "funcionou".
- A assinatura usa raw message delivery?
- Como o script do LocalStack lê a filter policy do repo de Terraform. Uma opção é usar o `workspace.yaml` com os caminhos locais.

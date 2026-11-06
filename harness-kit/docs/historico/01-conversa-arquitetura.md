# Histórico: como chegamos neste desenho

Resumo da conversa que partiu de `00-discussao-inicial.md` e chegou à
arquitetura atual. Serve para lembrar **por que** as coisas são como são.

## 1. Ponto de partida
O documento inicial propunha um Harness Core centralizado com Project Registry,
Execution Engine, Orchestrator, Context Manager, State Manager, Tool Registry,
LLM Gateway, Policy Engine e Observability, todo em código próprio.

**Virada:** já existem dois runtimes (Claude Code e Devin) que fazem tudo isso.
O harness para coding agents é a **camada de arquivos** que eles consomem.
→ decisão 001.

## 2. Ter ou não um harness central
Conclusão inicial: sim, como catálogo (não como runtime), começando pequeno; só
sobe para o central o que um segundo repo realmente precisar.

## 3. Correção do cenário: duas histórias, não quatro
Os quatro repos formam **dois pares** que andam juntos: aplicação + gateway
(história 1) e BFF + gateway BFF (história 2, ligada à 1). Mexer em rota na
aplicação implica mexer no contrato do gateway.

Ideia do usuário: a skill já sabe dessa relação e pergunta o caminho do gateway
na primeira vez, guardando fora do Git. Refinado para: relação commitada no
`project.yaml`, caminho num mapa por usuário. → decisão 006.

## 4. Subagents: api-owner, código, review
Workflow proposto: api-owner gera a spec → código implementa → loop de review →
com OK, segue para o BFF com as mesmas responsabilidades. Pontos acertados:
spec única, HITL antes de delegar, execução sequencial, briefing completo.
→ decisão 004.

## 5. Encadear a história do BFF
O fluxo é **fixo**: gateway → aplicação → review → OK → a skill pergunta o id da
história 2. O BFF não tem regra de negócio, só replica a interface. Solução:
handoff extraído do OpenAPI commitado. → decisão 005.

## 6. Branch `feature/<id>` a partir da develop
Pergunta: isso é hook? Resposta: **criar** a branch é passo da skill
(`preparar-branch`), **garantir** é hook. Quem cuida é o orquestrador, não o
agente de código. Preocupação do usuário: o agente alterar tudo e a branch nem
existir no commit → validar **antes de editar** com PreToolUse em Edit/Write
(escolha preferida do usuário). → decisão 007.

## 7. O que é o "orquestrador" e o que é o "kit"
Confusão resolvida:
- O orquestrador é o **agente principal da sessão** seguindo a skill. Não há
  outro programa.
- O harness fica **dentro da aplicação**. O kit não executa nada; é um repo
  Git com a cópia mestre, para não copiar e colar entre repos.
- O kit não é necessário para executar, nem para encadear os dois pares (tudo
  roda da sessão na aplicação).

O usuário inicialmente preferiu tudo dentro de um único projeto, mas decidiu
manter o kit **como documentação e lugar de entendimento** do que está sendo
construído, além de facilitar apresentar ao time. → decisão 002.

## 8. Evolução ponto a ponto (0.2.0 → 0.7.0)
Avaliação: o harness estava forte em **guiar** e fraco em **verificar**. Seis
pontos, um por vez:
1. **Sensores** (009): build, testes, ArchUnit com freeze, OpenAPI. Rodam quando
   o agente diz que terminou; compilar a cada edição seria lento no Maven.
2. **Permissões** (010): git de escrita negado para todos; o único caminho é o
   script, que valida a branch.
3. **Contrato entre agentes** (011): spec em JSON com schema; depois dela,
   ninguém relê a história.
4. **MCP local** (012): dúvida do usuário sobre publicar/rodar; resposta: stdio,
   o cliente inicia o processo. Criado como experimental, lógica também roda
   como script. O usuário pode remover se a medição não justificar.
5. **Medição** (013): log, resumo e comparação com a entrega real; evals em três
   cenários (sem harness, harness, harness + MCP).
6. **Aprendizado** (014): recorrência vira regra no lugar mais determinístico.

Em paralelo: o usuário quer transformar a solução num case de context
engineering, ligado ao The Context Course (Hugging Face).

## 9. Repo real já tem AGENTS.md e skills
A aplicação Java (ponto de partida) já tem um AGENTS.md e algumas skills feitos
por outra pessoa. Não dá para "desligar" um AGENTS.md: as ferramentas o
carregam sozinhas. Opções discutidas: contexto do harness em arquivo separado
com precedência; juntar ao AGENTS.md existente só localmente. Decisão adiada:
primeiro levar o kit e avaliar no ambiente real.

# Fundamentos

Os conceitos por trás do harness: engenharia de contexto, o papel do AGENTS.md
e das skills, e as razões de design do fluxo. Vieram da primeira versão
(`docs/historico/02-harness-agentes-v0.md`) e continuam valendo no kit.

## 1. Ponto de partida: feijão com arroz

Antes de squads agênticas, BMAD, SDD e afins, o objetivo aqui é dominar o
básico: escrever uma boa skill, usar bem o AGENTS.md e entender engenharia de
contexto.

Esses frameworks são camadas em cima disso. BMAD é um conjunto de prompts e
arquivos de contexto orquestrados; squad agêntica é subagente com contexto
isolado; SDD é persistir a spec fora da janela de contexto. Quem não entende o
básico usa o framework como caixa-preta e, quando dá errado, não sabe se o
problema é o contexto, a instrução ou a ferramenta.

Isso não torna os frameworks inúteis: eles empacotam padrões que funcionam.
A skill deste kit usa uma spec por história, que é a ideia central do SDD, mas
adotada por entender o porquê, não porque veio no pacote.

Para convencer o time, mostrar vale mais que argumentar: uma skill que pega a
história, pergunta só o que falta e entrega código no padrão com testes
passando. Se possível, medir algo (idas e voltas no PR, tempo de uma história
simples).

## 2. Engenharia de contexto

A janela de contexto é um recurso limitado. Quanto mais coisa irrelevante entra,
pior o agente fica. As técnicas costumam ser agrupadas em quatro:

| Técnica | Ideia | Onde aparece neste kit |
|---|---|---|
| **Select** | Escolher o que entra no contexto | Endpoints de referência em vez de varrer o projeto |
| **Write** | Persistir informação fora da janela | A spec da história salva em arquivo |
| **Compress** | Resumir | A história vira uma spec enxuta (`spec.json`); os subagents leem a spec, não o texto bruto |
| **Isolate** | Separar em subagentes | O `review` revisa com contexto limpo e devolve só os apontamentos |

**Progressive disclosure** é o princípio de carregar o contexto em camadas, só
quando necessário. Numa skill, são três níveis:

1. Nome + descrição: sempre no contexto (é o que faz a skill ser acionada).
2. SKILL.md: carregado quando a skill é acionada.
3. Arquivos de referência: lidos só quando aquele trecho é necessário.

O mesmo vale para o repositório: o AGENTS.md aponta para docs detalhados em vez
de colar o conteúdo.

## 3. AGENTS.md ou skill?

**Regra:** se vale para qualquer código do repo, vai no AGENTS.md. Se só faz
sentido dentro de um fluxo, vai na skill. O AGENTS.md guarda o
**conhecimento**; a skill guarda o **procedimento**.

Por que a arquitetura (clean arch, camadas, nomenclatura) vai no AGENTS.md e
não na skill:

1. **Vale para qualquer mudança.** Se estiver só na skill, o agente só conhece
   a arquitetura quando a skill é acionada. Num bugfix ou refactor sem skill,
   escreve fora do padrão. O AGENTS.md é carregado sempre; a skill, sob demanda.
2. **Uma fonte de verdade.** Com várias skills repetindo as regras, uma hora uma
   é atualizada e a outra não, e o agente recebe instruções contraditórias.
3. **Claude e Devin.** Os dois leem AGENTS.md. Arquitetura no repo garante o
   mesmo padrão nas duas ferramentas.
4. **Skill reutilizável.** O procedimento é igual em todo projeto; o que muda é
   a arquitetura de cada repo. Com a arquitetura no repo, a mesma skill serve
   para projetos diferentes.

Exceção: o que é específico do procedimento fica na skill (ex: "crie primeiro o
DTO, depois o use case, depois o controller").

## 4. AGENTS.md: teoria

### O que é
Arquivo markdown na raiz do repositório que o agente carrega automaticamente no
início de toda sessão. Um README escrito para o agente. É o padrão entre
ferramentas (Codex, Copilot, Cursor, Devin e outras leem nativamente).

### O modelo mental: ele custa caro
Está no contexto em **toda** tarefa. Cada linha compete pela atenção do agente o
tempo todo. O critério para algo entrar não é "é útil", é "vale para quase
qualquer tarefa e o agente erraria sem saber".

### O que entra
- **Comandos**: build, testes, lint. Sem eles o agente não verifica o próprio
  trabalho. Seção subestimada e das mais valiosas.
- **Mapa do projeto**: onde fica o quê. Evita exploração.
- **Arquitetura em alto nível**: camadas e direção das dependências.
- **Convenções não óbvias**: o que o agente não adivinharia olhando o código.
- **Armadilhas**: código legado, o que não usar como exemplo.
- **Ponteiros** para docs detalhados.

### O que não entra
- O que o modelo já sabe ("escreva código limpo", "siga SOLID", como funciona o
  Spring).
- O que o linter já garante. Se não há linter, configure um em vez de escrever
  um parágrafo.
- Procedimento de tarefa específica (isso é skill).
- Documentação longa (aponte, não cole).
- O que o código já mostra (versão do Java e dependências estão no build).

### Princípios
- **Específico vence genérico.** "Use clean arch" é fraco. "Controller não
  acessa repository; passa sempre por um use case em `application/`" é
  seguível e verificável.
- **Dê o porquê.** "Não use `legacy/` como exemplo, é anterior ao padrão atual"
  funciona melhor que só a proibição: o agente generaliza para casos não
  previstos.
- **Cresce por erro observado.** Não tente prever tudo no dia 1. Quando o agente
  errar a mesma coisa duas vezes, vira uma linha.
- **Trate como código.** Vai no PR, tem revisão e apodrece. Instrução
  desatualizada é pior que nenhuma: o agente segue com confiança.
- **Curto e imperativo.** Passou de ~150 linhas, algo deveria virar doc apontado
  ou skill.

### Anatomia (nesta ordem)
1. **Visão geral**: 2-3 linhas de orientação.
2. **Comandos**: build, testes, TAAC.
3. **Arquitetura**: regras verificáveis de como este repo aplica o padrão.
4. **Mapa do projeto**: pastas e o que vive nelas.
5. **Referências e legado**: endpoints de exemplo e o que evitar.
6. **Testes**: regras, com detalhe apontado para docs.

O template está em `templates/AGENTS.md`.

### Brownfield: o problema do legado
O agente aprende mais olhando código vizinho do que lendo instruções. Se ele
abrir um controller antigo para "ver como o projeto faz", copia o padrão errado.
Por isso o AGENTS.md precisa:
- dizer que o padrão é X e que existe código legado fora dele;
- listar **endpoints de referência** (vale mais que qualquer parágrafo);
- identificar o legado, se possível, como "não usar como referência";
- proibir refatorar legado sem pedido (essencial no fluxo de editar endpoint).

### Testes e TAAC
- Regra no AGENTS.md: "toda mudança tem teste unitário", "todo endpoint novo
  tem TAAC", framework, local, comando.
- Modelo detalhado do TAAC em `docs/patterns/testes.md`, apontado pelo AGENTS.md.
  O agente só precisa dele quando vai escrever um TAAC.

### Claude Code x Devin
Devin lê AGENTS.md nativamente. O Claude Code passou a ler AGENTS.md em 2026
(versão 2.1.277), mas só quando não existe CLAUDE.md; se os dois existirem, o
CLAUDE.md prevalece. Para funcionar igual para o time todo, independente de
versão: AGENTS.md é a fonte única e o `CLAUDE.md` tem uma linha só,
`@AGENTS.md`, que importa o conteúdo.

AGENTS.md em subpastas permite regras que só valem para aquela parte do código.

## 5. Razões de design do fluxo

Princípio geral: **conhecimento vai em skill, isolamento vai em subagent,
garantia vai em hook.**

### Da história à spec
- **A história é texto livre.** Ela só serve para montar a spec; dali em diante
  todos trabalham com a spec (decisão 011).
- **Classificar conferindo no código.** Procurar a rota (`listar_endpoints`) é o
  único dado objetivo para separar criar de alterar.
- **Confirmar antes de agir.** "Entendi como criação de `GET /x`. Sigo?" segura
  um erro de classificação antes de gastar tempo e contexto no fluxo errado.
- **✅ / 🟡 / ❌ em cada item** (`kit/contratos/checklist-endpoint.md`):
  ✅ exige citar o trecho da história (se não consegue citar, está inventando);
  🟡 inferido aparece para confirmação (chutar 201 para POST é ok, decidir em
  silêncio não); ❌ em item obrigatório bloqueia.
- **Perguntas em lote.** Tudo que falta é perguntado de uma vez.
- **Checklist com condicionais e inferíveis.** "Tem paginação?" é obrigatório;
  "tamanho da página" só se a resposta for sim. Defaults evitam perguntas inúteis.
- **Regra de negócio verificável.** "Validar o cliente" é vago e vira ❌: não dá
  para escrever teste. Isso liga o checklist aos testes.
- **Fluxo genérico em vez de "pare".** A skill nunca fica inútil, e serve de
  radar: muitas histórias iguais caindo no genérico pedem um fluxo próprio.

### Leitura limitada a referências
Em vez de varrer o projeto, o agente lê o endpoint de referência da variação
(simples, paginado, com integração) e os arquivos que vai alterar. Janela
menor, menos ruído do legado, resultados mais previsíveis. Cuidados: uma
referência por variação; limitar não é proibir; precisa de algo fora da lista,
diz o que e por quê; referência apodrece e precisa de dono.

### Review
- **Olhos de fora.** Quem implementou tende a concordar consigo mesmo. O
  revisor vê só diff, spec e AGENTS.md, num contexto isolado.
- **Read-only por ferramenta, não por instrução.** O `review` não tem Edit/Write.
- **Humano no loop fica no orquestrador.** Subagent não conversa com o usuário.
- **Critério objetivo.** APROVADO = zero BLOQUEANTES. Todo BLOQUEANTE ou
  IMPORTANTE cita a regra que o sustenta; sem regra, é SUGESTÃO (decisão 015).
- **Escopo = diff.** Num brownfield, um revisor solto aponta todo o legado.
- **Descartados não voltam.** O usuário descarta com motivo e a lista segue
  para as próximas rodadas.
- **Máximo de 3 rodadas.** Loop que não converge indica spec ambígua ou
  divergência que precisa de decisão humana.
- **Testes antes da revisão.** Revisão não se gasta com o que sensores já pegam.

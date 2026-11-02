# Harness de agentes

Kit para trabalhar com agentes de código (Claude Code e Devin IDE) num repositório
Java brownfield: um **AGENTS.md** com o conhecimento do repo, uma **skill**
`desenvolver-historia` com o procedimento para implementar histórias e um
**subagente** `code-reviewer` que revisa o resultado num loop com humano.

Este README documenta as decisões e o raciocínio por trás do kit, para servir
de referência de estudo e para levar ao time.

---

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
| **Compress** | Resumir | A história vira uma spec enxuta; as fases seguintes leem a spec, não o texto bruto |
| **Isolate** | Separar em subagentes | O `code-reviewer` revisa com contexto limpo e devolve só os apontamentos |

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

O template está em `AGENTS.md`.

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
- Modelo detalhado do TAAC em `docs/testes/taac.md`, apontado pelo AGENTS.md.
  O agente só precisa dele quando vai escrever um TAAC.

### Claude Code x Devin
Devin lê AGENTS.md nativamente. O Claude Code passou a ler AGENTS.md em 2026
(versão 2.1.277), mas só quando não existe CLAUDE.md; se os dois existirem, o
CLAUDE.md prevalece. Para funcionar igual para o time todo, independente de
versão: AGENTS.md é a fonte única e o `CLAUDE.md` tem uma linha só,
`@AGENTS.md`, que importa o conteúdo.

AGENTS.md em subpastas permite regras que só valem para aquela parte do código.

## 5. Compatibilidade Claude Code x Devin IDE

O objetivo é um único conjunto de arquivos, no nível do projeto, funcionando nas
duas ferramentas. O time usa o **Devin IDE** (Devin Desktop, antigo Windsurf) em
Windows.

| Peça | Claude Code | Devin IDE |
|---|---|---|
| `AGENTS.md` | via `CLAUDE.md` com `@AGENTS.md` | lê nativamente (raiz e subpastas) |
| `.agents/skills/` | **não lê** | lê |
| `.claude/skills/` | lê | **não lê** |
| `.claude/agents/` (subagente) | lê | não lê (tem subagentes, formato próprio) |

### Skills: fonte única + cópia gerada
Não existe um diretório de skills que os dois leiam. Por isso:

- **Fonte da verdade: `.agents/skills/`.** É o caminho do padrão aberto Agent
  Skills e o que o Devin lê.
- **`.claude/skills/` é uma cópia gerada** para o Claude Code. Não se edita
  direto (há um `.claude/LEIA-ME.md` avisando).
- **Sincronização por Gradle** (`gradle/sync-skills.gradle`), que funciona em
  qualquer SO e já faz parte do ferramental do time:
  - `gradlew syncSkills` copia `.agents/skills` para `.claude/skills`;
  - `gradlew checkSkills` falha se as duas divergirem. Coloque no pipeline.

Por que não link simbólico: seria o mais limpo (um arquivo só), mas no Git em
Windows exige modo desenvolvedor e `core.symlinks`. Quem clona sem isso recebe
um arquivo de texto no lugar da pasta, e a skill some sem erro aparente.

Se o projeto usar Maven, o equivalente do `syncSkills` é um
`maven-resources-plugin` com `copy-resources`.

### Regras para a skill ser portável
- Frontmatter só com campos do padrão (`name`, `description`). Campos
  específicos de uma ferramenta não existem na outra.
- Nada de depender de nome exato de ferramenta. O nome de uma tool de MCP muda
  entre as ferramentas; a skill referencia o **servidor** MCP.
- Recurso que só um lado tem vira **caminho alternativo**, não pré-requisito.
  O subagente de code review é o exemplo: no Claude Code a revisão roda no
  `code-reviewer`; no Devin, o próprio agente lê a skill `code-review` e revisa
  só com diff, spec e AGENTS.md.

### Invocação
Nas duas ferramentas: `/desenvolver-historia 1234`. Pedir em linguagem natural
também funciona pela `description`.

### Ainda a explorar no Devin IDE
- Subagentes próprios (aba Subagents em Customize): permitiria ter o revisor
  isolado também no Devin.
- MCP do projeto fica em `.devin/mcp_config.json`.
- Regras com escopo por arquivo em `.devin/rules/` (equivalente a AGENTS.md
  com `trigger: glob`).

## 6. A skill `desenvolver-historia`

### Ideia
No trabalho, toda história já traz os dados necessários (nome do endpoint,
regras, paginação, query params...). Em vez de um wizard que pergunta tudo, a
skill parte da história e **só pergunta o que falta**.

A ferramenta onde as histórias são escritas tem MCP. A entrada é
`desenvolver história <id>`: a skill busca a história pelo MCP e decide o
fluxo pelo conteúdo dela.

### Por que uma porta de entrada, e não uma skill por tipo
"Desenvolver história 1234" não diz se é criar ou editar endpoint; só lendo a
história se descobre. Por isso existe uma skill de entrada que classifica e
delega para um fluxo. Ela serve para qualquer tipo de história, não só
endpoints: novos tipos viram novos arquivos em `fluxos/`.

### Por que não encadear skills
Uma ideia inicial era ter uma skill de "validar contexto" rodando antes da de
criar endpoint. Encadear skills não é confiável: depende do agente acionar a
primeira e lembrar de acionar a segunda. A validação virou a primeira fase do
fluxo, dentro da mesma skill.

### Estrutura
```
.claude/agents/code-reviewer.md          subagente revisor (só Claude Code)
.agents/skills/code-review/SKILL.md      critérios e formato da revisão
.agents/skills/desenvolver-historia/
  SKILL.md                               obter, spec, classificar, confirmar, fechar
  fluxos/
    criar-endpoint.md                    validar, perguntar, referência, gerar, testes
    generico.md                          histórias sem fluxo próprio
  references/
    checklist-criar-endpoint.md          o que é obrigatório para criar endpoint
    paginacao.md                         lido só se a história tiver paginação
  templates/
    spec.md                              formato da spec da história
```

O SKILL.md tem o que é comum a toda história; cada fluxo tem só o que é
específico. Adicionar um tipo novo é escrever um arquivo e uma linha na
tabela de classificação.

### Fases
1. **Obter a história** pelo MCP (ou texto colado, como fallback).
2. **Montar a spec** a partir da história, sem inventar.
3. **Classificar** o tipo de trabalho.
4. **Confirmar** o entendimento em uma linha antes de agir.
5. **Executar o fluxo** escolhido.
6. **Testes**: unitários e TAAC passando.
7. **Code review**: loop com o subagente `code-reviewer` e o humano.
8. **Fechar**: atualizar a spec e resumir.

### Decisões de design e por quê

**MCP retorna texto livre.** A história é usada só para montar a spec; dali em
diante tudo trabalha com a spec. Sem campos estruturados, a classificação
depende da descrição, o que torna dois mecanismos essenciais:
- **Checar no código**: procurar a rota no repo é o único dado objetivo para
  separar criar de editar. É uma leitura pontual, não uma varredura.
- **Confirmar antes de agir**: "Entendi como criação de `GET /x`. Sigo?" segura
  um erro de classificação antes de gastar tempo e contexto no fluxo errado.

**Status ✅ / 🟡 / ❌ em cada campo.**
- ✅ encontrado exige **citar o trecho da história**. Se o agente não consegue
  citar, está inventando.
- 🟡 inferido tem que aparecer para confirmação. Chutar 201 para um POST é ok;
  decidir em silêncio não.
- ❌ faltando bloqueia a geração se o item for obrigatório.

**Perguntas em lote.** Tudo que falta é perguntado de uma vez, nunca pergunta
por pergunta.

**Checklist com campos condicionais e inferíveis.** "Tem paginação?" é
obrigatório; "tamanho da página" só se a resposta for sim. Itens com default
(status HTTP por método) evitam perguntas inúteis.

**Regra de negócio verificável.** "Validar o cliente" é vago e vira ❌: não dá
para escrever teste. Isso liga o checklist diretamente aos testes.

**Leitura limitada a referências.** Em vez de varrer o projeto, o agente lê o
endpoint de referência adequado à variação (simples, paginado, com integração)
e os arquivos que vai alterar. Ganhos: janela menor, menos ruído (não aprende
com o legado), resultados mais previsíveis entre devs. Cuidados:
- uma referência não cobre tudo, por isso há uma por variação;
- limitar não é proibir: o agente lê o que vai tocar;
- válvula de escape: precisa de algo fora da lista? diz o que e por quê antes;
- referência apodrece: precisa de dono ou check no PR.

**Spec como artefato.** A spec confirmada é a fonte de verdade das fases
seguintes e é salva em arquivo, virando documentação da história.

**Testes rodados, não só escritos.** A tarefa só está pronta com testes e TAAC
passando. Instrução de "escreva testes" sem verificação vira teste que nem
compila.

**Fluxo genérico em vez de "pare".** A skill nunca fica inútil. E serve de
radar: se muitas histórias caem no genérico com o mesmo padrão, aquele tipo
merece um fluxo próprio.

## 7. Subagente de code review

### Conceito: skill dentro de subagente
Um subagente é definido em `.claude/agents/<nome>.md`: frontmatter + um corpo
que vira o system prompt dele. O campo `skills:` pré-carrega o conteúdo completo
das skills listadas quando o subagente é iniciado. Regra prática:
**conhecimento vai em skill, isolamento vai em subagente, garantia vai em hook.**

Aqui:
- `.agents/skills/code-review/SKILL.md` diz **como** revisar (critérios,
  severidade, formato de saída).
- `.claude/agents/code-reviewer.md` diz **quem** revisa e com quais ferramentas.

### Por que um subagente
- **Olhos de fora.** O agente que implementou tem no contexto todo o raciocínio
  que o levou ao código, e tende a concordar consigo mesmo. O revisor vê só o
  diff, a spec e o AGENTS.md.
- **Contexto principal limpo.** A leitura da revisão acontece na janela do
  subagente; volta só a lista de apontamentos.

O subagente `.claude/agents/` é do Claude Code. No Devin, a revisão roda pela skill
`code-review` no próprio agente (ver "Compatibilidade"). Perde-se parte do
isolamento, por isso a skill instrui a julgar o código só pelo diff, spec e
AGENTS.md, como se fosse de outra pessoa.

### Decisões de design
**Read-only garantido por ferramenta, não por instrução.** O revisor só tem
`Read`, `Grep` e `Glob`. Sem `Edit`, `Write` ou `Bash`, ele não consegue "já
corrigir" nada nem rodar comandos. Por isso o diff é salvo em arquivo pelo
agente principal (`.review/rodada-<n>.patch`) e o revisor apenas lê. Adicione
`.review/` ao `.gitignore` do repo.

**Humano no loop fica no agente principal.** Subagente não conversa com o
usuário durante a execução: ele roda e devolve o resultado. Então quem mostra os
apontamentos, pergunta o que corrigir e corrige é o agente principal.

**Critério de "aceitável" objetivo.** APROVADO = zero bloqueantes. Todo
bloqueante ou importante precisa citar a regra que o sustenta (item da spec ou
linha do AGENTS.md); sem regra, é sugestão. Isso impede o loop de travar por
gosto pessoal do revisor.

**Escopo = diff.** Num brownfield, um revisor solto aponta todo o legado do
arquivo. A revisão se limita às linhas alteradas; o resto vira observação.

**Descartados não voltam.** O humano pode descartar apontamentos com motivo, e a
lista é passada para as rodadas seguintes. Sem isso, o revisor reabre o mesmo
item toda rodada.

**Limite de 3 rodadas.** Loop que não converge em 3 rodadas costuma indicar spec
ambígua ou uma divergência que precisa de decisão humana, não de mais uma volta.

**Testes antes da revisão.** Não se gasta revisão com o que o compilador e os
testes já apontam.

### O loop
```
implementa → testes passando → diff salvo → code-reviewer
     ↑                                            ↓
  corrige ← humano escolhe o que corrigir ← apontamentos
                     ↓
         APROVADO + ok do humano (ou rodada 3) → fecha
```

### Detalhes do Claude Code
- O `skills:` injeta a skill quando o subagente é **invocado** pelo agente
  principal. Por segurança, o corpo do subagente também manda ler o SKILL.md se
  ele não estiver no contexto.
- O subagente recebe só o próprio corpo como system prompt, não o prompt
  completo do agente principal. Por isso ele é instruído a ler o AGENTS.md
  explicitamente.
- Para garantir que um subagente específico rode, dá para mencioná-lo com
  `@agent-code-reviewer`.

### Uso
`/desenvolver-historia 1234`, no Claude Code e no Devin IDE.

A chamada explícita é determinística e não depende do agente casar a descrição
da skill com o pedido. Pedir em linguagem natural ("desenvolver história 1234")
também funciona pela `description` do frontmatter.

Observação: "hook" no Claude Code é outra coisa (comandos que rodam em eventos
da sessão). O que a skill faz é instruir o agente a chamar a ferramenta do MCP.

## 8. Como aplicar no repositório

1. Copie `AGENTS.md`, `CLAUDE.md`, `docs/`, `.agents/`, `.claude/` e
   `gradle/sync-skills.gradle` para o repo, e adicione `.review/` ao
   `.gitignore`.
2. Aplique o script no build (`apply from: 'gradle/sync-skills.gradle'`) e
   coloque `checkSkills` no pipeline.
3. Preencha os TODOs do `AGENTS.md`, começando por comandos e endpoints de
   referência.
4. Na skill, troque `<SERVIDOR_MCP>` (SKILL.md) pelo nome do servidor MCP de
   histórias.
5. Preencha `references/paginacao.md` e `docs/testes/taac.md`.
6. Teste primeiro com histórias escritas por você (que já seguem um padrão).
   Depois com histórias de outras pessoas: a diferença de resultado vira o
   argumento para padronizar a escrita.
7. A cada erro repetido do agente, uma linha nova no AGENTS.md ou no fluxo.

## 9. Pendências

- [ ] Nome do servidor MCP no SKILL.md (`<SERVIDOR_MCP>`)
- [ ] Preencher o AGENTS.md
- [ ] Padrão de paginação (`references/paginacao.md`)
- [ ] Modelo de TAAC (`docs/testes/taac.md`)
- [ ] Avaliar itens extras no checklist: autenticação/escopo, idempotência em
      POST, auditoria/log
- [ ] Fluxo `editar-endpoint` (hoje cai no genérico)
- [ ] Incorporar o checklist da skill/prompt de code review atual em
      `.agents/skills/code-review/SKILL.md`
- [ ] Validar no Devin IDE: skills aparecendo em Customize > Skills e acesso ao
      MCP de histórias
- [ ] Rodar `syncSkills`/`checkSkills` no build real (script não testado em
      Gradle ainda)
- [ ] Avaliar subagente de review nativo do Devin IDE
- [ ] **Débito:** padronizar a escrita de histórias do time (modelo leve com
      seções como Endpoint, Regras de negócio, Critérios de aceite). Com texto
      livre, a qualidade da extração depende de como a história é escrita.

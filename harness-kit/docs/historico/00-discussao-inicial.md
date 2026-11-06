# Discussão: Arquitetura de um Harness para múltiplos projetos

## 1. Objetivo

Construir um **Harness genérico e centralizado** para executar soluções
baseadas em agentes de IA, permitindo conectar diferentes projetos sem
duplicar infraestrutura ou acoplar o Harness a uma metodologia
específica.

A ideia é que o Harness forneça mecanismos de execução, coordenação,
contexto, estado, ferramentas, políticas e observabilidade. Cada projeto
continua responsável por suas particularidades técnicas e de negócio.

### Direção conceitual

> O Harness não deve determinar como o trabalho precisa ser feito. Deve
> fornecer os mecanismos para que diferentes soluções definam, executem
> e controlem como o trabalho será feito.

O Harness deve ser agnóstico a metodologias, frameworks de agentes e
domínios de negócio.

-   **Obsidian:** continua sendo uma ferramenta de interesse como
    possível fonte de conhecimento, mas não é uma dependência
    obrigatória.
-   **BMAD e SDD:** não fazem parte da direção desejada e não devem ser
    pressupostos na arquitetura.
-   **Agents, Skills e Hooks:** são componentes que podem ser utilizados
    pelos projetos, não o Harness inteiro.

------------------------------------------------------------------------

## 2. O que é Harness na prática?

Harness é a estrutura operacional que envolve, coordena e controla a
execução de agentes de IA.

Uma analogia útil: - Agents são os profissionais que executam
atividades. - Skills fornecem instruções e capacidades reutilizáveis. -
Hooks executam ações em determinados eventos. - O Harness é a estrutura
que organiza o trabalho: execução, coordenação, contexto, ferramentas,
permissões, estado e monitoramento.

### Conceitos relacionados

  -----------------------------------------------------------------------
  Conceito                            Responsabilidade
  ----------------------------------- -----------------------------------
  LLM                                 Modelo que gera respostas e realiza
                                      tarefas de raciocínio.

  Agent                               Executor com objetivo, instruções e
                                      ferramentas.

  Skill                               Instrução ou capacidade
                                      reutilizável para realizar uma
                                      atividade.

  Hook                                Ação automática disparada por um
                                      evento do ciclo de execução.

  Framework                           Biblioteca que facilita implementar
                                      agentes e workflows.

  Harness                             Estrutura operacional que controla
                                      e coordena a execução.
  -----------------------------------------------------------------------

Um framework como LangGraph pode implementar parte da orquestração, mas
não precisa representar o Harness inteiro.

------------------------------------------------------------------------

## 3. Centralizador ou Harness por projeto?

Foram consideradas duas abordagens.

### 3.1 Harness por projeto

Cada projeto possui sua própria infraestrutura de execução, seus Agents,
Skills, Hooks e Workflows.

**Vantagem:** simplicidade e autonomia inicial.

**Desvantagem:** duplicação de funcionalidades, manutenção distribuída e
dificuldade para compartilhar melhorias.

### 3.2 Harness centralizador

Um Harness central oferece infraestrutura compartilhada. Os projetos
conectam suas próprias configurações, Agents, Skills, Hooks, Workflows e
fontes de conhecimento.

**Vantagens:** - Reutilização de infraestrutura. - Padronização da
execução. - Observabilidade centralizada. - Possibilidade de gerenciar
vários projetos. - Evolução dos componentes compartilhados em um único
lugar.

### 3.3 Direção recomendada: arquitetura híbrida

Construir um **Harness Core centralizado**, mantendo os componentes e
regras particulares dentro de cada projeto.

  -----------------------------------------------------------------------
  Camada                              Estratégia
  ----------------------------------- -----------------------------------
  Execution Engine                    Compartilhado

  Orchestrator                        Compartilhado e extensível

  LLM Gateway                         Compartilhado

  Observability                       Compartilhada

  Context Manager                     Core compartilhado, fontes
                                      específicas por projeto

  Agents                              Compartilhados ou especializados
                                      por projeto

  Skills                              Compartilhadas quando aplicáveis

  Hooks                               Compartilhados ou específicos

  Workflows                           Compartilhados ou específicos

  Knowledge Base                      Específica por projeto, com
                                      possibilidade de fontes
                                      compartilhadas

  Policies                            Regras gerais no Core e regras
                                      específicas por projeto
  -----------------------------------------------------------------------

A recomendação é **projetar desde o início para suportar múltiplos
projetos, mas validar a arquitetura com um primeiro projeto antes de
construir uma plataforma genérica grande demais**.

------------------------------------------------------------------------

## 4. Harness Core em detalhe

O Harness Core é o núcleo responsável por executar e gerenciar soluções
conectadas à plataforma, sem conhecer as regras específicas de cada
projeto.

### 4.1 Project Registry

Responsável por descobrir, registrar e carregar projetos.

Atividades: - Descobrir projetos. - Carregar configurações. - Validar
configurações. - Resolver caminhos e dependências. - Criar contexto de
execução isolado por projeto.

Exemplo de configuração:

``` yaml
project:
  name: backend-python

knowledge:
  provider: obsidian
  path: ~/Documents/Obsidian/Backend

agents:
  path: ./agents

skills:
  path: ./skills

workflows:
  path: ./workflows

llm:
  provider: openai
  model: <configured-model>
```

O Registry prepara o ambiente; não executa os Agents.

### 4.2 Execution Engine

É o motor que efetivamente executa uma atividade ou Agent.

Responsabilidades: 1. Preparar a execução do Agent. 2. Carregar suas
instruções. 3. Disponibilizar ferramentas autorizadas. 4. Encaminhar a
solicitação ao LLM. 5. Processar o resultado. 6. Controlar tentativas e
erros. 7. Devolver um resultado padronizado.

O Execution Engine não deve decidir sozinho qual Agent executar em
seguida. Essa decisão pertence ao Orchestrator.

### 4.3 Orchestrator

Coordena o workflow e controla: - Ordem de execução. - Dependências
entre Agents. - Execução paralela, quando aplicável. - Condições de
decisão. - Reexecução de etapas. - Interrupção e retomada.

Exemplo:

``` text
Feature Analysis
    |
    v
Analyst
    |
    v
Architect
    |
    v
Story Creator
    |
    v
Reviewer
    |
    v
Final Output
```

Se o Reviewer encontrar inconsistências, o Orchestrator pode solicitar
nova execução do Story Creator.

A coordenação deve ficar no Harness, em vez de depender de Agents
coordenando uns aos outros livremente.

### 4.4 Context Manager

Monta o contexto relevante para cada execução.

Pode reunir: - Descrição da demanda. - Documentação do projeto. -
Arquitetura atual. - Padrões de desenvolvimento. - Decisões
anteriores. - Regras de negócio relacionadas. - Resultados de etapas
anteriores.

O Context Manager não precisa armazenar todo o conhecimento. Pode
consultar fontes externas, como Obsidian, arquivos Markdown, Git ou
bancos vetoriais.

Exemplo conceitual:

``` python
class ContextManager:

    def build_context(
        self,
        project,
        task,
        agent,
        previous_results=None
    ):
        knowledge = self.knowledge_provider.search(
            project=project,
            query=task
        )

        return ExecutionContext(
            project=project,
            task=task,
            agent=agent,
            knowledge=knowledge,
            previous_results=previous_results or {}
        )
```

Distinção: o Context Manager recupera, organiza e disponibiliza
informações. O Agent é quem as interpreta para realizar sua tarefa.

### 4.5 State Manager

Controla o estado de cada execução.

Exemplo:

``` yaml
execution_id: "123"
workflow: feature-analysis
status: running

steps:
  analyst: completed
  architect: completed
  story_creator: running
  reviewer: pending
```

Responsabilidades: - Retomar execuções. - Consultar resultados
anteriores. - Identificar etapas concluídas. - Controlar tentativas. -
Manter histórico de execução. - Evitar repetir etapas
desnecessariamente.

O estado do workflow deve ser diferenciado do histórico de conversas.

### 4.6 Tool Registry

Catálogo de ferramentas disponíveis para os Agents.

Exemplos:

  Tool              Responsabilidade
  ----------------- ------------------------------
  Obsidian Search   Pesquisar documentação
  File Reader       Ler arquivos
  File Writer       Criar documentos
  Git Diff          Consultar alterações
  Git History       Consultar histórico
  Jira Client       Consultar ou criar histórias
  Code Search       Pesquisar código

O Registry registra e disponibiliza ferramentas. O acesso deve respeitar
as permissões definidas pelo Policy Engine.

### 4.7 LLM Gateway

Abstrai os provedores de modelos de IA.

Exemplo conceitual:

``` python
response = llm_gateway.generate(
    provider="configured-provider",
    model="configured-model",
    messages=messages,
    temperature=0.2
)
```

Responsabilidades: - Integração com provedores. - Configuração de
modelos. - Retry e timeout. - Limites de tokens. - Contabilização de
consumo. - Tratamento de erros. - Fallback entre modelos, se
configurado.

Os Agents não precisam conhecer a implementação de cada provedor.

### 4.8 Policy Engine

Define o que pode ou não ser executado.

Exemplo:

  Operação                 Permissão
  ------------------------ -----------------
  Ler documentação         Permitida
  Criar arquivo Markdown   Permitida
  Alterar código-fonte     Exige aprovação

Também pode controlar: - Ferramentas permitidas por Agent. - Acesso a
diretórios. - Execução de comandos. - Limites de chamadas e tokens. -
Necessidade de aprovação humana.

### 4.9 Observability

Registra o comportamento do Harness.

Exemplo de dados:

``` text
Execution ID: 123
Project: backend-java
Workflow: feature-analysis

Agent: analyst
Duration: 12.4s
Tokens: 3200
Status: completed

Agent: architect
Duration: 18.2s
Tokens: 4100
Status: completed
```

Permite analisar: - Consumo de tokens por Agent. - Duração das etapas. -
Frequência de erros. - Número de tentativas. - Custo por workflow. -
Desempenho dos modelos.

Observability e Policy Engine acompanham a execução; não são atividades
executadas somente no final.

------------------------------------------------------------------------

## 5. Estrutura inicial de diretórios do Harness

Uma estrutura possível para o Core:

``` text
harness/
│
├── core/
│   ├── registry/
│   │   └── project_registry.py
│   │
│   ├── execution/
│   │   ├── engine.py
│   │   ├── orchestrator.py
│   │   └── execution_context.py
│   │
│   ├── context/
│   │   └── context_manager.py
│   │
│   ├── state/
│   │   └── state_manager.py
│   │
│   ├── tools/
│   │   └── tool_registry.py
│   │
│   ├── llm/
│   │   └── gateway.py
│   │
│   ├── policies/
│   │   └── policy_engine.py
│   │
│   └── observability/
│       └── logger.py
│
├── interfaces/
│   ├── agent.py
│   ├── tool.py
│   ├── knowledge_provider.py
│   ├── state_repository.py
│   └── llm_provider.py
│
├── adapters/
│   ├── llm/
│   ├── knowledge/
│   └── persistence/
│
├── shared/
│   ├── agents/
│   ├── skills/
│   ├── hooks/
│   └── tools/
│
├── projects/
│
└── cli.py
```

As interfaces definem contratos para que implementações diferentes
possam ser conectadas sem acoplar o Core a uma tecnologia específica.

Exemplo de contrato de Knowledge Provider:

``` python
from abc import ABC, abstractmethod

class KnowledgeProvider(ABC):

    @abstractmethod
    def search(self, query: str) -> list:
        pass

    @abstractmethod
    def read(self, document_id: str) -> str:
        pass
```

Implementações possíveis: - ObsidianKnowledgeProvider. -
LocalFilesystemProvider. - ConfluenceKnowledgeProvider. -
VectorDatabaseProvider.

O Core não precisa saber de onde veio a documentação.

------------------------------------------------------------------------

## 6. O que não deve pertencer ao Harness Core?

O Core deve fornecer mecanismos, não impor o conteúdo ou a metodologia
do trabalho.

  -----------------------------------------------------------------------
  Responsabilidade                    Local sugerido
  ----------------------------------- -----------------------------------
  Como escrever uma boa história      Skill

  Como realizar uma análise técnica   Skill e/ou Agent

  Como decompor uma demanda           Agent e Workflow

  Quais perguntas fazer ao usuário    Workflow e/ou Agent

  Como recuperar documentação         Core + Provider

  Como executar um Agent              Core

  Como controlar o workflow           Core

  Como registrar consumo              Core

  Como aplicar uma metodologia        Componentes do projeto, se desejado
  específica                          
  -----------------------------------------------------------------------

O Harness não precisa conhecer metodologias. Ele precisa saber executar
workflows compostos por componentes compatíveis.

------------------------------------------------------------------------

## 7. Problema real: quatro repositórios Git e histórias diferentes no Jira

O cenário concreto apresentado:

  -----------------------------------------------------------------------
  Projeto                 Tecnologia / tipo       Exemplo de história
  ----------------------- ----------------------- -----------------------
  1\. Aplicação Java      Java                    Adicionar rota GET
                                                  `/arquivos` na
                                                  aplicação Java

  2\. Aplicação Web BFF   Java                    Adicionar rota GET
                                                  `/arquivos` na
                                                  aplicação Java

  3\. Gateway BFF         Gateway                 Adicionar rota no
                                                  contrato do gateway
                                                  OpenAI

  4\. Gateway padrão      Gateway                 Adicionar rota no
                                                  contrato do gateway
                                                  OpenAI
  -----------------------------------------------------------------------

Cada repositório tem seu contexto técnico e histórias próprias no Jira.

O usuário já iniciou a implementação no projeto 2, criando: -
`AGENTS.md`. - Hooks. - Agents. - Skills.

A questão é como reaproveitar o que foi criado no projeto 2 na aplicação
Java (projeto 1) e nos demais repositórios.

### 7.1 AGENTS.md: específico por repositório

A recomendação é manter um `AGENTS.md` por repositório.

Exemplo:

``` text
repositories/
├── application-java/
│   └── AGENTS.md
│
├── web-bff-java/
│   └── AGENTS.md
│
├── gateway-bff/
│   └── AGENTS.md
│
└── gateway-standard/
    └── AGENTS.md
```

Não copiar simplesmente o `AGENTS.md` do Web BFF para a aplicação Java.

Mesmo utilizando Java e Spring, os projetos podem ter: - Estruturas de
pacotes diferentes. - Padrões arquiteturais diferentes. - Estratégias de
testes diferentes. - Regras de integração diferentes. - Comandos de
execução diferentes.

### 7.2 Agents: catálogo compartilhado

Criar Agents reutilizáveis, por exemplo:

``` text
shared/
└── agents/
    ├── analyst/
    │   └── agent.md
    ├── developer/
    │   └── agent.md
    ├── reviewer/
    │   └── agent.md
    └── tester/
        └── agent.md
```

Um Developer Agent pode atuar tanto na aplicação Java quanto no Web BFF,
desde que receba: - O `AGENTS.md` do repositório atual. - A história do
Jira. - As Skills relevantes. - As ferramentas permitidas para aquele
projeto.

Não é necessário criar Agents separados para cada projeto se a diferença
puder ser resolvida por contexto e capacidades.

Quando as responsabilidades forem realmente diferentes, Agents
especializados podem ser criados.

### 7.3 Skills: compartilhadas por capacidade

Organizar Skills por capacidade técnica, e não obrigatoriamente por
projeto.

Exemplo:

``` text
shared/
└── skills/
    ├── java/
    │   ├── spring-boot.md
    │   ├── rest-api.md
    │   └── testing.md
    │
    ├── api-design/
    │   ├── rest-conventions.md
    │   └── openapi-contract.md
    │
    ├── gateways/
    │   ├── route-configuration.md
    │   └── gateway-contracts.md
    │
    └── engineering/
        ├── code-review.md
        └── git-workflow.md
```

Aplicação possível:

  Projeto          Skills potenciais
  ---------------- -------------------------------
  Aplicação Java   Java, REST API, Testing
  Web BFF Java     Java, REST API, Testing
  Gateway BFF      API Design, Gateway Contracts
  Gateway padrão   API Design, Gateway Contracts

Uma Skill pode ser utilizada por vários Agents e projetos.

### 7.4 Hooks: compartilhados quando compatíveis

Hooks genéricos podem ser compartilhados, enquanto os comandos ou
configurações específicos ficam no projeto.

  Hook                       Estratégia
  -------------------------- --------------------------
  Before Agent               Global
  After Agent                Global
  Before Tool Execution      Global
  On Error                   Global
  Before Code Modification   Global
  After Code Modification    Global
  Test Execution             Configuração por projeto
  Lint                       Configuração por projeto

Exemplo: um hook `post_code_change` pode consultar a configuração do
projeto para descobrir se deve executar Maven, Gradle ou outra
ferramenta.

------------------------------------------------------------------------

## 8. Organização sugerida para o Harness e os projetos

``` text
harness/
│
├── core/
│   ├── orchestrator/
│   ├── execution/
│   ├── context/
│   ├── state/
│   ├── registry/
│   ├── policies/
│   └── observability/
│
├── shared/
│   ├── agents/
│   │   ├── analyst/
│   │   ├── developer/
│   │   ├── reviewer/
│   │   └── tester/
│   │
│   ├── skills/
│   │   ├── java/
│   │   ├── api-design/
│   │   ├── gateways/
│   │   └── engineering/
│   │
│   ├── hooks/
│   └── tools/
│
├── projects/
│   ├── application-java/
│   │   ├── project.yaml
│   │   └── workflows/
│   │
│   ├── web-bff-java/
│   │   ├── project.yaml
│   │   └── workflows/
│   │
│   ├── gateway-bff/
│   │   ├── project.yaml
│   │   └── workflows/
│   │
│   └── gateway-standard/
│       ├── project.yaml
│       └── workflows/
│
└── cli.py
```

Os repositórios Git continuam independentes. A estrutura acima
representa o catálogo e as configurações do Harness, não uma migração
dos códigos-fonte.

------------------------------------------------------------------------

## 9. Exemplo de execução integrada com Jira

Uma possível interface de CLI:

``` bash
harness jira execute PROJ-123
```

Fluxo esperado:

1.  Consultar a história no Jira.
2.  Identificar o projeto relacionado à história.
3.  Localizar o repositório Git.
4.  Carregar o `AGENTS.md` correspondente.
5.  Recuperar as Skills aplicáveis.
6.  Selecionar os Agents necessários.
7.  Executar o workflow.
8.  Registrar resultados e alterações.

O Jira fornece a demanda que inicia o trabalho; o Harness coordena a
execução.

A integração com Jira pode ser implementada posteriormente, sem ser uma
dependência do Core inicial.

------------------------------------------------------------------------

## 10. Histórias que envolvem múltiplos projetos

Uma funcionalidade pode exigir alterações nos quatro repositórios.

Nesse caso, pode existir um workflow de coordenação entre projetos:

``` text
Jira Epic
   |
   v
Cross-Project Orchestrator
   |
   +---- Application Java
   |
   +---- Web BFF Java
   |
   +---- Gateway BFF
   |
   +---- Gateway Standard
   |
   v
Integration Review
```

Cada projeto mantém sua execução independente, com contexto e estado
próprios.

Ao final, uma etapa de revisão integrada pode verificar a consistência
entre as implementações, por exemplo, se o contrato do gateway está
compatível com a aplicação.

------------------------------------------------------------------------

## 11. Princípios arquiteturais consolidados

1.  **Core agnóstico:** não conhece metodologias, frameworks de agentes
    ou domínios de negócio.
2.  **Agents reutilizáveis:** podem ser compartilhados quando suas
    responsabilidades forem equivalentes.
3.  **Skills por capacidade:** organizar conhecimentos reutilizáveis por
    competência técnica ou funcional.
4.  **Hooks configuráveis:** compartilhar a lógica genérica e
    parametrizar o comportamento por projeto.
5.  **Contexto isolado:** cada execução recebe o contexto do repositório
    e da demanda correspondentes.
6.  **Projetos independentes:** cada repositório mantém suas regras,
    configurações e documentação.
7.  **Workflows configuráveis:** cada projeto define a sequência de
    atividades necessária.
8.  **Integrações desacopladas:** Jira, Obsidian, Git e provedores de
    LLM entram por interfaces/adapters.
9.  **Extensibilidade:** novos projetos e componentes devem ser
    conectados sem modificar o Core.
10. **Estado e observabilidade:** execuções precisam ser rastreáveis e,
    quando possível, retomáveis.

### Divisão de responsabilidades

-   **Core:** sabe executar.
-   **Shared:** contém capacidades e componentes reutilizáveis.
-   **Project:** conhece as particularidades do repositório.
-   **Workflow:** define quais atividades precisam acontecer e em qual
    sequência.
-   **Jira:** fornece a demanda que inicia o trabalho.
-   **Knowledge Provider:** disponibiliza conhecimento de fontes
    configuradas.

------------------------------------------------------------------------

## 12. Próximos passos recomendados

Evitar começar implementando dezenas de Agents ou todos os módulos do
Core de uma vez.

Ordem sugerida:

1.  Revisar o que já existe no projeto 2.
2.  Identificar quais Agents, Skills e Hooks são realmente genéricos.
3.  Extrair os componentes reutilizáveis para `shared`.
4.  Manter um `AGENTS.md` específico para cada repositório.
5.  Criar o cadastro dos quatro projetos no Harness.
6.  Implementar o fluxo vertical mínimo: Project Registry, Orchestrator,
    Execution Engine, Context Manager e LLM Gateway.
7.  Executar um Agent em um projeto e validar o ciclo completo.
8.  Introduzir State Manager, Policies e Observability.
9.  Implementar integração com Jira.
10. Evoluir para workflows que coordenem alterações em múltiplos
    projetos.

**Recomendação final:** transformar o que já foi construído no Web BFF
em um primeiro projeto conectado ao Harness, extraindo apenas o que for
comprovadamente reutilizável. Assim, o trabalho existente é aproveitado
e a arquitetura evolui com validação prática.

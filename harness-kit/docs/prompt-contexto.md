# Prompt para retomar o contexto

Cole o bloco abaixo no Claude Code ou no Devin, com o `harness-kit` aberto ou
acessível. Ajuste o "Objetivo desta sessão" no final.

---

```text
Você vai me ajudar a evoluir e aplicar um harness de agentes de código.
Todo o desenho já foi discutido e está documentado neste repo (harness-kit).

Antes de responder, leia nesta ordem:
1. README.md
2. docs/arquitetura.md
3. docs/decisoes/ (todos)
4. docs/historico/01-conversa-arquitetura.md
5. docs/proximos-passos.md
Leia os arquivos de kit/ e templates/ só quando a tarefa precisar.

Contexto:
- Sou desenvolvedor e uso Claude Code e Devin Desktop no Windows. Tudo precisa
  funcionar nas duas ferramentas, no nível do projeto.
- Prefiro exemplos em Python. Respostas diretas e concisas, sem enrolação, e
  feedback honesto quando algo no desenho estiver errado.
- Cenário: dois pares de repos que andam juntos numa história:
  aplicação Java + gateway (contrato OpenAPI) e BFF + gateway BFF.
  A história do BFF é diferente, mas ligada à da aplicação.
- Fluxo fixo: api-owner gera a spec e altera o gateway → agente de código
  implementa → loop de review → aprovação → commit → handoff → história do BFF.
- Branch: feature/<id da história>, criada a partir da develop.
- O repo Java é brownfield: clean architecture, com endpoints legados fora do
  padrão; o time usa testes unitários e TAAC (test as code).
- As histórias vêm de uma ferramenta com MCP; a entrada do fluxo é
  "desenvolver história <id>".

Decisões que NÃO quero rediscutir sem um motivo forte:
- O harness é camada de arquivos, não um runtime próprio.
- O orquestrador é o agente principal seguindo a skill desenvolver-historia.
- Subagents não executam git; branch e commit são do orquestrador.
- O handoff é extraído do OpenAPI commitado.
- O harness-kit é a fonte e a documentação; ele não executa nada.
- Guias antes, sensores depois: o que máquina consegue checar, máquina checa.
- A spec.json é a fonte da verdade depois de aprovada.
- O MCP é experimental: fica ou sai conforme as evals.

Objetivo desta sessão:
<ex.: validar os itens de Windows/Devin de docs/proximos-passos.md>
<ex.: adaptar templates e AGENTS.md para o repo real em C:/dev/...>
<ex.: rodar a fase 1 numa história pequena e ajustar o que quebrar>

Antes de alterar qualquer arquivo, me diga o que pretende mudar e por quê.
```

# Próximos passos

## Validar no ambiente de trabalho (Windows)
Roteiro passo a passo em `docs/testes.md` (nível 2 cobre os itens abaixo no sandbox).
- [ ] O `command` dos hooks funciona com `python` ou precisa de `py`?
- [ ] `$CLAUDE_PROJECT_DIR` expande no shell que o Claude Code usa?
- [x] O git hook (`pre-commit` em sh chamando Python) roda pelo Git for Windows?
      Coberto por `tests/test_branch.py` (Git 2.34, Python 3.12).
- [ ] O Claude Code edita o gateway estando fora da pasta da sessão? Se não,
      adicionar o caminho em `additionalDirectories` no `.claude/settings.local.json`.

## Sensores (0.2.0)
- [ ] `mvn -q verify` roda na máquina do trabalho? Quanto tempo leva? Se for
      lento demais, trocar por `mvn -q test` ou rodar só o módulo alterado.
- [ ] O pom já tem ArchUnit? Se não, adicionar com a versão aprovada no time e
      copiar `templates/archunit/ArquiteturaTest.java`, ajustando os pacotes.
- [ ] Primeira execução do ArchUnit gera o `archunit_store`: commitar.
- [ ] `pip install openapi-spec-validator` é liberado no ambiente? Preencher o
      caminho do contrato no `.harness/sensores.json` do gateway.
- [ ] Hooks Stop/SubagentStop funcionam no Windows (mesmos cuidados de `python`).

## Permissões (0.3.0)
- [ ] Conferir na doc do Claude Code a sintaxe de caminhos das regras `Read(...)`
      (`**/`, `~/`) na versão instalada; testar pedindo ao agente para ler um `.env`.
- [ ] Testar que `git commit` direto é negado e que o script de commit funciona.
- [ ] Se o repo já tiver `.claude/settings.json`, juntar à mão `permissions` e `hooks`.
- [ ] Falta algo sensível específico do time (ex.: arquivos de config com segredo)?
      Adicionar ao `deny`.

## Contrato entre agentes (0.4.0)
- [ ] `pip install jsonschema` (ou `openapi-spec-validator`, que já inclui).
- [ ] Rodar o validador com uma spec escrita à mão de uma história antiga.
- [ ] Ajustar o schema se o time usar algo que ele não cobre (headers,
      paginação, versionamento de path).

## MCP (0.5.0, experimental)
- [ ] `pip install mcp pyyaml` é liberado? Se não, usar `endpoints.py` como script.
- [ ] Rodar `python .claude/mcp/endpoints.py listar` no repo real e conferir a
      tabela: algum endpoint ficou com path `?` ou faltando?
- [ ] Ajustar `marcador_padrao` em `.harness/mcp.json` para o pacote que
      identifica o padrão atual no repo.
- [ ] Na primeira sessão, aprovar o servidor `harness` se o Claude pedir.
- [ ] Devin: onde fica a config de MCP? Apontar para o mesmo `harness_mcp.py`.

## Medição (0.6.0)
- [ ] Rodar uma execução e conferir se `relatorio.py` soma tokens. Se vier zero,
      abrir o transcript (caminho no log) e ajustar a leitura de `usage`.
- [ ] Conferir se os tokens dos subagents entram na soma.
- [ ] Escolher as 3 a 5 histórias de eval e preencher `evals/historias.md`.
- [ ] Rodar os cenários A, B e C da primeira história (`docs/evals.md`).

## Aprendizado (0.7.0)
- [ ] Conferir se o review está usando o formato `- [categoria] ...`.
- [ ] Depois de 3 ou 4 histórias, rodar `aprendizado.py analisar` e aplicar a
      primeira regra. Registrar no case.

## Incorporado da v0 (0.8.0)
- [ ] Incorporar o checklist de code review atual do time em
      `kit/skills/code-review/SKILL.md` (`<regras de code review do time>`).
- [ ] Avaliar itens extras em `kit/contratos/checklist-endpoint.md`:
      autenticação/escopo, idempotência em POST, auditoria/log.
- [ ] Testar o fluxo genérico (`fluxo-generico.md`) com uma história sem endpoint.
- [ ] Conferir se o api-owner marca 🟡/❌ em `pendencias` com os prefixos
      `inferido:` e `faltando:`.
- [ ] **Débito:** padronizar a escrita de histórias do time (modelo leve com
      Endpoint, Regras de negócio, Critérios de aceite). Com texto livre, a
      qualidade da spec depende de como a história é escrita.
- [ ] Testar com histórias de outras pessoas, não só as suas: a diferença de
      resultado vira argumento para padronizar.

## Devin Desktop
- [ ] Confirmar que o Devin lê `.agents/skills` (Customize > Skills) e acessa o
      MCP de histórias. Regras/workflows em outro lugar? Ajustar `DESTINOS_*` no `sync.py`.
- [ ] MCP do projeto no Devin fica em `.devin/mcp_config.json`?
- [ ] Regras com escopo por arquivo em `.devin/rules/` (equivalente a AGENTS.md por pasta).
- [ ] Ele lê AGENTS.md?
- [ ] Tem subagents (aba Subagents em Customize)? Se não, as fases rodam em
      sequência num agente só e o review segue a skill `code-review` direto.
- [ ] Tem permissões configuráveis por projeto? Replicar o `deny` do kit.
- [ ] Tem hooks? Se não, a verificação de branch fica na skill e no git hook, e
      os sensores viram um passo explícito da skill antes do review.

## Preencher
- [ ] `AGENTS.md` da aplicação e dos gateways (placeholders).
- [ ] `docs/patterns/endpoint.md`, `paginacao.md` e `testes.md` na aplicação
      (criados pelo sync a partir de `templates/docs/`): clean arch, endpoints
      de referência, padrão de paginação, modelo de TAAC.
- [ ] Regras de code review do time em `kit/skills/code-review/SKILL.md`.
- [ ] Nome do MCP da ferramenta de histórias em `fase-aplicacao.md` e `fase-bff.md`
      (referencie o servidor, não o nome da ferramenta: muda entre Claude e Devin).
- [ ] `templates/project-*.yaml` com os nomes reais dos repos.

## Atenção: a aplicação já tem AGENTS.md e skills de outra pessoa
- [ ] Antes do sync, comparar os nomes das skills/agentes existentes em
      `.claude/` com os do kit: o sync **apaga e recria** pastas com o mesmo
      nome. Em caso de conflito, renomear as do kit.
- [ ] O sync não sobrescreve o AGENTS.md nem o settings.json existentes:
      decidir como juntar o conteúdo do harness ao AGENTS.md atual.
- [ ] Ler o AGENTS.md atual com calma: dois contextos conflitantes atrapalham
      o agente.

## Ordem sugerida
1. Clonar este repo no computador do trabalho.
   Ligar só as peças básicas primeiro (fluxo, branch, permissões); depois
   sensores, spec, medição e aprendizado, nessa ordem.
2. Validar os itens de Windows e Devin acima.
3. Rodar o sync na aplicação e no gateway; preencher os AGENTS.md.
4. Rodar uma história **real e pequena** só da fase 1.
5. Anotar o que quebrou; cada ajuste diz se é do kit ou do repo.
6. Só então ligar a fase 2 (BFF).

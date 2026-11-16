# Como testar o harness

O kit tem duas partes, e cada uma se testa de um jeito:

| Parte | O que é | Como testa |
|---|---|---|
| Scripts | hooks, sensores, validador da spec, preparar-branch, pre-commit, medição, aprendizado, MCP, sync | `pytest`, automático, em segundos |
| Agentes | skill orquestradora, subagents, perguntas, review | rodando no Claude Code, num **sandbox** com repos falsos |

Vá na ordem: cada nível só faz sentido se o anterior passou. Se algo falhar
num nível alto, desça um nível para isolar a causa.

---

## Nível 0 — Pré-requisitos (uma vez)

```bash
cd harness-kit
pip install -r requirements-dev.txt
```

`openapi-spec-validator` e `mcp` são opcionais. Sem o `mcp`, o servidor MCP
não sobe (o resto funciona; veja o nível 2).

Para o sandbox: `git`, `java` e `javac` no PATH (não precisa de Maven).

## Nível 1 — Testes automáticos dos scripts

```bash
cd harness-kit
pytest -q
```

**Espere:** tudo verde. Os testes usam um HOME temporário e repos git
temporários (com remote local), então não tocam no seu `~/.harness` nem em
repo nenhum.

| Arquivo | Garante que |
|---|---|
| `test_validar_spec.py` | spec errada é barrada (schema, path params, body em GET, duplicado); `--pronta` exige zero pendências; como hook, só age em `~/.harness/runs/*/spec.json` |
| `test_branch.py` | hook de branch bloqueia edição fora de `feature/<id>`; `preparar_branch` cria/retoma branch, não mexe em nada se um repo estiver sujo, commita só onde mudou; o git hook pre-commit bloqueia commit fora da branch |
| `test_sensores.py` | sensor só roda quando arquivo alterado casa com `quando`; falha devolve exit 2 com o log; na 4ª falha libera e manda escalar |
| `test_medicao_aprendizado.py` | log por execução, relatório, agrupamento de apontamentos por categoria e linha de corte do `aplicar` |
| `test_endpoints.py` | o MCP acha as rotas, separa padrão × legado e compara com o contrato |
| `test_sync.py` | cada perfil instala o que deve; rodar de novo não sobrescreve o que é do repo |

**Mudou um script do kit? Rode `pytest` de novo antes de sincronizar.**

## Nível 2 — Peças isoladas no Claude Code (sandbox)

### Criar o sandbox

```bash
cd harness-kit
python tests/sandbox/criar_sandbox.py --destino C:/dev/harness-sandbox
```

Ele cria:
- `aplicacao-java/`: Java puro (sem Spring/Maven) com clean arch, 2 endpoints de
  referência e 1 legado. O build + testes é `python .harness/compilar.py`.
- `gateway-padrao/`: contrato `openapi.yaml`.
- `remotes/`: remotes bare locais (o `preparar-branch` faz `fetch`/`pull`).
- `historias/`: textos de história para colar.
- `~/.harness/workspace.yaml` apontando para os dois repos (só se ainda não existir;
  senão ele imprime o que você deve conferir).
- `aplicacao-java/.claude/settings.local.json` com `additionalDirectories` para o
  gateway (o Claude Code só edita fora da pasta da sessão com isso).

Para recomeçar do zero: feche o Claude Code e rode com `--limpar`.

### Checagens (sessão aberta em `aplicacao-java/`)

Abra `claude` dentro de `C:/dev/harness-sandbox/aplicacao-java`. Para cada
item: o que fazer → o que esperar → se falhar.

1. **Instruções carregadas.** Pergunte "quais são as regras de arquitetura
   deste repo?" → responde com as regras do `AGENTS.md` (controller → use case,
   `*Response`…). Se não: confira o `CLAUDE.md` com `@AGENTS.md`.

2. **Skills e agentes visíveis.** Digite `/` → aparecem `desenvolver-historia`,
   `preparar-branch` e `code-review`. Rode `/agents` → aparecem `api-owner`,
   `codigo` e `review`.

3. **Hooks registrados.** Rode `/hooks` → PreToolUse, PostToolUse, Stop,
   SubagentStop e UserPromptSubmit apontando para `python "$CLAUDE_PROJECT_DIR/..."`.
   Se algum hook der erro de "comando não encontrado": troque `python` por `py`
   no `kit/settings.json` (item de Windows do `proximos-passos.md`).

4. **MCP.** Rode `/mcp` → servidor `harness` conectado (aprove se pedir).
   Peça "liste os endpoints com listar_endpoints" → 3 rotas, `/clientes` como
   `legado`. Se o servidor falhar: `pip install mcp pyyaml`; enquanto isso, o
   mesmo resultado sai de `python .claude/mcp/endpoints.py listar`.

5. **Permissões.** Peça "faça git commit de tudo" → negado. Peça "leia o
   arquivo .env" (crie um antes) → negado. Peça `git status` → roda sem perguntar.

6. **Hook de branch.** Sem execução ativa, peça uma edição qualquer → permitido
   (o harness não atrapalha trabalho manual). Depois, num terminal:
   ```bash
   python .claude/skills/preparar-branch/scripts/preparar_branch.py preparar --historia SBX-0 --repos C:/dev/harness-sandbox/aplicacao-java C:/dev/harness-sandbox/gateway-padrao
   git -C C:/dev/harness-sandbox/gateway-padrao switch develop
   ```
   e peça para editar o `openapi.yaml` → **bloqueado** com a mensagem
   "está na branch 'develop'". Isso também prova que `$CLAUDE_PROJECT_DIR`
   expande no seu shell. Desfaça com `git switch feature/SBX-0` no gateway.

7. **Sensor.** Com a execução SBX-0 ativa, peça "crie um arquivo Java com erro
   de sintaxe em src/main/java/sandbox/Teste.java e encerre" → ao terminar, o
   hook Stop devolve o erro do `javac` e o agente continua corrigindo.
   `~/.harness/runs/SBX-0/sensores.json` mostra o resultado.

8. **Pre-commit.** Num terminal, com SBX-0 ativa e o gateway na develop, tente
   `git commit` → "Commit bloqueado".

Ao final: `python .claude/skills/preparar-branch/scripts/preparar_branch.py encerrar`
e descarte as alterações (`git switch develop` e `git branch -D feature/SBX-0`
nos dois repos, ou `--limpar` e crie o sandbox de novo).

## Nível 3 — Fluxo completo com histórias do sandbox

Use as histórias de `C:/dev/harness-sandbox/historias/`. Em cada uma, cole:

```
/desenvolver-historia SBX-1
<texto da história>
```

### SBX-1: caminho feliz (criar endpoint)
Marque o que aconteceu:

- [ ] Classificou como **criação** de `GET /contratos/{id}/parcelas` e pediu OK em uma linha.
- [ ] Rodou `preparar-branch` e os dois repos foram para `feature/SBX-1`.
- [ ] `api-owner` gerou `~/.harness/runs/SBX-1/spec.json`; o gate `--pronta` passou.
      Pendências esperadas: só itens 🟡 (ex.: `inferido: status = 200`), perguntadas de uma vez.
- [ ] Mostrou a spec resumida e esperou o OK.
- [ ] `api-owner` alterou o `openapi.yaml` (path, schema `Parcela`, 404).
- [ ] `codigo` criou use case + método no controller + `ParcelaResponse` + teste,
      seguindo `ContratoController` (e não o legado). Build passou.
- [ ] `review` respondeu no formato da skill (`VEREDITO`, seções por severidade,
      linhas `- [categoria] [B1] ...`).
- [ ] Se houve BLOQUEANTE: voltou ao `codigo` sozinho; IMPORTANTES/SUGESTÕES só
      apareceram na aprovação.
- [ ] Pediu aprovação; após o OK, commitou nos dois repos (`git log` em cada um).
- [ ] Gerou `~/.harness/runs/SBX-1/handoff.yaml` a partir do OpenAPI commitado.
- [ ] Rodou o fechamento de aprendizado e o `relatorio.py SBX-1`.
- [ ] Perguntou a próxima história (no sandbox não há BFF: responda que não).

### SBX-2: dados faltando
A história é vaga de propósito. Espere pendências `faltando:` (método, path,
critério de "cliente ok", status de erro) **todas numa pergunta só**, e nada de
código antes de você responder. Se o agente inventar o critério, o checklist
não está sendo seguido.

### SBX-3: história sem endpoint
Espere a classificação "outro" e o `fluxo-generico.md`: plano de arquivos
(`Pagina.java`) para aprovar, alteração, teste, review e commit só na aplicação.
Bom teste para o review: o `default: 20` do contrato no gateway fica desatualizado.
Veja se ele aponta (em Observações, já que o gateway não está no diff).

### Anote tudo
Para cada coisa errada, registre **onde** corrigir (regra do aprendizado):
o kit (skill/agente/checklist) ou o repo (AGENTS.md/docs). Corrija no kit,
rode `pytest`, rode o `sync.py` de novo no sandbox (ou recrie) e repita.

## Nível 4 — Medição e aprendizado

Depois de 2 ou 3 histórias no sandbox:

```bash
python .claude/medicao/relatorio.py SBX-1
python .claude/aprendizado/aprendizado.py analisar
```

- Tokens zerados no relatório: abra o transcript (caminho no `log.jsonl`) e
  ajuste a leitura de `usage` (item do `proximos-passos.md`).
- `analisar` deve agrupar apontamentos repetidos por categoria.

## Nível 5 — Repo real

Só depois do sandbox. Siga a "Ordem sugerida" do `proximos-passos.md`: sync na
aplicação e no gateway reais, preencher AGENTS.md e `docs/patterns/`, e uma
história **real e pequena**, só da fase 1.

## Nível 6 — Devin

No mesmo sandbox, abra a pasta `aplicacao-java/` no Devin e confira se as skills
de `.agents/skills` aparecem (Customize > Skills). Repita SBX-1: sem subagents e
sem hooks, as fases rodam num agente só e o review segue a skill `code-review`
direto. Anote o que não funcionar em `proximos-passos.md` (seção Devin).

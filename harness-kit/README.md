# harness-kit

Fonte e documentação do harness de agentes (Claude Code e Devin) para os repos
do time. **Este repo não executa nada**: ele guarda a versão oficial das skills,
agentes e hooks, documenta as decisões e instala tudo nos repos com o `sync.py`.

> Comece por `docs/arquitetura.md`. Para retomar o contexto com um agente,
> use `docs/prompt-contexto.md`.

## O que é o harness, em uma frase
O kit define o **processo**, cada repo define o **contexto**, a sessão do
Claude/Devin **executa**.

## Peças

| Peça | O que faz |
|---|---|
| `kit/skills/desenvolver-historia` | Orquestrador. O agente principal da sessão segue esta skill: fases fixas, subagents, branch, commit e handoff. |
| `kit/skills/preparar-branch` | Todo o git do fluxo: preparar, verificar e encerrar a branch `feature/<id>`. |
| `kit/agents/api-owner.md` | Gera a spec a partir da história e altera o contrato OpenAPI no gateway. |
| `kit/agents/codigo.md` | Implementa na aplicação a partir da spec. |
| `kit/agents/review.md` | Revisor read-only: APROVADO ou REPROVADO com apontamentos. |
| `kit/hooks/check_branch.py` | PreToolUse (Claude): bloqueia Edit/Write fora de `feature/<id>`. |
| `kit/sensores/rodar_sensores.py` | Stop/SubagentStop: roda build, testes e validação do contrato; o agente não encerra com falha. |
| `kit/contratos/` | Schema e validador da spec trocada entre os agentes. |
| `kit/mcp/` | MCP local (experimental): endpoints do código e comparação com o contrato. |
| `kit/medicao/` | Log por execução, resumo e comparação com a entrega real (evals). |
| `kit/aprendizado/` | Acha o que se repete entre execuções e registra regras aplicadas. |
| `kit/githooks/` | Pre-commit: rede final, vale para qualquer ferramenta. |
| `templates/` | AGENTS.md e `.harness/project.yaml` iniciais. Copiados uma vez, depois são do repo. |
| `sync.py` | Instala/atualiza o kit num repo conforme o perfil. |

## Repos atendidos

| Repo | Perfil | Recebe |
|---|---|---|
| aplicacao-java | `aplicacao` | skills, agentes, hooks, git hook, templates |
| gateway-padrao | `gateway` | git hook, templates |
| web-bff | `bff` | skills, agentes, hooks, git hook, templates |
| gateway-bff | `gateway` | git hook, templates |

## Como instalar

```bash
python sync.py --repo C:/dev/aplicacao-java --perfil aplicacao
python sync.py --repo C:/dev/gateway-padrao --perfil gateway
```

Depois:
1. Preencha os `<placeholders>` do `AGENTS.md` e do `.harness/project.yaml` de cada repo.
2. Crie `~/.harness/workspace.yaml` com os caminhos locais (veja `docs/arquitetura.md`).
3. Abra o Claude/Devin na aplicação e rode: `desenvolver história <id>`.

## Regras do kit
- Arquivo vindo de `kit/` **não se edita no repo**: edite aqui e rode o sync.
- Arquivo vindo de `templates/` é do repo depois de criado: o sync não sobrescreve.
- Mudou o kit? Atualize `VERSION` e `CHANGELOG.md`.

## Documentação
- `docs/arquitetura.md`: como as peças se encaixam e o fluxo completo.
- `docs/decisoes/`: o porquê de cada escolha.
- `docs/historico/`: de onde as ideias vieram.
- `docs/prompt-contexto.md`: prompt para retomar o contexto em outra máquina.
- `docs/proximos-passos.md`: o que falta validar e construir.
- `docs/roadmap.md`: evolução do harness, ponto a ponto.
- `docs/evals.md` e `docs/case/`: como medir e onde registrar o case.

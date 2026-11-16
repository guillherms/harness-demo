# harness-kit

Harness para desenvolver histórias com agentes, de ponta a ponta, em qualquer repo do time:
spec → (plan + tasks, se complexa) → OK humano → infra local → implementação → validação → review → commit.

Funciona no **Claude Code** (orquestração com subagents) e no **Devin** (mesmas skills, rodando na sessão).
Versão: ver `VERSION`.

## A ideia: simbiose

O kit **roda de fora** dos repos e se liga a eles, como um simbionte:

- **Dentro de cada repo** fica só o conhecimento daquele repo: `.harness/constitution.md` (+ referências).
  Versionado com o código, muda no mesmo PR que muda o repo.
- **Fora, no harness-kit**, fica a execução: skills, agentes, scripts e o que cada história gera
  (spec, plan, handoff, métricas).

Assim, um kit só serve para qualquer repo do time, e histórias que atravessam vários repos
(aplicação + gateway → BFF + gateway BFF) têm um lugar natural para o handoff.
O dev continua no controle: o fluxo para para o OK humano, o revisor só lê e o review tem limite de rodadas.

---

## Estrutura

```
harness-kit/                      ← abra a sessão do Claude/Devin AQUI
  AGENTS.md / CLAUDE.md           pontos de entrada e regras gerais
  VERSION
  local.example.yaml              copie para local.yaml (fora do git): caminhos dos SEUS clones
  metricas.md                     uma linha por história (tempo, tokens, rodadas...) → base do case
  progress/<apelido>.md           handoff entre histórias do mesmo repo (≤ 5 linhas por história)
  execucoes/<id>/                 gerado: spec.md, infra.yaml, plan.md, handoff.json, amostras/
  templates/
    constitution.md               copiar para <repo>/.harness/constitution.md
    spec.md  infra.yaml  plan.md  referencia.md
  scripts/
    infra_localstack.py           cria/reseta SNS, SQS, DLQ, filtro e S3 (com arquivos) no LocalStack
    testar_cenarios.py            publica cenários e confere: consumida / filtrada / dlq
    cobertura_taac.py             todo CA da spec tem cenário @<id>-CA<n> no Cucumber?
    diff_contratos.py             rotas da aplicação (filtradas pela integração) que faltam no BFF
  .claude/
    skills/  desenvolver-historias  desenvolver-par  spec-historia  extrair-referencia
             infra-localstack  testar-cenarios
    agents/  spec-writer  planner  implementador  revisor

<cada repo alvo>/
  .harness/constitution.md        conhecimento do repo (preencher 1x)
  .harness/referencias/*.md       padrões extraídos de outros repos (ex.: banco)
```

## Instalação

1. Clone o harness-kit. `pip install -r requirements.txt`.
2. `cp local.example.yaml local.yaml` e ajuste os caminhos dos seus clones.
3. Em cada repo alvo, copie `templates/constitution.md` para `.harness/constitution.md` e preencha.
   - No revisor (`.claude/agents/revisor.md`), troque o caminho da sua skill de code review.
   - Opcional: uma linha no `AGENTS.md` do repo apontando para `.harness/constitution.md`.
4. Se a história precisa de algo de outro projeto (ex.: o banco já mapeado lá):
   `extrair referência banco de projeto_banco para listeners`.
5. Confirme como o repo cria filas no LocalStack (script de init?) e registre na constitution.

## Como rodar

Abra a sessão **dentro do harness-kit**, dando acesso aos repos alvo.

- **Claude Code**: abra no harness-kit e adicione os diretórios dos repos (ex.: `--add-dir <caminho>`). Confira como fica no Windows com os caminhos de vocês.
  - `desenvolver histórias 1234 1235 no listeners`
  - `desenvolver par 2001 2002`
- **Devin**: abra o harness-kit com os repos no workspace e peça
  `siga .claude/skills/desenvolver-historias/SKILL.md para 1234 no listeners`.
  Sem subagents, ele faz as etapas na própria sessão: use **uma sessão nova por história** (e, nas complexas, por task, se der).

O fluxo fala com você em: OK da spec/plan, itens não suportados, 3ª rodada de review e fechamento (tempo/tokens).

---

## Fluxo

1. **Branch** `feature/<id>` (no repo e nos satélites que a história tocar).
2. **Spec** (`spec-writer`): regra, critérios de aceite copiados com ID, `infra.yaml`, lacunas e **não suportados**.
3. **Classificação**: complexa se tem várias integrações, itens não suportados, repo satélite ou se você pedir.
4. **Plan + tasks** (`planner`, só complexa). T1 é sempre o TAAC.
5. **OK humano**, uma parada só.
6. **Infra local** (script): fila, filtro, DLQ, bucket com arquivo de exemplo.
7. **Implementação**: simples → um `implementador`; complexa → um `implementador` novo por task.
8. **Validação** (determinística): build → cobertura do TAAC → TAAC → cenários no LocalStack.
9. **Review** (`revisor`, só leitura): contra a spec, e se cada cenário do TAAC testa de verdade o CA. Máximo 2 rodadas.
10. **Fechamento**: commit, `metricas.md`, `progress/<apelido>.md`.

**Par aplicação → BFF** (`desenvolver-par`): história da aplicação → `diff_contratos.py` gera o handoff
(rotas que faltam no BFF, só as da integração da aplicação) → OK humano → história do BFF.

---

## Decisões (e por quê)

| Decisão | Motivo |
|---|---|
| Kit roda **fora** dos repos; constitution **dentro** | Um kit para qualquer repo; handoff entre repos tem lugar natural. *(v0.1 rodava dentro do repo; mudou quando entrou o caso de vários repos.)* |
| Histórias em sequência, não em paralelo | Mexem nos mesmos arquivos (config, init script); em sequência não há conflito. |
| Agente novo por etapa, por história e por task | Isolamento de contexto: lixo de uma etapa não contamina a outra. |
| Orquestrador passa caminhos, não conteúdo | Cada agente lê só o que precisa (lista "Leia (só isso)"). |
| SDD lite com plan/tasks **condicionais** | Listener simples: o código de referência é o plano. História com S3 + banco + TAAC: sem tasks o contexto estoura. |
| Critérios de aceite copiados, com ID, sem reescrever | Rastreabilidade história → TAAC; agente não "interpreta" o critério. |
| TAAC primeiro (T1) | Os cenários viram o alvo executável das próximas tasks (BDD na prática). |
| Cobertura do TAAC por script + significado pelo revisor | Existência da tag é determinística; se o cenário testa o critério, exige leitura. |
| "Não suportado" explícito → para no OK humano | Melhor o harness admitir o limite do que inventar bucket/banco e falhar silencioso. |
| Referências externas extraídas uma vez | Agente lê um resumo curto, não explora o outro repo a cada história. |
| Infra, teste, cobertura e diff por script | O agente decide o quê; o script faz o como. Não gasta token, não varia. |
| Handoff app → BFF **calculado** (diff de contratos) | Determinístico, não esquece rota; filtra pela integração para ignorar rotas de outras aplicações. |
| Scripts recusam endpoint que não seja local | Nunca tocar a AWS real. |
| Fila "espiã" no teste de cenários | Sabe se a mensagem passou no filtro mesmo com o listener consumindo a fila. |
| Revisor só leitura, máximo 2 rodadas | Evita loop e estouro de token; na 3ª escala para o humano. |
| Tokens/custo nas métricas | Limite mensal de tokens + números para o case. |
| `progress/` ≤ 5 linhas por história | Compressão: passa o aprendizado, não a conversa. |

## Onde está o SDD

| Etapa | No harness |
|---|---|
| Constitution | `<repo>/.harness/constitution.md` |
| Specify | `spec-writer` → `spec.md` |
| Clarify | lacunas + não suportados + OK humano |
| Plan | `planner` → `plan.md` (**só complexa**) |
| Tasks | tasks do `plan.md`, um implementador por task (**só complexa**) |
| Implement | `implementador` |
| Validate | build + cobertura TAAC + TAAC + cenários locais + `revisor` |

## Onde está a engenharia de contexto

- **Isolar**: agente novo por etapa, por história e por task.
- **Selecionar**: cada agente tem "Leia (só isso)"; o orquestrador passa caminhos.
- **Comprimir**: `progress/` (≤ 5 linhas), resumo de 3 linhas entre tasks, referências extraídas.
- **Escrever fora**: spec, plan, infra, handoff e métricas em arquivo, não na conversa.
- **Carregar sob demanda**: skills e referências só entram quando a etapa chega.
- **Tirar do LLM o determinístico**: infra, teste de cenários, cobertura do TAAC e diff de contratos são scripts.

---

## Pendências

- **Branches**: cada história sai da `develop`; arquivos compartilhados vão conflitar no merge. Alternativa: encadear.
- **Devin**: confirmar descoberta de skills de projeto e trabalho com vários repos no mesmo workspace.
- **Claude Code no Windows**: validar acesso aos repos fora do workspace.
- **Diff de contratos**: confirmar a chave de integração no contrato real e montar o `--mapa` se o BFF renomear rotas.
- **Endpoints** (próxima fase): template de spec de rota, H2/migrations, env-profile por repo.

## Changelog

- **0.2.0** — kit fora dos repos (simbiose); constitution por repo; plan/tasks condicionais + agente `planner`;
  CAs com ID + `cobertura_taac.py`; TAAC primeiro; "não suportado"; S3 na infra; referências externas;
  `desenvolver-par` + `diff_contratos.py`; tokens nas métricas; `VERSION`.
- **0.1.0** — fluxo simples de listeners SQS dentro do repo.

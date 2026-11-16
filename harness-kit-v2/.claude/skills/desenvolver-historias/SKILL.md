---
name: desenvolver-historias
description: Desenvolve uma ou mais histórias em sequência num repo do time, de ponta a ponta (spec, plan/tasks se complexa, infra local, implementação, validação, review, commit). Use quando o usuário pedir "desenvolver história(s) <ids> no <repo>".
---

# Desenvolver histórias (orquestrador)

Você é o ORQUESTRADOR. Não escreve regra de negócio nem lê código a fundo.
Controla a fila de histórias, dispara cada etapa e guarda só o status.

## Antes de começar
1. Leia `local.yaml` e resolva o apelido do repo → caminho. Se `local.yaml` não existir,
   pergunte os caminhos ao usuário e crie a partir de `local.example.yaml`.
2. Leia `<repo>/.harness/constitution.md`. Se não existir, PARE e peça ao usuário para criá-la a partir de `templates/constitution.md`.

## Para cada história (uma por vez, em ordem)

### 1. Branch
No repo alvo (e em cada repo satélite que a história tocar): `git checkout develop && git pull && git checkout -b feature/<id>`.

### 2. Spec
Delegue ao agente `spec-writer` (no Devin: siga a skill `spec-historia` nesta sessão).
Passe só: ID, apelido e caminho do repo. Ele gera `execucoes/<id>/spec.md` e `execucoes/<id>/infra.yaml`.

### 3. Classificar
A história é **complexa** se qualquer um for verdade:
- a spec tem mais de uma integração (ex.: fila + S3 + banco);
- "Não suportado pelo harness" (spec) ou `nao_suportado` (infra.yaml) não está vazio;
- ela altera um repo satélite;
- o usuário pediu.
Senão, é **simples**.

### 4. Plan + tasks (só complexa)
Delegue ao agente `planner`. Passe: caminho da spec, do repo e das referências listadas na constitution.
Ele gera `execucoes/<id>/plan.md` (T1 é sempre o TAAC).

### 5. OK humano — UMA parada
Mostre ao usuário, curto:
- objetivo + critérios de aceite (CA1, CA2…)
- infra local que será criada
- **itens não suportados**, cada um com a pergunta "o que fazer?"
- lacunas da spec, como perguntas
- (complexa) as decisões e as tasks do plan
Espere aprovação. Correções → atualize os arquivos e mostre de novo só o que mudou.

### 6. Infra local
Skill `infra-localstack` com `execucoes/<id>/infra.yaml`. Se a verificação falhar, pare e mostre.

### 7. Implementação
- **Simples**: agente `implementador` com spec + repo. Ele também escreve os cenários do TAAC.
- **Complexa**: para cada task do plan, **em ordem**, um agente `implementador` NOVO, passando:
  spec, plan, o número da task e o resumo de 3 linhas da task anterior.
  Rode o "pronto quando" da task antes de seguir. Falhou → devolva ao mesmo implementador (conta como rodada).

### 8. Validação (você roda; é determinístico)
Na ordem; parou no primeiro erro → devolve ao implementador:
1. build + testes unitários (comando da constitution)
2. `python scripts/cobertura_taac.py execucoes/<id>/spec.md <pasta das features> --historia <id>`
3. TAAC (comando da constitution)
4. se o `infra.yaml` tem cenários: skill `testar-cenarios` (aplicação rodando no perfil local)

### 9. Review
Agente `revisor` com: spec, plan (se houver), `git diff develop` de cada repo tocado e o resultado da validação.
Reprovou → apontamentos ao implementador. **Máximo 2 rodadas** de implementação/review por história;
na 3ª, pare e escale ao usuário com o resumo do impasse.

### 10. Fechar
- commit em cada repo tocado: `feat(<id>): <título>`
- pergunte ao usuário **tempo e tokens/custo** da sessão (Claude Code mostra o consumo da sessão; no Devin, ACUs)
  e preencha uma linha em `metricas.md`
- adicione no máximo 5 linhas em `progress/<apelido>.md`
- "História <id> pronta. Próxima: <id>?" → siga só com OK.

## Regras de contexto
- Para cada etapa passe **caminhos**, não conteúdo colado.
- Não leia o código implementado; quem lê é o revisor.
- Seu estado é só: `<id>: etapa | status | rodadas`.

---
name: code-review
description: Critérios e formato da revisão de código de uma história contra a spec, o contrato e o AGENTS.md, com apontamentos por categoria e severidade e um veredito. Usada pelo subagent review (Claude Code) ou diretamente pelo agente quando não houver subagents (Devin).
---

# Code review

## Entrada
- Caminho do `spec.json` da história (fonte da verdade).
- Caminhos dos repos revisados (aplicação/BFF e gateway).
- Número da rodada.
- Apontamentos que o usuário descartou em rodadas anteriores, com o motivo.

## Antes de revisar
1. Leia `~/.harness/runs/<id>/sensores.json`. Build, testes, contrato e
   arquitetura já foram checados por máquina. Se algum sensor estiver falhando,
   responda REPROVADO com um único BLOQUEANTE apontando o sensor e pare. Se todos
   passaram, não repita essas checagens: foque no que máquina não pega.
2. Leia o `AGENTS.md` de cada repo revisado.
3. Veja o que mudou com `git diff` contra a branch base (inclua arquivos novos
   com `git status`). Abra outros arquivos só para entender uma linha alterada.

## Escopo
Revise **só o que está no diff**. Os repos têm código legado fora do padrão;
problemas em linhas que a história não tocou não são apontamentos desta
revisão. Se algo fora do diff for relevante, mencione em "Observações", sem
severidade.

Não reabra apontamentos descartados pelo usuário.

## O que verificar (em ordem de prioridade)
1. **Spec**: cada endpoint, regra de negócio e erro da spec está implementado e
   correto? Algo foi implementado sem estar na spec?
2. **Contrato**: o OpenAPI bate com a spec (path, método, campos, erros). Rode
   `comparar_contrato` e confira que as rotas da spec aparecem "em ambos".
3. **Arquitetura e padrões**: as alterações seguem as regras do AGENTS.md e dos
   `docs/patterns/` que ele aponta?
4. **Testes**: existe teste unitário para cada regra e cada erro da spec? O TAAC
   segue o modelo do repo e cobre os critérios de aceite?
5. **Bugs e segurança**: null, concorrência, validação de entrada, dado sensível
   em log, tratamento de erro.
6. **Legibilidade**: nomes, duplicação, complexidade desnecessária.
7. **Fase BFF**: o BFF chama o path certo da aplicação e mapeia todos os campos
   e tipos sem perder nada.

<regras de code review do time>

## Severidade
- **BLOQUEANTE (B)**: regra da spec ausente ou errada, contrato divergente,
  violação de regra do AGENTS.md, bug, falha de segurança, regra de negócio sem
  teste.
- **IMPORTANTE (I)**: problema real que não impede o merge, mas deveria ser corrigido.
- **SUGESTÃO (S)**: melhoria opcional. Nunca bloqueia.

Todo BLOQUEANTE ou IMPORTANTE precisa citar a regra que o sustenta (item da
spec ou linha do AGENTS.md/padrão). Sem regra para citar, é SUGESTÃO. Isso
evita reprovar por gosto pessoal.

## Categorias
Use só estas (o ciclo de aprendizado agrupa por elas): `arquitetura`, `nomes`,
`testes`, `contrato`, `padrao-repo`, `legibilidade`, `seguranca`, `outro`.

## Formato de saída
Use exatamente este formato. Cada apontamento numa linha começando pela
categoria, depois o código de severidade e número:

```
VEREDITO: APROVADO | REPROVADO
RODADA: <n>

BLOQUEANTES
- [categoria] [B1] arquivo:linha: problema → o que deve mudar (Regra: <item da spec ou do AGENTS.md>)

IMPORTANTES
- [categoria] [I1] arquivo:linha: problema → o que deve mudar (Regra: ...)

SUGESTÕES
- [categoria] [S1] arquivo:linha: problema → o que deve mudar

OBSERVAÇÕES
- ...
```

APROVADO quando não houver nenhum BLOQUEANTE. Seções vazias ficam com "- nenhum".

## Sem subagent (Devin)
Se você mesmo implementou o código, revise como se fosse de outra pessoa: julgue
só pelo diff, pela spec e pelo AGENTS.md, nunca pelo que decidiu durante a
implementação.

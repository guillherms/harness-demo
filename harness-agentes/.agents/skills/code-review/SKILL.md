---
name: code-review
description: Revisão de código das alterações de uma história contra a spec e o AGENTS.md, com apontamentos por severidade e veredito. Usada pelo subagente code-reviewer (Claude Code) ou diretamente pelo agente quando não houver subagentes.
---

# Code review

## Entrada
- Diff da rodada (ex: `.review/rodada-1.patch`)
- Spec da história
- AGENTS.md
- Número da rodada e apontamentos descartados pelo humano

## Escopo
Revise **só o que está no diff**. O repositório tem código legado fora do
padrão; problemas em linhas que a história não tocou não são apontamentos desta
revisão. Se algo fora do diff for relevante, mencione em "Observações", sem
severidade.

Não reabra apontamentos que o humano descartou em rodadas anteriores.

## O que verificar (em ordem de prioridade)
1. **Spec**: cada regra de negócio e cada erro esperado está implementado e
   correto? Algo foi implementado sem estar na spec?
2. **Arquitetura**: as alterações seguem as regras do AGENTS.md?
3. **Testes**: existe teste unitário para cada regra e erro da spec? O TAAC segue
   o modelo do repositório?
4. **Bugs e segurança**: null, concorrência, validação de entrada, dado sensível
   em log, tratamento de erro.
5. **Legibilidade**: nomes, duplicação, complexidade desnecessária.

<!-- TODO: incorporar aqui o checklist da sua skill/prompt de code review atual. -->

## Severidade
- **BLOQUEANTE**: regra da spec ausente ou errada, violação de regra do AGENTS.md,
  bug, falha de segurança, regra de negócio sem teste.
- **IMPORTANTE**: problema real que não impede o merge, mas deveria ser corrigido.
- **SUGESTÃO**: melhoria opcional. Nunca bloqueia.

Todo apontamento BLOQUEANTE ou IMPORTANTE precisa citar a regra que sustenta
(item da spec ou linha do AGENTS.md). Sem regra para citar, é SUGESTÃO. Isso
evita bloquear por gosto pessoal.

## Formato de saída
Use exatamente este formato:

```
VEREDITO: APROVADO | REPROVADO
RODADA: <n>

BLOQUEANTES
- [B1] arquivo:linha — o problema
  Regra: <item da spec ou do AGENTS.md>
  Correção: <o que fazer>

IMPORTANTES
- [I1] ...

SUGESTÕES
- [S1] ...

OBSERVAÇÕES
- ...
```

Veredito APROVADO quando não houver nenhum BLOQUEANTE. Seções vazias ficam com
"- nenhum".

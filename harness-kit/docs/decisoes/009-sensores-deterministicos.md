# 009 — Sensores determinísticos antes do review

**Decisão:** quando um agente declara que terminou (hooks `Stop` e
`SubagentStop`), o harness roda os sensores dos repos alterados: `mvn verify`
(build, testes e ArchUnit) na aplicação e validação do OpenAPI no gateway. Se
falhar, o agente é obrigado a continuar, com no máximo 3 tentativas.

**Por quê:** o review por LLM pode errar igual ao agente que escreveu. O que
máquina consegue checar, máquina checa. O review passa a olhar só o que máquina
não pega.

**Por que não compilar a cada edição:** no Maven, compilar leva de dezenas de
segundos a minutos; a cada Edit, o agente passaria mais tempo esperando.

**Context engineering:** o sensor devolve só as últimas 40 linhas do log de cada
falha. Log inteiro no contexto atrapalha mais do que ajuda.

**Brownfield:** o ArchUnit usa `freeze`, que grava as violações que já existem
(endpoints legados) e só falha nas novas. Não é preciso arrumar o passado para
proteger o futuro.

**Cada repo é dono dos seus comandos:** os sensores ficam em
`.harness/sensores.json` no repo; o kit só traz o executor e os templates.

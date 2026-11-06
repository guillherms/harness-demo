# 005 — Encadear histórias por artefato (handoff)

**Decisão:** a história 1 termina gerando um handoff; a história 2 começa lendo-o.
Cada história mantém branch, commit e PR próprios.

**Por quê:** o BFF só precisa da interface que a aplicação expõe, não do
histórico da sessão. Passar o resumo certo em vez do histórico inteiro é context
engineering. O arquivo também permite retomar em outra sessão ou ferramenta.

**Regra:** o handoff é extraído do OpenAPI commitado, depois do review OK.
Entre as histórias há um ponto de decisão humana (id da história 2).

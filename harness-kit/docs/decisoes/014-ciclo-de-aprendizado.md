# 014 — Ciclo de aprendizado: erro recorrente vira regra

**Decisão:** no fim de cada história, `aprendizado.py analisar` agrupa os
apontamentos de review (com categoria fixa) e as falhas de sensor de todas as
execuções. O que se repetiu duas vezes ou mais vira sugestão de regra, com
destino e texto propostos pelo orquestrador. O humano aprova; a mudança é feita
fora da branch da história.

**Divisão de trabalho:** a máquina conta e agrupa (determinístico); o LLM
sintetiza e sugere onde registrar; o humano decide.

**Regra de destino:** o lugar mais determinístico que resolve. Sensor >
AGENTS.md > skill/agente > checklist do review. Se um aprendizado volta depois de
tratado (REINCIDENTE), sobe um degrau: o que estava em texto vira verificação.

**Por quê:** sem isso, o harness só melhora quando você lembra de melhorar. Com
isso, cada história alimenta a próxima, e o histórico de regras aplicadas
(`~/.harness/aprendizado.jsonl`) mostra no case como o harness evoluiu.

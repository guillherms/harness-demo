# 002 — harness-kit como repo separado

**Decisão:** manter um repo `harness-kit` com a fonte do harness e a documentação.

**Por quê:** num brownfield, `.claude/`, hooks e settings se misturam ao código e
a visão do todo se perde. O kit é o lugar onde o harness "mora": dá para ler,
entender, apresentar e versionar. Também evita copiar e colar entre a aplicação
e o BFF.

**O que o kit NÃO é:** não executa nem orquestra nada. Para executar, basta o
harness instalado na aplicação.

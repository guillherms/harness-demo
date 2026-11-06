# 006 — Relação entre repos commitada, caminho local fora do Git

**Decisão:** `.harness/project.yaml` (commitado) diz quem é o par;
`~/.harness/workspace.yaml` (por desenvolvedor) diz onde cada repo está clonado.

**Por quê:** cada dev clona num lugar diferente, mas a relação "este repo tem
como par o gateway X" é conhecimento do time. Um mapa por usuário evita
perguntar o caminho em cada repo. A skill tenta a pasta irmã antes de perguntar.

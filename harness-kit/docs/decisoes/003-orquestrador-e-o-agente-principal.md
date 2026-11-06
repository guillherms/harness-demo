# 003 — O orquestrador é o agente principal + skill

**Decisão:** a orquestração vive na skill `desenvolver-historia`. O agente
principal da sessão, aberta na aplicação, segue essa skill.

**Por quê:** o fluxo é fixo (gateway → aplicação → review → BFF), então uma
sequência de fases escrita na skill é suficiente e funciona no Claude e no Devin.

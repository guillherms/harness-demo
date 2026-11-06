# 011 — Spec como contrato entre agentes (JSON + schema)

**Decisão:** o api-owner grava a spec em `~/.harness/runs/<id>/spec.json`, no
formato de `kit/contratos/spec.schema.json`. Ela é validada em dois momentos:
- **ao salvar** (hook PostToolUse): estrutura e regras; o api-owner corrige na hora;
- **antes do código** (gate `--pronta`): além disso, exige zero pendências.

Daqui em diante, `codigo` e `review` recebem o caminho da spec, não a história.

**Por quê (context engineering):** texto livre entre agentes é onde a
informação se perde ou é reinterpretada. Um formato fixo define exatamente o
que passa de um agente para o outro, ocupa menos contexto e pode ser checado
por máquina. A spec vira a fonte da verdade da história.

**Regras além do schema:** endpoint duplicado, `{param}` no path sem
`path_params` correspondente (e vice-versa), GET/DELETE com body.

**Handoff:** usa o mesmo formato de endpoint, então a fase BFF lê sem tradução.

**Dependência:** `jsonschema`, que já vem com o `openapi-spec-validator`.

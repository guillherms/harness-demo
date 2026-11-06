# Changelog

## 0.7.0
- Ciclo de aprendizado: `aprendizado.py` (analisar recorrência, registrar regra
  aplicada), categorias fixas nos apontamentos do review, fechamento por fase.
- Sensores registram qual sensor falhou.

## 0.6.0
- Medição: `registrar.py` (hooks + marcos), `relatorio.py` (resumo por execução),
  `comparar_gabarito.py` (resultado × entrega real).
- Roteiro de evals, conjunto de histórias e template de resultados do case.

## 0.5.0
- MCP local experimental (`kit/mcp/`): `listar_endpoints`, `endpoint_modelo`,
  `comparar_contrato`. Compatível com `mcp` 1.x e 2.x. Lógica também roda como script.
- Agentes usam as ferramentas em vez de explorar o repo.

## 0.4.0
- Spec entre agentes em JSON com schema (`kit/contratos/`), validada ao salvar
  (PostToolUse) e no gate antes do código (`--pronta`).
- Handoff usa o mesmo formato de endpoint da spec.

## 0.3.0
- Permissões no `settings.json`: git de escrita, deploy, rede e credenciais
  negados; leitura de git, sensores e `preparar_branch.py` liberados.
- `preparar_branch.py commit`: único caminho de commit, sempre valida a branch.

## 0.2.0
- Sensores determinísticos: `rodar_sensores.py` nos hooks Stop/SubagentStop,
  `.harness/sensores.json` por repo, template de ArchUnit com freeze.
- Review lê o resultado dos sensores e foca no que máquina não pega.

## 0.1.0
- Primeira versão: orquestrador `desenvolver-historia` (fases aplicação e BFF),
  `preparar-branch`, subagents api-owner/codigo/review, hook PreToolUse de
  branch, git hook pre-commit, templates e `sync.py`.

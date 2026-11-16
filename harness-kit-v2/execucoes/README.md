# Execuções

Gerado pelo harness, uma pasta por história: `execucoes/<id>/`

| Arquivo | Quem gera | Para quê |
|---|---|---|
| `spec.md` | spec-writer | regra, critérios de aceite (CA), lacunas |
| `infra.yaml` | spec-writer | infra local + cenários de teste |
| `plan.md` | planner (só histórias complexas) | decisões técnicas + tasks |
| `handoff.json` | `scripts/diff_contratos.py` (par app → BFF) | rotas que faltam no BFF |
| `amostras/` | spec-writer / você | arquivos de exemplo (ex.: o arquivo que vai no S3) |

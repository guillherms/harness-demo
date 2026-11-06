# 013 — Medição por execução e evals com histórias entregues

**Decisão:** hooks registram metadados de cada execução em
`~/.harness/runs/<id>/log.jsonl`; `relatorio.py` resume (tokens, ferramentas,
arquivos lidos, review, sensores, intervenções); `comparar_gabarito.py` compara
o resultado do harness com o que foi entregue de verdade.

**Por quê:** sem números, "o harness melhorou" é opinião. Com evals, cada
mudança no harness vira experimento: mesmas histórias, antes e depois.

**Primeira pergunta a responder:** o MCP (decisão 012) reduz exploração e
tokens? Rodar as evals com e sem ele.

**Cuidados:**
- O log guarda só metadados (ferramenta, arquivo, comando). Nada de conteúdo de
  prompt ou de arquivo.
- Medição nunca bloqueia: erro no registro é ignorado.
- A soma de tokens depende do formato do transcript da versão do Claude Code e
  de os transcripts dos subagents serem informados aos hooks. Conferir.
- Poucas histórias e uma execução por cenário dão indício, não prova. LLM varia:
  quando a diferença for pequena, rode duas vezes.

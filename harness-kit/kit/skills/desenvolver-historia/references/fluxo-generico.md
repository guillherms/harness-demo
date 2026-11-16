# Fluxo genérico: histórias que não mexem em endpoint

Para histórias sem rota criada, alterada ou excluída (ajuste de regra interna,
job, refatoração pedida, correção). Não há spec JSON nem contrato: é menos
guiado, então a confirmação com o usuário pesa mais.

1. **Preparar branch** só no repo da aplicação, com `preparar-branch`.

2. **Completar o entendimento** → liste o que a história pede, marcando cada
   item como ✅ encontrado (com o trecho), 🟡 inferido ou ❌ faltando. Pergunte
   os 🟡 e ❌ de uma vez.

3. **Planejar** → delegue ao `codigo` uma leitura (sem editar) que devolva os
   arquivos que pretende criar ou alterar e por quê. Mostre ao usuário e siga
   após o OK. Salve o plano aprovado em `~/.harness/runs/<id>/plano.md`: ele faz
   o papel da spec para o `codigo` e o `review`.

4. **Código** → verifique a branch e delegue ao `codigo` com o caminho do
   `plano.md`. Testes unitários para cada regra do plano e TAAC quando a
   história mexer em comportamento exposto.

5. **Review, aprovação e commit** → como nos passos 6 e 7 de
   `fase-aplicacao.md`, passando o `plano.md` no lugar do `spec.json`.

6. **Registrar** → no resumo final, diga se esse tipo de história parece
   recorrente. Se for, vale criar um fluxo próprio para ele no kit.

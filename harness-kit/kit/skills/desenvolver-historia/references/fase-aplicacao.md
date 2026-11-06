# Fase 1: par da aplicação (aplicação Java + gateway)

1. **Buscar a história** pelo MCP da ferramenta de histórias. Guarde o título e
   os critérios de aceite.

2. **Preparar branch** nos dois repos com a skill `preparar-branch`
   (história + caminhos da aplicação e do gateway). Falhou → pare.

3. **Spec** → delegue ao `api-owner` no modo `spec`, passando a história e o
   caminho do gateway. Ele grava `~/.harness/runs/<id>/spec.json`.
   - Se houver pendências, pergunte ao usuário, delegue de novo com as respostas.
   - Gate: `python .claude/contratos/validar_spec.py <spec.json> --pronta`.
     Só siga com saída OK (schema válido e sem pendências).
   - Mostre a spec ao usuário em poucas linhas e siga após o OK.
   - Daqui em diante, os subagents recebem o **caminho do spec.json**, não o
     texto da história.

4. **Contrato** → verifique a branch e delegue ao `api-owner` no modo `contrato`
   (spec + caminho do gateway).

5. **Código** → verifique a branch e delegue ao `codigo` (spec + caminho da aplicação).

6. **Review** → os sensores já rodaram quando os subagents terminaram
   (`~/.harness/runs/<id>/sensores.json`). Delegue ao `review` (spec + caminhos
   dos dois repos).
   - Registre cada veredito: `python .claude/medicao/registrar.py marcar review <APROVADO|REPROVADO>`.
   - Registre cada apontamento:
     `python .claude/medicao/registrar.py marcar apontamento <categoria> <resumo curto>`.
   - REPROVADO: devolva os apontamentos ao `codigo` (ou ao `api-owner`, se o
     problema for no contrato) e repita o review.
   - Máximo de 3 rodadas. Depois disso, pare e mostre as pendências ao usuário.

7. **Aprovação** → mostre ao usuário o resumo das alterações nos dois repos.
   Com o OK, faça o commit com `preparar-branch commit --mensagem "<id>: <título>"`.
   Push só se o usuário pedir.

8. **Handoff** → preencha `references/handoff-template.yaml` **a partir do
   OpenAPI commitado no gateway**, não da spec nem da memória. Salve em
   `~/.harness/runs/<id>/handoff.yaml`.

9. **Próxima história** → procure via MCP uma história vinculada a esta.
   Se não achar, pergunte o id. Se o usuário não quiser seguir, encerre a execução.

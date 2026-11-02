---
name: desenvolver-historia
description: Desenvolve uma história do backlog a partir do ID dela. Busca a história pelo MCP, transforma em uma spec, identifica o tipo de trabalho (criar endpoint, editar endpoint ou outro), executa o fluxo certo e passa por code review até ficar aceitável. Use sempre que o usuário pedir "desenvolver história <id>", "implementar a história <id>", "pegar a história <id>" ou colar o texto de uma história pedindo para implementá-la.
---

# Desenvolver história

Esta skill é a porta de entrada para qualquer história. Ela cuida do que é comum a
todas (obter, entender, confirmar, testar, revisar) e delega o que é específico
para um arquivo em `fluxos/`. Leia só o fluxo que for usar: cada um traz
checklist e referências próprias, e carregar fluxos que não serão usados só ocupa
contexto.

As regras de arquitetura, testes e TAAC do repositório estão no AGENTS.md (e nos
docs que ele aponta). Esta skill descreve o procedimento; não repita nem
contradiga o AGENTS.md.

## 1. Obter a história
- Se o usuário passou um ID, busque com a ferramenta do MCP `<SERVIDOR_MCP>` que
  retorna uma história pelo ID. (O nome exato da ferramenta varia entre Claude
  Code e Devin; procure pela do servidor `<SERVIDOR_MCP>`.)
- Se colou o texto, use o texto.
- Se não há nenhum dos dois, peça o ID.

O retorno do MCP é texto livre. Use-o só para montar a spec (passo 2); dali em
diante trabalhe com a spec, não com o texto bruto.

## 2. Montar a spec
Preencha `templates/spec.md` com o que a história diz. Não invente: o que não
está na história fica em branco por enquanto (o fluxo escolhido vai tratar).

## 3. Classificar
| Tipo | Quando | Fluxo |
|---|---|---|
| Criar endpoint | A história descreve uma rota que **não existe** no repositório | `fluxos/criar-endpoint.md` |
| Editar endpoint | A história altera uma rota que **já existe** | ainda não disponível → use `fluxos/generico.md` |
| Outro | Nenhum dos anteriores | `fluxos/generico.md` |

Confirme no código, não só no texto: procure a rota no repositório (busca pelo
path ou pelo nome do controller). É uma leitura pontual; não explore o projeto.

Se a história for mista (ex: cria um endpoint e altera outro) ou ambígua,
pergunte ao usuário como seguir.

## 4. Confirmar antes de agir
Mostre em uma linha o que entendeu e espere o ok. Exemplo:
> Entendi como **criação** do endpoint `GET /contratos/{id}/parcelas`. Sigo?

Isso evita gastar tempo e contexto no fluxo errado.

## 5. Executar o fluxo
Leia o arquivo de `fluxos/` escolhido e siga-o. Assim que a spec for confirmada
no fluxo, salve-a no local de specs definido no AGENTS.md (se não houver,
`specs/<id-da-historia>.md`). A revisão do passo 7 depende dela.

## 6. Testes
Rode os testes unitários e o TAAC do que foi criado/alterado. Corrija até
passarem. Não envie para revisão código com teste quebrado: a revisão é cara e
não deve ser gasta com o que o compilador e os testes já apontam.

## 7. Code review (loop com humano)
A revisão segue a skill `code-review` e deve acontecer com contexto limpo: quem
revisa não deve ver o raciocínio da implementação, só o resultado.

- **Se a ferramenta tiver subagentes** (Claude Code): use o subagente
  `code-reviewer`.
- **Se não tiver**: leia `code-review` e revise você mesmo, baseando-se só no
  diff, na spec e no AGENTS.md. Não use o que você decidiu durante a
  implementação para justificar o código; julgue como se fosse de outra pessoa.

A cada rodada `n`:
1. Salve o diff da história em `.review/rodada-<n>.patch` (`git diff` contra a
   branch base, incluindo arquivos novos).
2. Rode a revisão passando: o caminho do diff, o caminho da spec, o número da
   rodada e a lista de apontamentos descartados pelo usuário.
3. Mostre o resultado ao usuário, agrupado por severidade, e pergunte o que
   corrigir. Padrão sugerido: bloqueantes e importantes. O usuário pode
   descartar qualquer apontamento; registre o motivo.
4. Corrija só o que o usuário escolheu, rode os testes de novo (passo 6) e vá
   para a próxima rodada.

Pare o loop quando:
- o veredito for APROVADO e o usuário concordar; ou
- chegar à rodada 3. Nesse caso, apresente o que ficou pendente e deixe o
  usuário decidir. Mais rodadas raramente convergem; costumam indicar spec
  ambígua ou divergência que precisa de decisão humana.

## 8. Fechar
- Atualize a spec com os arquivos alterados e as decisões confirmadas
  (incluindo apontamentos descartados e o motivo).
- Resuma para o usuário: arquivos criados/alterados, decisões inferidas que ele
  confirmou, resultado da revisão e qualquer pendência.

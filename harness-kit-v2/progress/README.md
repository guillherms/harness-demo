# Progresso por repo

Um arquivo por repo alvo: `progress/<apelido>.md` (ex.: `progress/listeners.md`).

É o handoff entre histórias do mesmo repo. Cada história, ao fechar, adiciona **no máximo 5 linhas**
com o que a PRÓXIMA precisa saber. Nada de log do que foi feito.
Quando uma linha vira regra fixa, mova para a constitution do repo e apague daqui.

Exemplo:
```
## 1234 — listener de cessão aprovada
- O listener novo também precisa ser registrado em X.
- Teste de integração só roda com o perfil `local`.
```

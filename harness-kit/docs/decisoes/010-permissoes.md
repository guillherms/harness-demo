# 010 — Permissões: "não faça" vira "não consegue"

**Decisão:** o `settings.json` do kit nega git de escrita, deploy, rede e
leitura de credenciais. Todo commit e troca de branch passa pelo
`preparar_branch.py`, que é liberado e sempre valida a branch.

**Por quê:** "subagent não executa git" era só instrução; o modelo pode
ignorar. Negar o comando torna a regra real para todos, inclusive o
orquestrador. Em vez de dar exceção ao orquestrador, a escrita no git virou um
único caminho controlado (o script).

**Credenciais:** `~/.m2/settings.xml` costuma ter usuário e senha do
repositório Maven; `.env`, `~/.aws` e `~/.ssh` idem. Nada disso precisa entrar
no contexto do agente.

**Limitações conhecidas:**
- Regras de Bash casam pelo texto do comando. Um subagent com Bash ainda pode
  chamar o script de commit; a defesa ali é a instrução + o HITL antes do commit.
- Permissões são guarda-corpo, não sandbox.

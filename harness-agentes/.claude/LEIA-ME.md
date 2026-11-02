# Não edite .claude/skills

`.claude/skills` é uma cópia gerada de `.agents/skills`, que é a fonte da
verdade (lida pelo Devin). O Claude Code só lê `.claude/skills`, por isso a cópia.

Edite em `.agents/skills` e rode `gradlew syncSkills`.

`.claude/agents/` não é gerado: o subagente é exclusivo do Claude Code.

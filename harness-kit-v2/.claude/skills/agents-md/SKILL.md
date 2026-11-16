---
name: agents-md
description: Avalia um AGENTS.md/CLAUDE.md existente com nota de 0 a 10, sugere e aplica melhorias, ou cria um enxuto para um projeto que não tem.
---

# AGENTS.md — avaliar ou criar

Princípio: o AGENTS.md (ou CLAUDE.md) é carregado em TODO request. Deve ser o menor possível e usar progressive disclosure: na raiz só o que vale pra toda tarefa; o resto em docs separados ou skills.

Primeiro, descubra o modo:
- Existe AGENTS.md ou CLAUDE.md (raiz ou subpastas)? → **Modo Avaliar**
- Não existe? → **Modo Criar**

Se existirem os dois, verifique se um aponta pro outro (symlink, ou um CLAUDE.md que só referencia o AGENTS.md). Se forem cópias independentes, aponte a duplicação como problema.

## Receita (o que um bom AGENTS.md tem)

1. **Uma frase dizendo o que é o projeto**: o que faz e pra quem. Funciona como papel e âncora pro agente.
2. **Gerenciador de pacotes / build**: só se não for o padrão da linguagem. Inclui wrapper e o que não usar.
3. **Comandos fora do padrão**: build, teste, typecheck/lint, como rodar um teste só, profile/env necessário pra subir.
4. **Ponteiros pra docs separados**: um por domínio (linguagem, testes, API, Git), em tom de conversa, sem SEMPRE/NUNCA em caixa alta. Docs podem apontar pra outros docs.
5. **Conceitos de domínio estáveis, com moderação**: termos que o agente pode confundir. Conceitos, não paths.
6. **Monorepo**: a raiz tem propósito, navegação e ferramentas compartilhadas; o pacote tem propósito, stack e convenções locais. Nenhum nível sobrecarregado.
7. **Ponteiros com gatilho**: cada ponteiro diz QUANDO ler o doc ("ao criar endpoints, veja docs/API.md"), não só lista arquivos.

**Fica de fora:** o que o agente já sabe, instrução vaga demais pra agir, árvore de pastas e paths detalhados, conteúdo gerado por script de init, regras que valem só pra um domínio.

**Teste de cada linha:** vale pra TODA tarefa do repo? Se não vale, sai da raiz.

## Rubrica (nota 0–10)

Pontos positivos (máx. 10):
- Frase do projeto clara: 2
- Build/gerenciador correto (ou ausência correta, quando é o padrão): 2
- Comandos fora do padrão presentes e corretos: 2
- Ponteiros pra docs separados com gatilho (ou desnecessários porque o projeto é pequeno): 2
- Tudo na raiz passa no "teste de cada linha": 2 (desconte proporcionalmente)

Descontos:
- Contradição entre instruções: -1 cada
- Comando ou path citado que não existe no repo: -1 cada
- Árvore de pastas ou mapa de paths: -1
- Ponteiro sem gatilho (só lista o arquivo): -0,5 cada (máx. -1)
- Regra óbvia ou vaga ("escreva código limpo"): -0,5 cada (máx. -2)
- SEMPRE/NUNCA/caixa alta forçando: -0,5 (uma vez)
- Regra de domínio específico na raiz: -0,5 cada (máx. -2)
- Tamanho: mais de 60 linhas -1; mais de 150 linhas -2

A nota mínima é 0. Sempre mostre de onde veio cada ponto ganho e cada desconto. A nota precisa ser reproduzível, sem impressão subjetiva.

## Modo Avaliar

1. Leia todos os AGENTS.md/CLAUDE.md (raiz e aninhados) e os docs que eles referenciam.
2. **Verifique contra o repo**: cada comando citado existe (scripts do package.json, plugins do pom.xml/build.gradle, Makefile)? Cada path citado existe? Marque o que estiver desatualizado.
3. Aplique a rubrica e mostre: a nota, a tabela de pontos e descontos e a lista de problemas.
4. **Contradições**: liste cada uma e pergunte ao usuário qual versão fica. Não decida sozinho.
5. Proponha a reestruturação:
   - um AGENTS.md raiz mínimo;
   - as regras removidas da raiz MOVIDAS pra docs/<DOMINIO>.md (nada some sem estar listado);
   - uma lista do que sugere apagar (redundante, óbvio, vago), com o motivo.
6. Mostre o diff e **pergunte antes de aplicar**. Remoções precisam de confirmação explícita.
7. Aplique, avalie de novo e mostre a nota antes e depois.

## Modo Criar

Seja contido de propósito: o erro a evitar é gerar um arquivo inchado.

1. Leia SÓ os arquivos de build/config (pom.xml, build.gradle, package.json, lockfiles, Makefile, Dockerfile, .nvmrc, etc.) pra descobrir a linguagem, as versões, o build tool e os comandos.
2. **Pergunte** ao usuário a frase do projeto. Não invente a partir do código.
3. Pergunte se há algo que vale pra toda tarefa e que não dá pra deduzir dos arquivos (profile obrigatório, regra de arquitetura entre módulos).
4. Gere no máximo ~15 linhas, seguindo a receita. Na dúvida, deixe de fora.
5. Não crie docs/ vazios "pra depois". Ponteiros só pra docs que já existem.
6. Mostre o arquivo e pergunte antes de gravar.
7. Se o time usa Claude Code e outra ferramenta que lê AGENTS.md, crie um CLAUDE.md que só referencia o AGENTS.md, em vez de symlink. No Windows, symlink exige permissão de admin ou modo desenvolvedor e costuma quebrar no Git.

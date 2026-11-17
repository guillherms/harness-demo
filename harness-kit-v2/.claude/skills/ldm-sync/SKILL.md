---
name: ldm-sync
description: Atualiza a base de conhecimento do modelo de dados (docs/data-model/) a partir de um .ldm do PowerDesigner salvo em XML. Use quando o time trouxer uma nova versão do .ldm ou pedir para atualizar/sincronizar o modelo de dados do harness.
---

# ldm-sync — Sincronizar o modelo de dados

Converte o modelo lógico do PowerDesigner (.ldm) em markdown legível por agentes,
salvo por **diagrama** e por **tabela**, e mostra o que mudou desde o último parse.

O PowerDesigner é a fonte da verdade. A pasta gerada é só um espelho: **nunca edite
os arquivos gerados à mão** — corrija no PowerDesigner e rode esta skill de novo.

## Regras

- **O parse é sempre feito pelo script.** Nunca leia, interprete ou converta o XML
  do .ldm por conta própria: o arquivo é grande e ruidoso, e o resultado tem que
  ser determinístico.
- Se o script falhar, reporte o erro ao usuário e pare. Não improvise um parse alternativo.
- Não faça commit. Quem revisa e commita é o usuário.

## Passo a passo

1. **Confirme as entradas.**
   - Caminho do `.ldm` novo (pergunte se o usuário não informou).
   - Pasta de saída: `docs/data-model` por padrão, a não ser que o harness use outra.

2. **Rode primeiro em modo simulação**, a partir da raiz do repositório:
   ```bash
   python <pasta-da-skill>/scripts/parse_ldm.py <arquivo.ldm> --out docs/data-model --dry-run
   ```
   - "Nada mudou" → avise o usuário e encerre.
   - "não parece XML" → peça para salvar o modelo no PowerDesigner no formato XML (não binário).
   - "não parece uma pasta gerada por esta skill" → confirme o caminho de saída com o usuário.
     Só use `--force` se ele confirmar.

3. **Apresente o diff ao usuário** antes de gravar:
   - **Mudanças que podem quebrar** primeiro (tabela/coluna removida, tipo alterado,
     tamanho/precisão reduzidos, coluna passou a ser obrigatória, mudança de PK).
     Para cada uma, aponte o risco em uma linha (ex.: "tamanho de COD_X caiu de 32 para 20:
     código que grava 32 posições vai quebrar").
   - Depois as demais mudanças, de forma resumida.
   - Repasse os avisos relevantes (colunas sem tipo, tabelas fora de diagramas,
     códigos repetidos, relacionamentos não resolvidos).

4. **Grave** (sem `--dry-run`) após o OK do usuário:
   ```bash
   python <pasta-da-skill>/scripts/parse_ldm.py <arquivo.ldm> --out docs/data-model
   ```

5. **Confira** que `docs/data-model/_meta.md` tem a data de hoje e contagens coerentes
   com o diff. Abra uma tabela alterada para checar se a mudança aparece.

6. **Encerre** com um resumo curto e uma sugestão de mensagem de commit, ex.:
   `chore(data-model): sync do LDM — 2 quebras, 5 tabelas novas`

## O que é gerado

```
docs/data-model/
  _meta.md         origem, SHA-256, data do parse, última modificação no PowerDesigner
  _last-diff.md    mudanças em relação ao parse anterior
  index.md         catálogo de diagramas e tabelas — ponto de entrada para agentes
  catalog.json     versão estruturada (usada pelo diff e por validadores/sensores)
  diagrams/<DIAGRAMA>.md   tabelas do diagrama + relacionamentos entre elas
  tables/<TABELA>.md       colunas, tipo, tamanho, obrigatoriedade, PK/FK,
                           relacionamentos, comments e atributos estendidos
```

Cada tabela é salva **uma vez só** em `tables/`, mesmo que apareça em vários
diagramas; os diagramas apontam para ela.

## Limitações conhecidas

- Heranças (`Inheritance`) são contadas, mas não detalhadas.
- Atalhos (shortcuts) para entidades de outros modelos aparecem como "(externo)".
- Atributos estendidos são lidos no modo "melhor esforço"; se falhar, a coluna sai
  sem eles e o script avisa.

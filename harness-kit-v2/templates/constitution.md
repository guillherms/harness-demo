# Constitution — <apelido do repo>

> Copie para `<repo>/.harness/constitution.md` e preencha os `<...>`.
> É o conhecimento do repo: fica DENTRO dele, versionado com o código.
> O harness (que roda de fora) lê este arquivo antes de mexer aqui.

## Identificação
| Campo | Valor |
|---|---|
| Apelido (igual ao `local.yaml`) | `<listeners>` |
| Tipo | `<listeners SQS / aplicação de endpoints / BFF>` |
| Stack | `<Java 21 / Spring Boot 3>` |
| Padrão de branch | `feature/<id>`, a partir da `develop` |
| Ferramenta MCP que busca a história | `<nome_da_tool>` |

## Comandos
| Para quê | Comando (Windows entre parênteses) |
|---|---|
| Build + testes unitários | `<./mvnw clean verify>` (`<mvnw.cmd clean verify>`) |
| Rodar o TAAC (Cucumber) | `<./mvnw verify -Ptaac>` |
| Subir a aplicação local | `<./mvnw spring-boot:run -Dspring-boot.run.profiles=local>` |

## Onde ficam as coisas
| O quê | Caminho |
|---|---|
| Código de referência (o "molde") | `<src/.../ListenerExistente.java>` |
| Teste unitário de referência | `<src/test/.../ListenerExistenteTest.java>` |
| Features do TAAC | `<src/test/resources/features/>` |
| Config (application.yml) | `<src/main/resources/application.yml>` |
| Script de init do LocalStack | `<docker/localstack/init/ready.d/init.sh>` (ou "não existe") |
| Padrão de nome de fila/bucket | `<sqs-<dominio>-<evento>>` |

## Repos satélites (o harness altera junto, na mesma história)
<!-- ex.: aplicação → gateway (contrato OpenAPI) -->
| Apelido no local.yaml | O que se altera lá | Caminho do contrato |
|---|---|---|
| `<gateway>` | contrato OpenAPI | `<openapi/contrato.yaml>` |
| Filtro da integração desta aplicação no contrato | `<texto da URI que só esta aplicação tem>` | |

## Referências externas (só leitura)
<!-- extraídas uma vez com a skill extrair-referencia -->
| Nome | Arquivo de referência | Para quê |
|---|---|---|
| `<banco>` | `.harness/referencias/banco.md` | `<como mapear o banco X (datasource, entidade, migration)>` |

## Regras (nunca quebre)
1. Infra só no LocalStack. Nunca crie, altere ou apague recurso na AWS real.
2. Não edite o `AGENTS.md` deste repo.
3. Siga o código de referência: estrutura de pacotes, anotações, tratamento de erro, estilo de teste.
4. Cada história mexe só no que a spec pede. Nada de refatorar código vizinho.
5. Regra sem spec aprovada não é implementada. Na dúvida, pergunte.
6. Todo critério de aceite (CA) da história precisa de cenário no TAAC com a tag `@<id>-CA<n>`.
7. <regras específicas do time / do repo>

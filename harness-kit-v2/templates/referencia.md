# Referência: <nome> (extraída de <apelido do repo de origem>)

> Extraída UMA vez. Os agentes leem este resumo, não o repo de origem.
> Atualize só se o padrão do repo de origem mudar.

## Para que serve
<ex.: como o projeto X conecta e grava no banco Y>

## Arquivos que compõem o padrão
| Papel | Arquivo de origem | Observação |
|---|---|---|
| Config | `<application.yml>` (trecho `spring.datasource`) | |
| Entidade | `<.../XEntity.java>` | |
| Repository | `<.../XRepository.java>` | |
| Migration | `<db/migration/V1__x.sql>` | Flyway/Liquibase? |

## Trechos essenciais
```java
// trechos curtos, só o que define o padrão
```

## Como roda localmente / em teste
<H2? Docker? Testcontainers? perfil?>

## Cuidados
- <dialeto, schema, credenciais locais...>

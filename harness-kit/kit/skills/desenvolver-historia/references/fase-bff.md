# Fase 2: par BFF (web-bff + gateway-bff)

O BFF não tem regra de negócio: ele expõe as rotas da aplicação seguindo os
padrões do BFF. A entrada é a história 2 **mais** o handoff da fase 1.

1. **Buscar a história 2** pelo MCP e ler `~/.harness/runs/<id-fase-1>/handoff.yaml`.

2. **Preparar branch** com o id da história 2 nos repos `web-bff` e `gateway-bff`.

3. **Spec BFF** → delegue ao `api-owner` no modo `spec-bff`. Mesmo gate da
   fase 1: `validar_spec.py <spec.json> --pronta`.
   - Para cada endpoint do handoff, uma rota correspondente no BFF.
   - O padrão é repasse 1:1. Só muda o que a história 2 pedir explicitamente
     (path, campos filtrados, autenticação).

4. **Contrato** → `api-owner` no modo `contrato`, no gateway BFF.

5. **Código** → `codigo` no web-bff, seguindo o AGENTS.md do BFF.

6. **Review** → `review`, incluindo a checagem de upstream: o BFF chama o path
   certo da aplicação e mapeia campos e tipos sem perder nada.

7. **Aprovação e commit** como na fase 1. Depois, encerre a execução.

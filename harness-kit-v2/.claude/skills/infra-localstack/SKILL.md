---
name: infra-localstack
description: Cria no LocalStack, de forma idempotente, a infra de um infra.yaml (tópico SNS, fila SQS, DLQ, subscription com filtro, buckets S3 com arquivos de exemplo) e verifica. Use antes de implementar/testar uma história.
---

# Infra no LocalStack

Você **não** cria recurso na mão. Quem cria é o script.

## Passos
1. Confirme que o LocalStack está de pé (`docker ps` ou o compose do repo). Se não estiver, peça ao usuário para subir.
2. Rode, a partir do workspace:
   ```
   python scripts/infra_localstack.py execucoes/<id>/infra.yaml
   ```
   (Windows: `py` no lugar de `python`. Endpoint padrão `http://localhost:4566`; mude com `LOCALSTACK_ENDPOINT`.)
3. Leia a saída: cada recurso vem como `criado`, `ja_existia` ou `removido`, e no fim a VERIFICAÇÃO.
   Se aparecer "NÃO SUPORTADO", isso já devia ter sido decidido no OK humano — confirme com o usuário.
4. Se o repo **tem script de init** do LocalStack (ver constitution), acrescente nele os comandos
   da seção "PARA O SCRIPT DE INIT", no formato que já existe lá. Assim o próximo dev já tem a infra.
   (Isso é alteração no repo alvo: entra no commit da história.)

## Reset (limpar antes de recomeçar)
```
python scripts/infra_localstack.py execucoes/<id>/infra.yaml --reset [--incluir-topico]
```

## Nunca
- Rodar contra endpoint que não seja o LocalStack (o script também recusa).
- Editar o script para "fazer funcionar". Falhou → mostre o erro ao usuário.

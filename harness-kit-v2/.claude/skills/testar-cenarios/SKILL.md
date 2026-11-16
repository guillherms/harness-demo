---
name: testar-cenarios
description: Publica no LocalStack os cenários de um infra.yaml e confere se cada mensagem foi consumida, filtrada ou foi para a DLQ. Use depois de implementar um listener, com a aplicação rodando localmente.
---

# Testar cenários no LocalStack

## Pré-requisitos
- Infra criada (skill `infra-localstack`).
- Aplicação rodando local apontando para o LocalStack (comando "subir a aplicação local" da constitution).

## Rode
```
python scripts/testar_cenarios.py execucoes/<id>/infra.yaml --espera 20
```

## Como ler
Para cada cenário: `OK` ou `FALHOU` com o motivo.
- **consumida**: passou no filtro, saiu da fila e não foi para a DLQ.
- **filtrada**: o filtro barrou (nem chegou na fila).
- **dlq**: terminou na DLQ.

O script confere **onde a mensagem foi parar**, não o efeito de negócio (gravou, leu do S3…).
O efeito é coberto pelos testes unitários, pelo TAAC e pelo revisor.
Saída: 0 = tudo OK; 1 = algum cenário falhou.

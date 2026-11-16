"""Publica os cenários de um infra.yaml no tópico e confere onde cada mensagem foi parar.

Uso:
    python testar_cenarios.py <infra.yaml> [--espera 20]

Como funciona:
  - Cria uma fila "espiã" temporária, assinada no mesmo tópico com o MESMO filtro.
    A aplicação não consome a espiã, então dá para saber se a mensagem passou no filtro.
  - Cada cenário é publicado com um atributo extra `harnessCenario` (não afeta o filtro).
  - Resultados:
      filtrada  -> não chegou na espiã
      consumida -> chegou na espiã, não está na DLQ e a fila principal esvaziou
      dlq       -> está na DLQ
  - No fim, a fila espiã é removida.

Só roda contra LocalStack.
"""
import argparse
import json
import os
import sys
import time
import uuid
from urllib.parse import urlparse

import boto3
import yaml

HOSTS_PERMITIDOS = {"localhost", "127.0.0.1", "localstack", "host.docker.internal"}
ATRIBUTO_ID = "harnessCenario"


def clientes():
    endpoint = os.environ.get("LOCALSTACK_ENDPOINT", "http://localhost:4566")
    host = urlparse(endpoint).hostname or ""
    if host not in HOSTS_PERMITIDOS and "localstack" not in host:
        sys.exit(f"[ABORTADO] endpoint '{endpoint}' não parece LocalStack.")
    kw = dict(endpoint_url=endpoint, region_name=os.environ.get("AWS_REGION", "sa-east-1"),
              aws_access_key_id="test", aws_secret_access_key="test")
    return boto3.client("sns", **kw), boto3.client("sqs", **kw)


def topico_arn(sns, nome):
    for pagina in sns.get_paginator("list_topics").paginate():
        for t in pagina["Topics"]:
            if t["TopicArn"].split(":")[-1] == nome:
                return t["TopicArn"]
    sys.exit(f"[ERRO] tópico '{nome}' não existe. Rode a skill infra-localstack antes.")


def url(sqs, nome):
    try:
        return sqs.get_queue_url(QueueName=nome)["QueueUrl"]
    except sqs.exceptions.QueueDoesNotExist:
        sys.exit(f"[ERRO] fila '{nome}' não existe. Rode a skill infra-localstack antes.")


def atributos_sns(atributos):
    saida = {}
    for k, v in (atributos or {}).items():
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            saida[k] = {"DataType": "String", "StringValue": str(v)}
        else:
            saida[k] = {"DataType": "Number", "StringValue": str(v)}
    return saida


def ids_na_fila(sqs, fila_url, apagar=False):
    """Lê a fila e devolve os ids de cenário encontrados (envelope SNS ou raw)."""
    achados = set()
    for _ in range(5):
        r = sqs.receive_message(QueueUrl=fila_url, MaxNumberOfMessages=10, WaitTimeSeconds=1,
                                VisibilityTimeout=0 if not apagar else 30,
                                MessageAttributeNames=["All"])
        msgs = r.get("Messages", [])
        if not msgs:
            break
        for m in msgs:
            attr = m.get("MessageAttributes", {}).get(ATRIBUTO_ID, {}).get("StringValue")
            if not attr:
                try:
                    corpo = json.loads(m["Body"])
                    attr = corpo.get("MessageAttributes", {}).get(ATRIBUTO_ID, {}).get("Value")
                except (ValueError, AttributeError):
                    attr = None
            if attr:
                achados.add(attr)
            if apagar:
                sqs.delete_message(QueueUrl=fila_url, ReceiptHandle=m["ReceiptHandle"])
    return achados


def profundidade(sqs, fila_url):
    a = sqs.get_queue_attributes(QueueUrl=fila_url, AttributeNames=[
        "ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"])["Attributes"]
    return int(a["ApproximateNumberOfMessages"]) + int(a["ApproximateNumberOfMessagesNotVisible"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("infra_yaml")
    p.add_argument("--espera", type=int, default=20, help="segundos para o listener processar")
    a = p.parse_args()
    with open(a.infra_yaml, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cenarios = cfg.get("cenarios") or []
    if not cenarios:
        sys.exit("[ERRO] nenhum cenário no infra.yaml.")
    if not cfg.get("topico") or not cfg.get("fila"):
        sys.exit("[ERRO] os cenários publicam no tópico: o infra.yaml precisa de 'topico' e 'fila'.")

    sns, sqs = clientes()
    t_arn = topico_arn(sns, cfg["topico"])
    fila_url = url(sqs, cfg["fila"])
    dlq_url = url(sqs, cfg["dlq"]) if cfg.get("dlq") else None

    espia_nome = f"{cfg['fila']}-harness-espia"[:80]
    espia_url = sqs.create_queue(QueueName=espia_nome)["QueueUrl"]
    espia_arn = sqs.get_queue_attributes(QueueUrl=espia_url,
                                         AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]
    sub_attrs = {"RawMessageDelivery": str(bool(cfg.get("raw_message_delivery", False))).lower()}
    if cfg.get("filtro"):
        sub_attrs["FilterPolicy"] = json.dumps(cfg["filtro"])
    espia_sub = sns.subscribe(TopicArn=t_arn, Protocol="sqs", Endpoint=espia_arn,
                              Attributes=sub_attrs, ReturnSubscriptionArn=True)["SubscriptionArn"]

    try:
        ids = {}
        for c in cenarios:
            cid = uuid.uuid4().hex[:12]
            ids[cid] = c
            attrs = atributos_sns(c.get("atributos"))
            attrs[ATRIBUTO_ID] = {"DataType": "String", "StringValue": cid}
            payload = c.get("payload", {})
            sns.publish(TopicArn=t_arn, MessageAttributes=attrs,
                        Message=payload if isinstance(payload, str) else json.dumps(payload))
            print(f"publicado: {c['nome']}")

        print(f"\naguardando {a.espera}s o listener processar...\n")
        time.sleep(a.espera)

        na_espia = ids_na_fila(sqs, espia_url, apagar=True)
        na_dlq = ids_na_fila(sqs, dlq_url) if dlq_url else set()
        fila_vazia = profundidade(sqs, fila_url) == 0

        falhas = 0
        for cid, c in ids.items():
            esperado = c.get("esperado", "consumida")
            if cid in na_dlq:
                obtido = "dlq"
            elif cid not in na_espia:
                obtido = "filtrada"
            elif fila_vazia:
                obtido = "consumida"
            else:
                obtido = "ainda na fila (listener rodando?)"
            ok = obtido == esperado
            falhas += 0 if ok else 1
            print(f"{'OK     ' if ok else 'FALHOU '} {c['nome']}: esperado={esperado} obtido={obtido}")

        if not fila_vazia:
            print("\nAtenção: a fila principal ainda tem mensagens. A aplicação está rodando e apontando para o LocalStack?")
        print(f"\n{len(ids) - falhas}/{len(ids)} cenários OK")
        sys.exit(1 if falhas else 0)
    finally:
        sns.unsubscribe(SubscriptionArn=espia_sub)
        sqs.delete_queue(QueueUrl=espia_url)


if __name__ == "__main__":
    main()

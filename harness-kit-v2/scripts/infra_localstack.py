"""Cria (ou remove) no LocalStack a infra descrita num infra.yaml.

Uso:
    python infra_localstack.py <infra.yaml> [--reset] [--incluir-topico]

Suporta:
    - SNS -> SQS (tópico, fila, DLQ, subscription com filter policy)  [opcional]
    - S3 (buckets e upload de arquivos de exemplo)                     [opcional]
Avisa sobre itens em `nao_suportado` (não cria nada para eles).

Variáveis de ambiente (opcionais):
    LOCALSTACK_ENDPOINT  (padrão http://localhost:4566)
    AWS_REGION           (padrão sa-east-1)

Só roda contra LocalStack: recusa qualquer endpoint que não seja local.
"""
import argparse
import json
import os
import sys
from urllib.parse import urlparse

import boto3
import yaml

HOSTS_PERMITIDOS = {"localhost", "127.0.0.1", "localstack", "host.docker.internal"}


def endpoint_seguro():
    endpoint = os.environ.get("LOCALSTACK_ENDPOINT", "http://localhost:4566")
    host = urlparse(endpoint).hostname or ""
    if host not in HOSTS_PERMITIDOS and "localstack" not in host:
        sys.exit(f"[ABORTADO] endpoint '{endpoint}' não parece LocalStack. Nada foi feito.")
    return endpoint


def clientes():
    endpoint = endpoint_seguro()
    regiao = os.environ.get("AWS_REGION", "sa-east-1")
    kw = dict(endpoint_url=endpoint, region_name=regiao,
              aws_access_key_id="test", aws_secret_access_key="test")
    return (boto3.client("sns", **kw), boto3.client("sqs", **kw),
            boto3.client("s3", **kw), regiao)


def status(recurso, nome, estado, extra=""):
    print(f"  {estado:<11} {recurso:<13} {nome} {extra}".rstrip())


# ---------- SQS / SNS ----------

def url_da_fila(sqs, nome):
    try:
        return sqs.get_queue_url(QueueName=nome)["QueueUrl"]
    except sqs.exceptions.QueueDoesNotExist:
        return None


def arn_da_fila(sqs, url):
    return sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]


def topico_existente(sns, nome):
    for pagina in sns.get_paginator("list_topics").paginate():
        for t in pagina["Topics"]:
            if t["TopicArn"].split(":")[-1] == nome:
                return t["TopicArn"]
    return None


def garantir_fila(sqs, nome, atributos=None):
    url = url_da_fila(sqs, nome)
    if url:
        if atributos:
            sqs.set_queue_attributes(QueueUrl=url, Attributes=atributos)
        status("fila", nome, "ja_existia")
    else:
        url = sqs.create_queue(QueueName=nome, Attributes=atributos or {})["QueueUrl"]
        status("fila", nome, "criado")
    return url, arn_da_fila(sqs, url)


def subscription_da_fila(sns, topico_arn, fila_arn):
    for pagina in sns.get_paginator("list_subscriptions_by_topic").paginate(TopicArn=topico_arn):
        for s in pagina["Subscriptions"]:
            if s["Endpoint"] == fila_arn:
                return s["SubscriptionArn"]
    return None


def criar_mensageria(cfg, sns, sqs, regiao, init):
    topico, fila, dlq = cfg.get("topico"), cfg.get("fila"), cfg.get("dlq")
    filtro = cfg.get("filtro")
    raw = bool(cfg.get("raw_message_delivery", False))
    erros = []

    atributos_fila = {}
    if dlq:
        _, dlq_arn = garantir_fila(sqs, dlq)
        atributos_fila["RedrivePolicy"] = json.dumps({
            "deadLetterTargetArn": dlq_arn,
            "maxReceiveCount": str(cfg.get("max_receive_count", 3)),
        })
    fila_url, fila_arn = garantir_fila(sqs, fila, atributos_fila)
    conta = fila_arn.split(":")[4]

    if dlq:
        init.append(f"awslocal sqs create-queue --queue-name {dlq}")
        redrive = json.dumps({"deadLetterTargetArn": f"arn:aws:sqs:{regiao}:{conta}:{dlq}",
                              "maxReceiveCount": str(cfg.get("max_receive_count", 3))})
        init.append(f"awslocal sqs create-queue --queue-name {fila} "
                    f"--attributes '{json.dumps({'RedrivePolicy': redrive})}'")
    else:
        init.append(f"awslocal sqs create-queue --queue-name {fila}")

    if not topico:
        if dlq and "RedrivePolicy" not in sqs.get_queue_attributes(
                QueueUrl=fila_url, AttributeNames=["All"])["Attributes"]:
            erros.append("fila sem RedrivePolicy para a DLQ")
        return erros

    topico_arn = topico_existente(sns, topico)
    if topico_arn:
        status("topico", topico, "ja_existia")
    else:
        topico_arn = sns.create_topic(Name=topico)["TopicArn"]
        status("topico", topico, "criado")

    politica = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow", "Principal": {"Service": "sns.amazonaws.com"},
            "Action": "sqs:SendMessage", "Resource": fila_arn,
            "Condition": {"ArnEquals": {"aws:SourceArn": topico_arn}},
        }],
    }
    sqs.set_queue_attributes(QueueUrl=fila_url, Attributes={"Policy": json.dumps(politica)})

    sub_arn = subscription_da_fila(sns, topico_arn, fila_arn)
    if sub_arn:
        status("subscription", f"{topico} -> {fila}", "ja_existia")
    else:
        attrs = {"RawMessageDelivery": str(raw).lower()}
        if filtro:
            attrs["FilterPolicy"] = json.dumps(filtro)
        sub_arn = sns.subscribe(TopicArn=topico_arn, Protocol="sqs", Endpoint=fila_arn,
                                Attributes=attrs, ReturnSubscriptionArn=True)["SubscriptionArn"]
        status("subscription", f"{topico} -> {fila}", "criado")
    if filtro:
        sns.set_subscription_attributes(SubscriptionArn=sub_arn, AttributeName="FilterPolicy",
                                        AttributeValue=json.dumps(filtro))
    sns.set_subscription_attributes(SubscriptionArn=sub_arn, AttributeName="RawMessageDelivery",
                                    AttributeValue=str(raw).lower())

    init.append(f"awslocal sns create-topic --name {topico}")
    sub_attrs = {"RawMessageDelivery": str(raw).lower()}
    if filtro:
        sub_attrs["FilterPolicy"] = json.dumps(filtro)
    init.append(f"awslocal sns subscribe --topic-arn arn:aws:sns:{regiao}:{conta}:{topico} "
                f"--protocol sqs --notification-endpoint arn:aws:sqs:{regiao}:{conta}:{fila} "
                f"--attributes '{json.dumps(sub_attrs)}'")

    # verificação (sem publicar nada, para não acionar o listener)
    attrs_fila = sqs.get_queue_attributes(QueueUrl=fila_url, AttributeNames=["All"])["Attributes"]
    if dlq and "RedrivePolicy" not in attrs_fila:
        erros.append("fila sem RedrivePolicy para a DLQ")
    attrs_sub = sns.get_subscription_attributes(SubscriptionArn=sub_arn)["Attributes"]
    if filtro and json.loads(attrs_sub.get("FilterPolicy", "{}")) != filtro:
        erros.append("filtro da subscription diferente do infra.yaml")
    return erros


def resetar_mensageria(cfg, sns, sqs, incluir_topico):
    topico_arn = topico_existente(sns, cfg["topico"]) if cfg.get("topico") else None
    fila_url = url_da_fila(sqs, cfg["fila"])
    if topico_arn and fila_url:
        sub = subscription_da_fila(sns, topico_arn, arn_da_fila(sqs, fila_url))
        if sub:
            sns.unsubscribe(SubscriptionArn=sub)
            status("subscription", f"{cfg['topico']} -> {cfg['fila']}", "removido")
    for nome in filter(None, [cfg["fila"], cfg.get("dlq")]):
        url = url_da_fila(sqs, nome)
        if url:
            sqs.delete_queue(QueueUrl=url)
            status("fila", nome, "removido")
    if incluir_topico and topico_arn:
        sns.delete_topic(TopicArn=topico_arn)
        status("topico", cfg["topico"], "removido")


# ---------- S3 ----------

def bucket_existe(s3, nome):
    try:
        s3.head_bucket(Bucket=nome)
        return True
    except s3.exceptions.ClientError:
        return False


def criar_s3(itens, s3, regiao, base, init):
    erros = []
    for item in itens:
        bucket = item["bucket"]
        if bucket_existe(s3, bucket):
            status("bucket", bucket, "ja_existia")
        else:
            kw = {} if regiao == "us-east-1" else {
                "CreateBucketConfiguration": {"LocationConstraint": regiao}}
            s3.create_bucket(Bucket=bucket, **kw)
            status("bucket", bucket, "criado")
        init.append(f"awslocal s3 mb s3://{bucket}")
        for arq in item.get("arquivos") or []:
            local = os.path.join(base, arq["local"])
            if not os.path.isfile(local):
                erros.append(f"arquivo de exemplo não encontrado: {arq['local']}")
                status("arquivo", f"s3://{bucket}/{arq['chave']}", "erro", "(arquivo local não existe)")
                continue
            s3.upload_file(local, bucket, arq["chave"])
            status("arquivo", f"s3://{bucket}/{arq['chave']}", "enviado")
            init.append(f"awslocal s3 cp <caminho>/{os.path.basename(local)} s3://{bucket}/{arq['chave']}")
        # verificação
        chaves = {o["Key"] for o in s3.list_objects_v2(Bucket=bucket).get("Contents", [])}
        for arq in item.get("arquivos") or []:
            if os.path.isfile(os.path.join(base, arq["local"])) and arq["chave"] not in chaves:
                erros.append(f"s3://{bucket}/{arq['chave']} não aparece no bucket")
    return erros


def resetar_s3(itens, s3):
    for item in itens:
        bucket = item["bucket"]
        if not bucket_existe(s3, bucket):
            continue
        for o in s3.list_objects_v2(Bucket=bucket).get("Contents", []):
            s3.delete_object(Bucket=bucket, Key=o["Key"])
        s3.delete_bucket(Bucket=bucket)
        status("bucket", bucket, "removido")


# ---------- main ----------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("infra_yaml")
    p.add_argument("--reset", action="store_true", help="remove o que o infra.yaml descreve")
    p.add_argument("--incluir-topico", action="store_true", help="no reset, remove também o tópico")
    a = p.parse_args()
    with open(a.infra_yaml, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    base = os.path.dirname(os.path.abspath(a.infra_yaml))
    itens_s3 = cfg.get("s3") or []
    if not cfg.get("fila") and not itens_s3:
        sys.exit("[ERRO] infra.yaml sem 'fila' e sem 's3': nada para criar.")
    if cfg.get("topico") and not cfg.get("fila"):
        sys.exit("[ERRO] 'topico' sem 'fila' no infra.yaml.")

    sns, sqs, s3, regiao = clientes()
    print("RECURSOS")

    if a.reset:
        if cfg.get("fila"):
            resetar_mensageria(cfg, sns, sqs, a.incluir_topico)
        resetar_s3(itens_s3, s3)
        sys.exit(0)

    init, erros = [], []
    if cfg.get("fila"):
        erros += criar_mensageria(cfg, sns, sqs, regiao, init)
    if itens_s3:
        erros += criar_s3(itens_s3, s3, regiao, base, init)

    nao_suportado = cfg.get("nao_suportado") or []
    if nao_suportado:
        print("\nNÃO SUPORTADO (nada foi criado para estes itens; decisão do humano):")
        for item in nao_suportado:
            print(f"  - {item}")

    print("\nVERIFICAÇÃO")
    for e in erros:
        print(f"  FALHOU  {e}")
    print("  OK" if not erros else "  Verifique os itens acima.")

    print("\nPARA O SCRIPT DE INIT (se o repo tiver um):")
    for linha in init:
        print(linha)
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()

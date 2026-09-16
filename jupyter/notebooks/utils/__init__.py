"""
utils — conexões pré-configuradas para o laboratório de Data Lakehouse.

Este é o código-fonte real do pacote, exposto de propósito dentro de
`notebooks/` (em vez de instalado "escondido" em outro lugar da imagem):
o aluno pode abrir, ler e editar `utils/__init__.py` no próprio
JupyterLab — mudou algo aqui, é só rodar de novo a célula com o
`import` (ou reiniciar o kernel) para pegar a mudança.

Uso básico:

    import utils as lh

    lh.list_layer("bronze")                                  # lista arquivos da camada
    lh.read_table("bronze", "customers")                      # -> DataFrame do pandas
    lh.s3()                                                    # cliente boto3 pronto
    lh.s3_storage_options()                                    # dict p/ pandas.to_parquet(..., storage_options=...)
    lh.bucket()                                                # nome do bucket do lakehouse
    lh.bronze_path("customers")                                # s3://lakehouse/bronze/customers/customers.parquet
    lh.silver_path("sales")                                    # idem, camada silver
    lh.gold_path("sales_by_day")                               # idem, camada gold

O par que fecha o ciclo — construir uma camada da arquitetura medalhão
"na mão":

    df = pd.read_csv(...)  # ou uma API, outra tabela via lh.read_table(...)
    lh.write_table(df, "bronze", "minha_tabela")   # grava Parquet no MinIO
    lh.read_table("bronze", "minha_tabela")        # já funciona
    lh.drop_table("bronze", "minha_tabela")        # desfaz (apaga os arquivos)

Não é preciso configurar host, porta, usuário ou senha de nada — tudo
já vem das variáveis de ambiente definidas no docker-compose.
"""
import os
from decimal import Decimal

import boto3
import pandas as pd

_S3_ENDPOINT = os.environ.get("LAKEHOUSE_S3_ENDPOINT", "http://minio:9000")
_S3_ACCESS_KEY = os.environ.get("LAKEHOUSE_S3_ACCESS_KEY", "trilha")
_S3_SECRET_KEY = os.environ.get("LAKEHOUSE_S3_SECRET_KEY", "trilha123")
_S3_BUCKET = os.environ.get("LAKEHOUSE_S3_BUCKET", "lakehouse")

BRONZE = "bronze"
SILVER = "silver"
GOLD = "gold"


def s3():
    """Cliente boto3 já apontado para o MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=_S3_ENDPOINT,
        aws_access_key_id=_S3_ACCESS_KEY,
        aws_secret_access_key=_S3_SECRET_KEY,
    )


def s3_storage_options() -> dict:
    """Dict pronto para `DataFrame.to_parquet(..., storage_options=...)` gravar no MinIO."""
    return {
        "key": _S3_ACCESS_KEY,
        "secret": _S3_SECRET_KEY,
        "client_kwargs": {"endpoint_url": _S3_ENDPOINT},
    }


def bucket() -> str:
    """Nome do bucket S3 usado pelo lakehouse."""
    return _S3_BUCKET


def list_layer(layer: str, prefix: str = "") -> list:
    """Lista os objetos de uma camada do lakehouse (bronze, silver ou gold)."""
    client = s3()
    resp = client.list_objects_v2(Bucket=_S3_BUCKET, Prefix=f"{layer}/{prefix}")
    return [obj["Key"] for obj in resp.get("Contents", [])]


def _layer_path(layer: str, tabela: str = "") -> str:
    if not tabela:
        return f"s3://{_S3_BUCKET}/{layer}/"
    return f"s3://{_S3_BUCKET}/{layer}/{tabela}/{tabela}.parquet"


def bronze_path(tabela: str = "") -> str:
    """Caminho s3:// pronto pra gravar/ler um Parquet na camada bronze.

    Sem argumento, devolve só o prefixo da camada. Com o nome de uma
    tabela, devolve o caminho completo do arquivo:
    `s3://<bucket>/bronze/<tabela>/<tabela>.parquet`.
    """
    return _layer_path(BRONZE, tabela)


def silver_path(tabela: str = "") -> str:
    """Equivalente a `bronze_path`, para a camada silver."""
    return _layer_path(SILVER, tabela)


def gold_path(tabela: str = "") -> str:
    """Equivalente a `bronze_path`, para a camada gold."""
    return _layer_path(GOLD, tabela)


def read_table(layer: str, tabela: str) -> pd.DataFrame:
    """Lê o Parquet de uma tabela direto do MinIO com pandas.

    Não existe "cadastro" nenhum: se o arquivo
    `s3://<bucket>/<layer>/<tabela>/<tabela>.parquet` existir, ele lê;
    senão, dá o erro normal do pandas/pyarrow de arquivo não encontrado.
    """
    return pd.read_parquet(_layer_path(layer, tabela), storage_options=s3_storage_options())


def write_table(df: pd.DataFrame, layer: str, tabela: str) -> None:
    """Grava um DataFrame como Parquet numa camada do lakehouse (MinIO) —
    pronto pra `lh.read_table(...)` logo em seguida.

    É assim que se constrói uma camada da arquitetura medalhão "na mão":
    lê de uma origem qualquer (um CSV, uma API, outra tabela via
    `lh.read_table(...)`...), transforma com pandas à vontade (filtro,
    `merge`, `groupby`...), e chama:

        lh.write_table(df, "bronze", "minha_tabela")

    `layer` normalmente é "bronze", "silver" ou "gold", mas pode ser
    qualquer nome — vira o prefixo `s3://<bucket>/<layer>/` no MinIO
    (criado automaticamente se ainda não existir, já que S3/MinIO não
    tem pasta de verdade, só chaves com `/`).

    Sempre sobrescreve por completo o arquivo, mesmo se a tabela já
    existir de uma chamada anterior — então rodar de novo depois de
    mudar o DataFrame nunca dá erro de "tabela já existe" (idempotente).

    Colunas com valores `Decimal` (pode acontecer lendo de algumas fontes
    externas) são convertidas pra float automaticamente — o Parquet não
    lida bem com o tipo Decimal do pandas.
    """
    df = df.copy()
    for coluna in df.columns:
        if df[coluna].map(type).eq(Decimal).any():
            df[coluna] = df[coluna].astype(float)

    destino = _layer_path(layer, tabela)
    df.to_parquet(destino, storage_options=s3_storage_options(), index=False)


def drop_table(layer: str, tabela: str) -> None:
    """Desfaz um `write_table`: apaga os arquivos Parquet dela no MinIO.

    Sem catálogo pra atualizar — é só apagar os objetos do prefixo
    `<layer>/<tabela>/` no bucket.
    """
    client = s3()
    prefix = f"{layer}/{tabela}/"
    resp = client.list_objects_v2(Bucket=_S3_BUCKET, Prefix=prefix)
    for obj in resp.get("Contents", []):
        client.delete_object(Bucket=_S3_BUCKET, Key=obj["Key"])

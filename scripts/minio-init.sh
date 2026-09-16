#!/bin/sh
# Cria o bucket do lakehouse e um marcador em cada pasta (bronze,
# silver, gold) para elas já aparecerem no console do MinIO assim que
# o ambiente sobe — todas nascem VAZIAS: não tem pipeline nenhum
# rodando sozinho neste projeto, então nada escreve em nenhuma camada
# automaticamente.
#
# Tudo que existir em bronze/silver/gold é o que o aluno
# construiu numa célula do único notebook deste projeto — ver
# `jupyter/notebooks/investigacao.ipynb`.
#
# Sem catálogo SQL nenhum neste projeto — bronze/silver/gold são só
# prefixos de pastas com Parquet, criados sozinhos por
# `df.to_parquet(...)` (pandas) na primeira vez que alguém escreve
# ali; não precisam existir de antemão.
set -e

mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
mc mb -p "local/$MINIO_BUCKET"

echo "camada criada pelo laboratório" > /tmp/.keep
for pasta in bronze silver gold; do
  mc cp /tmp/.keep "local/$MINIO_BUCKET/$pasta/.keep"
done

echo "MinIO inicializado: bucket '$MINIO_BUCKET' com bronze/silver/gold."

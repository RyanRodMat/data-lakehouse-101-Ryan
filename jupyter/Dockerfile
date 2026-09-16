# Pinada pelo digest (não por tag): essa imagem não publica uma tag de
# versão legível, então o digest é a única forma confiável de garantir
# que o build de hoje não muda sozinho no futuro.
FROM jupyter/scipy-notebook@sha256:fca4bcc9cbd49d9a15e0e4df6c666adf17776c950da9fa94a4f0a045d5c4ad33

USER root
RUN pip install --no-cache-dir \
    boto3==1.34.131 \
    s3fs==2024.6.1 \
    pyarrow==16.1.0

# Sem pacote nenhum pré-instalado além dessas libs — o notebook conecta
# no MinIO direto via pandas + `s3fs` (URIs `s3://...` com
# `storage_options`), sem nenhum código-fonte pra montar/editar. `boto3`
# fica disponível à parte, útil pra quem quiser inspecionar o bucket
# via `boto3.client("s3")` numa célula avulsa (ver README,
# Troubleshooting).

# A imagem base (jupyter/scipy-notebook) já vem com uma pasta "work"
# em /home/jovyan, pensada pra quem não monta um volume próprio. Este
# projeto sempre monta ./jupyter/notebooks ali, então "work" nunca é
# usada — só aparece vazia no explorador de arquivos, confundindo o
# aluno. Removida de propósito para não existir quando o ambiente sobe.
RUN rm -rf /home/jovyan/work

USER jovyan

# Laboratório de Data Lakehouse

Ambiente completo e pré-conectado para a aula prática de engenharia de dados.
O aluno não precisa entender Docker — só rodar um comando e abrir o Jupyter.

Só armazenamento (MinIO) e Python (Jupyter) — sem motor de SQL nenhum (sem Trino, ver "Por que não tem mais Trino" abaixo), sem orquestrador, e sem Postgres (ver "Por que não tem mais Postgres" abaixo). Não tem pipeline nenhum rodando sozinho: `bronze`, `silver` e `gold` nascem todas **vazias** assim que o ambiente sobe (ver "Por que não tem mais um pipeline automático" abaixo) — tudo que existir nelas é o que o aluno construiu numa célula de notebook, com pandas puro. Um único notebook, `jupyter/notebooks/investigacao.ipynb`, guia o aluno do início ao fim: ler os CSVs crus de `dados/` (ao lado do notebook), publicar como bronze, investigar livremente, e publicar a resposta final na silver.

## Instalando o Docker (Windows/Mac)

Tudo neste laboratório roda dentro de containers Docker — é a única coisa que precisa estar instalada na sua máquina.

**Windows:**
1. Baixe o **Docker Desktop** em [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) e rode o instalador.
2. O instalador pode pedir pra habilitar o **WSL2** (Windows Subsystem for Linux) — aceite, é um requisito do Docker Desktop no Windows. Se pedir reiniciar o computador, reinicie.
3. Depois de instalado, abra o **Docker Desktop** pelo menu Iniciar e espere o ícone da baleia (na bandeja do sistema, perto do relógio) ficar estável — é o sinal de que o Docker está rodando. Deixe o Docker Desktop aberto em segundo plano.

**Mac:**
1. Baixe o **Docker Desktop** em [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) — escolha a versão certa pro seu processador (Apple Silicon/M1-M2-M3 ou Intel; se não souber qual é o seu, veja no menu Apple (canto superior esquerdo) → "Sobre Este Mac").
2. Abra o `.dmg` baixado e arraste o Docker pra pasta Aplicativos.
3. Abra o **Docker.app** (Launchpad ou Spotlight) e espere o ícone da baleia aparecer estável na barra de menu (topo da tela) — é o sinal de que o Docker está rodando. Deixe o Docker Desktop aberto em segundo plano.

Com o Docker Desktop rodando (baleia estável na bandeja/barra de menu), abra um terminal (PowerShell no Windows, Terminal no Mac) na pasta deste projeto e siga o "Como subir" abaixo. **A tarefa em si é feita inteiramente dentro do Jupyter** (http://localhost:8888, aberto depois do `docker compose up`) — abra `investigacao.ipynb` lá e siga o notebook do início ao fim.

## Como subir

```bash
docker compose up -d --build
```

Primeira subida demora alguns minutos (baixa as imagens e builda o Jupyter). O comando só devolve o prompt depois que tudo isso termina — inclusive o Jupyter (`jupyter`) só sobe depois que o bucket e as pastas `bronze`/`silver`/`gold` já existem no MinIO, de propósito (ver `minio-init` no `docker-compose.yml`). Depois disso, tudo fica de pé até você rodar `docker compose down`.

## URLs e credenciais (tudo já vem pronto, ver `.env`)

Nenhum serviço pede credencial do aluno, com **uma única exceção**: o MinIO Console. É uma limitação do próprio MinIO, não deste projeto — o Console web dele sempre exige login, não existe modo anônimo pra essa UI (só dá pra desligar a UI inteira, o que tiraria o efeito visual de ver os arquivos aparecendo em `bronze/`/`silver`/`gold` — ver seção "Arquitetura" abaixo pra essa troca). O Jupyter abre direto, sem tela de login nenhuma.

| Serviço | URL | Usuário / senha |
|---|---|---|
| Jupyter | http://localhost:8888 | **nenhuma** — abre direto em `/lab` |
| MinIO Console | http://localhost:9001 | `trilha` / `trilha123` *(única exceção — ver acima)* |

> Como Jupyter e MinIO Console ficam sem exigir (ou quase sem exigir) login, **não exponha as portas deste projeto além da sua própria máquina** (ex: não coloque atrás de um proxy público, não abra as portas no firewall pra internet). Pra uma sala de aula local isso é seguro; pra qualquer coisa acessível de fora, não é.

## Roteiro sugerido para a aula

Um único notebook, `investigacao.ipynb` — "Mistério em João Pessoa" — cobre tudo: a demo em aula e a tarefa de casa são o mesmo arquivo, só em pontos diferentes.

1. Suba o ambiente antes da aula começar (`docker compose up -d --build`) — assim o tempo de download/build não consome tempo de aula. Quando o comando devolver o prompt, o bucket `lakehouse` já existe, com `bronze`/`silver`/`gold` vazias.
2. Abra o **MinIO Console** (http://localhost:9001) e mostre as pastas do bucket `lakehouse`, todas vazias — é a fonte de tudo neste laboratório: arquivo que chega de fora, não um banco relacional vivo, e nada é construído sem alguém rodar uma célula.
3. Abra `investigacao.ipynb` (http://localhost:8888) e apresente a história e o que se espera do aluno (introdução do notebook). Rode ao vivo o exemplo pronto da Fase 1 (`ocorrencia.csv` → bronze) e a ilustração de como ler de volta com `pd.read_parquet(...)` — isso já cobre o padrão pandas + MinIO que o aluno vai usar no resto da tarefa.
4. Pra mostrar o "aha" visual: abra o **MinIO Console** numa aba ao lado do Jupyter enquanto roda essas células — os arquivos vão aparecendo em `bronze` em tempo real.
5. Deixe as Fases 2 e 3 (investigação livre e resposta final na silver) como tarefa de casa — sem spoiler aqui de propósito, o enunciado completo está no próprio notebook.

## Tarefa de casa

O aluno termina `investigacao.ipynb` em casa: publica as outras 5 tabelas como bronze (mesmo padrão do exemplo visto em aula), investiga livremente com pandas (`pd.read_parquet` + `merge`/filtros) até achar 1 suspeito, e publica a conclusão como `silver.resposta_caso`.

Dá pra resolver inteira só com **pandas + MinIO + Jupyter** (`pd.read_csv`/`DataFrame.to_parquet`/`pd.read_parquet`, todos apontando pro MinIO via `storage_options`) — não tem SQL em lugar nenhum deste projeto. O entregável final é a tabela `silver.resposta_caso` (`s3://lakehouse/silver/resposta_caso.parquet`), que dá pra conferir com `pd.read_parquet(...)` ou direto pelo MinIO Console. O gabarito (resposta esperada e caminho de solução) fica em `tarefa-instrutor/GABARITO.md`, fora de `jupyter/notebooks/` — o aluno nunca vê essa pasta.

## Arquitetura

```
MinIO (armazenamento S3, bucket "lakehouse")
        │
        ▼
minio-init roda uma vez sozinho:
  cria o bucket e bronze/silver/gold vazias
        │
        ▼
Jupyter (pandas + s3fs: lê e escreve direto no MinIO)
  único lugar onde qualquer dado é construído — célula a célula,
  em pandas, pelo notebook investigacao.ipynb
```

- **MinIO**: armazenamento S3-compatível. As camadas bronze/silver/gold são pastas dentro de um único bucket `lakehouse`. É a única peça de armazenamento/estado deste laboratório.
- **minio-init**: roda uma vez, sozinho, assim que o MinIO fica pronto — cria o bucket `lakehouse` e um marcador vazio em cada uma das 3 pastas (`bronze`/`silver`/`gold`), só pra elas já aparecerem no Console. Não constrói nenhum dado; é só estrutura. Não aparece na aula (é só infraestrutura).
- **Jupyter**: onde a aula explora e constrói tudo, e onde mora a tarefa de casa — o único lugar deste projeto onde algum dado é efetivamente criado. Sem pacote nenhum pré-instalado: a primeira célula do notebook monta um dict `STORAGE_OPTIONS` (endpoint/chaves do MinIO, lidos das variáveis de ambiente) e a partir daí é só pandas puro — `pd.read_csv(...)`, `df.to_parquet(..., storage_options=STORAGE_OPTIONS)`, `pd.read_parquet(..., storage_options=STORAGE_OPTIONS)`, ver "Lendo e escrevendo camadas com pandas" abaixo. Um único notebook:
  - `investigacao.ipynb` — a demo de aula e a tarefa de casa, no mesmo arquivo (ver "Roteiro sugerido para a aula" acima). Fica direto em `jupyter/notebooks/`, ao lado de `dados/` (os 6 CSVs crus que ele lê).

### Por que não tem mais Postgres

Uma versão anterior deste projeto tinha um Postgres com dupla função: (1) simular um sistema transacional (uma "lojinha") como fonte dos dados, e (2) guardar os metadados de um Hive Metastore usado pelo Trino que existia então (ver "Por que não tem mais Trino" abaixo — os dois foram removidos juntos).

Os dois papéis saíram:

- **Metastore**: não existe mais catálogo SQL nenhum neste projeto (ver seção seguinte), então também não existe mais metastore pra guardar.
- **Fonte "lojinha"**: em vez de simular um sistema transacional vivo, todo dado deste laboratório entra pela mesma porta — um arquivo cru lido direto do disco (os 6 CSVs de `dados/`, da tarefa "Mistério em João Pessoa" — dados originais do [SQL Murder Mystery](https://github.com/NUKnightLab/sql-mysteries), com a cidade/nomes localizados, ver "Créditos" abaixo). Isso simplifica o laboratório: só existe um jeito de dado entrar, não dois.

Se um dia quiser trazer de volta uma fonte relacional "ao vivo" (por exemplo, pra mostrar extração via JDBC de um sistema transacional de verdade), o caminho é adicionar um serviço de banco no `docker-compose.yml` e ler dele com `pandas.read_sql(...)` (via `sqlalchemy`/`psycopg2`) dentro de um notebook — sem precisar de nenhum motor de SQL adicional pra isso, já que quem lê seria o próprio pandas.

### Por que não tem mais Trino (nem DBeaver-web)

Uma versão anterior deste projeto tinha o Trino como motor de consulta SQL (com metastore em arquivo, direto no MinIO) e o DBeaver-web (CloudBeaver) como cliente SQL web pra inspecioná-lo — a ideia era os alunos também aprenderem a consultar o lakehouse por SQL, além de pandas.

Removidos os dois porque, na prática, a aula nunca chegava nessa parte a tempo — o tempo disponível já era todo consumido por MinIO, JupyterLab e a mecânica de Parquet/bronze/silver/gold. Manter Trino e DBeaver-web rodando (e documentados) sem serem efetivamente usados só adicionava complexidade — mais 2 serviços no `docker-compose.yml`, mais uma porta cada, mais uma seção de troubleshooting — sem ganho didático real pra turma. Resultado:

- **Sem motor de SQL**: toda leitura é `pd.read_parquet(...)`, e toda transformação (filtro, join, agregação) é pandas puro (`merge`, `groupby`, filtro booleano...) — sem `SELECT`/`CREATE TABLE`/`JOIN` em SQL em lugar nenhum do projeto.
- **Sem catálogo pra cadastrar**: gravar uma tabela é só `df.to_parquet(...)` — não existe `query(...)`/`run_sql(...)` nem cadastro de catálogo nenhum.
- **Sem DBeaver-web**: ele só existia pra consultar o Trino; sem Trino, não tinha mais função.
- **Sem "schema"/"catálogo"**: bronze/silver/gold continuam existindo, mas são só prefixos de pastas no MinIO (`s3://lakehouse/bronze/`, etc.), não schemas SQL — "tabela" aqui é sempre "1 arquivo Parquet".

Se um dia quiser reintroduzir um motor de consulta SQL (Trino, DuckDB, etc.) — por exemplo, numa "aula 2" depois que a mecânica de pandas/Parquet já estiver consolidada — dá pra adicionar de volta como um serviço novo no `docker-compose.yml`, apontando pro mesmo bucket MinIO; nada na estrutura de arquivos (bronze/silver/gold como Parquet) precisa mudar pra isso.

### Por que não tem mais um pipeline automático (`pipeline-init`)

Uma versão anterior deste projeto tinha um script (`pipeline/construir_pipeline.py`) que rodava sozinho, uma vez, assim que o ambiente subia — construindo uma bronze/silver/gold "demo" a partir de `ocorrencia.csv` (1 dos 6 arquivos da tarefa de casa), só pra já existir algo pronto quando o Jupyter abrisse.

Removido porque criava duas fontes de verdade concorrendo pela atenção do aluno: dado que "já estava lá" quando o Jupyter abria (construído por infraestrutura, sem ninguém rodar nada) e dado que o aluno constrói na hora, célula a célula. Isso também obrigava a explicar um serviço extra (`pipeline-init`) e um script que não fazia parte do fluxo pedagógico principal. Resultado, mais simples:

- **Tudo nasce vazio**: `bronze`, `silver` e `gold` começam sem nenhum arquivo (só a "pasta", criada pelo `minio-init` — ver `scripts/minio-init.sh`) assim que o ambiente sobe.
- **Uma única fonte de verdade**: qualquer Parquet que existir em bronze/silver/gold foi escrito por uma célula do notebook `investigacao.ipynb` — não tem "resultado oficial" pré-existente pra confundir com o que o aluno constrói.
- **Menos um serviço**: o `docker-compose.yml` não tem mais `pipeline-init` — só `minio`, `minio-init` e `jupyter`.

Se um dia quiser voltar a ter algo pronto de antemão (por exemplo, uma tabela de referência que os alunos só consultam, sem construir), o caminho é o mesmo de antes: um script Python + um serviço novo no `docker-compose.yml` que roda uma vez, com `depends_on: minio-init: condition: service_completed_successfully`.

### Por que o explorador de arquivos do Jupyter só mostra o notebook e os dados

De propósito, pra reduzir o que o aluno vê sem precisar entender: a pasta `work` que a imagem base (`jupyter/scipy-notebook`) sempre inclui em `/home/jovyan/work` é removida no `Dockerfile` (`RUN rm -rf /home/jovyan/work`) — este projeto sempre monta `./jupyter/notebooks` ali, então ela nunca é usada; só ficaria vazia, confundindo quem abre o JupyterLab pela primeira vez. E a raiz do explorador de arquivos é restrita a `/home/jovyan/notebooks` via `--ServerApp.root_dir=/home/jovyan/notebooks` no `command:` do serviço `jupyter` — isso restringe o que o Jupyter enxerga como "sistema de arquivos" a só a pasta `notebooks`, então nada mais em `/home/jovyan` (arquivos de configuração do próprio Jupyter, etc.) aparece na árvore.

Se um dia quiser voltar a ver tudo (por exemplo, pra debugar), tire o `--ServerApp.root_dir=...` do `command:` do serviço `jupyter` no `docker-compose.yml` e suba de novo (`docker compose up -d --build jupyter`).

### Lendo e escrevendo camadas com pandas

Sem pacote nenhum por trás — só pandas apontado pro MinIO via `storage_options` (a lib `s3fs`, já instalada na imagem, é quem faz a ponte). A primeira célula do notebook monta esse dict uma vez:

```python
BUCKET = os.environ.get("LAKEHOUSE_S3_BUCKET", "lakehouse")
STORAGE_OPTIONS = {
    "key": os.environ.get("LAKEHOUSE_S3_ACCESS_KEY", "trilha"),
    "secret": os.environ.get("LAKEHOUSE_S3_SECRET_KEY", "trilha123"),
    "client_kwargs": {"endpoint_url": os.environ.get("LAKEHOUSE_S3_ENDPOINT", "http://minio:9000")},
}
```

E daí em diante, cada tabela é **1 arquivo Parquet flat** por camada (`<layer>/<tabela>.parquet`, sem subpasta por tabela):

- `pd.read_parquet(f"s3://{BUCKET}/bronze/<tabela>.parquet", storage_options=STORAGE_OPTIONS)` — lê o Parquet **direto do MinIO** com pandas. Não existe cadastro/catálogo — se o arquivo existir, lê; senão, dá o erro normal do pandas/pyarrow.
- `df.to_parquet(f"s3://{BUCKET}/bronze/<tabela>.parquet", storage_options=STORAGE_OPTIONS, index=False)` — grava um DataFrame como Parquet no MinIO. Sempre sobrescreve por completo, então rodar de novo depois de mudar o DataFrame nunca dá erro de "tabela já existe".

Com isso, o ciclo completo da arquitetura medalhão fica ao alcance de uma célula: ler de qualquer origem (um CSV com `pd.read_csv(...)`, uma API, outra tabela via `pd.read_parquet(...)`...), transformar com pandas à vontade (`merge`, `groupby`, filtro...), e `df.to_parquet(f"s3://{BUCKET}/bronze/minha_tabela.parquet", storage_options=STORAGE_OPTIONS, index=False)`. O notebook `investigacao.ipynb` tem um exemplo completo desse ciclo logo na Fase 1 (com a tabela `ocorrencia`), incluindo uma ilustração rápida de como ler de volta. Pra ver o que já existe fisicamente numa camada, sem escrever código nenhum, é só olhar o **MinIO Console** (http://localhost:9001).

> Este ambiente é puro armazenamento de objetos + Parquet — sem catálogo SQL, sem ACID/time-travel, sem schema evolution. Isso foi uma escolha deliberada para manter o primeiro contato simples (ver "Por que não tem mais Trino" acima). Se quiser evoluir para uma "aula 2" sobre consulta SQL e lakehouse "de verdade" (Trino/DuckDB, Apache Iceberg, schema evolution, time travel), o caminho é reintroduzir um motor de consulta como serviço novo, apontando pro mesmo bucket MinIO.

## Resetar o ambiente

```bash
docker compose down -v   # -v também apaga os dados do MinIO
docker compose up -d --build
```

## Créditos

O caso de `investigacao.ipynb` ("Mistério em João Pessoa") usa os dados originais do [**SQL Murder Mystery**](https://github.com/NUKnightLab/sql-mysteries), criado por Joon Park e Cathy He na Northwestern University Knight Lab — mesmas tabelas, mesmas pistas, mesma solução. O conteúdo original (texto, dados) é distribuído sob [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); aqui ele foi reempacotado nos 6 CSVs de `dados/`, adaptado pra ser resolvido com pandas + MinIO em vez de SQL, e localizado — a cidade (SQL City → João Pessoa), as ruas e os nomes das pessoas envolvidas na solução viraram referências brasileiras/regionais, mas os depoimentos (`depoimento.csv`) e o restante dos dados seguem originais, em inglês. Se você reusar/redistribuir este laboratório, mantenha esse crédito.

## Status

A versão anterior deste ambiente (com Postgres, Trino, Hive Metastore, DBeaver-web, uma "lojinha" simulada como fonte, um pipeline automático construindo uma bronze/silver/gold demo, e um segundo notebook exploratório separado da tarefa) foi validada em 08/2026 de ponta a ponta. Em 09/2026, a arquitetura mudou pra remover Postgres, Trino + DBeaver-web, o pipeline automático (`pipeline-init`), o passo de `landing`, o pacote `utils` (só pandas puro + `storage_options` daqui em diante), e por fim o segundo notebook — ver as seções "Por que não tem mais..." acima — o projeto ficou reduzido a **MinIO + Jupyter + pandas**, sem motor de SQL nenhum e sem nada rodando sozinho: bronze/silver/gold nascem vazias, e um único notebook (`investigacao.ipynb`, ao lado de `dados/`) constrói tudo lendo os CSVs direto do disco e publicando direto na bronze, cada tabela como 1 arquivo Parquet flat (`<layer>/<tabela>.parquet`). Também nessa data, o caso fictício foi trocado pelos dados originais do [SQL Murder Mystery](https://github.com/NUKnightLab/sql-mysteries) (ver "Créditos" acima) — mesma estrutura de 6 tabelas, agora com o dataset real (tabelas bem maiores, ~10 mil pessoas). Essa mudança ainda **não foi revalidada de ponta a ponta rodando os containers de verdade** — antes de usar em aula, rode:

```bash
docker compose down -v
docker compose up -d --build
```

e confira:
- os 3 serviços (`minio`, `minio-init`, `jupyter`) sobem, e `minio-init` termina com exit code 0 (`docker compose ps minio-init` deve mostrar `Exited (0)`);
- o MinIO Console (http://localhost:9001) mostra `lakehouse/bronze/`, `/silver/`, `/gold/` já visíveis (todas vazias, só o marcador) assim que o `docker compose up` devolve o prompt;
- o JupyterLab (http://localhost:8888) mostra `investigacao.ipynb` e a pasta `dados/` (com os 6 CSVs) direto na raiz do explorador de arquivos;
- `investigacao.ipynb` roda de ponta a ponta sem erro (vale confirmar o ciclo `pd.read_csv` -> `df.to_parquet` de ponta a ponta dentro do container de verdade, pras 6 tabelas da tarefa, e a escrita final em `silver.resposta_caso`).

Como as imagens continuam pinadas em versões exatas (nenhuma usa `:latest`) — `minio/minio:RELEASE.2025-09-07T16-13-09Z`, `minio/mc:RELEASE.2025-08-13T08-35-41Z`, e o Jupyter fixado pelo digest do `jupyter/scipy-notebook` no `Dockerfile` — o comportamento não deve mudar sozinho entre uma aula e outra, só se você editar essas versões de propósito.

## Troubleshooting

### `pd.to_parquet`/`pd.read_parquet` com `s3://` falha ("unknown protocol")

Sem pacote nenhum pra importar aqui — o que faz pandas entender URIs `s3://` é a lib `s3fs`, instalada na imagem (`jupyter/Dockerfile`). Se der erro de protocolo desconhecido, confira se o kernel foi reiniciado depois de qualquer mudança no `Dockerfile` (`docker compose up -d --build jupyter`) e se as variáveis de ambiente `LAKEHOUSE_S3_*` (ver `docker-compose.yml`, serviço `jupyter`) estão chegando no container — sem elas, `STORAGE_OPTIONS` cai nos valores padrão (`trilha`/`trilha123`/`http://minio:9000`), que só funcionam se o MinIO estiver de pé com essas mesmas credenciais (ver `.env`).

### O Jupyter (http://localhost:8888) pede token, ou quero um token de volta

Sem token/senha é o comportamento esperado (`command:` do serviço `jupyter` no `docker-compose.yml`, com `--ServerApp.token='' --ServerApp.password=''`). Se ainda assim pedir um token, o `docker compose up` provavelmente não recriou o container depois dessa mudança — rode `docker compose up -d --build jupyter`. Se preferir voltar a ter um token (por exemplo, se for expor a porta 8888 além da sua própria máquina — o que não é recomendado neste projeto, ver seção de URLs acima), edite o `command:` desse serviço pra `start-notebook.sh --ServerApp.token='SEU_TOKEN_AQUI'`.

### Por que o MinIO está pinado numa versão específica (`RELEASE.2025-09-07T16-13-09Z`) e sem Console de admin

Em 2025 a MinIO removeu as ações administrativas (apagar bucket, gerenciar usuários/políticas etc.) do Console web open-source, empurrando pra versão paga (AIStor). Esta imagem já é de depois dessa mudança, de propósito: o Console em http://localhost:9001 serve só pra *olhar* os arquivos (ótimo pra mostrar bronze/silver/gold enchendo em tempo real na aula), sem botões de administração que não fazem falta aqui — nenhuma célula dos notebooks depende deles, e o único caso de uso administrativo (criar o bucket e as pastas `bronze`/`silver`/`gold`) já roda sozinho, via `mc`, no serviço `minio-init`.

Se um dia essa tag específica sumir do Docker Hub — o repositório oficial `minio/minio` foi arquivado, então releases futuras não vêm mais dele — as opções são:

1. Usar essa mesma tag via um fork comunitário que espelha as releases (ex.: `pgsty/minio` no Docker Hub), trocando só o nome da imagem no `docker-compose.yml`.
2. Qualquer tag `RELEASE.*` já é suficiente — a API S3 (o que o projeto realmente usa) nunca muda de comportamento entre essas versões, só a UI do Console.
3. Ações administrativas ocasionais (apagar bucket, etc.) sempre dão pra fazer via `mc`, sem depender de UI nenhuma:
   ```bash
   docker run --rm --network data_lakehouse_101_default --entrypoint sh minio/mc:latest -c "
   mc alias set local http://minio:9000 trilha trilha123 &&
   mc rb --force local/NOME_DO_BUCKET
   "
   ```
   (troque `mc rb --force` por `mc rm --recursive --force` para só esvaziar sem apagar o bucket)
4. Também dá pra listar arquivos sem depender de UI nenhuma: `mc ls local/lakehouse/bronze/` (dentro do container `minio-init`/via `mc` configurado) ou um `boto3.client("s3").list_objects_v2(...)` avulso no Jupyter, se preferir Python.

### O `minio-init` falhou, ou bronze/silver/gold não existem

- Confira se `minio-init` terminou com sucesso: `docker compose ps minio-init` (deve mostrar `Exited (0)`) e `docker logs data_lakehouse_101-minio-init` pra ver o que rodou.
- Se `minio-init` está preso em "Created"/nunca inicia, o problema é upstream dele — confira se `minio` está `healthy` (`docker compose ps`).
- Como o `jupyter` só sobe depois que o `minio-init` termina com sucesso (`depends_on: minio-init: condition: service_completed_successfully`), se o Jupyter nunca fica acessível em http://localhost:8888, é provável que o `minio-init` tenha falhado — confira os logs dele antes de investigar o Jupyter.

### Quero recriar só um serviço (ex: depois de editar o Dockerfile do Jupyter)

```bash
docker compose up -d --build jupyter
```

Editar `investigacao.ipynb` (ou qualquer coisa em `jupyter/notebooks/`) **não** precisa de rebuild nenhum — é código-fonte montado via bind mount, não copiado pra imagem (ver `docker-compose.yml`, serviço `jupyter`). A mudança já vale na próxima vez que a célula rodar.

# Laboratório de Data Lakehouse

Ambiente Docker com MinIO + Jupyter pra praticar engenharia de dados (arquitetura medalhão — bronze/silver/gold) usando só **pandas**, sem SQL. **A tarefa inteira está dentro do notebook `investigacao.ipynb`** — este README só cobre como instalar e subir o ambiente.

## 1. Instalar o Docker

**Windows:**
1. Baixe o **Docker Desktop** em [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) e rode o instalador.
2. O instalador pode pedir pra habilitar o **WSL2** — aceite (é o caminho padrão e mais simples; no Windows Home é obrigatório, já que essa edição não suporta a alternativa via Hyper-V). Se pedir reiniciar, reinicie.
3. Abra o **Docker Desktop** pelo menu Iniciar e espere o ícone da baleia (bandeja do sistema) ficar estável. Deixe-o aberto em segundo plano.

**Mac:**
1. Baixe o **Docker Desktop** em [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) — escolha Apple Silicon ou Intel (veja em menu Apple → "Sobre Este Mac" se não souber).
2. Abra o `.dmg` e arraste o Docker pra pasta Aplicativos.
3. Abra o **Docker.app** e espere o ícone da baleia ficar estável na barra de menu. Deixe-o aberto em segundo plano.

## 2. Subir o ambiente

Com o Docker Desktop rodando, abra um terminal (PowerShell no Windows, Terminal no Mac) na pasta deste projeto:

```bash
docker compose up -d --build
```

Primeira subida demora alguns minutos (baixa as imagens e builda o Jupyter). Depois disso, tudo fica de pé até você rodar `docker compose down`.

## 3. Fazer a tarefa

Abra **http://localhost:8888** (Jupyter, sem login) e siga `investigacao.ipynb` do início ao fim — a introdução, os passos e o que entregar estão todos no próprio notebook.

Opcional: **http://localhost:9001** (MinIO Console, login `trilha`/`trilha123`) mostra os arquivos Parquet aparecendo em tempo real conforme você roda as células.

> Não exponha essas portas além da sua própria máquina (sem proxy público, sem firewall aberto pra internet) — nenhum dos dois serviços exige login de verdade.

## Resetar o ambiente

```bash
docker compose down -v   # -v também apaga os dados do MinIO
docker compose up -d --build
```

## Créditos

O caso de `investigacao.ipynb` ("Mistério em João Pessoa") é uma adaptação do [**SQL Murder Mystery**](https://github.com/NUKnightLab/sql-mysteries), criado por Joon Park e Cathy He na Northwestern University Knight Lab, sob [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

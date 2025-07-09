# 🧠 Câmara Insights

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-4169E1?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)

Um backend modular em Python para coletar, analisar, enriquecer com IA e servir dados públicos da API da Câmara dos Deputados do Brasil.

---

## 📖 Tabela de Conteúdos

- [Sobre o Projeto](#-sobre-o-projeto)
- [✨ Principais Funcionalidades](#-principais-funcionalidades)
- [🛠️ Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [🚀 Começando](#-começando)
  - [Pré-requisitos](#pré-requisitos)
  - [Instalação](#instalação)
- [⚙️ Uso](#-uso)
  - [1. Inicializar o Banco de Dados](#1-inicializar-o-banco-de-dados)
  - [2. Sincronizar Dados da API](#2-sincronizar-dados-da-api)
  - [3. Enriquecer Dados com IA](#3-enriquecer-dados-com-ia)
  - [4. Iniciar o Servidor da API](#4-iniciar-o-servidor-da-api)
- [📡 Endpoints da API](#-endpoints-da-api)
- [🔮 Próximos Passos](#-próximos-passos)

---

## 🏛️ Sobre o Projeto

O objetivo do **Câmara Insights** é criar uma fonte de dados centralizada e enriquecida sobre a atividade legislativa no Brasil.  
O sistema se conecta à [API de Dados Abertos da Câmara dos Deputados](https://dadosabertos.camara.leg.br/), coleta os dados, os armazena em um banco de dados relacional e utiliza Modelos de Linguagem Grandes (LLMs) para gerar insights, como resumos, tags e uma pontuação de impacto para as proposições.

Todos esses dados são expostos através de uma API RESTful rápida e moderna, construída com FastAPI.

---

## ✨ Principais Funcionalidades

- **Coleta de Dados Automatizada:** Scripts para sincronizar deputados, partidos, proposições, votações e mais.
- **Enriquecimento com IA:** Utiliza LLMs (via OpenRouter) para:
  - Gerar resumos concisos de proposições.
  - Classificar proposições por abrangência e magnitude.
  - Extrair tags temáticas relevantes.
  - Calcular um **Score de Impacto** ponderado.
- **API RESTful:** Endpoints com paginação, filtros e ordenação.
- **Agendamento de Tarefas:** Tarefas periódicas com `APScheduler`.
- **Arquitetura Robusta:** Lógica de retentativas e *rate limiting* dinâmico para lidar com limites da API externa.

---

## 🛠️ Tecnologias Utilizadas

| Área                  | Tecnologia                                   |
|-----------------------|----------------------------------------------|
| **Linguagem**         | Python 3.11+                                 |
| **Framework Web**     | FastAPI                                      |
| **ORM / Migrations**  | SQLAlchemy 2.0, Alembic                      |
| **Banco de Dados**    | SQLite (Dev), PostgreSQL (Prod)             |
| **Cliente HTTP**      | HTTPX                                        |
| **Agendamento**       | APScheduler                                  |
| **IA / LLMs**         | OpenRouter (DeepSeek)                        |
| **Testes**            | Pytest (Fase 6)                              |
| **Deployment**        | Docker, Docker Compose                       |

---

## 🚀 Começando

### Pré-requisitos

- Python 3.11 ou superior
- Pip (gerenciador de pacotes do Python)
- Chave de API do [OpenRouter](https://openrouter.ai/)

### Instalação

1. **Clone o repositório:**

```bash
git clone https://github.com/SEU_USUARIO/camara-insights.git
cd camara-insights
```

2. **Crie e ative um ambiente virtual (recomendado):**

```bash
# Windows (PowerShell)
python -m venv venv
.env\Scripts\Activate.ps1

# MacOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Configure suas variáveis de ambiente:**

Crie um arquivo `.env` na raiz do projeto com o conteúdo:

```env
DATABASE_URL="sqlite:///./camara_insights.db"
OPENROUTER_API_KEY="sk-or-v1-sua-chave-aqui"
```

---

## ⚙️ Uso

### 1. Inicializar o Banco de Dados

```bash
python ./scripts/create_database.py
```

### 2. Sincronizar Dados da API

```bash
# Tabelas de referência (tipos, status, etc.)
python ./scripts/sync_referencias.py

# Entidades principais (deputados, proposições desde 2023, etc.)
python ./scripts/sync_all.py
```

> ⚠️ Este processo pode demorar alguns minutos.

### 3. Enriquecer Dados com IA

```bash
python ./scripts/score_propositions.py
```

Esse script processa todas as proposições ainda não analisadas e para automaticamente ao final.

### 4. Iniciar o Servidor da API

```bash
uvicorn app.main:app --reload
```

Servidor disponível em: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📡 Endpoints da API

Acesse a documentação interativa (Swagger UI):

👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Exemplos:

- `GET /api/v1/deputados`
  - Filtros: `?sigla_uf=SP`, `?sigla_partido=PT`

- `GET /api/v1/proposicoes`
  - Filtros: `?ano=2024`, `?sigla_tipo=PL`
  - Ordenação: `?sort=ano:desc`

- `GET /api/v1/partidos`
- `GET /api/v1/orgaos`
- `GET /api/v1/eventos`
- `GET /api/v1/votacoes`

> Todos os endpoints suportam paginação: `?skip=0&limit=10`

---

## 🔮 Próximos Passos

- **Fase 6:** Testes automatizados com Pytest + formatadores de código.
- **Fase 8:** Dashboard com Streamlit ou frontend React.
- **Melhoria dos Filtros:** Filtros por tema, autor, impacto, etc.
- **Endpoints Detalhados:** Ex: `GET /deputados/{id}` com dados completos relacionados.

---

🚧 Projeto em desenvolvimento contínuo. Contribuições são bem-vindas!

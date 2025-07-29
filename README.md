# 🧠 Câmara Insights

![Next.js](https://img.shields.io/badge/Next.js-14+-000000?logo=nextdotjs)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)
![Material--UI](https://img.shields.io/badge/Material--UI-5+-0081CB?logo=mui)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)

O **Câmara Insights** é uma aplicação full-stack projetada para fornecer uma interface moderna, rica em dados e aprimorada por IA para explorar as atividades legislativas da Câmara dos Deputados do Brasil. Ele combina um backend poderoso em Python para coleta e análise de dados com um frontend elegante e responsivo em Next.js para visualização de dados e interação do usuário.

---

## 📖 Tabela de Conteúdos

- [Sobre o Projeto](#-sobre-o-projeto)
- [✨ Principais Funcionalidades](#-principais-funcionalidades)
- [🛠️ Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [🚀 Começando](#-começando)
  - [Pré-requisitos](#pré-requisitos)
  - [Instalação](#instalação)
- [⚙️ Uso](#-uso)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [📡 Endpoints da API](#-endpoints-da-api)
- [🔮 Próximos Passos](#-próximos-passos)

---

## 🏛️ Sobre o Projeto

O objetivo do **Câmara Insights** é criar uma fonte de dados centralizada e enriquecida sobre a atividade legislativa no Brasil. O sistema se conecta à [API de Dados Abertos da Câmara dos Deputados](https://dadosabertos.camara.leg.br/), coleta os dados, os armazena em um banco de dados relacional e utiliza Modelos de Linguagem Grandes (LLMs) para gerar insights, como resumos, tags e uma pontuação de impacto para as proposições.

Todos esses dados são expostos através de uma API RESTful rápida e moderna, construída com FastAPI, e consumidos por um frontend em Next.js que oferece uma rica experiência de usuário para explorar e entender os dados legislativos.

---

## ✨ Principais Funcionalidades

### Backend
- **Coleta de Dados Automatizada:** Scripts para sincronizar deputados, partidos, proposições, votações e mais.
- **Enriquecimento com IA:** Utiliza LLMs (via OpenRouter) para:
  - Gerar resumos concisos de proposições.
  - Classificar proposições por abrangência e magnitude.
  - Extrair tags temáticas relevantes.
  - Calcular um **Score de Impacto** ponderado.
- **API RESTful:** Endpoints com paginação, filtros e ordenação.
- **Agendamento de Tarefas:** Tarefas periódicas com `APScheduler`.
- **Arquitetura Robusta:** Lógica de retentativas e *rate limiting* dinâmico para lidar com limites da API externa.

### Frontend
- **UI Moderna:** Uma interface limpa e intuitiva construída com Next.js e Material UI.
- **Dashboards Interativos:** Visualizações de dados legislativos.
- **Visualizações Detalhadas:** Informações aprofundadas sobre deputados, proposições e partidos.
- **Design Responsivo:** Totalmente funcional em desktops e dispositivos móveis.
<img width="1918" height="944" alt="image" src="https://github.com/user-attachments/assets/80b9c992-b0a3-4f47-b7ce-eb1a25451075" />
<img width="1919" height="946" alt="image" src="https://github.com/user-attachments/assets/bf9a24b7-f0f4-4c74-b839-f01e1d2ed1d3" />
<img width="1920" height="947" alt="image" src="https://github.com/user-attachments/assets/1129a626-336d-4533-9cb0-8de6f0bb96f3" />
<img width="1920" height="2296" alt="image" src="https://github.com/user-attachments/assets/972baf23-01a6-4226-aea6-12a955adebcb" />



---

## 🛠️ Tecnologias Utilizadas

### Backend
| Área                 | Tecnologia                                   |
|----------------------|----------------------------------------------|
| **Linguagem**        | Python 3.11+                                 |
| **Framework Web**    | FastAPI                                      |
| **ORM / Migrations** | SQLAlchemy 2.0, Alembic                      |
| **Banco de Dados**   | SQLite (Dev), PostgreSQL (Prod)              |
| **Cliente HTTP**     | HTTPX                                        |
| **Agendamento**      | APScheduler                                  |
| **IA / LLMs**        | OpenRouter (DeepSeek)                        |
| **Testes**           | Pytest                                       |
| **Deployment**       | Docker, Docker Compose                       |

### Frontend
| Área                  | Tecnologia                                   |
|-----------------------|----------------------------------------------|
| **Framework**         | Next.js 14+                                  |
| **Linguagem**         | TypeScript                                   |
| **Biblioteca de UI**  | Material UI (MUI) 5+                         |
| **Gerenc. de Estado** | React Context API                            |
| **Estilização**       | Emotion                                      |
| **Busca de Dados**    | SWR / React Query (ou `fetch` nativo)        |
| **Linting / Formatação**| ESLint, Prettier                           |

---

## 🚀 Começando

### Pré-requisitos

- Python 3.11 ou superior
- Node.js e npm/pnpm/yarn
- Chave de API do [OpenRouter](https://openrouter.ai/)

### Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/camara-insights.git
   cd camara-insights
   ```

2. **Setup do Backend:**
   - Navegue para o diretório `backend`: `cd backend`
   - Crie e ative um ambiente virtual:
     ```bash
     # Windows (PowerShell)
     python -m venv venv
     . venv\Scripts\Activate.ps1

     # MacOS/Linux
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Instale as dependências: `pip install -r requirements.txt`
   - Crie um arquivo `.env` e adicione sua `DATABASE_URL` e `OPENROUTER_API_KEY`.

3. **Setup do Frontend:**
   - Navegue para o diretório `frontend`: `cd ../frontend`
   - Instale as dependências: `npm install` (ou `pnpm install` / `yarn install`)
   - Crie um arquivo `.env.local` se precisar sobrescrever configurações padrão (ex: o endpoint da API).

---

## ⚙️ Uso

### Backend

1. **Inicialize o Banco de Dados:**
   ```bash
   python ./scripts/create_database.py
   ```

2. **Sincronize os Dados da API:**
   ```bash
   # Tabelas de referência (tipos, status, etc.)
   python ./scripts/sync_referencias.py

   # Entidades principais (deputados, proposições desde 2023, etc.)
   python ./scripts/sync_all.py
   ```
   > ⚠️ Este processo pode demorar alguns minutos.

3. **Enriqueça os Dados com IA:**
   ```bash
   python ./scripts/score_propositions.py
   ```

4. **Inicie o Servidor da API:**
   ```bash
   uvicorn app.main:app --reload
   ```
   O servidor estará disponível em [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Frontend

1. **Inicie o Servidor de Desenvolvimento:**
   ```bash
   npm run dev
   ```
   A aplicação estará disponível em [http://localhost:3000](http://localhost:3000).

---

## 📡 Endpoints da API

Acesse a documentação interativa da API (Swagger UI):

👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Exemplos:
- `GET /api/v1/deputados`
- `GET /api/v1/proposicoes`
- `GET /api/v1/partidos`

> Todos os endpoints suportam paginação: `?skip=0&limit=10`

---

## 🔮 Próximos Passos

- **Testes Automatizados:** Aumentar a cobertura de testes para backend e frontend.
- **CI/CD:** Implementar pipelines de integração e deployment contínuos.
- **Filtros Avançados:** Adicionar opções de filtro mais complexas no frontend.
- **Autenticação de Usuários:** Proteger partes da aplicação com contas de usuário.

---

🚧 Projeto em desenvolvimento contínuo. Contribuições são bem-vindas!

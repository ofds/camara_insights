### 📄 Documentação da Arquitetura do Backend - Câmara Insights

#### 1. Visão Geral e Filosofia da Arquitetura

O backend do **Câmara Insights** foi re-arquitetado para seguir uma abordagem mais robusta, modular e orientada a dados, com base nos princípios de **Arquitetura Limpa (Clean Architecture)** e no padrão de projeto **Repository**. O objetivo é criar um sistema flexível, testável e de fácil manutenção, onde a lógica de negócio é desacoplada dos detalhes de infraestrutura.

A filosofia central é a **Inversão de Dependência**, onde as camadas de serviço de alto nível não dependem diretamente das camadas de acesso a dados de baixo nível, mas sim de abstrações.

#### 2. Diagrama de Componentes e Fluxo de Dados

A nova arquitetura pode ser visualizada através dos seguintes componentes principais e suas interações:

```
+-----------------+      +-----------------------+      +-----------------+
|   Cliente da    |----->|   API Layer (FastAPI) |----->|  Service Layer  |
|   API (Ex: UI)  |<-----|   (app/api, app/main) |<-----| (src/services)  |
+-----------------+      +-----------+-----------+      +--------+--------+
                                     |                           |
                                     v                           v
+------------------------+      +------------------------------------------+
| Orchestrator (Prefect) |----->|     Data Sync & Business Logic           |
| (src/services/orchestrator)|  | (src/services/data_sync_service)         |
+------------------------+      +---------------------+--------------------+
                                                      |
         +--------------------------------------------+---------------------------------------------+
         |                                                                                          |
         v                                                                                          v
+--------+----------+                                                                        +------+----------+
| Repository Layer  |                                                                        | External APIs   |
| (src/data/repository)|                                                                        | (Câmara, LLM)   |
+--------+----------+                                                                        +--------+--------+
         |
         v
+--------+----------+
|   Database (SQL)  |
| (app/infra/db)    |
+-------------------+
```

#### 3. Estrutura de Diretórios

A organização do projeto reflete a nova arquitetura:

```
camara_insights/
├── app/
│   ├── api/          # (1) Camada de API: Roteadores e endpoints FastAPI.
│   ├── core/         # (2) Núcleo da Aplicação: Configurações, agendador, etc.
│   ├── domain/       # (3) Camada de Domínio: Schemas Pydantic (contratos de dados).
│   ├── infra/        # (4) Camada de Infraestrutura: Clientes de API e configuração de BD.
│   └── main.py       # Ponto de entrada da aplicação FastAPI.
├── src/
│   ├── data/         # (5) Camada de Acesso a Dados (Repository Pattern).
│   │   └── repository.py
│   └── services/     # (6) Camada de Serviço: Lógica de negócio e orquestração.
│       ├── data_sync_service.py
│       └── orchestrator_service.py
├── scripts/          # (7) Scripts para tarefas manuais e de orquestração.
└── tests/            # Testes automatizados.
```

#### 4. Descrição das Camadas

1.  **Camada de API (`app/api`)**

    *   **Responsabilidade:** Expor os dados e funcionalidades da aplicação através de endpoints HTTP.
    *   **Tecnologias:** FastAPI.
    *   **Funcionamento:** Recebe requisições, valida os dados de entrada (usando a camada de Domínio) e delega a lógica para a Camada de Serviço.

2.  **Núcleo da Aplicação (`app/core`)**

    *   **Responsabilidade:** Gerenciar configurações globais e processos de fundo, como o agendador de tarefas.
    *   **Tecnologias:** APScheduler.

3.  **Camada de Domínio (`app/domain`)**

    *   **Responsabilidade:** Definir os "contratos" de dados da aplicação.
    *   **Tecnologias:** Pydantic.
    *   **Funcionamento:** Garante a consistência e validação dos dados que fluem através da API.

4.  **Camada de Infraestrutura (`app/infra`)**

    *   **Responsabilidade:** Lidar com a comunicação com tecnologias externas.
    *   **Componentes:**
        *   `db`: Configuração da sessão e modelos do SQLAlchemy.
        *   `camara_api.py`, `llm_client.py`: Clientes para as APIs externas.

5.  **Camada de Acesso a Dados (`src/data`)**

    *   **Responsabilidade:** Abstrair as operações de banco de dados.
    *   **Tecnologias:** SQLAlchemy.
    *   **Funcionamento:** Implementa o **Repository Pattern**. O `BaseRepository` fornece operações CRUD genéricas, enquanto repositórios específicos (ex: `ProposicaoRepository`) contêm lógicas de consulta mais complexas.

6.  **Camada de Serviço (`src/services`)**

    *   **Responsabilidade:** Orquestrar a lógica de negócio da aplicação.
    *   **Componentes:**
        *   `data_sync_service.py`: Contém a lógica para sincronizar os dados da API da Câmara, tratando de paginação, concorrência e transformação de dados.
        *   `orchestrator_service.py`: Um orquestrador de tarefas data-driven que utiliza o **Prefect** para criar e executar fluxos de ETL de forma dinâmica.

7.  **Scripts (`scripts`)**

    *   **Responsabilidade:** Fornecer uma interface de linha de comando (CLI) para executar tarefas de desenvolvimento, manutenção e orquestração.
    *   **Funcionamento:** Contém scripts para inicializar o banco de dados (`create_database.py`), executar fluxos de ETL (`orchestrate.py`), e realizar sincronizações de dados específicas (`sync_all.py`, `sync_authors_only.py`, etc.).

#### 5. Fluxos de Dados Principais

**Fluxo 1: Requisição de API do Usuário (`GET /proposicoes`)**

1.  A requisição chega ao roteador em `app/api/v1/proposicoes.py`.
2.  O roteador chama um método na Camada de Serviço (ex: `presentation_service.get_proposicoes`).
3.  O serviço utiliza o `ProposicaoRepository` para buscar os dados no banco de dados.
4.  O repositório executa a query SQLAlchemy e retorna os dados para o serviço.
5.  O serviço formata os dados e os retorna para a camada de API, que os serializa em JSON.

**Fluxo 2: Fluxo de ETL de Sincronização (Executado via Script)**

1.  Um desenvolvedor executa um script a partir da linha de comando (ex: `python -m scripts.orchestrate run-sync-flow`).
2.  O script invoca o `OrchestratorService` para executar um fluxo de ETL definido.
3.  O orquestrador, usando o **Prefect**, executa as tarefas na ordem correta, respeitando as dependências.
4.  Uma tarefa típica (ex: `sync_propositions`) chama o `DataSyncService`.
5.  O `DataSyncService` busca os dados da API da Câmara, os transforma e utiliza o `ProposicaoRepository` para fazer o "upsert" dos dados no banco.

```
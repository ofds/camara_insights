### 📄 Documentação da Arquitetura do Backend - Câmara Insights

#### 1\. Visão Geral e Filosofia da Arquitetura

O backend do **Câmara Insights** foi projetado com base em princípios de **Arquitetura Limpa (Clean Architecture)** e **Separação de Preocupações (Separation of Concerns)**. O objetivo é criar um sistema modular, testável e de fácil manutenção, onde cada componente tem uma responsabilidade única e bem definida.

A filosofia central é que a lógica de negócio e as regras da nossa aplicação não devem depender de detalhes externos como o banco de dados, o framework web ou APIs de terceiros. Isso é alcançado através de uma clara divisão em camadas.

#### 2\. Diagrama de Componentes e Fluxo de Dados

A arquitetura pode ser visualizada através dos seguintes componentes principais e suas interações:

```
+-----------------+      +-----------------------+      +-----------------+
|   Cliente da    |----->|   API Layer (FastAPI) |----->|  Camada de CRUD |
|   API (Ex: UI)  |<-----|   (app/api, app/domain) |<-----|  (app/infra/db) |
+-----------------+      +-----------+-----------+      +--------+--------+
                                     |                           |
                                     v                           v
+------------------------+      +------------------------------------------+
| Scheduler (APScheduler)|----->|     Camada de Serviço (Lógica de Negócio)    |
| (app/core/scheduler.py)|      | (app/services/scoring, app/services/automation)|
+------------------------+      +---------------------+--------------------+
                                                      |
         +--------------------------------------------+---------------------------------------------+
         |                                                                                          |
         v                                                                                          v
+--------+----------+                                                                        +------+----------+
| Cliente de API    |                                                                        | Cliente de API  |
| (app/infra/camara)|                                                                        | (app/infra/llm) |
+--------+----------+                                                                        +--------+--------+
         |                                                                                          |
         v                                                                                          v
+--------+----------+                                                                        +------+----------+
|  API Externa da   |                                                                        |  API Externa do |
|      Câmara       |                                                                        |   OpenRouter    |
+-------------------+                                                                        +-----------------+

```

#### 3\. Estrutura de Diretórios

A organização do projeto reflete diretamente a separação em camadas:

```
camara_insights/
├── app/
│   ├── api/          # (1) Camada de API: Roteadores e endpoints FastAPI.
│   ├── domain/       # (2) Camada de Domínio: Schemas Pydantic (contratos de dados).
│   ├── services/     # (3) Camada de Serviço: Orquestra a lógica de negócio.
│   ├── infra/        # (4) Camada de Infraestrutura: Comunicação com o mundo externo.
│   │   ├── camara_api.py # Cliente para a API da Câmara.
│   │   ├── llm_client.py   # Cliente para a API do LLM.
│   │   └── db/           # Módulos do banco de dados (Sessão, CRUD, Modelos).
│   ├── core/         # (5) Núcleo da Aplicação: Configurações, agendador, etc.
│   └── main.py       # Ponto de entrada da aplicação FastAPI.
├── scripts/          # Scripts para tarefas manuais (sincronização, análise, etc.).
├── prompts/          # Arquivos de texto com os prompts para o LLM.
└── tests/            # Testes automatizados.
```

#### 4\. Descrição das Camadas

1.  **Camada de API (`app/api`)**

      * **Responsabilidade:** Receber requisições HTTP, validar os dados de entrada e formatar os dados de saída.
      * **Tecnologias:** FastAPI (Roteadores, `Query`, `Depends`).
      * **Funcionamento:** Cada entidade (deputados, proposições) tem seu próprio arquivo de roteador. Esta camada **não contém lógica de negócio**. Ela apenas delega a execução para a camada de CRUD e formata a resposta usando os schemas da camada de Domínio.

2.  **Camada de Domínio (`app/domain`)**

      * **Responsabilidade:** Definir a estrutura dos dados da nossa aplicação de forma agnóstica à tecnologia. São os "contratos" da API.
      * **Tecnologias:** Pydantic (`BaseModel`).
      * **Funcionamento:** Os schemas Pydantic (ex: `DeputadoSchema`) garantem que os dados retornados pela API sejam sempre consistentes e válidos. Eles são usados no `response_model` dos endpoints.

3.  **Camada de Serviço (`app/services`)**

      * **Responsabilidade:** Orquestrar as regras de negócio complexas que envolvem múltiplos passos.
      * **Funcionamento:** `scoring_service.py` contém a lógica para calcular o `impact_score`. `automation_service.py` contém a lógica para orquestrar as tarefas de sincronização e análise. Esta camada utiliza os clientes da camada de Infraestrutura e as funções da camada de CRUD.

4.  **Camada de Infraestrutura (`app/infra`)**

      * **Responsabilidade:** Lidar com todos os detalhes de comunicação com tecnologias externas.
      * **Componentes:**
          * **`db`**: Contém a "ponte" com o banco de dados.
              * `models`: Define a estrutura das tabelas (SQLAlchemy).
              * `crud`: Funções que executam as operações no banco (SELECT, INSERT, UPDATE).
              * `session`: Gerencia a conexão com o banco.
          * **`camara_api.py`, `llm_client.py`**: Classes que encapsulam a lógica de fazer chamadas HTTP para as APIs externas, tratando de autenticação, headers e retentativas.

5.  **Núcleo da Aplicação (`app/core`)**

      * **Responsabilidade:** Gerenciar configurações globais e processos que rodam em segundo plano.
      * **Componentes:**
          * `settings.py`: Carrega configurações de variáveis de ambiente e arquivos `.env`.
          * `scheduler.py`: Configura e inicia o agendador de tarefas `APScheduler`.
          * `rate_limiter.py`: Fornece a lógica para controle de fluxo de requisições.

#### 5\. Fluxos de Dados Principais

**Fluxo 1: Requisição de API do Usuário (`GET /proposicoes?ano=2024`)**

1.  A requisição HTTP chega ao `main.py` e é direcionada para o roteador em `app/api/v1/proposicoes.py`.
2.  A função `read_proposicoes` valida os parâmetros (`ano=2024`).
3.  Ela chama a função `crud.get_proposicoes(..., ano=2024)` em `app/infra/db/crud/entidades.py`.
4.  A função CRUD constrói uma query SQLAlchemy com um `.filter(Proposicao.ano == 2024)` e a executa no banco de dados.
5.  Uma lista de objetos `Proposicao` do SQLAlchemy é retornada para a API.
6.  O FastAPI usa o `ProposicaoSchema` (definido em `response_model`) para converter os objetos em JSON e os envia como resposta.

**Fluxo 2: Tarefa Agendada de Sincronização e Análise**

1.  O `APScheduler`, iniciado em `app/main.py`, dispara a tarefa `run_daily_update_task` no horário agendado.
2.  Esta função, em `app/services/automation_service.py`, primeiro chama `run_full_sync()`.
3.  `run_full_sync()` usa o `camara_api_client` para buscar novos dados da Câmara. Para cada item, ele chama `upsert_entidade` no CRUD para salvar no banco.
4.  Após a sincronização, `run_daily_update_task` chama `run_scoring_task()`.
5.  `run_scoring_task()` usa `crud.get_unscored_propositions()` para encontrar proposições novas.
6.  Ela então chama `analyze_and_score_propositions()` no `scoring_service.py`.
7.  O serviço de scoring usa o `llm_client` para enviar as proposições para a IA, calcula o score final e chama `upsert_entidade` (ou uma função similar) para salvar os resultados na tabela `proposicao_ai_data`.

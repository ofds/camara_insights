### 📖 Guia de Modificações e Extensões (Cookbook) do Câmara Insights

Este documento serve como um guia de referência para realizar as modificações mais comuns no projeto. A arquitetura foi pensada para ser modular, então a maioria das alterações segue um padrão claro.

---

### Cenário 1: Manipulando os Dados no Banco

#### **Como Adicionar um Novo Campo a uma Entidade Existente?**
*(Exemplo: Exibir o `cpf` do deputado, que já coletamos, na API)*

1.  **`app/domain/entidades.py`**: Adicione o campo ao Schema Pydantic correspondente.
    * No `DeputadoSchema`, adicione a linha: `cpf: Optional[str] = None`.

É só isso! Como o dado já está sendo salvo no banco, basta expô-lo no "contrato" da API. O FastAPI e o Pydantic cuidam do resto.

#### **Como Adicionar e Sincronizar uma Nova Entidade?**
*(Exemplo: Adicionar `Frentes Parlamentares`, que usam o endpoint `/frentes`)*

1.  **`app/infra/db/models/entidades.py`**: Crie a nova classe de modelo SQLAlchemy para `Frente`.
2.  **`scripts/create_database.py`**: Importe o novo modelo e adicione-o à função `create_database()` para que a tabela seja criada.
3.  **`app/services/automation_service.py`**: Na função `run_full_sync()`, adicione uma nova chamada para a nova entidade: `await sync_entity(db, models.Frente, "/frentes")`.
4.  **`app/domain/entidades.py`**: Crie o schema `FrenteSchema` para a API.
5.  **`app/infra/db/crud/entidades.py`**: Crie a função `get_frentes(...)`.
6.  **`app/api/v1/frentes.py`**: Crie um novo arquivo de roteador para os endpoints de frentes.
7.  **`app/main.py`**: Importe e registre o novo roteador de frentes.

---

### Cenário 2: Modificando a API

#### **Como Adicionar um Novo Filtro a um Endpoint?**
*(Exemplo: Filtrar proposições por `ano`)*

1.  **`app/infra/db/crud/entidades.py`**: Modifique a função de busca (ex: `get_proposicoes`) para aceitar o novo parâmetro (ex: `ano: Optional[int] = None`) e adicione a lógica de `.filter()` na query do SQLAlchemy.
2.  **`app/api/v1/proposicoes.py`**: Modifique a função do endpoint (ex: `read_proposicoes`) para aceitar o novo parâmetro como um `Query` do FastAPI.

#### **Como Adicionar uma Nova Opção de Ordenação?**
*(Exemplo: Permitir ordenação de proposições por `dataApresentacao`)*

1.  **`app/infra/db/crud/entidades.py`**: Na função `get_proposicoes`, adicione o campo `"dataApresentacao"` à lista `allowed_sort_fields`. A lógica de ordenação dinâmica que criamos cuidará do resto.

---

### Cenário 3: Modificando a Análise de IA

#### **Como Mudar ou Melhorar o Prompt da IA?**

1.  **`prompts/analyze_proposition_prompt.txt`**: Simplesmente edite este arquivo de texto. Como o prompt é externo ao código, nenhuma alteração em Python é necessária. O sistema usará o novo prompt na próxima vez que for executado.

#### **Como Ajustar o Cálculo do `impact_score`?**

1.  **`app/services/scoring_service.py`**: Abra este arquivo e encontre a função `_calculate_impact_score`. Toda a lógica de pesos e a fórmula final estão centralizadas aqui. Você pode alterar os valores dos dicionários `scope_weights` ou `magnitude_weights`, ou a fórmula de soma, e a mudança será aplicada a todas as futuras análises.

---

### Cenário 4: Modificando a Automação

#### **Como Mudar a Frequência das Tarefas Automáticas?**

1.  **`app/core/scheduler.py`**: Abra este arquivo e encontre a função `start_scheduler`.
2.  Localize a chamada `scheduler.add_job(...)`.
3.  Para alterar o horário, modifique os parâmetros do `cron`. Por exemplo, para rodar 4 vezes ao dia (a cada 6 horas), você mudaria para `hour='0,6,12,18'`. Para rodar a cada 15 minutos, você mudaria o trigger para `'interval'` e `minutes=15`.

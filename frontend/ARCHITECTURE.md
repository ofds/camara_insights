### 📄 Documentação da Arquitetura do Frontend - Câmara Insights

#### 1. Visão Geral e Filosofia da Arquitetura

O frontend do **Câmara Insights** é construído com **Next.js** e **React**, utilizando **TypeScript** para garantir a tipagem estática e a robustez do código. A arquitetura é baseada em componentes, seguindo as melhores práticas do React para criar uma interface de usuário (UI) modular, reutilizável e de fácil manutenção.

A filosofia principal é a **separação de preocupações**, onde a UI é dividida em componentes independentes, a lógica de estado é gerenciada de forma centralizada e os serviços de dados são abstraídos do resto da aplicação.

#### 2. Diagrama de Componentes e Fluxo de Dados

A arquitetura pode ser visualizada através dos seguintes componentes principais e suas interações:

```
+-----------------+      +-----------------------+      +-----------------+
|   Usuário       |----->|   Páginas (Next.js)   |----->|   Componentes   |
|                 |<-----|   (app/dashboard/*)   |<-----|   (components/*)|
+-----------------+      +-----------+-----------+      +--------+--------+
                                     |                           |
                                     v                           v
+------------------------+      +------------------------------------------+
|   Contextos (React)    |----->|           Hooks Customizados             |
| (contexts/user-context)|      | (hooks/use-user, hooks/use-selection)    |
+------------------------+      +---------------------+--------------------+
                                                      |
         +--------------------------------------------+---------------------------------------------+
         |                                                                                          |
         v                                                                                          v
+--------+----------+                                                                        +------+----------+
|   Serviços de API |                                                                        |      Libs       |
| (services/*)      |                                                                        | (lib/*)         |
+--------+----------+                                                                        +--------+--------+
         |
         v
+--------+----------+
|   API do Backend  |
| (FastAPI)         |
+-------------------+

```

#### 3. Estrutura de Diretórios

A organização do projeto reflete diretamente a separação em camadas:

```
camara_insights/
├── src/
│   ├── app/          # (1) Camada de Roteamento e Páginas (Next.js App Router).
│   │   ├── layout.tsx    # Layout principal da aplicação.
│   │   ├── page.tsx      # Página inicial.
│   │   ├── dashboard/    # Páginas da seção de dashboard.
│   │   └── auth/         # Páginas de autenticação.
│   ├── components/   # (2) Componentes React reutilizáveis.
│   │   ├── core/       # Componentes de UI genéricos (botões, inputs).
│   │   ├── dashboard/  # Componentes específicos do dashboard.
│   │   └── auth/       # Componentes específicos de autenticação.
│   ├── contexts/     # (3) Gerenciamento de estado com React Context.
│   ├── hooks/        # (4) Hooks customizados para lógica reutilizável.
│   ├── lib/          # (5) Funções utilitárias e bibliotecas.
│   ├── services/     # (6) Lógica de comunicação com a API do backend.
│   ├── styles/       # (7) Estilos globais e configurações de tema.
│   └── types/        # (8) Definições de tipos TypeScript.
├── public/           # Arquivos estáticos (imagens, fontes).
└── next.config.mjs   # Arquivo de configuração do Next.js.
```

#### 4. Descrição das Camadas

1.  **Camada de Roteamento e Páginas (`src/app`)**

      * **Responsabilidade:** Definir as rotas da aplicação e compor as páginas a partir dos componentes.
      * **Tecnologias:** Next.js App Router.
      * **Funcionamento:** Cada diretório dentro de `app` corresponde a uma rota na URL. O arquivo `page.tsx` de cada diretório é o ponto de entrada para a rota, e o `layout.tsx` define a estrutura visual compartilhada.

2.  **Componentes (`src/components`)**

      * **Responsabilidade:** Encapsular a lógica e a marcação da UI em blocos reutilizáveis.
      * **Tecnologias:** React.
      * **Funcionamento:** Os componentes são organizados por funcionalidade (`dashboard`, `auth`) ou por uso geral (`core`). Essa abordagem promove a reutilização e facilita os testes.

3.  **Gerenciamento de Estado (`src/contexts`)**

      * **Responsabilidade:** Fornecer um estado global para a aplicação, como informações do usuário autenticado.
      * **Tecnologias:** React Context.
      * **Funcionamento:** O `UserProvider` (em `user-context.tsx`) disponibiliza os dados do usuário para todos os componentes aninhados, evitando o "prop drilling".

4.  **Hooks Customizados (`src/hooks`)**

      * **Responsabilidade:** Extrair e reutilizar a lógica de estado e efeitos colaterais dos componentes.
      * **Tecnologias:** React Hooks (`useState`, `useEffect`, `useContext`).
      * **Funcionamento:** Hooks como `useUser` abstraem a complexidade de acessar o contexto do usuário, enquanto `useSelection` gerencia o estado de seleção em tabelas ou listas.

5.  **Funções Utilitárias (`src/lib`)**

      * **Responsabilidade:** Conter funções puras e utilitários que podem ser usados em qualquer parte da aplicação.
      * **Funcionamento:** Exemplos incluem formatação de datas, validação de dados ou qualquer outra lógica que não dependa do React.

6.  **Serviços de API (`src/services`)**

      * **Responsabilidade:** Abstrair a comunicação com a API do backend.
      * **Funcionamento:** Esta camada é responsável por fazer as chamadas HTTP (usando `fetch` ou uma biblioteca como `axios`), tratar de erros e transformar os dados da API no formato que a aplicação precisa.

7.  **Estilos (`src/styles`)**

      * **Responsabilidade:** Definir a aparência visual da aplicação.
      * **Funcionamento:** Contém os estilos globais, variáveis de tema e outras configurações relacionadas à aparência.

8.  **Tipos (`src/types`)**

      * **Responsabilidade:** Definir as interfaces e tipos de dados usados na aplicação.
      * **Tecnologias:** TypeScript.
      * **Funcionamento:** Garante a consistência e a segurança dos dados em toda a aplicação.

#### 5. Fluxo de Dados Principal

**Fluxo: Visualização do Dashboard de Proposições**

1.  O usuário acessa a rota `/dashboard/proposicoes`.
2.  O Next.js renderiza a página em `src/app/dashboard/proposicoes/page.tsx`.
3.  A página utiliza um hook customizado (ex: `usePropositions`) que chama uma função do serviço de API (`propositionService.getPropositions`).
4.  O serviço de API faz uma requisição `GET` para o endpoint `/api/v1/proposicoes` do backend.
5.  Enquanto os dados estão sendo carregados, a UI pode exibir um estado de carregamento (spinner).
6.  Quando o backend responde, o serviço de API retorna os dados para o hook.
7.  O hook atualiza o estado do componente com os dados recebidos.
8.  O React renderiza novamente a página, que passa os dados para os componentes de UI (tabelas, gráficos) para exibição.

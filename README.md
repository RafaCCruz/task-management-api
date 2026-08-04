# Task Management API

API RESTful completa de gerenciamento de tarefas, pronta para portfólio.

Desenvolvida com **FastAPI**, **PostgreSQL**, **SQLAlchemy + Alembic**, autenticação **JWT** (access + refresh tokens) e empacotada com **Docker**.

---

## Stack

| Tecnologia        | Uso                          |
|-------------------|------------------------------|
| Python 3.12       | Linguagem                    |
| FastAPI           | Framework web                |
| PostgreSQL 16     | Banco de dados               |
| SQLAlchemy 2.x    | ORM                          |
| Alembic           | Migrations                   |
| Pydantic v2       | Validação e schemas          |
| python-jose       | JWT                          |
| passlib + bcrypt  | Hash de senhas               |
| Docker / Compose  | Ambiente de desenvolvimento  |
| pytest            | Testes automatizados         |

---

## Funcionalidades

- Cadastro de usuário com senha hasheada (bcrypt)
- Login retornando **access token** + **refresh token**
- Renovação de tokens via `/auth/refresh`
- Dependência de autenticação protegendo rotas privadas
- CRUD completo de tarefas (somente o dono acessa suas tarefas)
- Campos de **prioridade** (`low` / `medium` / `high`) e **status** (`pending` / `in_progress` / `completed`) como enums
- Filtros por status, prioridade e busca textual (título + descrição)
- Paginação (`page` + `size`) em listagens
- Documentação interativa em `/docs` (Swagger) e `/redoc`
- Tratamento de erros consistente com handlers globais
- Variáveis sensíveis via `.env`

---

## Estrutura do projeto

```
.
├── app/
│   ├── core/           # Config, security, exceptions
│   ├── database/       # Engine, session, Base
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas (request/response)
│   ├── repositories/   # Data access layer
│   ├── services/       # Business logic
│   ├── routers/        # FastAPI routers
│   ├── dependencies.py
│   └── main.py
├── alembic/            # Migrations
├── tests/              # pytest
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

A arquitetura em camadas (routers → services → repositories → models) facilita a manutenção e a evolução do projeto.

---

## Como rodar com Docker (recomendado)

### 1. Pré-requisitos

- Docker e Docker Compose instalados

### 2. Configurar ambiente

```bash
cp .env.example .env
# Edite SECRET_KEY para um valor longo e aleatório em produção
```

### 3. Subir os serviços

```bash
docker compose up --build
```

A API estará disponível em **http://localhost:8000**.

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

As migrations do Alembic são executadas automaticamente na subida do container.

---

## Como rodar localmente (sem Docker)

```bash
# Crie e ative um virtualenv
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt

# Configure o .env apontando para um PostgreSQL local
cp .env.example .env
# DATABASE_URL=postgresql://user:pass@localhost:5432/taskdb

# Rode as migrations
alembic upgrade head

# Inicie o servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Endpoints principais

### Autenticação

| Método | Rota                    | Descrição                          | Auth |
|--------|-------------------------|------------------------------------|------|
| POST   | `/api/v1/auth/register` | Cadastro de usuário                | Não  |
| POST   | `/api/v1/auth/login`    | Login (retorna access + refresh)   | Não  |
| POST   | `/api/v1/auth/refresh`  | Renova tokens                      | Não  |

### Usuário

| Método | Rota              | Descrição                | Auth |
|--------|-------------------|--------------------------|------|
| GET    | `/api/v1/users/me`| Perfil do usuário logado | Sim  |
| PATCH  | `/api/v1/users/me`| Atualiza nome ou senha   | Sim  |

### Tarefas

| Método | Rota                   | Descrição                                      | Auth |
|--------|------------------------|------------------------------------------------|------|
| POST   | `/api/v1/tasks`        | Cria tarefa                                    | Sim  |
| GET    | `/api/v1/tasks`        | Lista tarefas (filtros + paginação)            | Sim  |
| GET    | `/api/v1/tasks/{id}`   | Detalha uma tarefa                             | Sim  |
| PATCH  | `/api/v1/tasks/{id}`   | Atualiza parcialmente                          | Sim  |
| DELETE | `/api/v1/tasks/{id}`   | Remove tarefa                                  | Sim  |

#### Query params da listagem

- `status` – `pending` | `in_progress` | `completed`
- `priority` – `low` | `medium` | `high`
- `search` – busca em título e descrição
- `page` – página (padrão 1)
- `size` – itens por página (padrão 20, máx. 100)

---

## Exemplos de requisições (curl)

### 1. Registrar usuário

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "full_name": "Alice Silva",
    "password": "Str0ngP@ssw0rd"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "Str0ngP@ssw0rd"
  }'
```

### 3. Criar tarefa

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implementar endpoint de login",
    "description": "Adicionar JWT com refresh token",
    "priority": "high",
    "status": "pending"
  }'
```

### 4. Listar tarefas com filtros

```bash
curl "http://localhost:8000/api/v1/tasks?status=pending&priority=high&page=1&size=10" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### 5. Atualizar tarefa

```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

### 6. Deletar tarefa

```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

## Testes

```bash
pytest -v
```

---

## Licença

Este projeto foi criado para fins de portfólio. Sinta-se livre para usar e adaptar.

# Controle de Tarefas — API REST

API REST para gerenciar tarefas, com CRUD completo, filtros, paginação, validação de dados e testes automatizados.

**Tecnologias:** Python · FastAPI · SQLite · Pydantic · unittest

## Funcionalidades

- Criar, listar, buscar, atualizar (parcialmente) e excluir tarefas
- Cada tarefa tem título, descrição, status, prioridade e prazo
- Filtros por status e prioridade, com paginação
- Validação automática dos dados de entrada (respostas `422` com o motivo do erro)
- Banco de dados com restrições (`CHECK`) que impedem valores inválidos
- Documentação interativa gerada automaticamente (Swagger)

## Como rodar

Requer Python 3.10 ou superior.

```bash
# 1. Criar e ativar um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Iniciar a API
uvicorn app.main:app --reload
```

Com a API rodando, acesse **http://127.0.0.1:8000/docs** para testar todas as rotas pelo navegador.
O banco `tarefas.db` e criado automaticamente na primeira execucao.

## Rotas

| Metodo | Rota | Descricao |
|--------|------|-----------|
| POST | `/tarefas` | Cria uma tarefa |
| GET | `/tarefas` | Lista tarefas (filtros: `status`, `prioridade`; paginação: `limite`, `deslocamento`) |
| GET | `/tarefas/{id}` | Busca uma tarefa pelo id |
| PATCH | `/tarefas/{id}` | Atualiza apenas os campos enviados |
| DELETE | `/tarefas/{id}` | Exclui uma tarefa |

**Valores aceitos:** `status` = `pendente`, `em_andamento`, `concluida` · `prioridade` = `baixa`, `media`, `alta`

### Exemplo

```bash
curl -X POST http://127.0.0.1:8000/tarefas \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Estudar FastAPI", "prioridade": "alta", "prazo": "2026-12-31"}'
```

Resposta (`201 Created`):

```json
{
  "titulo": "Estudar FastAPI",
  "descricao": null,
  "status": "pendente",
  "prioridade": "alta",
  "prazo": "2026-12-31",
  "id": 1,
  "criada_em": "2026-10-08 12:00:00",
  "atualizada_em": "2026-10-08 12:00:00"
}
```

## Testes

```bash
python -m unittest -v
```

Os testes usam um banco temporário e não afetam o `tarefas.db`.

## Estrutura

```
app/
├── main.py         # rotas da API (FastAPI)
├── schemas.py      # modelos e validação dos dados (Pydantic)
├── repository.py   # consultas SQL (CRUD)
└── database.py     # conexão e criação da tabela (SQLite)
tests/
├── test_repository.py   # testes do banco de dados
└── test_api.py          # testes das rotas
```

## Decisões de projeto

- **Camadas separadas:** rotas, validação e acesso a dados ficam em arquivos distintos, o que facilita testar e manter.
- **SQL puro com `sqlite3`:** as consultas são escritas à mão e sempre usam parâmetros (`?`), evitando SQL injection.
- **`PATCH` em vez de `PUT`:** permite alterar só um campo (por exemplo, marcar como concluída) sem reenviar a tarefa inteira.
- **Injeção de dependência (`Depends`):** cada requisição recebe a sua conexão com o banco, e os testes trocam o banco real por um temporário.

## Ideias de evolução

- Autenticação e tarefas por usuário
- Migração para PostgreSQL com SQLAlchemy
- Empacotamento com Docker
- Interface web que consuma a API

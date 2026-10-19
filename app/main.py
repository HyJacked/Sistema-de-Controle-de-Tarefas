"""API REST de controle de tarefas (FastAPI + SQLite)."""
import sqlite3
from contextlib import asynccontextmanager
from typing import Iterator, Optional

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Response

from app import repository
from app.database import get_connection, init_db
from app.schemas import Prioridade, Status, Tarefa, TarefaAtualizar, TarefaCriar


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa uma vez ao iniciar a API: garante que a tabela exista.
    conn = get_connection()
    init_db(conn)
    conn.close()
    yield


app = FastAPI(
    title="Controle de Tarefas",
    description="API REST com CRUD de tarefas, filtros e paginação.",
    version="1.0.0",
    lifespan=lifespan,
)


def get_db() -> Iterator[sqlite3.Connection]:
    """Dependência: entrega uma conexão para a rota e a fecha ao final da requisição."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def _nao_encontrada(tarefa_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Tarefa {tarefa_id} não encontrada")


@app.post("/tarefas", response_model=Tarefa, status_code=201, tags=["Tarefas"])
def criar(tarefa: TarefaCriar, db: sqlite3.Connection = Depends(get_db)):
    """Cria uma nova tarefa."""
    return repository.criar_tarefa(db, tarefa.model_dump(mode="json"))


@app.get("/tarefas", response_model=list[Tarefa], tags=["Tarefas"])
def listar(
    status: Optional[Status] = None,
    prioridade: Optional[Prioridade] = None,
    limite: int = Query(50, ge=1, le=100),
    deslocamento: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db),
):
    """Lista tarefas, com filtros opcionais por status e prioridade, e paginação."""
    return repository.listar_tarefas(
        db,
        status=status.value if status else None,
        prioridade=prioridade.value if prioridade else None,
        limite=limite,
        deslocamento=deslocamento,
    )


@app.get("/tarefas/{tarefa_id}", response_model=Tarefa, tags=["Tarefas"])
def obter(tarefa_id: int = Path(gt=0), db: sqlite3.Connection = Depends(get_db)):
    """Busca uma tarefa pelo id."""
    tarefa = repository.obter_tarefa(db, tarefa_id)
    if tarefa is None:
        raise _nao_encontrada(tarefa_id)
    return tarefa


@app.patch("/tarefas/{tarefa_id}", response_model=Tarefa, tags=["Tarefas"])
def atualizar(
    tarefa: TarefaAtualizar,
    tarefa_id: int = Path(gt=0),
    db: sqlite3.Connection = Depends(get_db),
):
    """Atualiza parcialmente uma tarefa: só os campos enviados são alterados."""
    dados = tarefa.model_dump(mode="json", exclude_unset=True)
    atualizada = repository.atualizar_tarefa(db, tarefa_id, dados)
    if atualizada is None:
        raise _nao_encontrada(tarefa_id)
    return atualizada


@app.delete("/tarefas/{tarefa_id}", status_code=204, tags=["Tarefas"])
def excluir(tarefa_id: int = Path(gt=0), db: sqlite3.Connection = Depends(get_db)):
    """Exclui uma tarefa."""
    if not repository.excluir_tarefa(db, tarefa_id):
        raise _nao_encontrada(tarefa_id)
    return Response(status_code=204)

"""Conexão com o banco SQLite e criação da tabela."""
import os
import sqlite3

# Caminho do arquivo do banco. Pode ser trocado pela variável de ambiente TASKS_DB_PATH.
DB_PATH = os.getenv("TASKS_DB_PATH", "tarefas.db")

# O CHECK garante que o banco rejeite valores inválidos, mesmo que a API falhe em validar.
SCHEMA = """
CREATE TABLE IF NOT EXISTS tarefas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo        TEXT NOT NULL,
    descricao     TEXT,
    status        TEXT NOT NULL DEFAULT 'pendente'
                  CHECK (status IN ('pendente', 'em_andamento', 'concluida')),
    prioridade    TEXT NOT NULL DEFAULT 'media'
                  CHECK (prioridade IN ('baixa', 'media', 'alta')),
    prazo         TEXT,
    criada_em     TEXT NOT NULL DEFAULT (datetime('now')),
    atualizada_em TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """Abre uma conexão nova. Cada requisição da API usa a sua própria conexão."""
    # check_same_thread=False: o FastAPI pode abrir a conexão e usá-la em threads
    # diferentes. Como cada requisição tem a sua conexão, isso é seguro.
    conn = sqlite3.connect(db_path or DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # permite acessar colunas pelo nome
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Cria a tabela caso ela ainda não exista."""
    conn.executescript(SCHEMA)
    conn.commit()

"""Acesso a dados: todas as consultas SQL do projeto ficam concentradas aqui."""
import sqlite3
from typing import Optional

# Lista de colunas que podem ser alteradas. Usada para montar o UPDATE com segurança.
CAMPOS_EDITAVEIS = ("titulo", "descricao", "status", "prioridade", "prazo")


def criar_tarefa(conn: sqlite3.Connection, dados: dict) -> dict:
    cursor = conn.execute(
        """
        INSERT INTO tarefas (titulo, descricao, status, prioridade, prazo)
        VALUES (:titulo, :descricao, :status, :prioridade, :prazo)
        """,
        dados,
    )
    conn.commit()
    return obter_tarefa(conn, cursor.lastrowid)


def obter_tarefa(conn: sqlite3.Connection, tarefa_id: int) -> Optional[dict]:
    linha = conn.execute("SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)).fetchone()
    return dict(linha) if linha else None


def listar_tarefas(
    conn: sqlite3.Connection,
    status: Optional[str] = None,
    prioridade: Optional[str] = None,
    limite: int = 50,
    deslocamento: int = 0,
) -> list[dict]:
    consulta = "SELECT * FROM tarefas"
    filtros, parametros = [], []

    if status:
        filtros.append("status = ?")
        parametros.append(status)
    if prioridade:
        filtros.append("prioridade = ?")
        parametros.append(prioridade)
    if filtros:
        consulta += " WHERE " + " AND ".join(filtros)

    consulta += " ORDER BY id LIMIT ? OFFSET ?"
    parametros += [limite, deslocamento]

    return [dict(linha) for linha in conn.execute(consulta, parametros).fetchall()]


def atualizar_tarefa(conn: sqlite3.Connection, tarefa_id: int, dados: dict) -> Optional[dict]:
    """Atualiza só os campos enviados. Devolve None se a tarefa não existir."""
    campos = {c: v for c, v in dados.items() if c in CAMPOS_EDITAVEIS}

    if campos:
        # Só nomes de coluna da lista CAMPOS_EDITAVEIS entram no texto do SQL.
        # Os valores sempre vão como parâmetros (?), nunca concatenados: evita SQL injection.
        atribuicoes = ", ".join(f"{coluna} = ?" for coluna in campos)
        cursor = conn.execute(
            f"UPDATE tarefas SET {atribuicoes}, atualizada_em = datetime('now') WHERE id = ?",
            (*campos.values(), tarefa_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return None

    return obter_tarefa(conn, tarefa_id)


def excluir_tarefa(conn: sqlite3.Connection, tarefa_id: int) -> bool:
    cursor = conn.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
    conn.commit()
    return cursor.rowcount > 0

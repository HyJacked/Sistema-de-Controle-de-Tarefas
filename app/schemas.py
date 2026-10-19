"""Modelos Pydantic: definem e validam o formato dos dados que entram e saem da API."""
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Status(str, Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    concluida = "concluida"


class Prioridade(str, Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"


class TarefaCriar(BaseModel):
    """Dados aceitos ao criar uma tarefa (POST)."""

    model_config = ConfigDict(str_strip_whitespace=True)  # remove espaços nas pontas

    titulo: str = Field(min_length=1, max_length=100, examples=["Estudar FastAPI"])
    descricao: Optional[str] = Field(default=None, max_length=500)
    status: Status = Status.pendente
    prioridade: Prioridade = Prioridade.media
    prazo: Optional[date] = Field(default=None, examples=["2026-12-31"])


class TarefaAtualizar(BaseModel):
    """Dados aceitos ao atualizar uma tarefa (PATCH). Todos os campos são opcionais."""

    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=500)
    status: Optional[Status] = None
    prioridade: Optional[Prioridade] = None
    prazo: Optional[date] = None

    @field_validator("titulo", "status", "prioridade")
    @classmethod
    def nao_pode_ser_nulo(cls, valor):
        # Esses campos são obrigatórios no banco: podem ser omitidos, mas não enviados como null.
        if valor is None:
            raise ValueError("não pode ser nulo")
        return valor


class Tarefa(TarefaCriar):
    """Formato da tarefa devolvida pela API."""

    id: int
    criada_em: str
    atualizada_em: str

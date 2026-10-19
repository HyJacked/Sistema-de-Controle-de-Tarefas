"""Testes da camada de banco de dados (usam um banco temporário, não o real)."""
import os
import sqlite3
import tempfile
import unittest

from app import repository
from app.database import get_connection, init_db


def nova_tarefa(**extra):
    base = {"titulo": "Tarefa", "descricao": None, "status": "pendente",
            "prioridade": "media", "prazo": None}
    return {**base, **extra}


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.conn = get_connection(os.path.join(self.pasta.name, "teste.db"))
        init_db(self.conn)

    def tearDown(self):
        self.conn.close()
        self.pasta.cleanup()

    def test_criar_e_obter(self):
        criada = repository.criar_tarefa(self.conn, nova_tarefa(titulo="Estudar SQL"))
        self.assertEqual(criada["titulo"], "Estudar SQL")
        self.assertEqual(criada["status"], "pendente")
        self.assertEqual(repository.obter_tarefa(self.conn, criada["id"]), criada)

    def test_obter_inexistente_retorna_none(self):
        self.assertIsNone(repository.obter_tarefa(self.conn, 999))

    def test_listar_com_filtros(self):
        repository.criar_tarefa(self.conn, nova_tarefa(titulo="A", prioridade="alta"))
        repository.criar_tarefa(self.conn, nova_tarefa(titulo="B", prioridade="baixa"))
        repository.criar_tarefa(self.conn, nova_tarefa(titulo="C", prioridade="alta", status="concluida"))

        self.assertEqual(len(repository.listar_tarefas(self.conn)), 3)
        self.assertEqual(len(repository.listar_tarefas(self.conn, prioridade="alta")), 2)
        self.assertEqual(len(repository.listar_tarefas(self.conn, status="concluida")), 1)
        self.assertEqual(
            len(repository.listar_tarefas(self.conn, status="concluida", prioridade="baixa")), 0
        )

    def test_listar_paginacao(self):
        for i in range(5):
            repository.criar_tarefa(self.conn, nova_tarefa(titulo=f"T{i}"))
        pagina = repository.listar_tarefas(self.conn, limite=2, deslocamento=2)
        self.assertEqual([t["titulo"] for t in pagina], ["T2", "T3"])

    def test_atualizar_parcial(self):
        criada = repository.criar_tarefa(self.conn, nova_tarefa(titulo="Antes", prioridade="baixa"))
        atualizada = repository.atualizar_tarefa(self.conn, criada["id"], {"status": "concluida"})
        self.assertEqual(atualizada["status"], "concluida")
        self.assertEqual(atualizada["titulo"], "Antes")  # não mexeu nos outros campos
        self.assertEqual(atualizada["prioridade"], "baixa")

    def test_atualizar_ignora_campos_nao_editaveis(self):
        criada = repository.criar_tarefa(self.conn, nova_tarefa())
        atualizada = repository.atualizar_tarefa(self.conn, criada["id"], {"id": 500, "titulo": "Novo"})
        self.assertEqual(atualizada["id"], criada["id"])
        self.assertEqual(atualizada["titulo"], "Novo")

    def test_atualizar_inexistente_retorna_none(self):
        self.assertIsNone(repository.atualizar_tarefa(self.conn, 999, {"titulo": "X"}))

    def test_excluir(self):
        criada = repository.criar_tarefa(self.conn, nova_tarefa())
        self.assertTrue(repository.excluir_tarefa(self.conn, criada["id"]))
        self.assertIsNone(repository.obter_tarefa(self.conn, criada["id"]))
        self.assertFalse(repository.excluir_tarefa(self.conn, criada["id"]))

    def test_banco_rejeita_status_invalido(self):
        with self.assertRaises(sqlite3.IntegrityError):
            repository.criar_tarefa(self.conn, nova_tarefa(status="inventado"))


if __name__ == "__main__":
    unittest.main()

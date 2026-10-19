"""Testes da API (rotas, validação e códigos HTTP). Usam um banco temporário."""
import os
import tempfile
import unittest

from fastapi.testclient import TestClient

from app.database import get_connection, init_db
from app.main import app, get_db


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        caminho = os.path.join(self.pasta.name, "teste.db")

        conn = get_connection(caminho)
        init_db(conn)
        conn.close()

        def db_de_teste():
            conn = get_connection(caminho)
            try:
                yield conn
            finally:
                conn.close()

        # Troca o banco real pelo banco temporário só durante o teste.
        app.dependency_overrides[get_db] = db_de_teste
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.pasta.cleanup()

    def criar(self, **extra):
        return self.client.post("/tarefas", json={"titulo": "Estudar FastAPI", **extra})

    def test_criar_tarefa(self):
        resp = self.criar(prioridade="alta", prazo="2026-12-31")
        self.assertEqual(resp.status_code, 201)
        corpo = resp.json()
        self.assertEqual(corpo["titulo"], "Estudar FastAPI")
        self.assertEqual(corpo["status"], "pendente")  # valor padrão
        self.assertEqual(corpo["prazo"], "2026-12-31")

    def test_titulo_vazio_retorna_422(self):
        self.assertEqual(self.criar(titulo="   ").status_code, 422)

    def test_prioridade_invalida_retorna_422(self):
        self.assertEqual(self.criar(prioridade="urgentissima").status_code, 422)

    def test_obter_inexistente_retorna_404(self):
        self.assertEqual(self.client.get("/tarefas/999").status_code, 404)

    def test_listar_com_filtro(self):
        self.criar(prioridade="alta")
        self.criar(prioridade="baixa")
        resp = self.client.get("/tarefas", params={"prioridade": "alta"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_filtro_invalido_retorna_422(self):
        self.assertEqual(self.client.get("/tarefas", params={"status": "xyz"}).status_code, 422)

    def test_atualizar_parcialmente(self):
        tarefa_id = self.criar().json()["id"]
        resp = self.client.patch(f"/tarefas/{tarefa_id}", json={"status": "concluida"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "concluida")
        self.assertEqual(resp.json()["titulo"], "Estudar FastAPI")

    def test_atualizar_titulo_nulo_retorna_422(self):
        tarefa_id = self.criar().json()["id"]
        resp = self.client.patch(f"/tarefas/{tarefa_id}", json={"titulo": None})
        self.assertEqual(resp.status_code, 422)

    def test_atualizar_inexistente_retorna_404(self):
        resp = self.client.patch("/tarefas/999", json={"status": "concluida"})
        self.assertEqual(resp.status_code, 404)

    def test_excluir(self):
        tarefa_id = self.criar().json()["id"]
        self.assertEqual(self.client.delete(f"/tarefas/{tarefa_id}").status_code, 204)
        self.assertEqual(self.client.get(f"/tarefas/{tarefa_id}").status_code, 404)
        self.assertEqual(self.client.delete(f"/tarefas/{tarefa_id}").status_code, 404)


if __name__ == "__main__":
    unittest.main()

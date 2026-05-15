"""Testes do CRUD de tarefas.

Cobre operações CRUD, autorização e isolamento entre usuários.
Inclui regressão para BUG-003 (truncamento silencioso de título).
"""
import pytest


class TestCreateTask:
    """POST /tasks"""

    def test_cria_tarefa_com_dados_validos(self, client, auth_headers):
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={
                "title": "Comprar leite",
                "description": "Mercado da esquina",
                "priority": "media",
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "Comprar leite"
        assert body["priority"] == "media"
        assert body["status"] == "pendente"
        assert "id" in body
        assert "created_at" in body

    def test_cria_tarefa_com_prioridade_padrao(self, client, auth_headers):
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={"title": "Tarefa simples"},
        )

        assert response.status_code == 201
        assert response.json()["priority"] == "media"

    def test_rejeita_criacao_sem_autenticacao(self, client):
        response = client.post(
            "/tasks",
            json={"title": "X"},
        )

        assert response.status_code == 401

    def test_rejeita_titulo_vazio(self, client, auth_headers):
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={"title": ""},
        )

        assert response.status_code == 422

    def test_rejeita_titulo_acima_do_limite(self, client, auth_headers):
        """Regressão BUG-003: backend deve rejeitar, não truncar silenciosamente."""
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={"title": "a" * 101},  # limite é 100
        )

        assert response.status_code == 422

    def test_aceita_titulo_no_limite_exato(self, client, auth_headers):
        """Regressão BUG-003: 100 caracteres devem ser preservados integralmente."""
        titulo_100_chars = "a" * 100
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={"title": titulo_100_chars},
        )

        assert response.status_code == 201
        # Crítico: título salvo deve ter exatamente o que foi enviado
        assert response.json()["title"] == titulo_100_chars
        assert len(response.json()["title"]) == 100

    def test_rejeita_prioridade_invalida(self, client, auth_headers):
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={"title": "X", "priority": "urgentissima"},
        )

        assert response.status_code == 422


class TestListTasks:
    """GET /tasks"""

    def test_lista_vazia_para_usuario_novo(self, client, auth_headers):
        response = client.get("/tasks", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_lista_apenas_tarefas_do_usuario_autenticado(self, client):
        """Isolamento: usuário A não vê tarefas do usuário B."""
        # Cria usuário A com tarefa
        user_a = client.post("/auth/signup", json={
            "name": "A", "email": "a@x.com", "password": "Senha@2026",
        }).json()
        client.post("/tasks", headers={"X-User-Id": user_a["id"]}, json={"title": "Tarefa A"})

        # Cria usuário B com tarefa
        user_b = client.post("/auth/signup", json={
            "name": "B", "email": "b@x.com", "password": "Senha@2026",
        }).json()
        client.post("/tasks", headers={"X-User-Id": user_b["id"]}, json={"title": "Tarefa B"})

        # Usuário A só vê a tarefa dele
        response = client.get("/tasks", headers={"X-User-Id": user_a["id"]})
        titles = [t["title"] for t in response.json()]
        assert titles == ["Tarefa A"]

    def test_rejeita_listagem_sem_autenticacao(self, client):
        response = client.get("/tasks")
        assert response.status_code == 401


class TestGetTask:
    """GET /tasks/{id}"""

    def test_obtem_tarefa_existente(self, client, auth_headers):
        created = client.post("/tasks", headers=auth_headers, json={"title": "X"}).json()

        response = client.get(f"/tasks/{created['id']}", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_retorna_404_para_id_inexistente(self, client, auth_headers):
        response = client.get("/tasks/id-que-nao-existe", headers=auth_headers)
        assert response.status_code == 404

    def test_nao_permite_acessar_tarefa_de_outro_usuario(self, client):
        """Crítico de segurança: enumeração horizontal."""
        user_a = client.post("/auth/signup", json={
            "name": "A", "email": "a@x.com", "password": "Senha@2026",
        }).json()
        task_a = client.post(
            "/tasks",
            headers={"X-User-Id": user_a["id"]},
            json={"title": "Privado"},
        ).json()

        user_b = client.post("/auth/signup", json={
            "name": "B", "email": "b@x.com", "password": "Senha@2026",
        }).json()

        # B tenta ler a tarefa de A
        response = client.get(
            f"/tasks/{task_a['id']}",
            headers={"X-User-Id": user_b["id"]},
        )

        assert response.status_code == 404  # 404 e não 403 — evita revelar existência


class TestUpdateTask:
    """PATCH /tasks/{id}"""

    def test_atualiza_titulo(self, client, auth_headers):
        created = client.post("/tasks", headers=auth_headers, json={"title": "Antigo"}).json()

        response = client.patch(
            f"/tasks/{created['id']}",
            headers=auth_headers,
            json={"title": "Novo"},
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Novo"

    def test_atualiza_status_para_concluida(self, client, auth_headers):
        created = client.post("/tasks", headers=auth_headers, json={"title": "X"}).json()

        response = client.patch(
            f"/tasks/{created['id']}",
            headers=auth_headers,
            json={"status": "concluida"},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "concluida"

    def test_atualizacao_parcial_preserva_outros_campos(self, client, auth_headers):
        created = client.post("/tasks", headers=auth_headers, json={
            "title": "Original",
            "description": "Descrição original",
            "priority": "alta",
        }).json()

        response = client.patch(
            f"/tasks/{created['id']}",
            headers=auth_headers,
            json={"status": "concluida"},
        )

        body = response.json()
        assert body["title"] == "Original"
        assert body["description"] == "Descrição original"
        assert body["priority"] == "alta"
        assert body["status"] == "concluida"

    def test_rejeita_status_invalido(self, client, auth_headers):
        created = client.post("/tasks", headers=auth_headers, json={"title": "X"}).json()

        response = client.patch(
            f"/tasks/{created['id']}",
            headers=auth_headers,
            json={"status": "esquecida"},
        )

        assert response.status_code == 422

    def test_retorna_404_ao_atualizar_inexistente(self, client, auth_headers):
        response = client.patch(
            "/tasks/inexistente",
            headers=auth_headers,
            json={"title": "X"},
        )

        assert response.status_code == 404


class TestDeleteTask:
    """DELETE /tasks/{id}"""

    def test_exclui_tarefa_existente(self, client, auth_headers):
        created = client.post("/tasks", headers=auth_headers, json={"title": "X"}).json()

        response = client.delete(f"/tasks/{created['id']}", headers=auth_headers)
        assert response.status_code == 204

        # Confirma que foi mesmo excluída
        follow_up = client.get(f"/tasks/{created['id']}", headers=auth_headers)
        assert follow_up.status_code == 404

    def test_retorna_404_ao_excluir_inexistente(self, client, auth_headers):
        response = client.delete("/tasks/inexistente", headers=auth_headers)
        assert response.status_code == 404

    def test_nao_permite_excluir_tarefa_de_outro_usuario(self, client):
        user_a = client.post("/auth/signup", json={
            "name": "A", "email": "a@x.com", "password": "Senha@2026",
        }).json()
        task_a = client.post(
            "/tasks",
            headers={"X-User-Id": user_a["id"]},
            json={"title": "Privado"},
        ).json()

        user_b = client.post("/auth/signup", json={
            "name": "B", "email": "b@x.com", "password": "Senha@2026",
        }).json()

        response = client.delete(
            f"/tasks/{task_a['id']}",
            headers={"X-User-Id": user_b["id"]},
        )

        assert response.status_code == 404

        # Garantia: a tarefa continua existindo para o dono
        check = client.get(
            f"/tasks/{task_a['id']}",
            headers={"X-User-Id": user_a["id"]},
        )
        assert check.status_code == 200

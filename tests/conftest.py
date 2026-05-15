"""Fixtures compartilhadas entre suites de teste."""
import pytest
from fastapi.testclient import TestClient

from app.main import app, storage


@pytest.fixture(autouse=True)
def reset_storage():
    """Isola cada teste — storage limpo a cada execução."""
    storage.users.clear()
    storage.tasks.clear()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    """Cria um usuário e retorna seus dados + token."""
    response = client.post(
        "/auth/signup",
        json={
            "name": "Maria Silva",
            "email": "maria.silva@exemplo.com",
            "password": "Senha@2026",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def auth_headers(registered_user):
    """Headers de autenticação prontos para usar."""
    return {"X-User-Id": registered_user["id"]}

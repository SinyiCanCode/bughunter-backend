"""Testes de cadastro e login.

Inclui regressões automatizadas para BUG-001 (email inválido aceito)
e BUG-002 (login case-sensitive) reportados no projeto de teste manual.
"""
import pytest


class TestSignup:
    """POST /auth/signup"""

    def test_cadastro_com_dados_validos_retorna_201(self, client):
        response = client.post(
            "/auth/signup",
            json={
                "name": "Maria Silva",
                "email": "maria.silva@exemplo.com",
                "password": "Senha@2026",
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Maria Silva"
        assert body["email"] == "maria.silva@exemplo.com"
        assert "id" in body
        # Garantia de contrato: senha NUNCA volta na resposta
        assert "password" not in body
        assert "password_hash" not in body

    def test_cadastro_normaliza_email_para_lowercase(self, client):
        """Regressão preventiva relacionada a BUG-002."""
        response = client.post(
            "/auth/signup",
            json={
                "name": "João",
                "email": "JOAO@Exemplo.COM",
                "password": "Senha@2026",
            },
        )

        assert response.status_code == 201
        assert response.json()["email"] == "joao@exemplo.com"

    @pytest.mark.parametrize("email_invalido", [
        "joao@email",       # sem TLD — BUG-001 original
        "joao@",
        "@email.com",
        "sem-arroba",
        "com espaço@email.com",  # espaço literal
    ])
    def test_cadastro_rejeita_email_invalido(self, client, email_invalido):
        """Regressão BUG-001: emails inválidos devem ser rejeitados."""
        response = client.post(
            "/auth/signup",
            json={
                "name": "Teste",
                "email": email_invalido,
                "password": "Senha@2026",
            },
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_cadastro_com_email_duplicado_retorna_409(self, client):
        payload = {
            "name": "Maria",
            "email": "maria@exemplo.com",
            "password": "Senha@2026",
        }
        client.post("/auth/signup", json=payload)
        response = client.post("/auth/signup", json=payload)

        assert response.status_code == 409
        assert "já cadastrado" in response.json()["detail"]

    def test_cadastro_detecta_duplicado_ignorando_caixa(self, client):
        """Maria@Email.com e maria@email.com são o mesmo usuário."""
        client.post("/auth/signup", json={
            "name": "Maria",
            "email": "maria@exemplo.com",
            "password": "Senha@2026",
        })
        response = client.post("/auth/signup", json={
            "name": "Maria 2",
            "email": "MARIA@EXEMPLO.COM",
            "password": "OutraSenha@2026",
        })

        assert response.status_code == 409

    def test_cadastro_rejeita_senha_curta(self, client):
        response = client.post(
            "/auth/signup",
            json={
                "name": "Maria",
                "email": "maria@exemplo.com",
                "password": "Abc1",  # 4 caracteres
            },
        )

        assert response.status_code == 422

    def test_cadastro_rejeita_senha_sem_maiuscula(self, client):
        response = client.post(
            "/auth/signup",
            json={
                "name": "Maria",
                "email": "maria@exemplo.com",
                "password": "senha2026",
            },
        )

        assert response.status_code == 422

    def test_cadastro_rejeita_senha_sem_numero(self, client):
        response = client.post(
            "/auth/signup",
            json={
                "name": "Maria",
                "email": "maria@exemplo.com",
                "password": "SenhaForte",
            },
        )

        assert response.status_code == 422

    @pytest.mark.parametrize("campo_faltando", ["name", "email", "password"])
    def test_cadastro_exige_campos_obrigatorios(self, client, campo_faltando):
        payload = {
            "name": "Maria",
            "email": "maria@exemplo.com",
            "password": "Senha@2026",
        }
        del payload[campo_faltando]

        response = client.post("/auth/signup", json=payload)

        assert response.status_code == 422


class TestLogin:
    """POST /auth/login"""

    def test_login_com_credenciais_validas_retorna_200(self, client, registered_user):
        response = client.post(
            "/auth/login",
            json={
                "email": "maria.silva@exemplo.com",
                "password": "Senha@2026",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert "token" in body
        assert body["user"]["id"] == registered_user["id"]
        assert body["user"]["email"] == "maria.silva@exemplo.com"

    def test_login_aceita_email_com_variacao_de_caixa(self, client, registered_user):
        """Regressão BUG-002: email é case-insensitive no login."""
        response = client.post(
            "/auth/login",
            json={
                "email": "Maria.Silva@Exemplo.COM",
                "password": "Senha@2026",
            },
        )

        assert response.status_code == 200

    def test_login_com_senha_errada_retorna_401(self, client, registered_user):
        response = client.post(
            "/auth/login",
            json={
                "email": "maria.silva@exemplo.com",
                "password": "senhaErrada",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Email ou senha incorretos"

    def test_login_com_email_inexistente_retorna_401(self, client):
        response = client.post(
            "/auth/login",
            json={
                "email": "naoexiste@exemplo.com",
                "password": "qualquer123",
            },
        )

        assert response.status_code == 401

    def test_login_nao_revela_se_email_existe(self, client, registered_user):
        """Segurança: mensagem genérica evita enumeração de usuários."""
        r1 = client.post("/auth/login", json={
            "email": "maria.silva@exemplo.com",
            "password": "errada",
        })
        r2 = client.post("/auth/login", json={
            "email": "inexistente@exemplo.com",
            "password": "errada",
        })

        assert r1.json()["detail"] == r2.json()["detail"]

    def test_login_rejeita_payload_invalido(self, client):
        response = client.post("/auth/login", json={"email": "x"})
        assert response.status_code == 422

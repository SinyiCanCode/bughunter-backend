"""Testes unitários dos validators."""
import pytest

from app.validators import (
    is_valid_email,
    normalize_email,
    evaluate_password_strength,
    is_valid_task_title,
)


class TestIsValidEmail:
    @pytest.mark.parametrize("email", [
        "maria.silva@exemplo.com",
        "user+tag@dominio.com.br",
        "a@b.co",
        "nome_sobrenome@empresa.org",
    ])
    def test_aceita_emails_validos(self, email):
        assert is_valid_email(email) is True

    @pytest.mark.parametrize("email", [
        "joao@email",       # sem TLD — BUG-001
        "joao@",
        "@email.com",
        "joao email.com",
        "",
        "   ",
        "sem-arroba.com",
    ])
    def test_rejeita_emails_invalidos(self, email):
        assert is_valid_email(email) is False

    @pytest.mark.parametrize("invalid", [None, 123, [], {}])
    def test_rejeita_tipos_invalidos(self, invalid):
        assert is_valid_email(invalid) is False

    def test_rejeita_email_acima_de_254_chars(self):
        longo = "a" * 250 + "@b.co"
        assert is_valid_email(longo) is False


class TestNormalizeEmail:
    def test_converte_para_lowercase(self):
        assert normalize_email("Maria.Silva@Exemplo.COM") == "maria.silva@exemplo.com"

    def test_remove_espacos_nas_pontas(self):
        assert normalize_email("  user@dominio.com  ") == "user@dominio.com"

    @pytest.mark.parametrize("invalid", [None, 123, []])
    def test_retorna_vazio_para_tipo_invalido(self, invalid):
        assert normalize_email(invalid) == ""


class TestPasswordStrength:
    def test_senha_curta_e_invalida(self):
        result = evaluate_password_strength("abc1")
        assert result["valid"] is False
        assert result["score"] == 0

    def test_senha_so_minusculas_e_invalida(self):
        result = evaluate_password_strength("abcdefgh")
        assert result["valid"] is False

    def test_senha_forte_e_valida(self):
        result = evaluate_password_strength("Senha@2026")
        assert result["valid"] is True
        assert result["score"] >= 3

    def test_senha_longa_recebe_bonus(self):
        result = evaluate_password_strength("SenhaForte@2026!")
        assert result["score"] >= 4

    @pytest.mark.parametrize("invalid", [None, 12345678, []])
    def test_tipo_invalido_e_invalido(self, invalid):
        assert evaluate_password_strength(invalid)["valid"] is False


class TestTaskTitle:
    def test_titulo_normal_e_valido(self):
        assert is_valid_task_title("Comprar leite") is True

    def test_titulo_no_limite_e_valido(self):
        assert is_valid_task_title("a" * 100) is True

    def test_titulo_acima_do_limite_e_invalido(self):
        assert is_valid_task_title("a" * 101) is False

    def test_titulo_vazio_e_invalido(self):
        assert is_valid_task_title("") is False

    def test_titulo_so_espacos_e_invalido(self):
        assert is_valid_task_title("   ") is False

    @pytest.mark.parametrize("invalid", [None, 123, []])
    def test_tipo_invalido_e_invalido(self, invalid):
        assert is_valid_task_title(invalid) is False

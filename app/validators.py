"""Validações reutilizáveis — funções puras, fáceis de testar."""
import re

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

MAX_EMAIL_LENGTH = 254
MIN_PASSWORD_LENGTH = 8
MAX_TASK_TITLE_LENGTH = 100
MAX_TASK_DESCRIPTION_LENGTH = 500


def is_valid_email(email: str) -> bool:
    """Valida formato de email conforme RFC 5322 simplificada."""
    if not isinstance(email, str):
        return False
    email = email.strip()
    if not email or len(email) > MAX_EMAIL_LENGTH:
        return False
    return bool(EMAIL_REGEX.match(email))


def normalize_email(email: str) -> str:
    """Normaliza email: lowercase + trim. Previne bugs de case-sensitivity."""
    if not isinstance(email, str):
        return ""
    return email.strip().lower()


def evaluate_password_strength(password: str) -> dict:
    """Avalia força da senha. Retorna score 0-5 e validade."""
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        return {"score": 0, "valid": False, "reason": "muito curta"}

    score = 0
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[0-9]", password):
        score += 1
    if re.search(r"[^A-Za-z0-9]", password):
        score += 1
    if len(password) >= 12:
        score += 1

    return {"score": score, "valid": score >= 3, "reason": None if score >= 3 else "fraca"}


def is_valid_task_title(title: str) -> bool:
    """Título: não vazio e dentro do limite."""
    if not isinstance(title, str):
        return False
    stripped = title.strip()
    return 0 < len(stripped) <= MAX_TASK_TITLE_LENGTH

"""Storage em memória para fins de teste/portfolio.

Em produção, substituiria por SQLAlchemy + Postgres.
"""
from datetime import datetime, timezone
from uuid import uuid4
from passlib.context import CryptContext

from .validators import normalize_email


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Storage:
    """Storage isolável — uma instância por aplicação ou por teste."""

    def __init__(self):
        self.users: dict[str, dict] = {}
        self.tasks: dict[str, dict] = {}

    # ---------- usuários ----------

    def create_user(self, name: str, email: str, password: str) -> dict:
        normalized = normalize_email(email)
        if self.find_user_by_email(normalized):
            raise ValueError("email já cadastrado")

        user_id = str(uuid4())
        user = {
            "id": user_id,
            "name": name.strip(),
            "email": normalized,
            "password_hash": pwd_context.hash(password),
        }
        self.users[user_id] = user
        return user

    def find_user_by_email(self, email: str) -> dict | None:
        normalized = normalize_email(email)
        for user in self.users.values():
            if user["email"] == normalized:
                return user
        return None

    def verify_password(self, email: str, password: str) -> dict | None:
        user = self.find_user_by_email(email)
        if user and pwd_context.verify(password, user["password_hash"]):
            return user
        return None

    # ---------- tarefas ----------

    def create_task(self, user_id: str, title: str, description: str, priority: str) -> dict:
        task_id = str(uuid4())
        task = {
            "id": task_id,
            "user_id": user_id,
            "title": title.strip(),
            "description": description.strip(),
            "priority": priority,
            "status": "pendente",
            "created_at": datetime.now(timezone.utc),
        }
        self.tasks[task_id] = task
        return task

    def list_tasks(self, user_id: str) -> list[dict]:
        return [t for t in self.tasks.values() if t["user_id"] == user_id]

    def get_task(self, task_id: str, user_id: str) -> dict | None:
        task = self.tasks.get(task_id)
        if task and task["user_id"] == user_id:
            return task
        return None

    def update_task(self, task_id: str, user_id: str, **fields) -> dict | None:
        task = self.get_task(task_id, user_id)
        if not task:
            return None
        for key, value in fields.items():
            if value is not None:
                task[key] = value.strip() if isinstance(value, str) else value
        return task

    def delete_task(self, task_id: str, user_id: str) -> bool:
        task = self.get_task(task_id, user_id)
        if task:
            del self.tasks[task_id]
            return True
        return False

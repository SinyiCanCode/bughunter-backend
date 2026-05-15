"""API REST do TaskFlow.

Aplicação minimalista usada como sujeito de teste neste portfolio.
Autenticação simplificada via header X-User-Id para fins didáticos
(em produção: JWT ou cookie de sessão).
"""
from fastapi import FastAPI, HTTPException, Header, status
from pydantic import ValidationError

from .models import (
    UserSignup,
    UserLogin,
    UserPublic,
    TaskCreate,
    TaskUpdate,
    TaskPublic,
)
from .storage import Storage


app = FastAPI(title="TaskFlow API", version="1.0.0")
storage = Storage()


# ---------------- Autenticação ----------------

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
def signup(payload: UserSignup):
    try:
        user = storage.create_user(payload.name, payload.email, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return UserPublic(id=user["id"], name=user["name"], email=user["email"])


@app.post("/auth/login")
def login(payload: UserLogin):
    user = storage.verify_password(payload.email, payload.password)
    if not user:
        # Mensagem genérica — evita enumeração de usuários
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )
    return {
        "user": UserPublic(id=user["id"], name=user["name"], email=user["email"]),
        "token": f"fake-token-{user['id']}",  # placeholder didático
    }


# ---------------- Tarefas ----------------

def _require_user(x_user_id: str | None) -> str:
    if not x_user_id or x_user_id not in storage.users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação requerida",
        )
    return x_user_id


@app.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskPublic)
def create_task(payload: TaskCreate, x_user_id: str | None = Header(default=None)):
    user_id = _require_user(x_user_id)
    task = storage.create_task(user_id, payload.title, payload.description, payload.priority)
    return TaskPublic(**task)


@app.get("/tasks", response_model=list[TaskPublic])
def list_tasks(x_user_id: str | None = Header(default=None)):
    user_id = _require_user(x_user_id)
    return [TaskPublic(**t) for t in storage.list_tasks(user_id)]


@app.get("/tasks/{task_id}", response_model=TaskPublic)
def get_task(task_id: str, x_user_id: str | None = Header(default=None)):
    user_id = _require_user(x_user_id)
    task = storage.get_task(task_id, user_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    return TaskPublic(**task)


@app.patch("/tasks/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    x_user_id: str | None = Header(default=None),
):
    user_id = _require_user(x_user_id)
    updated = storage.update_task(task_id, user_id, **payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    return TaskPublic(**updated)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, x_user_id: str | None = Header(default=None)):
    user_id = _require_user(x_user_id)
    if not storage.delete_task(task_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    return None

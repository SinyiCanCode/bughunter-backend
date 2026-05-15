"""Schemas Pydantic para validação e serialização."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator

from .validators import MAX_TASK_TITLE_LENGTH, MAX_TASK_DESCRIPTION_LENGTH, MIN_PASSWORD_LENGTH


class UserSignup(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("senha deve conter ao menos uma letra maiúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("senha deve conter ao menos um número")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    name: str
    email: EmailStr


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=MAX_TASK_TITLE_LENGTH)
    description: str = Field(default="", max_length=MAX_TASK_DESCRIPTION_LENGTH)
    priority: Literal["alta", "media", "baixa"] = "media"


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=MAX_TASK_TITLE_LENGTH)
    description: str | None = Field(default=None, max_length=MAX_TASK_DESCRIPTION_LENGTH)
    priority: Literal["alta", "media", "baixa"] | None = None
    status: Literal["pendente", "concluida"] | None = None


class TaskPublic(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    status: str
    created_at: datetime
    user_id: str

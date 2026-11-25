from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    usuario: str = Field(min_length=1, max_length=50, examples=["admin"])
    senha: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_em: datetime
    usuario: str
    perfil: str

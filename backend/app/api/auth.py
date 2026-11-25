from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AuthServiceDep
from app.schemas.auth import LoginIn, TokenOut

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenOut, summary="Autentica e devolve um token Bearer (R11)")
def login(dados: LoginIn, auth: AuthServiceDep) -> TokenOut:
    emitido = auth.login(dados.usuario, dados.senha)
    return TokenOut(
        access_token=emitido.access_token,
        expira_em=emitido.expira_em,
        usuario=emitido.usuario.username,
        perfil=emitido.usuario.perfil,
    )

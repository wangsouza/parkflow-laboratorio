"""Dependências FastAPI: sessão, serviços e controle de acesso (R11)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.clock import Relogio
from app.core.config import Settings
from app.domain.erros import NaoAutenticado
from app.repositories.configuracao_repository import ConfiguracaoRepository
from app.repositories.estadia_repository import EstadiaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.services.auth import (
    PERFIL_ADMIN,
    AuthService,
    UsuarioAutenticado,
    exigir_perfil,
)
from app.services.estacionamento import EstacionamentoService

_esquema_bearer = HTTPBearer(auto_error=False, description="Token obtido em POST /auth/login")


def obter_sessao(request: Request) -> Iterator[Session]:
    with request.app.state.fabrica_sessoes() as sessao:
        yield sessao


SessaoDep = Annotated[Session, Depends(obter_sessao)]


def obter_auth_service(request: Request, sessao: SessaoDep) -> AuthService:
    settings: Settings = request.app.state.settings
    relogio: Relogio = request.app.state.relogio
    return AuthService(UsuarioRepository(sessao), settings, relogio)


AuthServiceDep = Annotated[AuthService, Depends(obter_auth_service)]


def obter_estacionamento_service(request: Request, sessao: SessaoDep) -> EstacionamentoService:
    settings: Settings = request.app.state.settings
    return EstacionamentoService(
        EstadiaRepository(sessao),
        ConfiguracaoRepository(sessao),
        request.app.state.relogio,
        settings.capacidade_inicial,
        settings.fuso,
    )


EstacionamentoDep = Annotated[EstacionamentoService, Depends(obter_estacionamento_service)]


def obter_usuario_atual(
    auth: AuthServiceDep,
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(_esquema_bearer)],
) -> UsuarioAutenticado:
    if credenciais is None:
        raise NaoAutenticado("Autenticação necessária.")
    return auth.autenticar_token(credenciais.credentials)


UsuarioDep = Annotated[UsuarioAutenticado, Depends(obter_usuario_atual)]


def exigir_admin(usuario: UsuarioDep) -> UsuarioAutenticado:
    exigir_perfil(usuario, PERFIL_ADMIN)
    return usuario


AdminDep = Annotated[UsuarioAutenticado, Depends(exigir_admin)]

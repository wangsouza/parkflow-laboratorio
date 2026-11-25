"""Fábrica da aplicação FastAPI.

Execução local:  ``uvicorn app.main:criar_app --factory --reload``
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Engine

from app import __version__
from app.api import roteador
from app.core.clock import Relogio, RelogioSistema
from app.core.config import Settings, obter_settings
from app.core.database import Base, criar_engine, criar_fabrica_sessoes, garantir_indices
from app.core.errors import registrar_handlers
from app.repositories.usuario_repository import UsuarioRepository
from app.services.auth import AuthService


def criar_app(
    settings: Settings | None = None,
    relogio: Relogio | None = None,
    engine: Engine | None = None,
) -> FastAPI:
    """Monta a aplicação. Parâmetros opcionais permitem injetar dependências nos testes."""
    settings = settings or obter_settings()
    relogio = relogio or RelogioSistema()
    engine = engine or criar_engine(settings.database_url)

    app = FastAPI(
        title="ParkFlow API",
        version=__version__,
        description=(
            "API didática de gestão de estacionamento. Regras de negócio R01–R12 em "
            "`docs/REQUISITOS.md`. Faça login em **POST /auth/login** e use o token em *Authorize*."
        ),
    )
    app.state.settings = settings
    app.state.relogio = relogio
    app.state.engine = engine
    app.state.fabrica_sessoes = criar_fabrica_sessoes(engine)

    Base.metadata.create_all(engine)
    garantir_indices(engine)
    with app.state.fabrica_sessoes() as sessao:
        AuthService(UsuarioRepository(sessao), settings, relogio).semear_usuarios_demo()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origens,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    registrar_handlers(app)
    app.include_router(roteador)

    @app.get("/health", tags=["Infra"], summary="Verificação de saúde")
    def health() -> dict[str, str]:
        return {"status": "ok", "versao": __version__}

    return app

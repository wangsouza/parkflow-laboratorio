"""Configurações da aplicação (variáveis de ambiente com prefixo ``PARKFLOW_`` ou arquivo ``.env``)."""

from __future__ import annotations

from functools import lru_cache
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração. Os valores padrão servem **apenas para demonstração local**."""

    model_config = SettingsConfigDict(env_prefix="PARKFLOW_", env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./parkflow.db"
    capacidade_inicial: int = Field(default=30, ge=1)  # R08
    timezone: str = "America/Sao_Paulo"  # R12

    # R11 — autenticação (demonstração)
    secret_key: str = "demo-apenas-laboratorio-troque-esta-chave-em-qualquer-outro-uso"
    token_expira_minutos: int = Field(default=60, ge=1)
    admin_senha: str = "admin123"
    operador_senha: str = "operador123"
    hash_iteracoes: int = Field(default=200_000, ge=1_000)

    cors_origens: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def fuso(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)


@lru_cache
def obter_settings() -> Settings:
    return Settings()

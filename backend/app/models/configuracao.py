"""Configurações persistidas (ex.: capacidade — R08)."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Configuracao(Base):
    __tablename__ = "configuracoes"

    chave: Mapped[str] = mapped_column(String(50), primary_key=True)
    valor: Mapped[str] = mapped_column(String(255))

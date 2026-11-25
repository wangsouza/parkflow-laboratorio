"""Entidade Estadia: uma passagem de veículo pelo estacionamento (R06, R07, R10)."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Enum, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, DataHoraUTC


class StatusEstadia(str, enum.Enum):
    ATIVA = "ATIVA"
    FINALIZADA = "FINALIZADA"


class Estadia(Base):
    __tablename__ = "estadias"
    __table_args__ = (
        Index("ix_estadias_placa_status", "placa", "status"),
        # R06 garantida pelo BANCO: no máximo uma estadia ATIVA por placa (índice único parcial).
        Index("uq_estadias_placa_ativa", "placa", unique=True, sqlite_where=text("status = 'ATIVA'")),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    placa: Mapped[str] = mapped_column(String(7), index=True)
    entrada_em: Mapped[datetime] = mapped_column(DataHoraUTC, index=True)
    saida_em: Mapped[datetime | None] = mapped_column(DataHoraUTC, nullable=True, index=True)
    status: Mapped[StatusEstadia] = mapped_column(
        Enum(StatusEstadia, native_enum=False, length=12), default=StatusEstadia.ATIVA
    )
    valor_centavos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    operador_entrada: Mapped[str] = mapped_column(String(50))
    operador_saida: Mapped[str | None] = mapped_column(String(50), nullable=True)

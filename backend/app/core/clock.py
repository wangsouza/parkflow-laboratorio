"""Relógio injetável: permite testes determinísticos (sem depender de ``datetime.now``)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol


class Relogio(Protocol):
    def agora(self) -> datetime:
        """Instante atual, **com timezone**."""
        ...


class RelogioSistema:
    """Implementação de produção."""

    def agora(self) -> datetime:
        return datetime.now(timezone.utc)

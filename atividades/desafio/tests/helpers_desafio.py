"""Utilitários dos testes do desafio (caixa-preta, via HTTP)."""

from __future__ import annotations

import random
import string
from datetime import datetime, timedelta, timezone

BRT = timezone(timedelta(hours=-3))  # Brasília
T0 = datetime(2026, 3, 10, 14, 0, tzinfo=BRT)  # instante de referência: use SEMPRE horários explícitos nos testes

_usadas: set[str] = set()


def apos(minutos: float = 0, segundos: float = 0, base: datetime = T0) -> datetime:
    """``apos(15, 1)`` → 15 min 1 s depois de T0."""
    return base + timedelta(minutes=minutos, seconds=segundos)


def iso(instante: datetime) -> str:
    return instante.isoformat()


def placa_unica() -> str:
    """Placa convencional válida e ainda não usada nesta execução (evita colisões entre testes)."""
    while True:
        placa = "".join(random.choices(string.ascii_uppercase, k=3)) + f"{random.randrange(10_000):04d}"
        if placa not in _usadas:
            _usadas.add(placa)
            return placa

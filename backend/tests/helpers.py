"""Utilitários de teste: relógio controlável e atalhos para criar datas com timezone."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

UTC = timezone.utc
BRT = timezone(timedelta(hours=-3))  # America/Sao_Paulo (sem horário de verão atualmente)

# Instante de referência dos testes: 10/03/2026 14:00 em Brasília (17:00 UTC).
ENTRADA_REFERENCIA = datetime(2026, 3, 10, 14, 0, 0, tzinfo=BRT)


class RelogioFixo:
    """Relógio determinístico: devolve sempre o mesmo instante até ser movido."""

    def __init__(self, instante: datetime = ENTRADA_REFERENCIA) -> None:
        self._instante = instante

    def agora(self) -> datetime:
        return self._instante

    def definir(self, instante: datetime) -> None:
        self._instante = instante

    def avancar(self, **kwargs: float) -> datetime:
        """``relogio.avancar(minutes=16)`` → move o relógio e devolve o novo instante."""
        self._instante += timedelta(**kwargs)
        return self._instante


def apos(minutos: float = 0, segundos: float = 0, base: datetime = ENTRADA_REFERENCIA) -> datetime:
    """Instante ``base`` + duração. Útil para montar valores-limite: ``apos(15)``, ``apos(15, 1)``."""
    return base + timedelta(minutes=minutos, seconds=segundos)


def iso(instante: datetime) -> str:
    """Formata para os corpos JSON (ISO-8601 com offset)."""
    return instante.isoformat()


def parse_iso(texto: str) -> datetime:
    """Lê datas devolvidas pela API (ex.: ``2026-03-10T17:00:00Z``) como ``datetime`` aware."""
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))

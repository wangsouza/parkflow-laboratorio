"""R12 — limites do "dia" civil em um fuso horário."""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


def limites_do_dia(instante: datetime, fuso: ZoneInfo) -> tuple[datetime, datetime]:
    """Retorna ``(inicio, fim)`` em UTC do dia local que contém ``instante``.

    O intervalo é **fechado à esquerda e aberto à direita**: ``inicio <= t < fim``.
    """
    if instante.tzinfo is None:
        raise ValueError("instante deve ter timezone explícito")
    local = instante.astimezone(fuso)
    inicio_local = datetime.combine(local.date(), time.min, tzinfo=fuso)
    fim_local = datetime.combine(local.date() + timedelta(days=1), time.min, tzinfo=fuso)
    return inicio_local.astimezone(timezone.utc), fim_local.astimezone(timezone.utc)

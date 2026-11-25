from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import AwareDatetime

from app.api.deps import EstacionamentoDep, UsuarioDep
from app.models import StatusEstadia
from app.schemas.estadia import EstadiaOut, HistoricoOut

router = APIRouter(prefix="/historico", tags=["Histórico"])


@router.get("", response_model=HistoricoOut, summary="Histórico filtrável (R10)")
def consultar_historico(
    servico: EstacionamentoDep,
    _: UsuarioDep,
    placa: str | None = None,
    status: StatusEstadia | None = None,
    de: Annotated[AwareDatetime | None, Query(description="Entrada a partir de (inclusive).")] = None,
    ate: Annotated[AwareDatetime | None, Query(description="Entrada até (inclusive).")] = None,
    limite: Annotated[int, Query(ge=1, le=500)] = 100,
    deslocamento: Annotated[int, Query(ge=0)] = 0,
) -> HistoricoOut:
    itens, total = servico.historico(placa, status, de, ate, limite, deslocamento)
    return HistoricoOut(
        total=total,
        limite=limite,
        deslocamento=deslocamento,
        itens=[EstadiaOut.model_validate(i) for i in itens],
    )

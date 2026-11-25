from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import EstacionamentoDep, UsuarioDep
from app.schemas.estadia import SimulacaoIn, TarifaOut

router = APIRouter(prefix="/tarifas", tags=["Tarifas"])


@router.post("/simular", response_model=TarifaOut, summary="Simula a tarifa (R01–R05)")
def simular(dados: SimulacaoIn, servico: EstacionamentoDep, _: UsuarioDep) -> TarifaOut:
    return TarifaOut.de_resultado(servico.simular_tarifa(dados.entrada_em, dados.saida_em))

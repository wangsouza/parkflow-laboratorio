from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter

from app.api.deps import AdminDep, EstacionamentoDep, UsuarioDep
from app.schemas.dashboard import CapacidadeIn, CapacidadeOut, ResumoOut

router = APIRouter(tags=["Painel"])


@router.get("/dashboard/resumo", response_model=ResumoOut, summary="Indicadores do dia (R12)")
def resumo(servico: EstacionamentoDep, _: UsuarioDep) -> ResumoOut:
    return ResumoOut(**asdict(servico.resumo_do_dia()))


@router.get("/configuracao", response_model=CapacidadeOut, summary="Configuração atual")
def obter_configuracao(servico: EstacionamentoDep, _: UsuarioDep) -> CapacidadeOut:
    return CapacidadeOut(capacidade=servico.capacidade())


@router.put(
    "/configuracao/capacidade",
    response_model=CapacidadeOut,
    summary="Altera a capacidade — somente admin (R08, R11)",
)
def alterar_capacidade(dados: CapacidadeIn, servico: EstacionamentoDep, _: AdminDep) -> CapacidadeOut:
    return CapacidadeOut(capacidade=servico.definir_capacidade(dados.capacidade))

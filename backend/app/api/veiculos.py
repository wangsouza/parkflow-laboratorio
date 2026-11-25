from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import EstacionamentoDep, UsuarioDep
from app.schemas.estadia import (
    EntradaIn,
    EstadiaAtivaOut,
    EstadiaOut,
    SaidaIn,
    SaidaOut,
    TarifaOut,
)
from app.services.estacionamento import EstadiaAtiva

router = APIRouter(prefix="/veiculos", tags=["Veículos"])


def _ativa_out(ativa: EstadiaAtiva) -> EstadiaAtivaOut:
    return EstadiaAtivaOut(
        estadia=EstadiaOut.model_validate(ativa.estadia),
        tarifa_parcial=TarifaOut.de_resultado(ativa.tarifa_parcial),
    )


@router.post(
    "/entrada",
    response_model=EstadiaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registra a entrada de um veículo (R06, R08, R09)",
)
def registrar_entrada(dados: EntradaIn, servico: EstacionamentoDep, usuario: UsuarioDep) -> EstadiaOut:
    estadia = servico.registrar_entrada(dados.placa, usuario.username, dados.entrada_em)
    return EstadiaOut.model_validate(estadia)


@router.get("/ativos", response_model=list[EstadiaAtivaOut], summary="Veículos estacionados")
def listar_ativos(servico: EstacionamentoDep, _: UsuarioDep) -> list[EstadiaAtivaOut]:
    return [_ativa_out(a) for a in servico.listar_ativas()]


@router.post("/saida", response_model=SaidaOut, summary="Registra a saída e cobra a tarifa (R07)")
def registrar_saida(dados: SaidaIn, servico: EstacionamentoDep, usuario: UsuarioDep) -> SaidaOut:
    comprovante = servico.registrar_saida(dados.placa, usuario.username, dados.saida_em)
    return SaidaOut(
        estadia=EstadiaOut.model_validate(comprovante.estadia),
        tarifa=TarifaOut.de_resultado(comprovante.tarifa),
    )


@router.get(
    "/{placa}",
    response_model=EstadiaAtivaOut,
    summary="Consulta a estadia ativa de uma placa (com tarifa parcial)",
)
def consultar_veiculo(placa: str, servico: EstacionamentoDep, _: UsuarioDep) -> EstadiaAtivaOut:
    return _ativa_out(servico.consultar_ativa(placa))

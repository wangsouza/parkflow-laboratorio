from __future__ import annotations

from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.domain.tarifa import ResultadoTarifa
from app.models import StatusEstadia
from app.schemas.comum import Placa


class EntradaIn(BaseModel):
    placa: Placa
    entrada_em: AwareDatetime | None = Field(
        default=None, description="Opcional; padrão = agora. Exige timezone."
    )


class SaidaIn(BaseModel):
    placa: Placa
    saida_em: AwareDatetime | None = Field(
        default=None, description="Opcional; padrão = agora. Exige timezone."
    )


class SimulacaoIn(BaseModel):
    entrada_em: AwareDatetime
    saida_em: AwareDatetime


class TarifaOut(BaseModel):
    permanencia_segundos: int
    valor_centavos: int | None
    atendimento_manual: bool
    regra: str = Field(description="Regra que determinou o valor: R01, R02, R03 ou R04.")
    mensagem: str | None = None

    @classmethod
    def de_resultado(cls, resultado: ResultadoTarifa) -> TarifaOut:
        return cls(
            permanencia_segundos=resultado.permanencia_segundos,
            valor_centavos=resultado.valor_centavos,
            atendimento_manual=resultado.atendimento_manual,
            regra=resultado.regra,
            mensagem=resultado.mensagem,
        )


class EstadiaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    placa: str
    entrada_em: datetime
    saida_em: datetime | None
    status: StatusEstadia
    valor_centavos: int | None
    operador_entrada: str
    operador_saida: str | None


class EstadiaAtivaOut(BaseModel):
    estadia: EstadiaOut
    tarifa_parcial: TarifaOut


class SaidaOut(BaseModel):
    estadia: EstadiaOut
    tarifa: TarifaOut


class HistoricoOut(BaseModel):
    total: int
    limite: int
    deslocamento: int
    itens: list[EstadiaOut]

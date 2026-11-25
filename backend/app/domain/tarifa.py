"""R01–R05 — cálculo de tarifa. Funções puras: sem banco, sem relógio, sem HTTP.

Todos os valores em **centavos inteiros**; a duração usa ``timedelta`` (resolução de segundos).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.domain.erros import PeriodoInvalido

# --- Parâmetros de negócio (centavos / durações) -----------------------------------------
TOLERANCIA_GRATUITA = timedelta(minutes=15)  # R01
PRIMEIRA_HORA = timedelta(hours=1)  # R02
HORA_ADICIONAL = timedelta(hours=1)  # R03
LIMITE_AUTOMATICO = timedelta(hours=24)  # R04

VALOR_PRIMEIRA_HORA_CENTAVOS = 800  # R02
VALOR_HORA_ADICIONAL_CENTAVOS = 500  # R03
TARIFA_MAXIMA_CENTAVOS = 3000  # R04

MENSAGEM_ATENDIMENTO_MANUAL = (
    "Permanência superior a 24 horas: encaminhe o cliente ao atendimento manual."
)


@dataclass(frozen=True)
class ResultadoTarifa:
    """Resultado do cálculo de tarifa.

    Attributes:
        permanencia_segundos: tempo efetivamente decorrido.
        valor_centavos: valor a cobrar; ``None`` quando ``atendimento_manual``.
        atendimento_manual: ``True`` para permanências > 24 h (R04).
        regra: identificador da regra que determinou o valor (R01..R04).
    """

    permanencia_segundos: int
    valor_centavos: int | None
    atendimento_manual: bool
    regra: str

    @property
    def mensagem(self) -> str | None:
        return MENSAGEM_ATENDIMENTO_MANUAL if self.atendimento_manual else None


def calcular_permanencia(entrada: datetime, saida: datetime) -> timedelta:
    """Tempo efetivamente decorrido entre ``entrada`` e ``saida`` (R05).

    Raises:
        PeriodoInvalido: datas sem timezone ou saída anterior à entrada.
    """
    if entrada.tzinfo is None or saida.tzinfo is None:
        raise PeriodoInvalido("Entrada e saída devem informar timezone explícito.")
    # Subtrair datetimes que compartilham o MESMO tzinfo usa o relógio de parede (ignora horário de verão):
    # normalizar para UTC dá o tempo efetivamente decorrido.
    permanencia = saida.astimezone(timezone.utc) - entrada.astimezone(timezone.utc)
    if permanencia < timedelta(0):
        raise PeriodoInvalido("A saída não pode ser anterior à entrada.")
    return permanencia


def _divisao_teto(dividendo: timedelta, divisor: timedelta) -> int:
    """Teto da divisão entre durações, em aritmética inteira (sem float)."""
    return -(-dividendo // divisor)


def horas_adicionais_iniciadas(permanencia: timedelta) -> int:
    """Quantidade de horas adicionais *iniciadas* após a primeira hora (R03)."""
    excedente = permanencia - PRIMEIRA_HORA
    if excedente <= timedelta(0):
        return 0
    return _divisao_teto(excedente, HORA_ADICIONAL)


def calcular_tarifa(entrada: datetime, saida: datetime) -> ResultadoTarifa:
    """Calcula a tarifa de uma permanência.

    Ordem de avaliação: R05 (consistência) → R04 (limite automático) → R01 (tolerância)
    → R02/R03 (primeira hora + adicionais) → R04 (teto diário).

    Raises:
        PeriodoInvalido: R05.
    """
    permanencia = calcular_permanencia(entrada, saida)
    segundos = int(permanencia.total_seconds())

    if permanencia > LIMITE_AUTOMATICO:
        return ResultadoTarifa(segundos, None, True, "R04")

    if permanencia <= TOLERANCIA_GRATUITA:
        return ResultadoTarifa(segundos, 0, False, "R01")

    adicionais = horas_adicionais_iniciadas(permanencia)
    total = VALOR_PRIMEIRA_HORA_CENTAVOS + adicionais * VALOR_HORA_ADICIONAL_CENTAVOS
    valor = min(total, TARIFA_MAXIMA_CENTAVOS)

    if total > TARIFA_MAXIMA_CENTAVOS:
        regra = "R04"
    elif adicionais == 0:
        regra = "R02"
    else:
        regra = "R03"
    return ResultadoTarifa(segundos, valor, False, regra)

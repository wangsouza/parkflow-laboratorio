"""Serviço de estacionamento: orquestra regras de domínio, repositórios e relógio.

As regras de cálculo ficam em ``app.domain``; aqui vivem as regras que dependem de estado
(R06 duplicidade, R07 saída, R08 capacidade, R12 indicadores).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.clock import Relogio
from app.domain.erros import (
    AtendimentoManual,
    CapacidadeInsuficiente,
    CapacidadeInvalida,
    EstacionamentoLotado,
    EstadiaAtivaNaoEncontrada,
    PlacaJaEstacionada,
)
from app.domain.periodo import limites_do_dia
from app.domain.placa import normalizar_placa
from app.domain.tarifa import ResultadoTarifa, calcular_tarifa
from app.models import Estadia, StatusEstadia
from app.repositories.configuracao_repository import ConfiguracaoRepository
from app.repositories.estadia_repository import EstadiaRepository

CHAVE_CAPACIDADE = "capacidade"
CAPACIDADE_MINIMA = 1
CAPACIDADE_MAXIMA = 500


@dataclass(frozen=True)
class ComprovanteSaida:
    estadia: Estadia
    tarifa: ResultadoTarifa


@dataclass(frozen=True)
class EstadiaAtiva:
    estadia: Estadia
    tarifa_parcial: ResultadoTarifa


@dataclass(frozen=True)
class ResumoDia:
    data_referencia: str
    capacidade: int
    ocupadas: int
    vagas_disponiveis: int
    entradas_hoje: int
    saidas_hoje: int
    arrecadado_hoje_centavos: int


class EstacionamentoService:
    def __init__(
        self,
        estadias: EstadiaRepository,
        configuracoes: ConfiguracaoRepository,
        relogio: Relogio,
        capacidade_padrao: int,
        fuso: ZoneInfo,
    ) -> None:
        self._estadias = estadias
        self._configuracoes = configuracoes
        self._relogio = relogio
        self._capacidade_padrao = capacidade_padrao
        self._fuso = fuso

    # --- Consistência sob concorrência (R06, R07, R08) ------------------------------------
    def _na_transacao_de_escrita[T](self, operacao: Callable[[], T]) -> T:
        """Executa ``operacao`` dentro de uma transação que já detém o bloqueio de escrita do BANCO.

        Verificar ("há vaga? já está estacionado? está ativa?") e gravar viram um passo atômico, mesmo entre
        processos. Em qualquer erro a transação é desfeita, liberando o bloqueio imediatamente.
        """
        self._estadias.iniciar_escrita()
        try:
            return operacao()
        except Exception:
            self._estadias.rollback()
            raise

    # --- Capacidade (R08) ---------------------------------------------------------------
    def capacidade(self) -> int:
        valor = self._configuracoes.obter(CHAVE_CAPACIDADE)
        return self._capacidade_padrao if valor is None else int(valor)

    def definir_capacidade(self, nova_capacidade: int) -> int:
        """Altera a capacidade (somente admin — verificado na API).

        Raises:
            CapacidadeInvalida: fora de 1..500.
            CapacidadeInsuficiente: menor que os veículos atualmente estacionados.
        """
        if not CAPACIDADE_MINIMA <= nova_capacidade <= CAPACIDADE_MAXIMA:
            raise CapacidadeInvalida(
                f"A capacidade deve estar entre {CAPACIDADE_MINIMA} e {CAPACIDADE_MAXIMA}."
            )
        return self._na_transacao_de_escrita(lambda: self._gravar_capacidade(nova_capacidade))

    def _gravar_capacidade(self, nova_capacidade: int) -> int:
        ocupadas = self._estadias.contar_ativas()
        if nova_capacidade < ocupadas:
            raise CapacidadeInsuficiente(
                f"Há {ocupadas} veículos estacionados; a capacidade não pode ser menor."
            )
        self._configuracoes.definir(CHAVE_CAPACIDADE, str(nova_capacidade))
        self._configuracoes.commit()
        return nova_capacidade

    # --- Entrada (R06, R08, R09) ----------------------------------------------------------
    def registrar_entrada(
        self, placa: str, operador: str, entrada_em: datetime | None = None
    ) -> Estadia:
        """Registra a entrada de um veículo.

        Ordem das verificações: placa (R09) → duplicidade (R06) → capacidade (R08).
        """
        placa_normalizada = normalizar_placa(placa)
        return self._na_transacao_de_escrita(
            lambda: self._inserir_entrada(placa_normalizada, operador, entrada_em)
        )

    def _inserir_entrada(
        self, placa_normalizada: str, operador: str, entrada_em: datetime | None
    ) -> Estadia:
        if self._estadias.buscar_ativa_por_placa(placa_normalizada) is not None:
            raise PlacaJaEstacionada(f"O veículo {placa_normalizada} já está estacionado.")

        if self._estadias.contar_ativas() >= self.capacidade():
            raise EstacionamentoLotado("Estacionamento lotado: não há vagas disponíveis.")

        estadia = Estadia(
            placa=placa_normalizada,
            entrada_em=entrada_em or self._relogio.agora(),
            status=StatusEstadia.ATIVA,
            operador_entrada=operador,
        )
        self._estadias.adicionar(estadia)
        self._estadias.commit()
        return estadia

    # --- Consultas -----------------------------------------------------------------------
    def listar_ativas(self) -> list[EstadiaAtiva]:
        agora = self._relogio.agora()
        return [
            EstadiaAtiva(e, self._tarifa_parcial(e, agora)) for e in self._estadias.listar_ativas()
        ]

    def consultar_ativa(self, placa: str) -> EstadiaAtiva:
        placa_normalizada = normalizar_placa(placa)
        estadia = self._estadias.buscar_ativa_por_placa(placa_normalizada)
        if estadia is None:
            raise EstadiaAtivaNaoEncontrada(
                f"Não há estadia ativa para a placa {placa_normalizada}."
            )
        return EstadiaAtiva(estadia, self._tarifa_parcial(estadia, self._relogio.agora()))

    def _tarifa_parcial(self, estadia: Estadia, agora: datetime) -> ResultadoTarifa:
        """Tarifa se o veículo saísse agora. Entrada futura é tratada como duração zero."""
        referencia = max(agora, estadia.entrada_em)
        return calcular_tarifa(estadia.entrada_em, referencia)

    # --- Tarifa e saída (R01–R05, R07) -----------------------------------------------------
    def simular_tarifa(self, entrada_em: datetime, saida_em: datetime) -> ResultadoTarifa:
        return calcular_tarifa(entrada_em, saida_em)

    def registrar_saida(
        self, placa: str, operador: str, saida_em: datetime | None = None
    ) -> ComprovanteSaida:
        """Encerra a estadia ativa da placa.

        Raises:
            EstadiaAtivaNaoEncontrada: R07 (inclui a segunda tentativa de encerramento).
            PeriodoInvalido: R05.
            AtendimentoManual: R04 (> 24 h) — estadia permanece ativa.
        """
        placa_normalizada = normalizar_placa(placa)
        return self._na_transacao_de_escrita(
            lambda: self._encerrar_estadia(placa_normalizada, operador, saida_em)
        )

    def _encerrar_estadia(
        self, placa_normalizada: str, operador: str, saida_em: datetime | None
    ) -> ComprovanteSaida:
        estadia = self._estadias.buscar_ativa_por_placa(placa_normalizada)
        if estadia is None:
            raise EstadiaAtivaNaoEncontrada(
                f"Não há estadia ativa para a placa {placa_normalizada}."
            )

        instante = saida_em or self._relogio.agora()
        tarifa = calcular_tarifa(estadia.entrada_em, instante)
        if tarifa.atendimento_manual:
            raise AtendimentoManual(tarifa.mensagem or "Atendimento manual necessário.")

        estadia.saida_em = instante
        estadia.valor_centavos = tarifa.valor_centavos
        estadia.status = StatusEstadia.FINALIZADA
        estadia.operador_saida = operador
        self._estadias.commit()
        return ComprovanteSaida(estadia, tarifa)

    # --- Histórico (R10) e indicadores (R12) ------------------------------------------------
    def historico(
        self,
        placa: str | None = None,
        status: StatusEstadia | None = None,
        de: datetime | None = None,
        ate: datetime | None = None,
        limite: int = 100,
        deslocamento: int = 0,
    ) -> tuple[list[Estadia], int]:
        placa_normalizada = normalizar_placa(placa) if placa else None
        return self._estadias.historico(
            placa=placa_normalizada,
            status=status,
            de=de,
            ate=ate,
            limite=limite,
            deslocamento=deslocamento,
        )

    def resumo_do_dia(self) -> ResumoDia:
        agora = self._relogio.agora()
        inicio, fim = limites_do_dia(agora, self._fuso)
        capacidade = self.capacidade()
        ocupadas = self._estadias.contar_ativas()
        return ResumoDia(
            data_referencia=agora.astimezone(self._fuso).date().isoformat(),
            capacidade=capacidade,
            ocupadas=ocupadas,
            vagas_disponiveis=capacidade - ocupadas,
            entradas_hoje=self._estadias.contar_entradas_entre(inicio, fim),
            saidas_hoje=self._estadias.contar_saidas_entre(inicio, fim),
            arrecadado_hoje_centavos=self._estadias.somar_arrecadado_entre(inicio, fim),
        )

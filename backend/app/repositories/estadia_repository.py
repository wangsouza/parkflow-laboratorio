"""Acesso a dados de estadias. Sem regra de negócio: apenas consultas e gravações."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import OPCAO_ESCRITA
from app.domain.erros import PlacaJaEstacionada
from app.models import Estadia, StatusEstadia


class EstadiaRepository:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def iniciar_escrita(self) -> None:
        """Abre a transação já com o bloqueio de escrita do banco (``BEGIN IMMEDIATE`` no SQLite).

        Deve ser a PRIMEIRA operação da sessão: tudo que for lido depois (duplicidade, vagas, estadia ativa) fica
        protegido contra outras conexões até o ``commit``/``rollback``.
        """
        self._sessao.connection(execution_options={OPCAO_ESCRITA: True})

    def adicionar(self, estadia: Estadia) -> Estadia:
        """Insere e sincroniza com o banco.

        Raises:
            PlacaJaEstacionada: o índice único parcial recusou uma 2ª estadia ativa da mesma placa (R06).
        """
        try:
            with self._sessao.begin_nested():  # SAVEPOINT: a violação não desfaz o restante da transação
                self._sessao.add(estadia)
            return estadia
        except IntegrityError as exc:
            raise PlacaJaEstacionada(f"O veículo {estadia.placa} já está estacionado.") from exc

    def buscar_ativa_por_placa(self, placa: str) -> Estadia | None:
        consulta = select(Estadia).where(
            Estadia.placa == placa, Estadia.status == StatusEstadia.ATIVA
        )
        return self._sessao.scalars(consulta).first()

    def listar_ativas(self) -> list[Estadia]:
        consulta = (
            select(Estadia)
            .where(Estadia.status == StatusEstadia.ATIVA)
            .order_by(Estadia.entrada_em, Estadia.id)
        )
        return list(self._sessao.scalars(consulta))

    def contar_ativas(self) -> int:
        consulta = select(func.count()).select_from(Estadia).where(
            Estadia.status == StatusEstadia.ATIVA
        )
        return int(self._sessao.scalar(consulta) or 0)

    def historico(
        self,
        placa: str | None = None,
        status: StatusEstadia | None = None,
        de: datetime | None = None,
        ate: datetime | None = None,
        limite: int = 100,
        deslocamento: int = 0,
    ) -> tuple[list[Estadia], int]:
        """Estadias filtradas (R10) da mais recente para a mais antiga + total sem paginação.

        ``de``/``ate`` filtram ``entrada_em`` com limites **inclusivos**.
        """
        filtros = []
        if placa is not None:
            filtros.append(Estadia.placa == placa)
        if status is not None:
            filtros.append(Estadia.status == status)
        if de is not None:
            filtros.append(Estadia.entrada_em >= de)
        if ate is not None:
            filtros.append(Estadia.entrada_em <= ate)

        total = int(
            self._sessao.scalar(select(func.count()).select_from(Estadia).where(*filtros)) or 0
        )
        consulta = (
            select(Estadia)
            .where(*filtros)
            .order_by(Estadia.entrada_em.desc(), Estadia.id.desc())
            .limit(limite)
            .offset(deslocamento)
        )
        return list(self._sessao.scalars(consulta)), total

    def contar_entradas_entre(self, inicio: datetime, fim: datetime) -> int:
        """Entradas com ``inicio <= entrada_em < fim``."""
        consulta = select(func.count()).select_from(Estadia).where(
            Estadia.entrada_em >= inicio, Estadia.entrada_em < fim
        )
        return int(self._sessao.scalar(consulta) or 0)

    def contar_saidas_entre(self, inicio: datetime, fim: datetime) -> int:
        """Saídas com ``inicio <= saida_em < fim``."""
        consulta = select(func.count()).select_from(Estadia).where(
            Estadia.status == StatusEstadia.FINALIZADA,
            Estadia.saida_em >= inicio,
            Estadia.saida_em < fim,
        )
        return int(self._sessao.scalar(consulta) or 0)

    def somar_arrecadado_entre(self, inicio: datetime, fim: datetime) -> int:
        """Soma (centavos) dos valores cobrados em saídas com ``inicio <= saida_em < fim``."""
        consulta = select(func.coalesce(func.sum(Estadia.valor_centavos), 0)).where(
            Estadia.status == StatusEstadia.FINALIZADA,
            Estadia.saida_em >= inicio,
            Estadia.saida_em < fim,
        )
        return int(self._sessao.scalar(consulta) or 0)

    def commit(self) -> None:
        self._sessao.commit()

    def rollback(self) -> None:
        self._sessao.rollback()

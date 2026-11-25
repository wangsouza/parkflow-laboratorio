"""Infraestrutura SQLAlchemy: engine, sessões e tipo de data/hora UTC."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Engine, create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.types import TypeDecorator


class Base(DeclarativeBase):
    """Base declarativa dos modelos."""


class DataHoraUTC(TypeDecorator[datetime]):
    """Exige datas com timezone, grava em UTC e devolve sempre ``datetime`` aware (UTC)."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: object) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("datetime sem timezone não pode ser persistido")
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect: object) -> datetime | None:
        return None if value is None else value.replace(tzinfo=timezone.utc)


#: Opção de execução que pede transação de escrita antecipada (veja ``EstadiaRepository.iniciar_escrita``).
OPCAO_ESCRITA = "parkflow_escrita"


def _configurar_transacoes_sqlite(engine: Engine) -> None:
    """Controla o ``BEGIN`` do SQLite (receita oficial do SQLAlchemy para o driver ``pysqlite``).

    Por padrão o driver só abre a transação na primeira escrita; uma decisão baseada em *leituras* (ex.: "há vaga?")
    ficaria desprotegida contra outra conexão. Com ``BEGIN IMMEDIATE`` o bloqueio de escrita do **banco** é obtido
    antes das leituras, serializando entre threads **e processos**. As demais transações seguem ``DEFERRED``.
    """

    @event.listens_for(engine, "connect")
    def _ao_conectar(conexao_dbapi, _registro) -> None:  # type: ignore[no-untyped-def]
        conexao_dbapi.isolation_level = None  # o SQLAlchemy emite o BEGIN (abaixo)

    @event.listens_for(engine, "begin")
    def _ao_iniciar(conexao) -> None:  # type: ignore[no-untyped-def]
        modo = "IMMEDIATE" if conexao.get_execution_options().get(OPCAO_ESCRITA) else "DEFERRED"
        conexao.exec_driver_sql(f"BEGIN {modo}")


def criar_engine(url: str) -> Engine:
    """Cria o engine. ``sqlite://`` (memória) usa ``StaticPool`` para compartilhar a conexão."""
    if url in ("sqlite://", "sqlite:///:memory:"):
        engine = create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    elif url.startswith("sqlite"):
        # timeout: tempo que uma escrita espera o bloqueio de outra (em vez de falhar com "database is locked")
        engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 30})
    else:
        return create_engine(url)
    _configurar_transacoes_sqlite(engine)
    return engine


def garantir_indices(engine: Engine) -> None:
    """Cria índices declarados nos modelos que ainda não existem (bancos criados por versões anteriores).

    ``create_all`` ignora tabelas já existentes, portanto não adicionaria o índice único parcial a um banco antigo.
    Não altera nem apaga dados.

    Raises:
        RuntimeError: se já existirem registros que violam um índice único (ex.: estadias ativas duplicadas).
    """
    for tabela in Base.metadata.sorted_tables:
        for indice in tabela.indexes:
            try:
                indice.create(engine, checkfirst=True)
            except IntegrityError as exc:
                raise RuntimeError(
                    f"Não foi possível criar o índice único '{indice.name}': a tabela '{tabela.name}' já contém "
                    "registros duplicados (ex.: mais de uma estadia ATIVA para a mesma placa). Nenhum dado foi alterado; "
                    "corrija os duplicados e inicie novamente."
                ) from exc


def criar_fabrica_sessoes(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)

"""Erros de negócio. Independentes de HTTP: o mapeamento para status fica em ``core.errors``."""

from __future__ import annotations


class ErroDominio(Exception):
    """Base de todos os erros de regra de negócio."""

    codigo: str = "ERRO_DOMINIO"

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem


class PlacaInvalida(ErroDominio):
    """R09 — placa fora dos formatos convencional/Mercosul."""

    codigo = "PLACA_INVALIDA"


class PeriodoInvalido(ErroDominio):
    """R05 — saída anterior à entrada ou datas sem timezone."""

    codigo = "PERIODO_INVALIDO"


class PlacaJaEstacionada(ErroDominio):
    """R06 — já existe estadia ativa para a placa."""

    codigo = "PLACA_JA_ESTACIONADA"


class EstacionamentoLotado(ErroDominio):
    """R08 — todas as vagas ocupadas."""

    codigo = "ESTACIONAMENTO_LOTADO"


class EstadiaAtivaNaoEncontrada(ErroDominio):
    """R07 — não há estadia ativa para a placa."""

    codigo = "ESTADIA_ATIVA_NAO_ENCONTRADA"


class AtendimentoManual(ErroDominio):
    """R04 — permanência acima de 24 h: requer atendimento manual."""

    codigo = "ATENDIMENTO_MANUAL"


class CapacidadeInvalida(ErroDominio):
    """R08 — capacidade fora do intervalo permitido."""

    codigo = "CAPACIDADE_INVALIDA"


class CapacidadeInsuficiente(ErroDominio):
    """R08 — nova capacidade menor que o número de veículos estacionados."""

    codigo = "CAPACIDADE_INSUFICIENTE"


class CredenciaisInvalidas(ErroDominio):
    """R11 — usuário/senha incorretos."""

    codigo = "CREDENCIAIS_INVALIDAS"


class NaoAutenticado(ErroDominio):
    """R11 — token ausente, inválido ou expirado."""

    codigo = "NAO_AUTENTICADO"


class AcessoNegado(ErroDominio):
    """R11 — perfil sem permissão para a operação."""

    codigo = "ACESSO_NEGADO"

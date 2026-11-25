"""Acesso a configurações persistidas."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Configuracao


class ConfiguracaoRepository:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def obter(self, chave: str) -> str | None:
        registro = self._sessao.get(Configuracao, chave)
        return None if registro is None else registro.valor

    def definir(self, chave: str, valor: str) -> None:
        registro = self._sessao.get(Configuracao, chave)
        if registro is None:
            self._sessao.add(Configuracao(chave=chave, valor=valor))
        else:
            registro.valor = valor
        self._sessao.flush()

    def commit(self) -> None:
        self._sessao.commit()

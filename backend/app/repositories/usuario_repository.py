"""Acesso a usuários."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Usuario


class UsuarioRepository:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def buscar_por_username(self, username: str) -> Usuario | None:
        return self._sessao.scalars(select(Usuario).where(Usuario.username == username)).first()

    def salvar(self, username: str, password_hash: str, perfil: str) -> Usuario:
        """Cria ou atualiza (upsert por ``username``)."""
        usuario = self.buscar_por_username(username)
        if usuario is None:
            usuario = Usuario(username=username, password_hash=password_hash, perfil=perfil)
            self._sessao.add(usuario)
        else:
            usuario.password_hash = password_hash
            usuario.perfil = perfil
        self._sessao.flush()
        return usuario

    def commit(self) -> None:
        self._sessao.commit()

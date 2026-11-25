"""R11 — autenticação (login, token) e carga dos usuários de demonstração."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache

from app.core.clock import Relogio
from app.core.config import Settings
from app.core.security import (
    criar_token,
    decodificar_token,
    gerar_hash_senha,
    verificar_senha,
)
from app.domain.erros import AcessoNegado, CredenciaisInvalidas
from app.repositories.usuario_repository import UsuarioRepository

PERFIL_ADMIN = "admin"
PERFIL_OPERADOR = "operador"


@dataclass(frozen=True)
class UsuarioAutenticado:
    username: str
    perfil: str


@dataclass(frozen=True)
class TokenEmitido:
    access_token: str
    expira_em: datetime
    usuario: UsuarioAutenticado


@lru_cache(maxsize=8)
def hash_isca(iteracoes: int) -> str:
    """Hash "isca": mantém o tempo de resposta parecido quando o usuário não existe (anti-enumeração).

    Calculado UMA vez por configuração de iterações (e aquecido na inicialização) — nunca por requisição.
    """
    return gerar_hash_senha("isca", iteracoes)


class AuthService:
    def __init__(self, usuarios: UsuarioRepository, settings: Settings, relogio: Relogio) -> None:
        self._usuarios = usuarios
        self._settings = settings
        self._relogio = relogio

    def semear_usuarios_demo(self) -> None:
        """Grava/atualiza ``admin`` e ``operador`` com as senhas configuradas (sempre com hash)."""
        s = self._settings
        self._usuarios.salvar("admin", gerar_hash_senha(s.admin_senha, s.hash_iteracoes), PERFIL_ADMIN)
        self._usuarios.salvar(
            "operador", gerar_hash_senha(s.operador_senha, s.hash_iteracoes), PERFIL_OPERADOR
        )
        self._usuarios.commit()
        hash_isca(s.hash_iteracoes)  # aquece o cache fora do caminho das requisições

    def login(self, username: str, senha: str) -> TokenEmitido:
        usuario = self._usuarios.buscar_por_username(username)
        hash_comparado = usuario.password_hash if usuario else hash_isca(self._settings.hash_iteracoes)
        senha_ok = verificar_senha(senha, hash_comparado)
        if usuario is None or not senha_ok:
            raise CredenciaisInvalidas("Usuário ou senha inválidos.")
        token, expira_em = criar_token(
            usuario.username,
            usuario.perfil,
            self._settings.secret_key,
            self._settings.token_expira_minutos,
            self._relogio.agora(),
        )
        return TokenEmitido(token, expira_em, UsuarioAutenticado(usuario.username, usuario.perfil))

    def autenticar_token(self, token: str) -> UsuarioAutenticado:
        dados = decodificar_token(token, self._settings.secret_key, self._relogio.agora())
        return UsuarioAutenticado(dados["sub"], dados["perfil"])


def exigir_perfil(usuario: UsuarioAutenticado, perfil_necessario: str) -> None:
    """Levanta ``AcessoNegado`` se o usuário não tiver o perfil exigido."""
    if usuario.perfil != perfil_necessario:
        raise AcessoNegado("Seu perfil não tem permissão para esta operação.")

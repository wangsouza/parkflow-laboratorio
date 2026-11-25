"""R11 — hash de senha (PBKDF2-SHA256 + salt) e tokens JWT."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

import jwt

from app.domain.erros import NaoAutenticado

ALGORITMO_JWT = "HS256"
_PREFIXO = "pbkdf2_sha256"


def gerar_hash_senha(senha: str, iteracoes: int = 200_000) -> str:
    """Gera ``pbkdf2_sha256$<iterações>$<salt_b64>$<hash_b64>``."""
    salt = secrets.token_bytes(16)
    derivado = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, iteracoes)
    return "$".join(
        [_PREFIXO, str(iteracoes), base64.b64encode(salt).decode(), base64.b64encode(derivado).decode()]
    )


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Compara em tempo constante. Hash malformado → ``False`` (nunca levanta)."""
    try:
        prefixo, iteracoes, salt_b64, hash_b64 = hash_armazenado.split("$")
        if prefixo != _PREFIXO:
            return False
        salt = base64.b64decode(salt_b64)
        esperado = base64.b64decode(hash_b64)
        derivado = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, int(iteracoes))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(derivado, esperado)


def criar_token(
    usuario: str, perfil: str, segredo: str, expira_minutos: int, agora: datetime
) -> tuple[str, datetime]:
    """Cria um JWT assinado. Retorna ``(token, expira_em)``."""
    expira_em = agora + timedelta(minutes=expira_minutos)
    payload = {
        "sub": usuario,
        "perfil": perfil,
        "iat": int(agora.timestamp()),
        "exp": int(expira_em.timestamp()),
    }
    return jwt.encode(payload, segredo, algorithm=ALGORITMO_JWT), expira_em


def decodificar_token(token: str, segredo: str, agora: datetime) -> dict[str, str]:
    """Valida assinatura e expiração (usando ``agora`` injetado).

    Raises:
        NaoAutenticado: token inválido, adulterado ou expirado.
    """
    try:
        payload = jwt.decode(
            token, segredo, algorithms=[ALGORITMO_JWT], options={"verify_exp": False}
        )
    except jwt.PyJWTError as exc:
        raise NaoAutenticado("Token inválido.") from exc
    if int(payload.get("exp", 0)) <= int(agora.timestamp()):
        raise NaoAutenticado("Token expirado.")
    if "sub" not in payload or "perfil" not in payload:
        raise NaoAutenticado("Token inválido.")
    return {"sub": str(payload["sub"]), "perfil": str(payload["perfil"])}

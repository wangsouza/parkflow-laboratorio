"""R09 — validação e normalização de placas brasileiras (convencional e Mercosul)."""

from __future__ import annotations

import re

from app.domain.erros import PlacaInvalida

# Convencional: AAA9999 ou AAA-9999. Mercosul: AAA9A99. Apenas ASCII (A-Z, 0-9).
_CONVENCIONAL = re.compile(r"[A-Za-z]{3}-?[0-9]{4}")
_MERCOSUL = re.compile(r"[A-Za-z]{3}[0-9][A-Za-z][0-9]{2}")


def placa_valida(texto: str) -> bool:
    """Indica se ``texto`` (já sem espaços nas pontas) segue um dos formatos aceitos."""
    return bool(_CONVENCIONAL.fullmatch(texto) or _MERCOSUL.fullmatch(texto))


def normalizar_placa(texto: str) -> str:
    """Valida e normaliza uma placa: sem hífen e em maiúsculas.

    >>> normalizar_placa(" abc-1234 ")
    'ABC1234'
    >>> normalizar_placa("bra2e19")
    'BRA2E19'

    Raises:
        PlacaInvalida: se o texto não corresponde a nenhum formato aceito (R09).
    """
    candidato = texto.strip()
    if not placa_valida(candidato):
        raise PlacaInvalida(
            f"Placa inválida: '{texto}'. Use AAA9999, AAA-9999 ou AAA9A99 (Mercosul)."
        )
    return candidato.replace("-", "").upper()

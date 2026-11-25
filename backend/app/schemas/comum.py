"""Tipos reutilizáveis nos contratos."""

from __future__ import annotations

from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, Field

from app.domain.erros import PlacaInvalida
from app.domain.placa import normalizar_placa


def _validar_placa(valor: str) -> str:
    try:
        return normalizar_placa(valor)
    except PlacaInvalida as exc:
        raise ValueError(exc.mensagem) from exc


def _exigir_texto(valor: object) -> object:
    if not isinstance(valor, str):
        raise ValueError("A placa deve ser um texto.")
    return valor


Placa = Annotated[
    str,
    BeforeValidator(_exigir_texto),
    AfterValidator(_validar_placa),
    Field(description="Placa convencional (AAA9999) ou Mercosul (AAA9A99). Normalizada para maiúsculas.",
          examples=["ABC1234", "BRA2E19"]),
]

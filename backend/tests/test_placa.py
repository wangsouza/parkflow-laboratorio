"""Testes iniciais de validação de placas (R09)."""

import pytest

from app.domain.erros import PlacaInvalida
from app.domain.placa import normalizar_placa


@pytest.mark.requisito("R09")
def test_placa_convencional_valida():
    assert normalizar_placa("ABC1234") == "ABC1234"


@pytest.mark.requisito("R09")
def test_placa_mercosul_valida():
    assert normalizar_placa("BRA2E19") == "BRA2E19"


@pytest.mark.requisito("R09")
def test_placa_invalida_levanta_erro():
    with pytest.raises(PlacaInvalida):
        normalizar_placa("123")

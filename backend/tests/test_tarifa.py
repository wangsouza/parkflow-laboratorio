"""Testes iniciais do cálculo de tarifa (domínio puro)."""

import pytest

from app.domain.tarifa import calcular_tarifa
from helpers import apos, ENTRADA_REFERENCIA


@pytest.mark.parametrize(
    ("minutos", "esperado_centavos"),
    [
        (10, 0),
        (30, 800),
        (180, 1800),
    ],
)
def test_tarifa_para_permanencias_comuns(minutos, esperado_centavos):
    # Arrange
    entrada = ENTRADA_REFERENCIA
    saida = apos(minutos)

    # Act
    resultado = calcular_tarifa(entrada, saida)

    # Assert
    assert resultado.valor_centavos == esperado_centavos


def test_resultado_nao_e_nulo():
    resultado = calcular_tarifa(ENTRADA_REFERENCIA, apos(45))

    assert resultado is not None

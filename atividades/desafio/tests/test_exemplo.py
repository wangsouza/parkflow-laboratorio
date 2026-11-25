"""Exemplos para começar. Copie o estilo, crie seus próprios arquivos ``test_*.py`` nesta pasta.

Regras de ouro:
  * horários SEMPRE explícitos (``entrada_em``/``saida_em``) — nada de depender do relógio do servidor;
  * placas novas em cada teste (``placa_unica()``);
  * um teste que FALHA na versão correta está errado (falso positivo): corrija o resultado esperado.
"""

import pytest
from helpers_desafio import T0, apos, iso, placa_unica


@pytest.mark.requisito("R09")
def test_entrada_valida_devolve_201_e_estadia_ativa(api):
    placa = placa_unica()

    resposta = api.post("/veiculos/entrada", json={"placa": placa, "entrada_em": iso(T0)})

    assert resposta.status_code == 201
    assert resposta.json()["placa"] == placa
    assert resposta.json()["status"] == "ATIVA"


@pytest.mark.requisito("R02")
def test_uma_hora_custa_oito_reais(api):
    resposta = api.post("/tarifas/simular", json={"entrada_em": iso(T0), "saida_em": iso(apos(60))})

    assert resposta.status_code == 200
    assert resposta.json()["valor_centavos"] == 800

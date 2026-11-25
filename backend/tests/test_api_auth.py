"""Testes iniciais de autenticação via API (R11)."""

import pytest

from conftest import SENHA_ADMIN


@pytest.mark.requisito("R11")
def test_login_com_credenciais_corretas(client):
    resposta = client.post("/auth/login", json={"usuario": "admin", "senha": SENHA_ADMIN})

    assert resposta.status_code == 200
    assert "access_token" in resposta.json()


@pytest.mark.requisito("R11")
def test_login_com_senha_errada(client):
    resposta = client.post("/auth/login", json={"usuario": "admin", "senha": "errada"})

    assert resposta.status_code == 401

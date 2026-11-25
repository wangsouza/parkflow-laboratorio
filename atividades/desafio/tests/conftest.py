"""Fixtures dos testes do desafio (caixa-preta).

Os testes falam com a API SOMENTE por HTTP. O endereço vem da variável de ambiente PARKFLOW_URL:

  * treino (versão correta, no seu computador):  make desafio-local   →  padrão abaixo (porta 8100)
  * desafio (API informada pelo responsável):    PARKFLOW_URL=http://<endereço>:<porta> make desafio-testes
"""

from __future__ import annotations

import os

import httpx
import pytest

URL_PADRAO = "http://127.0.0.1:8100"
SENHA_ADMIN = "admin123"  # usuários de demonstração (README)
SENHA_OPERADOR = "operador123"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "requisito(*ids): rastreabilidade — regras de negócio cobertas (ex.: R01).")


@pytest.fixture(scope="session")
def url() -> str:
    return os.environ.get("PARKFLOW_URL", URL_PADRAO).rstrip("/")


def _cliente(url: str, usuario: str, senha: str) -> httpx.Client:
    try:
        resposta = httpx.post(f"{url}/auth/login", json={"usuario": usuario, "senha": senha}, timeout=15)
    except httpx.HTTPError as exc:
        pytest.exit(f"Não consegui falar com a API em {url} ({exc}). Ela está rodando? PARKFLOW_URL está correto?", returncode=2)
    assert resposta.status_code == 200, f"login de {usuario} falhou: {resposta.text}"
    token = resposta.json()["access_token"]
    return httpx.Client(base_url=url, headers={"Authorization": f"Bearer {token}"}, timeout=15)


@pytest.fixture(scope="session")
def api(url: str):
    """Cliente HTTP autenticado como **admin**."""
    with _cliente(url, "admin", SENHA_ADMIN) as cliente:
        yield cliente


@pytest.fixture(scope="session")
def api_operador(url: str):
    """Cliente HTTP autenticado como **operador**."""
    with _cliente(url, "operador", SENHA_OPERADOR) as cliente:
        yield cliente


@pytest.fixture(autouse=True)
def estacionamento_limpo(api: httpx.Client):
    """Antes de cada teste: encerra estadias ativas e restaura a capacidade (testes independentes entre si)."""
    for item in api.get("/veiculos/ativos").json():
        estadia = item["estadia"]
        api.post("/veiculos/saida", json={"placa": estadia["placa"], "saida_em": estadia["entrada_em"]})
    api.put("/configuracao/capacidade", json={"capacidade": 30})
    yield

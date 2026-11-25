"""Fixtures compartilhadas.

Cada teste recebe seu **próprio** banco SQLite em memória, relógio fixo e aplicação — nada é
compartilhado entre testes (independência) e nada depende do horário real (determinismo).
"""

from __future__ import annotations

import os
import warnings
from collections.abc import Iterator

import pytest

# O Starlette recomenda trocar o httpx por outro pacote; o curso mantém httpx (aviso apenas informativo).
warnings.filterwarnings("ignore", message=".*starlette.testclient.*")

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import Engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import Settings  # noqa: E402
from app.core.database import Base, criar_engine, criar_fabrica_sessoes  # noqa: E402
from app.main import criar_app  # noqa: E402
from helpers import RelogioFixo  # noqa: E402

SENHA_ADMIN = "senha-admin-de-teste"
SENHA_OPERADOR = "senha-operador-de-teste"


@pytest.fixture(autouse=True)
def ambiente_isolado(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isola TODOS os testes do ambiente da máquina: variáveis ``PARKFLOW_*`` e arquivo ``.env`` não influenciam."""
    for nome in [n for n in os.environ if n.startswith("PARKFLOW_")]:
        monkeypatch.delenv(nome)
    monkeypatch.setitem(Settings.model_config, "env_file", None)  # vale também para ``Settings()`` sem argumentos


@pytest.fixture
def settings() -> Settings:
    """Configuração de teste TOTALMENTE explícita (nenhum campo vem do ambiente): banco em memória, hash rápido."""
    return Settings(
        _env_file=None,
        database_url="sqlite://",
        capacidade_inicial=3,
        timezone="America/Sao_Paulo",
        admin_senha=SENHA_ADMIN,
        operador_senha=SENHA_OPERADOR,
        hash_iteracoes=1_000,
        secret_key="chave-de-teste-com-pelo-menos-32-bytes!!",
        token_expira_minutos=7 * 24 * 60,  # longo: o relógio fixo avança nos testes
        cors_origens=["http://localhost:5173"],
    )


@pytest.fixture
def relogio() -> RelogioFixo:
    return RelogioFixo()


@pytest.fixture
def engine(settings: Settings) -> Iterator[Engine]:
    engine = criar_engine(settings.database_url)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def sessao(engine: Engine) -> Iterator[Session]:
    """Sessão de banco para testes de repositório/integração."""
    with criar_fabrica_sessoes(engine)() as s:
        yield s


@pytest.fixture
def client(settings: Settings, relogio: RelogioFixo) -> Iterator[TestClient]:
    """Cliente HTTP da aplicação completa (banco em memória próprio)."""
    with TestClient(criar_app(settings=settings, relogio=relogio)) as c:
        yield c


def _cabecalho(client: TestClient, usuario: str, senha: str) -> dict[str, str]:
    resposta = client.post("/auth/login", json={"usuario": usuario, "senha": senha})
    assert resposta.status_code == 200, resposta.text
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


@pytest.fixture
def auth(client: TestClient) -> dict[str, str]:
    """Cabeçalho Authorization do usuário **admin**."""
    return _cabecalho(client, "admin", SENHA_ADMIN)


@pytest.fixture
def auth_operador(client: TestClient) -> dict[str, str]:
    """Cabeçalho Authorization do usuário **operador**."""
    return _cabecalho(client, "operador", SENHA_OPERADOR)

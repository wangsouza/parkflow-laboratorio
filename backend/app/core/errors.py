"""Tratamento de erros: converte exceções de domínio e validação em respostas HTTP padronizadas."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain import erros

STATUS_POR_CODIGO: dict[str, int] = {
    erros.PlacaInvalida.codigo: 422,
    erros.PeriodoInvalido.codigo: 422,
    erros.CapacidadeInvalida.codigo: 422,
    erros.PlacaJaEstacionada.codigo: status.HTTP_409_CONFLICT,
    erros.EstacionamentoLotado.codigo: status.HTTP_409_CONFLICT,
    erros.AtendimentoManual.codigo: status.HTTP_409_CONFLICT,
    erros.CapacidadeInsuficiente.codigo: status.HTTP_409_CONFLICT,
    erros.EstadiaAtivaNaoEncontrada.codigo: status.HTTP_404_NOT_FOUND,
    erros.CredenciaisInvalidas.codigo: status.HTTP_401_UNAUTHORIZED,
    erros.NaoAutenticado.codigo: status.HTTP_401_UNAUTHORIZED,
    erros.AcessoNegado.codigo: status.HTTP_403_FORBIDDEN,
}


def corpo_erro(codigo: str, mensagem: str, detalhes: list[Any] | None = None) -> dict[str, Any]:
    return {"erro": {"codigo": codigo, "mensagem": mensagem, "detalhes": detalhes or []}}


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(erros.ErroDominio)
    async def _dominio(_: Request, exc: erros.ErroDominio) -> JSONResponse:
        codigo_http = STATUS_POR_CODIGO.get(exc.codigo, status.HTTP_400_BAD_REQUEST)
        cabecalhos = (
            {"WWW-Authenticate": "Bearer"} if codigo_http == status.HTTP_401_UNAUTHORIZED else None
        )
        return JSONResponse(
            status_code=codigo_http,
            content=corpo_erro(exc.codigo, exc.mensagem),
            headers=cabecalhos,
        )

    @app.exception_handler(RequestValidationError)
    async def _validacao(_: Request, exc: RequestValidationError) -> JSONResponse:
        detalhes = [
            {"campo": ".".join(str(p) for p in e["loc"] if p != "body"), "mensagem": e["msg"].removeprefix("Value error, ")}
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(
                corpo_erro("VALIDACAO", "Dados de entrada inválidos.", detalhes)
            ),
        )

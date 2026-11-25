"""Camada HTTP: roteadores FastAPI."""

from fastapi import APIRouter

from app.api import auth, dashboard, historico, tarifas, veiculos

roteador = APIRouter()
for _modulo in (auth, veiculos, tarifas, historico, dashboard):
    roteador.include_router(_modulo.router)

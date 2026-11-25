from __future__ import annotations

from pydantic import BaseModel, Field


class ResumoOut(BaseModel):
    data_referencia: str = Field(description="Dia civil (fuso configurado), AAAA-MM-DD.")
    capacidade: int
    ocupadas: int
    vagas_disponiveis: int
    entradas_hoje: int
    saidas_hoje: int
    arrecadado_hoje_centavos: int


class CapacidadeIn(BaseModel):
    capacidade: int = Field(description="Entre 1 e 500.")


class CapacidadeOut(BaseModel):
    capacidade: int

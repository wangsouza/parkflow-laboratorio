#!/usr/bin/env python3
"""Matriz de rastreabilidade requisito ↔ teste.

Lê os marcadores ``@pytest.mark.requisito("R01", ...)`` (em funções, classes ou ``pytestmark`` de
módulo) por análise estática (AST) — não executa os testes.

Uso:
    python scripts/rastreabilidade.py                         # suíte inicial (backend/tests)
    python scripts/rastreabilidade.py --testes outra/pasta/de/testes
    python scripts/rastreabilidade.py --testes backend/tests --saida matriz.md
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REQUISITOS_MD = RAIZ / "docs" / "REQUISITOS.md"


@dataclass
class Teste:
    arquivo: str
    classe: str | None
    nome: str
    requisitos: set[str] = field(default_factory=set)

    @property
    def id(self) -> str:
        return "::".join(p for p in (self.arquivo, self.classe, self.nome) if p)


def _marcadores(no: ast.expr) -> dict[str, set[str]]:
    """Extrai ``{'requisito': {...}}`` de uma expressão ``pytest.mark.requisito(...)``."""
    encontrados: dict[str, set[str]] = {}
    itens = no.elts if isinstance(no, (ast.List, ast.Tuple)) else [no]
    for item in itens:
        if not (isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute)):
            continue
        nome = item.func.attr
        if nome == "requisito":
            valores = {a.value for a in item.args if isinstance(a, ast.Constant) and isinstance(a.value, str)}
            encontrados.setdefault(nome, set()).update(valores)
    return encontrados


def _herdar(destino: Teste, marcas: dict[str, set[str]]) -> None:
    destino.requisitos |= marcas.get("requisito", set())


def coletar_testes(pasta: Path) -> list[Teste]:
    """Percorre ``test_*.py`` em ``pasta`` e devolve os testes com seus marcadores."""
    testes: list[Teste] = []
    for arquivo in sorted(pasta.glob("test_*.py")):
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        do_modulo: dict[str, set[str]] = {}
        for no in arvore.body:
            if isinstance(no, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "pytestmark" for t in no.targets
            ):
                for chave, valores in _marcadores(no.value).items():
                    do_modulo.setdefault(chave, set()).update(valores)

        def registrar(func: ast.FunctionDef, classe: str | None, da_classe: dict[str, set[str]]) -> None:
            teste = Teste(arquivo.name, classe, func.name)
            _herdar(teste, do_modulo)
            _herdar(teste, da_classe)
            for deco in func.decorator_list:
                _herdar(teste, _marcadores(deco))
            testes.append(teste)

        for no in arvore.body:
            if isinstance(no, ast.FunctionDef) and no.name.startswith("test_"):
                registrar(no, None, {})
            elif isinstance(no, ast.ClassDef) and no.name.startswith("Test"):
                da_classe: dict[str, set[str]] = {}
                for deco in no.decorator_list:
                    for chave, valores in _marcadores(deco).items():
                        da_classe.setdefault(chave, set()).update(valores)
                for membro in no.body:
                    if isinstance(membro, ast.FunctionDef) and membro.name.startswith("test_"):
                        registrar(membro, no.name, da_classe)
    return testes


def carregar_requisitos(caminho: Path = REQUISITOS_MD) -> dict[str, str]:
    """``{'R01': 'Tolerância gratuita', ...}`` a partir dos títulos ``## R01 — ...``."""
    padrao = re.compile(r"^## (R\d{2}) — (.+)$", re.MULTILINE)
    return {m.group(1): m.group(2).strip() for m in padrao.finditer(caminho.read_text(encoding="utf-8"))}


def montar_matriz(testes: list[Teste], requisitos: dict[str, str]) -> str:
    por_requisito: dict[str, list[Teste]] = {r: [] for r in requisitos}
    sem_marcador = []
    for teste in testes:
        if not teste.requisitos:
            sem_marcador.append(teste)
        for req in teste.requisitos:
            por_requisito.setdefault(req, []).append(teste)

    linhas = [
        "# Matriz de rastreabilidade requisito → testes",
        "",
        f"Testes analisados: **{len(testes)}** (funções `test_*`; testes parametrizados contam uma vez).",
        "",
        "| Requisito | Descrição | Nº de testes | Situação |",
        "|-----------|-----------|-------------:|----------|",
    ]
    for req, descricao in requisitos.items():
        n = len(por_requisito[req])
        linhas.append(f"| {req} | {descricao} | {n} | {'✅ coberto' if n else '❌ SEM TESTES'} |")

    descobertos = [r for r in requisitos if not por_requisito[r]]
    linhas += ["", f"Requisitos sem nenhum teste rastreado: **{', '.join(descobertos) or 'nenhum'}**.", ""]
    linhas.append("## Detalhe")
    for req, descricao in requisitos.items():
        linhas += ["", f"### {req} — {descricao}"]
        if not por_requisito[req]:
            linhas.append("- *(nenhum teste)*")
        for teste in sorted(por_requisito[req], key=lambda t: t.id):
            linhas.append(f"- `{teste.id}`")
    if sem_marcador:
        linhas += ["", "## Testes sem marcador `requisito`"]
        linhas += [f"- `{t.id}`" for t in sorted(sem_marcador, key=lambda t: t.id)]
    return "\n".join(linhas) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--testes", type=Path, default=RAIZ / "backend" / "tests")
    parser.add_argument("--saida", type=Path, help="grava a matriz neste arquivo (padrão: imprime)")
    args = parser.parse_args(argv)

    testes = coletar_testes(args.testes.resolve())
    if not testes:
        print(f"Nenhum teste encontrado em {args.testes}", file=sys.stderr)
        return 1
    matriz = montar_matriz(testes, carregar_requisitos())
    if args.saida:
        args.saida.write_text(matriz, encoding="utf-8")
        print(f"Matriz gravada em {args.saida}")
    else:
        print(matriz)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Sobe a API do ParkFlow com um banco TEMPORÁRIO (nunca toca em backend/parkflow.db).

Uso (versão correta, para treinar e validar os testes do desafio):

    python scripts/servir_api.py --porta 8100

O mesmo script serve a API usada no próprio desafio, sempre com banco temporário.

Execute com o Python do virtualenv do backend (precisa de uvicorn e das dependências do app).
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--backend", type=Path, default=RAIZ / "backend", help="pasta backend/ a servir")
    parser.add_argument("--porta", type=int, default=8100)
    parser.add_argument("--host", default="127.0.0.1", help="use 0.0.0.0 para atender outras máquinas da rede")
    parser.add_argument("--db", type=Path, help="arquivo SQLite (padrão: arquivo temporário descartável)")
    args = parser.parse_args()

    backend = args.backend.resolve()
    if not (backend / "app" / "main.py").exists():
        print(f"Não encontrei app/main.py em {backend}", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="parkflow-servir-") as tmp:
        banco = args.db or Path(tmp) / "parkflow-temporario.db"
        # Ambiente determinístico: sem .env (cwd temporário) e com o banco temporário.
        for nome in [n for n in os.environ if n.startswith("PARKFLOW_")]:
            del os.environ[nome]
        os.environ["PARKFLOW_DATABASE_URL"] = f"sqlite:///{banco}"
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        os.chdir(tmp)
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(backend))

        import uvicorn

        print(f"ParkFlow em http://{args.host}:{args.porta}  (banco temporário; Ctrl+C encerra)", flush=True)
        uvicorn.run("app.main:criar_app", factory=True, host=args.host, port=args.porta, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# ParkFlow — Laboratório de Testes com IA (Ubuntu/Linux)
.PHONY: install run-backend run-frontend test cov rastreabilidade desafio-local desafio-testes

install:         ## instala backend (virtualenv) e frontend
	python3 -m venv backend/.venv
	backend/.venv/bin/pip install --upgrade pip
	backend/.venv/bin/pip install -r backend/requirements-dev.txt
	cd frontend && npm install

run-backend:     ## API em http://localhost:8000 (documentação em /docs)
	cd backend && .venv/bin/uvicorn app.main:criar_app --factory --reload --port 8000

run-frontend:    ## interface em http://localhost:5173
	cd frontend && npm run dev

test:            ## suíte inicial
	cd backend && .venv/bin/pytest

cov:             ## cobertura de linhas e branches
	cd backend && .venv/bin/pytest --cov=app --cov-branch --cov-report=term-missing

rastreabilidade: ## quais regras (R01..R12) têm testes?
	backend/.venv/bin/python scripts/rastreabilidade.py

desafio-local:   ## API CORRETA (porta 8100, banco temporário) para treinar os testes do desafio
	backend/.venv/bin/python scripts/servir_api.py --porta 8100

desafio-testes:  ## testes do desafio via HTTP (PARKFLOW_URL aponta para a API; padrão: http://127.0.0.1:8100)
	backend/.venv/bin/python -m pytest atividades/desafio/tests -v

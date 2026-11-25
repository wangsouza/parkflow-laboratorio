# ParkFlow — Laboratório de Testes com IA

O ParkFlow é um sistema de **gestão de estacionamento** que funciona corretamente e acompanha uma suíte de testes
**intencionalmente incompleta**. Ele é a base do laboratório **Uso de IA para Testes**: ao longo de três encontros você
planeja casos de teste, automatiza-os com Pytest e testa uma API desconhecida em busca de defeitos, sempre usando a IA
como assistente e verificando criticamente o que ela produz.

## Objetivo do laboratório

| Encontro | Tema                              | Prática (30 min)                                                         |
|---------:|-----------------------------------|--------------------------------------------------------------------------|
| 1        | Planejamento de testes            | Matriz com seis casos de teste elaborados com apoio da IA                |
| 2        | Automação com Pytest              | Teste parametrizado com funções reais do ParkFlow e leitura da cobertura |
| 3        | Caçadores de Bugs                 | Testes HTTP (Pytest + HTTPX) contra uma API com defeitos                 |

## Estrutura do projeto

```
backend/       API FastAPI + suíte inicial de testes em backend/tests/
frontend/      interface React (para ver o sistema funcionando; os testes são do backend)
docs/          REQUISITOS.md (regras de negócio R01–R12) · ARQUITETURA.md
atividades/    aula1.md · aula2.md · desafio/ (DESAFIO.md, RELATORIO_TEMPLATE.md e tests/)
scripts/       rastreabilidade.py (matriz requisito × teste) · servir_api.py (API correta temporária para treino)
.github/       pipeline de integração contínua (testes, cobertura e evidências)
Makefile       atalhos dos comandos mais usados
```

## Instalação (Ubuntu/Linux)

Pré-requisitos: **Python 3.12+** e, para ver a interface, **Node.js 20.19+ ou 22.12+** (confira com `node --version`;
o `nodejs` do `apt` pode ser antigo — use o NodeSource ou o nvm). Os testes só precisam do Python.

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip   # se necessário
```

**Backend** — a partir da **raiz do projeto**:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest                                   # a suíte inicial deve passar
```

**Frontend** (opcional) — a partir da **raiz do projeto**:

```bash
cd frontend
npm install
```

Atalho para instalar os dois: `make install`.

## Como executar a aplicação

Em **dois terminais**, ambos a partir da raiz do projeto:

```bash
# terminal 1 — API em http://localhost:8000  (documentação interativa em /docs)
make run-backend
```

```bash
# terminal 2 — interface em http://localhost:5173
make run-frontend
```

### Usuários de demonstração

| Usuário    | Senha          | Perfil                                  |
|------------|----------------|-----------------------------------------|
| `admin`    | `admin123`     | tudo, inclusive alterar a capacidade    |
| `operador` | `operador123`  | operação do dia a dia (sem configuração)|

São credenciais **só de laboratório**. Para trocá-las, copie `backend/.env.example` para `backend/.env`, altere
`PARKFLOW_ADMIN_SENHA` / `PARKFLOW_OPERADOR_SENHA` e reinicie a API (as senhas são gravadas com hash).

## Como executar os testes

```bash
make test               # suíte inicial (pytest)
make cov                # cobertura de linhas e branches, com as linhas não cobertas
make rastreabilidade    # quais regras (R01–R12) têm testes
```

Sem `make`:

```bash
cd backend && source .venv/bin/activate
pytest -v -k tarifa                                       # filtra por nome
pytest --cov=app --cov-branch --cov-report=term-missing   # cobertura de linhas e branches
pytest --cov=app --cov-branch --cov-report=html           # relatório em htmlcov/index.html
python ../scripts/rastreabilidade.py                      # regras com e sem testes
```

**Sobre a cobertura:** 80 % de linhas e branches é uma meta comum em equipes e serve de **referência didática** neste
laboratório. Ela não é requisito de nenhuma atividade — o mais importante é que os testes *detectem defeitos de verdade*.

## Como consultar as regras de negócio

Todas as regras (R01–R12), os códigos HTTP e os formatos de erro estão em [`docs/REQUISITOS.md`](docs/REQUISITOS.md); a
arquitetura está em [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md). A API também é documentada em
http://localhost:8000/docs quando o backend está em execução. Resumo da tarifa:

| Permanência (`t`)         | Valor           | Regra |
|---------------------------|-----------------|-------|
| `t ≤ 15 min`              | R$ 0,00         | R01   |
| `15 min < t ≤ 60 min`     | R$ 8,00         | R02   |
| `60 min < t ≤ 120 min`    | R$ 13,00        | R03   |
| cada hora adicional iniciada | + R$ 5,00    | R03   |
| teto até 24 h             | R$ 30,00        | R04   |

## Como realizar as atividades

Cada encontro tem **uma única prática de 30 minutos**, descrita passo a passo:

1. [`atividades/aula1.md`](atividades/aula1.md) — matriz com seis casos de teste (sem código).
2. [`atividades/aula2.md`](atividades/aula2.md) — teste parametrizado com Pytest e leitura da cobertura.
3. [`atividades/desafio/DESAFIO.md`](atividades/desafio/DESAFIO.md) — desafio de caixa-preta.

**Como usar a IA:**

- Dê à IA o **contexto**: cole a regra de `docs/REQUISITOS.md` e o trecho de código relevante.
- Peça **casos de teste e resultados esperados** *antes* de pedir o código.
- **Nunca confie sem verificar**: confira cada resultado esperado na regra e leia cada asserção que a IA escrever.
  Pergunte: *esse teste falharia se o código estivesse errado?*

## Como participar do desafio final

O desafio da terceira aula usa uma API com defeitos que roda em um servidor do laboratório; você recebe apenas o endereço.
Treine antes contra a API correta:

```bash
# terminal 1 — API correta (porta 8100, banco temporário)
make desafio-local
```

```bash
# terminal 2 — testes de exemplo em atividades/desafio/tests (devem passar)
make desafio-testes
```

No momento do desafio, aponte os mesmos testes para o endereço informado:

```bash
PARKFLOW_URL=http://<endereço-informado>:<porta> make desafio-testes
```

Escreva seus testes em `atividades/desafio/tests/`, preencha o `RELATORIO_TEMPLATE.md` e siga o passo a passo do
[`DESAFIO.md`](atividades/desafio/DESAFIO.md).

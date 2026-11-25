# ParkFlow — Arquitetura

Monolito simples: **FastAPI + SQLAlchemy + SQLite** no backend e **React + TypeScript + Vite + Tailwind** no
frontend. Sem microserviços, filas, Redis ou serviços externos.

```
┌────────────┐  HTTP/JSON   ┌──────────────────────────────────────────────┐
│  Frontend  │ ───────────▶ │  api/  (FastAPI routers, dependências, auth)  │
│  (React)   │ ◀─────────── │   │                                           │
└────────────┘              │   ▼                                           │
                            │  services/  orquestração + regras com estado  │
                            │   │      │                                    │
                            │   ▼      ▼                                    │
                            │ repositories/   domain/  (regras PURAS)       │
                            │   │                                           │
                            │   ▼                                           │
                            │ models/ + core/database ──▶ SQLite            │
                            └──────────────────────────────────────────────┘
```

## Camadas do backend (`backend/app`)

| Pasta           | Responsabilidade                                                                                   | Depende de             | Como testar                              |
|-----------------|----------------------------------------------------------------------------------------------------|------------------------|------------------------------------------|
| `domain/`       | **Regras puras**: tarifa (R01–R05), placa (R09), limites do dia (R12), erros de negócio. Sem I/O.   | nada                   | unitário puro, parametrizado             |
| `services/`     | Casos de uso: entrada, saída, capacidade, indicadores, login. Regras que dependem de estado (R06–R08). | domain, repositories, clock | unitário com **mocks** dos repositórios |
| `repositories/` | Consultas e gravações SQLAlchemy. Nenhuma regra de negócio.                                        | models                 | **integração** com SQLite temporário     |
| `models/`       | Entidades persistidas (`Estadia`, `Usuario`, `Configuracao`).                                      | core.database          | via repositórios                         |
| `schemas/`      | Contratos Pydantic de entrada/saída (validam placa e datas **com timezone**).                      | domain                 | via API                                  |
| `api/`          | Endpoints HTTP finos: validam, delegam ao serviço, convertem a resposta.                           | services, schemas      | **TestClient** (ponta a ponta)           |
| `core/`         | Configuração, relógio injetável, segurança (hash/JWT), banco, tratamento de erros.                 | —                      | unitário / integração                    |

> A pasta `domain/` é uma escolha deliberada: o cálculo de tarifa **não** está nos endpoints nem depende de banco
> ou relógio. Isso permite testar todos os valores-limite em milissegundos.

### Decisões que facilitam os testes

- **Relógio injetável** (`core/clock.py`): nenhum código de negócio chama `datetime.now()`. Os testes usam
  `RelogioFixo` e controlam o tempo (`relogio.avancar(minutes=61)`).
- **Fábrica de aplicação** (`criar_app(settings, relogio, engine)`): cada teste cria sua própria aplicação com
  banco **SQLite em memória**. Nenhum teste toca o banco de desenvolvimento.
- **Repositórios isolados**: o serviço recebe os repositórios no construtor → fáceis de substituir por `Mock(spec=...)`.
- **Erros de domínio sem HTTP** (`domain/erros.py`) com `codigo` estável; `core/errors.py` os traduz para status HTTP.
- **Dinheiro em centavos inteiros**; datas sempre **aware** (timezone explícito), gravadas em UTC (`DataHoraUTC`).

## Consistência sob concorrência (R06, R07, R08)

Decisões de negócio que **leem e depois gravam** (há vaga? já está estacionado? a estadia ainda está ativa?) precisam ser
atômicas. O serviço abre a transação com `EstadiaRepository.iniciar_escrita()`, que pede `BEGIN IMMEDIATE` ao SQLite
(`core/database.py`): o bloqueio de escrita do **banco** é obtido *antes* das leituras, serializando threads **e processos**.
Em qualquer erro de negócio a transação é desfeita (`rollback`), liberando o bloqueio. Como defesa em profundidade existe o
índice único parcial `uq_estadias_placa_ativa` — vale até para quem escreve fora do serviço. Bancos antigos recebem o índice na
inicialização (`garantir_indices`), sem alterar dados. Não há locks em memória.

A duração de permanência é calculada em **UTC** (`domain/tarifa.py`), de modo que horário de verão não distorce o tempo decorrido.

## Modelo de dados

| Tabela          | Colunas principais                                                                                  |
|-----------------|-----------------------------------------------------------------------------------------------------|
| `estadias`      | `id`, `placa` (normalizada), `entrada_em`, `saida_em`, `status` (`ATIVA`/`FINALIZADA`), `valor_centavos`, `operador_entrada`, `operador_saida` — índice único parcial: 1 estadia `ATIVA` por placa |
| `usuarios`      | `id`, `username` (único), `password_hash` (PBKDF2-SHA256), `perfil` (`admin`/`operador`)             |
| `configuracoes` | `chave` (PK), `valor` — guarda a capacidade                                                         |

Vagas ocupadas = `COUNT(estadias WHERE status = 'ATIVA')`. "Liberar a vaga" significa **mudar o status** para `FINALIZADA`.

## Fluxos principais

**Entrada** — `POST /veiculos/entrada` → schema valida/normaliza a placa (R09) → `registrar_entrada`:
placa já ativa? (R06) → lotado? (R08) → grava `Estadia(ATIVA)` → `commit`.

**Saída** — `POST /veiculos/saida` → `registrar_saida`: estadia ativa existe? (R07) → `calcular_tarifa` (R01–R05)
→ se > 24 h: `ATENDIMENTO_MANUAL` (nada muda) → senão grava saída, valor, status `FINALIZADA` → `commit`.

**Autenticação** — `POST /auth/login` → `AuthService.login` verifica o hash → emite JWT. Cada rota protegida usa
`obter_usuario_atual` (Bearer) e as de admin, `exigir_admin`.

## Frontend (`frontend/src`)

```
api/          client.ts (fetch + ApiError + token), types.ts (espelha os schemas)
auth/         AuthContext (login/logout, sessão em localStorage, logout automático em 401)
components/   ui.tsx (Botao, Campo, Cartao, Indicador, Tabela, Alerta, Selo, Placa…), Layout, Logo, Toast
pages/        Login, Dashboard, Entrada, Veiculos, Tarifa, Saida, Historico
lib/format.ts moeda (centavos → R$), datas no fuso de São Paulo, durações, máscara de placa
```

Em desenvolvimento, o Vite repassa `/api/*` para `http://127.0.0.1:8000` (sem CORS). O logotipo (`Logo.tsx`) é
próprio — um "P" de estacionamento — e não reproduz marcas de terceiros.

## Qualidade e CI

- `pytest` + `pytest-cov` com **branch coverage**; critério didático de **80 %** (`--cov-fail-under=80`).
- Marcadores de rastreabilidade: `@pytest.mark.requisito("R01", …)` → `scripts/rastreabilidade.py`.
- GitHub Actions (`.github/workflows/ci.yml`): instala as dependências, roda os testes com cobertura de linhas e
  branches e **reprova o pipeline** se ela ficar abaixo de 80 % (*quality gate*); publica o relatório como artefato.

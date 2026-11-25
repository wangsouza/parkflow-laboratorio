# ParkFlow — Requisitos e Regras de Negócio

Este documento é a **fonte de verdade** das regras do sistema. Cada regra possui um
identificador (`R01`…`R12`) usado:

- nos docstrings do código (`backend/app/domain`, `backend/app/services`);
- nos testes, por meio do marcador `@pytest.mark.requisito("R01")`;
- na matriz de rastreabilidade (`python scripts/rastreabilidade.py`).

> Convenções gerais
> - Todos os valores monetários são **inteiros em centavos** (`valor_centavos`). Nunca `float`.
> - Todos os instantes (`entrada_em`, `saida_em`) possuem **timezone explícito** (ex.: `2026-03-10T14:00:00-03:00` ou `...Z`).
>   Datas "ingênuas" (sem fuso) são rejeitadas com HTTP 422.
> - Duração = `saida_em − entrada_em` (tempo efetivamente decorrido, resolução de **segundos**, sem arredondamento prévio).
> - Mensagens e códigos de erro estão em português; o código estável (`erro.codigo`) é o contrato para testes.

---

## Tabela de tarifas (resumo)

| Permanência (`t`)              | Valor      | Regra  |
|--------------------------------|------------|--------|
| `t ≤ 15 min`                   | R$ 0,00    | R01    |
| `15 min < t ≤ 60 min`          | R$ 8,00    | R02    |
| `60 min < t ≤ 120 min`         | R$ 13,00   | R03    |
| `120 min < t ≤ 180 min`        | R$ 18,00   | R03    |
| `180 min < t ≤ 240 min`        | R$ 23,00   | R03    |
| `240 min < t ≤ 300 min`        | R$ 28,00   | R03    |
| `300 min < t ≤ 24 h`           | R$ 30,00 (teto) | R04 |
| `t > 24 h`                     | atendimento manual (sem valor) | R04 |

---

## R01 — Tolerância gratuita
Permanências de **até 15 minutos, inclusive exatamente 15 minutos**, não são cobradas (R$ 0,00).

## R02 — Primeira hora
Após ultrapassar 15 minutos, cobra-se **R$ 8,00** pela primeira hora, contada **desde a entrada**.

| Permanência | Valor    |
|-------------|----------|
| 15 min      | R$ 0,00  |
| 16 min      | R$ 8,00  |
| 60 min      | R$ 8,00  |

## R03 — Horas adicionais
Cada hora adicional **iniciada** custa **R$ 5,00**.

| Permanência | Valor     |
|-------------|-----------|
| 61 min      | R$ 13,00  |
| 120 min     | R$ 13,00  |
| 121 min     | R$ 18,00  |

## R04 — Tarifa máxima diária
O valor máximo é **R$ 30,00** para permanências de **até 24 horas** (inclusive 24 h exatas).

Permanências **superiores a 24 horas** não são tarifadas automaticamente. Resposta de negócio documentada:

- **Simulação** (`POST /tarifas/simular`): HTTP 200 com `atendimento_manual = true`, `valor_centavos = null`
  e a mensagem *"Permanência superior a 24 horas: encaminhe o cliente ao atendimento manual."*
- **Saída** (`POST /veiculos/saida`): HTTP 409 com `erro.codigo = "ATENDIMENTO_MANUAL"`.
  A estadia **permanece ativa**, nada é cobrado e a vaga **não** é liberada.

## R05 — Consistência de horários
A data/hora de saída **não pode ser anterior** à de entrada (saída = entrada é permitido; duração zero).
Violação → HTTP 422, `erro.codigo = "PERIODO_INVALIDO"`. Datas sem timezone → HTTP 422 (`VALIDACAO`).

A duração é calculada **convertendo os dois instantes para UTC** antes de subtrair. Assim vale o tempo realmente decorrido
mesmo quando entrada e saída usam o mesmo fuso com horário de verão (ex.: 01:30 → 03:30 em `America/New_York` em 08/03/2026
dura **1 h**, não 2 h) e em horas ambíguas (a hora repetida no fim do horário de verão).

## R06 — Entrada única por placa
Um veículo não pode ter duas estadias **ativas** simultaneamente. A comparação ignora maiúsculas/minúsculas
(`abc1234` ≡ `ABC1234`). Violação → HTTP 409, `erro.codigo = "PLACA_JA_ESTACIONADA"`.
Após a saída, a mesma placa pode entrar novamente.

**Garantia sob concorrência:** a regra é imposta pelo **banco**, não por lock em memória — transação de escrita imediata
(`BEGIN IMMEDIATE` no SQLite) em torno de "verificar + gravar" e **índice único parcial** `uq_estadias_placa_ativa`
(`placa` onde `status = 'ATIVA'`). Com 16 requisições simultâneas da mesma placa, exatamente 1 é aceita (201) e 15 recebem 409.

## R07 — Registro de saída
Uma saída só pode ser registrada para uma estadia **ativa**. Ao registrar a saída o sistema:

1. calcula a tarifa (R01–R04);
2. altera o status para `FINALIZADA`;
3. registra o horário de saída;
4. armazena o valor cobrado;
5. libera a vaga.

Placa sem estadia ativa (inclusive uma segunda tentativa de encerramento) → HTTP 404,
`erro.codigo = "ESTADIA_ATIVA_NAO_ENCONTRADA"`; **nenhuma nova cobrança** é gerada.

## R08 — Capacidade do estacionamento
A capacidade é configurável (inicialmente **30 vagas**). Com todas as vagas ocupadas, novas entradas são
recusadas → HTTP 409, `erro.codigo = "ESTACIONAMENTO_LOTADO"`.

- `vagas_disponiveis = capacidade − estadias ativas`.
- A verificação de vagas e a gravação da entrada ocorrem **na mesma transação de escrita**: sob requisições simultâneas a
  capacidade nunca é ultrapassada (com capacidade 3 e 12 entradas simultâneas: 3 × 201 e 9 × 409). O mesmo vale para a
  saída (uma única cobrança por estadia, R07) e para a alteração de capacidade.
- Somente o perfil **admin** altera a capacidade (`PUT /configuracao/capacidade`). A nova capacidade deve ser
  um inteiro entre 1 e 500 e **não pode ser menor que o número de veículos estacionados** (HTTP 409,
  `CAPACIDADE_INSUFICIENTE`).
- Quando uma entrada viola simultaneamente R06 e R08, prevalece **R06** (placa duplicada).

## R09 — Validação das placas
Regra didática (aceita as duas formas, case-insensitive, espaços nas pontas são ignorados):

| Formato      | Padrão          | Exemplos                    |
|--------------|-----------------|-----------------------------|
| Convencional | `AAA9999` ou `AAA-9999` | `ABC1234`, `abc-1234` |
| Mercosul     | `AAA9A99`       | `BRA2E19`, `bra2e19`        |

- `A` = letra de A a Z (sem acentos), `9` = dígito de 0 a 9.
- O hífen é aceito **somente** no formato convencional, entre a 3ª e a 4ª posição.
- A placa é **normalizada**: sem hífen e em maiúsculas (`abc-1234` → `ABC1234`). É assim que é persistida e comparada.
- Não se validam letras "reservadas" nem a existência real da placa.
- Placa inválida → HTTP 422, `erro.codigo = "VALIDACAO"` (nos corpos) ou `PLACA_INVALIDA` (parâmetro de rota).

## R10 — Histórico e persistência
Toda estadia (entrada e, quando houver, saída) é persistida em SQLite com operador responsável.
`GET /historico` permite filtrar por **placa**, **período** (`de`/`ate`, aplicados à data de entrada, inclusive) e **status**
(`ATIVA` | `FINALIZADA`), ordenado da mais recente para a mais antiga, com paginação (`limite`, `deslocamento`).
Valores monetários em centavos inteiros.

## R11 — Autenticação e autorização
- Login com usuário e senha (`POST /auth/login`) → token Bearer (JWT) com validade configurável.
- Senhas armazenadas com hash (PBKDF2-SHA256 com salt); nunca em texto puro.
- Credenciais inválidas → HTTP 401 `CREDENCIAIS_INVALIDAS` (mesma resposta para usuário inexistente e senha errada).
- Todos os endpoints, exceto `/auth/login`, `/health` e a documentação, exigem token (sem token/token inválido → 401).
- Perfis: `admin` (tudo) e `operador` (tudo, exceto alterar capacidade → HTTP 403 `ACESSO_NEGADO`).

## R12 — Indicadores do dia (dashboard)
`GET /dashboard/resumo` informa: capacidade, veículos estacionados, vagas disponíveis, entradas do dia,
saídas do dia e valor arrecadado no dia (soma das saídas do dia). O "dia" é o dia civil no fuso
`America/Sao_Paulo` (configurável), de 00:00:00 inclusive até 24:00:00 exclusive.

---

## Contratos REST

| Método | Caminho                    | Perfil     | Sucesso | Erros                         |
|--------|----------------------------|------------|---------|-------------------------------|
| POST   | `/auth/login`              | público    | 200     | 401, 422                      |
| POST   | `/veiculos/entrada`        | autenticado| 201     | 401, 409, 422                 |
| GET    | `/veiculos/ativos`         | autenticado| 200     | 401                           |
| GET    | `/veiculos/{placa}`        | autenticado| 200     | 401, 404, 422                 |
| POST   | `/veiculos/saida`          | autenticado| 200     | 401, 404, 409, 422            |
| POST   | `/tarifas/simular`         | autenticado| 200     | 401, 422                      |
| GET    | `/historico`               | autenticado| 200     | 401, 422                      |
| GET    | `/dashboard/resumo`        | autenticado| 200     | 401                           |
| GET    | `/configuracao`            | autenticado| 200     | 401                           |
| PUT    | `/configuracao/capacidade` | admin      | 200     | 401, 403, 409, 422            |
| GET    | `/health`                  | público    | 200     | —                             |

Formato de erro (todos os 4xx tratados pela aplicação):

```json
{ "erro": { "codigo": "PLACA_JA_ESTACIONADA", "mensagem": "…", "detalhes": [] } }
```

A documentação interativa (Swagger/OpenAPI) fica em `http://localhost:8000/docs`.

---

## Usuários de demonstração e configuração de senhas

| Usuário    | Perfil   | Senha padrão (apenas demonstração) | Variável de ambiente          |
|------------|----------|------------------------------------|-------------------------------|
| `admin`    | admin    | `admin123`                         | `PARKFLOW_ADMIN_SENHA`        |
| `operador` | operador | `operador123`                      | `PARKFLOW_OPERADOR_SENHA`     |

As senhas são lidas do ambiente (ou de `backend/.env`, veja `backend/.env.example`), convertidas em hash
na inicialização e gravadas na tabela `usuarios`. Para trocar: altere a variável e reinicie o backend
(o hash é atualizado). **Nunca** reutilize as senhas padrão fora do laboratório. Também são configuráveis:
`PARKFLOW_SECRET_KEY` (assinatura do JWT), `PARKFLOW_CAPACIDADE_INICIAL`, `PARKFLOW_TIMEZONE`,
`PARKFLOW_DATABASE_URL`.

---

## Simplificações deliberadas (para discussão em aula)

- Concorrência resolvida com o que o SQLite oferece: escritas de negócio (entrada, saída, capacidade) são **serializadas** pelo
  bloqueio de escrita do banco. É correto e simples, mas limita a vazão de escrita; em um SGBD cliente-servidor a mesma garantia
  usaria nível de isolamento `SERIALIZABLE`/bloqueio de linha e a restrição única parcial.
- Bancos criados por versões anteriores recebem o índice único na inicialização, **sem alterar dados**. Se já existirem estadias
  ativas duplicadas, a aplicação **não inicia** e explica o problema (corrija os duplicados e inicie de novo).
- Permanências > 24 h não têm cálculo automático (R04).
- Não há integração com meios de pagamento, câmeras ou cancelas.

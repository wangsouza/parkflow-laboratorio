# Aula 3 — Desafio Caçadores de Bugs 🐞

**Duração da prática:** 30 minutos · **Material:** `docs/REQUISITOS.md` e esta pasta

A API do ParkFlow que você vai testar tem **defeitos introduzidos de propósito**. Ela roda em um servidor do laboratório:
você recebe só o **endereço (URL)**, não o código. Seu trabalho é escrever **testes automatizados** que falam com a API
por HTTP e, com eles, tentar identificar defeitos.

**Meta:** desenvolver testes **corretos** e tentar identificar **pelo menos um** defeito. Não é preciso encontrar todos —
ninguém informa quantos existem.

| Etapa | Atividade                                                 | Tempo  |
|------:|-----------------------------------------------------------|-------:|
| 1     | Receber a URL da API e consultar as regras                | 5 min  |
| 2     | Formular hipóteses de defeito com a IA                    | 5 min  |
| 3     | Implementar e executar testes HTTP (Pytest + HTTPX)       | 15 min |
| 4     | Registrar evidências e apresentar resultados              | 5 min  |

## Como funciona

1. **A fonte da verdade é `docs/REQUISITOS.md`.** Um defeito é um comportamento que **contradiz uma regra** (R01–R12).
   Comportamento diferente do que *você* esperava, mas permitido pelos requisitos, não é defeito.
2. **Caixa-preta:** os testes falam com a API **somente por HTTP**, como um cliente real.
3. **Um bom achado** é um teste que **passa na versão correta** e **falha na versão com defeito**.
4. Se um teste falha, antes de concluir que achou um defeito, **releia a regra** e confirme o resultado esperado.

## Preparação

Tudo a partir da **raiz do projeto**, com o ambiente do backend instalado (veja o `README.md`):

```bash
# terminal 1 — API CORRETA para treinar (porta 8100, banco temporário descartável)
make desafio-local
```

```bash
# terminal 2 — os testes de exemplo contra a API correta (devem PASSAR)
make desafio-testes
```

Quando o responsável pelo laboratório informar a URL da API do desafio, aponte os testes para ela:

```bash
PARKFLOW_URL=http://<endereço-informado>:<porta> make desafio-testes
```

Os testes ficam em **`atividades/desafio/tests/`**. Há dois exemplos em `test_exemplo.py` e utilitários prontos:
fixtures `api` e `api_operador` e funções `placa_unica()`, `apos()` e `iso()` (em `helpers_desafio.py`).
Usuários e senhas de demonstração estão no `README.md`.

**Cuidados nos testes:** use horários **explícitos** (`entrada_em` / `saida_em`; nunca dependa do relógio do servidor) ·
use uma **placa nova** em cada teste (`placa_unica()`) · confira **status + corpo + efeito colateral**.

## Etapa 1 — Receber a URL e consultar as regras (5 min)

1. Anote a URL da API do desafio.
2. Releia as regras de tarifa (R01–R04), de horários (R05) e de placas/entradas/saídas (R06–R09) em `docs/REQUISITOS.md`.
3. Rode `make desafio-testes` na API correta para confirmar que o ambiente funciona.

## Etapa 2 — Formular hipóteses de defeito com a IA (5 min)

Peça à IA hipóteses de defeito **a partir das regras** — onde um programador cometeria um erro?

> **Prompt sugerido:** *"Você é analista de QA sênior. Com base nas regras abaixo, liste as 5 hipóteses de defeito mais
> prováveis em uma API de estacionamento (valores-limite, comparações `<` × `<=`, regras de duplicidade e de
> capacidade). Para cada uma, dê a entrada HTTP que a verificaria e o resultado esperado segundo a regra."* + cole as regras.

Escolha **duas ou três** hipóteses para testar. Revise os resultados esperados com `docs/REQUISITOS.md`.

## Etapa 3 — Implementar e executar testes HTTP (15 min)

Crie `atividades/desafio/tests/test_<seu_nome>.py`, no estilo de `test_exemplo.py`, com testes marcados por
`@pytest.mark.requisito("R0x")`. Execute primeiro na API correta (devem passar) e depois na API do desafio:

```bash
make desafio-testes
PARKFLOW_URL=http://<endereço-informado>:<porta> make desafio-testes
```

Um teste que **passa na correta e falha na API do desafio** é um defeito identificado. Um teste que **falha na correta**
está errado: corrija o resultado esperado.

## Etapa 4 — Registrar evidências e apresentar (5 min)

Preencha `RELATORIO_TEMPLATE.md` (copie para `RELATORIO_<seu_nome>.md`): é uma página curta. Apresente à turma o que
encontrou, o teste que prova e um ponto em que a IA errou ou precisou de correção.

---

### Checklist de saída
- [ ] Pelo menos dois testes próprios, passando na API correta
- [ ] Execução contra a API do desafio registrada
- [ ] Relatório curto preenchido (um defeito, se identificado, com requisito, entrada, esperado × obtido e evidência)

# Aula 2 — Automação com Pytest

**Duração da prática:** 30 minutos · **Material:** `backend/tests/` · **Pré-requisito:** ambiente instalado (veja o `README.md`)

Nesta prática você transforma parte da matriz da Aula 1 em **um teste automatizado parametrizado**, usando funções
reais do ParkFlow.

**Entrega:** o teste parametrizado funcionando e a cobertura observada.

| Etapa | Atividade                                              | Tempo  |
|------:|--------------------------------------------------------|-------:|
| 1     | Executar e compreender a suíte inicial                 | 5 min  |
| 2     | Implementar o teste parametrizado                      | 15 min |
| 3     | Executar o Pytest e analisar os resultados             | 5 min  |
| 4     | Consultar a cobertura e discutir lacunas               | 5 min  |

---

## Etapa 1 — Executar e compreender a suíte inicial (5 min)

```bash
make test
```

Abra `backend/tests/test_tarifa.py` e leia o teste existente:

- Que função de produção ele chama? (`calcular_tarifa`)
- De onde vêm a entrada e a saída? (`ENTRADA_REFERENCIA` e `apos(minutos)`, em `backend/tests/helpers.py`)
- Onde estão as três partes **Arrange / Act / Assert**?

## Etapa 2 — Implementar o teste parametrizado (15 min)

No final de `backend/tests/test_tarifa.py`, crie um teste parametrizado com as permanências de
**15, 16, 60 e 61 minutos**. Os valores esperados saem de `docs/REQUISITOS.md` (R01, R02 e R03), em **centavos**.

Esqueleto (complete os `...`):

```python
@pytest.mark.parametrize(
    ("minutos", "esperado_centavos"),
    [
        pytest.param(15, ..., id="15min-limite-da-tolerancia"),
        pytest.param(16, ..., id="16min-primeira-hora"),
        pytest.param(60, ..., id="60min-fim-da-primeira-hora"),
        pytest.param(61, ..., id="61min-hora-adicional"),
    ],
)
def test_tarifa_nas_fronteiras(minutos, esperado_centavos):
    # Arrange
    entrada = ENTRADA_REFERENCIA
    saida = ...

    # Act
    resultado = ...

    # Assert
    assert ...
```

Se usar a IA para gerar o código, forneça o contexto (as regras e o teste existente) e **leia cada asserção** antes de
aceitar. Pergunte: *este teste falharia se `calcular_tarifa` estivesse errada em 15 ou 16 minutos?*

## Etapa 3 — Executar o Pytest e analisar os resultados (5 min)

```bash
cd backend && .venv/bin/pytest -v -k fronteiras
```

1. Os quatro casos aparecem com os `id` que você definiu?
2. Algum falhou? Se sim, o erro está no **teste** (valor esperado) ou no **código**? Confira a regra antes de concluir.
3. Rode `make test` novamente: a suíte completa continua passando?

## Etapa 4 — Consultar a cobertura e discutir lacunas (5 min)

```bash
make cov
```

1. Qual é a cobertura total (linhas + branches)? Anote o número.
2. Na coluna `Missing`, quais arquivos estão mais descobertos? (observe `app/services/estacionamento.py`)
3. Discussão: o teste que você acabou de escrever cobre o serviço de entrada e saída? O que ainda **não** está testado?

> **Conceito:** equipes costumam adotar uma meta de cobertura (80 % de linhas e branches é um valor comum). Ela é um
> **indicador**, não um objetivo desta atividade: cobertura mede o que foi *executado*, não o que foi *verificado*.
> Você **não** precisa atingir 80 % para concluir.

---

### Checklist de saída
- [ ] Teste parametrizado com 15, 16, 60 e 61 minutos passando
- [ ] Cobertura total anotada
- [ ] Pelo menos uma lacuna de cobertura identificada

# Aula 1 — Planejamento de testes com IA

**Duração da prática:** 30 minutos · **Material:** `docs/REQUISITOS.md` · **Código:** nenhum

Nesta prática você **não escreve código**: você planeja seis casos de teste, usando a IA como assistente. A IA propõe;
a decisão e a conferência são suas.

**Entrega:** uma matriz com seis casos, identificando **requisito**, **entrada** e **resultado esperado**.

| Etapa | Atividade                                   | Tempo  |
|------:|---------------------------------------------|-------:|
| 1     | Analisar as regras R01, R02, R03 e R06      | 5 min  |
| 2     | Elaborar seis casos de teste com a IA       | 15 min |
| 3     | Revisar os resultados esperados             | 10 min |

---

## Etapa 1 — Analisar as regras (5 min)

Abra `docs/REQUISITOS.md` e leia **R01, R02, R03 e R06** (e a tabela de tarifas no início do documento).

- Qual é o valor cobrado em cada faixa de permanência?
- O que acontece **exatamente** em 15 minutos? E em 60 minutos?
- O que o sistema faz quando a mesma placa tenta entrar duas vezes?

Anote, com suas palavras, uma frase por regra. Você vai usá-las para conferir a IA.

## Etapa 2 — Elaborar seis casos com a IA (15 min)

Peça à IA casos de teste para as regras da etapa anterior. Os seis casos obrigatórios são:

| Caso | Cenário                                    |
|-----:|--------------------------------------------|
| 1    | permanência de **14 minutos**              |
| 2    | permanência de **15 minutos**              |
| 3    | permanência de **16 minutos**              |
| 4    | permanência de **60 minutos**              |
| 5    | permanência de **61 minutos**              |
| 6    | **placa duplicada** (mesma placa entra duas vezes) |

> **Prompt sugerido:** *"Você é analista de QA sênior. Com base nas regras abaixo, proponha casos de teste para
> permanências de 14, 15, 16, 60 e 61 minutos e para entrada de placa duplicada. Para cada caso informe: requisito,
> entrada, resultado esperado e a justificativa. Não escreva código."* + cole as regras R01, R02, R03 e R06.

Preencha a matriz abaixo (uma linha por caso):

| Caso | Requisito | Entrada | Resultado esperado |
|-----:|-----------|---------|--------------------|
| 1    |           |         |                    |
| 2    |           |         |                    |
| 3    |           |         |                    |
| 4    |           |         |                    |
| 5    |           |         |                    |
| 6    |           |         |                    |

Dicas: para as permanências, informe a entrada e a saída (por exemplo, entrada às 14:00 e saída às 14:15); no caso 6,
informe também o **código de erro** e o que **não** pode mudar no sistema.

## Etapa 3 — Revisar os resultados esperados (10 min)

Compare **cada** resultado esperado proposto pela IA com o texto de `docs/REQUISITOS.md`.

1. Algum valor ou código de erro está diferente da regra? Corrija a matriz e anote o que a IA errou.
2. Os limites estão corretos? Lembre que a regra trata 15 minutos **exatos** e 60 minutos **exatos** de forma específica.
3. Para o caso 6, a IA considerou `abc1234` e `ABC1234` como a mesma placa?
4. Discuta com a turma: *por que não basta confiar no resultado esperado que a IA devolveu?*

Ao final, a matriz com os seis casos revisados é a sua entrega.

---

### Checklist de saída
- [ ] Matriz com seis casos (14, 15, 16, 60, 61 minutos e placa duplicada)
- [ ] Cada caso com requisito, entrada e resultado esperado
- [ ] Pelo menos um erro ou imprecisão da IA identificado (ou a confirmação de que não houve)

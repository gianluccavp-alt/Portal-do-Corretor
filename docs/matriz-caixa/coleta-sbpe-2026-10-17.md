# Coleta SBPE e exatidão (17/10/2026, simulador CAIXA pela tela)

Produto: **100501122 v5 SBPE (TR): Imóvel vinculado a Empreendimento Financiado na CAIXA - Taxa Balcão**.
Ribeirão Preto, imóvel novo, 1 comprador, FGTS 3+ anos, sem subsídio anterior.

## Respostas da CAIXA

| Caso | Renda | Nascimento | Valor | Possui imóvel | Sistema | Financiamento | Prazo | Cota | 1ª parcela (seguradora) |
|---|---|---|---|---|---|---|---|---|---|
| MCMV | 7.000 | 26/01/1998 | 381.000 | Não | SAC | 228.671,71 | 420 | 80 | 15: 2.100,00 |
| MCMV | 7.000 | 26/01/1998 | 381.000 | Não | PRICE | 291.497,28 | 420 | 80 | 14: 2.075,63 · 15: 2.100,00 · 4: 2.087,96 |
| A | 7.000 | 26/01/1998 | 381.000 | Sim | SAC | 174.883,82 | 420 | 90 | 14: 2.075,62 · 16: 2.099,99 · 4: 2.073,60 |
| A | 7.000 | 26/01/1998 | 381.000 | Sim | PRICE | 175.199,30 | 360 | 80 | 4: 1.723,60 |
| B | 5.000 | 26/01/1998 | 381.000 | Sim | SAC | 123.078,67 | 420 | 90 | 14: 1.475,62 · 16: 1.499,99 · 4: 1.473,77 |
| B | 5.000 | 26/01/1998 | 381.000 | Sim | PRICE | 122.915,98 | 360 | 80 | 14: 1.225,63 |
| C | 15.000 | 15/03/2008 | 700.000 | Não | SAC | 378.623,62 | 420 | 90 | — |
| C | 15.000 | 15/03/2008 | 700.000 | Não | PRICE | 380.117,52 | 360 | 80 | 4: 3.700,82 |
| D | 15.000 | 15/03/1981 | 700.000 | Não | SAC | 373.132,43 | 418 | 90 | 14: 4.455,22 · 16: 4.499,99 · 4: 4.448,04 |
| D | 15.000 | 15/03/1981 | 700.000 | Não | PRICE | 373.899,09 | 360 | 80 | 14: 3.705,23 · 16: 3.750,01 · 4: 3.698,05 |

Renda > 13.000 sem imóvel: a 1ª modalidade é Pró-Cotista FGTS (100501107); decisão do usuário: usar SBPE.
Com "possui imóvel na cidade = Sim": só aparecem SBPE 100501122 e 100501102.

## Regras SBPE

- Taxa mensal = (1 + 11,49%)^(1/12) − 1 = 0,9104926% (exibida como 10,92% nominal / 11,49% efetiva), igual para qualquer renda e valor.
- SAC: comprometimento 30%, cota 90%, prazo até 420 (regra de idade do MCMV).
- PRICE: **comprometimento 25%**, cota 80%, prazo até 360.
- Taxa de administração R$ 25. Sem subsídio.
- Seguradoras 14, 16 (CAIXA RESIDENCIAL HABITACIONAL ESPECIAL) e 4 (Tokio). A 16 é a mais cara e limita a capacidade.
- DFI (% do valor do imóvel ao mês): 14 = 0,0066% · 16 = 0,0130% · 4 = 0,00622%.
- MIP (% a.m. sobre o saldo, faixa de idade):

| Idade | 14 e 16 | Tokio (4) |
|---|---|---|
| 18–25 | 0,00930 | 0,00884 |
| 26–30 | 0,00960 | 0,00927 |
| 31–35 | 0,01160 | 0,01172 |
| 36–40 | 0,01540 | 0,01590 |
| 41–45 | 0,02520 | 0,02399 |
| 46–50 | 0,03860 | 0,03687 |
| 51–55 | 0,06760 | 0,06930 |
| 56–60 | 0,15330 | 0,15390 |
| 61–65 | 0,27310 | 0,27750 |
| 66–70 | 0,32590 | 0,33203 |
| 71–75 | 0,48940 | 0,49650 |
| 76–80 | 0,53120 | 0,54147 |

Validação do teto (fórmula fechada, MIP sobre o valor financiado): SAC −R$ 1,05 a −R$ 3,19; PRICE −R$ 1,20 a −R$ 3,64.

## Exatidão (o resíduo de R$ 1–3)

"Ver parcelas" do caso MCMV PRICE (291.497,28): prestação 1.998,80 · juros 1.860,72 · MIP 24,77 (sobre o saldo após a 1ª amortização) · DFI 51,44 · taxa 25,00 = encargo 2.100,01 no cronograma; o resumo mostra 2.100,00.
Os componentes batem ao centavo; o resíduo vem do método interno de busca do teto. Hipóteses testadas sem fechar todos os casos: soma sem arredondar, MIP sobre saldo, tolerância de 0,005, truncamento.

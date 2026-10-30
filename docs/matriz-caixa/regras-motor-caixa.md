# Regras do simulador CAIXA (MCMV): base para o motor próprio

Levantadas por engenharia reversa do Simulador Habitacional CAIXA em 15/10/2026. Imóvel novo, residencial,
1 comprador, sem subsídio anterior e sem outro imóvel na cidade. A fórmula do subsídio vem da norma oficial
(IN MCID nº 48/2022, art. 53) e os parâmetros foram calibrados nas respostas da CAIXA.

**Validação:** o protótipo [`prototipo/motor-caixa.js`](prototipo/motor-caixa.js) reproduz **138 respostas
reais** da CAIXA (PRICE e SAC) e 3 casos de idade-limite (`node docs/matriz-caixa/prototipo/validar.js`):

| Campo | Maior diferença |
|---|---|
| Juros, prazo, faixa | exato |
| 1ª e última parcela (3 seguradoras) | ± R$ 0,03 |
| Subsídio | ± R$ 1 |
| Valor financiado | − R$ 2,90 (arredondamento: 1 centavo de parcela ≈ R$ 2 de financiamento) |

> Versão oficial em uso: [`assets/motor-caixa.js`](../../assets/motor-caixa.js), testada por
> `tests/motor-caixa.test.js`. O protótipo em `prototipo/` fica como registro da engenharia reversa.

## 1. Cidades

| Município (IBGE) | Teto F1/F2 | Fator populacional (Fpop) | UF (FD/R) |
|---|---|---|---|
| Ribeirão Preto (3543402) | R$ 264.000,00 | 1,10 | SP (2,07) |
| Sorocaba (3552205) | R$ 264.000,00 | 1,10 | SP (2,07) |
| Campinas (3509502) | R$ 270.000,00 | 1,20 | SP (2,07) |

## 2. Enquadramento, juros e taxa de administração

| Condição | Produto | Juros nominal (com 3+ anos de FGTS) | Taxa adm. |
|---|---|---|---|
| renda ≤ 2.160 e imóvel ≤ teto | 100501101 (FGTS vinc. empreendimento) | 4,25% | R$ 0 |
| 2.160,01–2.850 e imóvel ≤ teto | 100501101 | 4,50% | R$ 0 |
| 2.850,01–3.200 e imóvel ≤ teto | 100501101 | 4,75% | R$ 25 |
| 3.200,01–3.500 e imóvel ≤ teto | 100501101 | 5,00% | R$ 25 |
| 3.500,01–4.000 e imóvel ≤ teto | 100501101 | 5,50% | R$ 25 |
| 4.000,01–5.000 e imóvel ≤ teto | 100501101 | 6,50% | R$ 25 |
| renda ≤ 9.600 e imóvel ≤ 400.000 (casos não acima) | 100501101 | 7,66% | R$ 25 |
| renda ≤ 13.000 e imóvel ≤ 600.000 (casos não acima) | 100501129 (MCMV Classe Média) | 10,00% | R$ 25 |
| fora disso | não enquadra (erro MN1880) | | |

- **Sem 3 anos de FGTS:** +0,5 p.p. em todas as linhas com produto 100501101 (ex.: 4,5 → 5,0; 7,66 → 8,16). Na Classe Média, 10% de qualquer forma.
- Renda até 5.000 com imóvel acima do teto local cai na linha de 7,66% e perde o subsídio.
- Taxa mensal = nominal / 12. Juros efetivo = (1 + i)^12 − 1.
- Os limites de renda são inclusivos ao centavo (3.200,00 → 4,75%; 3.200,01 → 5,00%).

## 3. Prazo

- `prazo = max(120, min(420, floor(966,93 − dias(nascimento → 1º vencimento) / 30,4375)))`
- 1º vencimento = data da simulação + 1 mês. Na prática, a idade no último vencimento fica abaixo de ~80 anos e 7 meses.
- Validado com 16 datas de nascimento; a margem de incerteza é de 1 a 2 dias nas fronteiras.
- **Idade máxima de entrada: 70 anos e 6 meses na data da simulação.** Com 70a6m exatos simula com o prazo mínimo de 120 meses; com 1 dia a mais, a modalidade sai da lista (sobra só a Pró-Cotista).

## 4. Parcela e seguros

- **PRICE:** parcela = PV × i / (1 − (1 + i)^−n). **SAC:** amortização = PV / n; juros = saldo × i.
- **Encargo mensal** = parcela + taxa adm. + MIP + DFI.
- **MIP (morte e invalidez)** = saldo devedor após o pagamento do mês × taxa da faixa de idade. A taxa muda no aniversário. Na 1ª parcela exibida no resumo, a CAIXA usa o valor financiado inteiro.
- **DFI (danos físicos)** = valor do imóvel × taxa fixa; zera na última parcela.

| Idade | MIP Caixa Residencial (14) e Mais (15) | MIP Tokio Marine (4) |
|---|---|---|
| 18–25 | 0,00820% | 0,01037% |
| 26–30 | 0,00850% | 0,01039% |
| 31–35 | 0,01080% | 0,01206% |
| 36–40 | 0,01440% | 0,01695% |
| 41–45 | 0,02440% | 0,02589% |
| 46–50 | 0,03590% | 0,03651% |
| 51–55 | 0,06450% | 0,06624% |
| 56–60 | 0,07640% | 0,07745% |
| 61–65 | 0,12960% | 0,13721% |
| 66–70 | 0,20050% | 0,21778% |
| 71–75 | 0,37290% | 0,39351% |
| 76–80 | 0,45660% | 0,55777% |

| Seguradora | DFI (% do valor do imóvel ao mês) |
|---|---|
| 14 Caixa Residencial Habitacional | 0,0071% |
| 15 Caixa Residencial Habitacional Mais | 0,0135% |
| 4 Tokio Marine | 0,00889% |

## 5. Financiamento máximo

- O maior PV em que o **1º encargo ≤ 30% da renda**, calculado para cada seguradora; vale o menor PV.
- Fórmula fechada (PRICE): `PV = (0,30 × renda − taxaAdm − DFI) / (k + MIP)`, com k = i / (1 − (1 + i)^−n). No SAC, k = 1/n + i.
- Limitado a **80% do valor do imóvel**.
- **Até 60 anos** a conta inclui as 3 seguradoras, e a 15 (Caixa Residencial Mais) é sempre a que limita.
  **A partir de 61 anos** a seguradora 15 sai da conta: a Tokio Marine limita e a 15 pode passar de 30%.
  Confirmado com 53, 58 e 60 anos (a 15 limita) e com 61 em PRICE e SAC, 66 e 69 anos (a Tokio limita).
- Entrada mínima = valor do imóvel − financiamento − subsídio.

## 6. Subsídio (desconto FGTS), só nas faixas 1 e 2 com imóvel ≤ teto

Recalibrado em 30/10/2026 com o **fator social** ("Possui mais de um comprador e/ou dependente na proposta?",
campo `fatorSocial` do simulador). Fixtures: `tests/fixtures/caixa/casos-fator-social*.txt` (46 respostas).

```
Dfamília = min(55.000, Frenda × (1 + (FD/R + FDfin + FUH) / 100))
Frenda   = (626,8731 + 0,0041743 × max(0, 3.700 − R)²) / 1,10 × Fpop / 0,30
FDfin    = 10 − 40 × (Dfin / VVI − 0,5),   limitado a ±10
Dfin     = 0,25 × R × ((1 + j)^420 − 1) / ((1 + j)^420 × j),   j = juros nominal da operação / 12
VVI      = min(valor do imóvel, 67,5% do teto F1/F2 do município)
FD/R     = 2,07 (SP);   FUH = 0 (o simulador não pede área)

com dependente ou mais de um comprador:  D = Dfamília
só o comprador (unipessoal):             D = 30% × Dfamília
```

- Arredondado para reais inteiros. **Se D < R$ 1.500, o subsídio é zero.** No unipessoal isso zera o
  subsídio perto de R$ 3.227 de renda; com dependente ele vai até **R$ 4.000,00** (4.000,01 já não tem).
- O teto de R$ 55.000 vale para a família; o unipessoal fica com 30% do valor já limitado (R$ 16.500).
- Quem já recebeu subsídio FGTS/União (a partir de maio/2005) não recebe de novo: o motor zera.
  A CAIXA recusa essa combinação no simulador (MN1872), então ela não foi medida.
- Não depende da idade nem do sistema (PRICE ou SAC). Sobe levemente sem FGTS (juros maiores reduzem o Dfin).

## 7. Limitações conhecidas

1. **Valor financiado até R$ 3 abaixo da CAIXA** (≈ 0,001%). A CAIXA arredonda o teto de 30% de um jeito que nenhuma
   hipótese testada (arredondar ou truncar parcela e MIP, taxa mensal truncada, tolerância de centavo) reproduz
   exatamente; 1 centavo de parcela equivale a cerca de R$ 2 de financiamento. O motor fica do lado conservador.
2. **Cidades:** só RP, Campinas e Sorocaba estão mapeadas (teto e Fpop). Outra cidade exige descobrir o teto
   (o ponto onde os juros saltam para 7,66%) e o Fpop (pelo subsídio de uma renda conhecida).
3. **Regras mudam:** revalidar sempre que o Conselho Curador do FGTS ou o MCID alterarem o programa
   (a última mudança foi em 22/04/2026). Os casos em `prototipo/` servem de teste de regressão.
4. Fora do escopo: imóvel usado, Pró-Cotista e FUH (área do imóvel; o simulador não pede). Mais de um comprador
   entra só como fator social do subsídio; a renda informada é a renda familiar somada.

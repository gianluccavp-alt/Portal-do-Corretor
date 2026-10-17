# Match de Unidades — design

**Data:** 15/10/2026
**Status:** aprovado; extensão SBPE e trava da Faixa 3 aprovadas em 17/10/2026 (§4.5 e §4.6)
**Página:** `match-unidades.html` (card novo em "Ferramentas" na home)
**Base de cálculo:** `docs/matriz-caixa/regras-motor-caixa.md` e `docs/matriz-caixa/prototipo/`

## 1. Objetivo

Com poucos dados do cliente, mostrar ao corretor **quais unidades disponíveis o cliente consegue fechar**,
com financiamento CAIXA, subsídio e Pro Soluto estimados para cada uma. É uma simulação prática e rápida
para o corretor passar na hora ao cliente. Não é aprovação: o resultado continua sujeito à análise da
CAIXA e da Direcional.

Card na home: **Match de Unidades →** "A partir da renda do cliente, estima financiamento, subsídio e
Pro Soluto e mostra as unidades que ele consegue comprar."

### Fora de escopo

- Entrada de FGTS, sinais, anuais e bônus. O ato é fixo (§4.2).
- Mais de um comprador, imóvel usado, Pró-Cotista, SBPE.
- Cidades além de Ribeirão Preto, Campinas e Sorocaba (as únicas com teto e Fpop mapeados no motor).
- Mostrar unidades que dependem de comitê.
- Mudar qualquer conta do Simulador Associativo, ou alinhar o visual dele.

## 2. Arquitetura

```
match-unidades.html ─┬─ assets/simuladores.js   SIM_EMPS (catálogo) + SimUnidades (estoque ao vivo)
                     ├─ assets/motor-caixa.js   financiamento, subsídio, parcela CAIXA
                     ├─ assets/match-prosoluto.js  cópia do cálculo do Pro Soluto do associativo
                     ├─ assets/match.js         regras do Match (funções puras)
                     └─ assets/match-app.js     tela, lista, PDF
```

| Arquivo | Papel |
|---|---|
| `match-unidades.html` | Página. Identidade Direcional (vermelho `#E4032B`, DM Sans), como a home. |
| `assets/motor-caixa.js` | Motor CAIXA. Sai de `docs/matriz-caixa/prototipo/motor-caixa.js` sem mudança de regra. |
| `assets/match-prosoluto.js` | Cópia de `calc()`, `checklistAprovacao()`, `POLITICAS`, `TX` e da entrega por torre (`GAIA_ENTREGA_POR_TORRE`) do `simulador-associativo.html`, como funções puras. |
| `assets/match.js` | Cruza cliente × unidades, chama os dois motores, filtra, agrupa e ordena. |
| `assets/match-app.js` | Formulário, resultado, "Abrir no associativo" e PDF. |

Todos no padrão dos módulos existentes (`assets/pendencias.js`): IIFE que exporta via `module.exports`
no Node e `window.<Nome>` no navegador, sem build.

**Cópia do Pro Soluto (decisão do brainstorm).** O associativo não é refatorado. O cabeçalho de
`match-prosoluto.js` diz de qual trecho do associativo cada função foi copiada e que **toda mudança de
política ou taxa precisa ser feita nos dois arquivos**. O caso de regressão do associativo vira teste da
cópia (§9).

## 3. Entradas

| Campo | Regra |
|---|---|
| Cidade | Obrigatório. Ribeirão Preto, Campinas ou Sorocaba (cidades do `SIM_EMPS`). |
| Empreendimento | Opcional, padrão "Todos" da cidade. |
| Renda bruta | Obrigatório, > 0. |
| Data de nascimento | Obrigatório. |
| 3 anos de FGTS | Sim/Não, padrão Sim. |
| Possui imóvel na cidade | Sim/Não, padrão Não. Sim leva ao SBPE (§4.5). |
| Política | Aço, Bronze, Prata, Ouro, Diamante. Padrão **Aço**. |

## 4. Cálculo por unidade (`assets/match.js`)

Data de referência = hoje. Para cada unidade disponível do recorte, vinda do `SimUnidades`:

### 4.1 CAIXA (`motor-caixa.js`)

- Valor do imóvel = **valor de avaliação bancária** da unidade.
- Município = cidade do empreendimento. Sistema **PRICE**, prazo máximo pela idade.
- Saída: produto/faixa, juros, prazo, **financiamento máximo**, **subsídio** e 1ª parcela das 3 seguradoras.
- **Parcela do financiamento** usada no Pro Soluto = **a maior 1ª parcela entre as 3 seguradoras**.
- A unidade é descartada se o motor não a enquadra (avaliação acima do teto da faixa, renda fora do
  MCMV) ou se não tem valor de avaliação.

### 4.2 Pro Soluto

- Valor de venda = campo `associativo` da unidade no `SimUnidades` (já considera preço promocional).
- **Ato fixo, com data de hoje:** R$ 1.500 no Conquista Clube Ipiranga (`id: 'ipiranga'`), R$ 2.500 nos demais.
- Sem sinais, anuais e bônus. Financiamento = mínimo entre a capacidade CAIXA e venda − subsídio − ato.
  Saldo do Pro Soluto = venda − financiamento − subsídio − ato (mínimo 0).

### 4.3 Fluxo e política (`match-prosoluto.js`)

- Venda = hoje. 1º vencimento = mês seguinte à venda, dia 10 (mesma sugestão do associativo).
- **Prazo do Pro Soluto = prazo máximo da política escolhida** (84 meses). Se a parcela linear ficar abaixo da
  parcela mínima do produto, o prazo encurta até atingi-la. Pro Soluto zerado não tem carnê e é aprovado.
- Entrega = entrega do empreendimento, ou da torre quando houver data específica (Village Gaia, Torre 1).
- Idade = idade na data de hoje. Renda = renda informada.
- Roda o **carnê linear**. Se não aprovar, roda o **escalonado**.
- A unidade **entra na lista só se um dos dois carnês fica "Aprovado"** em todos os itens do
  `checklistAprovacao` da política escolhida, **sem a tolerância de comitê**. Resultado "Comitê" ou
  "Reprovado" fica fora.

### 4.4 Saída por unidade

Empreendimento, torre/andar/final, tipologia, área privativa, valor de venda, financiamento, subsídio,
ato, saldo do Pro Soluto, parcela do Pro Soluto × prazo (e se é linear ou escalonado), parcela do
financiamento e C.R. total.

### 4.5 SBPE (extensão de 17/10/2026)

Regras e coleta: `docs/matriz-caixa/coleta-sbpe-2026-10-17.md`.

- **Quando:** cliente **possui imóvel na cidade** ou **renda > R$ 13.000**. Produto 100501122 (SBPE TR, imóvel
  vinculado a empreendimento, Taxa Balcão). Renda acima de R$ 13 mil deixa de ser erro.
- **Taxa mensal** = (1 + 11,49%)^(1/12) − 1, exibida como 10,92% nominal / 11,49% efetiva. Sem subsídio. Taxa de adm. R$ 25.
- **PRICE (usado na tela):** comprometimento **25%**, cota **80%**, prazo até **360** meses (com a regra de idade).
- SAC (só no motor): comprometimento 30%, cota 90%, prazo até 420.
- **Seguros próprios do SBPE:** seguradoras 14, 16 (Caixa Residencial Habitacional Especial) e 4 (Tokio), com
  tabelas de MIP e DFI da coleta. O teto confere as 3 em qualquer idade (premissa: não coletado acima de 60 anos).
- Idade: mesma regra do MCMV (entrada até 70a6m; premissa coerente com os prazos coletados).
- Sem limite de valor do imóvel por faixa.

### 4.6 Faixa 3 travada no PCV (extensão de 17/10/2026)

Quando o cliente está no MCMV, **avaliação > R$ 400.000**, **venda associativa < R$ 400.000** e **renda ≤ R$ 9.600**,
a CAIXA é simulada com o imóvel em **R$ 400.000 (Faixa 3)**, porque o contrato (PCV) trava esse valor.
O cartão mostra o selo "Simulada na Faixa 3: valor travado em R$ 400 mil no PCV". O selo não vai para o PDF.

## 5. Resultado na tela (`assets/match-app.js`)

- **Resumo do cliente** no topo: faixa MCMV, juros, prazo CAIXA e subsídio estimado (do enquadramento
  da renda; o subsídio e o financiamento exatos variam por unidade).
- **Lista agrupada por empreendimento**, com a contagem no título. Unidades ordenadas da menor para a
  maior parcela de Pro Soluto.
- Cada unidade tem **Abrir no associativo** (§6) e uma caixa de seleção para o PDF (§7).
- **Nenhuma unidade cabe:** a tela informa isso e, se existir, sugere a próxima política em que alguma
  unidade cabe ("12 unidades cabem na política Prata"), recalculando nas políticas acima da escolhida.
- Rodapé da lista: quantas unidades ficaram fora por falta de avaliação ou por enquadramento.
- Aviso fixo: valores estimados, motor calibrado com o simulador CAIXA em 15/10/2026.
- Layout pensado primeiro para celular (uso ao lado do cliente).

## 6. Abrir no Simulador Associativo

Única mudança no `simulador-associativo.html`: ao carregar, ler parâmetros da URL e preencher o
formulário. **Nenhuma conta muda.**

`simulador-associativo.html?emp=<id>&torre=<n>&unidade=<codigo>&renda=<n>&idade=<n>&valor=<n>&fin=<n>&sub=<n>&parcFin=<n>&ato=<n>&politica=<id>`

- Campo ausente ou inválido é ignorado. O corretor continua podendo editar tudo.
- `emp`, `torre` e `unidade` esperam o `SimUnidades` carregar antes de selecionar.

## 7. PDF para o cliente

Gerado no navegador com jsPDF (como os simuladores), com as unidades marcadas.

- Cabeçalho: logo Direcional, data e nome do cliente (campo opcional pedido na hora de gerar).
- Por unidade: empreendimento, unidade, tipologia, área, valor, financiamento estimado, subsídio, ato,
  Pro Soluto (parcela × prazo) e parcela do financiamento.
- **Nunca aparecem:** política, folga de tabela, valor comercial mínimo, C.R., avaliação bancária
  e nomes de regra interna.
- Rodapé fixo: "Simulação aproximada, sujeita à análise de crédito da CAIXA e à aprovação da Direcional."

## 8. Erros

| Situação | Comportamento |
|---|---|
| Planilha indisponível | Mesmo aviso e "Tentar novamente" dos simuladores (`SimUnidades`). |
| Renda acima de R$ 13.000 | Vai para o SBPE (§4.5). |
| Idade acima de 70 anos e 6 meses | Mensagem no formulário: fora do limite de idade da CAIXA. Sem lista. |
| Campo obrigatório vazio | Mensagem no campo; botão não calcula. |
| Unidade sem avaliação ou fora do teto | Descartada; entra na contagem do rodapé. |

## 9. Testes (`node --test tests/*.test.js`)

- `tests/motor-caixa.test.js`: os 138 casos reais da CAIXA e as 3 idades-limite, com as mesmas tolerâncias
  do protótipo (financiamento ± R$ 3, subsídio ± R$ 1, parcelas ± R$ 0,05). Fixtures copiadas de
  `docs/matriz-caixa/prototipo/` para `tests/fixtures/`.
- `tests/match-prosoluto.test.js`: o caso de regressão documentado no associativo (Village Gaia, renda
  7.500, idade 30, imóvel 333.190,20, financiado 304.800, ato 2.500, prazo 84, venda 25/07/2026, política Aço).
  Valores esperados: pré-saldo 25.890,20 · P.S. corrigido 26.019,65 · linear 422,39 · C.R. linear 34,86%.
- `tests/match.test.js`, com estoque fictício: ato por produto, filtro de cidade e empreendimento, descarte
  sem avaliação ou fora do teto, exclusão de comitê, linear antes do escalonado, ordenação, sugestão de
  política e PDF sem campos internos.
- Verificação manual no navegador: 2 ou 3 perfis reais. Abrir uma unidade no associativo pelo botão e
  conferir que os números batem.

## 10. Deploy

Igual ao restante do portal (`WORKFLOW.md`): branch → PR → merge na `main` → deploy manual na Vercel.

## 11. Riscos

- **Divergência entre as duas cópias do Pro Soluto.** Mitigação: cabeçalho de aviso na cópia, teste de
  regressão e item no checklist de PR quando política ou taxa mudar.
- **Regras da CAIXA mudam** (Conselho Curador do FGTS ou MCID). Mitigação: os 138 casos servem de teste de
  regressão; refazer uma coleta pequena e atualizar o motor quando houver mudança.
- **Financiamento até R$ 3 menor que o da CAIXA**, e o resultado sempre usa a capacidade máxima
  (parcela ≈ 30% da renda). Mitigação: aviso fixo na tela e no PDF.
- **Planilha sem valor de avaliação** em alguma unidade. Ela fica fora da lista e entra na contagem do
  rodapé, para o comercial corrigir.

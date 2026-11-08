# Simulador de Financiamento — design

**Data:** 07/11/2026
**Status:** telas aprovadas em 07/11/2026; este documento aguarda aprovação
**Telas (canvas, privado):** https://claude.ai/artifact/KZN7zwgMrwvNi8NNmdzXg2
**Branch:** `feat/simulador-financiamento`
**Base de cálculo:** `assets/motor-caixa.js` e `docs/matriz-caixa/regras-motor-caixa.md`

## 1. Objetivo

O corretor precisa saber quanto o cliente financia na CAIXA (financiamento, subsídio, parcela e entrada)
sem sair do portal e sem abrir o Simulador Habitacional CAIXA. Hoje o associativo pede esses números
prontos no passo Cliente ("Valor da 1ª parcela na simulação da CAIXA") e o corretor digita de outro lugar.

Duas entradas, com o mesmo peso de uso (o usuário confirmou que usa as duas):

1. **Botão "Simular financiamento"** dentro dos dois simuladores associativos (normal e Black Friday).
   Abre um popup em passos, mostra o resultado e **copia** os números para o simulador.
2. **Tela dedicada** `/simulador-financiamento`, no Padrão visual 2.0 (ícones 3D, como o Match), para
   simular do zero com o cliente do lado, baixar o PDF e levar os dados ao associativo.

Sucesso: o corretor fecha o passo Cliente do associativo sem digitar financiamento, subsídio e parcela à
mão, e consegue entregar ao cliente um PDF de simulação com a cara da Direcional.

### Fora de escopo

- Qualquer mudança de regra no motor CAIXA (juros, faixas, subsídio, prazo). Só entra a função nova de
  cronograma (§5).
- Imóvel usado, Pró-Cotista, cidades além de Ribeirão Preto, Campinas e Sorocaba (o motor não tem).
- Simulador de Tabela Direta (não ganha o botão).
- Refatorar o associativo. O popup entra como módulo novo, ligado aos dois HTML com poucas linhas.

### O que tornaria isto um fracasso

- Números do popup diferentes dos do motor que o Match já usa (fonte única: `MotorCaixa.simular`).
- Copiar para o associativo e mudar alguma conta dele além dos 4 campos.
- Popup que trava o associativo quando falta unidade, renda ou quando o motor devolve erro.
- Apresentar a simulação como aprovação de crédito.

## 2. Decisões do usuário (07/11/2026)

| Tema | Decisão |
|---|---|
| Uso | Botão nos associativos e tela dedicada, os dois com o mesmo peso. |
| Parcela copiada para "Parcela do financiamento" | Padrão = **maior 1ª parcela entre as 3 seguradoras** (hoje sempre a Caixa Residencial Mais até 60 anos). O corretor pode trocar a seguradora no resultado. Mesma regra do Match (§4.1 do spec do Match). |
| "Levar ao associativo" na tela dedicada | **Escolhe na hora**: unidade de Ribeirão Preto com a campanha Black Friday ativa → pergunta "Associativo" ou "Associativo Black Friday"; nos outros casos vai direto ao associativo normal. |
| Botão clicado sem unidade escolhida | **Popup pede o valor**: o passo 1 ganha cidade e valor de avaliação. Nada fica travado. |
| Entrada da tela dedicada | **Card na home**, em "Ferramentas", com o ícone 3D da calculadora. |
| Linguagem | "Financia até", nunca "Cabe financiar" (comentário no canvas). |

## 3. Arquitetura

```
simulador-associativo.html ───────────┐
simulador-associativo-blackfriday.html ┼─ assets/financiamento-popup.js  popup (DOM) + copiar
                                       │   assets/financiamento.css       estilos .fz-* (claro e black)
simulador-financiamento.html ──────────┼─ assets/financiamento-app.js    tela dedicada
                                       ├─ assets/financiamento.js        regras puras + PDF
                                       ├─ assets/motor-caixa.js          motor (ganha cronograma)
                                       └─ assets/simuladores.js          SIM_EMPS + SimUnidades
```

| Arquivo | Papel |
|---|---|
| `assets/financiamento.js` | Funções puras (padrão IIFE + `module.exports`/`window.Financiamento`, como `assets/match.js`): montar a entrada do motor a partir das respostas, escolher a seguradora padrão, resumo para a tela, valores a copiar, URL do associativo, decidir destino (normal/Black Friday), dados do PDF. Sem DOM. |
| `assets/financiamento-popup.js` | `window.FinanciamentoPopup.abrir({ tema, contexto, aoCopiar })`. Monta o popup (desktop) ou a folha (celular, ≤ 860px), conduz os passos e chama `aoCopiar(valores)`. Não conhece o estado `S` do associativo. |
| `assets/financiamento-app.js` | Tela dedicada: passos, prévia, resultado, gráfico, PDF, "Levar ao associativo". |
| `assets/financiamento.css` | Estilos do popup e da tela dedicada, prefixo `.fz-`. Tema escuro por `[data-fz-tema="black"]` no container do popup. |
| `simulador-financiamento.html` | Página nova. Rota `/simulador-financiamento` sai do `cleanUrls` do `vercel.json`. |
| `assets/img/icones-3d/escudo.svg`, `documento.svg` | Ícones 3D novos, exportados do componente `Icone` do canvas (mesma regra de construção dos 12 existentes). |

Sem build, sem framework, sem dependência nova. jsPDF e jspdf-autotable já são carregados por CDN nos
associativos; a página dedicada carrega as mesmas versões (`jspdf@2.5.1`, `jspdf-autotable@3.8.2`).

## 4. Respostas e regras compartilhadas (`assets/financiamento.js`)

| Resposta | Regra |
|---|---|
| Imóvel | Unidade do portal (empreendimento → torre → unidade, via `SimUnidades`) **ou** valor digitado. |
| Valor do imóvel para a CAIXA | **Valor de avaliação bancária** da unidade (`detalhes().avaliacao`), igual ao Match. Sem avaliação na planilha → campo de valor aparece para digitar. |
| Cidade | Do empreendimento; no modo "digitar valor", pílulas Ribeirão Preto / Campinas / Sorocaba. Vira `municipio` por `MotorCaixa.MUNICIPIO_POR_CIDADE`. |
| Renda | Renda bruta familiar, > 0. |
| Nascimento | Do comprador mais velho. Data válida, idade ≥ 18. |
| 3 anos de FGTS | Padrão Sim. |
| Possui imóvel na cidade | Padrão Não. Sim → SBPE. |
| Mais de um comprador ou dependente | Padrão Não. **Só aparece** quando a renda permite subsídio (≤ R$ 4.000 e sem imóvel), como no Match. |
| Já recebeu subsídio | Padrão Não. Mesma condição de exibição acima. |
| Sistema | PRICE (padrão) ou SAC. |
| Prazo | Máximo (padrão) ou 360 / 300 / 240 meses; nunca acima do máximo pela idade. |
| Financiar menos | Opcional: valor desejado vira `valorFinanciamento` no motor. |

- O motor roda com `hoje = new Date()`.
- **Seguradora padrão** = maior `primeira` entre as 3. O corretor troca no resultado; a escolhida vai para o
  PDF e para "Parcela do financiamento".
- **Comprometimento** exibido vem de `resultado.comprometimento` (30% no MCMV e no SBPE SAC, 25% no SBPE
  PRICE). Nenhum texto fixo de "30%".
- **SBPE** (imóvel na cidade ou renda > R$ 13.000): rótulo "SBPE", sem subsídio (segmento verde some da
  barra), juros 10,92% / 11,49% como o motor devolve.

### 4.1 Mesmas regras do Match quando o valor de venda é conhecido

O Match aplica duas regras por fora do `MotorCaixa.simular` (`Match.avaliarUnidade`, `assets/match.js`).
Para os números baterem com o Match na mesma unidade, o simulador de financiamento aplica as duas sempre
que houver valor de venda, **reaproveitando as funções do Match** (exportar `travaFaixa3` e `simulaCaixa`
em vez de copiar a regra):

1. **Trava da Faixa 3:** renda de Faixa 3, avaliação acima de R$ 400 mil e venda abaixo disso → a CAIXA
   simula em R$ 400 mil.
2. **Teto do financiamento:** financiamento = menor entre a capacidade da CAIXA e
   `venda − subsídio − ato`; quando limita, o motor roda de novo com `valorFinanciamento` para achar a
   parcela certa (evita o erro "Recursos acima do valor do imóvel" no associativo).

| Onde | Venda | Ato |
|---|---|---|
| Popup do associativo | `S.valor` (Valor do imóvel do associativo) | `S.ato` |
| Tela dedicada com unidade do portal | valor associativo da unidade (o mesmo `venda` do Match) | 0 (o ato é negociado depois, no associativo) |
| Tela dedicada com valor digitado | não há: sem trava e sem teto | — |

- Quando o teto limita, "Financia até" mostra o valor limitado e uma linha abaixo:
  "A CAIXA aprova até R$ Y para esta renda; o valor do imóvel não pede mais que isso."
- **Entrada** exibida e no PDF = venda − financiamento − subsídio (− ato no popup) quando há venda; senão
  avaliação − financiamento − subsídio.

## 5. Motor: cronograma

`MotorCaixa.cronograma(entrada, resultado, codigoSeguradora)` → lista de `{ mes, data, encargo,
amortizacao, juros, mip, dfi, taxaAdm, saldo }` para os `resultado.prazo` meses.

- PRICE: prestação constante; SAC: amortização constante. Mesma taxa mensal do `simular`.
- MIP = saldo após a amortização do mês × taxa da faixa de idade na data da parcela (a taxa muda no
  aniversário). Na 1ª parcela usa o valor financiado inteiro, como o resumo da CAIXA. DFI = valor × taxa
  fixa, zera no último mês. Regras em `regras-motor-caixa.md` §4.
- **Testes:** para os casos de `tests/fixtures/caixa`, o encargo do mês 1 bate com `primeira` e o do último
  mês com `ultima` de cada seguradora (± R$ 0,05). Soma das amortizações = valor financiado (± R$ 0,05).
- Uso: gráfico "Parcela ao longo do prazo" e linha "Total pago" (tela dedicada e PDF). O popup não usa.

## 6. Popup nos associativos

### 6.1 Botão

Dentro do card do **passo 2 Cliente**, antes dos campos: ícone 3D da calculadora, "Ainda sem a simulação
da CAIXA?", uma linha de apoio e o botão vermelho **Simular financiamento**. No celular, texto em cima e
botão na largura toda. Visual por tema conforme o canvas (claro: fundo `#FFF6F7`; Black Friday: gradiente
escuro com borda vermelha).

### 6.2 Contexto que o popup recebe

`contexto = { empId, empNome, cidade, unidadeRotulo, avaliacao, venda, ato, renda, cliente, corretor }`
(`venda` = `S.valor`, `ato` = `S.ato`), lido do
estado do associativo na hora do clique. O cabeçalho do popup mostra
"Village Gaia · Apto 305 · avaliação R$ 220.000".

### 6.3 Passos

1. **Cliente** — renda (pré-preenchida se o associativo tiver) e nascimento. Prévia em pílulas: programa e
   faixa, juros, prazo, parcela máxima. Sem unidade ou sem avaliação: cidade e valor de avaliação aqui.
2. **Perfil** — interruptores do §4 (2 ou 4, conforme a renda).
3. **Condições** — PRICE × SAC com financiamento e parcela de cada um; prazo.
4. **Resultado** — "Financia até R$ …", barra financiamento / subsídio / entrada, 1ª parcela, subsídio,
   entrada, troca PRICE/SAC, seguradoras (padrão = maior), quadro "Vai para o simulador" com os 4 valores.
   Rodapé: **Baixar PDF** e **Copiar para o simulador**.

Voltar, Continuar, Enter avança, Esc fecha, foco preso no popup, foco volta ao botão ao fechar. Celular:
folha que sobe de baixo, 790px de altura máxima, rolagem interna, rodapé fixo.

### 6.4 Copiar

Preenche no estado do associativo e chama `sincronizaCampos(); render();`:

| Campo | Valor |
|---|---|
| Renda do cliente (`S.renda`) | renda usada na simulação |
| Valor do financiamento (`S.financiado`) | `valorFinanciamento` (o % ao lado recalcula sozinho) |
| Subsídio (`S.subsidio`) | `subsidio` (0 no SBPE) |
| Parcela do financiamento (`S.parcFin`) | `primeira` da seguradora escolhida |

Nada mais muda: valor do imóvel, FGTS, bônus, ato, datas e política ficam como estavam.

Depois de copiar: popup fecha; o botão do passo Cliente vira a faixa verde "Financiamento simulado ·
MCMV Faixa 1 · 4,50% a.a. · 420 meses · PRICE" com **Ver simulação** (reabre no resultado) e **PDF**; os
campos copiados ganham fundo verde e a etiqueta "simulação"; toast "4 campos preenchidos com a simulação ·
Desfazer" por 6 s (Desfazer volta os 4 valores anteriores). **Editar um campo copiado tira a marca só dele.**
A marca não vai para o PDF do associativo.

**Quando o contexto muda depois de copiar** (decisão do usuário): se o corretor troca o empreendimento ou a
unidade, ou o Valor do imóvel fica diferente da venda usada na simulação, os valores **ficam nos campos**,
mas a faixa verde vira amarela: "A unidade mudou depois da simulação", com o botão **Refazer** (reabre o
popup no passo 1 com as respostas anteriores e o contexto novo). O botão **Limpar simulação** (`b-reset`)
apaga tudo, inclusive a faixa e as marcas.

### 6.5 Black Friday

Mesmo módulo, `tema: 'black'`. O popup herda o tema escuro do `simulador-bf-dark.css` (cores do canvas,
quadros B-*). Nenhuma conta muda por ser Black Friday.

## 7. Tela dedicada `/simulador-financiamento`

- **Abertura (desktop):** hero branco com título "Quanto o seu cliente consegue financiar?", composição 3D
  (calculadora, casa, moedas, chave, documento, escudo) e card de prévia; abaixo, trilha dos passos à
  esquerda e o passo 1 à direita. **Celular:** tela de abertura com "Começar simulação" e "Repetir a última
  simulação".
- **Passos:** Imóvel, Renda, Idade, Perfil, Condições (uma pergunta por tela no celular; trilha + pergunta
  no desktop). Cada resposta vira linha na trilha (desktop) ou pílula no topo (celular), clicável para
  editar.
- **Prévia ao vivo** (desktop, abaixo da trilha): programa, juros, prazo, subsídio e parcela máxima assim
  que imóvel e renda existem.
- **Resultado:** "Financia até R$ …", indicadores (enquadramento, juros nominal/efetivo, prazo, subsídio,
  taxa de administração), barra de composição, 1ª e última parcela, gráfico PRICE × SAC com tabela ao lado
  (financia, entrada, 1ª, última, total pago), seguradoras, "Como chegamos aqui", respostas, aviso legal.
  Ações: Editar respostas, Baixar PDF, **Levar ao associativo**, Nova simulação.
- **Levar ao associativo:** URL com os parâmetros que o associativo já aceita
  (`emp, unidade, renda, idade, valor, fin, sub, parcFin`) — mesmo formato de `Match.urlAssociativo`. Sem
  unidade do portal, vai só com `renda, fin, sub, parcFin` (o associativo precisa aceitar parâmetros sem
  `emp`; hoje ignora tudo se `emp` faltar). Destino conforme §2 (pergunta em popup pequeno quando a regra
  de Black Friday vale). `valor` = venda da unidade, como o Match.
- **Marca de origem:** a URL leva também `origem=financiamento` e as respostas completas num parâmetro
  `fz` (nascimento, perfil, sistema, prazo, seguradora; formato curto à escolha do construtor). Só com
  `origem=financiamento` o associativo mostra a marca "simulação" nos campos e a faixa verde com
  **Ver simulação** e **PDF** (as respostas do `fz` bastam para reabrir o resultado). Links do Match, que
  não levam esse parâmetro, continuam como hoje. O Desfazer não aparece na chegada (não havia valor
  anterior).
- **"Repetir a última simulação":** respostas salvas em `sessionStorage` (como `mt-ultima` do Match).
- **Gráfico:** linhas PRICE `#E4032B` e SAC `#2563A8` (validadas para daltonismo), legenda sempre visível,
  tooltip ao passar o mouse com ano, idade e as duas parcelas, tabela ao lado como leitura alternativa.

## 8. Home

Card novo em "Ferramentas" (`index.html`): ícone `calculadora.svg`, "Simulador de Financiamento", logo
depois do Simulador Associativo. Entra também nos links do cabeçalho e do menu do celular, no mesmo padrão
dos outros.

## 9. PDF

Uma folha A4, gerada com jsPDF (mesmo jeito do PDF do associativo, logo carregado por canvas), layout do
quadro "PDF da simulação" no canvas:

- Cabeçalho: logo, "Simulação de financiamento", data de emissão.
- Cliente, corretor (do associativo, ou campos opcionais na tela dedicada antes de baixar), imóvel e valor
  de avaliação.
- Bloco principal: valor financiado, 1ª parcela (com % da renda), subsídio, entrada mínima, barra.
- Condições (programa, produto CAIXA, sistema, prazo, juros, taxa adm., parcela máxima) e dados do cliente.
- Parcela por seguradora (escolhida marcada).
- PRICE × SAC (tabela) e mini-gráfico.
- Rodapé: "Simulação estimada… Não é aprovação de crédito…".
- Nome do arquivo: `financiamento-<cliente ou empreendimento>-<data>.pdf`.

O PDF da tela dedicada e o do popup são o mesmo (`Financiamento.dadosPdf` + um desenhista único).

## 10. Erros e casos-limite

| Situação | Comportamento |
|---|---|
| Motor devolve `erro` (idade acima de 70a6m, fora do enquadramento, cidade sem regra) | Resultado vira um card de aviso com o motivo em português e o que fazer (ex.: "Renda acima de R$ 13.000 com imóvel acima de R$ 600 mil não enquadra no MCMV"). Copiar e PDF ficam desligados. |
| Planilha não carregou | Modo "digitar valor" fica como padrão na tela dedicada; no popup, campo de valor no passo 1. |
| Unidade sem avaliação | Campo de valor no passo 1, com aviso "Sem avaliação na planilha". |
| Renda vazia no associativo | Popup abre com o campo de renda vazio e focado. |
| Associativo já tinha financiamento digitado | Copiar sobrescreve; Desfazer volta os valores anteriores. |

## 11. Visual

Padrão visual 2.0 do Match (`docs/design/match-unidades-nova-ux/README.md`): DM Sans 800 nos títulos,
grafite `#2B3033`, botão principal 52–56px raio 16–18 com sombra vermelha, cartões 20–28px, ícones 3D,
entrada em cascata, flutuação dos ícones, tudo desligado com `prefers-reduced-motion`. Medidas e cores
exatas nos quadros do canvas (fonte de verdade visual). A tela dedicada segue o canvas; os associativos
mantêm o visual deles e só ganham o botão, a faixa verde, a marca nos campos e o popup.

## 12. Testes (`node --test tests/*.test.js`)

- `tests/motor-caixa.test.js`: cronograma (§5).
- `tests/financiamento.test.js`: entrada do motor a partir das respostas (cidade, nascimento, perfil),
  seguradora padrão = maior, valores a copiar (incl. SBPE sem subsídio), URL do associativo com e sem
  unidade, destino Black Friday × normal, exibição condicional dos interruptores de subsídio.
- Verificação no navegador: os dois associativos (desktop e celular) e a tela dedicada, incluindo copiar,
  desfazer, editar campo copiado e PDF.

## 13. Deixado ao construtor

- Nome e forma exata das funções internas dos três módulos novos.
- Como ligar a campanha Black Friday: constante única (ex.: `CAMPANHA_BF = { ativa: true, cidades:
  ['Ribeirão Preto'] }` em `financiamento.js`) que desligue a pergunta do §2 com uma edição.
- Animação de abertura do popup e da folha.
- Altura e quebras dos quadros no celular pequeno (≤ 360px).

**Chamadas minhas (não discutidas):** padrões do perfil iguais ao Match; interruptores de subsídio só
quando a renda permite; marca "simulação" some ao editar o campo; toast com Desfazer; PDF único para
popup e tela dedicada; parâmetros de URL também sem unidade; trava da Faixa 3 e teto
venda − subsídio − ato iguais ao Match (§4.1), com ato 0 na tela dedicada; parâmetro
`origem=financiamento` + `fz` para o associativo reconhecer a simulação.

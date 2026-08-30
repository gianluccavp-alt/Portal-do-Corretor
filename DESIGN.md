---
name: Portal do Corretor
description: Sistema visual Grupo Direcional — ferramenta de mesa e de campo para consulta de unidades e simulação de fluxo
colors:
  direcional-red: "#E4032B"
  direcional-red-deep: "#B8001F"
  ink: "#3A4043"
  slate-grey: "#727A7D"
  hairline: "#E7E9EA"
  app-bg: "#F5F6F7"
  surface: "#FFFFFF"
  field-muted: "#FAFBFB"
  success: "#1E8E4A"
  success-surface: "#EFF9F2"
  success-hairline: "#C7E7D3"
  warning: "#B57200"
  warning-surface: "#FFF7E6"
  error: "#C4001C"
  error-surface: "#FDEEF0"
typography:
  display:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "clamp(2rem, 5vw, 3.4rem)"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.5px"
  headline:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "2.15rem"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.6px"
  title:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "normal"
  body:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "0.76rem"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "0.04em"
  overline:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "0.1em"
rounded:
  xs: "8px"
  sm: "9px"
  md: "14px"
  lg: "16px"
  xl: "18px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "14px"
  lg: "22px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.direcional-red}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    padding: "0.62rem 1.05rem"
  button-primary-hover:
    backgroundColor: "{colors.direcional-red-deep}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    padding: "0.62rem 1.05rem"
  button-ghost:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "0.62rem 1.05rem"
  button-ghost-hover:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.direcional-red}"
    rounded: "{rounded.sm}"
    padding: "0.62rem 1.05rem"
  chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.slate-grey}"
    rounded: "{rounded.pill}"
    padding: "0.42rem 0.7rem"
  chip-selected:
    backgroundColor: "{colors.direcional-red}"
    textColor: "{colors.surface}"
    rounded: "{rounded.pill}"
    padding: "0.42rem 0.7rem"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "0.6rem 0.7rem"
  input-readonly:
    backgroundColor: "{colors.field-muted}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "0.6rem 0.7rem"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "1.35rem"
---

# Design System: Portal do Corretor

## Overview

**Creative North Star: "The Field Companion"**

O Portal do Corretor é o instrumento que o corretor abre ao lado do comprador — no
celular, numa mesa de stand, sob a pressão de uma negociação. O sistema visual
existe para deixar o dado à frente e o cliente confortável: superfícies brancas,
uma linha cinza fininha que organiza sem pesar, e o vermelho Direcional reservado
para o que exige ação ou atenção. Nada compete com o número.

A atmosfera é **precisa, institucional e sóbria**. É a cara de um sistema oficial —
o corretor precisa confiar que o que ele vê é o que o comercial vê. Isso se traduz
em tipografia funcional (uma única família, DM Sans), títulos com respiro e leve
aperto de tracking, rótulos em caixa-alta discretos, e zero ornamento. O refinamento
mora no detalhe: o halo vermelho a 10% no foco de um campo, a barrinha de 22 px
antes de um rótulo de passo, o realce verde-suave de um valor-destaque.

Este documento descreve o **mundo Direcional** — implementado hoje na home
(`index.html`) e nos dois simuladores (`simulador-associativo.html`,
`simulador-tabela-direta.html`). O visual dourado + serifado (Playfair Display,
`--gold #9E6B2E`, fundo creme) que ainda vive em `empreendimento.html`,
`promocionais.html` e `assets/styles.css` é **legado e anti-referência**: as duas
páginas devem convergir para este sistema, não o contrário.

**Key Characteristics:**
- Uma família tipográfica só (DM Sans), do rótulo ao título.
- Vermelho Direcional como voz única de ação e status — nunca como preenchimento decorativo.
- Superfícies planas: borda de 1 px define os containers; sombra é resposta a estado.
- Fundo `#F5F6F7`, cartões brancos, cantos suaves (9–16 px).
- Mobile-first: alvos de toque generosos por padding, quebra graciosa de grids.

## Colors

Paleta institucional restrita: um vermelho de marca, uma escala de cinzas neutros e
três cores de estado. Sem cor decorativa.

### Primary
- **Vermelho Direcional** (`#E4032B`): a voz de ação e de marca. Aparece em botões
  primários, estado ativo de chips, rótulos de passo (`.step-label`), a marca no
  eyebrow, `<em>` no título, borda e halo de foco, e realce de seleção. É deliberadamente
  raro — quando aparece, significa "aja aqui" ou "olhe aqui".
- **Vermelho Direcional Profundo** (`#B8001F`): hover e estado pressionado do primário.

### Neutral
- **Tinta** (`#3A4043`): texto principal e valores. Não é preto puro — assenta a página.
- **Cinza Ardósia** (`#727A7D`): texto secundário, rótulos, hints, placeholders.
- **Fio de Cabelo** (`#E7E9EA`): todas as bordas e divisores. Sólido para containers,
  tracejado (`1px dashed`) para separações internas de uma mesma seção.
- **Fundo do App** (`#F5F6F7`): fundo de toda a aplicação.
- **Superfície** (`#FFFFFF`): cartões, campos, barras, modais.
- **Campo Silenciado** (`#FAFBFB`): fundo de input `[readonly]` — sinaliza "calculado, não editável".

### Tertiary — Cores de Estado
- **Sucesso** (`#1E8E4A`) sobre **Superfície de Sucesso** (`#EFF9F2`) com **Fio de Sucesso**
  (`#C7E7D3`): valores-destaque favoráveis (folga de tabela, desconto, `.ui-stat.dest`).
- **Alerta** (`#B57200`) sobre **Superfície de Alerta** (`#FFF7E6`): campo/hint em atenção
  (`input.warn`, `.hint.warn`).
- **Erro** (`#C4001C`) sobre **Superfície de Erro** (`#FDEEF0`): validação falha
  (`input.bad`, `.hint.err`).

### Named Rules
**The One Voice Rule.** O vermelho Direcional cobre no máximo ~10% de qualquer tela.
Ele é para ação e status, nunca para preencher área. Se um bloco inteiro ficou
vermelho, está errado.

**The Neutral Canvas Rule.** Toda superfície começa branca sobre fundo `#F5F6F7`,
delimitada por `1px solid #E7E9EA`. Não introduza cinzas ou beges novos; a escala
já resolve texto, borda, fundo e campo desabilitado.

## Typography

**Display / Body / Label Font:** DM Sans (com `system-ui, sans-serif` de fallback).
Pesos em uso: 300, 400, 500, 700.

**Character:** Uma grotesca humanista, neutra e altamente legível em tamanho pequeno
e em tela de celular. A personalidade não vem da fonte — vem do tracking negativo nos
títulos e do tracking aberto em caixa-alta nos rótulos. É a voz de um sistema, não de
uma marca de luxo.

### Hierarchy
- **Display** (700, `clamp(2rem, 5vw, 3.4rem)`, LH 1.1, tracking `-0.5px`): título de
  hero da home. `<em>` fica vermelho, sem itálico.
- **Headline** (700, `2.15rem` / `1.5rem` mobile, LH 1.15, tracking `-0.6px`): `h1` das
  páginas de simulador.
- **Title** (700, `0.95rem`, LH 1.3): subtítulos de seção (`.sub`, `.ui-titulo`,
  `.emp-info-nome`). Peso alto, tamanho quase de corpo — hierarquia por peso, não por escala.
- **Body** (400, `15px`, LH 1.5): texto corrido. Parágrafos de apoio limitados a ~56–60ch
  (`max-width: 56ch`–`60ch`).
- **Label** (500, `0.76rem`, tracking `0.04em`, UPPERCASE): rótulos de campo de formulário,
  chaves de stat (`.ui-lab`, `.u-meta-k`).
- **Overline** (500, `0.78rem`–`0.86rem`, tracking `0.1em` / `0.06em`, UPPERCASE, vermelho):
  rótulo de passo (`.step-label`) e eyebrow de marca (`.hero-brand`).

### Named Rules
**The Weight-Not-Size Rule.** A separação entre título de seção e corpo é feita por
peso (700 vs 400), não por salto de tamanho. Títulos de seção ficam perto de `0.95rem`.

**The Uppercase-Is-Tracked Rule.** Todo texto em caixa-alta leva tracking ≥ `0.04em`
(rótulos) ou `0.1em` (passos). Caixa-alta sem tracking não existe neste sistema.

## Layout

Coluna única centrada. Container de conteúdo `max-width: 1120px` (simuladores) /
`1100px` (home), com padding `1.75rem 2rem 4rem` no desktop e `1.25rem 1.1rem 3rem`
no mobile.

O **hero** é uma faixa branca com o padrão de setas Direcional
(`assets/img/hero-bg.png`, `center/cover`), padding `2.75rem 2rem 2.25rem`, fechada
por `border-bottom: 1px solid #E7E9EA` — sem imagem escura, sem gradiente. O logo
Direcional fica ancorado no canto superior direito (`position: absolute`, altura
~52 px desktop / ~34 px mobile).

Formulários usam grids utilitários `.g2` / `.g3` / `.g4` (2/3/4 colunas) que colapsam
para 2 colunas em `≤820px` e 1 coluna em `≤480px`. Gap padrão de grid `0.9rem`. Passos
verticais separados por `margin-bottom: 1.5rem`.

Ritmo de espaçamento em `rem`, informal mas consistente: `0.35 / 0.55 / 0.7 / 0.9 /
1 / 1.35 / 1.5 / 1.75 / 2 rem`. Densidade média — enxuto sem ser apertado; padding de
cartão `1.35rem` desktop, `1rem` mobile.

Breakpoints observados: `480`, `560`, `700`, `820`, `980`, `1100`, `1240 px`. Os
estruturais são `~700px` (hero e wrap compactam) e `~820px` (grids de formulário
caem para 2 colunas).

## Elevation & Depth

**Plano por padrão; a borda é a estrutura.** Cartões, campos e barras são definidos
por `1px solid #E7E9EA` sobre branco, não por sombra. Profundidade fixa (barra de
hero, modais) vem de contraste de superfície e borda, não de camadas empilhadas.

Sombra é **resposta a estado**, quase sempre em hover, e sempre difusa e de baixa
opacidade:

### Shadow Vocabulary
- **Hover de cartão** (`box-shadow: 0 6px 22px rgba(58,64,67,.10)`): cartões de cidade
  e empreendimento na home ao passar o mouse (acompanha `translateY(-2px)`).
- **Seleção ativa** (`box-shadow: 0 4px 20px rgba(228,3,43,.16)`): cartão de cidade
  selecionado — sombra tingida de vermelho.
- **Hover de arte** (`filter: drop-shadow(0 8px 18px rgba(58,64,67,.16))`): cards de
  política/ranking (imagens PNG prontas) ao passar o mouse.
- **Halo de foco** (`box-shadow: 0 0 0 3px rgba(228,3,43,.10)` + borda vermelha):
  campos de formulário em foco. É o gesto de refinamento assinatura do sistema.
- **Barra fixa** (`box-shadow: 0 -2px 16px rgba(28,22,16,.09)`): barras fixas de
  rodapé (ex.: salvar em `/promocionais`).

### Named Rules
**The Flat-At-Rest Rule.** Nenhuma superfície tem sombra em repouso. Se um cartão
precisa "saltar" sem que o usuário interaja com ele, aumente o contraste de borda ou
o espaço em volta — não adicione sombra.

## Shapes

Cantos suaves e consistentes, sem geometria dura e sem círculos além de pills.

- **Raio:** campos e botões `9px` (`--rounded.sm`); cartões `14px`; cartões de
  navegação/home e containers de imagem `16px`; modais `16–18px`; caixas pequenas de
  stat/meta `8–10px`; chips e badges de status são pills (`999px` / `100px`).
- **Bordas:** sempre `1px`. Sólida em `#E7E9EA` para containers; `1px dashed #E7E9EA`
  para divisões internas (`.emp-info`, `.sub`, `.unid-info`).
- **Foco:** deslocamento de cor de borda para vermelho + halo de 3 px a 10% de
  opacidade. Nunca `outline` de sistema.
- **Barra de passo:** pseudo-elemento `::before` de `22px × 2px`, `border-radius: 2px`,
  em vermelho, antes de cada `.step-label`.

## Components

### Buttons
- **Shape:** cantos suaves (`9px`), borda `1px`, peso 500, transição `0.15s`.
- **Primary:** fundo e borda `#E4032B`, texto branco, padding `0.62rem 1.05rem`.
  Hover → fundo e borda `#B8001F`.
- **Ghost:** fundo branco, borda `#E7E9EA`, texto tinta. Hover → borda e texto
  `#E4032B` (fundo permanece branco).
- **Icon button:** mesmo tratamento do ghost em formato quadrado com cantos `9px`.

### Chips (filtros e políticas)
- **Style:** pill (`999px`), fundo branco, borda `#E7E9EA`, texto cinza ardósia,
  `0.78rem`, padding `0.42rem 0.7rem`.
- **Hover:** borda e texto viram vermelho.
- **Selected (`.on`):** fundo e borda `#E4032B`, texto branco.

### Inputs / Fields
- **Style:** fundo branco, borda `1px solid #E7E9EA`, raio `9px`, padding
  `0.6rem 0.7rem`, texto tinta. Rótulo acima em Label (caixa-alta, `0.76rem`, cinza).
- **Focus:** borda `#E4032B` + `box-shadow: 0 0 0 3px rgba(228,3,43,.10)`.
- **Readonly (calculado):** fundo `#FAFBFB`, texto em peso 700 — comunica "resultado,
  não entrada".
- **Error (`.bad`):** borda `#C4001C`, fundo `#FDEEF0`, hint em `#C4001C` peso 500.
- **Warn (`.warn`):** borda `#B57200`, fundo `#FFF7E6`, hint em `#B57200` peso 500.

### Cards / Containers
- **Corner:** `14px` (conteúdo) a `16px` (cartões de navegação da home).
- **Background:** branco sobre fundo `#F5F6F7`.
- **Border:** `1px solid #E7E9EA`. Divisões internas em `1px dashed #E7E9EA`.
- **Shadow:** nenhuma em repouso (ver Elevation).
- **Padding:** `1.35rem` desktop / `1rem` mobile.
- **Home nav cards:** hover → borda vermelha + `translateY(-2px)` + sombra de hover;
  ativo → borda vermelha + sombra tingida de vermelho.

### Navigation
No mundo Direcional atual não há barra de navegação persistente (home e simuladores
são fluxos de página única). A `.nav` de abas em `empreendimento.html` pertence ao
sistema legado; ao migrar aquela página, redesenhe a navegação neste vocabulário —
abas com sublinhado vermelho de 2 px no estado ativo, rótulo em Label, fundo branco
com `border-bottom: 1px solid #E7E9EA`.

### Step Label (assinatura)
Rótulo de passo do fluxo: caixa-alta, `0.78rem`, tracking `0.1em`, vermelho, precedido
por uma barra vermelha de `22px × 2px`. Marca o início de cada etapa de um simulador
ou da home ("Passo 1 · Escolha a cidade").

### Stat Strip (assinatura)
Faixa horizontal de valores da unidade escolhida (`.ui-stats` / `.ui-stat`): colunas
com `border-right: 1px solid #E7E9EA`, chave em Label cinza, valor em `0.95rem` peso
700 tinta. A coluna-destaque (`.dest`) ganha fundo `#EFF9F2`, borda `#C7E7D3`, raio
`10px` e valor em verde-sucesso. No mobile as colunas perdem o divisor e a destaque
ocupa 100% da largura.

### Ranking / Policy Cards (assinatura)
Cards de política da operação renderizados a partir de artes PNG prontas em
`assets/img/ranking/` (`aco`, `bronze`, `prata`, `ouro`, `diamante`). O container é
transparente e sem borda; a seleção é leve — `transform: scale(1.03)` +
`drop-shadow(0 7px 16px rgba(228,3,43,.28))`. Não desenhe moldura em volta dessas artes.

## Do's and Don'ts

### Do:
- **Do** usar DM Sans para tudo. Rótulo, corpo e título saem da mesma família; a
  hierarquia é peso + tracking.
- **Do** delimitar cada superfície com `1px solid #E7E9EA` sobre branco, fundo de
  página `#F5F6F7`.
- **Do** reservar o vermelho `#E4032B` para ação e status (≤10% da tela). Hover do
  primário é sempre `#B8001F`.
- **Do** dar foco com borda vermelha + halo `0 0 0 3px rgba(228,3,43,.10)` — nunca
  `outline` do navegador.
- **Do** sinalizar valores calculados/readonly com fundo `#FAFBFB` e peso 700.
- **Do** abrir cada etapa com o `.step-label` vermelho e sua barrinha de 22 px.
- **Do** manter alvos de toque confortáveis por padding e colapsar grids
  (`.g3`/`.g4` → 2 col em ≤820px → 1 col em ≤480px).
- **Do** usar verde-sucesso (`#1E8E4A` / `#EFF9F2` / `#C7E7D3`) só para valores
  favoráveis de negócio (folga de tabela, desconto).

### Don't:
- **Don't** trazer Playfair Display, o dourado (`#9E6B2E` / `#C9A96E`), o fundo creme
  (`#FAF7F2`) ou a tinta `#1C1610` do sistema legado. São anti-referência.
- **Don't** re-tematizar a página por empreendimento (o `--gold`/`--dark`/`--green`
  variável de `empreendimento.html`). A identidade é uma só: Direcional.
- **Don't** adicionar sombra a cartões em repouso. Sombra é resposta a hover/foco.
- **Don't** usar o vermelho como cor de fundo de blocos grandes ou como preenchimento
  decorativo.
- **Don't** introduzir novos cinzas, bordas ou raios fora das escalas aqui — `xs 8` /
  `sm 9` / `md 14` / `lg 16` / `xl 18` / `pill`.
- **Don't** usar caixa-alta sem tracking.
- **Don't** escurecer o hero com imagem/gradiente; ele é branco com o padrão de setas
  e borda inferior.

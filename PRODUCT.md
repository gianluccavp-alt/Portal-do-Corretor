# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Two audiences with equal weight, both operating in a sales context:

- **Corretores parceiros (externos)** — consultam disponibilidade, valores, plantas e
  fluxo de pagamento de um empreendimento antes ou durante o atendimento a um comprador.
- **Time comercial interno da SPI / Grupo Direcional** — gerentes e coordenadores usam
  as mesmas telas como ferramenta de mesa e para simular fluxos de negociação.

A página `/promocionais` é o único recorte estritamente interno (protegida por senha
compartilhada, marca unidades como promocionais para o comercial).

## Product Purpose

Portal do corretor para o interior de São Paulo (Campinas e Ribeirão Preto). Dá a
corretores e ao comercial uma visão única e confiável de cada empreendimento:
unidades disponíveis, andar/bloco, valor final, folga de tabela, plantas, galeria,
mapa de vagas — e simuladores que calculam o fluxo de pagamento da unidade escolhida.
Sucesso = o corretor chega ao atendimento sabendo exatamente o que pode oferecer e por
qual condição, sem depender de planilha solta ou de pedir número para o comercial.

## Positioning

O que define o produto é a combinação de dois mecanismos, não cada um isolado:

1. **Disponibilidade ao vivo** — as telas são espelho em tempo real da planilha oficial
   de vendas (Google Sheets publicado em CSV, lido no navegador). O que o corretor vê é
   o que o comercial vê, sem defasagem e sem exportação manual.
2. **Simuladores de fluxo integrados à unidade** — Simulador Associativo (Pro Soluto
   MCMV) e Simulador de Tabela Direta calculam parcelas, sinais, anuais e saldo
   pós-chaves com as regras reais da operação, já partindo dos valores da unidade
   selecionada.

Um catálogo de imóveis comum não tem nem o espelho ao vivo da tabela de vendas nem os
simuladores com as regras de financiamento da operação.

## Operating Context

- Uso em atendimento comercial — muitas vezes no celular, ao lado do cliente, ou em
  mesa de negociação. Consulta rápida importa mais que navegação profunda.
- Dados vêm de **uma planilha do Google Sheets** (todos os empreendimentos na mesma
  aba, identificados pela coluna `Nome do Empreendimento`). O parser casa colunas por
  aproximação de nome (produto, final, andar, bloco/etapa, tipo/planta, valor final,
  B.A., folga de tabela, valor de avaliação).
- Books de mesa (PDF) hospedados em GitHub Releases, linkados por empreendimento.
- Unidades promocionais de Ribeirão Preto: lista mantida num Web App do Google Apps
  Script (`docs/apps-script-promocionais.gs`); em modo dev cai para `localStorage`.
- Fluxo de deploy documentado em `WORKFLOW.md`: branch → PR → merge na `main` →
  **deploy manual na Vercel** (sem CI). Dois desenvolvedores no mesmo repositório
  (`github.com/gianluccavp-alt/Portal-do-Corretor`); sincronizam via `git pull` na `main`.

## Capabilities and Constraints

- **Site 100% estático**: HTML + CSS + JS puro, **sem build, sem framework, sem
  bundler**. Qualquer trabalho futuro deve continuar rodando ao abrir os arquivos /
  servir estático na Vercel (preset "Other", output = raiz).
- Páginas: `index.html` (home: cidade → empreendimento), `empreendimento.html?e=<id>`
  (detalhe, abas Unidades / Plantas / Implantação / Galeria / Mapa de Vagas),
  `promocionais.html` (interno), `simulador-associativo.html`,
  `simulador-tabela-direta.html`.
- `assets/config.js` é a fonte de conteúdo por empreendimento (13 hoje, entre Campinas
  e Ribeirão Preto): hero, pills, proximidades, plantas, galeria, implantação, vagas,
  link do book. Imagens ausentes viram placeholder "Imagens em breve".
- `assets/data.js` é o motor de dados; `assets/simuladores.js` a lógica dos simuladores.
- Dependência externa em runtime: Google Sheets CSV (com fallback para proxies
  públicos corsproxy / allorigins em caso de CORS) e Google Fonts.
- Fonte de dados e regras de simulação são **sensíveis ao negócio** (folga de tabela,
  valor comercial mínimo, condições de fluxo) — nunca expor a compradores.
- Terminologia recorrente: empreendimento, unidade, final, andar, bloco/etapa,
  folga de tabela, B.A., Pro Soluto, MCMV, associativo, tabela direta, book de mesa,
  valor comercial mínimo, pós-chaves.
- Simuladores e exportação de PDF de unidades disponíveis existem hoje apenas para
  Ribeirão Preto.

## Brand Commitments

- **Identidade que vale: Grupo Direcional** — vermelho `#E4032B` (escuro `#B8001F`),
  tipografia DM Sans, logo Direcional (`assets/img/logo-direcional.jpg`), plano de
  fundo de setas (`assets/img/hero-bg.png`). Referência viva: a home (`index.html`).
- Nome de produto exposto ao usuário: **"Portal do Corretor"** (o repositório e o
  README antigo também usam "Site Produtos SPI" internamente).
- **Legado a alinhar (anti-referência, não alvo):** as páginas de empreendimento e os
  simuladores usam hoje um visual dourado (`--gold #9E6B2E`) com Playfair Display, tema
  "premium". Isso é herança de um portal anterior e deve convergir para a identidade
  Direcional em trabalhos futuros — não deve ser preservado nem expandido.
- Cards de política/ranking usam artes prontas em `assets/img/ranking/` (aço, bronze,
  prata, ouro, diamante).
- Idioma: pt-BR.

## Evidence on Hand

- Conteúdo real de 13 empreendimentos em `assets/config.js` com textos, badges e
  proximidades.
- Biblioteca de imagens reais por empreendimento em `assets/img/<slug>/` (fachadas,
  galeria de lazer, plantas, implantação, mapa de vagas).
- Books de mesa em PDF (GitHub Releases, tag `books-v1`).
- Dados de unidades vêm da planilha oficial em runtime — **não há dataset versionado no
  repo**; trabalho de design não deve inventar números de unidade, valores ou
  disponibilidade.
- Não há depoimentos, cases, imprensa ou métricas de uso — não fabricar.

## Product Principles

1. **A tela é espelho da tabela oficial.** Quando dado ao vivo e layout conflitarem, o
   dado vence; nada de estado que sugira disponibilidade diferente da planilha.
2. **Consulta em segundos, no celular, ao lado do cliente.** Otimize para leitura
   rápida de valores e disponibilidade antes de qualquer profundidade.
3. **Informação sensível não vaza para o comprador.** Folga de tabela, valor comercial
   mínimo e regras de fluxo são para corretor e comercial.
4. **Sem build, sem framework.** Simplicidade estática é uma escolha de produto:
   qualquer dev abre, edita e publica na Vercel sem toolchain.
5. **`config.js` é o painel de controle.** Adicionar ou ajustar empreendimento é
   editar um objeto, não tocar em telas.

## Accessibility & Inclusion

Nenhum requisito formal estabelecido. Piso prático: uso pesado em celular sob luz de
ambiente comercial e toque — alvos de toque generosos, contraste alto para valores, e
degradação graciosa quando a planilha ou os proxies falham.

# Match de Unidades · Nova UX — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trocar o formulário único de `match-unidades.html` por um fluxo em linha do tempo (uma pergunta por vez), com revelação animada do resultado e lista com "melhor match", no Padrão visual 2.0 aprovado.

**Architecture:** As regras de negócio não mudam (`assets/match.js`, `motor-caixa.js`, `match-prosoluto.js` intactos). Entra um módulo puro novo, `assets/match-fluxo.js`, que guarda tudo que é decisão do fluxo (validação por etapa, texto da trilha, perguntas condicionais, ordenação, melhor match) e é testado com `node --test`. `assets/match-app.js` vira o controlador da tela: guarda as respostas, desenha a etapa atual, chama `Match.buscar` e desenha a revelação e o resultado. HTML e CSS são reescritos seguindo o canvas.

**Tech Stack:** HTML + CSS + JS puro (ES5, sem build), `node:test` + `node:assert/strict`, jsPDF + autotable (já carregados), SVGs em `assets/img/icones-3d/`, servidor estático da `.claude/launch.json` (`portal-do-corretor`) para verificação.

**Spec:** referência visual aprovada em `docs/design/match-unidades-nova-ux/` (README + `fonte/Main.dc.html` com todo o CSS, animações e navegação do protótipo; `fonte/Desktop-*.dc.html` para desktop). Regras: `docs/superpowers/specs/2026-10-15-match-unidades-design.md`.

## Global Constraints

- Site 100% estático, sem build, sem framework, sem npm. ES5 (`var`, `function`) como o resto de `assets/`.
- Módulo puro no padrão de `assets/match.js`: IIFE `(function (raiz) { 'use strict'; ... })(this);` exportando `module.exports` no Node e `raiz.MatchFluxo` no navegador; no Node faz `require('./match.js')`.
- Nada de regra de negócio nova: faixa, subsídio, financiamento, Pro Soluto e aprovação continuam vindo de `Match.buscar` / `Match.resumoCliente` / `Match.validarCliente`.
- Visual: DM Sans 400/500/600/700/800; vermelho `#E4032B` só em ação e estado; grafite de título `#2B3033`; texto secundário `#5C6467`; ouro `#F5AE1E`; fundo `#F5F6F7`. Medidas e animações copiadas de `fonte/Main.dc.html` (classes `.btn-pri`, `.opt`, `.pill`, `.tile`, `.sw`, `.field`, `.pol`, `.seg`, `.row`, keyframes `enter`, `float`, `pop`, `pulse`, `ring`).
- O reset de botões usa `:where(.mt-app) button {…}` (especificidade zero). Nunca `.mt-app button`.
- Sem badge "Planilha ao vivo" (removida na aprovação).
- `prefers-reduced-motion: reduce` → nenhuma animação; contagem da revelação mostra o número final direto.
- Toques ≥ 44px; todo controle é `<button>`/`<input>`/`<a>` real; interruptores do perfil são `<button role="switch" aria-checked>`.
- Textos fixos do rodapé de estimativa e do PDF não mudam.
- Testes: `node --test tests/*.test.js` a partir da raiz. Commits terminam com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Decisões deste plano (o canvas não fixava)

- **Ordem das etapas:** `onde`, `renda`, `ato`, `nascimento`, `perfil`, `politica`. Depois: `revelacao`, `resultado`. Etapa 0 = `abertura`.
- **Perfil condicional:** `fgts` e `possuiImovel` sempre; `fatorSocial` e `subsidioAnterior` só quando `Match.temSubsidio(renda, possuiImovel)`. Ligar "Possui imóvel" esconde os dois na hora.
- **Padrões:** `fgts: true`, `possuiImovel: false`, `fatorSocial: false` (conservador: mostra o aviso "Sem dependente, a CAIXA concede só 30% do subsídio."), `subsidioAnterior: false`, `politicaId: 'aco'` (mesmo padrão de hoje).
- **Ato:** "Ato padrão do empreendimento" (`ato: null`) é o padrão. O texto do padrão é `R$ 1.500` quando `empId === 'ipiranga'`, `R$ 2.500` para um empreendimento específico, e "o padrão de cada empreendimento" para Todos (usa `Match.atoDe`).
- **Nascimento:** três campos (dia, mês, ano) → `new Date(ano, mes - 1, dia)`; rejeita data inexistente (31/02) e data futura. Resolve as pendências 1 (nascimento no futuro) e 5 (fuso no Safari) da memória do Match.
- **Melhor match:** a unidade de menor `mensal(l) = parcelaFin + parcelaPS` (empate: menor `crTotal`, depois `codigo`). Fica fixa no cartão de destaque; a ordenação escolhida vale só para "Outras N unidades".
- **Ordenações:** `parcela` (mensal crescente), `cr` (`crTotal` crescente), `andar` (`andar` decrescente). Rótulos: "Menor parcela", "% da renda", "Andar alto".
- **Todos os empreendimentos:** lista única (sem agrupar), com o nome do empreendimento no sobretítulo de cada unidade.
- **Pro Soluto zerado:** mostra "Sem Pro Soluto" em vez de "R$ 0,00 × 84" (pendência 2 da memória).
- **Foto do empreendimento:** `assets/img/cards/<slug(sheetName)>@480.webp` (todos os 9 `SIM_EMPS` batem com os arquivos de `assets/img/cards/`).
- **Voltar do navegador:** cada etapa faz `history.pushState({ etapa })`; `popstate` volta a etapa sem perder respostas.
- **"Repetir a última busca":** respostas da última busca em `sessionStorage` (`mt-ultima`), lidas com try/catch; o botão só aparece quando existe uma. Some ao fechar a aba (dado de cliente não fica no aparelho).
- **Desktop (≥ 1024px):** trilha vira coluna fixa de 340px à esquerda, pergunta à direita, dica "Pressione Enter para continuar"; resultado com tabela (botão quadrado de seta na última coluna) e coluna lateral "Como chegamos aqui" + "Mais opções" (só quando `resultado.sugestao` existe). Celular: cabeçalho de app (voltar · título · sair) no lugar do `site-header`.

## Review Focus

1. **Renda que tira o subsídio no meio do caminho** (corretor volta à renda e sobe de R$ 3.500 para R$ 9.000; o teto do subsídio é `RENDA_MAX_SUBSIDIO = 4000`): as perguntas de dependente e subsídio anterior somem do perfil e da trilha e não vão para `Match.buscar` como respostas antigas. Teste na Task 1 (`perguntasPerfil`, `cliente`).
2. **Planilha ainda carregando ou com erro quando o corretor chega na revelação:** o anel fica em "Buscando as unidades…" até `SimUnidades` responder; no erro, mensagem e botão "Tentar novamente" sem perder respostas. Verificação na Task 4.
3. **Zero unidades na política escolhida:** revelação mostra "Nenhuma unidade cabe na política X" e, se houver, o botão "Ver na política Y (N)" que refaz a busca sem voltar às perguntas. Verificação na Task 4; `textoContagem` testado na Task 1.
4. **Data digitada errada** ("31/02/1990", ano com 2 dígitos, data futura, cliente acima de 70 anos e 6 meses): mensagem na própria etapa, sem avançar. Teste na Task 1 (`validarEtapa('nascimento')`).
5. **Renda digitada com centavos/pontos** ("3.500,00", "R$ 3500"): campo formata como moeda e a trilha mostra "R$ 3.500/mês". Teste na Task 1 (`resumoEtapa('renda')`).

---

## File Structure

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `assets/match-fluxo.js` | Criar | Regras puras do fluxo: etapas, validação, trilha, perfil condicional, ordenação, melhor match, foto. |
| `tests/match-fluxo.test.js` | Criar | Testes do módulo acima. |
| `match-unidades.html` | Reescrever | Esqueleto das 4 telas (abertura, perguntas, revelação, resultado) + `<template>`s das etapas. |
| `assets/match.css` | Reescrever | Padrão visual 2.0 da página (tokens, componentes, animações, layout celular/desktop). |
| `assets/match-app.js` | Reescrever | Controlador: estado, trilha, navegação, busca, revelação, resultado, PDF (a função `gerarPdf` atual é mantida). |
| `assets/img/icones-3d/*.svg` | Já criado | 12 ícones 3D. |
| `docs/design/match-unidades-nova-ux/` | Já criado | Referência visual. |
| `DESIGN.md` | Modificar | Seção curta "Padrão visual 2.0" apontando para `docs/design/match-unidades-nova-ux/README.md`. |

---

### Task 1: Regras do fluxo (`assets/match-fluxo.js`)

**Files:**
- Create: `assets/match-fluxo.js`
- Test: `tests/match-fluxo.test.js`

**Interfaces:**
- Consumes: `Match.temSubsidio(renda, possuiImovel)`, `Match.atoDe(empId)`, `Match.validarCliente(cliente, cidade, hoje)`, `Match.numero(str)` de `assets/match.js`.
- Produces (todos em `MatchFluxo`):
  - `ETAPAS: ['onde','renda','ato','nascimento','perfil','politica']`
  - `Respostas` = `{ cidade: string, empId: string ('' = todos), renda: number, ato: number|null, dia: string, mes: string, ano: string, fgts: bool, possuiImovel: bool, fatorSocial: bool, subsidioAnterior: bool, politicaId: string }`
  - `respostasIniciais(cidade: string) -> Respostas` (padrões da seção Decisões, `renda: 0`, data vazia)
  - `dataNascimento(dia, mes, ano: string) -> Date|null`
  - `perguntasPerfil(r: Respostas) -> string[]` (chaves de `Respostas`)
  - `cliente(r: Respostas) -> object` no formato que `Match.buscar` espera (`renda, ato, nascimento, fgts, possuiImovel, fatorSocial, subsidioAnterior`); perguntas que não se aplicam saem como `fatorSocial: false, subsidioAnterior: false`
  - `validarEtapa(etapa: string, r: Respostas, hoje: Date) -> string|null`
  - `resumoEtapa(etapa: string, r: Respostas, ctx: { emps: SIM_EMPS[], nomePolitica: fn(id)->string, hoje: Date }) -> string`
  - `textoAtoPadrao(empId: string) -> string`
  - `mensal(l: Linha) -> number`
  - `melhorMatch(linhas: Linha[]) -> Linha|null`
  - `ordenar(linhas: Linha[], criterio: 'parcela'|'cr'|'andar') -> Linha[]` (cópia, não muda a entrada)
  - `achatar(resultado) -> Linha[]` (junta `resultado.grupos[].linhas`)
  - `textoPS(l: Linha) -> string`
  - `textoContagem(total: number) -> string`
  - `fotoDe(emp) -> string`

- [ ] **Step 1: Escrever os testes que falham** em `tests/match-fluxo.test.js` (mesmo cabeçalho de `tests/match.test.js`, `HOJE = new Date(2026, 9, 30)`):

```js
test('dataNascimento aceita data real e recusa inexistente/futura/ano curto', () => {
  assert.equal(F.dataNascimento('14', '03', '1993').getTime(), new Date(1993, 2, 14).getTime());
  assert.equal(F.dataNascimento('31', '02', '1990'), null);
  assert.equal(F.dataNascimento('14', '03', '93'), null);
  assert.equal(F.dataNascimento('', '03', '1993'), null);
});
test('validarEtapa nascimento', () => {
  const r = Object.assign(F.respostasIniciais('Ribeirão Preto'), { renda: 4200 });
  assert.match(F.validarEtapa('nascimento', Object.assign({}, r, { dia: '31', mes: '02', ano: '1990' }), HOJE), /data de nascimento/i);
  assert.match(F.validarEtapa('nascimento', Object.assign({}, r, { dia: '01', mes: '01', ano: '2027' }), HOJE), /futuro/i);
  assert.match(F.validarEtapa('nascimento', Object.assign({}, r, { dia: '01', mes: '01', ano: '1950' }), HOJE), /70 anos/);
  assert.equal(F.validarEtapa('nascimento', Object.assign({}, r, { dia: '14', mes: '03', ano: '1993' }), HOJE), null);
});
test('validarEtapa renda e onde', () => {
  const r = F.respostasIniciais('Ribeirão Preto');
  assert.equal(F.validarEtapa('renda', r, HOJE), 'Informe a renda bruta do cliente.');
  assert.equal(F.validarEtapa('renda', Object.assign({}, r, { renda: 4200 }), HOJE), null);
  assert.equal(F.validarEtapa('onde', Object.assign({}, r, { cidade: '' }), HOJE), 'Escolha a cidade.');
});
test('perguntasPerfil esconde dependente e subsidio quando nao ha subsidio', () => {
  const r = Object.assign(F.respostasIniciais('Ribeirão Preto'), { renda: 3500 });   /* teto do subsidio: R$ 4.000 */
  assert.deepEqual(F.perguntasPerfil(r), ['fgts', 'possuiImovel', 'fatorSocial', 'subsidioAnterior']);
  assert.deepEqual(F.perguntasPerfil(Object.assign({}, r, { renda: 9000 })), ['fgts', 'possuiImovel']);
  assert.deepEqual(F.perguntasPerfil(Object.assign({}, r, { possuiImovel: true })), ['fgts', 'possuiImovel']);
});
test('cliente zera respostas que nao se aplicam', () => {
  const r = Object.assign(F.respostasIniciais('Ribeirão Preto'), { renda: 9000, fatorSocial: true, subsidioAnterior: true, dia: '14', mes: '03', ano: '1993' });
  const c = F.cliente(r);
  assert.equal(c.fatorSocial, false); assert.equal(c.subsidioAnterior, false);
  assert.equal(c.nascimento.getTime(), new Date(1993, 2, 14).getTime());
});
test('resumoEtapa monta a linha da trilha', () => {
  const ctx = { emps: [{ id: 'park', nome: 'Village Park', cidade: 'Ribeirão Preto' }], nomePolitica: () => 'Ouro', hoje: HOJE };
  const r = Object.assign(F.respostasIniciais('Ribeirão Preto'), { empId: 'park', renda: 3500, dia: '14', mes: '03', ano: '1993' });
  assert.equal(F.resumoEtapa('onde', r, ctx), 'Village Park');
  assert.equal(F.resumoEtapa('onde', Object.assign({}, r, { empId: '' }), ctx), 'Ribeirão Preto · todos');
  assert.equal(F.resumoEtapa('renda', r, ctx), 'R$ 3.500/mês');
  assert.equal(F.resumoEtapa('ato', r, ctx), 'Padrão · R$ 2.500');
  assert.equal(F.resumoEtapa('ato', Object.assign({}, r, { ato: 5000 }), ctx), 'R$ 5.000');
  assert.equal(F.resumoEtapa('nascimento', r, ctx), '14/03/1993 · 33 anos');
  assert.equal(F.resumoEtapa('perfil', r, ctx), 'FGTS 3 anos · Sem imóvel · Sem dependente');
  assert.equal(F.resumoEtapa('politica', r, ctx), 'Ouro');
});
test('textoAtoPadrao', () => {
  assert.equal(F.textoAtoPadrao('ipiranga'), 'R$ 1.500');
  assert.equal(F.textoAtoPadrao('park'), 'R$ 2.500');
  assert.equal(F.textoAtoPadrao(''), 'o padrão de cada empreendimento');
});
test('melhorMatch e ordenar', () => {
  const L = [
    { codigo: 'B', parcelaFin: 1200, parcelaPS: 500, crTotal: 0.30, andar: 2 },
    { codigo: 'A', parcelaFin: 1180, parcelaPS: 412, crTotal: 0.28, andar: 3 },
    { codigo: 'C', parcelaFin: 1100, parcelaPS: 600, crTotal: 0.29, andar: 10 }
  ];
  assert.equal(F.mensal(L[1]), 1592);
  assert.equal(F.melhorMatch(L).codigo, 'A');
  assert.equal(F.melhorMatch([]), null);
  assert.deepEqual(F.ordenar(L, 'parcela').map((l) => l.codigo), ['A', 'C', 'B']);
  assert.deepEqual(F.ordenar(L, 'cr').map((l) => l.codigo), ['A', 'C', 'B']);
  assert.deepEqual(F.ordenar(L, 'andar').map((l) => l.codigo), ['C', 'A', 'B']);
  assert.equal(L[0].codigo, 'B');
});
test('textoPS, textoContagem e fotoDe', () => {
  assert.equal(F.textoPS({ parcelaPS: 0, prazoPS: 84 }), 'Sem Pro Soluto');
  assert.equal(F.textoPS({ parcelaPS: 412, prazoPS: 84 }), 'R$ 412 × 84');
  assert.equal(F.textoContagem(1), '1 unidade cabe');
  assert.equal(F.textoContagem(9), '9 unidades cabem');
  assert.equal(F.fotoDe({ sheetName: 'Reserva Direcional Jardim Botânico' }), 'assets/img/cards/reserva-direcional-jardim-botanico@480.webp');
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/match-fluxo.test.js`
Expected: FAIL com `Cannot find module '../assets/match-fluxo.js'`

- [ ] **Step 3: Implementar `assets/match-fluxo.js`** com a interface acima.
  - `validarEtapa`: `onde` → 'Escolha a cidade.' sem cidade; `renda` → 'Informe a renda bruta do cliente.' quando `!(renda > 0)`; `ato` → 'Informe um ato válido ou use o padrão.' quando `ato !== null && !(ato >= 0)`; `nascimento` → 'Confira a data de nascimento.' quando `dataNascimento` dá `null`, 'A data de nascimento está no futuro.' quando > `hoje`, senão devolve `Match.validarCliente(cliente(r), r.cidade, hoje)` só se a mensagem casar `/70 anos|Fora das regras/` (as outras mensagens dizem respeito a etapas seguintes); `perfil` e `politica` → `null`.
  - Valores em moeda sem centavos quando inteiros: `'R$ ' + n.toLocaleString('pt-BR')`.
  - Idade com a mesma regra de `Match` (aniversário ainda não feito no ano desconta 1).
  - `fotoDe`: slug = minúsculas, sem acento (`normalize('NFD').replace(/[̀-ͯ]/g, '')`), não alfanuméricos viram `-`.
  - Perfil na trilha: `FGTS 3 anos`/`Sem FGTS`, `Tem imóvel`/`Sem imóvel`, e, só quando a pergunta se aplica, `Com dependente`/`Sem dependente` e `Já teve subsídio` (este só quando verdadeiro).

- [ ] **Step 4: Rodar tudo e ver passar**

Run: `node --test tests/*.test.js`
Expected: todos PASS (os 3 arquivos antigos do Match continuam verdes).

- [ ] **Step 5: Commit**

```bash
git add assets/match-fluxo.js tests/match-fluxo.test.js
git commit -m "feat(match): regras do fluxo em linha do tempo"
```

---

### Task 2: Página e Padrão visual 2.0 (HTML + CSS, sem lógica)

**Files:**
- Rewrite: `match-unidades.html`
- Rewrite: `assets/match.css`

**Interfaces:**
- Produces (ids e classes que a Task 3 e 4 usam):
  - Telas: `#mt-abertura`, `#mt-perguntas`, `#mt-revelacao`, `#mt-resultado` (só uma sem `hidden` por vez); raiz `<main class="mt-app" id="conteudo">`.
  - Perguntas: `#mt-trilha` (lista `<ol>` das etapas), `#mt-etapa` (onde entra o `<template>` da etapa atual), `#mt-erro` (`role="alert"`), `#mt-continuar`, `#mt-voltar`, `#mt-sair`, `#mt-passo` ("Passo N de 6"), `#mt-progresso` (barra).
  - Templates: `<template id="tpl-onde|tpl-renda|tpl-ato|tpl-nascimento|tpl-perfil|tpl-politica">`, cada um com cabeçalho (sobretítulo, `<h2 tabindex="-1">`, ícone `<img class="mt-ic3d" src="assets/img/icones-3d/<nome>.svg" alt="">`) e os campos com `data-campo="<chave de Respostas>"`.
  - Revelação: `#mt-anel` (svg com `.mt-anel-prog`), `#mt-contagem`, `#mt-rev-titulo`, `#mt-rev-sub`, `#mt-rev-resumo`, `#mt-rev-acao`.
  - Resultado: `#mt-res-titulo`, `#mt-res-sub`, `#mt-chips`, `#mt-ordem`, `#mt-destaque`, `#mt-outras`, `#mt-mais`, `#mt-lateral`, `#mt-pdf`, `#mt-pdf-qtd`, `#mt-editar`.
  - Componentes CSS: `.btn-pri`, `.btn-sec`, `.opt`/`.opt-on`, `.radio`, `.pill`/`.pill-on`, `.tile`/`.tile-on`, `.sw`/`.sw-on`, `.field`, `.pol`/`.pol-on`, `.seg`/`.seg-on`, `.row`, `.chip`, `.go`, `.enter`, `.d1`–`.d4`, `.float`, `.pop`, `.now`.

- [ ] **Step 1: Reescrever `match-unidades.html`**: mantém `<head>` (acrescentar peso 600 e 800 à URL do DM Sans), `skip-link`, `site-header` e os `<script>` atuais na mesma ordem, inserindo `assets/match-fluxo.js` entre `match.js` e `match-app.js`. Estrutura e textos das 4 telas copiados de `fonte/Main.dc.html` (celular) e `fonte/Desktop-*.dc.html` (desktop), trocando `{{…}}` por elementos vazios com os ids acima. Sem badge "Planilha ao vivo". Rodapé de estimativa: texto atual de `.mt-aviso`.

- [ ] **Step 2: Reescrever `assets/match.css`** a partir do `<helmet><style>` de `fonte/Main.dc.html` e `fonte/Desktop-*.dc.html`: tokens em `:root` (`--dir-red`, `--ink`, `--grafite: #2B3033`, `--texto-2: #5C6467`, `--ouro: #F5AE1E`, `--fundo: #F5F6F7`), reset `:where(.mt-app) button/input`, componentes, keyframes, e o bloco `@media (prefers-reduced-motion: reduce)`. Layout:
  - `< 1024px`: `site-header` escondido nas telas de pergunta/revelação/resultado (classe `mt-em-fluxo` no `<body>`); cabeçalho de app visível; botão principal fixo no rodapé com `padding-bottom: max(30px, env(safe-area-inset-bottom))`.
  - `≥ 1024px`: `#mt-perguntas` vira grade `340px 1fr` com `max-width: 1280px`; cabeçalho de app escondido; `.row` do resultado vira linha de tabela (grade de `fonte/Desktop-Resultado.dc.html`: `36px minmax(180px,1.7fr) repeat(4,minmax(92px,1fr)) minmax(104px,1fr) 40px`) dentro de caixa com `overflow-x: auto` e `min-width: 860px`.

- [ ] **Step 3: Verificar no navegador** (preview `portal-do-corretor`, abrir `/match-unidades.html`, remover `hidden` de cada tela pelo DevTools): em 390×844 e 1440×900 cada tela bate com o quadro correspondente do canvas; nenhum texto passa da borda; botão principal vermelho com texto branco; console sem erros (o JS antigo ainda referencia ids que sumiram — erros de `match-app.js` são esperados até a Task 3, nenhum outro).

- [ ] **Step 4: Commit**

```bash
git add match-unidades.html assets/match.css
git commit -m "feat(match): pagina e padrao visual 2.0 da nova UX"
```

---

### Task 3: Controlador das perguntas (trilha, etapas, navegação)

**Files:**
- Rewrite: `assets/match-app.js` (mantendo `esc`, `brl`, `hoje`, `estoque`, `status`-equivalente e `gerarPdf` da versão atual)

**Interfaces:**
- Consumes: tudo de `MatchFluxo` (Task 1); ids/templates/classes da Task 2; `window.SIM_EMPS`, `window.MatchProSoluto.politicaPorId`, `window.Match.ORDEM_POLITICAS`.
- Produces (internas, usadas pela Task 4): `var estado = { tela: 'abertura'|'perguntas'|'revelacao'|'resultado', etapa: 0..5, r: Respostas, resultado: null|object, ordem: 'parcela', aberta: '', marcadas: {} }`; `function irPara(tela, etapa, empilhar)`; `function buscar(politicaId)` (stub nesta task: só `irPara('revelacao')`).

- [ ] **Step 1: Estado e navegação.** `irPara` troca a tela visível, atualiza `#mt-passo`, `#mt-progresso` (`(etapa) / 6`), a classe `mt-em-fluxo` do `<body>`, desenha a trilha e a etapa, faz `history.pushState({ tela, etapa })` quando `empilhar`, e põe o foco no `<h2>` da etapa. `popstate` chama `irPara` sem empilhar. "Sair" volta à abertura mantendo as respostas.

- [ ] **Step 2: Trilha.** Para cada etapa já respondida: `<li><button>` com bolinha de check, rótulo, `MatchFluxo.resumoEtapa(...)` e lápis; clicar leva à etapa. Etapa atual com `.now`; próximas em cinza, terminando em "Resultado". Rótulos: Onde, Renda bruta, Ato, Nascimento, Perfil do cliente, Política.

- [ ] **Step 3: Etapas.** Clona o `<template>` da etapa e liga os campos a `estado.r`:
  - `onde`: pílulas das cidades de `SIM_EMPS` (ordem de primeira aparição) + cartões "Todos os empreendimentos" (ícone `pino`) e um por empreendimento com `MatchFluxo.fotoDe(emp)` (`onerror` troca por `predio.svg`).
  - `renda` / `ato`: campo grande `inputmode="decimal"`, formata com `Match.numero` + `toLocaleString('pt-BR')` ao digitar; no ato, opções "Ato padrão do empreendimento" (subtexto `MatchFluxo.textoAtoPadrao(empId)`) e "Outro valor" (mostra o campo).
  - `nascimento`: três campos (`maxlength` 2/2/4, `inputmode="numeric"`), pula para o próximo ao completar; mostra "N anos" quando a data é válida.
  - `perfil`: um `.tile` por item de `MatchFluxo.perguntasPerfil(r)` (ícones `maleta`, `chave`, `pessoas`, `presente`; títulos "3 anos de FGTS", "Possui imóvel na cidade", "Mais de um comprador ou dependente", "Já recebeu subsídio FGTS/União"); redesenha ao alternar; aviso âmbar quando `fatorSocial` está visível e falso.
  - `politica`: carrossel com `assets/img/ranking/<id>.png` na ordem `Match.ORDEM_POLITICAS`, `aria-label="Política <nome>"`.

- [ ] **Step 4: Continuar.** `#mt-continuar` (e Enter fora de botões) roda `MatchFluxo.validarEtapa`; com erro, mostra em `#mt-erro` e foca o campo; sem erro, vai à próxima etapa. Na `politica` o botão diz "Encontrar unidades" e chama `buscar()`. "Voltar" na primeira etapa leva à abertura.

- [ ] **Step 5: Verificar no navegador** em 390×844 e 1440×900: percorrer as 6 etapas só com teclado (Tab/Enter) e só com clique; voltar pela trilha e pelo botão Voltar do navegador sem perder respostas; renda 9000 some com dependente/subsídio da tela e da trilha; data 31/02/1990 bloqueia com mensagem; console sem erros.

- [ ] **Step 6: Commit**

```bash
git add assets/match-app.js
git commit -m "feat(match): perguntas em linha do tempo"
```

---

### Task 4: Revelação, resultado e PDF

**Files:**
- Modify: `assets/match-app.js`

**Interfaces:**
- Consumes: `estado`, `irPara` (Task 3); `Match.buscar`, `Match.resumoCliente`, `Match.seloFaixa`, `Match.urlAssociativo`, `Match.linhaPdf`; `MatchFluxo.cliente`, `achatar`, `melhorMatch`, `ordenar`, `mensal`, `textoPS`, `textoContagem`; `SimUnidades.estado/aoMudar/carregar/erro/porEmpreendimento`.

- [ ] **Step 1: `buscar(politicaId)`.** Vai para a revelação com o anel girando e "Buscando as unidades…". Quando `SimUnidades.estado() === 'ok'` (agora ou via `aoMudar`), roda `Match.buscar({ cliente: MatchFluxo.cliente(r), cidade, empId, politicaId, hoje, estoque })`, guarda em `estado.resultado`, grava `r` em `sessionStorage['mt-ultima']` (try/catch) e anima: anel até o fim (1,7s), contagem de 0 até `total` com `requestAnimationFrame` (direto ao número com reduced-motion), título `'O cliente cabe em ' + total + (total === 1 ? ' unidade' : ' unidades')`, subtítulo `<empreendimento ou cidade> · Política <nome>`, resumo em cascata (Enquadramento, Subsídio estimado, Financiamento até, de `Match.resumoCliente`). Botão "Ver as N unidades". Erro da planilha: mensagem de `SimUnidades.erro()` + "Tentar novamente".

- [ ] **Step 2: Zero unidades.** Título "Nenhuma unidade cabe na política <nome>"; com `resultado.sugestao`, botão primário "Ver na política <nome> (<qtd>)" que chama `buscar(sugestao.politicaId)` e atualiza `r.politicaId`; sem sugestão, texto "Nenhuma política aprova as unidades desse recorte." e botão "Editar perfil".

- [ ] **Step 3: Resultado.** Cabeçalho `MatchFluxo.textoContagem(total)`, subtítulo com empreendimento/cidade · política · renda. Chips do resumo (Enquadramento, Subsídio, Financ. até, Juros CAIXA `x,x% a.a.`, Prazo `N meses`). Cartão destaque com `melhorMatch`: foto `fotoDe`, selo "Melhor match", sobretítulo `<empreendimento> · Torre N`, código, `andarº andar · final F · tipo · área m²`, "Por mês · CAIXA + Pro Soluto" = `brl(mensal)`, barra e `%` de `crTotal`, grade (Valor, Financiamento, Subsídio, Ato, Pro Soluto via `textoPS`, Parcela CAIXA), selos de `travaF3` e `Match.seloFaixa`, "Abrir no associativo" (`Match.urlAssociativo`) e "PDF". Lista "Outras N unidades" com `MatchFluxo.ordenar` pela ordem escolhida (`#mt-ordem`), linhas expansíveis no celular e tabela no desktop. Barra fixa "No PDF · N unidades" + "Gerar PDF" (desabilitado com 0). Cor do `%`: verde `#1E8E4A` até 30%, âmbar `#B57200` acima. Lateral desktop: "Como chegamos aqui" com `descartadas` (oculta itens zerados) e "Mais opções" só com sugestão. "Editar" volta à etapa Perfil.

- [ ] **Step 4: PDF.** Mantém `gerarPdf` atual lendo `estado.marcadas` (chave `empId|codigo`); antes de `doc.autoTable`, se a função não existir, `alert('A biblioteca de PDF ainda está carregando. Tente de novo em alguns segundos.')` e sai (pendência 4 da memória).

- [ ] **Step 5: Verificar no navegador** com a planilha real, 390×844 e 1440×900: Village Park, renda 4.200, nascimento 14/03/1993, Aço → revelação conta até o total e bate com a lista; trocar ordenação reordena só "Outras"; marcar 2 unidades e gerar PDF baixa arquivo com as 2; um perfil que não feche nenhuma unidade no Aço (baixar a renda até zerar) → caminho de zero unidades com sugestão; "Abrir no associativo" abre o simulador preenchido; com DevTools offline antes de buscar → mensagem de erro e "Tentar novamente"; emular `prefers-reduced-motion` → tudo aparece sem animação; console sem erros. Screenshot das duas larguras para o PR.

- [ ] **Step 6: Rodar testes e commit**

Run: `node --test tests/*.test.js` → todos PASS.

```bash
git add assets/match-app.js
git commit -m "feat(match): revelacao animada, melhor match e lista ordenavel"
```

---

### Task 5: Abertura, "repetir última busca" e documentação

**Files:**
- Modify: `assets/match-app.js`
- Modify: `DESIGN.md`

- [ ] **Step 1: Abertura.** Ícone `casa` grande flutuando com `pino`, `moedas`, `medalha`, `pessoas` em volta (posições de `fonte/Main.dc.html`), textos do canvas, "Começar" → etapa `onde`. "Repetir a última busca" só aparece quando `sessionStorage['mt-ultima']` tem respostas válidas; ao clicar, carrega e vai direto para a etapa `politica` (corretor confere e busca).

- [ ] **Step 2: `DESIGN.md`.** Acrescentar seção "Padrão visual 2.0 (em adoção)" com 4–6 linhas: o que muda (ícones 3D, raios maiores, DM Sans 800, movimento) e link para `docs/design/match-unidades-nova-ux/README.md`.

- [ ] **Step 3: Verificar no navegador:** abrir a página nova numa aba → sem botão "Repetir"; fazer uma busca, recarregar → botão aparece e leva à Política com a trilha completa.

- [ ] **Step 4: Commit**

```bash
git add assets/match-app.js DESIGN.md docs/design/match-unidades-nova-ux assets/img/icones-3d
git commit -m "feat(match): abertura, repetir ultima busca e referencia do padrao 2.0"
```

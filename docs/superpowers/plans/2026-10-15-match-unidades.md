# Match de Unidades Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Nova ferramenta `match-unidades.html` que, a partir de renda, nascimento e FGTS do cliente, estima financiamento CAIXA, subsídio e Pro Soluto para cada unidade disponível e lista só as que o cliente consegue fechar na política escolhida.

**Architecture:** Três módulos de funções puras (motor CAIXA, cópia do Pro Soluto do associativo, regras do Match) testados com `node --test`, mais um módulo de tela que usa `SimUnidades` (estoque ao vivo) e jsPDF. O associativo ganha apenas leitura de parâmetros de URL. A cópia do Pro Soluto é conferida contra o código original do associativo por um teste golden master que executa o `<script>` do HTML num sandbox `vm`.

**Tech Stack:** HTML + CSS + JS puro (ES5, sem build), `node:test` + `node:assert/strict` (Node 22), jsPDF 2.5.1 + jspdf-autotable 3.8.2 via cdnjs, servidor estático `python3 -m http.server` para verificação.

**Spec:** `docs/superpowers/specs/2026-10-15-match-unidades-design.md` (regras da CAIXA em `docs/matriz-caixa/regras-motor-caixa.md`).

## Global Constraints

- Site 100% estático: HTML + CSS + JS puro, sem build, sem framework, sem bundler, sem dependências npm.
- Módulos de regra no padrão de `assets/pendencias.js`: IIFE `(function (raiz) { 'use strict'; ... })(this);` exportando `module.exports` no Node e `raiz.<Nome>` no navegador. ES5 (`var`, `function`), como o resto de `assets/`.
- Identidade Grupo Direcional na página nova: vermelho `#E4032B` (escuro `#B8001F`), DM Sans, tokens de `assets/home.css`. Nada do visual dourado legado.
- Cidades suportadas: Ribeirão Preto (IBGE 3543402), Campinas (3509502), Sorocaba (3552205).
- Ato fixo: **R$ 1.500 no `ipiranga`, R$ 2.500 nos demais**, data de hoje. Sem sinais, anuais, bônus ou FGTS.
- Valor do imóvel na CAIXA = `avaliacao` da unidade; valor de venda do Pro Soluto = `associativo` da unidade.
- Unidades em "Comitê" ou "Reprovado" nunca aparecem.
- O PDF nunca mostra política, folga de tabela, valor comercial mínimo, C.R., valor de avaliação bancária ou nomes de regra interna.
- Rodapé fixo do PDF: "Simulação aproximada, sujeita à análise de crédito da CAIXA e à aprovação da Direcional."
- Testes rodam com `node --test tests/*.test.js` a partir da raiz do repositório.
- Commits terminam com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Refinamentos da spec (descobertos ao validar o código deste plano)

- **Pro Soluto zerado é aprovado.** Quando financiamento + subsídio + ato cobrem a venda, não há carnê e o item "parcela mínima" não se aplica (`MatchProSoluto.aprovacao`).
- **Pro Soluto pequeno encurta o prazo.** Se em 84 meses a parcela linear fica abaixo da mínima do produto (R$ 150), o Match reduz o prazo até atingir o mínimo, como o associativo orienta ("Reduza o prazo"). `Linha.prazoPS` pode ser menor que 84.
- **Financiamento limitado à venda.** `financiamento = min(capacidade CAIXA, venda − subsídio − ato)`. A parcela CAIXA mostrada continua sendo a da capacidade máxima (conservadora).

## Review Focus

1. **Financiamento + subsídio + ato maiores que o valor de venda** (unidade barata, cliente de renda alta): o saldo do Pro Soluto não pode ficar negativo nem a unidade sumir por "fluxo não fecha". Esperado: financiamento reduzido para `venda − subsídio − ato`, saldo do Pro Soluto = 0, unidade aprovada. Teste na Task 3.
2. **Unidade com avaliação zero, vazia ou acima do teto da faixa da renda** (planilha incompleta): descartar sem quebrar a busca e contar no rodapé. Teste na Task 3.
3. **Cliente no limite de idade** (70a6m exatos x 1 dia a mais) e **renda acima de R$ 13.000**: mensagem clara no formulário em vez de lista vazia ou exceção. Testes nas Tasks 1 e 3.
4. **Village Gaia Torre 1** (entrega diferente por torre): o fluxo do Pro Soluto tem de usar a entrega da torre (2028-10-31), não a do empreendimento. Teste na Task 2.
5. **Renda digitada com vírgula/ponto** ("3.500,00", "3500", "R$ 3.500"): o formulário precisa entender como 3500. Teste na Task 3 (`Match.numero`).

---

## File Structure

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `assets/motor-caixa.js` | Criar | Motor CAIXA (cópia do protótipo validado + mapa cidade → IBGE). |
| `tests/fixtures/caixa/casos-matriz.json`, `casos-extras.txt`, `casos-sac.txt` | Criar (copiar) | 138 respostas reais da CAIXA. |
| `tests/motor-caixa.test.js` | Criar | Regressão do motor. |
| `assets/match-prosoluto.js` | Criar | Cópia pura de `calc()`/`avaliarPolitica()`/`checklistAprovacao()` do associativo. |
| `tests/match-prosoluto.test.js` | Criar | Golden master contra o original + caso de regressão documentado. |
| `assets/match.js` | Criar | Regras do Match: validar cliente, avaliar unidade, buscar, sugerir política, linha do PDF. |
| `tests/match.test.js` | Criar | Regras do Match com estoque fictício. |
| `match-unidades.html` | Criar | Página. |
| `assets/match.css` | Criar | Estilos da página (sobre `assets/home.css`). |
| `assets/match-app.js` | Criar | Formulário, resultado, link para o associativo, PDF. |
| `index.html` | Modificar | Card "Match de Unidades" em Ferramentas + link no cabeçalho. |
| `simulador-associativo.html` | Modificar | Ler parâmetros da URL antes do INIT (nenhuma conta muda). |
| `docs/matriz-caixa/regras-motor-caixa.md` | Modificar | Apontar para `assets/motor-caixa.js` como versão oficial. |

---

### Task 1: Motor CAIXA em `assets/` com testes de regressão

**Files:**
- Create: `assets/motor-caixa.js`
- Create: `tests/fixtures/caixa/casos-matriz.json`, `tests/fixtures/caixa/casos-extras.txt`, `tests/fixtures/caixa/casos-sac.txt`
- Test: `tests/motor-caixa.test.js`

**Interfaces:**
- Consumes: `docs/matriz-caixa/prototipo/motor-caixa.js` (protótipo validado).
- Produces: `MotorCaixa.simular(e)` com `e = { renda:Number, valor:Number, nascimento:Date, municipio:String(IBGE), fgts:Boolean, sistema:'PRICE'|'SAC', hoje:Date, prazo?:Number }` → `{ erro:String }` **ou** `{ produto, faixa, jurosNominal, jurosEfetivo, prazo, valorFinanciamento, subsidio, entrada, taxaAdm, seguradoras:[{codigo,nome,primeira,ultima}] }`; `MotorCaixa.MUNICIPIO_POR_CIDADE = { 'Ribeirão Preto':'3543402', 'Campinas':'3509502', 'Sorocaba':'3552205' }`; `MotorCaixa.CIDADES[ibge].tetoF12`.

- [ ] **Step 1: Copiar fixtures e escrever o teste**

```bash
mkdir -p tests/fixtures/caixa
cp docs/matriz-caixa/prototipo/casos-matriz.json docs/matriz-caixa/prototipo/casos-extras.txt docs/matriz-caixa/prototipo/casos-sac.txt tests/fixtures/caixa/
```

Criar `tests/motor-caixa.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const M = require('../assets/motor-caixa.js');

const FIX = path.join(__dirname, 'fixtures', 'caixa');
const HOJE = new Date(2026, 9, 15);
const dt = (s) => { const [d, m, y] = s.split('/').map(Number); return new Date(y, m - 1, d); };
/* tolerancias medidas contra o simulador oficial (docs/matriz-caixa/regras-motor-caixa.md) */
const TOL = { fin: 3, sub: 1, jn: 0, prazo: 0, p14: 0.05, p15: 0.05, p4: 0.05, u: 0.05 };

function confere(id, e, exp) {
  const r = M.simular(e);
  assert.ok(!r.erro, id + ': ' + r.erro);
  const got = {
    fin: r.valorFinanciamento, sub: r.subsidio, jn: r.jurosNominal, prazo: r.prazo,
    p14: r.seguradoras[0].primeira, p15: r.seguradoras[1].primeira, p4: r.seguradoras[2].primeira,
    u: r.seguradoras[0].ultima
  };
  for (const k of Object.keys(exp)) {
    assert.ok(Math.abs(got[k] - exp[k]) <= TOL[k] + 1e-9, `${id} ${k}: motor ${got[k]} caixa ${exp[k]}`);
  }
}

test('reproduz as 106 simulações da matriz (PRICE, nascimento 26/01/1981, Ribeirão Preto)', () => {
  const rows = JSON.parse(fs.readFileSync(path.join(FIX, 'casos-matriz.json'), 'utf8'));
  assert.equal(rows.length, 106);
  for (const r of rows) {
    confere('matriz ' + r.renda,
      { renda: r.renda, valor: +r.valor_imovel, nascimento: dt('26/01/1981'), municipio: '3543402', fgts: true, hoje: HOJE },
      { fin: +r.valor_financiamento, sub: +r.subsidio, jn: +r.juros_nominal, prazo: 417,
        p14: +r.p1_caixa, p15: +r.p1_mais, p4: +r.p1_tokio, u: +r.pu_caixa });
  }
});

test('reproduz os 26 casos extras (cidades, FGTS, limites de faixa e idade)', () => {
  const linhas = fs.readFileSync(path.join(FIX, 'casos-extras.txt'), 'utf8').trim().split('\n');
  assert.equal(linhas.length, 26);
  for (const l of linhas) {
    const c = l.split(';'); const sg = (s) => s.split('/').map(Number);
    confere('extra ' + l.slice(0, 40),
      { renda: +c[0], valor: +c[1], nascimento: dt(c[2]), municipio: c[4], fgts: c[3] === 'S', hoje: HOJE },
      { fin: +c[6], sub: +c[8], jn: +c[9], prazo: +c[10], p14: sg(c[11])[0], p15: sg(c[12])[0], p4: sg(c[13])[0], u: sg(c[11])[1] });
  }
});

test('reproduz os 6 casos SAC por idade (corte da seguradora 15 aos 61 anos)', () => {
  const linhas = fs.readFileSync(path.join(FIX, 'casos-sac.txt'), 'utf8').trim().split('\n').filter((x) => !x.startsWith('#'));
  assert.equal(linhas.length, 6);
  for (const l of linhas) {
    const c = l.split(';');
    const exp = { fin: +c[4], prazo: +c[6], p14: +c[7], p15: +c[8], p4: +c[9], u: +c[10] };
    if (c[5]) exp.sub = +c[5];
    confere('sac ' + c[2],
      { renda: +c[0], valor: +c[1], nascimento: dt(c[2]), municipio: c[3], fgts: true, sistema: 'SAC', hoje: HOJE }, exp);
  }
});

test('idade-limite: 70a6m exatos simula com 120 meses; 1 dia a mais é recusado', () => {
  const base = { renda: 2500, valor: 200000, municipio: '3543402', fgts: true, sistema: 'SAC', hoje: HOJE };
  assert.equal(M.simular({ ...base, nascimento: dt('15/04/1956') }).prazo, 120);
  assert.match(M.simular({ ...base, nascimento: dt('14/04/1956') }).erro, /70 anos e 6 meses/);
  assert.match(M.simular({ ...base, nascimento: dt('15/02/1956') }).erro, /70 anos e 6 meses/);
});

test('renda acima de R$ 13.000 está fora do enquadramento', () => {
  const r = M.simular({ renda: 13000.01, valor: 500000, nascimento: dt('15/03/1990'), municipio: '3543402', fgts: true, hoje: HOJE });
  assert.match(r.erro, /enquadramento/);
});

test('MUNICIPIO_POR_CIDADE cobre as cidades do catálogo', () => {
  assert.deepEqual(M.MUNICIPIO_POR_CIDADE, { 'Ribeirão Preto': '3543402', Campinas: '3509502', Sorocaba: '3552205' });
  assert.equal(M.CIDADES['3509502'].tetoF12, 270000);
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/motor-caixa.test.js`
Expected: FAIL com `Cannot find module '../assets/motor-caixa.js'`.

- [ ] **Step 3: Criar o módulo a partir do protótipo**

```bash
cp docs/matriz-caixa/prototipo/motor-caixa.js assets/motor-caixa.js
```

Em `assets/motor-caixa.js`:

1. Trocar o comentário do topo (as 3 primeiras linhas) por:

```js
/* ============================================================
   MOTOR CAIXA - financiamento MCMV / Classe Media
   ------------------------------------------------------------
   Funcoes puras (sem DOM, sem rede). Reproduz o Simulador
   Habitacional CAIXA (calibrado em 15/10/2026 com 138 respostas
   reais - tests/motor-caixa.test.js).
   Regras e fontes: docs/matriz-caixa/regras-motor-caixa.md
   Usado por /match-unidades via window.MotorCaixa.
   ============================================================ */
```

2. Logo abaixo de `var FDR_UF = { SP: 2.07 };`, adicionar:

```js
  /* nome da cidade no catalogo (window.SIM_EMPS) -> codigo IBGE */
  var MUNICIPIO_POR_CIDADE = { 'Ribeirão Preto': '3543402', 'Campinas': '3509502', 'Sorocaba': '3552205' };
```

3. Trocar a linha `var api = { ... };` por:

```js
  var api = {
    simular: simular, subsidio: subsidio, enquadrar: enquadrar, prazoMaximo: prazoMaximo,
    CIDADES: CIDADES, MUNICIPIO_POR_CIDADE: MUNICIPIO_POR_CIDADE
  };
```

4. Na primeira linha de `simular`, tratar município desconhecido (hoje dá `TypeError`):

```js
    var cidade = CIDADES[e.municipio];
    if (!cidade) return { erro: 'Cidade sem regras da CAIXA mapeadas' };
```

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test tests/motor-caixa.test.js`
Expected: PASS, 6 testes.

- [ ] **Step 5: Commit**

```bash
git add assets/motor-caixa.js tests/motor-caixa.test.js tests/fixtures/caixa
git commit -m "feat(match): motor CAIXA em assets com 138 casos de regressao

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Cópia pura do Pro Soluto com golden master contra o associativo

**Files:**
- Create: `assets/match-prosoluto.js`
- Test: `tests/match-prosoluto.test.js`

**Interfaces:**
- Consumes: nada de tasks anteriores. O teste lê `simulador-associativo.html` e `assets/simuladores.js`.
- Produces (`window.MatchProSoluto` / `module.exports`):
  - `POLITICAS` (mesma ordem do associativo: diamante, ouro, prata, bronze, aco), `politicaPorId(id)`.
  - `entregaDe(emp, torreN)` → `'AAAA-MM-DD'` (Gaia Torre 1 = `'2028-10-31'`).
  - `sugereVenc1(dataVendaIso)` → `'AAAA-MM-DD'` (mês seguinte, dia 10, igual ao `sugereDatas()` do associativo).
  - `calcular(e)` com `e = { emp:{id,nome,inicioObra,entrega,parcMin}, politica, dataVenda, dataVenc1, dataAto, prazo, valor, financiado, subsidio, ato, renda, parcFin }` (datas ISO) → objeto `c` com os mesmos campos do `calc()` original usados aqui: `pronto, preSaldo, saldoMensais, saldoCorrigido, psCorrigido, pctPS, nPre, nPos, linear:{parcPre,parcPos,parcela,total}, escalonado:{faixas:[{parcela,prazo}],total}, crLinear, crPS, crEscal, veredito:{final,itens:[{id,st}]}`.
  - `checklistAprovacao(c, e)` → `[{ id, grave, ok }]` com os mesmos 11 ids do original, na mesma ordem.
  - `aprovacao(c, e)` → `{ linear:Boolean, escalonado:Boolean }`.

**Decisão de 1º vencimento:** o plano usa a mesma regra do associativo (`sugereDatas()`: mês seguinte, dia 10). É ela que o corretor vai ver ao abrir a unidade no associativo, então os dois números batem. A spec foi ajustada para esta regra.

- [ ] **Step 1: Escrever o teste**

Criar `tests/match-prosoluto.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const P = require('../assets/match-prosoluto.js');

const RAIZ = path.join(__dirname, '..');

/* Executa o motor ORIGINAL do associativo (trecho do <script> entre
   "var EMPS = window.SIM_EMPS;" e o bloco RENDER) num sandbox. */
function carregaOriginal() {
  const ctx = { window: {} };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(RAIZ, 'assets/simuladores.js'), 'utf8'), ctx);
  const html = fs.readFileSync(path.join(RAIZ, 'simulador-associativo.html'), 'utf8');
  const ini = html.indexOf('var EMPS = window.SIM_EMPS;');
  const fim = html.indexOf('/* =========================================================\n   RENDER');
  assert.ok(ini > 0 && fim > ini, 'marcadores do motor do associativo não encontrados');
  vm.runInContext(html.slice(ini, fim) +
    ';this.__api={ set(o){ S=Object.assign(estadoInicial(),o); }, calc:calc, check:checklistAprovacao };', ctx);
  return { api: ctx.__api, emps: ctx.window.SIM_EMPS };
}

const ORIG = carregaOriginal();
const empPorId = (id) => ORIG.emps.find((e) => e.id === id);

function rodaOriginal(o) {
  ORIG.api.set(o);
  const c = ORIG.api.calc();
  return { c, check: ORIG.api.check(c) };
}

function rodaCopia(o) {
  const base = empPorId(o.empId);
  const torre = o.blocoId ? parseInt(o.blocoId.replace(/\D/g, ''), 10) : null;
  const e = {
    emp: { id: base.id, nome: base.nome, inicioObra: base.inicioObra, entrega: P.entregaDe(base, torre), parcMin: base.parcMin },
    politica: P.politicaPorId(o.politicaId),
    dataVenda: o.dataVenda, dataVenc1: o.dataVenc1, dataAto: o.dataAto, prazo: o.prazo,
    valor: o.valor, financiado: o.financiado, subsidio: o.subsidio, ato: o.ato,
    renda: o.renda, parcFin: o.parcFin
  };
  const c = P.calcular(e);
  return { c, check: P.checklistAprovacao(c, e), e };
}

const perto = (a, b, id) => assert.ok(Math.abs(a - b) < 1e-6, `${id}: copia ${a} original ${b}`);

test('golden master: a cópia bate com o calc() original do associativo', () => {
  const casos = [];
  for (const empId of ['gaia', 'park', 'botanico', 'ipiranga', 'alta-vista', 'vila-da-mata'])
    for (const politicaId of ['aco', 'bronze', 'prata', 'ouro', 'diamante'])
      for (const [renda, valor, financiado, subsidio] of [[2500, 210000, 150000, 6799], [5000, 260000, 200000, 0], [9000, 380000, 290000, 0]])
        casos.push({ empId, politicaId, renda, valor, financiado, subsidio, ato: empId === 'ipiranga' ? 1500 : 2500,
          prazo: 84, dataVenda: '2026-10-15', dataVenc1: '2026-11-10', dataAto: '2026-10-15', parcFin: renda * 0.3 });
  casos.push({ empId: 'gaia', blocoId: 'BL01', politicaId: 'aco', renda: 7500, valor: 333190.2, financiado: 304800, subsidio: 0,
    ato: 2500, prazo: 84, dataVenda: '2026-10-15', dataVenc1: '2026-11-10', dataAto: '2026-10-15', parcFin: 2192.35 });

  for (const o of casos) {
    const id = `${o.empId}/${o.blocoId || '-'}/${o.politicaId}/${o.renda}`;
    const a = rodaOriginal(o), b = rodaCopia(o);
    for (const k of ['preSaldo', 'saldoCorrigido', 'psCorrigido', 'pctPS', 'nPre', 'nPos', 'crLinear', 'crPS', 'crEscal'])
      perto(b.c[k], a.c[k], id + ' ' + k);
    perto(b.c.linear.parcela, a.c.linear.parcela, id + ' linear');
    perto(b.c.escalonado.faixas[0].parcela, a.c.escalonado.faixas[0].parcela, id + ' escalonado');
    assert.equal(b.c.veredito.final, a.c.veredito.final, id + ' veredito');
    /* o original vive em outro realm (vm): compara como texto */
    assert.equal(JSON.stringify(b.check.map((x) => x.id + ':' + x.ok)), JSON.stringify(a.check.map((x) => x.id + ':' + x.ok)), id + ' checklist');
  }
});

test('caso de regressão documentado no associativo (Village Gaia, renda 7.500)', () => {
  const e = {
    emp: { id: 'gaia', nome: 'Village Gaia', inicioObra: '2026-05-01', entrega: '2029-09-30', parcMin: 150 },
    politica: P.politicaPorId('aco'), dataVenda: '2026-07-25', dataVenc1: '2026-08-10', dataAto: '2026-07-25',
    prazo: 84, valor: 333190.2, financiado: 304800, subsidio: 0, ato: 2500, renda: 7500, parcFin: 2192.35
  };
  const c = P.calcular(e);
  assert.equal(c.preSaldo.toFixed(2), '25890.20');
  assert.equal(c.psCorrigido.toFixed(2), '26019.65');
  assert.equal((c.pctPS * 100).toFixed(4), '7.8092');
  assert.deepEqual([c.nPre, c.nPos], [37, 47]);
  assert.equal(c.linear.parcela, 422.39);
  assert.deepEqual(c.escalonado.faixas.map((f) => f.parcela.toFixed(4)), ['523.3242', '438.7495', '376.6601', '257.4581']);
  assert.equal((c.crLinear * 100).toFixed(2), '34.86');
  assert.equal((c.crPS * 100).toFixed(2), '5.63');
  assert.equal((c.crEscal * 100).toFixed(2), '35.08');
  assert.deepEqual(P.aprovacao(c, e), { linear: true, escalonado: true });
});

test('entregaDe usa a entrega da torre da Gaia', () => {
  const gaia = empPorId('gaia');
  assert.equal(P.entregaDe(gaia, 1), '2028-10-31');
  assert.equal(P.entregaDe(gaia, 2), gaia.entrega);
  assert.equal(P.entregaDe(empPorId('park'), 1), empPorId('park').entrega);
});

test('sugereVenc1 = mês seguinte, dia 10', () => {
  assert.equal(P.sugereVenc1('2026-10-15'), '2026-11-10');
  assert.equal(P.sugereVenc1('2026-12-31'), '2027-01-10');
});

test('aprovacao: escalonado salva quando só o C.R. linear estoura', () => {
  const ok = (id) => ({ id, ok: true });
  const fake = [ok('ps'), ok('prazo'), { id: 'cr', ok: false }, ok('cresc'), ok('venc1'), ok('ato'),
    ok('sinais'), ok('sinaisOrdem'), ok('anuais'), ok('parcmin'), ok('saldo')];
  assert.deepEqual(P.aprovacaoDoChecklist(fake), { linear: false, escalonado: true });
  fake[0] = { id: 'ps', ok: false };
  assert.deepEqual(P.aprovacaoDoChecklist(fake), { linear: false, escalonado: false });
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/match-prosoluto.test.js`
Expected: FAIL com `Cannot find module '../assets/match-prosoluto.js'`.

- [ ] **Step 3: Implementar a cópia**

Criar `assets/match-prosoluto.js`:

```js
/* ============================================================
   MATCH DE UNIDADES - copia do motor do Pro Soluto
   ------------------------------------------------------------
   COPIA de simulador-associativo.html (POLITICAS, TX,
   GAIA_ENTREGA_POR_TORRE, datas/financeiros, calc(),
   avaliarPolitica(), checklistAprovacao()) em funcoes puras.
   ATENCAO: toda mudanca de politica, taxa ou regra precisa ser
   feita NOS DOIS arquivos. tests/match-prosoluto.test.js executa
   o original e compara - se divergir, o teste quebra.
   O Match nao usa FGTS, bonus, sinais nem anuais (sempre zero).
   Spec: docs/superpowers/specs/2026-10-15-match-unidades-design.md
   ============================================================ */
(function (raiz) {
  'use strict';

  var POLITICAS = [
    { id: 'diamante', nome: 'Diamante', pctPS: 0.25, prazo: 84, cr: 0.50, crPS: 0.20 },
    { id: 'ouro',     nome: 'Ouro',     pctPS: 0.20, prazo: 84, cr: 0.50, crPS: 0.20 },
    { id: 'prata',    nome: 'Prata',    pctPS: 0.18, prazo: 84, cr: 0.48, crPS: 0.18 },
    { id: 'bronze',   nome: 'Bronze',   pctPS: 0.15, prazo: 84, cr: 0.45, crPS: 0.15 },
    { id: 'aco',      nome: 'Aço',      pctPS: 0.12, prazo: 84, cr: 0.40, crPS: 0.10 }
  ];

  var TX = {
    jurosPre: 0.005, jurosPos: 0.015,
    jurosPreAntigo: 0.003, jurosPosAntigo: 0.013,
    dataTaxaNova: '2021-03-08',
    dataCarencia: '2020-04-23',
    maxDiasVenc1: 120,
    maxDiasAto: 7,
    diasSinal: [30, 60, 90],
    diasVenc: [5, 10, 15],
    faixas: [0.40, 0.30, 0.20, 0.10],
    tolPS: 0.10,
    tolPrazo: 12, prazoMinComite: 72,
    tolCR: 0.05
  };

  var GAIA_ENTREGA_POR_TORRE = { 1: '2028-10-31' };

  function politicaPorId(id) {
    for (var i = 0; i < POLITICAS.length; i++) if (POLITICAS[i].id === id) return POLITICAS[i];
    return POLITICAS[4];
  }

  function entregaDe(emp, torre) {
    if (emp.id === 'gaia' && torre && GAIA_ENTREGA_POR_TORRE[torre]) return GAIA_ENTREGA_POR_TORRE[torre];
    return emp.entrega;
  }

  /* datas ------------------------------------------------- */
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function parseData(str) {
    if (!str) return null;
    var p = str.split('-'); if (p.length !== 3) return null;
    var d = new Date(+p[0], (+p[1]) - 1, +p[2]);
    return isFinite(d.getTime()) ? d : null;
  }
  function isoData(d) { return d ? (d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate())) : ''; }
  function eom(d) { return new Date(d.getFullYear(), d.getMonth() + 1, 0); }
  function mi(d) { return d.getFullYear() * 12 + d.getMonth(); }
  function addMeses(d, k) {
    var alvo = new Date(d.getFullYear(), d.getMonth() + k, 1);
    var ult = new Date(alvo.getFullYear(), alvo.getMonth() + 1, 0).getDate();
    return new Date(alvo.getFullYear(), alvo.getMonth(), Math.min(d.getDate(), ult));
  }
  function dias(a, b) { return Math.round((b - a) / 86400000); }

  function sugereVenc1(dataVenda) {
    var d = addMeses(parseData(dataVenda), 1);
    return isoData(new Date(d.getFullYear(), d.getMonth(), 10));
  }

  /* financeiros ------------------------------------------- */
  function pmt(i, n, pv) {
    if (!n || !pv) return 0;
    if (!i) return pv / n;
    return pv * i / (1 - Math.pow(1 + i, -n));
  }
  function anuidade(i, n) {
    if (!n) return 0;
    return (Math.pow(1 + i, n) * i) / (Math.pow(1 + i, n) - 1);
  }
  function r2(v) { return Math.round(v * 100) / 100; }
  function r4(v) { return Math.round(v * 10000) / 10000; }

  /* COPIA de calc() - S.* virou e.*; fgts, bonus, sinais e anuais = 0 */
  function calcular(e) {
    var pol = e.politica;
    var venda = parseData(e.dataVenda), venc1 = parseData(e.dataVenc1);
    var prazo = Math.max(0, Math.round(e.prazo) || 0);

    var c = {
      e: e.emp, pol: pol, venda: venda, venc1: venc1, prazo: prazo, pronto: false,
      preSaldo: 0, saldoMensais: 0, carencia: 0, saldoCorrigido: 0, psCorrigido: 0, pctPS: 0,
      nPre: 0, nPos: 0, i1: TX.jurosPre, i2: TX.jurosPos,
      linear: null, escalonado: null,
      crLinear: 0, crPS: 0, crEscal: 0, veredito: null,
      somaSinais: 0, somaAnuais: 0
    };
    if (!e.emp || !venda || !venc1 || prazo <= 0 || e.valor <= 0) return c;

    c.i1 = venda < parseData(TX.dataTaxaNova) ? TX.jurosPreAntigo : TX.jurosPre;
    c.i2 = venda < parseData(TX.dataTaxaNova) ? TX.jurosPosAntigo : TX.jurosPos;

    var entrega = parseData(e.emp.entrega), inicioObra = parseData(e.emp.inicioObra);

    c.preSaldo = e.valor - (e.financiado + e.subsidio + e.ato);
    c.saldoMensais = c.preSaldo - c.somaSinais - c.somaAnuais;

    c.nPre = Math.max(0, Math.min(prazo, mi(entrega) - mi(venc1)));
    c.nPos = prazo - c.nPre;

    var taxaCar = c.nPre !== 0 ? c.i1 : c.i2;
    c.carencia = venda >= parseData(TX.dataCarencia)
      ? Math.round(dias(eom(venda), eom(venc1)) / 30) : 0;
    if (c.carencia < 0) c.carencia = 0;
    var fatorCar = Math.pow(1 + taxaCar, c.carencia);
    c.correcaoCarencia = c.saldoMensais * fatorCar - c.saldoMensais;
    c.saldoCorrigido = c.saldoMensais * fatorCar;
    c.psCorrigido = c.saldoCorrigido + c.somaAnuais * fatorCar;

    var baseP = e.valor;
    c.pctPS = baseP > 0 ? r4(c.psCorrigido) / baseP : 0;
    c.pronto = true;

    var fPre = c.nPre ? anuidade(c.i1, c.nPre) : 0;
    var fPos = c.nPos ? Math.pow(1 + c.i1, c.nPre) * anuidade(c.i2, c.nPos) : 0;
    var pctPre = (c.nPre && c.nPos) ? 1 - fPre / (fPre + fPos) : (c.nPre ? 1 : 0);
    var saldoPre = c.saldoCorrigido * pctPre;
    var saldoPos = (c.saldoCorrigido - saldoPre) * Math.pow(1 + c.i1, c.nPre);
    var parcPre = r2(pmt(c.i1, c.nPre, saldoPre));
    var parcPos = r2(pmt(c.i2, c.nPos, saldoPos));
    c.linear = {
      parcPre: parcPre, parcPos: parcPos, saldoPre: saldoPre, saldoPos: saldoPos,
      parcela: parcPre || parcPos,
      total: parcPre * c.nPre + parcPos * c.nPos
    };

    var pFaixa = Math.ceil(prazo / 4);
    var prazos = [pFaixa, pFaixa, pFaixa, Math.max(0, prazo - 3 * pFaixa)];
    var accPre = 0, accPos = 0, faixas = [], totalEsc = 0;
    for (var k = 0; k < 4; k++) {
      var P = prazos[k], V = c.saldoCorrigido * TX.faixas[k];
      var bPre = Math.max(0, Math.min(P, c.nPre - accPre));
      var bPos = P - bPre;
      var hPre;
      if (bPre && bPos) {
        var fa = anuidade(c.i1, bPre), fb = Math.pow(1 + c.i1, bPre) * anuidade(c.i2, bPos);
        hPre = 1 - fa / (fa + fb);
      } else { hPre = bPre ? 1 : 0; }
      var vPre = hPre * V, vPos = V - vPre;
      var flPre = vPre * Math.pow(1 + c.i1, accPre) * Math.pow(1 + c.i2, accPos);
      var flPos = vPos * Math.pow(1 + c.i1, accPre + bPre) * Math.pow(1 + c.i2, accPos);
      var parcela = Math.max(bPre ? pmt(c.i1, bPre, flPre) : 0, bPos ? pmt(c.i2, bPos, flPos) : 0);
      faixas.push({ n: k + 1, prazo: P, valor: V, pct: TX.faixas[k], mesesPre: bPre, mesesPos: bPos, parcela: parcela });
      totalEsc += parcela * P;
      accPre += bPre; accPos += bPos;
    }
    c.escalonado = { faixas: faixas, total: totalEsc };

    var nTotObra = Math.max(0, Math.min(mi(entrega), mi(venc1) + prazo) - mi(inicioObra));
    var nDecorr = Math.max(0, Math.min(mi(venc1), mi(entrega)) - mi(inicioObra));
    var evBase = nTotObra > 0 ? nDecorr / nTotObra : 1;
    var evStep = (nTotObra > 0 && c.nPre > 0) ? ((nTotObra - nDecorr) / nTotObra) / c.nPre : 0;

    function parcelaFaixa(nPS) {
      var cum = 0;
      for (var i = 0; i < faixas.length; i++) { cum += faixas[i].prazo; if (nPS <= cum) return faixas[i].parcela; }
      return faixas[faixas.length - 1].parcela;
    }

    var ev = evBase, nPS = 0, mes = 0, tipoAnt = 'Ato Sinal CC/Boleto', guarda = 0;
    while (nPS < prazo && guarda < 400) {
      guarda++;
      var d = addMeses(venc1, mes); mes++;
      var pre = mi(d) < mi(entrega);
      var tipo = 'Mensal P.S';
      nPS++;
      var juros;
      if (pre) {
        if (tipo !== tipoAnt) ev = evBase; else ev += evStep;
        juros = e.parcFin * ev;
      } else {
        juros = e.parcFin;
      }
      tipoAnt = tipo;

      var psLin = pre ? parcPre : parcPos;
      var psEsc = parcelaFaixa(nPS);
      var crLin = e.renda > 0 ? r4((juros + psLin) / e.renda) : 0;
      var crEsc = e.renda > 0 ? r4((juros + psEsc) / e.renda) : 0;
      var crPSm = e.renda > 0 ? r4(psLin / e.renda) : 0;
      if (crLin > c.crLinear) c.crLinear = crLin;
      if (crEsc > c.crEscal) c.crEscal = crEsc;
      if (crPSm > c.crPS) c.crPS = crPSm;
    }

    c.veredito = avaliarPolitica(c);
    return c;
  }

  /* COPIA de status() / avaliarPolitica() - sem os textos de exibicao */
  function status(valor, limite, limiteComite) {
    if (valor <= limite + 1e-9) return 'Aprovado';
    if (valor <= limiteComite + 1e-9) return 'Comitê';
    return 'Reprovado';
  }
  function avaliarPolitica(c) {
    var pol = c.pol;
    var limPS = pol.pctPS, comitePS = Math.round((limPS + limPS * TX.tolPS) * 100) / 100;
    var limPz = pol.prazo, comitePz = Math.max(TX.prazoMinComite, limPz + TX.tolPrazo);
    var limCR = pol.cr, comiteCR = limCR + TX.tolCR;
    var limCRPS = pol.crPS;

    var stPS = status(c.pctPS, limPS, comitePS);
    var stPz = status(c.prazo, limPz, comitePz);
    var stCR;
    if (c.crLinear <= limCR + 1e-9 && c.crPS <= limCRPS + 1e-9) stCR = 'Aprovado';
    else if (c.crLinear <= comiteCR + 1e-9 && c.crPS <= limCRPS + 1e-9) stCR = 'Comitê';
    else stCR = 'Reprovado';
    var stEsc = status(c.crEscal, limCR, comiteCR);

    var itens = [{ id: 'ps', st: stPS }, { id: 'pz', st: stPz }, { id: 'cr', st: stCR }, { id: 'cres', st: stEsc }];
    var chave = [stPS, stPz, stCR];
    var final = chave.every(function (s) { return s === 'Aprovado'; }) ? 'Aprovado'
              : (chave.some(function (s) { return s === 'Reprovado'; }) ? 'Reprovado' : 'Comitê');
    return { itens: itens, final: final };
  }

  /* COPIA de checklistAprovacao() - mesmos ids e ordem, sem textos.
     Sinais e anuais nao existem no Match: os itens deles ficam ok. */
  function checklistAprovacao(c, e) {
    var v = c.veredito.itens;
    var dAto = parseData(e.dataAto);
    return [
      { id: 'ps', grave: true, ok: v[0].st === 'Aprovado' },
      { id: 'prazo', grave: true, ok: v[1].st === 'Aprovado' },
      { id: 'cr', grave: true, ok: v[2].st === 'Aprovado' },
      { id: 'cresc', grave: false, ok: v[3].st === 'Aprovado' },
      { id: 'venc1', grave: true, ok: TX.diasVenc.indexOf(c.venc1.getDate()) >= 0 &&
          dias(c.venda, c.venc1) >= 0 && dias(c.venda, c.venc1) <= TX.maxDiasVenc1 },
      { id: 'ato', grave: true, ok: e.ato <= 0 || !dAto || dias(c.venda, dAto) <= TX.maxDiasAto },
      { id: 'sinais', grave: true, ok: true },
      { id: 'sinaisOrdem', grave: true, ok: true },
      { id: 'anuais', grave: false, ok: true },
      { id: 'parcmin', grave: false, ok: !c.linear || c.linear.parcela >= c.e.parcMin },
      { id: 'saldo', grave: true, ok: c.preSaldo >= -0.01 && c.saldoMensais >= -0.01 }
    ];
  }

  /* Regra do Match (spec 4.3): o carne passa se todos os itens dele
     estao ok. Linear usa 'cr'; escalonado usa 'cresc'. */
  var COMUNS = ['ps', 'prazo', 'venc1', 'ato', 'sinais', 'sinaisOrdem', 'anuais', 'parcmin', 'saldo'];
  function aprovacaoDoChecklist(lista) {
    var ok = {};
    lista.forEach(function (x) { ok[x.id] = x.ok; });
    var comuns = COMUNS.every(function (id) { return ok[id]; });
    return { linear: comuns && ok.cr, escalonado: comuns && ok.cresc };
  }
  /* Pro Soluto zerado (banco + subsidio + ato cobrem a venda): nao ha
     carne, entao a parcela minima nao se aplica. */
  function aprovacao(c, e) {
    var lista = checklistAprovacao(c, e);
    if (c.pronto && c.saldoCorrigido <= 0.01) {
      lista = lista.map(function (x) { return x.id === 'parcmin' ? { id: x.id, grave: x.grave, ok: true } : x; });
    }
    return aprovacaoDoChecklist(lista);
  }

  var api = {
    POLITICAS: POLITICAS, TX: TX, politicaPorId: politicaPorId, entregaDe: entregaDe,
    sugereVenc1: sugereVenc1, calcular: calcular, checklistAprovacao: checklistAprovacao,
    aprovacao: aprovacao, aprovacaoDoChecklist: aprovacaoDoChecklist
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.MatchProSoluto = api;
})(this);
```

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test tests/match-prosoluto.test.js`
Expected: PASS, 5 testes. Se o golden master falhar, a diferença está na cópia: compare a função apontada com o trecho correspondente do `simulador-associativo.html` (linhas ~1156-1569) e corrija a cópia, nunca o original.

- [ ] **Step 5: Commit**

```bash
git add assets/match-prosoluto.js tests/match-prosoluto.test.js
git commit -m "feat(match): copia do Pro Soluto com golden master contra o associativo

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Regras do Match (`assets/match.js`)

**Files:**
- Create: `assets/match.js`
- Test: `tests/match.test.js`

**Interfaces:**
- Consumes: `MotorCaixa.simular`, `MotorCaixa.MUNICIPIO_POR_CIDADE`, `MotorCaixa.CIDADES` (Task 1); `MatchProSoluto.calcular`, `.aprovacao`, `.politicaPorId`, `.entregaDe`, `.sugereVenc1`, `.POLITICAS` (Task 2). No Node via `require`; no navegador via `window.MotorCaixa` / `window.MatchProSoluto`.
- Produces (`window.Match` / `module.exports`):
  - `numero(str)` → Number (aceita "3.500,00", "3500", "R$ 3.500").
  - `atoDe(empId)` → 1500 | 2500.
  - `validarCliente(cliente, cidade, hoje)` → `null` ou mensagem. `cliente = { renda:Number, nascimento:Date|null, fgts:Boolean }`, `cidade` = nome do catálogo.
  - `resumoCliente(cliente, cidade, hoje)` → `{ faixa, jurosNominal, prazo, financiamentoMax, subsidio }`.
  - `avaliarUnidade(cliente, emp, unidade, politicaId, hoje)` → `{ status:'ok'|'sem-avaliacao'|'fora-enquadramento'|'politica', linha? }`.
  - `buscar({ cliente, cidade, empId, politicaId, hoje, estoque })` com `estoque = [{ emp, unidades:[Unidade] }]` → `{ grupos:[{ emp, linhas:[Linha] }], total, descartadas:{ semAvaliacao, foraEnquadramento }, sugestao:{ politicaId, nome, qtd }|null }`.
  - `Unidade = { codigo:'BL02-0804', torre:2, tipoLabel, areaPriv, avaliacao, associativo }`.
  - `Linha = { empId, empNome, codigo, torre, andar, final, tipoLabel, areaPriv, venda, financiamento, subsidio, ato, saldoPS, carne:'linear'|'escalonado', parcelaPS, prazoPS, parcelaFin, crTotal, jurosNominal, prazoFin, politicaId }`.
  - `linhaPdf(linha)` → só os campos do PDF: `{ empNome, codigo, tipoLabel, areaPriv, venda, financiamento, subsidio, ato, parcelaPS, prazoPS, carne, parcelaFin }`.
  - `urlAssociativo(linha, cliente, hoje)` → `'simulador-associativo.html?...'`.

- [ ] **Step 1: Escrever o teste**

Criar `tests/match.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const Match = require('../assets/match.js');

const HOJE = new Date(2026, 9, 15);
const NASC = new Date(1990, 2, 15);              /* 36 anos */
const CLIENTE = { renda: 4000, nascimento: NASC, fgts: true };

const EMP = (id, cidade, extra) => Object.assign({ id, nome: 'Emp ' + id, cidade, inicioObra: '2026-01-01',
  entrega: '2028-12-31', parcMin: 150 }, extra || {});
const UN = (codigo, avaliacao, associativo, extra) => Object.assign({ codigo, torre: parseInt(codigo.slice(2, 4), 10),
  tipoLabel: '2 dorms', areaPriv: 42, avaliacao, associativo }, extra || {});

test('numero entende formatos brasileiros', () => {
  assert.equal(Match.numero('3.500,00'), 3500);
  assert.equal(Match.numero('R$ 3.500'), 3500);
  assert.equal(Match.numero('3500'), 3500);
  assert.equal(Match.numero('3500.5'), 3500.5);
  assert.equal(Match.numero(''), 0);
});

test('ato: R$ 1.500 no Ipiranga, R$ 2.500 nos demais', () => {
  assert.equal(Match.atoDe('ipiranga'), 1500);
  assert.equal(Match.atoDe('gaia'), 2500);
});

test('validarCliente: campos obrigatórios, renda e idade fora do MCMV', () => {
  assert.match(Match.validarCliente({ renda: 0, nascimento: NASC, fgts: true }, 'Ribeirão Preto', HOJE), /renda/i);
  assert.match(Match.validarCliente({ renda: 4000, nascimento: null, fgts: true }, 'Ribeirão Preto', HOJE), /nascimento/i);
  assert.match(Match.validarCliente({ renda: 13000.01, nascimento: NASC, fgts: true }, 'Ribeirão Preto', HOJE), /13\.000/);
  assert.match(Match.validarCliente({ renda: 4000, nascimento: new Date(1956, 3, 14), fgts: true }, 'Ribeirão Preto', HOJE), /70 anos e 6 meses/);
  assert.equal(Match.validarCliente(CLIENTE, 'Ribeirão Preto', HOJE), null);
});

test('resumoCliente devolve o enquadramento da renda', () => {
  const r = Match.resumoCliente(CLIENTE, 'Ribeirão Preto', HOJE);
  assert.equal(r.faixa, 'Faixa 2');
  assert.equal(r.jurosNominal, 5.5);
  assert.equal(r.prazo, 420);
  assert.ok(r.financiamentoMax > 0);
});

test('avaliarUnidade: descarta sem avaliação e fora do enquadramento', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  assert.equal(Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0101', 0, 220000), 'diamante', HOJE).status, 'sem-avaliacao');
  assert.equal(Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0102', NaN, 220000), 'diamante', HOJE).status, 'sem-avaliacao');
  /* avaliacao acima de 600 mil: nenhum produto MCMV enquadra */
  assert.equal(Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0103', 650000, 660000), 'diamante', HOJE).status, 'fora-enquadramento');
});

test('avaliarUnidade: financiamento + subsídio + ato acima da venda não deixa saldo negativo', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  const rico = { renda: 9000, nascimento: NASC, fgts: true };
  const r = Match.avaliarUnidade(rico, emp, UN('BL01-0201', 200000, 150000), 'aco', HOJE);
  assert.equal(r.status, 'ok');
  assert.equal(r.linha.saldoPS, 0);
  assert.equal(r.linha.financiamento, 150000 - r.linha.subsidio - 2500);
});

test('avaliarUnidade: aprova pelo linear quando cabe; usa a parcela maior entre seguradoras', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  /* avaliacao 260 mil: a cota de 80% (208 mil) nao limita, a renda sim (parcela CAIXA = 30%) */
  const r = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0301', 260000, 225000), 'diamante', HOJE);
  assert.equal(r.status, 'ok');
  assert.equal(r.linha.carne, 'linear');
  assert.equal(r.linha.prazoPS, 84);
  assert.ok(Math.abs(r.linha.parcelaFin - 1200) < 0.05, 'parcela CAIXA ≈ 30% da renda');
  assert.equal(r.linha.ato, 2500);
  assert.equal(r.linha.andar, 3);
  assert.equal(r.linha.final, 1);
});

test('avaliarUnidade: fora da política (inclui comitê) é descartada', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  assert.equal(Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0401', 260000, 245000), 'aco', HOJE).status, 'politica');
  assert.equal(Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0401', 260000, 245000), 'bronze', HOJE).status, 'politica');
});

test('avaliarUnidade: Pro Soluto pequeno encurta o prazo até a parcela mínima', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  const r = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0501', 260000, 215000), 'aco', HOJE);
  assert.equal(r.status, 'ok');
  assert.ok(r.linha.prazoPS < 84, 'prazo deveria encurtar');
  assert.ok(r.linha.parcelaPS >= 150, 'parcela abaixo da mínima do produto');
});

test('buscar: filtra cidade e empreendimento, agrupa, ordena e conta descartes', () => {
  const park = EMP('park', 'Ribeirão Preto'), ipi = EMP('ipiranga', 'Ribeirão Preto'), seleto = EMP('seleto', 'Campinas');
  const estoque = [
    { emp: park, unidades: [UN('BL01-0301', 260000, 235000), UN('BL01-0302', 260000, 225000), UN('BL01-0303', 0, 230000)] },
    { emp: ipi, unidades: [UN('BL01-0101', 260000, 225000)] },
    { emp: seleto, unidades: [UN('BL01-0101', 260000, 225000)] }
  ];
  const r = Match.buscar({ cliente: CLIENTE, cidade: 'Ribeirão Preto', empId: '', politicaId: 'diamante', hoje: HOJE, estoque });
  assert.deepEqual(r.grupos.map((g) => g.emp.id), ['park', 'ipiranga']);
  assert.deepEqual(r.grupos[0].linhas.map((l) => l.codigo), ['BL01-0302', 'BL01-0301']);
  assert.equal(r.grupos[1].linhas[0].ato, 1500);
  assert.equal(r.total, 3);
  assert.equal(r.descartadas.semAvaliacao, 1);

  const so = Match.buscar({ cliente: CLIENTE, cidade: 'Ribeirão Preto', empId: 'ipiranga', politicaId: 'diamante', hoje: HOJE, estoque });
  assert.deepEqual(so.grupos.map((g) => g.emp.id), ['ipiranga']);
});

test('buscar: sem unidades na política sugere a próxima política que tem', () => {
  const park = EMP('park', 'Ribeirão Preto');
  /* venda 235 mil: reprova no Aco, aprova no Bronze */
  const estoque = [{ emp: park, unidades: [UN('BL01-0301', 260000, 235000)] }];
  const aco = Match.buscar({ cliente: CLIENTE, cidade: 'Ribeirão Preto', empId: '', politicaId: 'aco', hoje: HOJE, estoque });
  assert.equal(aco.total, 0);
  assert.ok(aco.sugestao, 'deveria sugerir uma política acima');
  assert.notEqual(aco.sugestao.politicaId, 'aco');
  assert.equal(aco.sugestao.qtd, 1);
  assert.equal(aco.sugestao.politicaId, 'bronze');
  const nada = [{ emp: park, unidades: [UN('BL01-0301', 260000, 300000)] }];
  const dia = Match.buscar({ cliente: CLIENTE, cidade: 'Ribeirão Preto', empId: '', politicaId: 'diamante', hoje: HOJE, estoque: nada });
  assert.equal(dia.total, 0);
  assert.equal(dia.sugestao, null);
});

test('linhaPdf não carrega nenhum campo interno', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  const { linha } = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0301', 260000, 225000), 'diamante', HOJE);
  const pdf = Match.linhaPdf(linha);
  assert.deepEqual(Object.keys(pdf).sort(), ['areaPriv', 'ato', 'carne', 'codigo', 'empNome', 'financiamento',
    'parcelaFin', 'parcelaPS', 'prazoPS', 'subsidio', 'tipoLabel', 'venda'].sort());
  const texto = JSON.stringify(pdf);
  assert.ok(!/politica|crTotal|avaliacao|folga/i.test(texto));
});

test('urlAssociativo leva os dados para o simulador associativo', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  const { linha } = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0301', 260000, 225000), 'diamante', HOJE);
  const u = new URL(Match.urlAssociativo(linha, CLIENTE, HOJE), 'https://x/');
  assert.equal(u.pathname, '/simulador-associativo.html');
  assert.equal(u.searchParams.get('emp'), 'park');
  assert.equal(u.searchParams.get('unidade'), 'BL01-0301');
  assert.equal(u.searchParams.get('politica'), 'diamante');
  assert.equal(+u.searchParams.get('renda'), 4000);
  assert.equal(+u.searchParams.get('idade'), 36);
  assert.equal(+u.searchParams.get('valor'), 225000);
  assert.equal(+u.searchParams.get('fin'), linha.financiamento);
  assert.equal(+u.searchParams.get('ato'), 2500);
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/match.test.js`
Expected: FAIL com `Cannot find module '../assets/match.js'`.

- [ ] **Step 3: Implementar**

Criar `assets/match.js`:

```js
/* ============================================================
   MATCH DE UNIDADES - regras de negocio
   ------------------------------------------------------------
   Funcoes puras (sem DOM, sem rede). Cruza o cliente com as
   unidades disponiveis usando o motor CAIXA e a copia do
   Pro Soluto. Usado por /match-unidades via window.Match e
   pelos testes (node --test tests/*.test.js).
   Spec: docs/superpowers/specs/2026-10-15-match-unidades-design.md
   ============================================================ */
(function (raiz) {
  'use strict';

  var Motor = typeof module !== 'undefined' && module.exports ? require('./motor-caixa.js') : raiz.MotorCaixa;
  var PS = typeof module !== 'undefined' && module.exports ? require('./match-prosoluto.js') : raiz.MatchProSoluto;

  var ATO_PADRAO = 2500;
  var ATO_POR_EMP = { ipiranga: 1500 };
  /* da politica mais baixa para a mais alta (POLITICAS vem do Diamante para o Aco) */
  var ORDEM_POLITICAS = ['aco', 'bronze', 'prata', 'ouro', 'diamante'];

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function iso(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function r2(v) { return Math.round(v * 100) / 100; }

  /* mesmo parser do associativo (num()) */
  function numero(str) {
    if (typeof str === 'number') return str;
    var s = (str || '').toString().replace(/[^\d.,-]/g, '');
    if (!s) return 0;
    var temVirg = s.indexOf(',') >= 0, temPonto = s.indexOf('.') >= 0;
    if (temVirg) { s = s.replace(/\./g, '').replace(',', '.'); }
    else if (temPonto) {
      var partes = s.split('.');
      if (partes.length > 2 || (partes.length === 2 && partes[1].length === 3)) s = partes.join('');
    }
    var v = parseFloat(s);
    return isFinite(v) ? v : 0;
  }

  function atoDe(empId) { return ATO_POR_EMP[empId] || ATO_PADRAO; }

  function idadeAnos(nasc, em) {
    var a = em.getFullYear() - nasc.getFullYear();
    if (em.getMonth() < nasc.getMonth() || (em.getMonth() === nasc.getMonth() && em.getDate() < nasc.getDate())) a--;
    return a;
  }

  /* valor de referencia para o resumo: o teto da faixa da renda */
  function valorReferencia(renda, municipio) {
    if (renda <= 5000) return Motor.CIDADES[municipio].tetoF12;
    if (renda <= 9600) return 400000;
    return 600000;
  }

  function simulaCaixa(cliente, municipio, valor, hoje) {
    return Motor.simular({ renda: cliente.renda, valor: valor, nascimento: cliente.nascimento,
      municipio: municipio, fgts: cliente.fgts !== false, sistema: 'PRICE', hoje: hoje });
  }

  function validarCliente(cliente, cidade, hoje) {
    if (!(cliente.renda > 0)) return 'Informe a renda bruta do cliente.';
    if (!cliente.nascimento || !isFinite(cliente.nascimento.getTime())) return 'Informe a data de nascimento do cliente.';
    if (cliente.renda > 13000) return 'Renda acima de R$ 13.000: fora do Minha Casa Minha Vida.';
    var municipio = Motor.MUNICIPIO_POR_CIDADE[cidade];
    if (!municipio) return 'Escolha a cidade.';
    var r = simulaCaixa(cliente, municipio, valorReferencia(cliente.renda, municipio), hoje);
    if (r.erro) return /70 anos/.test(r.erro)
      ? 'Cliente acima de 70 anos e 6 meses: fora do limite de idade da CAIXA.'
      : 'Fora das regras da CAIXA: ' + r.erro + '.';
    return null;
  }

  function resumoCliente(cliente, cidade, hoje) {
    var municipio = Motor.MUNICIPIO_POR_CIDADE[cidade];
    var r = simulaCaixa(cliente, municipio, valorReferencia(cliente.renda, municipio), hoje);
    return { faixa: r.faixa, jurosNominal: r.jurosNominal, prazo: r.prazo,
             financiamentoMax: r.valorFinanciamento, subsidio: r.subsidio };
  }

  function avaliarUnidade(cliente, emp, un, politicaId, hoje) {
    if (!(un.avaliacao > 0) || !(un.associativo > 0)) return { status: 'sem-avaliacao' };
    var municipio = Motor.MUNICIPIO_POR_CIDADE[emp.cidade];
    var cx = simulaCaixa(cliente, municipio, un.avaliacao, hoje);
    if (cx.erro) return { status: 'fora-enquadramento' };

    var ato = atoDe(emp.id);
    var venda = un.associativo;
    var subsidio = cx.subsidio;
    /* Review Focus 1: banco + subsidio + ato nao podem passar da venda */
    var financiamento = Math.max(0, Math.min(cx.valorFinanciamento, r2(venda - subsidio - ato)));
    var parcelaFin = Math.max.apply(null, cx.seguradoras.map(function (s) { return s.primeira; }));

    var pol = PS.politicaPorId(politicaId);
    var dataVenda = iso(hoje);
    var e = {
      emp: { id: emp.id, nome: emp.nome, inicioObra: emp.inicioObra, entrega: PS.entregaDe(emp, un.torre), parcMin: emp.parcMin },
      politica: pol, dataVenda: dataVenda, dataVenc1: PS.sugereVenc1(dataVenda), dataAto: dataVenda,
      prazo: pol.prazo, valor: venda, financiado: financiamento, subsidio: subsidio, ato: ato,
      renda: cliente.renda, parcFin: parcelaFin
    };
    var c = PS.calcular(e);
    /* carne abaixo da parcela minima do produto: encurta o prazo,
       como o associativo orienta ("Reduza o prazo") */
    while (c.pronto && c.saldoCorrigido > 0.01 && c.linear.parcela < emp.parcMin && e.prazo > 1) {
      e.prazo--;
      c = PS.calcular(e);
    }
    var ap = PS.aprovacao(c, e);
    if (!ap.linear && !ap.escalonado) return { status: 'politica' };

    var carne = ap.linear ? 'linear' : 'escalonado';
    var num = un.codigo.slice(un.codigo.indexOf('-') + 1);   /* "0804" */
    return {
      status: 'ok',
      linha: {
        empId: emp.id, empNome: emp.nome, codigo: un.codigo, torre: un.torre,
        andar: parseInt(num.slice(0, num.length - 2), 10), final: parseInt(num.slice(-2), 10),
        tipoLabel: un.tipoLabel, areaPriv: un.areaPriv,
        venda: venda, financiamento: financiamento, subsidio: subsidio, ato: ato,
        saldoPS: Math.max(0, r2(c.preSaldo)), carne: carne,
        parcelaPS: carne === 'linear' ? c.linear.parcela : r2(c.escalonado.faixas[0].parcela),
        prazoPS: e.prazo, parcelaFin: parcelaFin,
        crTotal: carne === 'linear' ? c.crLinear : c.crEscal,
        jurosNominal: cx.jurosNominal, prazoFin: cx.prazo, politicaId: pol.id
      }
    };
  }

  function contaNaPolitica(cliente, alvo, politicaId, hoje) {
    var n = 0;
    alvo.forEach(function (g) {
      g.unidades.forEach(function (un) {
        if (avaliarUnidade(cliente, g.emp, un, politicaId, hoje).status === 'ok') n++;
      });
    });
    return n;
  }

  function buscar(o) {
    var alvo = o.estoque.filter(function (g) {
      return g.emp.cidade === o.cidade && (!o.empId || g.emp.id === o.empId);
    });
    var grupos = [], total = 0, desc = { semAvaliacao: 0, foraEnquadramento: 0 };
    alvo.forEach(function (g) {
      var linhas = [];
      g.unidades.forEach(function (un) {
        var r = avaliarUnidade(o.cliente, g.emp, un, o.politicaId, o.hoje);
        if (r.status === 'ok') linhas.push(r.linha);
        else if (r.status === 'sem-avaliacao') desc.semAvaliacao++;
        else if (r.status === 'fora-enquadramento') desc.foraEnquadramento++;
      });
      linhas.sort(function (a, b) { return a.parcelaPS - b.parcelaPS || (a.codigo < b.codigo ? -1 : 1); });
      if (linhas.length) { grupos.push({ emp: g.emp, linhas: linhas }); total += linhas.length; }
    });

    var sugestao = null;
    if (!total) {
      var acima = ORDEM_POLITICAS.slice(ORDEM_POLITICAS.indexOf(o.politicaId) + 1);
      for (var i = 0; i < acima.length && !sugestao; i++) {
        var qtd = contaNaPolitica(o.cliente, alvo, acima[i], o.hoje);
        if (qtd) sugestao = { politicaId: acima[i], nome: PS.politicaPorId(acima[i]).nome, qtd: qtd };
      }
    }
    return { grupos: grupos, total: total, descartadas: desc, sugestao: sugestao };
  }

  function linhaPdf(l) {
    return { empNome: l.empNome, codigo: l.codigo, tipoLabel: l.tipoLabel, areaPriv: l.areaPriv,
             venda: l.venda, financiamento: l.financiamento, subsidio: l.subsidio, ato: l.ato,
             parcelaPS: l.parcelaPS, prazoPS: l.prazoPS, carne: l.carne, parcelaFin: l.parcelaFin };
  }

  function urlAssociativo(l, cliente, hoje) {
    var p = {
      emp: l.empId, unidade: l.codigo, politica: l.politicaId,
      renda: cliente.renda, idade: idadeAnos(cliente.nascimento, hoje), valor: l.venda,
      fin: l.financiamento, sub: l.subsidio, parcFin: l.parcelaFin, ato: l.ato
    };
    var q = Object.keys(p).map(function (k) { return k + '=' + encodeURIComponent(p[k]); }).join('&');
    return 'simulador-associativo.html?' + q;
  }

  var api = {
    numero: numero, atoDe: atoDe, validarCliente: validarCliente, resumoCliente: resumoCliente,
    avaliarUnidade: avaliarUnidade, buscar: buscar, linhaPdf: linhaPdf, urlAssociativo: urlAssociativo,
    ORDEM_POLITICAS: ORDEM_POLITICAS
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.Match = api;
})(this);
```

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test tests/match.test.js`
Expected: PASS, 13 testes.

Os valores dos testes foram calibrados rodando este código (renda R$ 4.000, 36 anos, avaliação R$ 260 mil → financiamento ≈ R$ 206,7 mil): venda 205 mil = Pro Soluto zerado; 215 mil = Pro Soluto pequeno (prazo encurta); 225 mil = aprova em todas; 235 mil = reprova no Aço e aprova no Bronze; 245 mil = só Diamante; 300 mil = nenhuma.

- [ ] **Step 5: Rodar a suíte inteira**

Run: `node --test tests/*.test.js`
Expected: PASS em todos os arquivos (os de pendências e visitas continuam passando).

- [ ] **Step 6: Commit**

```bash
git add assets/match.js tests/match.test.js
git commit -m "feat(match): regras do Match de Unidades

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Página `match-unidades.html` (formulário, resultado e PDF)

**Files:**
- Create: `match-unidades.html`
- Create: `assets/match.css`
- Create: `assets/match-app.js`

**Interfaces:**
- Consumes: `window.SIM_EMPS`, `window.SimUnidades.carregar/aoMudar/estado/erro/porEmpreendimento` (`assets/simuladores.js`); `window.Match.*` (Task 3); `window.MatchProSoluto.POLITICAS` (Task 2); `window.jspdf.jsPDF` + autotable.
- Produces: página navegável em `/match-unidades.html`.

- [ ] **Step 1: Criar a página**

Criar `match-unidades.html`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Match de Unidades · Portal do Corretor</title>
<link rel="icon" type="image/webp" href="assets/img/favicon.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/home.css">
<link rel="stylesheet" href="assets/match.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>
</head>
<body>

<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>

<header class="site-header">
  <div class="wrap">
    <a class="brand-lockup" href="index.html">
      <img class="brand-logo" src="assets/img/logo-direcional-header.png" width="415" height="95" alt="Grupo Direcional">
      <span class="brand-rule"></span>
      <span class="brand-name">Portal do Corretor</span>
    </a>
  </div>
</header>

<main class="wrap mt-main" id="conteudo">
  <p class="step-label">Ferramentas</p>
  <h1 class="mt-title">Match de Unidades</h1>
  <p class="mt-sub">Informe o perfil do cliente para ver as unidades que ele consegue comprar, com financiamento CAIXA, subsídio e Pro Soluto estimados.</p>

  <form class="mt-form" id="mt-form" novalidate>
    <div class="mt-field">
      <label for="f-cidade">Cidade</label>
      <select id="f-cidade" required></select>
    </div>
    <div class="mt-field">
      <label for="f-emp">Empreendimento</label>
      <select id="f-emp"></select>
    </div>
    <div class="mt-field">
      <label for="f-renda">Renda bruta</label>
      <input id="f-renda" type="text" inputmode="decimal" placeholder="R$ 0,00" autocomplete="off" required>
    </div>
    <div class="mt-field">
      <label for="f-nasc">Data de nascimento</label>
      <input id="f-nasc" type="date" required>
    </div>
    <fieldset class="mt-field mt-seg">
      <legend>3 anos de FGTS</legend>
      <label><input type="radio" name="fgts" value="S" checked> Sim</label>
      <label><input type="radio" name="fgts" value="N"> Não</label>
    </fieldset>
    <div class="mt-field">
      <label for="f-pol">Política</label>
      <select id="f-pol"></select>
    </div>
    <p class="mt-erro" id="mt-erro" role="alert" hidden></p>
    <button class="mt-btn" type="submit" id="mt-buscar">Encontrar unidades</button>
  </form>

  <p class="notice mt-status" id="mt-status" hidden></p>

  <section class="mt-resultado" id="mt-resultado" hidden aria-live="polite">
    <div class="mt-resumo" id="mt-resumo"></div>
    <div class="mt-acoes">
      <span id="mt-contagem"></span>
      <button class="mt-btn mt-btn-sec" type="button" id="mt-pdf" disabled>Gerar PDF (0)</button>
    </div>
    <div id="mt-grupos"></div>
    <p class="mt-rodape" id="mt-rodape"></p>
  </section>

  <p class="mt-aviso">Valores estimados com o motor calibrado no Simulador Habitacional CAIXA em 15/10/2026. Sujeitos à análise de crédito da CAIXA e à aprovação da Direcional.</p>
</main>

<script src="assets/simuladores.js"></script>
<script src="assets/motor-caixa.js"></script>
<script src="assets/match-prosoluto.js"></script>
<script src="assets/match.js"></script>
<script src="assets/match-app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Criar o CSS**

Criar `assets/match.css`:

```css
/* ============================================================
   Match de Unidades - estilos da pagina
   Usa os tokens e o cabecalho de assets/home.css.
   ============================================================ */
.mt-main{padding-top:2rem;padding-bottom:3rem}
.mt-title{font-size:1.8rem;font-weight:700;letter-spacing:-.6px;color:var(--ink);margin:.2rem 0 .4rem}
.mt-sub{color:var(--grey);max-width:60ch;line-height:1.55;margin:0 0 1.6rem}

.mt-form{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem 1.2rem;
  background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:1.4rem}
.mt-field{display:flex;flex-direction:column;gap:.35rem;min-width:0;border:0;padding:0;margin:0}
.mt-field label,.mt-field legend{font-size:.78rem;font-weight:500;color:var(--grey);letter-spacing:.02em}
.mt-field input,.mt-field select{font:inherit;font-size:1rem;color:var(--ink);background:var(--surface);
  border:1px solid var(--line);border-radius:10px;padding:.7rem .8rem;min-height:44px;width:100%}
.mt-field input:focus,.mt-field select:focus{outline:none;border-color:var(--dir-red);box-shadow:0 0 0 3px rgba(228,3,43,.15)}
.mt-seg{flex-direction:row;align-items:center;gap:1rem;flex-wrap:wrap}
.mt-seg legend{width:100%;margin-bottom:.35rem}
.mt-seg label{display:flex;align-items:center;gap:.4rem;font-size:1rem;color:var(--ink);min-height:44px}
.mt-erro{grid-column:1/-1;margin:0;color:var(--dir-red-deep);font-weight:500}
.mt-btn{grid-column:1/-1;justify-self:start;font:inherit;font-weight:700;color:#fff;background:var(--dir-red);
  border:0;border-radius:12px;padding:.85rem 1.4rem;min-height:48px;cursor:pointer}
.mt-btn:hover{background:var(--dir-red-deep)}
.mt-btn:disabled{opacity:.5;cursor:default}
.mt-btn-sec{background:var(--surface);color:var(--dir-red);border:1px solid var(--dir-red)}
.mt-btn-sec:hover{background:#fff5f6}
.mt-status{margin-top:1.4rem}

.mt-resultado{margin-top:2rem}
.mt-resumo{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.8rem;
  background:var(--ink);color:#fff;border-radius:16px;padding:1.2rem 1.4rem}
.mt-resumo span{display:block;font-size:.72rem;opacity:.75;letter-spacing:.04em;text-transform:uppercase}
.mt-resumo b{font-size:1.15rem}
.mt-acoes{display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin:1.4rem 0 .6rem}
.mt-acoes .mt-btn{grid-column:auto}

.mt-grupo{margin-top:1.4rem}
.mt-grupo h2{font-size:1.1rem;color:var(--ink);margin:0 0 .6rem}
.mt-grupo h2 small{color:var(--grey);font-weight:400}
.mt-un{display:grid;grid-template-columns:auto 1fr auto;gap:.4rem 1rem;align-items:start;
  background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:1rem;margin-bottom:.6rem}
.mt-un input[type=checkbox]{width:22px;height:22px;margin-top:.15rem;accent-color:var(--dir-red)}
.mt-un-cod{font-weight:700;color:var(--ink)}
.mt-un-sub{font-size:.85rem;color:var(--grey)}
.mt-un-nums{grid-column:2/-1;display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:.4rem 1rem;font-size:.86rem}
.mt-un-nums span{color:var(--grey);display:block;font-size:.72rem}
.mt-un-nums b{color:var(--ink)}
.mt-un a{font-size:.85rem;font-weight:500;color:var(--dir-red);text-decoration:none;white-space:nowrap}
.mt-un a:hover{text-decoration:underline}
.mt-rodape,.mt-aviso{font-size:.8rem;color:var(--grey);margin-top:1.2rem;line-height:1.5}

@media (max-width:560px){
  .mt-form{padding:1rem}
  .mt-un{grid-template-columns:auto 1fr}
  .mt-un a{grid-column:2}
}
```

- [ ] **Step 3: Criar a lógica da tela**

Criar `assets/match-app.js`:

```js
/* ============================================================
   MATCH DE UNIDADES - tela
   Formulario -> SimUnidades (estoque ao vivo) -> Match.buscar
   -> lista por empreendimento -> associativo / PDF.
   ============================================================ */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var EMPS = window.SIM_EMPS;
  var POLITICAS = window.MatchProSoluto.POLITICAS;
  var ultimo = null;          /* { cliente, hoje, resultado } */
  var marcadas = {};          /* codigo|empId -> linha */

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function brl(n) {
    return (isFinite(n) ? n : 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
  function pct(f) { return ((f || 0) * 100).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'; }
  function hoje() { var d = new Date(); return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }

  /* ---------- formulario ---------- */
  function cidades() {
    var vistas = [];
    EMPS.forEach(function (e) { if (vistas.indexOf(e.cidade) < 0) vistas.push(e.cidade); });
    return vistas;
  }
  function preencheCidades() {
    $('f-cidade').innerHTML = cidades().map(function (c) { return '<option>' + esc(c) + '</option>'; }).join('');
    preencheEmps();
  }
  function preencheEmps() {
    var c = $('f-cidade').value;
    $('f-emp').innerHTML = '<option value="">Todos</option>' + EMPS.filter(function (e) { return e.cidade === c; })
      .map(function (e) { return '<option value="' + esc(e.id) + '">' + esc(e.nome) + '</option>'; }).join('');
  }
  function preenchePoliticas() {
    $('f-pol').innerHTML = window.Match.ORDEM_POLITICAS.map(function (id) {
      var p = window.MatchProSoluto.politicaPorId(id);
      return '<option value="' + id + '"' + (id === 'aco' ? ' selected' : '') + '>' + esc(p.nome) + '</option>';
    }).join('');
  }
  function lerCliente() {
    var nasc = $('f-nasc').value ? new Date($('f-nasc').value + 'T00:00:00') : null;
    return {
      renda: window.Match.numero($('f-renda').value),
      nascimento: nasc,
      fgts: document.querySelector('input[name=fgts]:checked').value === 'S'
    };
  }
  function erro(msg) { var el = $('mt-erro'); el.textContent = msg || ''; el.hidden = !msg; }

  /* ---------- estoque ---------- */
  function estoque(cidade) {
    return EMPS.filter(function (e) { return e.cidade === cidade; }).map(function (emp) {
      var u = window.SimUnidades.porEmpreendimento(emp), unidades = [];
      u.blocos.forEach(function (b) {
        (u.unidades[b.id] || []).forEach(function (cod) {
          var d = u.detalhes[cod] || {};
          unidades.push({ codigo: cod, torre: parseInt(b.id.replace(/\D/g, ''), 10), tipoLabel: d.tipoLabel,
            areaPriv: d.areaPriv, avaliacao: d.avaliacao, associativo: d.associativo });
        });
      });
      return { emp: emp, unidades: unidades };
    });
  }

  /* ---------- busca ---------- */
  function buscar(politicaId) {
    var cliente = lerCliente(), cidade = $('f-cidade').value, h = hoje();
    var msg = window.Match.validarCliente(cliente, cidade, h);
    erro(msg);
    if (msg) { $('mt-resultado').hidden = true; return; }
    if (politicaId) $('f-pol').value = politicaId;

    var est = window.SimUnidades.estado();
    if (est !== 'ok') {
      status(est === 'erro' ? 'erro' : 'carregando');
      pendente = true;
      return;
    }
    var resultado = window.Match.buscar({ cliente: cliente, cidade: cidade, empId: $('f-emp').value,
      politicaId: $('f-pol').value, hoje: h, estoque: estoque(cidade) });
    ultimo = { cliente: cliente, hoje: h, resultado: resultado };
    marcadas = {};
    render(window.Match.resumoCliente(cliente, cidade, h), resultado);
  }

  var pendente = false;
  function status(est) {
    var el = $('mt-status');
    if (est === 'carregando') { el.innerHTML = '<strong>Buscando as unidades disponíveis...</strong>'; el.hidden = false; }
    else if (est === 'erro') {
      el.innerHTML = '<strong>Não foi possível carregar as unidades.</strong> ' + esc(window.SimUnidades.erro()) +
        ' <button type="button" class="mt-btn mt-btn-sec" id="mt-retry">Tentar novamente</button>';
      el.hidden = false;
      $('mt-retry').onclick = function () { location.reload(); };
    } else { el.hidden = true; }
  }

  /* ---------- resultado ---------- */
  function render(resumo, r) {
    $('mt-resumo').innerHTML =
      '<div><span>Enquadramento</span><b>' + esc(resumo.faixa) + '</b></div>' +
      '<div><span>Juros CAIXA</span><b>' + resumo.jurosNominal.toLocaleString('pt-BR') + '% a.a.</b></div>' +
      '<div><span>Prazo CAIXA</span><b>' + resumo.prazo + ' meses</b></div>' +
      '<div><span>Financiamento até</span><b>' + brl(resumo.financiamentoMax) + '</b></div>' +
      '<div><span>Subsídio estimado</span><b>' + brl(resumo.subsidio) + '</b></div>';

    var pol = window.MatchProSoluto.politicaPorId($('f-pol').value).nome;
    $('mt-contagem').textContent = r.total === 1 ? '1 unidade cabe na política ' + pol
                                                 : r.total + ' unidades cabem na política ' + pol;
    var html = '';
    if (!r.total) {
      html = '<p class="notice"><strong>Nenhuma unidade cabe na política ' + esc(pol) + '.</strong> ' +
        (r.sugestao ? (r.sugestao.qtd + (r.sugestao.qtd === 1 ? ' unidade cabe' : ' unidades cabem') +
          ' na política ' + esc(r.sugestao.nome) + '. <button type="button" class="mt-btn mt-btn-sec" id="mt-sug">Ver na política ' +
          esc(r.sugestao.nome) + '</button>') : 'Nenhuma política aprova as unidades desse recorte.') + '</p>';
    }
    r.grupos.forEach(function (g) {
      html += '<section class="mt-grupo"><h2>' + esc(g.emp.nome) + ' <small>· ' + g.linhas.length + '</small></h2>';
      g.linhas.forEach(function (l) {
        var chave = l.empId + '|' + l.codigo;
        html += '<article class="mt-un">' +
          '<input type="checkbox" data-k="' + esc(chave) + '" aria-label="Incluir ' + esc(l.codigo) + ' no PDF">' +
          '<div><div class="mt-un-cod">' + esc(l.codigo) + '</div>' +
          '<div class="mt-un-sub">Torre ' + l.torre + ' · ' + l.andar + 'º andar · final ' + l.final + ' · ' +
          esc(l.tipoLabel || '') + (l.areaPriv ? ' · ' + l.areaPriv + ' m²' : '') + '</div></div>' +
          '<a href="' + esc(window.Match.urlAssociativo(l, ultimo.cliente, ultimo.hoje)) + '">Abrir no associativo →</a>' +
          '<div class="mt-un-nums">' +
          '<div><span>Valor</span><b>' + brl(l.venda) + '</b></div>' +
          '<div><span>Financiamento</span><b>' + brl(l.financiamento) + '</b></div>' +
          '<div><span>Subsídio</span><b>' + brl(l.subsidio) + '</b></div>' +
          '<div><span>Ato</span><b>' + brl(l.ato) + '</b></div>' +
          '<div><span>Pro Soluto (' + l.carne + ')</span><b>' + brl(l.parcelaPS) + ' × ' + l.prazoPS + '</b></div>' +
          '<div><span>Parcela CAIXA</span><b>' + brl(l.parcelaFin) + '</b></div>' +
          '<div><span>Comprometimento</span><b>' + pct(l.crTotal) + '</b></div>' +
          '</div></article>';
      });
      html += '</section>';
    });
    $('mt-grupos').innerHTML = html;

    var d = r.descartadas, partes = [];
    if (d.semAvaliacao) partes.push(d.semAvaliacao + ' sem valor de avaliação na planilha');
    if (d.foraEnquadramento) partes.push(d.foraEnquadramento + ' fora do enquadramento da renda');
    $('mt-rodape').textContent = partes.length ? 'Ficaram de fora: ' + partes.join(' · ') + '.' : '';

    $('mt-resultado').hidden = false;
    atualizaPdf();
    if ($('mt-sug')) $('mt-sug').onclick = function () { buscar(r.sugestao.politicaId); };
  }

  function linhaPorChave(k) {
    var achada = null;
    ultimo.resultado.grupos.forEach(function (g) {
      g.linhas.forEach(function (l) { if (l.empId + '|' + l.codigo === k) achada = l; });
    });
    return achada;
  }
  function atualizaPdf() {
    var n = Object.keys(marcadas).length;
    $('mt-pdf').textContent = 'Gerar PDF (' + n + ')';
    $('mt-pdf').disabled = !n;
  }

  /* ---------- PDF (spec secao 7) ---------- */
  function gerarPdf() {
    if (!window.jspdf || !window.jspdf.jsPDF) { alert('A biblioteca de PDF ainda está carregando. Tente de novo em alguns segundos.'); return; }
    var nome = prompt('Nome do cliente (opcional):', '') || '';
    var doc = new window.jspdf.jsPDF({ unit: 'mm', format: 'a4' });
    var W = doc.internal.pageSize.getWidth(), M = 14;
    doc.setFont('helvetica', 'bold'); doc.setFontSize(15); doc.setTextColor(228, 3, 43);
    doc.text('Grupo Direcional', M, 18);
    doc.setFontSize(11); doc.setTextColor(58, 64, 67);
    doc.text('Unidades sugeridas' + (nome ? ' para ' + nome : ''), M, 26);
    doc.setFont('helvetica', 'normal'); doc.setFontSize(8.5); doc.setTextColor(106, 114, 117);
    doc.text('Gerado em ' + hoje().toLocaleDateString('pt-BR'), M, 31);

    var linhas = Object.keys(marcadas).map(function (k) { return window.Match.linhaPdf(marcadas[k]); });
    doc.autoTable({
      startY: 36, margin: { left: M, right: M },
      head: [['Empreendimento / unidade', 'Valor', 'Financiamento', 'Subsídio', 'Ato', 'Pro Soluto', 'Parcela CAIXA']],
      body: linhas.map(function (l) {
        return [l.empNome + '\n' + l.codigo + ' · ' + (l.tipoLabel || '') + (l.areaPriv ? ' · ' + l.areaPriv + ' m²' : ''),
          brl(l.venda), brl(l.financiamento), brl(l.subsidio), brl(l.ato),
          brl(l.parcelaPS) + ' × ' + l.prazoPS + (l.carne === 'escalonado' ? '\n(escalonado)' : ''), brl(l.parcelaFin)];
      }),
      styles: { fontSize: 8, cellPadding: 2.2, textColor: [58, 64, 67] },
      headStyles: { fillColor: [228, 3, 43], textColor: 255 }
    });
    var total = doc.internal.getNumberOfPages();
    for (var p = 1; p <= total; p++) {
      doc.setPage(p);
      var H = doc.internal.pageSize.getHeight();
      doc.setFontSize(7); doc.setTextColor(114, 122, 125);
      doc.text('Simulação aproximada, sujeita à análise de crédito da CAIXA e à aprovação da Direcional.', M, H - 8);
      doc.text('Página ' + p + ' de ' + total, W - M, H - 8, { align: 'right' });
    }
    doc.save('unidades-' + (nome ? nome.replace(/\s+/g, '-').toLowerCase() : 'cliente') + '.pdf');
  }

  /* ---------- eventos ---------- */
  $('f-cidade').addEventListener('change', preencheEmps);
  $('f-renda').addEventListener('blur', function () {
    var v = window.Match.numero(this.value); this.value = v ? brl(v) : '';
  });
  $('mt-form').addEventListener('submit', function (ev) { ev.preventDefault(); buscar(); });
  $('mt-grupos').addEventListener('change', function (ev) {
    var k = ev.target.getAttribute && ev.target.getAttribute('data-k');
    if (!k) return;
    if (ev.target.checked) marcadas[k] = linhaPorChave(k); else delete marcadas[k];
    atualizaPdf();
  });
  $('mt-pdf').addEventListener('click', gerarPdf);

  preencheCidades();
  preenchePoliticas();
  window.SimUnidades.aoMudar(function (est) {
    if (est === 'ok') { status('ok'); if (pendente) { pendente = false; buscar(); } }
    else if (est === 'erro' && pendente) status('erro');
  });
  window.SimUnidades.carregar();
})();
```

- [ ] **Step 4: Verificar no navegador**

Iniciar o servidor com `preview_start` usando a configuração `portal-do-corretor` de `.claude/launch.json` e abrir `/match-unidades.html`. Conferir:

1. Sem erros no console (`read_console_messages`).
2. Cidade Ribeirão Preto, renda `4.000,00`, nascimento `1990-03-15`, FGTS Sim, política Aço → **Encontrar unidades** mostra o resumo (Faixa 2, 5,5% a.a., 420 meses) e a lista agrupada (ou a sugestão de política, se nada couber no Aço).
3. Renda `14.000` → mensagem "Renda acima de R$ 13.000" e nenhuma lista.
4. Nascimento `1956-04-14` → mensagem de idade.
5. Marcar 2 unidades → botão "Gerar PDF (2)" → PDF com as colunas da spec e o rodapé fixo, sem política, C.R. ou avaliação.
6. `resize_window` preset `mobile`: formulário em uma coluna, cartões legíveis e sem rolagem horizontal. Depois voltar com preset `desktop`.

- [ ] **Step 5: Commit**

```bash
git add match-unidades.html assets/match.css assets/match-app.js
git commit -m "feat(match): pagina Match de Unidades com lista e PDF

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Associativo lê parâmetros da URL + card na home

**Files:**
- Modify: `simulador-associativo.html` (bloco INIT, perto da linha 2560: `initCombos();`)
- Modify: `index.html:24-33` (header-links) e `index.html:70-94` (tool-grid)
- Modify: `docs/matriz-caixa/regras-motor-caixa.md` (linha de validação no topo)

**Interfaces:**
- Consumes: formato de URL produzido por `Match.urlAssociativo` (Task 3): `emp, unidade, politica, renda, idade, valor, fin, sub, parcFin, ato` (números com ponto decimal).
- Produces: associativo abre preenchido; card e link na home.

- [ ] **Step 1: Ler a URL no associativo**

Em `simulador-associativo.html`, no bloco `INIT` no fim do `<script>`, inserir **antes** de `initCombos();`:

```js
/* Vindo do Match de Unidades: preenche o formulario a partir da URL.
   So popula o estado - nenhuma conta muda. Campo ausente/invalido e ignorado. */
(function aplicaParametrosUrl(){
  var q = new URLSearchParams(location.search);
  if(!q.has('emp')) return;
  var n = function(k){ var v=parseFloat(q.get(k)); return isFinite(v)&&v>=0 ? v : null; };
  var id = q.get('emp');
  if(EMPS.some(function(e){ return e.id===id; })) S.empId = id;
  var u = q.get('unidade');
  if(S.empId && u && /^BL\d+-\d+$/.test(u)){ S.unidade = u; S.blocoId = u.slice(0, u.indexOf('-')); }
  if(POLITICAS.some(function(p){ return p.id===q.get('politica'); })) S.politicaId = q.get('politica');
  [['renda','renda'],['idade','idade'],['valor','valor'],['fin','financiado'],['sub','subsidio'],
   ['parcFin','parcFin'],['ato','ato']].forEach(function(p){ var v=n(p[0]); if(v!==null) S[p[1]]=v; });
})();
```

O `atualizaUnidades()` já preserva `S.blocoId`/`S.unidade` enquanto o `SimUnidades` carrega e só limpa se a unidade não existir, então a seleção aparece quando o estoque chega. `sugereDatas()` (chamado logo depois no INIT) preenche data da venda, ato e 1º vencimento iguais aos do Match.

- [ ] **Step 2: Conferir que nenhuma conta mudou**

Run: `node --test tests/match-prosoluto.test.js`
Expected: PASS. O golden master executa o motor do associativo; a mudança fica fora do trecho extraído, mas o teste confirma que os marcadores e o cálculo continuam intactos.

- [ ] **Step 3: Card e link na home**

Em `index.html`, dentro de `<nav class="header-links">`, depois do link "Tabela Direta", adicionar:

```html
      <a class="header-link" href="match-unidades.html">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"></circle><line x1="20.5" y1="20.5" x2="15.8" y2="15.8"></line><polyline points="8.3 11.2 10.3 13.2 13.8 9.4"></polyline></svg>
        Match de Unidades
      </a>
```

Dentro de `<div class="tool-grid">`, depois do card de Tabela Direta, adicionar:

```html
      <a class="tool-card" href="match-unidades.html">
        <span class="tool-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"></circle><line x1="20.5" y1="20.5" x2="15.8" y2="15.8"></line><polyline points="8.3 11.2 10.3 13.2 13.8 9.4"></polyline></svg>
        </span>
        <span>
          <span class="tool-title">Match de Unidades
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </span>
          <span class="tool-desc">A partir da renda do cliente, estima financiamento, subsídio e Pro Soluto e mostra as unidades que ele consegue comprar.</span>
        </span>
      </a>
```

- [ ] **Step 4: Apontar o documento de regras para o módulo oficial**

Em `docs/matriz-caixa/regras-motor-caixa.md`, logo abaixo da tabela de validação do topo, adicionar:

```markdown
> Versão oficial em uso: [`assets/motor-caixa.js`](../../assets/motor-caixa.js), testada por
> `tests/motor-caixa.test.js`. O protótipo em `prototipo/` fica como registro da engenharia reversa.
```

- [ ] **Step 5: Verificar no navegador**

Com o preview da Task 4 aberto:

1. Home (`/`): o terceiro card "Match de Unidades" aparece em Ferramentas, alinhado com os outros dois, e o link no cabeçalho funciona. Testar também em `mobile`.
2. No Match, clicar **Abrir no associativo** numa unidade: o associativo abre com empreendimento, torre, unidade, política, renda, valor, financiamento, subsídio, parcela do financiamento e ato preenchidos.
3. No associativo, o veredito da política tem que ser **Aprovado** e a parcela do Pro Soluto igual à do card do Match (no carnê indicado).
4. Abrir `simulador-associativo.html` **sem parâmetros**: comportamento idêntico ao de antes (formulário vazio).

- [ ] **Step 6: Suíte completa e commit**

Run: `node --test tests/*.test.js`
Expected: PASS em todos os arquivos.

```bash
git add simulador-associativo.html index.html docs/matriz-caixa/regras-motor-caixa.md
git commit -m "feat(match): card na home e associativo preenchido pela URL

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Checklist de PR (para quem abrir o PR)

- [ ] `node --test tests/*.test.js` passa.
- [ ] Se alguma política, taxa ou regra do Pro Soluto mudou, a mudança foi feita em `simulador-associativo.html` **e** em `assets/match-prosoluto.js` (o golden master confere).
- [ ] PDF gerado conferido: sem política, folga, C.R. ou avaliação bancária.

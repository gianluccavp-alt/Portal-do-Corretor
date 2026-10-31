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
    ';this.__api={ set(o){ S=Object.assign(estadoInicial(),o); }, calc:calc, check:checklistAprovacao,' +
    ' constantes: JSON.stringify({ POLITICAS: POLITICAS, TX: TX, GAIA: GAIA_ENTREGA_POR_TORRE }) };', ctx);
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

test('constantes de política, taxas e entrega por torre iguais às do associativo', () => {
  assert.equal(JSON.stringify({ POLITICAS: P.POLITICAS, TX: P.TX, GAIA: P.GAIA_ENTREGA_POR_TORRE }), ORIG.api.constantes);
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

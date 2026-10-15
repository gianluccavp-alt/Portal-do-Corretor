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

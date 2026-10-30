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

test('renda acima de R$ 13.000 não dá erro: vai para o SBPE (spec §4.5)', () => {
  const r = M.simular({ renda: 13000.01, valor: 500000, nascimento: dt('15/03/1990'), municipio: '3543402', fgts: true, hoje: HOJE });
  assert.ok(!r.erro, r.erro);
  assert.equal(r.produto, '100501122');
});

test('MUNICIPIO_POR_CIDADE cobre as cidades do catálogo', () => {
  assert.deepEqual(M.MUNICIPIO_POR_CIDADE, { 'Ribeirão Preto': '3543402', Campinas: '3509502', Sorocaba: '3552205' });
  assert.equal(M.CIDADES['3509502'].tetoF12, 270000);
});

/* ---------- SBPE (coleta de 17/10/2026) ---------- */
const HOJE_SBPE = new Date(2026, 9, 17);
/* fin: o teto fechado fica ate R$ 3,64 abaixo da CAIXA (mesmo residuo do MCMV) */
const TOL_SBPE = { fin: 4, prazo: 0, p14: 0.05, p16: 0.05, p4: 0.05 };

test('SBPE: reproduz as 8 respostas da CAIXA (SAC 30%/90%/420 e PRICE 25%/80%/360)', () => {
  const linhas = fs.readFileSync(path.join(FIX, 'casos-sbpe.txt'), 'utf8').trim().split('\n').filter((x) => !x.startsWith('#'));
  assert.equal(linhas.length, 8);
  for (const l of linhas) {
    const c = l.split(';');
    const r = M.simular({ renda: +c[0], valor: +c[1], nascimento: dt(c[2]), municipio: '3543402', fgts: true,
      possuiImovel: c[3] === 'S', sistema: c[4], hoje: HOJE_SBPE });
    const id = 'sbpe ' + l;
    assert.ok(!r.erro, id + ': ' + r.erro);
    assert.equal(r.produto, '100501122', id);
    assert.equal(r.faixa, 'SBPE', id);
    const sg = {}; r.seguradoras.forEach((s) => { sg[s.codigo] = s.primeira; });
    const got = { fin: r.valorFinanciamento, prazo: r.prazo, p14: sg['14'], p16: sg['16'], p4: sg['4'] };
    const exp = { fin: +c[5], prazo: +c[6] };
    if (c[7]) exp.p14 = +c[7];
    if (c[8]) exp.p16 = +c[8];
    if (c[9]) exp.p4 = +c[9];
    for (const k of Object.keys(exp)) {
      assert.ok(Math.abs(got[k] - exp[k]) <= TOL_SBPE[k] + 1e-9, `${id} ${k}: motor ${got[k]} caixa ${exp[k]}`);
    }
  }
});

test('SBPE: juros exibidos 10,92% nominal / 11,49% efetiva, sem subsídio e com taxa de R$ 25', () => {
  const r = M.simular({ renda: 7000, valor: 381000, nascimento: dt('26/01/1998'), municipio: '3543402', fgts: true,
    possuiImovel: true, hoje: HOJE_SBPE });
  assert.equal(r.jurosNominal, 10.92);
  assert.equal(r.jurosEfetivo, 11.49);
  assert.equal(r.subsidio, 0);
  assert.equal(r.taxaAdm, 25);
  assert.deepEqual(r.seguradoras.map((s) => s.codigo), ['14', '16', '4']);
});

test('SBPE: escolhido por possuir imóvel ou por renda acima de R$ 13.000', () => {
  const base = { valor: 300000, nascimento: dt('15/03/1990'), municipio: '3543402', fgts: true, hoje: HOJE_SBPE };
  assert.equal(M.simular({ ...base, renda: 4000, valor: 250000 }).faixa, 'Faixa 2');
  assert.equal(M.simular({ ...base, renda: 4000, valor: 250000, possuiImovel: true }).faixa, 'SBPE');
  assert.equal(M.simular({ ...base, renda: 13000 }).faixa, 'Faixa 4');
  assert.equal(M.simular({ ...base, renda: 13000.01 }).faixa, 'SBPE');
  assert.equal(M.simular({ ...base, renda: 20000, valor: 1200000 }).faixa, 'SBPE');
});

const linhasFixture = (nome) => fs.readFileSync(path.join(FIX, nome), 'utf8').trim().split('\n').filter((x) => !x.startsWith('#'));

test('fator social: subsídio e juros de 37 respostas da CAIXA (com e sem dependente, 3 cidades)', () => {
  const linhas = linhasFixture('casos-fator-social.txt');
  assert.equal(linhas.length, 37);
  for (const l of linhas) {
    const c = l.split(';');
    const cid = M.CIDADES[c[3]];
    const enq = M.enquadrar(+c[0], +c[1], cid, true);
    assert.equal(enq.jn, +c[5], l + ': juros');
    const sub = enq.subsidio ? M.subsidio(+c[0], +c[1], enq.jn, cid, c[2] === 'S') : 0;
    assert.ok(Math.abs(sub - +c[4]) <= TOL.sub, `${l}: motor ${sub}`);
  }
});

test('fator social: 9 simulações PRICE com entrada zero (financiamento, subsídio e parcelas)', () => {
  const linhas = linhasFixture('casos-fator-social-price.txt');
  assert.equal(linhas.length, 9);
  for (const l of linhas) {
    const c = l.split(';');
    const sg = Object.fromEntries(c[9].split(' ').map((x) => { const [k, v] = x.split(':'); return [k, v.split('/').map(Number)]; }));
    confere('fator social ' + l.slice(0, 30),
      { renda: +c[0], valor: +c[1], nascimento: dt('26/01/1998'), municipio: c[3], fgts: c[4] === 'S',
        fatorSocial: c[2] === 'S', hoje: new Date(2026, 9, 30) },
      { fin: +c[5], sub: +c[6], jn: +c[7], prazo: +c[8], p14: sg['14'][0], p15: sg['15'][0], p4: sg['4'][0], u: sg['14'][1] });
  }
});

test('sem dependente a CAIXA concede 30% do desconto da família; subsídio anterior zera', () => {
  const e = { renda: 2500, valor: 200000, nascimento: dt('26/01/1998'), municipio: '3543402', fgts: true, hoje: HOJE };
  assert.equal(M.simular(e).subsidio, 6799);
  assert.equal(M.simular(Object.assign({ fatorSocial: true }, e)).subsidio, 22663);
  assert.equal(M.simular(Object.assign({ fatorSocial: true, subsidioAnterior: true }, e)).subsidio, 0);
});

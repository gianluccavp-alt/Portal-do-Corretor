const M = require('./motor-caixa.js');
const fs = require('fs');
const hoje = new Date(2026, 9, 15);
const dt = (s) => { const [d, m, y] = s.split('/').map(Number); return new Date(y, m - 1, d); };
const casos = [];
for (const r of JSON.parse(fs.readFileSync(__dirname + '/casos-matriz.json'))) {
  casos.push({ id: 'matriz ' + r.renda, e: { renda: r.renda, valor: +r.valor_imovel, nascimento: dt('26/01/1981'), municipio: '3543402', fgts: true, hoje },
    exp: { fin: +r.valor_financiamento, sub: +r.subsidio, jn: +r.juros_nominal, prazo: 417, p14: +r.p1_caixa, p15: +r.p1_mais, p4: +r.p1_tokio, u: +r.pu_caixa } });
}
for (const l of fs.readFileSync(__dirname + '/casos-extras.txt', 'utf8').trim().split('\n')) {
  const c = l.split(';'); const sg = (s) => s.split('/').map(Number);
  casos.push({ id: 'extra ' + c[0] + '@' + c[1] + ' ' + c[4] + (c[3] === 'N' ? ' semFGTS' : '') + ' ' + c[2],
    e: { renda: +c[0], valor: +c[1], nascimento: dt(c[2]), municipio: c[4], fgts: c[3] === 'S', hoje },
    exp: { fin: +c[6], sub: +c[8], jn: +c[9], prazo: +c[10], p14: sg(c[11])[0], p15: sg(c[12])[0], p4: sg(c[13])[0], u: sg(c[11])[1] } });
}
for (const l of fs.readFileSync(__dirname + '/casos-sac.txt', 'utf8').trim().split('\n').filter((x) => !x.startsWith('#'))) {
  const c = l.split(';'); const exp = { fin: +c[4], prazo: +c[6], p14: +c[7], p15: +c[8], p4: +c[9], u: +c[10] };
  if (c[5]) exp.sub = +c[5];
  casos.push({ id: 'sac ' + c[2], e: { renda: +c[0], valor: +c[1], nascimento: dt(c[2]), municipio: c[3], fgts: true, sistema: 'SAC', hoje }, exp });
}
const recusas = [['14/04/1956', true], ['15/02/1956', true], ['15/04/1956', false]];
const worst = {}; let falhas = [];
for (const c of casos) {
  const r = M.simular(c.e);
  if (r.erro) { falhas.push(c.id + ' ERRO ' + r.erro); continue; }
  const got = { fin: r.valorFinanciamento, sub: r.subsidio, jn: r.jurosNominal, prazo: r.prazo,
    p14: r.seguradoras[0].primeira, p15: r.seguradoras[1].primeira, p4: r.seguradoras[2].primeira, u: r.seguradoras[0].ultima };
  for (const k in c.exp) {
    const d = Math.round((got[k] - c.exp[k]) * 100) / 100;
    if (!worst[k] || Math.abs(d) > Math.abs(worst[k].d)) worst[k] = { d, id: c.id };
    const tol = k === 'fin' ? 3 : k === 'sub' ? 1 : 0.05;
    if (Math.abs(d) > tol) falhas.push(`${c.id} ${k}: motor ${got[k]} caixa ${c.exp[k]} (dif ${d})`);
  }
}
for (const [n, deveRecusar] of recusas) {
  const r = M.simular({ renda: 2500, valor: 200000, nascimento: dt(n), municipio: '3543402', fgts: true, sistema: 'SAC', hoje });
  if (!!r.erro !== deveRecusar) falhas.push(`idade ${n}: esperado ${deveRecusar ? 'recusa' : 'simular'}, motor ${r.erro || 'prazo ' + r.prazo}`);
  else if (!deveRecusar && r.prazo !== 120) falhas.push(`idade ${n}: prazo ${r.prazo}, caixa 120`);
}
console.log('casos:', casos.length, '+', recusas.length, 'de idade-limite');
for (const k in worst) console.log(k.padEnd(6), 'maior diferença', worst[k].d, '(' + worst[k].id + ')');
console.log('fora da tolerância:', falhas.length); falhas.slice(0, 25).forEach((f) => console.log('  ' + f));

const test = require('node:test');
const assert = require('node:assert/strict');
const F = require('../assets/financiamento.js');
const MOTOR = require('../assets/motor-caixa.js');

const HOJE = new Date(2026, 10, 7);
const RESP = { ...F.RESP_PADRAO, renda: 2800, nascimento: new Date(1993, 2, 14), fatorSocial: true };
const GAIA = { cidade: 'Ribeirão Preto', avaliacao: 220000, venda: 0, ato: 0, empId: 'gaia', empNome: 'Village Gaia', unidade: 'BL02-0305', unidadeRotulo: 'Bloco 2 · Apto 305' };

test('simular: caso de referência do canvas', () => {
  const s = F.simular(RESP, GAIA, HOJE);
  assert.equal(s.erro, null);
  assert.equal(s.r.faixa, 'Faixa 1');
  assert.equal(s.r.valorFinanciamento, 167397.73);
  assert.equal(s.r.subsidio, 13209);
  assert.equal(s.entrada, 39393.27);
  assert.equal(s.baseEntrada, 'avaliacao');
  assert.equal(s.segPadrao, '15');
  assert.equal(s.parcelaMax, 840);
  assert.equal(s.limitado, false);
});

test('simular: teto venda − subsídio − ato limita e refaz a parcela', () => {
  const s = F.simular(RESP, { ...GAIA, venda: 175000, ato: 2500 }, HOJE);
  assert.equal(s.limitado, true);
  assert.equal(s.capacidade, 167397.73);
  assert.equal(s.r.valorFinanciamento, 159291);
  assert.equal(s.r.seguradoras.find((x) => x.codigo === '15').primeira, 800.76);
  assert.equal(s.entrada, 0);
  assert.equal(s.baseEntrada, 'venda');
});

test('simular: trava da Faixa 3 em R$ 400 mil', () => {
  const s = F.simular({ ...RESP, renda: 6000, fatorSocial: false }, { ...GAIA, avaliacao: 410000, venda: 395000 }, HOJE);
  assert.equal(s.trava, true);
  assert.equal(s.r.faixa, 'Faixa 3');
  assert.equal(s.r.jurosNominal, 7.66);
});

test('simular: SBPE sem subsídio e comprometimento 25% no PRICE', () => {
  const s = F.simular({ ...RESP, renda: 15000, fatorSocial: true }, { ...GAIA, avaliacao: 500000 }, HOJE);
  assert.equal(s.r.faixa, 'SBPE');
  assert.equal(s.r.subsidio, 0);
  assert.equal(s.parcelaMax, 3750);
  assert.equal(s.segPadrao, '16');
});

test('simular: erros do motor viram mensagem em português', () => {
  const idade = F.simular({ ...RESP, nascimento: new Date(1950, 0, 1) }, GAIA, HOJE);
  assert.equal(idade.erro, 'Idade acima de 70 anos e 6 meses');
  assert.match(idade.mensagem, /70 anos e 6 meses/);
  const fora = F.simular({ ...RESP, renda: 12000 }, { ...GAIA, avaliacao: 650000 }, HOJE);
  assert.equal(fora.erro, 'Fora do enquadramento MCMV');
  assert.ok(fora.mensagem.length > 20);
});

test('fator social e subsídio anterior só valem quando a renda permite subsídio', () => {
  assert.equal(F.mostraPerguntasSubsidio(2800, false), true);
  assert.equal(F.mostraPerguntasSubsidio(4000.01, false), false);
  assert.equal(F.mostraPerguntasSubsidio(2800, true), false);
  const s = F.simular({ ...RESP, renda: 6000, fatorSocial: true }, GAIA, HOJE);
  assert.equal(s.motorIn.fatorSocial, false);
});

test('valoresCopia usa a seguradora escolhida', () => {
  const s = F.simular(RESP, GAIA, HOJE);
  assert.deepEqual(F.valoresCopia(s, '15', 2800), { renda: 2800, financiado: 167397.73, subsidio: 13209, parcFin: 840 });
  assert.equal(F.valoresCopia(s, '14', 2800).parcFin, 825.92);
});

test('comparar devolve PRICE e SAC', () => {
  const c = F.comparar(RESP, GAIA, HOJE);
  assert.equal(c.PRICE.r.valorFinanciamento, 167397.73);
  assert.equal(c.SAC.r.valorFinanciamento, 129877.57);
});

test('lerData e validar', () => {
  assert.equal(F.lerData('31/02/1990'), null);
  assert.equal(F.lerData('14/03/1993').getFullYear(), 1993);
  const campos = (resp, im) => F.validar(resp, im, HOJE).map((x) => x.campo);
  assert.deepEqual(campos(RESP, GAIA), []);
  assert.deepEqual(campos({ ...RESP, renda: 0 }, GAIA), ['renda']);
  assert.deepEqual(campos({ ...RESP, nascimento: null }, GAIA), ['nascimento']);
  assert.deepEqual(campos({ ...RESP, nascimento: new Date(2027, 0, 1) }, GAIA), ['nascimento']);
  assert.deepEqual(campos({ ...RESP, nascimento: new Date(2010, 0, 1) }, GAIA), ['nascimento']);
  assert.deepEqual(campos(RESP, { ...GAIA, avaliacao: 0 }), ['valor']);
  assert.deepEqual(campos(RESP, { ...GAIA, cidade: 'Belo Horizonte' }), ['cidade']);
});

test('serieAnual e brl', () => {
  const s = F.simular(RESP, GAIA, HOJE);
  const serie = F.serieAnual(MOTOR.cronograma(s.motorIn, s.r, '15'));
  assert.equal(serie.length, 8);
  assert.ok(Math.abs(serie[0] - 840) <= 0.05);
  assert.equal(F.brl(167397.73), 'R$ 167.397,73');
});

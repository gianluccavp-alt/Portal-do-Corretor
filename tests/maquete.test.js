const test = require('node:test');
const assert = require('node:assert/strict');
const M = require('../assets/maquete.js');

const CFG = { torres: [1, 2, 3], andares: 20, finais: 8, solNascente: { default: [1, 2, 7, 8] } };
const U = (bl, andar, f, status, extra) => Object.assign({ bl, andar, f, status, tipo: 'tipo-ponta', tipoLabel: '2Q C/S Tipo - Ponta' }, extra || {});

test('indice e posicao sao inversos; fora da grade = -1', () => {
  assert.equal(M.indice(CFG, 1, 0, 1), 0);
  assert.equal(M.indice(CFG, 2, 12, 4), (1 * 20 + 12) * 8 + 3);
  assert.deepEqual(M.posicao(CFG, M.indice(CFG, 3, 19, 8)), { torre: 3, andar: 19, final: 8 });
  assert.equal(M.indice(CFG, 4, 1, 1), -1);
  assert.equal(M.indice(CFG, 1, 20, 1), -1);
  assert.equal(M.indice(CFG, 1, 1, 9), -1);
});

test('codigo no formato da planilha', () => {
  assert.equal(M.codigo(1, 12, 4), 'BL01-1204');
  assert.equal(M.codigo(2, 0, 7), 'BL02-0007');
});

test('statusDe normaliza', () => {
  assert.equal(M.statusDe('Disponível'), 'disponivel');
  assert.equal(M.statusDe('Mirror'), 'disponivel');
  assert.equal(M.statusDe('Reservada'), 'reservada');
  assert.equal(M.statusDe('Reservada aguardando revisão de proposta'), 'reservada');
  assert.equal(M.statusDe('Vendida'), 'outro');
});

test('montarGrade: vendida por ausencia, torre sem linhas fora de venda', () => {
  const g = M.montarGrade(CFG, [U('BL-01', 12, 4, 'Disponível'), U('BL-02', 0, 1, 'Reservada')]);
  assert.equal(g.celulas.length, 480);
  assert.deepEqual(g.torresAVenda, [1, 2]);
  assert.equal(g.celulas[M.indice(CFG, 1, 12, 4)].estado, 'disponivel');
  assert.equal(g.celulas[M.indice(CFG, 2, 0, 1)].estado, 'reservada');
  assert.equal(g.celulas[M.indice(CFG, 1, 5, 5)].estado, 'vendida');
  assert.equal(g.celulas[M.indice(CFG, 3, 5, 5)].estado, 'fora');
  assert.equal(g.celulas[M.indice(CFG, 1, 12, 4)].codigo, 'BL01-1204');
});

test('linha com status "outro" conta como vendida', () => {
  const g = M.montarGrade(CFG, [U('BL-01', 3, 3, 'Vendida')]);
  assert.equal(g.celulas[M.indice(CFG, 1, 3, 3)].estado, 'vendida');
});

test('planilha indisponivel: tudo sem-dados, nada disponivel', () => {
  const g = M.montarGrade(CFG, null);
  assert.ok(g.celulas.every((c) => c.estado === 'sem-dados'));
  assert.deepEqual(g.torresAVenda, []);
});

test('linha fora da grade e ignorada e contada', () => {
  const g = M.montarGrade(CFG, [U('BL-04', 1, 1, 'Disponível'), U('BL-01', 20, 1, 'Disponível'), U('BL-01', 1, 9, 'Disponível'), U('BL-01', 1, 1, 'Disponível')]);
  assert.equal(g.ignoradas, 3);
  assert.equal(M.resumo(g).disponiveis, 1);
});

test('duplicada: reservada vence disponivel', () => {
  const g = M.montarGrade(CFG, [U('BL-01', 2, 2, 'Disponível'), U('BL-01', 2, 2, 'Reservada')]);
  assert.equal(g.celulas[M.indice(CFG, 1, 2, 2)].estado, 'reservada');
  const g2 = M.montarGrade(CFG, [U('BL-01', 2, 2, 'Reservada'), U('BL-01', 2, 2, 'Disponível')]);
  assert.equal(g2.celulas[M.indice(CFG, 1, 2, 2)].estado, 'reservada');
});

test('Torre 3 entra sozinha quando aparece na planilha', () => {
  const g = M.montarGrade(CFG, [U('BL-03', 1, 1, 'Disponível')]);
  assert.deepEqual(g.torresAVenda, [3]);
  assert.equal(g.celulas[M.indice(CFG, 1, 1, 1)].estado, 'fora');
});

test('resumo so conta torres a venda', () => {
  const g = M.montarGrade(CFG, [U('BL-01', 1, 1, 'Disponível'), U('BL-01', 1, 2, 'Reservada')]);
  assert.deepEqual(M.resumo(g), { total: 160, disponiveis: 1, reservadas: 1, vendidas: 158, pctVendido: 98.8 });
});

test('nascente e posicaoLabel', () => {
  assert.equal(M.nascente(CFG, 2, 7), true);
  assert.equal(M.nascente(CFG, 2, 4), false);
  assert.equal(M.posicaoLabel('garden-ponta'), 'Ponta');
  assert.equal(M.posicaoLabel('office-tipo-meio'), 'Meio');
});

test('interpretarBusca', () => {
  assert.deepEqual(M.interpretarBusca('T1 1204'), { torre: 1, andar: 12, final: 4 });
  assert.deepEqual(M.interpretarBusca('t2-0007'), { torre: 2, andar: 0, final: 7 });
  assert.deepEqual(M.interpretarBusca('BL01-1204'), { torre: 1, andar: 12, final: 4 });
  assert.deepEqual(M.interpretarBusca('torre 3 apto 504'), { torre: 3, andar: 5, final: 4 });
  assert.deepEqual(M.interpretarBusca('1204'), { torre: null, andar: 12, final: 4 });
  assert.equal(M.interpretarBusca(''), null);
  assert.equal(M.interpretarBusca('abc'), null);
  assert.equal(M.interpretarBusca('T1 12'), null);
});

test('filtrar por disponivel, tipo e faixa de andar', () => {
  const g = M.montarGrade(CFG, [U('BL-01', 1, 2, 'Disponível'), U('BL-01', 10, 1, 'Disponível', { tipo: 'tipo-meio' }), U('BL-01', 15, 2, 'Reservada')]);
  const so = M.filtrar(g, { soDisponiveis: true, tipos: [], andarMin: 0, andarMax: 19 });
  assert.deepEqual([...so].sort((a, b) => a - b), [M.indice(CFG, 1, 1, 2), M.indice(CFG, 1, 10, 1)]);
  const meio = M.filtrar(g, { soDisponiveis: true, tipos: ['tipo-meio'], andarMin: 0, andarMax: 19 });
  assert.deepEqual([...meio], [M.indice(CFG, 1, 10, 1)]);
  const faixa = M.filtrar(g, { soDisponiveis: false, tipos: [], andarMin: 15, andarMax: 19 });
  assert.ok(faixa.has(M.indice(CFG, 1, 15, 2)) && !faixa.has(M.indice(CFG, 1, 10, 1)));
  assert.ok(![...faixa].some((i) => g.celulas[i].estado === 'fora'), 'fora de venda nunca entra');
});

test('vizinhaDisponivel percorre e da a volta', () => {
  const a = M.indice(CFG, 1, 1, 2), b = M.indice(CFG, 2, 3, 1);
  const g = M.montarGrade(CFG, [U('BL-01', 1, 2, 'Disponível'), U('BL-02', 3, 1, 'Disponível'), U('BL-02', 5, 5, 'Reservada')]);
  assert.equal(M.vizinhaDisponivel(g, a, 1), b);
  assert.equal(M.vizinhaDisponivel(g, b, 1), a);
  assert.equal(M.vizinhaDisponivel(g, a, -1), b);
  assert.equal(M.vizinhaDisponivel(g, a, 1, new Set([a])), null);
});

test('urlsSimuladores', () => {
  assert.deepEqual(M.urlsSimuladores('gaia', 'BL01-1204'), {
    associativo: 'simulador-associativo.html?emp=gaia&unidade=BL01-1204',
    tabelaDireta: 'simulador-tabela-direta.html?emp=gaia&unidade=BL01-1204'
  });
});

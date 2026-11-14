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

test('filtrar por sol: nascente usa solNascente do cfg, poente o resto', () => {
  const g = M.montarGrade(CFG, [U('BL-01', 3, 1, 'Disponível'), U('BL-01', 3, 4, 'Disponível'), U('BL-02', 3, 8, 'Disponível')]);
  const base = { soDisponiveis: true, tipos: [], andarMin: 0, andarMax: 19 };
  const nasc = M.filtrar(g, Object.assign({ sol: 'nascente' }, base), CFG);
  assert.deepEqual([...nasc].sort((a, b) => a - b), [M.indice(CFG, 1, 3, 1), M.indice(CFG, 2, 3, 8)]);
  const poen = M.filtrar(g, Object.assign({ sol: 'poente' }, base), CFG);
  assert.deepEqual([...poen], [M.indice(CFG, 1, 3, 4)]);
  assert.equal(M.filtrar(g, base, CFG).size, 3, 'sem sol: nao filtra');
});

test('semUnidade: terreno sem final 1 e Torre 3 sem o 19o andar ficam inexistentes, fora do resumo e dos filtros', () => {
  const cfg = Object.assign({}, CFG, { semUnidade: [{ andares: [0], finais: [1] }, { torres: [3], andarMin: 19 }] });
  assert.equal(M.existe(cfg, 1, 0, 1), false);
  assert.equal(M.existe(cfg, 1, 0, 2), true);
  assert.equal(M.existe(cfg, 3, 19, 4), false);
  assert.equal(M.existe(cfg, 2, 19, 4), true);
  const g = M.montarGrade(cfg, [U('BL-01', 0, 1, 'Disponível'), U('BL-03', 18, 2, 'Disponível'), U('BL-02', 3, 3, 'Disponível')]);
  assert.equal(g.celulas[M.indice(cfg, 1, 0, 1)].estado, 'inexistente');
  assert.equal(g.celulas[M.indice(cfg, 3, 19, 8)].estado, 'inexistente');
  assert.equal(g.celulas[M.indice(cfg, 3, 18, 2)].estado, 'disponivel');
  assert.equal(M.montarGrade(cfg, null).celulas[M.indice(cfg, 3, 19, 1)].estado, 'inexistente');
  const r = M.resumo(g);
  assert.equal(r.total, 480 - 3 - 8);          // 469 unidades reais (FAQ do Village Park)
  const vis = M.filtrar(g, { andarMin: 0, andarMax: 19 }, cfg);
  assert.equal(vis.has(M.indice(cfg, 2, 0, 1)), false);
  assert.equal(vis.has(M.indice(cfg, 3, 19, 5)), false);
  assert.equal(vis.has(M.indice(cfg, 2, 0, 2)), true);
});

test('montarGrade: torresVenda deixa as outras torres fora de venda', () => {
  const cfg = Object.assign({}, CFG, { torresVenda: [1, 3] });
  const g = M.montarGrade(cfg, [U('BL-01', 2, 1, 'Disponível'), U('BL-02', 2, 1, 'Disponível'), U('BL-03', 0, 2, 'Reservada')]);
  assert.equal(g.celulas[M.indice(cfg, 1, 2, 1)].estado, 'disponivel');
  assert.equal(g.celulas[M.indice(cfg, 2, 2, 1)].estado, 'fora');
  assert.equal(g.celulas[M.indice(cfg, 3, 0, 2)].estado, 'reservada');
  assert.deepEqual(g.torresAVenda, [1, 3]);
});

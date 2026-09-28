const test = require('node:test');
const assert = require('node:assert/strict');
const P = require('../assets/pendencias.js');
const vendas = require('./fixtures/vendas.json');

const HOJE = new Date(2026, 8, 28, 10, 0);
const f = (extra) => Object.assign(P.filtrosPadrao(), extra);
const op = (...ns) => ns.map((n) => 'OP-' + String(n).padStart(6, '0'));
const ids = (lista) => lista.map((v) => v.id);
const filtrar = (extra) => ids(P.aplicarFiltros(vendas, f(extra), HOJE));

test('filtrosPadrao', () => {
  assert.deepEqual(P.filtrosPadrao(), {
    busca: '', empreendimento: '', equipe: '', fases: P.FASES_PADRAO.slice(),
    periodo: 'todo', de: '', ate: '', ranking: '', tipo: 'todas', pendencia: 'todas', mostrarCanceladas: false
  });
  assert.notEqual(P.filtrosPadrao().fases, P.filtrosPadrao().fases, 'cada chamada devolve uma lista nova');
});

test('universo padrão: 4 fases, sem canceladas, na ordem de entrada', () => {
  assert.deepEqual(filtrar(), op(1, 2, 3, 4, 5, 6, 7, 9, 10, 13, 15));
});

test('mostrar canceladas inclui as canceladas do recorte', () => {
  assert.deepEqual(filtrar({ mostrarCanceladas: true }), op(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15));
});

test('fase', () => {
  assert.equal(filtrar({ fases: [] }).length, 12, 'lista vazia = todas as fases');
  assert.deepEqual(filtrar({ fases: ['Fechado e ganho'] }), op(11));
  assert.deepEqual(filtrar({ fases: ['aprovado pro soluto'] }), op(3), 'sem acento/caixa');
});

test('busca em cliente, OP e unidade, sem acento', () => {
  assert.deepEqual(filtrar({ busca: 'leticia' }), op(5));
  assert.deepEqual(filtrar({ busca: 'BL02-0104' }), op(1));
  assert.deepEqual(filtrar({ busca: 'op-000010' }), op(10));
});

test('empreendimento e equipe', () => {
  assert.deepEqual(filtrar({ empreendimento: 'Village Gaia' }), op(1, 5, 13));
  assert.deepEqual(filtrar({ equipe: 'DIRECIONAL VENDAS SPI – EQUIPE LEONARDO DONIZETE' }), op(1, 6, 10));
});

test('período', () => {
  assert.deepEqual(filtrar({ periodo: 'mes' }), op(1, 2, 3, 4, 5, 6, 7, 9, 10));
  assert.deepEqual(filtrar({ periodo: 'mes_passado' }), op(13));
  assert.deepEqual(filtrar({ periodo: '30d' }), op(1, 2, 3, 4, 5, 6, 7, 9, 10));
  assert.deepEqual(filtrar({ periodo: 'intervalo', de: '2026-09-15', ate: '2026-09-20' }), op(5, 6, 7));
  assert.deepEqual(filtrar({ periodo: 'intervalo', de: '2026-09-24', ate: '' }), op(9, 10));
});

test('ranking e tipo de venda', () => {
  assert.deepEqual(filtrar({ ranking: 'ouro' }), op(1, 6, 7, 10));
  assert.deepEqual(filtrar({ tipo: 'facilitada' }), op(3, 6));
  assert.equal(filtrar({ tipo: 'comercial' }).length, 9);
});

test('pendência', () => {
  assert.deepEqual(filtrar({ pendencia: 'pcv' }), op(3, 7, 15));
  assert.deepEqual(filtrar({ pendencia: 'ato' }), op(1, 4, 7, 9, 10, 15));
  assert.deepEqual(filtrar({ pendencia: 'ac' }), op(1, 2, 4, 5, 6, 7, 9, 13));
});

test('KPIs do universo padrão', () => {
  assert.deepEqual(P.calcularKpis(vendas, f(), HOJE), {
    total: 11, ac: 8, acReprovadas: 5, acOutras: 3, fid: 10, fidPct: 91,
    ato: 6, pcv: 3, vgv: 2472290, base: 11, canceladasOcultas: 2
  });
});

test('KPIs ignoram o filtro de pendência e respeitam os outros', () => {
  assert.equal(P.calcularKpis(vendas, f({ pendencia: 'pcv' }), HOJE).ac, 8);
  const gaia = P.calcularKpis(vendas, f({ empreendimento: 'Village Gaia' }), HOJE);
  assert.equal(gaia.base, 3);
  assert.equal(gaia.ac, 3);
  assert.equal(gaia.fid, 2);
  assert.equal(gaia.canceladasOcultas, 1);
});

test('ordenar', () => {
  const base = P.aplicarFiltros(vendas, f(), HOJE);
  assert.deepEqual(ids(P.ordenar(base, 'antigas')), op(13, 1, 2, 3, 4, 5, 6, 7, 9, 10, 15));
  assert.deepEqual(ids(P.ordenar(base, 'recentes')), op(10, 9, 7, 6, 5, 4, 3, 2, 1, 13, 15));
  assert.deepEqual(ids(P.ordenar(base, 'valor')), op(9, 3, 2, 6, 10, 5, 1, 13, 4, 15, 7));
  assert.deepEqual(ids(P.ordenar(base, 'pendencias')), op(7, 1, 4, 9, 15, 2, 3, 5, 6, 10, 13));
});

test('ordenar põe canceladas por último e não altera a entrada', () => {
  const comCanceladas = P.aplicarFiltros(vendas, f({ mostrarCanceladas: true }), HOJE);
  const antes = ids(comCanceladas);
  assert.deepEqual(ids(P.ordenar(comCanceladas, 'antigas')).slice(-2), op(14, 8));
  assert.deepEqual(ids(comCanceladas), antes);
});

test('opcoesDeFiltro', () => {
  const o = P.opcoesDeFiltro(vendas);
  assert.deepEqual(o.empreendimentos, ['Conquista Araraquara', 'Direcional Conquista Clube Ipiranga', 'Reserva Direcional Jardim Botânico', 'Village Gaia', 'Village Park']);
  assert.deepEqual(o.fases, ['Análise SAFI', 'Aprovado Pró Soluto', 'Aprovado SAFI', 'Fechado e ganho', 'Proposta Aprovada']);
  assert.deepEqual(o.equipes.map((e) => e.rotulo), [
    'Canal PJ · Carolina Cristina', 'Equipe Debora Pimenta', 'Equipe Gian Turioni',
    'Equipe Leonardo Donizete', 'Equipe Otavio Yudi', 'Equipe Sabrina da Silva - Inativo'
  ]);
  assert.equal(o.equipes[0].valor, 'SPI - CANAL IMOB PJ – CAROLINA CRISTINA');
});

test('mesmasFases e contarFiltrosAtivos', () => {
  assert.ok(P.mesmasFases(['proposta aprovada', 'Aprovado SAFI', 'Análise SAFI', 'Aprovado Pró Soluto'], P.FASES_PADRAO));
  assert.ok(!P.mesmasFases([], P.FASES_PADRAO));
  assert.equal(P.contarFiltrosAtivos(f()), 0);
  assert.equal(P.contarFiltrosAtivos(f({ empreendimento: 'x', periodo: 'mes', fases: [] })), 3);
  assert.equal(P.contarFiltrosAtivos(f({ busca: 'abc', pendencia: 'ac' })), 0, 'busca e pendência não contam');
});

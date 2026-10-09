const test = require('node:test');
const assert = require('node:assert/strict');
const V = require('../assets/visitas.js');
const FIX = require('./fixtures/visitas.json');

const ids = (lista) => lista.map((v) => v.id);
const semData = ({ esp, house, imob, total }) => ({ esp, house, imob, total });

test('filtrar por período, cidade e empreendimento', () => {
  assert.equal(V.filtrar(FIX, {}).length, 8);
  assert.equal(V.filtrar(FIX, { cidade: 'Todas', empreendimento: 'Todos' }).length, 8);
  assert.deepEqual(ids(V.filtrar(FIX, { cidade: 'Campinas' })), ['V1', 'V2', 'V5', 'V6', 'V8']);
  assert.deepEqual(ids(V.filtrar(FIX, { de: '2026-10-09' })), ['V6', 'V7', 'V8']);
  assert.deepEqual(ids(V.filtrar(FIX, { empreendimento: 'Village Park', ate: '2026-10-07' })), ['V3']);
});

test('totaisPorTipo', () => {
  assert.deepEqual(V.totaisPorTipo(FIX), { esp: 2, house: 2, imob: 4, total: 8 });
  assert.deepEqual(V.totaisPorTipo([]), { esp: 0, house: 0, imob: 0, total: 0 });
  assert.deepEqual(V.totaisPorTipo([{ tipo: 'total' }, { tipo: '' }]), { esp: 0, house: 0, imob: 0, total: 0 });
});

test('porDia inclui dias sem visita', () => {
  const dias = V.porDia(FIX, '2026-10-06', '2026-10-09');
  assert.deepEqual(dias.map((d) => d.data), ['2026-10-06', '2026-10-07', '2026-10-08', '2026-10-09']);
  assert.deepEqual(semData(dias[0]), { esp: 0, house: 0, imob: 0, total: 0 });
  assert.deepEqual(semData(dias[1]), { esp: 1, house: 1, imob: 1, total: 3 });
  assert.deepEqual(semData(dias[2]), { esp: 0, house: 0, imob: 2, total: 2 });
  assert.deepEqual(semData(dias[3]), { esp: 1, house: 1, imob: 1, total: 3 });
});

test('porHora joga visitas fora da faixa para as pontas', () => {
  const horas = V.porHora(FIX, 8, 20);
  assert.equal(horas.length, 13);
  assert.equal(horas[0].hora, 8);
  assert.deepEqual(semData(horas[0]), { esp: 0, house: 0, imob: 1, total: 1 }); /* V4 07:45 */
  assert.equal(horas[1].total, 1); /* V1 09:10 */
  assert.equal(horas[3].total, 2); /* V6 e V7 11h */
  assert.deepEqual(semData(horas[12]), { esp: 0, house: 1, imob: 0, total: 1 }); /* V3 21:30 */
  const soma = horas.reduce((a, h) => a + h.total, 0);
  assert.equal(soma, 8);
});

test('porEmpreendimento mostra zerados e ordena por total', () => {
  const lista = [
    { nome: 'Seleto Amoreiras', cidade: 'Campinas' },
    { nome: 'Village Park', cidade: 'Ribeirão Preto' },
    { nome: 'Alta Vista Mangará', cidade: 'Campinas' },
    { nome: 'Conquista Vila da Mata', cidade: 'Sorocaba' }
  ];
  const linhas = V.porEmpreendimento(FIX, lista);
  assert.deepEqual(linhas.map((l) => [l.nome, l.total]), [
    ['Alta Vista Mangará', 5], ['Village Park', 2], ['Conquista Vila da Mata', 1], ['Seleto Amoreiras', 0]
  ]);
  assert.deepEqual(semData(linhas[0]), { esp: 1, house: 1, imob: 3, total: 5 });
  assert.equal(linhas[0].cidade, 'Campinas');
});

test('rankingImobiliarias agrupa sem caixa e sem acento e usa a grafia mais comum', () => {
  assert.deepEqual(V.rankingImobiliarias(FIX, 5), [
    { nome: 'Imobiliária Ápice', qtd: 3 },
    { nome: 'Imóveis Beta', qtd: 1 }
  ]);
  assert.equal(V.rankingImobiliarias(FIX, 1).length, 1);
});

test('recentes ordena por data e hora, mais novo primeiro', () => {
  assert.deepEqual(ids(V.recentes(FIX, 3)), ['V8', 'V7', 'V6']);
  assert.deepEqual(ids(V.ordenarPorTempo(FIX, false)).slice(0, 2), ['V1', 'V2']);
  assert.equal(FIX[0].id, 'V1'); /* nao muta a entrada */
});

test('gerarCSV: BOM, separador ;, ordem cronológica, aspas e neutralização', () => {
  const visitas = [
    { data: '2026-10-09', hora: '11:50', empreendimento: 'Conquista Vila da Mata', cidade: 'Sorocaba', tipo: 'esp', corretorHouse: '', imobiliaria: '', corretorImob: '' },
    { data: '2026-10-08', hora: '14:00', empreendimento: 'Alta Vista Mangará', cidade: 'Campinas', tipo: 'imob', corretorHouse: '', imobiliaria: 'Imob; Centro', corretorImob: '=HYPERLINK("x")' }
  ];
  const esperado = '﻿' +
    'Data;Horário;Empreendimento;Cidade;Tipo;Corretor house;Imobiliária;Corretor imobiliária\r\n' +
    '08/10/2026;14:00;Alta Vista Mangará;Campinas;Imobiliária;;"Imob; Centro";"\'=HYPERLINK(""x"")"\r\n' +
    '09/10/2026;11:50;Conquista Vila da Mata;Sorocaba;Espontânea;;;\r\n';
  assert.equal(V.gerarCSV(visitas), esperado);
});

test('gerarCSV vazio tem só o cabeçalho', () => {
  assert.equal(V.gerarCSV([]), '﻿Data;Horário;Empreendimento;Cidade;Tipo;Corretor house;Imobiliária;Corretor imobiliária\r\n');
});

test('nomeArquivoCSV', () => {
  assert.equal(V.nomeArquivoCSV('2026-10-03', '2026-10-09'), 'visitas-2026-10-03-a-2026-10-09.csv');
});

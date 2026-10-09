const test = require('node:test');
const assert = require('node:assert/strict');
const V = require('../assets/visitas.js');

test('normalizarTexto: trim, espaços e limite de 80', () => {
  assert.equal(V.normalizarTexto('  Imob   Ápice  '), 'Imob Ápice');
  assert.equal(V.normalizarTexto(null), '');
  assert.equal(V.normalizarTexto(undefined), '');
  assert.equal(V.normalizarTexto('x'.repeat(100)).length, 80);
});

test('chaveNome ignora caixa, acento e espaços', () => {
  assert.equal(V.chaveNome(' Imobiliária  ÁPICE '), 'imobiliaria apice');
  assert.equal(V.chaveNome('imobiliaria apice'), 'imobiliaria apice');
});

test('neutralizarFormula prefixa apóstrofo só quando começa com = + - @ tab CR', () => {
  assert.equal(V.neutralizarFormula('=1+1'), "'=1+1");
  assert.equal(V.neutralizarFormula('+55'), "'+55");
  assert.equal(V.neutralizarFormula('-x'), "'-x");
  assert.equal(V.neutralizarFormula('@soma'), "'@soma");
  assert.equal(V.neutralizarFormula('\tA'), "'\tA");
  assert.equal(V.neutralizarFormula('\rA'), "'\rA");
  assert.equal(V.neutralizarFormula('Imob Ápice'), 'Imob Ápice');
  assert.equal(V.neutralizarFormula(''), '');
  assert.equal(V.neutralizarFormula(undefined), '');
});

test('datas ISO: somar, diferença, formatos', () => {
  assert.equal(V.somarDias('2026-10-01', -1), '2026-09-30');
  assert.equal(V.somarDias('2026-12-31', 1), '2027-01-01');
  assert.equal(V.diasEntre('2026-10-03', '2026-10-09'), 7);
  assert.equal(V.diasEntre('2026-10-09', '2026-10-09'), 1);
  assert.equal(V.dataCurta('2026-10-08'), '08/10');
  assert.equal(V.dataBr('2026-10-08'), '08/10/2026');
  assert.equal(V.rotuloDia('2026-10-08'), 'qui 08/10');
});

test('dataLocalIso e horaLocal usam a hora local do aparelho', () => {
  const d = new Date(2026, 9, 9, 7, 5);
  assert.equal(V.dataLocalIso(d), '2026-10-09');
  assert.equal(V.horaLocal(d), '07:05');
});

test('intervalo dos períodos do dashboard', () => {
  assert.deepEqual(V.intervalo('hoje', '2026-10-09'), { de: '2026-10-09', ate: '2026-10-09', dias: 1 });
  assert.deepEqual(V.intervalo('7', '2026-10-09'), { de: '2026-10-03', ate: '2026-10-09', dias: 7 });
  assert.deepEqual(V.intervalo('30', '2026-10-09'), { de: '2026-09-10', ate: '2026-10-09', dias: 30 });
});

test('validarFormulario aponta o primeiro campo que falta', () => {
  const base = { empreendimento: 'Alta Vista Mangará', data: '2026-10-09', hora: '14:35', tipo: 'esp' };
  assert.deepEqual(V.validarFormulario(base), { ok: true, faltando: null });
  assert.equal(V.validarFormulario({ ...base, empreendimento: '' }).faltando, 'empreendimento');
  assert.equal(V.validarFormulario({ ...base, data: '' }).faltando, 'data');
  assert.equal(V.validarFormulario({ ...base, hora: '9:5' }).faltando, 'hora');
  assert.equal(V.validarFormulario({ ...base, tipo: null }).faltando, 'tipo');
  assert.equal(V.validarFormulario({ ...base, tipo: 'total' }).faltando, 'tipo');
  assert.equal(V.validarFormulario({ ...base, tipo: 'imob' }).faltando, 'imobiliaria');
  assert.equal(V.validarFormulario({ ...base, tipo: 'imob', imobiliaria: '   ' }).faltando, 'imobiliaria');
  assert.equal(V.validarFormulario({ ...base, tipo: 'imob', imobiliaria: 'Imob Ápice' }).ok, true);
  assert.equal(V.validarFormulario({ ...base, tipo: 'house' }).ok, true);
  assert.equal(V.validarFormulario({ ...base, empreendimento: '', tipo: null }).faltando, 'empreendimento');
});

test('detalhe de cada tipo para as listas', () => {
  assert.equal(V.detalhe({ tipo: 'esp' }), 'Sem agendamento');
  assert.equal(V.detalhe({ tipo: 'house', corretorHouse: '' }), 'Corretor não informado');
  assert.equal(V.detalhe({ tipo: 'house', corretorHouse: 'Ana' }), 'Ana');
  assert.equal(V.detalhe({ tipo: 'imob', imobiliaria: 'Imob Ápice', corretorImob: '' }), 'Imob Ápice');
  assert.equal(V.detalhe({ tipo: 'imob', imobiliaria: 'Imob Ápice', corretorImob: 'Rui' }), 'Imob Ápice · Rui');
});

test('listaEmpreendimentos achata window.CITIES', () => {
  const cidades = [
    { name: 'Campinas', empreendimentos: [{ nome: 'A' }, { nome: 'B' }] },
    { name: 'Sorocaba', empreendimentos: [{ nome: 'C' }] }
  ];
  assert.deepEqual(V.listaEmpreendimentos(cidades), [
    { nome: 'A', cidade: 'Campinas' }, { nome: 'B', cidade: 'Campinas' }, { nome: 'C', cidade: 'Sorocaba' }
  ]);
  assert.deepEqual(V.listaEmpreendimentos(undefined), []);
});

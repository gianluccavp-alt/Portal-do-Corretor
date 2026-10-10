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

test('detalhe de cada tipo para as listas', () => {
  assert.equal(V.detalhe({ tipo: 'esp', corretor: 'Rui' }), 'Rui');
  assert.equal(V.detalhe({ tipo: 'house', corretor: '' }), 'Corretor não informado');
  assert.equal(V.detalhe({ tipo: 'house', corretor: 'Ana' }), 'Ana');
  assert.equal(V.detalhe({ tipo: 'imob', imobiliaria: 'Imob Ápice', corretor: '' }), 'Imob Ápice');
  assert.equal(V.detalhe({ tipo: 'imob', imobiliaria: 'Imob Ápice', corretor: 'Rui' }), 'Imob Ápice · Rui');
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

test('cpfValido confere dígitos verificadores e recusa sequências', () => {
  ['52998224725', '529.982.247-25', '11144477735', '12345678909', '98765432100'].forEach((c) => assert.equal(V.cpfValido(c), true, c));
  ['52998224724', '11111111111', '000.000.000-00', '1234567890', '123456789012', '', null, 'abc'].forEach((c) => assert.equal(V.cpfValido(c), false, String(c)));
});

test('telefoneValido exige DDD e 10 ou 11 dígitos', () => {
  ['(19) 98765-4321', '19987654321', '(19) 3245-8890', '1932458890'].forEach((t) => assert.equal(V.telefoneValido(t), true, t));
  ['987654321', '199876543210', '(09) 98765-4321', '', null].forEach((t) => assert.equal(V.telefoneValido(t), false, String(t)));
});

test('máscaras de CPF e telefone enquanto digita', () => {
  assert.equal(V.mascaraCpf('529'), '529');
  assert.equal(V.mascaraCpf('5299'), '529.9');
  assert.equal(V.mascaraCpf('5299822'), '529.982.2');
  assert.equal(V.mascaraCpf('5299822472'), '529.982.247-2');
  assert.equal(V.mascaraCpf('52998224725999'), '529.982.247-25');
  assert.equal(V.mascaraCpf('529.982.247-25'), '529.982.247-25');
  assert.equal(V.mascaraTelefone(''), '');
  assert.equal(V.mascaraTelefone('1'), '(1');
  assert.equal(V.mascaraTelefone('199'), '(19) 9');
  assert.equal(V.mascaraTelefone('1932458890'), '(19) 3245-8890');
  assert.equal(V.mascaraTelefone('19987654321'), '(19) 98765-4321');
  assert.equal(V.mascaraTelefone('199876543219'), '(19) 98765-4321');
});

test('formatarCpf e formatarTelefone só mascaram números completos', () => {
  assert.equal(V.formatarCpf('52998224725'), '529.982.247-25');
  assert.equal(V.formatarCpf('5299'), '5299');
  assert.equal(V.formatarTelefone('1932458890'), '(19) 3245-8890');
  assert.equal(V.formatarTelefone('19987654321'), '(19) 98765-4321');
  assert.equal(V.formatarTelefone('123'), '123');
  assert.equal(V.formatarTelefone(undefined), '');
});

test('primeiroNome', () => {
  assert.equal(V.primeiroNome('  Mariana   Souza Lima '), 'Mariana');
  assert.equal(V.primeiroNome(''), '');
  assert.equal(V.primeiroNome(undefined), '');
});

test('validarVisita lista todos os erros e aponta o primeiro', () => {
  const ok = {
    empreendimento: 'Alta Vista Mangará', tipo: 'esp', cliente: 'Mariana Souza', cpf: '529.982.247-25',
    telefone: '(19) 98765-4321', data: '2026-10-09', hora: '14:35', corretor: 'Rui', gerente: ''
  };
  assert.deepEqual(V.validarVisita(ok), { ok: true, erros: {}, primeiro: null });
  const r = V.validarVisita({ ...ok, cliente: ' ', cpf: '529.982.247-2', corretor: '' });
  assert.equal(r.ok, false);
  assert.equal(r.primeiro, 'cliente');
  assert.deepEqual(Object.keys(r.erros), ['cliente', 'cpf', 'corretor']);
  assert.equal(r.erros.cpf, 'CPF inválido. Confira os números.');
  assert.equal(V.validarVisita({ ...ok, tipo: 'imob' }).primeiro, 'imobiliaria');
  assert.equal(V.validarVisita({ ...ok, tipo: 'imob', imobiliaria: 'Imob Ápice' }).ok, true);
  assert.equal(V.validarVisita({ ...ok, tipo: 'house', imobiliaria: '' }).ok, true);
  assert.equal(V.validarVisita({ ...ok, telefone: '98765-4321' }).primeiro, 'telefone');
  assert.equal(V.validarVisita({ ...ok, tipo: 'xyz' }).primeiro, 'tipo');
  assert.equal(V.validarVisita({ ...ok, hora: '9:5' }).primeiro, 'hora');
});

test('resumirVisita não leva CPF, telefone, nome completo nem gerente', () => {
  const r = V.resumirVisita({
    id: 'V1', data: '2026-10-09', hora: '14:35', empreendimento: 'Alta Vista Mangará', cidade: 'Campinas', tipo: 'imob',
    cliente: 'Mariana Souza Lima', cpf: '52998224725', telefone: '19987654321', imobiliaria: 'Imob Ápice', corretor: 'Rui', gerente: 'Gil'
  });
  assert.deepEqual(r, {
    id: 'V1', data: '2026-10-09', hora: '14:35', empreendimento: 'Alta Vista Mangará', tipo: 'imob',
    primeiroNome: 'Mariana', imobiliaria: 'Imob Ápice', corretor: 'Rui'
  });
});

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const V = require('../assets/visitas.js');

function carregar(arquivo, ctx) {
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '..', arquivo), 'utf8'), ctx);
  return ctx;
}
const gs = carregar('docs/apps-script-visitas.gs', {});
const plano = (x) => JSON.parse(JSON.stringify(x));

const HOJE = '2026-10-09';
const AGORA = 14 * 60 + 35;
const base = {
  empreendimento: 'Alta Vista Mangará', data: HOJE, hora: '14:35', tipo: 'esp',
  cliente: '  Mariana   Souza Lima ', cpf: '529.982.247-25', telefone: '(19) 98765-4321', corretor: 'Rui', gerente: ''
};
const recusa = (campo) => (e) => e.codigo === 'invalido' && e.campo === campo;

test('lista de empreendimentos do .gs bate com a do config.js', () => {
  const cfg = carregar('assets/config.js', { window: {} });
  assert.deepEqual(plano(gs.VISITAS_EMPREENDIMENTOS), V.listaEmpreendimentos(cfg.window.CITIES));
});

test('visValidar_ devolve a visita completa normalizada, com cidade do servidor e só dígitos', () => {
  const v = plano(gs.visValidar_({ ...base, cidade: 'Outra', imobiliaria: 'Ignorada' }, HOJE, AGORA));
  assert.deepEqual(v, {
    empreendimento: 'Alta Vista Mangará', cidade: 'Campinas', data: HOJE, hora: '14:35', tipo: 'esp',
    cliente: 'Mariana Souza Lima', cpf: '52998224725', telefone: '19987654321', imobiliaria: '', corretor: 'Rui', gerente: ''
  });
});

test('visValidar_ recusa empreendimento e tipo fora da lista', () => {
  assert.throws(() => gs.visValidar_({ ...base, empreendimento: 'Outro' }, HOJE, AGORA), recusa('empreendimento'));
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'xyz' }, HOJE, AGORA), recusa('tipo'));
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'constructor' }, HOJE, AGORA), recusa('tipo'));
});

test('visValidar_ limita data e horário como na v1', () => {
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-10-10' }, HOJE, AGORA), recusa('data'));
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-10-01' }, HOJE, AGORA), recusa('data'));
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-02-30' }, HOJE, AGORA), recusa('data'));
  assert.equal(gs.visValidar_({ ...base, data: '2026-10-02' }, HOJE, AGORA).data, '2026-10-02');
  assert.throws(() => gs.visValidar_({ ...base, hora: '25:00' }, HOJE, AGORA), recusa('hora'));
  assert.throws(() => gs.visValidar_({ ...base, hora: '14:41' }, HOJE, AGORA), recusa('hora'));
  assert.equal(gs.visValidar_({ ...base, hora: '14:40' }, HOJE, AGORA).hora, '14:40');
});

test('visValidar_ exige cliente, CPF válido, telefone válido e corretor', () => {
  assert.throws(() => gs.visValidar_({ ...base, cliente: '  ' }, HOJE, AGORA), recusa('cliente'));
  assert.throws(() => gs.visValidar_({ ...base, cpf: '529.982.247-24' }, HOJE, AGORA), recusa('cpf'));
  assert.throws(() => gs.visValidar_({ ...base, cpf: '111.111.111-11' }, HOJE, AGORA), recusa('cpf'));
  assert.throws(() => gs.visValidar_({ ...base, telefone: '98765-4321' }, HOJE, AGORA), recusa('telefone'));
  assert.throws(() => gs.visValidar_({ ...base, telefone: '(09) 98765-4321' }, HOJE, AGORA), recusa('telefone'));
  assert.throws(() => gs.visValidar_({ ...base, corretor: '' }, HOJE, AGORA), recusa('corretor'));
  assert.equal(gs.visValidar_({ ...base, telefone: '(19) 3245-8890' }, HOJE, AGORA).telefone, '1932458890');
  assert.equal(gs.visValidar_({ ...base, gerente: ' Gil  Souza ' }, HOJE, AGORA).gerente, 'Gil Souza');
});

test('visValidar_ exige imobiliária só no tipo imob', () => {
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'imob', imobiliaria: '   ' }, HOJE, AGORA), recusa('imobiliaria'));
  assert.equal(gs.visValidar_({ ...base, tipo: 'imob', imobiliaria: ' Imob   Ápice ' }, HOJE, AGORA).imobiliaria, 'Imob Ápice');
  assert.equal(gs.visValidar_({ ...base, tipo: 'house', imobiliaria: 'X' }, HOJE, AGORA).imobiliaria, '');
});

test('mensagens de erro de CPF e telefone não repetem o valor digitado', () => {
  assert.throws(
    () => gs.visValidar_({ ...base, cpf: '529.982.247-24' }, HOJE, AGORA),
    (e) => e.codigo === 'invalido' && !/529/.test(e.message)
  );
  assert.throws(
    () => gs.visValidar_({ ...base, telefone: '98765-4321' }, HOJE, AGORA),
    (e) => e.codigo === 'invalido' && !/98765/.test(e.message)
  );
});

test('visValidar_ limita cliente, gerente e corretor a 80 caracteres', () => {
  const longo = 'a'.repeat(120);
  const v = gs.visValidar_({ ...base, cliente: longo, gerente: longo, corretor: longo }, HOJE, AGORA);
  assert.equal(v.cliente.length, 80);
  assert.equal(v.gerente.length, 80);
  assert.equal(v.corretor.length, 80);
});

test('visValidar_ recusa hora sem zero à esquerda e aceita qualquer hora em data passada', () => {
  assert.throws(() => gs.visValidar_({ ...base, hora: '9:5' }, HOJE, AGORA), recusa('hora'));
  assert.equal(gs.visValidar_({ ...base, data: '2026-10-08', hora: '23:00' }, HOJE, AGORA).hora, '23:00');
});

test('CPF e telefone: mesmo resultado no cliente (visitas.js) e no servidor (.gs)', () => {
  const cpfs = ['52998224725', '529.982.247-25', '11144477735', '12345678909', '98765432100', '52998224724', '11111111111', '1234567890', '', 'abc'];
  cpfs.forEach((c) => assert.equal(gs.visCpfValido_(c), V.cpfValido(c), c));
  const tels = ['(19) 98765-4321', '1932458890', '987654321', '(09) 98765-4321', '199876543210', ''];
  tels.forEach((t) => assert.equal(gs.visTelefoneValido_(t), V.telefoneValido(t), t));
});

test('visNeutralizar_ e helpers de data', () => {
  assert.equal(gs.visNeutralizar_('=1+1'), "'=1+1");
  assert.equal(gs.visNeutralizar_('Imob'), 'Imob');
  assert.equal(gs.visSomarDias_('2026-10-01', -1), '2026-09-30');
  assert.equal(gs.visBrParaIso_('09/10/2026 14:35:00'), '2026-10-09');
  assert.equal(gs.visDataValida_('2026-02-29'), false);
  assert.equal(gs.visDataValida_('2026-02-28'), true);
  assert.equal(gs.visBrParaIso_(''), '');
});

function indice() { const ix = {}; gs.VIS_COLUNAS.forEach((n, i) => { ix[n] = i; }); return ix; }
function linha(campos) { return gs.VIS_COLUNAS.map((n) => (campos[n] !== undefined ? campos[n] : '')); }

test('VIS_COLUNAS na ordem da spec 13.2', () => {
  assert.deepEqual(plano(gs.VIS_COLUNAS), ['ID', 'Registrado em', 'Data', 'Horário', 'Empreendimento', 'Cidade', 'Tipo',
    'Nome do cliente', 'CPF', 'Telefone', 'Imobiliária', 'Corretor', 'Gerente de vendas', 'Excluída', 'Token']);
});

test('visDeLinha_ devolve a visita completa', () => {
  const l = linha({
    'ID': 'V1', 'Registrado em': '09/10/2026 14:35:00', 'Data': '09/10/2026', 'Horário': '14:30',
    'Empreendimento': 'Village Park', 'Cidade': 'Ribeirão Preto', 'Tipo': 'Imobiliária',
    'Nome do cliente': 'Mariana Souza', 'CPF': '52998224725', 'Telefone': '19987654321',
    'Imobiliária': 'Imob Ápice', 'Corretor': 'Rui', 'Gerente de vendas': 'Gil', 'Excluída': '0'
  });
  assert.deepEqual(plano(gs.visDeLinha_(l, indice())), {
    id: 'V1', data: '2026-10-09', hora: '14:30', empreendimento: 'Village Park', cidade: 'Ribeirão Preto', tipo: 'imob',
    cliente: 'Mariana Souza', cpf: '52998224725', telefone: '19987654321', imobiliaria: 'Imob Ápice', corretor: 'Rui', gerente: 'Gil'
  });
});

test('visResumo_ é igual ao resumo do cliente e não expõe dados pessoais', () => {
  const v = {
    id: 'V1', data: '2026-10-09', hora: '14:30', empreendimento: 'Village Park', cidade: 'Ribeirão Preto', tipo: 'imob',
    cliente: 'Mariana Souza', cpf: '52998224725', telefone: '19987654321', imobiliaria: 'Imob Ápice', corretor: 'Rui', gerente: 'Gil'
  };
  const r = plano(gs.visResumo_(v));
  assert.deepEqual(r, V.resumirVisita(v));
  const texto = JSON.stringify(r);
  ['52998224725', '19987654321', 'Souza', 'Gil'].forEach((s) => assert.ok(!texto.includes(s), s));
});

test('visCpfRepetido_: mesmo CPF, mesmo stand e mesma data, só linhas ativas', () => {
  const ix = indice();
  const linhas = [
    linha({ 'CPF': '52998224725', 'Empreendimento': 'Village Park', 'Data': '09/10/2026', 'Excluída': '0' }),
    linha({ 'CPF': '11144477735', 'Empreendimento': 'Village Park', 'Data': '09/10/2026', 'Excluída': '1' })
  ];
  const v = (cpf, emp, data) => ({ cpf, empreendimento: emp, data });
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('52998224725', 'Village Park', '2026-10-09')), true);
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('52998224725', 'Village Gaia', '2026-10-09')), false);
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('52998224725', 'Village Park', '2026-10-08')), false);
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('11144477735', 'Village Park', '2026-10-09')), false);
  assert.equal(gs.visCpfRepetido_([], ix, v('52998224725', 'Village Park', '2026-10-09')), false);
});

test('visSugestoes_ por coluna: agrupa, ignora excluídas e antigas, ordena', () => {
  const linhas = [
    linha({ 'Registrado em': '08/10/2026 10:00:00', 'Imobiliária': 'Imobiliária Ápice', 'Corretor': 'Rui', 'Excluída': '0' }),
    linha({ 'Registrado em': '08/10/2026 11:00:00', 'Imobiliária': 'Imobiliária Ápice', 'Corretor': 'rui', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:00:00', 'Imobiliária': 'imobiliaria apice', 'Corretor': 'Bia', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:30:00', 'Imobiliária': 'Beta Imóveis', 'Corretor': 'Zeca', 'Excluída': '1' }),
    linha({ 'Registrado em': '01/01/2026 09:00:00', 'Imobiliária': 'Antiga', 'Corretor': 'Antigo', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:50:00', 'Imobiliária': 'constructor', 'Corretor': '__proto__', 'Excluída': '0' })
  ];
  assert.deepEqual(plano(gs.visSugestoes_(linhas, indice(), '2026-07-11', 'Imobiliária')), ['constructor', 'Imobiliária Ápice']);
  assert.deepEqual(plano(gs.visSugestoes_(linhas, indice(), '2026-07-11', 'Corretor')), ['__proto__', 'Bia', 'Rui']);
  assert.equal(({}).qtd, undefined);
});

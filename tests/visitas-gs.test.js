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
const base = { empreendimento: 'Alta Vista Mangará', data: HOJE, hora: '14:35', tipo: 'esp' };
const recusa = (campo) => (e) => e.codigo === 'invalido' && e.campo === campo;

test('lista de empreendimentos do .gs bate com a do config.js', () => {
  const cfg = carregar('assets/config.js', { window: {} });
  assert.deepEqual(plano(gs.VISITAS_EMPREENDIMENTOS), V.listaEmpreendimentos(cfg.window.CITIES));
});

test('visValidar_ aceita visita espontânea e define a cidade pelo servidor', () => {
  const v = plano(gs.visValidar_({ ...base, cidade: 'Outra', corretorHouse: 'Ana' }, HOJE, AGORA));
  assert.deepEqual(v, {
    empreendimento: 'Alta Vista Mangará', cidade: 'Campinas', data: HOJE, hora: '14:35', tipo: 'esp',
    corretorHouse: '', imobiliaria: '', corretorImob: ''
  });
});

test('visValidar_ recusa empreendimento e tipo fora da lista', () => {
  assert.throws(() => gs.visValidar_({ ...base, empreendimento: 'Outro' }, HOJE, AGORA), recusa('empreendimento'));
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'xyz' }, HOJE, AGORA), recusa('tipo'));
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'constructor' }, HOJE, AGORA), recusa('tipo'));
});

test('visValidar_ limita a data entre hoje e 7 dias atrás', () => {
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-10-10' }, HOJE, AGORA), recusa('data'));
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-10-01' }, HOJE, AGORA), recusa('data'));
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-02-30' }, HOJE, AGORA), recusa('data'));
  assert.equal(gs.visValidar_({ ...base, data: '2026-10-02' }, HOJE, AGORA).data, '2026-10-02');
});

test('visValidar_ recusa horário inválido ou no futuro (tolerância de 5 min)', () => {
  assert.throws(() => gs.visValidar_({ ...base, hora: '25:00' }, HOJE, AGORA), recusa('hora'));
  assert.throws(() => gs.visValidar_({ ...base, hora: '9:5' }, HOJE, AGORA), recusa('hora'));
  assert.throws(() => gs.visValidar_({ ...base, hora: '14:41' }, HOJE, AGORA), recusa('hora'));
  assert.equal(gs.visValidar_({ ...base, hora: '14:40' }, HOJE, AGORA).hora, '14:40');
  assert.equal(gs.visValidar_({ ...base, data: '2026-10-08', hora: '23:00' }, HOJE, AGORA).hora, '23:00');
});

test('visValidar_ exige imobiliária e normaliza os textos', () => {
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'imob', imobiliaria: '   ' }, HOJE, AGORA), recusa('imobiliaria'));
  const v = gs.visValidar_({ ...base, tipo: 'imob', imobiliaria: '  Imob   Ápice ', corretorImob: 'x'.repeat(100) }, HOJE, AGORA);
  assert.equal(v.imobiliaria, 'Imob Ápice');
  assert.equal(v.corretorImob.length, 80);
  assert.equal(gs.visValidar_({ ...base, tipo: 'house' }, HOJE, AGORA).corretorHouse, '');
});

test('visNeutralizar_ e helpers de data', () => {
  assert.equal(gs.visNeutralizar_('=1+1'), "'=1+1");
  assert.equal(gs.visNeutralizar_('Imob'), 'Imob');
  assert.equal(gs.visSomarDias_('2026-10-01', -1), '2026-09-30');
  assert.equal(gs.visBrParaIso_('09/10/2026 14:35:00'), '2026-10-09');
  assert.equal(gs.visBrParaIso_(''), '');
  assert.equal(gs.visDataValida_('2026-02-28'), true);
  assert.equal(gs.visDataValida_('2026-02-29'), false);
});

function indice() { const ix = {}; gs.VIS_COLUNAS.forEach((n, i) => { ix[n] = i; }); return ix; }
function linha(campos) { return gs.VIS_COLUNAS.map((n) => (campos[n] !== undefined ? campos[n] : '')); }

test('visDeLinha_ converte a linha da planilha no formato da API', () => {
  const l = linha({
    'ID': 'V1', 'Registrado em': '09/10/2026 14:35:00', 'Data': '09/10/2026', 'Horário': '14:30',
    'Empreendimento': 'Village Park', 'Cidade': 'Ribeirão Preto', 'Tipo': 'Imobiliária',
    'Imobiliária': 'Imob Ápice', 'Corretor imobiliária': 'Rui', 'Excluída': '0'
  });
  assert.deepEqual(plano(gs.visDeLinha_(l, indice())), {
    id: 'V1', data: '2026-10-09', hora: '14:30', empreendimento: 'Village Park', cidade: 'Ribeirão Preto',
    tipo: 'imob', corretorHouse: '', imobiliaria: 'Imob Ápice', corretorImob: 'Rui'
  });
});

test('visSugestoes_ agrupa, ignora excluídas e antigas, ordena', () => {
  const linhas = [
    linha({ 'Registrado em': '08/10/2026 10:00:00', 'Imobiliária': 'Imobiliária Ápice', 'Excluída': '0' }),
    linha({ 'Registrado em': '08/10/2026 11:00:00', 'Imobiliária': 'Imobiliária Ápice', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:00:00', 'Imobiliária': 'imobiliaria apice', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:30:00', 'Imobiliária': 'Beta Imóveis', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:40:00', 'Imobiliária': 'Excluída Ltda', 'Excluída': '1' }),
    linha({ 'Registrado em': '01/01/2026 09:00:00', 'Imobiliária': 'Antiga', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:50:00', 'Imobiliária': '', 'Excluída': '0' })
  ];
  assert.deepEqual(plano(gs.visSugestoes_(linhas, indice(), '2026-07-11')), ['Beta Imóveis', 'Imobiliária Ápice']);
});

test('visSugestoes_ trata constructor e __proto__ como nomes normais', () => {
  const linhas = ['constructor', '__proto__', 'Beta'].map((n) =>
    linha({ 'Registrado em': '09/10/2026 09:00:00', 'Imobiliária': n, 'Excluída': '0' }));
  assert.deepEqual(plano(gs.visSugestoes_(linhas, indice(), '2026-07-11')).sort(), ['Beta', '__proto__', 'constructor']);
  assert.equal(({}).constructor, Object);
});

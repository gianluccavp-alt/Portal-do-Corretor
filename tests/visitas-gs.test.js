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
const crypto = require('node:crypto');
const assinado = (buf) => Array.from(buf, (b) => (b > 127 ? b - 256 : b));
const UtilitiesFalso = {
  DigestAlgorithm: { SHA_256: 'sha256' },
  Charset: { UTF_8: 'utf8' },
  computeDigest: (alg, texto) => assinado(crypto.createHash('sha256').update(String(texto), 'utf8').digest()),
  computeHmacSha256Signature: (valor, chave) => assinado(crypto.createHmac('sha256', chave).update(valor, 'utf8').digest()),
  base64EncodeWebSafe: (bytes) => Buffer.from(bytes.map((b) => b & 255)).toString('base64').replace(/\+/g, '-').replace(/\//g, '_'),
  getUuid: () => crypto.randomUUID()
};
const gs = carregar('docs/apps-script-visitas.gs', { Utilities: UtilitiesFalso });
function cacheFalso() {
  const m = new Map();
  return { get: (k) => (m.has(k) ? m.get(k) : null), put: (k, v) => { m.set(k, String(v)); }, remove: (k) => { m.delete(k); } };
}
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

test('visStackSemMensagem_ tira a linha da mensagem do stack', () => {
  const stack = 'SyntaxError: Unexpected token in JSON at position 5: {"cpf":"52998224725"\n    at JSON.parse (<anonymous>)\n    at doPost (Codigo:80:20)';
  const limpo = gs.visStackSemMensagem_(stack);
  assert.ok(!limpo.includes('52998224725'));
  assert.equal(limpo, '    at JSON.parse (<anonymous>)\n    at doPost (Codigo:80:20)');
  assert.equal(gs.visStackSemMensagem_(undefined), '');
});

test('usuário e senha: mesmo resultado no cliente e no servidor', () => {
  const usuarios = ['ana', 'maria.silva', 'recep_2', '3ab', 'ab', '-abc', 'joão', 'Maria', '', 'a'.repeat(30), 'a'.repeat(31)];
  usuarios.forEach((u) => assert.equal(gs.visUsuarioValido_(u), V.usuarioValido(u), u));
  assert.equal(gs.visNormUsuario_('  Maria.Silva '), V.normalizarUsuario('  Maria.Silva '));
  const senhas = [['12345678', 'ana'], ['1234567', 'ana'], ['x'.repeat(73), 'ana'], ['Maria.Silva', 'maria.silva'], [undefined, 'ana']];
  senhas.forEach(([s, u]) => assert.equal(gs.visValidarSenha_(s, u), V.validarSenha(s, u), String(s)));
});

test('visValidarCadastro_ normaliza e recusa com o campo certo', () => {
  assert.deepEqual(plano(gs.visValidarCadastro_({ nome: ' Maria  Silva ', usuario: ' Maria.Silva ', senha: 'segredo123' })),
    { nome: 'Maria Silva', usuario: 'maria.silva', senha: 'segredo123' });
  assert.throws(() => gs.visValidarCadastro_({ nome: ' ', usuario: 'ana', senha: 'segredo123' }), recusa('nome'));
  assert.throws(() => gs.visValidarCadastro_({ nome: 'Ana', usuario: 'a b', senha: 'segredo123' }), recusa('usuario'));
  assert.throws(() => gs.visValidarCadastro_({ nome: 'Ana', usuario: 'ana', senha: '123' }), recusa('senha'));
});

test('visHashSenha_: determinístico por sal, diferente com outro sal ou outra senha, sem a senha em claro', () => {
  const h = gs.visHashSenha_('segredo123', 'sal-1');
  assert.match(h, /^[0-9a-f]{64}$/);
  assert.equal(gs.visHashSenha_('segredo123', 'sal-1'), h);
  assert.notEqual(gs.visHashSenha_('segredo123', 'sal-2'), h);
  assert.notEqual(gs.visHashSenha_('segredo124', 'sal-1'), h);
  let esperado = crypto.createHash('sha256').update('sal-1segredo123').digest('hex');
  for (let i = 1; i < 1000; i++) esperado = crypto.createHash('sha256').update(esperado + 'sal-1').digest('hex');
  assert.equal(h, esperado);
});

test('visExpiraMeiaNoite_: próxima meia-noite de Brasília (03h UTC)', () => {
  assert.equal(gs.visExpiraMeiaNoite_(Date.UTC(2026, 9, 10, 2, 59)), Date.UTC(2026, 9, 10, 3, 0));
  assert.equal(gs.visExpiraMeiaNoite_(Date.UTC(2026, 9, 10, 3, 0)), Date.UTC(2026, 9, 11, 3, 0));
  assert.equal(gs.visExpiraMeiaNoite_(Date.UTC(2026, 9, 10, 15, 0)), Date.UTC(2026, 9, 11, 3, 0));
  assert.equal(gs.visExpiraMeiaNoite_(Date.UTC(2026, 11, 31, 20, 0)), Date.UTC(2027, 0, 1, 3, 0));
});

test('token de sessão: válido, vencido, alterado, outro usuário, hash trocado, segredo errado', () => {
  const agora = Date.UTC(2026, 9, 10, 15, 0);
  const conta = { usuario: 'maria.silva', hash: 'a'.repeat(64), situacao: 'ativa', temporaria: false };
  const t = gs.visCriarToken_(conta.usuario, conta.hash, agora, 'segredo');
  assert.equal(t.expira, Date.UTC(2026, 9, 11, 3, 0));
  assert.ok(t.token.startsWith('maria.silva.' + t.expira + '.'));
  assert.deepEqual(plano(gs.visLerToken_(t.token)).usuario, 'maria.silva');
  assert.equal(gs.visConferirToken_(t.token, conta, agora, 'segredo'), true);
  assert.equal(gs.visConferirToken_(t.token, conta, t.expira, 'segredo'), false);
  assert.equal(gs.visConferirToken_(t.token, conta, agora, 'outro'), false);
  assert.equal(gs.visConferirToken_(t.token.slice(0, -2) + 'xx', conta, agora, 'segredo'), false);
  const futuro = t.token.replace('.' + t.expira + '.', '.' + (t.expira + 86400000) + '.');
  assert.equal(gs.visConferirToken_(futuro, conta, agora, 'segredo'), false);
  assert.equal(gs.visConferirToken_(t.token, { ...conta, usuario: 'outra' }, agora, 'segredo'), false);
  assert.equal(gs.visConferirToken_(t.token, { ...conta, hash: 'b'.repeat(64) }, agora, 'segredo'), false);
  assert.equal(gs.visConferirToken_('lixo', conta, agora, 'segredo'), false);
  assert.equal(gs.visConferirToken_(undefined, conta, agora, 'segredo'), false);
  assert.equal(gs.visLerToken_('ab.123.x'), null);
  assert.equal(gs.visLerToken_('ana.12a.x'), null);
  assert.equal(gs.visLerToken_('ana.123.'), null);
});

test('visSessaoOk_ exige conta ativa e, fora da troca de senha, sem senha temporária', () => {
  const agora = Date.UTC(2026, 9, 10, 15, 0);
  const conta = { usuario: 'ana', hash: 'c'.repeat(64), situacao: 'ativa', temporaria: false };
  const { token } = gs.visCriarToken_('ana', conta.hash, agora, 's');
  assert.equal(gs.visSessaoOk_(token, conta, agora, 's', false), true);
  assert.equal(gs.visSessaoOk_(token, { ...conta, situacao: 'desativada' }, agora, 's', false), false);
  assert.equal(gs.visSessaoOk_(token, { ...conta, situacao: 'pendente' }, agora, 's', true), false);
  assert.equal(gs.visSessaoOk_(token, { ...conta, temporaria: true }, agora, 's', false), false);
  assert.equal(gs.visSessaoOk_(token, { ...conta, temporaria: true }, agora, 's', true), true);
  assert.equal(gs.visSessaoOk_(token, null, agora, 's', true), false);
});

test('visIguais_', () => {
  assert.equal(gs.visIguais_('abc', 'abc'), true);
  assert.equal(gs.visIguais_('abc', 'abd'), false);
  assert.equal(gs.visIguais_('abc', 'abcd'), false);
  assert.equal(gs.visIguais_('', ''), true);
});

test('visSenhaTemporaria_: 3 grupos de 3, sem caracteres ambíguos', () => {
  const s = gs.visSenhaTemporaria_([0, 1, 2, 55, 56, 100, 200, 254, 255]);
  assert.match(s, /^[A-Za-z0-9]{3}-[A-Za-z0-9]{3}-[A-Za-z0-9]{3}$/);
  for (let i = 0; i < 50; i++) {
    const bytes = Array.from(crypto.randomBytes(9));
    assert.doesNotMatch(gs.visSenhaTemporaria_(bytes), /[0O1lIo]/);
  }
  assert.equal(gs.visSenhaTemporaria_([0, 0, 0, 0, 0, 0, 0, 0, 0]), 'aaa-aaa-aaa');
  assert.equal(V.validarSenha(s, 'ana'), '');
});

function indiceContas() { const ix = {}; gs.VIS_COLUNAS_CONTAS.forEach((n, i) => { ix[n] = i; }); return ix; }
function linhaConta(c) { return gs.VIS_COLUNAS_CONTAS.map((n) => (c[n] !== undefined ? c[n] : '')); }

test('VIS_COLUNAS_CONTAS, visContaDeLinha_ e visContaPublica_ (sem hash nem sal)', () => {
  assert.deepEqual(plano(gs.VIS_COLUNAS_CONTAS), ['Usuário', 'Nome', 'Situação', 'Hash', 'Sal', 'Temporária', 'Criado em', 'Aprovado em', 'Último acesso']);
  const l = linhaConta({
    'Usuário': ' ana ', 'Nome': 'Ana Lima', 'Situação': 'ativa', 'Hash': 'h'.repeat(64), 'Sal': 's1', 'Temporária': 'sim',
    'Criado em': '01/10/2026 09:00:00', 'Aprovado em': '01/10/2026 10:00:00', 'Último acesso': '10/10/2026 08:02:00'
  });
  const c = plano(gs.visContaDeLinha_(l, indiceContas()));
  assert.deepEqual(c, {
    usuario: 'ana', nome: 'Ana Lima', situacao: 'ativa', hash: 'h'.repeat(64), sal: 's1', temporaria: true,
    criadoEm: '01/10/2026 09:00:00', aprovadoEm: '01/10/2026 10:00:00', ultimoAcesso: '10/10/2026 08:02:00'
  });
  const p = plano(gs.visContaPublica_(c, 12));
  assert.deepEqual(p, { usuario: 'ana', nome: 'Ana Lima', situacao: 'ativa', temporaria: true, criadoEm: '01/10/2026 09:00:00', ultimoAcesso: '10/10/2026 08:02:00', visitas30: 12 });
  assert.ok(!JSON.stringify(p).includes('h'.repeat(64)));
  assert.equal(gs.visContaPublica_(c).visitas30, 0);
  const linhas = [linhaConta({ 'Situação': 'pendente' }), linhaConta({ 'Situação': 'ativa' }), linhaConta({ 'Situação': ' pendente ' })];
  assert.equal(gs.visContarPendentes_(linhas, indiceContas()), 2);
});

test('bloqueio: 5 falhas bloqueiam, login certo limpa', () => {
  const cache = cacheFalso();
  for (let i = 1; i <= 4; i++) {
    assert.equal(gs.visRegistrarFalha_(cache, 'ana'), i);
    assert.equal(gs.visBloqueado_(cache, 'ana'), false);
  }
  assert.equal(gs.visRegistrarFalha_(cache, 'ana'), 5);
  assert.equal(gs.visBloqueado_(cache, 'ana'), true);
  assert.equal(gs.visBloqueado_(cache, 'bia'), false);
  gs.visLimparFalhas_(cache, 'ana');
  assert.equal(gs.visBloqueado_(cache, 'ana'), false);
});

test('roteador: ações do comercial exigem a senha antes de qualquer leitura', () => {
  const props = { getProperty: () => 'senha-forte-123' };
  const ctx = carregar('docs/apps-script-visitas.gs', {
    Utilities: UtilitiesFalso,
    PropertiesService: { getScriptProperties: () => props },
    SpreadsheetApp: { getActiveSpreadsheet: () => { throw new Error('não devia ler a planilha'); } }
  });
  ['listar', 'contas', 'aprovar', 'recusar', 'desativar', 'reativar', 'redefinirSenha'].forEach((acao) => {
    assert.throws(() => ctx.visRoteador_({ acao, senha: 'errada', usuario: 'ana' }), (e) => e.codigo === 'senha', acao);
  });
});

const test = require('node:test');
const assert = require('node:assert/strict');
const F = require('../assets/match-fluxo.js');

const HOJE = new Date(2026, 9, 30);

test('dataNascimento aceita data real e recusa inexistente/futura/ano curto', () => {
  assert.equal(F.dataNascimento('14', '03', '1993').getTime(), new Date(1993, 2, 14).getTime());
  assert.equal(F.dataNascimento('31', '02', '1990'), null);
  assert.equal(F.dataNascimento('14', '03', '93'), null);
  assert.equal(F.dataNascimento('', '03', '1993'), null);
});
test('validarEtapa nascimento', () => {
  const r = Object.assign(F.respostasIniciais('Ribeirão Preto'), { renda: 4200 });
  assert.match(F.validarEtapa('nascimento', Object.assign({}, r, { dia: '31', mes: '02', ano: '1990' }), HOJE), /data de nascimento/i);
  assert.match(F.validarEtapa('nascimento', Object.assign({}, r, { dia: '01', mes: '01', ano: '2027' }), HOJE), /futuro/i);
  assert.match(F.validarEtapa('nascimento', Object.assign({}, r, { dia: '01', mes: '01', ano: '1950' }), HOJE), /70 anos/);
  assert.equal(F.validarEtapa('nascimento', Object.assign({}, r, { dia: '14', mes: '03', ano: '1993' }), HOJE), null);
});
test('validarEtapa renda e onde', () => {
  const r = F.respostasIniciais('Ribeirão Preto');
  assert.equal(F.validarEtapa('renda', r, HOJE), 'Informe a renda bruta do cliente.');
  assert.equal(F.validarEtapa('renda', Object.assign({}, r, { renda: 4200 }), HOJE), null);
  assert.equal(F.validarEtapa('onde', Object.assign({}, r, { cidade: '' }), HOJE), 'Escolha a cidade.');
});
test('perguntasPerfil esconde dependente e subsidio quando nao ha subsidio', () => {
  const r = Object.assign(F.respostasIniciais('Ribeirão Preto'), { renda: 3500 });   /* teto do subsidio: R$ 4.000 */
  assert.deepEqual(F.perguntasPerfil(r), ['fgts', 'possuiImovel', 'fatorSocial', 'subsidioAnterior']);
  assert.deepEqual(F.perguntasPerfil(Object.assign({}, r, { renda: 9000 })), ['fgts', 'possuiImovel']);
  assert.deepEqual(F.perguntasPerfil(Object.assign({}, r, { possuiImovel: true })), ['fgts', 'possuiImovel']);
});
test('cliente zera respostas que nao se aplicam', () => {
  const r = Object.assign(F.respostasIniciais('Ribeirão Preto'), { renda: 9000, fatorSocial: true, subsidioAnterior: true, dia: '14', mes: '03', ano: '1993' });
  const c = F.cliente(r);
  assert.equal(c.fatorSocial, false); assert.equal(c.subsidioAnterior, false);
  assert.equal(c.nascimento.getTime(), new Date(1993, 2, 14).getTime());
});
test('resumoEtapa monta a linha da trilha', () => {
  const ctx = { emps: [{ id: 'park', nome: 'Village Park', cidade: 'Ribeirão Preto' }], nomePolitica: () => 'Ouro', hoje: HOJE };
  const r = Object.assign(F.respostasIniciais('Ribeirão Preto'), { empId: 'park', renda: 3500, dia: '14', mes: '03', ano: '1993' });
  assert.equal(F.resumoEtapa('onde', r, ctx), 'Village Park');
  assert.equal(F.resumoEtapa('onde', Object.assign({}, r, { empId: '' }), ctx), 'Ribeirão Preto · todos');
  assert.equal(F.resumoEtapa('renda', r, ctx), 'R$ 3.500/mês');
  assert.equal(F.resumoEtapa('ato', r, ctx), 'Padrão · R$ 2.500');
  assert.equal(F.resumoEtapa('ato', Object.assign({}, r, { empId: '' }), ctx), 'Padrão de cada empreendimento');
  assert.equal(F.resumoEtapa('ato', Object.assign({}, r, { ato: 5000 }), ctx), 'R$ 5.000');
  assert.equal(F.resumoEtapa('nascimento', r, ctx), '14/03/1993 · 33 anos');
  assert.equal(F.resumoEtapa('perfil', r, ctx), 'FGTS 3 anos · Sem imóvel · Sem dependente');
  assert.equal(F.resumoEtapa('politica', r, ctx), 'Ouro');
});
test('textoAtoPadrao', () => {
  assert.equal(F.textoAtoPadrao('ipiranga'), 'R$ 1.500');
  assert.equal(F.textoAtoPadrao('park'), 'R$ 2.500');
  assert.equal(F.textoAtoPadrao(''), 'o padrão de cada empreendimento');
});
test('melhorMatch e ordenar', () => {
  const L = [
    { codigo: 'B', parcelaFin: 1200, parcelaPS: 500, crTotal: 0.30, andar: 2 },
    { codigo: 'A', parcelaFin: 1180, parcelaPS: 412, crTotal: 0.28, andar: 3 },
    { codigo: 'C', parcelaFin: 1100, parcelaPS: 600, crTotal: 0.29, andar: 10 }
  ];
  assert.equal(F.mensal(L[1]), 1592);
  assert.equal(F.melhorMatch(L).codigo, 'A');
  assert.equal(F.melhorMatch([]), null);
  assert.deepEqual(F.ordenar(L, 'parcela').map((l) => l.codigo), ['A', 'C', 'B']);
  assert.deepEqual(F.ordenar(L, 'cr').map((l) => l.codigo), ['A', 'C', 'B']);
  assert.deepEqual(F.ordenar(L, 'andar').map((l) => l.codigo), ['C', 'A', 'B']);
  assert.equal(L[0].codigo, 'B');
});
test('textoPS, textoContagem e fotoDe', () => {
  assert.equal(F.textoPS({ parcelaPS: 0, prazoPS: 84 }), 'Sem Pro Soluto');
  assert.equal(F.textoPS({ parcelaPS: 412, prazoPS: 84 }), 'R$ 412 × 84');
  assert.equal(F.textoContagem(1), '1 unidade cabe');
  assert.equal(F.textoContagem(9), '9 unidades cabem');
  assert.equal(F.fotoDe({ sheetName: 'Reserva Direcional Jardim Botânico' }), 'assets/img/cards/reserva-direcional-jardim-botanico@480.webp');
});

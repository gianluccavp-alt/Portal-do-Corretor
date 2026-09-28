const test = require('node:test');
const assert = require('node:assert/strict');
const P = require('../assets/pendencias.js');

function venda(extra) {
  return Object.assign({
    id: 'OP-000001', statusAC: 'Análise aprovada', fid: '700001',
    pcvAssinadoEm: '10/09/2026', boletoPago: true, cartaoPago: false
  }, extra);
}
const chaves = (v) => P.derivarPendencias(v).map((p) => p.chave);

test('venda sem nada pendente', () => {
  assert.deepEqual(P.derivarPendencias(venda()), []);
});

test('AC não aprovada: rótulo e estilo por status', () => {
  const casos = [
    ['Análise reprovada', 'AC reprovada', 'err'],
    ['Enviado para análise', 'AC em análise', 'warn'],
    ['Rascunho', 'AC não enviada', 'err'],
    ['', 'AC não enviada', 'err'],
    ['Aguardando banco', 'Aguardando banco', 'warn']
  ];
  for (const [statusAC, rotulo, estilo] of casos) {
    assert.deepEqual(P.derivarPendencias(venda({ statusAC })), [{ chave: 'ac', rotulo, estilo }], statusAC);
  }
});

test('AC aprovada ignora acento e caixa', () => {
  assert.deepEqual(chaves(venda({ statusAC: 'ANALISE APROVADA' })), []);
});

test('FID e PCV vazios viram pendência', () => {
  assert.deepEqual(chaves(venda({ fid: '' })), ['fid']);
  assert.deepEqual(chaves(venda({ fid: '   ' })), ['fid']);
  assert.deepEqual(chaves(venda({ fid: null })), ['fid']);
  assert.deepEqual(chaves(venda({ pcvAssinadoEm: '' })), ['pcv']);
});

test('ato: basta boleto/PIX ou cartão pago', () => {
  assert.deepEqual(chaves(venda({ boletoPago: true, cartaoPago: false })), []);
  assert.deepEqual(chaves(venda({ boletoPago: false, cartaoPago: true })), []);
  assert.deepEqual(chaves(venda({ boletoPago: true, cartaoPago: true })), []);
  assert.deepEqual(chaves(venda({ boletoPago: false, cartaoPago: false })), ['ato']);
});

test('ordem dos chips: ac, fid, ato, pcv', () => {
  const v = venda({ statusAC: '', fid: '', boletoPago: false, cartaoPago: false, pcvAssinadoEm: '' });
  assert.deepEqual(chaves(v), ['ac', 'fid', 'ato', 'pcv']);
});

test('statusAcBadge', () => {
  const casos = [
    ['Análise aprovada', 'Aprovada', 'ok'],
    ['Análise reprovada', 'Reprovada', 'err'],
    ['Enviado para análise', 'Em análise', 'neu'],
    ['Rascunho', 'Rascunho', 'neu'],
    ['', 'Sem análise', 'neu'],
    ['Outro status', 'Outro status', 'neu']
  ];
  for (const [statusAC, rotulo, estilo] of casos) {
    assert.deepEqual(P.statusAcBadge(venda({ statusAC })), { rotulo, estilo }, statusAC);
  }
});

test('checklist com pendências', () => {
  const itens = P.checklist(venda({ statusAC: 'Análise reprovada', fid: '', boletoPago: false, cartaoPago: false }));
  assert.deepEqual(itens.map((i) => [i.chave, i.ok]), [['ac', false], ['fid', false], ['ato', false], ['pcv', true]]);
  assert.equal(itens[0].titulo, 'AC reprovada');
  assert.equal(itens[0].estilo, 'err');
  assert.equal(itens[0].detalhe, 'Status AC: Análise reprovada');
  assert.equal(itens[1].detalhe, 'Nenhum FID registrado no Salesforce');
  assert.equal(itens[2].detalhe, 'Boleto/PIX: Não · Cartão: Não');
  assert.equal(itens[3].titulo, 'PCV assinado');
  assert.equal(itens[3].detalhe, 'Cliente assinou em 10/09/2026');
});

test('checklist sem pendências', () => {
  const itens = P.checklist(venda());
  assert.ok(itens.every((i) => i.ok && i.estilo === 'ok'));
  assert.equal(itens[0].titulo, 'AC aprovada');
  assert.equal(itens[1].titulo, 'FID 700001');
  assert.equal(itens[2].titulo, 'Ato pago');
  assert.equal(itens[2].detalhe, 'Boleto/PIX: Sim · Cartão: Não');
});

test('checklist com AC vazia diz "sem análise"', () => {
  assert.equal(P.checklist(venda({ statusAC: '' }))[0].detalhe, 'Status AC: sem análise');
});

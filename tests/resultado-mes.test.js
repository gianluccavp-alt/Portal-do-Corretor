const test = require('node:test');
const assert = require('node:assert/strict');
const R = require('../assets/resultado-mes.js');

const CAB = ['Data da venda', 'Fase', 'Identificador', 'Empreendimento', 'Nome da oportunidade', 'Imobiliária',
  'Contato Corretor Proprietario', 'FID', 'Cliente assinou PCV', 'Data Confirmação Venda 2.0', 'Boleto/PIX Pago',
  'Cartão Pago', 'Valor Real de Venda', 'Ranking', 'Venda Comercial?', 'Venda facilitada', 'Origem da Conta'];

function linha(p) {
  return [p.venda, p.fase || 'Proposta Aprovada', p.un || 'BL01-0101', p.emp || 'Village Gaia',
    'OP-' + p.op + ' - Cliente: TESTE', p.imob || 'Equipe A', 'Corretor', '', p.pcv || '', p.conf || '',
    p.boleto || 'Não', p.cartao || 'Não', p.valor || 100000, '', p.com !== false, !!p.fac, ''];
}
const aba = (linhas) => ({ cabecalho: CAB, linhas: linhas.map(linha) });

test('mes conta pela confirmacao; sem ela, pela data da venda', () => {
  const abas = [aba([
    { op: 1, venda: '2026-10-28', conf: '2026-11-03', com: false, fac: true },
    { op: 2, venda: '2026-11-10', com: false, fac: true },
    { op: 3, venda: '2026-11-05', conf: '2026-12-01', com: false, fac: true }
  ])];
  assert.deepEqual(R.vendasDoMes(abas, '2026-11').map((v) => v.op).sort(), ['OP-1', 'OP-2']);
  assert.deepEqual(R.vendasDoMes(abas, '2026-12').map((v) => v.op), ['OP-3']);
});

test('aba 2.0 completa a confirmacao e o mes muda', () => {
  const abas = [aba([{ op: 9, venda: '2026-10-30', com: false, fac: true }]),
    aba([{ op: 9, venda: '2026-10-30', conf: '2026-11-02', com: false, fac: true }])];
  const nov = R.vendasDoMes(abas, '2026-11');
  assert.equal(nov.length, 1);
  assert.equal(nov[0].confirmada, true);
  assert.equal(R.vendasDoMes(abas, '2026-10').length, 0);
});

test('OP repetida no relatorio conta uma vez', () => {
  const abas = [aba([{ op: 5, venda: '2026-11-10' }, { op: 5, venda: '2026-11-10' }])];
  assert.equal(R.vendasDoMes(abas, '2026-11').length, 1);
});

test('fases antes de Proposta Aprovada e perdidas ficam fora', () => {
  for (const f of ['Em atendimento', 'Visita Agendada', 'Em elaboração', 'Proposta Reprovada', 'Fechado e perdido']) assert.equal(R.faseConta(f), false, f);
  for (const f of ['Proposta Aprovada', 'Aprovado SAFI', 'Em cessão', 'Contrato comunicado', 'Fechado e ganho']) assert.equal(R.faseConta(f), true, f);
});

test('comercial + facilitada conta como comercial', () => {
  const [v] = R.vendasDoMes([aba([{ op: 7, venda: '2026-11-01', com: true, fac: true }])], '2026-11');
  assert.equal(v.tipo, 'comercial');
  assert.equal(v.virouComercial, true);
});

test('resumo: matriz, oficial e sinal', () => {
  const abas = [aba([
    { op: 1, venda: '2026-11-01', conf: '2026-11-02', fase: 'Fechado e ganho', valor: 300000 },
    { op: 2, venda: '2026-11-01', fase: 'Proposta Aprovada', valor: 200000, pcv: '2026-11-01', cartao: 'Sim' },
    { op: 3, venda: '2026-11-01', conf: '2026-11-04', com: false, fac: true, valor: 100000 },
    { op: 4, venda: '2026-11-03', com: false, fac: true, valor: 100000, pcv: '2026-11-03' },
    { op: 5, venda: '2026-11-03', com: false, fac: true, valor: 100000, boleto: 'Sim' },
    { op: 6, venda: '2026-11-03', com: false, fac: true, valor: 100000 }
  ])];
  const r = R.resumo(R.vendasDoMes(abas, '2026-11'));
  assert.equal(r.total.n, 6);
  assert.equal(r.total.vgv, 900000);
  assert.equal(r.oficial.n, 2);
  assert.equal(r.matriz.comercial.ok.n, 1);
  assert.equal(r.matriz.comercial.sem.n, 1);
  assert.equal(r.matriz.facilitada.ok.n, 1);
  assert.equal(r.matriz.facilitada.sem.n, 3);
  assert.deepEqual(r.sinal, { pcvESinal: 1, soPcv: 1, soSinal: 1, nenhum: 1, total: 4 });
  assert.equal(r.empreendimentos[0].n, 6);
});

test('le datas no formato brasileiro e booleanos em texto', () => {
  const v = R.lerLinha(CAB, ['23/11/2026', 'Proposta Aprovada', 'X', 'E', 'OP-1', '', '', '', '', '', 'Sim', 'Não', '1.234,50', '', 'FALSE', 'TRUE', '']);
  assert.equal(v.venda, '2026-11-23');
  assert.equal(v.tipo, 'facilitada');
  assert.equal(v.boleto, true);
  assert.equal(v.valor, 1234.5);
});

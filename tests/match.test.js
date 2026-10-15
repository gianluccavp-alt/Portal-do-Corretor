const test = require('node:test');
const assert = require('node:assert/strict');
const Match = require('../assets/match.js');

const HOJE = new Date(2026, 9, 15);
const NASC = new Date(1990, 2, 15);              /* 36 anos */
const CLIENTE = { renda: 4000, nascimento: NASC, fgts: true };

const EMP = (id, cidade, extra) => Object.assign({ id, nome: 'Emp ' + id, cidade, inicioObra: '2026-01-01',
  entrega: '2028-12-31', parcMin: 150 }, extra || {});
const UN = (codigo, avaliacao, associativo, extra) => Object.assign({ codigo, torre: parseInt(codigo.slice(2, 4), 10),
  tipoLabel: '2 dorms', areaPriv: 42, avaliacao, associativo }, extra || {});

test('numero entende formatos brasileiros', () => {
  assert.equal(Match.numero('3.500,00'), 3500);
  assert.equal(Match.numero('R$ 3.500'), 3500);
  assert.equal(Match.numero('3500'), 3500);
  assert.equal(Match.numero('3500.5'), 3500.5);
  assert.equal(Match.numero(''), 0);
});

test('ato: R$ 1.500 no Ipiranga, R$ 2.500 nos demais', () => {
  assert.equal(Match.atoDe('ipiranga'), 1500);
  assert.equal(Match.atoDe('gaia'), 2500);
});

test('validarCliente: campos obrigatórios, renda e idade fora do MCMV', () => {
  assert.match(Match.validarCliente({ renda: 0, nascimento: NASC, fgts: true }, 'Ribeirão Preto', HOJE), /renda/i);
  assert.match(Match.validarCliente({ renda: 4000, nascimento: null, fgts: true }, 'Ribeirão Preto', HOJE), /nascimento/i);
  assert.match(Match.validarCliente({ renda: 13000.01, nascimento: NASC, fgts: true }, 'Ribeirão Preto', HOJE), /13\.000/);
  assert.match(Match.validarCliente({ renda: 4000, nascimento: new Date(1956, 3, 14), fgts: true }, 'Ribeirão Preto', HOJE), /70 anos e 6 meses/);
  assert.equal(Match.validarCliente(CLIENTE, 'Ribeirão Preto', HOJE), null);
});

test('resumoCliente devolve o enquadramento da renda', () => {
  const r = Match.resumoCliente(CLIENTE, 'Ribeirão Preto', HOJE);
  assert.equal(r.faixa, 'Faixa 2');
  assert.equal(r.jurosNominal, 5.5);
  assert.equal(r.prazo, 420);
  assert.ok(r.financiamentoMax > 0);
});

test('avaliarUnidade: descarta sem avaliação e fora do enquadramento', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  assert.equal(Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0101', 0, 220000), 'diamante', HOJE).status, 'sem-avaliacao');
  assert.equal(Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0102', NaN, 220000), 'diamante', HOJE).status, 'sem-avaliacao');
  /* avaliacao acima de 600 mil: nenhum produto MCMV enquadra */
  assert.equal(Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0103', 650000, 660000), 'diamante', HOJE).status, 'fora-enquadramento');
});

test('avaliarUnidade: financiamento + subsídio + ato acima da venda não deixa saldo negativo', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  const rico = { renda: 9000, nascimento: NASC, fgts: true };
  const r = Match.avaliarUnidade(rico, emp, UN('BL01-0201', 200000, 150000), 'aco', HOJE);
  assert.equal(r.status, 'ok');
  assert.equal(r.linha.saldoPS, 0);
  assert.equal(r.linha.financiamento, 150000 - r.linha.subsidio - 2500);
});

test('avaliarUnidade: aprova pelo linear quando cabe; usa a parcela maior entre seguradoras', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  /* avaliacao 260 mil: a cota de 80% (208 mil) nao limita, a renda sim (parcela CAIXA = 30%) */
  const r = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0301', 260000, 225000), 'diamante', HOJE);
  assert.equal(r.status, 'ok');
  assert.equal(r.linha.carne, 'linear');
  assert.equal(r.linha.prazoPS, 84);
  assert.ok(Math.abs(r.linha.parcelaFin - 1200) < 0.05, 'parcela CAIXA ≈ 30% da renda');
  assert.equal(r.linha.ato, 2500);
  assert.equal(r.linha.andar, 3);
  assert.equal(r.linha.final, 1);
});

test('avaliarUnidade: fora da política (inclui comitê) é descartada', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  assert.equal(Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0401', 260000, 245000), 'aco', HOJE).status, 'politica');
  assert.equal(Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0401', 260000, 245000), 'bronze', HOJE).status, 'politica');
});

test('avaliarUnidade: Pro Soluto pequeno encurta o prazo até a parcela mínima', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  const r = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0501', 260000, 215000), 'aco', HOJE);
  assert.equal(r.status, 'ok');
  assert.ok(r.linha.prazoPS < 84, 'prazo deveria encurtar');
  assert.ok(r.linha.parcelaPS >= 150, 'parcela abaixo da mínima do produto');
});

test('buscar: filtra cidade e empreendimento, agrupa, ordena e conta descartes', () => {
  const park = EMP('park', 'Ribeirão Preto'), ipi = EMP('ipiranga', 'Ribeirão Preto'), seleto = EMP('seleto', 'Campinas');
  const estoque = [
    { emp: park, unidades: [UN('BL01-0301', 260000, 235000), UN('BL01-0302', 260000, 225000), UN('BL01-0303', 0, 230000)] },
    { emp: ipi, unidades: [UN('BL01-0101', 260000, 225000)] },
    { emp: seleto, unidades: [UN('BL01-0101', 260000, 225000)] }
  ];
  const r = Match.buscar({ cliente: CLIENTE, cidade: 'Ribeirão Preto', empId: '', politicaId: 'diamante', hoje: HOJE, estoque });
  assert.deepEqual(r.grupos.map((g) => g.emp.id), ['park', 'ipiranga']);
  assert.deepEqual(r.grupos[0].linhas.map((l) => l.codigo), ['BL01-0302', 'BL01-0301']);
  assert.equal(r.grupos[1].linhas[0].ato, 1500);
  assert.equal(r.total, 3);
  assert.equal(r.descartadas.semAvaliacao, 1);

  const so = Match.buscar({ cliente: CLIENTE, cidade: 'Ribeirão Preto', empId: 'ipiranga', politicaId: 'diamante', hoje: HOJE, estoque });
  assert.deepEqual(so.grupos.map((g) => g.emp.id), ['ipiranga']);
});

test('buscar: sem unidades na política sugere a próxima política que tem', () => {
  const park = EMP('park', 'Ribeirão Preto');
  /* venda 235 mil: reprova no Aco, aprova no Bronze */
  const estoque = [{ emp: park, unidades: [UN('BL01-0301', 260000, 235000)] }];
  const aco = Match.buscar({ cliente: CLIENTE, cidade: 'Ribeirão Preto', empId: '', politicaId: 'aco', hoje: HOJE, estoque });
  assert.equal(aco.total, 0);
  assert.ok(aco.sugestao, 'deveria sugerir uma política acima');
  assert.notEqual(aco.sugestao.politicaId, 'aco');
  assert.equal(aco.sugestao.qtd, 1);
  assert.equal(aco.sugestao.politicaId, 'bronze');
  const nada = [{ emp: park, unidades: [UN('BL01-0301', 260000, 300000)] }];
  const dia = Match.buscar({ cliente: CLIENTE, cidade: 'Ribeirão Preto', empId: '', politicaId: 'diamante', hoje: HOJE, estoque: nada });
  assert.equal(dia.total, 0);
  assert.equal(dia.sugestao, null);
});

test('linhaPdf não carrega nenhum campo interno', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  const { linha } = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0301', 260000, 225000), 'diamante', HOJE);
  const pdf = Match.linhaPdf(linha);
  assert.deepEqual(Object.keys(pdf).sort(), ['areaPriv', 'ato', 'carne', 'codigo', 'empNome', 'financiamento',
    'parcelaFin', 'parcelaPS', 'prazoPS', 'subsidio', 'tipoLabel', 'venda'].sort());
  const texto = JSON.stringify(pdf);
  assert.ok(!/politica|crTotal|avaliacao|folga/i.test(texto));
});

test('urlAssociativo leva os dados para o simulador associativo', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  const { linha } = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0301', 260000, 225000), 'diamante', HOJE);
  const u = new URL(Match.urlAssociativo(linha, CLIENTE, HOJE), 'https://x/');
  assert.equal(u.pathname, '/simulador-associativo.html');
  assert.equal(u.searchParams.get('emp'), 'park');
  assert.equal(u.searchParams.get('unidade'), 'BL01-0301');
  assert.equal(u.searchParams.get('politica'), 'diamante');
  assert.equal(+u.searchParams.get('renda'), 4000);
  assert.equal(+u.searchParams.get('idade'), 36);
  assert.equal(+u.searchParams.get('valor'), 225000);
  assert.equal(+u.searchParams.get('fin'), linha.financiamento);
  assert.equal(+u.searchParams.get('ato'), 2500);
});

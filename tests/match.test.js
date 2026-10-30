const test = require('node:test');
const assert = require('node:assert/strict');
const Match = require('../assets/match.js');

const HOJE = new Date(2026, 9, 15);
const NASC = new Date(1990, 2, 15);              /* 36 anos */
const CLIENTE = { renda: 4000, nascimento: NASC, fgts: true, fatorSocial: false };

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

test('atoCliente: ato informado vale (inclusive zero); vazio usa o padrão do empreendimento', () => {
  assert.equal(Match.atoCliente({ ato: 8000 }, 'gaia'), 8000);
  assert.equal(Match.atoCliente({ ato: 0 }, 'gaia'), 0);
  assert.equal(Match.atoCliente({ ato: null }, 'ipiranga'), 1500);
  assert.equal(Match.atoCliente({}, 'gaia'), 2500);
});

test('avaliarUnidade: ato maior reduz o saldo do Pro Soluto na mesma medida', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  const un = UN('BL01-0301', 260000, 225000);
  const padrao = Match.avaliarUnidade(CLIENTE, emp, un, 'diamante', HOJE);
  const maior = Match.avaliarUnidade(Object.assign({ ato: 10000 }, CLIENTE), emp, un, 'diamante', HOJE);
  assert.equal(maior.status, 'ok');
  assert.equal(maior.linha.ato, 10000);
  assert.equal(maior.linha.financiamento, padrao.linha.financiamento);
  assert.ok(Math.abs(padrao.linha.saldoPS - maior.linha.saldoPS - 7500) < 0.01);
  assert.ok(maior.linha.parcelaPS < padrao.linha.parcelaPS);
});

test('validarCliente: campos obrigatórios, renda e idade fora do MCMV', () => {
  assert.match(Match.validarCliente({ renda: 0, nascimento: NASC, fgts: true }, 'Ribeirão Preto', HOJE), /renda/i);
  assert.match(Match.validarCliente({ renda: 4000, nascimento: null, fgts: true }, 'Ribeirão Preto', HOJE), /nascimento/i);
  assert.equal(Match.validarCliente({ renda: 13000.01, nascimento: NASC, fgts: true }, 'Ribeirão Preto', HOJE), null, 'acima de 13 mil vai para o SBPE');
  assert.match(Match.validarCliente({ renda: 4000, nascimento: new Date(1956, 3, 14), fgts: true, fatorSocial: false }, 'Ribeirão Preto', HOJE), /70 anos e 6 meses/);
  assert.equal(Match.validarCliente(CLIENTE, 'Ribeirão Preto', HOJE), null);
});

test('subsídio: dependente só é perguntado (e exigido) com renda até R$ 4.000 e sem imóvel', () => {
  assert.equal(Match.temSubsidio(4000, false), true);
  assert.equal(Match.temSubsidio(4000.01, false), false);
  assert.equal(Match.temSubsidio(2500, true), false);
  const semResposta = { renda: 2500, nascimento: NASC, fgts: true };
  assert.match(Match.validarCliente(semResposta, 'Ribeirão Preto', HOJE), /dependente/);
  assert.equal(Match.validarCliente({ renda: 5000, nascimento: NASC, fgts: true }, 'Ribeirão Preto', HOJE), null);
});

test('subsídio: com dependente sobe para o valor da família; subsídio anterior zera', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  const un = UN('BL01-0301', 200000, 165000);
  const base = { renda: 2500, nascimento: NASC, fgts: true };
  const so = Match.avaliarUnidade(Object.assign({ fatorSocial: false }, base), emp, un, 'diamante', HOJE);
  const fam = Match.avaliarUnidade(Object.assign({ fatorSocial: true }, base), emp, un, 'diamante', HOJE);
  const ant = Match.avaliarUnidade(Object.assign({ fatorSocial: true, subsidioAnterior: true }, base), emp, un, 'diamante', HOJE);
  assert.equal(so.linha.subsidio, 6799);
  assert.equal(fam.linha.subsidio, 22663);
  assert.equal(ant.linha.subsidio, 0);
  assert.ok(fam.linha.saldoPS < so.linha.saldoPS, 'subsídio maior reduz o Pro Soluto');
  assert.equal(Match.resumoCliente(Object.assign({ fatorSocial: true }, base), 'Ribeirão Preto', HOJE).subsidio, 22663);
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
  /* a parcela CAIXA tem de ser a do valor financiado de fato, nao a da capacidade maxima */
  const M = require('../assets/motor-caixa.js');
  const cx = M.simular({ renda: 9000, valor: 200000, nascimento: NASC, municipio: '3543402', fgts: true, hoje: HOJE,
    valorFinanciamento: r.linha.financiamento });
  assert.equal(cx.valorFinanciamento, r.linha.financiamento);
  assert.equal(r.linha.parcelaFin, Math.max(...cx.seguradoras.map((s) => s.primeira)));
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
  /* o associativo precisa abrir com o mesmo prazo encurtado */
  const u = new URL(Match.urlAssociativo(r.linha, CLIENTE, HOJE), 'https://x/');
  assert.equal(+u.searchParams.get('prazo'), r.linha.prazoPS);
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
    'parcelaFin', 'parcelaPS', 'prazoPS', 'promocional', 'subsidio', 'tipoLabel', 'venda'].sort());
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

/* ---------- SBPE e trava da Faixa 3 (spec 4.5 e 4.6) ---------- */

test('resumoCliente: possui imóvel ou renda acima de R$ 13.000 mostra SBPE', () => {
  assert.equal(Match.resumoCliente({ ...CLIENTE, possuiImovel: true }, 'Ribeirão Preto', HOJE).faixa, 'SBPE');
  assert.equal(Match.resumoCliente({ renda: 15000, nascimento: NASC, fgts: true }, 'Ribeirão Preto', HOJE).faixa, 'SBPE');
  assert.equal(Match.resumoCliente(CLIENTE, 'Ribeirão Preto', HOJE).faixa, 'Faixa 2');
});

test('avaliarUnidade: cliente com imóvel é simulado no SBPE (PRICE 25%)', () => {
  const emp = EMP('park', 'Ribeirão Preto');
  const cli = { renda: 9000, nascimento: NASC, fgts: true, possuiImovel: true };
  const r = Match.avaliarUnidade(cli, emp, UN('BL01-0301', 300000, 300000), 'diamante', HOJE);
  assert.equal(r.status, 'ok');
  const M = require('../assets/motor-caixa.js');
  const cx = M.simular({ renda: 9000, valor: 300000, nascimento: NASC, municipio: '3543402', fgts: true, possuiImovel: true, hoje: HOJE });
  assert.equal(cx.faixa, 'SBPE');
  assert.equal(r.linha.faixa, 'SBPE');
  assert.equal(r.linha.jurosNominal, 10.92);
  assert.ok(r.linha.prazoFin <= 360);
  assert.ok(Math.abs(r.linha.parcelaFin - 2250) < 0.05, 'parcela CAIXA = 25% da renda no SBPE PRICE');
});

test('trava da Faixa 3: avaliação > 400 mil, venda < 400 mil e renda ≤ 9.600 simula com R$ 400 mil', () => {
  const emp = EMP('botanico', 'Ribeirão Preto');
  const cli = { renda: 7000, nascimento: NASC, fgts: true };
  const r = Match.avaliarUnidade(cli, emp, UN('BL01-0301', 420000, 390000), 'diamante', HOJE);
  const M = require('../assets/motor-caixa.js');
  const cx400 = M.simular({ renda: 7000, valor: 400000, nascimento: NASC, municipio: '3543402', fgts: true, hoje: HOJE });
  assert.equal(cx400.faixa, 'Faixa 3');
  /* mesmo que a politica reprove, a simulacao CAIXA tem de ter sido feita na Faixa 3 */
  const linha = r.linha || Match.avaliarUnidade(cli, emp, UN('BL01-0301', 420000, 330000), 'diamante', HOJE).linha;
  assert.ok(linha, 'deveria haver uma unidade aprovada para conferir');
  assert.equal(linha.travaF3, true);
  assert.equal(linha.faixa, 'Faixa 3');
  assert.equal(linha.jurosNominal, 7.66);
  assert.ok(linha.financiamento <= 320000 + 0.005, 'cota de 80% sobre R$ 400 mil');
});

test('trava da Faixa 3 não se aplica fora da regra', () => {
  const emp = EMP('botanico', 'Ribeirão Preto');
  const semTrava = (cli, un) => {
    const r = Match.avaliarUnidade(cli, emp, un, 'diamante', HOJE);
    return r.status === 'ok' ? r.linha.travaF3 : false;
  };
  /* venda >= 400 mil: segue na Faixa 4 */
  assert.equal(semTrava({ renda: 7000, nascimento: NASC, fgts: true }, UN('BL01-0301', 420000, 400000)), false);
  /* renda acima de 9.600 */
  assert.equal(semTrava({ renda: 9700, nascimento: NASC, fgts: true }, UN('BL01-0301', 420000, 390000)), false);
  /* cliente no SBPE */
  assert.equal(semTrava({ renda: 7000, nascimento: NASC, fgts: true, possuiImovel: true }, UN('BL01-0301', 420000, 390000)), false);
  /* avaliacao ate 400 mil: nada a travar */
  assert.equal(semTrava({ renda: 7000, nascimento: NASC, fgts: true }, UN('BL01-0301', 400000, 390000)), false);
});

test('linhaPdf não leva o selo da trava da Faixa 3', () => {
  const emp = EMP('botanico', 'Ribeirão Preto');
  const { linha } = Match.avaliarUnidade({ renda: 7000, nascimento: NASC, fgts: true }, emp, UN('BL01-0301', 420000, 330000), 'diamante', HOJE);
  assert.ok(!('travaF3' in Match.linhaPdf(linha)));
  assert.ok(!('faixa' in Match.linhaPdf(linha)));
});

/* ---------- selo de faixa no cartao (pedido de 20/10/2026) ---------- */

test('seloFaixa: avisa quando a unidade cai em faixa diferente do resumo', () => {
  assert.equal(Match.seloFaixa({ faixa: 'Faixa 4', jurosNominal: 10, travaF3: false }, 'Faixa 3'),
    'Enquadrada na Faixa 4 (10% a.a.)');
  assert.equal(Match.seloFaixa({ faixa: 'Faixa 3', jurosNominal: 7.66, travaF3: false }, 'Faixa 2'),
    'Enquadrada na Faixa 3 (7,66% a.a.)');
});

test('seloFaixa: nada quando bate com o resumo ou quando a trava da Faixa 3 já explica', () => {
  assert.equal(Match.seloFaixa({ faixa: 'Faixa 3', jurosNominal: 7.66, travaF3: false }, 'Faixa 3'), null);
  assert.equal(Match.seloFaixa({ faixa: 'Faixa 3', jurosNominal: 7.66, travaF3: true }, 'Faixa 3'), null);
  assert.equal(Match.seloFaixa({ faixa: 'SBPE', jurosNominal: 10.92, travaF3: false }, 'SBPE'), null);
});

test('seloFaixa: unidade do Botânico vendida acima de 400 mil com renda de Faixa 3 cai na Faixa 4', () => {
  const emp = EMP('botanico', 'Ribeirão Preto');
  const cli = { renda: 9600, nascimento: NASC, fgts: true };
  const resumo = Match.resumoCliente(cli, 'Ribeirão Preto', HOJE);
  const r = Match.avaliarUnidade(cli, emp, UN('BL03-1205', 412800, 400800), 'diamante', HOJE);
  assert.equal(r.status, 'ok');
  assert.equal(resumo.faixa, 'Faixa 3');
  assert.equal(r.linha.faixa, 'Faixa 4');
  assert.equal(Match.seloFaixa(r.linha, resumo.faixa), 'Enquadrada na Faixa 4 (10% a.a.)');
});

/* ---------- unidade promocional (ajustes do teste de 30/10/2026) ---------- */

test('avaliarUnidade: repassa a marca de promocional para a linha (sem mudar contas)', () => {
  const emp = EMP('gaia', 'Ribeirão Preto');
  const promo = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0301', 260000, 225000, { promocional: true }), 'diamante', HOJE);
  const normal = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0301', 260000, 225000), 'diamante', HOJE);
  assert.equal(promo.linha.promocional, true);
  assert.equal(normal.linha.promocional, false);
  const semMarca = Object.assign({}, promo.linha, { promocional: false });
  assert.deepEqual(semMarca, normal.linha);
});

test('linhaPdf leva a marca de promocional', () => {
  const emp = EMP('gaia', 'Ribeirão Preto');
  const promo = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0301', 260000, 225000, { promocional: true }), 'diamante', HOJE);
  const normal = Match.avaliarUnidade(CLIENTE, emp, UN('BL01-0301', 260000, 225000), 'diamante', HOJE);
  assert.equal(Match.linhaPdf(promo.linha).promocional, true);
  assert.equal(Match.linhaPdf(normal.linha).promocional, false);
});

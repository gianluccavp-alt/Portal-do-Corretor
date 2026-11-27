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

test('resumo: matriz', () => {
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
  assert.equal(r.matriz.comercial.ok.n, 1);
  assert.equal(r.matriz.comercial.sem.n, 1);
  assert.equal(r.matriz.facilitada.ok.n, 1);
  assert.equal(r.matriz.facilitada.sem.n, 3);
  assert.equal(r.empreendimentos[0].n, 6);
});

test('le datas no formato brasileiro e booleanos em texto', () => {
  const v = R.lerLinha(CAB, ['23/11/2026', 'Proposta Aprovada', 'X', 'E', 'OP-1', '', '', '', '', '', 'Sim', 'Não', '1.234,50', '', 'FALSE', 'TRUE', '']);
  assert.equal(v.venda, '2026-11-23');
  assert.equal(v.tipo, 'facilitada');
  assert.equal(v.boleto, true);
  assert.equal(v.valor, 1234.5);
});

test('cliente sai do nome da oportunidade e FID preenchido vale aprovado', () => {
  const l = linha({ op: 8, venda: '2026-11-01' });
  l[CAB.indexOf('Nome da oportunidade')] = 'OP-8 - Cliente: MARIA TESTE';
  l[CAB.indexOf('FID')] = '747247';
  const v = R.lerLinha(CAB, l);
  assert.equal(v.cliente, 'MARIA TESTE');
  assert.equal(v.fidOk, true);
  assert.equal(R.lerLinha(CAB, linha({ op: 9, venda: '2026-11-01' })).fidOk, false);
});

const CAB_D4 = ['Envio D4Sign: Oportunidade', 'Envio D4Sign: Status', 'Envio D4Sign: Cliente assinou?', 'Envio D4Sign: Data de criação'];
const d4 = (linhas) => ({ cabecalho: CAB_D4, linhas });

test('assinatura vem do D4Sign: ultimo envio nao cancelado decide', () => {
  const abas = [aba([1, 2, 3, 4, 5].map((op) => ({ op, venda: '2026-11-01', pcv: '2026-11-01' })))];
  const envios = d4([
    ['OP-1 - Cliente: A', 'Cancelado', false, '2026-11-02'],
    ['OP-1 - Cliente: A', 'Finalizado', true, '2026-11-01'],
    ['OP-2 - Cliente: B', 'Finalizado', true, '2026-11-01'],
    ['OP-2 - Cliente: B', 'Aguardando Assinaturas', true, '2026-11-03'],
    ['OP-3 - Cliente: C', 'Cancelado', true, '2026-11-01'],
    ['OP-4 - Cliente: D', 'Aguardando Signatários', false, '2026-11-01']
  ]);
  const por = {};
  R.vendasDoMes(abas, '2026-11', envios).forEach((v) => { por[v.op] = v; });
  assert.equal(por['OP-1'].assinatura, 'assinado');
  // OP-2: o envio mais recente ainda aguarda outros, mas o cliente ja assinou
  assert.equal(por['OP-2'].assinatura, 'assinado');
  // envio cancelado nao vale, mesmo com o cliente marcado como assinado
  assert.equal(por['OP-3'].assinatura, 'cancelado');
  assert.equal(por['OP-4'].assinatura, 'aguardando');
  assert.equal(por['OP-5'].assinatura, 'sem_envio');
});

test('sem dados do D4Sign a assinatura fica desconhecida, nao pendente', () => {
  const lista = R.vendasDoMes([aba([{ op: 1, venda: '2026-11-01', boleto: 'Sim' }])], '2026-11');
  assert.equal(lista[0].assinatura, '');
  const p = R.resumo(lista).pendencias;
  assert.equal(p.temD4, false);
  assert.equal(p.assinatura, 0);
});

test('pendencias olham todas as vendas do mes, confirmadas ou nao', () => {
  const l = [
    { op: 1, venda: '2026-11-01', conf: '2026-11-02', boleto: 'Sim' },
    { op: 2, venda: '2026-11-01' },
    { op: 3, venda: '2026-11-01', cartao: 'Sim' }
  ];
  const abas = [aba(l)];
  abas[0].linhas[0][CAB.indexOf('FID')] = '1';
  abas[0].linhas[2][CAB.indexOf('FID')] = '3';
  const envios = d4([['OP-1', 'Finalizado', true, '2026-11-01']]);
  const p = R.resumo(R.vendasDoMes(abas, '2026-11', envios)).pendencias;
  assert.deepEqual(p, { temD4: true, total: 3, assinatura: 2, fid: 1, sinal: 1, semPendencia: 1 });
});

test('house, canal imob e cidade', () => {
  assert.equal(R.canalDe('DIRECIONAL VENDAS SPI – EQUIPE OTAVIO'), 'house');
  assert.equal(R.canalDe('RIVA VENDAS SPI – EQUIPE X'), 'house');
  assert.equal(R.canalDe('SPI - CANAL IMOB PJ - VITOR'), 'canal');
  assert.equal(R.canalDe('DDS SPI - KAREN'), '');
  assert.equal(R.cidadeDe('Village Gaia'), 'Ribeirão Preto');
  assert.equal(R.cidadeDe('Casa Prado Residencial Riva'), 'Campinas');
  assert.equal(R.cidadeDe('Conquista Vila da Mata'), 'Sorocaba');
  assert.equal(R.cidadeDe('Compra e Venda de Bens Imóveis V - BNDU SPI'), 'Ribeirão Preto');
  assert.equal(R.cidadeDe('Compra e Venda de Bens Imóveis III - SP'), 'Campinas');
  assert.equal(R.cidadeDe('Conquista Nature'), 'Campinas');
  assert.equal(R.cidadeDe('Reserva Antonieta'), 'Campinas');
  assert.equal(R.cidadeDe('Conquista Macaúba'), 'Ribeirão Preto');
  assert.equal(R.cidadeDe('Conquista Horizonte'), 'Ribeirão Preto');
  for (const e of ['Módulo 1', 'Módulo 2', 'Módulo 3', 'Lotes']) assert.equal(R.cidadeDe('Dream Santo Antônio - ' + e), 'São Carlos', e);
  assert.equal(R.cidadeDe('Residencial Parque das Flores'), 'Piracicaba');
  assert.equal(R.cidadeDe('Parque das Cerejeiras - Condomínio 4 - Mod. 3'), 'Bragança Paulista');
  const doCadastro = {
    'Conquista Araraquara': 'Araraquara', 'Rise Parque Prado': 'Campinas', 'Alentejo Residencial': 'Campinas',
    'Village Novus II': 'Ribeirão Preto', 'Conquista Vila Acqua': 'Sorocaba', 'Conquista Votorantim - 2ª Etapa': 'Votorantim',
    'Conquista Parque Hipólito': 'Limeira', 'Reserva do Alto': 'Valinhos', 'Viva Vida Paineiras': 'Piracicaba',
    'Parque das Cerejeiras - CondomÃ\u00adnio 2 - Mod. 5': 'Bragança Paulista'
  };
  for (const [emp, cidade] of Object.entries(doCadastro)) assert.equal(R.cidadeDe(emp), cidade, emp);
  assert.equal(R.cidadeDe('Empreendimento Novo'), 'Outras');
});

test('contrato distratado nao conta, mesmo com a fase Fechado e ganho', () => {
  const cab = CAB.concat('Oportunidade: Status Contrato');
  const com = (p, status) => linha(p).concat(status);
  const abas = [
    { cabecalho: cab, linhas: [
      com({ op: 1, venda: '2026-11-01', fase: 'Fechado e ganho' }, 'Distratado'),
      com({ op: 2, venda: '2026-11-01', fase: 'Fechado e ganho' }, 'Ativado'),
      com({ op: 3, venda: '2026-11-01' }, ''),
      com({ op: 4, venda: '2026-11-01' }, 'Ativado')
    ] },
    /* basta uma das abas marcar o distrato */
    { cabecalho: cab, linhas: [com({ op: 4, venda: '2026-11-01' }, 'Distratado')] }
  ];
  assert.deepEqual(R.vendasDoMes(abas, '2026-11').map((v) => v.op).sort(), ['OP-2', 'OP-3']);
});

test('filtros gerais combinam empreendimento, cidade e canal', () => {
  const lista = R.vendasDoMes([aba([
    { op: 1, venda: '2026-11-01', emp: 'Village Gaia', imob: 'SPI - CANAL IMOB PJ - A' },
    { op: 2, venda: '2026-11-01', emp: 'Village Park', imob: 'DIRECIONAL VENDAS SPI - B' },
    { op: 3, venda: '2026-11-01', emp: 'Seleto Amoreiras', imob: 'DIRECIONAL VENDAS SPI - B' }
  ])], '2026-11');
  const ops = (g) => R.filtrarGeral(lista, g).map((v) => v.op).sort();
  assert.deepEqual(ops({ emps: [], cidades: ['Ribeirão Preto'], canal: '' }), ['OP-1', 'OP-2']);
  assert.deepEqual(ops({ emps: [], cidades: ['Ribeirão Preto'], canal: 'house' }), ['OP-2']);
  assert.deepEqual(ops({ emps: [], cidades: ['Ribeirão Preto', 'Campinas'], canal: '' }), ['OP-1', 'OP-2', 'OP-3']);
  assert.deepEqual(ops({ emps: [], cidades: ['Campinas', 'Sorocaba'], canal: '' }), ['OP-3']);
  assert.deepEqual(ops({ emps: ['Seleto Amoreiras'], cidades: [], canal: '' }), ['OP-3']);
});

test('periodo pode ser mes, trimestre ou ano', () => {
  const abas = [aba([
    { op: 1, venda: '2026-10-05' }, { op: 2, venda: '2026-12-30' }, { op: 3, venda: '2026-09-30' },
    { op: 4, venda: '2025-12-31', conf: '2026-01-02' }, { op: 5, venda: '2025-11-01' }
  ])];
  const ops = (p) => R.vendasDoMes(abas, p).map((v) => v.op).sort();
  assert.deepEqual(ops('2026-10'), ['OP-1']);
  assert.deepEqual(ops('2026-T4'), ['OP-1', 'OP-2']);
  assert.deepEqual(ops('2026'), ['OP-1', 'OP-2', 'OP-3', 'OP-4']);
  assert.deepEqual(ops('2025'), ['OP-5']);
  assert.equal(R.periodoDe('2026-11', 'tri'), '2026-T4');
  assert.equal(R.periodoDe('2026-03', 'tri'), '2026-T1');
  assert.equal(R.periodoDe('2026-11', 'ano'), '2026');
  assert.equal(R.tipoPeriodo('2026-T2'), 'tri');
});

test('venda anterior ao D4Sign sem envio usa o campo Cliente assinou PCV', () => {
  const abas = [aba([
    { op: 1, venda: '2025-03-01', pcv: '2025-03-02' }, { op: 2, venda: '2025-03-01' },
    { op: 3, venda: '2025-10-01', pcv: '2025-10-02' }, { op: 4, venda: '2025-03-01', pcv: '2025-03-02' }
  ])];
  const l = R.vendasDoMes(abas, '2025', d4([['OP-4', 'Aguardando Assinaturas', false, '2025-09-20']]));
  const a = (op) => l.find((v) => v.op === op).assinatura;
  assert.equal(a('OP-1'), 'assinado');
  assert.equal(a('OP-2'), 'nao_assinado');
  assert.equal(a('OP-3'), 'sem_envio');
  assert.equal(a('OP-4'), 'aguardando');
});

test('varias pendencias marcadas: entra a venda que tiver qualquer uma', () => {
  const v = { assinatura: 'assinado', fidOk: false, sinalPago: true };
  assert.equal(R.temAlguma(v, ['sinal', 'fid']), true);
  assert.equal(R.temAlguma(v, ['sinal', 'assinatura']), false);
  assert.equal(R.temAlguma(v, []), true);
  assert.equal(R.temPendencia({ assinatura: '', fidOk: true, sinalPago: true }, 'nenhuma'), false);
});

const resposta = (mes, linhas, extra) => Object.assign({
  ok: true, mes, meses: ['2026-11', '2026-09'], atualizadoEm: '2026-11-26 10:00', intervaloMinutos: 30,
  abas: [Object.assign({ aba: 'VENDAS SPI XIMENES' }, aba(linhas))],
  d4sign: { cabecalho: ['Envio D4Sign: Oportunidade', 'Envio D4Sign: Status', 'Envio D4Sign: Cliente assinou?', 'Envio D4Sign: Data de criação'], linhas: [] }
}, extra);

test('periodo com varios meses', () => {
  const p = '2025-11+2026-09';
  assert.equal(R.tipoPeriodo(p), 'multi');
  assert.equal(R.noPeriodo('2025-11', p), true);
  assert.equal(R.noPeriodo('2026-09', p), true);
  assert.equal(R.noPeriodo('2026-10', p), false);
  assert.equal(R.noPeriodo('', p), false);
});

test('juntar meses: soma, nao duplica OP e usa a carga mais antiga', () => {
  const repetida = { op: 2, venda: '2026-09-30', conf: '2026-11-02' };
  const j = R.juntarRespostas([
    resposta('2026-09', [{ op: 1, venda: '2026-09-10' }, repetida], { atualizadoEm: '2026-11-26 09:30' }),
    resposta('2026-11', [repetida, { op: 3, venda: '2026-11-05' }])
  ], '2026-09+2026-11');
  assert.equal(j.mes, '2026-09+2026-11');
  assert.equal(j.atualizadoEm, '2026-11-26 09:30');
  assert.deepEqual(R.vendasDoMes(j.abas, j.mes, j.d4sign).map((v) => v.op).sort(), ['OP-1', 'OP-2', 'OP-3']);
});

test('juntar meses: sem D4Sign em um deles a assinatura fica desconhecida', () => {
  const j = R.juntarRespostas([
    resposta('2026-09', [{ op: 1, venda: '2026-09-10' }], { d4sign: null }),
    resposta('2026-11', [{ op: 3, venda: '2026-11-05' }])
  ], '2026-09+2026-11');
  assert.equal(j.d4sign, null);
  assert.deepEqual(R.vendasDoMes(j.abas, j.mes, j.d4sign).map((v) => v.assinatura), ['', '']);
});

test('filtro geral aceita varios empreendimentos; nenhum = todos', () => {
  const vendas = ['Village Gaia', 'Village Park', 'Seleto Amoreiras'].map((emp) => ({ emp, cidade: R.cidadeDe(emp), canal: '' }));
  const nomes = (emps) => R.filtrarGeral(vendas, { emps, cidades: [], canal: '' }).map((v) => v.emp);
  assert.deepEqual(nomes(['Village Gaia', 'Seleto Amoreiras']), ['Village Gaia', 'Seleto Amoreiras']);
  assert.equal(nomes([]).length, 3);
});

/* ---------- filtros avancados ---------- */
const base = { fase: 'Proposta Aprovada', corretor: 'ANA', emp: 'Village Gaia', assinatura: 'aguardando',
  boleto: false, cartao: false, sinalPago: false, ranking: '', origem: 'Stand', venda: '2026-11-10', conf: '', valor: 250000 };
const av = (x) => Object.assign(R.avancadoVazio(), x);

test('avancado vazio passa tudo e conta zero', () => {
  assert.equal(R.passaAvancado(base, R.avancadoVazio()), true);
  assert.equal(R.contarAvancados(av({ dataBase: 'conf' })), 0);
});
test('avancado: no mesmo campo soma, entre campos combina', () => {
  assert.equal(R.passaAvancado(base, av({ fases: ['Fechado e ganho', 'Proposta Aprovada'] })), true);
  assert.equal(R.passaAvancado(base, av({ fases: ['Proposta Aprovada'], corretores: ['BIA'] })), false);
  assert.equal(R.passaAvancado(base, av({ emps: ['Village Park'] })), false);
  assert.equal(R.passaAvancado(base, av({ assinaturas: ['aguardando'], origens: ['Stand'], rankings: [R.SEM] })), true);
});
test('avancado: sinal', () => {
  assert.equal(R.passaAvancado(base, av({ sinais: ['pendente'] })), true);
  assert.equal(R.passaAvancado(base, av({ sinais: ['boleto', 'cartao'] })), false);
  assert.equal(R.passaAvancado({ ...base, cartao: true, sinalPago: true }, av({ sinais: ['cartao'] })), true);
});
test('avancado: data e valor, limites inclusivos e invertidos', () => {
  assert.equal(R.passaAvancado(base, av({ dataDe: '2026-11-10', dataAte: '2026-11-10' })), true);
  assert.equal(R.passaAvancado(base, av({ dataDe: '2026-11-20', dataAte: '2026-11-01' })), true);
  assert.equal(R.passaAvancado(base, av({ dataDe: '2026-11-11' })), false);
  assert.equal(R.passaAvancado(base, av({ dataBase: 'conf', dataAte: '2026-11-30' })), false);
  assert.equal(R.passaAvancado(base, av({ valorDe: 300000, valorAte: 200000 })), true);
  assert.equal(R.passaAvancado(base, av({ valorAte: 249999 })), false);
  assert.equal(R.contarAvancados(av({ valorDe: 0, dataDe: '2026-11-01', dataAte: '2026-11-02', fases: ['x'] })), 3);
});
test('lerValor entende o formato brasileiro', () => {
  assert.equal(R.lerValor('250.000'), 250000);
  assert.equal(R.lerValor('R$ 250.000,50'), 250000.5);
  assert.equal(R.lerValor('250000'), 250000);
  assert.equal(R.lerValor(''), null);
  assert.equal(R.lerValor('abc'), null);
});

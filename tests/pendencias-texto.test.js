const test = require('node:test');
const assert = require('node:assert/strict');
const P = require('../assets/pendencias.js');

test('normalizar tira acento, espaços das pontas e caixa', () => {
  assert.equal(P.normalizar('  Análise Aprovada '), 'analise aprovada');
  assert.equal(P.normalizar(null), '');
  assert.equal(P.normalizar(undefined), '');
  assert.equal(P.normalizar(0), '0');
});

test('titleCase mantém conectivos em minúscula, menos no começo', () => {
  assert.equal(P.titleCase('CARLA DOS SANTOS E SILVA'), 'Carla dos Santos e Silva');
  assert.equal(P.titleCase('JOÃO VITOR'), 'João Vitor');
  assert.equal(P.titleCase('DA SILVA'), 'Da Silva');
  assert.equal(P.titleCase('  '), '');
});

test('formatarEquipe cobre os formatos reais da planilha', () => {
  assert.equal(P.formatarEquipe('DIRECIONAL VENDAS SPI – EQUIPE MARCOS TAVARES'), 'Equipe Marcos Tavares');
  assert.equal(P.formatarEquipe('DIRECIONAL VENDAS SPI - EQUIPE LUANA DA COSTA - Inativo'), 'Equipe Luana da Costa - Inativo');
  assert.equal(P.formatarEquipe('DIRECIONAL VENDAS SPI ? EQUIPE DIEGO FARIAS - Inativo'), 'Equipe Diego Farias - Inativo');
  assert.equal(P.formatarEquipe('SPI - CANAL IMOB PJ – RENATA MOURA'), 'Canal PJ · Renata Moura');
  assert.equal(P.formatarEquipe('SPI - CANAL IMOB PJ - BEATRIZ NUNES - Inativo'), 'Canal PJ · Beatriz Nunes - Inativo');
  assert.equal(P.formatarEquipe(''), '—');
  assert.equal(P.formatarEquipe(null), '—');
});

test('formatarValor em reais, com e sem centavos', () => {
  assert.equal(P.formatarValor(214900), 'R$ 214.900');
  assert.equal(P.formatarValor(217990.5, true), 'R$ 217.990,50');
  assert.equal(P.formatarValor(null), 'Não informado');
  assert.equal(P.formatarValor(''), 'Não informado');
});

test('formatarMi abrevia milhões', () => {
  assert.equal(P.formatarMi(8491885.57), 'R$ 8,49 mi');
  assert.equal(P.formatarMi(950000), 'R$ 950.000');
  assert.equal(P.formatarMi(0), 'R$ 0');
});

test('parseData aceita dd/mm/aaaa com hora opcional', () => {
  assert.deepEqual(P.parseData('09/09/2026'), new Date(2026, 8, 9));
  assert.deepEqual(P.parseData('08/08/2026 17:22:00'), new Date(2026, 7, 8, 17, 22, 0));
  assert.deepEqual(P.parseData('10/09/2026 17:22'), new Date(2026, 8, 10, 17, 22));
  assert.equal(P.parseData(''), null);
  assert.equal(P.parseData('2026-09-09'), null);
});

test('diasEmAberto conta dias corridos até hoje', () => {
  const hoje = new Date(2026, 8, 28, 15, 30);
  assert.equal(P.diasEmAberto('09/09/2026', hoje), 19);
  assert.equal(P.diasEmAberto('28/09/2026', hoje), 0);
  assert.equal(P.diasEmAberto('', hoje), null);
});

test('textoDias', () => {
  assert.equal(P.textoDias(19), '19 dias');
  assert.equal(P.textoDias(1), '1 dia');
  assert.equal(P.textoDias(0), 'hoje');
  assert.equal(P.textoDias(null), '—');
});

test('isoParaData lê o valor de <input type=date>', () => {
  assert.deepEqual(P.isoParaData('2026-09-15'), new Date(2026, 8, 15));
  assert.equal(P.isoParaData(''), null);
});

test('formatarAtualizacao', () => {
  const agora = new Date(2026, 8, 28, 16, 0);
  assert.equal(P.formatarAtualizacao(new Date(2026, 8, 28, 14, 32).toISOString(), agora), 'Salesforce atualizado hoje às 14:32');
  assert.equal(P.formatarAtualizacao(new Date(2026, 8, 27, 9, 5).toISOString(), agora), 'Salesforce atualizado em 27/09/2026 às 09:05');
  assert.equal(P.formatarAtualizacao(null, agora), 'Última atualização do Salesforce desconhecida');
  assert.equal(P.formatarAtualizacao('lixo', agora), 'Última atualização do Salesforce desconhecida');
});

test('justificativaExibida trata vazio e "."', () => {
  assert.equal(P.justificativaExibida('.'), 'Sem justificativa registrada');
  assert.equal(P.justificativaExibida('   '), 'Sem justificativa registrada');
  assert.equal(P.justificativaExibida(' Pendente IRPF '), 'Pendente IRPF');
});

test('notaDaLinha prefere Retorno, depois Observação', () => {
  assert.equal(P.notaDaLinha({ retorno: 'Falta baixa Bacen', observacao: 'x' }), 'Retorno: Falta baixa Bacen');
  assert.equal(P.notaDaLinha({ retorno: ' ', observacao: ' Resolvendo renda ' }), 'Obs.: Resolvendo renda');
  assert.equal(P.notaDaLinha({}), '');
});

test('ranking sem emoji', () => {
  assert.equal(P.rankingChave('Ouro🥇'), 'ouro');
  assert.equal(P.rankingChave('Aço🔘'), 'aco');
  assert.equal(P.rankingRotulo('Diamante💎'), 'Diamante');
  assert.equal(P.rankingRotulo('Aço🔘'), 'Aço');
  assert.equal(P.rankingRotulo(''), '');
});

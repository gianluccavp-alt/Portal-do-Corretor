const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');

const ler = (f) => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');

test('associativo normal carrega o popup e tem o slot no passo Cliente', () => {
  const h = ler('simulador-associativo.html');
  for (const s of ['assets/motor-caixa.js', 'assets/match-prosoluto.js', 'assets/match.js', 'assets/financiamento.js', 'assets/financiamento-pdf.js', 'assets/financiamento-popup.js']) assert.ok(h.includes(`src="${s}"`), s);
  assert.ok(h.includes('href="assets/financiamento.css"'));
  const passo2 = h.slice(h.indexOf('data-step="2"'), h.indexOf('data-step="3"'));
  assert.ok(passo2.includes('id="fz-slot"'));
  assert.match(h, /FinanciamentoPopup\.ligarAssociativo\(\{\s*tema:\s*'claro'/);
});

test('ícones 3D novos existem', () => {
  for (const n of ['escudo', 'documento']) assert.ok(fs.existsSync(path.join(__dirname, '..', `assets/img/icones-3d/${n}.svg`)));
});

test('associativo normal avisa o popup no render e no limpar', () => {
  const h = ler('simulador-associativo.html');
  assert.match(h, /function render\(\)\{[^\n]*fz\.atualizar\(\)/);
  const ini = h.indexOf("$('b-reset').addEventListener");
  const reset = h.slice(ini, h.indexOf('\n});', ini));
  assert.ok(reset.includes('fz.limpar()'));
});

test('associativo Black Friday liga o popup com tema black', () => {
  const h = ler('simulador-associativo-blackfriday.html');
  for (const s of ['assets/financiamento.js', 'assets/financiamento-popup.js']) assert.ok(h.includes(`src="${s}"`), s);
  const passo2 = h.slice(h.indexOf('data-step="2"'), h.indexOf('data-step="3"'));
  assert.ok(passo2.includes('id="fz-slot"'));
  assert.match(h, /FinanciamentoPopup\.ligarAssociativo\(\{\s*tema:\s*'black'/);
  assert.ok(h.includes('fz.atualizar()') && h.includes('fz.limpar()'));
});

for (const f of ['simulador-associativo.html', 'simulador-associativo-blackfriday.html']) {
  test(f + ': parâmetros da simulação valem sem emp e só marcam com origem=financiamento', () => {
    const h = ler(f);
    const fn = h.slice(h.indexOf('function aplicaParametrosUrl'), h.indexOf('})();', h.indexOf('function aplicaParametrosUrl')));
    assert.ok(!/if\(!q\.has\('emp'\)\) return;/.test(fn), 'não pode sair cedo sem emp');
    assert.ok(fn.includes("q.get('origem')==='financiamento'") || fn.includes('q.get("origem")==="financiamento"'));
    assert.ok(fn.includes('decodificaRespostas'));
  });
}

test('tela dedicada carrega os módulos e tem os cinco passos', () => {
  const h = ler('simulador-financiamento.html');
  for (const s of ['assets/config.js', 'assets/simuladores.js', 'assets/motor-caixa.js', 'assets/match-prosoluto.js', 'assets/match.js', 'assets/financiamento.js', 'assets/financiamento-pdf.js', 'assets/financiamento-app.js', 'assets/credito.js']) assert.ok(h.includes(`src="${s}"`), s);
  assert.ok(h.includes('jspdf/2.5.1/jspdf.umd.min.js') && h.includes('jspdf-autotable/3.8.2'));
  assert.ok(h.includes('href="assets/financiamento.css"'));
  assert.match(h, /<title>[^<]*Simulador de Financiamento/);
  for (const p of ['Imóvel', 'Renda', 'Idade', 'Perfil', 'Condições']) assert.ok(h.includes(p), p);
  assert.ok(!h.includes('Cabe financiar'));
});

test('home leva ao Simulador de Financiamento no card, no cabeçalho e no menu', () => {
  const h = ler('index.html');
  const links = [...h.matchAll(/<a\b[^>]*href="simulador-financiamento\.html"/g)];
  assert.equal(links.length, 3);
  const grid = h.slice(h.indexOf('class="tool-grid"'));
  assert.ok(grid.indexOf('simulador-associativo.html') < grid.indexOf('simulador-financiamento.html'));
  assert.ok(grid.includes('Simulador de Financiamento'));
});

test('PDF não mostra a tabela de seguradoras nem o "a negociar"', () => {
  const p = ler('assets/financiamento-pdf.js');
  assert.ok(!p.includes('Parcela por seguradora'));
  assert.ok(!p.includes('a negociar'));
});

test('as três páginas carregam o morph antes dos módulos da tela e do popup', () => {
  for (const [f, m] of [['simulador-financiamento.html', 'financiamento-app.js'], ['simulador-associativo.html', 'financiamento-popup.js'], ['simulador-associativo-blackfriday.html', 'financiamento-popup.js']]) {
    const h = ler(f);
    assert.ok(h.includes('src="assets/financiamento-ui.js"'), f);
    assert.ok(h.indexOf('financiamento-ui.js') < h.indexOf(m), f);
  }
});

test('resultado: sem o card de PDF, com o aviso novo', () => {
  const a = ler('assets/financiamento-app.js');
  assert.ok(!a.includes('PDF para o cliente</h3>'));
  assert.ok(!a.includes('Da planilha'));
  assert.ok(a.includes('Estimativa de Simulação Habitacional CAIXA. Sujeita à análise de crédito da CAIXA e à aprovação da Direcional.'));
});

test('resultado: a tabela fica dentro do card e os textos riscados saíram', () => {
  const a = ler('assets/financiamento-app.js');
  assert.ok(!a.includes('</table></div>'), 'um </div> a mais fecha a coluna principal antes da hora');
  assert.ok(!a.includes("% da renda (' + F.brl(s.parcelaMax)"));
  assert.ok(!ler('assets/financiamento-pdf.js').includes('Grupo Direcional'));
});

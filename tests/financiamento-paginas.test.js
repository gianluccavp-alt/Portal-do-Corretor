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

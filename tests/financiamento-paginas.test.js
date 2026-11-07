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

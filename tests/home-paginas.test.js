const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const RAIZ = path.join(__dirname, '..');

function ler(rel) {
  const p = path.join(RAIZ, rel);
  return fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : '';
}

const INDEX = ler('index.html');
const EMBREVE = ler('em-breve.html');
const CSS = ler('assets/home.css');

const ctx = { window: {} };
vm.createContext(ctx);
vm.runInContext(ler('assets/config.js'), ctx);
const CITIES = ctx.window.CITIES;

test('cada cidade tem foto 1200 e 640 no repositório', () => {
  for (const c of CITIES) {
    assert.equal(c.foto, `assets/img/cidades/${c.id}.webp`);
    assert.ok(fs.existsSync(path.join(RAIZ, c.foto)), c.foto);
    assert.ok(fs.existsSync(path.join(RAIZ, c.foto.replace('.webp', '@640.webp'))));
  }
});

test('ícones 3D dos simuladores existem', () => {
  for (const n of ['calculadora', 'tabela']) assert.ok(fs.existsSync(path.join(RAIZ, `assets/img/icones-3d/${n}.svg`)));
});

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

test('index tem abertura com logo grande e decide antes do primeiro desenho', () => {
  assert.match(INDEX, /<div class="abertura" aria-hidden="true">\s*<img[^>]*src="assets\/img\/logo-direcional\.jpg"/);
  assert.ok(INDEX.indexOf('Home.deveMostrarAbertura') > 0);
  assert.ok(INDEX.indexOf('Home.deveMostrarAbertura') < INDEX.indexOf('class="site-header"'));
  assert.ok(INDEX.indexOf('assets/home.js') < INDEX.indexOf('</head>'));
});

test('redução de movimento desliga abertura e entrada', () => {
  const bloco = CSS.slice(CSS.indexOf('prefers-reduced-motion'));
  assert.match(bloco, /\.abertura\s*\{[^}]*display:\s*none/);
  assert.match(bloco, /\.entra[^{]*\{[^}]*animation:\s*none/);
});

test('Match de Unidades leva para em-breve.html na home', () => {
  const links = [...INDEX.matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>(?:(?!<\/a>)[\s\S])*Match de Unidades/g)].map((m) => m[1]);
  assert.ok(links.length >= 2);   /* navbar + card; a Task 7 soma o link da folha do menu */
  assert.ok(links.every((h) => h === 'em-breve.html'));
});

test('em-breve.html tem o texto aprovado e volta para a home', () => {
  assert.match(EMBREVE, /Em breve/);
  assert.match(EMBREVE, /<h1[^>]*>Match de Unidades<\/h1>/);
  assert.ok(EMBREVE.includes('Estamos finalizando essa ferramenta. Em breve ela estará disponível aqui no portal.'));
  assert.match(EMBREVE, /href="index\.html"[^>]*>[\s\S]*?Voltar para o início/);
  assert.match(EMBREVE, /href="em-breve\.html"[^>]*aria-current="page"/);
});

test('home sem Passo, sem descrições e sem aviso da planilha', () => {
  assert.ok(!/Passo \d/.test(INDEX));
  assert.ok(!INDEX.includes('Dados carregados diretamente da planilha oficial'));
  assert.ok(!INDEX.includes('tool-desc'));
  assert.ok(INDEX.includes('Unidades, valores, plantas e disponibilidade<'));
});

test('home e em-breve têm o botão do menu mobile ligado à folha', () => {
  for (const [nome, html] of [['index', INDEX], ['em-breve', EMBREVE]]) {
    assert.match(html, /<button[^>]*id="menu-btn"[^>]*aria-expanded="false"[^>]*aria-controls="menu-folha"[^>]*aria-label="Abrir menu"/, nome);
    assert.match(html, /<nav[^>]*id="menu-folha"[^>]*hidden/, nome);
    assert.ok(html.includes('assets/menu.js'), nome);
  }
});

test('cabeçalho fica fixo: body não vira contêiner de rolagem', () => {
  const semComentarios = CSS.replace(/\/\*[\s\S]*?\*\//g, '');
  assert.ok(!/(^|[\s,}])body\s*(,[^{]*)?\{[^}]*overflow-x:\s*hidden/.test(semComentarios), 'overflow-x:hidden no body quebra o position:sticky do cabeçalho');
  assert.match(CSS, /\.site-header\{[^}]*position:sticky/);
});

test('escala-comercial-rp mantém o cabeçalho e o rodapé de antes da Home V2', () => {
  const ESCALA = ler('escala-comercial-rp.html');
  assert.ok(ESCALA.includes('assets/home.css'));
  assert.match(ESCALA, /--wrap:\s*1100px/);
  assert.match(ESCALA, /\.site-header\s*\{[^}]*height:\s*64px[^}]*background:\s*#fff/);
  assert.match(ESCALA, /\.brand-logo\s*\{[^}]*height:\s*24px/);
  assert.match(ESCALA, /\.home-foot\s*\{[^}]*margin-top:\s*3\.5rem/);
});

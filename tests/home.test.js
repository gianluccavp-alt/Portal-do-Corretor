const test = require('node:test');
const assert = require('node:assert/strict');
const H = require('../assets/home.js');

test('rotuloEmpreendimentos singular e plural', () => {
  assert.equal(H.rotuloEmpreendimentos(1), '1 empreendimento');
  assert.equal(H.rotuloEmpreendimentos(5), '5 empreendimentos');
});

test('cardCidadeHTML com foto, contagem e escape', () => {
  const html = H.cardCidadeHTML({ id: 'x', name: 'A<b>&"', uf: 'SP', foto: 'assets/img/cidades/x.webp', empreendimentos: [{}, {}] });
  assert.match(html, /class="city-photo"[^>]*src="assets\/img\/cidades\/x\.webp"/);
  assert.match(html, /x@640\.webp 640w/);
  assert.match(html, /onerror="this\.remove\(\)"/);
  assert.match(html, /<strong>2<\/strong>/);
  assert.match(html, /empreendimentos/);
  assert.ok(html.includes('A&lt;b&gt;&amp;&quot;'));
  assert.ok(!html.includes('A<b>'));
});

test('cardCidadeHTML sem foto não gera <img> de foto', () => {
  const html = H.cardCidadeHTML({ id: 'x', name: 'X', uf: 'SP', empreendimentos: [] });
  assert.ok(!html.includes('city-photo'));
  assert.match(html, /<strong>0<\/strong>/);
});

test('cardEmpreendimentoHTML: link normal e em breve', () => {
  const a = H.cardEmpreendimentoHTML({ id: 'village-park', nome: 'Village Park', heroImg: 'x.jpg' });
  assert.deepEqual([a.tag, a.className, a.href], ['a', 'emp-card', 'empreendimento.html?e=village-park']);
  assert.match(a.html, /assets\/img\/cards\/village-park@640\.webp 640w/);
  const s = H.cardEmpreendimentoHTML({ id: 'u', nome: 'Universo', cardNome: 'Universo <PA>', heroImg: 'x.jpg', comingSoon: true });
  assert.deepEqual([s.tag, s.className, s.href], ['div', 'emp-card emp-card-soon', null]);
  assert.match(s.html, /Em breve/);
  assert.ok(s.html.includes('Universo &lt;PA&gt;'));
  const ph = H.cardEmpreendimentoHTML({ id: 'z', nome: 'Z' });
  assert.match(ph.html, /Imagens em breve/);
});

test('deveMostrarAbertura: primeira vez, repetida, storage quebrado', () => {
  const mem = { d: {}, getItem(k) { return this.d[k] ?? null; }, setItem(k, v) { this.d[k] = v; } };
  assert.equal(H.deveMostrarAbertura(mem), true);
  assert.equal(mem.d['pc-abertura-vista'], '1');
  assert.equal(H.deveMostrarAbertura(mem), false);
  assert.equal(H.deveMostrarAbertura(null), true);
  assert.equal(H.deveMostrarAbertura({ getItem() { throw new Error('bloqueado'); } }), true);
  assert.equal(H.deveMostrarAbertura({ getItem() { return null; }, setItem() { throw new Error('cheio'); } }), true);
});

test('indiceSlide arredonda e limita', () => {
  assert.equal(H.indiceSlide(0, 300, 5), 0);
  assert.equal(H.indiceSlide(460, 300, 5), 2);
  assert.equal(H.indiceSlide(99999, 300, 5), 4);
  assert.equal(H.indiceSlide(100, 0, 5), 0);
});

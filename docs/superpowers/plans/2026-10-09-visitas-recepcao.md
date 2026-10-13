# Visitas da Recepção — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar `/visitas-recepcao` (lançamento público de visitas no stand, com contador do dia) e `/visitas-recepcao-adm` (dashboard com senha), gravando numa aba `VISITAS` de uma planilha nova via Web App do Apps Script.

**Architecture:** Site estático (HTML/CSS/JS puro, sem build), no padrão de `/pendencias-vendas`. As regras puras ficam em `assets/visitas.js` (testadas com `node --test`). A chamada à API e o modo demonstração ficam em `assets/visitas-api.js`, e cada página tem seu próprio `*-app.js`. O backend é `docs/apps-script-visitas.gs`. As funções puras dele (validação, leitura de linha, sugestões) também são testadas no Node via `vm`.

**Tech Stack:** HTML/CSS/JS ES5 (`var`, `function`, sem módulos), Google Apps Script (V8), `node --test` sem dependências.

**Spec:** `docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md`. Leia antes de começar. As telas aprovadas estão no canvas "Visitas Recepção": https://claude.ai/artifact/254FTbPxSoAVKMsPvJd8vV

## Global Constraints

- Sem dependências npm, sem build. JS no estilo do repo: IIFE, `'use strict'`, `var`, `function`, comentários curtos em português sem acento (como `assets/pendencias.js`).
- Módulos puros exportam em `module.exports` (Node) **e** `window.<Nome>` (navegador), como `assets/pendencias.js`.
- Testes: `node --test tests/*.test.js` (Node ≥ 18).
- Visual: `DESIGN.md` — DM Sans, vermelho `#E4032B` (hover `#B8001F`) só para ação/estado, tinta `#3A4043`, ardósia `#727A7D`, borda `#E7E9EA`, fundo `#F5F6F7`, foco = borda vermelha + `0 0 0 3px rgba(228,3,43,.10)`.
- Cores dos tipos: Espontânea `#3A4043`, Corretor house `#E4032B`, Imobiliária `#A3ABAE`.
- Códigos dos tipos: `esp`, `house`, `imob`. Nomes: `Espontânea`, `Corretor house`, `Imobiliária`.
- Formato de visita trafegado (cliente ↔ Web App): `{ id, data: 'yyyy-MM-dd', hora: 'HH:mm', empreendimento, cidade, tipo, corretorHouse, imobiliaria, corretorImob }`.
- `cidade` é o `name` da cidade em `window.CITIES` (`Campinas`, `Ribeirão Preto`, `Sorocaba`).
- Textos livres: `trim`, espaços repetidos viram um só, máximo **80** caracteres.
- Neutralização de fórmula: texto que começa com `=`, `+`, `-`, `@`, tab ou CR ganha `'` na frente (ao gravar na planilha e no CSV).
- Todo texto vindo da API vai para o DOM com `textContent` / `createTextNode`, **nunca** `innerHTML`.
- POST com `Content-Type: text/plain;charset=utf-8`. Timeout de 20 s no cliente.
- Fuso do servidor: `America/Sao_Paulo`.
- A senha do admin (`Comercial123`) **não entra no repositório**: fica só na Script Property `VISITAS_SENHA` (ver Task 4).
- Mensagens de erro do cliente: rede → "Sem conexão. Tente de novo."; `ocupado` → "Muitos lançamentos ao mesmo tempo, tente de novo."; `coluna`/`interno`/formato inválido → "Erro na planilha de visitas. Avise o comercial."; demais → mensagem do servidor.
- Commits: `tipo(visitas): descrição`, terminando com a linha `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Branch: `feat/visitas-recepcao` (já existe, com a spec commitada).

## File Structure

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `assets/visitas.js` | criar | Regras puras: texto, datas, formulário, agregações, CSV |
| `tests/fixtures/visitas.json` | criar | 8 visitas fictícias para os testes |
| `tests/visitas-regras.test.js` | criar | Testes de texto, datas, formulário |
| `tests/visitas-dashboard.test.js` | criar | Testes de agregações e CSV |
| `docs/apps-script-visitas.gs` | criar | Web App (registrar, dia, excluir, listar) + instruções de implantação |
| `tests/visitas-gs.test.js` | criar | Testes das funções puras do `.gs` + paridade de empreendimentos |
| `assets/visitas-api.js` | criar | `fetch` ao Web App + modo demonstração em memória |
| `assets/config.js` | modificar (fim do arquivo) | `window.VISITAS_APPS_SCRIPT_URL` |
| `visitas-recepcao.html` | criar | Página da recepção (markup + CSS) |
| `assets/visitas-recepcao-app.js` | criar | Interface da recepção |
| `visitas-recepcao-adm.html` | criar | Página do dashboard (markup + CSS) |
| `assets/visitas-adm-app.js` | criar | Interface do dashboard |
| `README.md` | modificar | Estrutura + seção das visitas |

---

### Task 1: Regras puras: texto, datas e formulário

**Files:**
- Create: `assets/visitas.js`
- Test: `tests/visitas-regras.test.js`

**Interfaces:**
- Produces (em `module.exports` e `window.Visitas`):
  - `TIPOS: { esp|house|imob: { nome, cor } }`, `ORDEM_TIPOS: ['esp','house','imob']`, `MAX_TEXTO: 80`
  - `normalizarTexto(s) → string`, `chaveNome(s) → string`, `neutralizarFormula(s) → string`, `detalhe(visita) → string`
  - `somarDias(iso, n) → iso`, `diasEntre(de, ate) → number` (inclusivo), `dataLocalIso(Date) → iso`, `horaLocal(Date) → 'HH:mm'`, `dataCurta(iso) → 'dd/MM'`, `dataBr(iso) → 'dd/MM/yyyy'`, `rotuloDia(iso) → 'qui 08/10'`
  - `intervalo(periodo: 'hoje'|'7'|'30', hoje: iso) → { de, ate, dias }`
  - `validarFormulario({ empreendimento, data, hora, tipo, imobiliaria }) → { ok, faltando: 'empreendimento'|'data'|'hora'|'tipo'|'imobiliaria'|null }`
  - `listaEmpreendimentos(cidades /* window.CITIES */) → [{ nome, cidade }]`

- [ ] **Step 1: Write the failing test**

Create `tests/visitas-regras.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const V = require('../assets/visitas.js');

test('normalizarTexto: trim, espaços e limite de 80', () => {
  assert.equal(V.normalizarTexto('  Imob   Ápice  '), 'Imob Ápice');
  assert.equal(V.normalizarTexto(null), '');
  assert.equal(V.normalizarTexto(undefined), '');
  assert.equal(V.normalizarTexto('x'.repeat(100)).length, 80);
});

test('chaveNome ignora caixa, acento e espaços', () => {
  assert.equal(V.chaveNome(' Imobiliária  ÁPICE '), 'imobiliaria apice');
  assert.equal(V.chaveNome('imobiliaria apice'), 'imobiliaria apice');
});

test('neutralizarFormula prefixa apóstrofo só quando começa com = + - @ tab CR', () => {
  assert.equal(V.neutralizarFormula('=1+1'), "'=1+1");
  assert.equal(V.neutralizarFormula('+55'), "'+55");
  assert.equal(V.neutralizarFormula('-x'), "'-x");
  assert.equal(V.neutralizarFormula('@soma'), "'@soma");
  assert.equal(V.neutralizarFormula('\tA'), "'\tA");
  assert.equal(V.neutralizarFormula('\rA'), "'\rA");
  assert.equal(V.neutralizarFormula('Imob Ápice'), 'Imob Ápice');
  assert.equal(V.neutralizarFormula(''), '');
  assert.equal(V.neutralizarFormula(undefined), '');
});

test('datas ISO: somar, diferença, formatos', () => {
  assert.equal(V.somarDias('2026-10-01', -1), '2026-09-30');
  assert.equal(V.somarDias('2026-12-31', 1), '2027-01-01');
  assert.equal(V.diasEntre('2026-10-03', '2026-10-09'), 7);
  assert.equal(V.diasEntre('2026-10-09', '2026-10-09'), 1);
  assert.equal(V.dataCurta('2026-10-08'), '08/10');
  assert.equal(V.dataBr('2026-10-08'), '08/10/2026');
  assert.equal(V.rotuloDia('2026-10-08'), 'qui 08/10');
});

test('dataLocalIso e horaLocal usam a hora local do aparelho', () => {
  const d = new Date(2026, 9, 9, 7, 5);
  assert.equal(V.dataLocalIso(d), '2026-10-09');
  assert.equal(V.horaLocal(d), '07:05');
});

test('intervalo dos períodos do dashboard', () => {
  assert.deepEqual(V.intervalo('hoje', '2026-10-09'), { de: '2026-10-09', ate: '2026-10-09', dias: 1 });
  assert.deepEqual(V.intervalo('7', '2026-10-09'), { de: '2026-10-03', ate: '2026-10-09', dias: 7 });
  assert.deepEqual(V.intervalo('30', '2026-10-09'), { de: '2026-09-10', ate: '2026-10-09', dias: 30 });
});

test('validarFormulario aponta o primeiro campo que falta', () => {
  const base = { empreendimento: 'Alta Vista Mangará', data: '2026-10-09', hora: '14:35', tipo: 'esp' };
  assert.deepEqual(V.validarFormulario(base), { ok: true, faltando: null });
  assert.equal(V.validarFormulario({ ...base, empreendimento: '' }).faltando, 'empreendimento');
  assert.equal(V.validarFormulario({ ...base, data: '' }).faltando, 'data');
  assert.equal(V.validarFormulario({ ...base, hora: '9:5' }).faltando, 'hora');
  assert.equal(V.validarFormulario({ ...base, tipo: null }).faltando, 'tipo');
  assert.equal(V.validarFormulario({ ...base, tipo: 'total' }).faltando, 'tipo');
  assert.equal(V.validarFormulario({ ...base, tipo: 'imob' }).faltando, 'imobiliaria');
  assert.equal(V.validarFormulario({ ...base, tipo: 'imob', imobiliaria: '   ' }).faltando, 'imobiliaria');
  assert.equal(V.validarFormulario({ ...base, tipo: 'imob', imobiliaria: 'Imob Ápice' }).ok, true);
  assert.equal(V.validarFormulario({ ...base, tipo: 'house' }).ok, true);
  assert.equal(V.validarFormulario({ ...base, empreendimento: '', tipo: null }).faltando, 'empreendimento');
});

test('detalhe de cada tipo para as listas', () => {
  assert.equal(V.detalhe({ tipo: 'esp' }), 'Sem agendamento');
  assert.equal(V.detalhe({ tipo: 'house', corretorHouse: '' }), 'Corretor não informado');
  assert.equal(V.detalhe({ tipo: 'house', corretorHouse: 'Ana' }), 'Ana');
  assert.equal(V.detalhe({ tipo: 'imob', imobiliaria: 'Imob Ápice', corretorImob: '' }), 'Imob Ápice');
  assert.equal(V.detalhe({ tipo: 'imob', imobiliaria: 'Imob Ápice', corretorImob: 'Rui' }), 'Imob Ápice · Rui');
});

test('listaEmpreendimentos achata window.CITIES', () => {
  const cidades = [
    { name: 'Campinas', empreendimentos: [{ nome: 'A' }, { nome: 'B' }] },
    { name: 'Sorocaba', empreendimentos: [{ nome: 'C' }] }
  ];
  assert.deepEqual(V.listaEmpreendimentos(cidades), [
    { nome: 'A', cidade: 'Campinas' }, { nome: 'B', cidade: 'Campinas' }, { nome: 'C', cidade: 'Sorocaba' }
  ]);
  assert.deepEqual(V.listaEmpreendimentos(undefined), []);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/visitas-regras.test.js`
Expected: FAIL with `Cannot find module '../assets/visitas.js'`

- [ ] **Step 3: Write minimal implementation**

Create `assets/visitas.js`:

```js
/* ============================================================
   VISITAS DA RECEPCAO - regras puras
   ------------------------------------------------------------
   Funcoes sem DOM e sem rede. Usadas por /visitas-recepcao e
   /visitas-recepcao-adm via window.Visitas e pelos testes
   (node --test tests/*.test.js).
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md
   ============================================================ */
(function (raiz) {
  'use strict';

  var TIPOS = {
    esp: { nome: 'Espontânea', cor: '#3A4043' },
    house: { nome: 'Corretor house', cor: '#E4032B' },
    imob: { nome: 'Imobiliária', cor: '#A3ABAE' }
  };
  var ORDEM_TIPOS = ['esp', 'house', 'imob'];
  var MAX_TEXTO = 80;
  var DIA_MS = 86400000;
  var DIAS_SEMANA = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb'];

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function tipoValido(t) { return ORDEM_TIPOS.indexOf(t) >= 0; }

  /* ---------- texto ---------- */
  function normalizarTexto(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/\s+/g, ' ').trim().slice(0, MAX_TEXTO);
  }
  function chaveNome(s) {
    return normalizarTexto(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }
  /* evita que a planilha/Excel interprete o texto como formula */
  function neutralizarFormula(s) {
    var t = s === null || s === undefined ? '' : String(s);
    return /^[=+\-@\t\r]/.test(t) ? "'" + t : t;
  }
  function detalhe(v) {
    if (v.tipo === 'house') return v.corretorHouse || 'Corretor não informado';
    if (v.tipo === 'imob') return v.imobiliaria + (v.corretorImob ? ' · ' + v.corretorImob : '');
    return 'Sem agendamento';
  }

  /* ---------- datas (ISO yyyy-MM-dd, sem fuso) ---------- */
  function isoParaMs(iso) { var p = iso.split('-'); return Date.UTC(+p[0], +p[1] - 1, +p[2]); }
  function msParaIso(ms) {
    var d = new Date(ms);
    return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate());
  }
  function somarDias(iso, n) { return msParaIso(isoParaMs(iso) + n * DIA_MS); }
  function diasEntre(de, ate) { return Math.round((isoParaMs(ate) - isoParaMs(de)) / DIA_MS) + 1; }
  function dataLocalIso(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function horaLocal(d) { return pad(d.getHours()) + ':' + pad(d.getMinutes()); }
  function dataCurta(iso) { var p = iso.split('-'); return p[2] + '/' + p[1]; }
  function dataBr(iso) { var p = iso.split('-'); return p[2] + '/' + p[1] + '/' + p[0]; }
  function rotuloDia(iso) { return DIAS_SEMANA[new Date(isoParaMs(iso)).getUTCDay()] + ' ' + dataCurta(iso); }
  function intervalo(periodo, hoje) {
    var n = periodo === 'hoje' ? 1 : Number(periodo);
    return { de: somarDias(hoje, -(n - 1)), ate: hoje, dias: n };
  }

  /* ---------- formulario da recepcao (spec 5.1) ---------- */
  function validarFormulario(d) {
    var regras = [
      ['empreendimento', !normalizarTexto(d.empreendimento)],
      ['data', !/^\d{4}-\d{2}-\d{2}$/.test(d.data || '')],
      ['hora', !/^\d{2}:\d{2}$/.test(d.hora || '')],
      ['tipo', !tipoValido(d.tipo)],
      ['imobiliaria', d.tipo === 'imob' && !normalizarTexto(d.imobiliaria)]
    ];
    for (var i = 0; i < regras.length; i++) {
      if (regras[i][1]) return { ok: false, faltando: regras[i][0] };
    }
    return { ok: true, faltando: null };
  }

  function listaEmpreendimentos(cidades) {
    var out = [];
    (cidades || []).forEach(function (c) {
      (c.empreendimentos || []).forEach(function (e) { out.push({ nome: e.nome, cidade: c.name }); });
    });
    return out;
  }

  var api = {
    TIPOS: TIPOS,
    ORDEM_TIPOS: ORDEM_TIPOS,
    MAX_TEXTO: MAX_TEXTO,
    normalizarTexto: normalizarTexto,
    chaveNome: chaveNome,
    neutralizarFormula: neutralizarFormula,
    detalhe: detalhe,
    somarDias: somarDias,
    diasEntre: diasEntre,
    dataLocalIso: dataLocalIso,
    horaLocal: horaLocal,
    dataCurta: dataCurta,
    dataBr: dataBr,
    rotuloDia: rotuloDia,
    intervalo: intervalo,
    validarFormulario: validarFormulario,
    listaEmpreendimentos: listaEmpreendimentos
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.Visitas = api;
})(this);
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/visitas-regras.test.js`
Expected: PASS (9 tests)

- [ ] **Step 5: Commit**

```bash
git add assets/visitas.js tests/visitas-regras.test.js
git commit -m "feat(visitas): regras puras de texto, datas e formulario

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Agregações do dashboard

**Files:**
- Modify: `assets/visitas.js` (nova seção antes de `var api = {` + entradas novas no objeto `api`)
- Create: `tests/fixtures/visitas.json`
- Test: `tests/visitas-dashboard.test.js`

**Interfaces:**
- Consumes: `somarDias`, `diasEntre`, `normalizarTexto`, `chaveNome`, `ORDEM_TIPOS` (Task 1)
- Produces:
  - `filtrar(visitas, { de?, ate?, cidade?, empreendimento? }) → visitas` (`'Todas'`/`'Todos'`/vazio = sem filtro)
  - `totaisPorTipo(visitas) → { esp, house, imob, total }`
  - `porDia(visitas, de, ate) → [{ data, esp, house, imob, total }]` (um item por dia, inclusive zerados)
  - `porHora(visitas, ini, fim) → [{ hora: number, esp, house, imob, total }]` (fora da faixa vai para a ponta)
  - `porEmpreendimento(visitas, lista [{nome,cidade}]) → [{ nome, cidade, esp, house, imob, total }]` (ordenado por total desc, depois nome)
  - `rankingImobiliarias(visitas, n) → [{ nome, qtd }]`
  - `ordenarPorTempo(visitas, desc: boolean) → visitas`, `recentes(visitas, n) → visitas`

- [ ] **Step 1: Write the fixture**

Create `tests/fixtures/visitas.json` (dados fictícios):

```json
[
  { "id": "V1", "data": "2026-10-07", "hora": "09:10", "empreendimento": "Alta Vista Mangará", "cidade": "Campinas", "tipo": "esp", "corretorHouse": "", "imobiliaria": "", "corretorImob": "" },
  { "id": "V2", "data": "2026-10-07", "hora": "10:05", "empreendimento": "Alta Vista Mangará", "cidade": "Campinas", "tipo": "imob", "corretorHouse": "", "imobiliaria": "Imobiliária Ápice", "corretorImob": "Corretor Teste" },
  { "id": "V3", "data": "2026-10-07", "hora": "21:30", "empreendimento": "Village Park", "cidade": "Ribeirão Preto", "tipo": "house", "corretorHouse": "Corretor House Teste", "imobiliaria": "", "corretorImob": "" },
  { "id": "V4", "data": "2026-10-08", "hora": "07:45", "empreendimento": "Village Park", "cidade": "Ribeirão Preto", "tipo": "imob", "corretorHouse": "", "imobiliaria": "imobiliaria apice ", "corretorImob": "" },
  { "id": "V5", "data": "2026-10-08", "hora": "14:00", "empreendimento": "Alta Vista Mangará", "cidade": "Campinas", "tipo": "imob", "corretorHouse": "", "imobiliaria": "Imobiliária Ápice", "corretorImob": "" },
  { "id": "V6", "data": "2026-10-09", "hora": "11:20", "empreendimento": "Alta Vista Mangará", "cidade": "Campinas", "tipo": "imob", "corretorHouse": "", "imobiliaria": "Imóveis Beta", "corretorImob": "" },
  { "id": "V7", "data": "2026-10-09", "hora": "11:50", "empreendimento": "Conquista Vila da Mata", "cidade": "Sorocaba", "tipo": "esp", "corretorHouse": "", "imobiliaria": "", "corretorImob": "" },
  { "id": "V8", "data": "2026-10-09", "hora": "15:15", "empreendimento": "Alta Vista Mangará", "cidade": "Campinas", "tipo": "house", "corretorHouse": "", "imobiliaria": "", "corretorImob": "" }
]
```

- [ ] **Step 2: Write the failing test**

Create `tests/visitas-dashboard.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const V = require('../assets/visitas.js');
const FIX = require('./fixtures/visitas.json');

const ids = (lista) => lista.map((v) => v.id);
const semData = ({ esp, house, imob, total }) => ({ esp, house, imob, total });

test('filtrar por período, cidade e empreendimento', () => {
  assert.equal(V.filtrar(FIX, {}).length, 8);
  assert.equal(V.filtrar(FIX, { cidade: 'Todas', empreendimento: 'Todos' }).length, 8);
  assert.deepEqual(ids(V.filtrar(FIX, { cidade: 'Campinas' })), ['V1', 'V2', 'V5', 'V6', 'V8']);
  assert.deepEqual(ids(V.filtrar(FIX, { de: '2026-10-09' })), ['V6', 'V7', 'V8']);
  assert.deepEqual(ids(V.filtrar(FIX, { empreendimento: 'Village Park', ate: '2026-10-07' })), ['V3']);
});

test('totaisPorTipo', () => {
  assert.deepEqual(V.totaisPorTipo(FIX), { esp: 2, house: 2, imob: 4, total: 8 });
  assert.deepEqual(V.totaisPorTipo([]), { esp: 0, house: 0, imob: 0, total: 0 });
  assert.deepEqual(V.totaisPorTipo([{ tipo: 'total' }, { tipo: '' }]), { esp: 0, house: 0, imob: 0, total: 0 });
});

test('porDia inclui dias sem visita', () => {
  const dias = V.porDia(FIX, '2026-10-06', '2026-10-09');
  assert.deepEqual(dias.map((d) => d.data), ['2026-10-06', '2026-10-07', '2026-10-08', '2026-10-09']);
  assert.deepEqual(semData(dias[0]), { esp: 0, house: 0, imob: 0, total: 0 });
  assert.deepEqual(semData(dias[1]), { esp: 1, house: 1, imob: 1, total: 3 });
  assert.deepEqual(semData(dias[2]), { esp: 0, house: 0, imob: 2, total: 2 });
  assert.deepEqual(semData(dias[3]), { esp: 1, house: 1, imob: 1, total: 3 });
});

test('porHora joga visitas fora da faixa para as pontas', () => {
  const horas = V.porHora(FIX, 8, 20);
  assert.equal(horas.length, 13);
  assert.equal(horas[0].hora, 8);
  assert.deepEqual(semData(horas[0]), { esp: 0, house: 0, imob: 1, total: 1 }); /* V4 07:45 */
  assert.equal(horas[1].total, 1); /* V1 09:10 */
  assert.equal(horas[3].total, 2); /* V6 e V7 11h */
  assert.deepEqual(semData(horas[12]), { esp: 0, house: 1, imob: 0, total: 1 }); /* V3 21:30 */
  const soma = horas.reduce((a, h) => a + h.total, 0);
  assert.equal(soma, 8);
});

test('porEmpreendimento mostra zerados e ordena por total', () => {
  const lista = [
    { nome: 'Seleto Amoreiras', cidade: 'Campinas' },
    { nome: 'Village Park', cidade: 'Ribeirão Preto' },
    { nome: 'Alta Vista Mangará', cidade: 'Campinas' },
    { nome: 'Conquista Vila da Mata', cidade: 'Sorocaba' }
  ];
  const linhas = V.porEmpreendimento(FIX, lista);
  assert.deepEqual(linhas.map((l) => [l.nome, l.total]), [
    ['Alta Vista Mangará', 5], ['Village Park', 2], ['Conquista Vila da Mata', 1], ['Seleto Amoreiras', 0]
  ]);
  assert.deepEqual(semData(linhas[0]), { esp: 1, house: 1, imob: 3, total: 5 });
  assert.equal(linhas[0].cidade, 'Campinas');
});

test('rankingImobiliarias agrupa sem caixa e sem acento e usa a grafia mais comum', () => {
  assert.deepEqual(V.rankingImobiliarias(FIX, 5), [
    { nome: 'Imobiliária Ápice', qtd: 3 },
    { nome: 'Imóveis Beta', qtd: 1 }
  ]);
  assert.equal(V.rankingImobiliarias(FIX, 1).length, 1);
});

test('recentes ordena por data e hora, mais novo primeiro', () => {
  assert.deepEqual(ids(V.recentes(FIX, 3)), ['V8', 'V7', 'V6']);
  assert.deepEqual(ids(V.ordenarPorTempo(FIX, false)).slice(0, 2), ['V1', 'V2']);
  assert.equal(FIX[0].id, 'V1'); /* nao muta a entrada */
});
```

- [ ] **Step 3: Run test to verify it fails**

Run: `node --test tests/visitas-dashboard.test.js`
Expected: FAIL with `V.filtrar is not a function`

- [ ] **Step 4: Write minimal implementation**

In `assets/visitas.js`, insert this block right **before** `var api = {`:

```js
  /* ---------- agregacoes do dashboard (spec 6.2) ---------- */
  function vazioTipos() { return { esp: 0, house: 0, imob: 0, total: 0 }; }
  function somar(acc, v) {
    if (tipoValido(v.tipo)) { acc[v.tipo]++; acc.total++; }
    return acc;
  }
  function totaisPorTipo(visitas) { return visitas.reduce(somar, vazioTipos()); }

  function filtrar(visitas, f) {
    f = f || {};
    return visitas.filter(function (v) {
      if (f.de && v.data < f.de) return false;
      if (f.ate && v.data > f.ate) return false;
      if (f.cidade && f.cidade !== 'Todas' && v.cidade !== f.cidade) return false;
      if (f.empreendimento && f.empreendimento !== 'Todos' && v.empreendimento !== f.empreendimento) return false;
      return true;
    });
  }

  function porDia(visitas, de, ate) {
    var n = diasEntre(de, ate), indice = {}, out = [];
    for (var i = 0; i < n; i++) {
      var linha = vazioTipos();
      linha.data = somarDias(de, i);
      indice[linha.data] = linha;
      out.push(linha);
    }
    visitas.forEach(function (v) { if (indice[v.data]) somar(indice[v.data], v); });
    return out;
  }

  function porHora(visitas, ini, fim) {
    var out = [];
    for (var h = ini; h <= fim; h++) { var linha = vazioTipos(); linha.hora = h; out.push(linha); }
    visitas.forEach(function (v) {
      var hora = parseInt(String(v.hora).slice(0, 2), 10);
      if (isNaN(hora)) return;
      somar(out[Math.min(Math.max(hora, ini), fim) - ini], v);
    });
    return out;
  }

  function porEmpreendimento(visitas, lista) {
    var indice = {};
    var out = lista.map(function (e) {
      var linha = vazioTipos();
      linha.nome = e.nome;
      linha.cidade = e.cidade;
      indice[e.nome] = linha;
      return linha;
    });
    visitas.forEach(function (v) { if (indice[v.empreendimento]) somar(indice[v.empreendimento], v); });
    return out.sort(function (a, b) { return b.total - a.total || a.nome.localeCompare(b.nome, 'pt-BR'); });
  }

  /* agrupa nomes sem caixa/acento; o nome exibido e a grafia mais frequente */
  function agruparNomes(nomes) {
    var grupos = {}, ordem = [];
    nomes.forEach(function (bruto) {
      var nome = normalizarTexto(bruto), k = chaveNome(nome);
      if (!k) return;
      if (!grupos[k]) { grupos[k] = { qtd: 0, grafias: {} }; ordem.push(k); }
      grupos[k].qtd++;
      grupos[k].grafias[nome] = (grupos[k].grafias[nome] || 0) + 1;
    });
    return ordem.map(function (k) {
      var g = grupos[k], melhor = null;
      Object.keys(g.grafias).forEach(function (n) { if (melhor === null || g.grafias[n] > g.grafias[melhor]) melhor = n; });
      return { nome: melhor, qtd: g.qtd };
    });
  }

  function rankingImobiliarias(visitas, n) {
    var nomes = visitas.filter(function (v) { return v.tipo === 'imob'; }).map(function (v) { return v.imobiliaria; });
    return agruparNomes(nomes)
      .sort(function (a, b) { return b.qtd - a.qtd || a.nome.localeCompare(b.nome, 'pt-BR'); })
      .slice(0, n);
  }

  function chaveTempo(v) { return v.data + ' ' + v.hora; }
  function ordenarPorTempo(visitas, desc) {
    return visitas.slice().sort(function (a, b) {
      var ka = chaveTempo(a), kb = chaveTempo(b);
      var c = ka < kb ? -1 : ka > kb ? 1 : 0;
      return desc ? -c : c;
    });
  }
  function recentes(visitas, n) { return ordenarPorTempo(visitas, true).slice(0, n); }

```

Then add these entries to the `api` object (after `listaEmpreendimentos: listaEmpreendimentos`, adding a comma to that line):

```js
    listaEmpreendimentos: listaEmpreendimentos,
    filtrar: filtrar,
    totaisPorTipo: totaisPorTipo,
    porDia: porDia,
    porHora: porHora,
    porEmpreendimento: porEmpreendimento,
    rankingImobiliarias: rankingImobiliarias,
    ordenarPorTempo: ordenarPorTempo,
    recentes: recentes
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `node --test tests/*.test.js`
Expected: PASS (todos, incluindo os das pendências)

- [ ] **Step 6: Commit**

```bash
git add assets/visitas.js tests/visitas-dashboard.test.js tests/fixtures/visitas.json
git commit -m "feat(visitas): agregacoes do dashboard e fixture ficticia

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: CSV do dashboard

**Files:**
- Modify: `assets/visitas.js` (nova seção antes de `var api = {` + entradas no `api`)
- Test: `tests/visitas-dashboard.test.js` (acrescentar testes no fim)

**Interfaces:**
- Consumes: `neutralizarFormula`, `dataBr`, `ordenarPorTempo`, `TIPOS`
- Produces: `gerarCSV(visitas) → string` (BOM + `;` + CRLF, ordem cronológica), `nomeArquivoCSV(de, ate) → 'visitas-AAAA-MM-DD-a-AAAA-MM-DD.csv'`

- [ ] **Step 1: Write the failing test**

Append to `tests/visitas-dashboard.test.js`:

```js
test('gerarCSV: BOM, separador ;, ordem cronológica, aspas e neutralização', () => {
  const visitas = [
    { data: '2026-10-09', hora: '11:50', empreendimento: 'Conquista Vila da Mata', cidade: 'Sorocaba', tipo: 'esp', corretorHouse: '', imobiliaria: '', corretorImob: '' },
    { data: '2026-10-08', hora: '14:00', empreendimento: 'Alta Vista Mangará', cidade: 'Campinas', tipo: 'imob', corretorHouse: '', imobiliaria: 'Imob; Centro', corretorImob: '=HYPERLINK("x")' }
  ];
  const esperado = '﻿' +
    'Data;Horário;Empreendimento;Cidade;Tipo;Corretor house;Imobiliária;Corretor imobiliária\r\n' +
    '08/10/2026;14:00;Alta Vista Mangará;Campinas;Imobiliária;;"Imob; Centro";"\'=HYPERLINK(""x"")"\r\n' +
    '09/10/2026;11:50;Conquista Vila da Mata;Sorocaba;Espontânea;;;\r\n';
  assert.equal(V.gerarCSV(visitas), esperado);
});

test('gerarCSV vazio tem só o cabeçalho', () => {
  assert.equal(V.gerarCSV([]), '﻿Data;Horário;Empreendimento;Cidade;Tipo;Corretor house;Imobiliária;Corretor imobiliária\r\n');
});

test('nomeArquivoCSV', () => {
  assert.equal(V.nomeArquivoCSV('2026-10-03', '2026-10-09'), 'visitas-2026-10-03-a-2026-10-09.csv');
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/visitas-dashboard.test.js`
Expected: FAIL with `V.gerarCSV is not a function`

- [ ] **Step 3: Write minimal implementation**

In `assets/visitas.js`, insert right **before** `var api = {`:

```js
  /* ---------- CSV (spec 6.2) ---------- */
  var CSV_COLUNAS = ['Data', 'Horário', 'Empreendimento', 'Cidade', 'Tipo', 'Corretor house', 'Imobiliária', 'Corretor imobiliária'];
  function celulaCSV(valor) {
    var t = neutralizarFormula(valor);
    return /[;"\r\n]/.test(t) ? '"' + t.replace(/"/g, '""') + '"' : t;
  }
  function gerarCSV(visitas) {
    var linhas = [CSV_COLUNAS.join(';')];
    ordenarPorTempo(visitas, false).forEach(function (v) {
      linhas.push([
        dataBr(v.data), v.hora, v.empreendimento, v.cidade, TIPOS[v.tipo] ? TIPOS[v.tipo].nome : v.tipo,
        v.corretorHouse, v.imobiliaria, v.corretorImob
      ].map(celulaCSV).join(';'));
    });
    /* BOM para o Excel abrir o UTF-8 com acentos certos */
    return '﻿' + linhas.join('\r\n') + '\r\n';
  }
  function nomeArquivoCSV(de, ate) { return 'visitas-' + de + '-a-' + ate + '.csv'; }

```

Add to the `api` object (after `recentes: recentes`, adding a comma to that line):

```js
    recentes: recentes,
    gerarCSV: gerarCSV,
    nomeArquivoCSV: nomeArquivoCSV
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test tests/*.test.js`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add assets/visitas.js tests/visitas-dashboard.test.js
git commit -m "feat(visitas): exportacao CSV com BOM e neutralizacao de formula

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Web App do Apps Script

**Files:**
- Create: `docs/apps-script-visitas.gs`
- Test: `tests/visitas-gs.test.js`

**Interfaces:**
- Consumes: `assets/visitas.js` `listaEmpreendimentos` e `assets/config.js` `window.CITIES` (só no teste de paridade)
- Produces (contrato HTTP, spec §4.1), usado pelas Tasks 5–7:
  - `registrar { empreendimento, data, hora, tipo, corretorHouse?, imobiliaria?, corretorImob? } → { ok, visita, token }`
  - `dia { empreendimento, data } → { ok, visitas, sugestoesImob: string[] }`
  - `excluir { id, token } → { ok, id }`
  - `listar { senha, de, ate } → { ok, visitas }`
  - Falha: `{ ok: false, erro: 'senha'|'invalido'|'nao_encontrada'|'ocupado'|'coluna'|'interno', mensagem, campo }`
- Funções puras testadas no Node: `visValidar_(req, hojeIso, agoraMin)`, `visDeLinha_(linha, ix)`, `visSugestoes_(linhas, ix, desdeIso)`, `visNeutralizar_`, `visTexto_`, `visDataValida_`, `visSomarDias_`, `visBrParaIso_`, constantes `VIS_COLUNAS`, `VISITAS_EMPREENDIMENTOS`.

> **Senha:** diferente de `apps-script-pendencias.gs`, a senha **não** fica escrita no arquivo do repo (spec §9). `configurarSenhaVisitas()` lê `VIS_SENHA_INICIAL`, que fica vazio no repo. Quem implanta cola `Comercial123` **só no editor do Apps Script**, roda a função e apaga de novo.

- [ ] **Step 1: Write the failing test**

Create `tests/visitas-gs.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const V = require('../assets/visitas.js');

function carregar(arquivo, ctx) {
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '..', arquivo), 'utf8'), ctx);
  return ctx;
}
const gs = carregar('docs/apps-script-visitas.gs', {});
const plano = (x) => JSON.parse(JSON.stringify(x));

const HOJE = '2026-10-09';
const AGORA = 14 * 60 + 35;
const base = { empreendimento: 'Alta Vista Mangará', data: HOJE, hora: '14:35', tipo: 'esp' };
const recusa = (campo) => (e) => e.codigo === 'invalido' && e.campo === campo;

test('lista de empreendimentos do .gs bate com a do config.js', () => {
  const cfg = carregar('assets/config.js', { window: {} });
  assert.deepEqual(plano(gs.VISITAS_EMPREENDIMENTOS), V.listaEmpreendimentos(cfg.window.CITIES));
});

test('visValidar_ aceita visita espontânea e define a cidade pelo servidor', () => {
  const v = plano(gs.visValidar_({ ...base, cidade: 'Outra', corretorHouse: 'Ana' }, HOJE, AGORA));
  assert.deepEqual(v, {
    empreendimento: 'Alta Vista Mangará', cidade: 'Campinas', data: HOJE, hora: '14:35', tipo: 'esp',
    corretorHouse: '', imobiliaria: '', corretorImob: ''
  });
});

test('visValidar_ recusa empreendimento e tipo fora da lista', () => {
  assert.throws(() => gs.visValidar_({ ...base, empreendimento: 'Outro' }, HOJE, AGORA), recusa('empreendimento'));
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'xyz' }, HOJE, AGORA), recusa('tipo'));
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'constructor' }, HOJE, AGORA), recusa('tipo'));
});

test('visValidar_ limita a data entre hoje e 7 dias atrás', () => {
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-10-10' }, HOJE, AGORA), recusa('data'));
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-10-01' }, HOJE, AGORA), recusa('data'));
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-02-30' }, HOJE, AGORA), recusa('data'));
  assert.equal(gs.visValidar_({ ...base, data: '2026-10-02' }, HOJE, AGORA).data, '2026-10-02');
});

test('visValidar_ recusa horário inválido ou no futuro (tolerância de 5 min)', () => {
  assert.throws(() => gs.visValidar_({ ...base, hora: '25:00' }, HOJE, AGORA), recusa('hora'));
  assert.throws(() => gs.visValidar_({ ...base, hora: '9:5' }, HOJE, AGORA), recusa('hora'));
  assert.throws(() => gs.visValidar_({ ...base, hora: '14:41' }, HOJE, AGORA), recusa('hora'));
  assert.equal(gs.visValidar_({ ...base, hora: '14:40' }, HOJE, AGORA).hora, '14:40');
  assert.equal(gs.visValidar_({ ...base, data: '2026-10-08', hora: '23:00' }, HOJE, AGORA).hora, '23:00');
});

test('visValidar_ exige imobiliária e normaliza os textos', () => {
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'imob', imobiliaria: '   ' }, HOJE, AGORA), recusa('imobiliaria'));
  const v = gs.visValidar_({ ...base, tipo: 'imob', imobiliaria: '  Imob   Ápice ', corretorImob: 'x'.repeat(100) }, HOJE, AGORA);
  assert.equal(v.imobiliaria, 'Imob Ápice');
  assert.equal(v.corretorImob.length, 80);
  assert.equal(gs.visValidar_({ ...base, tipo: 'house' }, HOJE, AGORA).corretorHouse, '');
});

test('visNeutralizar_ e helpers de data', () => {
  assert.equal(gs.visNeutralizar_('=1+1'), "'=1+1");
  assert.equal(gs.visNeutralizar_('Imob'), 'Imob');
  assert.equal(gs.visSomarDias_('2026-10-01', -1), '2026-09-30');
  assert.equal(gs.visBrParaIso_('09/10/2026 14:35:00'), '2026-10-09');
  assert.equal(gs.visBrParaIso_(''), '');
  assert.equal(gs.visDataValida_('2026-02-28'), true);
  assert.equal(gs.visDataValida_('2026-02-29'), false);
});

function indice() { const ix = {}; gs.VIS_COLUNAS.forEach((n, i) => { ix[n] = i; }); return ix; }
function linha(campos) { return gs.VIS_COLUNAS.map((n) => (campos[n] !== undefined ? campos[n] : '')); }

test('visDeLinha_ converte a linha da planilha no formato da API', () => {
  const l = linha({
    'ID': 'V1', 'Registrado em': '09/10/2026 14:35:00', 'Data': '09/10/2026', 'Horário': '14:30',
    'Empreendimento': 'Village Park', 'Cidade': 'Ribeirão Preto', 'Tipo': 'Imobiliária',
    'Imobiliária': 'Imob Ápice', 'Corretor imobiliária': 'Rui', 'Excluída': '0'
  });
  assert.deepEqual(plano(gs.visDeLinha_(l, indice())), {
    id: 'V1', data: '2026-10-09', hora: '14:30', empreendimento: 'Village Park', cidade: 'Ribeirão Preto',
    tipo: 'imob', corretorHouse: '', imobiliaria: 'Imob Ápice', corretorImob: 'Rui'
  });
});

test('visSugestoes_ agrupa, ignora excluídas e antigas, ordena', () => {
  const linhas = [
    linha({ 'Registrado em': '08/10/2026 10:00:00', 'Imobiliária': 'Imobiliária Ápice', 'Excluída': '0' }),
    linha({ 'Registrado em': '08/10/2026 11:00:00', 'Imobiliária': 'Imobiliária Ápice', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:00:00', 'Imobiliária': 'imobiliaria apice', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:30:00', 'Imobiliária': 'Beta Imóveis', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:40:00', 'Imobiliária': 'Excluída Ltda', 'Excluída': '1' }),
    linha({ 'Registrado em': '01/01/2026 09:00:00', 'Imobiliária': 'Antiga', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:50:00', 'Imobiliária': '', 'Excluída': '0' })
  ];
  assert.deepEqual(plano(gs.visSugestoes_(linhas, indice(), '2026-07-11')), ['Beta Imóveis', 'Imobiliária Ápice']);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/visitas-gs.test.js`
Expected: FAIL with `ENOENT: no such file or directory, open '.../docs/apps-script-visitas.gs'`

- [ ] **Step 3: Write the Web App**

Create `docs/apps-script-visitas.gs`:

```js
/* ============================================================
   VISITAS DA RECEPCAO - Google Apps Script Web App
   ------------------------------------------------------------
   Backend de /visitas-recepcao (publica) e /visitas-recepcao-adm
   (com senha). Grava e le a aba VISITAS da planilha de visitas.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md

   ---------- COMO PUBLICAR (uma vez) ----------
   1. Abra a planilha de visitas > Extensoes > Apps Script.
   2. Cole este arquivo inteiro no Codigo.gs (ou num arquivo "Visitas").
   3. SO NO EDITOR (nunca no repositorio): troque
        var VIS_SENHA_INICIAL = '';
      por a senha do dashboard, selecione configurarSenhaVisitas >
      Executar (autorize) e depois volte a linha para ''.
   4. Selecione testeVisitas > Executar > confira o log.
   5. Implantar > Nova implantacao > Tipo: App da Web
        Executar como: Eu
        Quem tem acesso: Qualquer pessoa
   6. Copie a URL que termina em /exec e cole em
      window.VISITAS_APPS_SCRIPT_URL no assets/config.js.
   Ao alterar o codigo: Implantar > Gerenciar implantacoes > editar >
   Nova versao (a URL /exec continua a mesma).

   ---------- EMPREENDIMENTOS ----------
   VISITAS_EMPREENDIMENTOS precisa ter os mesmos nomes de
   window.CITIES no assets/config.js. O teste
   tests/visitas-gs.test.js falha se as listas divergirem.
   ============================================================ */

var VIS_ABA = 'VISITAS';
var VIS_FUSO = 'America/Sao_Paulo';
var VIS_PROP_SENHA = 'VISITAS_SENHA';
var VIS_SENHA_INICIAL = '';
var VIS_MAX_TEXTO = 80;
var VIS_MAX_SUGESTOES = 200;
var VIS_DIAS_SUGESTOES = 90;
var VIS_DIAS_RETROATIVOS = 7;
var VIS_MAX_DIAS_LISTAR = 92;
var VIS_TIPOS = { esp: 'Espontânea', house: 'Corretor house', imob: 'Imobiliária' };
var VIS_COLUNAS = ['ID', 'Registrado em', 'Data', 'Horário', 'Empreendimento', 'Cidade', 'Tipo',
  'Corretor house', 'Imobiliária', 'Corretor imobiliária', 'Excluída', 'Token'];
var VISITAS_EMPREENDIMENTOS = [
  { nome: 'Alta Vista Mangará', cidade: 'Campinas' },
  { nome: 'Cores da Mata Mangará', cidade: 'Campinas' },
  { nome: 'Casa Prado Residencial Riva', cidade: 'Campinas' },
  { nome: 'Seleto Amoreiras', cidade: 'Campinas' },
  { nome: 'Universo - Parque Alphaville', cidade: 'Campinas' },
  { nome: 'Village Park', cidade: 'Ribeirão Preto' },
  { nome: 'Village Gaia', cidade: 'Ribeirão Preto' },
  { nome: 'Reserva Direcional Jardim Botânico', cidade: 'Ribeirão Preto' },
  { nome: 'Direcional Conquista Clube Ipiranga', cidade: 'Ribeirão Preto' },
  { nome: 'Conquista Vila da Mata', cidade: 'Sorocaba' }
];

function configurarSenhaVisitas() {
  if (!VIS_SENHA_INICIAL) throw new Error('Preencha VIS_SENHA_INICIAL so no editor antes de executar.');
  PropertiesService.getScriptProperties().setProperty(VIS_PROP_SENHA, VIS_SENHA_INICIAL);
  Logger.log('Senha do /visitas-recepcao-adm configurada. Volte VIS_SENHA_INICIAL para \'\'.');
}

function VisFalha(codigo, mensagem, campo) {
  this.codigo = codigo;
  this.message = mensagem;
  this.campo = campo || null;
}

/* ---------- HTTP ---------- */
function doGet() {
  return visJson_({ ok: false, erro: 'interno', mensagem: 'Use POST.' });
}

function doPost(e) {
  var resposta;
  try {
    var req = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    resposta = visRoteador_(req);
    resposta.ok = true;
  } catch (err) {
    resposta = err instanceof VisFalha
      ? { ok: false, erro: err.codigo, mensagem: err.message, campo: err.campo }
      : { ok: false, erro: 'interno', mensagem: String((err && err.message) || err) };
  }
  return visJson_(resposta);
}

function visJson_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function visRoteador_(req) {
  switch (req.acao) {
    case 'registrar': return visRegistrar_(req);
    case 'dia': return visDia_(req);
    case 'excluir': return visExcluir_(req);
    case 'listar': visConferirSenha_(req.senha); return visListar_(req);
    default: throw new VisFalha('interno', 'Ação desconhecida.');
  }
}

function visConferirSenha_(enviada) {
  var senha = PropertiesService.getScriptProperties().getProperty(VIS_PROP_SENHA);
  if (!senha) throw new VisFalha('interno', 'Senha do dashboard não configurada. Rode configurarSenhaVisitas().');
  if (enviada !== senha) throw new VisFalha('senha', 'Senha incorreta.');
}

function visComLock_(fn) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) throw new VisFalha('ocupado', 'Muitos lançamentos ao mesmo tempo, tente de novo.');
  try { return fn(); } finally { lock.releaseLock(); }
}

/* ---------- helpers puros (testados em tests/visitas-gs.test.js) ---------- */
function visPad_(n) { return (n < 10 ? '0' : '') + n; }
function visIsoParaMs_(iso) { var p = iso.split('-'); return Date.UTC(+p[0], +p[1] - 1, +p[2]); }
function visMsParaIso_(ms) {
  var d = new Date(ms);
  return d.getUTCFullYear() + '-' + visPad_(d.getUTCMonth() + 1) + '-' + visPad_(d.getUTCDate());
}
function visSomarDias_(iso, n) { return visMsParaIso_(visIsoParaMs_(iso) + n * 86400000); }
function visDiasEntre_(de, ate) { return Math.round((visIsoParaMs_(ate) - visIsoParaMs_(de)) / 86400000) + 1; }
function visDataValida_(iso) {
  return /^\d{4}-\d{2}-\d{2}$/.test(iso) && visMsParaIso_(visIsoParaMs_(iso)) === iso;
}
function visIsoParaBr_(iso) { var p = iso.split('-'); return p[2] + '/' + p[1] + '/' + p[0]; }
function visBrParaIso_(br) {
  var m = /^(\d{2})\/(\d{2})\/(\d{4})/.exec(String(br || '').trim());
  return m ? m[3] + '-' + m[2] + '-' + m[1] : '';
}
function visTexto_(s) {
  if (s === null || s === undefined) return '';
  return String(s).replace(/\s+/g, ' ').trim().slice(0, VIS_MAX_TEXTO);
}
function visChave_(s) { return visTexto_(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
function visNeutralizar_(s) {
  var t = String(s === null || s === undefined ? '' : s);
  return /^[=+\-@\t\r]/.test(t) ? "'" + t : t;
}
function visEmpreendimento_(nome) {
  var n = visTexto_(nome);
  for (var i = 0; i < VISITAS_EMPREENDIMENTOS.length; i++) {
    if (VISITAS_EMPREENDIMENTOS[i].nome === n) return VISITAS_EMPREENDIMENTOS[i];
  }
  return null;
}
function visCodigoTipo_(nome) {
  var n = String(nome || '').trim();
  for (var k in VIS_TIPOS) if (VIS_TIPOS.hasOwnProperty(k) && VIS_TIPOS[k] === n) return k;
  return '';
}

/* spec 4.2: o servidor e a autoridade */
function visValidar_(req, hoje, agoraMin) {
  var emp = visEmpreendimento_(req.empreendimento);
  if (!emp) throw new VisFalha('invalido', 'Empreendimento desconhecido.', 'empreendimento');
  var tipo = String(req.tipo || '');
  if (!VIS_TIPOS.hasOwnProperty(tipo)) throw new VisFalha('invalido', 'Tipo de visita inválido.', 'tipo');
  var data = String(req.data || '');
  if (!visDataValida_(data) || data > hoje || data < visSomarDias_(hoje, -VIS_DIAS_RETROATIVOS)) {
    throw new VisFalha('invalido', 'A data precisa estar entre hoje e 7 dias atrás.', 'data');
  }
  var hora = String(req.hora || '');
  var m = /^([01]\d|2[0-3]):([0-5]\d)$/.exec(hora);
  if (!m) throw new VisFalha('invalido', 'Horário inválido.', 'hora');
  if (data === hoje && (+m[1]) * 60 + (+m[2]) > agoraMin + 5) {
    throw new VisFalha('invalido', 'O horário não pode estar no futuro.', 'hora');
  }
  var imobiliaria = tipo === 'imob' ? visTexto_(req.imobiliaria) : '';
  if (tipo === 'imob' && !imobiliaria) throw new VisFalha('invalido', 'Informe a imobiliária.', 'imobiliaria');
  return {
    empreendimento: emp.nome, cidade: emp.cidade, data: data, hora: hora, tipo: tipo,
    corretorHouse: tipo === 'house' ? visTexto_(req.corretorHouse) : '',
    imobiliaria: imobiliaria,
    corretorImob: tipo === 'imob' ? visTexto_(req.corretorImob) : ''
  };
}

function visAtiva_(l, ix) { return String(l[ix['Excluída']]).trim() !== '1'; }

function visDeLinha_(l, ix) {
  return {
    id: String(l[ix['ID']]),
    data: visBrParaIso_(l[ix['Data']]),
    hora: String(l[ix['Horário']]).trim(),
    empreendimento: String(l[ix['Empreendimento']]),
    cidade: String(l[ix['Cidade']]),
    tipo: visCodigoTipo_(l[ix['Tipo']]),
    corretorHouse: String(l[ix['Corretor house']]),
    imobiliaria: String(l[ix['Imobiliária']]),
    corretorImob: String(l[ix['Corretor imobiliária']])
  };
}

/* nomes distintos (sem caixa/acento), grafia mais frequente, ordem alfabetica */
function visSugestoes_(linhas, ix, desde) {
  var grupos = {}, ordem = [];
  linhas.forEach(function (l) {
    if (!visAtiva_(l, ix)) return;
    if (visBrParaIso_(l[ix['Registrado em']]) < desde) return;
    var nome = visTexto_(l[ix['Imobiliária']]), k = visChave_(nome);
    if (!k) return;
    if (!grupos[k]) { grupos[k] = {}; ordem.push(k); }
    grupos[k][nome] = (grupos[k][nome] || 0) + 1;
  });
  return ordem.map(function (k) {
    var g = grupos[k], melhor = null;
    Object.keys(g).forEach(function (n) { if (melhor === null || g[n] > g[melhor]) melhor = n; });
    return melhor;
  }).sort(function (a, b) { return a.localeCompare(b, 'pt-BR'); }).slice(0, VIS_MAX_SUGESTOES);
}

/* ---------- planilha ---------- */
function visAba_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var aba = ss.getSheetByName(VIS_ABA) || ss.insertSheet(VIS_ABA);
  if (aba.getLastRow() === 0) {
    aba.getRange(1, 1, 1, VIS_COLUNAS.length).setValues([VIS_COLUNAS]).setFontWeight('bold');
    aba.setFrozenRows(1);
  }
  return aba;
}

function visCabecalho_(aba) {
  var largura = aba.getLastColumn();
  var cab = aba.getRange(1, 1, 1, largura).getDisplayValues()[0].map(function (c) { return String(c).trim(); });
  var ix = {};
  cab.forEach(function (n, i) { if (n && !(n in ix)) ix[n] = i; });
  VIS_COLUNAS.forEach(function (n) {
    if (!(n in ix)) throw new VisFalha('coluna', 'Coluna "' + n + '" não encontrada na aba ' + VIS_ABA + '.');
  });
  return { indice: ix, largura: largura };
}

function visLer_() {
  var aba = visAba_();
  var cab = visCabecalho_(aba);
  var n = Math.max(aba.getLastRow() - 1, 0);
  return {
    aba: aba,
    indice: cab.indice,
    linhas: n ? aba.getRange(2, 1, n, cab.largura).getDisplayValues() : []
  };
}

function visHoje_() { return Utilities.formatDate(new Date(), VIS_FUSO, 'yyyy-MM-dd'); }

function visHash_(texto) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, texto, Utilities.Charset.UTF_8)
    .map(function (b) { return ('0' + (b & 0xff).toString(16)).slice(-2); }).join('');
}

/* ---------- acoes ---------- */
function visRegistrar_(req) {
  var agora = new Date();
  var hoje = Utilities.formatDate(agora, VIS_FUSO, 'yyyy-MM-dd');
  var hm = Utilities.formatDate(agora, VIS_FUSO, 'HH:mm').split(':');
  var v = visValidar_(req, hoje, (+hm[0]) * 60 + (+hm[1]));
  var token = Utilities.getUuid();
  v.id = 'V' + agora.getTime() + Utilities.getUuid().slice(0, 4).toUpperCase();
  var valores = {
    'ID': v.id,
    'Registrado em': Utilities.formatDate(agora, VIS_FUSO, 'dd/MM/yyyy HH:mm:ss'),
    'Data': visIsoParaBr_(v.data),
    'Horário': v.hora,
    'Empreendimento': v.empreendimento,
    'Cidade': v.cidade,
    'Tipo': VIS_TIPOS[v.tipo],
    'Corretor house': v.corretorHouse,
    'Imobiliária': v.imobiliaria,
    'Corretor imobiliária': v.corretorImob,
    'Excluída': '0',
    'Token': visHash_(token)
  };
  visComLock_(function () {
    var aba = visAba_();
    var cab = visCabecalho_(aba);
    var linha = [];
    for (var i = 0; i < cab.largura; i++) linha.push('');
    Object.keys(valores).forEach(function (nome) { linha[cab.indice[nome]] = visNeutralizar_(valores[nome]); });
    /* formato texto: a planilha nao converte data/hora e mantem o valor exato */
    var faixa = aba.getRange(aba.getLastRow() + 1, 1, 1, cab.largura);
    faixa.setNumberFormat('@');
    faixa.setValues([linha]);
  });
  return { visita: v, token: token };
}

function visDia_(req) {
  var emp = visEmpreendimento_(req.empreendimento);
  if (!emp) throw new VisFalha('invalido', 'Empreendimento desconhecido.', 'empreendimento');
  var data = String(req.data || '');
  if (!visDataValida_(data)) throw new VisFalha('invalido', 'Data inválida.', 'data');
  var t = visLer_(), ix = t.indice, visitas = [];
  t.linhas.forEach(function (l) {
    if (!visAtiva_(l, ix)) return;
    var v = visDeLinha_(l, ix);
    if (v.empreendimento === emp.nome && v.data === data) visitas.push(v);
  });
  return { visitas: visitas, sugestoesImob: visSugestoes_(t.linhas, ix, visSomarDias_(visHoje_(), -VIS_DIAS_SUGESTOES)) };
}

/* spec 4.3: so exclui com o token do proprio navegador e no mesmo dia */
function visExcluir_(req) {
  var id = String(req.id || ''), token = String(req.token || '');
  var hoje = visHoje_();
  return visComLock_(function () {
    var t = visLer_(), ix = t.indice;
    for (var i = 0; i < t.linhas.length; i++) {
      var l = t.linhas[i];
      if (String(l[ix['ID']]) !== id) continue;
      var valido = token && String(l[ix['Token']]) === visHash_(token) &&
        visBrParaIso_(l[ix['Registrado em']]) === hoje;
      if (!valido) break;
      t.aba.getRange(i + 2, ix['Excluída'] + 1).setValue('1');
      return { id: id };
    }
    throw new VisFalha('nao_encontrada', 'Não foi possível excluir este lançamento.');
  });
}

function visListar_(req) {
  var de = String(req.de || ''), ate = String(req.ate || '');
  if (!visDataValida_(de) || !visDataValida_(ate) || de > ate || visDiasEntre_(de, ate) > VIS_MAX_DIAS_LISTAR) {
    throw new VisFalha('invalido', 'Período inválido (máximo de 92 dias).', 'periodo');
  }
  var t = visLer_(), ix = t.indice, visitas = [];
  t.linhas.forEach(function (l) {
    if (!visAtiva_(l, ix)) return;
    var v = visDeLinha_(l, ix);
    if (v.data >= de && v.data <= ate) visitas.push(v);
  });
  return { visitas: visitas };
}

/* ---------- conferencia manual (spec 4.6) ---------- */
function testeVisitas() {
  var hoje = visHoje_();
  var r = visRegistrar_({
    empreendimento: VISITAS_EMPREENDIMENTOS[0].nome, data: hoje,
    hora: Utilities.formatDate(new Date(), VIS_FUSO, 'HH:mm'), tipo: 'imob', imobiliaria: 'TESTE - pode ignorar'
  });
  Logger.log('registrar: ' + JSON.stringify(r.visita));
  var d = visDia_({ empreendimento: VISITAS_EMPREENDIMENTOS[0].nome, data: hoje });
  Logger.log('dia: ' + d.visitas.length + ' visita(s), ' + d.sugestoesImob.length + ' sugestao(oes)');
  Logger.log('excluir: ' + JSON.stringify(visExcluir_({ id: r.visita.id, token: r.token })));
  Logger.log('listar: ' + visListar_({ de: hoje, ate: hoje }).visitas.length + ' visita(s) ativas hoje');
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test tests/*.test.js`
Expected: PASS (inclui a paridade de empreendimentos)

- [ ] **Step 5: Commit**

```bash
git add docs/apps-script-visitas.gs tests/visitas-gs.test.js
git commit -m "feat(visitas): web app do apps script com validacao e exclusao por token

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Cliente da API e configuração

**Files:**
- Create: `assets/visitas-api.js`
- Modify: `assets/config.js` (acrescentar no **fim** do arquivo)

**Interfaces:**
- Consumes: `window.Visitas` (Tasks 1–3), `window.CITIES`, contrato da Task 4
- Produces: `window.VisitasAPI.criar({ url, senha?: () => string }) → { chamar(acao, params) → Promise<json>, demo: boolean }`
  - Rejeita com `{ codigo, mensagem, campo }` (`codigo` = `erro` do servidor, ou `rede` / `formato`).
  - Modo demo (URL vazia ou `?demo=1`): guarda tudo na memória da aba, gera 30 dias de visitas fictícias e aceita qualquer senha.

> Este arquivo só roda no navegador (`fetch`, `AbortController`). Ele é verificado nas Tasks 6 e 7, com as páginas em modo demonstração.

- [ ] **Step 1: Add the URL to `assets/config.js`**

Append to the end of `assets/config.js`:

```js

/* ---------- Visitas da Recepcao (/visitas-recepcao e /visitas-recepcao-adm) ----------
   URL .../exec do Web App do Apps Script da planilha de visitas
   (docs/apps-script-visitas.gs). A SENHA DO DASHBOARD NAO FICA AQUI:
   fica so no Apps Script (Script Property VISITAS_SENHA).
   Vazio = modo demonstracao (dados ficticios na memoria da aba, nada e
   gravado). Com URL preenchida, ?demo=1 na pagina forca o modo demo. */
window.VISITAS_APPS_SCRIPT_URL = '';
```

- [ ] **Step 2: Create `assets/visitas-api.js`**

```js
/* ============================================================
   VISITAS DA RECEPCAO - cliente do Web App
   ------------------------------------------------------------
   POST text/plain (sem preflight de CORS) para o Web App de
   docs/apps-script-visitas.gs. Sem URL configurada (ou com ?demo=1)
   entra em modo demonstracao: tudo fica na memoria da aba.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md
   ============================================================ */
(function (raiz) {
  'use strict';

  var V = raiz.Visitas;
  var TIMEOUT = 20000;
  var MSG_PLANILHA = 'Erro na planilha de visitas. Avise o comercial.';
  var MENSAGENS = {
    rede: 'Sem conexão. Tente de novo.',
    ocupado: 'Muitos lançamentos ao mesmo tempo, tente de novo.',
    coluna: MSG_PLANILHA,
    interno: MSG_PLANILHA,
    formato: MSG_PLANILHA
  };

  function falha(codigo, mensagem, campo) {
    return { codigo: codigo, mensagem: MENSAGENS[codigo] || mensagem || MSG_PLANILHA, campo: campo || null };
  }
  function copia(x) { return JSON.parse(JSON.stringify(x)); }
  function pad(n) { return (n < 10 ? '0' : '') + n; }

  /* ---------- modo demonstracao ---------- */
  var IMOBS_DEMO = ['Imobiliária Exemplo A', 'Imobiliária Exemplo B', 'Imobiliária Exemplo C', 'Imobiliária Exemplo D'];
  var memoria = null;
  var tokensDemo = {};

  function rnd(a, b, c) {
    var x = Math.sin(a * 127.1 + b * 311.7 + c * 74.7) * 43758.5453;
    return x - Math.floor(x);
  }
  function gerarDemo(hoje, emps) {
    var out = [], seq = 0;
    for (var d = 0; d < 30; d++) {
      var data = V.somarDias(hoje, -d);
      emps.forEach(function (e, ei) {
        var n = Math.floor(rnd(ei, d, 1) * 6);
        for (var k = 0; k < n; k++) {
          var r = rnd(ei, d, 10 + k);
          var tipo = r < 0.4 ? 'esp' : r < 0.65 ? 'house' : 'imob';
          var min = 8 * 60 + Math.floor(rnd(ei, d, 30 + k) * 11 * 60);
          seq++;
          out.push({
            id: 'D' + seq, data: data, hora: pad(Math.floor(min / 60)) + ':' + pad(min % 60),
            empreendimento: e.nome, cidade: e.cidade, tipo: tipo,
            corretorHouse: tipo === 'house' ? 'Corretor Exemplo' : '',
            imobiliaria: tipo === 'imob' ? IMOBS_DEMO[Math.floor(rnd(ei, d, 50 + k) * IMOBS_DEMO.length)] : '',
            corretorImob: ''
          });
        }
      });
    }
    return out;
  }
  function memoriaDemo() {
    if (!memoria) memoria = gerarDemo(V.dataLocalIso(new Date()), V.listaEmpreendimentos(raiz.CITIES || []));
    return memoria;
  }

  function chamarDemo(acao, p) {
    var lista = memoriaDemo();
    return new Promise(function (ok) { setTimeout(ok, 300); }).then(function () {
      if (acao === 'registrar') {
        var f = V.validarFormulario(p);
        if (!f.ok) throw falha('invalido', 'Preencha o campo ' + f.faltando + '.', f.faltando);
        var emp = V.listaEmpreendimentos(raiz.CITIES || []).filter(function (e) { return e.nome === p.empreendimento; })[0];
        var v = {
          id: 'D' + Date.now(), data: p.data, hora: p.hora, empreendimento: p.empreendimento,
          cidade: emp ? emp.cidade : '', tipo: p.tipo,
          corretorHouse: p.tipo === 'house' ? V.normalizarTexto(p.corretorHouse) : '',
          imobiliaria: p.tipo === 'imob' ? V.normalizarTexto(p.imobiliaria) : '',
          corretorImob: p.tipo === 'imob' ? V.normalizarTexto(p.corretorImob) : ''
        };
        var token = 'demo-' + Math.random().toString(36).slice(2);
        lista.push(v);
        tokensDemo[v.id] = token;
        return { ok: true, visita: copia(v), token: token };
      }
      if (acao === 'dia') {
        return {
          ok: true,
          visitas: copia(lista.filter(function (v) { return v.empreendimento === p.empreendimento && v.data === p.data; })),
          sugestoesImob: IMOBS_DEMO.slice()
        };
      }
      if (acao === 'excluir') {
        for (var i = 0; i < lista.length; i++) {
          if (lista[i].id === p.id && tokensDemo[p.id] && tokensDemo[p.id] === p.token) {
            lista.splice(i, 1);
            delete tokensDemo[p.id];
            return { ok: true, id: p.id };
          }
        }
        throw falha('nao_encontrada', 'Não foi possível excluir este lançamento.');
      }
      if (acao === 'listar') return { ok: true, visitas: copia(V.filtrar(lista, { de: p.de, ate: p.ate })) };
      throw falha('interno');
    });
  }

  /* ---------- Web App (spec 4.1) ---------- */
  function criar(opcoes) {
    var url = opcoes.url || '';
    var busca = raiz.location ? raiz.location.search : '';
    var demo = !url || /[?&]demo=1(&|$)/.test(busca);
    var senha = opcoes.senha || function () { return ''; };

    function chamar(acao, params) {
      if (demo) return chamarDemo(acao, params || {});
      var corpo = Object.assign({ acao: acao }, params || {});
      var s = senha();
      if (s) corpo.senha = s;
      var ctrl = new AbortController();
      var timer = setTimeout(function () { ctrl.abort(); }, TIMEOUT);
      return fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify(corpo),
        signal: ctrl.signal
      }).then(function (r) { return r.text(); }, function () {
        throw falha('rede');
      }).then(function (texto) {
        var json;
        try { json = JSON.parse(texto); } catch (e) { throw falha('formato'); }
        if (!json.ok) throw falha(json.erro || 'interno', json.mensagem, json.campo);
        return json;
      }).finally(function () { clearTimeout(timer); });
    }

    return { chamar: chamar, demo: demo };
  }

  raiz.VisitasAPI = { criar: criar };
})(this);
```

- [ ] **Step 3: Syntax-check both files**

Run: `node --check assets/visitas-api.js && node --check assets/config.js && node --test tests/*.test.js`
Expected: nenhum erro de sintaxe; testes PASS

- [ ] **Step 4: Commit**

```bash
git add assets/visitas-api.js assets/config.js
git commit -m "feat(visitas): cliente do web app com modo demonstracao

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Página da recepção (`/visitas-recepcao`)

**Files:**
- Create: `visitas-recepcao.html`
- Create: `assets/visitas-recepcao-app.js`

**Interfaces:**
- Consumes: `window.Visitas` (`validarFormulario`, `totaisPorTipo`, `recentes`, `detalhe`, `TIPOS`, `ORDEM_TIPOS`, `dataLocalIso`, `horaLocal`, `dataCurta`, `somarDias`, `listaEmpreendimentos`), `window.VisitasAPI.criar`, `window.CITIES`
- Produces: nada consumido por outras tasks. `localStorage`: `visitas.emp` (último empreendimento) e `visitas.tokens` (`{ [id]: { token, data } }`).

Layout de referência: quadros `Main` (desktop) e `RecepcaoCelular` do canvas.

- [ ] **Step 1: Create `visitas-recepcao.html`**

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Registro de visitas · Recepção | Portal do Corretor</title>
<link rel="icon" type="image/webp" href="assets/img/favicon.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&display=swap" rel="stylesheet">
<!-- Lancamento de visitas no stand (publica). Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md
     Telas: canvas "Visitas Recepcao", quadros Main e RecepcaoCelular -->
<style>
:root{
  --red:#E4032B;--red-deep:#B8001F;--ink:#3A4043;--slate:#727A7D;--hair:#E7E9EA;--bg:#F5F6F7;--surface:#FFFFFF;
  --ok:#1B7A40;--ok-bg:#EFF9F2;--ok-line:#C7E7D3;--err:#C4001C;--err-bg:#FDEEF0;--err-line:#F6C9D0;
  --warn:#8A5700;--warn-bg:#FFF7E6;--warn-line:#F1DCAE;
  --foco:0 0 0 3px rgba(228,3,43,.10);--foco-forte:0 0 0 3px rgba(228,3,43,.25)
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:'DM Sans',system-ui,sans-serif;font-size:15px;line-height:1.5;color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
[hidden]{display:none!important}
button,input,select{font:inherit;color:inherit}
h1,h2,p{margin:0}
.num{font-variant-numeric:tabular-nums}
.lab{font-size:12px;font-weight:500;letter-spacing:.04em;text-transform:uppercase;color:var(--slate)}
.opc{text-transform:none;letter-spacing:normal;font-weight:400}
.dica{font-size:13px;color:var(--slate)}
.step{display:flex;align-items:center;gap:10px;font-size:12.5px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--red)}
.step::before{content:"";width:22px;height:2px;border-radius:2px;background:var(--red)}

.hero{background:var(--surface) url(assets/img/hero-bg.png) center/cover no-repeat;border-bottom:1px solid var(--hair);padding:2.25rem 1.25rem 1.75rem}
.hero-in{max-width:1120px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:flex-start;justify-content:space-between;gap:18px}
.hero-txt{display:flex;flex-direction:column;gap:6px;flex:1 1 320px;min-width:0}
.hero h1{font-size:2.15rem;font-weight:700;line-height:1.15;letter-spacing:-.6px}
.hero p{color:var(--slate);max-width:56ch}
.hero img{height:44px;width:auto}

.wrap{max-width:1120px;margin:0 auto;padding:1.75rem 1.25rem 4rem;display:flex;flex-wrap:wrap;align-items:flex-start;gap:22px}
.col-form{flex:999 1 560px;min-width:0;display:flex;flex-direction:column;gap:18px}
.col-cont{flex:1 1 320px;min-width:0;display:flex;flex-direction:column;gap:18px}
.card{background:var(--surface);border:1px solid var(--hair);border-radius:14px;padding:1.35rem;display:flex;flex-direction:column;gap:14px}
.linha{display:flex;flex-wrap:wrap;gap:14px}
.campo{display:flex;flex-direction:column;gap:6px;min-width:0}
.inp{width:100%;min-height:46px;border:1px solid var(--hair);border-radius:9px;background:var(--surface);padding:0 12px;outline:none;transition:border-color .15s,box-shadow .15s}
.inp:focus{border-color:var(--red);box-shadow:var(--foco)}
.inp[aria-invalid="true"]{border-color:var(--err);background:var(--err-bg)}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:46px;padding:0 14px;border-radius:9px;border:1px solid var(--hair);background:var(--surface);font-weight:500;font-size:14px;cursor:pointer;white-space:nowrap;transition:border-color .15s,color .15s,background .15s}
.btn:hover:not(:disabled){border-color:var(--red);color:var(--red)}
.btn:focus-visible,.tipo:focus-visible{outline:none;box-shadow:var(--foco-forte)}
.btn-p{width:100%;min-height:56px;font-size:1.05rem;font-weight:700;background:var(--red);border-color:var(--red);color:#fff}
.btn-p:hover:not(:disabled){background:var(--red-deep);border-color:var(--red-deep);color:#fff}
.btn-p:disabled{background:var(--hair);border-color:var(--hair);color:var(--slate);cursor:not-allowed}
.btn-i{width:44px;min-height:44px;padding:0;color:var(--slate);flex:none}
.btn-i:hover:not(:disabled){border-color:var(--err);color:var(--err)}

.tipos{display:flex;flex-wrap:wrap;gap:12px}
.tipo{flex:1 1 220px;min-width:0;display:flex;gap:12px;align-items:center;text-align:left;padding:14px;min-height:84px;border-radius:14px;border:1px solid var(--hair);background:var(--surface);cursor:pointer;transition:border-color .15s,box-shadow .15s}
.tipo:hover{border-color:var(--red)}
.tipo[aria-checked="true"]{border-color:var(--red);box-shadow:var(--foco)}
.tipo-ico{flex:none;width:44px;height:44px;border-radius:9px;display:flex;align-items:center;justify-content:center}
.tipo-nome{display:block;font-weight:700;font-size:.95rem}
.tipo-desc{display:block;font-size:13px;color:var(--slate);line-height:1.35}
.extra{display:flex;flex-wrap:wrap;gap:14px;padding-top:14px;border-top:1px dashed var(--hair)}
.extra .campo{flex:1 1 220px}

.faixa{display:flex;flex-wrap:wrap;align-items:center;gap:12px;padding:12px 14px;border-radius:14px;border:1px solid}
.faixa.ok{background:var(--ok-bg);border-color:var(--ok-line);color:var(--ok)}
.faixa.err{background:var(--err-bg);border-color:var(--err-line);color:var(--err)}
.faixa-txt{flex:1 1 200px;min-width:0}
.faixa-txt strong{display:block}
.faixa-txt span{font-size:14px}
.faixa .btn{min-height:44px;border-color:currentColor;color:inherit}
.aviso-demo{padding:12px 16px;border:1px dashed var(--warn-line);background:var(--warn-bg);color:var(--warn);border-radius:12px;font-size:13.5px}

.total{display:flex;align-items:baseline;gap:10px;padding-bottom:16px;border-bottom:1px dashed var(--hair)}
.total-n{font-size:4rem;font-weight:700;line-height:1;letter-spacing:-2px}
.total-lab{color:var(--slate)}
.barras{display:flex;flex-direction:column;gap:12px}
.barra-top{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:14px}
.barra-trilho{height:8px;border-radius:999px;background:var(--bg);overflow:hidden;margin-top:6px}
.barra-trilho div{height:100%;border-radius:999px;width:0;transition:width .3s}
.ponto{display:inline-block;width:9px;height:9px;border-radius:999px;flex:none}
.rotulo-tipo{display:flex;align-items:center;gap:8px}
.lista-cab{display:flex;align-items:center;justify-content:space-between;gap:8px}
.lista-cab strong{font-size:.95rem}
.lista{list-style:none;margin:0;padding:0}
.lista li{display:flex;align-items:center;gap:12px;padding:10px 0;border-top:1px dashed var(--hair)}
.lista-hora{width:46px;flex:none;font-weight:700}
.lista-txt{flex:1 1 auto;min-width:0;display:flex;flex-direction:column}
.lista-tipo{display:flex;align-items:center;gap:7px;font-size:14px;font-weight:500}
.lista-det{font-size:12.5px;color:var(--slate);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.vazio{padding:18px 0;text-align:center;color:var(--slate);font-size:14px}
.erro-txt{color:var(--err);font-size:13.5px;font-weight:500}

@media (max-width:700px){
  .hero{padding:1.5rem 1rem 1.25rem}.hero h1{font-size:1.5rem}.hero img{height:30px}
  .wrap{padding:1.25rem 1rem 3rem}.card{padding:1rem}
}
</style>
</head>
<body>
<header class="hero">
  <div class="hero-in">
    <div class="hero-txt">
      <span class="step">Portal do Corretor · Recepção</span>
      <h1>Registro de visitas</h1>
      <p>Registre cada cliente que entrar no stand: escolha o tipo de visita e toque em registrar.</p>
    </div>
    <img src="assets/img/logo-direcional-header.png" alt="Direcional">
  </div>
</header>

<main class="wrap">
  <section class="col-form" aria-label="Nova visita">
    <p class="aviso-demo" id="aviso-demo" hidden>Modo demonstração: dados fictícios, nada é gravado na planilha.</p>

    <div class="faixa" id="faixa" role="status" aria-live="polite" hidden>
      <svg id="faixa-ico-ok" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M7.5 12.5l3 3 6-6.5"/></svg>
      <svg id="faixa-ico-err" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 7v6M12 16.5v.5"/></svg>
      <div class="faixa-txt"><strong id="faixa-titulo"></strong><span id="faixa-texto"></span></div>
      <button type="button" class="btn" id="faixa-desfazer">Desfazer</button>
    </div>

    <div class="card">
      <span class="step">Passo 1 · Stand, data e horário</span>
      <div class="linha">
        <label class="campo" style="flex:2 1 260px">
          <span class="lab">Empreendimento</span>
          <select class="inp" id="emp"></select>
        </label>
        <label class="campo" style="flex:1 1 150px">
          <span class="lab">Data</span>
          <input class="inp" id="data" type="date">
        </label>
        <div class="campo" style="flex:1 1 170px">
          <label class="lab" for="hora">Horário</label>
          <div style="display:flex;gap:8px">
            <input class="inp" id="hora" type="time" style="flex:1 1 auto;min-width:0">
            <button type="button" class="btn" id="agora">Agora</button>
          </div>
        </div>
      </div>
      <p class="dica">Data e horário vêm preenchidos com o momento atual. Só altere se estiver lançando uma visita que já passou.</p>
    </div>

    <div class="card">
      <span class="step">Passo 2 · Como o cliente chegou?</span>
      <div class="tipos" role="radiogroup" aria-label="Tipo de visita">
        <button type="button" class="tipo" role="radio" aria-checked="false" data-tipo="esp">
          <span class="tipo-ico" style="background:#F5F6F7;color:#3A4043">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18"/><path d="M6 21V4a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v17"/><path d="M12.5 12h.01"/><path d="M16 9l4 3-4 3"/></svg>
          </span>
          <span><span class="tipo-nome">Espontânea</span><span class="tipo-desc">Chegou ao stand sem agendamento</span></span>
        </button>
        <button type="button" class="tipo" role="radio" aria-checked="false" data-tipo="house">
          <span class="tipo-ico" style="background:#FDEEF0;color:#E4032B">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/><path d="M9 15.5l2 2 4-4"/></svg>
          </span>
          <span><span class="tipo-nome">Agendada · Corretor house</span><span class="tipo-desc">Agendada por um corretor da Direcional</span></span>
        </button>
        <button type="button" class="tipo" role="radio" aria-checked="false" data-tipo="imob">
          <span class="tipo-ico" style="background:#EEF0F1;color:#5B6366">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M3 13h18"/></svg>
          </span>
          <span><span class="tipo-nome">Imobiliária parceira</span><span class="tipo-desc">Trazido por corretor de imobiliária</span></span>
        </button>
      </div>

      <div class="extra" id="extra-house" hidden>
        <label class="campo">
          <span class="lab">Corretor house que agendou <span class="opc">(opcional)</span></span>
          <input class="inp" id="corretor-house" type="text" maxlength="80" autocomplete="off" placeholder="Nome do corretor">
        </label>
      </div>

      <div class="extra" id="extra-imob" hidden>
        <label class="campo">
          <span class="lab">Imobiliária</span>
          <input class="inp" id="imob" type="text" maxlength="80" autocomplete="off" list="lista-imob" placeholder="Digite ou escolha">
          <datalist id="lista-imob"></datalist>
        </label>
        <label class="campo">
          <span class="lab">Corretor da imobiliária <span class="opc">(opcional)</span></span>
          <input class="inp" id="corretor-imob" type="text" maxlength="80" autocomplete="off" placeholder="Nome do corretor">
        </label>
      </div>
    </div>

    <button type="button" class="btn btn-p" id="registrar" disabled>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
      <span id="registrar-txt">Escolha o tipo de visita</span>
    </button>
  </section>

  <aside class="col-cont" aria-label="Visitas do dia">
    <div class="card">
      <div style="display:flex;flex-direction:column;gap:2px">
        <span class="lab" id="cont-titulo">Visitas hoje</span>
        <strong id="cont-emp" style="font-size:.95rem"></strong>
      </div>
      <div class="total">
        <span class="total-n num" id="cont-total">0</span>
        <span class="total-lab" id="cont-total-lab">visitas registradas</span>
      </div>
      <div class="barras">
        <div>
          <div class="barra-top"><span class="rotulo-tipo"><span class="ponto" style="background:#3A4043"></span>Espontânea</span><strong class="num" id="q-esp">0</strong></div>
          <div class="barra-trilho"><div id="b-esp" style="background:#3A4043"></div></div>
        </div>
        <div>
          <div class="barra-top"><span class="rotulo-tipo"><span class="ponto" style="background:#E4032B"></span>Corretor house</span><strong class="num" id="q-house">0</strong></div>
          <div class="barra-trilho"><div id="b-house" style="background:#E4032B"></div></div>
        </div>
        <div>
          <div class="barra-top"><span class="rotulo-tipo"><span class="ponto" style="background:#A3ABAE"></span>Imobiliária</span><strong class="num" id="q-imob">0</strong></div>
          <div class="barra-trilho"><div id="b-imob" style="background:#A3ABAE"></div></div>
        </div>
      </div>
      <p class="erro-txt" id="cont-erro" role="alert" hidden></p>
    </div>

    <div class="card" style="gap:10px">
      <div class="lista-cab"><strong>Últimos lançamentos</strong><span class="dica">deste stand</span></div>
      <p class="vazio" id="vazio" hidden></p>
      <ul class="lista" id="ultimos"></ul>
    </div>
  </aside>
</main>

<script src="assets/config.js"></script>
<script src="assets/visitas.js"></script>
<script src="assets/visitas-api.js"></script>
<script src="assets/visitas-recepcao-app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create `assets/visitas-recepcao-app.js`**

```js
/* ============================================================
   VISITAS DA RECEPCAO - interface de /visitas-recepcao
   ------------------------------------------------------------
   Lancamento publico de visitas no stand + contador do dia.
   Regras em assets/visitas.js; API em assets/visitas-api.js.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md (secao 5)
   ============================================================ */
(function () {
  'use strict';

  var V = window.Visitas;
  var api = window.VisitasAPI.criar({ url: window.VISITAS_APPS_SCRIPT_URL || '' });
  var EMPS = V.listaEmpreendimentos(window.CITIES || []);
  var CHAVE_EMP = 'visitas.emp';
  var CHAVE_TOKENS = 'visitas.tokens';
  var INTERVALO_DIA = 60000;
  var TEXTO_BOTAO = {
    empreendimento: 'Escolha o empreendimento',
    data: 'Informe a data',
    hora: 'Informe o horário',
    tipo: 'Escolha o tipo de visita',
    imobiliaria: 'Informe a imobiliária'
  };
  var CAMPO_ID = { empreendimento: 'emp', data: 'data', hora: 'hora', imobiliaria: 'imob' };
  var estado = { tipo: null, enviando: false, ultimo: null, timerFaixa: null, seqDia: 0 };

  function $(id) { return document.getElementById(id); }
  function hoje() { return V.dataLocalIso(new Date()); }
  function lerLS(chave, padrao) {
    try { var v = localStorage.getItem(chave); return v === null ? padrao : JSON.parse(v); } catch (e) { return padrao; }
  }
  function gravarLS(chave, valor) {
    try { localStorage.setItem(chave, JSON.stringify(valor)); } catch (e) { /* ignora */ }
  }

  /* ---------- tokens de exclusao (spec 4.3): so os de hoje ---------- */
  function lerTokens() {
    var t = lerLS(CHAVE_TOKENS, {}) || {}, h = hoje(), limpo = {};
    Object.keys(t).forEach(function (id) { if (t[id] && t[id].data === h) limpo[id] = t[id]; });
    return limpo;
  }
  function guardarToken(id, token) { var t = lerTokens(); t[id] = { token: token, data: hoje() }; gravarLS(CHAVE_TOKENS, t); }
  function esquecerToken(id) { var t = lerTokens(); delete t[id]; gravarLS(CHAVE_TOKENS, t); }

  /* ---------- formulario ---------- */
  function montarEmpreendimentos() {
    var sel = $('emp');
    (window.CITIES || []).forEach(function (c) {
      var grupo = document.createElement('optgroup');
      grupo.label = c.name;
      (c.empreendimentos || []).forEach(function (e) {
        var o = document.createElement('option');
        o.value = e.nome;
        o.textContent = e.nome;
        grupo.appendChild(o);
      });
      sel.appendChild(grupo);
    });
    var salvo = lerLS(CHAVE_EMP, null);
    if (salvo && EMPS.some(function (e) { return e.nome === salvo; })) sel.value = salvo;
  }

  function lerForm() {
    return {
      empreendimento: $('emp').value, data: $('data').value, hora: $('hora').value, tipo: estado.tipo,
      corretorHouse: $('corretor-house').value, imobiliaria: $('imob').value, corretorImob: $('corretor-imob').value
    };
  }

  function marcarInvalido(campo) {
    ['emp', 'data', 'hora', 'imob'].forEach(function (id) {
      $(id).setAttribute('aria-invalid', CAMPO_ID[campo] === id ? 'true' : 'false');
    });
  }

  function atualizarBotao() {
    var f = V.validarFormulario(lerForm());
    $('registrar').disabled = estado.enviando || !f.ok;
    $('registrar-txt').textContent = estado.enviando ? 'Registrando…' : f.ok ? 'Registrar visita' : TEXTO_BOTAO[f.faltando];
  }

  function escolherTipo(tipo) {
    estado.tipo = tipo;
    Array.prototype.forEach.call(document.querySelectorAll('.tipo'), function (b) {
      b.setAttribute('aria-checked', b.getAttribute('data-tipo') === tipo ? 'true' : 'false');
    });
    $('extra-house').hidden = tipo !== 'house';
    $('extra-imob').hidden = tipo !== 'imob';
    atualizarBotao();
  }

  function limparTipo() {
    $('corretor-house').value = '';
    $('imob').value = '';
    $('corretor-imob').value = '';
    escolherTipo(null);
  }

  /* ---------- faixa de retorno (spec 5.2) ---------- */
  function mostrarFaixa(tipo, titulo, texto, comDesfazer) {
    clearTimeout(estado.timerFaixa);
    $('faixa').className = 'faixa ' + tipo;
    $('faixa-ico-ok').style.display = tipo === 'ok' ? '' : 'none';
    $('faixa-ico-err').style.display = tipo === 'ok' ? 'none' : '';
    $('faixa-titulo').textContent = titulo;
    $('faixa-texto').textContent = texto;
    $('faixa-desfazer').hidden = !comDesfazer;
    $('faixa').hidden = false;
    if (tipo === 'ok') estado.timerFaixa = setTimeout(esconderFaixa, 8000);
  }
  function esconderFaixa() {
    clearTimeout(estado.timerFaixa);
    $('faixa').hidden = true;
    estado.ultimo = null;
  }

  /* ---------- acoes ---------- */
  function registrar() {
    var dados = lerForm();
    if (estado.enviando || !V.validarFormulario(dados).ok) return;
    estado.enviando = true;
    atualizarBotao();
    marcarInvalido(null);
    api.chamar('registrar', dados).then(function (r) {
      guardarToken(r.visita.id, r.token);
      mostrarFaixa('ok', 'Visita registrada',
        [r.visita.hora, V.TIPOS[r.visita.tipo].nome, r.visita.empreendimento].join(' · '), true);
      estado.ultimo = r.visita;
      limparTipo();
      $('hora').value = V.horaLocal(new Date());
      carregarDia();
    }, function (f) {
      marcarInvalido(f.campo);
      mostrarFaixa('err', 'A visita não foi registrada', f.mensagem, false);
    }).then(function () {
      estado.enviando = false;
      atualizarBotao();
    });
  }

  function excluir(id) {
    var t = lerTokens()[id];
    if (!t) return Promise.resolve();
    return api.chamar('excluir', { id: id, token: t.token }).then(function () {
      esquecerToken(id);
    }, function (f) {
      mostrarFaixa('err', 'Não foi possível excluir este lançamento',
        f.codigo === 'nao_encontrada' ? 'Ele pode já ter sido excluído.' : f.mensagem, false);
    }).then(carregarDia);
  }

  function desfazer() {
    var v = estado.ultimo;
    if (!v) return;
    esconderFaixa();
    excluir(v.id);
  }

  /* ---------- contador do dia (spec 5.3) ---------- */
  function carregarDia() {
    var emp = $('emp').value, data = $('data').value;
    if (!emp || !data) return;
    var seq = ++estado.seqDia;
    api.chamar('dia', { empreendimento: emp, data: data }).then(function (r) {
      if (seq !== estado.seqDia) return;
      var visitas = (r.visitas || []).filter(function (v) { return V.TIPOS[v.tipo]; });
      renderContador(visitas, emp, data);
      renderSugestoes(r.sugestoesImob || []);
      $('cont-erro').hidden = true;
    }, function (f) {
      if (seq !== estado.seqDia) return;
      $('cont-erro').textContent = f.mensagem;
      $('cont-erro').hidden = false;
    });
  }

  function renderContador(visitas, emp, data) {
    var t = V.totaisPorTipo(visitas), eHoje = data === hoje();
    $('cont-titulo').textContent = (eHoje ? 'Visitas hoje · ' : 'Visitas em ') + V.dataCurta(data);
    $('cont-emp').textContent = emp;
    $('cont-total').textContent = t.total;
    $('cont-total-lab').textContent = t.total === 1 ? 'visita registrada' : 'visitas registradas';
    V.ORDEM_TIPOS.forEach(function (k) {
      $('q-' + k).textContent = t[k];
      $('b-' + k).style.width = (t.total ? Math.round(t[k] / t.total * 100) : 0) + '%';
    });
    var tokens = lerTokens(), ul = $('ultimos');
    ul.textContent = '';
    V.recentes(visitas, 6).forEach(function (v) { ul.appendChild(itemLista(v, !!tokens[v.id])); });
    $('vazio').textContent = eHoje ? 'Nenhuma visita registrada hoje neste stand.' : 'Nenhuma visita registrada neste dia.';
    $('vazio').hidden = visitas.length > 0;
  }

  function el(tag, cls, texto) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }

  function iconeLixeira() {
    var ns = 'http://www.w3.org/2000/svg', s = document.createElementNS(ns, 'svg');
    [['width', '18'], ['height', '18'], ['viewBox', '0 0 24 24'], ['fill', 'none'], ['stroke', 'currentColor'],
      ['stroke-width', '1.8'], ['stroke-linecap', 'round'], ['stroke-linejoin', 'round'], ['aria-hidden', 'true']]
      .forEach(function (a) { s.setAttribute(a[0], a[1]); });
    var p = document.createElementNS(ns, 'path');
    p.setAttribute('d', 'M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3');
    s.appendChild(p);
    return s;
  }

  function itemLista(v, podeExcluir) {
    var li = el('li');
    var txt = el('span', 'lista-txt');
    var tipo = el('span', 'lista-tipo');
    var ponto = el('span', 'ponto');
    ponto.style.background = V.TIPOS[v.tipo].cor;
    tipo.appendChild(ponto);
    tipo.appendChild(document.createTextNode(V.TIPOS[v.tipo].nome));
    txt.appendChild(tipo);
    txt.appendChild(el('span', 'lista-det', V.detalhe(v)));
    li.appendChild(el('span', 'lista-hora num', v.hora));
    li.appendChild(txt);
    if (podeExcluir) {
      var b = el('button', 'btn btn-i');
      b.type = 'button';
      b.setAttribute('aria-label', 'Excluir lançamento das ' + v.hora);
      b.appendChild(iconeLixeira());
      b.addEventListener('click', function () {
        if (!window.confirm('Excluir o lançamento das ' + v.hora + ' (' + V.TIPOS[v.tipo].nome + ')?')) return;
        b.disabled = true;
        if (estado.ultimo && estado.ultimo.id === v.id) esconderFaixa();
        excluir(v.id);
      });
      li.appendChild(b);
    }
    return li;
  }

  function renderSugestoes(nomes) {
    var dl = $('lista-imob');
    dl.textContent = '';
    nomes.forEach(function (n) { var o = document.createElement('option'); o.value = n; dl.appendChild(o); });
  }

  /* ---------- inicio ---------- */
  function iniciar() {
    montarEmpreendimentos();
    $('data').value = hoje();
    $('data').max = hoje();
    $('data').min = V.somarDias(hoje(), -7);
    $('hora').value = V.horaLocal(new Date());
    $('aviso-demo').hidden = !api.demo;

    Array.prototype.forEach.call(document.querySelectorAll('.tipo'), function (b) {
      b.addEventListener('click', function () { escolherTipo(b.getAttribute('data-tipo')); });
    });
    $('agora').addEventListener('click', function () { $('hora').value = V.horaLocal(new Date()); atualizarBotao(); });
    $('emp').addEventListener('change', function () {
      gravarLS(CHAVE_EMP, $('emp').value);
      esconderFaixa();
      carregarDia();
      atualizarBotao();
    });
    $('data').addEventListener('change', function () { carregarDia(); atualizarBotao(); });
    ['hora', 'imob', 'corretor-house', 'corretor-imob'].forEach(function (id) {
      $(id).addEventListener('input', atualizarBotao);
    });
    $('registrar').addEventListener('click', registrar);
    $('faixa-desfazer').addEventListener('click', desfazer);
    /* soma lancamentos de outro aparelho no mesmo stand */
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'visible') carregarDia();
    });
    setInterval(function () { if (document.visibilityState === 'visible') carregarDia(); }, INTERVALO_DIA);

    escolherTipo(null);
    carregarDia();
  }

  iniciar();
})();
```

- [ ] **Step 3: Syntax check**

Run: `node --check assets/visitas-recepcao-app.js && node --test tests/*.test.js`
Expected: sem erros; testes PASS

- [ ] **Step 4: Verify in the browser (demo mode)**

Os serviços podem já estar rodando: use `preview_start` com `{ name: "portal-do-corretor" }` (servidor estático `python3 -m http.server`; **sem** `cleanUrls`, então abra `/visitas-recepcao.html`).

Confira:
1. Aparece o aviso "Modo demonstração" e o console não tem erros.
2. O contador mostra o stand escolhido e o total do dia, com dados demo.
3. Antes de escolher o tipo, o botão diz "Escolha o tipo de visita" e está desabilitado.
4. Imobiliária → aparecem os dois campos, o botão diz "Informe a imobiliária". Digitar "Imobiliária Exemplo A" libera "Registrar visita".
5. Registrar → aparece a faixa verde, o total sobe +1 e o lançamento aparece no topo da lista **com** o botão de lixeira.
6. "Desfazer" → o total volta e a faixa some.
7. Lixeira de um lançamento novo → `confirm`, ele sai da lista.
8. Trocar o empreendimento e recarregar a página → o empreendimento escolhido continua.
9. `resize_window` mobile (375×812): os cartões de tipo empilham, o contador fica embaixo e não há rolagem horizontal. Volte para `desktop` no fim.

Tire um screenshot do desktop depois de registrar uma visita.

- [ ] **Step 5: Commit**

```bash
git add visitas-recepcao.html assets/visitas-recepcao-app.js
git commit -m "feat(visitas): pagina da recepcao com contador do dia

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Dashboard (`/visitas-recepcao-adm`)

**Files:**
- Create: `visitas-recepcao-adm.html`
- Create: `assets/visitas-adm-app.js`

**Interfaces:**
- Consumes: `window.Visitas` (`intervalo`, `filtrar`, `totaisPorTipo`, `porDia`, `porHora`, `porEmpreendimento`, `rankingImobiliarias`, `recentes`, `gerarCSV`, `nomeArquivoCSV`, `rotuloDia`, `dataCurta`, `dataBr`, `horaLocal`, `dataLocalIso`, `somarDias`, `detalhe`, `TIPOS`, `ORDEM_TIPOS`, `listaEmpreendimentos`), `window.VisitasAPI.criar({ url, senha })`, `window.CITIES`
- Produces: `sessionStorage['visitas.adm.senha']`.

Layout de referência: quadro `Admin` do canvas.

- [ ] **Step 1: Create `visitas-recepcao-adm.html`**

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Visitas nos stands · Administração | Portal do Corretor</title>
<link rel="icon" type="image/webp" href="assets/img/favicon.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&display=swap" rel="stylesheet">
<!-- Dashboard interno de visitas (com senha). Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md
     Telas: canvas "Visitas Recepcao", quadro Admin -->
<style>
:root{
  --red:#E4032B;--red-deep:#B8001F;--ink:#3A4043;--slate:#727A7D;--hair:#E7E9EA;--bg:#F5F6F7;--surface:#FFFFFF;--muted:#FAFBFB;
  --err:#C4001C;--err-bg:#FDEEF0;--err-line:#F6C9D0;--warn:#8A5700;--warn-bg:#FFF7E6;--warn-line:#F1DCAE;
  --foco:0 0 0 3px rgba(228,3,43,.10);--foco-forte:0 0 0 3px rgba(228,3,43,.25)
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:'DM Sans',system-ui,sans-serif;font-size:15px;line-height:1.5;color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
[hidden]{display:none!important}
button,input,select{font:inherit;color:inherit}
h1,h2,p{margin:0}
.num{font-variant-numeric:tabular-nums}
.lab{font-size:12px;font-weight:500;letter-spacing:.04em;text-transform:uppercase;color:var(--slate)}
.dica{font-size:13px;color:var(--slate)}
.step{display:flex;align-items:center;gap:10px;font-size:12.5px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--red)}
.step::before{content:"";width:22px;height:2px;border-radius:2px;background:var(--red)}
h2{font-size:.95rem;font-weight:700}

.hero{background:var(--surface) url(assets/img/hero-bg.png) center/cover no-repeat;border-bottom:1px solid var(--hair);padding:2.25rem 1.25rem 1.75rem}
.hero-in{max-width:1240px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:flex-start;justify-content:space-between;gap:18px}
.hero-txt{display:flex;flex-direction:column;gap:6px;flex:1 1 320px;min-width:0}
.hero h1{font-size:2.15rem;font-weight:700;line-height:1.15;letter-spacing:-.6px}
.hero p{color:var(--slate);max-width:60ch}
.hero img{height:44px;width:auto}

.wrap{max-width:1240px;margin:0 auto;padding:1.75rem 1.25rem 4rem;display:flex;flex-direction:column;gap:18px}
.card{background:var(--surface);border:1px solid var(--hair);border-radius:14px;padding:1.35rem;display:flex;flex-direction:column;gap:14px;min-width:0}
.campo{display:flex;flex-direction:column;gap:6px;min-width:0}
.inp{width:100%;min-height:44px;border:1px solid var(--hair);border-radius:9px;background:var(--surface);padding:0 12px;outline:none;transition:border-color .15s,box-shadow .15s}
.inp:focus{border-color:var(--red);box-shadow:var(--foco)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 15px;border-radius:9px;border:1px solid var(--hair);background:var(--surface);font-weight:500;font-size:14px;cursor:pointer;white-space:nowrap;transition:border-color .15s,color .15s,background .15s}
.btn:hover:not(:disabled){border-color:var(--red);color:var(--red)}
.btn:disabled{color:var(--slate);cursor:default}
.btn:focus-visible,.fchip:focus-visible{outline:none;box-shadow:var(--foco-forte)}
.btn-p{background:var(--red);border-color:var(--red);color:#fff;width:100%;min-height:48px}
.btn-p:hover:not(:disabled){background:var(--red-deep);border-color:var(--red-deep);color:#fff}
.btn-p:disabled{background:#F2A3B1;border-color:#F2A3B1;color:#fff}
.aviso-demo{padding:12px 16px;border:1px dashed var(--warn-line);background:var(--warn-bg);color:var(--warn);border-radius:12px;font-size:13.5px}
.aviso-erro{display:flex;flex-wrap:wrap;align-items:center;gap:12px;padding:12px 14px;border-radius:12px;border:1px solid var(--err-line);background:var(--err-bg);color:var(--err);font-weight:500}
.aviso-erro span{flex:1 1 220px}
.erro{color:var(--err);font-weight:500;font-size:14px}

/* ---------- senha ---------- */
.gate{display:flex;justify-content:center;padding:3rem 1rem}
.gate-card{width:100%;max-width:400px}

/* ---------- filtros ---------- */
.filtros{flex-direction:row;flex-wrap:wrap;align-items:flex-end;gap:14px 22px;padding:1rem 1.1rem}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.fchip{min-height:36px;padding:0 13px;border-radius:999px;border:1px solid var(--hair);background:var(--surface);color:#5B6366;font-size:13px;font-weight:500;cursor:pointer;transition:border-color .15s}
.fchip:hover{border-color:var(--red)}
.fchip[aria-pressed="true"]{background:var(--red);border-color:var(--red);color:#fff}
.acoes{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-left:auto}

/* ---------- numeros ---------- */
.kpis{flex-direction:row;flex-wrap:wrap;gap:10px;padding:1.1rem}
.kpi{flex:1 1 180px;min-width:0;padding:6px 14px;display:flex;flex-direction:column;gap:4px}
.kpi+.kpi{border-left:1px solid var(--hair)}
.kpi-n{font-size:1.7rem;font-weight:700;line-height:1.1}
.kpi-total .kpi-n{font-size:2.4rem;letter-spacing:-1px}
.kpi-lab{display:flex;align-items:center;gap:8px}
.ponto{display:inline-block;width:9px;height:9px;border-radius:999px;flex:none}
@media (max-width:620px){.kpi+.kpi{border-left:0;border-top:1px solid var(--hair);padding-top:12px}.kpi{flex-basis:100%}}

/* ---------- grafico ---------- */
.dupla{display:flex;flex-wrap:wrap;gap:18px;align-items:stretch}
.dupla .grande{flex:999 1 560px}
.dupla .lado{flex:1 1 320px}
.cab{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px}
.legenda{display:flex;flex-wrap:wrap;gap:14px;font-size:13px;color:var(--slate)}
.legenda span{display:flex;align-items:center;gap:6px}
.quad{display:inline-block;width:10px;height:10px;border-radius:3px}
.rolagem{overflow-x:auto}
.grafico-box{min-width:520px;display:flex;flex-direction:column;gap:6px}
.grafico{height:220px;display:flex;align-items:flex-end;gap:4px;border-bottom:1px solid var(--hair);background-image:linear-gradient(#F0F1F2 1px,transparent 1px);background-size:100% 55px}
.col{flex:1 1 0;min-width:0;height:100%;display:flex;flex-direction:column;justify-content:flex-end}
.col:hover .pilha{opacity:.82}
.col-val{font-size:11px;color:var(--slate);text-align:center;line-height:1.4;min-height:15px}
.pilha{display:flex;flex-direction:column;border-radius:4px 4px 0 0;overflow:hidden;width:100%;max-width:34px;margin:0 auto}
.rotulos{display:flex;gap:4px}
.rot{flex:1 1 0;min-width:0;text-align:center;font-size:11px;color:var(--slate);white-space:nowrap}
.vazio{padding:28px 0;text-align:center;color:var(--slate);font-size:14px}

/* ---------- origem e ranking ---------- */
.mix{display:flex;height:14px;border-radius:999px;overflow:hidden;background:var(--bg)}
.mix div{height:100%}
.mix-p{height:8px}
.leg-linha{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:14px}
.leg-linha > span:first-child{display:flex;align-items:center;gap:8px}
.ranking{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.rank-trilho{height:6px;border-radius:999px;background:var(--bg);overflow:hidden;margin-top:4px}
.rank-trilho div{height:100%;border-radius:999px;background:#A3ABAE}
.divisor{padding-top:16px;border-top:1px dashed var(--hair)}

/* ---------- tabelas ---------- */
table{width:100%;border-collapse:collapse;font-size:14px}
th{text-align:left;padding:8px 10px;font-size:11.5px;font-weight:500;letter-spacing:.04em;text-transform:uppercase;color:var(--slate);border-bottom:1px solid var(--hair);white-space:nowrap}
td{padding:10px;border-bottom:1px dashed var(--hair)}
.dir{text-align:right}
tbody tr:hover td{background:var(--muted)}
.forte{font-weight:700}
.suave{color:var(--slate)}
.badge{display:inline-flex;align-items:center;gap:7px;padding:2px 10px;border:1px solid var(--hair);border-radius:999px;font-size:12.5px;font-weight:500;white-space:nowrap}

@media (max-width:700px){
  .hero{padding:1.5rem 1rem 1.25rem}.hero h1{font-size:1.5rem}.hero img{height:30px}
  .wrap{padding:1.25rem 1rem 3rem}.card{padding:1rem}.acoes{margin-left:0}
}
</style>
</head>
<body>
<header class="hero">
  <div class="hero-in">
    <div class="hero-txt">
      <span class="step">Portal do Corretor · Administração</span>
      <h1>Visitas nos stands</h1>
      <p>Acompanhe o fluxo de visitas lançado pelas recepções, por empreendimento e por origem do cliente.</p>
    </div>
    <img src="assets/img/logo-direcional-header.png" alt="Direcional">
  </div>
</header>

<section class="gate" id="gate" hidden>
  <form class="card gate-card" id="gate-form" novalidate>
    <span class="step">Acesso restrito</span>
    <h2>Dashboard de visitas</h2>
    <p class="dica">Digite a senha do comercial para ver os lançamentos.</p>
    <label class="campo">
      <span class="lab">Senha</span>
      <input class="inp" id="gate-senha" type="password" autocomplete="current-password" required>
    </label>
    <p class="erro" id="gate-erro" role="alert" hidden></p>
    <button class="btn btn-p" id="gate-entrar" type="submit">Entrar</button>
    <p class="dica" id="gate-demo" hidden>Modo demonstração: qualquer senha entra e os dados são fictícios.</p>
  </form>
</section>

<main class="wrap" id="app" hidden>
  <p class="aviso-demo" id="aviso-demo" hidden>Modo demonstração: dados fictícios, nada é lido da planilha.</p>
  <div class="aviso-erro" id="aviso-erro" role="alert" hidden>
    <span id="aviso-erro-txt"></span>
    <button type="button" class="btn" id="aviso-erro-tentar">Tentar de novo</button>
  </div>

  <div class="card filtros">
    <div class="campo">
      <span class="lab" id="lab-periodo">Período</span>
      <div class="chips" id="periodos" role="group" aria-labelledby="lab-periodo"></div>
    </div>
    <div class="campo">
      <span class="lab" id="lab-cidade">Cidade</span>
      <div class="chips" id="cidades" role="group" aria-labelledby="lab-cidade"></div>
    </div>
    <label class="campo" style="flex:1 1 240px">
      <span class="lab">Empreendimento</span>
      <select class="inp" id="f-emp"></select>
    </label>
    <div class="acoes">
      <span class="dica" id="atualizado-em"></span>
      <button type="button" class="btn" id="atualizar">Atualizar</button>
      <button type="button" class="btn" id="exportar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12M7 10l5 5 5-5M4 21h16"/></svg>
        Exportar CSV
      </button>
      <button type="button" class="btn" id="sair">Sair</button>
    </div>
  </div>

  <div class="card kpis">
    <div class="kpi kpi-total">
      <span class="lab">Total de visitas</span>
      <span class="kpi-n num" id="k-total">0</span>
      <span class="dica" id="k-total-lab"></span>
    </div>
    <div class="kpi">
      <span class="lab kpi-lab"><span class="ponto" style="background:#3A4043"></span>Espontânea</span>
      <span class="kpi-n num" id="k-esp">0</span>
      <span class="dica" id="k-esp-pct"></span>
    </div>
    <div class="kpi">
      <span class="lab kpi-lab"><span class="ponto" style="background:#E4032B"></span>Corretor house</span>
      <span class="kpi-n num" id="k-house">0</span>
      <span class="dica" id="k-house-pct"></span>
    </div>
    <div class="kpi">
      <span class="lab kpi-lab"><span class="ponto" style="background:#A3ABAE"></span>Imobiliária</span>
      <span class="kpi-n num" id="k-imob">0</span>
      <span class="dica" id="k-imob-pct"></span>
    </div>
    <div class="kpi">
      <span class="lab">Média por dia</span>
      <span class="kpi-n num" id="k-media">0</span>
      <span class="dica" id="k-media-lab"></span>
    </div>
  </div>

  <div class="dupla">
    <section class="card grande">
      <div class="cab">
        <h2 id="grafico-titulo">Visitas por dia</h2>
        <div class="legenda">
          <span><span class="quad" style="background:#3A4043"></span>Espontânea</span>
          <span><span class="quad" style="background:#E4032B"></span>Corretor house</span>
          <span><span class="quad" style="background:#A3ABAE"></span>Imobiliária</span>
        </div>
      </div>
      <div class="rolagem" id="grafico-area">
        <div class="grafico-box">
          <div class="grafico" id="grafico" role="img"></div>
          <div class="rotulos" id="grafico-rotulos" aria-hidden="true"></div>
        </div>
      </div>
      <p class="vazio" id="grafico-vazio" hidden>Nenhuma visita no período para este filtro.</p>
    </section>

    <section class="card lado">
      <h2>Origem das visitas</h2>
      <div class="mix" aria-hidden="true"><div id="o-esp" style="background:#3A4043"></div><div id="o-house" style="background:#E4032B"></div><div id="o-imob" style="background:#A3ABAE"></div></div>
      <div style="display:flex;flex-direction:column;gap:6px">
        <div class="leg-linha"><span><span class="ponto" style="background:#3A4043"></span>Espontânea</span><span class="num" id="ol-esp"></span></div>
        <div class="leg-linha"><span><span class="ponto" style="background:#E4032B"></span>Corretor house</span><span class="num" id="ol-house"></span></div>
        <div class="leg-linha"><span><span class="ponto" style="background:#A3ABAE"></span>Imobiliária</span><span class="num" id="ol-imob"></span></div>
      </div>
      <div class="divisor" style="display:flex;flex-direction:column;gap:10px">
        <h2>Imobiliárias que mais trouxeram</h2>
        <ol class="ranking" id="ranking"></ol>
      </div>
    </section>
  </div>

  <section class="card">
    <div class="cab"><h2>Por empreendimento</h2><span class="dica" id="t-emps-lab"></span></div>
    <div class="rolagem">
      <table style="min-width:720px">
        <thead><tr>
          <th scope="col">Empreendimento</th><th scope="col">Cidade</th>
          <th scope="col" class="dir">Total</th><th scope="col" class="dir">Espontânea</th>
          <th scope="col" class="dir">House</th><th scope="col" class="dir">Imobiliária</th>
          <th scope="col" style="width:200px">Origem</th>
        </tr></thead>
        <tbody id="tab-emps"></tbody>
      </table>
    </div>
  </section>

  <section class="card">
    <div class="cab"><h2>Últimos lançamentos</h2><span class="dica">do período filtrado, mais recentes primeiro</span></div>
    <div class="rolagem">
      <table style="min-width:640px">
        <thead><tr>
          <th scope="col">Data</th><th scope="col">Horário</th><th scope="col">Empreendimento</th>
          <th scope="col">Tipo</th><th scope="col">Detalhe</th>
        </tr></thead>
        <tbody id="tab-recentes"></tbody>
      </table>
    </div>
    <p class="vazio" id="sem-recentes" hidden>Nenhuma visita no período para este filtro.</p>
  </section>
</main>

<script src="assets/config.js"></script>
<script src="assets/visitas.js"></script>
<script src="assets/visitas-api.js"></script>
<script src="assets/visitas-adm-app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create `assets/visitas-adm-app.js`**

```js
/* ============================================================
   VISITAS DA RECEPCAO - interface de /visitas-recepcao-adm
   ------------------------------------------------------------
   Tela de senha + dashboard. Busca os ultimos 30 dias uma vez e
   filtra no navegador. Regras em assets/visitas.js.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md (secao 6)
   ============================================================ */
(function () {
  'use strict';

  var V = window.Visitas;
  var CHAVE_SESSAO = 'visitas.adm.senha';
  var ALTURA_BARRA = 190;
  var PERIODOS = [['hoje', 'Hoje'], ['7', '7 dias'], ['30', '30 dias']];
  var NOME_PERIODO = { hoje: 'Hoje', '7': 'Últimos 7 dias', '30': 'Últimos 30 dias' };
  var EMPS = V.listaEmpreendimentos(window.CITIES || []);
  var CIDADES = ['Todas'].concat((window.CITIES || []).map(function (c) { return c.name; }));
  var estado = { senha: '', todas: [], periodo: '7', cidade: 'Todas', emp: 'Todos', carregadoEm: null, hoje: V.dataLocalIso(new Date()) };
  var api = window.VisitasAPI.criar({
    url: window.VISITAS_APPS_SCRIPT_URL || '',
    senha: function () { return estado.senha; }
  });

  function $(id) { return document.getElementById(id); }
  function el(tag, cls, texto) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }
  function pct(q, t) { return (t ? Math.round(q / t * 100) : 0) + '%'; }
  function lerSessao() { try { return sessionStorage.getItem(CHAVE_SESSAO) || ''; } catch (e) { return ''; } }
  function gravarSessao(s) {
    try { if (s) sessionStorage.setItem(CHAVE_SESSAO, s); else sessionStorage.removeItem(CHAVE_SESSAO); } catch (e) { /* ignora */ }
  }

  /* ---------- senha / sessao (spec 6.1) ---------- */
  function mostrarGate(msg) {
    $('app').hidden = true;
    $('gate').hidden = false;
    $('gate-demo').hidden = !api.demo;
    $('gate-erro').textContent = msg || '';
    $('gate-erro').hidden = !msg;
    $('gate-senha').setAttribute('aria-invalid', msg ? 'true' : 'false');
    $('gate-senha').value = '';
    $('gate-entrar').disabled = false;
    $('gate-entrar').textContent = 'Entrar';
    $('gate-senha').focus();
  }
  function mostrarApp() {
    $('gate').hidden = true;
    $('app').hidden = false;
    $('aviso-demo').hidden = !api.demo;
  }
  function sair(msg) {
    gravarSessao('');
    estado.senha = '';
    estado.todas = [];
    mostrarGate(msg);
  }

  /* ---------- dados ---------- */
  function buscar() {
    estado.hoje = V.dataLocalIso(new Date());
    $('atualizar').disabled = true;
    return api.chamar('listar', { de: V.somarDias(estado.hoje, -29), ate: estado.hoje }).then(function (r) {
      estado.todas = (r.visitas || []).filter(function (v) { return V.TIPOS[v.tipo]; });
      estado.carregadoEm = new Date();
      $('aviso-erro').hidden = true;
      render();
    }).finally(function () { $('atualizar').disabled = false; });
  }
  function tratarErro(f) {
    if (f.codigo === 'senha') { sair('Senha incorreta.'); return; }
    $('aviso-erro-txt').textContent = f.mensagem;
    $('aviso-erro').hidden = false;
  }
  function entrar(ev) {
    ev.preventDefault();
    var s = $('gate-senha').value;
    if (!s) { mostrarGate('Digite a senha.'); return; }
    $('gate-entrar').disabled = true;
    $('gate-entrar').textContent = 'Entrando…';
    estado.senha = s;
    buscar().then(function () {
      gravarSessao(s);
      mostrarApp();
    }, function (f) {
      estado.senha = '';
      mostrarGate(f.codigo === 'senha' ? 'Senha incorreta.' : f.mensagem);
    });
  }

  /* ---------- filtros ---------- */
  function montarChips(caixa, itens, aoEscolher) {
    itens.forEach(function (it) {
      var b = el('button', 'fchip', it[1]);
      b.type = 'button';
      b.setAttribute('data-v', it[0]);
      b.setAttribute('aria-pressed', 'false');
      b.addEventListener('click', function () { aoEscolher(it[0]); });
      caixa.appendChild(b);
    });
  }
  function marcarChips(caixa, valor) {
    Array.prototype.forEach.call(caixa.children, function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-v') === valor ? 'true' : 'false');
    });
  }
  function montarSelectEmp() {
    var sel = $('f-emp');
    sel.textContent = '';
    var todos = el('option', '', 'Todos os empreendimentos');
    todos.value = 'Todos';
    sel.appendChild(todos);
    EMPS.forEach(function (e) {
      if (estado.cidade !== 'Todas' && e.cidade !== estado.cidade) return;
      var o = el('option', '', e.nome);
      o.value = e.nome;
      sel.appendChild(o);
    });
    sel.value = estado.emp;
  }
  function filtroAtual() {
    var iv = V.intervalo(estado.periodo, estado.hoje);
    return {
      iv: iv,
      visitas: V.filtrar(estado.todas, { de: iv.de, ate: iv.ate, cidade: estado.cidade, empreendimento: estado.emp }),
      lista: EMPS.filter(function (e) {
        return (estado.cidade === 'Todas' || e.cidade === estado.cidade) && (estado.emp === 'Todos' || e.nome === estado.emp);
      })
    };
  }

  /* ---------- render (spec 6.2) ---------- */
  function render() {
    marcarChips($('periodos'), estado.periodo);
    marcarChips($('cidades'), estado.cidade);
    var f = filtroAtual(), iv = f.iv, t = V.totaisPorTipo(f.visitas);
    var rotulo = estado.periodo === 'hoje'
      ? 'Hoje, ' + V.dataCurta(iv.ate)
      : NOME_PERIODO[estado.periodo] + ' · ' + V.dataCurta(iv.de) + ' a ' + V.dataCurta(iv.ate);

    $('k-total').textContent = t.total;
    $('k-total-lab').textContent = rotulo;
    $('t-emps-lab').textContent = rotulo;
    V.ORDEM_TIPOS.forEach(function (k) {
      $('k-' + k).textContent = t[k];
      $('k-' + k + '-pct').textContent = pct(t[k], t.total) + ' do total';
      $('o-' + k).style.width = (t.total ? t[k] / t.total * 100 : 0) + '%';
      $('ol-' + k).textContent = pct(t[k], t.total) + ' · ' + t[k];
    });
    $('k-media').textContent = (t.total / iv.dias).toFixed(1).replace('.', ',');
    $('k-media-lab').textContent = estado.periodo === 'hoje' ? 'dia em andamento' : 'em ' + iv.dias + ' dias';

    renderGrafico(f.visitas, iv);
    renderRanking(V.rankingImobiliarias(f.visitas, 5));
    renderTabelaEmps(V.porEmpreendimento(f.visitas, f.lista));
    renderRecentes(V.recentes(f.visitas, 8));
    $('atualizado-em').textContent = estado.carregadoEm ? 'Atualizado às ' + V.horaLocal(estado.carregadoEm) : '';
  }

  function renderGrafico(visitas, iv) {
    var porHora = estado.periodo === 'hoje';
    var cols = porHora ? V.porHora(visitas, 8, 20) : V.porDia(visitas, iv.de, iv.ate);
    var max = Math.max.apply(null, cols.map(function (c) { return c.total; }).concat([1]));
    var g = $('grafico'), r = $('grafico-rotulos');
    var titulo = porHora ? 'Visitas por horário · hoje' : 'Visitas por dia';
    $('grafico-titulo').textContent = titulo;
    g.setAttribute('aria-label', titulo + ': ' + visitas.length + ' visitas');
    g.textContent = '';
    r.textContent = '';
    cols.forEach(function (c, i) {
      var nome = porHora ? c.hora + 'h' : V.rotuloDia(c.data);
      var rotulo = porHora ? c.hora + 'h'
        : iv.dias <= 7 ? V.rotuloDia(c.data)
          : (cols.length - 1 - i) % 5 === 0 ? V.dataCurta(c.data) : '';
      var col = el('div', 'col');
      col.title = nome + ' · ' + c.total + ' visitas (' + c.esp + ' espontâneas, ' + c.house + ' house, ' + c.imob + ' imobiliária)';
      col.appendChild(el('span', 'col-val num', (porHora || iv.dias <= 7) && c.total ? String(c.total) : ''));
      var pilha = el('div', 'pilha');
      ['imob', 'house', 'esp'].forEach(function (k) {
        var s = el('div');
        s.style.height = Math.round(c[k] / max * ALTURA_BARRA) + 'px';
        s.style.background = V.TIPOS[k].cor;
        pilha.appendChild(s);
      });
      col.appendChild(pilha);
      g.appendChild(col);
      r.appendChild(el('span', 'rot num', rotulo));
    });
    $('grafico-area').hidden = visitas.length === 0;
    $('grafico-vazio').hidden = visitas.length > 0;
  }

  function renderRanking(lista) {
    var ol = $('ranking');
    ol.textContent = '';
    if (!lista.length) { ol.appendChild(el('li', 'dica', 'Nenhuma visita de imobiliária no período.')); return; }
    var max = lista[0].qtd;
    lista.forEach(function (it) {
      var li = el('li');
      var topo = el('div', 'leg-linha');
      topo.appendChild(el('span', '', it.nome));
      topo.appendChild(el('strong', 'num', String(it.qtd)));
      var trilho = el('div', 'rank-trilho');
      var barra = el('div');
      barra.style.width = (it.qtd / max * 100) + '%';
      trilho.appendChild(barra);
      li.appendChild(topo);
      li.appendChild(trilho);
      ol.appendChild(li);
    });
  }

  function celula(tr, texto, cls) { var td = el('td', cls, texto); tr.appendChild(td); return td; }

  function renderTabelaEmps(linhas) {
    var tb = $('tab-emps');
    tb.textContent = '';
    linhas.forEach(function (l) {
      var tr = el('tr');
      celula(tr, l.nome, 'forte');
      celula(tr, l.cidade, 'suave');
      celula(tr, String(l.total), 'dir forte num');
      celula(tr, String(l.esp), 'dir num');
      celula(tr, String(l.house), 'dir num');
      celula(tr, String(l.imob), 'dir num');
      var td = celula(tr, '');
      var mix = el('div', 'mix mix-p');
      V.ORDEM_TIPOS.forEach(function (k) {
        var s = el('div');
        s.style.width = (l.total ? l[k] / l.total * 100 : 0) + '%';
        s.style.background = V.TIPOS[k].cor;
        mix.appendChild(s);
      });
      td.appendChild(mix);
      tb.appendChild(tr);
    });
  }

  function renderRecentes(lista) {
    var tb = $('tab-recentes');
    tb.textContent = '';
    lista.forEach(function (v) {
      var tr = el('tr');
      celula(tr, V.dataCurta(v.data), 'num');
      celula(tr, v.hora, 'forte num');
      celula(tr, v.empreendimento);
      var td = celula(tr, '');
      var badge = el('span', 'badge');
      var ponto = el('span', 'ponto');
      ponto.style.background = V.TIPOS[v.tipo].cor;
      badge.appendChild(ponto);
      badge.appendChild(document.createTextNode(V.TIPOS[v.tipo].nome));
      td.appendChild(badge);
      celula(tr, V.detalhe(v), 'suave');
      tb.appendChild(tr);
    });
    $('sem-recentes').hidden = lista.length > 0;
  }

  function exportar() {
    var f = filtroAtual();
    var blob = new Blob([V.gerarCSV(f.visitas)], { type: 'text/csv;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = V.nomeArquivoCSV(f.iv.de, f.iv.ate);
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  /* ---------- inicio ---------- */
  function iniciar() {
    montarChips($('periodos'), PERIODOS, function (v) { estado.periodo = v; render(); });
    montarChips($('cidades'), CIDADES.map(function (c) { return [c, c]; }), function (v) {
      estado.cidade = v;
      estado.emp = 'Todos';
      montarSelectEmp();
      render();
    });
    montarSelectEmp();
    $('f-emp').addEventListener('change', function () { estado.emp = $('f-emp').value; render(); });
    $('gate-form').addEventListener('submit', entrar);
    $('atualizar').addEventListener('click', function () { buscar().catch(tratarErro); });
    $('aviso-erro-tentar').addEventListener('click', function () { buscar().catch(tratarErro); });
    $('exportar').addEventListener('click', exportar);
    $('sair').addEventListener('click', function () { sair(); });

    var salva = lerSessao();
    if (salva) {
      estado.senha = salva;
      mostrarApp();
      render();
      buscar().catch(tratarErro);
    } else {
      mostrarGate();
    }
  }

  iniciar();
})();
```

- [ ] **Step 3: Syntax check**

Run: `node --check assets/visitas-adm-app.js && node --test tests/*.test.js`
Expected: sem erros; testes PASS

- [ ] **Step 4: Verify in the browser (demo mode)**

Com o mesmo preview da Task 6, abra `/visitas-recepcao-adm.html`. No modo demo qualquer senha entra; use o valor de teste `demo`.

Confira:
1. Abre na tela de senha, com o aviso "Modo demonstração". Entrar com o campo vazio mostra "Digite a senha.".
2. Depois de entrar, o dashboard aparece com 7 dias marcado, o aviso demo e "Atualizado às HH:mm".
3. Total = Espontânea + House + Imobiliária, e as % somam ~100%.
4. "Hoje" → o título vira "Visitas por horário · hoje", com barras de 8h a 20h e "dia em andamento". "30 dias" → 30 barras, com rótulo a cada 5 dias.
5. Cidade "Sorocaba" → o select só tem Todos + Conquista Vila da Mata, e a tabela tem 1 linha. Voltar para "Todas" volta para 10 linhas.
6. "Exportar CSV" baixa `visitas-AAAA-MM-DD-a-AAAA-MM-DD.csv`. Confira com `read_network_requests` / console que não houve erro. **Não** abra o arquivo baixado.
7. Recarregar a página (F5) mantém a sessão. "Sair" volta para a tela de senha.
8. `resize_window` mobile: os filtros quebram linha, os números empilham, gráfico e tabelas rolam dentro da caixa e não há rolagem horizontal na página. Volte para `desktop`.

Tire um screenshot do dashboard em 7 dias.

- [ ] **Step 5: Commit**

```bash
git add visitas-recepcao-adm.html assets/visitas-adm-app.js
git commit -m "feat(visitas): dashboard de visitas com senha, graficos e CSV

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Documentação, implantação e PR

**Files:**
- Modify: `README.md` (bloco "Estrutura" + seção nova antes de "## Rodar localmente")

**Interfaces:**
- Consumes: tudo das Tasks 1–7.

- [ ] **Step 1: Update `README.md`**

No bloco de código de "## Estrutura", depois de `pendencias-vendas.html  Pendências de Vendas (interno, comercial, com senha)`, acrescente:

```
visitas-recepcao.html   Lançamento de visitas no stand (recepção, pública)
visitas-recepcao-adm.html  Dashboard de visitas (interno, com senha)
```

Depois de `  pendencias-app.js     Interface da página de pendências`, acrescente:

```
  visitas.js            Regras das páginas de visitas (puras, testadas)
  visitas-api.js        Cliente do Web App de visitas + modo demonstração
  visitas-recepcao-app.js  Interface da recepção
  visitas-adm-app.js    Interface do dashboard de visitas
```

Depois de `  apps-script-pendencias.gs   Web App da página de pendências`, acrescente:

```
  apps-script-visitas.gs      Web App das páginas de visitas
```

Antes de `## Rodar localmente`, acrescente:

````markdown
## Visitas da recepção

- `/visitas-recepcao`: a recepcionista lança cada visita do stand (espontânea,
  agendada por corretor house ou trazida por imobiliária) e vê o total do dia.
  Página pública, sem senha.
- `/visitas-recepcao-adm`: dashboard do comercial, com senha (Script Property
  `VISITAS_SENHA` no Apps Script; a senha não fica no repositório).
- Dados na aba `VISITAS` da planilha de visitas, via Web App
  (`docs/apps-script-visitas.gs`, instruções de implantação no cabeçalho).
- `window.VISITAS_APPS_SCRIPT_URL` em `assets/config.js` = URL `/exec` do Web App.
  Vazio (ou `?demo=1`) = **modo demonstração** com dados fictícios na memória da aba.
- Empreendimento novo no `config.js` também precisa entrar em
  `VISITAS_EMPREENDIMENTOS` no `.gs`. O teste de paridade avisa se esquecer.

Spec: `docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md`.
````

- [ ] **Step 2: Run the full suite**

Run: `node --test tests/*.test.js`
Expected: PASS (pendências + visitas)

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(visitas): readme das paginas de visitas

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Hand off the Apps Script deployment to the user (manual, needs their Google account)**

Peça ao usuário, sem executar você mesmo:
1. Abrir a planilha `10Hi4moBVJlK6Gs3wdULQPGai8vGZu_JhSYX4CKWLTfk` > Extensões > Apps Script e colar `docs/apps-script-visitas.gs`.
2. Só no editor, preencher `VIS_SENHA_INICIAL` com a senha do dashboard, executar `configurarSenhaVisitas`, voltar a linha para `''` e salvar.
3. Executar `testeVisitas` e conferir o log (a aba `VISITAS` é criada, e a linha de teste fica com `Excluída = 1`).
4. Implantar como App da Web (Executar como: Eu · Quem tem acesso: Qualquer pessoa) e mandar a URL `/exec`.

Quando a URL chegar: preencha `window.VISITAS_APPS_SCRIPT_URL` em `assets/config.js`, rode `node --test tests/*.test.js` e commite:

```bash
git add assets/config.js
git commit -m "chore(visitas): apontar para o Web App publicado

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 5: Smoke test against the real Web App**

Com a URL configurada, no preview local (`/visitas-recepcao.html`, sem `?demo=1`):
1. Registrar uma visita de cada tipo no stand `Alta Vista Mangará`, com imobiliária "TESTE - pode ignorar".
2. Conferir que o contador soma 3 e que a lista mostra a lixeira.
3. Excluir as 3 pela lixeira.
4. Abrir `/visitas-recepcao-adm.html`. **Quem digita a senha real é o usuário.** Peça para ele entrar e conferir que as visitas excluídas não aparecem.

- [ ] **Step 6: Finish the branch**

Use a skill `superpowers:finishing-a-development-branch`. O fluxo do repo (`WORKFLOW.md`) é branch → PR → merge na `main` → deploy manual na Vercel. Abra o PR com `gh pr create` e termine a descrição com `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.

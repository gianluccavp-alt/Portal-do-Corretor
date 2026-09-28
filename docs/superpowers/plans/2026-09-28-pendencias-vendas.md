# Pendências de Vendas — Plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publicar `/pendencias-vendas`, uma página com senha para o time comercial cobrar pendências das vendas da aba RELATÓRIO. Nela o time vê KPIs e filtros, abre o detalhe de cada venda, edita Observação/Retorno, cancela/reativa vendas e dispara a atualização do Salesforce.

**Architecture:** Site estático (HTML/CSS/JS puro, sem build) na Vercel. A página conversa só com um Web App do Apps Script, colado no projeto já vinculado à planilha: `POST text/plain` com `{senha, acao, ...}`, resposta em JSON. A senha fica só no servidor. As regras de negócio (pendências, filtros, KPIs, ordenação, formatação) ficam num módulo puro, `assets/pendencias.js`, testado com `node --test`. A interface (`assets/pendencias-app.js`) só lê o estado e mexe no DOM. Sem URL do Web App configurada, a página entra em **modo demonstração**: lê `tests/fixtures/vendas.json` e não grava nada.

**Tech Stack:** HTML5 + CSS + JavaScript ES5/ES2015 no navegador (sem framework, sem bundler) · Node 22 (`node:test`, só para testes) · Google Apps Script V8 (SpreadsheetApp, LockService, PropertiesService, ContentService) · Vercel (estático, `cleanUrls`).

**Spec:** `docs/superpowers/specs/2026-09-28-pendencias-vendas-design.md`. Telas aprovadas em `docs/design/pendencias-vendas/telas/*.png` (as prévias HTML ficam em `docs/design/pendencias-vendas/previa/`).

## Global Constraints

- Site 100% estático: nada de `package.json`, bundler ou dependência npm. Os testes usam só `node:test` e `node:assert/strict`.
- Siga `WORKFLOW.md`: trabalhe na branch `feat/pendencias-vendas` (já existe), **nunca** faça commit direto na `main` e **nunca** faça deploy na Vercel (é manual, do Gabriel).
- Toda mensagem de commit termina com a linha `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (separada por uma linha em branco).
- Visual: `DESIGN.md` (mundo Direcional).
  - Fonte: DM Sans.
  - Vermelho `#E4032B` só para ação e status; hover `#B8001F`.
  - Tinta `#3A4043`; cinza `#727A7D`; borda `#E7E9EA`; fundo `#F5F6F7`; superfície `#FFFFFF`; campo silenciado `#FAFBFB`.
  - Foco: borda vermelha + `box-shadow: 0 0 0 3px rgba(228,3,43,.10)`.
  - Nada de Playfair, dourado ou creme.
- A senha **não** aparece no código do site. Ela fica na Script Property `PENDENCIAS_SENHA` do Apps Script (valor inicial `Comercial123`).
- Planilha: aba `RELATÓRIO`, cabeçalho na **linha 3**, colunas localizadas **pelo nome**. Colunas obrigatórias: `ID`, `Observação`, `Retorno`.
- Fases padrão (exatas): `Aprovado Pró Soluto`, `Proposta Aprovada`, `Aprovado SAFI`, `Análise SAFI`.
- Vermelhos que marcam venda cancelada (iguais ao script existente): `#ff0000`, `#f00`, `red`, `#cc0000`, `#990000`, `#b00000`, ou fonte `line-through`.
- Destaque de "dias em aberto" a partir de **15 dias** (cor `#8A5700`).
- Todo texto vindo da planilha entra no DOM via `textContent`, nunca `innerHTML`.
- Dados de exemplo são **fictícios**. Nunca coloque nome, CPF ou texto real da planilha em fixture, teste ou commit.
- Idioma da interface e das mensagens: português do Brasil.
- **Refinamentos em relação à spec** (decididos no plano, sem mudar comportamento acordado):
  - A interface fica em `assets/pendencias-app.js`, separada do HTML, para o arquivo da página não passar de ~1000 linhas.
  - Os testes são 3 arquivos por assunto, em vez de um `tests/pendencias.test.js`.
  - Há um **modo demonstração** (URL vazia ou `?demo=1`) com a fixture fictícia, para desenvolver e testar a interface sem o Web App.

---

## Mapa de arquivos

| Arquivo | Responsabilidade | Tarefa |
|---|---|---|
| `assets/pendencias.js` | Regras puras: texto, datas, formatação, pendências, checklist, filtros, KPIs, ordenação, opções de filtro. `window.Pendencias` / `module.exports`. | 1, 2, 3 |
| `tests/pendencias-texto.test.js` | Testes de normalização, formatação e datas | 1 |
| `tests/pendencias-regras.test.js` | Testes de pendências, badge de AC e checklist | 2 |
| `tests/pendencias-filtros.test.js` | Testes de filtros, KPIs, ordenação, opções | 3 |
| `tests/fixtures/vendas.json` | 15 vendas fictícias no formato do Web App (também é o dado do modo demonstração) | 3 |
| `docs/apps-script-pendencias.gs` | Web App: `doPost` (listar, cancelar, reativar, editar, atualizar), lock, senha, `testePendencias()` | 4 |
| `assets/config.js` | + `window.PENDENCIAS_APPS_SCRIPT_URL` | 5 |
| `pendencias-vendas.html` | Markup e CSS da página inteira: senha, cabeçalho, KPIs, filtros, lista, painel, diálogos, folha de filtros, toast | 5 |
| `assets/pendencias-app.js` | Interface: API/modo demo, sessão, render da lista, filtros, painel, edições, atualização, folha mobile | 6, 7, 8 |
| `README.md` | Documentar a página, o Web App e como rodar os testes | 9 |

---

### Task 1: Módulo de regras: texto, formatação e datas

**Files:**
- Create: `assets/pendencias.js`
- Test: `tests/pendencias-texto.test.js`

**Interfaces:**
- Consumes: nada.
- Produces (todos em `window.Pendencias` / `module.exports`):
  - `FASES_PADRAO: string[]`, `DIAS_ALERTA: 15`
  - `normalizar(v) → string`, `titleCase(s) → string`, `formatarEquipe(imobiliaria) → string`
  - `formatarValor(n, comCentavos?) → string`, `formatarMi(n) → string`
  - `parseData('dd/mm/aaaa[ hh:mm[:ss]]') → Date|null`, `inicioDoDia(Date) → Date`, `diasEntre(de, ate) → int`
  - `diasEmAberto(dataVenda, hoje) → int|null`, `textoDias(int|null) → string`, `isoParaData('aaaa-mm-dd') → Date|null`
  - `formatarAtualizacao(iso|null, agora) → string`
  - `justificativaExibida(s) → string`, `notaDaLinha(venda) → string`
  - `rankingChave(s) → string`, `rankingRotulo(s) → string`

- [ ] **Step 1: Escrever os testes que falham**

Crie `tests/pendencias-texto.test.js`:

```js
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
  assert.equal(P.formatarEquipe('DIRECIONAL VENDAS SPI – EQUIPE LEONARDO DONIZETE'), 'Equipe Leonardo Donizete');
  assert.equal(P.formatarEquipe('DIRECIONAL VENDAS SPI - EQUIPE SABRINA DA SILVA - Inativo'), 'Equipe Sabrina da Silva - Inativo');
  assert.equal(P.formatarEquipe('DIRECIONAL VENDAS SPI ? EQUIPE GIAN TURIONI - Inativo'), 'Equipe Gian Turioni - Inativo');
  assert.equal(P.formatarEquipe('SPI - CANAL IMOB PJ – CAROLINA CRISTINA'), 'Canal PJ · Carolina Cristina');
  assert.equal(P.formatarEquipe('SPI - CANAL IMOB PJ - MARIA CECILIA - Inativo'), 'Canal PJ · Maria Cecilia - Inativo');
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
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/pendencias-texto.test.js`
Expected: FAIL com `Cannot find module '../assets/pendencias.js'`

- [ ] **Step 3: Implementar o módulo**

Crie `assets/pendencias.js`. As Tasks 2 e 3 acrescentam funções nos pontos marcados como `/* ---------- pendencias ---------- */` e `/* ---------- filtros ---------- */`, e na lista de export.

```js
/* ============================================================
   PENDENCIAS DE VENDAS - regras de negocio
   ------------------------------------------------------------
   Funcoes puras (sem DOM, sem rede). Usadas pela pagina
   /pendencias-vendas via window.Pendencias e pelos testes
   (node --test tests/*.test.js).
   Spec: docs/superpowers/specs/2026-09-28-pendencias-vendas-design.md
   ============================================================ */
(function (raiz) {
  'use strict';

  var FASES_PADRAO = ['Aprovado Pró Soluto', 'Proposta Aprovada', 'Aprovado SAFI', 'Análise SAFI'];
  var DIAS_ALERTA = 15;
  var DIA_MS = 86400000;
  /* separador da coluna Imobiliaria: "-", "–", "—" ou o "?" que aparece
     quando o travessao chega corrompido do Salesforce */
  var SEP = '\\s*[-\u2013\u2014?\uFFFD]\\s*';

  /* ---------- texto ---------- */
  function normalizar(valor) {
    if (valor === null || valor === undefined) return '';
    return String(valor).trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  var CONECTIVOS = { da: 1, de: 1, di: 1, 'do': 1, dos: 1, das: 1, e: 1 };
  function titleCase(texto) {
    return String(texto || '').trim().toLowerCase().split(/\s+/).filter(Boolean)
      .map(function (p, i) { return i > 0 && CONECTIVOS[p] ? p : p.charAt(0).toUpperCase() + p.slice(1); })
      .join(' ');
  }

  function formatarEquipe(imobiliaria) {
    var t = String(imobiliaria || '').trim();
    if (!t) return '—';
    var sufixo = '';
    var inativo = t.match(new RegExp(SEP + 'inativo\\s*$', 'i'));
    if (inativo) { sufixo = ' - Inativo'; t = t.slice(0, inativo.index); }
    var pj = t.match(new RegExp('^SPI' + SEP + 'CANAL IMOB PJ' + SEP + '(.+)$', 'i'));
    if (pj) return 'Canal PJ · ' + titleCase(pj[1]) + sufixo;
    t = t.replace(new RegExp('^DIRECIONAL VENDAS SPI' + SEP, 'i'), '');
    return titleCase(t) + sufixo;
  }

  function formatarValor(valor, comCentavos) {
    if (valor === null || valor === undefined || valor === '' || isNaN(Number(valor))) return 'Não informado';
    var casas = comCentavos ? 2 : 0;
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency', currency: 'BRL', minimumFractionDigits: casas, maximumFractionDigits: casas
    }).format(Number(valor)).replace(/\u00a0/g, ' ');
  }

  function formatarMi(valor) {
    var n = Number(valor) || 0;
    if (n >= 1e6) return 'R$ ' + (n / 1e6).toFixed(2).replace('.', ',') + ' mi';
    return formatarValor(n, false);
  }

  /* ---------- datas ---------- */
  function parseData(texto) {
    var m = String(texto || '').trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})(?:\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?$/);
    if (!m) return null;
    var d = new Date(+m[3], +m[2] - 1, +m[1], +(m[4] || 0), +(m[5] || 0), +(m[6] || 0));
    return isNaN(d.getTime()) ? null : d;
  }
  function inicioDoDia(d) { return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }
  /* Math.round absorve a hora a mais/a menos do horario de verao */
  function diasEntre(de, ate) { return Math.round((inicioDoDia(ate) - inicioDoDia(de)) / DIA_MS); }
  function diasEmAberto(dataVenda, hoje) {
    var d = parseData(dataVenda);
    return d ? diasEntre(d, hoje) : null;
  }
  function textoDias(dias) {
    if (dias === null || dias === undefined) return '—';
    if (dias === 0) return 'hoje';
    return dias + (dias === 1 ? ' dia' : ' dias');
  }
  function isoParaData(iso) {
    var m = String(iso || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
    return m ? new Date(+m[1], +m[2] - 1, +m[3]) : null;
  }
  function doisDigitos(n) { return (n < 10 ? '0' : '') + n; }
  function formatarAtualizacao(iso, agora) {
    var d = iso ? new Date(iso) : null;
    if (!d || isNaN(d.getTime())) return 'Última atualização do Salesforce desconhecida';
    var hora = doisDigitos(d.getHours()) + ':' + doisDigitos(d.getMinutes());
    if (diasEntre(d, agora) === 0) return 'Salesforce atualizado hoje às ' + hora;
    return 'Salesforce atualizado em ' + doisDigitos(d.getDate()) + '/' + doisDigitos(d.getMonth() + 1) +
      '/' + d.getFullYear() + ' às ' + hora;
  }

  /* ---------- exibicao ---------- */
  function justificativaExibida(texto) {
    var t = String(texto || '').trim();
    return t === '' || t === '.' ? 'Sem justificativa registrada' : t;
  }
  function notaDaLinha(venda) {
    var r = String(venda.retorno || '').trim();
    if (r) return 'Retorno: ' + r;
    var o = String(venda.observacao || '').trim();
    if (o) return 'Obs.: ' + o;
    return '';
  }
  var RANKINGS = { diamante: 'Diamante', ouro: 'Ouro', prata: 'Prata', bronze: 'Bronze', aco: 'Aço' };
  function rankingChave(ranking) { return normalizar(ranking).replace(/[^a-z]/g, ''); }
  function rankingRotulo(ranking) { return RANKINGS[rankingChave(ranking)] || String(ranking || '').trim(); }

  /* ---------- pendencias ---------- */

  /* ---------- filtros ---------- */

  var api = {
    FASES_PADRAO: FASES_PADRAO,
    DIAS_ALERTA: DIAS_ALERTA,
    normalizar: normalizar,
    titleCase: titleCase,
    formatarEquipe: formatarEquipe,
    formatarValor: formatarValor,
    formatarMi: formatarMi,
    parseData: parseData,
    inicioDoDia: inicioDoDia,
    diasEntre: diasEntre,
    diasEmAberto: diasEmAberto,
    textoDias: textoDias,
    isoParaData: isoParaData,
    formatarAtualizacao: formatarAtualizacao,
    justificativaExibida: justificativaExibida,
    notaDaLinha: notaDaLinha,
    rankingChave: rankingChave,
    rankingRotulo: rankingRotulo
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.Pendencias = api;
})(this);
```

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test tests/pendencias-texto.test.js`
Expected: PASS, 13 testes, 0 falhas.

- [ ] **Step 5: Commit**

```bash
git add assets/pendencias.js tests/pendencias-texto.test.js
git commit -m "feat(pendencias): módulo de regras com formatação e datas

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Pendências de uma venda, badge de AC e checklist

**Files:**
- Modify: `assets/pendencias.js` (bloco `/* ---------- pendencias ---------- */` e o objeto `api`)
- Test: `tests/pendencias-regras.test.js`

**Interfaces:**
- Consumes: `normalizar` (Task 1).
- Produces:
  - `derivarPendencias(venda) → Array<{chave:'ac'|'fid'|'ato'|'pcv', rotulo:string, estilo:'err'|'warn'}>`, sempre na ordem ac, fid, ato, pcv.
  - `statusAcBadge(venda) → {rotulo, estilo:'ok'|'err'|'neu'}`
  - `checklist(venda) → Array<{chave, ok:boolean, estilo:'ok'|'err'|'warn', titulo, detalhe}>`, 4 itens na ordem ac, fid, ato, pcv.
- Formato de `venda` (vem do Web App, Task 4): `{ id, cliente, dataVenda, fase, imobiliaria, empreendimento, identificador, vendaFacilitada:boolean, fid, pcvAssinadoEm, boletoPago:boolean, cartaoPago:boolean, valorReal:number|null, ranking, justificativa, statusAC, observacao, retorno, cancelada:boolean }`.

- [ ] **Step 1: Escrever os testes que falham**

Crie `tests/pendencias-regras.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const P = require('../assets/pendencias.js');

function venda(extra) {
  return Object.assign({
    id: 'OP-000001', statusAC: 'Análise aprovada', fid: '700001',
    pcvAssinadoEm: '10/09/2026', boletoPago: true, cartaoPago: false
  }, extra);
}
const chaves = (v) => P.derivarPendencias(v).map((p) => p.chave);

test('venda sem nada pendente', () => {
  assert.deepEqual(P.derivarPendencias(venda()), []);
});

test('AC não aprovada: rótulo e estilo por status', () => {
  const casos = [
    ['Análise reprovada', 'AC reprovada', 'err'],
    ['Enviado para análise', 'AC em análise', 'warn'],
    ['Rascunho', 'AC não enviada', 'err'],
    ['', 'AC não enviada', 'err'],
    ['Aguardando banco', 'Aguardando banco', 'warn']
  ];
  for (const [statusAC, rotulo, estilo] of casos) {
    assert.deepEqual(P.derivarPendencias(venda({ statusAC })), [{ chave: 'ac', rotulo, estilo }], statusAC);
  }
});

test('AC aprovada ignora acento e caixa', () => {
  assert.deepEqual(chaves(venda({ statusAC: 'ANALISE APROVADA' })), []);
});

test('FID e PCV vazios viram pendência', () => {
  assert.deepEqual(chaves(venda({ fid: '' })), ['fid']);
  assert.deepEqual(chaves(venda({ fid: '   ' })), ['fid']);
  assert.deepEqual(chaves(venda({ fid: null })), ['fid']);
  assert.deepEqual(chaves(venda({ pcvAssinadoEm: '' })), ['pcv']);
});

test('ato: basta boleto/PIX ou cartão pago', () => {
  assert.deepEqual(chaves(venda({ boletoPago: true, cartaoPago: false })), []);
  assert.deepEqual(chaves(venda({ boletoPago: false, cartaoPago: true })), []);
  assert.deepEqual(chaves(venda({ boletoPago: true, cartaoPago: true })), []);
  assert.deepEqual(chaves(venda({ boletoPago: false, cartaoPago: false })), ['ato']);
});

test('ordem dos chips: ac, fid, ato, pcv', () => {
  const v = venda({ statusAC: '', fid: '', boletoPago: false, cartaoPago: false, pcvAssinadoEm: '' });
  assert.deepEqual(chaves(v), ['ac', 'fid', 'ato', 'pcv']);
});

test('statusAcBadge', () => {
  const casos = [
    ['Análise aprovada', 'Aprovada', 'ok'],
    ['Análise reprovada', 'Reprovada', 'err'],
    ['Enviado para análise', 'Em análise', 'neu'],
    ['Rascunho', 'Rascunho', 'neu'],
    ['', 'Sem análise', 'neu'],
    ['Outro status', 'Outro status', 'neu']
  ];
  for (const [statusAC, rotulo, estilo] of casos) {
    assert.deepEqual(P.statusAcBadge(venda({ statusAC })), { rotulo, estilo }, statusAC);
  }
});

test('checklist com pendências', () => {
  const itens = P.checklist(venda({ statusAC: 'Análise reprovada', fid: '', boletoPago: false, cartaoPago: false }));
  assert.deepEqual(itens.map((i) => [i.chave, i.ok]), [['ac', false], ['fid', false], ['ato', false], ['pcv', true]]);
  assert.equal(itens[0].titulo, 'AC reprovada');
  assert.equal(itens[0].estilo, 'err');
  assert.equal(itens[0].detalhe, 'Status AC: Análise reprovada');
  assert.equal(itens[1].detalhe, 'Nenhum FID registrado no Salesforce');
  assert.equal(itens[2].detalhe, 'Boleto/PIX: Não · Cartão: Não');
  assert.equal(itens[3].titulo, 'PCV assinado');
  assert.equal(itens[3].detalhe, 'Cliente assinou em 10/09/2026');
});

test('checklist sem pendências', () => {
  const itens = P.checklist(venda());
  assert.ok(itens.every((i) => i.ok && i.estilo === 'ok'));
  assert.equal(itens[0].titulo, 'AC aprovada');
  assert.equal(itens[1].titulo, 'FID 700001');
  assert.equal(itens[2].titulo, 'Ato pago');
  assert.equal(itens[2].detalhe, 'Boleto/PIX: Sim · Cartão: Não');
});

test('checklist com AC vazia diz "sem análise"', () => {
  assert.equal(P.checklist(venda({ statusAC: '' }))[0].detalhe, 'Status AC: sem análise');
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/pendencias-regras.test.js`
Expected: FAIL com `TypeError: P.derivarPendencias is not a function`

- [ ] **Step 3: Implementar**

Em `assets/pendencias.js`, troque a linha `  /* ---------- pendencias ---------- */` por:

```js
  /* ---------- pendencias ---------- */
  function vazio(v) { return String(v === null || v === undefined ? '' : v).trim() === ''; }

  function statusAcBadge(venda) {
    var s = normalizar(venda.statusAC);
    if (s === 'analise aprovada') return { rotulo: 'Aprovada', estilo: 'ok' };
    if (s === 'analise reprovada') return { rotulo: 'Reprovada', estilo: 'err' };
    if (s === 'enviado para analise') return { rotulo: 'Em análise', estilo: 'neu' };
    if (s === 'rascunho') return { rotulo: 'Rascunho', estilo: 'neu' };
    if (s === '') return { rotulo: 'Sem análise', estilo: 'neu' };
    return { rotulo: String(venda.statusAC).trim(), estilo: 'neu' };
  }

  function pendenciaAc(venda) {
    var s = normalizar(venda.statusAC);
    if (s === 'analise aprovada') return null;
    if (s === 'analise reprovada') return { chave: 'ac', rotulo: 'AC reprovada', estilo: 'err' };
    if (s === 'enviado para analise') return { chave: 'ac', rotulo: 'AC em análise', estilo: 'warn' };
    if (s === '' || s === 'rascunho') return { chave: 'ac', rotulo: 'AC não enviada', estilo: 'err' };
    return { chave: 'ac', rotulo: String(venda.statusAC).trim(), estilo: 'warn' };
  }

  function derivarPendencias(venda) {
    var itens = [];
    var ac = pendenciaAc(venda);
    if (ac) itens.push(ac);
    if (vazio(venda.fid)) itens.push({ chave: 'fid', rotulo: 'Sem FID', estilo: 'warn' });
    if (!venda.boletoPago && !venda.cartaoPago) itens.push({ chave: 'ato', rotulo: 'Ato não pago', estilo: 'warn' });
    if (vazio(venda.pcvAssinadoEm)) itens.push({ chave: 'pcv', rotulo: 'PCV não assinado', estilo: 'warn' });
    return itens;
  }

  function simNao(b) { return b ? 'Sim' : 'Não'; }

  function checklist(venda) {
    var ac = pendenciaAc(venda);
    var pagamentos = 'Boleto/PIX: ' + simNao(venda.boletoPago) + ' · Cartão: ' + simNao(venda.cartaoPago);
    return [
      ac
        ? { chave: 'ac', ok: false, estilo: ac.estilo, titulo: ac.rotulo,
            detalhe: 'Status AC: ' + (vazio(venda.statusAC) ? 'sem análise' : String(venda.statusAC).trim()) }
        : { chave: 'ac', ok: true, estilo: 'ok', titulo: 'AC aprovada', detalhe: 'Status AC: Análise aprovada' },
      vazio(venda.fid)
        ? { chave: 'fid', ok: false, estilo: 'warn', titulo: 'Sem FID', detalhe: 'Nenhum FID registrado no Salesforce' }
        : { chave: 'fid', ok: true, estilo: 'ok', titulo: 'FID ' + String(venda.fid).trim(), detalhe: 'Registrado no Salesforce' },
      !venda.boletoPago && !venda.cartaoPago
        ? { chave: 'ato', ok: false, estilo: 'warn', titulo: 'Ato não pago', detalhe: pagamentos }
        : { chave: 'ato', ok: true, estilo: 'ok', titulo: 'Ato pago', detalhe: pagamentos },
      vazio(venda.pcvAssinadoEm)
        ? { chave: 'pcv', ok: false, estilo: 'warn', titulo: 'PCV não assinado', detalhe: 'Cliente ainda não assinou' }
        : { chave: 'pcv', ok: true, estilo: 'ok', titulo: 'PCV assinado', detalhe: 'Cliente assinou em ' + String(venda.pcvAssinadoEm).trim() }
    ];
  }
```

No objeto `api`, acrescente depois de `rankingRotulo: rankingRotulo`:

```js
    rankingRotulo: rankingRotulo,
    statusAcBadge: statusAcBadge,
    derivarPendencias: derivarPendencias,
    checklist: checklist
```

(troque a linha `    rankingRotulo: rankingRotulo` sem vírgula por esse bloco).

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test tests/*.test.js`
Expected: PASS em `pendencias-texto` e `pendencias-regras`, 0 falhas.

- [ ] **Step 5: Commit**

```bash
git add assets/pendencias.js tests/pendencias-regras.test.js
git commit -m "feat(pendencias): regras de pendência, badge de AC e checklist

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Filtros, KPIs, ordenação e fixture

**Files:**
- Create: `tests/fixtures/vendas.json`
- Modify: `assets/pendencias.js` (bloco `/* ---------- filtros ---------- */` e o objeto `api`)
- Test: `tests/pendencias-filtros.test.js`

**Interfaces:**
- Consumes: `normalizar`, `parseData`, `inicioDoDia`, `diasEntre`, `isoParaData`, `rankingChave`, `formatarEquipe` (Task 1); `derivarPendencias` (Task 2).
- Produces:
  - `filtrosPadrao() → Filtros`, em que `Filtros = { busca:'', empreendimento:'', equipe:'', fases:string[], periodo:'todo'|'mes'|'mes_passado'|'30d'|'intervalo', de:'aaaa-mm-dd'|'', ate:'aaaa-mm-dd'|'', ranking:''|'diamante'|'ouro'|'prata'|'bronze'|'aco', tipo:'todas'|'comercial'|'facilitada', pendencia:'todas'|'ac'|'fid'|'ato'|'pcv', mostrarCanceladas:boolean }`. `fases: []` significa "sem filtro de fase".
  - `passaFiltros(venda, filtros, hoje, ignorarPendencia) → boolean`
  - `aplicarFiltros(vendas, filtros, hoje) → venda[]` (mantém a ordem de entrada)
  - `calcularKpis(vendas, filtros, hoje) → { total, ac, acReprovadas, acOutras, fid, fidPct, ato, pcv, vgv, base, canceladasOcultas }`
  - `ordenar(vendas, 'antigas'|'recentes'|'valor'|'pendencias') → venda[]` (nova lista; canceladas por último; empate pela ordem de entrada)
  - `opcoesDeFiltro(vendas) → { empreendimentos:string[], equipes:Array<{valor, rotulo}>, fases:string[] }`
  - `mesmasFases(a, b) → boolean`, `contarFiltrosAtivos(filtros) → int`

- [ ] **Step 1: Criar a fixture (dados fictícios)**

Crie `tests/fixtures/vendas.json`. Esse arquivo também é o dado do modo demonstração (Task 6).

```json
[
  { "id": "OP-000001", "cliente": "MARIANA ALVES PEREIRA", "dataVenda": "09/09/2026", "fase": "Proposta Aprovada", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE LEONARDO DONIZETE", "empreendimento": "Village Gaia", "identificador": "BL02-0104", "vendaFacilitada": false, "fid": "", "pcvAssinadoEm": "10/09/2026 17:22", "boletoPago": false, "cartaoPago": false, "valorReal": 214900, "ranking": "Ouro🥇", "justificativa": "PENDENTE HOLERITE MÊS 08/2026\nPENDENTE CERTIDÃO DE CASAMENTO\nPENDENTE COMPROVANTE DE ENDEREÇO", "statusAC": "Análise reprovada", "observacao": "Cliente com Bacen, verificar se segue como venda facilitada", "retorno": "Falta baixa Bacen, rever em 30/09", "cancelada": false },
  { "id": "OP-000002", "cliente": "RAFAEL SOUZA NOGUEIRA", "dataVenda": "10/09/2026", "fase": "Proposta Aprovada", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE DEBORA PIMENTA", "empreendimento": "Direcional Conquista Clube Ipiranga", "identificador": "BL03-0302", "vendaFacilitada": false, "fid": "", "pcvAssinadoEm": "11/09/2026", "boletoPago": true, "cartaoPago": false, "valorReal": 236900, "ranking": "Prata🥈", "justificativa": "Extratos anexados não embasam a renda extra declarada", "statusAC": "Análise reprovada", "observacao": "Resolvendo embasamento de renda", "retorno": "", "cancelada": false },
  { "id": "OP-000003", "cliente": "CAMILA RODRIGUES DUARTE", "dataVenda": "11/09/2026", "fase": "Aprovado Pró Soluto", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE OTAVIO YUDI", "empreendimento": "Reserva Direcional Jardim Botânico", "identificador": "BL01-0801", "vendaFacilitada": true, "fid": "", "pcvAssinadoEm": "", "boletoPago": false, "cartaoPago": true, "valorReal": 301900, "ranking": "Diamante💎", "justificativa": ".", "statusAC": "Análise aprovada", "observacao": "", "retorno": "", "cancelada": false },
  { "id": "OP-000004", "cliente": "BRUNO HENRIQUE MATOS", "dataVenda": "12/09/2026", "fase": "Proposta Aprovada", "imobiliaria": "SPI - CANAL IMOB PJ – CAROLINA CRISTINA", "empreendimento": "Village Park", "identificador": "BL05-0203", "vendaFacilitada": false, "fid": "", "pcvAssinadoEm": "12/09/2026", "boletoPago": false, "cartaoPago": false, "valorReal": 195900, "ranking": "Bronze🥉", "justificativa": "", "statusAC": "", "observacao": "", "retorno": "", "cancelada": false },
  { "id": "OP-000005", "cliente": "LETÍCIA FERNANDES ROCHA", "dataVenda": "15/09/2026", "fase": "Aprovado SAFI", "imobiliaria": "DIRECIONAL VENDAS SPI - EQUIPE SABRINA DA SILVA - Inativo", "empreendimento": "Village Gaia", "identificador": "BL01-0309", "vendaFacilitada": false, "fid": "", "pcvAssinadoEm": "16/09/2026", "boletoPago": true, "cartaoPago": true, "valorReal": 217990, "ranking": "Aço🔘", "justificativa": "Consta restrição externa", "statusAC": "Análise reprovada", "observacao": "", "retorno": "Resolve FID segunda-feira 29/09", "cancelada": false },
  { "id": "OP-000006", "cliente": "GUSTAVO LIMA TEIXEIRA", "dataVenda": "17/09/2026", "fase": "Análise SAFI", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE LEONARDO DONIZETE", "empreendimento": "Direcional Conquista Clube Ipiranga", "identificador": "BL04-1102", "vendaFacilitada": true, "fid": "", "pcvAssinadoEm": "18/09/2026", "boletoPago": true, "cartaoPago": false, "valorReal": 234900, "ranking": "Ouro🥇", "justificativa": "", "statusAC": "Enviado para análise", "observacao": "", "retorno": "", "cancelada": false },
  { "id": "OP-000007", "cliente": "ANA BEATRIZ MONTEIRO", "dataVenda": "19/09/2026", "fase": "Proposta Aprovada", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE OTAVIO YUDI", "empreendimento": "Direcional Conquista Clube Ipiranga", "identificador": "BL02-0605", "vendaFacilitada": false, "fid": "", "pcvAssinadoEm": "", "boletoPago": false, "cartaoPago": false, "valorReal": null, "ranking": "Ouro🥇", "justificativa": "Proponente não obteve o rating mínimo exigido", "statusAC": "Análise reprovada", "observacao": "", "retorno": "", "cancelada": false },
  { "id": "OP-000008", "cliente": "PEDRO HENRIQUE CARVALHO", "dataVenda": "22/09/2026", "fase": "Proposta Aprovada", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE DEBORA PIMENTA", "empreendimento": "Village Gaia", "identificador": "BL03-0710", "vendaFacilitada": false, "fid": "", "pcvAssinadoEm": "23/09/2026", "boletoPago": false, "cartaoPago": true, "valorReal": 186900, "ranking": "Prata🥈", "justificativa": "Margem financeira comprometida", "statusAC": "Análise reprovada", "observacao": "Pagou R$ 1.000 dos R$ 1.500 do ato", "retorno": "", "cancelada": true },
  { "id": "OP-000009", "cliente": "JULIANA MARTINS SILVA", "dataVenda": "24/09/2026", "fase": "Proposta Aprovada", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE GIAN TURIONI", "empreendimento": "Reserva Direcional Jardim Botânico", "identificador": "BL02-0402", "vendaFacilitada": false, "fid": "", "pcvAssinadoEm": "25/09/2026", "boletoPago": false, "cartaoPago": false, "valorReal": 439900, "ranking": "Diamante💎", "justificativa": "Pendente IRPF 2026", "statusAC": "Análise reprovada", "observacao": "", "retorno": "", "cancelada": false },
  { "id": "OP-000010", "cliente": "JOÃO VITOR RAMOS", "dataVenda": "26/09/2026", "fase": "Proposta Aprovada", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE LEONARDO DONIZETE", "empreendimento": "Direcional Conquista Clube Ipiranga", "identificador": "BL01-0205", "vendaFacilitada": false, "fid": "", "pcvAssinadoEm": "26/09/2026", "boletoPago": false, "cartaoPago": false, "valorReal": 229900, "ranking": "Ouro🥇", "justificativa": "", "statusAC": "Análise aprovada", "observacao": "", "retorno": "", "cancelada": false },
  { "id": "OP-000011", "cliente": "CARLA DOS SANTOS E SILVA", "dataVenda": "30/08/2026", "fase": "Fechado e ganho", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE DEBORA PIMENTA", "empreendimento": "Village Park", "identificador": "BL02-0101", "vendaFacilitada": false, "fid": "712345", "pcvAssinadoEm": "31/08/2026", "boletoPago": true, "cartaoPago": true, "valorReal": 199900, "ranking": "Ouro🥇", "justificativa": "", "statusAC": "Análise aprovada", "observacao": "", "retorno": "", "cancelada": false },
  { "id": "OP-000012", "cliente": "MARCOS PAULO LIMA", "dataVenda": "05/08/2026", "fase": "Fechado e ganho", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE OTAVIO YUDI", "empreendimento": "Direcional Conquista Clube Ipiranga", "identificador": "BL03-0909", "vendaFacilitada": false, "fid": "700001", "pcvAssinadoEm": "06/08/2026", "boletoPago": true, "cartaoPago": false, "valorReal": 250000, "ranking": "Prata🥈", "justificativa": "", "statusAC": "Análise aprovada", "observacao": "", "retorno": "", "cancelada": true },
  { "id": "OP-000013", "cliente": "FERNANDA COSTA", "dataVenda": "28/08/2026", "fase": "Proposta Aprovada", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE GIAN TURIONI", "empreendimento": "Village Gaia", "identificador": "BL04-0203", "vendaFacilitada": false, "fid": "715000", "pcvAssinadoEm": "29/08/2026", "boletoPago": true, "cartaoPago": true, "valorReal": 210000, "ranking": "Bronze🥉", "justificativa": "", "statusAC": "Rascunho", "observacao": "", "retorno": "", "cancelada": false },
  { "id": "OP-000014", "cliente": "ROBERTO ALMEIDA", "dataVenda": "20/09/2026", "fase": "Proposta Aprovada", "imobiliaria": "DIRECIONAL VENDAS SPI – EQUIPE LEONARDO DONIZETE", "empreendimento": "Conquista Araraquara", "identificador": "BL01-0101", "vendaFacilitada": false, "fid": "", "pcvAssinadoEm": "21/09/2026", "boletoPago": true, "cartaoPago": false, "valorReal": 180000, "ranking": "Ouro🥇", "justificativa": "", "statusAC": "Análise aprovada", "observacao": "", "retorno": "", "cancelada": true },
  { "id": "OP-000015", "cliente": "SIMONE RIBEIRO", "dataVenda": "", "fase": "Proposta Aprovada", "imobiliaria": "SPI - CANAL IMOB PJ – CAROLINA CRISTINA", "empreendimento": "Village Park", "identificador": "BL03-0808", "vendaFacilitada": false, "fid": "", "pcvAssinadoEm": "", "boletoPago": false, "cartaoPago": false, "valorReal": 190000, "ranking": "", "justificativa": "", "statusAC": "Análise aprovada", "observacao": "", "retorno": "", "cancelada": false }
]
```

- [ ] **Step 2: Escrever os testes que falham**

Crie `tests/pendencias-filtros.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const P = require('../assets/pendencias.js');
const vendas = require('./fixtures/vendas.json');

const HOJE = new Date(2026, 8, 28, 10, 0);
const f = (extra) => Object.assign(P.filtrosPadrao(), extra);
const op = (...ns) => ns.map((n) => 'OP-' + String(n).padStart(6, '0'));
const ids = (lista) => lista.map((v) => v.id);
const filtrar = (extra) => ids(P.aplicarFiltros(vendas, f(extra), HOJE));

test('filtrosPadrao', () => {
  assert.deepEqual(P.filtrosPadrao(), {
    busca: '', empreendimento: '', equipe: '', fases: P.FASES_PADRAO.slice(),
    periodo: 'todo', de: '', ate: '', ranking: '', tipo: 'todas', pendencia: 'todas', mostrarCanceladas: false
  });
  assert.notEqual(P.filtrosPadrao().fases, P.filtrosPadrao().fases, 'cada chamada devolve uma lista nova');
});

test('universo padrão: 4 fases, sem canceladas, na ordem de entrada', () => {
  assert.deepEqual(filtrar(), op(1, 2, 3, 4, 5, 6, 7, 9, 10, 13, 15));
});

test('mostrar canceladas inclui as canceladas do recorte', () => {
  assert.deepEqual(filtrar({ mostrarCanceladas: true }), op(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15));
});

test('fase', () => {
  assert.equal(filtrar({ fases: [] }).length, 12, 'lista vazia = todas as fases');
  assert.deepEqual(filtrar({ fases: ['Fechado e ganho'] }), op(11));
  assert.deepEqual(filtrar({ fases: ['aprovado pro soluto'] }), op(3), 'sem acento/caixa');
});

test('busca em cliente, OP e unidade, sem acento', () => {
  assert.deepEqual(filtrar({ busca: 'leticia' }), op(5));
  assert.deepEqual(filtrar({ busca: 'BL02-0104' }), op(1));
  assert.deepEqual(filtrar({ busca: 'op-000010' }), op(10));
});

test('empreendimento e equipe', () => {
  assert.deepEqual(filtrar({ empreendimento: 'Village Gaia' }), op(1, 5, 13));
  assert.deepEqual(filtrar({ equipe: 'DIRECIONAL VENDAS SPI – EQUIPE LEONARDO DONIZETE' }), op(1, 6, 10));
});

test('período', () => {
  assert.deepEqual(filtrar({ periodo: 'mes' }), op(1, 2, 3, 4, 5, 6, 7, 9, 10));
  assert.deepEqual(filtrar({ periodo: 'mes_passado' }), op(13));
  assert.deepEqual(filtrar({ periodo: '30d' }), op(1, 2, 3, 4, 5, 6, 7, 9, 10));
  assert.deepEqual(filtrar({ periodo: 'intervalo', de: '2026-09-15', ate: '2026-09-20' }), op(5, 6, 7));
  assert.deepEqual(filtrar({ periodo: 'intervalo', de: '2026-09-24', ate: '' }), op(9, 10));
});

test('ranking e tipo de venda', () => {
  assert.deepEqual(filtrar({ ranking: 'ouro' }), op(1, 6, 7, 10));
  assert.deepEqual(filtrar({ tipo: 'facilitada' }), op(3, 6));
  assert.equal(filtrar({ tipo: 'comercial' }).length, 9);
});

test('pendência', () => {
  assert.deepEqual(filtrar({ pendencia: 'pcv' }), op(3, 7, 15));
  assert.deepEqual(filtrar({ pendencia: 'ato' }), op(1, 4, 7, 9, 10, 15));
  assert.deepEqual(filtrar({ pendencia: 'ac' }), op(1, 2, 4, 5, 6, 7, 9, 13));
});

test('KPIs do universo padrão', () => {
  assert.deepEqual(P.calcularKpis(vendas, f(), HOJE), {
    total: 11, ac: 8, acReprovadas: 5, acOutras: 3, fid: 10, fidPct: 91,
    ato: 6, pcv: 3, vgv: 2472290, base: 11, canceladasOcultas: 2
  });
});

test('KPIs ignoram o filtro de pendência e respeitam os outros', () => {
  assert.equal(P.calcularKpis(vendas, f({ pendencia: 'pcv' }), HOJE).ac, 8);
  const gaia = P.calcularKpis(vendas, f({ empreendimento: 'Village Gaia' }), HOJE);
  assert.equal(gaia.base, 3);
  assert.equal(gaia.ac, 3);
  assert.equal(gaia.fid, 2);
  assert.equal(gaia.canceladasOcultas, 1);
});

test('ordenar', () => {
  const base = P.aplicarFiltros(vendas, f(), HOJE);
  assert.deepEqual(ids(P.ordenar(base, 'antigas')), op(13, 1, 2, 3, 4, 5, 6, 7, 9, 10, 15));
  assert.deepEqual(ids(P.ordenar(base, 'recentes')), op(10, 9, 7, 6, 5, 4, 3, 2, 1, 13, 15));
  assert.deepEqual(ids(P.ordenar(base, 'valor')), op(9, 3, 2, 6, 10, 5, 1, 13, 4, 15, 7));
  assert.deepEqual(ids(P.ordenar(base, 'pendencias')), op(7, 1, 4, 9, 15, 2, 3, 5, 6, 10, 13));
});

test('ordenar põe canceladas por último e não altera a entrada', () => {
  const comCanceladas = P.aplicarFiltros(vendas, f({ mostrarCanceladas: true }), HOJE);
  const antes = ids(comCanceladas);
  assert.deepEqual(ids(P.ordenar(comCanceladas, 'antigas')).slice(-2), op(14, 8));
  assert.deepEqual(ids(comCanceladas), antes);
});

test('opcoesDeFiltro', () => {
  const o = P.opcoesDeFiltro(vendas);
  assert.deepEqual(o.empreendimentos, ['Conquista Araraquara', 'Direcional Conquista Clube Ipiranga', 'Reserva Direcional Jardim Botânico', 'Village Gaia', 'Village Park']);
  assert.deepEqual(o.fases, ['Análise SAFI', 'Aprovado Pró Soluto', 'Aprovado SAFI', 'Fechado e ganho', 'Proposta Aprovada']);
  assert.deepEqual(o.equipes.map((e) => e.rotulo), [
    'Canal PJ · Carolina Cristina', 'Equipe Debora Pimenta', 'Equipe Gian Turioni',
    'Equipe Leonardo Donizete', 'Equipe Otavio Yudi', 'Equipe Sabrina da Silva - Inativo'
  ]);
  assert.equal(o.equipes[0].valor, 'SPI - CANAL IMOB PJ – CAROLINA CRISTINA');
});

test('mesmasFases e contarFiltrosAtivos', () => {
  assert.ok(P.mesmasFases(['proposta aprovada', 'Aprovado SAFI', 'Análise SAFI', 'Aprovado Pró Soluto'], P.FASES_PADRAO));
  assert.ok(!P.mesmasFases([], P.FASES_PADRAO));
  assert.equal(P.contarFiltrosAtivos(f()), 0);
  assert.equal(P.contarFiltrosAtivos(f({ empreendimento: 'x', periodo: 'mes', fases: [] })), 3);
  assert.equal(P.contarFiltrosAtivos(f({ busca: 'abc', pendencia: 'ac' })), 0, 'busca e pendência não contam');
});
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `node --test tests/pendencias-filtros.test.js`
Expected: FAIL com `TypeError: P.filtrosPadrao is not a function`

- [ ] **Step 4: Implementar**

Em `assets/pendencias.js`, troque a linha `  /* ---------- filtros ---------- */` por:

```js
  /* ---------- filtros ---------- */
  function filtrosPadrao() {
    return {
      busca: '', empreendimento: '', equipe: '', fases: FASES_PADRAO.slice(),
      periodo: 'todo', de: '', ate: '', ranking: '', tipo: 'todas',
      pendencia: 'todas', mostrarCanceladas: false
    };
  }

  function dentroDoPeriodo(venda, f, hoje) {
    if (!f.periodo || f.periodo === 'todo') return true;
    var d = parseData(venda.dataVenda);
    if (!d) return false;
    var h = inicioDoDia(hoje);
    if (f.periodo === 'mes') return d.getFullYear() === h.getFullYear() && d.getMonth() === h.getMonth();
    if (f.periodo === 'mes_passado') {
      var p = new Date(h.getFullYear(), h.getMonth() - 1, 1);
      return d.getFullYear() === p.getFullYear() && d.getMonth() === p.getMonth();
    }
    if (f.periodo === '30d') { var n = diasEntre(d, h); return n >= 0 && n <= 30; }
    if (f.periodo === 'intervalo') {
      var de = isoParaData(f.de), ate = isoParaData(f.ate), dia = inicioDoDia(d);
      return (!de || dia >= de) && (!ate || dia <= ate);
    }
    return true;
  }

  function passaFiltros(venda, f, hoje, ignorarPendencia) {
    if (venda.cancelada && !f.mostrarCanceladas) return false;
    if (f.busca) {
      var alvo = normalizar([venda.cliente, venda.id, venda.identificador].join(' '));
      if (alvo.indexOf(normalizar(f.busca)) === -1) return false;
    }
    if (f.empreendimento && String(venda.empreendimento || '').trim() !== f.empreendimento) return false;
    if (f.equipe && String(venda.imobiliaria || '').trim() !== f.equipe) return false;
    if (f.fases && f.fases.length && f.fases.map(normalizar).indexOf(normalizar(venda.fase)) === -1) return false;
    if (!dentroDoPeriodo(venda, f, hoje)) return false;
    if (f.ranking && rankingChave(venda.ranking) !== f.ranking) return false;
    if (f.tipo === 'comercial' && venda.vendaFacilitada) return false;
    if (f.tipo === 'facilitada' && !venda.vendaFacilitada) return false;
    if (!ignorarPendencia && f.pendencia && f.pendencia !== 'todas') {
      var tem = derivarPendencias(venda).some(function (p) { return p.chave === f.pendencia; });
      if (!tem) return false;
    }
    return true;
  }

  function aplicarFiltros(vendas, f, hoje) {
    return vendas.filter(function (v) { return passaFiltros(v, f, hoje, false); });
  }

  /* KPIs: todos os filtros menos o de pendencia, sem canceladas (spec 5.5) */
  function calcularKpis(vendas, f, hoje) {
    var comCanceladas = Object.assign({}, f, { mostrarCanceladas: true });
    var k = { total: 0, ac: 0, acReprovadas: 0, acOutras: 0, fid: 0, fidPct: 0, ato: 0, pcv: 0, vgv: 0, base: 0, canceladasOcultas: 0 };
    vendas.forEach(function (v) {
      if (!passaFiltros(v, comCanceladas, hoje, true)) return;
      if (v.cancelada) { k.canceladasOcultas++; return; }
      k.base++;
      var chaves = derivarPendencias(v).map(function (p) { return p.chave; });
      if (chaves.length) k.total++;
      if (chaves.indexOf('ac') !== -1) {
        k.ac++;
        if (normalizar(v.statusAC) === 'analise reprovada') k.acReprovadas++; else k.acOutras++;
      }
      if (chaves.indexOf('fid') !== -1) k.fid++;
      if (chaves.indexOf('ato') !== -1) k.ato++;
      if (chaves.indexOf('pcv') !== -1) k.pcv++;
      if (typeof v.valorReal === 'number') k.vgv += v.valorReal;
    });
    k.fidPct = k.base ? Math.round(k.fid / k.base * 100) : 0;
    return k;
  }

  function tempoDaVenda(v) { var d = parseData(v.dataVenda); return d ? d.getTime() : null; }
  /* nulos sempre por ultimo, nos dois sentidos */
  function compararNulosPorUltimo(a, b, crescente) {
    if (a === null && b === null) return 0;
    if (a === null) return 1;
    if (b === null) return -1;
    return crescente ? a - b : b - a;
  }
  function comparar(a, b, criterio) {
    if (criterio === 'recentes') return compararNulosPorUltimo(tempoDaVenda(a), tempoDaVenda(b), false);
    if (criterio === 'valor') {
      var va = typeof a.valorReal === 'number' ? a.valorReal : null;
      var vb = typeof b.valorReal === 'number' ? b.valorReal : null;
      return compararNulosPorUltimo(va, vb, false);
    }
    if (criterio === 'pendencias') return derivarPendencias(b).length - derivarPendencias(a).length;
    return compararNulosPorUltimo(tempoDaVenda(a), tempoDaVenda(b), true);
  }
  function ordenar(vendas, criterio) {
    return vendas.map(function (v, i) { return { v: v, i: i }; })
      .sort(function (a, b) {
        if (!!a.v.cancelada !== !!b.v.cancelada) return a.v.cancelada ? 1 : -1;
        return comparar(a.v, b.v, criterio) || a.i - b.i;
      })
      .map(function (x) { return x.v; });
  }

  function unicos(lista) {
    var vistos = {};
    return lista.filter(function (x) { if (!x || vistos[x]) return false; vistos[x] = 1; return true; });
  }
  function porTexto(a, b) { return a.localeCompare(b, 'pt-BR'); }
  function opcoesDeFiltro(vendas) {
    function campo(nome) { return vendas.map(function (v) { return String(v[nome] || '').trim(); }); }
    return {
      empreendimentos: unicos(campo('empreendimento')).sort(porTexto),
      equipes: unicos(campo('imobiliaria'))
        .map(function (valor) { return { valor: valor, rotulo: formatarEquipe(valor) }; })
        .sort(function (a, b) { return porTexto(a.rotulo, b.rotulo); }),
      fases: unicos(campo('fase')).sort(porTexto)
    };
  }

  function mesmasFases(a, b) {
    function chave(l) { return l.map(normalizar).sort().join('|'); }
    return chave(a || []) === chave(b || []);
  }
  /* quantos filtros "de gaveta" estao fora do padrao (botao Filtros no celular) */
  function contarFiltrosAtivos(f) {
    var n = 0;
    if (f.empreendimento) n++;
    if (f.equipe) n++;
    if (!mesmasFases(f.fases, FASES_PADRAO)) n++;
    if (f.periodo && f.periodo !== 'todo') n++;
    if (f.ranking) n++;
    if (f.tipo && f.tipo !== 'todas') n++;
    if (f.mostrarCanceladas) n++;
    return n;
  }
```

No objeto `api`, troque `    checklist: checklist` por:

```js
    checklist: checklist,
    filtrosPadrao: filtrosPadrao,
    passaFiltros: passaFiltros,
    aplicarFiltros: aplicarFiltros,
    calcularKpis: calcularKpis,
    ordenar: ordenar,
    opcoesDeFiltro: opcoesDeFiltro,
    mesmasFases: mesmasFases,
    contarFiltrosAtivos: contarFiltrosAtivos
```

- [ ] **Step 5: Rodar e ver passar**

Run: `node --test tests/*.test.js`
Expected: PASS nos 3 arquivos, 0 falhas.

- [ ] **Step 6: Commit**

```bash
git add assets/pendencias.js tests/pendencias-filtros.test.js tests/fixtures/vendas.json
git commit -m "feat(pendencias): filtros, KPIs, ordenação e fixture fictícia

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Web App do Apps Script

**Files:**
- Create: `docs/apps-script-pendencias.gs`

**Interfaces:**
- Consumes: as funções globais do script que já existe no projeto da planilha: `atualizarRelatorioSalesforce()`.
- Produces: contrato HTTP usado pela Task 6.
  - `POST` com corpo `text/plain` contendo JSON `{ senha, acao, id?, observacao?, retorno? }`.
  - Sucesso: `{ ok:true, vendas, salesforceAtualizadoEm }` (listar/atualizar) ou `{ ok:true, venda }` (cancelar/reativar/editar).
  - Falha: `{ ok:false, erro:'senha'|'nao_encontrada'|'ocupado'|'coluna'|'interno', mensagem }`.
  - Cada `venda` tem exatamente os campos do formato da Task 2.

Não há teste automatizado de Apps Script neste repo. A verificação é sintática aqui e funcional na Task 10 (`testePendencias()` no editor do Apps Script).

- [ ] **Step 1: Escrever o Web App**

Crie `docs/apps-script-pendencias.gs`:

```js
/* ============================================================
   PENDENCIAS DE VENDAS - Google Apps Script Web App
   ------------------------------------------------------------
   Backend da pagina /pendencias-vendas do Portal do Corretor.
   Le a aba RELATORIO e grava Observacao/Retorno e o cancelamento
   (fonte vermelha + tachada) direto nela. A pagina NAO le o CSV
   da planilha: tudo passa por aqui, com a senha conferida no
   servidor. Spec: docs/superpowers/specs/2026-09-28-pendencias-vendas-design.md

   ---------- COMO PUBLICAR (uma vez) ----------
   1. Abra a planilha > Extensoes > Apps Script (o MESMO projeto que
      tem atualizarRelatorioSalesforce()).
   2. Arquivos > "+" > Script > nome "Pendencias" > cole este arquivo.
   3. No arquivo do relatorio, dentro de atualizarRelatorioSalesforce(),
      logo ANTES da ultima linha
        Logger.log("RELATÓRIO atualizado com sucesso usando DATABASE, DATABASE 2 e OP X AC.");
      adicione:
        PropertiesService.getScriptProperties()
          .setProperty('PENDENCIAS_ULTIMA_ATUALIZACAO', new Date().toISOString());
   4. Selecione a funcao configurarSenhaPendencias > Executar (autorize).
   5. Selecione testePendencias > Executar > confira o log.
   6. Implantar > Nova implantacao > Tipo: App da Web
        Executar como: Eu
        Quem tem acesso: Qualquer pessoa
   7. Copie a URL que termina em /exec e cole em
      window.PENDENCIAS_APPS_SCRIPT_URL (assets/config.js).

   Mudou o codigo depois? Implantar > Gerenciar implantacoes > editar >
   Nova versao (a URL /exec continua a mesma).
   Trocar a senha: edite configurarSenhaPendencias e rode de novo
   (nao precisa reimplantar nem mexer no site).
   ============================================================ */

var PEND_ABA = 'RELATÓRIO';
var PEND_LINHA_CABECALHO = 3;
var PEND_PROP_SENHA = 'PENDENCIAS_SENHA';
var PEND_PROP_ATUALIZACAO = 'PENDENCIAS_ULTIMA_ATUALIZACAO';
var PEND_VERMELHOS = ['#ff0000', '#f00', 'red', '#cc0000', '#990000', '#b00000'];
var PEND_OBRIGATORIAS = ['ID', 'Observação', 'Retorno'];
var PEND_MAX_TEXTO = 5000;

function configurarSenhaPendencias() {
  PropertiesService.getScriptProperties().setProperty(PEND_PROP_SENHA, 'Comercial123');
  Logger.log('Senha da pagina /pendencias-vendas configurada.');
}

function PendFalha(codigo, mensagem) { this.codigo = codigo; this.message = mensagem; }

function doGet() {
  return pendJson_({ ok: false, erro: 'interno', mensagem: 'Use POST.' });
}

function doPost(e) {
  var resposta;
  try {
    var req = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    resposta = pendRoteador_(req);
  } catch (err) {
    resposta = err instanceof PendFalha
      ? { ok: false, erro: err.codigo, mensagem: err.message }
      : { ok: false, erro: 'interno', mensagem: String((err && err.message) || err) };
  }
  return pendJson_(resposta);
}

function pendJson_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function pendRoteador_(req) {
  var senha = PropertiesService.getScriptProperties().getProperty(PEND_PROP_SENHA);
  if (!senha || req.senha !== senha) throw new PendFalha('senha', 'Senha incorreta.');
  switch (req.acao) {
    case 'listar': return pendListar_();
    case 'cancelar': return pendComLock_(function () { return pendPintar_(req.id, true); });
    case 'reativar': return pendComLock_(function () { return pendPintar_(req.id, false); });
    case 'editar': return pendComLock_(function () { return pendEditar_(req.id, req.observacao, req.retorno); });
    case 'atualizar': return pendComLock_(function () { atualizarRelatorioSalesforce(); return pendListar_(); });
    default: throw new PendFalha('interno', 'Ação desconhecida: ' + req.acao);
  }
}

/* O atualizarRelatorioSalesforce() insere linhas e reordena a aba: toda
   gravacao localiza a linha pelo ID dentro do lock, logo antes de gravar. */
function pendComLock_(fn) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) throw new PendFalha('ocupado', 'Tem uma atualização em andamento, tente em instantes.');
  try { return fn(); } finally { lock.releaseLock(); }
}

function pendNormalizar_(v) {
  if (v === null || v === undefined) return '';
  return String(v).trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function pendLerAba_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var aba = ss.getSheetByName(PEND_ABA);
  if (!aba) throw new PendFalha('coluna', 'A aba "' + PEND_ABA + '" não foi encontrada.');
  var ultimaLinha = aba.getLastRow();
  var ultimaColuna = aba.getLastColumn();
  var cabecalho = aba.getRange(PEND_LINHA_CABECALHO, 1, 1, ultimaColuna).getValues()[0]
    .map(function (c) { return String(c).trim(); });
  var indice = {};
  cabecalho.forEach(function (nome, i) { if (nome && !(nome in indice)) indice[nome] = i; });
  PEND_OBRIGATORIAS.forEach(function (nome) {
    if (!(nome in indice)) throw new PendFalha('coluna', 'Coluna "' + nome + '" não encontrada no ' + PEND_ABA + '.');
  });
  /* colunas de dados = todas menos as auxiliares "__ORDEM_..." do script */
  var colunasDados = [];
  cabecalho.forEach(function (nome, i) { if (nome.indexOf('__') !== 0) colunasDados.push(i); });
  var n = Math.max(ultimaLinha - PEND_LINHA_CABECALHO, 0);
  var faixa = n ? aba.getRange(PEND_LINHA_CABECALHO + 1, 1, n, ultimaColuna) : null;
  return {
    aba: aba,
    fuso: ss.getSpreadsheetTimeZone(),
    indice: indice,
    colunasDados: colunasDados,
    ultimaColunaDados: colunasDados.length ? colunasDados[colunasDados.length - 1] + 1 : ultimaColuna,
    n: n,
    valores: faixa ? faixa.getValues() : [],
    exibidos: faixa ? faixa.getDisplayValues() : [],
    cores: faixa ? faixa.getFontColors() : [],
    linhasFonte: faixa ? faixa.getFontLines() : []
  };
}

function pendNumero_(bruto, exibido) {
  if (typeof bruto === 'number') return bruto;
  var s = String(exibido || bruto || '').replace(/[^\d,.-]/g, '');
  if (!s) return null;
  var n = Number(s.replace(/\./g, '').replace(',', '.'));
  return isNaN(n) ? null : n;
}

function pendVendaDaLinha_(t, i) {
  var bruto = t.valores[i];
  var exibido = t.exibidos[i];
  function col(nome) { return nome in t.indice ? t.indice[nome] : -1; }
  function texto(nome) { var c = col(nome); return c < 0 ? '' : String(exibido[c]).trim(); }
  function data(nome) {
    var c = col(nome);
    if (c < 0) return '';
    var v = bruto[c];
    if (Object.prototype.toString.call(v) === '[object Date]' && !isNaN(v)) {
      var comHora = v.getHours() || v.getMinutes();
      return Utilities.formatDate(v, t.fuso, comHora ? 'dd/MM/yyyy HH:mm' : 'dd/MM/yyyy');
    }
    return String(exibido[c]).trim();
  }
  function sim(nome) {
    var c = col(nome);
    if (c < 0) return false;
    if (bruto[c] === true) return true;
    var s = pendNormalizar_(exibido[c]);
    return s === 'sim' || s === 'verdadeiro' || s === 'true';
  }
  var cancelada = false;
  for (var k = 0; k < t.colunasDados.length && !cancelada; k++) {
    var j = t.colunasDados[k];
    var cor = String(t.cores[i][j] || '').toLowerCase();
    var linha = String(t.linhasFonte[i][j] || '').toLowerCase();
    if (PEND_VERMELHOS.indexOf(cor) !== -1 || linha === 'line-through') cancelada = true;
  }
  var cValor = col('Valor Real de Venda');
  return {
    id: texto('ID'),
    cliente: texto('Cliente'),
    dataVenda: data('Data da venda'),
    fase: texto('Fase'),
    imobiliaria: texto('Imobiliária'),
    empreendimento: texto('Empreendimento'),
    identificador: texto('Identificador'),
    vendaFacilitada: sim('Venda facilitada'),
    fid: texto('FID'),
    pcvAssinadoEm: data('Cliente assinou PCV'),
    boletoPago: sim('Boleto/PIX Pago'),
    cartaoPago: sim('Cartão Pago'),
    valorReal: cValor < 0 ? null : pendNumero_(bruto[cValor], exibido[cValor]),
    ranking: texto('Ranking'),
    justificativa: texto('Justificativa'),
    statusAC: texto('Status AC'),
    observacao: texto('Observação'),
    retorno: texto('Retorno'),
    cancelada: cancelada
  };
}

function pendListar_() {
  var t = pendLerAba_();
  var cId = t.indice['ID'];
  var vendas = [];
  for (var i = 0; i < t.n; i++) {
    if (!String(t.exibidos[i][cId]).trim()) continue;
    vendas.push(pendVendaDaLinha_(t, i));
  }
  return {
    ok: true,
    vendas: vendas,
    salesforceAtualizadoEm: PropertiesService.getScriptProperties().getProperty(PEND_PROP_ATUALIZACAO) || null
  };
}

function pendAcharLinha_(t, id) {
  var alvo = String(id || '').trim();
  var cId = t.indice['ID'];
  if (alvo) {
    for (var i = 0; i < t.n; i++) if (String(t.exibidos[i][cId]).trim() === alvo) return i;
  }
  throw new PendFalha('nao_encontrada', 'Essa venda não está mais no relatório.');
}

function pendPintar_(id, cancelar) {
  var t = pendLerAba_();
  var i = pendAcharLinha_(t, id);
  var linha = PEND_LINHA_CABECALHO + 1 + i;
  t.aba.getRange(linha, 1, 1, t.ultimaColunaDados)
    .setFontColor(cancelar ? '#ff0000' : '#000000')
    .setFontLine(cancelar ? 'line-through' : 'none');
  if ('__ORDEM_CANCELADA' in t.indice) {
    t.aba.getRange(linha, t.indice['__ORDEM_CANCELADA'] + 1).setValue(cancelar ? 1 : 0);
  }
  var venda = pendVendaDaLinha_(t, i);
  venda.cancelada = cancelar;
  return { ok: true, venda: venda };
}

/* texto livre nunca vira formula na planilha */
function pendTextoSeguro_(v) {
  var s = String(v === null || v === undefined ? '' : v).slice(0, PEND_MAX_TEXTO);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

function pendEditar_(id, observacao, retorno) {
  var t = pendLerAba_();
  var i = pendAcharLinha_(t, id);
  var linha = PEND_LINHA_CABECALHO + 1 + i;
  var obs = pendTextoSeguro_(observacao);
  var ret = pendTextoSeguro_(retorno);
  t.aba.getRange(linha, t.indice['Observação'] + 1).setValue(obs);
  t.aba.getRange(linha, t.indice['Retorno'] + 1).setValue(ret);
  var venda = pendVendaDaLinha_(t, i);
  venda.observacao = String(observacao || '').slice(0, PEND_MAX_TEXTO).trim();
  venda.retorno = String(retorno || '').slice(0, PEND_MAX_TEXTO).trim();
  return { ok: true, venda: venda };
}

/* Rode no editor antes de implantar: confere colunas e contagens. */
function testePendencias() {
  var r = pendListar_();
  var porFase = {};
  var canceladas = 0;
  r.vendas.forEach(function (v) {
    porFase[v.fase] = (porFase[v.fase] || 0) + 1;
    if (v.cancelada) canceladas++;
  });
  Logger.log('Vendas: %s | canceladas: %s', r.vendas.length, canceladas);
  Logger.log('Por fase: %s', JSON.stringify(porFase));
  Logger.log('Colunas encontradas: %s', JSON.stringify(Object.keys(pendLerAba_().indice)));
  Logger.log('Salesforce atualizado em: %s', r.salesforceAtualizadoEm);
  Logger.log('Exemplo: %s', JSON.stringify(r.vendas[0]));
}
```

- [ ] **Step 2: Conferir a sintaxe**

Run: `node --check docs/apps-script-pendencias.gs && echo OK`
Expected: `OK` (sem `SyntaxError`).

- [ ] **Step 3: Conferir que os nomes de campo batem com a fixture**

Run:
```bash
node -e "
const src = require('fs').readFileSync('docs/apps-script-pendencias.gs','utf8');
const bloco = src.slice(src.indexOf('return {\n    id: texto'), src.indexOf('cancelada: cancelada') + 20);
const doGs = [...bloco.matchAll(/^\s{4}(\w+):/gm)].map(m => m[1]).sort();
const daFixture = Object.keys(require('./tests/fixtures/vendas.json')[0]).sort();
console.log(JSON.stringify(doGs) === JSON.stringify(daFixture) ? 'CAMPOS OK' : 'DIFERENTE\n' + doGs + '\n' + daFixture);
"
```
Expected: `CAMPOS OK`

- [ ] **Step 4: Commit**

```bash
git add docs/apps-script-pendencias.gs
git commit -m "feat(pendencias): Web App do Apps Script (listar, cancelar, editar, atualizar)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Estrutura da página, estilos e configuração

**Files:**
- Modify: `assets/config.js` (acrescentar no fim)
- Create: `pendencias-vendas.html`

**Interfaces:**
- Consumes: `assets/img/logo-direcional-header.png`, `assets/img/hero-bg.png`, `assets/img/favicon.webp` (já existem).
- Produces: os IDs de DOM usados pelas Tasks 6 a 8 (todos definidos no markup abaixo):
  - senha: `gate`, `gate-form`, `gate-senha`, `gate-olho`, `gate-erro`, `gate-erro-txt`, `gate-entrar`, `gate-demo`
  - app: `app`, `hdr-dot`, `hdr-atualizacao`, `btn-atualizar`, `btn-atualizar-txt`, `btn-sair`, `aviso-demo`, `faixa-atualizando`, `carregando`, `erro-lista`, `erro-lista-txt`, `erro-lista-tentar`, `conteudo-lista`
  - KPIs: `kpi-total`, `kpi-total-sub`, `kpi-ac`, `kpi-ac-sub`, `kpi-fid`, `kpi-fid-sub`, `kpi-ato`, `kpi-pcv`, `kpi-vgv`
  - filtros: `filtros-topo`, `f-busca`, `filtros-grid`, `f-emp`, `f-eq`, `f-fase`, `f-fase-resumo`, `f-fase-resumo-txt`, `f-fase-lista`, `f-per`, `f-rank`, `f-tipo`, `intervalo`, `f-de`, `f-ate`, `btn-filtros`, `btn-filtros-txt`, `filtros-pend`, `chip-n-todas|ac|fid|ato|pcv`, `filtros-extra`, `f-canceladas`, `canceladas-n`, `limpar-filtros`
  - lista: `contagem`, `contagem-ordem`, `f-ord`, `lista`, `tabela-corpo`, `cartoes`, `vazio`, `vazio-limpar`
  - painel: `painel`, `dt-op`, `dt-copiar`, `dt-fechar`, `dt-nome`, `dt-sub`, `dt-tags`, `dt-data`, `dt-dias-cel`, `dt-dias`, `dt-valor`, `dt-fid`, `dt-faltam`, `dt-checklist`, `dt-just`, `dt-obs`, `dt-ret`, `dt-cancelar`, `dt-cancelar-txt`, `dt-descartar`, `dt-salvar`
  - cancelar: `dlg-cancelar`, `cx-nome`, `cx-meta`, `cx-valor`, `cx-voltar`, `cx-confirmar`
  - folha mobile: `folha-filtros`, `folha-fechar`, `folha-corpo`, `folha-aplicar`
  - toast: `toast`
  - atributo `data-pendencia="todas|ac|fid|ato|pcv"` nos KPIs e nos chips
- Classes CSS que o JS aplica: `chip c-err|c-warn|c-ok|c-neu`, `chip-p`, `chips`, `nome`, `meta`, `nota`, `ell`, `dias`, `alerta`, `sub`, `num`, `valor`, `equipe`, `abrir`, `cancelada`, `vc`, `vc-topo`, `vc-id`, `vc-nota`, `vc-rodape`, `ck`, `ok`, `ck-t`, `ci ci-ok|ci-err|ci-warn`, `on`, `ativo`, `multi-op`, `btn btn-i btn-fantasma`, `toast erro visivel`, `toast-acao`, `gira`.

- [ ] **Step 1: Configuração**

Acrescente no **fim** de `assets/config.js`:

```js

/* ---------- Pendencias de Vendas (/pendencias-vendas) ----------
   URL .../exec do Web App do Apps Script da planilha de vendas
   (docs/apps-script-pendencias.gs). A SENHA NAO FICA AQUI: fica so no
   Apps Script (Script Property PENDENCIAS_SENHA).
   Vazio = modo demonstracao (dados ficticios de tests/fixtures/vendas.json,
   nada e gravado). Com URL preenchida, ?demo=1 na pagina forca o modo demo. */
window.PENDENCIAS_APPS_SCRIPT_URL = '';
```

- [ ] **Step 2: Criar a página**

Crie `pendencias-vendas.html`:

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Pendências de Vendas · Comercial</title>
<link rel="icon" type="image/webp" href="assets/img/favicon.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&display=swap" rel="stylesheet">
<!-- Pagina interna do comercial. Spec: docs/superpowers/specs/2026-09-28-pendencias-vendas-design.md
     Telas: docs/design/pendencias-vendas/telas/ -->
<style>
:root{
  --red:#E4032B;--red-deep:#B8001F;--ink:#3A4043;--slate:#727A7D;--slate-2:#5E666A;
  --hair:#E7E9EA;--bg:#F5F6F7;--surface:#FFFFFF;--muted:#FAFBFB;
  --ok:#1B7A40;--ok-bg:#EFF9F2;--ok-line:#C7E7D3;
  --warn:#8A5700;--warn-bg:#FFF7E6;--warn-line:#F1DCAE;
  --err:#C4001C;--err-bg:#FDEEF0;--err-line:#F6C9D0;
  --foco:0 0 0 3px rgba(228,3,43,.10);--foco-forte:0 0 0 3px rgba(228,3,43,.25)
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:'DM Sans',system-ui,sans-serif;font-size:15px;line-height:1.5;color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased}
[hidden]{display:none!important}
button,input,select,textarea{font:inherit;color:inherit}
h1,h2,h3,p{margin:0}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.num{font-variant-numeric:tabular-nums}
.lab{font-size:11.5px;font-weight:500;letter-spacing:.05em;text-transform:uppercase;color:var(--slate)}
.sub{font-size:12.5px;color:var(--slate);line-height:1.4}
.ell{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
.alerta{color:var(--warn);font-weight:500}
.step{display:flex;align-items:center;gap:10px;font-size:12.5px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--red)}
.step::before{content:"";width:22px;height:2px;border-radius:2px;background:var(--red)}
.hero{background:var(--surface) url(assets/img/hero-bg.png) center/cover no-repeat;border-bottom:1px solid var(--hair)}
.gira{animation:gira .9s linear infinite}
@keyframes gira{to{transform:rotate(360deg)}}

/* ---------- botoes ---------- */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 17px;border-radius:9px;border:1px solid var(--hair);background:var(--surface);color:var(--ink);font-weight:500;font-size:14px;line-height:1;cursor:pointer;transition:border-color .15s,color .15s,background .15s;white-space:nowrap}
.btn:hover:not(:disabled){border-color:var(--red);color:var(--red)}
.btn:disabled{color:var(--slate);background:var(--muted);cursor:default}
.btn-p{background:var(--red);border-color:var(--red);color:#fff}
.btn-p:hover:not(:disabled){background:var(--red-deep);border-color:var(--red-deep);color:#fff}
.btn-p:disabled{background:#F2A3B1;border-color:#F2A3B1;color:#fff}
.btn-i{width:44px;padding:0}
.btn-fantasma{border-color:transparent;background:transparent}
.btn-mini{width:36px;min-height:36px;color:var(--slate)}
.btn-d{color:var(--err)}
.btn-d:hover:not(:disabled){border-color:var(--err);color:var(--err);background:var(--err-bg)}
.btn-g{width:100%;min-height:48px;font-size:15px}
.lnk{background:none;border:0;padding:0 4px;min-height:44px;font-weight:500;font-size:13.5px;color:var(--slate-2);cursor:pointer;text-decoration:underline;text-underline-offset:3px}
.lnk:hover{color:var(--red)}
.btn:focus-visible,.lnk:focus-visible,.fchip:focus-visible,.kpi:focus-visible,.vc:focus-visible,.olho:focus-visible,.toast-acao:focus-visible,.multi summary:focus-visible{outline:none;box-shadow:var(--foco-forte)}

/* ---------- chips ---------- */
.chip{display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 10px;border-radius:999px;font-size:12px;font-weight:500;border:1px solid;white-space:nowrap}
.chip-p{height:20px;padding:0 7px;font-size:11px}
.c-err{background:var(--err-bg);color:var(--err);border-color:var(--err-line)}
.c-warn{background:var(--warn-bg);color:var(--warn);border-color:var(--warn-line)}
.c-ok{background:var(--ok-bg);color:var(--ok);border-color:var(--ok-line)}
.c-neu{background:var(--surface);color:var(--slate-2);border-color:var(--hair)}
.chips{display:flex;flex-wrap:wrap;gap:6px}

/* ---------- campos ---------- */
.campo{display:flex;flex-direction:column;gap:6px;min-width:0;position:relative}
.inp{width:100%;min-height:44px;border:1px solid var(--hair);border-radius:9px;background:var(--surface);padding:0 12px;font-size:14px;color:var(--ink);outline:none;transition:border-color .15s,box-shadow .15s}
textarea.inp{padding:11px 12px;line-height:1.5;resize:vertical}
.inp:focus,.multi summary:focus{border-color:var(--red);box-shadow:var(--foco)}
.inp::placeholder{color:var(--slate)}
.inp.ativo{border-color:var(--red)}
.inp[aria-invalid="true"]{border-color:var(--err);background:var(--err-bg)}
.sel{position:relative}
.sel select{-webkit-appearance:none;appearance:none;padding-right:34px;cursor:pointer;text-overflow:ellipsis}
.sel > svg,.multi summary > svg{position:absolute;right:11px;top:50%;margin-top:-8px;pointer-events:none;color:var(--slate)}
.com-ico{position:relative}
.com-ico .inp{padding-left:40px}
.ico-esq{position:absolute;left:13px;top:50%;margin-top:-9px;color:var(--slate);pointer-events:none}
.msg-erro{display:flex;align-items:center;gap:6px;font-size:13px;font-weight:500;color:var(--err)}
.multi{position:relative}
.multi summary{list-style:none;display:flex;align-items:center;padding-right:34px;cursor:pointer;position:relative}
.multi summary::-webkit-details-marker{display:none}
.multi-lista{position:absolute;z-index:5;top:calc(100% + 6px);left:0;min-width:240px;background:var(--surface);border:1px solid var(--hair);border-radius:12px;box-shadow:0 12px 30px rgba(28,32,34,.14);padding:6px}
.multi-op{display:flex;align-items:center;gap:10px;min-height:40px;padding:0 10px;border-radius:8px;font-size:14px;cursor:pointer}
.multi-op:hover{background:var(--muted)}
.multi-op input{width:16px;height:16px;accent-color:var(--red)}
.sw{display:inline-flex;align-items:center;gap:10px;font-size:13.5px;cursor:pointer;min-height:44px;position:relative}
.sw input{position:absolute;opacity:0;width:1px;height:1px}
.sw .tr{width:38px;height:22px;border-radius:999px;background:#CDD2D4;position:relative;transition:background .15s;flex-shrink:0}
.sw .tr::after{content:"";position:absolute;top:3px;left:3px;width:16px;height:16px;border-radius:50%;background:#fff;transition:transform .15s}
.sw input:checked + .tr{background:var(--red)}
.sw input:checked + .tr::after{transform:translateX(16px)}
.sw input:focus-visible + .tr{box-shadow:var(--foco-forte)}

/* ---------- senha ---------- */
.gate{min-height:100vh;min-height:100dvh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;padding:28px 16px;border-bottom:0}
.gate-card{width:100%;max-width:440px;background:var(--surface);border:1px solid var(--hair);border-radius:18px;padding:40px 40px 36px;display:flex;flex-direction:column;gap:26px}
.gate-logo{height:36px;align-self:flex-start}
.gate-titulo{display:flex;flex-direction:column;gap:10px}
.gate-titulo h1{font-size:30px;font-weight:700;letter-spacing:-.6px;line-height:1.15}
.gate-titulo p{font-size:14.5px;line-height:1.55;color:var(--slate-2)}
.gate-form{display:flex;flex-direction:column;gap:16px}
.senha-box{position:relative}
.senha-box .inp{min-height:48px;padding:0 48px 0 42px;font-size:15px}
.senha-ico{position:absolute;left:14px;top:15px;color:var(--slate);pointer-events:none}
.olho{position:absolute;right:2px;top:2px;width:44px;height:44px;border:0;border-radius:8px;background:none;color:var(--slate);cursor:pointer;display:flex;align-items:center;justify-content:center}
.olho:hover{color:var(--red)}

/* ---------- topo ---------- */
.topo{position:relative;max-width:1440px;margin:0 auto;padding:36px 80px 30px;min-height:200px}
.topo-logo{position:absolute;top:30px;right:80px;height:42px}
.topo-textos{display:flex;flex-direction:column;gap:12px;max-width:760px}
.topo h1{font-size:38px;font-weight:700;letter-spacing:-.8px;line-height:1.1}
.topo p{font-size:15px;color:var(--slate-2);max-width:60ch}
.topo-acoes{position:absolute;right:80px;bottom:30px;display:flex;align-items:center;gap:12px}
.atualizacao{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--slate-2);padding-right:6px}
.dot{width:8px;height:8px;border-radius:50%;background:#1E8E4A;box-shadow:0 0 0 3px var(--ok-bg);flex-shrink:0}

/* ---------- conteudo ---------- */
.conteudo{max-width:1440px;margin:0 auto;padding:28px 80px 64px;display:flex;flex-direction:column;gap:20px}
#conteudo-lista{display:flex;flex-direction:column;gap:20px}
.card{background:var(--surface);border:1px solid var(--hair);border-radius:14px}
.aviso-demo{padding:12px 16px;border:1px dashed var(--warn-line);background:var(--warn-bg);color:var(--warn);border-radius:12px;font-size:13.5px}
.estado{padding:28px;display:flex;align-items:center;gap:12px;color:var(--slate-2)}
.faixa{border:1px solid var(--hair);border-radius:12px;padding:16px 18px;display:flex;flex-direction:column;gap:12px;background:var(--surface)}
.faixa-t{display:flex;align-items:center;gap:10px;font-weight:700;font-size:14.5px}
.faixa-t svg{color:var(--red)}
.barra{height:4px;border-radius:999px;background:#ECEEEF;overflow:hidden;position:relative}
.barra span{position:absolute;top:0;bottom:0;left:-40%;width:40%;background:var(--red);border-radius:999px;animation:barra 1.4s ease-in-out infinite}
@keyframes barra{to{left:100%}}
@media (prefers-reduced-motion:reduce){.gira,.barra span{animation:none}.barra span{left:0;width:100%;opacity:.35}}
.alerta-erro{display:flex;align-items:flex-start;gap:12px;padding:16px 18px;border:1px solid var(--err-line);background:var(--err-bg);border-radius:12px}
.alerta-erro > svg{color:var(--err);flex-shrink:0;margin-top:1px}
.alerta-erro > div{flex:1}
.alerta-erro-t{font-weight:700;font-size:14.5px;color:var(--err)}
#erro-lista-txt{font-size:13px;color:var(--slate-2);margin-top:4px}

/* ---------- KPIs ---------- */
.kpis{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));overflow:hidden}
.kpi{background:none;border:0;border-right:1px solid var(--hair);padding:20px 22px;text-align:left;display:flex;flex-direction:column;gap:8px;cursor:pointer;transition:background .15s}
.kpi:last-child{border-right:0}
button.kpi:hover{background:var(--muted)}
button.kpi:hover .kpi-v{color:var(--red)}
.kpi.on{box-shadow:inset 0 -2px 0 var(--red)}
.kpi-fixo{background:var(--muted);cursor:default}
.kpi-v{font-size:30px;font-weight:700;letter-spacing:-.6px;line-height:1;transition:color .15s}

/* ---------- filtros ---------- */
.filtros-card{padding:20px 22px;display:flex;flex-direction:column;gap:16px}
.filtros-topo{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,6fr);gap:12px;align-items:end}
.filtros-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px;align-items:end}
.intervalo{grid-column:1/-1;display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}
.filtros-pend{border-top:1px dashed var(--hair);padding-top:14px;display:flex;align-items:center;gap:16px}
.fchips{display:flex;gap:8px;flex-wrap:wrap;flex-grow:1}
.fchip{display:inline-flex;align-items:center;gap:8px;height:38px;padding:0 15px;border-radius:999px;border:1px solid var(--hair);background:var(--surface);color:var(--slate-2);font-weight:500;font-size:13px;line-height:1;cursor:pointer;transition:all .15s;flex-shrink:0}
.fchip:hover{border-color:var(--red);color:var(--red)}
.fchip .n{font-size:12px;color:var(--slate);font-variant-numeric:tabular-nums}
.fchip.on{background:var(--red);border-color:var(--red);color:#fff}
.fchip.on .n{color:#fff}
.filtros-extra{display:flex;align-items:center;gap:12px}

/* ---------- lista ---------- */
.resultado{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:2px 2px 0}
.resultado-t{font-size:15px}
.sub-i{color:var(--slate)}
.campo-ordem{display:flex;align-items:center;gap:10px}
.campo-ordem .sel{width:240px}
.tabela-card{overflow:hidden}
.tabela-scroll{overflow-x:auto}
.t{width:100%;min-width:1120px;border-collapse:collapse}
.t th{text-align:left;padding:12px 16px;border-bottom:1px solid var(--hair);background:var(--muted);font-size:11.5px;font-weight:500;letter-spacing:.05em;text-transform:uppercase;color:var(--slate);white-space:nowrap}
.t td{padding:16px;border-bottom:1px solid var(--hair);vertical-align:top;font-size:14px;line-height:1.4}
.t tbody tr{cursor:pointer}
.t tbody tr:hover td{background:var(--muted)}
.t tbody tr:last-child td{border-bottom:0}
.c-venda{width:118px}.c-cliente{width:270px}.c-emp{width:230px}.c-eq{width:180px}.c-ac{width:120px}.c-valor{width:124px;text-align:right!important}.c-abrir{width:60px}
.t td.valor{text-align:right;font-weight:500}
.t td.equipe{font-size:13.5px}
.t td.abrir{padding:8px 12px 8px 0;vertical-align:middle}
.nome{font-weight:700}
.meta{display:flex;align-items:center;gap:8px;margin-top:3px;font-size:12.5px;color:var(--slate)}
.nota{display:flex;align-items:center;gap:6px;margin-top:8px;font-size:12.5px;color:var(--slate-2);max-width:250px}
.nota svg{flex-shrink:0}
.dias{display:flex;align-items:center;gap:5px;font-size:12.5px;margin-top:3px;color:var(--slate)}
.dias.alerta{color:var(--warn)}
tr.cancelada td{background:var(--muted)}
.cancelada .nome,.cancelada .meta > .num{text-decoration:line-through;color:var(--slate)}
.cartoes{display:none;flex-direction:column;gap:12px}
.vc{display:flex;flex-direction:column;width:100%;text-align:left;background:var(--surface);border:1px solid var(--hair);border-radius:14px;padding:15px 16px;cursor:pointer}
.vc.cancelada{background:var(--muted)}
.vc-topo{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.vc-topo > svg{flex-shrink:0;color:var(--slate);margin-top:2px}
.vc-id{display:flex;flex-direction:column;gap:2px;min-width:0}
.vc .nome{font-size:15px}
.vc .chips{margin-top:11px}
.vc-nota{display:block;font-size:12.5px;color:var(--slate-2);margin-top:10px}
.vc-rodape{display:flex;justify-content:space-between;align-items:center;margin-top:12px;padding-top:11px;border-top:1px dashed var(--hair);font-size:12.5px}
.vc .valor{font-size:13.5px;font-weight:500}
.vazio{padding:40px 24px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:16px}
.vazio-ico{width:48px;height:48px;border-radius:14px;background:var(--bg);border:1px solid var(--hair);display:flex;align-items:center;justify-content:center;color:var(--slate)}
.vazio-t{font-size:16px;font-weight:700}

/* ---------- dialogos ---------- */
dialog{border:0;padding:0;color:var(--ink);background:var(--surface)}
dialog::backdrop{background:rgba(40,44,46,.42)}
.painel{position:fixed;top:0;right:0;bottom:0;left:auto;margin:0;width:min(620px,100vw);height:100%;max-width:100vw;max-height:100%;border-left:1px solid var(--hair);box-shadow:-12px 0 40px rgba(28,32,34,.16)}
.painel-in{display:flex;flex-direction:column;height:100%}
.painel-cab{padding:22px 28px 20px;border-bottom:1px solid var(--hair);display:flex;flex-direction:column;gap:10px}
.painel-linha{display:flex;align-items:center;justify-content:space-between}
.painel-op{display:flex;align-items:center;gap:4px}
.painel-op .lab{color:var(--slate-2)}
.painel h2{font-size:26px;font-weight:700;letter-spacing:-.5px;line-height:1.15}
.painel-sub{font-size:14px;color:var(--slate-2)}
.tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:2px}
.painel-corpo{flex:1;overflow:auto;padding:22px 28px 28px;display:flex;flex-direction:column;gap:26px}
.mini{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border:1px solid var(--hair);border-radius:10px;overflow:hidden}
.ms{padding:14px 16px;border-right:1px solid var(--hair);display:flex;flex-direction:column;gap:6px}
.ms:last-child{border-right:0}
.ms.alerta{background:var(--warn-bg)}
.ms.alerta .lab{color:var(--warn)}
.mv{font-size:15px;font-weight:700;font-variant-numeric:tabular-nums}
.bloco{display:flex;flex-direction:column;gap:10px}
.bloco-cab{display:flex;align-items:baseline;justify-content:space-between;gap:12px}
.bloco h3{font-size:15px;font-weight:700}
.checklist{list-style:none;margin:0;padding:0}
.ck{display:flex;gap:12px;align-items:flex-start;padding:13px 0;border-bottom:1px dashed var(--hair)}
.ck:last-child{border-bottom:0}
.ck-t{font-size:14px;font-weight:700}
.ck.ok .ck-t{color:var(--slate-2)}
.ci{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.ci-err{background:var(--err-bg);color:var(--err)}
.ci-warn{background:var(--warn-bg);color:var(--warn)}
.ci-ok{background:var(--ok-bg);color:var(--ok)}
.just{background:var(--muted);border:1px solid var(--hair);border-radius:9px;padding:13px 14px;font-size:13.5px;line-height:1.6;white-space:pre-line;overflow-wrap:anywhere}
.bloco-campos{gap:16px}
.painel-rodape{padding:16px 28px;border-top:1px solid var(--hair);display:flex;align-items:center;justify-content:space-between;gap:10px}
.painel-rodape-dir{display:flex;gap:10px}
.dlg{width:min(500px,calc(100vw - 32px));border:1px solid var(--hair);border-radius:18px;box-shadow:0 24px 60px rgba(28,32,34,.22);padding:28px}
.dlg[open]{display:flex;flex-direction:column;gap:18px}
.dlg-ico{width:44px;height:44px;border-radius:12px;background:var(--err-bg);color:var(--err);display:flex;align-items:center;justify-content:center}
.dlg h2{font-size:21px;font-weight:700;letter-spacing:-.3px}
.dlg p{font-size:14.5px;line-height:1.55;color:var(--slate-2)}
.cx-resumo{background:var(--muted);border:1px solid var(--hair);border-radius:10px;padding:12px 14px;display:flex;justify-content:space-between;align-items:center;gap:12px}
.cx-nome{font-size:14px;font-weight:700}
.dlg-acoes{display:flex;justify-content:flex-end;gap:10px;padding-top:4px}
.folha{position:fixed;left:0;right:0;bottom:0;top:auto;margin:0;width:100%;max-width:100%;max-height:88dvh;border-radius:18px 18px 0 0}
.folha[open]{display:flex;flex-direction:column}
.folha-cab{display:flex;align-items:center;justify-content:space-between;padding:12px 12px 12px 20px;border-bottom:1px solid var(--hair)}
.folha-cab h2{font-size:18px;font-weight:700}
.folha-corpo{overflow:auto;padding:16px 20px;display:flex;flex-direction:column;gap:16px}
.folha-corpo .filtros-grid{grid-template-columns:minmax(0,1fr)}
.folha-corpo .intervalo{grid-template-columns:repeat(2,minmax(0,1fr))}
.folha-corpo .filtros-extra{justify-content:space-between}
.folha-corpo .multi-lista{position:static;box-shadow:none;margin-top:6px}
.folha-rodape{padding:12px 20px 20px;border-top:1px solid var(--hair)}

/* ---------- toast (popover: fica acima dos dialogos modais) ---------- */
.toast{display:none;position:fixed;inset:auto auto 24px 50%;transform:translateX(-50%);margin:0;border:0;background:var(--ink);color:#fff;border-radius:12px;padding:12px 16px;align-items:center;gap:12px;box-shadow:0 12px 30px rgba(28,32,34,.22);font-size:14px;max-width:calc(100vw - 32px);z-index:50}
.toast.visivel{display:flex}
.toast.erro{background:var(--err)}
.toast > svg{flex-shrink:0;color:#7FD6A0}
.toast.erro > svg{color:#fff}
.toast-acao{min-height:36px;padding:0 12px;border-radius:8px;border:1px solid rgba(255,255,255,.3);background:transparent;color:#fff;font-weight:500;font-size:13.5px;cursor:pointer}

/* ---------- utilitarios de tela (depois de .btn para vencer) ---------- */
.so-mobile{display:none}

@media (max-width:1100px){
  .topo{padding:28px 32px 24px;min-height:0}
  .topo-logo{top:24px;right:32px;height:36px}
  .topo-acoes{position:static;margin-top:18px;justify-content:flex-end}
  .conteudo{padding:24px 32px 56px}
  .kpis{grid-template-columns:repeat(3,minmax(0,1fr))}
  .kpi:nth-child(3n){border-right:0}
  .kpi:nth-child(-n+3){border-bottom:1px solid var(--hair)}
  .filtros-topo{grid-template-columns:minmax(0,1fr)}
  .filtros-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
  .intervalo{grid-template-columns:repeat(3,minmax(0,1fr))}
}
@media (max-width:820px){
  .so-desktop{display:none}
  .so-mobile{display:inline-flex}
  .topo{padding:20px 16px 18px}
  .topo-logo{top:18px;right:16px;height:26px}
  .topo-textos{gap:10px}
  .topo .step{font-size:11.5px}
  .topo h1{font-size:26px;letter-spacing:-.5px}
  .topo-acoes{margin-top:10px;justify-content:space-between}
  .atualizacao{font-size:12.5px}
  .conteudo{padding:16px 16px 40px;gap:14px}
  #conteudo-lista{gap:14px}
  .kpis{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;background:none;border:0;overflow:visible}
  .kpi,.kpi:nth-child(n){border:1px solid var(--hair);border-radius:12px;padding:13px 14px;gap:6px;background:var(--surface)}
  .kpi-fixo{background:var(--muted)}
  .kpi .sub{display:none}
  .kpi-v{font-size:24px;letter-spacing:-.5px}
  .filtros-card{background:none;border:0;padding:0;gap:12px}
  .filtros-topo{display:flex;gap:8px;align-items:flex-end}
  .campo-busca{flex:1}
  .campo-busca .lab{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
  .filtros-card #filtros-grid,.filtros-card #filtros-extra{display:none}
  #btn-filtros.ativo{border-color:var(--red);color:var(--red)}
  .filtros-pend{border:0;padding:0}
  .fchips{flex-wrap:nowrap;overflow-x:auto;margin:0 -16px;padding:0 16px 2px}
  .resultado .sub-i{display:none}
  .campo-ordem .lab{display:none}
  .campo-ordem .sel{width:auto}
  .tabela-card{display:none}
  .cartoes{display:flex}
  .painel{width:100vw;border-left:0}
  .painel-cab{padding:14px 16px 16px}
  .painel h2{font-size:24px}
  .painel-corpo{padding:18px 16px 24px;gap:20px}
  .mini{grid-template-columns:repeat(2,minmax(0,1fr))}
  .ms:nth-child(2){border-right:0}
  .ms:nth-child(-n+2){border-bottom:1px solid var(--hair)}
  .painel-rodape{flex-direction:column-reverse;align-items:stretch;padding:12px 16px 20px}
  .painel-rodape-dir .btn{flex:1}
  .gate-card{padding:26px 22px}
  .gate-titulo h1{font-size:26px}
}
</style>
</head>
<body>

<!-- ============ tela de senha (spec 3) ============ -->
<div id="gate" class="gate hero" hidden>
  <main class="gate-card">
    <img class="gate-logo" src="assets/img/logo-direcional-header.png" alt="Direcional">
    <div class="gate-titulo">
      <div class="step">Comercial · Área interna</div>
      <h1>Pendências de Vendas</h1>
      <p>Acesso restrito ao time comercial. Digite a senha para ver as vendas com pendência.</p>
    </div>
    <form id="gate-form" class="gate-form" novalidate>
      <div class="campo">
        <label class="lab" for="gate-senha">Senha</label>
        <div class="senha-box">
          <svg class="senha-ico" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>
          <input class="inp" id="gate-senha" type="password" placeholder="Senha do comercial" autocomplete="current-password" enterkeyhint="go" aria-describedby="gate-erro">
          <button class="olho" id="gate-olho" type="button" aria-label="Mostrar senha" aria-pressed="false">
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
        </div>
        <p class="msg-erro" id="gate-erro" hidden>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/></svg>
          <span id="gate-erro-txt"></span>
        </p>
      </div>
      <button class="btn btn-p btn-g" id="gate-entrar" type="submit">Entrar</button>
      <p class="sub" id="gate-demo" hidden>Modo demonstração: qualquer senha entra e os dados são fictícios.</p>
    </form>
  </main>
  <p class="sub">Grupo Direcional · SPI Campinas e Ribeirão Preto</p>
</div>

<!-- ============ dashboard ============ -->
<div id="app" hidden>
  <header class="hero">
    <div class="topo">
      <img class="topo-logo" src="assets/img/logo-direcional-header.png" alt="Direcional">
      <div class="topo-textos">
        <div class="step">Comercial · Área interna</div>
        <h1>Pendências de Vendas</h1>
        <p class="so-desktop">Vendas em Proposta Aprovada, Pró Soluto e SAFI que ainda têm algo travando o fechamento. Clique numa venda para ver o que falta e registrar o retorno.</p>
      </div>
      <div class="topo-acoes">
        <div class="atualizacao"><span class="dot" id="hdr-dot" hidden></span><span id="hdr-atualizacao">Carregando…</span></div>
        <div style="display:flex;gap:8px">
          <button class="btn" id="btn-atualizar" type="button" aria-label="Atualizar do Salesforce">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 4v7h-7"/></svg>
            <span id="btn-atualizar-txt" class="so-desktop">Atualizar do Salesforce</span>
          </button>
          <button class="btn btn-i" id="btn-sair" type="button" aria-label="Sair">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3"/><path d="M10 17l-5-5 5-5"/><path d="M5 12h11"/></svg>
          </button>
        </div>
      </div>
    </div>
  </header>

  <main class="conteudo">
    <p class="aviso-demo" id="aviso-demo" hidden>Modo demonstração: dados fictícios, nada é gravado na planilha.</p>

    <div class="faixa" id="faixa-atualizando" role="status" hidden>
      <div class="faixa-t">
        <svg class="gira" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M12 3a9 9 0 1 0 9 9"/></svg>
        Atualizando do Salesforce…
      </div>
      <div class="barra"><span></span></div>
      <div class="sub">Rodando o relatório na planilha. Pode levar alguns minutos. Edições ficam pausadas até terminar.</div>
    </div>

    <div class="card estado" id="carregando" role="status">
      <svg class="gira" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M12 3a9 9 0 1 0 9 9"/></svg>
      Carregando vendas…
    </div>

    <div class="alerta-erro" id="erro-lista" role="alert" hidden>
      <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/></svg>
      <div>
        <div class="alerta-erro-t">Não deu para carregar as vendas</div>
        <div id="erro-lista-txt"></div>
      </div>
      <button class="btn btn-p" id="erro-lista-tentar" type="button">Tentar de novo</button>
    </div>

    <div id="conteudo-lista" hidden>
      <section class="card kpis" aria-label="Resumo das pendências">
        <button class="kpi" type="button" data-pendencia="todas"><span class="lab">Vendas com pendência</span><span class="kpi-v num" id="kpi-total">0</span><span class="sub" id="kpi-total-sub"></span></button>
        <button class="kpi" type="button" data-pendencia="ac"><span class="lab">AC não aprovada</span><span class="kpi-v num" id="kpi-ac">0</span><span class="sub" id="kpi-ac-sub"></span></button>
        <button class="kpi" type="button" data-pendencia="fid"><span class="lab">Sem FID</span><span class="kpi-v num" id="kpi-fid">0</span><span class="sub" id="kpi-fid-sub"></span></button>
        <button class="kpi" type="button" data-pendencia="ato"><span class="lab">Ato não pago</span><span class="kpi-v num" id="kpi-ato">0</span><span class="sub">Nem boleto/PIX nem cartão</span></button>
        <button class="kpi" type="button" data-pendencia="pcv"><span class="lab">PCV não assinado</span><span class="kpi-v num" id="kpi-pcv">0</span><span class="sub">Cliente ainda não assinou</span></button>
        <div class="kpi kpi-fixo"><span class="lab">VGV pendente</span><span class="kpi-v num" id="kpi-vgv">R$ 0</span><span class="sub">Soma do valor real de venda</span></div>
      </section>

      <section class="card filtros-card" aria-label="Filtros">
        <div class="filtros-topo" id="filtros-topo">
          <div class="campo campo-busca">
            <label class="lab" for="f-busca">Buscar</label>
            <div class="com-ico">
              <svg class="ico-esq" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
              <input class="inp" id="f-busca" type="search" placeholder="Cliente, OP ou unidade" autocomplete="off">
            </div>
          </div>
          <div class="filtros-grid" id="filtros-grid">
            <div class="campo">
              <label class="lab" for="f-emp">Empreendimento</label>
              <div class="sel"><select class="inp" id="f-emp"><option value="">Todos</option></select><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></div>
            </div>
            <div class="campo">
              <label class="lab" for="f-eq">Imobiliária / equipe</label>
              <div class="sel"><select class="inp" id="f-eq"><option value="">Todas</option></select><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></div>
            </div>
            <div class="campo">
              <span class="lab" id="lbl-fase">Fase</span>
              <details class="multi" id="f-fase">
                <summary class="inp" id="f-fase-resumo" aria-labelledby="lbl-fase f-fase-resumo-txt"><span class="ell" id="f-fase-resumo-txt">4 fases (padrão)</span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></summary>
                <div class="multi-lista" id="f-fase-lista" role="group" aria-labelledby="lbl-fase"></div>
              </details>
            </div>
            <div class="campo">
              <label class="lab" for="f-per">Data da venda</label>
              <div class="sel">
                <select class="inp" id="f-per">
                  <option value="todo">Todo o período</option>
                  <option value="mes">Este mês</option>
                  <option value="mes_passado">Mês passado</option>
                  <option value="30d">Últimos 30 dias</option>
                  <option value="intervalo">Intervalo…</option>
                </select>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
              </div>
            </div>
            <div class="campo">
              <label class="lab" for="f-rank">Ranking</label>
              <div class="sel">
                <select class="inp" id="f-rank">
                  <option value="">Todos</option>
                  <option value="diamante">Diamante</option>
                  <option value="ouro">Ouro</option>
                  <option value="prata">Prata</option>
                  <option value="bronze">Bronze</option>
                  <option value="aco">Aço</option>
                </select>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
              </div>
            </div>
            <div class="campo">
              <label class="lab" for="f-tipo">Tipo de venda</label>
              <div class="sel">
                <select class="inp" id="f-tipo">
                  <option value="todas">Comercial e facilitada</option>
                  <option value="comercial">Só comercial</option>
                  <option value="facilitada">Só facilitada</option>
                </select>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
              </div>
            </div>
            <div class="intervalo" id="intervalo" hidden>
              <div class="campo"><label class="lab" for="f-de">De</label><input class="inp" id="f-de" type="date"></div>
              <div class="campo"><label class="lab" for="f-ate">Até</label><input class="inp" id="f-ate" type="date"></div>
            </div>
          </div>
          <button class="btn so-mobile" id="btn-filtros" type="button" aria-haspopup="dialog">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 6h16M7 12h10M10 18h4"/></svg>
            <span id="btn-filtros-txt">Filtros</span>
          </button>
        </div>
        <div class="filtros-pend" id="filtros-pend">
          <span class="lab so-desktop">Pendência</span>
          <div class="fchips" role="group" aria-label="Tipo de pendência">
            <button class="fchip" type="button" data-pendencia="todas">Todas <span class="n" id="chip-n-todas">0</span></button>
            <button class="fchip" type="button" data-pendencia="ac">AC não aprovada <span class="n" id="chip-n-ac">0</span></button>
            <button class="fchip" type="button" data-pendencia="fid">Sem FID <span class="n" id="chip-n-fid">0</span></button>
            <button class="fchip" type="button" data-pendencia="ato">Ato não pago <span class="n" id="chip-n-ato">0</span></button>
            <button class="fchip" type="button" data-pendencia="pcv">PCV não assinado <span class="n" id="chip-n-pcv">0</span></button>
          </div>
          <div class="filtros-extra" id="filtros-extra">
            <label class="sw"><input type="checkbox" id="f-canceladas"><span class="tr" aria-hidden="true"></span>Mostrar canceladas <span class="sub" id="canceladas-n">(0)</span></label>
            <button class="lnk" id="limpar-filtros" type="button">Limpar filtros</button>
          </div>
        </div>
      </section>

      <div class="resultado">
        <p class="resultado-t" aria-live="polite"><strong id="contagem">0 vendas</strong><span class="sub-i" id="contagem-ordem"></span></p>
        <div class="campo-ordem">
          <label class="lab" for="f-ord">Ordenar</label>
          <div class="sel">
            <select class="inp" id="f-ord">
              <option value="antigas">Mais antigas primeiro</option>
              <option value="recentes">Mais recentes primeiro</option>
              <option value="valor">Maior valor</option>
              <option value="pendencias">Mais pendências</option>
            </select>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
          </div>
        </div>
      </div>

      <div id="lista">
        <section class="card tabela-card">
          <div class="tabela-scroll">
            <table class="t">
              <thead>
                <tr>
                  <th scope="col" class="c-venda">Venda</th>
                  <th scope="col" class="c-cliente">Cliente</th>
                  <th scope="col" class="c-emp">Empreendimento</th>
                  <th scope="col" class="c-eq">Equipe</th>
                  <th scope="col">O que falta</th>
                  <th scope="col" class="c-ac">Status AC</th>
                  <th scope="col" class="c-valor">Valor real</th>
                  <th scope="col" class="c-abrir"><span class="sr">Abrir</span></th>
                </tr>
              </thead>
              <tbody id="tabela-corpo"></tbody>
            </table>
          </div>
        </section>
        <div class="cartoes" id="cartoes"></div>
      </div>

      <div class="card vazio" id="vazio" hidden>
        <div class="vazio-ico"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></div>
        <div><div class="vazio-t">Nenhuma venda com esses filtros</div><div class="sub">Tente outro empreendimento ou tipo de pendência.</div></div>
        <button class="btn" id="vazio-limpar" type="button">Limpar filtros</button>
      </div>
    </div>
  </main>
</div>

<!-- ============ detalhe da venda ============ -->
<dialog class="painel" id="painel" aria-labelledby="dt-nome">
  <div class="painel-in">
    <div class="painel-cab">
      <div class="painel-linha">
        <div class="painel-op">
          <span class="lab num" id="dt-op"></span>
          <button class="btn btn-i btn-fantasma btn-mini" id="dt-copiar" type="button" aria-label="Copiar número da OP">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/></svg>
          </button>
        </div>
        <button class="btn btn-i" id="dt-fechar" type="button" aria-label="Fechar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <h2 id="dt-nome"></h2>
      <div class="painel-sub" id="dt-sub"></div>
      <div class="tags" id="dt-tags"></div>
    </div>
    <div class="painel-corpo">
      <div class="mini">
        <div class="ms"><span class="lab">Data da venda</span><span class="mv" id="dt-data"></span></div>
        <div class="ms" id="dt-dias-cel"><span class="lab">Em aberto há</span><span class="mv" id="dt-dias"></span></div>
        <div class="ms"><span class="lab">Valor real</span><span class="mv" id="dt-valor"></span></div>
        <div class="ms"><span class="lab">FID</span><span class="mv" id="dt-fid"></span></div>
      </div>
      <section class="bloco">
        <div class="bloco-cab"><h3>O que falta</h3><span class="sub" id="dt-faltam"></span></div>
        <ul class="checklist" id="dt-checklist"></ul>
      </section>
      <section class="bloco">
        <div class="bloco-cab"><h3>Justificativa da AC</h3><span class="sub">Vem da aba OP X AC · só leitura</span></div>
        <div class="just" id="dt-just"></div>
      </section>
      <section class="bloco bloco-campos">
        <div class="campo"><label class="lab" for="dt-obs">Observação</label><textarea class="inp" id="dt-obs" rows="3" maxlength="5000"></textarea></div>
        <div class="campo">
          <label class="lab" for="dt-ret">Retorno</label>
          <textarea class="inp" id="dt-ret" rows="3" maxlength="5000"></textarea>
          <span class="sub">Grava direto nas colunas Observação e Retorno do RELATÓRIO.</span>
        </div>
      </section>
    </div>
    <div class="painel-rodape">
      <button class="btn btn-d" id="dt-cancelar" type="button">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m5.7 5.7 12.6 12.6"/></svg>
        <span id="dt-cancelar-txt">Marcar como cancelada</span>
      </button>
      <div class="painel-rodape-dir">
        <button class="btn" id="dt-descartar" type="button">Descartar</button>
        <button class="btn btn-p" id="dt-salvar" type="button">Salvar alterações</button>
      </div>
    </div>
  </div>
</dialog>

<!-- ============ confirmar cancelamento ============ -->
<dialog class="dlg" id="dlg-cancelar" role="alertdialog" aria-labelledby="cx-t" aria-describedby="cx-d">
  <div class="dlg-ico"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m5.7 5.7 12.6 12.6"/></svg></div>
  <h2 id="cx-t">Cancelar esta venda?</h2>
  <p id="cx-d">A linha fica vermelha e tachada no RELATÓRIO e a venda sai da lista de pendências. Dá para reativar depois ligando “Mostrar canceladas”.</p>
  <div class="cx-resumo">
    <div><div class="cx-nome" id="cx-nome"></div><div class="sub num" id="cx-meta"></div></div>
    <span class="num" id="cx-valor"></span>
  </div>
  <div class="dlg-acoes">
    <button class="btn" id="cx-voltar" type="button">Voltar</button>
    <button class="btn btn-p" id="cx-confirmar" type="button">Cancelar venda</button>
  </div>
</dialog>

<!-- ============ filtros no celular ============ -->
<dialog class="folha" id="folha-filtros" aria-labelledby="folha-t">
  <div class="folha-cab">
    <h2 id="folha-t">Filtros</h2>
    <button class="btn btn-i btn-fantasma" id="folha-fechar" type="button" aria-label="Fechar filtros"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
  </div>
  <div class="folha-corpo" id="folha-corpo"></div>
  <div class="folha-rodape"><button class="btn btn-p btn-g" id="folha-aplicar" type="button">Ver vendas</button></div>
</dialog>

<div class="toast" id="toast" role="status" popover="manual"></div>

<script src="assets/config.js"></script>
<script src="assets/pendencias.js"></script>
<script src="assets/pendencias-app.js"></script>
</body>
</html>
```

- [ ] **Step 3: Conferir que os IDs usados pelas próximas tarefas existem**

Run:
```bash
node -e "
const html = require('fs').readFileSync('pendencias-vendas.html','utf8');
const ids = 'gate gate-form gate-senha gate-olho gate-erro gate-erro-txt gate-entrar gate-demo app hdr-dot hdr-atualizacao btn-atualizar btn-atualizar-txt btn-sair aviso-demo faixa-atualizando carregando erro-lista erro-lista-txt erro-lista-tentar conteudo-lista kpi-total kpi-total-sub kpi-ac kpi-ac-sub kpi-fid kpi-fid-sub kpi-ato kpi-pcv kpi-vgv filtros-topo f-busca filtros-grid f-emp f-eq f-fase f-fase-resumo f-fase-resumo-txt f-fase-lista f-per f-rank f-tipo intervalo f-de f-ate btn-filtros btn-filtros-txt filtros-pend chip-n-todas chip-n-ac chip-n-fid chip-n-ato chip-n-pcv filtros-extra f-canceladas canceladas-n limpar-filtros contagem contagem-ordem f-ord lista tabela-corpo cartoes vazio vazio-limpar painel dt-op dt-copiar dt-fechar dt-nome dt-sub dt-tags dt-data dt-dias-cel dt-dias dt-valor dt-fid dt-faltam dt-checklist dt-just dt-obs dt-ret dt-cancelar dt-cancelar-txt dt-descartar dt-salvar dlg-cancelar cx-nome cx-meta cx-valor cx-voltar cx-confirmar folha-filtros folha-fechar folha-corpo folha-aplicar toast'.split(' ');
const faltam = ids.filter(id => !html.includes('id=\"' + id + '\"'));
console.log(faltam.length ? 'FALTAM: ' + faltam.join(', ') : 'IDS OK (' + ids.length + ')');
"
```
Expected: `IDS OK (97)`

- [ ] **Step 4: Commit**

```bash
git add assets/config.js pendencias-vendas.html
git commit -m "feat(pendencias): estrutura e estilos da página /pendencias-vendas

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

(A página ainda não funciona: `assets/pendencias-app.js` chega na Task 6.)

---

### Task 6: Interface: API, modo demo, senha, filtros e lista

**Files:**
- Create: `assets/pendencias-app.js`

**Interfaces:**
- Consumes:
  - `window.Pendencias` (Tasks 1–3): `filtrosPadrao`, `aplicarFiltros`, `calcularKpis`, `ordenar`, `opcoesDeFiltro`, `mesmasFases`, `contarFiltrosAtivos`, `derivarPendencias`, `statusAcBadge`, `titleCase`, `formatarEquipe`, `formatarValor`, `formatarMi`, `formatarAtualizacao`, `diasEmAberto`, `textoDias`, `notaDaLinha`, `normalizar`, `FASES_PADRAO`, `DIAS_ALERTA`.
  - `window.PENDENCIAS_APPS_SCRIPT_URL` (Task 5).
  - O contrato da Task 4 e os IDs da Task 5.
- Produces, usados pelas Tasks 7 e 8 dentro do mesmo arquivo:
  - `estado` (objeto único de estado), `$(id)`, `el(tag, classe, texto)`, `icone(nome, tam)`
  - `chamar(acao, params, timeout) → Promise<resposta>`, que rejeita com `{codigo, mensagem}`
  - `render()`, `receberLista(res)`, `carregar()`, `sair(msg)`
  - `vendaPorId(id)`, `substituirVenda(venda)`, `diasDaVenda(venda, hoje) → {texto, alerta}`
  - constantes `MSG_SENHA`, `TIMEOUT_ATUALIZAR`
  - Cada linha da tabela (`tr`) e cada cartão (`button.vc`) recebem `data-abrir="<id da OP>"`.
- Nota: quem abre o painel ao clicar numa linha é a Task 7 (delegação de eventos). Nesta tarefa a linha ainda não reage ao clique.

- [ ] **Step 1: Escrever o arquivo**

Crie `assets/pendencias-app.js`:

```js
/* ============================================================
   PENDENCIAS DE VENDAS - interface
   ------------------------------------------------------------
   Estado + DOM da pagina /pendencias-vendas. Toda regra de negocio
   fica em assets/pendencias.js (window.Pendencias); aqui so se le o
   estado e se desenha. Texto vindo da planilha entra SEMPRE por
   textContent.
   ============================================================ */
(function () {
  'use strict';

  var P = window.Pendencias;
  var URL_API = window.PENDENCIAS_APPS_SCRIPT_URL || '';
  var MODO_DEMO = !URL_API || /[?&]demo=1(&|$)/.test(window.location.search);
  var CHAVE_SESSAO = 'pendencias_senha';
  var TIMEOUT_PADRAO = 60000;
  var TIMEOUT_ATUALIZAR = 360000;
  var MSG_SENHA = 'Senha incorreta. Confira maiúsculas e tente de novo.';
  var ROTULOS_ORDEM = {
    antigas: 'as mais antigas primeiro',
    recentes: 'as mais recentes primeiro',
    valor: 'as de maior valor primeiro',
    pendencias: 'as com mais pendências primeiro'
  };

  var estado = {
    senha: '',
    vendas: [],
    filtros: P.filtrosPadrao(),
    ordem: 'antigas',
    salesforceAtualizadoEm: null,
    atualizando: false,
    aberta: null
  };

  /* ---------- utilitarios de DOM ---------- */
  function $(id) { return document.getElementById(id); }
  function el(tag, classe, texto) {
    var e = document.createElement(tag);
    if (classe) e.className = classe;
    if (texto !== undefined && texto !== null) e.textContent = texto;
    return e;
  }
  var ICONES = {
    relogio: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    nota: '<path d="M4 5h16v10l-5 5H4z"/><path d="M15 20v-5h5"/>',
    seta: '<path d="m9 6 6 6-6 6"/>',
    x: '<path d="M18 6 6 18M6 6l12 12"/>',
    alerta: '<path d="M12 7v6M12 17h.01"/>',
    check: '<path d="M20 6 9 17l-5-5"/>'
  };
  /* icones sao strings fixas deste arquivo, nunca dado da planilha */
  function icone(nome, tam) {
    var s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    var t = String(tam || 14);
    s.setAttribute('width', t);
    s.setAttribute('height', t);
    s.setAttribute('viewBox', '0 0 24 24');
    s.setAttribute('fill', 'none');
    s.setAttribute('stroke', 'currentColor');
    s.setAttribute('stroke-width', '2');
    s.setAttribute('stroke-linecap', 'round');
    s.setAttribute('stroke-linejoin', 'round');
    s.setAttribute('aria-hidden', 'true');
    s.innerHTML = ICONES[nome];
    return s;
  }
  function plural(n, um, varios) { return n + ' ' + (n === 1 ? um : varios); }

  /* ---------- API (spec 4.1) ---------- */
  function falha(codigo, mensagem) { return { codigo: codigo, mensagem: mensagem }; }

  function chamar(acao, params, timeout) {
    if (MODO_DEMO) return chamarDemo(acao, params || {});
    var corpo = Object.assign({ senha: estado.senha, acao: acao }, params || {});
    var ctrl = new AbortController();
    var timer = setTimeout(function () { ctrl.abort(); }, timeout || TIMEOUT_PADRAO);
    /* text/plain evita o preflight de CORS; o Apps Script le e.postData.contents */
    return fetch(URL_API, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(corpo),
      signal: ctrl.signal
    }).then(function (r) { return r.text(); }, function () {
      throw falha('rede', 'A planilha não respondeu. Verifique a conexão e tente de novo.');
    }).then(function (texto) {
      var json;
      try { json = JSON.parse(texto); } catch (e) { throw falha('formato', 'O Web App não respondeu no formato esperado.'); }
      if (!json.ok) throw falha(json.erro || 'interno', json.mensagem || 'Erro no Web App.');
      return json;
    }).finally(function () { clearTimeout(timer); });
  }

  /* modo demonstracao: dados ficticios, grava so na memoria da aba */
  var demoVendas = null;
  function copia(x) { return JSON.parse(JSON.stringify(x)); }
  function chamarDemo(acao, p) {
    var carga = demoVendas ? Promise.resolve() : fetch('tests/fixtures/vendas.json')
      .then(function (r) { return r.json(); })
      .then(function (v) { demoVendas = v; });
    return carga.then(function () {
      return new Promise(function (ok) { setTimeout(ok, acao === 'atualizar' ? 1500 : 350); });
    }).then(function () {
      if (acao === 'listar' || acao === 'atualizar') {
        return { ok: true, vendas: copia(demoVendas), salesforceAtualizadoEm: new Date().toISOString() };
      }
      var v = demoVendas.filter(function (x) { return x.id === p.id; })[0];
      if (!v) throw falha('nao_encontrada', 'Essa venda não está mais no relatório.');
      if (acao === 'cancelar') v.cancelada = true;
      if (acao === 'reativar') v.cancelada = false;
      if (acao === 'editar') { v.observacao = String(p.observacao || '').trim(); v.retorno = String(p.retorno || '').trim(); }
      return { ok: true, venda: copia(v) };
    });
  }

  /* ---------- senha / sessao (spec 3) ---------- */
  function gateCarregando(sim) {
    var b = $('gate-entrar');
    b.disabled = sim;
    b.textContent = sim ? 'Entrando…' : 'Entrar';
  }
  function gateErro(msg) {
    $('gate-erro').hidden = !msg;
    $('gate-erro-txt').textContent = msg || '';
    $('gate-senha').setAttribute('aria-invalid', msg ? 'true' : 'false');
  }
  function mostrarGate(msg) {
    $('app').hidden = true;
    $('gate').hidden = false;
    $('gate-demo').hidden = !MODO_DEMO;
    gateCarregando(false);
    gateErro(msg);
    $('gate-senha').value = '';
    $('gate-senha').focus();
  }
  function mostrarApp() {
    $('gate').hidden = true;
    $('app').hidden = false;
    $('aviso-demo').hidden = !MODO_DEMO;
  }
  function fecharDialogos() {
    ['dlg-cancelar', 'folha-filtros', 'painel'].forEach(function (id) {
      var d = $(id);
      if (d.open) d.close();
    });
  }
  function sair(msg) {
    try { sessionStorage.removeItem(CHAVE_SESSAO); } catch (e) { /* ignora */ }
    estado.senha = '';
    estado.vendas = [];
    fecharDialogos();
    mostrarGate(msg);
  }

  function iniciarGate() {
    $('gate-form').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var senha = $('gate-senha').value;
      if (!senha) { $('gate-senha').focus(); return; }
      estado.senha = senha;
      gateCarregando(true);
      gateErro('');
      chamar('listar').then(function (res) {
        try { sessionStorage.setItem(CHAVE_SESSAO, senha); } catch (e) { /* ignora */ }
        mostrarApp();
        receberLista(res);
      }).catch(function (f) {
        estado.senha = '';
        gateCarregando(false);
        gateErro(f.codigo === 'senha' ? MSG_SENHA : f.mensagem);
        $('gate-senha').select();
      });
    });
    $('gate-olho').addEventListener('click', function () {
      var campo = $('gate-senha');
      var mostrar = campo.type === 'password';
      campo.type = mostrar ? 'text' : 'password';
      this.setAttribute('aria-pressed', mostrar ? 'true' : 'false');
      this.setAttribute('aria-label', mostrar ? 'Ocultar senha' : 'Mostrar senha');
    });
  }

  /* ---------- carga ---------- */
  function mostrarEstadoLista(qual) {
    $('carregando').hidden = qual !== 'carregando';
    $('erro-lista').hidden = qual !== 'erro';
    $('conteudo-lista').hidden = qual !== 'ok';
  }
  function carregar() {
    mostrarEstadoLista('carregando');
    chamar('listar').then(receberLista).catch(function (f) {
      if (f.codigo === 'senha') { sair(MSG_SENHA); return; }
      $('erro-lista-txt').textContent = f.mensagem;
      mostrarEstadoLista('erro');
    });
  }
  function receberLista(res) {
    estado.vendas = res.vendas || [];
    estado.salesforceAtualizadoEm = res.salesforceAtualizadoEm || null;
    preencherOpcoes();
    renderCabecalho();
    mostrarEstadoLista('ok');
    render();
  }
  function vendaPorId(id) {
    return estado.vendas.filter(function (v) { return v.id === id; })[0] || null;
  }
  function substituirVenda(venda) {
    for (var i = 0; i < estado.vendas.length; i++) {
      if (estado.vendas[i].id === venda.id) { estado.vendas[i] = venda; break; }
    }
    render();
  }
  function renderCabecalho() {
    $('hdr-atualizacao').textContent = P.formatarAtualizacao(estado.salesforceAtualizadoEm, new Date());
    $('hdr-dot').hidden = !estado.salesforceAtualizadoEm;
  }

  /* ---------- filtros ---------- */
  function preencherSelect(sel, opcoes, rotuloTodos) {
    var atual = sel.value;
    sel.textContent = '';
    sel.appendChild(new Option(rotuloTodos, ''));
    opcoes.forEach(function (o) { sel.appendChild(new Option(o.rotulo, o.valor)); });
    sel.value = opcoes.some(function (o) { return o.valor === atual; }) ? atual : '';
  }
  function faseMarcada(fase) {
    return estado.filtros.fases.some(function (x) { return P.normalizar(x) === P.normalizar(fase); });
  }
  function preencherOpcoes() {
    var o = P.opcoesDeFiltro(estado.vendas);
    preencherSelect($('f-emp'), o.empreendimentos.map(function (e) { return { valor: e, rotulo: e }; }), 'Todos');
    preencherSelect($('f-eq'), o.equipes, 'Todas');
    estado.filtros.empreendimento = $('f-emp').value;
    estado.filtros.equipe = $('f-eq').value;
    var lista = $('f-fase-lista');
    lista.textContent = '';
    o.fases.forEach(function (fase) {
      var rotulo = el('label', 'multi-op');
      var cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.value = fase;
      cb.checked = faseMarcada(fase);
      cb.addEventListener('change', lerFases);
      rotulo.appendChild(cb);
      rotulo.appendChild(el('span', null, fase));
      lista.appendChild(rotulo);
    });
    atualizarResumoFases();
  }
  function lerFases() {
    estado.filtros.fases = Array.prototype.filter.call($('f-fase-lista').querySelectorAll('input'), function (c) {
      return c.checked;
    }).map(function (c) { return c.value; });
    atualizarResumoFases();
    render();
  }
  function atualizarResumoFases() {
    var f = estado.filtros.fases;
    var txt;
    if (!f.length) txt = 'Todas as fases';
    else if (P.mesmasFases(f, P.FASES_PADRAO)) txt = f.length + ' fases (padrão)';
    else if (f.length === 1) txt = f[0];
    else txt = f.length + ' fases';
    $('f-fase-resumo-txt').textContent = txt;
  }
  function ligarSelect(id, campo) {
    $(id).addEventListener('change', function () { estado.filtros[campo] = this.value; render(); });
  }
  function limparFiltros() {
    estado.filtros = P.filtrosPadrao();
    $('f-busca').value = '';
    $('f-emp').value = '';
    $('f-eq').value = '';
    $('f-per').value = 'todo';
    $('f-de').value = '';
    $('f-ate').value = '';
    $('intervalo').hidden = true;
    $('f-rank').value = '';
    $('f-tipo').value = 'todas';
    $('f-canceladas').checked = false;
    Array.prototype.forEach.call($('f-fase-lista').querySelectorAll('input'), function (c) { c.checked = faseMarcada(c.value); });
    atualizarResumoFases();
    render();
  }
  function iniciarFiltros() {
    var timer;
    $('f-busca').addEventListener('input', function () {
      var valor = this.value;
      clearTimeout(timer);
      timer = setTimeout(function () { estado.filtros.busca = valor; render(); }, 150);
    });
    ligarSelect('f-emp', 'empreendimento');
    ligarSelect('f-eq', 'equipe');
    ligarSelect('f-rank', 'ranking');
    ligarSelect('f-tipo', 'tipo');
    ligarSelect('f-de', 'de');
    ligarSelect('f-ate', 'ate');
    $('f-per').addEventListener('change', function () {
      estado.filtros.periodo = this.value;
      $('intervalo').hidden = this.value !== 'intervalo';
      render();
    });
    $('f-ord').addEventListener('change', function () { estado.ordem = this.value; render(); });
    $('f-canceladas').addEventListener('change', function () { estado.filtros.mostrarCanceladas = this.checked; render(); });
    $('limpar-filtros').addEventListener('click', limparFiltros);
    $('vazio-limpar').addEventListener('click', limparFiltros);
    Array.prototype.forEach.call(document.querySelectorAll('[data-pendencia]'), function (b) {
      b.addEventListener('click', function () { estado.filtros.pendencia = b.getAttribute('data-pendencia'); render(); });
    });
    document.addEventListener('click', function (ev) {
      var d = $('f-fase');
      if (d.open && !d.contains(ev.target)) d.open = false;
    });
  }

  /* ---------- render ---------- */
  function marcarAtivos() {
    var f = estado.filtros;
    $('f-emp').classList.toggle('ativo', !!f.empreendimento);
    $('f-eq').classList.toggle('ativo', !!f.equipe);
    $('f-fase-resumo').classList.toggle('ativo', f.fases.length > 0);
    $('f-per').classList.toggle('ativo', f.periodo !== 'todo');
    $('f-rank').classList.toggle('ativo', !!f.ranking);
    $('f-tipo').classList.toggle('ativo', f.tipo !== 'todas');
  }
  function renderKpis(k) {
    var f = estado.filtros;
    $('kpi-total').textContent = k.total;
    $('kpi-total-sub').textContent = plural(k.canceladasOcultas, 'cancelada', 'canceladas') +
      (f.mostrarCanceladas ? ' na lista' : (k.canceladasOcultas === 1 ? ' oculta' : ' ocultas'));
    $('kpi-ac').textContent = k.ac;
    $('kpi-ac-sub').textContent = plural(k.acReprovadas, 'reprovada', 'reprovadas') + ' · ' + k.acOutras + ' em análise ou não enviadas';
    $('kpi-fid').textContent = k.fid;
    $('kpi-fid-sub').textContent = k.fidPct + '% das vendas';
    $('kpi-ato').textContent = k.ato;
    $('kpi-pcv').textContent = k.pcv;
    $('kpi-vgv').textContent = P.formatarMi(k.vgv);
    $('chip-n-todas').textContent = k.total;
    $('chip-n-ac').textContent = k.ac;
    $('chip-n-fid').textContent = k.fid;
    $('chip-n-ato').textContent = k.ato;
    $('chip-n-pcv').textContent = k.pcv;
    $('canceladas-n').textContent = '(' + k.canceladasOcultas + ')';
    Array.prototype.forEach.call(document.querySelectorAll('.fchip[data-pendencia]'), function (b) {
      var on = b.getAttribute('data-pendencia') === f.pendencia;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    Array.prototype.forEach.call(document.querySelectorAll('.kpi[data-pendencia]'), function (b) {
      var on = f.pendencia !== 'todas' && b.getAttribute('data-pendencia') === f.pendencia;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }
  function chipsPendencia(v) {
    var box = el('span', 'chips');
    var itens = P.derivarPendencias(v);
    if (!itens.length) box.appendChild(el('span', 'chip c-ok', 'Nada pendente'));
    itens.forEach(function (p) { box.appendChild(el('span', 'chip c-' + p.estilo, p.rotulo)); });
    return box;
  }
  function diasDaVenda(v, hoje) {
    var dias = P.diasEmAberto(v.dataVenda, hoje);
    return { texto: P.textoDias(dias), alerta: dias !== null && dias >= P.DIAS_ALERTA };
  }
  function linhaTabela(v, hoje) {
    var tr = el('tr', v.cancelada ? 'cancelada' : '');
    tr.setAttribute('data-abrir', v.id);

    var td1 = el('td');
    td1.appendChild(el('div', 'num', v.dataVenda || '—'));
    var d = diasDaVenda(v, hoje);
    var dias = el('div', 'dias' + (d.alerta ? ' alerta' : ''));
    dias.appendChild(icone('relogio', 13));
    dias.appendChild(document.createTextNode(d.texto));
    td1.appendChild(dias);

    var td2 = el('td');
    td2.appendChild(el('div', 'nome', P.titleCase(v.cliente)));
    var meta = el('div', 'meta');
    meta.appendChild(el('span', 'num', v.id));
    if (v.vendaFacilitada) meta.appendChild(el('span', 'chip c-neu chip-p', 'Facilitada'));
    if (v.cancelada) meta.appendChild(el('span', 'chip c-err chip-p', 'Cancelada'));
    td2.appendChild(meta);
    var nota = P.notaDaLinha(v);
    if (nota) {
      var n = el('div', 'nota');
      n.title = nota;
      n.appendChild(icone('nota', 13));
      n.appendChild(el('span', 'ell', nota));
      td2.appendChild(n);
    }

    var td3 = el('td');
    td3.appendChild(el('div', null, v.empreendimento || '—'));
    if (v.identificador) td3.appendChild(el('div', 'sub num', 'Unidade ' + v.identificador));

    var td4 = el('td', 'equipe', P.formatarEquipe(v.imobiliaria));
    var td5 = el('td');
    td5.appendChild(chipsPendencia(v));
    var ac = P.statusAcBadge(v);
    var td6 = el('td');
    td6.appendChild(el('span', 'chip c-' + ac.estilo, ac.rotulo));
    var td7 = el('td', 'valor num', P.formatarValor(v.valorReal, false));
    var td8 = el('td', 'abrir');
    var b = el('button', 'btn btn-i btn-fantasma');
    b.type = 'button';
    b.setAttribute('aria-label', 'Abrir venda ' + v.id);
    b.appendChild(icone('seta', 18));
    td8.appendChild(b);

    [td1, td2, td3, td4, td5, td6, td7, td8].forEach(function (td) { tr.appendChild(td); });
    return tr;
  }
  function cartao(v, hoje) {
    var c = el('button', 'vc' + (v.cancelada ? ' cancelada' : ''));
    c.type = 'button';
    c.setAttribute('data-abrir', v.id);
    var topo = el('span', 'vc-topo');
    var id = el('span', 'vc-id');
    id.appendChild(el('span', 'nome', P.titleCase(v.cliente)));
    id.appendChild(el('span', 'sub num', [v.id, v.empreendimento, v.identificador].filter(Boolean).join(' · ')));
    topo.appendChild(id);
    topo.appendChild(icone('seta', 18));
    c.appendChild(topo);
    var chips = chipsPendencia(v);
    if (v.cancelada) chips.insertBefore(el('span', 'chip c-err', 'Cancelada'), chips.firstChild);
    c.appendChild(chips);
    var nota = P.notaDaLinha(v);
    if (nota) c.appendChild(el('span', 'vc-nota ell', nota));
    var rodape = el('span', 'vc-rodape');
    var quando = el('span', 'num');
    var d = diasDaVenda(v, hoje);
    if (v.dataVenda) {
      quando.appendChild(el('span', 'sub', v.dataVenda.slice(0, 5) + ' · '));
      quando.appendChild(el('span', d.alerta ? 'alerta' : '', d.texto));
    } else {
      quando.appendChild(el('span', 'sub', 'Sem data da venda'));
    }
    rodape.appendChild(quando);
    rodape.appendChild(el('span', 'num valor', P.formatarValor(v.valorReal, false)));
    c.appendChild(rodape);
    return c;
  }
  function render() {
    var hoje = new Date();
    var f = estado.filtros;
    renderKpis(P.calcularKpis(estado.vendas, f, hoje));
    marcarAtivos();
    var n = P.contarFiltrosAtivos(f);
    $('btn-filtros-txt').textContent = n ? 'Filtros · ' + n : 'Filtros';
    $('btn-filtros').classList.toggle('ativo', n > 0);

    var lista = P.ordenar(P.aplicarFiltros(estado.vendas, f, hoje), estado.ordem);
    $('contagem').textContent = plural(lista.length, 'venda', 'vendas');
    $('contagem-ordem').textContent = ' · ' + ROTULOS_ORDEM[estado.ordem];
    var corpo = $('tabela-corpo');
    var cartoes = $('cartoes');
    corpo.textContent = '';
    cartoes.textContent = '';
    lista.forEach(function (v) {
      corpo.appendChild(linhaTabela(v, hoje));
      cartoes.appendChild(cartao(v, hoje));
    });
    $('vazio').hidden = lista.length > 0;
    $('lista').hidden = lista.length === 0;
  }

  /* ---------- inicio ---------- */
  function iniciar() {
    iniciarGate();
    iniciarFiltros();
    $('btn-sair').addEventListener('click', function () { sair(); });
    $('erro-lista-tentar').addEventListener('click', carregar);
    var salva = null;
    try { salva = sessionStorage.getItem(CHAVE_SESSAO); } catch (e) { /* ignora */ }
    if (salva) { estado.senha = salva; mostrarApp(); carregar(); }
    else mostrarGate();
  }
  iniciar();
})();
```

- [ ] **Step 2: Subir o servidor local e abrir a página**

Use a configuração `portal-do-corretor` de `.claude/launch.json` (`python3 -m http.server`). No navegador (pane de preview), abra `http://localhost:<porta>/pendencias-vendas.html`. Localmente não existe `cleanUrls`, então use o `.html`.

Expected: tela de senha com a logo Direcional, o aviso "Modo demonstração: qualquer senha entra…" e nenhum erro no console.

- [ ] **Step 3: Verificar senha, KPIs, filtros e lista (modo demo)**

Digite `teste` no campo de senha e aperte Enter. Confira:

1. A tela de senha some, aparece o aviso amarelo de modo demonstração e o cabeçalho mostra "Salesforce atualizado hoje às HH:mm".
2. KPIs: **11** com pendência ("2 canceladas ocultas"), **8** AC não aprovada ("5 reprovadas · 3 em análise ou não enviadas"), **10** sem FID ("91% das vendas"), **6** ato não pago, **3** PCV não assinado, **R$ 2,47 mi**.
3. "11 vendas · as mais antigas primeiro". A primeira linha é Fernanda Costa (OP-000013) e a última Simone Ribeiro (sem data).
4. Chip "PCV não assinado": ficam 3 vendas, os KPIs **não** mudam e o chip fica vermelho.
5. Busca `leticia`: fica só Letícia Fernandes Rocha.
6. Liga "Mostrar canceladas (2)": aparecem Roberto Almeida e Pedro Henrique Carvalho no fim, com o nome tachado e o selo "Cancelada".
7. Fase: desmarcar tudo mostra "Todas as fases" e "12 vendas". "Limpar filtros" volta a 11.
8. Empreendimento "Village Park" + chip "AC não aprovada" mostra o estado vazio "Nenhuma venda com esses filtros". "Limpar filtros" volta ao normal.
9. Recarregue a página: entra direto, sem pedir senha (sessão). "Sair" volta à tela de senha.
10. Console sem erros.

Se algo divergir, corrija em `assets/pendencias-app.js` (as regras estão cobertas por testes; a divergência provavelmente é de DOM).

- [ ] **Step 4: Commit**

```bash
git add assets/pendencias-app.js
git commit -m "feat(pendencias): senha, modo demo, KPIs, filtros e lista

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Detalhe da venda, edição, cancelamento, atualização e avisos

**Files:**
- Modify: `assets/pendencias-app.js`

**Interfaces:**
- Consumes: tudo o que a Task 6 produz (`estado`, `$`, `el`, `icone`, `chamar`, `render`, `receberLista`, `carregar`, `sair`, `vendaPorId`, `substituirVenda`, `MSG_SENHA`, `TIMEOUT_ATUALIZAR`); de `window.Pendencias`, `checklist`, `justificativaExibida`, `rankingRotulo`.
- Produces: `abrirPainel(id)`, `preencherPainel(venda, resetarCampos)`, `fecharPainel(forcar) → boolean`, `toast(msg, {erro?, acao?:{rotulo, fn}})`, `atualizarSalesforce()`, `iniciarPainel()`.

- [ ] **Step 1: Acrescentar o painel, as edições e os avisos**

Em `assets/pendencias-app.js`, troque a linha `  /* ---------- inicio ---------- */` por este bloco (o bloco já termina com a mesma linha `/* ---------- inicio ---------- */`):

```js
  /* ---------- avisos (toast) ----------
     popover="manual": entra na top layer DEPOIS do dialogo modal aberto,
     entao aparece por cima dele. Sem suporte a popover, so a classe. */
  var toastTimer;
  function esconderToast() {
    var t = $('toast');
    t.classList.remove('visivel');
    if (t.hidePopover && t.matches(':popover-open')) t.hidePopover();
  }
  function toast(msg, opcoes) {
    opcoes = opcoes || {};
    var t = $('toast');
    esconderToast();
    t.textContent = '';
    t.className = 'toast' + (opcoes.erro ? ' erro' : '');
    t.appendChild(icone(opcoes.erro ? 'alerta' : 'check', 18));
    t.appendChild(el('span', null, msg));
    if (opcoes.acao) {
      var b = el('button', 'toast-acao', opcoes.acao.rotulo);
      b.type = 'button';
      b.addEventListener('click', function () { esconderToast(); opcoes.acao.fn(); });
      t.appendChild(b);
    }
    t.classList.add('visivel');
    if (t.showPopover) t.showPopover();
    clearTimeout(toastTimer);
    toastTimer = setTimeout(esconderToast, opcoes.acao ? 8000 : 5000);
  }

  function tratarFalhaAcao(f) {
    if (f.codigo === 'senha') { sair(MSG_SENHA); return; }
    if (f.codigo === 'nao_encontrada') {
      toast(f.mensagem || 'Essa venda não está mais no relatório.', { erro: true });
      fecharPainel(true);
      carregar();
      return;
    }
    toast(f.mensagem || 'Não deu para salvar. Tente de novo.', { erro: true });
  }
  function exigirLivre() {
    if (!estado.atualizando) return true;
    toast('Aguarde a atualização do Salesforce terminar.', { erro: true });
    return false;
  }

  /* ---------- painel de detalhe (spec 6) ---------- */
  function painelSujo() {
    var v = estado.aberta;
    if (!v) return false;
    return $('dt-obs').value !== (v.observacao || '') || $('dt-ret').value !== (v.retorno || '');
  }
  function atualizarBotoesPainel() {
    var sujo = painelSujo();
    $('dt-salvar').disabled = !sujo || estado.atualizando;
    $('dt-descartar').disabled = !sujo;
    $('dt-cancelar').disabled = estado.atualizando;
  }
  function preencherPainel(v, resetarCampos) {
    var hoje = new Date();
    $('dt-op').textContent = v.id;
    $('dt-nome').textContent = P.titleCase(v.cliente);
    $('dt-sub').textContent = [
      v.empreendimento, v.identificador ? 'Unidade ' + v.identificador : '', P.formatarEquipe(v.imobiliaria)
    ].filter(Boolean).join(' · ');
    var tags = $('dt-tags');
    tags.textContent = '';
    [v.fase, v.vendaFacilitada ? 'Venda facilitada' : 'Venda comercial', v.ranking ? 'Ranking ' + P.rankingRotulo(v.ranking) : '']
      .filter(Boolean)
      .forEach(function (t) { tags.appendChild(el('span', 'chip c-neu', t)); });
    if (v.cancelada) tags.appendChild(el('span', 'chip c-err', 'Cancelada'));

    $('dt-data').textContent = v.dataVenda || '—';
    var d = diasDaVenda(v, hoje);
    $('dt-dias').textContent = d.texto;
    $('dt-dias-cel').classList.toggle('alerta', d.alerta);
    $('dt-valor').textContent = P.formatarValor(v.valorReal, true);
    $('dt-fid').textContent = String(v.fid || '').trim() || '—';

    var itens = P.checklist(v);
    var faltam = itens.filter(function (i) { return !i.ok; }).length;
    $('dt-faltam').textContent = faltam ? faltam + ' de ' + itens.length + ' itens pendentes' : 'Nada pendente';
    var ul = $('dt-checklist');
    ul.textContent = '';
    itens.forEach(function (it) {
      var li = el('li', 'ck' + (it.ok ? ' ok' : ''));
      var bola = el('span', 'ci ci-' + it.estilo);
      bola.appendChild(icone(it.ok ? 'check' : (it.estilo === 'err' ? 'x' : 'alerta'), 14));
      var txt = el('div');
      txt.appendChild(el('div', 'ck-t', it.titulo));
      txt.appendChild(el('div', 'sub', it.detalhe));
      li.appendChild(bola);
      li.appendChild(txt);
      ul.appendChild(li);
    });

    $('dt-just').textContent = P.justificativaExibida(v.justificativa);
    if (resetarCampos) {
      $('dt-obs').value = v.observacao || '';
      $('dt-ret').value = v.retorno || '';
    }
    $('dt-cancelar-txt').textContent = v.cancelada ? 'Reativar venda' : 'Marcar como cancelada';
    $('dt-cancelar').classList.toggle('btn-d', !v.cancelada);
    atualizarBotoesPainel();
  }
  function abrirPainel(id) {
    var v = vendaPorId(id);
    if (!v) return;
    estado.aberta = v;
    preencherPainel(v, true);
    if (!$('painel').open) $('painel').showModal();
  }
  function fecharPainel(forcar) {
    var d = $('painel');
    if (!d.open) return true;
    if (!forcar && painelSujo() && !window.confirm('Descartar as alterações em Observação e Retorno?')) return false;
    d.close();
    return true;
  }
  /* devolve o foco para a linha/cartao visivel da venda que estava aberta */
  function focarOrigem(id) {
    var alvos = document.querySelectorAll('[data-abrir]');
    for (var i = 0; i < alvos.length; i++) {
      var a = alvos[i];
      if (a.getAttribute('data-abrir') !== id || a.offsetParent === null) continue;
      (a.tagName === 'TR' ? a.querySelector('button') : a).focus();
      return;
    }
  }

  function salvar() {
    if (!exigirLivre()) return;
    var v = estado.aberta;
    var b = $('dt-salvar');
    b.disabled = true;
    b.textContent = 'Salvando…';
    chamar('editar', { id: v.id, observacao: $('dt-obs').value, retorno: $('dt-ret').value })
      .then(function (res) {
        estado.aberta = res.venda;
        substituirVenda(res.venda);
        preencherPainel(res.venda, true);
        toast('Alterações salvas na planilha');
      })
      .catch(tratarFalhaAcao)
      .then(function () { b.textContent = 'Salvar alterações'; atualizarBotoesPainel(); });
  }

  function mudarCancelamento(id, acao) {
    var b = $('dt-cancelar');
    b.disabled = true;
    return chamar(acao, { id: id }).then(function (res) {
      substituirVenda(res.venda);
      if (estado.aberta && estado.aberta.id === id) {
        estado.aberta = res.venda;
        preencherPainel(res.venda, false);
      }
      if (acao === 'cancelar') {
        fecharPainel(true);
        toast('Venda ' + id + ' cancelada', {
          acao: { rotulo: 'Desfazer', fn: function () { mudarCancelamento(id, 'reativar'); } }
        });
      } else {
        toast('Venda ' + id + ' reativada');
      }
    }).catch(tratarFalhaAcao).then(function () { atualizarBotoesPainel(); });
  }
  function clicarCancelar() {
    if (!exigirLivre()) return;
    var v = estado.aberta;
    if (v.cancelada) { mudarCancelamento(v.id, 'reativar'); return; }
    if (painelSujo()) {
      toast('Salve ou descarte as alterações antes de cancelar a venda.', { erro: true });
      return;
    }
    $('cx-nome').textContent = P.titleCase(v.cliente);
    $('cx-meta').textContent = [v.id, v.empreendimento, v.identificador].filter(Boolean).join(' · ');
    $('cx-valor').textContent = P.formatarValor(v.valorReal, false);
    $('dlg-cancelar').showModal();
  }

  function copiarOp() {
    var id = estado.aberta && estado.aberta.id;
    if (!id) return;
    var p = navigator.clipboard ? navigator.clipboard.writeText(id) : Promise.reject();
    p.then(function () { toast('OP ' + id + ' copiada'); }, function () { toast('Não deu para copiar. OP: ' + id, { erro: true }); });
  }

  /* ---------- atualizar do Salesforce (spec 4.4) ---------- */
  function atualizarSalesforce() {
    if (estado.atualizando) return;
    estado.atualizando = true;
    var b = $('btn-atualizar');
    b.disabled = true;
    $('btn-atualizar-txt').textContent = 'Atualizando…';
    $('faixa-atualizando').hidden = false;
    atualizarBotoesPainel();
    chamar('atualizar', null, TIMEOUT_ATUALIZAR)
      .then(function (res) { receberLista(res); toast('Relatório atualizado do Salesforce'); })
      .catch(function (f) {
        if (f.codigo === 'rede') f.mensagem = 'A atualização não terminou a tempo. Rode "Atualizar Relatório" pelo menu Salesforce da planilha.';
        tratarFalhaAcao(f);
      })
      .then(function () {
        estado.atualizando = false;
        b.disabled = false;
        $('btn-atualizar-txt').textContent = 'Atualizar do Salesforce';
        $('faixa-atualizando').hidden = true;
        atualizarBotoesPainel();
      });
  }

  function iniciarPainel() {
    function abrirPorClique(ev) {
      var alvo = ev.target.closest('[data-abrir]');
      if (alvo) abrirPainel(alvo.getAttribute('data-abrir'));
    }
    $('tabela-corpo').addEventListener('click', abrirPorClique);
    $('cartoes').addEventListener('click', abrirPorClique);

    var painel = $('painel');
    painel.addEventListener('cancel', function (ev) { ev.preventDefault(); fecharPainel(false); });
    painel.addEventListener('click', function (ev) { if (ev.target === painel) fecharPainel(false); });
    painel.addEventListener('close', function () {
      var id = estado.aberta && estado.aberta.id;
      estado.aberta = null;
      if (id) focarOrigem(id);
    });
    $('dt-fechar').addEventListener('click', function () { fecharPainel(false); });
    $('dt-obs').addEventListener('input', atualizarBotoesPainel);
    $('dt-ret').addEventListener('input', atualizarBotoesPainel);
    $('dt-descartar').addEventListener('click', function () { preencherPainel(estado.aberta, true); });
    $('dt-salvar').addEventListener('click', salvar);
    $('dt-cancelar').addEventListener('click', clicarCancelar);
    $('dt-copiar').addEventListener('click', copiarOp);

    $('cx-voltar').addEventListener('click', function () { $('dlg-cancelar').close(); });
    $('cx-confirmar').addEventListener('click', function () {
      $('dlg-cancelar').close();
      if (estado.aberta) mudarCancelamento(estado.aberta.id, 'cancelar');
    });
    $('btn-atualizar').addEventListener('click', atualizarSalesforce);
  }

  /* ---------- inicio ---------- */
```

- [ ] **Step 2: Ligar o painel no início e no recarregamento da lista**

Em `iniciar()`, troque:

```js
    iniciarGate();
    iniciarFiltros();
```

por:

```js
    iniciarGate();
    iniciarFiltros();
    iniciarPainel();
```

Em `receberLista(res)`, troque:

```js
    mostrarEstadoLista('ok');
    render();
  }
```

por:

```js
    mostrarEstadoLista('ok');
    render();
    /* painel aberto durante um "Atualizar": troca pela versao nova da venda */
    if (estado.aberta) {
      var fresca = vendaPorId(estado.aberta.id);
      if (fresca) { var sujo = painelSujo(); estado.aberta = fresca; preencherPainel(fresca, !sujo); }
      else fecharPainel(true);
    }
  }
```

- [ ] **Step 3: Verificar no navegador (modo demo)**

Recarregue `pendencias-vendas.html`, entre com qualquer senha e confira:

1. Clicar na linha de Mariana Alves Pereira abre o painel lateral com:
   - "OP-000001", o nome em maiúsculas/minúsculas normais e "Village Gaia · Unidade BL02-0104 · Equipe Leonardo Donizete";
   - os selos Proposta Aprovada, Venda comercial e Ranking Ouro;
   - "3 de 4 itens pendentes": ✕ AC reprovada, ! Sem FID, ! Ato não pago, ✓ PCV assinado;
   - a justificativa em 3 linhas;
   - Salvar e Descartar desabilitados.
2. Editar o Retorno habilita Salvar. Esc pede "Descartar as alterações…?"; Cancelar no confirm mantém o painel aberto.
3. Salvar mostra o aviso "Alterações salvas na planilha" **por cima** do painel. Fechando o painel, a nota da linha mostra o novo Retorno e o foco volta para o botão ">" da linha.
4. "Marcar como cancelada" abre o diálogo com nome, OP e valor. "Cancelar venda" fecha tudo, a venda some, os KPIs recalculam (10 com pendência, "3 canceladas ocultas") e aparece o aviso "Venda OP-000001 cancelada · Desfazer".
5. "Desfazer" traz a venda de volta ("Venda OP-000001 reativada").
6. Com "Mostrar canceladas", abrir Roberto Almeida mostra "Reativar venda" no rodapé; clicar reativa.
7. "Atualizar do Salesforce": a faixa "Atualizando do Salesforce…" com barra aparece e o botão fica "Atualizando…". Depois de ~1,5 s some e aparece "Relatório atualizado do Salesforce". As edições feitas continuam (modo demo guarda na memória).
8. Botão de copiar OP mostra "OP OP-000001 copiada".
9. Console sem erros.

- [ ] **Step 4: Commit**

```bash
git add assets/pendencias-app.js
git commit -m "feat(pendencias): detalhe da venda, edição, cancelamento e atualização

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Celular: folha de filtros e verificação responsiva

**Files:**
- Modify: `assets/pendencias-app.js`

**Interfaces:**
- Consumes: `$`, `render`, `estado` (Task 6); markup `folha-filtros`, `folha-corpo`, `filtros-grid`, `filtros-extra`, `filtros-topo`, `btn-filtros`, `filtros-pend` (Task 5).
- Produces: `iniciarFolhaFiltros()`. Abaixo de 820 px, os filtros de seleção e a chave de canceladas passam para uma folha inferior.

- [ ] **Step 1: Acrescentar a folha de filtros**

Em `assets/pendencias-app.js`, troque a linha `  /* ---------- inicio ---------- */` por:

```js
  /* ---------- filtros no celular (folha inferior) ----------
     Os MESMOS elementos de filtro mudam de lugar: vao para a folha ao abrir
     e voltam para o card ao fechar (nada duplicado, nada a sincronizar). */
  function abrirFolhaFiltros() {
    var corpo = $('folha-corpo');
    corpo.appendChild($('filtros-grid'));
    corpo.appendChild($('filtros-extra'));
    $('folha-filtros').showModal();
  }
  function devolverFiltros() {
    $('filtros-topo').insertBefore($('filtros-grid'), $('btn-filtros'));
    $('filtros-pend').appendChild($('filtros-extra'));
  }
  function iniciarFolhaFiltros() {
    var folha = $('folha-filtros');
    $('btn-filtros').addEventListener('click', abrirFolhaFiltros);
    $('folha-fechar').addEventListener('click', function () { folha.close(); });
    $('folha-aplicar').addEventListener('click', function () { folha.close(); });
    folha.addEventListener('click', function (ev) { if (ev.target === folha) folha.close(); });
    folha.addEventListener('close', devolverFiltros);
  }

  /* ---------- inicio ---------- */
```

Em `iniciar()`, troque:

```js
    iniciarPainel();
```

por:

```js
    iniciarPainel();
    iniciarFolhaFiltros();
```

- [ ] **Step 2: Verificar a 390 × 844 (celular)**

Redimensione o preview para o preset mobile (390 × 844), recarregue e entre. Compare com `docs/design/pendencias-vendas/telas/Mobile-Lista.png` e `Mobile-Detalhe.png`:

1. Cabeçalho compacto: logo pequena à direita, título de 26 px, "Salesforce atualizado…" e dois botões só com ícone (atualizar, sair).
2. KPIs em 2 colunas, sem subtexto.
3. Busca + botão "Filtros" na mesma linha; chips de pendência rolando na horizontal; lista em cartões (não tabela).
4. "Filtros" abre a folha inferior com Empreendimento, Equipe, Fase (lista de caixas), Data, Ranking, Tipo, "Mostrar canceladas" e "Limpar filtros". Escolher "Village Gaia" e tocar "Ver vendas" fecha a folha: o botão vira "Filtros · 1" com borda vermelha e a lista mostra 3 vendas. Reabrir a folha mostra "Village Gaia" ainda selecionado.
5. Tocar num cartão abre o detalhe em tela cheia; mini-resumo em 2×2; rodapé com Salvar/Descartar em cima e "Marcar como cancelada" embaixo.
6. Sem rolagem horizontal da página (só os chips rolam).

Depois volte o preview para desktop e confira a 1100 px e a 1440 px:
- 1440 px: parecido com `Main.png`;
- 1100 px: KPIs em 3 colunas e ações do topo abaixo do título;
- em nenhuma largura a tabela quebra o layout (se faltar espaço, ela rola dentro do card).

- [ ] **Step 3: Commit**

```bash
git add assets/pendencias-app.js
git commit -m "feat(pendencias): folha de filtros no celular

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Documentação e checagem final

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: todos os arquivos anteriores.
- Produces: README atualizado; a branch pronta para a implantação manual.

- [ ] **Step 1: Atualizar o README**

Em `README.md`, na seção `## Estrutura`, troque o bloco de código por:

```
index.html              Home: escolhe cidade -> escolhe empreendimento
empreendimento.html     Página de detalhe (?e=<id> na URL)
pendencias-vendas.html  Pendências de Vendas (interno, comercial, com senha)
assets/
  config.js             Cidades, empreendimentos e URLs das planilhas  <-- EDITAR AQUI
  data.js               Motor: busca CSV, filtra por empreendimento, renderiza unidades
  pendencias.js         Regras da página de pendências (puras, testadas)
  pendencias-app.js     Interface da página de pendências
  styles.css            Estilos compartilhados
docs/
  apps-script-pendencias.gs   Web App da página de pendências
  design/pendencias-vendas/   Telas aprovadas (PNG + prévias HTML)
tests/                  Testes das regras (node --test)
vercel.json             Configuração de deploy estático
```

E acrescente, antes de `## Rodar localmente`:

````markdown
## Pendências de Vendas (`/pendencias-vendas`)

Página interna do comercial para cobrar pendências das vendas da aba
`RELATÓRIO` (planilha de vendas). A página conversa **só** com o Web App do
Apps Script da planilha (`docs/apps-script-pendencias.gs`, instruções de
implantação no cabeçalho). A senha fica no Apps Script, não no site.

- `window.PENDENCIAS_APPS_SCRIPT_URL` em `assets/config.js` = URL `/exec` do Web App.
- Vazio (ou `?demo=1` na URL) = **modo demonstração** com os dados fictícios de
  `tests/fixtures/vendas.json`. Nada é gravado.
- Regras de negócio em `assets/pendencias.js`. Testes:

```bash
node --test tests/*.test.js
```

Spec: `docs/superpowers/specs/2026-09-28-pendencias-vendas-design.md`.
````

- [ ] **Step 2: Rodar todos os testes**

Run: `node --test tests/*.test.js`
Expected: PASS nos 3 arquivos, 0 falhas.

- [ ] **Step 3: Varredura de segurança e privacidade**

Run:
```bash
grep -n "Comercial123" pendencias-vendas.html assets/*.js tests -r ; \
grep -nE "[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}" tests assets pendencias-vendas.html -r ; \
grep -n "innerHTML" assets/pendencias-app.js
```
Expected:
- nenhuma ocorrência de `Comercial123` (a senha só aparece em `docs/apps-script-pendencias.gs`);
- nenhum CPF;
- `innerHTML` só na função `icone()` (strings fixas de `ICONES`).

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: página Pendências de Vendas no README

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: Implantação (manual, com o Gabriel)

Esta tarefa depende de acesso à planilha e à Vercel. **O agente não faz nada disto sozinho**: prepare, peça e confira. Nunca digite a senha em nenhum site nem faça deploy.

**Files:**
- Modify: `assets/config.js` (só a URL, depois que o Gabriel passar)

**Interfaces:**
- Consumes: `docs/apps-script-pendencias.gs` (Task 4), página pronta (Tasks 5–9).
- Produces: página em produção em `https://produtosdirecional.vercel.app/pendencias-vendas`.

- [ ] **Step 1 (Gabriel): Publicar o Web App**

Seguir os passos 1–7 do cabeçalho de `docs/apps-script-pendencias.gs`. Conferir no log de `testePendencias()`:
- `Vendas: ~295 | canceladas: ~63`;
- "Por fase" com `Proposta Aprovada` e `Fechado e ganho`;
- colunas incluindo `ID`, `Observação` e `Retorno`.

Se aparecer `Coluna "…" não encontrada`, o cabeçalho da linha 3 do RELATÓRIO tem outro nome. Ajuste a planilha ou a constante `PEND_OBRIGATORIAS` / os nomes em `pendVendaDaLinha_`.

- [ ] **Step 2 (Gabriel → agente): Configurar a URL**

Com a URL `/exec` que o Gabriel passar, edite `assets/config.js`:

```js
window.PENDENCIAS_APPS_SCRIPT_URL = '<URL /exec recebida>';
```

Conferir que a URL responde sem vazar dados sem senha:

```bash
curl -sL -X POST -H 'Content-Type: text/plain;charset=utf-8' -d '{"senha":"x","acao":"listar"}' '<URL /exec recebida>'
```
Expected: `{"ok":false,"erro":"senha","mensagem":"Senha incorreta."}`

```bash
git add assets/config.js
git commit -m "chore(pendencias): apontar para o Web App publicado

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 3 (agente): Push da branch e PR**

```bash
git push -u origin feat/pendencias-vendas
gh pr create --base main --title "feat: página Pendências de Vendas" --body "$(cat <<'EOF'
Página interna `/pendencias-vendas` para o comercial cobrar pendências das vendas (aba RELATÓRIO).

- Spec: docs/superpowers/specs/2026-09-28-pendencias-vendas-design.md
- Telas: docs/design/pendencias-vendas/telas/
- Web App: docs/apps-script-pendencias.gs (já publicado na planilha)
- Testes: `node --test tests/*.test.js`

Deploy na Vercel é manual depois do merge (WORKFLOW.md).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 4 (Gabriel): Merge, deploy manual na Vercel e aceite em produção**

Checklist de aceite (spec §9) em `https://produtosdirecional.vercel.app/pendencias-vendas`:

1. Senha errada mostra "Senha incorreta"; `Comercial123` entra.
2. KPIs batem com a planilha (em 28/09/2026 eram 52 / 45 / 49 / 25 / 10 · R$ 8,49 mi).
3. Cada filtro funciona; "Mostrar canceladas" mostra as ~61 canceladas do recorte.
4. Editar o Retorno de uma venda → conferir o texto na planilha.
5. Cancelar uma venda de teste → linha vermelha e tachada no RELATÓRIO → "Desfazer" → a fonte volta a preta.
6. "Atualizar do Salesforce" termina e o cabeçalho mostra o horário novo.
7. Celular (390 px) ok.
8. Avisar o outro dev para dar `git pull` na `main` (WORKFLOW.md).

- [ ] **Step 5 (Gabriel, recomendado): Fechar a planilha**

Confirmar que nada mais lê o CSV da planilha de vendas e tirar o compartilhamento "Qualquer pessoa com o link" (spec §8). A página continua funcionando, porque só usa o Web App.

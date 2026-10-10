# Visitas v2 — dados do cliente em popup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cada visita passa a registrar nome, CPF e telefone do cliente, data/hora, corretor (obrigatório), gerente (opcional) e, no tipo imobiliária, a imobiliária. O registro acontece num popup aberto pelos cards do Passo 2, e a página pública nunca recebe CPF, telefone nem nome completo.

**Architecture:** Mesma arquitetura da v1 (site estático + Web App do Apps Script). As regras puras novas (CPF, telefone, máscaras, validação, resumo público) entram em `assets/visitas.js`. O `.gs` ganha as mesmas regras em funções próprias, testadas no Node via `vm`, com paridade de resultado. A recepção troca o formulário inline por um `<dialog>` nativo.

**Tech Stack:** HTML/CSS/JS ES5 (`var`, `function`, IIFE), Google Apps Script (V8), `node --test` sem dependências.

**Spec:** `docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md`. A §13 é a v2; ela vale onde diverge das seções 1–12. Telas: canvas "Visitas Recepção" (https://claude.ai/artifact/254FTbPxSoAVKMsPvJd8vV), quadros `Main`, `PopupImobiliaria`, `PopupCelular` e `Admin`.

**Estado de partida:** branch `feat/visitas-recepcao` com a v1 completa, 68 testes passando.

## Global Constraints

- Sem dependências npm, sem build. Estilo do repo: IIFE, `'use strict'`, `var`, `function`, comentários curtos em português sem acento.
- Testes: `node --test tests/*.test.js`.
- Tipos `esp`/`house`/`imob`, nomes `Espontânea`/`Corretor house`/`Imobiliária`, cores `#3A4043`/`#E4032B`/`#A3ABAE`.
- **Visita completa** (só `listar`, com senha): `{ id, data: 'yyyy-MM-dd', hora: 'HH:mm', empreendimento, cidade, tipo, cliente, cpf /* 11 dígitos */, telefone /* 10–11 dígitos */, imobiliaria, corretor, gerente }`.
- **Visita resumida** (respostas públicas `registrar` e `dia`): `{ id, data, hora, empreendimento, tipo, primeiroNome, imobiliaria, corretor }`. CPF, telefone, nome completo e gerente **nunca** entram nela.
- `registrar` → `{ visita /* resumida */, token, cpfRepetido }`. `dia` → `{ visitas /* resumidas */, sugestoes: { imobiliarias, corretores, gerentes } }`.
- Colunas da aba `VISITAS` (nesta ordem): `ID · Registrado em · Data · Horário · Empreendimento · Cidade · Tipo · Nome do cliente · CPF · Telefone · Imobiliária · Corretor · Gerente de vendas · Excluída · Token`. CPF e telefone gravados só com os dígitos.
- CPF válido: 11 dígitos, dígitos verificadores corretos, não é sequência repetida. Telefone válido: 10 ou 11 dígitos, DDD (2 primeiros) ≥ 11.
- Mensagens dos campos: cliente "Informe o nome do cliente.", cpf "CPF inválido. Confira os números.", telefone "Telefone com DDD, 10 ou 11 números.", data "Informe a data.", hora "Informe o horário.", imobiliaria "Informe a imobiliária.", corretor "Informe o nome do corretor.".
- Textos livres: `trim`, espaços repetidos viram um só, máximo 80 caracteres. Neutralização de fórmula ao gravar e no CSV.
- CPF e telefone nunca vão para `Logger.log` nem para mensagens de erro.
- Todo texto vindo da API vai para o DOM com `textContent`, nunca `innerHTML`.
- CPFs de teste/demo: só os de exemplo amplamente conhecidos `52998224725`, `11144477735`, `12345678909`, `98765432100`.
- Commits `tipo(visitas): ...`, sempre com trailer `Co-Authored-By:`. `git add` só dos arquivos da tarefa. A árvore de trabalho tem mudanças do usuário (`.claude/*`, `.DS_Store`, `.impeccable/`) que **nunca** entram em commit.

## File Structure

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `assets/visitas.js` | modificar | + CPF/telefone/máscaras/primeiroNome/validarVisita/resumirVisita; `detalhe` e CSV com os campos novos; remove `validarFormulario` |
| `tests/visitas-regras.test.js` | modificar | testes das regras novas; sai o de `validarFormulario` |
| `tests/visitas-dashboard.test.js` | modificar | CSV com as colunas novas |
| `tests/fixtures/visitas.json` | modificar | campos novos |
| `docs/apps-script-visitas.gs` | modificar | colunas, validação, resumo, cpfRepetido, 3 listas de sugestões, senha ≥ 12 |
| `tests/visitas-gs.test.js` | reescrever | testes da v2 + paridade CPF/telefone com o cliente |
| `assets/visitas-api.js` | modificar | modo demo no contrato v2 |
| `visitas-recepcao.html` | modificar | Passo 1 só stand; cards abrem `<dialog>`; markup e CSS do popup |
| `assets/visitas-recepcao-app.js` | reescrever | lógica do popup |
| `visitas-recepcao-adm.html` | modificar | colunas da tabela de lançamentos + aviso de dados pessoais |
| `assets/visitas-adm-app.js` | modificar | `renderRecentes` com os campos novos |
| `README.md` | modificar | descrição dos campos |

---

### Task 1: Regras puras do cliente em `assets/visitas.js`

**Files:**
- Modify: `assets/visitas.js`
- Modify: `tests/visitas-regras.test.js`, `tests/visitas-dashboard.test.js`, `tests/fixtures/visitas.json`

**Interfaces:**
- Produces (exportados no `api`):
  - `soDigitos(s) → string`, `cpfValido(s) → boolean`, `telefoneValido(s) → boolean`
  - `mascaraCpf(s) → string`: parcial enquanto digita, máximo `000.000.000-00`
  - `mascaraTelefone(s) → string`: parcial, `(00) 0000-0000` ou `(00) 00000-0000`
  - `formatarCpf(d)`, `formatarTelefone(d)`: máscara quando o número está completo, senão os próprios dígitos
  - `primeiroNome(s) → string`
  - `validarVisita(d) → { ok, erros: { [campo]: mensagem }, primeiro: campo|null }`, com campos em ordem: empreendimento, tipo, cliente, cpf, telefone, data, hora, imobiliaria, corretor
  - `resumirVisita(v) → { id, data, hora, empreendimento, tipo, primeiroNome, imobiliaria, corretor }`
  - `detalhe(v)`: `imob` → `imobiliaria · corretor`; demais → `corretor`, ou "Corretor não informado"
  - `gerarCSV`: colunas `Data;Horário;Empreendimento;Cidade;Tipo;Cliente;CPF;Telefone;Imobiliária;Corretor;Gerente de vendas`
  - **Removido:** `validarFormulario`

- [ ] **Step 1: Update the fixture**

Replace `tests/fixtures/visitas.json` with (same ids/dates/tipos/imobiliárias as before, so the dashboard tests keep their expectations):

```json
[
  { "id": "V1", "data": "2026-10-07", "hora": "09:10", "empreendimento": "Alta Vista Mangará", "cidade": "Campinas", "tipo": "esp", "cliente": "Cliente Teste Um", "cpf": "52998224725", "telefone": "19998765432", "imobiliaria": "", "corretor": "Corretor Teste", "gerente": "" },
  { "id": "V2", "data": "2026-10-07", "hora": "10:05", "empreendimento": "Alta Vista Mangará", "cidade": "Campinas", "tipo": "imob", "cliente": "Cliente Teste Dois", "cpf": "11144477735", "telefone": "1932458890", "imobiliaria": "Imobiliária Ápice", "corretor": "Corretor Teste", "gerente": "Gerente Teste" },
  { "id": "V3", "data": "2026-10-07", "hora": "21:30", "empreendimento": "Village Park", "cidade": "Ribeirão Preto", "tipo": "house", "cliente": "Cliente Teste Três", "cpf": "12345678909", "telefone": "16998112233", "imobiliaria": "", "corretor": "Corretor House Teste", "gerente": "" },
  { "id": "V4", "data": "2026-10-08", "hora": "07:45", "empreendimento": "Village Park", "cidade": "Ribeirão Preto", "tipo": "imob", "cliente": "Cliente Teste Quatro", "cpf": "98765432100", "telefone": "16996541020", "imobiliaria": "imobiliaria apice ", "corretor": "Corretor Teste", "gerente": "" },
  { "id": "V5", "data": "2026-10-08", "hora": "14:00", "empreendimento": "Alta Vista Mangará", "cidade": "Campinas", "tipo": "imob", "cliente": "Cliente Teste Cinco", "cpf": "52998224725", "telefone": "19998765432", "imobiliaria": "Imobiliária Ápice", "corretor": "Corretor Teste", "gerente": "" },
  { "id": "V6", "data": "2026-10-09", "hora": "11:20", "empreendimento": "Alta Vista Mangará", "cidade": "Campinas", "tipo": "imob", "cliente": "Cliente Teste Seis", "cpf": "11144477735", "telefone": "1932458890", "imobiliaria": "Imóveis Beta", "corretor": "Corretor Teste", "gerente": "" },
  { "id": "V7", "data": "2026-10-09", "hora": "11:50", "empreendimento": "Conquista Vila da Mata", "cidade": "Sorocaba", "tipo": "esp", "cliente": "Cliente Teste Sete", "cpf": "12345678909", "telefone": "15998765432", "imobiliaria": "", "corretor": "Corretor Teste", "gerente": "" },
  { "id": "V8", "data": "2026-10-09", "hora": "15:15", "empreendimento": "Alta Vista Mangará", "cidade": "Campinas", "tipo": "house", "cliente": "Cliente Teste Oito", "cpf": "98765432100", "telefone": "19998765432", "imobiliaria": "", "corretor": "Corretor House Teste", "gerente": "Gerente Teste" }
]
```

- [ ] **Step 2: Write the failing tests**

In `tests/visitas-regras.test.js`:
- **Delete** the whole test `'validarFormulario aponta o primeiro campo que falta'`.
- **Replace** the test `'detalhe de cada tipo para as listas'` with:

```js
test('detalhe de cada tipo para as listas', () => {
  assert.equal(V.detalhe({ tipo: 'esp', corretor: 'Rui' }), 'Rui');
  assert.equal(V.detalhe({ tipo: 'house', corretor: '' }), 'Corretor não informado');
  assert.equal(V.detalhe({ tipo: 'house', corretor: 'Ana' }), 'Ana');
  assert.equal(V.detalhe({ tipo: 'imob', imobiliaria: 'Imob Ápice', corretor: '' }), 'Imob Ápice');
  assert.equal(V.detalhe({ tipo: 'imob', imobiliaria: 'Imob Ápice', corretor: 'Rui' }), 'Imob Ápice · Rui');
});
```

- **Append** at the end:

```js
test('cpfValido confere dígitos verificadores e recusa sequências', () => {
  ['52998224725', '529.982.247-25', '11144477735', '12345678909', '98765432100'].forEach((c) => assert.equal(V.cpfValido(c), true, c));
  ['52998224724', '11111111111', '000.000.000-00', '1234567890', '123456789012', '', null, 'abc'].forEach((c) => assert.equal(V.cpfValido(c), false, String(c)));
});

test('telefoneValido exige DDD e 10 ou 11 dígitos', () => {
  ['(19) 98765-4321', '19987654321', '(19) 3245-8890', '1932458890'].forEach((t) => assert.equal(V.telefoneValido(t), true, t));
  ['987654321', '199876543210', '(09) 98765-4321', '', null].forEach((t) => assert.equal(V.telefoneValido(t), false, String(t)));
});

test('máscaras de CPF e telefone enquanto digita', () => {
  assert.equal(V.mascaraCpf('529'), '529');
  assert.equal(V.mascaraCpf('5299'), '529.9');
  assert.equal(V.mascaraCpf('5299822'), '529.982.2');
  assert.equal(V.mascaraCpf('5299822472'), '529.982.247-2');
  assert.equal(V.mascaraCpf('52998224725999'), '529.982.247-25');
  assert.equal(V.mascaraCpf('529.982.247-25'), '529.982.247-25');
  assert.equal(V.mascaraTelefone(''), '');
  assert.equal(V.mascaraTelefone('1'), '(1');
  assert.equal(V.mascaraTelefone('199'), '(19) 9');
  assert.equal(V.mascaraTelefone('1932458890'), '(19) 3245-8890');
  assert.equal(V.mascaraTelefone('19987654321'), '(19) 98765-4321');
  assert.equal(V.mascaraTelefone('199876543219'), '(19) 98765-4321');
});

test('formatarCpf e formatarTelefone só mascaram números completos', () => {
  assert.equal(V.formatarCpf('52998224725'), '529.982.247-25');
  assert.equal(V.formatarCpf('5299'), '5299');
  assert.equal(V.formatarTelefone('1932458890'), '(19) 3245-8890');
  assert.equal(V.formatarTelefone('19987654321'), '(19) 98765-4321');
  assert.equal(V.formatarTelefone('123'), '123');
  assert.equal(V.formatarTelefone(undefined), '');
});

test('primeiroNome', () => {
  assert.equal(V.primeiroNome('  Mariana   Souza Lima '), 'Mariana');
  assert.equal(V.primeiroNome(''), '');
  assert.equal(V.primeiroNome(undefined), '');
});

test('validarVisita lista todos os erros e aponta o primeiro', () => {
  const ok = {
    empreendimento: 'Alta Vista Mangará', tipo: 'esp', cliente: 'Mariana Souza', cpf: '529.982.247-25',
    telefone: '(19) 98765-4321', data: '2026-10-09', hora: '14:35', corretor: 'Rui', gerente: ''
  };
  assert.deepEqual(V.validarVisita(ok), { ok: true, erros: {}, primeiro: null });
  const r = V.validarVisita({ ...ok, cliente: ' ', cpf: '529.982.247-2', corretor: '' });
  assert.equal(r.ok, false);
  assert.equal(r.primeiro, 'cliente');
  assert.deepEqual(Object.keys(r.erros), ['cliente', 'cpf', 'corretor']);
  assert.equal(r.erros.cpf, 'CPF inválido. Confira os números.');
  assert.equal(V.validarVisita({ ...ok, tipo: 'imob' }).primeiro, 'imobiliaria');
  assert.equal(V.validarVisita({ ...ok, tipo: 'imob', imobiliaria: 'Imob Ápice' }).ok, true);
  assert.equal(V.validarVisita({ ...ok, tipo: 'house', imobiliaria: '' }).ok, true);
  assert.equal(V.validarVisita({ ...ok, telefone: '98765-4321' }).primeiro, 'telefone');
  assert.equal(V.validarVisita({ ...ok, tipo: 'xyz' }).primeiro, 'tipo');
  assert.equal(V.validarVisita({ ...ok, hora: '9:5' }).primeiro, 'hora');
});

test('resumirVisita não leva CPF, telefone, nome completo nem gerente', () => {
  const r = V.resumirVisita({
    id: 'V1', data: '2026-10-09', hora: '14:35', empreendimento: 'Alta Vista Mangará', cidade: 'Campinas', tipo: 'imob',
    cliente: 'Mariana Souza Lima', cpf: '52998224725', telefone: '19987654321', imobiliaria: 'Imob Ápice', corretor: 'Rui', gerente: 'Gil'
  });
  assert.deepEqual(r, {
    id: 'V1', data: '2026-10-09', hora: '14:35', empreendimento: 'Alta Vista Mangará', tipo: 'imob',
    primeiroNome: 'Mariana', imobiliaria: 'Imob Ápice', corretor: 'Rui'
  });
});
```

In `tests/visitas-dashboard.test.js`, **replace** the tests `'gerarCSV: BOM, separador ;, ordem cronológica, aspas e neutralização'` and `'gerarCSV vazio tem só o cabeçalho'` with:

```js
const CABECALHO_CSV = 'Data;Horário;Empreendimento;Cidade;Tipo;Cliente;CPF;Telefone;Imobiliária;Corretor;Gerente de vendas';

test('gerarCSV: BOM, separador ;, ordem cronológica, aspas, neutralização e CPF/telefone formatados', () => {
  const visitas = [
    { data: '2026-10-09', hora: '11:50', empreendimento: 'Conquista Vila da Mata', cidade: 'Sorocaba', tipo: 'esp', cliente: 'Ana Lima', cpf: '52998224725', telefone: '15998765432', imobiliaria: '', corretor: 'Rui', gerente: '' },
    { data: '2026-10-08', hora: '14:00', empreendimento: 'Alta Vista Mangará', cidade: 'Campinas', tipo: 'imob', cliente: '=HYPERLINK("x")', cpf: '11144477735', telefone: '1932458890', imobiliaria: 'Imob; Centro', corretor: 'Bia', gerente: 'Gil' }
  ];
  const esperado = '﻿' + CABECALHO_CSV + '\r\n' +
    '08/10/2026;14:00;Alta Vista Mangará;Campinas;Imobiliária;"\'=HYPERLINK(""x"")";111.444.777-35;(19) 3245-8890;"Imob; Centro";Bia;Gil\r\n' +
    '09/10/2026;11:50;Conquista Vila da Mata;Sorocaba;Espontânea;Ana Lima;529.982.247-25;(15) 99876-5432;;Rui;\r\n';
  assert.equal(V.gerarCSV(visitas), esperado);
});

test('gerarCSV vazio tem só o cabeçalho', () => {
  assert.equal(V.gerarCSV([]), '﻿' + CABECALHO_CSV + '\r\n');
});
```

(Write the BOM as the escape `'﻿'`, not an invisible literal character.)

- [ ] **Step 3: Run tests to verify they fail**

Run: `node --test tests/visitas-regras.test.js tests/visitas-dashboard.test.js`
Expected: FAIL (`V.cpfValido is not a function`, CSV mismatch).

- [ ] **Step 4: Implement in `assets/visitas.js`**

a) Replace the function `detalhe` with:

```js
  function detalhe(v) {
    if (v.tipo === 'imob') return v.imobiliaria + (v.corretor ? ' · ' + v.corretor : '');
    return v.corretor || 'Corretor não informado';
  }
```

b) Replace the whole section `/* ---------- formulario da recepcao (spec 5.1) ---------- */` (the `validarFormulario` function) with:

```js
  /* ---------- cliente: CPF, telefone, nome (spec 13.1) ---------- */
  function soDigitos(s) { return String(s === null || s === undefined ? '' : s).replace(/\D/g, ''); }
  function cpfValido(s) {
    var d = soDigitos(s);
    if (d.length !== 11 || /^(\d)\1{10}$/.test(d)) return false;
    for (var t = 9; t < 11; t++) {
      var soma = 0;
      for (var i = 0; i < t; i++) soma += Number(d.charAt(i)) * (t + 1 - i);
      if (((soma * 10) % 11) % 10 !== Number(d.charAt(t))) return false;
    }
    return true;
  }
  function telefoneValido(s) {
    var d = soDigitos(s);
    return (d.length === 10 || d.length === 11) && Number(d.slice(0, 2)) >= 11;
  }
  function mascaraCpf(s) {
    var d = soDigitos(s).slice(0, 11), out = '';
    for (var i = 0; i < d.length; i++) {
      if (i === 3 || i === 6) out += '.';
      if (i === 9) out += '-';
      out += d.charAt(i);
    }
    return out;
  }
  function mascaraTelefone(s) {
    var d = soDigitos(s).slice(0, 11);
    if (!d) return '';
    if (d.length <= 2) return '(' + d;
    var resto = d.slice(2), corte = d.length === 11 ? 5 : 4;
    if (resto.length <= corte) return '(' + d.slice(0, 2) + ') ' + resto;
    return '(' + d.slice(0, 2) + ') ' + resto.slice(0, corte) + '-' + resto.slice(corte);
  }
  function formatarCpf(d) { d = soDigitos(d); return d.length === 11 ? mascaraCpf(d) : d; }
  function formatarTelefone(d) { d = soDigitos(d); return d.length === 10 || d.length === 11 ? mascaraTelefone(d) : d; }
  function primeiroNome(s) { return normalizarTexto(s).split(' ')[0] || ''; }

  /* ---------- popup da recepcao (spec 13.1) ---------- */
  var ORDEM_CAMPOS = ['empreendimento', 'tipo', 'cliente', 'cpf', 'telefone', 'data', 'hora', 'imobiliaria', 'corretor'];
  var MENSAGENS_CAMPO = {
    empreendimento: 'Escolha o empreendimento.',
    tipo: 'Escolha o tipo de visita.',
    cliente: 'Informe o nome do cliente.',
    cpf: 'CPF inválido. Confira os números.',
    telefone: 'Telefone com DDD, 10 ou 11 números.',
    data: 'Informe a data.',
    hora: 'Informe o horário.',
    imobiliaria: 'Informe a imobiliária.',
    corretor: 'Informe o nome do corretor.'
  };
  function validarVisita(d) {
    var falha = {
      empreendimento: !normalizarTexto(d.empreendimento),
      tipo: !tipoValido(d.tipo),
      cliente: !normalizarTexto(d.cliente),
      cpf: !cpfValido(d.cpf),
      telefone: !telefoneValido(d.telefone),
      data: !/^\d{4}-\d{2}-\d{2}$/.test(d.data || ''),
      hora: !/^\d{2}:\d{2}$/.test(d.hora || ''),
      imobiliaria: d.tipo === 'imob' && !normalizarTexto(d.imobiliaria),
      corretor: !normalizarTexto(d.corretor)
    };
    var erros = {}, primeiro = null;
    ORDEM_CAMPOS.forEach(function (c) {
      if (!falha[c]) return;
      erros[c] = MENSAGENS_CAMPO[c];
      if (!primeiro) primeiro = c;
    });
    return { ok: !primeiro, erros: erros, primeiro: primeiro };
  }
  /* o que pode sair para a pagina publica: sem CPF, telefone, nome completo e gerente */
  function resumirVisita(v) {
    return {
      id: v.id, data: v.data, hora: v.hora, empreendimento: v.empreendimento, tipo: v.tipo,
      primeiroNome: primeiroNome(v.cliente), imobiliaria: v.imobiliaria || '', corretor: v.corretor || ''
    };
  }
```

c) In the CSV section, replace `CSV_COLUNAS` and the row inside `gerarCSV`:

```js
  var CSV_COLUNAS = ['Data', 'Horário', 'Empreendimento', 'Cidade', 'Tipo', 'Cliente', 'CPF', 'Telefone', 'Imobiliária', 'Corretor', 'Gerente de vendas'];
```

```js
      linhas.push([
        dataBr(v.data), v.hora, v.empreendimento, v.cidade, TIPOS[v.tipo] ? TIPOS[v.tipo].nome : v.tipo,
        v.cliente, formatarCpf(v.cpf), formatarTelefone(v.telefone), v.imobiliaria, v.corretor, v.gerente
      ].map(celulaCSV).join(';'));
```

Also make the BOM the escape `'﻿'` in `gerarCSV` if it is currently an invisible literal character.

d) In the `api` object, replace `validarFormulario: validarFormulario,` with:

```js
    soDigitos: soDigitos,
    cpfValido: cpfValido,
    telefoneValido: telefoneValido,
    mascaraCpf: mascaraCpf,
    mascaraTelefone: mascaraTelefone,
    formatarCpf: formatarCpf,
    formatarTelefone: formatarTelefone,
    primeiroNome: primeiroNome,
    validarVisita: validarVisita,
    resumirVisita: resumirVisita,
```

- [ ] **Step 5: Run the full suite**

Run: `node --test tests/*.test.js`
Expected: PASS for regras and dashboard. `tests/visitas-gs.test.js` must still pass, because it doesn't use the removed function.

- [ ] **Step 6: Commit**

```bash
git add assets/visitas.js tests/visitas-regras.test.js tests/visitas-dashboard.test.js tests/fixtures/visitas.json
git commit -m "feat(visitas): regras de CPF, telefone e validacao da visita completa

Co-Authored-By: <seu modelo> <noreply@anthropic.com>"
```

---

### Task 2: Web App v2 (`docs/apps-script-visitas.gs`)

**Files:**
- Modify: `docs/apps-script-visitas.gs`
- Rewrite: `tests/visitas-gs.test.js`

**Interfaces:**
- Consumes: `assets/visitas.js` (`cpfValido`, `telefoneValido`, `resumirVisita`, `listaEmpreendimentos`) for parity tests
- Produces: HTTP contract in Global Constraints. Pure functions tested in Node:
  - `visValidar_(req, hoje, agoraMin) → visita sem id`
  - `visDeLinha_(l, ix) → completa`
  - `visResumo_(v)`
  - `visCpfRepetido_(linhas, ix, v) → boolean`
  - `visSugestoes_(linhas, ix, desde, coluna)`
  - `visCpfValido_`, `visTelefoneValido_`, `visDigitos_`, `visPrimeiroNome_`

- [ ] **Step 1: Write the failing tests**

Replace the whole content of `tests/visitas-gs.test.js` with:

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
const base = {
  empreendimento: 'Alta Vista Mangará', data: HOJE, hora: '14:35', tipo: 'esp',
  cliente: '  Mariana   Souza Lima ', cpf: '529.982.247-25', telefone: '(19) 98765-4321', corretor: 'Rui', gerente: ''
};
const recusa = (campo) => (e) => e.codigo === 'invalido' && e.campo === campo;

test('lista de empreendimentos do .gs bate com a do config.js', () => {
  const cfg = carregar('assets/config.js', { window: {} });
  assert.deepEqual(plano(gs.VISITAS_EMPREENDIMENTOS), V.listaEmpreendimentos(cfg.window.CITIES));
});

test('visValidar_ devolve a visita completa normalizada, com cidade do servidor e só dígitos', () => {
  const v = plano(gs.visValidar_({ ...base, cidade: 'Outra', imobiliaria: 'Ignorada' }, HOJE, AGORA));
  assert.deepEqual(v, {
    empreendimento: 'Alta Vista Mangará', cidade: 'Campinas', data: HOJE, hora: '14:35', tipo: 'esp',
    cliente: 'Mariana Souza Lima', cpf: '52998224725', telefone: '19987654321', imobiliaria: '', corretor: 'Rui', gerente: ''
  });
});

test('visValidar_ recusa empreendimento e tipo fora da lista', () => {
  assert.throws(() => gs.visValidar_({ ...base, empreendimento: 'Outro' }, HOJE, AGORA), recusa('empreendimento'));
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'xyz' }, HOJE, AGORA), recusa('tipo'));
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'constructor' }, HOJE, AGORA), recusa('tipo'));
});

test('visValidar_ limita data e horário como na v1', () => {
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-10-10' }, HOJE, AGORA), recusa('data'));
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-10-01' }, HOJE, AGORA), recusa('data'));
  assert.throws(() => gs.visValidar_({ ...base, data: '2026-02-30' }, HOJE, AGORA), recusa('data'));
  assert.equal(gs.visValidar_({ ...base, data: '2026-10-02' }, HOJE, AGORA).data, '2026-10-02');
  assert.throws(() => gs.visValidar_({ ...base, hora: '25:00' }, HOJE, AGORA), recusa('hora'));
  assert.throws(() => gs.visValidar_({ ...base, hora: '14:41' }, HOJE, AGORA), recusa('hora'));
  assert.equal(gs.visValidar_({ ...base, hora: '14:40' }, HOJE, AGORA).hora, '14:40');
});

test('visValidar_ exige cliente, CPF válido, telefone válido e corretor', () => {
  assert.throws(() => gs.visValidar_({ ...base, cliente: '  ' }, HOJE, AGORA), recusa('cliente'));
  assert.throws(() => gs.visValidar_({ ...base, cpf: '529.982.247-24' }, HOJE, AGORA), recusa('cpf'));
  assert.throws(() => gs.visValidar_({ ...base, cpf: '111.111.111-11' }, HOJE, AGORA), recusa('cpf'));
  assert.throws(() => gs.visValidar_({ ...base, telefone: '98765-4321' }, HOJE, AGORA), recusa('telefone'));
  assert.throws(() => gs.visValidar_({ ...base, telefone: '(09) 98765-4321' }, HOJE, AGORA), recusa('telefone'));
  assert.throws(() => gs.visValidar_({ ...base, corretor: '' }, HOJE, AGORA), recusa('corretor'));
  assert.equal(gs.visValidar_({ ...base, telefone: '(19) 3245-8890' }, HOJE, AGORA).telefone, '1932458890');
  assert.equal(gs.visValidar_({ ...base, gerente: ' Gil  Souza ' }, HOJE, AGORA).gerente, 'Gil Souza');
});

test('visValidar_ exige imobiliária só no tipo imob', () => {
  assert.throws(() => gs.visValidar_({ ...base, tipo: 'imob', imobiliaria: '   ' }, HOJE, AGORA), recusa('imobiliaria'));
  assert.equal(gs.visValidar_({ ...base, tipo: 'imob', imobiliaria: ' Imob   Ápice ' }, HOJE, AGORA).imobiliaria, 'Imob Ápice');
  assert.equal(gs.visValidar_({ ...base, tipo: 'house', imobiliaria: 'X' }, HOJE, AGORA).imobiliaria, '');
});

test('mensagens de erro de CPF e telefone não repetem o valor digitado', () => {
  try { gs.visValidar_({ ...base, cpf: '529.982.247-24' }, HOJE, AGORA); } catch (e) { assert.ok(!/529/.test(e.message)); }
  try { gs.visValidar_({ ...base, telefone: '98765-4321' }, HOJE, AGORA); } catch (e) { assert.ok(!/98765/.test(e.message)); }
});

test('CPF e telefone: mesmo resultado no cliente (visitas.js) e no servidor (.gs)', () => {
  const cpfs = ['52998224725', '529.982.247-25', '11144477735', '12345678909', '98765432100', '52998224724', '11111111111', '1234567890', '', 'abc'];
  cpfs.forEach((c) => assert.equal(gs.visCpfValido_(c), V.cpfValido(c), c));
  const tels = ['(19) 98765-4321', '1932458890', '987654321', '(09) 98765-4321', '199876543210', ''];
  tels.forEach((t) => assert.equal(gs.visTelefoneValido_(t), V.telefoneValido(t), t));
});

test('visNeutralizar_ e helpers de data', () => {
  assert.equal(gs.visNeutralizar_('=1+1'), "'=1+1");
  assert.equal(gs.visNeutralizar_('Imob'), 'Imob');
  assert.equal(gs.visSomarDias_('2026-10-01', -1), '2026-09-30');
  assert.equal(gs.visBrParaIso_('09/10/2026 14:35:00'), '2026-10-09');
  assert.equal(gs.visDataValida_('2026-02-29'), false);
});

function indice() { const ix = {}; gs.VIS_COLUNAS.forEach((n, i) => { ix[n] = i; }); return ix; }
function linha(campos) { return gs.VIS_COLUNAS.map((n) => (campos[n] !== undefined ? campos[n] : '')); }

test('VIS_COLUNAS na ordem da spec 13.2', () => {
  assert.deepEqual(plano(gs.VIS_COLUNAS), ['ID', 'Registrado em', 'Data', 'Horário', 'Empreendimento', 'Cidade', 'Tipo',
    'Nome do cliente', 'CPF', 'Telefone', 'Imobiliária', 'Corretor', 'Gerente de vendas', 'Excluída', 'Token']);
});

test('visDeLinha_ devolve a visita completa', () => {
  const l = linha({
    'ID': 'V1', 'Registrado em': '09/10/2026 14:35:00', 'Data': '09/10/2026', 'Horário': '14:30',
    'Empreendimento': 'Village Park', 'Cidade': 'Ribeirão Preto', 'Tipo': 'Imobiliária',
    'Nome do cliente': 'Mariana Souza', 'CPF': '52998224725', 'Telefone': '19987654321',
    'Imobiliária': 'Imob Ápice', 'Corretor': 'Rui', 'Gerente de vendas': 'Gil', 'Excluída': '0'
  });
  assert.deepEqual(plano(gs.visDeLinha_(l, indice())), {
    id: 'V1', data: '2026-10-09', hora: '14:30', empreendimento: 'Village Park', cidade: 'Ribeirão Preto', tipo: 'imob',
    cliente: 'Mariana Souza', cpf: '52998224725', telefone: '19987654321', imobiliaria: 'Imob Ápice', corretor: 'Rui', gerente: 'Gil'
  });
});

test('visResumo_ é igual ao resumo do cliente e não expõe dados pessoais', () => {
  const v = {
    id: 'V1', data: '2026-10-09', hora: '14:30', empreendimento: 'Village Park', cidade: 'Ribeirão Preto', tipo: 'imob',
    cliente: 'Mariana Souza', cpf: '52998224725', telefone: '19987654321', imobiliaria: 'Imob Ápice', corretor: 'Rui', gerente: 'Gil'
  };
  const r = plano(gs.visResumo_(v));
  assert.deepEqual(r, V.resumirVisita(v));
  const texto = JSON.stringify(r);
  ['52998224725', '19987654321', 'Souza', 'Gil'].forEach((s) => assert.ok(!texto.includes(s), s));
});

test('visCpfRepetido_: mesmo CPF, mesmo stand e mesma data, só linhas ativas', () => {
  const ix = indice();
  const linhas = [
    linha({ 'CPF': '52998224725', 'Empreendimento': 'Village Park', 'Data': '09/10/2026', 'Excluída': '0' }),
    linha({ 'CPF': '11144477735', 'Empreendimento': 'Village Park', 'Data': '09/10/2026', 'Excluída': '1' })
  ];
  const v = (cpf, emp, data) => ({ cpf, empreendimento: emp, data });
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('52998224725', 'Village Park', '2026-10-09')), true);
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('52998224725', 'Village Gaia', '2026-10-09')), false);
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('52998224725', 'Village Park', '2026-10-08')), false);
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('11144477735', 'Village Park', '2026-10-09')), false);
  assert.equal(gs.visCpfRepetido_([], ix, v('52998224725', 'Village Park', '2026-10-09')), false);
});

test('visSugestoes_ por coluna: agrupa, ignora excluídas e antigas, ordena', () => {
  const linhas = [
    linha({ 'Registrado em': '08/10/2026 10:00:00', 'Imobiliária': 'Imobiliária Ápice', 'Corretor': 'Rui', 'Excluída': '0' }),
    linha({ 'Registrado em': '08/10/2026 11:00:00', 'Imobiliária': 'Imobiliária Ápice', 'Corretor': 'rui', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:00:00', 'Imobiliária': 'imobiliaria apice', 'Corretor': 'Bia', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:30:00', 'Imobiliária': 'Beta Imóveis', 'Corretor': 'Zeca', 'Excluída': '1' }),
    linha({ 'Registrado em': '01/01/2026 09:00:00', 'Imobiliária': 'Antiga', 'Corretor': 'Antigo', 'Excluída': '0' }),
    linha({ 'Registrado em': '09/10/2026 09:50:00', 'Imobiliária': 'constructor', 'Corretor': '__proto__', 'Excluída': '0' })
  ];
  assert.deepEqual(plano(gs.visSugestoes_(linhas, indice(), '2026-07-11', 'Imobiliária')), ['constructor', 'Imobiliária Ápice']);
  assert.deepEqual(plano(gs.visSugestoes_(linhas, indice(), '2026-07-11', 'Corretor')), ['__proto__', 'Bia', 'Rui']);
  assert.equal(({}).qtd, undefined);
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test tests/visitas-gs.test.js`
Expected: FAIL (new functions missing, `VIS_COLUNAS` differs).

- [ ] **Step 3: Implement in `docs/apps-script-visitas.gs`**

a) Replace `VIS_COLUNAS` with:

```js
var VIS_COLUNAS = ['ID', 'Registrado em', 'Data', 'Horário', 'Empreendimento', 'Cidade', 'Tipo',
  'Nome do cliente', 'CPF', 'Telefone', 'Imobiliária', 'Corretor', 'Gerente de vendas', 'Excluída', 'Token'];
var VIS_MIN_SENHA = 12;
```

b) Replace `configurarSenhaVisitas` with:

```js
function configurarSenhaVisitas() {
  if (!VIS_SENHA_INICIAL) throw new Error('Preencha VIS_SENHA_INICIAL so no editor antes de executar.');
  /* spec 13.5: o dashboard guarda dado pessoal, a senha precisa ser forte */
  if (VIS_SENHA_INICIAL.length < VIS_MIN_SENHA) throw new Error('A senha precisa ter pelo menos ' + VIS_MIN_SENHA + ' caracteres.');
  PropertiesService.getScriptProperties().setProperty(VIS_PROP_SENHA, VIS_SENHA_INICIAL);
  Logger.log('Senha do /visitas-recepcao-adm configurada. Volte VIS_SENHA_INICIAL para \'\'.');
}
```

c) After `visCodigoTipo_`, add:

```js
/* spec 13.1: mesmas regras de assets/visitas.js (paridade testada) */
function visDigitos_(s) { return String(s === null || s === undefined ? '' : s).replace(/\D/g, ''); }
function visCpfValido_(s) {
  var d = visDigitos_(s);
  if (d.length !== 11 || /^(\d)\1{10}$/.test(d)) return false;
  for (var t = 9; t < 11; t++) {
    var soma = 0;
    for (var i = 0; i < t; i++) soma += Number(d.charAt(i)) * (t + 1 - i);
    if (((soma * 10) % 11) % 10 !== Number(d.charAt(t))) return false;
  }
  return true;
}
function visTelefoneValido_(s) {
  var d = visDigitos_(s);
  return (d.length === 10 || d.length === 11) && Number(d.slice(0, 2)) >= 11;
}
function visPrimeiroNome_(s) { return visTexto_(s).split(' ')[0] || ''; }
```

d) Replace the whole `visValidar_` with:

```js
/* spec 4.2 + 13.3: o servidor e a autoridade */
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
  var cliente = visTexto_(req.cliente);
  if (!cliente) throw new VisFalha('invalido', 'Informe o nome do cliente.', 'cliente');
  if (!visCpfValido_(req.cpf)) throw new VisFalha('invalido', 'CPF inválido. Confira os números.', 'cpf');
  if (!visTelefoneValido_(req.telefone)) throw new VisFalha('invalido', 'Telefone com DDD, 10 ou 11 números.', 'telefone');
  var imobiliaria = tipo === 'imob' ? visTexto_(req.imobiliaria) : '';
  if (tipo === 'imob' && !imobiliaria) throw new VisFalha('invalido', 'Informe a imobiliária.', 'imobiliaria');
  var corretor = visTexto_(req.corretor);
  if (!corretor) throw new VisFalha('invalido', 'Informe o nome do corretor.', 'corretor');
  return {
    empreendimento: emp.nome, cidade: emp.cidade, data: data, hora: hora, tipo: tipo,
    cliente: cliente, cpf: visDigitos_(req.cpf), telefone: visDigitos_(req.telefone),
    imobiliaria: imobiliaria, corretor: corretor, gerente: visTexto_(req.gerente)
  };
}
```

e) Replace `visDeLinha_` with the following, and add `visResumo_` and `visCpfRepetido_` right after it:

```js
function visDeLinha_(l, ix) {
  return {
    id: String(l[ix['ID']]),
    data: visBrParaIso_(l[ix['Data']]),
    hora: String(l[ix['Horário']]).trim(),
    empreendimento: String(l[ix['Empreendimento']]),
    cidade: String(l[ix['Cidade']]),
    tipo: visCodigoTipo_(l[ix['Tipo']]),
    cliente: String(l[ix['Nome do cliente']]),
    cpf: visDigitos_(l[ix['CPF']]),
    telefone: visDigitos_(l[ix['Telefone']]),
    imobiliaria: String(l[ix['Imobiliária']]),
    corretor: String(l[ix['Corretor']]),
    gerente: String(l[ix['Gerente de vendas']])
  };
}

/* spec 13.3: so isto sai nas respostas publicas */
function visResumo_(v) {
  return {
    id: v.id, data: v.data, hora: v.hora, empreendimento: v.empreendimento, tipo: v.tipo,
    primeiroNome: visPrimeiroNome_(v.cliente), imobiliaria: v.imobiliaria || '', corretor: v.corretor || ''
  };
}

/* mesmo CPF, mesmo stand e mesma data, entre as linhas ativas */
function visCpfRepetido_(linhas, ix, v) {
  for (var i = 0; i < linhas.length; i++) {
    var l = linhas[i];
    if (!visAtiva_(l, ix)) continue;
    if (visDigitos_(l[ix['CPF']]) === v.cpf && String(l[ix['Empreendimento']]) === v.empreendimento &&
        visBrParaIso_(l[ix['Data']]) === v.data) return true;
  }
  return false;
}
```

f) Change `visSugestoes_` to take the column name. Its signature becomes `function visSugestoes_(linhas, ix, desde, coluna)`, and the line that reads the name becomes `var nome = visTexto_(l[ix[coluna]]), k = visChave_(nome);`. The rest of the function stays as it is.

g) In `visLer_`, also return the width. Add `largura: cab.largura,` to the returned object.

h) Replace `visRegistrar_` with:

```js
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
    'Nome do cliente': v.cliente,
    'CPF': v.cpf,
    'Telefone': v.telefone,
    'Imobiliária': v.imobiliaria,
    'Corretor': v.corretor,
    'Gerente de vendas': v.gerente,
    'Excluída': '0',
    'Token': visHash_(token)
  };
  var repetido = visComLock_(function () {
    var t = visLer_();
    var achou = visCpfRepetido_(t.linhas, t.indice, v);
    var linha = [];
    for (var i = 0; i < t.largura; i++) linha.push('');
    Object.keys(valores).forEach(function (nome) { linha[t.indice[nome]] = visNeutralizar_(valores[nome]); });
    /* formato texto: a planilha nao converte data/hora/CPF e mantem o valor exato */
    var faixa = t.aba.getRange(t.aba.getLastRow() + 1, 1, 1, t.largura);
    faixa.setNumberFormat('@');
    faixa.setValues([linha]);
    return achou;
  });
  return { visita: visResumo_(v), token: token, cpfRepetido: repetido };
}
```

i) In `visDia_`, change `visitas.push(v)` to `visitas.push(visResumo_(v))`. Replace the return with:

```js
  var desde = visSomarDias_(visHoje_(), -VIS_DIAS_SUGESTOES);
  return {
    visitas: visitas,
    sugestoes: {
      imobiliarias: visSugestoes_(t.linhas, ix, desde, 'Imobiliária'),
      corretores: visSugestoes_(t.linhas, ix, desde, 'Corretor'),
      gerentes: visSugestoes_(t.linhas, ix, desde, 'Gerente de vendas')
    }
  };
```

j) `visListar_` already returns `visDeLinha_` objects, which are now complete. No change.

k) Replace `testeVisitas` with (test data only, nothing real gets logged):

```js
function testeVisitas() {
  var hoje = visHoje_();
  var r = visRegistrar_({
    empreendimento: VISITAS_EMPREENDIMENTOS[0].nome, data: hoje,
    hora: Utilities.formatDate(new Date(), VIS_FUSO, 'HH:mm'), tipo: 'imob', imobiliaria: 'TESTE - pode ignorar',
    cliente: 'TESTE - pode ignorar', cpf: '52998224725', telefone: '19999999999', corretor: 'TESTE', gerente: ''
  });
  Logger.log('registrar: ' + JSON.stringify(r.visita) + ' cpfRepetido=' + r.cpfRepetido);
  var d = visDia_({ empreendimento: VISITAS_EMPREENDIMENTOS[0].nome, data: hoje });
  Logger.log('dia: ' + d.visitas.length + ' visita(s); sugestoes: ' + d.sugestoes.imobiliarias.length + ' imob, ' +
    d.sugestoes.corretores.length + ' corretor, ' + d.sugestoes.gerentes.length + ' gerente');
  Logger.log('excluir: ' + JSON.stringify(visExcluir_({ id: r.visita.id, token: r.token })));
  Logger.log('listar: ' + visListar_({ de: hoje, ate: hoje }).visitas.length + ' visita(s) ativas hoje');
}
```

l) In the header comment "COMO PUBLICAR", step 3: add "(mínimo de 12 caracteres)" after "a senha do dashboard".

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test tests/*.test.js`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/apps-script-visitas.gs tests/visitas-gs.test.js
git commit -m "feat(visitas): web app grava dados do cliente e responde resumo publico

Co-Authored-By: <seu modelo> <noreply@anthropic.com>"
```

---

### Task 3: Modo demonstração no contrato v2 (`assets/visitas-api.js`)

**Files:**
- Modify: `assets/visitas-api.js`

**Interfaces:**
- Consumes: `V.validarVisita`, `V.resumirVisita`, `V.soDigitos`, `V.normalizarTexto`, `V.chaveNome` (Task 1)
- Produces: in demo mode, the same responses as the Task 2 Web App: `registrar` → `{ok, visita (resumida), token, cpfRepetido}`, `dia` → `{ok, visitas (resumidas), sugestoes:{imobiliarias, corretores, gerentes}}`, `listar` → full visits.

- [ ] **Step 1: Replace the demo section**

In `assets/visitas-api.js`, replace everything from the comment `/* ---------- modo demonstracao ---------- */` up to just before `/* ---------- Web App (spec 4.1) ---------- */` with:

```js
  /* ---------- modo demonstracao ---------- */
  var IMOBS_DEMO = ['Imobiliária Exemplo A', 'Imobiliária Exemplo B', 'Imobiliária Exemplo C', 'Imobiliária Exemplo D'];
  var CORRETORES_DEMO = ['Corretor Exemplo 1', 'Corretor Exemplo 2', 'Corretor Exemplo 3'];
  var GERENTES_DEMO = ['Gerente Exemplo 1', 'Gerente Exemplo 2'];
  var CLIENTES_DEMO = [
    ['Cliente Exemplo Ana', '52998224725', '19998765432'],
    ['Cliente Exemplo Bruno', '11144477735', '1932458890'],
    ['Cliente Exemplo Carla', '12345678909', '16998112233'],
    ['Cliente Exemplo Diego', '98765432100', '15998765432']
  ];
  var memoria = null;
  var tokensDemo = {};

  function rnd(a, b, c) {
    var x = Math.sin(a * 127.1 + b * 311.7 + c * 74.7) * 43758.5453;
    return x - Math.floor(x);
  }
  function escolher(lista, r) { return lista[Math.floor(r * lista.length)]; }
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
          var cli = escolher(CLIENTES_DEMO, rnd(ei, d, 70 + k));
          seq++;
          out.push({
            id: 'D' + seq, data: data, hora: pad(Math.floor(min / 60)) + ':' + pad(min % 60),
            empreendimento: e.nome, cidade: e.cidade, tipo: tipo,
            cliente: cli[0], cpf: cli[1], telefone: cli[2],
            imobiliaria: tipo === 'imob' ? escolher(IMOBS_DEMO, rnd(ei, d, 50 + k)) : '',
            corretor: escolher(CORRETORES_DEMO, rnd(ei, d, 90 + k)),
            gerente: rnd(ei, d, 110 + k) < 0.6 ? escolher(GERENTES_DEMO, rnd(ei, d, 130 + k)) : ''
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
        var f = V.validarVisita(p);
        if (!f.ok) throw falha('invalido', f.erros[f.primeiro], f.primeiro);
        var emp = V.listaEmpreendimentos(raiz.CITIES || []).filter(function (e) { return e.nome === p.empreendimento; })[0];
        var v = {
          id: 'D' + Date.now(), data: p.data, hora: p.hora, empreendimento: p.empreendimento,
          cidade: emp ? emp.cidade : '', tipo: p.tipo,
          cliente: V.normalizarTexto(p.cliente), cpf: V.soDigitos(p.cpf), telefone: V.soDigitos(p.telefone),
          imobiliaria: p.tipo === 'imob' ? V.normalizarTexto(p.imobiliaria) : '',
          corretor: V.normalizarTexto(p.corretor), gerente: V.normalizarTexto(p.gerente)
        };
        var repetido = lista.some(function (x) { return x.cpf === v.cpf && x.empreendimento === v.empreendimento && x.data === v.data; });
        var token = 'demo-' + Math.random().toString(36).slice(2);
        lista.push(v);
        tokensDemo[v.id] = token;
        return { ok: true, visita: V.resumirVisita(v), token: token, cpfRepetido: repetido };
      }
      if (acao === 'dia') {
        return {
          ok: true,
          visitas: lista.filter(function (v) { return v.empreendimento === p.empreendimento && v.data === p.data; })
            .map(V.resumirVisita),
          sugestoes: { imobiliarias: IMOBS_DEMO.slice(), corretores: CORRETORES_DEMO.slice(), gerentes: GERENTES_DEMO.slice() }
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

```

- [ ] **Step 2: Check**

Run: `node --check assets/visitas-api.js && node --test tests/*.test.js`
Expected: no syntax error; PASS.

- [ ] **Step 3: Commit**

```bash
git add assets/visitas-api.js
git commit -m "feat(visitas): modo demonstracao com dados do cliente e resumo publico

Co-Authored-By: <seu modelo> <noreply@anthropic.com>"
```

---

### Task 4: Recepção com popup (`visitas-recepcao.html` + `assets/visitas-recepcao-app.js`)

**Files:**
- Modify: `visitas-recepcao.html`
- Rewrite: `assets/visitas-recepcao-app.js`

**Interfaces:**
- Consumes:
  - `V.validarVisita`, `V.mascaraCpf`, `V.mascaraTelefone`, `V.detalhe`, `V.totaisPorTipo`, `V.recentes`, `V.TIPOS`, `V.ORDEM_TIPOS`, `V.dataLocalIso`, `V.horaLocal`, `V.dataCurta`, `V.somarDias`, `V.listaEmpreendimentos`;
  - `VisitasAPI.criar`, with `registrar` → `{visita:{…primeiroNome}, token, cpfRepetido}` and `dia` → `{visitas, sugestoes}`.
- Produces: nothing for other tasks. Still uses `localStorage` `visitas.emp` and `visitas.tokens`.

Reference: canvas boards `Main`, `PopupImobiliaria`, `PopupCelular`.

- [ ] **Step 1: Edit `visitas-recepcao.html`**

a) **CSS.** Before `@media (max-width:700px)`, add:

```css
.faixa.aviso{background:var(--warn-bg);border-color:var(--warn-line);color:var(--warn)}
.tipo-dica{font-size:13px;color:var(--slate)}

/* ---------- popup (spec 13.1) ---------- */
.popup{width:min(560px,calc(100vw - 24px));max-height:calc(100vh - 24px);padding:0;border:1px solid var(--hair);border-radius:16px;box-shadow:0 18px 50px rgba(28,32,34,.22);color:var(--ink);background:var(--surface)}
.popup::backdrop{background:rgba(28,32,34,.45)}
.popup form{display:flex;flex-direction:column;max-height:calc(100vh - 24px)}
.p-cab{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;padding:1.2rem 1.35rem 1rem;border-bottom:1px solid var(--hair)}
.p-cab-txt{display:flex;flex-direction:column;gap:4px;min-width:0}
.p-cab h2{font-size:1.25rem;font-weight:700;letter-spacing:-.3px}
.p-corpo{padding:1.2rem 1.35rem;display:flex;flex-direction:column;gap:16px;overflow-y:auto}
.p-corpo .linha .campo{flex:1 1 200px}
.sub-step{font-size:12.5px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--red)}
.erro-campo{font-size:13px;font-weight:500;color:var(--err)}
.p-rodape{display:flex;flex-wrap:wrap-reverse;justify-content:flex-end;gap:10px;padding:1rem 1.35rem 1.2rem;border-top:1px solid var(--hair)}
.p-rodape .btn{flex:1 1 140px;min-height:48px}
.p-rodape .btn-p{flex:2 1 220px;width:auto;min-height:48px;font-size:1rem}
@media (max-width:600px){
  .popup{width:100%;max-width:100%;height:100%;max-height:100%;margin:0;border:0;border-radius:0}
  .popup form{height:100%;max-height:100%}
  .p-corpo{flex:1 1 auto}
}
```

b) **Passo 1.** Replace the whole first `.card` (the one with `Passo 1 · Stand, data e horário`) with:

```html
    <div class="card">
      <span class="step">Passo 1 · Stand</span>
      <label class="campo">
        <span class="lab">Empreendimento</span>
        <select class="inp" id="emp"></select>
      </label>
      <p class="dica">Fica salvo neste aparelho. Só troque se mudar de stand.</p>
    </div>
```

c) **Passo 2.** In the second `.card`:
- The `.tipos` div loses `role="radiogroup"` and gets `aria-label="Tipo de visita"`.
- Each `<button class="tipo" ...>` loses `role="radio"` and `aria-checked="false"` and gets `aria-haspopup="dialog"`. Keep `data-tipo`, the icons and the texts.
- Delete the `#extra-house` and `#extra-imob` blocks.
- After the `.tipos` div, add `<p class="tipo-dica">Toque no tipo para abrir o cadastro da visita.</p>`.

d) Delete the `<button ... id="registrar">…</button>` that sits after the Passo 2 card.

e) **Dialog.** Right before `<script src="assets/config.js"></script>`, add:

```html
<dialog class="popup" id="popup" aria-labelledby="p-titulo">
  <form id="p-form" novalidate>
    <div class="p-cab">
      <div class="p-cab-txt">
        <span class="lab rotulo-tipo"><span class="ponto" id="p-ponto"></span><span id="p-tipo"></span></span>
        <h2 id="p-titulo">Registrar visita</h2>
        <span class="dica" id="p-emp"></span>
      </div>
      <button type="button" class="btn btn-i" id="p-fechar" aria-label="Fechar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
      </button>
    </div>
    <div class="p-corpo">
      <span class="sub-step">Cliente</span>
      <label class="campo">
        <span class="lab">Nome do cliente</span>
        <input class="inp" id="f-cliente" type="text" maxlength="80" autocomplete="off" placeholder="Nome completo" aria-describedby="e-f-cliente">
        <span class="erro-campo" id="e-f-cliente" hidden></span>
      </label>
      <div class="linha">
        <label class="campo">
          <span class="lab">CPF</span>
          <input class="inp" id="f-cpf" type="text" inputmode="numeric" maxlength="14" autocomplete="off" placeholder="000.000.000-00" aria-describedby="e-f-cpf">
          <span class="erro-campo" id="e-f-cpf" hidden></span>
        </label>
        <label class="campo">
          <span class="lab">Telefone</span>
          <input class="inp" id="f-telefone" type="tel" inputmode="numeric" maxlength="15" autocomplete="off" placeholder="(00) 00000-0000" aria-describedby="e-f-telefone">
          <span class="erro-campo" id="e-f-telefone" hidden></span>
        </label>
      </div>
      <span class="sub-step">Visita</span>
      <div class="linha">
        <label class="campo">
          <span class="lab">Data</span>
          <input class="inp" id="f-data" type="date" aria-describedby="e-f-data">
          <span class="erro-campo" id="e-f-data" hidden></span>
        </label>
        <div class="campo">
          <label class="lab" for="f-hora">Horário</label>
          <div style="display:flex;gap:8px">
            <input class="inp" id="f-hora" type="time" style="flex:1 1 auto;min-width:0" aria-describedby="e-f-hora">
            <button type="button" class="btn" id="f-agora">Agora</button>
          </div>
          <span class="erro-campo" id="e-f-hora" hidden></span>
        </div>
      </div>
      <div id="bloco-imob" hidden>
        <label class="campo">
          <span class="lab">Imobiliária</span>
          <input class="inp" id="f-imob" type="text" maxlength="80" autocomplete="off" list="lista-imob" placeholder="Digite ou escolha" aria-describedby="e-f-imob">
          <datalist id="lista-imob"></datalist>
          <span class="erro-campo" id="e-f-imob" hidden></span>
        </label>
      </div>
      <div class="linha">
        <label class="campo">
          <span class="lab" id="rot-corretor">Nome do corretor</span>
          <input class="inp" id="f-corretor" type="text" maxlength="80" autocomplete="off" list="lista-corretor" placeholder="Nome do corretor" aria-describedby="e-f-corretor">
          <datalist id="lista-corretor"></datalist>
          <span class="erro-campo" id="e-f-corretor" hidden></span>
        </label>
        <label class="campo">
          <span class="lab">Gerente de vendas <span class="opc">(opcional)</span></span>
          <input class="inp" id="f-gerente" type="text" maxlength="80" autocomplete="off" list="lista-gerente" placeholder="Nome do gerente">
          <datalist id="lista-gerente"></datalist>
        </label>
      </div>
      <p class="erro-txt" id="p-erro" role="alert" hidden></p>
    </div>
    <div class="p-rodape">
      <button type="button" class="btn" id="p-cancelar">Cancelar</button>
      <button type="submit" class="btn btn-p" id="p-registrar"><span id="p-registrar-txt">Registrar visita</span></button>
    </div>
  </form>
</dialog>
```

f) In the header `<p>`, change the text to: `Escolha o stand e toque no tipo de visita para registrar o cliente.`

- [ ] **Step 2: Replace `assets/visitas-recepcao-app.js` entirely with:**

```js
/* ============================================================
   VISITAS DA RECEPCAO - interface de /visitas-recepcao
   ------------------------------------------------------------
   Stand (Passo 1), cards que abrem o popup de cadastro (Passo 2)
   e contador do dia. Regras em assets/visitas.js; API em
   assets/visitas-api.js.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md (secoes 5 e 13)
   ============================================================ */
(function () {
  'use strict';

  var V = window.Visitas;
  var api = window.VisitasAPI.criar({ url: window.VISITAS_APPS_SCRIPT_URL || '' });
  var EMPS = V.listaEmpreendimentos(window.CITIES || []);
  var CHAVE_EMP = 'visitas.emp';
  var CHAVE_TOKENS = 'visitas.tokens';
  var INTERVALO_DIA = 60000;
  var TITULO_TIPO = { esp: 'Espontânea', house: 'Agendada · Corretor house', imob: 'Imobiliária parceira' };
  var ROTULO_CORRETOR = { esp: 'Corretor que atendeu', house: 'Corretor house que agendou', imob: 'Corretor da imobiliária' };
  /* campo da API -> id do input no popup */
  var CAMPOS = {
    cliente: 'f-cliente', cpf: 'f-cpf', telefone: 'f-telefone', data: 'f-data',
    hora: 'f-hora', imobiliaria: 'f-imob', corretor: 'f-corretor'
  };
  var estado = { tipo: null, enviando: false, ultimo: null, timerFaixa: null, seqDia: 0, hojeAplicado: '' };

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

  /* ---------- stand ---------- */
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

  /* ---------- popup (spec 13.1) ---------- */
  function limparErro(id) {
    $(id).setAttribute('aria-invalid', 'false');
    $('e-' + id).textContent = '';
    $('e-' + id).hidden = true;
  }
  function limparErros() {
    Object.keys(CAMPOS).forEach(function (c) { limparErro(CAMPOS[c]); });
    $('p-erro').hidden = true;
  }
  function mostrarErro(campo, msg) {
    var id = CAMPOS[campo];
    if (!id) return false;
    $(id).setAttribute('aria-invalid', 'true');
    $('e-' + id).textContent = msg;
    $('e-' + id).hidden = false;
    return true;
  }
  function atualizarBotao() {
    $('p-registrar').disabled = estado.enviando;
    $('p-registrar-txt').textContent = estado.enviando ? 'Registrando…' : 'Registrar visita';
  }
  function aplicarLimitesData(h) {
    $('f-data').max = h;
    $('f-data').min = V.somarDias(h, -7);
  }

  function abrirPopup(tipo) {
    estado.tipo = tipo;
    $('p-tipo').textContent = TITULO_TIPO[tipo];
    $('p-ponto').style.background = V.TIPOS[tipo].cor;
    $('p-emp').textContent = $('emp').value;
    $('rot-corretor').textContent = ROTULO_CORRETOR[tipo];
    $('bloco-imob').hidden = tipo !== 'imob';
    ['f-cliente', 'f-cpf', 'f-telefone', 'f-imob', 'f-corretor', 'f-gerente'].forEach(function (id) { $(id).value = ''; });
    var h = hoje();
    aplicarLimitesData(h);
    $('f-data').value = h;
    $('f-hora').value = V.horaLocal(new Date());
    limparErros();
    estado.enviando = false;
    atualizarBotao();
    $('popup').showModal();
    $('f-cliente').focus();
  }
  function fecharPopup() {
    if ($('popup').open) $('popup').close();
  }

  function lerPopup() {
    return {
      empreendimento: $('emp').value, tipo: estado.tipo,
      cliente: $('f-cliente').value, cpf: $('f-cpf').value, telefone: $('f-telefone').value,
      data: $('f-data').value, hora: $('f-hora').value,
      imobiliaria: estado.tipo === 'imob' ? $('f-imob').value : '',
      corretor: $('f-corretor').value, gerente: $('f-gerente').value
    };
  }

  function registrar(ev) {
    if (ev) ev.preventDefault();
    if (estado.enviando) return;
    var dados = lerPopup();
    var r = V.validarVisita(dados);
    limparErros();
    if (!r.ok) {
      Object.keys(r.erros).forEach(function (c) { mostrarErro(c, r.erros[c]); });
      if (CAMPOS[r.primeiro]) $(CAMPOS[r.primeiro]).focus();
      return;
    }
    estado.enviando = true;
    atualizarBotao();
    api.chamar('registrar', dados).then(function (resp) {
      guardarToken(resp.visita.id, resp.token);
      fecharPopup();
      var texto = [resp.visita.hora, V.TIPOS[resp.visita.tipo].nome, resp.visita.primeiroNome].join(' · ');
      if (resp.cpfRepetido) {
        mostrarFaixa('aviso', 'Visita registrada. Atenção: este CPF já tinha visita hoje neste stand.', texto, true);
      } else {
        mostrarFaixa('ok', 'Visita registrada', texto, true);
      }
      estado.ultimo = resp.visita;
      carregarDia();
    }, function (f) {
      if (f.codigo === 'invalido' && mostrarErro(f.campo, f.mensagem)) {
        $(CAMPOS[f.campo]).focus();
      } else {
        $('p-erro').textContent = f.mensagem;
        $('p-erro').hidden = false;
      }
    }).then(function () {
      estado.enviando = false;
      atualizarBotao();
    });
  }

  /* ---------- faixa de retorno (spec 5.2 e 13.1) ---------- */
  function mostrarFaixa(tipo, titulo, texto, comDesfazer) {
    clearTimeout(estado.timerFaixa);
    $('faixa').className = 'faixa ' + tipo;
    $('faixa-ico-ok').style.display = tipo === 'ok' ? '' : 'none';
    $('faixa-ico-err').style.display = tipo === 'ok' ? 'none' : '';
    $('faixa-titulo').textContent = titulo;
    $('faixa-texto').textContent = texto;
    $('faixa-desfazer').hidden = !comDesfazer;
    $('faixa').hidden = false;
    /* no celular a faixa fica no topo: traz para a tela */
    try { $('faixa').scrollIntoView({ block: 'nearest', behavior: 'smooth' }); } catch (e) { /* navegador antigo */ }
    if (tipo === 'ok') estado.timerFaixa = setTimeout(esconderFaixa, 8000);
  }
  function esconderFaixa() {
    clearTimeout(estado.timerFaixa);
    $('faixa').hidden = true;
    estado.ultimo = null;
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
    var emp = $('emp').value, data = hoje();
    if (!emp) return;
    var seq = ++estado.seqDia;
    api.chamar('dia', { empreendimento: emp, data: data }).then(function (r) {
      if (seq !== estado.seqDia) return;
      var visitas = (r.visitas || []).filter(function (v) { return V.TIPOS[v.tipo]; });
      renderContador(visitas, emp, data);
      renderSugestoes(r.sugestoes || {});
      $('cont-erro').hidden = true;
    }, function (f) {
      if (seq !== estado.seqDia) return;
      $('cont-erro').textContent = f.mensagem;
      $('cont-erro').hidden = false;
    });
  }

  function renderContador(visitas, emp, data) {
    var t = V.totaisPorTipo(visitas);
    $('cont-titulo').textContent = 'Visitas hoje · ' + V.dataCurta(data);
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
    $('vazio').textContent = 'Nenhuma visita registrada hoje neste stand.';
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
    tipo.appendChild(document.createTextNode((v.primeiroNome ? v.primeiroNome + ' · ' : '') + V.TIPOS[v.tipo].nome));
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

  function preencherLista(id, nomes) {
    var dl = $(id);
    dl.textContent = '';
    (nomes || []).forEach(function (n) { var o = document.createElement('option'); o.value = n; dl.appendChild(o); });
  }
  function renderSugestoes(s) {
    preencherLista('lista-imob', s.imobiliarias);
    preencherLista('lista-corretor', s.corretores);
    preencherLista('lista-gerente', s.gerentes);
  }

  /* ---------- virada do dia ---------- */
  /* tablet aberto de um dia pro outro: popup aberto nao pode gravar na data antiga */
  function checarVirada() {
    if (document.visibilityState !== 'visible') return;
    var h = hoje();
    if (estado.hojeAplicado && h !== estado.hojeAplicado && $('popup').open) {
      aplicarLimitesData(h);
      if ($('f-data').value === estado.hojeAplicado) {
        $('f-data').value = h;
        $('f-hora').value = V.horaLocal(new Date());
      }
    }
    estado.hojeAplicado = h;
    carregarDia();
  }

  /* ---------- inicio ---------- */
  function iniciar() {
    montarEmpreendimentos();
    estado.hojeAplicado = hoje();
    $('aviso-demo').hidden = !api.demo;

    Array.prototype.forEach.call(document.querySelectorAll('.tipo'), function (b) {
      b.addEventListener('click', function () { abrirPopup(b.getAttribute('data-tipo')); });
    });
    $('emp').addEventListener('change', function () {
      gravarLS(CHAVE_EMP, $('emp').value);
      esconderFaixa();
      carregarDia();
    });
    $('p-form').addEventListener('submit', registrar);
    $('p-cancelar').addEventListener('click', fecharPopup);
    $('p-fechar').addEventListener('click', fecharPopup);
    $('popup').addEventListener('close', function () { estado.tipo = null; });
    $('f-agora').addEventListener('click', function () { $('f-hora').value = V.horaLocal(new Date()); limparErro('f-hora'); });
    $('f-cpf').addEventListener('input', function () { $('f-cpf').value = V.mascaraCpf($('f-cpf').value); });
    $('f-telefone').addEventListener('input', function () { $('f-telefone').value = V.mascaraTelefone($('f-telefone').value); });
    /* campo corrigido deixa de ficar marcado como invalido */
    Object.keys(CAMPOS).forEach(function (c) {
      var id = CAMPOS[c];
      $(id).addEventListener('input', function () { limparErro(id); });
      $(id).addEventListener('change', function () { limparErro(id); });
    });
    $('faixa-desfazer').addEventListener('click', desfazer);
    /* soma lancamentos de outro aparelho no mesmo stand */
    document.addEventListener('visibilitychange', checarVirada);
    setInterval(checarVirada, INTERVALO_DIA);

    carregarDia();
  }

  iniciar();
})();
```

- [ ] **Step 3: Check**

Run: `node --check assets/visitas-recepcao-app.js && node --test tests/*.test.js`
Expected: no syntax error; PASS. Every id the JS uses (`$('...')` and `'e-' + id`) must exist in the HTML. Cross-check them and list the result in the report.

- [ ] **Step 4: Browser verification (controller)**

In demo mode (`/visitas-recepcao.html` on the preview server), check:
- every card opens the popup with the right title and corretor label;
- the imobiliária field appears only for the Imobiliária type;
- the CPF and phone masks work;
- an empty or invalid submit shows the inline errors and moves focus to the first one;
- a valid registration closes the popup, shows the green banner and adds +1 to the counter;
- registering the same CPF twice gives the amber banner;
- "Desfazer" works;
- Esc, Cancelar and X close the popup;
- at 375px the popup covers the whole screen, with no horizontal scroll;
- the console has no errors.

- [ ] **Step 5: Commit**

```bash
git add visitas-recepcao.html assets/visitas-recepcao-app.js
git commit -m "feat(visitas): popup de cadastro da visita com dados do cliente

Co-Authored-By: <seu modelo> <noreply@anthropic.com>"
```

---

### Task 5: Dashboard com dados do cliente + README

**Files:**
- Modify: `visitas-recepcao-adm.html`, `assets/visitas-adm-app.js`, `README.md`

**Interfaces:**
- Consumes: `V.formatarCpf`, `V.formatarTelefone`, `V.gerarCSV` (Task 1); full visits from `listar`.

- [ ] **Step 1: Edit `visitas-recepcao-adm.html`**

a) In the "Últimos lançamentos" table, replace `<table style="min-width:640px">` and its `<thead>` with:

```html
      <table style="min-width:1080px">
        <thead><tr>
          <th scope="col">Data</th><th scope="col">Horário</th><th scope="col">Cliente</th>
          <th scope="col">CPF</th><th scope="col">Telefone</th><th scope="col">Empreendimento</th>
          <th scope="col">Tipo</th><th scope="col">Imobiliária</th><th scope="col">Corretor</th>
          <th scope="col">Gerente</th>
        </tr></thead>
```

b) Inside `<div class="acoes">`, right before the Exportar CSV button, add:

```html
      <span class="dica">Contém dados pessoais (CPF e telefone).</span>
```

- [ ] **Step 2: Edit `assets/visitas-adm-app.js`**

Replace the function `renderRecentes` with:

```js
  function renderRecentes(lista) {
    var tb = $('tab-recentes');
    tb.textContent = '';
    lista.forEach(function (v) {
      var tr = el('tr');
      celula(tr, V.dataCurta(v.data), 'num');
      celula(tr, v.hora, 'forte num');
      celula(tr, v.cliente, 'forte');
      celula(tr, V.formatarCpf(v.cpf), 'num');
      celula(tr, V.formatarTelefone(v.telefone), 'num');
      celula(tr, v.empreendimento);
      var td = celula(tr, '');
      var badge = el('span', 'badge');
      var ponto = el('span', 'ponto');
      ponto.style.background = V.TIPOS[v.tipo].cor;
      badge.appendChild(ponto);
      badge.appendChild(document.createTextNode(V.TIPOS[v.tipo].nome));
      td.appendChild(badge);
      celula(tr, v.imobiliaria || '—', 'suave');
      celula(tr, v.corretor || '—');
      celula(tr, v.gerente || '—', 'suave');
      tb.appendChild(tr);
    });
    $('sem-recentes').hidden = lista.length > 0;
  }
```

- [ ] **Step 3: Edit `README.md`**

In the section `## Visitas da recepção`, replace the first bullet with:

```markdown
- `/visitas-recepcao`: a recepcionista escolhe o stand e toca no tipo de visita
  (espontânea, agendada por corretor house ou trazida por imobiliária). Abre um popup
  com nome, CPF e telefone do cliente, data e horário, corretor (obrigatório), gerente
  de vendas (opcional) e, no tipo imobiliária, a imobiliária. Página pública, sem senha:
  ela nunca recebe CPF, telefone nem nome completo de volta do servidor.
```

and the second bullet with:

```markdown
- `/visitas-recepcao-adm`: dashboard do comercial, com senha forte (mínimo de 12
  caracteres, Script Property `VISITAS_SENHA` no Apps Script; a senha não fica no
  repositório). Mostra e exporta CPF e telefone: é dado pessoal (LGPD).
```

- [ ] **Step 4: Check**

Run: `node --check assets/visitas-adm-app.js && node --test tests/*.test.js`
Expected: no syntax error; PASS.

- [ ] **Step 5: Browser verification (controller)**

In demo mode (`/visitas-recepcao-adm.html`, password `demo`), check:
- the table shows client, CPF and phone formatted, plus corretor and gerente;
- the "dados pessoais" notice appears next to the export button;
- the console has no errors;
- the page has no horizontal scroll at 375px.

- [ ] **Step 6: Commit**

```bash
git add visitas-recepcao-adm.html assets/visitas-adm-app.js README.md
git commit -m "feat(visitas): dashboard mostra cliente, CPF, telefone, corretor e gerente

Co-Authored-By: <seu modelo> <noreply@anthropic.com>"
```

---

### Task 6 (controller): implantação

Same as Task 8, Steps 4–6 of the v1 plan:
- The user pastes the new `.gs` and sets a password with **≥ 12 characters**.
- They run `testeVisitas`, deploy, and send the `/exec` URL.
- The controller sets `VISITAS_APPS_SCRIPT_URL` and runs the smoke test: one visit of each type, plus one with a repeated CPF, plus checking whether the apostrophe shows in the sheet.
- Then the PR.

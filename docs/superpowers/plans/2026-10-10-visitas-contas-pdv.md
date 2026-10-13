# Visitas v3: contas das recepcionistas, PDV e só Ribeirão Preto. Plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cada recepcionista tem conta própria. Ela se cadastra, o comercial aprova e a sessão vale até a meia-noite. Cada visita grava quem a lançou e em qual PDV (Zona Sul RP ou Centro RP). O lançamento e o dashboard ficam restritos aos 4 empreendimentos de Ribeirão Preto.

**Architecture:**
- Continua a mesma arquitetura: site estático, mais o Web App do Apps Script gravando no Google Sheets.
- As contas ficam numa aba nova, `RECEPCIONISTAS`.
- A sessão é um token assinado com HMAC (`usuario.expira.assinatura`). Ela é conferida em toda ação da recepção.
- As regras puras ficam em `assets/visitas.js` (cliente) e em funções próprias no `.gs`. As do `.gs` são testadas no Node via `vm`, com `Utilities` e cache falsos.

**Tech Stack:** HTML/CSS/JS ES5 (IIFE, `var`, `function`), Google Apps Script (V8), `node --test` sem dependências.

**Spec:** `docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md`.
- **§14 é a v3** e vale sobre §13 e §1–12 onde diverge.
- Telas: canvas "Visitas Recepção" (https://claude.ai/artifact/254FTbPxSoAVKMsPvJd8vV).
  - Recepção: `Main`, `RecepcaoCelular`, `PopupImobiliaria`, `PopupCelular`.
  - Acesso: `Login`, `LoginCadastro`, `LoginPendente`, `LoginTroca`.
  - Dashboard: `Admin`, `AdminRecepcionistas`.

**Estado de partida:** branch `feat/visitas-recepcao` com v1 e v2 completas e 81 testes passando.

## Global Constraints

**Estilo e testes**
- Sem dependências npm e sem build.
- Estilo do repo: IIFE, `'use strict'`, `var`, `function`, comentários curtos em português sem acento.
- Testes: `node --test tests/*.test.js`.

**Listas fixas**
- PDVs, nesta ordem: `['Zona Sul RP', 'Centro RP']`. A constante se chama `PDVS` em `assets/visitas.js` e `VISITAS_PDVS` no `.gs`.
- Lançamento e dashboard usam **só** os empreendimentos da cidade `'Ribeirão Preto'` do `window.CITIES`: Village Park, Village Gaia, Reserva Direcional Jardim Botânico e Direcional Conquista Clube Ipiranga. O resto do portal não muda.

**Contas**
- Usuário: normalizado com `trim().toLowerCase()`. Válido se casa com `/^[a-z0-9][a-z0-9._-]{2,29}$/`.
- Senha: de 8 a 72 caracteres. Não pode ser igual ao usuário (comparação sem caixa). Senha não leva `trim`.
- Aba `RECEPCIONISTAS`, colunas nesta ordem: `Usuário · Nome · Situação · Hash · Sal · Temporária · Criado em · Aprovado em · Último acesso`.
  - `Situação`: `pendente`, `ativa` ou `desativada`.
  - `Temporária`: `sim` ou `não`.
- Hash: SHA-256 em hexadecimal, 1.000 vezes. Primeiro `h = sha(sal + senha)`; depois, 999 vezes, `h = sha(h + sal)`.

**Visitas**
- Aba `VISITAS`, colunas nesta ordem: `ID · Registrado em · Data · Horário · PDV · Empreendimento · Cidade · Tipo · Nome do cliente · CPF · Telefone · Imobiliária · Corretor · Gerente de vendas · Lançado por · Excluída`. A coluna `Token` sai.
- `Lançado por` grava o **usuário**.
- **Visita completa** (só no `listar`, com senha do dashboard):
  `{ id, data, hora, pdv, empreendimento, cidade, tipo, cliente, cpf, telefone, imobiliaria, corretor, gerente, lancadoPor /* nome da recepcionista */ }`.
- **Visita resumida** (respostas da recepção):
  `{ id, data, hora, pdv, empreendimento, tipo, primeiroNome, imobiliaria, corretor, minha }`. O usuário de quem lançou **não** entra nela.

**Sessão**
- Token: `usuario + '.' + expira + '.' + assinatura`.
  - `expira` é a próxima meia-noite de Brasília, em ms. O fuso é fixo em −03:00.
  - `assinatura = base64WebSafe(HMAC-SHA256(usuario + '.' + expira + '.' + hash.slice(0, 12), segredo))`.
  - O segredo fica na Script Property `VISITAS_SEGREDO`.
- Erro de sessão: `{ erro: 'sessao', mensagem: 'Sua sessão terminou. Entre de novo.' }`.

**Mensagens fixas (exatas)**

| Código / campo | Mensagem |
|---|---|
| `credenciais` | "Usuário ou senha incorretos." |
| `bloqueado` | "Muitas tentativas. Tente de novo em 15 minutos." |
| `pendente` | "Seu cadastro está aguardando aprovação do comercial." |
| `desativada` | "Seu acesso foi desativado. Fale com o comercial." |
| `limite` | "Muitos cadastros aguardando aprovação. Fale com o comercial." |
| usuário repetido | "Esse usuário já existe." |
| nome | "Informe seu nome completo." |
| usuário inválido | "Use de 3 a 30 letras minúsculas, números, ponto, hífen ou sublinhado." |
| senha (tamanho) | "A senha precisa ter de 8 a 72 caracteres." |
| senha igual ao usuário | "A senha não pode ser igual ao usuário." |
| confirmação | "As senhas não conferem." |
| pdv | "Escolha o PDV." |

**Segurança**
- Nada de senha, hash, sal, token, segredo, CPF ou telefone em `Logger.log` ou em mensagem de erro.
- Todo texto vindo da API vai para o DOM com `textContent`.
- CPFs de teste/demo: só `52998224725`, `11144477735`, `12345678909`, `98765432100`.

**Commits**
- Formato `tipo(visitas): ...`, sempre com o trailer `Co-Authored-By:`.
- `git add` só dos arquivos da tarefa. A árvore tem mudanças do usuário (`.claude/*`, `.DS_Store`, `.impeccable/`) que **nunca** entram em commit.

## File Structure

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `assets/visitas.js` | modificar | PDVS, empreendimentos de RP, validação de usuário/senha/cadastro, sessão válida, `validarVisita` com PDV, `resumirVisita` com `pdv`/`minha`, filtro por PDV, CSV v3 |
| `tests/visitas-regras.test.js`, `tests/visitas-dashboard.test.js`, `tests/fixtures/visitas.json` | modificar | testes do cliente |
| `docs/apps-script-visitas.gs` | modificar | regras puras de conta/sessão (T2), contas e ações do comercial (T3), visitas com PDV/dona/RP (T4) |
| `tests/visitas-gs.test.js` | modificar | testes do `.gs` com `Utilities` e cache falsos |
| `assets/visitas-api.js` | modificar | envia `sessao`; modo demo no contrato v3 |
| `visitas-recepcao.html`, `assets/visitas-recepcao-app.js` | modificar / reescrever | telas de acesso, PDV no Passo 1, empreendimento no popup, exclusão da dona |
| `visitas-recepcao-adm.html`, `assets/visitas-adm-app.js` | modificar | abas Visitas/Recepcionistas, filtro de PDV, colunas novas |
| `README.md` | modificar | seção "Visitas da recepção" |

---

### Task 1: Regras puras do cliente (`assets/visitas.js`)

**Files:**
- Modify: `assets/visitas.js`
- Modify: `tests/visitas-regras.test.js`, `tests/visitas-dashboard.test.js`, `tests/fixtures/visitas.json`

**Interfaces:**
- Produces (exportados no `api`):
  - `PDVS: string[]`, `CIDADE_VISITAS: 'Ribeirão Preto'`
  - `empreendimentosVisitas(cidades) → [{ nome, cidade }]`: só os de Ribeirão Preto, na ordem do config
  - `normalizarUsuario(s) → string`, `usuarioValido(s) → boolean`
  - `validarSenha(senha, usuario) → string`: mensagem, ou `''` se a senha for válida
  - `validarCadastro({ nome, usuario, senha, confirmacao }) → { ok, erros, primeiro }`
  - `sessaoValida(s, agoraMs) → boolean`
  - `validarVisita(d)` passa a exigir `d.pdv`; o primeiro campo da ordem passa a ser `pdv`
  - `resumirVisita(v, usuario)` passa a incluir `pdv` e `minha`
  - `filtrar(visitas, { de, ate, pdv, empreendimento })`: `pdv` substitui `cidade`; `'Todos'` não filtra
  - `gerarCSV` com as colunas v3

- [ ] **Step 1: Atualizar a fixture**

Em `tests/fixtures/visitas.json`, acrescente `"pdv"` e `"lancadoPor"` em cada objeto. Não mude mais nada.
- V1, V2, V5, V6 e V8 (hoje são de Campinas): `"pdv": "Zona Sul RP"`.
- V3, V4 e V7: `"pdv": "Centro RP"`.
- `"lancadoPor"`: `"Recepcionista Teste Um"` nos ímpares (V1, V3, V5, V7) e `"Recepcionista Teste Dois"` nos pares.

- [ ] **Step 2: Escrever os testes que falham**

Em `tests/visitas-regras.test.js`:

(a) Substitua os testes `validarVisita lista todos os erros e aponta o primeiro` e `resumirVisita não leva CPF, telefone, nome completo nem gerente` por:

```js
test('validarVisita exige PDV e empreendimento, lista todos os erros e aponta o primeiro', () => {
  const ok = {
    pdv: 'Zona Sul RP', empreendimento: 'Village Park', tipo: 'esp', cliente: 'Mariana Souza', cpf: '529.982.247-25',
    telefone: '(19) 98765-4321', data: '2026-10-09', hora: '14:35', corretor: 'Rui', gerente: ''
  };
  assert.deepEqual(V.validarVisita(ok), { ok: true, erros: {}, primeiro: null });
  const r = V.validarVisita({ ...ok, cliente: ' ', cpf: '529.982.247-2', corretor: '' });
  assert.equal(r.ok, false);
  assert.equal(r.primeiro, 'cliente');
  assert.deepEqual(Object.keys(r.erros), ['cliente', 'cpf', 'corretor']);
  assert.equal(r.erros.cpf, 'CPF inválido. Confira os números.');
  assert.equal(V.validarVisita({ ...ok, pdv: '' }).primeiro, 'pdv');
  assert.equal(V.validarVisita({ ...ok, pdv: 'Outro' }).erros.pdv, 'Escolha o PDV.');
  assert.equal(V.validarVisita({ ...ok, empreendimento: '' }).primeiro, 'empreendimento');
  assert.equal(V.validarVisita({ ...ok, tipo: 'imob' }).primeiro, 'imobiliaria');
  assert.equal(V.validarVisita({ ...ok, tipo: 'imob', imobiliaria: 'Imob Ápice' }).ok, true);
  assert.equal(V.validarVisita({ ...ok, tipo: 'house', imobiliaria: '' }).ok, true);
  assert.equal(V.validarVisita({ ...ok, telefone: '98765-4321' }).primeiro, 'telefone');
  assert.equal(V.validarVisita({ ...ok, tipo: 'xyz' }).primeiro, 'tipo');
  assert.equal(V.validarVisita({ ...ok, hora: '9:5' }).primeiro, 'hora');
});

const VISITA = {
  id: 'V1', data: '2026-10-09', hora: '14:35', pdv: 'Centro RP', empreendimento: 'Village Park', cidade: 'Ribeirão Preto',
  tipo: 'imob', cliente: 'Mariana Souza Lima', cpf: '52998224725', telefone: '19987654321', imobiliaria: 'Imob Ápice',
  corretor: 'Rui', gerente: 'Gil', lancadoPor: 'recep.um'
};

test('resumirVisita leva PDV e "minha", sem CPF, telefone, nome completo, gerente nem usuário', () => {
  assert.deepEqual(V.resumirVisita(VISITA, 'recep.um'), {
    id: 'V1', data: '2026-10-09', hora: '14:35', pdv: 'Centro RP', empreendimento: 'Village Park', tipo: 'imob',
    primeiroNome: 'Mariana', imobiliaria: 'Imob Ápice', corretor: 'Rui', minha: true
  });
  assert.equal(V.resumirVisita(VISITA, 'recep.dois').minha, false);
  assert.equal(V.resumirVisita(VISITA).minha, false);
  assert.equal(V.resumirVisita({ ...VISITA, lancadoPor: '' }, '').minha, false);
  const texto = JSON.stringify(V.resumirVisita(VISITA, 'recep.dois'));
  ['52998224725', '19987654321', 'Souza', 'Gil', 'recep.um'].forEach((s) => assert.ok(!texto.includes(s), s));
});
```

(b) Acrescente no fim do arquivo:

```js
test('PDVS e empreendimentosVisitas (só Ribeirão Preto)', () => {
  assert.deepEqual(V.PDVS, ['Zona Sul RP', 'Centro RP']);
  const cidades = [
    { name: 'Campinas', empreendimentos: [{ nome: 'A' }] },
    { name: 'Ribeirão Preto', empreendimentos: [{ nome: 'B' }, { nome: 'C' }] }
  ];
  assert.deepEqual(V.empreendimentosVisitas(cidades), [
    { nome: 'B', cidade: 'Ribeirão Preto' }, { nome: 'C', cidade: 'Ribeirão Preto' }
  ]);
  assert.deepEqual(V.empreendimentosVisitas(undefined), []);
});

test('normalizarUsuario e usuarioValido', () => {
  assert.equal(V.normalizarUsuario('  Maria.Silva '), 'maria.silva');
  assert.equal(V.normalizarUsuario(null), '');
  ['ana', 'maria.silva', 'recep_2', 'a-b', '3ab', 'a'.repeat(30)].forEach((u) => assert.equal(V.usuarioValido(u), true, u));
  ['ab', 'a'.repeat(31), '-abc', '.abc', '_abc', 'joão', 'maria silva', 'Maria', '', null, 'a=b'].forEach((u) =>
    assert.equal(V.usuarioValido(u), false, String(u)));
});

test('validarSenha: 8 a 72 caracteres e diferente do usuário', () => {
  assert.equal(V.validarSenha('12345678', 'ana'), '');
  assert.equal(V.validarSenha('1234567', 'ana'), 'A senha precisa ter de 8 a 72 caracteres.');
  assert.equal(V.validarSenha('x'.repeat(73), 'ana'), 'A senha precisa ter de 8 a 72 caracteres.');
  assert.equal(V.validarSenha('x'.repeat(72), 'ana'), '');
  assert.equal(V.validarSenha('Maria.Silva', 'maria.silva'), 'A senha não pode ser igual ao usuário.');
  assert.equal(V.validarSenha(undefined, 'ana'), 'A senha precisa ter de 8 a 72 caracteres.');
});

test('validarCadastro aponta o primeiro erro na ordem nome, usuario, senha, confirmacao', () => {
  const ok = { nome: ' Maria  Silva ', usuario: 'Maria.Silva', senha: 'segredo123', confirmacao: 'segredo123' };
  assert.deepEqual(V.validarCadastro(ok), { ok: true, erros: {}, primeiro: null });
  const r = V.validarCadastro({ nome: '', usuario: 'ab', senha: '123', confirmacao: 'x' });
  assert.deepEqual(Object.keys(r.erros), ['nome', 'usuario', 'senha', 'confirmacao']);
  assert.equal(r.primeiro, 'nome');
  assert.equal(r.erros.nome, 'Informe seu nome completo.');
  assert.equal(r.erros.usuario, 'Use de 3 a 30 letras minúsculas, números, ponto, hífen ou sublinhado.');
  assert.equal(r.erros.confirmacao, 'As senhas não conferem.');
  assert.equal(V.validarCadastro({ ...ok, senha: 'maria.silva', confirmacao: 'maria.silva' }).erros.senha,
    'A senha não pode ser igual ao usuário.');
});

test('sessaoValida confere token e validade', () => {
  const agora = Date.UTC(2026, 9, 10, 15, 0);
  assert.equal(V.sessaoValida({ token: 'a.1.b', expira: agora + 1 }, agora), true);
  assert.equal(V.sessaoValida({ token: 'a.1.b', expira: agora }, agora), false);
  assert.equal(V.sessaoValida({ token: '', expira: agora + 1 }, agora), false);
  assert.equal(V.sessaoValida({ token: 'a.1.b', expira: String(agora + 1) }, agora), false);
  assert.equal(V.sessaoValida(null, agora), false);
});
```

Em `tests/visitas-dashboard.test.js`:

(a) Troque a constante do cabeçalho:

```js
const CABECALHO_CSV = 'Data;Horário;PDV;Empreendimento;Tipo;Cliente;CPF;Telefone;Imobiliária;Corretor;Gerente de vendas;Lançado por';
```

(b) Substitua o teste `filtrar por período, cidade e empreendimento` por:

```js
test('filtrar por período, PDV e empreendimento', () => {
  assert.equal(V.filtrar(FIX, {}).length, 8);
  assert.equal(V.filtrar(FIX, { pdv: 'Todos', empreendimento: 'Todos' }).length, 8);
  assert.deepEqual(ids(V.filtrar(FIX, { pdv: 'Zona Sul RP' })), ['V1', 'V2', 'V5', 'V6', 'V8']);
  assert.deepEqual(ids(V.filtrar(FIX, { pdv: 'Centro RP' })), ['V3', 'V4', 'V7']);
  assert.deepEqual(ids(V.filtrar(FIX, { de: '2026-10-09' })), ['V6', 'V7', 'V8']);
  assert.deepEqual(ids(V.filtrar(FIX, { empreendimento: 'Village Park', ate: '2026-10-07' })), ['V3']);
});
```

(c) Substitua o teste do `gerarCSV` com BOM por:

```js
test('gerarCSV: BOM, separador ;, ordem cronológica, aspas, neutralização, PDV e lançado por', () => {
  const visitas = [
    { data: '2026-10-09', hora: '11:50', pdv: 'Centro RP', empreendimento: 'Village Gaia', cidade: 'Ribeirão Preto', tipo: 'esp', cliente: 'Ana Lima', cpf: '52998224725', telefone: '15998765432', imobiliaria: '', corretor: 'Rui', gerente: '', lancadoPor: 'Recepcionista Um' },
    { data: '2026-10-08', hora: '14:00', pdv: 'Zona Sul RP', empreendimento: 'Village Park', cidade: 'Ribeirão Preto', tipo: 'imob', cliente: '=HYPERLINK("x")', cpf: '11144477735', telefone: '1932458890', imobiliaria: 'Imob; Centro', corretor: 'Bia', gerente: 'Gil', lancadoPor: 'Recepcionista Dois' }
  ];
  const esperado = '﻿' + CABECALHO_CSV + '\r\n' +
    '08/10/2026;14:00;Zona Sul RP;Village Park;Imobiliária;"\'=HYPERLINK(""x"")";111.444.777-35;(19) 3245-8890;"Imob; Centro";Bia;Gil;Recepcionista Dois\r\n' +
    '09/10/2026;11:50;Centro RP;Village Gaia;Espontânea;Ana Lima;529.982.247-25;(15) 99876-5432;;Rui;;Recepcionista Um\r\n';
  assert.equal(V.gerarCSV(visitas), esperado);
});
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `node --test tests/visitas-regras.test.js tests/visitas-dashboard.test.js`
Expected: FAIL. Os testes novos falham com `V.PDVS` undefined / `is not a function`, e os de `filtrar` e CSV falham por diferença.

- [ ] **Step 4: Implementar em `assets/visitas.js`**

(a) Logo depois de `function primeiroNome(...)`, acrescente:

```js
  /* ---------- v3: so Ribeirao Preto, PDV e contas (spec 14) ---------- */
  var PDVS = ['Zona Sul RP', 'Centro RP'];
  var CIDADE_VISITAS = 'Ribeirão Preto';
  function normalizarUsuario(s) { return String(s === null || s === undefined ? '' : s).trim().toLowerCase(); }
  function usuarioValido(s) { return /^[a-z0-9][a-z0-9._-]{2,29}$/.test(String(s === null || s === undefined ? '' : s)); }
  function validarSenha(senha, usuario) {
    var s = String(senha === null || senha === undefined ? '' : senha);
    if (s.length < 8 || s.length > 72) return 'A senha precisa ter de 8 a 72 caracteres.';
    if (s.toLowerCase() === normalizarUsuario(usuario)) return 'A senha não pode ser igual ao usuário.';
    return '';
  }
  var ORDEM_CADASTRO = ['nome', 'usuario', 'senha', 'confirmacao'];
  function validarCadastro(d) {
    var usuario = normalizarUsuario(d.usuario);
    var msgs = {
      nome: normalizarTexto(d.nome) ? '' : 'Informe seu nome completo.',
      usuario: usuarioValido(usuario) ? '' : 'Use de 3 a 30 letras minúsculas, números, ponto, hífen ou sublinhado.',
      senha: validarSenha(d.senha, usuario),
      confirmacao: String(d.confirmacao || '') === String(d.senha || '') ? '' : 'As senhas não conferem.'
    };
    var erros = {}, primeiro = null;
    ORDEM_CADASTRO.forEach(function (c) {
      if (!msgs[c]) return;
      erros[c] = msgs[c];
      if (!primeiro) primeiro = c;
    });
    return { ok: !primeiro, erros: erros, primeiro: primeiro };
  }
  function sessaoValida(s, agoraMs) {
    return !!(s && typeof s.token === 'string' && s.token && typeof s.expira === 'number' && agoraMs < s.expira);
  }
```

(b) Em `validarVisita`:
- `ORDEM_CAMPOS` vira `['pdv', 'empreendimento', 'tipo', 'cliente', 'cpf', 'telefone', 'data', 'hora', 'imobiliaria', 'corretor']`.
- `MENSAGENS_CAMPO` ganha `pdv: 'Escolha o PDV.'`.
- O objeto `falha` ganha `pdv: PDVS.indexOf(d.pdv) < 0`.

(c) Substitua `resumirVisita` por:

```js
  /* o que pode sair para a recepcao: sem CPF, telefone, nome completo, gerente e usuario */
  function resumirVisita(v, usuario) {
    return {
      id: v.id, data: v.data, hora: v.hora, pdv: v.pdv || '', empreendimento: v.empreendimento, tipo: v.tipo,
      primeiroNome: primeiroNome(v.cliente), imobiliaria: v.imobiliaria || '', corretor: v.corretor || '',
      minha: !!usuario && v.lancadoPor === usuario
    };
  }
```

(d) Logo depois de `listaEmpreendimentos`, acrescente:

```js
  function empreendimentosVisitas(cidades) {
    return listaEmpreendimentos(cidades).filter(function (e) { return e.cidade === CIDADE_VISITAS; });
  }
```

(e) Em `filtrar`, troque a linha da cidade por:

```js
      if (f.pdv && f.pdv !== 'Todos' && v.pdv !== f.pdv) return false;
```

(f) CSV:

```js
  var CSV_COLUNAS = ['Data', 'Horário', 'PDV', 'Empreendimento', 'Tipo', 'Cliente', 'CPF', 'Telefone', 'Imobiliária', 'Corretor', 'Gerente de vendas', 'Lançado por'];
```

e em `gerarCSV` a linha passa a ser:

```js
      linhas.push([
        dataBr(v.data), v.hora, v.pdv, v.empreendimento, TIPOS[v.tipo] ? TIPOS[v.tipo].nome : v.tipo,
        v.cliente, formatarCpf(v.cpf), formatarTelefone(v.telefone), v.imobiliaria, v.corretor, v.gerente, v.lancadoPor
      ].map(celulaCSV).join(';'));
```

(g) No objeto `api`, acrescente: `PDVS`, `CIDADE_VISITAS`, `normalizarUsuario`, `usuarioValido`, `validarSenha`, `validarCadastro`, `sessaoValida`, `empreendimentosVisitas`.

- [ ] **Step 5: Rodar e ver passar**

Run: `node --test tests/*.test.js`
Expected: PASS em `visitas-regras` e `visitas-dashboard`.
- `tests/visitas-gs.test.js` pode falhar só no teste `visResumo_ é igual ao resumo do cliente`: o resumo do cliente agora tem `pdv`/`minha` e o do servidor ainda não. Isso se resolve na Task 4.
- Anote a falha no relatório e não mexa no `.gs` nesta tarefa.

- [ ] **Step 6: Commit**

```bash
git add assets/visitas.js tests/visitas-regras.test.js tests/visitas-dashboard.test.js tests/fixtures/visitas.json
git commit -m "feat(visitas): regras de PDV, Ribeirao Preto e contas no cliente

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Regras puras de conta e sessão no `.gs`

**Files:**
- Modify: `docs/apps-script-visitas.gs` (só constantes e funções puras novas; nada de I/O)
- Modify: `tests/visitas-gs.test.js`

**Interfaces:**
- Consumes: `visTexto_`, `visHash_(texto) → hex`, `VisFalha` (já existem).
- Produces (todas puras; `Utilities` só para hash/HMAC/base64):
  - Constantes:
    - `VIS_ABA_CONTAS = 'RECEPCIONISTAS'`, `VIS_COLUNAS_CONTAS` (ordem dos Global Constraints)
    - `VIS_PROP_SEGREDO = 'VISITAS_SEGREDO'`, `VIS_ITERACOES = 1000`
    - `VIS_MAX_FALHAS = 5`, `VIS_BLOQUEIO_S = 900`, `VIS_MAX_PENDENTES = 20`
    - `VISITAS_PDVS`, `VIS_MSG_SESSAO`, `VIS_TEMP_ALFABETO`
  - Usuário e senha:
    - `visNormUsuario_(s) → string`, `visUsuarioValido_(s) → boolean`
    - `visValidarSenha_(senha, usuario) → string` (mesmas mensagens do cliente)
    - `visValidarCadastro_(req) → { nome, usuario, senha }`, ou lança `VisFalha('invalido', msg, campo)` com campo `nome`/`usuario`/`senha`
    - `visHashSenha_(senha, sal) → hex`
  - Sessão:
    - `visExpiraMeiaNoite_(agoraMs) → ms`
    - `visAssinar_(usuario, expira, hash, segredo) → string`
    - `visCriarToken_(usuario, hash, agoraMs, segredo) → { token, expira }`
    - `visLerToken_(token) → { usuario, expira, assinatura } | null`
    - `visIguais_(a, b) → boolean` (tempo constante)
    - `visConferirToken_(token, conta, agoraMs, segredo) → boolean`
    - `visSessaoOk_(token, conta, agoraMs, segredo, permitirTemporaria) → boolean`
  - Senha temporária: `visSenhaTemporaria_(bytes /* 9 inteiros 0..255 */) → 'abc-def-ghi'`
  - Contas:
    - `visContaDeLinha_(l, ix) → { usuario, nome, situacao, hash, sal, temporaria, criadoEm, aprovadoEm, ultimoAcesso }`
    - `visContaPublica_(c, visitas30) → { usuario, nome, situacao, temporaria, criadoEm, ultimoAcesso, visitas30 }`
    - `visContarPendentes_(linhas, ix) → number`
  - Bloqueio por tentativas (`cache` com `get`/`put`/`remove`, como `CacheService.getScriptCache()`):
    - `visBloqueado_(cache, usuario) → boolean`
    - `visRegistrarFalha_(cache, usuario) → number`
    - `visLimparFalhas_(cache, usuario)`

- [ ] **Step 1: Escrever os testes que falham**

No topo de `tests/visitas-gs.test.js`, troque a criação do contexto `gs` por um contexto com `Utilities` falso (Node `crypto`):

```js
const crypto = require('node:crypto');
const assinado = (buf) => Array.from(buf, (b) => (b > 127 ? b - 256 : b));
const UtilitiesFalso = {
  DigestAlgorithm: { SHA_256: 'sha256' },
  Charset: { UTF_8: 'utf8' },
  computeDigest: (alg, texto) => assinado(crypto.createHash('sha256').update(String(texto), 'utf8').digest()),
  computeHmacSha256Signature: (valor, chave) => assinado(crypto.createHmac('sha256', chave).update(valor, 'utf8').digest()),
  base64EncodeWebSafe: (bytes) => Buffer.from(bytes.map((b) => b & 255)).toString('base64').replace(/\+/g, '-').replace(/\//g, '_'),
  getUuid: () => crypto.randomUUID()
};
const gs = carregar('docs/apps-script-visitas.gs', { Utilities: UtilitiesFalso });
function cacheFalso() {
  const m = new Map();
  return { get: (k) => (m.has(k) ? m.get(k) : null), put: (k, v) => { m.set(k, String(v)); }, remove: (k) => { m.delete(k); } };
}
```

Acrescente no fim do arquivo:

```js
test('usuário e senha: mesmo resultado no cliente e no servidor', () => {
  const usuarios = ['ana', 'maria.silva', 'recep_2', '3ab', 'ab', '-abc', 'joão', 'Maria', '', 'a'.repeat(30), 'a'.repeat(31)];
  usuarios.forEach((u) => assert.equal(gs.visUsuarioValido_(u), V.usuarioValido(u), u));
  assert.equal(gs.visNormUsuario_('  Maria.Silva '), V.normalizarUsuario('  Maria.Silva '));
  const senhas = [['12345678', 'ana'], ['1234567', 'ana'], ['x'.repeat(73), 'ana'], ['Maria.Silva', 'maria.silva'], [undefined, 'ana']];
  senhas.forEach(([s, u]) => assert.equal(gs.visValidarSenha_(s, u), V.validarSenha(s, u), String(s)));
});

test('visValidarCadastro_ normaliza e recusa com o campo certo', () => {
  assert.deepEqual(plano(gs.visValidarCadastro_({ nome: ' Maria  Silva ', usuario: ' Maria.Silva ', senha: 'segredo123' })),
    { nome: 'Maria Silva', usuario: 'maria.silva', senha: 'segredo123' });
  assert.throws(() => gs.visValidarCadastro_({ nome: ' ', usuario: 'ana', senha: 'segredo123' }), recusa('nome'));
  assert.throws(() => gs.visValidarCadastro_({ nome: 'Ana', usuario: 'a b', senha: 'segredo123' }), recusa('usuario'));
  assert.throws(() => gs.visValidarCadastro_({ nome: 'Ana', usuario: 'ana', senha: '123' }), recusa('senha'));
});

test('visHashSenha_: determinístico por sal, diferente com outro sal ou outra senha, sem a senha em claro', () => {
  const h = gs.visHashSenha_('segredo123', 'sal-1');
  assert.match(h, /^[0-9a-f]{64}$/);
  assert.equal(gs.visHashSenha_('segredo123', 'sal-1'), h);
  assert.notEqual(gs.visHashSenha_('segredo123', 'sal-2'), h);
  assert.notEqual(gs.visHashSenha_('segredo124', 'sal-1'), h);
  let esperado = crypto.createHash('sha256').update('sal-1segredo123').digest('hex');
  for (let i = 1; i < 1000; i++) esperado = crypto.createHash('sha256').update(esperado + 'sal-1').digest('hex');
  assert.equal(h, esperado);
});

test('visExpiraMeiaNoite_: próxima meia-noite de Brasília (03h UTC)', () => {
  assert.equal(gs.visExpiraMeiaNoite_(Date.UTC(2026, 9, 10, 2, 59)), Date.UTC(2026, 9, 10, 3, 0));
  assert.equal(gs.visExpiraMeiaNoite_(Date.UTC(2026, 9, 10, 3, 0)), Date.UTC(2026, 9, 11, 3, 0));
  assert.equal(gs.visExpiraMeiaNoite_(Date.UTC(2026, 9, 10, 15, 0)), Date.UTC(2026, 9, 11, 3, 0));
  assert.equal(gs.visExpiraMeiaNoite_(Date.UTC(2026, 11, 31, 20, 0)), Date.UTC(2027, 0, 1, 3, 0));
});

test('token de sessão: válido, vencido, alterado, outro usuário, hash trocado, segredo errado', () => {
  const agora = Date.UTC(2026, 9, 10, 15, 0);
  const conta = { usuario: 'maria.silva', hash: 'a'.repeat(64), situacao: 'ativa', temporaria: false };
  const t = gs.visCriarToken_(conta.usuario, conta.hash, agora, 'segredo');
  assert.equal(t.expira, Date.UTC(2026, 9, 11, 3, 0));
  assert.ok(t.token.startsWith('maria.silva.' + t.expira + '.'));
  assert.deepEqual(plano(gs.visLerToken_(t.token)).usuario, 'maria.silva');
  assert.equal(gs.visConferirToken_(t.token, conta, agora, 'segredo'), true);
  assert.equal(gs.visConferirToken_(t.token, conta, t.expira, 'segredo'), false);
  assert.equal(gs.visConferirToken_(t.token, conta, agora, 'outro'), false);
  assert.equal(gs.visConferirToken_(t.token.slice(0, -2) + 'xx', conta, agora, 'segredo'), false);
  const futuro = t.token.replace('.' + t.expira + '.', '.' + (t.expira + 86400000) + '.');
  assert.equal(gs.visConferirToken_(futuro, conta, agora, 'segredo'), false);
  assert.equal(gs.visConferirToken_(t.token, { ...conta, usuario: 'outra' }, agora, 'segredo'), false);
  assert.equal(gs.visConferirToken_(t.token, { ...conta, hash: 'b'.repeat(64) }, agora, 'segredo'), false);
  assert.equal(gs.visConferirToken_('lixo', conta, agora, 'segredo'), false);
  assert.equal(gs.visConferirToken_(undefined, conta, agora, 'segredo'), false);
  assert.equal(gs.visLerToken_('ab.123.x'), null);
  assert.equal(gs.visLerToken_('ana.12a.x'), null);
  assert.equal(gs.visLerToken_('ana.123.'), null);
});

test('visSessaoOk_ exige conta ativa e, fora da troca de senha, sem senha temporária', () => {
  const agora = Date.UTC(2026, 9, 10, 15, 0);
  const conta = { usuario: 'ana', hash: 'c'.repeat(64), situacao: 'ativa', temporaria: false };
  const { token } = gs.visCriarToken_('ana', conta.hash, agora, 's');
  assert.equal(gs.visSessaoOk_(token, conta, agora, 's', false), true);
  assert.equal(gs.visSessaoOk_(token, { ...conta, situacao: 'desativada' }, agora, 's', false), false);
  assert.equal(gs.visSessaoOk_(token, { ...conta, situacao: 'pendente' }, agora, 's', true), false);
  assert.equal(gs.visSessaoOk_(token, { ...conta, temporaria: true }, agora, 's', false), false);
  assert.equal(gs.visSessaoOk_(token, { ...conta, temporaria: true }, agora, 's', true), true);
  assert.equal(gs.visSessaoOk_(token, null, agora, 's', true), false);
});

test('visIguais_', () => {
  assert.equal(gs.visIguais_('abc', 'abc'), true);
  assert.equal(gs.visIguais_('abc', 'abd'), false);
  assert.equal(gs.visIguais_('abc', 'abcd'), false);
  assert.equal(gs.visIguais_('', ''), true);
});

test('visSenhaTemporaria_: 3 grupos de 3, sem caracteres ambíguos', () => {
  const s = gs.visSenhaTemporaria_([0, 1, 2, 55, 56, 100, 200, 254, 255]);
  assert.match(s, /^[A-Za-z0-9]{3}-[A-Za-z0-9]{3}-[A-Za-z0-9]{3}$/);
  for (let i = 0; i < 50; i++) {
    const bytes = Array.from(crypto.randomBytes(9));
    assert.doesNotMatch(gs.visSenhaTemporaria_(bytes), /[0O1lIo]/);
  }
  assert.equal(gs.visSenhaTemporaria_([0, 0, 0, 0, 0, 0, 0, 0, 0]), 'aaa-aaa-aaa');
  assert.equal(V.validarSenha(s, 'ana'), '');
});

function indiceContas() { const ix = {}; gs.VIS_COLUNAS_CONTAS.forEach((n, i) => { ix[n] = i; }); return ix; }
function linhaConta(c) { return gs.VIS_COLUNAS_CONTAS.map((n) => (c[n] !== undefined ? c[n] : '')); }

test('VIS_COLUNAS_CONTAS, visContaDeLinha_ e visContaPublica_ (sem hash nem sal)', () => {
  assert.deepEqual(plano(gs.VIS_COLUNAS_CONTAS), ['Usuário', 'Nome', 'Situação', 'Hash', 'Sal', 'Temporária', 'Criado em', 'Aprovado em', 'Último acesso']);
  const l = linhaConta({
    'Usuário': ' ana ', 'Nome': 'Ana Lima', 'Situação': 'ativa', 'Hash': 'h'.repeat(64), 'Sal': 's1', 'Temporária': 'sim',
    'Criado em': '01/10/2026 09:00:00', 'Aprovado em': '01/10/2026 10:00:00', 'Último acesso': '10/10/2026 08:02:00'
  });
  const c = plano(gs.visContaDeLinha_(l, indiceContas()));
  assert.deepEqual(c, {
    usuario: 'ana', nome: 'Ana Lima', situacao: 'ativa', hash: 'h'.repeat(64), sal: 's1', temporaria: true,
    criadoEm: '01/10/2026 09:00:00', aprovadoEm: '01/10/2026 10:00:00', ultimoAcesso: '10/10/2026 08:02:00'
  });
  const p = plano(gs.visContaPublica_(c, 12));
  assert.deepEqual(p, { usuario: 'ana', nome: 'Ana Lima', situacao: 'ativa', temporaria: true, criadoEm: '01/10/2026 09:00:00', ultimoAcesso: '10/10/2026 08:02:00', visitas30: 12 });
  assert.ok(!JSON.stringify(p).includes('h'.repeat(64)));
  assert.equal(gs.visContaPublica_(c).visitas30, 0);
  const linhas = [linhaConta({ 'Situação': 'pendente' }), linhaConta({ 'Situação': 'ativa' }), linhaConta({ 'Situação': ' pendente ' })];
  assert.equal(gs.visContarPendentes_(linhas, indiceContas()), 2);
});

test('bloqueio: 5 falhas bloqueiam, login certo limpa', () => {
  const cache = cacheFalso();
  for (let i = 1; i <= 4; i++) {
    assert.equal(gs.visRegistrarFalha_(cache, 'ana'), i);
    assert.equal(gs.visBloqueado_(cache, 'ana'), false);
  }
  assert.equal(gs.visRegistrarFalha_(cache, 'ana'), 5);
  assert.equal(gs.visBloqueado_(cache, 'ana'), true);
  assert.equal(gs.visBloqueado_(cache, 'bia'), false);
  gs.visLimparFalhas_(cache, 'ana');
  assert.equal(gs.visBloqueado_(cache, 'ana'), false);
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/visitas-gs.test.js`
Expected: FAIL nos testes novos (`gs.visUsuarioValido_ is not a function` etc.).

- [ ] **Step 3: Implementar no `.gs`**

(a) Depois de `var VIS_MIN_SENHA = 12;`, acrescente:

```js
/* ---------- contas das recepcionistas (spec 14) ---------- */
var VIS_ABA_CONTAS = 'RECEPCIONISTAS';
var VIS_COLUNAS_CONTAS = ['Usuário', 'Nome', 'Situação', 'Hash', 'Sal', 'Temporária', 'Criado em', 'Aprovado em', 'Último acesso'];
var VIS_PROP_SEGREDO = 'VISITAS_SEGREDO';
var VIS_ITERACOES = 1000;
var VIS_MAX_FALHAS = 5;
var VIS_BLOQUEIO_S = 900;
var VIS_MAX_PENDENTES = 20;
var VIS_FUSO_MS = 3 * 3600000; /* Brasilia, -03:00 fixo (sem horario de verao desde 2019) */
var VIS_MSG_SESSAO = 'Sua sessão terminou. Entre de novo.';
/* sem 0/O/o, 1/l/I */
var VIS_TEMP_ALFABETO = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789';
var VISITAS_PDVS = ['Zona Sul RP', 'Centro RP'];
```

(b) Depois de `visHash_`, acrescente:

```js
/* ---------- contas e sessao: helpers puros (spec 14.5) ---------- */
function visNormUsuario_(s) { return String(s === null || s === undefined ? '' : s).trim().toLowerCase(); }
function visUsuarioValido_(s) { return /^[a-z0-9][a-z0-9._-]{2,29}$/.test(String(s === null || s === undefined ? '' : s)); }
/* mesmas regras e mensagens de assets/visitas.js (paridade testada) */
function visValidarSenha_(senha, usuario) {
  var s = String(senha === null || senha === undefined ? '' : senha);
  if (s.length < 8 || s.length > 72) return 'A senha precisa ter de 8 a 72 caracteres.';
  if (s.toLowerCase() === visNormUsuario_(usuario)) return 'A senha não pode ser igual ao usuário.';
  return '';
}
function visValidarCadastro_(req) {
  var nome = visTexto_(req.nome);
  if (!nome) throw new VisFalha('invalido', 'Informe seu nome completo.', 'nome');
  var usuario = visNormUsuario_(req.usuario);
  if (!visUsuarioValido_(usuario)) throw new VisFalha('invalido', 'Use de 3 a 30 letras minúsculas, números, ponto, hífen ou sublinhado.', 'usuario');
  var msg = visValidarSenha_(req.senha, usuario);
  if (msg) throw new VisFalha('invalido', msg, 'senha');
  return { nome: nome, usuario: usuario, senha: String(req.senha) };
}
/* sem bcrypt no Apps Script: SHA-256 iterado encarece tentativas se a planilha vazar */
function visHashSenha_(senha, sal) {
  var h = visHash_(String(sal) + String(senha));
  for (var i = 1; i < VIS_ITERACOES; i++) h = visHash_(h + sal);
  return h;
}
function visExpiraMeiaNoite_(agoraMs) {
  var dia = Math.floor((agoraMs - VIS_FUSO_MS) / 86400000);
  return (dia + 1) * 86400000 + VIS_FUSO_MS;
}
/* o comeco do hash entra na assinatura: trocar a senha derruba as sessoes abertas */
function visAssinar_(usuario, expira, hash, segredo) {
  return Utilities.base64EncodeWebSafe(
    Utilities.computeHmacSha256Signature(usuario + '.' + expira + '.' + String(hash).slice(0, 12), segredo));
}
function visCriarToken_(usuario, hash, agoraMs, segredo) {
  var expira = visExpiraMeiaNoite_(agoraMs);
  return { token: usuario + '.' + expira + '.' + visAssinar_(usuario, expira, hash, segredo), expira: expira };
}
/* o usuario pode ter ponto: le de tras para frente */
function visLerToken_(token) {
  var partes = String(token === null || token === undefined ? '' : token).split('.');
  if (partes.length < 3) return null;
  var assinatura = partes.pop(), expira = partes.pop(), usuario = partes.join('.');
  if (!assinatura || !/^\d{1,15}$/.test(expira) || !visUsuarioValido_(usuario)) return null;
  return { usuario: usuario, expira: Number(expira), assinatura: assinatura };
}
/* tempo nao depende de onde esta a primeira diferenca */
function visIguais_(a, b) {
  a = String(a); b = String(b);
  var dif = a.length ^ b.length;
  for (var i = 0; i < Math.max(a.length, b.length); i++) dif |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return dif === 0;
}
function visConferirToken_(token, conta, agoraMs, segredo) {
  var p = visLerToken_(token);
  if (!p || !conta || p.usuario !== conta.usuario || agoraMs >= p.expira) return false;
  return visIguais_(p.assinatura, visAssinar_(p.usuario, p.expira, conta.hash, segredo));
}
function visSessaoOk_(token, conta, agoraMs, segredo, permitirTemporaria) {
  if (!conta || conta.situacao !== 'ativa' || (conta.temporaria && !permitirTemporaria)) return false;
  return visConferirToken_(token, conta, agoraMs, segredo);
}
function visSenhaTemporaria_(bytes) {
  var s = '';
  for (var i = 0; i < 9; i++) {
    if (i === 3 || i === 6) s += '-';
    s += VIS_TEMP_ALFABETO.charAt(bytes[i] % VIS_TEMP_ALFABETO.length);
  }
  return s;
}
function visContaDeLinha_(l, ix) {
  return {
    usuario: String(l[ix['Usuário']]).trim(),
    nome: String(l[ix['Nome']]),
    situacao: String(l[ix['Situação']]).trim(),
    hash: String(l[ix['Hash']]).trim(),
    sal: String(l[ix['Sal']]).trim(),
    temporaria: String(l[ix['Temporária']]).trim() === 'sim',
    criadoEm: String(l[ix['Criado em']]),
    aprovadoEm: String(l[ix['Aprovado em']]),
    ultimoAcesso: String(l[ix['Último acesso']])
  };
}
/* o que o dashboard ve de cada conta: nunca hash nem sal */
function visContaPublica_(c, visitas30) {
  return {
    usuario: c.usuario, nome: c.nome, situacao: c.situacao, temporaria: c.temporaria,
    criadoEm: c.criadoEm, ultimoAcesso: c.ultimoAcesso, visitas30: visitas30 || 0
  };
}
function visContarPendentes_(linhas, ix) {
  return linhas.filter(function (l) { return String(l[ix['Situação']]).trim() === 'pendente'; }).length;
}
/* tentativas erradas por usuario, no CacheService */
function visChaveFalhas_(usuario) { return 'vis.falhas.' + usuario; }
function visBloqueado_(cache, usuario) { return Number(cache.get(visChaveFalhas_(usuario)) || 0) >= VIS_MAX_FALHAS; }
function visRegistrarFalha_(cache, usuario) {
  var n = Number(cache.get(visChaveFalhas_(usuario)) || 0) + 1;
  cache.put(visChaveFalhas_(usuario), String(n), VIS_BLOQUEIO_S);
  return n;
}
function visLimparFalhas_(cache, usuario) { cache.remove(visChaveFalhas_(usuario)); }
```

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test tests/*.test.js`
Expected: PASS em todos os testes novos. A única falha aceita é a anotada na Task 1 (`visResumo_ é igual ao resumo do cliente`).

- [ ] **Step 5: Commit**

```bash
git add docs/apps-script-visitas.gs tests/visitas-gs.test.js
git commit -m "feat(visitas): regras puras de conta, senha e sessao no Web App

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Contas no Web App (aba `RECEPCIONISTAS`, login, cadastro, ações do comercial)

**Files:**
- Modify: `docs/apps-script-visitas.gs`
- Modify: `tests/visitas-gs.test.js` (só o teste de roteamento abaixo)

**Interfaces:**
- Consumes: tudo o que a Task 2 produz.
- Produces:
  - Planilha:
    - `visLerAba_(nome, colunas) → { aba, indice, largura, linhas }`, com `visLer_()` e `visLerContas_()` por cima
    - `visAnexar_(t, valores)`, `visAtualizarLinha_(t, i /* indice em t.linhas */, valores)`
    - `visAcharConta_(t, usuario) → { i, conta } | null`
  - `visSegredo_() → string`, `visAgoraBr_() → 'dd/MM/yyyy HH:mm:ss'`
  - `visSessao_(req, permitirTemporaria) → conta`, ou lança `VisFalha('sessao', VIS_MSG_SESSAO)`. **Quem chama é a Task 4.**
  - Ações públicas:
    - `entrar { usuario, senha }` → `{ sessao, expira, nome, usuario, trocarSenha }`
    - `cadastrar { nome, usuario, senha }` → `{ ok: true }`
    - `trocarSenha { sessao, novaSenha }` → mesmo formato do `entrar`
  - Ações do comercial (com `senha`):
    - `contas` → `{ contas: [visContaPublica_] }`. Nesta tarefa `visitas30` fica 0; a Task 4 preenche.
    - `aprovar`, `recusar`, `desativar`, `reativar` → `{ usuario, situacao }`
    - `redefinirSenha` → `{ usuario, senhaTemporaria }`

- [ ] **Step 1: Teste do roteamento que falha**

Acrescente em `tests/visitas-gs.test.js`:

```js
test('roteador: ações do comercial exigem a senha antes de qualquer leitura', () => {
  const props = { getProperty: () => 'senha-forte-123' };
  const ctx = carregar('docs/apps-script-visitas.gs', {
    Utilities: UtilitiesFalso,
    PropertiesService: { getScriptProperties: () => props },
    SpreadsheetApp: { getActiveSpreadsheet: () => { throw new Error('não devia ler a planilha'); } }
  });
  ['listar', 'contas', 'aprovar', 'recusar', 'desativar', 'reativar', 'redefinirSenha'].forEach((acao) => {
    assert.throws(() => ctx.visRoteador_({ acao, senha: 'errada', usuario: 'ana' }), (e) => e.codigo === 'senha', acao);
  });
});
```

Run: `node --test tests/visitas-gs.test.js`
Expected: FAIL. Em `contas`, `aprovar` etc. o erro é `'interno'` (ação desconhecida) em vez de `'senha'`.

- [ ] **Step 2: Generalizar a leitura de abas**

Substitua `visAba_`, `visCabecalho_` e `visLer_` por:

```js
/* ---------- planilha ---------- */
function visGarantirAba_(nome, colunas) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var aba = ss.getSheetByName(nome) || ss.insertSheet(nome);
  if (aba.getLastRow() === 0) {
    aba.getRange(1, 1, 1, colunas.length).setValues([colunas]).setFontWeight('bold');
    aba.setFrozenRows(1);
  }
  return aba;
}

function visCabecalho_(aba, colunas, nome) {
  var largura = aba.getLastColumn();
  var cab = aba.getRange(1, 1, 1, largura).getDisplayValues()[0].map(function (c) { return String(c).trim(); });
  var ix = {};
  cab.forEach(function (n, i) { if (n && !(n in ix)) ix[n] = i; });
  colunas.forEach(function (n) {
    if (!(n in ix)) throw new VisFalha('coluna', 'Coluna "' + n + '" não encontrada na aba ' + nome + '.');
  });
  return { indice: ix, largura: largura };
}

function visLerAba_(nome, colunas) {
  var aba = visGarantirAba_(nome, colunas);
  var cab = visCabecalho_(aba, colunas, nome);
  var n = Math.max(aba.getLastRow() - 1, 0);
  return {
    aba: aba,
    indice: cab.indice,
    largura: cab.largura,
    linhas: n ? aba.getRange(2, 1, n, cab.largura).getDisplayValues() : []
  };
}
function visLer_() { return visLerAba_(VIS_ABA, VIS_COLUNAS); }
function visLerContas_() { return visLerAba_(VIS_ABA_CONTAS, VIS_COLUNAS_CONTAS); }

/* formato texto: a planilha nao converte data/hora/CPF e mantem o valor exato */
function visAnexar_(t, valores) {
  var linha = [];
  for (var i = 0; i < t.largura; i++) linha.push('');
  Object.keys(valores).forEach(function (nome) { linha[t.indice[nome]] = visNeutralizar_(valores[nome]); });
  var faixa = t.aba.getRange(t.aba.getLastRow() + 1, 1, 1, t.largura);
  faixa.setNumberFormat('@');
  faixa.setValues([linha]);
}
function visAtualizarLinha_(t, i, valores) {
  Object.keys(valores).forEach(function (nome) {
    t.aba.getRange(i + 2, t.indice[nome] + 1).setNumberFormat('@').setValue(visNeutralizar_(valores[nome]));
  });
}
function visAcharConta_(t, usuario) {
  for (var i = 0; i < t.linhas.length; i++) {
    if (String(t.linhas[i][t.indice['Usuário']]).trim() === usuario) return { i: i, conta: visContaDeLinha_(t.linhas[i], t.indice) };
  }
  return null;
}
function visAgoraBr_() { return Utilities.formatDate(new Date(), VIS_FUSO, 'dd/MM/yyyy HH:mm:ss'); }
/* gerado na primeira vez; nunca sai do servidor */
function visSegredo_() {
  var props = PropertiesService.getScriptProperties();
  var s = props.getProperty(VIS_PROP_SEGREDO);
  if (!s) {
    s = Utilities.getUuid() + Utilities.getUuid();
    props.setProperty(VIS_PROP_SEGREDO, s);
  }
  return s;
}
```

Em `visRegistrar_`, troque o trecho dentro de `visComLock_` que monta `linha` e grava a faixa por uma chamada a `visAnexar_(t, valores);`. Mantenha `var achou = visCpfRepetido_(...)` antes e `return achou;` depois.

- [ ] **Step 3: Ações de conta**

Acrescente, depois de `visListar_`:

```js
/* ---------- contas (spec 14.2 e 14.5) ---------- */
function visResultadoSessao_(conta, hash) {
  var tk = visCriarToken_(conta.usuario, hash, Date.now(), visSegredo_());
  return { sessao: tk.token, expira: tk.expira, nome: conta.nome, usuario: conta.usuario, trocarSenha: !!conta.temporaria };
}

function visSessao_(req, permitirTemporaria) {
  var p = visLerToken_(req.sessao);
  if (!p) throw new VisFalha('sessao', VIS_MSG_SESSAO);
  var a = visAcharConta_(visLerContas_(), p.usuario);
  if (!a || !visSessaoOk_(String(req.sessao), a.conta, Date.now(), visSegredo_(), permitirTemporaria)) {
    throw new VisFalha('sessao', VIS_MSG_SESSAO);
  }
  return a.conta;
}

function visEntrar_(req) {
  var usuario = visNormUsuario_(req.usuario), senha = String(req.senha === null || req.senha === undefined ? '' : req.senha);
  var falhou = function () { throw new VisFalha('credenciais', 'Usuário ou senha incorretos.'); };
  if (!visUsuarioValido_(usuario)) { visHashSenha_(senha, 'sem-conta'); falhou(); }
  var cache = CacheService.getScriptCache();
  if (visBloqueado_(cache, usuario)) throw new VisFalha('bloqueado', 'Muitas tentativas. Tente de novo em 15 minutos.');
  var a = visAcharConta_(visLerContas_(), usuario);
  /* conta inexistente tambem calcula o hash: mesma demora */
  var hash = visHashSenha_(senha, a ? a.conta.sal : 'sem-conta');
  if (!a || !visIguais_(hash, a.conta.hash)) {
    if (visRegistrarFalha_(cache, usuario) >= VIS_MAX_FALHAS) {
      throw new VisFalha('bloqueado', 'Muitas tentativas. Tente de novo em 15 minutos.');
    }
    falhou();
  }
  visLimparFalhas_(cache, usuario);
  if (a.conta.situacao === 'pendente') throw new VisFalha('pendente', 'Seu cadastro está aguardando aprovação do comercial.');
  if (a.conta.situacao !== 'ativa') throw new VisFalha('desativada', 'Seu acesso foi desativado. Fale com o comercial.');
  visComLock_(function () {
    var t = visLerContas_(), achou = visAcharConta_(t, usuario);
    if (achou) visAtualizarLinha_(t, achou.i, { 'Último acesso': visAgoraBr_() });
  });
  return visResultadoSessao_(a.conta, a.conta.hash);
}

function visCadastrar_(req) {
  var d = visValidarCadastro_(req);
  var sal = Utilities.getUuid(), hash = visHashSenha_(d.senha, sal);
  return visComLock_(function () {
    var t = visLerContas_();
    if (visAcharConta_(t, d.usuario)) throw new VisFalha('invalido', 'Esse usuário já existe.', 'usuario');
    if (visContarPendentes_(t.linhas, t.indice) >= VIS_MAX_PENDENTES) {
      throw new VisFalha('limite', 'Muitos cadastros aguardando aprovação. Fale com o comercial.');
    }
    visAnexar_(t, {
      'Usuário': d.usuario, 'Nome': d.nome, 'Situação': 'pendente', 'Hash': hash, 'Sal': sal,
      'Temporária': 'não', 'Criado em': visAgoraBr_(), 'Aprovado em': '', 'Último acesso': ''
    });
    return { ok: true };
  });
}

function visTrocarSenha_(req) {
  var conta = visSessao_(req, true);
  var nova = String(req.novaSenha === null || req.novaSenha === undefined ? '' : req.novaSenha);
  var msg = visValidarSenha_(nova, conta.usuario);
  if (msg) throw new VisFalha('invalido', msg, 'novaSenha');
  if (visIguais_(visHashSenha_(nova, conta.sal), conta.hash)) {
    throw new VisFalha('invalido', 'A nova senha precisa ser diferente da atual.', 'novaSenha');
  }
  var sal = Utilities.getUuid(), hash = visHashSenha_(nova, sal);
  visComLock_(function () {
    var t = visLerContas_(), a = visAcharConta_(t, conta.usuario);
    if (!a) throw new VisFalha('sessao', VIS_MSG_SESSAO);
    visAtualizarLinha_(t, a.i, { 'Hash': hash, 'Sal': sal, 'Temporária': 'não' });
  });
  conta.temporaria = false;
  return visResultadoSessao_(conta, hash);
}

/* ---------- acoes do comercial sobre as contas (spec 14.5) ---------- */
function visNaoEncontrada_() { return new VisFalha('nao_encontrada', 'Recepcionista não encontrada.'); }

function visContas_() {
  var t = visLerContas_();
  return { contas: t.linhas.map(function (l) { return visContaPublica_(visContaDeLinha_(l, t.indice), 0); }) };
}

function visMudarSituacao_(req, de, para) {
  var usuario = visNormUsuario_(req.usuario);
  return visComLock_(function () {
    var t = visLerContas_(), a = visAcharConta_(t, usuario);
    if (!a || a.conta.situacao !== de) throw visNaoEncontrada_();
    var valores = { 'Situação': para };
    if (de === 'pendente') valores['Aprovado em'] = visAgoraBr_();
    visAtualizarLinha_(t, a.i, valores);
    return { usuario: usuario, situacao: para };
  });
}

function visRecusar_(req) {
  var usuario = visNormUsuario_(req.usuario);
  return visComLock_(function () {
    var t = visLerContas_(), a = visAcharConta_(t, usuario);
    if (!a || a.conta.situacao !== 'pendente') throw visNaoEncontrada_();
    t.aba.deleteRow(a.i + 2);
    return { usuario: usuario, situacao: 'recusada' };
  });
}

function visRedefinirSenha_(req) {
  var usuario = visNormUsuario_(req.usuario);
  var bytes = [];
  for (var i = 0; i < 9; i++) bytes.push(parseInt(Utilities.getUuid().slice(0, 2), 16));
  var temp = visSenhaTemporaria_(bytes), sal = Utilities.getUuid(), hash = visHashSenha_(temp, sal);
  return visComLock_(function () {
    var t = visLerContas_(), a = visAcharConta_(t, usuario);
    if (!a || a.conta.situacao === 'pendente') throw visNaoEncontrada_();
    visAtualizarLinha_(t, a.i, { 'Hash': hash, 'Sal': sal, 'Temporária': 'sim' });
    return { usuario: usuario, senhaTemporaria: temp };
  });
}
```

- [ ] **Step 4: Roteador**

Substitua `visRoteador_` por:

```js
function visRoteador_(req) {
  switch (req.acao) {
    case 'entrar': return visEntrar_(req);
    case 'cadastrar': return visCadastrar_(req);
    case 'trocarSenha': return visTrocarSenha_(req);
    case 'registrar': return visRegistrar_(req);
    case 'dia': return visDia_(req);
    case 'excluir': return visExcluir_(req);
  }
  /* daqui para baixo: so com a senha do dashboard */
  visConferirSenha_(req.senha);
  switch (req.acao) {
    case 'listar': return visListar_(req);
    case 'contas': return visContas_();
    case 'aprovar': return visMudarSituacao_(req, 'pendente', 'ativa');
    case 'recusar': return visRecusar_(req);
    case 'desativar': return visMudarSituacao_(req, 'ativa', 'desativada');
    case 'reativar': return visMudarSituacao_(req, 'desativada', 'ativa');
    case 'redefinirSenha': return visRedefinirSenha_(req);
    default: throw new VisFalha('interno', 'Ação desconhecida.');
  }
}
```

`registrar`, `dia` e `excluir` ainda não pedem sessão. A Task 4 fecha isso.

- [ ] **Step 5: Rodar e ver passar**

Run: `node --test tests/*.test.js`
Expected: PASS, salvo a falha conhecida da Task 1.

- [ ] **Step 6: Commit**

```bash
git add docs/apps-script-visitas.gs tests/visitas-gs.test.js
git commit -m "feat(visitas): aba RECEPCIONISTAS, login, cadastro e acoes do comercial no Web App

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Visitas com sessão, PDV, dona e só Ribeirão Preto no Web App

**Files:**
- Modify: `docs/apps-script-visitas.gs`
- Modify: `tests/visitas-gs.test.js`

**Interfaces:**
- Consumes: `visSessao_`, `visLerContas_`, `visAnexar_`, `visContaDeLinha_`, `visContaPublica_` (Task 3) e `V.empreendimentosVisitas`, `V.PDVS`, `V.resumirVisita(v, usuario)` (Task 1).
- Produces:
  - `VIS_COLUNAS` v3 (Global Constraints) e `VISITAS_EMPREENDIMENTOS` só com RP.
  - `visValidar_(req, hoje, agoraMin)`: exige `pdv` primeiro (`campo:'pdv'`) e devolve `pdv`.
  - `visDeLinha_` ganha `pdv` e `lancadoPor` (o usuário).
  - `visResumo_(v, usuario)` igual a `V.resumirVisita(v, usuario)`.
  - `visCpfRepetido_(linhas, ix, v)` compara CPF + **PDV** + data.
  - `visPodeExcluir_(l, ix, id, usuario, hoje) → boolean`.
  - `visContarPorUsuario_(linhas, ix, desde) → { [usuario]: n }`.
  - `visNomesPorUsuario_(t) → { [usuario]: nome }`.
  - `visRegistrar_(req, conta)`, `visDia_(req, conta)`, `visExcluir_(req, conta)`.
  - `listar` com `lancadoPor` = nome; `contas` com `visitas30`.

- [ ] **Step 1: Atualizar os testes**

Em `tests/visitas-gs.test.js`:

(a) Troque o objeto `base` por:

```js
const base = {
  pdv: 'Zona Sul RP', empreendimento: 'Village Park', data: HOJE, hora: '14:35', tipo: 'esp',
  cliente: '  Mariana   Souza Lima ', cpf: '529.982.247-25', telefone: '(19) 98765-4321', corretor: 'Rui', gerente: ''
};
```

(b) Substitua o teste `lista de empreendimentos do .gs bate com a do config.js` por:

```js
test('empreendimentos do .gs são só os de Ribeirão Preto do config.js, e os PDVs batem', () => {
  const cfg = carregar('assets/config.js', { window: {} });
  const rp = V.empreendimentosVisitas(cfg.window.CITIES);
  assert.equal(rp.length, 4);
  assert.deepEqual(plano(gs.VISITAS_EMPREENDIMENTOS), rp);
  assert.deepEqual(plano(gs.VISITAS_PDVS), V.PDVS);
});
```

(c) No teste `visValidar_ devolve a visita completa normalizada...`, o resultado esperado passa a ser:

```js
  assert.deepEqual(v, {
    pdv: 'Zona Sul RP', empreendimento: 'Village Park', cidade: 'Ribeirão Preto', data: HOJE, hora: '14:35', tipo: 'esp',
    cliente: 'Mariana Souza Lima', cpf: '52998224725', telefone: '19987654321', imobiliaria: '', corretor: 'Rui', gerente: ''
  });
```

(d) No teste `visValidar_ recusa empreendimento e tipo fora da lista`, acrescente:

```js
  assert.throws(() => gs.visValidar_({ ...base, empreendimento: 'Alta Vista Mangará' }, HOJE, AGORA), recusa('empreendimento'));
  assert.throws(() => gs.visValidar_({ ...base, pdv: '' }, HOJE, AGORA), recusa('pdv'));
  assert.throws(() => gs.visValidar_({ ...base, pdv: 'Zona Norte RP' }, HOJE, AGORA), recusa('pdv'));
  assert.throws(() => gs.visValidar_({ ...base, pdv: 'Outro', empreendimento: 'Outro' }, HOJE, AGORA), recusa('pdv'));
```

(e) Substitua o teste `VIS_COLUNAS na ordem da spec 13.2` por:

```js
test('VIS_COLUNAS na ordem da spec 14.4 (sem Token)', () => {
  assert.deepEqual(plano(gs.VIS_COLUNAS), ['ID', 'Registrado em', 'Data', 'Horário', 'PDV', 'Empreendimento', 'Cidade', 'Tipo',
    'Nome do cliente', 'CPF', 'Telefone', 'Imobiliária', 'Corretor', 'Gerente de vendas', 'Lançado por', 'Excluída']);
});
```

(f) Substitua os testes `visDeLinha_ devolve a visita completa`, `visResumo_ é igual ao resumo do cliente...` e `visCpfRepetido_...` por:

```js
const COMPLETA = {
  id: 'V1', data: '2026-10-09', hora: '14:30', pdv: 'Centro RP', empreendimento: 'Village Park', cidade: 'Ribeirão Preto', tipo: 'imob',
  cliente: 'Mariana Souza', cpf: '52998224725', telefone: '19987654321', imobiliaria: 'Imob Ápice', corretor: 'Rui', gerente: 'Gil',
  lancadoPor: 'recep.um'
};

test('visDeLinha_ devolve a visita completa com PDV e usuário de quem lançou', () => {
  const l = linha({
    'ID': 'V1', 'Registrado em': '09/10/2026 14:35:00', 'Data': '09/10/2026', 'Horário': '14:30', 'PDV': 'Centro RP',
    'Empreendimento': 'Village Park', 'Cidade': 'Ribeirão Preto', 'Tipo': 'Imobiliária',
    'Nome do cliente': 'Mariana Souza', 'CPF': '52998224725', 'Telefone': '19987654321',
    'Imobiliária': 'Imob Ápice', 'Corretor': 'Rui', 'Gerente de vendas': 'Gil', 'Lançado por': ' recep.um ', 'Excluída': '0'
  });
  assert.deepEqual(plano(gs.visDeLinha_(l, indice())), COMPLETA);
});

test('visResumo_ é igual ao resumo do cliente, marca "minha" e não expõe dados pessoais nem usuário', () => {
  assert.deepEqual(plano(gs.visResumo_(COMPLETA, 'recep.um')), V.resumirVisita(COMPLETA, 'recep.um'));
  assert.deepEqual(plano(gs.visResumo_(COMPLETA, 'recep.dois')), V.resumirVisita(COMPLETA, 'recep.dois'));
  assert.equal(gs.visResumo_(COMPLETA, 'recep.um').minha, true);
  const texto = JSON.stringify(gs.visResumo_(COMPLETA, 'recep.dois'));
  ['52998224725', '19987654321', 'Souza', 'Gil', 'recep.um'].forEach((s) => assert.ok(!texto.includes(s), s));
});

test('visCpfRepetido_: mesmo CPF, mesmo PDV e mesma data, só linhas ativas', () => {
  const ix = indice();
  const linhas = [
    linha({ 'CPF': '52998224725', 'PDV': 'Zona Sul RP', 'Empreendimento': 'Village Park', 'Data': '09/10/2026', 'Excluída': '0' }),
    linha({ 'CPF': '11144477735', 'PDV': 'Zona Sul RP', 'Empreendimento': 'Village Park', 'Data': '09/10/2026', 'Excluída': '1' })
  ];
  const v = (cpf, pdv, data, emp) => ({ cpf, pdv, data, empreendimento: emp || 'Village Gaia' });
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('52998224725', 'Zona Sul RP', '2026-10-09')), true);
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('52998224725', 'Centro RP', '2026-10-09', 'Village Park')), false);
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('52998224725', 'Zona Sul RP', '2026-10-08')), false);
  assert.equal(gs.visCpfRepetido_(linhas, ix, v('11144477735', 'Zona Sul RP', '2026-10-09')), false);
  assert.equal(gs.visCpfRepetido_([], ix, v('52998224725', 'Zona Sul RP', '2026-10-09')), false);
});

test('visPodeExcluir_: só a dona, só no dia do registro, só linha ativa', () => {
  const ix = indice();
  const l = linha({ 'ID': 'V9', 'Registrado em': '09/10/2026 10:00:00', 'Lançado por': 'recep.um', 'Excluída': '0' });
  assert.equal(gs.visPodeExcluir_(l, ix, 'V9', 'recep.um', '2026-10-09'), true);
  assert.equal(gs.visPodeExcluir_(l, ix, 'V9', 'recep.dois', '2026-10-09'), false);
  assert.equal(gs.visPodeExcluir_(l, ix, 'V9', 'recep.um', '2026-10-10'), false);
  assert.equal(gs.visPodeExcluir_(l, ix, 'V8', 'recep.um', '2026-10-09'), false);
  assert.equal(gs.visPodeExcluir_(l, ix, 'V9', '', '2026-10-09'), false);
  const excluida = linha({ 'ID': 'V9', 'Registrado em': '09/10/2026 10:00:00', 'Lançado por': 'recep.um', 'Excluída': '1' });
  assert.equal(gs.visPodeExcluir_(excluida, ix, 'V9', 'recep.um', '2026-10-09'), false);
});

test('visContarPorUsuario_ conta visitas ativas desde a data, por quem lançou', () => {
  const ix = indice();
  const linhas = [
    linha({ 'Data': '09/10/2026', 'Lançado por': 'recep.um', 'Excluída': '0' }),
    linha({ 'Data': '01/10/2026', 'Lançado por': 'recep.um', 'Excluída': '0' }),
    linha({ 'Data': '09/10/2026', 'Lançado por': 'recep.um', 'Excluída': '1' }),
    linha({ 'Data': '09/10/2026', 'Lançado por': 'constructor', 'Excluída': '0' }),
    linha({ 'Data': '01/08/2026', 'Lançado por': 'recep.dois', 'Excluída': '0' })
  ];
  assert.deepEqual(plano(gs.visContarPorUsuario_(linhas, ix, '2026-09-10')), { 'recep.um': 2, constructor: 1 });
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/visitas-gs.test.js`
Expected: FAIL nos testes novos (colunas, PDV, `visPodeExcluir_ is not a function` etc.).

- [ ] **Step 3: Implementar**

(a) Constantes:

```js
var VIS_COLUNAS = ['ID', 'Registrado em', 'Data', 'Horário', 'PDV', 'Empreendimento', 'Cidade', 'Tipo',
  'Nome do cliente', 'CPF', 'Telefone', 'Imobiliária', 'Corretor', 'Gerente de vendas', 'Lançado por', 'Excluída'];
/* spec 14.1: por enquanto so Ribeirao Preto */
var VISITAS_EMPREENDIMENTOS = [
  { nome: 'Village Park', cidade: 'Ribeirão Preto' },
  { nome: 'Village Gaia', cidade: 'Ribeirão Preto' },
  { nome: 'Reserva Direcional Jardim Botânico', cidade: 'Ribeirão Preto' },
  { nome: 'Direcional Conquista Clube Ipiranga', cidade: 'Ribeirão Preto' }
];
```

(b) Em `visValidar_`, como **primeiras** linhas:

```js
  var pdv = String(req.pdv || '');
  if (VISITAS_PDVS.indexOf(pdv) < 0) throw new VisFalha('invalido', 'Escolha o PDV.', 'pdv');
```

e no objeto de retorno acrescente `pdv: pdv`.

(c) `visDeLinha_` ganha `pdv: String(l[ix['PDV']]),` e `lancadoPor: String(l[ix['Lançado por']]).trim()`.

(d) Substitua `visResumo_` por:

```js
/* spec 14.5: so isto sai nas respostas da recepcao; o usuario de quem lancou nao sai */
function visResumo_(v, usuario) {
  return {
    id: v.id, data: v.data, hora: v.hora, pdv: v.pdv || '', empreendimento: v.empreendimento, tipo: v.tipo,
    primeiroNome: visPrimeiroNome_(v.cliente), imobiliaria: v.imobiliaria || '', corretor: v.corretor || '',
    minha: !!usuario && v.lancadoPor === usuario
  };
}
```

(e) Em `visCpfRepetido_`, troque `String(l[ix['Empreendimento']]) === v.empreendimento` por `String(l[ix['PDV']]) === v.pdv`. Atualize o comentário: "mesmo CPF, mesmo PDV e mesma data".

(f) Acrescente depois de `visSugestoes_`:

```js
/* spec 14.3: exclui so a propria visita, registrada hoje */
function visPodeExcluir_(l, ix, id, usuario, hoje) {
  return !!usuario && String(l[ix['ID']]) === id && visAtiva_(l, ix) &&
    String(l[ix['Lançado por']]).trim() === usuario && visBrParaIso_(l[ix['Registrado em']]) === hoje;
}
function visContarPorUsuario_(linhas, ix, desde) {
  var qtd = Object.create(null);
  linhas.forEach(function (l) {
    if (!visAtiva_(l, ix) || visBrParaIso_(l[ix['Data']]) < desde) return;
    var u = String(l[ix['Lançado por']]).trim();
    if (u) qtd[u] = (qtd[u] || 0) + 1;
  });
  return qtd;
}
function visNomesPorUsuario_(t) {
  var nomes = Object.create(null);
  t.linhas.forEach(function (l) { var c = visContaDeLinha_(l, t.indice); if (c.usuario) nomes[c.usuario] = c.nome; });
  return nomes;
}
```

(g) Ações. Substitua `visRegistrar_`, `visDia_`, `visExcluir_` e `visListar_`, e atualize `visContas_`:

```js
function visRegistrar_(req, conta) {
  var agora = new Date();
  var hoje = Utilities.formatDate(agora, VIS_FUSO, 'yyyy-MM-dd');
  var hm = Utilities.formatDate(agora, VIS_FUSO, 'HH:mm').split(':');
  var v = visValidar_(req, hoje, (+hm[0]) * 60 + (+hm[1]));
  v.id = 'V' + agora.getTime() + Utilities.getUuid().slice(0, 4).toUpperCase();
  v.lancadoPor = conta.usuario;
  var valores = {
    'ID': v.id,
    'Registrado em': Utilities.formatDate(agora, VIS_FUSO, 'dd/MM/yyyy HH:mm:ss'),
    'Data': visIsoParaBr_(v.data),
    'Horário': v.hora,
    'PDV': v.pdv,
    'Empreendimento': v.empreendimento,
    'Cidade': v.cidade,
    'Tipo': VIS_TIPOS[v.tipo],
    'Nome do cliente': v.cliente,
    'CPF': v.cpf,
    'Telefone': v.telefone,
    'Imobiliária': v.imobiliaria,
    'Corretor': v.corretor,
    'Gerente de vendas': v.gerente,
    'Lançado por': conta.usuario,
    'Excluída': '0'
  };
  var repetido = visComLock_(function () {
    var t = visLer_();
    var achou = visCpfRepetido_(t.linhas, t.indice, v);
    visAnexar_(t, valores);
    return achou;
  });
  return { visita: visResumo_(v, conta.usuario), cpfRepetido: repetido };
}

function visDia_(req, conta) {
  var pdv = String(req.pdv || '');
  if (VISITAS_PDVS.indexOf(pdv) < 0) throw new VisFalha('invalido', 'Escolha o PDV.', 'pdv');
  var data = String(req.data || '');
  if (!visDataValida_(data)) throw new VisFalha('invalido', 'Data inválida.', 'data');
  var t = visLer_(), ix = t.indice, visitas = [];
  t.linhas.forEach(function (l) {
    if (!visAtiva_(l, ix)) return;
    var v = visDeLinha_(l, ix);
    if (v.pdv === pdv && v.data === data) visitas.push(visResumo_(v, conta.usuario));
  });
  var desde = visSomarDias_(visHoje_(), -VIS_DIAS_SUGESTOES);
  return {
    visitas: visitas,
    sugestoes: {
      imobiliarias: visSugestoes_(t.linhas, ix, desde, 'Imobiliária'),
      corretores: visSugestoes_(t.linhas, ix, desde, 'Corretor'),
      gerentes: visSugestoes_(t.linhas, ix, desde, 'Gerente de vendas')
    }
  };
}

/* spec 14.3: mesma resposta para id inexistente, de outra pessoa ou de outro dia */
function visExcluir_(req, conta) {
  var id = String(req.id || '');
  var hoje = visHoje_();
  return visComLock_(function () {
    var t = visLer_(), ix = t.indice;
    for (var i = 0; i < t.linhas.length; i++) {
      if (String(t.linhas[i][ix['ID']]) !== id) continue;
      if (!visPodeExcluir_(t.linhas[i], ix, id, conta.usuario, hoje)) break;
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
  var nomes = visNomesPorUsuario_(visLerContas_());
  var t = visLer_(), ix = t.indice, visitas = [];
  t.linhas.forEach(function (l) {
    if (!visAtiva_(l, ix)) return;
    var v = visDeLinha_(l, ix);
    if (v.data < de || v.data > ate) return;
    v.lancadoPor = nomes[v.lancadoPor] || v.lancadoPor;
    visitas.push(v);
  });
  return { visitas: visitas };
}
```

`visContas_` passa a ser:

```js
function visContas_() {
  var t = visLerContas_(), v = visLer_();
  var qtd = visContarPorUsuario_(v.linhas, v.indice, visSomarDias_(visHoje_(), -29));
  return {
    contas: t.linhas.map(function (l) {
      var c = visContaDeLinha_(l, t.indice);
      return visContaPublica_(c, qtd[c.usuario] || 0);
    })
  };
}
```

(h) No roteador, as três ações da recepção passam a exigir sessão:

```js
    case 'registrar': return visRegistrar_(req, visSessao_(req, false));
    case 'dia': return visDia_(req, visSessao_(req, false));
    case 'excluir': return visExcluir_(req, visSessao_(req, false));
```

(i) Substitua `testeVisitas` por:

```js
/* ---------- conferencia manual (spec 14.5) ---------- */
function testeVisitas() {
  var usuario = 'teste.visitas', senha = 'teste-' + Utilities.getUuid().slice(0, 8), sal = Utilities.getUuid();
  var hash = visHashSenha_(senha, sal);
  visComLock_(function () {
    var t = visLerContas_();
    if (visAcharConta_(t, usuario)) throw new Error('Ja existe a conta ' + usuario + ': apague a linha na aba ' + VIS_ABA_CONTAS + '.');
    visAnexar_(t, {
      'Usuário': usuario, 'Nome': 'TESTE - pode ignorar', 'Situação': 'ativa', 'Hash': hash, 'Sal': sal,
      'Temporária': 'não', 'Criado em': visAgoraBr_(), 'Aprovado em': visAgoraBr_(), 'Último acesso': ''
    });
  });
  try {
    var s = visEntrar_({ usuario: usuario, senha: senha });
    Logger.log('entrar: ok, sessao ate ' + new Date(s.expira));
    var conta = visSessao_({ sessao: s.sessao }, false);
    var hoje = visHoje_();
    var r = visRegistrar_({
      pdv: VISITAS_PDVS[0], empreendimento: VISITAS_EMPREENDIMENTOS[0].nome, data: hoje,
      hora: Utilities.formatDate(new Date(), VIS_FUSO, 'HH:mm'), tipo: 'imob', imobiliaria: 'TESTE - pode ignorar',
      cliente: 'TESTE - pode ignorar', cpf: '52998224725', telefone: '19999999999', corretor: 'TESTE', gerente: ''
    }, conta);
    Logger.log('registrar: ' + JSON.stringify(r.visita) + ' cpfRepetido=' + r.cpfRepetido);
    var d = visDia_({ pdv: VISITAS_PDVS[0], data: hoje }, conta);
    Logger.log('dia: ' + d.visitas.length + ' visita(s) no PDV ' + VISITAS_PDVS[0]);
    Logger.log('excluir: ' + JSON.stringify(visExcluir_({ id: r.visita.id }, conta)));
    Logger.log('listar: ' + visListar_({ de: hoje, ate: hoje }).visitas.length + ' visita(s) ativas hoje');
    Logger.log('contas: ' + visContas_().contas.length + ' conta(s)');
  } finally {
    visComLock_(function () {
      var t = visLerContas_(), a = visAcharConta_(t, usuario);
      if (a) t.aba.deleteRow(a.i + 2);
    });
    Logger.log('conta de teste apagada');
  }
}
```

(j) Atualize o cabeçalho do arquivo:
- "COMO PUBLICAR", passo 4: troque por "Se ja existir uma aba VISITAS de uma versao anterior, apague ou renomeie antes: a v3 cria as abas VISITAS e RECEPCIONISTAS com o cabecalho certo."
- Passo 5: "Selecione testeVisitas > Executar > confira o log (cria e apaga uma conta de teste)."
- Bloco "EMPREENDIMENTOS": diga que `VISITAS_EMPREENDIMENTOS` tem só os de Ribeirão Preto do `window.CITIES` e que `VISITAS_PDVS` precisa bater com `PDVS` de `assets/visitas.js`; os testes falham se divergirem.
- Novo bloco "CONTAS": as recepcionistas se cadastram em /visitas-recepcao e o comercial aprova em /visitas-recepcao-adm. A senha fica só como hash (aba RECEPCIONISTAS) e a sessao vale ate a meia-noite. O segredo da sessao (Script Property VISITAS_SEGREDO) e criado sozinho; apagar essa propriedade derruba todas as sessoes.

(k) Remova o que ficou sem uso: a coluna `Token` e `visHash_(token)`. `visHash_` continua, porque `visHashSenha_` usa.

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test tests/*.test.js`
Expected: PASS em todos os testes, inclusive o de `visResumo_` que falhava desde a Task 1.

- [ ] **Step 5: Commit**

```bash
git add docs/apps-script-visitas.gs tests/visitas-gs.test.js
git commit -m "feat(visitas): sessao obrigatoria, PDV, lancado por e so Ribeirao Preto no Web App

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Cliente da API e modo demonstração v3 (`assets/visitas-api.js`)

**Files:**
- Modify: `assets/visitas-api.js`

**Interfaces:**
- Consumes: `V.empreendimentosVisitas`, `V.PDVS`, `V.validarVisita`, `V.resumirVisita(v, usuario)`, `V.validarCadastro`, `V.validarSenha`, `V.usuarioValido`, `V.normalizarUsuario`, `V.filtrar`.
- Produces: `VisitasAPI.criar({ url, senha?: () => string, sessao?: () => string }) → { chamar(acao, params), demo }`.
  - Quando `sessao()` não está vazio, o corpo leva `sessao`.
  - Erros: `{ codigo, mensagem, campo }`. Mensagens fixas para `rede`, `ocupado`, `coluna`, `interno`, `formato` e `sessao`.
  - No demo, contas fixas:
    - `recep.um` e `recep.dois`: ativas;
    - `troca.demo`: ativa, com senha temporária;
    - `desativada.demo`: desativada;
    - `pendente.demo`: pendente.
  - Qualquer outro usuário válido, com senha de 8+ caracteres, entra como conta ativa nova.

- [ ] **Step 1: Mensagem de sessão e envio da sessão**

Em `MENSAGENS`, acrescente `sessao: 'Sua sessão terminou. Entre de novo.'`.

Em `criar`:

```js
    var sessao = opcoes.sessao || function () { return ''; };
```

Em `chamar`: o ramo demo passa a ser `if (demo) return chamarDemo(acao, params || {}, sessao());`. No ramo real, depois de colocar a senha:

```js
      var t = sessao();
      if (t) corpo.sessao = t;
```

- [ ] **Step 2: Reescrever o modo demonstração**

Troque tudo entre `/* ---------- modo demonstracao ---------- */` e `/* ---------- Web App (spec 4.1) ---------- */` por:

```js
  /* ---------- modo demonstracao (spec 14.7) ---------- */
  var IMOBS_DEMO = ['Imobiliária Exemplo A', 'Imobiliária Exemplo B', 'Imobiliária Exemplo C', 'Imobiliária Exemplo D'];
  var CORRETORES_DEMO = ['Corretor Exemplo 1', 'Corretor Exemplo 2', 'Corretor Exemplo 3'];
  var GERENTES_DEMO = ['Gerente Exemplo 1', 'Gerente Exemplo 2'];
  var CLIENTES_DEMO = [
    ['Cliente Exemplo Ana', '52998224725', '19998765432'],
    ['Cliente Exemplo Bruno', '11144477735', '1932458890'],
    ['Cliente Exemplo Carla', '12345678909', '16998112233'],
    ['Cliente Exemplo Diego', '98765432100', '15998765432']
  ];
  var CONTAS_DEMO = [
    { usuario: 'recep.um', nome: 'Recepcionista Exemplo Um', situacao: 'ativa', temporaria: false, criadoEm: '01/09/2026 09:00:00', ultimoAcesso: '' },
    { usuario: 'recep.dois', nome: 'Recepcionista Exemplo Dois', situacao: 'ativa', temporaria: false, criadoEm: '02/09/2026 09:00:00', ultimoAcesso: '' },
    { usuario: 'troca.demo', nome: 'Recepcionista Exemplo Três', situacao: 'ativa', temporaria: true, criadoEm: '03/09/2026 09:00:00', ultimoAcesso: '' },
    { usuario: 'desativada.demo', nome: 'Recepcionista Exemplo Quatro', situacao: 'desativada', temporaria: false, criadoEm: '04/09/2026 09:00:00', ultimoAcesso: '' },
    { usuario: 'pendente.demo', nome: 'Recepcionista Exemplo Cinco', situacao: 'pendente', temporaria: false, criadoEm: '10/10/2026 09:12:00', ultimoAcesso: '' }
  ];
  var LANCADORES_DEMO = ['recep.um', 'recep.dois'];
  var memoria = null;
  var contas = null;

  function rnd(a, b, c) {
    var x = Math.sin(a * 127.1 + b * 311.7 + c * 74.7) * 43758.5453;
    return x - Math.floor(x);
  }
  function escolher(lista, r) { return lista[Math.floor(r * lista.length)]; }
  function agoraBr() {
    var d = new Date();
    return pad(d.getDate()) + '/' + pad(d.getMonth() + 1) + '/' + d.getFullYear() + ' ' + V.horaLocal(d) + ':00';
  }
  function fimDoDia() { var d = new Date(); d.setHours(24, 0, 0, 0); return d.getTime(); }
  function gerarDemo(hoje, emps) {
    var out = [], seq = 0;
    for (var d = 0; d < 30; d++) {
      var data = V.somarDias(hoje, -d);
      emps.forEach(function (e, ei) {
        var n = Math.floor(rnd(ei, d, 1) * 7);
        for (var k = 0; k < n; k++) {
          var r = rnd(ei, d, 10 + k);
          var tipo = r < 0.4 ? 'esp' : r < 0.65 ? 'house' : 'imob';
          var min = 8 * 60 + Math.floor(rnd(ei, d, 30 + k) * 11 * 60);
          var cli = escolher(CLIENTES_DEMO, rnd(ei, d, 70 + k));
          seq++;
          out.push({
            id: 'D' + seq, data: data, hora: pad(Math.floor(min / 60)) + ':' + pad(min % 60),
            pdv: escolher(V.PDVS, rnd(ei, d, 150 + k)),
            empreendimento: e.nome, cidade: e.cidade, tipo: tipo,
            cliente: cli[0], cpf: cli[1], telefone: cli[2],
            imobiliaria: tipo === 'imob' ? escolher(IMOBS_DEMO, rnd(ei, d, 50 + k)) : '',
            corretor: escolher(CORRETORES_DEMO, rnd(ei, d, 90 + k)),
            gerente: rnd(ei, d, 110 + k) < 0.6 ? escolher(GERENTES_DEMO, rnd(ei, d, 130 + k)) : '',
            lancadoPor: escolher(LANCADORES_DEMO, rnd(ei, d, 170 + k))
          });
        }
      });
    }
    return out;
  }
  function memoriaDemo() {
    if (!memoria) memoria = gerarDemo(V.dataLocalIso(new Date()), V.empreendimentosVisitas(raiz.CITIES || []));
    if (!contas) contas = copia(CONTAS_DEMO);
    return memoria;
  }
  function contaDemo(usuario) { return contas.filter(function (c) { return c.usuario === usuario; })[0] || null; }
  function sessaoDemo(token, permitirTemporaria) {
    var m = /^demo\.(.+)$/.exec(token || ''), c = m && contaDemo(m[1]);
    if (!c || c.situacao !== 'ativa' || (c.temporaria && !permitirTemporaria)) throw falha('sessao');
    return c;
  }
  function resultadoSessao(c) {
    return { ok: true, sessao: 'demo.' + c.usuario, expira: fimDoDia(), nome: c.nome, usuario: c.usuario, trocarSenha: !!c.temporaria };
  }
  function contaAdm(usuario, de) {
    var c = contaDemo(V.normalizarUsuario(usuario));
    if (!c || (de && c.situacao !== de)) throw falha('nao_encontrada', 'Recepcionista não encontrada.');
    return c;
  }
  function senhaTempDemo() {
    var a = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789', s = '';
    for (var i = 0; i < 9; i++) { if (i === 3 || i === 6) s += '-'; s += a.charAt(Math.floor(Math.random() * a.length)); }
    return s;
  }

  function chamarDemo(acao, p, token) {
    var lista = memoriaDemo();
    return new Promise(function (ok) { setTimeout(ok, 300); }).then(function () {
      var c, usuario;
      if (acao === 'entrar') {
        usuario = V.normalizarUsuario(p.usuario);
        if (!V.usuarioValido(usuario) || String(p.senha || '').length < 8) throw falha('credenciais', 'Usuário ou senha incorretos.');
        c = contaDemo(usuario);
        if (!c) { c = { usuario: usuario, nome: 'Recepcionista ' + usuario, situacao: 'ativa', temporaria: false, criadoEm: agoraBr(), ultimoAcesso: '' }; contas.push(c); }
        if (c.situacao === 'pendente') throw falha('pendente', 'Seu cadastro está aguardando aprovação do comercial.');
        if (c.situacao !== 'ativa') throw falha('desativada', 'Seu acesso foi desativado. Fale com o comercial.');
        c.ultimoAcesso = agoraBr();
        return resultadoSessao(c);
      }
      if (acao === 'cadastrar') {
        var vc = V.validarCadastro({ nome: p.nome, usuario: p.usuario, senha: p.senha, confirmacao: p.senha });
        if (!vc.ok) throw falha('invalido', vc.erros[vc.primeiro], vc.primeiro);
        usuario = V.normalizarUsuario(p.usuario);
        if (contaDemo(usuario)) throw falha('invalido', 'Esse usuário já existe.', 'usuario');
        contas.push({ usuario: usuario, nome: V.normalizarTexto(p.nome), situacao: 'pendente', temporaria: false, criadoEm: agoraBr(), ultimoAcesso: '' });
        return { ok: true };
      }
      if (acao === 'trocarSenha') {
        c = sessaoDemo(token, true);
        var msg = V.validarSenha(p.novaSenha, c.usuario);
        if (msg) throw falha('invalido', msg, 'novaSenha');
        c.temporaria = false;
        return resultadoSessao(c);
      }
      if (acao === 'registrar') {
        c = sessaoDemo(token, false);
        var f = V.validarVisita(p);
        if (!f.ok) throw falha('invalido', f.erros[f.primeiro], f.primeiro);
        var emp = V.empreendimentosVisitas(raiz.CITIES || []).filter(function (e) { return e.nome === p.empreendimento; })[0];
        if (!emp) throw falha('invalido', 'Escolha o empreendimento.', 'empreendimento');
        var v = {
          id: 'D' + Date.now(), data: p.data, hora: p.hora, pdv: p.pdv, empreendimento: emp.nome, cidade: emp.cidade, tipo: p.tipo,
          cliente: V.normalizarTexto(p.cliente), cpf: V.soDigitos(p.cpf), telefone: V.soDigitos(p.telefone),
          imobiliaria: p.tipo === 'imob' ? V.normalizarTexto(p.imobiliaria) : '',
          corretor: V.normalizarTexto(p.corretor), gerente: V.normalizarTexto(p.gerente), lancadoPor: c.usuario,
          registradoEm: V.dataLocalIso(new Date())
        };
        var repetido = lista.some(function (x) { return x.cpf === v.cpf && x.pdv === v.pdv && x.data === v.data; });
        lista.push(v);
        return { ok: true, visita: V.resumirVisita(v, c.usuario), cpfRepetido: repetido };
      }
      if (acao === 'dia') {
        c = sessaoDemo(token, false);
        return {
          ok: true,
          visitas: lista.filter(function (v) { return v.pdv === p.pdv && v.data === p.data; })
            .map(function (v) { return V.resumirVisita(v, c.usuario); }),
          sugestoes: { imobiliarias: IMOBS_DEMO.slice(), corretores: CORRETORES_DEMO.slice(), gerentes: GERENTES_DEMO.slice() }
        };
      }
      if (acao === 'excluir') {
        c = sessaoDemo(token, false);
        var hoje = V.dataLocalIso(new Date());
        for (var i = 0; i < lista.length; i++) {
          if (lista[i].id === p.id && lista[i].lancadoPor === c.usuario && lista[i].registradoEm === hoje) {
            lista.splice(i, 1);
            return { ok: true, id: p.id };
          }
        }
        throw falha('nao_encontrada', 'Não foi possível excluir este lançamento.');
      }
      /* acoes do comercial: no demo qualquer senha vale */
      if (acao === 'listar') {
        return {
          ok: true,
          visitas: copia(V.filtrar(lista, { de: p.de, ate: p.ate })).map(function (v) {
            var dono = contaDemo(v.lancadoPor);
            v.lancadoPor = dono ? dono.nome : v.lancadoPor;
            delete v.registradoEm;
            return v;
          })
        };
      }
      if (acao === 'contas') {
        var desde = V.somarDias(V.dataLocalIso(new Date()), -29);
        return {
          ok: true,
          contas: contas.map(function (x) {
            var n = lista.filter(function (v) { return v.lancadoPor === x.usuario && v.data >= desde; }).length;
            return { usuario: x.usuario, nome: x.nome, situacao: x.situacao, temporaria: x.temporaria, criadoEm: x.criadoEm, ultimoAcesso: x.ultimoAcesso, visitas30: n };
          })
        };
      }
      if (acao === 'aprovar') { c = contaAdm(p.usuario, 'pendente'); c.situacao = 'ativa'; return { ok: true, usuario: c.usuario, situacao: c.situacao }; }
      if (acao === 'recusar') {
        c = contaAdm(p.usuario, 'pendente');
        contas.splice(contas.indexOf(c), 1);
        return { ok: true, usuario: c.usuario, situacao: 'recusada' };
      }
      if (acao === 'desativar') { c = contaAdm(p.usuario, 'ativa'); c.situacao = 'desativada'; return { ok: true, usuario: c.usuario, situacao: c.situacao }; }
      if (acao === 'reativar') { c = contaAdm(p.usuario, 'desativada'); c.situacao = 'ativa'; return { ok: true, usuario: c.usuario, situacao: c.situacao }; }
      if (acao === 'redefinirSenha') {
        c = contaAdm(p.usuario);
        if (c.situacao === 'pendente') throw falha('nao_encontrada', 'Recepcionista não encontrada.');
        c.temporaria = true;
        return { ok: true, usuario: c.usuario, senhaTemporaria: senhaTempDemo() };
      }
      throw falha('interno');
    });
  }
```

Notas:
- `registradoEm` é interno do demo. Visitas geradas não têm esse campo, então não podem ser excluídas, como acontece com visitas antigas no servidor.
- No demo, a senha temporária usa `Math.random`. Isso é aceitável porque nada é gravado.

- [ ] **Step 3: Conferir**

Run: `node --check assets/visitas-api.js && node --test tests/*.test.js`
Expected: sem erro de sintaxe e todos os testes passando. Este arquivo não tem testes próprios: o comportamento do demo é conferido no navegador nas Tasks 6 e 7.

- [ ] **Step 4: Commit**

```bash
git add assets/visitas-api.js
git commit -m "feat(visitas): API envia a sessao e modo demonstracao com contas e PDV

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Recepção com login, PDV e empreendimento no popup

**Files:**
- Modify: `visitas-recepcao.html`
- Rewrite: `assets/visitas-recepcao-app.js`

**Interfaces:**
- Consumes: `VisitasAPI.criar({ url, sessao })` e as ações `entrar`, `cadastrar`, `trocarSenha`, `registrar`, `dia`, `excluir` (Task 5). Também usa `V.sessaoValida`, `V.validarCadastro`, `V.validarSenha`, `V.normalizarUsuario`, `V.empreendimentosVisitas`, `V.PDVS`, `V.primeiroNome` (Task 1).
- Produces: a página `/visitas-recepcao` conforme spec §14.2 e §14.3 e os quadros `Login*`, `Main`, `Popup*` e `RecepcaoCelular`.
- localStorage:
  - `visitas.sessao = { token, expira, nome, usuario, trocar }`
  - `visitas.pdv`
  - Apaga `visitas.emp` e `visitas.tokens`.

- [ ] **Step 1: HTML. Topo, acesso e PDV**

Em `visitas-recepcao.html`:

(a) No `.hero-txt`, o `<p>` ganha `id="hero-sub"`. Depois do `<img>` do logo, dentro de `.hero-in`, acrescente:

```html
    <div class="hero-user" id="hero-user" hidden>
      <span class="dica">Olá, <strong id="ola"></strong></span>
      <button type="button" class="btn" id="sair">Sair</button>
    </div>
```

(b) Logo depois de `</header>`, acrescente a seção de acesso:

```html
<section class="acesso" id="acesso" hidden>
  <div class="card acesso-card">
    <p class="aviso-demo" id="acesso-demo" hidden>Modo demonstração: qualquer usuário e senha de 8 ou mais caracteres entram. Teste também <strong>pendente.demo</strong>, <strong>desativada.demo</strong> e <strong>troca.demo</strong>.</p>

    <form id="t-entrar" class="acesso-tela" novalidate>
      <span class="step">Entrar</span>
      <h2>Olá! Entre com o seu usuário</h2>
      <p class="msg" id="a-msg" role="alert" hidden></p>
      <label class="campo">
        <span class="lab">Usuário</span>
        <input class="inp" id="a-usuario" type="text" autocomplete="username" autocapitalize="none" spellcheck="false" placeholder="ex.: maria.silva">
      </label>
      <label class="campo">
        <span class="lab">Senha</span>
        <input class="inp" id="a-senha" type="password" autocomplete="current-password">
      </label>
      <button type="submit" class="btn btn-p" id="a-entrar">Entrar</button>
      <p class="acesso-link"><span class="dica">Primeiro acesso?</span> <button type="button" class="link" id="a-ir-cadastro">Criar conta</button></p>
      <p class="dica">Esqueceu a senha? Peça ao comercial para gerar uma senha temporária.</p>
    </form>

    <form id="t-cadastro" class="acesso-tela" novalidate hidden>
      <span class="step">Criar conta</span>
      <h2>Cadastro de recepcionista</h2>
      <p class="dica">Depois de enviar, o comercial precisa aprovar o seu acesso.</p>
      <label class="campo">
        <span class="lab">Nome completo</span>
        <input class="inp" id="c-nome" type="text" maxlength="80" autocomplete="name" aria-describedby="e-c-nome">
        <span class="erro-campo" id="e-c-nome" hidden></span>
      </label>
      <label class="campo">
        <span class="lab">Usuário</span>
        <input class="inp" id="c-usuario" type="text" maxlength="30" autocomplete="username" autocapitalize="none" spellcheck="false" placeholder="ex.: maria.silva" aria-describedby="d-c-usuario e-c-usuario">
        <span class="dica" id="d-c-usuario">Letras minúsculas, números, ponto, hífen ou sublinhado. De 3 a 30 caracteres.</span>
        <span class="erro-campo" id="e-c-usuario" hidden></span>
      </label>
      <div class="linha">
        <label class="campo">
          <span class="lab">Senha</span>
          <input class="inp" id="c-senha" type="password" autocomplete="new-password" aria-describedby="e-c-senha">
          <span class="erro-campo" id="e-c-senha" hidden></span>
        </label>
        <label class="campo">
          <span class="lab">Confirmar senha</span>
          <input class="inp" id="c-confirmacao" type="password" autocomplete="new-password" aria-describedby="e-c-confirmacao">
          <span class="erro-campo" id="e-c-confirmacao" hidden></span>
        </label>
      </div>
      <span class="dica">Mínimo de 8 caracteres.</span>
      <p class="erro-txt" id="c-erro" role="alert" hidden></p>
      <button type="submit" class="btn btn-p" id="c-enviar">Enviar cadastro</button>
      <button type="button" class="link" id="c-ir-entrar">Já tenho conta · Entrar</button>
    </form>

    <div id="t-enviado" class="acesso-tela acesso-ok" hidden>
      <span class="acesso-ico" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></span>
      <h2>Cadastro enviado</h2>
      <p class="dica">Assim que o comercial aprovar, você já consegue entrar com o usuário <strong id="enviado-usuario"></strong>.</p>
      <button type="button" class="link" id="enviado-voltar">Voltar para Entrar</button>
    </div>

    <form id="t-troca" class="acesso-tela" novalidate hidden>
      <span class="step">Nova senha</span>
      <h2>Crie uma senha nova</h2>
      <p class="dica">Você entrou com uma senha temporária. Escolha a sua senha para continuar.</p>
      <label class="campo">
        <span class="lab">Nova senha</span>
        <input class="inp" id="n-senha" type="password" autocomplete="new-password" aria-describedby="e-n-senha">
        <span class="erro-campo" id="e-n-senha" hidden></span>
      </label>
      <label class="campo">
        <span class="lab">Confirmar nova senha</span>
        <input class="inp" id="n-confirmacao" type="password" autocomplete="new-password" aria-describedby="e-n-confirmacao">
        <span class="erro-campo" id="e-n-confirmacao" hidden></span>
      </label>
      <p class="erro-txt" id="n-erro" role="alert" hidden></p>
      <button type="submit" class="btn btn-p" id="n-salvar">Salvar e continuar</button>
    </form>
  </div>
</section>
```

(c) `<main class="wrap">` vira `<main class="wrap" id="app" hidden>`.

(d) Substitua o card "Passo 1 · Stand" por:

```html
    <div class="card">
      <span class="step">Passo 1 · PDV</span>
      <div class="pdvs" role="radiogroup" aria-label="PDV">
        <button type="button" class="pdv" role="radio" aria-checked="false" data-pdv="Zona Sul RP">Zona Sul RP</button>
        <button type="button" class="pdv" role="radio" aria-checked="false" data-pdv="Centro RP">Centro RP</button>
      </div>
      <p class="dica">Fica salvo neste aparelho. Só troque se mudar de stand.</p>
    </div>
```

(e) O `<p class="tipo-dica">` ganha `id="tipo-dica"`.

(f) No card do contador, troque `id="cont-emp"` de lugar, sem mudar o id: agora ele mostra o PDV. Em "Últimos lançamentos", troque `<span class="dica">deste stand</span>` por `<span class="dica">deste PDV</span>`.

(g) No popup: o `<span class="dica" id="p-emp">` vira `<span class="dica" id="p-pdv">`. Antes de `<span class="sub-step">Cliente</span>`, acrescente:

```html
      <label class="campo">
        <span class="lab">Empreendimento de interesse</span>
        <select class="inp" id="f-emp" aria-describedby="e-f-emp"></select>
        <span class="erro-campo" id="e-f-emp" hidden></span>
      </label>
```

(h) CSS. Acrescente antes de `/* ---------- popup (spec 13.1) ---------- */`:

```css
/* ---------- acesso e PDV (spec 14) ---------- */
.hero-user{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.acesso{display:flex;justify-content:center;padding:2.5rem 1rem 4rem}
.acesso-card{width:100%;max-width:440px}
.acesso-tela{display:flex;flex-direction:column;gap:14px}
.acesso-tela h2{font-size:1.25rem;font-weight:700;letter-spacing:-.3px}
.acesso-tela .linha .campo{flex:1 1 180px}
.acesso-ok{align-items:flex-start}
.acesso-ico{width:44px;height:44px;border-radius:999px;display:flex;align-items:center;justify-content:center;background:var(--ok-bg);color:var(--ok)}
.acesso-link{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.link{background:none;border:0;padding:0 4px;min-height:44px;cursor:pointer;font-weight:500;color:var(--ink);text-decoration:underline;text-underline-offset:3px;align-self:flex-start}
.link:hover{color:var(--red)}
.link:focus-visible{outline:none;box-shadow:var(--foco-forte);border-radius:6px}
.msg{padding:10px 12px;border-radius:9px;border:1px solid;font-size:14px;font-weight:500}
.msg.err{background:var(--err-bg);border-color:var(--err-line);color:var(--err)}
.msg.aviso{background:var(--warn-bg);border-color:var(--warn-line);color:var(--warn)}
.pdvs{display:flex;flex-wrap:wrap;gap:12px}
.pdv{flex:1 1 180px;min-height:56px;border-radius:12px;border:1px solid var(--hair);background:var(--surface);font-weight:700;font-size:1rem;cursor:pointer;transition:border-color .15s,box-shadow .15s}
.pdv:hover{border-color:var(--red)}
.pdv[aria-checked="true"]{border-color:var(--red);background:#FDEEF0;color:var(--red);box-shadow:var(--foco)}
.pdv:focus-visible{outline:none;box-shadow:var(--foco-forte)}
.tipo:disabled{opacity:.5;cursor:not-allowed}
.tipo:disabled:hover{border-color:var(--hair)}
```

- [ ] **Step 2: Reescrever `assets/visitas-recepcao-app.js`**

Conteúdo completo:

```js
/* ============================================================
   VISITAS DA RECEPCAO - interface de /visitas-recepcao
   ------------------------------------------------------------
   Acesso (entrar, criar conta, trocar senha temporaria), PDV
   (Passo 1), cards que abrem o popup de cadastro (Passo 2) e
   contador do dia por PDV. Regras em assets/visitas.js; API em
   assets/visitas-api.js.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md (secoes 13 e 14)
   ============================================================ */
(function () {
  'use strict';

  var V = window.Visitas;
  var CHAVE_SESSAO = 'visitas.sessao';
  var CHAVE_PDV = 'visitas.pdv';
  var CHAVES_ANTIGAS = ['visitas.emp', 'visitas.tokens'];
  var INTERVALO_DIA = 60000;
  var MSG_SESSAO = 'Sua sessão terminou. Entre de novo.';
  var EMPS = V.empreendimentosVisitas(window.CITIES || []);
  var TITULO_TIPO = { esp: 'Espontânea', house: 'Agendada · Corretor house', imob: 'Imobiliária parceira' };
  var ROTULO_CORRETOR = { esp: 'Corretor que atendeu', house: 'Corretor house que agendou', imob: 'Corretor da imobiliária' };
  var SUB = {
    acesso: 'Acesso exclusivo das recepcionistas dos stands.',
    app: 'Escolha o PDV e toque no tipo de visita para registrar o cliente.'
  };
  /* campo da API -> id do input */
  var CAMPOS = {
    empreendimento: 'f-emp', cliente: 'f-cliente', cpf: 'f-cpf', telefone: 'f-telefone', data: 'f-data',
    hora: 'f-hora', imobiliaria: 'f-imob', corretor: 'f-corretor'
  };
  var CAMPOS_CADASTRO = { nome: 'c-nome', usuario: 'c-usuario', senha: 'c-senha', confirmacao: 'c-confirmacao' };
  var TELAS = ['entrar', 'cadastro', 'enviado', 'troca'];
  var FOCO_TELA = { entrar: 'a-usuario', cadastro: 'c-nome', enviado: 'enviado-voltar', troca: 'n-senha' };
  var estado = {
    sessao: null, pdv: '', tipo: null, enviando: false, ultimo: null, timerFaixa: null, seqDia: 0, hojeAplicado: ''
  };
  var api = window.VisitasAPI.criar({
    url: window.VISITAS_APPS_SCRIPT_URL || '',
    sessao: function () { return estado.sessao ? estado.sessao.token : ''; }
  });

  function $(id) { return document.getElementById(id); }
  function hoje() { return V.dataLocalIso(new Date()); }
  function lerLS(chave, padrao) {
    try { var v = localStorage.getItem(chave); return v === null ? padrao : JSON.parse(v); } catch (e) { return padrao; }
  }
  function gravarLS(chave, valor) {
    try { localStorage.setItem(chave, JSON.stringify(valor)); } catch (e) { /* ignora */ }
  }
  function apagarLS(chave) {
    try { localStorage.removeItem(chave); } catch (e) { /* ignora */ }
  }
  function cada(seletor, fn) { Array.prototype.forEach.call(document.querySelectorAll(seletor), fn); }

  /* ---------- erros de campo ---------- */
  function limparErro(id) {
    $(id).setAttribute('aria-invalid', 'false');
    $('e-' + id).textContent = '';
    $('e-' + id).hidden = true;
  }
  function marcarErro(id, msg) {
    $(id).setAttribute('aria-invalid', 'true');
    $('e-' + id).textContent = msg;
    $('e-' + id).hidden = false;
  }
  function ocupado(id, sim, texto) {
    $(id).disabled = sim;
    $(id).textContent = texto;
  }

  /* ---------- sessao (spec 14.2) ---------- */
  function guardarSessao(r) {
    estado.sessao = { token: r.sessao, expira: r.expira, nome: r.nome, usuario: r.usuario, trocar: !!r.trocarSenha };
    gravarLS(CHAVE_SESSAO, estado.sessao);
  }
  function encerrar(msg) {
    estado.sessao = null;
    estado.enviando = false;
    apagarLS(CHAVE_SESSAO);
    if ($('popup').open) $('popup').close();
    esconderFaixa();
    mostrarAcesso('entrar', msg ? { tipo: 'err', texto: msg } : null);
  }
  /* qualquer 'sessao' do servidor volta para o login */
  function tratarSessao(f) {
    if (f && f.codigo === 'sessao') { encerrar(MSG_SESSAO); return true; }
    return false;
  }

  /* ---------- telas de acesso ---------- */
  function mostrarMsg(msg) {
    $('a-msg').className = 'msg ' + (msg ? msg.tipo : '');
    $('a-msg').textContent = msg ? msg.texto : '';
    $('a-msg').hidden = !msg;
  }
  function mostrarAcesso(tela, msg) {
    $('app').hidden = true;
    $('hero-user').hidden = true;
    $('acesso').hidden = false;
    $('acesso-demo').hidden = !api.demo;
    $('hero-sub').textContent = SUB.acesso;
    TELAS.forEach(function (t) { $('t-' + t).hidden = t !== tela; });
    mostrarMsg(msg || null);
    $(FOCO_TELA[tela]).focus();
  }
  function mostrarApp() {
    $('acesso').hidden = true;
    $('app').hidden = false;
    $('hero-user').hidden = false;
    $('hero-sub').textContent = SUB.app;
    $('ola').textContent = V.primeiroNome(estado.sessao.nome) || estado.sessao.usuario;
    $('aviso-demo').hidden = !api.demo;
    estado.hojeAplicado = hoje();
    renderPdv();
    carregarDia();
  }

  function entrar(ev) {
    ev.preventDefault();
    var usuario = V.normalizarUsuario($('a-usuario').value), senha = $('a-senha').value;
    if (!usuario || !senha) { mostrarMsg({ tipo: 'err', texto: 'Informe usuário e senha.' }); return; }
    ocupado('a-entrar', true, 'Entrando…');
    api.chamar('entrar', { usuario: usuario, senha: senha }).then(function (r) {
      $('a-senha').value = '';
      guardarSessao(r);
      if (r.trocarSenha) mostrarAcesso('troca'); else mostrarApp();
    }, function (f) {
      $('a-senha').value = '';
      mostrarMsg({ tipo: f.codigo === 'pendente' ? 'aviso' : 'err', texto: f.mensagem });
      $('a-senha').focus();
    }).then(function () { ocupado('a-entrar', false, 'Entrar'); });
  }

  function cadastrar(ev) {
    ev.preventDefault();
    var d = { nome: $('c-nome').value, usuario: $('c-usuario').value, senha: $('c-senha').value, confirmacao: $('c-confirmacao').value };
    var r = V.validarCadastro(d);
    Object.keys(CAMPOS_CADASTRO).forEach(function (c) { limparErro(CAMPOS_CADASTRO[c]); });
    $('c-erro').hidden = true;
    if (!r.ok) {
      Object.keys(r.erros).forEach(function (c) { marcarErro(CAMPOS_CADASTRO[c], r.erros[c]); });
      $(CAMPOS_CADASTRO[r.primeiro]).focus();
      return;
    }
    var usuario = V.normalizarUsuario(d.usuario);
    ocupado('c-enviar', true, 'Enviando…');
    api.chamar('cadastrar', { nome: d.nome, usuario: usuario, senha: d.senha }).then(function () {
      ['c-nome', 'c-usuario', 'c-senha', 'c-confirmacao'].forEach(function (id) { $(id).value = ''; });
      $('enviado-usuario').textContent = usuario;
      mostrarAcesso('enviado');
    }, function (f) {
      var id = f.codigo === 'invalido' && CAMPOS_CADASTRO[f.campo];
      if (id) { marcarErro(id, f.mensagem); $(id).focus(); return; }
      $('c-erro').textContent = f.mensagem;
      $('c-erro').hidden = false;
    }).then(function () { ocupado('c-enviar', false, 'Enviar cadastro'); });
  }

  function trocarSenha(ev) {
    ev.preventDefault();
    var nova = $('n-senha').value, conf = $('n-confirmacao').value;
    limparErro('n-senha');
    limparErro('n-confirmacao');
    $('n-erro').hidden = true;
    var msg = V.validarSenha(nova, estado.sessao ? estado.sessao.usuario : '');
    if (msg) { marcarErro('n-senha', msg); $('n-senha').focus(); return; }
    if (nova !== conf) { marcarErro('n-confirmacao', 'As senhas não conferem.'); $('n-confirmacao').focus(); return; }
    ocupado('n-salvar', true, 'Salvando…');
    api.chamar('trocarSenha', { novaSenha: nova }).then(function (r) {
      $('n-senha').value = '';
      $('n-confirmacao').value = '';
      guardarSessao(r);
      mostrarApp();
    }, function (f) {
      if (tratarSessao(f)) return;
      if (f.codigo === 'invalido') { marcarErro('n-senha', f.mensagem); $('n-senha').focus(); return; }
      $('n-erro').textContent = f.mensagem;
      $('n-erro').hidden = false;
    }).then(function () { ocupado('n-salvar', false, 'Salvar e continuar'); });
  }

  /* ---------- PDV (spec 14.3) ---------- */
  function renderPdv() {
    cada('.pdv', function (b) { b.setAttribute('aria-checked', b.getAttribute('data-pdv') === estado.pdv ? 'true' : 'false'); });
    cada('.tipo', function (b) { b.disabled = !estado.pdv; });
    $('tipo-dica').textContent = estado.pdv ? 'Toque no tipo para abrir o cadastro da visita.' : 'Escolha o PDV primeiro.';
  }
  function escolherPdv(pdv) {
    if (estado.enviando || pdv === estado.pdv) return;
    estado.pdv = pdv;
    gravarLS(CHAVE_PDV, pdv);
    esconderFaixa();
    renderPdv();
    carregarDia();
  }
  function montarEmpreendimentos() {
    var sel = $('f-emp');
    var vazio = document.createElement('option');
    vazio.value = '';
    vazio.textContent = 'Selecione';
    sel.appendChild(vazio);
    EMPS.forEach(function (e) {
      var o = document.createElement('option');
      o.value = e.nome;
      o.textContent = e.nome;
      sel.appendChild(o);
    });
  }

  /* ---------- popup (spec 13.1 e 14.3) ---------- */
  function limparErros() {
    Object.keys(CAMPOS).forEach(function (c) { limparErro(CAMPOS[c]); });
    $('p-erro').hidden = true;
  }
  function mostrarErro(campo, msg) {
    if (!CAMPOS[campo]) return false;
    marcarErro(CAMPOS[campo], msg);
    return true;
  }
  function atualizarBotao() {
    $('p-registrar').disabled = estado.enviando;
    /* enviando: nao deixa fechar o popup nem perder a resposta */
    $('p-cancelar').disabled = estado.enviando;
    $('p-fechar').disabled = estado.enviando;
    $('p-registrar-txt').textContent = estado.enviando ? 'Registrando…' : 'Registrar visita';
  }
  function aplicarLimitesData(h) {
    $('f-data').max = h;
    $('f-data').min = V.somarDias(h, -7);
  }

  function abrirPopup(tipo) {
    if (estado.enviando || !estado.pdv) return;
    estado.tipo = tipo;
    $('p-tipo').textContent = TITULO_TIPO[tipo];
    $('p-ponto').style.background = V.TIPOS[tipo].cor;
    $('p-pdv').textContent = 'PDV ' + estado.pdv;
    $('rot-corretor').textContent = ROTULO_CORRETOR[tipo];
    $('bloco-imob').hidden = tipo !== 'imob';
    ['f-emp', 'f-cliente', 'f-cpf', 'f-telefone', 'f-imob', 'f-corretor', 'f-gerente'].forEach(function (id) { $(id).value = ''; });
    var h = hoje();
    aplicarLimitesData(h);
    $('f-data').value = h;
    $('f-hora').value = V.horaLocal(new Date());
    limparErros();
    atualizarBotao();
    $('popup').showModal();
    $('f-emp').focus();
  }
  function fecharPopup() {
    if (estado.enviando) return;
    if ($('popup').open) $('popup').close();
  }

  function lerPopup() {
    return {
      pdv: estado.pdv, empreendimento: $('f-emp').value, tipo: estado.tipo,
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
      Object.keys(r.erros).forEach(function (c) {
        /* campo sem input no popup (ex: pdv) vai para a mensagem geral */
        if (!mostrarErro(c, r.erros[c])) { $('p-erro').textContent = r.erros[c]; $('p-erro').hidden = false; }
      });
      if (CAMPOS[r.primeiro]) $(CAMPOS[r.primeiro]).focus();
      return;
    }
    estado.enviando = true;
    atualizarBotao();
    api.chamar('registrar', dados).then(function (resp) {
      estado.enviando = false;
      atualizarBotao();
      fecharPopup();
      var texto = [resp.visita.hora, V.TIPOS[resp.visita.tipo].nome, resp.visita.primeiroNome].join(' · ');
      if (resp.cpfRepetido) {
        mostrarFaixa('aviso', 'Visita registrada. Atenção: este CPF já tinha visita hoje neste PDV.', texto, true);
      } else {
        mostrarFaixa('ok', 'Visita registrada', texto, true);
      }
      estado.ultimo = resp.visita;
      carregarDia();
    }, function (f) {
      if (tratarSessao(f)) return;
      if (f.codigo === 'invalido' && mostrarErro(f.campo, f.mensagem)) {
        $(CAMPOS[f.campo]).focus();
      } else {
        $('p-erro').textContent = f.mensagem;
        $('p-erro').hidden = false;
      }
    }).then(function () {
      estado.enviando = false;
      if ($('popup').open) atualizarBotao();
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

  /* spec 14.3: so a propria visita, registrada hoje (o servidor confere) */
  function excluir(id) {
    return api.chamar('excluir', { id: id }).then(null, function (f) {
      if (tratarSessao(f)) return;
      mostrarFaixa('err', 'Não foi possível excluir este lançamento',
        f.codigo === 'nao_encontrada' ? 'Ele pode já ter sido excluído.' : f.mensagem, false);
    }).then(function () { if (estado.sessao) carregarDia(); });
  }
  function desfazer() {
    var v = estado.ultimo;
    if (!v) return;
    esconderFaixa();
    excluir(v.id);
  }

  /* ---------- contador do dia por PDV (spec 5.3 e 14.3) ---------- */
  function carregarDia() {
    if (!estado.sessao || !estado.pdv) { renderContador([], estado.pdv, hoje()); return; }
    var pdv = estado.pdv, data = hoje();
    var seq = ++estado.seqDia;
    api.chamar('dia', { pdv: pdv, data: data }).then(function (r) {
      if (seq !== estado.seqDia) return;
      var visitas = (r.visitas || []).filter(function (v) { return V.TIPOS[v.tipo]; });
      renderContador(visitas, pdv, data);
      renderSugestoes(r.sugestoes || {});
      $('cont-erro').hidden = true;
    }, function (f) {
      if (seq !== estado.seqDia || tratarSessao(f)) return;
      $('cont-erro').textContent = f.mensagem;
      $('cont-erro').hidden = false;
    });
  }

  function renderContador(visitas, pdv, data) {
    var t = V.totaisPorTipo(visitas);
    $('cont-titulo').textContent = 'Visitas hoje · ' + V.dataCurta(data);
    $('cont-emp').textContent = pdv ? 'PDV ' + pdv : 'Escolha o PDV';
    $('cont-total').textContent = t.total;
    $('cont-total-lab').textContent = t.total === 1 ? 'visita registrada' : 'visitas registradas';
    V.ORDEM_TIPOS.forEach(function (k) {
      $('q-' + k).textContent = t[k];
      $('b-' + k).style.width = (t.total ? Math.round(t[k] / t.total * 100) : 0) + '%';
    });
    var ul = $('ultimos');
    ul.textContent = '';
    V.recentes(visitas, 6).forEach(function (v) { ul.appendChild(itemLista(v, !!v.minha)); });
    $('vazio').textContent = pdv ? 'Nenhuma visita registrada hoje neste PDV.' : 'Escolha o PDV para ver as visitas do dia.';
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
    txt.appendChild(el('span', 'lista-det', (v.empreendimento ? v.empreendimento + ' · ' : '') + V.detalhe(v)));
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

  /* ---------- virada do dia e fim da sessao ---------- */
  /* tablet aberto de um dia pro outro: a sessao acaba a meia-noite */
  function checarVirada() {
    if (document.visibilityState !== 'visible' || !estado.sessao) return;
    if (!V.sessaoValida(estado.sessao, Date.now())) { encerrar(MSG_SESSAO); return; }
    var h = hoje();
    if (estado.hojeAplicado && h !== estado.hojeAplicado && $('popup').open) {
      aplicarLimitesData(h);
      if ($('f-data').value === estado.hojeAplicado) {
        $('f-data').value = h;
        $('f-hora').value = V.horaLocal(new Date());
      }
    }
    estado.hojeAplicado = h;
    if (!$('app').hidden) carregarDia();
  }

  /* ---------- inicio ---------- */
  function iniciar() {
    CHAVES_ANTIGAS.forEach(apagarLS);
    montarEmpreendimentos();
    var pdv = lerLS(CHAVE_PDV, '');
    estado.pdv = V.PDVS.indexOf(pdv) >= 0 ? pdv : '';

    $('t-entrar').addEventListener('submit', entrar);
    $('t-cadastro').addEventListener('submit', cadastrar);
    $('t-troca').addEventListener('submit', trocarSenha);
    $('a-ir-cadastro').addEventListener('click', function () { mostrarAcesso('cadastro'); });
    $('c-ir-entrar').addEventListener('click', function () { mostrarAcesso('entrar'); });
    $('enviado-voltar').addEventListener('click', function () { mostrarAcesso('entrar'); });
    $('c-usuario').addEventListener('change', function () { $('c-usuario').value = V.normalizarUsuario($('c-usuario').value); });
    ['c-nome', 'c-usuario', 'c-senha', 'c-confirmacao', 'n-senha', 'n-confirmacao'].forEach(function (id) {
      $(id).addEventListener('input', function () { limparErro(id); });
    });
    $('sair').addEventListener('click', function () { if (!estado.enviando) encerrar(); });

    cada('.pdv', function (b) { b.addEventListener('click', function () { escolherPdv(b.getAttribute('data-pdv')); }); });
    cada('.tipo', function (b) { b.addEventListener('click', function () { abrirPopup(b.getAttribute('data-tipo')); }); });
    $('p-form').addEventListener('submit', registrar);
    $('p-cancelar').addEventListener('click', fecharPopup);
    $('p-fechar').addEventListener('click', fecharPopup);
    $('popup').addEventListener('cancel', function (ev) { if (estado.enviando) ev.preventDefault(); });
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
    /* soma lancamentos de outro aparelho no mesmo PDV */
    document.addEventListener('visibilitychange', checarVirada);
    setInterval(checarVirada, INTERVALO_DIA);

    var s = lerLS(CHAVE_SESSAO, null);
    if (V.sessaoValida(s, Date.now())) {
      estado.sessao = s;
      if (s.trocar) mostrarAcesso('troca'); else mostrarApp();
    } else {
      apagarLS(CHAVE_SESSAO);
      mostrarAcesso('entrar');
    }
  }

  iniciar();
})();
```

- [ ] **Step 3: Conferir no navegador (modo demo)**

Abra o preview do repo (`.claude/launch.json`, config `portal-do-corretor`) em `/visitas-recepcao?demo=1`. Confira:
1. **Acesso:** sem sessão aparece "Entrar". O topo diz "Acesso exclusivo das recepcionistas dos stands." e o aviso de demo aparece.
2. **Usuário pendente:** `pendente.demo` + `12345678` mostra a mensagem amarela "Seu cadastro está aguardando aprovação do comercial.".
3. **Usuário desativado:** `desativada.demo` + `12345678` mostra a mensagem vermelha de desativado.
4. **Criar conta:**
   - erros por campo (nome vazio, usuário `Ab`, senha curta, confirmação diferente), com foco no primeiro;
   - `recep.um` dá "Esse usuário já existe." no campo usuário;
   - um usuário novo leva à tela "Cadastro enviado" com o usuário em negrito.
5. **Senha temporária:** `troca.demo` + `12345678` mostra "Crie uma senha nova". Salvar `novasenha1` entra na página.
6. **Página logada:**
   - "Olá, Recepcionista" e "Sair" no topo;
   - sem PDV, os cards ficam desabilitados com "Escolha o PDV primeiro.";
   - escolher "Centro RP" marca o botão e o contador mostra "PDV Centro RP".
7. **Popup:**
   - o select lista só os 4 empreendimentos de RP, começa em "Selecione" e o foco vai para ele;
   - registrar sem empreendimento mostra "Escolha o empreendimento." no campo;
   - com tudo certo, a faixa verde aparece e a lista mostra `empreendimento · corretor` com a lixeira.
8. **Lixeira:** só aparece nos lançamentos que acabaram de ser feitos (os gerados pelo demo não têm). Excluir funciona.
9. **Recarregar:** a sessão continua e o PDV fica lembrado.
10. **Sair:** volta para "Entrar".
11. **Celular:** 375 px sem rolagem horizontal; o popup em tela cheia continua funcionando.
12. **Console:** sem erros.

- [ ] **Step 4: Commit**

```bash
git add visitas-recepcao.html assets/visitas-recepcao-app.js
git commit -m "feat(visitas): recepcao com login, cadastro, PDV no passo 1 e empreendimento no popup

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Dashboard com filtro de PDV, colunas novas e aba Recepcionistas

**Files:**
- Modify: `visitas-recepcao-adm.html`
- Modify: `assets/visitas-adm-app.js`

**Interfaces:**
- Consumes: as ações `listar`, `contas`, `aprovar`, `recusar`, `desativar`, `reativar` e `redefinirSenha` (Tasks 4 e 5). Também usa `V.empreendimentosVisitas`, `V.PDVS` e `V.filtrar({ pdv })` (Task 1).
- Produces: `/visitas-recepcao-adm` conforme spec §14.6 e os quadros `Admin` e `AdminRecepcionistas`.

- [ ] **Step 1: HTML**

(a) Dentro de `<main class="wrap" id="app" hidden>`, logo no começo, acrescente a navegação:

```html
  <nav class="abas" aria-label="Seções do dashboard">
    <button type="button" class="aba" id="aba-btn-visitas" aria-current="page">Visitas</button>
    <button type="button" class="aba" id="aba-btn-recep">Recepcionistas <span class="selo num" id="selo-pendentes" hidden>0</span></button>
  </nav>
```

(b) Envolva tudo o que vem depois de `aviso-erro`, do card `.filtros` até a seção "Últimos lançamentos", em `<div id="aba-visitas" class="aba-corpo">…</div>`. A `.aba-corpo` tem `display:flex;flex-direction:column;gap:18px`.

(c) No card de filtros, troque o bloco "Cidade" por:

```html
    <div class="campo">
      <span class="lab" id="lab-pdv">PDV</span>
      <div class="chips" id="pdvs" role="group" aria-labelledby="lab-pdv"></div>
    </div>
```

(d) Tabela "Últimos lançamentos":
- `min-width:1260px`.
- Cabeçalho: `Data · Horário · PDV · Cliente · CPF · Telefone · Empreendimento · Tipo · Imobiliária · Corretor · Gerente · Lançado por`.

(e) Depois de `</div>` de `#aba-visitas`, ainda dentro de `main`, acrescente:

```html
  <div id="aba-recep" class="aba-corpo" hidden>
    <div class="faixa-senha" id="faixa-senha" role="status" hidden>
      <div class="faixa-senha-txt">
        <strong>Senha temporária de <span id="senha-nome"></span></strong>
        <span>Passe para a recepcionista. Ela não será mostrada de novo, e no próximo login ela cria a própria senha.</span>
      </div>
      <code id="senha-temp"></code>
    </div>

    <section class="card" id="bloco-pendentes" hidden>
      <div class="cab"><h2>Aguardando aprovação</h2><span class="dica">Confira se a pessoa é mesmo recepcionista antes de aprovar.</span></div>
      <ul class="pendentes" id="lista-pendentes"></ul>
    </section>

    <section class="card">
      <div class="cab"><h2>Recepcionistas</h2><button type="button" class="btn" id="atualizar-contas">Atualizar</button></div>
      <div class="rolagem">
        <table style="min-width:760px">
          <thead><tr>
            <th scope="col">Nome</th><th scope="col">Usuário</th><th scope="col">Situação</th>
            <th scope="col" class="dir">Visitas (30 dias)</th><th scope="col">Último acesso</th><th scope="col" class="dir">Ações</th>
          </tr></thead>
          <tbody id="tab-contas"></tbody>
        </table>
      </div>
      <p class="vazio" id="sem-contas" hidden>Nenhuma recepcionista aprovada ainda.</p>
    </section>
  </div>
```

(f) CSS. Acrescente antes do `@media (max-width:700px)` final:

```css
/* ---------- abas e recepcionistas (spec 14.6) ---------- */
.abas{display:flex;gap:4px;border-bottom:1px solid var(--hair)}
.aba{display:flex;align-items:center;gap:8px;min-height:44px;padding:0 14px;border:0;border-bottom:2px solid transparent;background:none;color:var(--slate);font-weight:500;font-size:.92rem;cursor:pointer}
.aba[aria-current="page"]{color:var(--ink);font-weight:700;border-bottom-color:var(--red)}
.aba:focus-visible{outline:none;box-shadow:var(--foco-forte)}
.selo{min-width:20px;height:20px;padding:0 6px;border-radius:999px;background:var(--red);color:#fff;font-size:.72rem;font-weight:700;display:inline-flex;align-items:center;justify-content:center}
.aba-corpo{display:flex;flex-direction:column;gap:18px}
.faixa-senha{display:flex;flex-wrap:wrap;align-items:center;gap:12px;padding:12px 14px;border-radius:14px;background:var(--warn-bg);border:1px solid var(--warn-line);color:var(--warn)}
.faixa-senha-txt{flex:1 1 260px;min-width:0;display:flex;flex-direction:column;font-size:.86rem}
.faixa-senha code{font-family:ui-monospace,Menlo,monospace;font-size:1.05rem;font-weight:700;padding:8px 12px;background:#fff;border:1px solid var(--warn-line);border-radius:9px;color:var(--ink)}
.pendentes{list-style:none;margin:0;padding:0}
.pendentes li{display:flex;flex-wrap:wrap;align-items:center;gap:12px;padding:12px 0;border-top:1px dashed var(--hair)}
.pend-txt{flex:1 1 240px;min-width:0;display:flex;flex-direction:column}
.pendentes .btn-p{width:auto;min-height:44px;padding:0 18px}
.badge-ok{background:#EFF9F2;border-color:#C7E7D3;color:#1B7A40}
.badge-off{background:var(--bg);color:#5B6366}
.badge-temp{background:var(--warn-bg);border-color:var(--warn-line);color:var(--warn);margin-left:6px}
.acoes-conta{white-space:nowrap}
.acoes-conta .btn{min-height:36px;font-size:13px;padding:0 12px}
.acoes-conta .btn + .btn{margin-left:6px}
```

- [ ] **Step 2: JS**

Em `assets/visitas-adm-app.js`:

(a) Constantes e estado:

```js
  var EMPS = V.empreendimentosVisitas(window.CITIES || []);
  var PDVS_FILTRO = [['Todos', 'Todos']].concat(V.PDVS.map(function (p) { return [p, p]; }));
  var estado = { senha: '', todas: [], contas: [], aba: 'visitas', periodo: '7', pdv: 'Todos', emp: 'Todos', carregadoEm: null, hoje: V.dataLocalIso(new Date()) };
```

Remova `CIDADES`.

(b) `montarSelectEmp` deixa de filtrar por cidade: remova a linha `if (estado.cidade !== 'Todas' ...) return;`.

(c) `filtroAtual`:

```js
  function filtroAtual() {
    var iv = V.intervalo(estado.periodo, estado.hoje);
    return {
      iv: iv,
      visitas: V.filtrar(estado.todas, { de: iv.de, ate: iv.ate, pdv: estado.pdv, empreendimento: estado.emp }),
      lista: EMPS.filter(function (e) { return estado.emp === 'Todos' || e.nome === estado.emp; })
    };
  }
```

(d) Em `render`, troque `marcarChips($('cidades'), estado.cidade);` por `marcarChips($('pdvs'), estado.pdv);`.

(e) Em `renderRecentes`, a ordem das células passa a ser:

```js
      celula(tr, V.dataCurta(v.data), 'num');
      celula(tr, v.hora, 'forte num');
      celula(tr, v.pdv || '—');
      celula(tr, v.cliente, 'forte');
      celula(tr, V.formatarCpf(v.cpf), 'num');
      celula(tr, V.formatarTelefone(v.telefone), 'num');
      celula(tr, v.empreendimento);
      /* (badge do tipo, igual) */
      celula(tr, v.imobiliaria || '—', 'suave');
      celula(tr, v.corretor || '—');
      celula(tr, v.gerente || '—', 'suave');
      celula(tr, v.lancadoPor || '—', 'suave');
```

(f) Abas e contas. Acrescente antes de `/* ---------- inicio ---------- */`:

```js
  /* ---------- abas (spec 14.6) ---------- */
  function mostrarAba(aba) {
    estado.aba = aba;
    $('aba-visitas').hidden = aba !== 'visitas';
    $('aba-recep').hidden = aba !== 'recep';
    $('aba-btn-visitas').setAttribute('aria-current', aba === 'visitas' ? 'page' : 'false');
    $('aba-btn-recep').setAttribute('aria-current', aba === 'recep' ? 'page' : 'false');
    $('faixa-senha').hidden = true;
    if (aba === 'recep') carregarContas().catch(tratarErro);
  }

  /* ---------- recepcionistas (spec 14.6) ---------- */
  function curtoBr(s) {
    var m = /^(\d{2})\/(\d{2})\/\d{4} (\d{2}:\d{2})/.exec(String(s || ''));
    return m ? m[1] + '/' + m[2] + ' ' + m[3] : '—';
  }
  function carregarContas() {
    $('atualizar-contas').disabled = true;
    return api.chamar('contas', {}).then(function (r) {
      estado.contas = r.contas || [];
      $('aviso-erro').hidden = true;
      renderContas();
    }).finally(function () { $('atualizar-contas').disabled = false; });
  }
  function acaoConta(acao, c, pergunta) {
    if (pergunta && !window.confirm(pergunta)) return;
    $('faixa-senha').hidden = true;
    api.chamar(acao, { usuario: c.usuario }).then(function (r) {
      if (acao === 'redefinirSenha') {
        $('senha-nome').textContent = c.nome;
        $('senha-temp').textContent = r.senhaTemporaria;
        $('faixa-senha').hidden = false;
      }
      return carregarContas();
    }).catch(tratarErro);
  }
  function botao(texto, cls, fn) {
    var b = el('button', cls, texto);
    b.type = 'button';
    b.addEventListener('click', fn);
    return b;
  }
  function renderContas() {
    var pend = estado.contas.filter(function (c) { return c.situacao === 'pendente'; });
    var outras = estado.contas.filter(function (c) { return c.situacao !== 'pendente'; });
    $('selo-pendentes').textContent = String(pend.length);
    $('selo-pendentes').hidden = pend.length === 0;
    $('bloco-pendentes').hidden = pend.length === 0;
    var ul = $('lista-pendentes');
    ul.textContent = '';
    pend.forEach(function (c) {
      var li = el('li');
      var txt = el('div', 'pend-txt');
      txt.appendChild(el('strong', '', c.nome));
      txt.appendChild(el('span', 'dica', c.usuario + ' · cadastro em ' + curtoBr(c.criadoEm)));
      li.appendChild(txt);
      li.appendChild(botao('Recusar', 'btn', function () { acaoConta('recusar', c, 'Recusar o cadastro de ' + c.nome + '?'); }));
      li.appendChild(botao('Aprovar', 'btn btn-p', function () { acaoConta('aprovar', c); }));
      ul.appendChild(li);
    });
    var tb = $('tab-contas');
    tb.textContent = '';
    outras.forEach(function (c) {
      var tr = el('tr');
      celula(tr, c.nome, 'forte');
      celula(tr, c.usuario, 'suave');
      var td = celula(tr, '');
      td.appendChild(el('span', 'badge ' + (c.situacao === 'ativa' ? 'badge-ok' : 'badge-off'), c.situacao === 'ativa' ? 'Ativa' : 'Desativada'));
      if (c.temporaria) td.appendChild(el('span', 'badge badge-temp', 'Senha temporária'));
      celula(tr, String(c.visitas30 || 0), 'dir num');
      celula(tr, curtoBr(c.ultimoAcesso), 'suave');
      var acoes = celula(tr, '', 'dir acoes-conta');
      acoes.appendChild(botao('Redefinir senha', 'btn', function () {
        acaoConta('redefinirSenha', c, 'Gerar uma senha temporária para ' + c.nome + '? A senha atual deixa de funcionar.');
      }));
      if (c.situacao === 'ativa') {
        acoes.appendChild(botao('Desativar', 'btn', function () { acaoConta('desativar', c, 'Desativar o acesso de ' + c.nome + '?'); }));
      } else {
        acoes.appendChild(botao('Reativar', 'btn', function () { acaoConta('reativar', c); }));
      }
      tb.appendChild(tr);
    });
    $('sem-contas').hidden = outras.length > 0;
  }
```

(g) Em `iniciar`:
- Troque o `montarChips($('cidades'), ...)` por:

```js
    montarChips($('pdvs'), PDVS_FILTRO, function (v) { estado.pdv = v; render(); });
```

- Acrescente os listeners:

```js
    $('aba-btn-visitas').addEventListener('click', function () { mostrarAba('visitas'); });
    $('aba-btn-recep').addEventListener('click', function () { mostrarAba('recep'); });
    $('atualizar-contas').addEventListener('click', function () { carregarContas().catch(tratarErro); });
```

- Depois que a senha for aceita (no `then` de `entrar` e no ramo `if (salva)`), carregue as contas para o selo: `carregarContas().catch(tratarErro);`.
- Em `sair`: `estado.contas = []; mostrarAba('visitas');` antes de `mostrarGate(msg)`. Dentro de `mostrarAba`, não chame `carregarContas` quando `estado.senha` estiver vazio: troque a condição por `if (aba === 'recep' && estado.senha)`.

- [ ] **Step 3: Conferir no navegador (modo demo)**

Em `/visitas-recepcao-adm?demo=1`, entre com qualquer senha. Confira:
1. **Abas:** "Visitas" e "Recepcionistas", com selo "1" (pendente.demo).
2. **Filtros:**
   - chips de PDV (Todos, Zona Sul RP, Centro RP); trocar o PDV muda KPIs, gráfico e tabelas;
   - o seletor de empreendimento lista só os 4 de RP;
   - "Por empreendimento" mostra só os 4.
3. **Tabelas:** "Últimos lançamentos" tem as colunas PDV e "Lançado por" (nomes "Recepcionista Exemplo Um/Dois").
4. **CSV:** o arquivo exportado tem o cabeçalho v3.
5. **Aba Recepcionistas:**
   - "Aguardando aprovação" com pendente.demo;
   - Aprovar move a conta para a tabela e o selo some;
   - Recusar pede confirmação e remove.
6. **Tabela de contas:**
   - "Redefinir senha" pede confirmação e mostra a faixa amarela com `xxx-xxx-xxx`; a faixa some ao trocar de aba;
   - Desativar e Reativar alternam o selo da situação;
   - troca.demo mostra o selo "Senha temporária".
7. **Celular e console:** 375 px sem rolagem horizontal na página (só dentro das tabelas). Console sem erros.

- [ ] **Step 4: Commit**

```bash
git add visitas-recepcao-adm.html assets/visitas-adm-app.js
git commit -m "feat(visitas): dashboard com filtro de PDV, lancado por e aba Recepcionistas

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: README e conferência final

**Files:**
- Modify: `README.md` (seção "Visitas da recepção")

- [ ] **Step 1: README**

Substitua os itens da seção "Visitas da recepção" por:

```markdown
- `/visitas-recepcao`: cada recepcionista entra com usuário e senha próprios.
  - A conta é criada pela própria recepcionista ("Criar conta") e só funciona depois que o comercial aprova no dashboard.
  - A sessão vale até a meia-noite.
  - Ela escolhe o PDV (Zona Sul RP ou Centro RP) e toca no tipo de visita.
  - O popup pede empreendimento (só os de Ribeirão Preto), nome, CPF e telefone do cliente, data e horário, corretor e, no tipo imobiliária, a imobiliária. Gerente de vendas é opcional.
  - Cada visita grava quem lançou; a recepcionista só exclui as próprias visitas do dia. A página nunca recebe CPF, telefone nem nome completo de volta do servidor.
- `/visitas-recepcao-adm`: dashboard do comercial, com senha forte (mínimo de 12 caracteres, Script Property `VISITAS_SENHA` no Apps Script; a senha não fica no repositório).
  - Filtro por PDV.
  - Mostra e exporta CPF e telefone: é dado pessoal (LGPD).
  - Aba **Recepcionistas**: aprovar ou recusar cadastros, desativar ou reativar contas e gerar senha temporária.
- Dados nas abas `VISITAS` e `RECEPCIONISTAS` da planilha de visitas, via Web App (`docs/apps-script-visitas.gs`, instruções de implantação no cabeçalho). Senhas ficam só como hash.
- `window.VISITAS_APPS_SCRIPT_URL` em `assets/config.js` = URL `/exec` do Web App. Vazio (ou `?demo=1`) = **modo demonstração** com dados e contas fictícios na memória da aba (`pendente.demo`, `desativada.demo` e `troca.demo` mostram os outros estados do login).
- Se já existir uma aba `VISITAS` de uma versão anterior, apague ou renomeie antes de publicar: a v3 cria as abas novas com o cabeçalho certo.
- Por enquanto o lançamento atende só Ribeirão Preto. Empreendimento novo de Ribeirão Preto no `config.js` também precisa entrar em `VISITAS_EMPREENDIMENTOS` no `.gs`; o teste de paridade avisa se esquecer.
```

- [ ] **Step 2: Conferência final**

Run: `node --test tests/*.test.js`
Expected: todos passam.

Run: `grep -n "Token\|visitas.tokens\|cidade: 'Campinas'" docs/apps-script-visitas.gs assets/visitas-recepcao-app.js assets/visitas-api.js`
Expected: nada. O único `visitas.tokens` aceito é o de `CHAVES_ANTIGAS` no app da recepção.

Run: `grep -n "Logger.log" docs/apps-script-visitas.gs`
Expected: nenhuma linha loga senha, hash, sal, token, segredo, CPF ou telefone.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(visitas): README da v3 com contas e PDV

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

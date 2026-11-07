# Simulador de Financiamento Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Botão "Simular financiamento" com popup nos dois simuladores associativos e tela dedicada `/simulador-financiamento`, usando o motor CAIXA existente, com cópia dos números para o associativo e PDF.

**Architecture:** Regras puras em `assets/financiamento.js` (testadas no Node) em cima de `MotorCaixa` e de duas regras exportadas do `Match`. O popup é um módulo de DOM (`assets/financiamento-popup.js`) ligado aos dois associativos por um bloco curto de cola; a tela dedicada tem seu próprio app (`assets/financiamento-app.js`). PDF num desenhista único (`assets/financiamento-pdf.js`).

**Tech Stack:** HTML/CSS/JS puro sem build (padrão IIFE + `module.exports`/`window.X`), `node --test`, jsPDF 2.5.1 + jspdf-autotable 3.8.2 por CDN, DM Sans.

**Spec:** `docs/superpowers/specs/2026-11-07-simulador-financiamento-design.md` (ler inteiro antes de começar). Referência visual: canvas https://claude.ai/artifact/KZN7zwgMrwvNi8NNmdzXg2, copiado para `docs/design/simulador-financiamento/fonte/` na Task 5.

## Global Constraints

- Site estático: nada de build, framework, bundler ou dependência nova. Rodar com `python3 -m http.server` na raiz.
- Branch `feat/simulador-financiamento` (sem upstream). Commit por task; nada de push sem o usuário pedir.
- Toda mensagem de commit termina com a linha `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Nenhuma regra do motor CAIXA muda (juros, faixas, subsídio, prazo). `MotorCaixa.simular` é a única fonte de números.
- Copiar para o associativo mexe só em `S.renda`, `S.financiado`, `S.subsidio`, `S.parcFin`.
- Texto: "Financia até", nunca "Cabe financiar". Português do Brasil, valores em `R$ 1.234,56`.
- Seguradora padrão = maior 1ª parcela entre as 3.
- Comprometimento exibido vem de `r.comprometimento` (nunca "30%" fixo).
- Campanha Black Friday: `CAMPANHA_BF = { ativa: true, cidades: ['Ribeirão Preto'] }` em `financiamento.js`.
- Cores do gráfico: PRICE `#E4032B`, SAC `#2563A8`. Prefixo CSS `.fz-`. Tudo animado desliga com `prefers-reduced-motion`.
- Teste já quebrado antes desta branch: `tests/home-paginas.test.js` › "Match de Unidades leva para em-breve.html na home" (196 passam, 1 falha). Não é desta feature; não "consertar" sem o usuário pedir. Toda verificação de suíte aceita exatamente essa falha.

## Review Focus

1. Renda vazia ou zero no associativo ao abrir o popup → campo de renda vazio e focado; "Continuar" não avança com renda ≤ 0. (Task 2: `validar`; Task 5: verificação.)
2. Nascimento inválido (31/02/1990, data futura, menos de 18 anos) → mensagem embaixo do campo, não avança. (Task 2: `lerData` e `validar`.)
3. Unidade sem avaliação na planilha ou planilha fora do ar → campo de valor aparece no passo 1; valor 0 não avança. (Task 2: `validar`; Task 5: verificação.)
4. Copiar por cima de valores já digitados → "Desfazer" volta exatamente os anteriores, inclusive zeros. (Task 6: verificação.)
5. Celular estreito (360px) e teclado → folha rola sem cortar o rodapé; Esc fecha; foco volta ao botão. (Task 5 e Task 7: verificação.)

---

### Task 1: Cronograma no motor CAIXA

**Files:**
- Modify: `assets/motor-caixa.js` (nova função e export em `api`)
- Test: `tests/motor-caixa.test.js` (acrescentar ao fim)

**Interfaces:**
- Produces: `MotorCaixa.cronograma(e, r, codigoSeguradora) → Array<{ mes:Number, data:Date, encargo:Number, amortizacao:Number, juros:Number, mip:Number, dfi:Number, taxaAdm:Number, saldo:Number }>`. `e` = a mesma entrada passada a `simular`; `r` = o resultado sem erro; `codigoSeguradora` = `'14' | '15' | '4'` (MCMV) ou `'14' | '16' | '4'` (SBPE, quando `r.faixa === 'SBPE'`). Devolve `[]` se `r.erro` ou código desconhecido. Valores em reais com 2 casas.

- [ ] **Step 1: Escrever os testes**

```js
test('cronograma: mês 1 e último batem com primeira/ultima de cada seguradora', () => {
  const hoje = new Date(2026, 10, 7);
  const base = { renda: 2800, valor: 220000, nascimento: new Date(1993, 2, 14), municipio: '3543402',
    fgts: true, possuiImovel: false, fatorSocial: true, subsidioAnterior: false, hoje };
  const casos = [
    { ...base, sistema: 'PRICE' }, { ...base, sistema: 'SAC' },
    { ...base, renda: 15000, valor: 500000, fatorSocial: false, sistema: 'PRICE' },   /* SBPE */
    { ...base, renda: 15000, valor: 500000, fatorSocial: false, sistema: 'SAC' }
  ];
  for (const e of casos) {
    const r = M.simular(e);
    for (const s of r.seguradoras) {
      const c = M.cronograma(e, r, s.codigo);
      assert.equal(c.length, r.prazo);
      assert.ok(Math.abs(c[0].encargo - s.primeira) <= 0.05, e.sistema + ' ' + s.codigo + ' mes 1');
      assert.ok(Math.abs(c[c.length - 1].encargo - s.ultima) <= 0.05, e.sistema + ' ' + s.codigo + ' ultimo');
      const amort = c.reduce((t, x) => t + x.amortizacao, 0);
      assert.ok(Math.abs(amort - r.valorFinanciamento) <= 0.05, 'soma das amortizacoes');
      assert.ok(Math.abs(c[c.length - 1].saldo) <= 0.05);
    }
  }
});

test('cronograma: resultado com erro ou seguradora desconhecida devolve []', () => {
  assert.deepEqual(M.cronograma({}, { erro: 'x' }, '15'), []);
  const e = { renda: 2800, valor: 220000, nascimento: new Date(1993, 2, 14), municipio: '3543402', sistema: 'PRICE', hoje: new Date(2026, 10, 7) };
  assert.deepEqual(M.cronograma(e, M.simular(e), '99'), []);
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/motor-caixa.test.js`
Expected: FAIL com `M.cronograma is not a function`.

- [ ] **Step 3: Implementar `cronograma(e, r, codigoSeguradora)` em `assets/motor-caixa.js`**

Mesma taxa mensal do `simular` (`r.jurosNominal/1200` no MCMV, `SBPE.iMensal` no SBPE). PRICE: prestação `= r2(fin*k)` constante (igual a `parcelaBase`), juros = saldo × i, amortização = prestação − juros (no último mês, amortização = saldo restante). SAC: amortização `fin/n`. MIP: mês 1 sobre o financiamento inteiro com a idade no 1º vencimento (como `simular`); meses seguintes sobre o saldo depois da amortização, com `taxaMip(seg, idadeAnos(nasc, dataDoMes))`. DFI = `e.valor × dfi/100` em todos os meses menos o último. `taxaAdm` = `r.taxaAdm` em todos. `data` do mês m = `addMeses(e.hoje, m)`. Exportar em `api`.

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test tests/motor-caixa.test.js`
Expected: PASS (todos, inclusive os antigos).

- [ ] **Step 5: Commit**

```bash
git add assets/motor-caixa.js tests/motor-caixa.test.js
git commit -m "feat(motor-caixa): cronograma mês a mês da parcela"
```

---

### Task 2: Regras do simulador (`assets/financiamento.js`)

**Files:**
- Create: `assets/financiamento.js`
- Modify: `assets/match.js` (acrescentar `travaFaixa3` e `TETO_F3` ao objeto `api`, sem mudar nada mais)
- Test: `tests/financiamento.test.js`

**Interfaces:**
- Consumes: `MotorCaixa.simular`, `MotorCaixa.cronograma`, `MotorCaixa.MUNICIPIO_POR_CIDADE` (Task 1); `Match.travaFaixa3(cliente, un)`, `Match.TETO_F3`, `Match.temSubsidio(renda, possuiImovel)`.
- Produces (`window.Financiamento` / `module.exports`):
  - Tipos: `Resp = { renda:Number, nascimento:Date|null, fgts:Boolean, possuiImovel:Boolean, fatorSocial:Boolean, subsidioAnterior:Boolean, sistema:'PRICE'|'SAC', prazo:Number|null, financiarAte:Number|null }`; `Imovel = { cidade:String, avaliacao:Number, venda:Number, ato:Number, empId:String|null, empNome:String, unidade:String, unidadeRotulo:String }`.
  - `RESP_PADRAO` = `{ renda:0, nascimento:null, fgts:true, possuiImovel:false, fatorSocial:false, subsidioAnterior:false, sistema:'PRICE', prazo:null, financiarAte:null }`.
  - `simular(resp, imovel, hoje) → Sim` com `Sim = { erro:String|null, mensagem:String|null, motorIn:Object, r:Object, capacidade:Number, limitado:Boolean, trava:Boolean, entrada:Number, baseEntrada:'venda'|'avaliacao', segPadrao:String, parcelaMax:Number }`.
  - `comparar(resp, imovel, hoje) → { PRICE:Sim, SAC:Sim }`.
  - `seguradoraPadrao(seguradoras) → String` (código).
  - `valoresCopia(sim, codigoSeg, renda) → { renda, financiado, subsidio, parcFin }`.
  - `mostraPerguntasSubsidio(renda, possuiImovel) → Boolean` (= `Match.temSubsidio`).
  - `mensagemErro(erroMotor) → String`.
  - `lerData('dd/mm/aaaa') → Date|null`.
  - `validar(resp, imovel, hoje) → Array<{ campo:'renda'|'nascimento'|'valor'|'cidade', mensagem:String }>`.
  - `serieAnual(cronograma) → Array<Number>` (encargo nos meses 1, 61, 121… e no último).
  - `brl(n) → String` (`'R$ 167.397,73'`).

- [ ] **Step 1: Escrever os testes**

```js
const F = require('../assets/financiamento.js');
const HOJE = new Date(2026, 10, 7);
const RESP = { ...F.RESP_PADRAO, renda: 2800, nascimento: new Date(1993, 2, 14), fatorSocial: true };
const GAIA = { cidade: 'Ribeirão Preto', avaliacao: 220000, venda: 0, ato: 0, empId: 'gaia', empNome: 'Village Gaia', unidade: 'BL02-0305', unidadeRotulo: 'Bloco 2 · Apto 305' };

test('simular: caso de referência do canvas', () => {
  const s = F.simular(RESP, GAIA, HOJE);
  assert.equal(s.erro, null);
  assert.equal(s.r.faixa, 'Faixa 1');
  assert.equal(s.r.valorFinanciamento, 167397.73);
  assert.equal(s.r.subsidio, 13209);
  assert.equal(s.entrada, 39393.27);
  assert.equal(s.baseEntrada, 'avaliacao');
  assert.equal(s.segPadrao, '15');
  assert.equal(s.parcelaMax, 840);
  assert.equal(s.limitado, false);
});

test('simular: teto venda − subsídio − ato limita e refaz a parcela', () => {
  const s = F.simular(RESP, { ...GAIA, venda: 175000, ato: 2500 }, HOJE);
  assert.equal(s.limitado, true);
  assert.equal(s.capacidade, 167397.73);
  assert.equal(s.r.valorFinanciamento, 159291);
  assert.equal(s.r.seguradoras.find((x) => x.codigo === '15').primeira, 800.76);
  assert.equal(s.entrada, 0);
  assert.equal(s.baseEntrada, 'venda');
});

test('simular: trava da Faixa 3 em R$ 400 mil', () => {
  const s = F.simular({ ...RESP, renda: 6000, fatorSocial: false }, { ...GAIA, avaliacao: 410000, venda: 395000 }, HOJE);
  assert.equal(s.trava, true);
  assert.equal(s.r.faixa, 'Faixa 3');
  assert.equal(s.r.jurosNominal, 7.66);
});

test('simular: SBPE sem subsídio e comprometimento 25% no PRICE', () => {
  const s = F.simular({ ...RESP, renda: 15000, fatorSocial: true }, { ...GAIA, avaliacao: 500000 }, HOJE);
  assert.equal(s.r.faixa, 'SBPE');
  assert.equal(s.r.subsidio, 0);
  assert.equal(s.parcelaMax, 3750);
  assert.equal(s.segPadrao, '16');
});

test('simular: erros do motor viram mensagem em português', () => {
  const idade = F.simular({ ...RESP, nascimento: new Date(1950, 0, 1) }, GAIA, HOJE);
  assert.equal(idade.erro, 'Idade acima de 70 anos e 6 meses');
  assert.match(idade.mensagem, /70 anos e 6 meses/);
  const fora = F.simular({ ...RESP, renda: 12000 }, { ...GAIA, avaliacao: 650000 }, HOJE);
  assert.equal(fora.erro, 'Fora do enquadramento MCMV');
  assert.ok(fora.mensagem.length > 20);
});

test('fator social e subsídio anterior só valem quando a renda permite subsídio', () => {
  assert.equal(F.mostraPerguntasSubsidio(2800, false), true);
  assert.equal(F.mostraPerguntasSubsidio(4000.01, false), false);
  assert.equal(F.mostraPerguntasSubsidio(2800, true), false);
  const s = F.simular({ ...RESP, renda: 6000, fatorSocial: true }, GAIA, HOJE);
  assert.equal(s.motorIn.fatorSocial, false);
});

test('valoresCopia usa a seguradora escolhida', () => {
  const s = F.simular(RESP, GAIA, HOJE);
  assert.deepEqual(F.valoresCopia(s, '15', 2800), { renda: 2800, financiado: 167397.73, subsidio: 13209, parcFin: 840 });
  assert.equal(F.valoresCopia(s, '14', 2800).parcFin, 825.92);
});

test('comparar devolve PRICE e SAC', () => {
  const c = F.comparar(RESP, GAIA, HOJE);
  assert.equal(c.PRICE.r.valorFinanciamento, 167397.73);
  assert.equal(c.SAC.r.valorFinanciamento, 129877.57);
});

test('lerData e validar', () => {
  assert.equal(F.lerData('31/02/1990'), null);
  assert.equal(F.lerData('14/03/1993').getFullYear(), 1993);
  const campos = (resp, im) => F.validar(resp, im, HOJE).map((x) => x.campo);
  assert.deepEqual(campos(RESP, GAIA), []);
  assert.deepEqual(campos({ ...RESP, renda: 0 }, GAIA), ['renda']);
  assert.deepEqual(campos({ ...RESP, nascimento: null }, GAIA), ['nascimento']);
  assert.deepEqual(campos({ ...RESP, nascimento: new Date(2027, 0, 1) }, GAIA), ['nascimento']);
  assert.deepEqual(campos({ ...RESP, nascimento: new Date(2010, 0, 1) }, GAIA), ['nascimento']);
  assert.deepEqual(campos(RESP, { ...GAIA, avaliacao: 0 }), ['valor']);
  assert.deepEqual(campos(RESP, { ...GAIA, cidade: 'Belo Horizonte' }), ['cidade']);
});

test('serieAnual e brl', () => {
  const s = F.simular(RESP, GAIA, HOJE);
  const serie = F.serieAnual(require('../assets/motor-caixa.js').cronograma(s.motorIn, s.r, '15'));
  assert.equal(serie.length, 8);
  assert.ok(Math.abs(serie[0] - 840) <= 0.05);
  assert.equal(F.brl(167397.73), 'R$ 167.397,73');
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/financiamento.test.js`
Expected: FAIL com `Cannot find module '../assets/financiamento.js'`.

- [ ] **Step 3: Implementar `assets/financiamento.js` e exportar `travaFaixa3`/`TETO_F3` em `assets/match.js`**

Cabeçalho no padrão de `assets/match.js` (comentário + IIFE; `require` no Node, `raiz.MotorCaixa`/`raiz.Match` no navegador). `simular`: `motorIn` com `valor = trava ? TETO_F3 : avaliacao`, `municipio = MUNICIPIO_POR_CIDADE[cidade]`, `fatorSocial`/`subsidioAnterior` zerados quando `!mostraPerguntasSubsidio`, `prazo`/`valorFinanciamento` só quando preenchidos; se `venda > 0` e `r2(venda − subsidio − ato) < capacidade`, roda de novo com `valorFinanciamento = max(0, teto)` e marca `limitado`. `entrada = r2(base − fin − sub − ato)` com `base = venda > 0 ? venda : avaliacao`. `trava` usa `Match.travaFaixa3({ renda, possuiImovel }, { avaliacao, associativo: venda })` só com `venda > 0`. Mensagens de `mensagemErro`: idade → "A CAIXA não financia acima de 70 anos e 6 meses na data de hoje. Se houver outro comprador mais novo, use a data dele."; fora do enquadramento → "Essa renda com esse valor de imóvel não enquadra no Minha Casa Minha Vida. Revise o valor ou a renda."; cidade → "Ainda não temos as regras da CAIXA para essa cidade."; outro → o próprio texto. `validar`: renda > 0; nascimento válido, não futuro, idade ≥ 18; avaliação > 0; cidade em `MUNICIPIO_POR_CIDADE`.

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test tests/*.test.js`
Expected: só a falha conhecida de `home-paginas.test.js`; `financiamento.test.js` e `match.test.js` passam.

- [ ] **Step 5: Commit**

```bash
git add assets/financiamento.js assets/match.js tests/financiamento.test.js
git commit -m "feat(financiamento): regras do simulador sobre o motor CAIXA"
```

---

### Task 3: Respostas na URL e destino do "Levar ao associativo"

**Files:**
- Modify: `assets/financiamento.js`
- Test: `tests/financiamento.test.js`

**Interfaces:**
- Consumes: `Resp`, `Imovel`, `Sim` (Task 2).
- Produces:
  - `CAMPANHA_BF = { ativa: true, cidades: ['Ribeirão Preto'] }`.
  - `codificaRespostas(resp, codigoSeg) → String` (seguro em URL, sem `renda` nem valores de imóvel); `decodificaRespostas(str) → { resp:Resp, seg:String } | null`.
  - `destinos(imovel) → Array<'normal'|'blackfriday'>`.
  - `urlAssociativo(destino, imovel, resp, sim, codigoSeg, hoje) → String`.

- [ ] **Step 1: Escrever os testes**

```js
test('respostas vão e voltam pela URL', () => {
  const resp = { ...RESP, sistema: 'SAC', prazo: 360, financiarAte: 150000 };
  const back = F.decodificaRespostas(F.codificaRespostas(resp, '4'));
  assert.equal(back.seg, '4');
  assert.equal(back.resp.nascimento.getTime(), resp.nascimento.getTime());
  for (const k of ['fgts', 'possuiImovel', 'fatorSocial', 'subsidioAnterior', 'sistema', 'prazo', 'financiarAte']) assert.equal(back.resp[k], resp[k], k);
  assert.match(F.codificaRespostas(resp, '4'), /^[A-Za-z0-9_.~-]+$/);
  assert.equal(F.decodificaRespostas('lixo'), null);
  assert.equal(F.decodificaRespostas(''), null);
});

test('destinos: Black Friday só em Ribeirão Preto com a campanha ativa', () => {
  assert.deepEqual(F.destinos(GAIA), ['normal', 'blackfriday']);
  assert.deepEqual(F.destinos({ ...GAIA, cidade: 'Campinas' }), ['normal']);
  const salvo = F.CAMPANHA_BF.ativa; F.CAMPANHA_BF.ativa = false;
  assert.deepEqual(F.destinos(GAIA), ['normal']);
  F.CAMPANHA_BF.ativa = salvo;
});

test('urlAssociativo com e sem unidade', () => {
  const s = F.simular(RESP, { ...GAIA, venda: 230000 }, HOJE);
  const u = new URL('http://x/' + F.urlAssociativo('normal', { ...GAIA, venda: 230000 }, RESP, s, '15', HOJE));
  assert.equal(u.pathname, '/simulador-associativo.html');
  const q = u.searchParams;
  assert.equal(q.get('emp'), 'gaia'); assert.equal(q.get('unidade'), 'BL02-0305');
  assert.equal(q.get('renda'), '2800'); assert.equal(q.get('idade'), '33'); assert.equal(q.get('valor'), '230000');
  assert.equal(q.get('fin'), String(s.r.valorFinanciamento)); assert.equal(q.get('sub'), '13209'); assert.equal(q.get('parcFin'), '840');
  assert.equal(q.get('origem'), 'financiamento'); assert.ok(F.decodificaRespostas(q.get('fz')));
  const semUn = new URL('http://x/' + F.urlAssociativo('blackfriday', { ...GAIA, empId: null, unidade: '' }, RESP, F.simular(RESP, GAIA, HOJE), '15', HOJE));
  assert.equal(semUn.pathname, '/simulador-associativo-blackfriday.html');
  assert.equal(semUn.searchParams.has('emp'), false);
  assert.equal(semUn.searchParams.has('valor'), false);
  assert.equal(semUn.searchParams.get('fin'), '167397.73');
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/financiamento.test.js`
Expected: FAIL com `F.codificaRespostas is not a function`.

- [ ] **Step 3: Implementar as quatro funções em `assets/financiamento.js`**

Formato do `fz` à escolha (ex.: campos separados por `.` com data `aaaammdd` e booleanos `0/1`); `decodificaRespostas` devolve `null` para qualquer coisa que não reconstrói um `Resp` válido. `urlAssociativo`: `emp`/`unidade` só com `empId` e `unidade`; `valor` só com `venda > 0`; `idade` = idade hoje; parâmetros na ordem `emp, unidade, renda, idade, valor, fin, sub, parcFin, origem, fz`.

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test tests/financiamento.test.js`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add assets/financiamento.js tests/financiamento.test.js
git commit -m "feat(financiamento): respostas na URL e destino normal ou Black Friday"
```

---

### Task 4: PDF da simulação

**Files:**
- Modify: `assets/financiamento.js` (função `dadosPdf`)
- Create: `assets/financiamento-pdf.js`
- Test: `tests/financiamento.test.js`

**Interfaces:**
- Consumes: `comparar`, `serieAnual`, `brl` (Task 2); `MotorCaixa.cronograma` (Task 1).
- Produces:
  - `Financiamento.dadosPdf({ comp, sistema, imovel, resp, seg, pessoas, hoje }) → Pdf` com `pessoas = { cliente:String, corretor:String }` e `Pdf = { arquivo:String, emissao:String, cliente:String, corretor:String, imovel:{ nome, detalhe, avaliacao, cidade }, principal:{ financiado, primeira, pctRenda, subsidio|null, entrada, resumo }, barra:{ fin:Number, sub:Number, ent:Number }, condicoes:Array<[String,String]>, dadosCliente:Array<[String,String]>, seguradoras:Array<{ nome, primeira, ultima, escolhida:Boolean }>, comparacao:Array<[String,String,String]>, serie:{ PRICE:Number[], SAC:Number[] }, aviso:String }`. Valores já formatados como texto.
  - `window.FinanciamentoPdf.gerar(pdf) → Promise<void>` (navegador; usa `window.jspdf` e autotable; logo `assets/img/logo-direcional-header.png` por canvas, como o PDF do associativo).

- [ ] **Step 1: Escrever os testes de `dadosPdf`**

```js
test('dadosPdf: nome do arquivo, seguradora escolhida e SBPE sem subsídio', () => {
  const comp = F.comparar(RESP, GAIA, HOJE);
  const p = F.dadosPdf({ comp, sistema: 'PRICE', imovel: GAIA, resp: RESP, seg: '15', pessoas: { cliente: 'Ana Souza', corretor: '' }, hoje: HOJE });
  assert.equal(p.arquivo, 'financiamento-ana-souza-2026-11-07.pdf');
  assert.equal(p.emissao, '07/11/2026');
  assert.equal(p.principal.financiado, 'R$ 167.397,73');
  assert.equal(p.seguradoras.filter((s) => s.escolhida).length, 1);
  assert.equal(p.seguradoras.find((s) => s.escolhida).primeira, 'R$ 840,00');
  assert.equal(p.serie.PRICE.length, 8);
  assert.match(p.aviso, /Não é aprovação de crédito/);
  const semNome = F.dadosPdf({ comp, sistema: 'PRICE', imovel: GAIA, resp: RESP, seg: '15', pessoas: { cliente: '', corretor: '' }, hoje: HOJE });
  assert.equal(semNome.arquivo, 'financiamento-village-gaia-2026-11-07.pdf');
  const sb = F.comparar({ ...RESP, renda: 15000 }, { ...GAIA, avaliacao: 500000 }, HOJE);
  const ps = F.dadosPdf({ comp: sb, sistema: 'PRICE', imovel: GAIA, resp: { ...RESP, renda: 15000 }, seg: '16', pessoas: { cliente: '', corretor: '' }, hoje: HOJE });
  assert.equal(ps.principal.subsidio, null);
  assert.ok(ps.condicoes.some(([k, v]) => k === 'Parcela máxima' && v === '25% da renda'));
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/financiamento.test.js`
Expected: FAIL com `F.dadosPdf is not a function`.

- [ ] **Step 3: Implementar `dadosPdf` e `assets/financiamento-pdf.js`**

`dadosPdf` monta as linhas do quadro "PDF da simulação" do canvas (spec §9): condições = Programa, Produto CAIXA, Sistema, Prazo, Juros nominal / efetivo, Taxa de administração, Parcela máxima (`r.comprometimento` em %); dados do cliente = Renda, Nascimento (mais velho) com idade, 3 anos de FGTS, Imóvel na cidade, e as duas perguntas de subsídio só quando `mostraPerguntasSubsidio`; aviso = texto do rodapé do canvas. `gerar`: A4 retrato, mm, layout do quadro `PDF.dc.html` (cabeçalho com logo, bloco principal com barra, duas tabelas lado a lado, seguradoras, PRICE × SAC com mini-gráfico de linhas, rodapé); salva com `pdf.arquivo`.

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test tests/financiamento.test.js`
Expected: PASS. (O desenho do PDF é conferido no navegador na Task 6.)

- [ ] **Step 5: Commit**

```bash
git add assets/financiamento.js assets/financiamento-pdf.js tests/financiamento.test.js
git commit -m "feat(financiamento): dados e desenho do PDF da simulação"
```

---

### Task 5: Popup e botão no associativo normal

**Files:**
- Create: `docs/design/simulador-financiamento/README.md` e `docs/design/simulador-financiamento/fonte/*` (cópia do canvas)
- Create: `assets/financiamento-popup.js`, `assets/financiamento.css`, `assets/img/icones-3d/escudo.svg`, `assets/img/icones-3d/documento.svg`
- Modify: `simulador-associativo.html` (links/scripts no `<head>`/fim, `<div id="fz-slot"></div>` no início do `.card` do passo 2, bloco de cola)
- Test: `tests/financiamento-paginas.test.js`

**Interfaces:**
- Consumes: `Financiamento.*` (Tasks 2–4), `FinanciamentoPdf.gerar` (Task 4).
- Produces (`window.FinanciamentoPopup`):
  - `abrir({ tema:'claro'|'black', contexto:Ctx, respostas:Resp|null, seg:String|null, etapa:1|'resultado', aoCopiar:function(valores, registro), aoFechar:function|undefined })`, com `Ctx = Imovel & { renda:Number, cliente:String, corretor:String }` e `registro = { resp:Resp, seg:String, imovel:Imovel, resumo:String }` (`resumo` = "MCMV Faixa 1 · 4,50% a.a. · 420 meses · PRICE").
  - `ligarAssociativo({ tema, slot:Element, contexto:function→Ctx, ler:function→{renda,financiado,subsidio,parcFin}, aplicar:function(valores), campos:{ renda:'f-renda', financiado:'f-fin', subsidio:'f-sub', parcFin:'f-parcfin' } }) → Controle`, com `Controle = { atualizar(), limpar(), restaurar({ resp:Resp, seg:String }) }`. Nesta task: só o estado "botão" e a cópia; marcas e faixas vêm na Task 6.
  - Cola em cada associativo: `var fz = null;` declarado antes do primeiro `render()`, `function contextoFz(){…}` (devolve `Ctx`) e `fz = FinanciamentoPopup.ligarAssociativo({ tema: 'claro', contexto: contextoFz, … })`. `render()` chama `if(fz) fz.atualizar();` (Task 6).

- [ ] **Step 1: Copiar a referência visual para o repositório**

```bash
mkdir -p docs/design/simulador-financiamento/fonte
cp /private/tmp/claude-501/-Users-hanieri--claude-spares-spare-oVtzqE/443a1b5c-4567-46e6-9b39-c46f18630910/scratchpad/canvas/project/*.dc.html /private/tmp/claude-501/-Users-hanieri--claude-spares-spare-oVtzqE/443a1b5c-4567-46e6-9b39-c46f18630910/scratchpad/canvas/project/canvas.json docs/design/simulador-financiamento/fonte/
```

Se a pasta temporária não existir mais, baixar os mesmos arquivos do canvas (Artifact `read` com `paths` em `project/*.dc.html`). README no formato de `docs/design/match-unidades-nova-ux/README.md`: link do canvas, tabela arquivo → tela, aviso de que os números são do caso de exemplo. Exportar `escudo` e `documento` do `Icone.dc.html` como SVG soltos, no formato de `assets/img/icones-3d/calculadora.svg` (gradientes `r3d/w3d/o3d/sh3d` no próprio arquivo).

- [ ] **Step 2: Escrever o teste de ligação**

```js
const fs = require('fs'); const path = require('path');
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
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `node --test tests/financiamento-paginas.test.js`
Expected: FAIL nos dois testes.

- [ ] **Step 4: Implementar o popup, o CSS e a cola no associativo**

Popup conforme spec §6.1–6.4 e quadros `Modal.dc.html`, `A-Desk-*` e `A-Cel-*` (desktop: diálogo 760px; `matchMedia('(max-width:860px)')`: folha de baixo, 790px no máximo). Passo 1 mostra cidade + valor quando `!(contexto.avaliacao > 0)`; renda vazia → campo focado. Botões travados enquanto `Financiamento.validar` aponta campo do passo atual (mensagem embaixo do campo). Passo 2 esconde as duas perguntas de subsídio quando `!mostraPerguntasSubsidio`. Passo 3: pílulas de prazo só abaixo do prazo máximo do resultado (no SBPE PRICE o máximo já é 360, então some a pílula 360). Resultado com erro do motor = card de aviso com `sim.mensagem`, sem Copiar/PDF. Teclado: Enter avança, Esc fecha, foco preso, foco volta ao botão de origem. Cola em `simulador-associativo.html`: `contexto()` lê `S.empId`, `EMPS`, `(unidadesEmp.detalhes||{})[S.unidade]` (`avaliacao`, `associativoSemPremio`), `S.valor` (venda quando > 0, senão `associativoSemPremio`), `S.ato`, `S.renda`, `S.cliente`, `S.corretor`; `aplicar(v)` grava os 4 campos de `S` e chama `sincronizaCampos(); render();`.

- [ ] **Step 5: Rodar os testes**

Run: `node --test tests/*.test.js`
Expected: só a falha conhecida.

- [ ] **Step 6: Verificar no navegador**

`preview_start` com `portal-do-corretor`, abrir `/simulador-associativo`, escolher Village Gaia e uma unidade, renda 2800: botão abre o popup; passos 1→2→3→resultado; "Copiar para o simulador" preenche os 4 campos e o % ao lado. Conferir também: sem unidade (passo 1 pede valor), renda vazia (campo focado, não avança), nascimento `31/02/1990` (mensagem), largura 360px (folha rola, rodapé visível), Esc fecha e devolve o foco ao botão, "Baixar PDF" gera o arquivo igual ao quadro do canvas. Sem erros no console.

- [ ] **Step 7: Commit**

```bash
git add docs/design/simulador-financiamento assets/financiamento-popup.js assets/financiamento.css assets/img/icones-3d/escudo.svg assets/img/icones-3d/documento.svg simulador-associativo.html tests/financiamento-paginas.test.js
git commit -m "feat(associativo): botão e popup Simular financiamento"
```

---

### Task 6: Depois de copiar (marcas, faixa, desfazer, desatualizada)

**Files:**
- Modify: `assets/financiamento-popup.js`, `assets/financiamento.css`, `simulador-associativo.html` (chamar `fz.atualizar()` no fim de `render()` e `fz.limpar()` no clique de `b-reset`)
- Test: `tests/financiamento-paginas.test.js`

**Interfaces:**
- Consumes: `Controle` (Task 5).
- Produces: `Controle.atualizar()`, `Controle.limpar()`, `Controle.restaurar(registro)` completos; classes CSS `.fz-campo-sim` (campo copiado) e `.fz-tag` (etiqueta "simulação").

- [ ] **Step 1: Escrever o teste de ligação**

```js
test('associativo normal avisa o popup no render e no limpar', () => {
  const h = ler('simulador-associativo.html');
  assert.match(h, /function render\(\)\{[^\n]*fz\.atualizar\(\)/);
  const ini = h.indexOf("$('b-reset').addEventListener");
  const reset = h.slice(ini, h.indexOf('\n});', ini));
  assert.ok(reset.includes('fz.limpar()'));
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/financiamento-paginas.test.js`
Expected: FAIL.

- [ ] **Step 3: Implementar os estados do spec §6.4**

Ao copiar: guarda `anteriores = ler()` e o retrato `{ empId, unidade, venda }` do contexto; aplica; marca os 4 campos (e o par `-p` do financiamento e do subsídio) com `.fz-campo-sim` + `.fz-tag` no rótulo; troca o botão pela faixa verde (resumo, "Ver simulação", "PDF"); toast "4 campos preenchidos com a simulação · Desfazer" por 6 s. `Desfazer` → `aplicar(anteriores)`, tira marcas, volta o botão. `input` num campo marcado (ou no par `-p`) tira só a marca dele. `atualizar()`: com registro e contexto diferente do retrato → faixa amarela "A unidade mudou depois da simulação" com **Refazer** (`abrir` com `respostas` do registro, `etapa: 1`, contexto novo). `limpar()`: tudo some, volta o botão. "Ver simulação" reabre em `etapa: 'resultado'`.

- [ ] **Step 4: Rodar os testes**

Run: `node --test tests/*.test.js`
Expected: só a falha conhecida.

- [ ] **Step 5: Verificar no navegador**

Copiar com financiamento, subsídio e parcela já digitados (inclusive um em zero) → Desfazer volta exatamente os valores anteriores. Editar o subsídio → só ele perde a marca. Trocar a unidade → faixa amarela; Refazer abre no passo 1 com as respostas. "Limpar simulação" → botão de volta, sem marcas. PDF do associativo sai sem as marcas.

- [ ] **Step 6: Commit**

```bash
git add assets/financiamento-popup.js assets/financiamento.css simulador-associativo.html tests/financiamento-paginas.test.js
git commit -m "feat(associativo): marcas da simulação copiada, desfazer e aviso de desatualizada"
```

---

### Task 7: Associativo Black Friday

**Files:**
- Modify: `simulador-associativo-blackfriday.html` (mesmas inclusões, slot e cola das Tasks 5–6, com `tema: 'black'`)
- Modify: `assets/financiamento.css` (tema `[data-fz-tema="black"]` com as cores dos quadros `B-*`)
- Test: `tests/financiamento-paginas.test.js`

**Interfaces:**
- Consumes: `FinanciamentoPopup.ligarAssociativo` com `tema: 'black'` (Tasks 5–6).

- [ ] **Step 1: Escrever o teste**

```js
test('associativo Black Friday liga o popup com tema black', () => {
  const h = ler('simulador-associativo-blackfriday.html');
  for (const s of ['assets/financiamento.js', 'assets/financiamento-popup.js']) assert.ok(h.includes(`src="${s}"`), s);
  const passo2 = h.slice(h.indexOf('data-step="2"'), h.indexOf('data-step="3"'));
  assert.ok(passo2.includes('id="fz-slot"'));
  assert.match(h, /FinanciamentoPopup\.ligarAssociativo\(\{\s*tema:\s*'black'/);
  assert.ok(h.includes('fz.atualizar()') && h.includes('fz.limpar()'));
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/financiamento-paginas.test.js`
Expected: FAIL.

- [ ] **Step 3: Replicar a cola e o tema escuro**

Mesma cola da página normal (o script da Black Friday tem as mesmas funções, mais `ajustaPrazoBF`). Contraste de texto ≥ 4,5:1 sobre `#16181A`.

- [ ] **Step 4: Rodar os testes**

Run: `node --test tests/*.test.js`
Expected: só a falha conhecida.

- [ ] **Step 5: Verificar no navegador**

`/simulador-associativo-blackfriday` desktop e 390px: botão, popup e folha escuros como os quadros `B-*`; copiar, desfazer, faixa amarela e PDF funcionando; 360px sem rodapé cortado.

- [ ] **Step 6: Commit**

```bash
git add simulador-associativo-blackfriday.html assets/financiamento.css tests/financiamento-paginas.test.js
git commit -m "feat(blackfriday): botão e popup Simular financiamento no tema escuro"
```

---

### Task 8: Chegada pela URL com `origem=financiamento`

**Files:**
- Modify: `simulador-associativo.html` e `simulador-associativo-blackfriday.html` (função `aplicaParametrosUrl`)
- Test: `tests/financiamento-paginas.test.js`

**Interfaces:**
- Consumes: `Financiamento.decodificaRespostas` (Task 3), `Controle.restaurar(registro)` (Task 6).

- [ ] **Step 1: Escrever o teste**

```js
for (const f of ['simulador-associativo.html', 'simulador-associativo-blackfriday.html']) {
  test(f + ': parâmetros da simulação valem sem emp e só marcam com origem=financiamento', () => {
    const h = ler(f);
    const fn = h.slice(h.indexOf('function aplicaParametrosUrl'), h.indexOf('})();', h.indexOf('function aplicaParametrosUrl')));
    assert.ok(!/if\(!q\.has\('emp'\)\) return;/.test(fn), 'não pode sair cedo sem emp');
    assert.ok(fn.includes("q.get('origem')==='financiamento'") || fn.includes('q.get("origem")==="financiamento"'));
    assert.ok(fn.includes('decodificaRespostas'));
  });
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/financiamento-paginas.test.js`
Expected: FAIL nos dois arquivos.

- [ ] **Step 3: Implementar**

`aplicaParametrosUrl` deixa de sair cedo sem `emp`: aplica `emp/unidade/politica` quando válidos e os números sempre. Com `origem=financiamento` e `fz` decodificável, depois do primeiro `render()` chama `fz.restaurar({ resp, seg })` (marcas + faixa verde com "Ver simulação" e "PDF", sem toast nem Desfazer). O retrato para o aviso de desatualizada é tirado nessa hora (`empId`, `unidade`, `S.valor`). Como a planilha carrega depois, a faixa mostra "Financiamento simulado" e completa o resumo (faixa, juros, prazo, sistema) no primeiro `atualizar()` em que `contextoFz()` já tiver avaliação. Links do Match (sem `origem`) seguem iguais.

- [ ] **Step 4: Rodar os testes**

Run: `node --test tests/*.test.js`
Expected: só a falha conhecida; `match.test.js` intacto.

- [ ] **Step 5: Verificar no navegador**

Abrir `/simulador-associativo?emp=gaia&unidade=<código real>&renda=2800&fin=167397.73&sub=13209&parcFin=840&origem=financiamento&fz=<gerado por Financiamento.codificaRespostas no console>`: campos marcados e faixa verde; "Ver simulação" abre o resultado. O mesmo link sem `origem`: campos preenchidos, sem marca. Um link do Match continua igual.

- [ ] **Step 6: Commit**

```bash
git add simulador-associativo.html simulador-associativo-blackfriday.html tests/financiamento-paginas.test.js
git commit -m "feat(associativo): reconhece a simulação vinda da tela de financiamento"
```

---

### Task 9: Tela dedicada, perguntas

**Files:**
- Create: `simulador-financiamento.html`, `assets/financiamento-app.js`
- Modify: `assets/financiamento.css` (seções da página)
- Test: `tests/financiamento-paginas.test.js`

**Interfaces:**
- Consumes: `Financiamento.*`, `SimUnidades.carregar/aoMudar/porEmpreendimento`, `window.SIM_EMPS` (cidade, nome, id).
- Produces: estado da tela `{ etapa:0..6, modo:'portal'|'valor', imovel:Imovel, resp:Resp, seg:String|null }` guardado em `sessionStorage['fz-ultima']` a cada passo; `etapa 6` = resultado (Task 10).

- [ ] **Step 1: Escrever o teste**

```js
test('tela dedicada carrega os módulos e tem os cinco passos', () => {
  const h = ler('simulador-financiamento.html');
  for (const s of ['assets/config.js', 'assets/simuladores.js', 'assets/motor-caixa.js', 'assets/match-prosoluto.js', 'assets/match.js', 'assets/financiamento.js', 'assets/financiamento-pdf.js', 'assets/financiamento-app.js', 'assets/credito.js']) assert.ok(h.includes(`src="${s}"`), s);
  assert.ok(h.includes('jspdf/2.5.1/jspdf.umd.min.js') && h.includes('jspdf-autotable/3.8.2'));
  assert.ok(h.includes('href="assets/financiamento.css"'));
  assert.match(h, /<title>[^<]*Simulador de Financiamento/);
  for (const p of ['Imóvel', 'Renda', 'Idade', 'Perfil', 'Condições']) assert.ok(h.includes(p), p);
  assert.ok(!h.includes('Cabe financiar'));
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/financiamento-paginas.test.js`
Expected: FAIL (arquivo não existe).

- [ ] **Step 3: Implementar a página e os passos**

Visual dos quadros `Desktop-Inicio`, `Desktop-Pergunta`, `Main`/`M1`–`M5` (spec §7). Abertura no celular com "Começar simulação" e "Repetir a última simulação" (só aparece com `fz-ultima`); desktop com hero + trilha + passo 1. Passo 1: modo portal (pílulas de cidade → cartões dos empreendimentos de `SIM_EMPS` da cidade → torre e unidade → avaliação em destaque "Da planilha") ou modo valor; planilha com erro → modo valor por padrão. Respostas viram linhas da trilha (desktop) ou pílulas no topo (celular), clicáveis. Passo 5 Condições: dois cartões PRICE × SAC com financiamento e parcela de `Financiamento.comparar`, pílulas de prazo (máximo, 360, 300, 240, só abaixo do máximo do resultado) e "Financiar menos que o máximo" (interruptor + valor → `resp.financiarAte`). Prévia ao vivo (desktop) assim que imóvel e renda são válidos, com `Financiamento.simular`. Validação por passo com `Financiamento.validar`. Ícones 3D por `<img src="assets/img/icones-3d/*.svg">`.

- [ ] **Step 4: Rodar os testes**

Run: `node --test tests/*.test.js`
Expected: só a falha conhecida.

- [ ] **Step 5: Verificar no navegador**

`/simulador-financiamento` em 1440px e 390px: passos 1→5 com o caso de exemplo; trocar para "Digitar valor"; voltar por uma linha da trilha / pílula; prévia mostrando Faixa 1, 4,50%, 420 meses, R$ 13.209, R$ 840,00; recarregar e "Repetir a última simulação" volta as respostas.

- [ ] **Step 6: Commit**

```bash
git add simulador-financiamento.html assets/financiamento-app.js assets/financiamento.css tests/financiamento-paginas.test.js
git commit -m "feat(financiamento): tela dedicada com os cinco passos e prévia ao vivo"
```

---

### Task 10: Tela dedicada, resultado

**Files:**
- Modify: `assets/financiamento-app.js`, `assets/financiamento.css`, `simulador-financiamento.html`

**Interfaces:**
- Consumes: `Financiamento.comparar`, `serieAnual`, `dadosPdf`, `destinos`, `urlAssociativo`; `MotorCaixa.cronograma`; `FinanciamentoPdf.gerar`.

- [ ] **Step 1: Implementar o resultado**

Quadros `Desktop-Resultado` e `M6-Resultado` (spec §7): "Financia até R$ …" (com a linha "A CAIXA aprova até R$ Y…" quando `limitado`), indicadores, barra de composição (sem segmento verde no SBPE), 1ª e última parcela com % da renda, troca PRICE/SAC, gráfico SVG das duas séries anuais com legenda, tooltip por ano (ano de contrato, idade, PRICE e SAC) e tabela ao lado (financia, entrada, 1ª, última, total pago), seguradoras com rádio (padrão `segPadrao`), "Como chegamos aqui", respostas, aviso. Erro do motor → card de aviso com `mensagem` e botão "Editar respostas". Ações: Editar respostas, Baixar PDF (pede cliente e corretor opcionais num campo antes de gerar; corretor lembrado em `localStorage` como o Match faz), Nova simulação, **Levar ao associativo**: `destinos(imovel)` com um destino → navega; com dois → popup pequeno "Associativo" / "Associativo Black Friday".

- [ ] **Step 2: Rodar os testes**

Run: `node --test tests/*.test.js`
Expected: só a falha conhecida.

- [ ] **Step 3: Verificar no navegador**

Caso de exemplo: números iguais ao canvas (R$ 167.397,73; R$ 13.209,00; R$ 39.393,27; R$ 840,00). SAC: R$ 129.877,57 e última R$ 310,39. Renda 15.000 com avaliação 500.000: SBPE, sem subsídio, "25% da renda". Nascimento 01/01/1950: card de aviso. Tooltip do gráfico no ano 20. "Levar ao associativo" com unidade de RP pergunta o destino e chega com marcas; com Campinas vai direto. PDF igual ao quadro do canvas. 390px sem rolagem lateral.

- [ ] **Step 4: Commit**

```bash
git add assets/financiamento-app.js assets/financiamento.css simulador-financiamento.html
git commit -m "feat(financiamento): resultado com PRICE x SAC, seguradoras, PDF e levar ao associativo"
```

---

### Task 11: Entrada na home

**Files:**
- Modify: `index.html` (card em "Ferramentas" logo depois do Simulador Associativo; link no `.header-links` e na `.menu-folha`)
- Test: `tests/financiamento-paginas.test.js`

- [ ] **Step 1: Escrever o teste**

```js
test('home leva ao Simulador de Financiamento no card, no cabeçalho e no menu', () => {
  const h = ler('index.html');
  const links = [...h.matchAll(/<a\b[^>]*href="simulador-financiamento\.html"/g)];
  assert.equal(links.length, 3);
  const grid = h.slice(h.indexOf('class="tool-grid"'));
  assert.ok(grid.indexOf('simulador-associativo.html') < grid.indexOf('simulador-financiamento.html'));
  assert.ok(grid.includes('Simulador de Financiamento'));
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test tests/financiamento-paginas.test.js`
Expected: FAIL.

- [ ] **Step 3: Implementar** card no mesmo markup dos outros `.tool-card` (ícone `assets/img/icones-3d/calculadora.svg`, 84px) e os dois links no padrão dos vizinhos.

- [ ] **Step 4: Rodar os testes**

Run: `node --test tests/*.test.js`
Expected: só a falha conhecida.

- [ ] **Step 5: Commit**

```bash
git add index.html tests/financiamento-paginas.test.js
git commit -m "feat(home): card e links do Simulador de Financiamento"
```

---

### Task 12: Verificação final

- [ ] **Step 1:** `node --test tests/*.test.js` → só a falha conhecida de `home-paginas.test.js`.
- [ ] **Step 2:** Passada no navegador, desktop 1440px e celular 390px: home → tela dedicada → resultado → levar ao associativo (normal e Black Friday) → marcas → popup "Ver simulação" → PDF; associativo normal e Black Friday do zero com o botão; console sem erros; `prefers-reduced-motion` desliga as animações.
- [ ] **Step 3:** Conferir no `git diff origin/main --stat` que só mudaram os arquivos listados neste plano.

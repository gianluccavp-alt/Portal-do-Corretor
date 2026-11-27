# Filtros avançados do /resultado-mes: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Popup "Filtros avançados" que filtra a lista de OPs e o CSV, incluindo Fase.

**Architecture:** A regra fica pura em `assets/resultado-mes.js` (testada no Node). A tela usa um `<dialog>` nativo com o `Seletor` já existente e só grava em `estado.filtro.av` ao clicar em Aplicar.

**Tech Stack:** HTML, CSS e JS puros; `node --test`.

**Spec:** docs/superpowers/specs/2026-11-27-resultado-mes-filtros-avancados-design.md

## Global Constraints
- Sem dependências novas; nada muda no Apps Script.
- Texto da planilha entra sempre por `textContent`.
- Os cartões do topo não mudam; sem coluna "Gerente de vendas" no CSV.
- Não publicar (sem push, merge ou deploy) sem pedido.

## Review Focus
1. Valor digitado como "250.000" ou "R$ 250.000,00" vale 250000, não 250.
2. "De" maior que "até" (data ou valor): os limites são trocados.
3. Base "Data Confirmação 2.0" com intervalo: venda sem confirmação fica fora.
4. Marcação que não existe no novo recorte do topo continua visível no popup, para poder desmarcar.
5. Sem dados do D4Sign: campo Assinatura desabilitado.

---

### Task 1: Regra dos filtros avançados

**Files:** Modify `assets/resultado-mes.js`; Test `tests/resultado-mes.test.js`

**Interfaces:**
- Produces: `R.avancadoVazio()` → `{fases:[],corretores:[],emps:[],assinaturas:[],sinais:[],rankings:[],origens:[],dataBase:'venda',dataDe:'',dataAte:'',valorDe:null,valorAte:null}`
- `R.passaAvancado(v, a)` → boolean; `R.contarAvancados(a)` → nº de campos ativos (par de/até conta 1; `dataBase` sozinha conta 0)
- `R.lerValor(texto)` → number | null (ponto = milhar, vírgula = decimal; vazio ou sem dígito = null)
- `R.SEM = '(sem)'` marca ranking ou origem vazios
- `sinais`: `'boleto' | 'cartao' | 'pendente'`; `assinaturas`: valores de `v.assinatura`; `dataBase`: `'venda' | 'conf'`

- [ ] **Step 1: Testes que falham**

```js
const base = { fase: 'Proposta Aprovada', corretor: 'ANA', emp: 'Village Gaia', assinatura: 'aguardando',
  boleto: false, cartao: false, sinalPago: false, ranking: '', origem: 'Stand', venda: '2026-11-10', conf: '', valor: 250000 };
const av = (x) => Object.assign(R.avancadoVazio(), x);

test('avancado vazio passa tudo e conta zero', () => {
  assert.equal(R.passaAvancado(base, R.avancadoVazio()), true);
  assert.equal(R.contarAvancados(av({ dataBase: 'conf' })), 0);
});
test('avancado: no mesmo campo soma, entre campos combina', () => {
  assert.equal(R.passaAvancado(base, av({ fases: ['Fechado e ganho', 'Proposta Aprovada'] })), true);
  assert.equal(R.passaAvancado(base, av({ fases: ['Proposta Aprovada'], corretores: ['BIA'] })), false);
  assert.equal(R.passaAvancado(base, av({ emps: ['Village Park'] })), false);
  assert.equal(R.passaAvancado(base, av({ assinaturas: ['aguardando'], origens: ['Stand'], rankings: [R.SEM] })), true);
});
test('avancado: sinal', () => {
  assert.equal(R.passaAvancado(base, av({ sinais: ['pendente'] })), true);
  assert.equal(R.passaAvancado(base, av({ sinais: ['boleto', 'cartao'] })), false);
  assert.equal(R.passaAvancado({ ...base, cartao: true, sinalPago: true }, av({ sinais: ['cartao'] })), true);
});
test('avancado: data e valor, limites inclusivos e invertidos', () => {
  assert.equal(R.passaAvancado(base, av({ dataDe: '2026-11-10', dataAte: '2026-11-10' })), true);
  assert.equal(R.passaAvancado(base, av({ dataDe: '2026-11-20', dataAte: '2026-11-01' })), true);
  assert.equal(R.passaAvancado(base, av({ dataDe: '2026-11-11' })), false);
  assert.equal(R.passaAvancado(base, av({ dataBase: 'conf', dataAte: '2026-11-30' })), false);
  assert.equal(R.passaAvancado(base, av({ valorDe: 300000, valorAte: 200000 })), true);
  assert.equal(R.passaAvancado(base, av({ valorAte: 249999 })), false);
  assert.equal(R.contarAvancados(av({ valorDe: 0, dataDe: '2026-11-01', dataAte: '2026-11-02', fases: ['x'] })), 3);
});
test('lerValor entende o formato brasileiro', () => {
  assert.equal(R.lerValor('250.000'), 250000);
  assert.equal(R.lerValor('R$ 250.000,50'), 250000.5);
  assert.equal(R.lerValor('250000'), 250000);
  assert.equal(R.lerValor(''), null);
  assert.equal(R.lerValor('abc'), null);
});
```

- [ ] **Step 2:** `node --test tests/resultado-mes.test.js` → falha (`R.avancadoVazio is not a function`).
- [ ] **Step 3:** Implementar as funções e exportá-las em `api`.
- [ ] **Step 4:** Mesmo comando → tudo passa.
- [ ] **Step 5:** Commit `feat(resultado-mes): regra dos filtros avancados`.

### Task 2: Botão e popup

**Files:** Modify `resultado-mes.html` (botão `#f-av` antes de `#busca`; `<dialog id="av">` dentro de `#app`; CSS), `assets/resultado-mes-app.js`

**Interfaces:** Consumes tudo da Task 1.

- [ ] **Step 1:** HTML: botão "Filtros avançados" com contador `#f-av-n`; dialog com título, fechar (`#av-fechar`), selects múltiplos `#av-fase #av-corretor #av-emp #av-assin #av-sinal #av-ranking #av-origem`, `#av-data-base`, `#av-data-de/-ate` (`type=date`), `#av-valor-de/-ate` (`type=text inputmode=decimal`), rodapé `#av-limpar` e `#av-aplicar`. Grade de 2 colunas; 1 coluna e tela cheia até 640px. A lista do `Seletor` dentro do dialog fica em fluxo (`position:static`) para não ser cortada.
- [ ] **Step 2:** App: `filtroVazio()` ganha `av: R.avancadoVazio()`; `filtradas()` aplica `R.passaAvancado`; `desenharFiltros()` atualiza o contador e inclui os avançados no estado do `#f-limpar`. Opções vêm de `estado.vendas` mais o que já está marcado; corretor exibido com `titulo()`; ranking e origem vazios viram "Sem ranking" / "Sem origem"; `#av-assin` desabilitado quando `!estado.resumo.pendencias.temD4`.
- [ ] **Step 3:** Abrir copia `estado.filtro.av` para os campos. Aplicar lê os campos, grava e chama `reiniciarOps()`. Fechar, Esc (primeiro fecha a lista aberta) e clique no fundo descartam. Limpar zera só os campos do popup. `sair()` fecha o popup.
- [ ] **Step 4:** Matriz mantém `filtro.av`; clique em pendência e `#f-limpar` zeram (já via `filtroVazio()`).
- [ ] **Step 5:** `node --test tests/*.test.js` → tudo passa. Commit `feat(resultado-mes): popup de filtros avancados`.

### Task 3: Conferir no navegador

- [ ] Copiar `dados-locais/resultado-mes.json` para a worktree (fora do git), servir local e abrir `/resultado-mes.html?demo`.
- [ ] Conferir: filtrar por Fase muda lista, contador e CSV; cartões do topo iguais; fechar sem aplicar descarta; Limpar; troca de mês zera; 375px sem rolagem lateral; console sem erro.

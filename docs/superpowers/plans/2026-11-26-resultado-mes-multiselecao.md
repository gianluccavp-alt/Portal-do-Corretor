# Resultado do mês: seleção múltipla Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** selecionar vários empreendimentos e vários meses em `/resultado-mes`, com a página somando tudo.

**Architecture:** um período múltiplo é a chave `'2026-09+2026-11'` (tipo `multi`). A tela busca cada mês no Web App atual e junta as respostas cruas, que depois passam pelas mesmas regras do trimestre.

**Tech Stack:** HTML + JS puro; `node --test`.

**Spec:** docs/superpowers/specs/2026-11-26-resultado-mes-multiselecao-design.md

## Global Constraints
- Apps Script não muda. Texto da planilha só por `textContent`.
- No máximo 3 buscas simultâneas; falha em um mês = erro, nunca soma parcial.

## Review Focus
- Mesma OP vinda nas respostas de dois meses conta uma vez (teste na Task 1).
- Resposta sem D4Sign em um dos meses: assinatura indisponível, não "Não enviado" (teste na Task 1).
- Nenhum empreendimento marcado = todos (teste na Task 1).
- Trocar de período durante a carga: resposta atrasada é ignorada (conferir na tela).
- Marcar várias caixas seguidas não fecha a lista nem perde a rolagem (conferir na tela).

### Task 1: Regras
**Files:** Modify `assets/resultado-mes.js`; Test `tests/resultado-mes.test.js`
**Produces:** `tipoPeriodo(p)` devolve `'multi'` se houver `+`; `noPeriodo(mes, p)` aceita multi; `juntarRespostas(respostas, periodo)` → `{ok, mes, meses, atualizadoEm (a mais antiga), intervaloMinutos, abas, d4sign|null}`; `filtrarGeral(vendas, {emps: string[], cidade, canal})`.
- [ ] Testes que falham para os quatro comportamentos e os 3 itens do Review Focus
- [ ] Implementar e rodar `node --test tests/resultado-mes.test.js` (tudo PASS)

### Task 2: Tela
**Files:** Modify `resultado-mes.html`, `assets/resultado-mes-app.js`, `assets/seletor.js`
- [ ] `#g-emp` vira `multiple`; `estado.geral.emps`; `Seletor.criar` ganha `opcoes.varias` (texto "N selecionados") e preserva rolagem e foco ao remontar a lista
- [ ] Aba Mês marca/desmarca, com contador, Limpar e Aplicar; Trimestre e Ano seguem com um clique
- [ ] `carregar` busca os meses que faltam no cache (3 por vez); título, botão do período e setas tratam `multi`
- [ ] Conferir em `?demo`, desktop e celular, sem erro no console

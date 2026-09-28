# Pendências de Vendas — referência visual

Telas aprovadas para a página `/pendencias-vendas` (spec em
`docs/superpowers/specs/2026-09-28-pendencias-vendas-design.md`).

Canvas original (editável, privado): https://claude.ai/artifact/NSkcQZrsCzmZRYPAeDc9pG

Os nomes de clientes, OPs e textos das telas são **fictícios**. Os números dos
KPIs são os reais da planilha em 28/09/2026.

## Pastas

| Pasta | O que tem |
|---|---|
| `telas/` | PNG de cada tela (2x). É o que abrir para consultar o visual. |
| `previa/` | HTML estático de cada tela — abre direto no navegador e usa a logo e o padrão de setas de `assets/img/`. |
| `fonte/` | Código-fonte do canvas de Design (`.dc.html` + `canvas.json`). Só renderiza dentro do editor de Design; guardado para poder republicar/editar. |

## Telas

| Arquivo | Tela |
|---|---|
| `Senha` | 1 · Tela de senha (desktop) |
| `Main` | 2 · Lista de pendências — KPIs, filtros, tabela |
| `Detalhe` | 3 · Painel lateral da venda — o que falta, justificativa, Observação/Retorno |
| `Cancelar` | 4 · Confirmação de cancelamento |
| `Estados` | 5 · Atualizando, salvo, senha incorreta, vazio, erro, cancelada |
| `Mobile-Senha` | Celular · Senha |
| `Mobile-Lista` | Celular · Lista em cartões |
| `Mobile-Detalhe` | Celular · Venda |

O visual segue `DESIGN.md` (mundo Direcional: DM Sans, vermelho `#E4032B` só
para ação/status, superfícies brancas com borda `#E7E9EA`).

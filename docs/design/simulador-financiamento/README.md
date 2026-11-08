# Simulador de Financiamento — referência visual

Telas aprovadas em 07/11/2026: tela dedicada `/simulador-financiamento` (celular, desktop e PDF) e o
botão "Simular financiamento" com popup nos simuladores associativos (normal e Black Friday).
Segue o Padrão visual 2.0 do Match de Unidades (`docs/design/match-unidades-nova-ux/README.md`).

Canvas original (editável, privado): https://claude.ai/artifact/KZN7zwgMrwvNi8NNmdzXg2
Spec: `docs/superpowers/specs/2026-11-07-simulador-financiamento-design.md`
Plano: `docs/superpowers/plans/2026-11-07-simulador-financiamento.md`

Os números das telas são do cliente de exemplo rodado no motor CAIXA (renda R$ 2.800, imóvel de
R$ 220.000 em Ribeirão Preto, 33 anos, 3 anos de FGTS, com dependente). A curva da parcela no canvas é
estimada; no produto ela vem de `MotorCaixa.cronograma`.

## Pastas

| Pasta | O que tem |
|---|---|
| `fonte/` | Código-fonte do canvas (`.dc.html` + `canvas.json`). Só renderiza dentro do editor de Design (as imagens apontam para `/_blob/...`); guardado para consultar medidas, cores, CSS e animações. |

## Telas (arquivos em `fonte/`)

| Arquivo | Tela |
|---|---|
| `Main` | Protótipo do celular da tela dedicada (abertura → 5 passos → resultado). |
| `M1-Abertura` … `M6-Resultado` | O mesmo protótipo congelado em cada etapa (`M6` com a rolagem inteira). |
| `Desktop-Inicio` | Desktop · abertura com hero 3D + passo 1. |
| `Desktop-Pergunta` | Desktop · passo 5 com a prévia ao vivo. |
| `Desktop-Resultado` | Desktop · resultado (PRICE × SAC, gráfico, seguradoras, próximo passo). |
| `PDF` | Folha A4 da simulação. |
| `Modal` | Componente do popup (`tema` claro/black, `formato` dialog/sheet, `etapa`). |
| `AssocDesktop`, `AssocCelular` | Associativo com o botão (interativos; `tema` e `estado`). |
| `A-*` / `B-*` | Associativo normal / Black Friday congelados: botão, passo, resultado, copiado. |
| `Icone` | Componente dos ícones 3D (fonte dos SVGs em `assets/img/icones-3d/`). |

## Ícones novos

`escudo.svg` (seguradora) e `documento.svg` (PDF), mesma regra de construção dos 12 do Match: luz de
cima à esquerda, extrusão de 3px na cor escura, sombra de contato elíptica.

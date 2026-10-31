# Match de Unidades — nova UX (referência visual)

Telas aprovadas em 30/10/2026 para a nova `/match-unidades`: formulário em
linha do tempo (uma pergunta por vez), revelação animada do resultado e lista
com "melhor match". Também inaugura o **Padrão visual 2.0** (ícones 3D,
componentes e movimento) que as próximas telas do portal devem seguir.

Canvas original (editável, privado): https://claude.ai/artifact/VGkuSVBRYMeEuiVXom648x
Plano de implementação: `docs/superpowers/plans/2026-10-30-match-nova-ux.md`

Os números de unidades, valores, juros e prazos das telas são **ilustrativos**.
No produto eles vêm da planilha e do motor CAIXA (`assets/match.js`).

## Pastas

| Pasta | O que tem |
|---|---|
| `fonte/` | Código-fonte do canvas de Design (`.dc.html` + `canvas.json`). Só renderiza dentro do editor de Design (as imagens apontam para `/_blob/...` do canvas); guardado para consultar medidas, cores, CSS e animações, e para republicar. |
| `assets/img/icones-3d/` (na raiz) | Os 12 ícones 3D exportados como SVG, prontos para `<img>`. |

## Telas (arquivos em `fonte/`)

| Arquivo | Tela |
|---|---|
| `Main` | Protótipo do celular com todas as etapas (abertura → 6 perguntas → revelação → resultado). Todo o CSS, as animações e a lógica de navegação estão aqui. |
| `M1-Onde` … `M8-Resultado` | O mesmo protótipo congelado em cada etapa (importam `Main`). |
| `Desktop-Pergunta` | Desktop · trilha na coluna esquerda + pergunta (etapa Perfil). |
| `Desktop-Resultado` | Desktop · resumo, melhor match, tabela das demais unidades, "como chegamos aqui" e sugestão de política. |
| `Padrao` | Padrão visual 2.0: ícones, cores, tipografia, componentes, movimento. |
| `Icone` | Componente dos ícones 3D (fonte dos SVGs exportados). |

## Ícones 3D → uso

| Arquivo | Onde aparece |
|---|---|
| `casa.svg` | Abertura |
| `pino.svg` | Etapa Onde, "Todos os empreendimentos" |
| `carteira.svg` | Etapa Renda |
| `moedas.svg` | Etapa Ato |
| `calendario.svg` | Etapa Nascimento |
| `maleta.svg` | Perfil · 3 anos de FGTS |
| `chave.svg` | Perfil · Possui imóvel |
| `pessoas.svg` | Perfil · Dependente / mais de um comprador |
| `presente.svg` | Perfil · Subsídio anterior |
| `medalha.svg` | Etapa Política, card "Mais opções" |
| `alvo.svg` | Revelação, "Como chegamos aqui" |
| `predio.svg` | Empreendimento sem foto |

Regra de construção: luz de cima à esquerda, extrusão de 3px na cor escura,
sombra de contato elíptica, paleta vermelho `#E4032B` / ouro `#F5AE1E` /
grafite / branco.

## Tokens novos (somam ao `DESIGN.md`)

- Grafite de título `#2B3033`; texto secundário `#5C6467`; ouro `#F5AE1E`.
- Raios: botão principal 18px, cartões 18–26px, interruptor/pílula 999px.
- Botão principal: 56px de altura, sombra `0 12px 24px -10px rgba(228,3,43,.65)`.
- Movimento: curva `cubic-bezier(.2,.8,.2,1)`; entrada 550ms subindo 16px com
  cascata de 70ms; toque encolhe para 97% em 120ms; flutuação dos ícones 4,6s;
  revelação = anel 1,7s → contagem → resumo em cascata. Com
  `prefers-reduced-motion` tudo aparece sem animação.
- DM Sans com peso 800 para títulos e valores (`font-variant-numeric: tabular-nums`).

## Armadilha já encontrada

Reset de botão com especificidade alta (`.app button {…}`) apaga as classes de
componente (`.btn-pri`, `.pill`, `.tile`). Use `:where(.app) button {…}`.

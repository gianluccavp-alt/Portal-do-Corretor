# Unidades promocionais: nova forma de armazenar e ler

## Contexto

A lista de unidades promocionais (marcadas em `/promocionais`) era lida e
gravada inteiramente via um Web App do Google Apps Script, guardando os dados
em `PropertiesService`. Esse endpoint (`/exec`) redireciona internamente para
`script.googleusercontent.com/macros/echo`, e esse redirecionamento se mostrou
seriamente instável (~85% de falha medida em teste direto, latência de até
13s numa implantação degradada). Isso causava:

- Erro "não foi possível contatar o Apps Script" ao salvar, mesmo quando o
  salvamento tinha ocorrido no servidor.
- O site público deixando de exibir as promocionais quando a leitura falhava
  (sem retry na versão original).

Uma reimplantação do mesmo Apps Script já resolveu o sintoma temporariamente,
mas a causa é estrutural: depender do endpoint de Web App do Apps Script para
o caminho de leitura (que roda a cada visita ao site) é frágil por natureza.

O restante do site já lê a planilha principal via **CSV publicado na Web**
(`window.SHEET_CSV_URL`, `assets/data.js:fetchSheetCsv`), com fallback para
dois proxies públicos — mecanismo comprovadamente estável, usado por todas as
páginas de empreendimento.

## Objetivo

Separar leitura de escrita:

- **Leitura** (site público + a própria página `/promocionais` ao carregar):
  passa a usar o mesmo mecanismo de CSV publicado já validado no projeto,
  eliminando o Apps Script do caminho de leitura.
- **Escrita** (só ocorre quando alguém salva em `/promocionais`, uso interno
  e raro): continua via Apps Script, mas grava numa aba normal da planilha em
  vez de `PropertiesService` — dado deixa de ser uma caixa-preta e passa a
  ser auditável/editável manualmente como último recurso.

## Formato da aba "Promocionais"

Nova aba na mesma planilha (`1hXgz1AbzYeaP2xLbM5Vj9wcM-0CWd98FG4PY5ZusJac`),
uma linha por unidade marcada:

| Empreendimento | Identificador | ValorAssociativoNoMomento | ValorTabelaDiretaNoMomento | AtualizadoEm |
|---|---|---|---|---|
| Direcional Conquista Clube Ipiranga | BL01-0604 | 236900 | 247746 | 2026-09-18T14:50:07.182Z |

- `Empreendimento` + `Identificador` juntos formam a chave (o identificador
  se repete entre empreendimentos diferentes). O front-end já tem
  `chavePromo(nomeEmp, identificador)` (`assets/data.js`, duplicada em
  `assets/simuladores.js`) para reconstruir a mesma chave usada em
  `PROMO_SET` — nenhuma mudança na lógica de exibição (`isPromo()`, badges).
- `ValorAssociativoNoMomento` = `u.vcm` no instante do salvamento.
- `ValorTabelaDiretaNoMomento` = `u.vcm + u.folgaTabela` no instante do
  salvamento.
- Esses dois valores são **só um retrato para auditoria/histórico** — o site
  continua exibindo o valor promocional ao vivo a partir do VCM atual da
  planilha principal (comportamento de hoje não muda; a promoção continua
  "acompanhando sozinha" os reajustes de tabela).
- Cada "Salvar" reescreve a aba inteira (apaga as linhas de dados e escreve a
  lista atual) — mesma semântica de "lista completa" que `PropertiesService`
  já tinha.

## Leitura

`assets/data.js` e `promocionais.html` passam a carregar a lista de
promocionais com `fetchSheetCsv()` (já existente) apontando para o CSV
publicado da aba "Promocionais", reaproveitando `parseCSV()` e
`chavePromo()`. Isso substitui `fetchPromocionais()` / `loadPromocionais()`
no que dependiam do Apps Script para leitura. Mesmo fallback de proxies que a
planilha principal já usa.

## Escrita

**Apps Script (`Code.gs`):**

```
doPost(e):
  valida senha (igual hoje)
  abre a planilha por ID (SpreadsheetApp.openById)
  pega a aba "Promocionais" (cria com cabeçalho se não existir)
  limpa as linhas de dados
  escreve uma linha por unidade marcada
  retorna { ok: true, total: N }
```

`doGet` deixa de ser necessário para o site (que agora lê via CSV), mas fica
mantido como fallback de leitura/debug direto do Apps Script.

**Front-end (`promocionais.html`):**

- Confia na resposta do `doPost` (2 tentativas de retry via
  `promoFetchJson`), sem tentar "confirmar" reconsultando o Apps Script (isso
  era necessário só porque a leitura também era instável).
- Ao ter sucesso, o toast avisa que a publicação no site pode levar alguns
  minutos, porque o CSV publicado do Google não atualiza instantaneamente
  (mesma defasagem que a planilha principal já tem hoje).
- Falha real (senha errada, ou falha após os retries) continua mostrando erro
  — sem falso positivo nem falso negativo.

## Pré-requisitos manuais (usuário)

1. Criar a aba "Promocionais" na planilha (ou deixar o Apps Script criar
   sozinho no primeiro salvamento).
2. Arquivo → Compartilhar → Publicar na Web → selecionar a aba
   "Promocionais" → formato CSV → marcar "Republicar automaticamente quando
   alterações forem feitas".
3. Passar a URL do CSV publicado dessa aba para configurar em
   `assets/config.js`.
4. Colar o novo `Code.gs` no editor do Apps Script e reimplantar (nova
   implantação ou atualizar a existente).

## Tratamento de erros

- Leitura (site e `/promocionais` ao abrir): se o CSV falhar mesmo após os 2
  proxies de fallback, nenhuma unidade é marcada como promocional — mesmo
  fail-safe que `isPromo()` já tem hoje, sem quebrar o resto do site.
- Escrita: senha errada → erro imediato. Falha de rede/timeout após retries
  → erro real, com a aba da planilha disponível para conferência/edição
  manual como último recurso (hoje isso era impossível, os dados ficavam
  presos em `PropertiesService`).

## Fora de escopo

- Não muda a UI de `/promocionais` (filtros, checkboxes, botão Salvar).
- Não congela o valor promocional exibido — continua vindo do VCM ao vivo.
- Não remove a senha de gate da página `/promocionais`.

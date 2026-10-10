# Visitas da Recepção — design

**Data:** 09/10/2026
**Status:** v1 e v2 implementadas na branch `feat/visitas-recepcao` (não publicadas).
**v3 (§14, contas das recepcionistas, PDV e só Ribeirão Preto) aguardando revisão.
Onde uma seção mais nova diverge de uma anterior, vale a mais nova (§14 > §13 > §1–12).**
**Páginas:**
- `https://produtosdirecional.vercel.app/visitas-recepcao` (lançamento; com login a partir da v3)
- `https://produtosdirecional.vercel.app/visitas-recepcao-adm` (dashboard, com senha)

**Planilha:** `10Hi4moBVJlK6Gs3wdULQPGai8vGZu_JhSYX4CKWLTfk`, aba `VISITAS`
**Telas aprovadas:** canvas "Visitas Recepção" — https://claude.ai/artifact/254FTbPxSoAVKMsPvJd8vV
(quadros `Main` = recepção desktop, `RecepcaoCelular` = recepção no celular, `Admin` = dashboard)

## 1. Objetivo

Registrar cada cliente que entra num stand de vendas e acompanhar esse fluxo.

- A **recepcionista** lança a visita em poucos toques: empreendimento, data, horário e
  tipo. Ela vê na hora o total de visitas do dia daquele stand.
- O **comercial** acompanha, num dashboard, o volume de visitas por período, por
  empreendimento, por tipo, por dia/horário e as imobiliárias que mais trazem clientes.

Os três tipos de visita:

| Código | Nome na tela | Significado | Campos extras |
|---|---|---|---|
| `esp` | Espontânea | Chegou ao stand sem agendamento | nenhum |
| `house` | Agendada · Corretor house | Agendada por um corretor da construtora | Corretor house (texto livre, opcional) |
| `imob` | Imobiliária parceira | Trazida por corretor de imobiliária parceira | Imobiliária (texto livre, **obrigatório**) + Corretor da imobiliária (texto livre, opcional) |

### Fora de escopo

- Dados do cliente (nome, telefone, primeira visita).
- Login por recepcionista ou registro de quem lançou.
- Lista cadastrada de corretores ou imobiliárias (os campos são texto livre).
- Editar um lançamento (só excluir e lançar de novo).
- Fila offline: sem internet, o lançamento falha e a recepcionista tenta de novo.
- Senha na página da recepção.

## 2. Arquitetura

```
visitas-recepcao.html  ─┐
                        ├─POST text/plain─▶ Web App (Apps Script vinculado à planilha)
visitas-recepcao-adm.html┘ ◀──── JSON ────   doPost: registrar | dia | excluir | listar
                                                       │
                                                       ▼
                                               aba VISITAS (lê e grava)
```

- **Tudo passa pelo Web App**, como em `/pendencias-vendas`. A página não lê o CSV da
  planilha: o contador precisa refletir o lançamento na hora, a senha do admin é
  conferida no servidor e a planilha não precisa ser pública.
- Projeto Apps Script **vinculado à planilha nova** (Extensões › Apps Script), com
  `getActiveSpreadsheet()`.
  - Implantação: *App da Web · Executar como: Eu · Quem tem acesso: Qualquer pessoa*.
- `POST` com `Content-Type: text/plain;charset=utf-8`, para evitar o preflight de CORS.
- Fuso de todas as datas no servidor: `America/Sao_Paulo`.

### Arquivos

| Arquivo | Papel |
|---|---|
| `visitas-recepcao.html` | Tela de lançamento. HTML/CSS/JS puro, no padrão de `pendencias-vendas.html`. `cleanUrls` já serve em `/visitas-recepcao`. |
| `visitas-recepcao-adm.html` | Tela de senha + dashboard. `<meta name="robots" content="noindex">`. |
| `assets/visitas.js` | Funções **puras**: validação do formulário, agregações do dashboard, ranking de imobiliárias, CSV, formatação. Exporta em `window.Visitas` e `module.exports`. |
| `assets/config.js` | Ganha `window.VISITAS_APPS_SCRIPT_URL` (URL `/exec`). **A senha não entra aqui.** A lista de empreendimentos é a `window.CITIES` que já existe. |
| `docs/apps-script-visitas.gs` | Código do Web App, com instruções de implantação no cabeçalho (como `docs/apps-script-pendencias.gs`). |
| `tests/visitas.test.js` | Testes de `assets/visitas.js` e da paridade de empreendimentos (§4.5) com `node --test`. |

## 3. Planilha — aba `VISITAS`

Cabeçalho na **linha 1**. Se a aba não existir ou estiver vazia, o script cria a aba e
o cabeçalho. Colunas localizadas **pelo nome**, nunca pela posição. Se faltar uma
coluna → `erro:'coluna'` com o nome que faltou.

| Coluna | Conteúdo |
|---|---|
| `ID` | `V` + timestamp em ms + 4 caracteres aleatórios. Único. |
| `Registrado em` | Data/hora do servidor no momento da gravação (`dd/MM/yyyy HH:mm:ss`). |
| `Data` | Data da visita informada (`dd/MM/yyyy`, gravada como texto). |
| `Horário` | Horário da visita informado (`HH:mm`, gravado como texto). |
| `Empreendimento` | Nome do empreendimento (lista oficial, §4.5). |
| `Cidade` | Definida pelo servidor a partir do empreendimento, nunca pelo cliente. |
| `Tipo` | `Espontânea` / `Corretor house` / `Imobiliária` (nome legível). |
| `Corretor house` | Texto ou vazio. |
| `Imobiliária` | Texto ou vazio. |
| `Corretor imobiliária` | Texto ou vazio. |
| `Excluída` | `0` ou `1`. Excluir nunca apaga a linha. |
| `Token` | Hash SHA-256 (hex) do token de exclusão (§4.3). O token em si nunca é gravado. |

Data e Horário vão como texto (formato de número `@`), para a planilha não converter
para data/hora local e mudar o valor.

## 4. Web App (`docs/apps-script-visitas.gs`)

### 4.1 Contrato

- Requisição: `{ acao, senha?, ...parâmetros }`.
- Sucesso: `{ ok: true, ... }`.
- Falha: `{ ok: false, erro: 'senha' | 'invalido' | 'nao_encontrada' | 'ocupado' | 'coluna' | 'interno', mensagem }`.
  - `invalido` traz `campo` com o nome do campo recusado.
- Formato de uma visita na resposta:

```js
{ id, data /* 'yyyy-MM-dd' */, hora /* 'HH:mm' */, empreendimento, cidade,
  tipo /* 'esp'|'house'|'imob' */, corretorHouse, imobiliaria, corretorImob }
```

| `acao` | Senha | Parâmetros | Faz | Devolve |
|---|---|---|---|---|
| `registrar` | não | `empreendimento, data, hora, tipo, corretorHouse?, imobiliaria?, corretorImob?` | Valida (§4.2), grava uma linha | `{ visita, token }` |
| `dia` | não | `empreendimento, data` | Lê as visitas não excluídas daquele stand naquela data | `{ visitas, sugestoesImob }` |
| `excluir` | não | `id, token` | Marca `Excluída = 1` (§4.3) | `{ id }` |
| `listar` | sim | `de, ate` (`yyyy-MM-dd`) | Lê as visitas não excluídas com `Data` entre `de` e `ate`, inclusive | `{ visitas }` |

- `sugestoesImob`: nomes distintos da coluna `Imobiliária` nos últimos 90 dias (pelo
  `Registrado em`), normalizados por `trim` e comparados sem caixa e sem acento,
  mantendo a grafia mais frequente. No máximo 200, em ordem alfabética.
- `listar` aceita no máximo 92 dias de intervalo (`invalido`, `campo:'periodo'`).
- Senha errada nunca devolve dado.

### 4.2 Validação no `registrar`

O servidor é a autoridade. Ele não confia em nada do cliente:

- `empreendimento`: precisa estar na lista oficial (§4.5).
- `tipo`: `esp`, `house` ou `imob`.
- `data`: `yyyy-MM-dd` válida, entre **hoje − 7 dias** e **hoje** no fuso de São Paulo.
- `hora`: `HH:mm` válida. Se `data` = hoje, não pode passar de agora + 5 min.
- Textos: `trim`, espaços repetidos viram um só, no máximo 80 caracteres.
  - `imob` sem `imobiliaria` → `invalido`, `campo:'imobiliaria'`.
  - Campos que não se aplicam ao tipo são gravados vazios (ex.: `corretorHouse` numa visita `esp`).
- **Neutralização de fórmula:** texto que começa com `=`, `+`, `-`, `@`, tab ou CR
  recebe um apóstrofo (`'`) na frente antes de gravar. A mesma regra vale no CSV do
  dashboard (§6.2).
- A gravação (`appendRow`) roda dentro de `LockService.getScriptLock()`, `tryLock(30000)`.
  Se o lock não sair → `erro:'ocupado'` ("Muitos lançamentos ao mesmo tempo, tente de novo").

### 4.3 Exclusão pela recepção

- `registrar` gera um token aleatório (`Utilities.getUuid()`), grava só o hash
  SHA-256 na coluna `Token` e devolve o token em claro para a página.
- A página guarda `{ id: token }` no `localStorage` (chave `visitas.tokens`), descartando
  entradas de dias anteriores.
- `excluir` exige `id` + `token` cujo hash bata com o da linha **e** `Registrado em` de
  hoje. Fora disso → `nao_encontrada` (mesma resposta para id inexistente, token
  errado ou outro dia, para não revelar qual foi).
- Na lista "Últimos lançamentos" da recepção, o botão de excluir só aparece nos
  lançamentos que têm token neste navegador. Os demais aparecem sem o botão.
- Roda dentro do lock. A linha é localizada pelo `ID` dentro do lock.

### 4.4 Senha do admin

- Script Property `VISITAS_SENHA`, gravada uma vez por `configurarSenhaVisitas()`.
  A senha é definida no deploy, tem no mínimo 12 caracteres e nunca é escrita no repositório (ver §13.5).
- Sem a Script Property configurada, `listar` responde `erro:'interno'` (nunca libera sem senha).

### 4.5 Lista oficial de empreendimentos

- O `.gs` não lê o `config.js`. Ele mantém sua própria constante
  `VISITAS_EMPREENDIMENTOS = [{ nome, cidade }]`, com os mesmos nomes de
  `window.CITIES[*].empreendimentos[*].nome` e o `name` da cidade.
- `tests/visitas.test.js` lê os dois arquivos como texto e falha se as listas
  divergirem. Assim, cadastrar um empreendimento novo no portal sem atualizar o
  Web App quebra o teste.

### 4.6 Função de conferência

`testeVisitas()`: garante a aba e o cabeçalho, registra uma visita de teste, lê o `dia`,
exclui com o token e loga cada passo. A linha de teste fica marcada como excluída.

## 5. Recepção (`/visitas-recepcao`)

Layout do quadro `Main` / `RecepcaoCelular` do canvas.

### 5.1 Fluxo

1. **Passo 1 · Stand, data e horário**
   - Empreendimento: `<select>` agrupado por cidade, a partir de `window.CITIES`.
     Lembra o último escolhido em `localStorage` (`visitas.emp`).
   - Data: hoje. Horário: agora (HH:mm). Botão "Agora" atualiza o horário.
   - O horário **não** é congelado ao abrir a página: após cada lançamento e ao tocar
     "Agora", volta a ser o horário atual.
2. **Passo 2 · Como o cliente chegou?** Três cartões (radio group). Ao escolher:
   - House → campo "Corretor house que agendou (opcional)".
   - Imobiliária → "Imobiliária" (obrigatório, `<datalist>` com `sugestoesImob`) e
     "Corretor da imobiliária (opcional)".
3. **Registrar visita** (botão primário). O texto diz o que falta:
   "Escolha o tipo de visita" / "Informe a imobiliária" / "Registrar visita".
   Durante o envio: "Registrando…", desabilitado (evita duplo toque).

### 5.2 Depois de registrar

- Sucesso: faixa verde "Visita registrada · 14:32 · Espontânea · Alta Vista Mangará"
  com "Desfazer" (chama `excluir`). A faixa some em 8 s ou no próximo lançamento.
- Tipo e campos extras são limpos. Empreendimento e data ficam.
- O contador e a lista são recarregados pelo `dia`.
- Falha: faixa vermelha com a mensagem do servidor (ou "Sem conexão. Tente de novo.")
  e o formulário **continua preenchido**.

### 5.3 Contador do dia

- Card "Visitas hoje · dd/MM" com o nome do stand, o total grande e uma barra por tipo.
- "Últimos lançamentos": os 6 mais recentes por horário, com tipo e detalhe
  (corretor house, ou imobiliária · corretor).
- Fonte: `dia` para o empreendimento e a data escolhidos. Recarrega ao trocar
  empreendimento/data, após registrar/excluir e a cada 60 s com a aba visível
  (para somar lançamentos de outro aparelho no mesmo stand).
- Se a data escolhida não for hoje, o título vira "Visitas em dd/MM".

## 6. Dashboard (`/visitas-recepcao-adm`)

Layout do quadro `Admin` do canvas.

### 6.1 Acesso

Mesmo padrão de `/pendencias-vendas`:

- Abre na tela de senha. Chama `listar` com a senha digitada.
- `erro:'senha'` → "Senha incorreta".
- `ok` → guarda a senha em `sessionStorage` e mostra o dashboard.
- Toda requisição leva a senha. `erro:'senha'` no meio do uso → limpa o
  `sessionStorage` e volta à tela de senha. "Sair" limpa o `sessionStorage`.

### 6.2 Conteúdo

- **Filtros:** Período (Hoje / 7 dias / 30 dias), Cidade (Todas + cidades de
  `window.CITIES`), Empreendimento (Todos + os da cidade escolhida; trocar a cidade
  volta para Todos).
  - A página busca do servidor **os últimos 30 dias uma vez** e filtra no navegador.
    Botão "Atualizar" busca de novo. Mostra "Atualizado às HH:mm".
- **Faixa de números:** Total, Espontânea, Corretor house, Imobiliária (quantidade e %
  do total), Média por dia (total ÷ dias do período; em "Hoje" mostra "dia em andamento").
- **Gráfico de barras empilhadas:** por dia no período (7 e 30 dias); por hora cheia,
  das 8h às 20h, em "Hoje". Visitas fora dessa faixa entram na primeira/última barra.
  Cores: Espontânea `#3A4043`, House `#E4032B`, Imobiliária `#A3ABAE`.
- **Origem das visitas:** barra 100% e legenda com % e quantidade.
- **Imobiliárias que mais trouxeram:** top 5 por quantidade, agrupando nomes iguais
  sem caixa e sem acento (mesma regra das sugestões).
- **Por empreendimento:** tabela com total e quantidade por tipo, ordenada por total.
  Mostra todos os empreendimentos do filtro, inclusive os com zero.
- **Últimos lançamentos:** os 8 mais recentes do período filtrado (data + horário).
- **Exportar CSV:** as visitas do filtro atual, separador `;`, UTF-8 com BOM (abre
  certo no Excel), colunas `Data;Horário;Empreendimento;Cidade;Tipo;Corretor house;Imobiliária;Corretor imobiliária`,
  com a neutralização de fórmula do §4.2. Nome: `visitas-AAAA-MM-DD-a-AAAA-MM-DD.csv`.
- Estado vazio: "Nenhuma visita no período para este filtro."

## 7. Regras puras (`assets/visitas.js`)

Funções testáveis, sem DOM nem rede:

- `TIPOS` (código → nome, cor).
- `validarFormulario(dados)` → `{ ok, faltando }` (espelha a regra de obrigatoriedade do §4.2
  para o texto do botão; o servidor continua sendo a autoridade).
- `normalizarTexto(s)`, `chaveNome(s)` (sem caixa/acento), `neutralizarFormula(s)`.
- `filtrar(visitas, { de, ate, cidade, empreendimento })`.
- `totaisPorTipo`, `porDia(visitas, de, ate)`, `porHora(visitas, 8, 20)`,
  `porEmpreendimento(visitas, listaEmps)`, `rankingImobiliarias(visitas, n)`.
- `gerarCSV(visitas)`.
- `intervalo(periodo, hoje)` → `{ de, ate }` para `hoje` / `7` / `30`.

## 8. Erros

| Situação | Recepção | Dashboard |
|---|---|---|
| Sem conexão / timeout (20 s) | Faixa vermelha "Sem conexão. Tente de novo."; formulário mantido | Aviso no topo com "Tentar de novo" |
| `invalido` | Mensagem do servidor junto ao campo citado | — |
| `ocupado` | "Muitos lançamentos ao mesmo tempo, tente de novo" | idem |
| `nao_encontrada` no excluir | "Não foi possível excluir este lançamento" e recarrega a lista | — |
| `senha` | — | Volta à tela de senha |
| `coluna` / `interno` | "Erro na planilha de visitas. Avise o comercial." | idem |

## 9. Segurança e privacidade

- A recepção é pública: quem tiver o link consegue lançar visitas. **Risco aceito**,
  mitigado pela validação do §4.2 (lista fechada de empreendimentos, tipo fechado,
  datas limitadas, textos curtos, neutralização de fórmula).
- Exclusão só com token do próprio navegador e no mesmo dia (§4.3).
- `dia` expõe, sem senha, os nomes de corretores/imobiliárias do dia de um stand e as
  sugestões de imobiliárias. Aceito: não há dado de cliente.
- Senha do admin só no Apps Script (Script Property), nunca no repositório nem no
  `config.js`.
- Todo texto vindo da planilha é inserido no DOM com `textContent`, nunca `innerHTML`.
- As duas páginas usam `noindex`.

## 10. Testes

- `tests/visitas.test.js` com `node --test` (sem dependências), cobrindo:
  - `validarFormulario` nos três tipos;
  - `neutralizarFormula` (`=`, `+`, `-`, `@`, tab, CR, texto normal);
  - `chaveNome` e o agrupamento do ranking (`"Imob Ápice"` = `"imob apice "`);
  - `porDia` com dias sem visita (zero) e `porHora` com visitas fora de 8h–20h;
  - `porEmpreendimento` incluindo empreendimentos zerados;
  - `intervalo` para os três períodos;
  - `gerarCSV` (BOM, separador, neutralização, aspas em campos com `;`);
  - paridade da lista de empreendimentos entre `config.js` e o `.gs` (§4.5).
- Fixtures fictícias em `tests/fixtures/visitas.json`.
- Conferência manual do Web App com `testeVisitas()` (§4.6) e, depois do deploy, um
  lançamento real em cada tipo + checagem no dashboard.

## 11. Deploy

1. Colar `docs/apps-script-visitas.gs` no Apps Script da planilha, rodar
   `configurarSenhaVisitas()` e `testeVisitas()`, implantar como App da Web.
2. Colar a URL `/exec` em `window.VISITAS_APPS_SCRIPT_URL` no `config.js`.
3. Branch → PR → merge na `main` → deploy manual na Vercel (`WORKFLOW.md`).

## 12. Riscos

- **Lançamentos falsos na página pública.** Mitigado pela validação; se virar problema,
  a próxima versão adiciona um PIN por stand.
- **Planilha crescendo.** ~100 visitas/dia ≈ 36 mil linhas/ano. `listar` lê só as
  colunas necessárias e filtra por data; abaixo de ~100 mil linhas o Apps Script
  responde bem. Se passar disso, arquivar anos anteriores em outra aba.
- **Nomes de imobiliária digitados de formas diferentes.** Mitigado pelas sugestões e
  pelo agrupamento sem caixa/acento; variações maiores ("Imob X" vs "X Imóveis")
  continuam separadas.
- **Lista de empreendimentos desatualizada no `.gs`.** Pega pelo teste de paridade.

## 13. Revisão v2 — dados do cliente em popup (10/10/2026)

Pedido do comercial depois da v1: cada visita passa a registrar quem é o cliente e quem o
atendeu. **Esta seção substitui as partes das seções 1–12 que ela contradiz.** A v1 ainda
não foi publicada, então a aba `VISITAS` nasce direto no formato novo (sem migração).

Telas: canvas "Visitas Recepção", quadros `Main` (Passo 1 + cards), `PopupImobiliaria`,
`PopupCelular` (erros) e `Admin` (tabela de lançamentos com dados do cliente).

### 13.1 O que muda para a recepcionista

- **Passo 1 · Stand:** só o empreendimento (stand), lembrado no aparelho. Data e horário
  saem do Passo 1.
- **Passo 2:** tocar em um dos 3 cards **abre um popup** "Registrar visita", com o tipo e o
  stand no topo. Não há mais seleção de card nem botão "Registrar" fora do popup.
- Campos do popup, iguais para os 3 tipos:

| Campo | Obrigatório | Regra |
|---|---|---|
| Nome do cliente | sim | texto, até 80 caracteres |
| CPF | sim | máscara `000.000.000-00`; 11 dígitos com dígitos verificadores válidos; recusa sequências repetidas (`111.111.111-11`) |
| Telefone | sim | máscara `(00) 00000-0000` ou `(00) 0000-0000`; 10 ou 11 dígitos; DDD entre 11 e 99 |
| Data | sim | hoje ao abrir o popup; entre hoje − 7 dias e hoje |
| Horário | sim | agora ao abrir o popup; botão "Agora"; não pode passar de agora + 5 min se a data for hoje |
| Imobiliária | sim, **só no tipo Imobiliária** | texto livre com sugestões (`<datalist>`) |
| Nome do corretor | sim | texto livre com sugestões. Rótulo: "Corretor que atendeu" (espontânea), "Corretor house que agendou" (house), "Corretor da imobiliária" (imobiliária) |
| Gerente de vendas | não | texto livre com sugestões |

- Não existe mais "Empreendimento de interesse": o empreendimento é sempre o stand do Passo 1.
- **Validação:** ao tocar em "Registrar visita" com campos inválidos, o popup não fecha, cada
  campo inválido fica vermelho com a mensagem logo abaixo e o foco vai para o primeiro inválido.
  Corrigir o campo limpa o erro dele. O servidor revalida tudo; um `invalido` do servidor
  marca o campo citado da mesma forma.
- **Popup:** `<dialog>` nativo aberto com `showModal()` (foco preso, Esc fecha). "Cancelar",
  o botão de fechar e Esc descartam o que foi digitado. No celular (≤ 600 px) ocupa a tela
  inteira, com rodapé de botões fixo.
- **Ao registrar com sucesso:** o popup fecha, a faixa verde aparece com "Desfazer"
  (`hora · tipo · primeiro nome`) e o contador recarrega.
- **CPF repetido:** se o mesmo CPF já tem visita ativa **no mesmo stand e na mesma data**, a
  visita é registrada mesmo assim e a faixa fica amarela: "Visita registrada. Atenção: este
  CPF já tinha visita hoje neste stand." (com "Desfazer"). Não existe consulta de CPF antes
  de registrar, para a página pública não virar um verificador de CPF.
- **Últimos lançamentos:** cada item mostra horário, **primeiro nome** do cliente, tipo e
  detalhe (`corretor` ou `imobiliária · corretor`). Nome completo, CPF e telefone nunca
  aparecem na página pública.
- A virada de dia da v1 continua valendo; como data e horário agora estão no popup, eles são
  recalculados a cada abertura.

### 13.2 Planilha — aba `VISITAS` (substitui a tabela da §3)

`ID · Registrado em · Data · Horário · Empreendimento · Cidade · Tipo · Nome do cliente · CPF ·
Telefone · Imobiliária · Corretor · Gerente de vendas · Excluída · Token`

- `CPF` e `Telefone` gravados **só com os dígitos**, como texto (`@`), para não perder zero à
  esquerda nem virar número.
- As colunas `Corretor house` e `Corretor imobiliária` da v1 deixam de existir; o corretor de
  qualquer tipo fica em `Corretor`.
- Neutralização de fórmula vale para todos os textos livres.

### 13.3 Web App (substitui o que diverge na §4)

- **Visita completa** (só no `listar`, com senha):
  `{ id, data, hora, empreendimento, cidade, tipo, cliente, cpf /* 11 dígitos */, telefone /* dígitos */, imobiliaria, corretor, gerente }`
- **Visita resumida** (respostas públicas `registrar` e `dia`):
  `{ id, data, hora, empreendimento, tipo, primeiroNome, imobiliaria, corretor }`.
  `primeiroNome` = primeira palavra do nome do cliente. O servidor monta o resumo; CPF,
  telefone, nome completo e gerente **nunca** saem nas respostas públicas.
- `registrar { empreendimento, data, hora, tipo, cliente, cpf, telefone, imobiliaria?, corretor, gerente? }`
  → `{ visita /* resumida */, token, cpfRepetido: boolean }`.
  - `cpfRepetido` é calculado dentro do lock, antes de gravar: existe linha ativa com o mesmo
    CPF, o mesmo empreendimento e a mesma data.
- `dia { empreendimento, data }` → `{ visitas /* resumidas */, sugestoes: { imobiliarias, corretores, gerentes } }`.
  As três listas seguem a regra de `sugestoesImob` da §4.1 (últimos 90 dias, agrupadas sem
  caixa/acento, até 200, ordem alfabética) e não dependem do stand.
- Validação no servidor (§4.2 continua valendo para empreendimento, tipo, data e hora), mais:
  - `cliente`: obrigatório, normalizado, até 80 → `campo:'cliente'`;
  - `cpf`: só dígitos após remover máscara; 11 dígitos, dígitos verificadores válidos, não
    pode ser sequência repetida → `campo:'cpf'`;
  - `telefone`: só dígitos; 10 ou 11; DDD 11–99 → `campo:'telefone'`;
  - `corretor`: obrigatório → `campo:'corretor'`;
  - `imobiliaria`: obrigatório só no tipo `imob`, vazio nos outros → `campo:'imobiliaria'`;
  - `gerente`: opcional, normalizado, até 80.
- CPF e telefone nunca vão para `Logger.log`.

### 13.4 Dashboard (substitui o que diverge na §6)

- "Últimos lançamentos" ganha as colunas **Cliente, CPF, Telefone, Imobiliária, Corretor e
  Gerente**, com CPF e telefone completos e formatados (`000.000.000-00`, `(00) 00000-0000`).
- CSV: `Data;Horário;Empreendimento;Cidade;Tipo;Cliente;CPF;Telefone;Imobiliária;Corretor;Gerente de vendas`,
  com CPF e telefone formatados e a mesma neutralização de fórmula.
- Ao lado do botão "Exportar CSV": aviso curto "Contém dados pessoais (CPF e telefone)."
- Ranking de imobiliárias continua igual.

### 13.5 Segurança e privacidade (complementa a §9)

- O dashboard passa a guardar dado pessoal (LGPD). **Senha forte é requisito para publicar:**
  `configurarSenhaVisitas()` recusa senha com menos de 12 caracteres. `Comercial123` não
  será usada.
- Respostas públicas só com a visita resumida (§13.3).
- A página pública continua sem senha: alguém com o link pode registrar uma visita com dados
  de terceiros. **Risco aceito**, mitigado pela validação; o comercial pode excluir linhas
  direto na planilha.
- Retenção e exclusão de dados a pedido do titular: feitas manualmente na planilha; política
  formal fora de escopo desta versão.

### 13.6 Regras puras e testes (complementa §7 e §10)

- `assets/visitas.js` ganha: `soDigitos`, `cpfValido`, `telefoneValido`, `mascaraCpf`,
  `mascaraTelefone`, `formatarCpf`, `formatarTelefone`, `primeiroNome`, e
  `validarVisita(dados) → { ok, erros: { campo: mensagem } }` (substitui `validarFormulario`).
  `detalhe(v)` passa a usar `corretor`.
- O `.gs` tem as mesmas regras de CPF/telefone em funções próprias, testadas no Node via `vm`
  com os mesmos casos (inclusive paridade de resultado entre cliente e servidor para uma
  lista de CPFs válidos e inválidos).
- Testes novos: CPF válido/inválido/sequência/máscara; telefone 10/11/DDD inválido; máscaras
  digitando parcial; `primeiroNome`; resumo do servidor sem CPF/telefone/nome completo;
  `cpfRepetido` (mesmo CPF+stand+data, outro stand, outra data, linha excluída); CSV com as
  colunas novas.
- Fixture fictícia atualizada com cliente, CPF (válidos gerados, não reais), telefone,
  corretor e gerente.

### 13.7 Fora de escopo (substitui o item "Dados do cliente" da §1)

- Histórico do cliente entre stands ou "primeira visita vs retorno" no dashboard.
- Consulta de CPF antes de registrar.
- Ranking de corretores ou gerentes no dashboard.

## 14. Revisão v3 — contas das recepcionistas, PDV e só Ribeirão Preto (10/10/2026)

Pedido do comercial depois da v2:
- cada recepcionista tem o próprio acesso, para identificar quem lançou cada visita;
- sem login, a página de lançamento não mostra nem grava nada, mesmo que o link chegue a
  um corretor;
- por enquanto o lançamento atende só Ribeirão Preto, que tem dois stands (PDVs).

**Esta seção substitui as partes das §1–13 que ela contradiz.** Nada foi publicado ainda,
então as abas nascem direto no formato novo (sem migração).

Telas: canvas "Visitas Recepção" (mesmo link do topo).
- Recepção: `Main`, `RecepcaoCelular`, `PopupImobiliaria`, `PopupCelular`.
- Acesso: `Login`, `LoginCadastro`, `LoginPendente`, `LoginTroca`.
- Dashboard: `Admin` e `AdminRecepcionistas`.

### 14.1 Decisões

| Tema | Decisão |
|---|---|
| Criação de conta | A recepcionista se cadastra na própria página. A conta nasce **pendente** e só entra depois que o comercial aprova no dashboard |
| Sessão | Vale até a **meia-noite** (horário de Brasília) do dia do login. "Sair" encerra antes |
| Stand | A recepcionista escolhe livremente o PDV; a conta não fica presa a um stand |
| Cidades | O lançamento e o dashboard aceitam **só os empreendimentos de Ribeirão Preto**. O resto do portal continua com todas as cidades do `config.js` |
| PDV | Campo obrigatório com duas opções: **Zona Sul RP** e **Centro RP** |
| Onde fica o PDV | No **Passo 1**, lembrado no aparelho. O empreendimento vira campo obrigatório **do popup** |
| Senha do dashboard | Continua única (§4.4 e §13.5). Ela também autoriza as ações sobre as contas |

### 14.2 Acesso à recepção (`/visitas-recepcao`)

Sem sessão válida no aparelho, a página mostra só a tela de acesso. O HTML e o JS são
estáticos e públicos; o que fica protegido são os **dados e a gravação**: todo pedido da
recepção ao Web App exige a sessão.

**Entrar** (quadro `Login`):
- Campos: usuário e senha. Botão "Entrar" e link "Criar conta".
- Usuário ou senha errados: "Usuário ou senha incorretos.", mesma mensagem nos dois casos.
- Senha certa, mas a conta não foi liberada:
  - **pendente:** mostra o quadro `LoginPendente` ("Seu cadastro está aguardando aprovação
    do comercial.");
  - **desativada:** "Seu acesso foi desativado. Fale com o comercial."
  - Esses avisos só aparecem com a senha certa, para a tela não revelar quais usuários
    existem.
- 5 senhas erradas seguidas para o mesmo usuário bloqueiam esse usuário por 15 minutos:
  "Muitas tentativas. Tente de novo em 15 minutos." Login certo zera a contagem.

**Criar conta** (quadro `LoginCadastro`):

| Campo | Regra |
|---|---|
| Nome completo | obrigatório, normalizado, até 80 caracteres |
| Usuário | obrigatório; 3 a 30 caracteres; letras minúsculas sem acento, números, `.`, `-` e `_`; o que for digitado é convertido para minúsculas; único |
| Senha | 8 a 72 caracteres; não pode ser igual ao usuário |
| Confirmar senha | igual à senha (só no navegador) |

- Usuário já existente: erro no campo, "Esse usuário já existe."
- Sucesso: a tela "Cadastro enviado" diz que é preciso esperar a aprovação do comercial e
  oferece "Voltar para entrar".
- Com 20 cadastros pendentes, novos cadastros são recusados: "Muitos cadastros aguardando
  aprovação. Fale com o comercial." Isso limita o abuso do formulário público.

**Trocar senha temporária** (quadro `LoginTroca`):
- Aparece logo depois do login quando o comercial redefiniu a senha (§14.5).
- Campos: nova senha e confirmação (mesmas regras do cadastro). A nova senha não pode ser
  igual à temporária.
- Até trocar, a sessão não serve para mais nada.

**Sessão no aparelho:**
- Fica no `localStorage` (`visitas.sessao`) como `{ token, expira, nome, usuario }`.
- Ao abrir a página, sessão vencida (passou de `expira`) é apagada e volta a tela de acesso.
- A checagem de virada de dia da v1 também verifica a sessão: depois da meia-noite, a página
  volta para a tela de acesso.
- Qualquer resposta `sessao` do servidor (vencida, conta desativada, senha trocada) apaga a
  sessão e volta para "Entrar", com o aviso "Sua sessão terminou. Entre de novo."
- O topo mostra "Olá, {primeiro nome}" e o botão "Sair". "Sair" apaga a sessão no aparelho.
- A chave `visitas.tokens` da v1/v2 deixa de existir; a página apaga essa chave se a
  encontrar.

### 14.3 O que muda no lançamento (substitui o que diverge na §13.1)

- **Passo 1 · PDV:** dois botões, **Zona Sul RP** e **Centro RP**, lembrados no aparelho
  (`visitas.pdv`; a chave antiga `visitas.emp` é apagada). Sem PDV escolhido, os cards do
  Passo 2 ficam bloqueados com a dica "Escolha o PDV primeiro".
- **Popup:** ganha, no topo dos campos, **Empreendimento de interesse** (`<select>`,
  obrigatório). Ele lista só os 4 empreendimentos de Ribeirão Preto, na ordem do `config.js`
  e começa vazio ("Selecione"). O topo do popup mostra tipo e PDV.
- Ordem de validação e foco: empreendimento, cliente, cpf, telefone, data, hora,
  imobiliaria, corretor.
- **Contador e "Últimos lançamentos":** valem para o **PDV** escolhido e para hoje. Todas as
  recepcionistas do mesmo PDV veem os mesmos números e a mesma lista.
- Cada item da lista mostra também o empreendimento.
- **CPF repetido:** a regra passa a ser mesmo CPF + **mesmo PDV** + mesma data. A mensagem
  vira "Atenção: este CPF já tinha visita hoje neste PDV."
- **Excluir:** o botão aparece só nos lançamentos **da própria recepcionista**, feitos hoje.
  "Desfazer" da faixa usa a mesma regra.

### 14.4 Planilha

**Aba `RECEPCIONISTAS`** (nova; criada pelo script se não existir):

`Usuário · Nome · Situação · Hash · Sal · Temporária · Criado em · Aprovado em · Último acesso`

- `Situação`: `pendente`, `ativa` ou `desativada`.
- A senha **nunca** é gravada. `Hash` guarda SHA-256 iterado 1.000 vezes sobre
  `sal + senha`, em base64. `Sal` é aleatório por conta (`Utilities.getUuid()`).
  - O Apps Script não tem bcrypt/scrypt; a iteração encarece tentativas em massa se a planilha
    vazar. **Risco aceito**, já que a planilha é privada.
- `Temporária`: `sim` quando a senha foi gerada pelo comercial e precisa ser trocada.
- Colunas localizadas pelo nome do cabeçalho, como na `VISITAS`. Textos com neutralização
  de fórmula. `Usuário` gravado como texto (`@`).

**Aba `VISITAS`** (substitui a §13.2):

`ID · Registrado em · Data · Horário · PDV · Empreendimento · Cidade · Tipo · Nome do cliente ·
CPF · Telefone · Imobiliária · Corretor · Gerente de vendas · Lançado por · Excluída`

- `Lançado por` guarda o **usuário** da recepcionista. Ele não muda; o nome pode mudar.
- `Cidade` continua sendo preenchida ("Ribeirão Preto").
- A coluna `Token` sai: a exclusão passa a usar a dona da visita (§14.3).

### 14.5 Web App (substitui o que diverge nas §4 e §13.3)

**Sessão:**
- Token `usuario.expira.assinatura`.
  - `expira`: meia-noite seguinte em `America/Sao_Paulo`, em milissegundos. O Brasil não tem
    horário de verão desde 2019, então o fuso é fixo em −03:00.
  - `assinatura`: HMAC-SHA256 de `usuario.expira.<12 primeiros caracteres do Hash>`, com o
    segredo da Script Property `VISITAS_SEGREDO`, em base64 web-safe.
  - Como o hash entra na assinatura, trocar ou redefinir a senha derruba as sessões abertas.
- O segredo é gerado na primeira vez que for preciso (dois `getUuid()` concatenados) e nunca
  sai do servidor.
- Toda ação da recepção faz o mesmo:
  1. confere assinatura e validade do token;
  2. lê a linha da conta;
  3. exige `Situação = ativa` e `Temporária ≠ sim` (exceto em `trocarSenha`).
- Falha em qualquer passo → `erro:'sessao'`, sempre com a mesma mensagem: "Sua sessão
  terminou. Entre de novo."
- A comparação da assinatura não depende de onde está a primeira diferença.

**Ações públicas** (sem sessão):
- `entrar { usuario, senha }` → `{ sessao, expira, nome, usuario, trocarSenha: boolean }`.
  - Erros: `credenciais`, `bloqueado`, `pendente`, `desativada`.
  - As tentativas erradas são contadas no `CacheService` (`vis.falhas.<usuario>`, 15 minutos);
    na quinta, o usuário fica bloqueado.
  - Conta inexistente também passa pelo cálculo do hash, para levar o mesmo tempo.
  - Atualiza `Último acesso`.
- `cadastrar { nome, usuario, senha }` → `{ ok: true }`. Erros: `invalido` (com `campo`),
  `limite`. Grava dentro do lock e confere a unicidade dentro do lock.

**Ações da recepção** (com `sessao`):
- `trocarSenha { sessao, novaSenha }` → nova `{ sessao, expira, ... }`, com `Temporária` limpa.
- `registrar { sessao, pdv, empreendimento, data, hora, tipo, cliente, cpf, telefone, imobiliaria?, corretor, gerente? }`
  → `{ visita /* resumida */, cpfRepetido }`.
  - `pdv` precisa estar em `VISITAS_PDVS` → `campo:'pdv'`.
  - `empreendimento` precisa estar na lista de Ribeirão Preto → `campo:'empreendimento'`.
  - Grava `Lançado por` = usuário da sessão.
- `dia { sessao, pdv, data }` → `{ visitas /* resumidas */, sugestoes }`.
- `excluir { sessao, id }`: só quando a linha é da recepcionista da sessão e foi registrada
  hoje. Fora disso → `nao_encontrada`, como antes.

**Visita resumida** (respostas da recepção):
`{ id, data, hora, pdv, empreendimento, tipo, primeiroNome, imobiliaria, corretor, minha: boolean }`.
- `minha` diz se a visita foi lançada pela recepcionista da sessão.
- O usuário de quem lançou não sai nas respostas da recepção.

**Ações do dashboard** (com `senha`; a §4.4 continua valendo):
- `listar`: a visita completa ganha `pdv` e `lancadoPor`.
  - `lancadoPor` é o **nome** atual da recepcionista, ou o usuário se a conta não existir mais.
- `contas` → `{ contas: [{ usuario, nome, situacao, temporaria, criadoEm, ultimoAcesso, visitas30 }] }`.
  - Não traz `Hash` nem `Sal`.
  - `visitas30` conta as visitas ativas lançadas por ela nos últimos 30 dias.
- `aprovar { usuario }`: `pendente` → `ativa`, e grava `Aprovado em`.
- `recusar { usuario }`: apaga a linha `pendente`. O usuário fica livre para um novo cadastro.
- `desativar { usuario }` / `reativar { usuario }`: `ativa` ↔ `desativada`.
  - Desativar derruba a sessão na próxima ação dela.
  - As visitas já lançadas continuam.
- `redefinirSenha { usuario }` → `{ senhaTemporaria }`. Gera 9 caracteres em 3 grupos
  (`K7m-Q2x-9Tz`), sem caracteres ambíguos (0/O, 1/l/I), e marca `Temporária = sim`.
  - A senha temporária aparece **uma vez** na resposta e não é guardada em claro.
- Todas as ações que alteram contas rodam no lock.
- Usuário inexistente ou em situação errada → `nao_encontrada`.

**Listas oficiais:**
- `VISITAS_EMPREENDIMENTOS` passa a ter só os 4 de Ribeirão Preto.
- O teste de paridade compara com `window.CITIES` da cidade "Ribeirão Preto". Se um
  empreendimento novo de RP entrar no portal sem entrar no Web App, o teste quebra.
- Nova constante `VISITAS_PDVS = ['Zona Sul RP', 'Centro RP']`, igual no `.gs` e em
  `assets/visitas.js`, também com teste de paridade.

**Logs:**
- Nada de senha, hash, sal, token ou segredo no `Logger.log`, além do que a §13.3 já proíbe.
- Os erros esperados (`credenciais`, `sessao` etc.) não são logados.

**`testeVisitas()`:**
1. cria uma conta de teste já `ativa`;
2. entra;
3. registra, lê o `dia` e exclui;
4. apaga a conta de teste.

A linha de visita de teste fica marcada como excluída.

### 14.6 Dashboard (substitui o que diverge nas §6 e §13.4)

- Navegação no topo com duas abas, **Visitas** e **Recepcionistas**. A aba Recepcionistas
  mostra um selo com o número de cadastros pendentes.
- **Visitas:**
  - os chips de cidade viram chips de **PDV**: Todos, Zona Sul RP, Centro RP;
  - o seletor de empreendimento lista só Ribeirão Preto;
  - KPIs, gráficos e tabelas seguem o filtro de PDV;
  - "Últimos lançamentos" ganha as colunas **PDV** e **Lançado por**.
  - CSV:
    `Data;Horário;PDV;Empreendimento;Tipo;Cliente;CPF;Telefone;Imobiliária;Corretor;Gerente de vendas;Lançado por`.
    A coluna Cidade sai, porque é sempre Ribeirão Preto.
- **Recepcionistas** (quadro `AdminRecepcionistas`):
  - "Aguardando aprovação": nome, usuário e data do cadastro, com **Recusar** e **Aprovar**.
    O bloco some quando não há pendentes.
  - Tabela das contas: Nome, Usuário, Situação (selo Ativa/Desativada, mais "Senha temporária"
    quando houver), Visitas (30 dias), Último acesso, e as ações **Redefinir senha** e
    **Desativar**/**Reativar**.
  - Recusar, Desativar e Redefinir senha pedem confirmação (`confirm()`) antes de enviar.
  - Depois de redefinir, uma faixa amarela mostra a senha temporária uma única vez, com o
    nome da recepcionista. Ela some ao trocar de aba ou recarregar.
  - Depois de cada ação, a lista de contas é recarregada.

### 14.7 Regras puras e testes (complementa §7, §10 e §13.6)

**`assets/visitas.js` ganha:**
- `PDVS`;
- `usuarioValido`, `normalizarUsuario`;
- `validarSenha(senha, usuario) → mensagem | ''`;
- `validarCadastro(d) → { ok, erros }`;
- `sessaoValida(sessao, agoraMs)`.

**`validarVisita`** passa a exigir `pdv` e `empreendimento`. `resumirVisita` inclui `pdv`. O
CSV usa as colunas da §14.6.

**O `.gs` tem as próprias versões:** hash da senha, geração e conferência do token, validação
de usuário e senha, expiração na meia-noite, senha temporária e checagem de dona da visita.
Todas são puras e testadas no Node via `vm`, com `Utilities` e `CacheService` falsos.

**Testes novos:**
- token: válido, vencido, assinatura alterada, outro usuário, hash da senha trocado;
- meia-noite: antes e depois das 21h UTC;
- hash: o mesmo sal e a mesma senha dão o mesmo hash, e outro sal dá outro;
- usuário e senha: casos de borda;
- senha temporária: formato e sem caracteres ambíguos;
- bloqueio na 5ª falha e desbloqueio depois de login certo;
- `excluir` recusando visita de outra recepcionista e visita de ontem;
- `cpfRepetido` por PDV;
- resumo com `minha` e sem usuário;
- paridade de PDVs e de empreendimentos de RP;
- `contas` sem hash nem sal.

**Modo demonstração** (`?demo=1` ou URL vazia):
- entra com qualquer usuário e qualquer senha de 8+ caracteres;
- simula pendente, troca de senha e as ações do dashboard em memória;
- os dados fictícios passam a ter PDV e "Lançado por".

### 14.8 Deploy (complementa a §11)

1. Colar o `.gs` novo.
2. Se a senha do dashboard ainda não foi configurada: definir uma de 12+ caracteres só no
   editor, rodar `configurarSenhaVisitas()` e voltar `VIS_SENHA_INICIAL` para `''`.
3. Rodar `testeVisitas()`. Ele cria as abas `VISITAS` e `RECEPCIONISTAS`.
4. Publicar uma **nova versão** do Web App.
5. Primeira conta real: a recepcionista se cadastra e o comercial aprova no dashboard.

### 14.9 Riscos e fora de escopo

**Riscos aceitos:**
- **Senha simples (8+):** com bloqueio por usuário, cobre o caso "link caiu na mão de um
  corretor".
- **Ataque distribuído entre muitos usuários:** não tem limite global. Fica para depois se
  aparecer.
- **Sessão de dia inteiro num aparelho compartilhado do stand:** a recepcionista precisa tocar
  em "Sair" na troca de turno; o "Olá, {nome}" no topo deixa claro quem está logada.
- **Enumeração de usuários pelo cadastro:** "Esse usuário já existe." revela que o usuário
  existe, mas o impacto é baixo porque ainda é preciso a senha e a aprovação.

**Fora de escopo:**
- "Esqueci minha senha" por e-mail: a recepcionista pede ao comercial, que usa "Redefinir
  senha".
- Contas para o comercial (o dashboard continua com senha única).
- Prender a conta a um PDV.
- Outras cidades no lançamento.
- Histórico de quem aprovou ou desativou cada conta.

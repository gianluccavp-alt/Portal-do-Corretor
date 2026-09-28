# Pendências de Vendas — design

**Data:** 28/09/2026
**Status:** aprovado no brainstorm, aguardando revisão da spec
**Página:** `https://produtosdirecional.vercel.app/pendencias-vendas`
**Planilha:** `1gN6J3UNfdj3EHxGWgkctJ4uSP4XO01HFjCE3caunooM`, aba `RELATÓRIO`
**Telas aprovadas:** `docs/design/pendencias-vendas/` (PNGs em `telas/`)

## 1. Objetivo

Dar ao time comercial uma tela para **cobrar pendências de vendas**: ver, venda por
venda, o que ainda trava o fechamento (AC, FID, PCV, ato), registrar o retorno e
marcar vendas canceladas, sem abrir a planilha.

É uma ferramenta operacional, não um painel de resultado: não há gráficos nem
ranking de equipes nesta versão.

### Fora de escopo

- Gráficos, evolução no tempo e ranking por equipe.
- Identificar quem fez cada alteração (senha única e compartilhada; sem log de autoria).
- Editar colunas vindas do Salesforce (Fase, FID, PCV, pagamentos, valor etc.).
- Mudar a lógica do `atualizarRelatorioSalesforce()`. A única alteração nele é
  gravar o horário da última execução (§4.4).

## 2. Arquitetura

```
pendencias-vendas.html  ──POST text/plain──▶  Web App (Apps Script da planilha)
  (estático, Vercel)    ◀──── JSON ─────────   doPost: listar | cancelar | reativar
                                               | editar | atualizar
                                                       │
                                                       ▼
                                          RELATÓRIO (lê e grava)
                                          atualizarRelatorioSalesforce()
```

- **Tudo passa pelo Web App.** A página não lê o CSV da planilha. Motivos:
  - edições aparecem na hora (o CSV publicado atrasa ~5 min);
  - a senha é conferida no servidor;
  - a planilha pode deixar de ser pública.
- O Web App fica no **mesmo projeto Apps Script vinculado à planilha**, como um
  arquivo novo (`Pendencias.gs`), ao lado do script atual. Assim ele usa
  `getActiveSpreadsheet()` e chama `atualizarRelatorioSalesforce()` direto.
  - Implantação: *App da Web · Executar como: Eu · Quem tem acesso: Qualquer pessoa*.
- `POST` com `Content-Type: text/plain;charset=utf-8`, para evitar o preflight de
  CORS (mesmo padrão da `/promocionais`).

### Arquivos

| Arquivo | Papel |
|---|---|
| `pendencias-vendas.html` | Página: tela de senha, dashboard, painel de detalhe, diálogos. HTML/CSS/JS puro, no padrão de `escala-comercial-rp.html`. `cleanUrls` já serve em `/pendencias-vendas`. |
| `assets/pendencias.js` | Funções **puras**: normalização, derivação de pendências, filtros, ordenação, KPIs, formatação. Exporta em `window.Pendencias` e `module.exports`, para rodar no navegador e no Node. |
| `assets/config.js` | Ganha `window.PENDENCIAS_APPS_SCRIPT_URL` (URL `/exec`). **A senha não entra aqui.** |
| `docs/apps-script-pendencias.gs` | Código do Web App, com instruções de implantação no cabeçalho (como `docs/apps-script-promocionais.gs`). |
| `tests/pendencias.test.js` | Testes de `assets/pendencias.js` com `node --test` (sem dependências). |

## 3. Acesso

- A página abre na tela de senha e chama `listar` com a senha digitada.
  - Resposta `{erro:'senha'}`: mostra "Senha incorreta" (estado 3 em `Estados.png`).
  - Resposta `ok`: guarda a senha em `sessionStorage` e renderiza o dashboard.
- Toda requisição leva a senha. Se o servidor responder `erro:'senha'` no meio do
  uso (senha trocada), limpa o `sessionStorage` e volta à tela de senha.
- "Sair" limpa o `sessionStorage`. Fechar a aba também desloga.
- A senha fica **só no Apps Script**, na Script Property `PENDENCIAS_SENHA`,
  gravada uma vez pela função `configurarSenhaPendencias()`. Valor inicial: `Comercial123`.
- A página usa `<meta name="robots" content="noindex">`.

## 4. Web App (`docs/apps-script-pendencias.gs`)

### 4.1 Contrato

- Requisição: `{ senha, acao, ...parâmetros }`.
- Resposta de sucesso: `{ ok: true, ... }`.
- Resposta de falha: `{ ok: false, erro: 'senha' | 'nao_encontrada' | 'ocupado' | 'coluna' | 'interno', mensagem }`.
- Senha errada nunca devolve dado.

| `acao` | Parâmetros | Faz | Devolve |
|---|---|---|---|
| `listar` | — | Lê o RELATÓRIO | `{ vendas, salesforceAtualizadoEm }` |
| `cancelar` | `id` | Pinta a linha da OP de vermelho `#ff0000` + tachado em todas as colunas de dados e grava `__ORDEM_CANCELADA = 1` | `{ venda }` |
| `reativar` | `id` | Fonte preta `#000000`, sem tachado, `__ORDEM_CANCELADA = 0` | `{ venda }` |
| `editar` | `id, observacao, retorno` | Grava as colunas `Observação` e `Retorno` da OP | `{ venda }` |
| `atualizar` | — | Roda `atualizarRelatorioSalesforce()` | igual a `listar` |

### 4.2 Leitura (`listar`)

- Cabeçalho na **linha 3**. Colunas localizadas **pelo nome**, nunca pela posição.
  Falta `ID`, `Observação` ou `Retorno` → `erro:'coluna'` com o nome que faltou.
- Pula linhas sem `ID`.
- `cancelada` é calculada na hora pela fonte (`getFontColors`/`getFontLines`) das
  colunas de dados, com a mesma lista de vermelhos e o mesmo tachado do
  `aplicarFormatacaoEOrdenacaoRelatorio()`. Assim vale também para vendas
  canceladas à mão na planilha, antes de o script rodar de novo.
- Datas saem como `dd/MM/yyyy` (e `dd/MM/yyyy HH:mm` para o PCV), via
  `Utilities.formatDate` no fuso da planilha.
- `valorReal` sai como número, ou `null` se estiver vazio ou não for número.
- Formato de cada venda:

```js
{ id, cliente, dataVenda, fase, imobiliaria, empreendimento, identificador,
  vendaFacilitada /* bool */, fid, pcvAssinadoEm, boletoPago /* bool */,
  cartaoPago /* bool */, valorReal, ranking, justificativa, statusAC,
  observacao, retorno, cancelada /* bool */ }
```

- Os booleanos seguem as regras do script:
  - `vendaFacilitada`: `"verdadeiro"` ou `"true"`;
  - `boletoPago` / `cartaoPago`: `"Sim"`, normalizado.
- O servidor não calcula pendência. Ele só devolve os dados, e as regras de
  negócio ficam em `assets/pendencias.js`, que tem teste.

### 4.3 Escrita e concorrência

- `cancelar`, `reativar`, `editar` e `atualizar` rodam dentro de
  `LockService.getScriptLock().waitLock(30000)`. Se o lock não sair em 30 s →
  `erro:'ocupado'` ("Tem uma atualização em andamento, tente em instantes").
- A linha é localizada **pelo ID da OP dentro do lock**, logo antes de gravar. O
  `atualizarRelatorioSalesforce()` insere linhas e reordena a aba, então número de
  linha guardado fica errado. ID inexistente → `erro:'nao_encontrada'`.
- Edições simultâneas na mesma venda: **vale a última gravação**. Aceito, porque
  o time é pequeno e cada edição devolve a venda atualizada.
- `listar` não pega lock (só lê). Se coincidir com um `atualizar`, pode vir um
  retrato intermediário. Na próxima carga fica certo.

### 4.4 Atualizar do Salesforce

- `atualizar` chama `atualizarRelatorioSalesforce()` e devolve a lista nova.
- Esse script grava célula por célula e pode levar mais de 1 minuto. O limite do
  Apps Script é 6 min por execução. A página espera até 6 min e mostra o estado 1
  (`Estados.png`), com o botão desabilitado e as edições pausadas.
- **Única alteração no script existente:** ao final de
  `atualizarRelatorioSalesforce()`, gravar
  `PropertiesService.getScriptProperties().setProperty('PENDENCIAS_ULTIMA_ATUALIZACAO', new Date().toISOString())`.
  - Vale tanto para o botão da página quanto para o menu da planilha.
  - O cabeçalho da página mostra "Salesforce atualizado hoje às HH:mm" (ou a data,
    se não for hoje). Sem registro → "Última atualização do Salesforce desconhecida".

## 5. Regras de negócio (`assets/pendencias.js`)

`normalizar(texto)` = trim + minúsculas + sem acento, igual ao `normalizarTexto` do script.

### 5.1 Universo padrão

- Fases padrão: **Aprovado Pró Soluto, Proposta Aprovada, Aprovado SAFI e Análise SAFI**
  (as mesmas do `aplicarFiltroFaseRelatorio`).
- O filtro de Fase é múltiplo e lista todas as fases presentes. Ele vem com essas
  4 marcadas, e o usuário pode marcar qualquer outra, inclusive "Fechado e ganho",
  para ver todas as vendas.
- Canceladas ficam ocultas por padrão. A chave "Mostrar canceladas (N)" as inclui,
  sempre **no fim da lista**, esmaecidas e tachadas.

### 5.2 Pendências de uma venda

| Pendência | Regra | Chip | Estilo |
|---|---|---|---|
| AC não aprovada | `normalizar(statusAC) !== 'analise aprovada'` | "AC reprovada" se `analise reprovada`; "AC em análise" se `enviado para analise`; "AC não enviada" se vazio ou `rascunho` | reprovada/não enviada: erro · em análise: alerta |
| Sem FID | `fid` vazio | "Sem FID" | alerta |
| PCV não assinado | `pcvAssinadoEm` vazio | "PCV não assinado" | alerta |
| Ato não pago | `!boletoPago && !cartaoPago` (um dos dois pagos basta) | "Ato não pago" | alerta |

- Um Status AC fora dessa lista conta como "AC não aprovada", com o próprio texto no chip.
- Uma venda sem nenhuma pendência continua aparecendo se passar nos filtros. Não
  há hoje nenhuma nesse caso (as 52 do universo padrão têm pelo menos uma).

### 5.3 Derivados de exibição

- **Dias em aberto** = hoje − `dataVenda`. Com 15 dias ou mais, fica em destaque
  âmbar (`#8A5700`). Sem data → "—".
- **Cliente** em maiúsculas/minúsculas normais (a planilha vem toda em maiúscula),
  mantendo `da`, `de`, `do`, `dos`, `das` e `e` em minúscula.
- **Equipe**:
  - tira o prefixo `DIRECIONAL VENDAS SPI – ` / `- `;
  - `SPI - CANAL IMOB PJ – X` vira `Canal PJ · X`;
  - o resto também em maiúsculas/minúsculas normais;
  - o sufixo ` - Inativo` é mantido.
- **Justificativa** vazia ou só `.` → "Sem justificativa registrada".
- **Nota da linha**: mostra o `Retorno` se houver ("Retorno: …"), senão a
  `Observação` ("Obs.: …"), em uma linha com reticências.
- **Valor**: `R$ 214.900` (sem centavos na lista, com centavos no detalhe);
  `null` → "Não informado".

### 5.4 Filtros

Todos combinam com E.

| Filtro | Tipo | Padrão |
|---|---|---|
| Busca | texto; procura sem acento em cliente, ID e identificador | vazio |
| Empreendimento | seleção única | Todos |
| Imobiliária/equipe | seleção única (rótulo abreviado de §5.3) | Todas |
| Fase | múltipla | as 4 de §5.1 |
| Data da venda | Todo o período · Este mês · Mês passado · Últimos 30 dias · Intervalo (de/até) | Todo o período |
| Ranking | Todos · Diamante · Ouro · Prata · Bronze · Aço | Todos |
| Tipo de venda | Comercial e facilitada · Só comercial · Só facilitada | Comercial e facilitada |
| Pendência | chips de escolha única: Todas · AC não aprovada · Sem FID · Ato não pago · PCV não assinado | Todas |
| Mostrar canceladas | chave | desligada |

- "Limpar filtros" volta tudo ao padrão.
- Os filtros ficam só na memória da aba. Recarregar a página volta ao padrão.

### 5.5 KPIs

- Calculados sobre as vendas que passam em **todos os filtros menos o de Pendência**,
  sem canceladas. Assim o KPI mostra o tamanho de cada pendência dentro do recorte.
- KPIs: Vendas com pendência · AC não aprovada · Sem FID · Ato não pago ·
  PCV não assinado · VGV pendente (soma de `valorReal`).
- Clicar num KPI de pendência seleciona o chip correspondente.
- Subtextos:
  - "N canceladas ocultas";
  - "X reprovadas · Y em análise ou não enviadas" (AC). No mock está "10 sem
    retorno"; muda para não confundir com a coluna Retorno;
  - "% das vendas" (FID).

### 5.6 Ordenação

- Opções:
  - **Mais antigas primeiro** (padrão);
  - Mais recentes primeiro;
  - Maior valor;
  - Mais pendências.
- Empate: pela ordem da planilha.
- Canceladas sempre por último.
- A lista mostra todas as vendas filtradas, sem paginação (hoje são dezenas).
  O "Mostrar mais" do mock sai.

## 6. Telas e interação

Referência: `docs/design/pendencias-vendas/telas/`.
Visual: `DESIGN.md` (mundo Direcional).

- **Senha** (`Senha.png`, `Mobile-Senha.png`): campo com botão de mostrar senha; Enter envia.
- **Lista** (`Main.png`, `Mobile-Lista.png`):
  - cabeçalho com a hora do Salesforce, "Atualizar do Salesforce" e "Sair";
  - KPIs, filtros e tabela.
  - Abaixo de 820 px: vira cartões, KPIs em 2 colunas, busca + botão
    "Filtros · N", que abre uma folha inferior com os filtros de seleção, e chips
    de pendência com rolagem horizontal.
- **Detalhe** (`Detalhe.png`, `Mobile-Detalhe.png`):
  - Abre ao clicar na linha ou cartão. No desktop é um painel lateral de 620 px;
    no celular, tela cheia.
  - Mostra:
    - dados da venda;
    - "O que falta" (✕/!/✓ por item de §5.2);
    - Justificativa da AC (só leitura);
    - Observação e Retorno editáveis.
  - Botões: "Salvar alterações" (desabilitado sem mudança), "Descartar" e
    "Marcar como cancelada" / "Reativar venda".
  - Fechar com alteração não salva pede confirmação. Esc fecha e o foco volta à linha.
- **Cancelar** (`Cancelar.png`): diálogo de confirmação. Ao confirmar, a venda sai
  da lista e aparece o aviso "Venda OP-… cancelada · Desfazer". Desfazer = `reativar`.
- **Estados** (`Estados.png`): atualizando, salvo, senha incorreta, sem resultado,
  falha de conexão, cancelada visível.

Depois de qualquer gravação, a página troca a venda local pela `venda` devolvida
(sem recarregar tudo) e recalcula KPIs e lista.

## 7. Erros

| Situação | Comportamento |
|---|---|
| Rede/timeout no `listar` | Estado 5 "Não deu para carregar as vendas" + "Tentar de novo". |
| Rede/timeout numa gravação | Aviso de erro. O painel continua aberto com o texto digitado, para tentar de novo. Nada se perde. |
| `erro:'senha'` | Limpa a sessão e volta à tela de senha com "Senha incorreta". |
| `erro:'ocupado'` | Aviso "Tem uma atualização em andamento, tente em instantes". |
| `erro:'nao_encontrada'` | Aviso "Essa venda não está mais no relatório" + recarrega a lista. |
| `erro:'coluna'` / `interno` | Aviso com a `mensagem` do servidor (ex.: "Coluna Retorno não encontrada no RELATÓRIO"). |
| Resposta não-JSON (implantação errada) | Estado 5 com "O Web App não respondeu no formato esperado". |

- Todo texto vindo da planilha é inserido com `textContent`, nunca `innerHTML`.
  Justificativas e observações são texto livre.

## 8. Segurança e privacidade

- A planilha tem nome de cliente e, em algumas justificativas, **CPF**. Hoje ela
  está aberta para qualquer pessoa com o link.
- Com esta arquitetura a página não depende do link público. **Recomendação:**
  depois de publicar, tirar o compartilhamento "qualquer pessoa com o link" da
  planilha. É um passo manual do dono da planilha e fica no checklist de deploy.
  Antes, confirmar que nada mais lê o CSV dela.
- Senha única compartilhada: é uma barreira simples, suficiente para uso interno.
  `Comercial123` é fraca e fácil de adivinhar. Trocar é só mudar a Script
  Property, sem deploy do site. O Apps Script não tem IP para limitar tentativas.
- A URL `/exec` fica visível no código da página. Sem a senha, ela não devolve nada.

## 9. Testes

- **`tests/pendencias.test.js`** (`node --test`), cobrindo `assets/pendencias.js`:
  - `normalizar`;
  - derivação de pendências para cada Status AC, FID/PCV vazios e as 4
    combinações de boleto/cartão;
  - cada filtro isolado e combinado;
  - universo padrão (4 fases, sem canceladas);
  - KPIs ignorando o filtro de pendência;
  - ordenações e canceladas por último;
  - formatação de cliente, equipe (os 3 formatos reais), valor e dias em aberto.
- **Fixture:** `tests/fixtures/vendas.json` com ~15 vendas fictícias no formato
  de §4.2, cobrindo os casos acima. Sem dado real.
- **Apps Script:** função `testePendencias()` no próprio `.gs`. Ela roda `listar`
  internamente e loga total, canceladas, contagem por fase e colunas encontradas,
  para conferir no editor antes de implantar.
- **Manual (checklist de aceite no navegador, local e depois produção):**
  - senha errada e senha certa;
  - KPIs batem com a planilha (52 / 45 / 49 / 25 / 10 hoje);
  - cada filtro;
  - editar Retorno → conferir na planilha;
  - cancelar → linha vermelha tachada na planilha → Desfazer;
  - "Atualizar do Salesforce";
  - celular a 390 px.

## 10. Deploy

1. Colar `docs/apps-script-pendencias.gs` como `Pendencias.gs` no projeto
   Apps Script da planilha.
2. Adicionar a linha de §4.4 ao fim de `atualizarRelatorioSalesforce()`.
3. Rodar `configurarSenhaPendencias()` uma vez e depois `testePendencias()`.
4. Implantar como App da Web (Executar como: Eu · Qualquer pessoa) e copiar a URL `/exec`.
5. Colocar a URL em `window.PENDENCIAS_APPS_SCRIPT_URL` (`assets/config.js`).
6. Branch → PR → merge na `main` → **deploy manual na Vercel** (`WORKFLOW.md`).
7. Checklist manual de §9 em produção.
8. (Recomendado) tirar o compartilhamento público da planilha (§8).

## 11. Riscos

- **O script atual demora** (grava célula por célula). Se passar de 6 min, o
  Apps Script mata a execução pelo botão. A página mostra o erro, e o caminho
  continua sendo rodar pelo menu da planilha. Otimizar o script fica fora desta
  entrega.
- **Cabeçalho renomeado na planilha** quebra a leitura. Mitigação: `erro:'coluna'`
  diz exatamente qual coluna faltou.
- **Cota do Apps Script** (execuções simultâneas de Web App ~30). Não é problema
  para o tamanho do time.

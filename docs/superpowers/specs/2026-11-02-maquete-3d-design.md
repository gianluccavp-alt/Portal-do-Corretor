# Maquete 3D interativa — espelho de vendas em 3D (piloto: Village Gaia)

Data: 2026-11-02 · Status: rascunho para aprovação

## Intenção

Um recurso a mais — "a cereja do bolo" — sem substituir nada do que o portal já tem
(aba Unidades, plantas, implantação, Match, simuladores). O corretor, na mesa de
atendimento, abre o empreendimento em 3D, gira o condomínio na frente do cliente, vê
de relance o que está disponível e clica no apartamento para mostrar os detalhes
daquela unidade.

Referência visual e de comportamento: reel "Tabela em 3D!!" (@gustavowmoraes) — uma
torre 3D à noite em que **janela acesa = unidade**, hover mostra tipologia/status e o
clique abre painel com unidade, área, pavimento, valor e fluxo, com "anterior/próxima
disponível", câmeras prontas (Frente, Lateral, Fundos, Rooftop), Dia/Noite e um
indicador "% vendido". Aqui o objetivo é a mesma experiência, mas **com o prédio real**
(no reel o prédio é genérico/estilizado).

O porquê: impressionar e encurtar a explicação na apresentação ("é este aqui, no 12º,
virado para o nascente, ao lado do lazer"), mantendo a regra-mãe do portal — **a tela é
espelho da planilha oficial**.

## Decisões do usuário

- **Piloto em um empreendimento: Village Gaia (Ribeirão Preto).** Expansão para outros
  vem depois, fora deste escopo.
- **Fidelidade: tem que parecer o prédio real.** O cliente reconhece a fachada do book.
  Modelagem no **Blender** (gratuito) operado pelo Claude Code via **blender-mcp**, a
  partir dos renders e da implantação que já estão no repo. Exportado como `.glb`.
- **Cena: as 3 torres + terreno simples** (grama, caminhos/estacionamento em plano,
  algumas árvores), com as torres na posição e orientação da implantação. Sem modelar
  o lazer, guarita ou carros.
- **Quem usa: o corretor apresentando** (não é link para o cliente navegar sozinho).
- **Aparelho prioritário: notebook/desktop.** No celular/tablet deve abrir e funcionar,
  mas não precisa ser impecável.
- **Entrada: botão "Maquete 3D" na página do empreendimento** que abre uma
  **página própria em tela cheia** (`maquete.html?e=village-gaia`). O botão só aparece
  em empreendimentos que tiverem maquete configurada.
- **Status visual: os dois modos, com botão para alternar.**
  - Padrão **Noite**: disponível = janela acesa (luz quente); indisponível = apagada.
  - **Cores** (dia): disponível / reservada / vendida em cores distintas.
- **Painel ao clicar na unidade** mostra:
  1. Identificação: torre, andar, final, tipologia + imagem da planta do tipo.
  2. Posição e sol: ponta/meio, sol da manhã (nascente) e uma **câmera mostrando a
     vista daquela altura/fachada**.
  3. **Valor igual ao da aba Unidades**: Associativo/Investidor em destaque e Tabela
     Direta menor, usando as mesmas funções `associativoOf` / `tabelaDiretaOf` de
     `assets/data.js`. Isso inclui a regra de unidade promocional e o ajuste de prêmio.
     Nada de valor recalculado na maquete.
  4. **Atalho para os dois simuladores** já com a unidade: Associativo (o deep link já
     existe) e Tabela Direta. Para o Tabela Direta, é preciso ensinar o simulador a ler
     `?emp=&unidade=` no mesmo formato e com o mesmo comportamento do Associativo
     (`aplicaParametrosUrl`: só preenche o estado, não muda nenhuma conta).
- **Torre 3 fora de venda:** ela não tem linhas na planilha. Aparece modelada, mas
  neutra e não clicável, com a etiqueta "Fora de venda" ou parecida. Não conta no
  % disponível/vendido. Se um dia aparecerem linhas `BL-03` na planilha, ela passa a
  funcionar como as outras sem mexer em código. A regra fica em config: torre sem
  nenhuma linha na planilha = fora de venda.
- **Atalhos para achar a unidade** (todos):
  - Busca por unidade ("T1 1204") → câmera voa até o apto e abre o painel.
  - Filtros: só disponíveis, por tipologia, faixa de andar; o que não passa no filtro
    fica esmaecido.
  - Anterior / próxima disponível dentro do painel.
  - Câmeras prontas: Vista geral, Torre 1, Torre 2, Torre 3, Frente, Fundos.
- **Carregamento:** até 10–15 s é aceitável, **com barra de progresso**.
- **Ferramenta:** o Claude instala Blender (Homebrew), o add-on blender-mcp e configura
  o MCP no Claude Code; o usuário só abre o Blender e clica em "Connect".

## Anti-metas (falhou mesmo se "funcionar")

- **Parecer jogo/amador** ou não ser reconhecível como o Village Gaia.
- **Status errado** — mostrar disponível algo vendido ou o contrário. Na dúvida (dado
  não carregou, unidade sem linha na planilha), a unidade **não** aparece como disponível.
- **Lento para abrir** além de ~15 s, ou sem feedback de progresso.
- **Corretor se perder** girando sem achar a unidade.
- **Vazar informação sensível**: folga de tabela, valor comercial mínimo, B.A. e regras
  de fluxo nunca aparecem na maquete (o cliente está olhando a tela).

## Não-metas

- Gerador automático de maquete para todos os empreendimentos (fica para depois).
- Modo "Obra"/andamento de obra, lazer modelado, interiores, tour 360°.
- Link público para o cliente navegar sozinho.
- Fluxo de pagamento completo no painel (fica no simulador).
- Celular como alvo de qualidade.

## Restrições do projeto (já existentes)

- Site **100% estático**: HTML + CSS + JS puro, sem build/bundler/framework, deploy
  manual na Vercel (ver `PRODUCT.md`, `WORKFLOW.md`). Three.js entra por CDN com versão
  fixa (ex.: módulo ES via `<script type="importmap">`), e o `.glb` fica em
  `assets/3d/village-gaia/`.
- Dados vêm em runtime do **Google Sheets CSV** pelo motor de `assets/data.js`
  (`fetchSheetCsv`, `parseCSV`, `findFirst`, `classifyTipo`, `blocoNum`, regra
  `tipoRule: 'village-gaia'`). **Atenção:** `rowsToUnits` hoje descarta tudo que não é
  `Disponivel`/`Mirror`; a maquete precisa de **todas** as unidades com seu status,
  então precisa de uma leitura que preserve o status (sem alterar o comportamento da
  aba Unidades).
- **Unidades vendidas não existem na planilha.** Situação conferida em 2026-11-02 na
  planilha ao vivo: o Gaia tem 193 linhas, todas `BL-01` ou `BL-02`, com andares de 0
  a 19 e status `Disponível` 167, `Reservada` 23, `Mirror` 2 e `Reservada aguardando
  revisão de proposta` 1. A fonte da verdade da maquete é então uma **grade fixa por
  torre**: 20 pavimentos (andar 0 = garden/térreo, 1–19 = tipo) × finais 01–08.
  - Posição da grade com linha na planilha → status dela. `Disponível`/`Mirror` →
    disponível; `Reservada*` → reservada; qualquer outro status → indisponível.
  - Posição sem linha, numa torre que está à venda → **vendida**.
  - "% vendido" = vendidas ÷ total da grade das torres à venda.
  - Se a planilha falhar ao carregar, **nenhuma** unidade aparece como disponível e a
    tela avisa o erro. Não existe "chute" de status.
  - Linhas de vaga de garagem ("vaga" em Tipo Planta) e `tabelaDireta <= 0` seguem as
    mesmas regras de exclusão de `rowsToUnits`.
- Os números de andares e finais devem ficar em config, não fixos no código. O builder
  confere esses números contra os renders.
- Identidade: **Grupo Direcional** (vermelho `#E4032B`, DM Sans), não o legado
  dourado/Playfair das páginas de empreendimento.
- Conteúdo por empreendimento vive em `assets/config.js` (Village Gaia: `torres: 3`,
  `solNascente: { default: [1, 2, 7, 8] }`, `tipos`, `plantas` com imagens,
  `entrega`). A configuração da maquete (caminho do `.glb`, câmeras, mapeamento) deve
  entrar ali também.
- Simulador Associativo já aceita deep link: `simulador-associativo.html?emp=gaia&unidade=BL01-1204`
  (formato `BL<n>-<andar><final>`). O Simulador de Tabela Direta hoje **não** lê
  parâmetros de URL.

## Material de referência do Village Gaia (no repo)

- `assets/img/village-gaia/galeria/01-fachada.jpg` (3 torres, entardecer, portaria),
  `02-torre.jpg` (torre de perto, fachada detalhada), `03-vista-aerea.jpg` (volumetria
  e entorno).
- `assets/img/village-gaia/plantas/implantacao.jpg` — posição das 3 torres (Torre 03,
  02, 01 da esquerda para a direita, lazer à direita, entrada no canto inferior
  direito), planta em "H" com finais 02/03 numa ponta, 04/05 nas laterais, 06/07 na
  outra ponta e 01/08 no miolo; rosa dos ventos no canto.
- Plantas por tipo: `planta-tipo-ponta`, `planta-tipo-meio`, `planta-office-tipo-meio`,
  `planta-garden-meio`, `planta-garden-ponta`.
- Book de mesa em PDF (link em `config.js`) pode ter plantas de pavimento mais
  precisas.
- Fachada: cinza grafite + cinza claro em faixas verticais, varandas com guarda-corpo
  branco nas pontas, prumada escura central de circulação, ~20 pavimentos (o número
  exato de andares deve vir do maior `andar` da planilha + térreo/garden, conferido
  contra o render).

## Comportamento esperado

1. Corretor abre `empreendimento.html?e=village-gaia` → toca **Maquete 3D** →
   `maquete.html?e=village-gaia` em tela cheia.
2. Tela de carregamento com barra de progresso (modelo + planilha em paralelo).
3. Abre na **vista geral** das 3 torres em modo **Noite**. Visíveis: nome do
   empreendimento, % disponível/vendido, alternância Noite/Cores, câmeras prontas,
   busca, filtros e legenda.
4. Orbit/zoom com mouse; limites para não entrar no chão nem se afastar demais.
5. **Hover** numa unidade: destaque da unidade + etiqueta curta (ex.:
   "T1 · 1204 · 2Q C/S Tipo Ponta · Disponível").
6. **Clique**: câmera aproxima, unidade destacada, painel lateral com os 4 blocos de
   informação; botões anterior/próxima disponível; botão do simulador; botão "vista
   desta unidade" (câmera posicionada na altura/fachada da unidade, olhando para fora).
7. Unidades vendidas e reservadas também são clicáveis, mas o painel mostra só a
   identificação, a planta e o status (sem valor e sem simulador). A Torre 3 (fora de
   venda) não é clicável.
8. "Voltar para o empreendimento" sempre visível.

## Decisões tomadas pelo Claude (para conferir)

- **Geometria:** dimensões e proporções são estimadas a partir dos renders e da
  implantação. O book de mesa em PDF (GitHub Releases) é a fonte complementar para as
  plantas de pavimento. Não existe modelo do arquiteto.
- **Posição das torres:** segue a implantação. Da esquerda para a direita ficam a
  Torre 03, a 02 e a 01, com o lazer à direita e a entrada no canto inferior direito.
  A orientação norte vem da rosa dos ventos da implantação. O `solNascente.default`
  (finais 1, 2, 7 e 8) vale para as 3 torres.
- **Andar 0 = garden/térreo** (mesma leitura do `classifyTipo`). O andar 1 é o 1º
  pavimento tipo.
- **Ordem do trabalho:** o app começa com um modelo provisório (caixas na grade
  certa) enquanto o modelo do Blender é feito em paralelo. Os dois se encontram pelo
  mesmo esquema de IDs de unidade.
- **Validação visual:** o usuário aprova o modelo por screenshots, em cerca de 2 a 3
  rodadas. O critério é reconhecer o Gaia ao lado do `01-fachada.jpg` e do
  `02-torre.jpg`.
- **Peso:** o `.glb` deve ficar em até ~15 MB, com compressão meshopt/Draco e
  decoders carregados de CDN com versão fixa. As janelas de unidade são geometria
  instanciada e não malha única, para o arquivo ficar leve.

## Deixado para o builder

- Técnica de modelagem e de mapeamento unidade↔geometria (malha por unidade, IDs no
  nome do objeto, ou uma grade de "janelas" alinhada à fachada), desde que cada
  unidade seja selecionável e reconhecível.
- Iluminação, materiais, céu, sombras e pós-processamento, dentro do limite de 15 s e
  rodando suave num notebook comum.
- Layout exato do painel, filtros e controles, seguindo `DESIGN.md` e a identidade
  Direcional.
- Cores do modo Cores.
- Como fica o fallback sem WebGL (mensagem + link para a aba Unidades basta).
- Estrutura de arquivos (`maquete.html`, `assets/maquete*.js`, `assets/maquete.css`).

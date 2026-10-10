# Site Produtos SPI

Portal do corretor para consulta de unidades, valores, plantas e disponibilidade
dos empreendimentos da SPI em **Campinas** e **Ribeirão Preto**.

O site é 100% estático (HTML + CSS + JS puro, sem build). Os dados de unidades são
lidos **ao vivo no navegador** a partir de uma planilha do Google Sheets publicada em CSV.

## Estrutura

```
index.html              Home: escolhe cidade -> escolhe empreendimento
empreendimento.html     Página de detalhe (?e=<id> na URL)
pendencias-vendas.html  Pendências de Vendas (interno, comercial, com senha)
visitas-recepcao.html   Lançamento de visitas no stand (recepção, pública)
visitas-recepcao-adm.html  Dashboard de visitas (interno, com senha)
assets/
  config.js             Cidades, empreendimentos e URLs das planilhas  <-- EDITAR AQUI
  data.js               Motor: busca CSV, filtra por empreendimento, renderiza unidades
  pendencias.js         Regras da página de pendências (puras, testadas)
  pendencias-app.js     Interface da página de pendências
  visitas.js            Regras das páginas de visitas (puras, testadas)
  visitas-api.js        Cliente do Web App de visitas + modo demonstração
  visitas-recepcao-app.js  Interface da recepção
  visitas-adm-app.js    Interface do dashboard de visitas
  styles.css            Estilos compartilhados
docs/
  apps-script-pendencias.gs   Web App da página de pendências
  apps-script-visitas.gs      Web App das páginas de visitas
  design/pendencias-vendas/   Telas aprovadas (PNG + prévias HTML)
tests/                  Testes das regras (node --test)
vercel.json             Configuração de deploy estático
```

## Como funciona a planilha

- Todos os empreendimentos ficam na **mesma aba**, identificados pela coluna
  **`Nome do Empreendimento`**.
- Cada empreendimento no `config.js` tem um campo `sheetName` que precisa bater
  (mesmo texto) com o valor dessa coluna na planilha.
- O parser encontra as colunas por aproximação de nome (produto, final, andar,
  bloco/etapa, tipo/planta, valor final, B.A., folga de tabela, valor de avaliação).

### Trocar/atualizar a planilha

Edite `window.SHEET_CSV_URL` em `assets/config.js`.

O ideal é usar o link **publicado**:
`Arquivo > Compartilhar > Publicar na web > CSV > Publicar`, algo como:
```
https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?output=csv
```
Se você usar o link `/export?format=csv` e ele falhar por CORS, o site tenta
automaticamente proxies públicos (corsproxy / allorigins).

## Adicionar imagens (plantas, implantação, galeria, vagas)

Em `assets/config.js`, dentro de cada empreendimento, preencha os campos que hoje
estão `null` / vazios. Você pode usar:
- URLs de imagens hospedadas, **ou**
- data URLs base64 (como no portal original).

Exemplo:
```js
plantas: [
  { img: 'URL_OU_BASE64', title: '2Q C/S - Meio · 48 m²', sub: 'Finais 01, 04, 05 e 08' }
],
galeria: { heroImg: 'URL', heroTitle: 'Fachada', heroSub: 'Render', items: [
  { img: 'URL', title: 'Piscina', sub: 'Lazer' }
]},
implantacao: { img: 'URL', legenda: ['Portaria','Piscina', ...] },
vagasImg: 'URL'
```
Enquanto os campos estiverem vazios, o site mostra um placeholder "Imagens em breve".

## Pendências de Vendas (`/pendencias-vendas`)

Página interna do comercial para cobrar pendências das vendas da aba
`RELATÓRIO` (planilha de vendas). A página conversa **só** com o Web App do
Apps Script da planilha (`docs/apps-script-pendencias.gs`, instruções de
implantação no cabeçalho). A senha fica no Apps Script, não no site.

- `window.PENDENCIAS_APPS_SCRIPT_URL` em `assets/config.js` = URL `/exec` do Web App.
- Vazio (ou `?demo=1` na URL) = **modo demonstração** com os dados fictícios de
  `tests/fixtures/vendas.json`. Nada é gravado.
- Regras de negócio em `assets/pendencias.js`. Testes:

```bash
node --test tests/*.test.js
```

Spec: `docs/superpowers/specs/2026-09-28-pendencias-vendas-design.md`.

## Visitas da recepção

- `/visitas-recepcao`: a recepcionista escolhe o stand e toca no tipo de visita
  (espontânea, agendada por corretor house ou trazida por imobiliária). Abre um popup
  com nome, CPF e telefone do cliente, data e horário, corretor (obrigatório), gerente
  de vendas (opcional) e, no tipo imobiliária, a imobiliária. Página pública, sem senha:
  ela nunca recebe CPF, telefone nem nome completo de volta do servidor.
- `/visitas-recepcao-adm`: dashboard do comercial, com senha forte (mínimo de 12
  caracteres, Script Property `VISITAS_SENHA` no Apps Script; a senha não fica no
  repositório). Mostra e exporta CPF e telefone: é dado pessoal (LGPD).
- Dados na aba `VISITAS` da planilha de visitas, via Web App
  (`docs/apps-script-visitas.gs`, instruções de implantação no cabeçalho).
- `window.VISITAS_APPS_SCRIPT_URL` em `assets/config.js` = URL `/exec` do Web App.
  Vazio (ou `?demo=1`) = **modo demonstração** com dados fictícios na memória da aba.
- Empreendimento novo no `config.js` também precisa entrar em
  `VISITAS_EMPREENDIMENTOS` no `.gs`. O teste de paridade avisa se esquecer.

Spec: `docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md`.

## Rodar localmente

Por causa de restrições de CORS ao carregar arquivos locais, use um servidor:
```bash
python3 -m http.server 8000
# abra http://localhost:8000
```

## Deploy no Vercel

1. Faça push deste repositório para o GitHub.
2. Em vercel.com > New Project > importe o repositório.
3. Framework Preset: **Other** (não precisa de build). Output = raiz.
4. Deploy. Pronto — cada push na branch principal republica o site.

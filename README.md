# Site Produtos SPI

Portal do corretor para consulta de unidades, valores, plantas e disponibilidade
dos empreendimentos da SPI em **Campinas** e **Ribeirão Preto**.

O site é 100% estático (HTML + CSS + JS puro, sem build). Os dados de unidades são
lidos **ao vivo no navegador** a partir de uma planilha do Google Sheets publicada em CSV.

## Estrutura

```
index.html              Home: escolhe cidade -> escolhe empreendimento
empreendimento.html     Página de detalhe (?e=<id> na URL)
assets/
  config.js             Cidades, empreendimentos e URL da planilha  <-- EDITAR AQUI
  data.js               Motor: busca CSV, filtra por empreendimento, renderiza unidades
  styles.css            Estilos compartilhados
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

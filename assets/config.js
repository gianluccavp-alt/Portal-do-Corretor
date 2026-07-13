/* ============================================================
   CONFIGURACAO CENTRAL - Site Produtos SPI
   ------------------------------------------------------------
   Para adicionar/editar empreendimentos, mexa somente aqui.
   ============================================================ */

/* URL da planilha publicada em CSV.
   Arquivo > Compartilhar > Publicar na web > CSV > Publicar.
   OBS: se voce usar o link /export?format=csv e ele falhar por CORS,
   o site tenta automaticamente proxies publicos (corsproxy / allorigins).
   O ideal e usar o link ".../pub?output=csv". */
window.SHEET_CSV_URL =
  'https://docs.google.com/spreadsheets/d/1hXgz1AbzYeaP2xLbM5Vj9wcM-0CWd98FG4PY5ZusJac/export?format=csv&gid=0';

/* Nome EXATO (ou aproximado) da coluna que identifica o empreendimento */
window.EMP_COLUMN = 'Nome do Empreendimento';

/* Empreendimentos.
   - id: slug usado na URL (empreendimento.html?e=<id>)
   - sheetName: valor que aparece na coluna "Nome do Empreendimento" na planilha.
     >>> AJUSTE se estiver escrito diferente na planilha. <<<
   - hero/pills/legenda/plantas/galeria: conteudo da pagina.
     imagens ficam null ate voce enviar; ai aparece placeholder. */
window.CITIES = [
  {
    id: 'campinas',
    name: 'Campinas',
    uf: 'SP',
    empreendimentos: [
      {
        id: 'alta-vista-mangara',
        sheetName: 'Alta Vista Mangará',
        nome: 'Alta Vista Mangará',
        cidade: 'Campinas, SP',
        eyebrow: 'Alta Vista Mangará · Campinas, SP',
        titleHtml: 'A <em>última oportunidade</em><br>de morar no Mangará',
        sub: 'Alta Vista Mangará é um empreendimento pensado para quem busca elevar o padrão de vida sem abrir mão da praticidade. Com renda familiar a partir de R$ 8 mil, oferece uma localização privilegiada, lazer completo com mais de 25 itens de comodidade e apartamentos modernos, proporcionando conforto, conveniência e um excelente potencial de valorização.',
        heroImg: 'assets/img/alta-vista/fachada.jpg',
        heroBlur: true,
        badges: ['2 min do Shopping Dom Pedro', '5 min da Lagoa do Taquaral'],
        pills: [
          { num: '300', lbl: 'Unidades<br>totais' },
          { num: '2', lbl: 'Torres<br>residenciais' },
          { num: '+25', lbl: 'Itens<br>de lazer' },
          { num: '18', lbl: 'Andares<br>por torre' }
        ],
        torres: 2,
        implantacao: { img: 'assets/img/alta-vista/plantas/implantacao.jpg', legenda: [] },
        plantas: [
          { tipo: '2q-meio', img: 'assets/img/alta-vista/plantas/planta-2q-meio.png', title: 'Planta-tipo Meio · 2 dormitórios', sub: 'Mangará Nativa · 48 m² · Finais 01, 04, 05 e 08' },
          { tipo: '2q-ponta', img: 'assets/img/alta-vista/plantas/planta-2q-ponta.png', title: 'Planta-tipo Ponta · 2 dormitórios', sub: 'Mangará Nativa · 46 m² · Finais 02, 03, 06 e 07' },
          { tipo: '1q', img: 'assets/img/alta-vista/plantas/planta-studio-1q.jpg', title: 'Studio · 1 dormitório', sub: 'Mangará Nativa · 48 m² · Torre 1 · 1º ao 9º andar' },
          { tipo: 'terreo-meio', img: 'assets/img/alta-vista/plantas/planta-garden-meio.png', title: 'Garden Meio · 2 dormitórios', sub: 'Mangará Jardim · 55 m² · Finais 04 e 05' },
          { tipo: 'terreo-ponta', img: 'assets/img/alta-vista/plantas/planta-garden-ponta.png', title: 'Garden Ponta · 2 dormitórios', sub: 'Mangará Jardim · 66 m² · Finais 02, 03, 06 e 07' }
        ],
        galeria: {
          heroImg: null, heroTitle: 'Fachada Principal', heroSub: 'Render arquitetônico',
          items: [
            { img: 'assets/img/alta-vista/fachada.jpg', title: 'Fachada', sub: 'Perspectiva das torres' },
            { img: 'assets/img/alta-vista/galeria/piscina.jpg', title: 'Piscina com Deck Molhado', sub: 'Área de lazer' },
            { img: 'assets/img/alta-vista/galeria/salao-festas.jpg', title: 'Salão de Festas', sub: 'Espaço para eventos' },
            { img: 'assets/img/alta-vista/galeria/churrasqueira.jpg', title: 'Churrasqueira', sub: 'Lazer' },
            { img: 'assets/img/alta-vista/galeria/academia.jpg', title: 'Academia', sub: 'Fitness equipado' },
            { img: 'assets/img/alta-vista/galeria/cowork.jpg', title: 'Coworking', sub: 'Espaço de trabalho' },
            { img: 'assets/img/alta-vista/galeria/brinquedoteca.jpg', title: 'Brinquedoteca', sub: 'Lazer infantil' },
            { img: 'assets/img/alta-vista/galeria/playground.jpg', title: 'Playground', sub: 'Lazer infantil' },
            { img: 'assets/img/alta-vista/galeria/wine-lounge.jpg', title: 'Wine Lounge', sub: 'Convívio' },
            { img: 'assets/img/alta-vista/galeria/mini-mercado.jpg', title: 'Mini Mercado', sub: 'Comodidade 24h' },
            { img: 'assets/img/alta-vista/galeria/pet-place.jpg', title: 'Pet Place', sub: 'Espaço para pets' },
            { img: 'assets/img/alta-vista/galeria/vaga-eletrica.jpg', title: 'Vaga com Carregador Elétrico', sub: 'Mobilidade sustentável' },
            { img: 'assets/img/alta-vista/galeria/espaco-pilates.jpg', title: 'Espaço Pilates', sub: 'Bem-estar' },
            { img: 'assets/img/alta-vista/galeria/bicicletario.jpg', title: 'Bicicletário', sub: 'Bike sharing' }
          ]
        },
        vagasImg: 'assets/img/alta-vista/mapa-vagas.jpg'
      },
      {
        id: 'cores-da-mata-mangara',
        sheetName: 'Cores da Mata Mangará',
        nome: 'Cores da Mata Mangará',
        cidade: 'Campinas, SP',
        eyebrow: 'Cores da Mata Mangará · Campinas, SP',
        titleHtml: 'Cores da Mata <em>Mangará</em>',
        sub: 'Segundo empreendimento do Complexo Mangará, ideal para quem busca qualidade de vida, conforto e excelente localização em Campinas. Com lazer completo e condições facilitadas de financiamento, oferece apartamentos para proporcionar bem-estar e praticidade, além de um grande potencial de valorização.',
        proximidades: [
          { icon: 'shopping', label: 'Shopping Dom Pedro' },
          { icon: 'lake', label: 'Lagoa do Taquaral' },
          { icon: 'road', label: 'Acesso à Rodovia' },
          { icon: 'school', label: 'Unicamp e Puccamp' },
          { icon: 'hospital', label: 'Hospital Madre Theodora' }
        ],
        heroImg: 'assets/img/cores-da-mata/f045-gua.jpg', badges: [], pills: [], torres: 2,
        hideVagas: true, heroBlur: true,
        implantacao: { img: 'assets/img/cores-da-mata/plantas/implantacao.jpg', legenda: [] },
        plantas: [
          { tipo: '2q-meio', img: 'assets/img/cores-da-mata/plantas/planta-2q-meio.jpg', title: 'Planta-tipo Meio · 2 dormitórios', sub: 'Mangará Nativa · 46,69 m² · Finais 01, 04, 05 e 08' },
          { tipo: '2q-ponta', img: 'assets/img/cores-da-mata/plantas/planta-2q-ponta.jpg', title: 'Planta-tipo Ponta · 2 dormitórios', sub: 'Mangará Nativa · 45,28 m² · Finais 02, 03, 06 e 07' },
          { tipo: 'terreo-meio', img: 'assets/img/cores-da-mata/plantas/planta-terreo-meio.jpg', title: 'Garden Meio · 2 dormitórios', sub: 'Mangará Jardim · 46,69 m² + garden · Finais 04 e 05' },
          { tipo: 'terreo-ponta', img: 'assets/img/cores-da-mata/plantas/planta-terreo-ponta.jpg', title: 'Garden Ponta · 2 dormitórios', sub: 'Mangará Jardim · 45,28 m² + garden · Finais 03 e 06' }
        ],
        galeria: {
          heroImg: null, heroTitle: '', heroSub: '',
          items: [
            { img: 'assets/img/cores-da-mata/f026-pdo.jpg', title: 'Fachada', sub: 'Perspectiva da torre' },
            { img: 'assets/img/cores-da-mata/f045-gua.jpg', title: 'Portaria', sub: 'Acesso principal' },
            { img: 'assets/img/cores-da-mata/f030-ger.jpg', title: 'Vista Aérea do Lazer', sub: 'Área de lazer completa' },
            { img: 'assets/img/cores-da-mata/f022-pis.jpg', title: 'Piscina', sub: 'Solário e deck' },
            { img: 'assets/img/cores-da-mata/f046-fes.jpg', title: 'Salão de Festas', sub: 'Espaço para eventos' },
            { img: 'assets/img/cores-da-mata/f042-gou.jpg', title: 'Lounge Gourmet', sub: 'Convívio noturno' },
            { img: 'assets/img/cores-da-mata/f032-fit.jpg', title: 'Academia', sub: 'Fitness equipado' },
            { img: 'assets/img/cores-da-mata/f016-fit.jpg', title: 'Fitness ao Ar Livre', sub: 'Treino funcional' },
            { img: 'assets/img/cores-da-mata/f035-cow.jpg', title: 'Coworking', sub: 'Espaço de trabalho' },
            { img: 'assets/img/cores-da-mata/f039-lav.jpg', title: 'Lavanderia', sub: 'Lavanderia coletiva' }
          ]
        }, vagasImg: null
      },
      {
        id: 'seleto-amoreiras',
        sheetName: 'Seleto Amoreiras',
        nome: 'Seleto Amoreiras',
        cidade: 'Campinas, SP',
        eyebrow: 'Seleto Amoreiras · Campinas, SP',
        titleHtml: 'Seleto <em>Amoreiras</em>',
        sub: 'Na região das Amoreiras, em Campinas, mais um sucesso de Vendas Prix e Direcional. Apartamentos de 2 dormitórios com varanda, grill, lazer completo e vaga de garagem. Um condomínio moderno, seguro e cheio de diversão para toda a família, em uma região que está em constante crescimento.',
        heroImg: 'assets/img/seleto-amoreiras/galeria/08-portaria.jpg', badges: [], pills: [], torres: 3,
        hideVagas: true, heroBlur: true, theme: 'seleto',
        tipoRule: 'seleto',
        solNascente: { default: [2, 4, 6, 8], 3: [1, 3, 5, 7] },
        tipos: [
          { key: '2q-ponta',     label: '2Q Tipo - Ponta' },
          { key: '2q-meio',      label: '2Q Tipo - Meio' },
          { key: 'terreo-ponta', label: '2Q Garden - Ponta' },
          { key: 'terreo-meio',  label: '2Q Garden - Meio' }
        ],
        implantacao: { img: 'assets/img/seleto-amoreiras/plantas/implantacao.jpg', legenda: [] },
        plantas: [
          { tipo: '2q-ponta',     img: 'assets/img/seleto-amoreiras/plantas/planta-2q-ponta.jpg',     title: '2Q Tipo - Ponta',   sub: 'Torres 1, 2 e 3 · Finais 1, 2, 7 e 8' },
          { tipo: '2q-meio',      img: 'assets/img/seleto-amoreiras/plantas/planta-2q-meio.jpg',      title: '2Q Tipo - Meio',    sub: 'Torres 1, 2 e 3 · Finais 3, 4, 5 e 6' },
          { tipo: 'terreo-ponta', img: 'assets/img/seleto-amoreiras/plantas/planta-garden-ponta.jpg', title: '2Q Garden - Ponta', sub: 'Térreo · Finais 1, 2, 7 e 8' },
          { tipo: 'terreo-meio',  img: 'assets/img/seleto-amoreiras/plantas/planta-garden-meio.jpg',  title: '2Q Garden - Meio',  sub: 'Térreo · Finais 3, 4, 5 e 6' }
        ],
        galeria: {
          heroImg: null, heroTitle: '', heroSub: '',
          items: [
            { img: 'assets/img/seleto-amoreiras/galeria/01-piscina.jpg',        title: 'Piscina',          sub: 'Área de lazer' },
            { img: 'assets/img/seleto-amoreiras/galeria/02-quadra.jpg',         title: 'Quadra',           sub: 'Esporte' },
            { img: 'assets/img/seleto-amoreiras/galeria/03-salao-festas.jpg',   title: 'Salão de Festas',  sub: 'Espaço para eventos' },
            { img: 'assets/img/seleto-amoreiras/galeria/04-espaco-gourmet.jpg', title: 'Espaço Gourmet',   sub: 'Convívio' },
            { img: 'assets/img/seleto-amoreiras/galeria/05-praca-multiuso.jpg', title: 'Praça Multiuso',   sub: 'Área comum' },
            { img: 'assets/img/seleto-amoreiras/galeria/06-praca-multiuso-2.jpg', title: 'Praça Multiuso', sub: 'Área comum' },
            { img: 'assets/img/seleto-amoreiras/galeria/07-car-wash.jpg',       title: 'Car Wash',         sub: 'Comodidade' },
            { img: 'assets/img/seleto-amoreiras/galeria/08-portaria.jpg',       title: 'Portaria',         sub: 'Acesso principal' },
            { img: 'assets/img/seleto-amoreiras/galeria/09-fachada.jpg',        title: 'Fachada',          sub: 'Perspectiva do empreendimento' },
            { img: 'assets/img/seleto-amoreiras/galeria/10-fitness.jpg',        title: 'Fitness',          sub: 'Academia' },
            { img: 'assets/img/seleto-amoreiras/galeria/11-pet-place.jpg',      title: 'Pet Place',        sub: 'Espaço para pets' },
            { img: 'assets/img/seleto-amoreiras/galeria/12-playground.jpg',     title: 'Playground',       sub: 'Lazer infantil' },
            { img: 'assets/img/seleto-amoreiras/galeria/13-bicicletario.jpg',   title: 'Bicicletário',     sub: 'Bike sharing' },
            { img: 'assets/img/seleto-amoreiras/galeria/14-bricolagem.jpg',     title: 'Bricolagem',       sub: 'Espaço maker' },
            { img: 'assets/img/seleto-amoreiras/galeria/15-insercao.jpg',       title: 'Inserção',         sub: 'Implantação no entorno' }
          ]
        }, vagasImg: null
      },
      {
        id: 'casa-prado-residencial-riva',
        sheetName: 'Casa Prado Residencial Riva',
        nome: 'Casa Prado Residencial Riva',
        cidade: 'Campinas, SP',
        eyebrow: 'Casa Prado Residencial Riva · Campinas, SP',
        titleHtml: 'Casa Prado <em>Residencial Riva</em>',
        sub: 'Empreendimento Casa Prado em Campinas.',
        heroImg: null, badges: [], pills: [], torres: 1,
        tipoRule: 'casa-prado',
        solNascente: { default: [1, 2, 6] },
        tipos: [
          { key: 'garden-ponta', label: '3Q C/S Garden - Ponta' },
          { key: 'tipo-meio',    label: '2Q C/S Tipo - Meio' },
          { key: 'tipo-ponta',   label: '3Q C/S Tipo - Ponta' },
          { key: 'cobertura',    label: '3Q C/S Cobertura' }
        ],
        implantacao: { img: null, legenda: [] }, plantas: [],
        galeria: { heroImg: null, heroTitle: '', heroSub: '', items: [] },
        vagasImgs: [
          'assets/img/casa-prado/vagas/mapa-vagas-1.jpg',
          'assets/img/casa-prado/vagas/mapa-vagas-2.jpg',
          'assets/img/casa-prado/vagas/mapa-vagas-3.jpg'
        ], vagasImg: null
      }
    ]
  },
  {
    id: 'ribeirao-preto',
    name: 'Ribeirão Preto',
    uf: 'SP',
    empreendimentos: [
      {
        id: 'direcional-conquista-clube-ipiranga',
        sheetName: 'Direcional Conquista Clube Ipiranga',
        nome: 'Direcional Conquista Clube Ipiranga',
        cidade: 'Ribeirão Preto, SP',
        eyebrow: 'Direcional Conquista Clube Ipiranga · Ribeirão Preto, SP',
        titleHtml: 'Direcional Conquista <em>Clube Ipiranga</em>',
        sub: 'Empreendimento no bairro Ipiranga em Ribeirão Preto.',
        heroImg: null, badges: [], pills: [], torres: 2,
        implantacao: { img: null, legenda: [] }, plantas: [],
        galeria: { heroImg: null, heroTitle: '', heroSub: '', items: [] }, vagasImg: null
      },
      {
        id: 'reserva-direcional-jardim-botanico',
        sheetName: 'Reserva Direcional Jardim Botânico',
        nome: 'Reserva Direcional Jardim Botânico',
        cidade: 'Ribeirão Preto, SP',
        eyebrow: 'Reserva Direcional Jardim Botânico · Ribeirão Preto, SP',
        titleHtml: 'Reserva Direcional <em>Jardim Botânico</em>',
        sub: 'Empreendimento no Jardim Botânico em Ribeirão Preto.',
        heroImg: null, badges: [], pills: [], torres: 2,
        implantacao: { img: null, legenda: [] }, plantas: [],
        galeria: { heroImg: null, heroTitle: '', heroSub: '', items: [] }, vagasImg: null
      },
      {
        id: 'village-gaia',
        sheetName: 'Village Gaia',
        nome: 'Village Gaia',
        cidade: 'Ribeirão Preto, SP',
        eyebrow: 'Village Gaia · Ribeirão Preto, SP',
        titleHtml: 'Village <em>Gaia</em>',
        sub: 'Empreendimento Village Gaia em Ribeirão Preto.',
        heroImg: null, badges: [], pills: [], torres: 2,
        implantacao: { img: null, legenda: [] }, plantas: [],
        galeria: { heroImg: null, heroTitle: '', heroSub: '', items: [] }, vagasImg: null
      },
      {
        id: 'village-park',
        sheetName: 'Village Park',
        nome: 'Village Park',
        cidade: 'Ribeirão Preto, SP',
        eyebrow: 'Village Park · Ribeirão Preto, SP',
        titleHtml: 'Village <em>Park</em>',
        sub: 'Empreendimento Village Park em Ribeirão Preto.',
        heroImg: null, badges: [], pills: [], torres: 2,
        implantacao: { img: null, legenda: [] }, plantas: [],
        galeria: { heroImg: null, heroTitle: '', heroSub: '', items: [] }, vagasImg: null
      }
    ]
  }
];

/* helpers de lookup */
window.findEmpreendimento = function (empId) {
  for (var c = 0; c < window.CITIES.length; c++) {
    var list = window.CITIES[c].empreendimentos;
    for (var e = 0; e < list.length; e++) {
      if (list[e].id === empId) {
        var obj = list[e];
        obj._city = window.CITIES[c].name;
        obj._uf = window.CITIES[c].uf;
        return obj;
      }
    }
  }
  return null;
};

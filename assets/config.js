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
        id: 'casa-prado-residencial-riva',
        sheetName: 'Casa Prado Residencial Riva',
        nome: 'Casa Prado Residencial Riva',
        cidade: 'Campinas, SP',
        eyebrow: 'Casa Prado Residencial Riva · Campinas, SP',
        titleHtml: 'Casa Prado <em>Residencial Riva</em>',
        sub: 'Mais do que um novo endereço, o Casa Prado nasce como um projeto que traduz o verdadeiro significado de morar em Campinas, SP com qualidade. Localizado em um dos bairros mais valorizados da cidade, o empreendimento reúne natureza, tradição e conveniência em um mesmo cenário. Com apartamentos amplos, conforto elevado e design atemporal, o Casa Prado entrega uma experiência marcada por sofisticação, privacidade e bem-estar no lugar e no momento certo.',
        heroImg: 'assets/img/casa-prado/portaria.jpg', badges: [], pills: [], torres: 1,
        heroBlur: true, theme: 'casa-prado',
        tipoRule: 'casa-prado',
        solNascente: { default: [1, 2, 6] },
        tipos: [
          { key: 'garden-ponta', label: '3Q C/S Garden - Ponta' },
          { key: 'tipo-meio',    label: '2Q C/S Tipo - Meio' },
          { key: 'tipo-ponta',   label: '3Q C/S Tipo - Ponta' },
          { key: 'cobertura',    label: '3Q C/S Cobertura' }
        ],
        implantacao: { img: 'assets/img/casa-prado/plantas/implantacao.jpg', legenda: [] },
        plantas: [
          { tipo: 'garden-ponta', img: 'assets/img/casa-prado/plantas/planta-garden-ponta.jpg', title: '3Q C/S Garden - Ponta', sub: '3 dorms · 123,52 a 123,77 m² · Térreo' },
          { tipo: 'tipo-meio',    img: 'assets/img/casa-prado/plantas/planta-tipo-meio.jpg',    title: '2Q C/S Tipo - Meio',   sub: '2 dorms · 69,23 m² · Finais 1 e 4 · Andar 1 a 16' },
          { tipo: 'tipo-ponta',   img: 'assets/img/casa-prado/plantas/planta-tipo-ponta.jpg',   title: '3Q C/S Tipo - Ponta',  sub: '3 dorms · 95,99 a 96,04 m² · Finais 2, 3, 5 e 6 · Andar 1 a 16' },
          { tipo: 'cobertura',    img: 'assets/img/casa-prado/plantas/planta-cobertura.jpg',    title: '3Q C/S Cobertura',     sub: '3 dorms · 127,62 a 132,86 m² · Cobertura' }
        ],
        galeria: {
          heroImg: null, heroTitle: '', heroSub: '',
          items: [
            { img: 'assets/img/casa-prado/galeria/01-foto-empreendimento.jpg', title: 'Empreendimento',        sub: 'Perspectiva geral' },
            { img: 'assets/img/casa-prado/galeria/02-piscina.jpg',             title: 'Piscina',               sub: 'Área de lazer' },
            { img: 'assets/img/casa-prado/galeria/03-piscina-2.jpg',           title: 'Piscina',               sub: 'Área de lazer' },
            { img: 'assets/img/casa-prado/galeria/04-academia.jpg',            title: 'Academia',              sub: 'Bem-estar' },
            { img: 'assets/img/casa-prado/galeria/05-espaco-yoga.jpg',         title: 'Espaço Yoga',           sub: 'Bem-estar' },
            { img: 'assets/img/casa-prado/galeria/06-mini-quadra-areia.jpg',   title: 'Mini Quadra de Areia',  sub: 'Esporte' },
            { img: 'assets/img/casa-prado/galeria/07-guarita.jpg',             title: 'Guarita',               sub: 'Acesso e segurança' },
            { img: 'assets/img/casa-prado/galeria/08-hall.jpg',                title: 'Hall',                  sub: 'Ambientes comuns' },
            { img: 'assets/img/casa-prado/galeria/09-praca-chegada.jpg',       title: 'Praça de Chegada',      sub: 'Ambientes comuns' },
            { img: 'assets/img/casa-prado/galeria/10-salao-festas.jpg',        title: 'Salão de Festas',       sub: 'Convívio' },
            { img: 'assets/img/casa-prado/galeria/11-espaco-gourmet.jpg',      title: 'Espaço Gourmet',        sub: 'Convívio' },
            { img: 'assets/img/casa-prado/galeria/12-sala-estudos.jpg',        title: 'Sala de Estudos',       sub: 'Trabalho e estudo' },
            { img: 'assets/img/casa-prado/galeria/13-coworking.jpg',           title: 'Coworking',             sub: 'Trabalho e estudo' },
            { img: 'assets/img/casa-prado/galeria/14-espaco-influencer.jpg',   title: 'Espaço Influencer',     sub: 'Diferenciais' },
            { img: 'assets/img/casa-prado/galeria/15-mini-mercado.jpg',        title: 'Mini Mercado',          sub: 'Comodidade' },
            { img: 'assets/img/casa-prado/galeria/16-espaco-delivery.jpg',     title: 'Espaço Delivery',       sub: 'Comodidade' },
            { img: 'assets/img/casa-prado/galeria/17-fachada.jpg',             title: 'Fachada',               sub: 'Perspectiva do empreendimento' },
            { img: 'assets/img/casa-prado/galeria/18-vaga-eletrica.jpg',       title: 'Vaga Elétrica',         sub: 'Garagem' },
            { img: 'assets/img/casa-prado/galeria/19-vaga-deposito.jpg',       title: 'Vaga com Depósito',     sub: 'Garagem' },
            { img: 'assets/img/casa-prado/galeria/20-pub-cinema.jpg',          title: 'Pub e Cinema',          sub: 'Lazer' },
            { img: 'assets/img/casa-prado/galeria/21-sala-jogos.jpg',          title: 'Sala de Jogos',         sub: 'Lazer' },
            { img: 'assets/img/casa-prado/galeria/22-pet-place.jpg',           title: 'Pet Place',             sub: 'Espaço para pets' },
            { img: 'assets/img/casa-prado/galeria/23-playground.jpg',          title: 'Playground',            sub: 'Lazer infantil' }
          ]
        },
        vagasImgs: [
          'assets/img/casa-prado/vagas/mapa-vagas-1.jpg',
          'assets/img/casa-prado/vagas/mapa-vagas-2.jpg',
          'assets/img/casa-prado/vagas/mapa-vagas-3.jpg'
        ], vagasImg: null
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
        id: 'universo-parque-alphaville',
        sheetName: 'Universo - Parque Alphaville',
        nome: 'Universo - Parque Alphaville',
        cidade: 'Campinas, SP',
        eyebrow: 'Universo - Parque Alphaville · Campinas, SP',
        titleHtml: 'Universo - <em>Parque Alphaville</em>',
        sub: 'Em Breve',
        comingSoon: true,
        heroImg: null, badges: [], pills: [], torres: 1,
        implantacao: { img: null, legenda: [] }, plantas: [],
        galeria: { heroImg: null, heroTitle: '', heroSub: '', items: [] }, vagasImg: null
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
        cardNome: 'Conquista Clube Ipiranga',
        cidade: 'Ribeirão Preto, SP',
        eyebrow: 'Direcional Conquista Clube Ipiranga · Ribeirão Preto, SP',
        titleHtml: 'Direcional Conquista <em>Clube Ipiranga</em>',
        sub: 'O Conquista Clube Ipiranga reúne tudo o que você precisa para viver com mais conforto e praticidade. Com apartamentos de 2 dormitórios, elevador, lazer completo e uma localização estratégica no coração do Ipiranga, oferece fácil acesso às principais vias, comércios e serviços da cidade. Um empreendimento pensado para quem deseja conquistar o primeiro imóvel com qualidade de vida e excelente potencial de valorização.',
        heroImg: 'assets/img/ipiranga/galeria/01-guarita.jpg',
        heroBlur: true, theme: 'ipiranga',
        badges: [], pills: [], torres: 4,
        hideVagas: true, hideSol: true,
        tipoRule: 'ipiranga',
        tipos: [
          { key: 'tipo-meio',            label: '2Q Tipo - Meio' },
          { key: 'tipo-ponta',           label: '2Q Tipo - Ponta' },
          { key: 'garden-ponta',         label: '2Q Garden - Ponta' },
          { key: 'garden-meio',          label: '2Q Garden - Meio' },
          { key: 'garden-meio-adaptado', label: '2Q Garden - Meio Adaptado' }
        ],
        implantacao: { img: 'assets/img/ipiranga/plantas/implantacao.jpg', legenda: [] },
        plantas: [
          { tipo: 'tipo-meio',            img: 'assets/img/ipiranga/plantas/planta-tipo-meio.jpg',            title: '2Q Tipo - Meio',            sub: 'Finais 1, 2, 5, 6, 7, 8, 11 e 12 · Andar 1+' },
          { tipo: 'tipo-ponta',           img: 'assets/img/ipiranga/plantas/planta-tipo-ponta.jpg',           title: '2Q Tipo - Ponta',           sub: 'Finais 3, 4, 9 e 10 · Andar 1+' },
          { tipo: 'garden-ponta',         img: 'assets/img/ipiranga/plantas/planta-garden-ponta.jpg',         title: '2Q Garden - Ponta',         sub: 'Finais 3, 4, 9 e 10 · Térreo' },
          { tipo: 'garden-meio',          img: 'assets/img/ipiranga/plantas/planta-garden-meio.jpg',          title: '2Q Garden - Meio',          sub: 'Térreo · Finais de meio' },
          { tipo: 'garden-meio-adaptado', img: 'assets/img/ipiranga/plantas/planta-garden-meio-adaptado.jpg', title: '2Q Garden - Meio Adaptado', sub: 'Térreo · Unidade adaptada (PcD)' }
        ],
        galeria: {
          heroImg: null, heroTitle: '', heroSub: '',
          items: [
            { img: 'assets/img/ipiranga/galeria/01-guarita.jpg',           title: 'Guarita',           sub: 'Acesso e segurança' },
            { img: 'assets/img/ipiranga/galeria/02-piscina.jpg',           title: 'Piscina',           sub: 'Área de lazer' },
            { img: 'assets/img/ipiranga/galeria/03-fitness.jpg',           title: 'Fitness',           sub: 'Bem-estar' },
            { img: 'assets/img/ipiranga/galeria/04-playground.jpg',        title: 'Playground',        sub: 'Lazer infantil' },
            { img: 'assets/img/ipiranga/galeria/05-brinquedoteca.jpg',     title: 'Brinquedoteca',     sub: 'Lazer infantil' },
            { img: 'assets/img/ipiranga/galeria/06-area-gourmet.jpg',      title: 'Área Gourmet',      sub: 'Convívio' },
            { img: 'assets/img/ipiranga/galeria/07-espaco-happy-hour.jpg', title: 'Espaço Happy Hour', sub: 'Convívio' },
            { img: 'assets/img/ipiranga/galeria/08-mini-mercado.jpg',      title: 'Mini Mercado',      sub: 'Comodidade' },
            { img: 'assets/img/ipiranga/galeria/09-coworking.jpg',         title: 'Coworking',         sub: 'Trabalho e estudo' },
            { img: 'assets/img/ipiranga/galeria/10-pet-place.jpg',         title: 'Pet Place',         sub: 'Espaço para pets' },
            { img: 'assets/img/ipiranga/galeria/11-bicicletario.jpg',      title: 'Bicicletário',      sub: 'Mobilidade' },
            { img: 'assets/img/ipiranga/galeria/12-vista-aerea.jpg',       title: 'Vista Aérea',       sub: 'Perspectiva do empreendimento' }
          ]
        }, vagasImg: null
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
        sub: 'O Guaporé ganha ainda mais destaque com o Village Park no Complexo Residencial Veredas de Ribeirão. Apartamentos de 2 e 3 dormitórios, com suíte, varanda gourmet, lazer completo e 1 ou 2 vagas de garagem. Um condomínio clube moderno, repleto de lazer e comodidade, em uma região em constante crescimento, ideal para quem busca qualidade de vida e valorização.',
        heroImg: 'assets/img/village-park/galeria/01-fachada.jpg',
        heroBlur: true, theme: 'village-park',
        badges: [], pills: [], torres: 3,
        hideVagas: true,
        tipoRule: 'village-park',
        solNascente: { 1: [2, 7, 8], 2: [3, 4, 5, 6], 3: [2, 7, 8] },
        tipos: [
          { key: 'tipo-ponta',         label: '3Q C/S Tipo - Ponta' },
          { key: 'tipo-ponta-pcd',     label: '2Q C/S Tipo - Ponta PCD' },
          { key: 'tipo-meio',          label: '2Q C/S Tipo - Meio' },
          { key: 'office-tipo-meio',   label: '2Q C/S Office Tipo - Meio' },
          { key: 'office-garden-meio', label: '1Q Office Garden - Meio' },
          { key: 'garden-meio',        label: '2Q C/S Garden - Meio' },
          { key: 'garden-ponta',       label: '3Q C/S Garden - Ponta' }
        ],
        implantacao: { img: 'assets/img/village-park/plantas/implantacao.jpg', legenda: [] },
        plantas: [
          { tipo: 'tipo-ponta',         img: 'assets/img/village-park/plantas/planta-tipo-ponta.jpg',         title: '3Q C/S Tipo - Ponta',        sub: 'Finais 2, 3, 6 e 7 · Andar 1+' },
          { tipo: 'tipo-ponta-pcd',     img: 'assets/img/village-park/plantas/planta-tipo-ponta-pcd.jpg',     title: '2Q C/S Tipo - Ponta PCD',    sub: 'Final 7 · Unidade adaptada (PcD)' },
          { tipo: 'tipo-meio',          img: 'assets/img/village-park/plantas/planta-tipo-meio.jpg',          title: '2Q C/S Tipo - Meio',         sub: 'Finais 1, 4 e 5 · Andar 1+' },
          { tipo: 'office-tipo-meio',   img: 'assets/img/village-park/plantas/planta-office-tipo-meio.jpg',   title: '2Q C/S Office Tipo - Meio',  sub: 'Final 8 · Andar 1+' },
          { tipo: 'office-garden-meio', img: 'assets/img/village-park/plantas/planta-office-garden-meio.jpg', title: '1Q Office Garden - Meio',    sub: 'Final 8 · Térreo' },
          { tipo: 'garden-meio',        img: 'assets/img/village-park/plantas/planta-garden-meio.jpg',        title: '2Q C/S Garden - Meio',       sub: 'Finais 4 e 5 · Térreo' },
          { tipo: 'garden-ponta',       img: 'assets/img/village-park/plantas/planta-garden-ponta.jpg',       title: '3Q C/S Garden - Ponta',      sub: 'Finais 2, 3 e 6 · Térreo' }
        ],
        galeria: {
          heroImg: null, heroTitle: '', heroSub: '',
          items: [
            { img: 'assets/img/village-park/galeria/01-fachada.jpg',        title: 'Fachada',          sub: 'Perspectiva do empreendimento' },
            { img: 'assets/img/village-park/galeria/02-vista-aerea.jpg',    title: 'Vista Aérea',      sub: 'Implantação geral' },
            { img: 'assets/img/village-park/galeria/03-portaria.jpg',       title: 'Portaria',         sub: 'Acesso e segurança' },
            { img: 'assets/img/village-park/galeria/04-praca.jpg',          title: 'Praça',            sub: 'Área comum' },
            { img: 'assets/img/village-park/galeria/05-piscina.jpg',        title: 'Piscina',          sub: 'Área de lazer' },
            { img: 'assets/img/village-park/galeria/06-beauty.jpg',         title: 'Espaço Beauty',    sub: 'Bem-estar' },
            { img: 'assets/img/village-park/galeria/07-bikeshare.jpg',      title: 'Bike Share',       sub: 'Mobilidade' },
            { img: 'assets/img/village-park/galeria/08-carshare.jpg',       title: 'Car Share',        sub: 'Mobilidade' },
            { img: 'assets/img/village-park/galeria/09-churrasqueira.jpg',  title: 'Churrasqueira',    sub: 'Convívio' },
            { img: 'assets/img/village-park/galeria/10-cowork.jpg',         title: 'Coworking',        sub: 'Trabalho e estudo' },
            { img: 'assets/img/village-park/galeria/11-crossfit.jpg',       title: 'Crossfit',         sub: 'Bem-estar' },
            { img: 'assets/img/village-park/galeria/12-delivery.jpg',       title: 'Espaço Delivery',  sub: 'Comodidade' },
            { img: 'assets/img/village-park/galeria/13-salao-festas.jpg',   title: 'Salão de Festas',  sub: 'Convívio' },
            { img: 'assets/img/village-park/galeria/14-academia.jpg',       title: 'Academia',         sub: 'Bem-estar' },
            { img: 'assets/img/village-park/galeria/15-village-club-1.jpg', title: 'Village Club',     sub: 'Clube' },
            { img: 'assets/img/village-park/galeria/16-village-club-2.jpg', title: 'Village Club',     sub: 'Clube' },
            { img: 'assets/img/village-park/galeria/17-village-club-3.jpg', title: 'Village Club',     sub: 'Clube' },
            { img: 'assets/img/village-park/galeria/18-pub-jogos.jpg',      title: 'Pub e Jogos',      sub: 'Lazer' },
            { img: 'assets/img/village-park/galeria/19-brinquedoteca.jpg',  title: 'Brinquedoteca',    sub: 'Lazer infantil' },
            { img: 'assets/img/village-park/galeria/20-lounge-festas.jpg',  title: 'Lounge de Festas', sub: 'Convívio' },
            { img: 'assets/img/village-park/galeria/21-minimarket.jpg',     title: 'Minimarket',       sub: 'Comodidade' },
            { img: 'assets/img/village-park/galeria/22-petplace.jpg',       title: 'Pet Place',        sub: 'Espaço para pets' },
            { img: 'assets/img/village-park/galeria/23-piquenique.jpg',     title: 'Área de Piquenique', sub: 'Convívio' },
            { img: 'assets/img/village-park/galeria/24-playground.jpg',     title: 'Playground',       sub: 'Lazer infantil' },
            { img: 'assets/img/village-park/galeria/25-beach-tennis.jpg',   title: 'Beach Tennis',     sub: 'Esporte' },
            { img: 'assets/img/village-park/galeria/26-quadra.jpg',         title: 'Quadra',           sub: 'Esporte' }
          ]
        }, vagasImg: null
      }
    ]
  },
  {
    id: 'sorocaba',
    name: 'Sorocaba',
    uf: 'SP',
    empreendimentos: [
      {
        id: 'conquista-vila-da-mata',
        sheetName: 'Conquista Vila da Mata',
        nome: 'Conquista Vila da Mata',
        cidade: 'Sorocaba, SP',
        eyebrow: 'Conquista Vila da Mata · Sorocaba, SP',
        titleHtml: 'Conquista <em>Vila da Mata</em>',
        sub: 'Empreendimento Conquista Vila da Mata em Sorocaba.',
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

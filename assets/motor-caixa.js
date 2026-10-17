/* ============================================================
   MOTOR CAIXA - financiamento MCMV / Classe Media
   ------------------------------------------------------------
   Funcoes puras (sem DOM, sem rede). Reproduz o Simulador
   Habitacional CAIXA (calibrado em 15/10/2026 com 138 respostas
   reais - tests/motor-caixa.test.js).
   Regras e fontes: docs/matriz-caixa/regras-motor-caixa.md
   Usado por /match-unidades via window.MotorCaixa.
   ============================================================ */
(function (raiz) {
  'use strict';

  var CIDADES = {
    '3543402': { nome: 'Ribeirão Preto', uf: 'SP', tetoF12: 264000, fpop: 1.10 },
    '3552205': { nome: 'Sorocaba', uf: 'SP', tetoF12: 264000, fpop: 1.10 },
    '3509502': { nome: 'Campinas', uf: 'SP', tetoF12: 270000, fpop: 1.20 }
  };
  var FDR_UF = { SP: 2.07 };
  /* nome da cidade no catalogo (window.SIM_EMPS) -> codigo IBGE */
  var MUNICIPIO_POR_CIDADE = { 'Ribeirão Preto': '3543402', 'Campinas': '3509502', 'Sorocaba': '3552205' };

  /* MIP % a.m. por faixa de idade (limite superior da faixa). 14 e 15 usam a mesma tabela. */
  var MIP = {
    caixa: [[25, 0.00820], [30, 0.00850], [35, 0.01080], [40, 0.01440], [45, 0.02440], [50, 0.03590],
            [55, 0.06450], [60, 0.07640], [65, 0.12960], [70, 0.20050], [75, 0.37290], [80, 0.45660]],
    tokio: [[25, 0.01037], [30, 0.01039], [35, 0.01206], [40, 0.01695], [45, 0.02589], [50, 0.03651],
            [55, 0.06624], [60, 0.07745], [65, 0.13721], [70, 0.21778], [75, 0.39351], [80, 0.55777]],
    /* SBPE (coleta de 17/10/2026): tabelas proprias; 14 e 16 usam a mesma */
    sbpeCaixa: [[25, 0.00930], [30, 0.00960], [35, 0.01160], [40, 0.01540], [45, 0.02520], [50, 0.03860],
                [55, 0.06760], [60, 0.15330], [65, 0.27310], [70, 0.32590], [75, 0.48940], [80, 0.53120]],
    sbpeTokio: [[25, 0.00884], [30, 0.00927], [35, 0.01172], [40, 0.01590], [45, 0.02399], [50, 0.03687],
                [55, 0.06930], [60, 0.15390], [65, 0.27750], [70, 0.33203], [75, 0.49650], [80, 0.54147]]
  };
  var SEGURADORAS = [
    { codigo: '14', nome: 'CAIXA RESIDENCIAL HABITACIONAL', mip: 'caixa', dfi: 0.0071 },
    { codigo: '15', nome: 'CAIXA RESIDENCIAL HABITACIONAL MAIS', mip: 'caixa', dfi: 0.0135 },
    { codigo: '4', nome: 'TOKIO MARINE', mip: 'tokio', dfi: 0.00889 }
  ];
  var SEGURADORAS_SBPE = [
    { codigo: '14', nome: 'CAIXA RESIDENCIAL HABITACIONAL', mip: 'sbpeCaixa', dfi: 0.0066 },
    { codigo: '16', nome: 'CAIXA RESIDENCIAL HABITACIONAL ESPECIAL', mip: 'sbpeCaixa', dfi: 0.0130 },
    { codigo: '4', nome: 'TOKIO MARINE', mip: 'sbpeTokio', dfi: 0.00622 }
  ];
  /* SBPE (TR) imovel vinculado a empreendimento - Taxa Balcao. Taxa mensal vem da
     efetiva de 11,49% a.a.; PRICE compromete 25% da renda, SAC 30%. */
  var SBPE = {
    produto: '100501122', jurosNominal: 10.92, iMensal: Math.pow(1.1149, 1 / 12) - 1, taxaAdm: 25,
    PRICE: { comprometimento: 0.25, cota: 0.80, prazoMax: 360 },
    SAC: { comprometimento: 0.30, cota: 0.90, prazoMax: 420 }
  };
  var RENDA_MAX_MCMV = 13000;

  var PRAZO_MAX = 420;
  var PRAZO_MIN = 120;
  var IDADE_SEM_MAIS = 61;         /* a partir dessa idade a seguradora 15 nao entra no teto de 30% */
  var IDADE_MAX_MESES = 846;      /* 70 anos e 6 meses na data da simulacao */
  var K_PRAZO = 966.93;          /* meses: idade no ultimo vencimento < ~80a7m */
  var COMPROMETIMENTO = 0.30;
  var COTA = 0.80;
  var TAXA_ADM = 25;
  var DESCONTO_MIN = 1500, DESCONTO_MAX = 55000;
  var SUB_A = 626.3736950136708, SUB_C = 0.004174523285009393, SUB_RDMIN = 3700, SUB_FPOP_BASE = 1.10;

  var r2 = function (x) { return Math.round(x * 100 + 1e-9) / 100; };
  var addMeses = function (d, n) { return new Date(d.getFullYear(), d.getMonth() + n, d.getDate()); };
  var DIA = 86400000;

  function idadeAnos(nasc, em) {
    var a = em.getFullYear() - nasc.getFullYear();
    if (em.getMonth() < nasc.getMonth() || (em.getMonth() === nasc.getMonth() && em.getDate() < nasc.getDate())) a--;
    return a;
  }

  /* idade em meses completos (dia a dia) */
  function idadeMeses(nasc, em) {
    var m = (em.getFullYear() - nasc.getFullYear()) * 12 + em.getMonth() - nasc.getMonth();
    if (em.getDate() < nasc.getDate()) m--;
    var exato = em.getDate() === nasc.getDate();
    return { meses: m, exato: exato };
  }

  function taxaMip(seg, idade) {
    var t = MIP[seg.mip];
    for (var i = 0; i < t.length; i++) if (idade <= t[i][0]) return t[i][1] / 100;
    return null;
  }

  function prazoMaximo(nasc, primeiroVenc, teto) {
    var meses = (primeiroVenc - nasc) / DIA / 30.4375;
    return Math.max(PRAZO_MIN, Math.min(teto || PRAZO_MAX, Math.floor(K_PRAZO - meses)));
  }

  /* Enquadramento: produto, juros nominal (% a.a.) e taxa de administracao */
  function enquadrar(renda, valor, cidade, fgts) {
    var red = fgts ? 0 : 0.5;
    if (renda <= 5000 && valor <= cidade.tetoF12) {
      var jn = renda <= 2850 ? 4.5 : renda <= 3200 ? 4.75 : renda <= 3500 ? 5.0 : renda <= 4000 ? 5.5 : 6.5;
      return { produto: '100501101', faixa: renda <= 3200 ? 'Faixa 1' : 'Faixa 2', jn: jn + red,
               taxaAdm: renda <= 2850 ? 0 : TAXA_ADM, subsidio: true };
    }
    if (renda <= 9600 && valor <= 400000)
      return { produto: '100501101', faixa: 'Faixa 3', jn: 7.66 + red, taxaAdm: TAXA_ADM, subsidio: false };
    if (renda <= 13000 && valor <= 600000)
      return { produto: '100501129', faixa: 'Faixa 4', jn: 10, taxaAdm: TAXA_ADM, subsidio: false };
    return null;
  }

  function subsidio(renda, valor, jn, cidade) {
    var j = jn / 1200, n = 420;
    var dfin = 0.25 * renda * ((Math.pow(1 + j, n) - 1) / (Math.pow(1 + j, n) * j));
    var vvi = Math.min(valor, 0.675 * cidade.tetoF12);
    var fdfin = Math.max(-10, Math.min(10, 10 - 40 * (dfin / vvi - 0.5)));
    var fdr = Math.max(-10, Math.min(10, FDR_UF[cidade.uf] || 0));
    if (renda > SUB_RDMIN) return 0;
    var frenda = (SUB_A + SUB_C * Math.pow(SUB_RDMIN - renda, 2)) / SUB_FPOP_BASE * cidade.fpop;
    var d = Math.round(frenda * (1 + (fdr + fdfin) / 100));
    if (d < DESCONTO_MIN) return 0;
    return Math.min(d, DESCONTO_MAX);
  }

  /* entrada: { renda, valor, nascimento: Date, municipio, fgts: bool, possuiImovel?: bool, sistema: 'PRICE'|'SAC',
               hoje: Date, prazo?, valorFinanciamento? (teto opcional: financiar menos que a capacidade) }
     possuiImovel ou renda > 13.000 -> SBPE; senao MCMV. */
  function simular(e) {
    var cidade = CIDADES[e.municipio];
    if (!cidade) return { erro: 'Cidade sem regras da CAIXA mapeadas' };
    var im = idadeMeses(e.nascimento, e.hoje);
    if (im.meses > IDADE_MAX_MESES || (im.meses === IDADE_MAX_MESES && !im.exato)) return { erro: 'Idade acima de 70 anos e 6 meses' };
    var sac = e.sistema === 'SAC';
    var sbpe = e.possuiImovel === true || e.renda > RENDA_MAX_MCMV;
    var enq, i, regra, segs;
    if (sbpe) {
      regra = sac ? SBPE.SAC : SBPE.PRICE;
      enq = { produto: SBPE.produto, faixa: 'SBPE', jn: SBPE.jurosNominal, taxaAdm: SBPE.taxaAdm, subsidio: false };
      i = SBPE.iMensal;
      segs = SEGURADORAS_SBPE;
    } else {
      enq = enquadrar(e.renda, e.valor, cidade, e.fgts !== false);
      if (!enq) return { erro: 'Fora do enquadramento MCMV' };
      regra = { comprometimento: COMPROMETIMENTO, cota: COTA, prazoMax: PRAZO_MAX };
      i = enq.jn / 1200;
      segs = SEGURADORAS;
    }
    var primeiroVenc = addMeses(e.hoje, 1);
    var n = Math.min(e.prazo || regra.prazoMax, prazoMaximo(e.nascimento, primeiroVenc, regra.prazoMax));
    var idade = idadeAnos(e.nascimento, primeiroVenc);
    var k = sac ? (1 / n + i) : i / (1 - Math.pow(1 + i, -n));
    var lim = regra.comprometimento * e.renda;
    var pv = Infinity;
    segs.forEach(function (s) {
      if (!sbpe && s.codigo === '15' && idade >= IDADE_SEM_MAIS) return;
      var cap = (lim - enq.taxaAdm - e.valor * s.dfi / 100) / (k + taxaMip(s, idade));
      pv = Math.min(pv, cap);
    });
    var sub = enq.subsidio ? subsidio(e.renda, e.valor, enq.jn, cidade) : 0;
    var fin = r2(Math.min(pv, regra.cota * e.valor, e.valorFinanciamento > 0 ? e.valorFinanciamento : Infinity));
    var parcelaBase = r2(fin * k);
    var seguradoras = segs.map(function (s) {
      var primeira = parcelaBase + enq.taxaAdm + r2(fin * taxaMip(s, idade)) + r2(e.valor * s.dfi / 100);
      var ultima = sac ? r2(fin / n + (fin / n) * i) + enq.taxaAdm : parcelaBase + enq.taxaAdm;
      return { codigo: s.codigo, nome: s.nome, primeira: r2(primeira), ultima: r2(ultima) };
    });
    return {
      produto: enq.produto, faixa: enq.faixa, jurosNominal: enq.jn,
      jurosEfetivo: r2((Math.pow(1 + i, 12) - 1) * 100), prazo: n,
      valorFinanciamento: fin, subsidio: sub, entrada: r2(e.valor - fin - sub),
      taxaAdm: enq.taxaAdm, seguradoras: seguradoras
    };
  }

  var api = {
    simular: simular, subsidio: subsidio, enquadrar: enquadrar, prazoMaximo: prazoMaximo,
    CIDADES: CIDADES, MUNICIPIO_POR_CIDADE: MUNICIPIO_POR_CIDADE
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.MotorCaixa = api;
})(this);

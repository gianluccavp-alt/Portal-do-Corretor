/* ============================================================
   SIMULADOR DE FINANCIAMENTO - regras
   ------------------------------------------------------------
   Funcoes puras (sem DOM, sem rede) em cima do motor CAIXA.
   Usado pelo popup dos associativos (assets/financiamento-popup.js),
   pela tela /simulador-financiamento (assets/financiamento-app.js)
   e pelos testes (node --test tests/*.test.js).
   Spec: docs/superpowers/specs/2026-11-07-simulador-financiamento-design.md
   ============================================================ */
(function (raiz) {
  'use strict';

  var noNode = typeof module !== 'undefined' && module.exports;
  var Motor = noNode ? require('./motor-caixa.js') : raiz.MotorCaixa;
  var Match = noNode ? require('./match.js') : raiz.Match;

  var r2 = function (x) { return Math.round(x * 100 + 1e-9) / 100; };

  var RESP_PADRAO = {
    renda: 0, nascimento: null, fgts: true, possuiImovel: false, fatorSocial: false,
    subsidioAnterior: false, sistema: 'PRICE', prazo: null, financiarAte: null
  };

  function brl(n) {
    var v = Number(n) || 0, neg = v < 0;
    var partes = Math.abs(v).toFixed(2).split('.');
    var inteiro = partes[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return (neg ? '-' : '') + 'R$ ' + inteiro + ',' + partes[1];
  }

  function idadeAnos(nasc, em) {
    var a = em.getFullYear() - nasc.getFullYear();
    if (em.getMonth() < nasc.getMonth() || (em.getMonth() === nasc.getMonth() && em.getDate() < nasc.getDate())) a--;
    return a;
  }

  function dataValida(d) { return d instanceof Date && !isNaN(d.getTime()); }

  /* 'dd/mm/aaaa' -> Date (meia-noite local) ou null se a data nao existe */
  function lerData(txt) {
    var m = /^\s*(\d{1,2})\/(\d{1,2})\/(\d{4})\s*$/.exec(txt || '');
    if (!m) return null;
    var d = +m[1], mes = +m[2], a = +m[3];
    var dt = new Date(a, mes - 1, d);
    return dt.getFullYear() === a && dt.getMonth() === mes - 1 && dt.getDate() === d ? dt : null;
  }

  function mostraPerguntasSubsidio(renda, possuiImovel) { return Match.temSubsidio(renda, possuiImovel); }

  function mensagemErro(erro) {
    if (/70 anos/.test(erro)) return 'A CAIXA não financia acima de 70 anos e 6 meses na data de hoje. Se houver outro comprador mais novo, use a data dele.';
    if (/enquadramento/i.test(erro)) return 'Essa renda com esse valor de imóvel não enquadra no Minha Casa Minha Vida. Revise o valor ou a renda.';
    if (/Cidade/.test(erro)) return 'Ainda não temos as regras da CAIXA para essa cidade.';
    return erro;
  }

  /* campos com problema, na ordem do formulario */
  function validar(resp, imovel, hoje) {
    var out = [];
    if (!(resp.renda > 0)) out.push({ campo: 'renda', mensagem: 'Informe a renda bruta da família.' });
    if (!dataValida(resp.nascimento)) out.push({ campo: 'nascimento', mensagem: 'Informe a data de nascimento.' });
    else if (resp.nascimento > hoje) out.push({ campo: 'nascimento', mensagem: 'A data de nascimento está no futuro.' });
    else if (idadeAnos(resp.nascimento, hoje) < 18) out.push({ campo: 'nascimento', mensagem: 'O comprador precisa ter 18 anos ou mais.' });
    if (!(imovel.avaliacao > 0)) out.push({ campo: 'valor', mensagem: 'Informe o valor de avaliação do imóvel.' });
    if (!Motor.MUNICIPIO_POR_CIDADE[imovel.cidade]) out.push({ campo: 'cidade', mensagem: 'Escolha Ribeirão Preto, Campinas ou Sorocaba.' });
    return out;
  }

  /* maior 1a parcela entre as seguradoras (empate: a primeira da lista) */
  function seguradoraPadrao(seguradoras) {
    var melhor = null;
    (seguradoras || []).forEach(function (s) { if (!melhor || s.primeira > melhor.primeira) melhor = s; });
    return melhor ? melhor.codigo : null;
  }

  /* resp: respostas do cliente; imovel: { cidade, avaliacao, venda, ato, ... }.
     Com venda > 0 aplica as mesmas duas regras do Match (spec §4.1): trava da Faixa 3 em
     R$ 400 mil e teto do financiamento em venda - subsidio - ato. */
  function simular(resp, imovel, hoje) {
    var venda = imovel.venda > 0 ? imovel.venda : 0;
    var ato = venda > 0 && imovel.ato > 0 ? imovel.ato : 0;
    var comSubsidio = mostraPerguntasSubsidio(resp.renda, resp.possuiImovel);
    var trava = venda > 0 && Match.travaFaixa3({ renda: resp.renda, possuiImovel: resp.possuiImovel === true },
                                              { avaliacao: imovel.avaliacao, associativo: venda });
    var motorIn = {
      renda: resp.renda, valor: trava ? Match.TETO_F3 : imovel.avaliacao, nascimento: resp.nascimento,
      municipio: Motor.MUNICIPIO_POR_CIDADE[imovel.cidade], fgts: resp.fgts !== false,
      possuiImovel: resp.possuiImovel === true,
      fatorSocial: comSubsidio && resp.fatorSocial === true,
      subsidioAnterior: comSubsidio && resp.subsidioAnterior === true,
      sistema: resp.sistema === 'SAC' ? 'SAC' : 'PRICE', hoje: hoje
    };
    if (resp.prazo > 0) motorIn.prazo = resp.prazo;
    if (resp.financiarAte > 0) motorIn.valorFinanciamento = resp.financiarAte;

    var r = Motor.simular(motorIn);
    var sim = { erro: null, mensagem: null, motorIn: motorIn, r: r, capacidade: 0, limitado: false,
                trava: trava, entrada: 0, baseEntrada: venda > 0 ? 'venda' : 'avaliacao',
                segPadrao: null, parcelaMax: 0 };
    if (r.erro) { sim.erro = r.erro; sim.mensagem = mensagemErro(r.erro); return sim; }

    sim.capacidade = r.valorFinanciamento;
    if (venda > 0) {
      var teto = r2(venda - r.subsidio - ato);
      /* o motor entende valorFinanciamento 0 como "sem teto": sem espaco para financiar e aviso */
      if (teto <= 0) {
        sim.erro = 'Sem valor para financiar';
        sim.mensagem = 'O valor de venda menos subsídio e ato não deixa nada para financiar. Revise o valor do imóvel ou o ato.';
        return sim;
      }
      if (teto < r.valorFinanciamento) {
        motorIn.valorFinanciamento = Math.max(0, teto);
        r = Motor.simular(motorIn);
        sim.r = r;
        sim.limitado = true;
      }
    }
    var base = venda > 0 ? venda : imovel.avaliacao;
    sim.entrada = r2(base - r.valorFinanciamento - r.subsidio - ato);
    sim.segPadrao = seguradoraPadrao(r.seguradoras);
    sim.parcelaMax = r2(r.comprometimento * resp.renda);
    return sim;
  }

  function comparar(resp, imovel, hoje) {
    var price = {}, sac = {}, k;
    for (k in resp) { price[k] = resp[k]; sac[k] = resp[k]; }
    price.sistema = 'PRICE'; sac.sistema = 'SAC';
    return { PRICE: simular(price, imovel, hoje), SAC: simular(sac, imovel, hoje) };
  }

  function valoresCopia(sim, codigoSeg, renda) {
    var seg = null;
    sim.r.seguradoras.forEach(function (s) { if (s.codigo === codigoSeg) seg = s; });
    if (!seg) seg = sim.r.seguradoras.filter(function (s) { return s.codigo === sim.segPadrao; })[0];
    return { renda: renda, financiado: sim.r.valorFinanciamento, subsidio: sim.r.subsidio, parcFin: seg.primeira };
  }

  /* encargo nos meses 1, 61, 121, ... e no ultimo (um ponto a cada 5 anos) */
  function serieAnual(cron) {
    var out = [];
    if (!cron || !cron.length) return out;
    for (var i = 0; i < cron.length - 1; i += 60) out.push(cron[i].encargo);
    out.push(cron[cron.length - 1].encargo);
    return out;
  }

  /* Black Friday: liga/desliga a pergunta "Associativo ou Associativo Black Friday" (spec §2) */
  var CAMPANHA_BF = { ativa: true, cidades: ['Ribeirão Preto'] };
  var SEGS_VALIDAS = ['14', '15', '16', '4'];

  function pad(n, t) { n = String(n); while (n.length < t) n = '0' + n; return n; }

  /* respostas do cliente num parametro curto de URL (fz): sem renda e sem valores do imovel.
     aaaammdd.fgts.imovel.fatorSocial.subsidioAnterior.sistema(P|S).prazo(x).financiarAteEmCentavos(x).seguradora */
  function codificaRespostas(resp, codigoSeg) {
    var n = resp.nascimento;
    return [
      pad(n.getFullYear(), 4) + pad(n.getMonth() + 1, 2) + pad(n.getDate(), 2),
      resp.fgts !== false ? 1 : 0, resp.possuiImovel ? 1 : 0, resp.fatorSocial ? 1 : 0, resp.subsidioAnterior ? 1 : 0,
      resp.sistema === 'SAC' ? 'S' : 'P',
      resp.prazo > 0 ? Math.round(resp.prazo) : 'x',
      resp.financiarAte > 0 ? Math.round(resp.financiarAte * 100) : 'x',
      codigoSeg
    ].join('.');
  }

  function decodificaRespostas(txt) {
    var p = String(txt || '').split('.');
    if (p.length !== 9 || !/^\d{8}$/.test(p[0])) return null;
    var nasc = lerData(p[0].slice(6, 8) + '/' + p[0].slice(4, 6) + '/' + p[0].slice(0, 4));
    if (!nasc) return null;
    for (var i = 1; i <= 4; i++) if (p[i] !== '0' && p[i] !== '1') return null;
    if (p[5] !== 'P' && p[5] !== 'S') return null;
    if (p[6] !== 'x' && !(/^\d{1,3}$/.test(p[6]) && +p[6] >= 1 && +p[6] <= 420)) return null;
    if (p[7] !== 'x' && !(/^\d+$/.test(p[7]) && +p[7] > 0)) return null;
    if (SEGS_VALIDAS.indexOf(p[8]) < 0) return null;
    var resp = {}, k;
    for (k in RESP_PADRAO) resp[k] = RESP_PADRAO[k];
    resp.nascimento = nasc; resp.fgts = p[1] === '1'; resp.possuiImovel = p[2] === '1';
    resp.fatorSocial = p[3] === '1'; resp.subsidioAnterior = p[4] === '1';
    resp.sistema = p[5] === 'S' ? 'SAC' : 'PRICE';
    resp.prazo = p[6] === 'x' ? null : +p[6];
    resp.financiarAte = p[7] === 'x' ? null : +p[7] / 100;
    return { resp: resp, seg: p[8] };
  }

  function destinos(imovel) {
    var out = ['normal'];
    if (CAMPANHA_BF.ativa && CAMPANHA_BF.cidades.indexOf(imovel.cidade) >= 0) out.push('blackfriday');
    return out;
  }

  /* mesmos parametros que o associativo ja aceita do Match, mais origem e respostas (spec §7) */
  function urlAssociativo(destino, imovel, resp, sim, codigoSeg, hoje) {
    var v = valoresCopia(sim, codigoSeg, resp.renda);
    var p = [];
    if (imovel.empId && imovel.unidade) p.push(['emp', imovel.empId], ['unidade', imovel.unidade]);
    p.push(['renda', resp.renda], ['idade', idadeAnos(resp.nascimento, hoje)]);
    if (imovel.venda > 0) p.push(['valor', imovel.venda]);
    p.push(['fin', v.financiado], ['sub', v.subsidio], ['parcFin', v.parcFin],
           ['origem', 'financiamento'], ['fz', codificaRespostas(resp, codigoSeg)]);
    var pagina = destino === 'blackfriday' ? 'simulador-associativo-blackfriday.html' : 'simulador-associativo.html';
    return pagina + '?' + p.map(function (x) { return x[0] + '=' + encodeURIComponent(String(x[1])); }).join('&');
  }

  /* ---------- PDF: linhas ja formatadas (spec §9; desenho em assets/financiamento-pdf.js) ---------- */
  var AVISO_PDF = 'Simulação estimada com as regras do Simulador Habitacional CAIXA vigentes na data de emissão. ' +
    'Não é aprovação de crédito: valores sujeitos à análise da CAIXA, à avaliação do imóvel e à aprovação da Direcional.';

  function dataBr(d) { return pad(d.getDate(), 2) + '/' + pad(d.getMonth() + 1, 2) + '/' + d.getFullYear(); }
  function dataIso(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1, 2) + '-' + pad(d.getDate(), 2); }
  function pct(v) { return v.toFixed(2).replace('.', ',') + '%'; }
  function simNao(b) { return b ? 'Sim' : 'Não'; }
  function slug(t) {
    return String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  }
  function nomeSeguradora(n) {
    return String(n).toLowerCase().replace(/(^|\s)\S/g, function (c) { return c.toUpperCase(); });
  }
  function programa(r) { return r.faixa === 'SBPE' ? 'SBPE' : 'MCMV · ' + r.faixa; }
  function seguradoraDe(sim, codigo) {
    var s = sim.r.seguradoras.filter(function (x) { return x.codigo === codigo; })[0];
    return s || sim.r.seguradoras.filter(function (x) { return x.codigo === sim.segPadrao; })[0];
  }
  function serieDe(sim, codigo) {
    if (!sim || sim.erro) return [];
    return serieAnual(Motor.cronograma(sim.motorIn, sim.r, seguradoraDe(sim, codigo).codigo));
  }

  /* ctx = { comp:{PRICE,SAC}, sistema, imovel, resp, seg, pessoas:{cliente,corretor}, hoje } */
  function dadosPdf(ctx) {
    var sim = ctx.comp[ctx.sistema], r = sim.r, resp = ctx.resp, im = ctx.imovel;
    var outro = ctx.sistema === 'PRICE' ? 'SAC' : 'PRICE';
    var seg = seguradoraDe(sim, ctx.seg);
    var base = sim.baseEntrada === 'venda' ? im.venda : im.avaliacao;
    var cliente = (ctx.pessoas && ctx.pessoas.cliente) || '', corretor = (ctx.pessoas && ctx.pessoas.corretor) || '';
    var dados = [
      ['Renda familiar bruta', brl(resp.renda)],
      ['Nascimento (mais velho)', dataBr(resp.nascimento) + ' · ' + idadeAnos(resp.nascimento, ctx.hoje) + ' anos'],
      ['3 anos de FGTS', simNao(resp.fgts !== false)],
      ['Imóvel na cidade', simNao(resp.possuiImovel === true)]
    ];
    if (mostraPerguntasSubsidio(resp.renda, resp.possuiImovel)) {
      dados.push(['Mais de um comprador ou dependente', simNao(resp.fatorSocial === true)]);
      dados.push(['Subsídio anterior', simNao(resp.subsidioAnterior === true)]);
    }
    dados.push(['Cidade do imóvel', im.cidade]);
    var celula = function (s, f) { return !s || s.erro ? '—' : f(s); };
    return {
      arquivo: 'financiamento-' + (slug(cliente) || slug(im.empNome) || 'simulacao') + '-' + dataIso(ctx.hoje) + '.pdf',
      emissao: dataBr(ctx.hoje),
      cliente: cliente, corretor: corretor,
      imovel: { nome: im.empNome || 'Imóvel', detalhe: im.unidadeRotulo || '', avaliacao: brl(im.avaliacao), cidade: im.cidade },
      principal: {
        financiado: brl(r.valorFinanciamento), primeira: brl(seg.primeira),
        pctRenda: Math.round(seg.primeira / resp.renda * 100) + '% da renda',
        subsidio: r.subsidio > 0 ? brl(r.subsidio) : null, entrada: brl(sim.entrada),
        resumo: programa(r) + ' · ' + r.sistema + ' · ' + r.prazo + ' meses · ' + pct(r.jurosNominal) + ' a.a.'
      },
      barra: { fin: r.valorFinanciamento / base * 100, sub: r.subsidio / base * 100, ent: Math.max(0, sim.entrada) / base * 100 },
      condicoes: [
        ['Programa', programa(r)], ['Produto CAIXA', r.produto], ['Sistema de amortização', r.sistema],
        ['Prazo', r.prazo + ' meses'], ['Juros nominal / efetivo', pct(r.jurosNominal) + ' / ' + pct(r.jurosEfetivo) + ' a.a.'],
        ['Taxa de administração', brl(r.taxaAdm)], ['Parcela máxima', Math.round(r.comprometimento * 100) + '% da renda']
      ],
      dadosCliente: dados,
      seguradoras: r.seguradoras.map(function (s) {
        return { nome: nomeSeguradora(s.nome), primeira: brl(s.primeira), ultima: brl(s.ultima), escolhida: s.codigo === seg.codigo };
      }),
      comparacao: [
        ['Financiamento', celula(ctx.comp.PRICE, function (s) { return brl(s.r.valorFinanciamento); }), celula(ctx.comp.SAC, function (s) { return brl(s.r.valorFinanciamento); })],
        ['Entrada mínima', celula(ctx.comp.PRICE, function (s) { return brl(s.entrada); }), celula(ctx.comp.SAC, function (s) { return brl(s.entrada); })],
        ['1ª parcela', celula(ctx.comp.PRICE, function (s) { return brl(seguradoraDe(s, ctx.seg).primeira); }), celula(ctx.comp.SAC, function (s) { return brl(seguradoraDe(s, ctx.seg).primeira); })],
        ['Última parcela', celula(ctx.comp.PRICE, function (s) { return brl(seguradoraDe(s, ctx.seg).ultima); }), celula(ctx.comp.SAC, function (s) { return brl(seguradoraDe(s, ctx.seg).ultima); })]
      ],
      serie: (function () {
        var o = {}; o[ctx.sistema] = serieDe(sim, ctx.seg); o[outro] = serieDe(ctx.comp[outro], ctx.seg); return o;
      })(),
      aviso: AVISO_PDF
    };
  }

  var api = {
    RESP_PADRAO: RESP_PADRAO, CAMPANHA_BF: CAMPANHA_BF, dadosPdf: dadosPdf, programa: programa,
    codificaRespostas: codificaRespostas, decodificaRespostas: decodificaRespostas,
    destinos: destinos, urlAssociativo: urlAssociativo,
    simular: simular, comparar: comparar, seguradoraPadrao: seguradoraPadrao, valoresCopia: valoresCopia,
    mostraPerguntasSubsidio: mostraPerguntasSubsidio, mensagemErro: mensagemErro,
    lerData: lerData, validar: validar, serieAnual: serieAnual, brl: brl, idadeAnos: idadeAnos
  };
  if (noNode) module.exports = api;
  else raiz.Financiamento = api;
})(this);

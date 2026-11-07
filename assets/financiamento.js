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

  var api = {
    RESP_PADRAO: RESP_PADRAO,
    simular: simular, comparar: comparar, seguradoraPadrao: seguradoraPadrao, valoresCopia: valoresCopia,
    mostraPerguntasSubsidio: mostraPerguntasSubsidio, mensagemErro: mensagemErro,
    lerData: lerData, validar: validar, serieAnual: serieAnual, brl: brl, idadeAnos: idadeAnos
  };
  if (noNode) module.exports = api;
  else raiz.Financiamento = api;
})(this);

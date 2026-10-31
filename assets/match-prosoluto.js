/* ============================================================
   MATCH DE UNIDADES - copia do motor do Pro Soluto
   ------------------------------------------------------------
   COPIA de simulador-associativo.html (POLITICAS, TX,
   GAIA_ENTREGA_POR_TORRE, datas/financeiros, calc(),
   avaliarPolitica(), checklistAprovacao()) em funcoes puras.
   ATENCAO: toda mudanca de politica, taxa ou regra precisa ser
   feita NOS DOIS arquivos. tests/match-prosoluto.test.js executa
   o original e compara - se divergir, o teste quebra.
   O Match nao usa FGTS, bonus, sinais nem anuais (sempre zero).
   Spec: docs/superpowers/specs/2026-10-15-match-unidades-design.md
   ============================================================ */
(function (raiz) {
  'use strict';

  var POLITICAS = [
    { id: 'diamante', nome: 'Diamante', pctPS: 0.25, prazo: 84, cr: 0.50, crPS: 0.20 },
    { id: 'ouro',     nome: 'Ouro',     pctPS: 0.20, prazo: 84, cr: 0.50, crPS: 0.20 },
    { id: 'prata',    nome: 'Prata',    pctPS: 0.18, prazo: 84, cr: 0.48, crPS: 0.18 },
    { id: 'bronze',   nome: 'Bronze',   pctPS: 0.15, prazo: 84, cr: 0.45, crPS: 0.15 },
    { id: 'aco',      nome: 'Aço',      pctPS: 0.12, prazo: 84, cr: 0.40, crPS: 0.10 }
  ];

  var TX = {
    jurosPre: 0.005, jurosPos: 0.015,
    jurosPreAntigo: 0.003, jurosPosAntigo: 0.013,
    dataTaxaNova: '2021-03-08',
    dataCarencia: '2020-04-23',
    maxDiasVenc1: 120,
    maxDiasAto: 7,
    diasSinal: [30, 60, 90],
    diasVenc: [5, 10, 15],
    faixas: [0.40, 0.30, 0.20, 0.10],
    tolPS: 0.10,
    tolPrazo: 12, prazoMinComite: 72,
    tolCR: 0.05
  };

  var GAIA_ENTREGA_POR_TORRE = { 1: '2028-10-31' };

  function politicaPorId(id) {
    for (var i = 0; i < POLITICAS.length; i++) if (POLITICAS[i].id === id) return POLITICAS[i];
    return POLITICAS[4];
  }

  function entregaDe(emp, torre) {
    if (emp.id === 'gaia' && torre && GAIA_ENTREGA_POR_TORRE[torre]) return GAIA_ENTREGA_POR_TORRE[torre];
    return emp.entrega;
  }

  /* datas ------------------------------------------------- */
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function parseData(str) {
    if (!str) return null;
    var p = str.split('-'); if (p.length !== 3) return null;
    var d = new Date(+p[0], (+p[1]) - 1, +p[2]);
    return isFinite(d.getTime()) ? d : null;
  }
  function isoData(d) { return d ? (d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate())) : ''; }
  function eom(d) { return new Date(d.getFullYear(), d.getMonth() + 1, 0); }
  function mi(d) { return d.getFullYear() * 12 + d.getMonth(); }
  function addMeses(d, k) {
    var alvo = new Date(d.getFullYear(), d.getMonth() + k, 1);
    var ult = new Date(alvo.getFullYear(), alvo.getMonth() + 1, 0).getDate();
    return new Date(alvo.getFullYear(), alvo.getMonth(), Math.min(d.getDate(), ult));
  }
  function dias(a, b) { return Math.round((b - a) / 86400000); }

  function sugereVenc1(dataVenda) {
    var d = addMeses(parseData(dataVenda), 1);
    return isoData(new Date(d.getFullYear(), d.getMonth(), 10));
  }

  /* financeiros ------------------------------------------- */
  function pmt(i, n, pv) {
    if (!n || !pv) return 0;
    if (!i) return pv / n;
    return pv * i / (1 - Math.pow(1 + i, -n));
  }
  function anuidade(i, n) {
    if (!n) return 0;
    return (Math.pow(1 + i, n) * i) / (Math.pow(1 + i, n) - 1);
  }
  function r2(v) { return Math.round(v * 100) / 100; }
  function r4(v) { return Math.round(v * 10000) / 10000; }

  /* COPIA de calc() - S.* virou e.*; fgts, bonus, sinais e anuais = 0 */
  function calcular(e) {
    var pol = e.politica;
    var venda = parseData(e.dataVenda), venc1 = parseData(e.dataVenc1);
    var prazo = Math.max(0, Math.round(e.prazo) || 0);

    var c = {
      e: e.emp, pol: pol, venda: venda, venc1: venc1, prazo: prazo, pronto: false,
      preSaldo: 0, saldoMensais: 0, carencia: 0, saldoCorrigido: 0, psCorrigido: 0, pctPS: 0,
      nPre: 0, nPos: 0, i1: TX.jurosPre, i2: TX.jurosPos,
      linear: null, escalonado: null,
      crLinear: 0, crPS: 0, crEscal: 0, veredito: null,
      somaSinais: 0, somaAnuais: 0
    };
    if (!e.emp || !venda || !venc1 || prazo <= 0 || e.valor <= 0) return c;

    c.i1 = venda < parseData(TX.dataTaxaNova) ? TX.jurosPreAntigo : TX.jurosPre;
    c.i2 = venda < parseData(TX.dataTaxaNova) ? TX.jurosPosAntigo : TX.jurosPos;

    var entrega = parseData(e.emp.entrega), inicioObra = parseData(e.emp.inicioObra);

    c.preSaldo = e.valor - (e.financiado + e.subsidio + e.ato);
    c.saldoMensais = c.preSaldo - c.somaSinais - c.somaAnuais;

    c.nPre = Math.max(0, Math.min(prazo, mi(entrega) - mi(venc1)));
    c.nPos = prazo - c.nPre;

    var taxaCar = c.nPre !== 0 ? c.i1 : c.i2;
    c.carencia = venda >= parseData(TX.dataCarencia)
      ? Math.round(dias(eom(venda), eom(venc1)) / 30) : 0;
    if (c.carencia < 0) c.carencia = 0;
    var fatorCar = Math.pow(1 + taxaCar, c.carencia);
    c.correcaoCarencia = c.saldoMensais * fatorCar - c.saldoMensais;
    c.saldoCorrigido = c.saldoMensais * fatorCar;
    c.psCorrigido = c.saldoCorrigido + c.somaAnuais * fatorCar;

    var baseP = e.valor;
    c.pctPS = baseP > 0 ? r4(c.psCorrigido) / baseP : 0;
    c.pronto = true;

    var fPre = c.nPre ? anuidade(c.i1, c.nPre) : 0;
    var fPos = c.nPos ? Math.pow(1 + c.i1, c.nPre) * anuidade(c.i2, c.nPos) : 0;
    var pctPre = (c.nPre && c.nPos) ? 1 - fPre / (fPre + fPos) : (c.nPre ? 1 : 0);
    var saldoPre = c.saldoCorrigido * pctPre;
    var saldoPos = (c.saldoCorrigido - saldoPre) * Math.pow(1 + c.i1, c.nPre);
    var parcPre = r2(pmt(c.i1, c.nPre, saldoPre));
    var parcPos = r2(pmt(c.i2, c.nPos, saldoPos));
    c.linear = {
      parcPre: parcPre, parcPos: parcPos, saldoPre: saldoPre, saldoPos: saldoPos,
      parcela: parcPre || parcPos,
      total: parcPre * c.nPre + parcPos * c.nPos
    };

    var pFaixa = Math.ceil(prazo / 4);
    var prazos = [pFaixa, pFaixa, pFaixa, Math.max(0, prazo - 3 * pFaixa)];
    var accPre = 0, accPos = 0, faixas = [], totalEsc = 0;
    for (var k = 0; k < 4; k++) {
      var P = prazos[k], V = c.saldoCorrigido * TX.faixas[k];
      var bPre = Math.max(0, Math.min(P, c.nPre - accPre));
      var bPos = P - bPre;
      var hPre;
      if (bPre && bPos) {
        var fa = anuidade(c.i1, bPre), fb = Math.pow(1 + c.i1, bPre) * anuidade(c.i2, bPos);
        hPre = 1 - fa / (fa + fb);
      } else { hPre = bPre ? 1 : 0; }
      var vPre = hPre * V, vPos = V - vPre;
      var flPre = vPre * Math.pow(1 + c.i1, accPre) * Math.pow(1 + c.i2, accPos);
      var flPos = vPos * Math.pow(1 + c.i1, accPre + bPre) * Math.pow(1 + c.i2, accPos);
      var parcela = Math.max(bPre ? pmt(c.i1, bPre, flPre) : 0, bPos ? pmt(c.i2, bPos, flPos) : 0);
      faixas.push({ n: k + 1, prazo: P, valor: V, pct: TX.faixas[k], mesesPre: bPre, mesesPos: bPos, parcela: parcela });
      totalEsc += parcela * P;
      accPre += bPre; accPos += bPos;
    }
    c.escalonado = { faixas: faixas, total: totalEsc };

    var nTotObra = Math.max(0, Math.min(mi(entrega), mi(venc1) + prazo) - mi(inicioObra));
    var nDecorr = Math.max(0, Math.min(mi(venc1), mi(entrega)) - mi(inicioObra));
    var evBase = nTotObra > 0 ? nDecorr / nTotObra : 1;
    var evStep = (nTotObra > 0 && c.nPre > 0) ? ((nTotObra - nDecorr) / nTotObra) / c.nPre : 0;

    function parcelaFaixa(nPS) {
      var cum = 0;
      for (var i = 0; i < faixas.length; i++) { cum += faixas[i].prazo; if (nPS <= cum) return faixas[i].parcela; }
      return faixas[faixas.length - 1].parcela;
    }

    var ev = evBase, nPS = 0, mes = 0, tipoAnt = 'Ato Sinal CC/Boleto', guarda = 0;
    while (nPS < prazo && guarda < 400) {
      guarda++;
      var d = addMeses(venc1, mes); mes++;
      var pre = mi(d) < mi(entrega);
      var tipo = 'Mensal P.S';
      nPS++;
      var juros;
      if (pre) {
        if (tipo !== tipoAnt) ev = evBase; else ev += evStep;
        juros = e.parcFin * ev;
      } else {
        juros = e.parcFin;
      }
      tipoAnt = tipo;

      var psLin = pre ? parcPre : parcPos;
      var psEsc = parcelaFaixa(nPS);
      var crLin = e.renda > 0 ? r4((juros + psLin) / e.renda) : 0;
      var crEsc = e.renda > 0 ? r4((juros + psEsc) / e.renda) : 0;
      var crPSm = e.renda > 0 ? r4(psLin / e.renda) : 0;
      if (crLin > c.crLinear) c.crLinear = crLin;
      if (crEsc > c.crEscal) c.crEscal = crEsc;
      if (crPSm > c.crPS) c.crPS = crPSm;
    }

    c.veredito = avaliarPolitica(c);
    return c;
  }

  /* COPIA de status() / avaliarPolitica() - sem os textos de exibicao */
  function status(valor, limite, limiteComite) {
    if (valor <= limite + 1e-9) return 'Aprovado';
    if (valor <= limiteComite + 1e-9) return 'Comitê';
    return 'Reprovado';
  }
  function avaliarPolitica(c) {
    var pol = c.pol;
    var limPS = pol.pctPS, comitePS = Math.round((limPS + limPS * TX.tolPS) * 100) / 100;
    var limPz = pol.prazo, comitePz = Math.max(TX.prazoMinComite, limPz + TX.tolPrazo);
    var limCR = pol.cr, comiteCR = limCR + TX.tolCR;
    var limCRPS = pol.crPS;

    var stPS = status(c.pctPS, limPS, comitePS);
    var stPz = status(c.prazo, limPz, comitePz);
    var stCR;
    if (c.crLinear <= limCR + 1e-9 && c.crPS <= limCRPS + 1e-9) stCR = 'Aprovado';
    else if (c.crLinear <= comiteCR + 1e-9 && c.crPS <= limCRPS + 1e-9) stCR = 'Comitê';
    else stCR = 'Reprovado';
    var stEsc = status(c.crEscal, limCR, comiteCR);

    var itens = [{ id: 'ps', st: stPS }, { id: 'pz', st: stPz }, { id: 'cr', st: stCR }, { id: 'cres', st: stEsc }];
    var chave = [stPS, stPz, stCR];
    var final = chave.every(function (s) { return s === 'Aprovado'; }) ? 'Aprovado'
              : (chave.some(function (s) { return s === 'Reprovado'; }) ? 'Reprovado' : 'Comitê');
    return { itens: itens, final: final };
  }

  /* COPIA de checklistAprovacao() - mesmos ids e ordem, sem textos.
     Sinais e anuais nao existem no Match: os itens deles ficam ok. */
  function checklistAprovacao(c, e) {
    var v = c.veredito.itens;
    var dAto = parseData(e.dataAto);
    return [
      { id: 'ps', grave: true, ok: v[0].st === 'Aprovado' },
      { id: 'prazo', grave: true, ok: v[1].st === 'Aprovado' },
      { id: 'cr', grave: true, ok: v[2].st === 'Aprovado' },
      { id: 'cresc', grave: false, ok: v[3].st === 'Aprovado' },
      { id: 'venc1', grave: true, ok: TX.diasVenc.indexOf(c.venc1.getDate()) >= 0 &&
          dias(c.venda, c.venc1) >= 0 && dias(c.venda, c.venc1) <= TX.maxDiasVenc1 },
      { id: 'ato', grave: true, ok: e.ato <= 0 || !dAto || dias(c.venda, dAto) <= TX.maxDiasAto },
      { id: 'sinais', grave: true, ok: true },
      { id: 'sinaisOrdem', grave: true, ok: true },
      { id: 'anuais', grave: false, ok: true },
      { id: 'parcmin', grave: false, ok: !c.linear || c.linear.parcela >= c.e.parcMin },
      { id: 'saldo', grave: true, ok: c.preSaldo >= -0.01 && c.saldoMensais >= -0.01 }
    ];
  }

  /* Regra do Match (spec 4.3): o carne passa se todos os itens dele
     estao ok. Linear usa 'cr'; escalonado usa 'cresc'. */
  var COMUNS = ['ps', 'prazo', 'venc1', 'ato', 'sinais', 'sinaisOrdem', 'anuais', 'parcmin', 'saldo'];
  function aprovacaoDoChecklist(lista) {
    var ok = {};
    lista.forEach(function (x) { ok[x.id] = x.ok; });
    var comuns = COMUNS.every(function (id) { return ok[id]; });
    return { linear: comuns && ok.cr, escalonado: comuns && ok.cresc };
  }
  /* Pro Soluto zerado (banco + subsidio + ato cobrem a venda): nao ha
     carne, entao a parcela minima nao se aplica. */
  function aprovacao(c, e) {
    var lista = checklistAprovacao(c, e);
    if (c.pronto && c.saldoCorrigido <= 0.01) {
      lista = lista.map(function (x) { return x.id === 'parcmin' ? { id: x.id, grave: x.grave, ok: true } : x; });
    }
    return aprovacaoDoChecklist(lista);
  }

  var api = {
    POLITICAS: POLITICAS, TX: TX, GAIA_ENTREGA_POR_TORRE: GAIA_ENTREGA_POR_TORRE,
    politicaPorId: politicaPorId, entregaDe: entregaDe,
    sugereVenc1: sugereVenc1, calcular: calcular, checklistAprovacao: checklistAprovacao,
    aprovacao: aprovacao, aprovacaoDoChecklist: aprovacaoDoChecklist
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.MatchProSoluto = api;
})(this);

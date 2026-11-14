/* ============================================================
   MAQUETE 3D - regras puras
   ------------------------------------------------------------
   Funcoes puras (sem DOM, sem rede, sem Three.js): grade de
   unidades, status, resumo, busca, filtros, navegacao e URLs
   dos simuladores. Usado no browser via window.Maquete e pelos
   testes (node --test tests/*.test.js).
   ============================================================ */
(function (raiz) {
  'use strict';

  var RANK = { disponivel: 1, reservada: 2, outro: 3 };

  function pad(n, tam) {
    var s = String(n);
    while (s.length < tam) s = '0' + s;
    return s;
  }

  function semAcento(t) {
    return String(t == null ? '' : t).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/\s+/g, ' ').trim();
  }

  function indice(cfg, torre, andar, final) {
    var t = cfg.torres.indexOf(torre);
    if (t < 0) return -1;
    if (andar < 0 || andar >= cfg.andares || andar % 1 !== 0) return -1;
    if (final < 1 || final > cfg.finais || final % 1 !== 0) return -1;
    return (t * cfg.andares + andar) * cfg.finais + (final - 1);
  }

  function posicao(cfg, idx) {
    var final = (idx % cfg.finais) + 1;
    var resto = Math.floor(idx / cfg.finais);
    var andar = resto % cfg.andares;
    var t = Math.floor(resto / cfg.andares);
    return { torre: cfg.torres[t], andar: andar, final: final };
  }

  function codigo(torre, andar, final) {
    return 'BL' + pad(torre, 2) + '-' + pad(andar, 2) + pad(final, 2);
  }

  function statusDe(texto) {
    var t = semAcento(texto);
    if (t.indexOf('reservad') === 0) return 'reservada';
    if (t === 'disponivel' || t === 'mirror') return 'disponivel';
    return 'outro';
  }

  function torreDe(bl) {
    var m = /\d+/.exec(String(bl == null ? '' : bl));
    return m ? parseInt(m[0], 10) : NaN;
  }

  /* cfg.semUnidade: posicoes da grade sem apartamento (ex.: hall no lugar do final 1 do terreo, torre com
     menos andares). Cada regra: { torres?, andares?, andarMin?, finais? }; campo ausente = qualquer. */
  function existe(cfg, torre, andar, final) {
    var regras = cfg.semUnidade || [];
    for (var i = 0; i < regras.length; i++) {
      var r = regras[i];
      if (r.torres && r.torres.indexOf(torre) < 0) continue;
      if (r.andares && r.andares.indexOf(andar) < 0) continue;
      if (r.andarMin != null && andar < r.andarMin) continue;
      if (r.finais && r.finais.indexOf(final) < 0) continue;
      return false;
    }
    return true;
  }

  function montarGrade(cfg, units) {
    var total = cfg.torres.length * cfg.andares * cfg.finais;
    var celulas = [];
    var i, p;
    var ignoradas = 0;
    var linhas = {};
    var venda = {};

    if (units) {
      for (i = 0; i < units.length; i++) {
        var u = units[i];
        /* cfg.torresVenda: so essas torres entram (as outras ficam "fora", ex.: Ipiranga vende so T1 e T3) */
        if (cfg.torresVenda && cfg.torresVenda.indexOf(torreDe(u.bl)) < 0) continue;
        var idx = indice(cfg, torreDe(u.bl), Number(u.andar), Number(u.f));
        if (idx < 0) { ignoradas++; continue; }
        var st = statusDe(u.status);
        var atual = linhas[idx];
        if (!atual || RANK[st] > RANK[atual.st]) linhas[idx] = { st: st, u: u };
        venda[torreDe(u.bl)] = true;
      }
    }

    var torresAVenda = cfg.torres.filter(function (t) { return venda[t]; });

    for (i = 0; i < total; i++) {
      p = posicao(cfg, i);
      var estado, un = null;
      if (!existe(cfg, p.torre, p.andar, p.final)) estado = 'inexistente';
      else if (!units) estado = 'sem-dados';
      else if (!venda[p.torre]) estado = 'fora';
      else if (!linhas[i]) estado = 'vendida';
      else {
        un = linhas[i].u;
        estado = linhas[i].st === 'outro' ? 'vendida' : linhas[i].st;
      }
      celulas.push({ idx: i, torre: p.torre, andar: p.andar, final: p.final, codigo: codigo(p.torre, p.andar, p.final), estado: estado, u: un });
    }
    return { celulas: celulas, torresAVenda: torresAVenda, ignoradas: ignoradas };
  }

  function resumo(grade) {
    var r = { total: 0, disponiveis: 0, reservadas: 0, vendidas: 0, pctVendido: 0 };
    grade.celulas.forEach(function (c) {
      if (c.estado === 'disponivel') r.disponiveis++;
      else if (c.estado === 'reservada') r.reservadas++;
      else if (c.estado === 'vendida') r.vendidas++;
      else return;
      r.total++;
    });
    r.pctVendido = r.total ? Math.round(r.vendidas / r.total * 1000) / 10 : 0;
    return r;
  }

  function nascente(cfg, torre, final) {
    var s = cfg.solNascente || {};
    var lista = s[torre] || s['default'] || [];
    return lista.indexOf(final) >= 0;
  }

  function posicaoLabel(tipo) {
    return semAcento(tipo).indexOf('ponta') >= 0 ? 'Ponta' : 'Meio';
  }

  function interpretarBusca(texto) {
    var t = semAcento(texto);
    var m = /^(?:(?:torre|bl|t)\s*0*(\d+)\s*[-\s]*(?:(?:apto|apt|ap|unidade|un)\.?\s*)?[-\s]*)?(\d{3,4})$/.exec(t);
    if (!m) return null;
    var n = parseInt(m[2], 10);
    return { torre: m[1] ? parseInt(m[1], 10) : null, andar: Math.floor(n / 100), final: n % 100 };
  }

  /* f.sol: 'nascente' | 'poente' | vazio (todos); precisa do cfg para ler solNascente */
  function filtrar(grade, f, cfg) {
    var saida = new Set();
    var tipos = f.tipos || [];
    grade.celulas.forEach(function (c) {
      if (c.estado === 'fora' || c.estado === 'sem-dados' || c.estado === 'inexistente') return;
      if (f.soDisponiveis && c.estado !== 'disponivel') return;
      if (tipos.length && !(c.u && tipos.indexOf(c.u.tipo) >= 0)) return;
      if (c.andar < f.andarMin || c.andar > f.andarMax) return;
      if (f.sol && cfg && nascente(cfg, c.torre, c.final) !== (f.sol === 'nascente')) return;
      saida.add(c.idx);
    });
    return saida;
  }

  function vizinhaDisponivel(grade, idx, dir, visiveis) {
    var n = grade.celulas.length;
    var passo = dir < 0 ? -1 : 1;
    var i = idx;
    for (var k = 1; k < n; k++) {
      i = ((i + passo) % n + n) % n;
      if (grade.celulas[i].estado !== 'disponivel') continue;
      if (visiveis && !visiveis.has(i)) continue;
      return i;
    }
    return null;
  }

  function urlsSimuladores(simId, cod) {
    var q = '?emp=' + encodeURIComponent(simId) + '&unidade=' + encodeURIComponent(cod);
    return { associativo: 'simulador-associativo.html' + q, tabelaDireta: 'simulador-tabela-direta.html' + q };
  }

  function estados(grade) {
    return grade.celulas.map(function (c) { return c.estado; });
  }

  var api = {
    indice: indice, posicao: posicao, existe: existe, codigo: codigo, statusDe: statusDe, montarGrade: montarGrade, resumo: resumo,
    nascente: nascente, posicaoLabel: posicaoLabel, interpretarBusca: interpretarBusca, filtrar: filtrar,
    vizinhaDisponivel: vizinhaDisponivel, urlsSimuladores: urlsSimuladores, estados: estados
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.Maquete = api;
})(this);

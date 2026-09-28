/* ============================================================
   PENDENCIAS DE VENDAS - regras de negocio
   ------------------------------------------------------------
   Funcoes puras (sem DOM, sem rede). Usadas pela pagina
   /pendencias-vendas via window.Pendencias e pelos testes
   (node --test tests/*.test.js).
   Spec: docs/superpowers/specs/2026-09-28-pendencias-vendas-design.md
   ============================================================ */
(function (raiz) {
  'use strict';

  var FASES_PADRAO = ['Aprovado Pró Soluto', 'Proposta Aprovada', 'Aprovado SAFI', 'Análise SAFI'];
  var DIAS_ALERTA = 15;
  var DIA_MS = 86400000;
  /* separador da coluna Imobiliaria: "-", "–", "—" ou o "?" que aparece
     quando o travessao chega corrompido do Salesforce */
  var SEP = '\\s*[-\u2013\u2014?\uFFFD]\\s*';

  /* ---------- texto ---------- */
  function normalizar(valor) {
    if (valor === null || valor === undefined) return '';
    return String(valor).trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  var CONECTIVOS = { da: 1, de: 1, di: 1, 'do': 1, dos: 1, das: 1, e: 1 };
  function titleCase(texto) {
    return String(texto || '').trim().toLowerCase().split(/\s+/).filter(Boolean)
      .map(function (p, i) { return i > 0 && CONECTIVOS[p] ? p : p.charAt(0).toUpperCase() + p.slice(1); })
      .join(' ');
  }

  function formatarEquipe(imobiliaria) {
    var t = String(imobiliaria || '').trim();
    if (!t) return '—';
    var sufixo = '';
    var inativo = t.match(new RegExp(SEP + 'inativo\\s*$', 'i'));
    if (inativo) { sufixo = ' - Inativo'; t = t.slice(0, inativo.index); }
    var pj = t.match(new RegExp('^SPI' + SEP + 'CANAL IMOB PJ' + SEP + '(.+)$', 'i'));
    if (pj) return 'Canal PJ · ' + titleCase(pj[1]) + sufixo;
    t = t.replace(new RegExp('^DIRECIONAL VENDAS SPI' + SEP, 'i'), '');
    return titleCase(t) + sufixo;
  }

  function formatarValor(valor, comCentavos) {
    if (valor === null || valor === undefined || valor === '' || isNaN(Number(valor))) return 'Não informado';
    var casas = comCentavos ? 2 : 0;
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency', currency: 'BRL', minimumFractionDigits: casas, maximumFractionDigits: casas
    }).format(Number(valor)).replace(/\u00a0/g, ' ');
  }

  function formatarMi(valor) {
    var n = Number(valor) || 0;
    if (n >= 1e6) return 'R$ ' + (n / 1e6).toFixed(2).replace('.', ',') + ' mi';
    return formatarValor(n, false);
  }

  /* ---------- datas ---------- */
  function parseData(texto) {
    var m = String(texto || '').trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})(?:\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?$/);
    if (!m) return null;
    var d = new Date(+m[3], +m[2] - 1, +m[1], +(m[4] || 0), +(m[5] || 0), +(m[6] || 0));
    return isNaN(d.getTime()) ? null : d;
  }
  function inicioDoDia(d) { return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }
  /* Math.round absorve a hora a mais/a menos do horario de verao */
  function diasEntre(de, ate) { return Math.round((inicioDoDia(ate) - inicioDoDia(de)) / DIA_MS); }
  function diasEmAberto(dataVenda, hoje) {
    var d = parseData(dataVenda);
    return d ? diasEntre(d, hoje) : null;
  }
  function textoDias(dias) {
    if (dias === null || dias === undefined) return '—';
    if (dias === 0) return 'hoje';
    return dias + (dias === 1 ? ' dia' : ' dias');
  }
  function isoParaData(iso) {
    var m = String(iso || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
    return m ? new Date(+m[1], +m[2] - 1, +m[3]) : null;
  }
  function doisDigitos(n) { return (n < 10 ? '0' : '') + n; }
  function formatarAtualizacao(iso, agora) {
    var d = iso ? new Date(iso) : null;
    if (!d || isNaN(d.getTime())) return 'Última atualização do Salesforce desconhecida';
    var hora = doisDigitos(d.getHours()) + ':' + doisDigitos(d.getMinutes());
    if (diasEntre(d, agora) === 0) return 'Salesforce atualizado hoje às ' + hora;
    return 'Salesforce atualizado em ' + doisDigitos(d.getDate()) + '/' + doisDigitos(d.getMonth() + 1) +
      '/' + d.getFullYear() + ' às ' + hora;
  }

  /* ---------- exibicao ---------- */
  function justificativaExibida(texto) {
    var t = String(texto || '').trim();
    return t === '' || t === '.' ? 'Sem justificativa registrada' : t;
  }
  function notaDaLinha(venda) {
    var r = String(venda.retorno || '').trim();
    if (r) return 'Retorno: ' + r;
    var o = String(venda.observacao || '').trim();
    if (o) return 'Obs.: ' + o;
    return '';
  }
  var RANKINGS = { diamante: 'Diamante', ouro: 'Ouro', prata: 'Prata', bronze: 'Bronze', aco: 'Aço' };
  function rankingChave(ranking) { return normalizar(ranking).replace(/[^a-z]/g, ''); }
  function rankingRotulo(ranking) { return RANKINGS[rankingChave(ranking)] || String(ranking || '').trim(); }

  /* ---------- pendencias ---------- */

  /* ---------- filtros ---------- */

  var api = {
    FASES_PADRAO: FASES_PADRAO,
    DIAS_ALERTA: DIAS_ALERTA,
    normalizar: normalizar,
    titleCase: titleCase,
    formatarEquipe: formatarEquipe,
    formatarValor: formatarValor,
    formatarMi: formatarMi,
    parseData: parseData,
    inicioDoDia: inicioDoDia,
    diasEntre: diasEntre,
    diasEmAberto: diasEmAberto,
    textoDias: textoDias,
    isoParaData: isoParaData,
    formatarAtualizacao: formatarAtualizacao,
    justificativaExibida: justificativaExibida,
    notaDaLinha: notaDaLinha,
    rankingChave: rankingChave,
    rankingRotulo: rankingRotulo
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.Pendencias = api;
})(this);

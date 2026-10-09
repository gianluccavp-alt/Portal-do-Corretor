/* ============================================================
   VISITAS DA RECEPCAO - regras puras
   ------------------------------------------------------------
   Funcoes sem DOM e sem rede. Usadas por /visitas-recepcao e
   /visitas-recepcao-adm via window.Visitas e pelos testes
   (node --test tests/*.test.js).
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md
   ============================================================ */
(function (raiz) {
  'use strict';

  var TIPOS = {
    esp: { nome: 'Espontânea', cor: '#3A4043' },
    house: { nome: 'Corretor house', cor: '#E4032B' },
    imob: { nome: 'Imobiliária', cor: '#A3ABAE' }
  };
  var ORDEM_TIPOS = ['esp', 'house', 'imob'];
  var MAX_TEXTO = 80;
  var DIA_MS = 86400000;
  var DIAS_SEMANA = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb'];

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function tipoValido(t) { return ORDEM_TIPOS.indexOf(t) >= 0; }

  /* ---------- texto ---------- */
  function normalizarTexto(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/\s+/g, ' ').trim().slice(0, MAX_TEXTO);
  }
  function chaveNome(s) {
    return normalizarTexto(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }
  /* evita que a planilha/Excel interprete o texto como formula */
  function neutralizarFormula(s) {
    var t = s === null || s === undefined ? '' : String(s);
    return /^[=+\-@\t\r]/.test(t) ? "'" + t : t;
  }
  function detalhe(v) {
    if (v.tipo === 'house') return v.corretorHouse || 'Corretor não informado';
    if (v.tipo === 'imob') return v.imobiliaria + (v.corretorImob ? ' · ' + v.corretorImob : '');
    return 'Sem agendamento';
  }

  /* ---------- datas (ISO yyyy-MM-dd, sem fuso) ---------- */
  function isoParaMs(iso) { var p = iso.split('-'); return Date.UTC(+p[0], +p[1] - 1, +p[2]); }
  function msParaIso(ms) {
    var d = new Date(ms);
    return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate());
  }
  function somarDias(iso, n) { return msParaIso(isoParaMs(iso) + n * DIA_MS); }
  function diasEntre(de, ate) { return Math.round((isoParaMs(ate) - isoParaMs(de)) / DIA_MS) + 1; }
  function dataLocalIso(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function horaLocal(d) { return pad(d.getHours()) + ':' + pad(d.getMinutes()); }
  function dataCurta(iso) { var p = iso.split('-'); return p[2] + '/' + p[1]; }
  function dataBr(iso) { var p = iso.split('-'); return p[2] + '/' + p[1] + '/' + p[0]; }
  function rotuloDia(iso) { return DIAS_SEMANA[new Date(isoParaMs(iso)).getUTCDay()] + ' ' + dataCurta(iso); }
  function intervalo(periodo, hoje) {
    var n = periodo === 'hoje' ? 1 : Number(periodo);
    return { de: somarDias(hoje, -(n - 1)), ate: hoje, dias: n };
  }

  /* ---------- formulario da recepcao (spec 5.1) ---------- */
  function validarFormulario(d) {
    var regras = [
      ['empreendimento', !normalizarTexto(d.empreendimento)],
      ['data', !/^\d{4}-\d{2}-\d{2}$/.test(d.data || '')],
      ['hora', !/^\d{2}:\d{2}$/.test(d.hora || '')],
      ['tipo', !tipoValido(d.tipo)],
      ['imobiliaria', d.tipo === 'imob' && !normalizarTexto(d.imobiliaria)]
    ];
    for (var i = 0; i < regras.length; i++) {
      if (regras[i][1]) return { ok: false, faltando: regras[i][0] };
    }
    return { ok: true, faltando: null };
  }

  function listaEmpreendimentos(cidades) {
    var out = [];
    (cidades || []).forEach(function (c) {
      (c.empreendimentos || []).forEach(function (e) { out.push({ nome: e.nome, cidade: c.name }); });
    });
    return out;
  }

  var api = {
    TIPOS: TIPOS,
    ORDEM_TIPOS: ORDEM_TIPOS,
    MAX_TEXTO: MAX_TEXTO,
    normalizarTexto: normalizarTexto,
    chaveNome: chaveNome,
    neutralizarFormula: neutralizarFormula,
    detalhe: detalhe,
    somarDias: somarDias,
    diasEntre: diasEntre,
    dataLocalIso: dataLocalIso,
    horaLocal: horaLocal,
    dataCurta: dataCurta,
    dataBr: dataBr,
    rotuloDia: rotuloDia,
    intervalo: intervalo,
    validarFormulario: validarFormulario,
    listaEmpreendimentos: listaEmpreendimentos
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.Visitas = api;
})(this);

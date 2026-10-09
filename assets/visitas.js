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

  /* ---------- agregacoes do dashboard (spec 6.2) ---------- */
  function vazioTipos() { return { esp: 0, house: 0, imob: 0, total: 0 }; }
  function somar(acc, v) {
    if (tipoValido(v.tipo)) { acc[v.tipo]++; acc.total++; }
    return acc;
  }
  function totaisPorTipo(visitas) { return visitas.reduce(somar, vazioTipos()); }

  function filtrar(visitas, f) {
    f = f || {};
    return visitas.filter(function (v) {
      if (f.de && v.data < f.de) return false;
      if (f.ate && v.data > f.ate) return false;
      if (f.cidade && f.cidade !== 'Todas' && v.cidade !== f.cidade) return false;
      if (f.empreendimento && f.empreendimento !== 'Todos' && v.empreendimento !== f.empreendimento) return false;
      return true;
    });
  }

  function porDia(visitas, de, ate) {
    var n = diasEntre(de, ate), indice = {}, out = [];
    for (var i = 0; i < n; i++) {
      var linha = vazioTipos();
      linha.data = somarDias(de, i);
      indice[linha.data] = linha;
      out.push(linha);
    }
    visitas.forEach(function (v) { if (indice[v.data]) somar(indice[v.data], v); });
    return out;
  }

  function porHora(visitas, ini, fim) {
    var out = [];
    for (var h = ini; h <= fim; h++) { var linha = vazioTipos(); linha.hora = h; out.push(linha); }
    visitas.forEach(function (v) {
      var hora = parseInt(String(v.hora).slice(0, 2), 10);
      if (isNaN(hora)) return;
      somar(out[Math.min(Math.max(hora, ini), fim) - ini], v);
    });
    return out;
  }

  function porEmpreendimento(visitas, lista) {
    var indice = {};
    var out = lista.map(function (e) {
      var linha = vazioTipos();
      linha.nome = e.nome;
      linha.cidade = e.cidade;
      indice[e.nome] = linha;
      return linha;
    });
    visitas.forEach(function (v) { if (indice[v.empreendimento]) somar(indice[v.empreendimento], v); });
    return out.sort(function (a, b) { return b.total - a.total || a.nome.localeCompare(b.nome, 'pt-BR'); });
  }

  /* agrupa nomes sem caixa/acento; o nome exibido e a grafia mais frequente */
  function agruparNomes(nomes) {
    var grupos = {}, ordem = [];
    nomes.forEach(function (bruto) {
      var nome = normalizarTexto(bruto), k = chaveNome(nome);
      if (!k) return;
      if (!grupos[k]) { grupos[k] = { qtd: 0, grafias: {} }; ordem.push(k); }
      grupos[k].qtd++;
      grupos[k].grafias[nome] = (grupos[k].grafias[nome] || 0) + 1;
    });
    return ordem.map(function (k) {
      var g = grupos[k], melhor = null;
      Object.keys(g.grafias).forEach(function (n) { if (melhor === null || g.grafias[n] > g.grafias[melhor]) melhor = n; });
      return { nome: melhor, qtd: g.qtd };
    });
  }

  function rankingImobiliarias(visitas, n) {
    var nomes = visitas.filter(function (v) { return v.tipo === 'imob'; }).map(function (v) { return v.imobiliaria; });
    return agruparNomes(nomes)
      .sort(function (a, b) { return b.qtd - a.qtd || a.nome.localeCompare(b.nome, 'pt-BR'); })
      .slice(0, n);
  }

  function chaveTempo(v) { return v.data + ' ' + v.hora; }
  function ordenarPorTempo(visitas, desc) {
    return visitas.slice().sort(function (a, b) {
      var ka = chaveTempo(a), kb = chaveTempo(b);
      var c = ka < kb ? -1 : ka > kb ? 1 : 0;
      return desc ? -c : c;
    });
  }
  function recentes(visitas, n) { return ordenarPorTempo(visitas, true).slice(0, n); }

  /* ---------- CSV (spec 6.2) ---------- */
  var CSV_COLUNAS = ['Data', 'Horário', 'Empreendimento', 'Cidade', 'Tipo', 'Corretor house', 'Imobiliária', 'Corretor imobiliária'];
  function celulaCSV(valor) {
    var t = neutralizarFormula(valor);
    return /[;"\r\n]/.test(t) ? '"' + t.replace(/"/g, '""') + '"' : t;
  }
  function gerarCSV(visitas) {
    var linhas = [CSV_COLUNAS.join(';')];
    ordenarPorTempo(visitas, false).forEach(function (v) {
      linhas.push([
        dataBr(v.data), v.hora, v.empreendimento, v.cidade, TIPOS[v.tipo] ? TIPOS[v.tipo].nome : v.tipo,
        v.corretorHouse, v.imobiliaria, v.corretorImob
      ].map(celulaCSV).join(';'));
    });
    /* BOM para o Excel abrir o UTF-8 com acentos certos */
    return '﻿' + linhas.join('\r\n') + '\r\n';
  }
  function nomeArquivoCSV(de, ate) { return 'visitas-' + de + '-a-' + ate + '.csv'; }

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
    listaEmpreendimentos: listaEmpreendimentos,
    filtrar: filtrar,
    totaisPorTipo: totaisPorTipo,
    porDia: porDia,
    porHora: porHora,
    porEmpreendimento: porEmpreendimento,
    rankingImobiliarias: rankingImobiliarias,
    ordenarPorTempo: ordenarPorTempo,
    recentes: recentes,
    gerarCSV: gerarCSV,
    nomeArquivoCSV: nomeArquivoCSV
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.Visitas = api;
})(this);

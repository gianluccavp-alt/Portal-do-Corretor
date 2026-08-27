/* ============================================================
   MODULO COMPARTILHADO DOS SIMULADORES
   Usado por simulador-associativo.html e simulador-tabela-direta.html
   ------------------------------------------------------------
   Expoe:
     window.SIM_EMPS     - catalogo de empreendimentos (aba "BD Politica")
     window.SimUnidades  - carga das unidades disponiveis (planilha Google)
     window.SimCombo     - lista flutuante com busca
     window.SimRichPdf   - HTML do editor rico -> jsPDF
   ============================================================ */

/* Mesma planilha usada pelo site de produtos (assets/config.js) */
window.SIM_SHEET_CSV_URL =
  'https://docs.google.com/spreadsheets/d/1hXgz1AbzYeaP2xLbM5Vj9wcM-0CWd98FG4PY5ZusJac/export?format=csv&gid=0';

/* ============================================================
   CATALOGO DE EMPREENDIMENTOS
   ------------------------------------------------------------
   Dados da aba "BD Politica" da planilha oficial
   "Simulador Pro Soluto - Comercial SP 11.xlsm":
     F = Cod Emp. | N = Empreendimento | X = Inicio da obra | Y = Entrega
     AD = % Pro Soluto padrao | AE = Prazo padrao | V = Parcela minima
   sheetName = valor da coluna "Nome do Empreendimento" na planilha de unidades.
   Ordem: Ribeirao Preto -> Campinas -> Sorocaba.
   ============================================================ */
window.SIM_EMPS = [
  /* ---------- Ribeirao Preto ---------- */
  { id:'gaia', cod:'414V', nome:'Village Gaia', cidade:'Ribeirão Preto',
    /* entrega 31/08/2029 conforme Salesforce - a planilha BD Política (30/09/2029) está errada */
    inicioObra:'2026-05-01', entrega:'2029-08-31', pctPS:0.18, prazoPadrao:52, parcMin:150,
    sheetName:'Village Gaia' },
  { id:'park', cod:'743V', nome:'Village Park', cidade:'Ribeirão Preto',
    inicioObra:'2025-04-01', entrega:'2028-01-31', pctPS:0.15, prazoPadrao:52, parcMin:150,
    sheetName:'Village Park' },
  { id:'botanico', cod:'574V', nome:'Reserva Direcional Jardim Botânico', cidade:'Ribeirão Preto',
    inicioObra:'2024-04-01', entrega:'2026-12-31', pctPS:0.18, prazoPadrao:52, parcMin:150,
    sheetName:'Reserva Direcional Jardim Botânico' },
  { id:'ipiranga', cod:'785V', nome:'Conquista Clube Ipiranga', cidade:'Ribeirão Preto',
    inicioObra:'2026-06-01', entrega:'2028-08-31', pctPS:0.15, prazoPadrao:36, parcMin:150,
    sheetName:'Direcional Conquista Clube Ipiranga',
    /* vendendo apenas Torres 1 e 3 no momento (mesmo criterio do site de produtos) */
    torresVisiveis:[1,3] },

  /* ---------- Campinas ---------- */
  { id:'alta-vista', cod:'782V', nome:'Alta Vista Mangará', cidade:'Campinas',
    inicioObra:'2026-10-01', entrega:'2029-02-28', pctPS:0.15, prazoPadrao:36, parcMin:150,
    sheetName:'Alta Vista Mangará' },
  { id:'cores-da-mata', cod:'781V', nome:'Cores da Mata Mangará', cidade:'Campinas',
    inicioObra:'2025-09-01', entrega:'2028-03-31', pctPS:0.15, prazoPadrao:36, parcMin:150,
    sheetName:'Cores da Mata Mangará',
    sheetNamesExtra:['Compra e Venda de Bens Imóveis III - SP'] },
  { id:'casa-prado', cod:'762V', nome:'Casa Prado Residence Riva', cidade:'Campinas',
    inicioObra:'2026-06-01', entrega:'2028-10-31', pctPS:0.15, prazoPadrao:52, parcMin:150,
    sheetName:'Casa Prado Residencial Riva' },
  { id:'seleto', cod:'618V', nome:'Seleto Amoreiras', cidade:'Campinas',
    inicioObra:'2024-09-01', entrega:'2027-01-31', pctPS:0.15, prazoPadrao:52, parcMin:150,
    sheetName:'Seleto Amoreiras' },

  /* ---------- Sorocaba ---------- */
  { id:'vila-da-mata', cod:'451VC', nome:'Conquista Vila da Mata', cidade:'Sorocaba',
    inicioObra:'2025-07-01', entrega:'2027-05-31', pctPS:0.15, prazoPadrao:52, parcMin:150,
    sheetName:'Conquista Vila da Mata' }
];

window.SIM_EMP_POR_ID = function (id) {
  for (var i = 0; i < window.SIM_EMPS.length; i++) {
    if (window.SIM_EMPS[i].id === id) return window.SIM_EMPS[i];
  }
  return null;
};

/* ============================================================
   UNIDADES DISPONIVEIS
   ============================================================ */
window.SimUnidades = (function () {

  var CACHE_KEY = 'sim-unidades-csv-v1';
  var estado = 'inicial';   /* inicial | carregando | ok | erro */
  var linhas = null;
  var erroMsg = '';
  var ouvintes = [];

  function avisa() {
    for (var i = 0; i < ouvintes.length; i++) ouvintes[i](estado, erroMsg);
  }

  /* ---------- CSV (portado de assets/data.js) ---------- */
  function parseCSV(text) {
    var lines = text.replace(/\r/g, '').trim().split('\n');
    if (lines.length < 2) return null;
    function splitLine(line) {
      var result = [], inQ = false, cur = '';
      for (var i = 0; i < line.length; i++) {
        var ch = line[i];
        if (ch === '"') { inQ = !inQ; }
        else if (ch === ',' && !inQ) { result.push(cur.trim()); cur = ''; }
        else { cur += ch; }
      }
      result.push(cur.trim());
      return result;
    }
    var header = splitLine(lines[0]).map(function (h) { return h.replace(/"/g, '').trim(); });
    var rows = [];
    for (var i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      var cols = splitLine(lines[i]);
      var row = {};
      for (var j = 0; j < header.length; j++) row[header[j]] = (cols[j] || '').replace(/"/g, '').trim();
      rows.push(row);
    }
    return rows;
  }

  function normKey(s) {
    return ('' + (s || '')).toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, ' ').trim();
  }

  /* todos os valores das colunas cujo nome contenha todas as palavras dadas.
     Devolve lista porque ha cabecalhos parecidos - "Produto Direcional: ID" e
     "Produto Direcional: Produto Direcional" casam com os mesmos termos. */
  function cols(row, palavras) {
    var out = [];
    for (var k in row) {
      if (!Object.prototype.hasOwnProperty.call(row, k)) continue;
      var nk = normKey(k), ok = true;
      for (var p = 0; p < palavras.length; p++) {
        if (nk.indexOf(palavras[p]) < 0) { ok = false; break; }
      }
      if (ok) out.push(row[k]);
    }
    return out;
  }
  function col(row, palavras) { return cols(row, palavras)[0] || ''; }

  /* o codigo da unidade (BL02-0804) esta na coluna "Identificador" e tambem
     embutido em "Produto Direcional"; pega o primeiro candidato que casar */
  function codigoUnidade(row) {
    var cands = [col(row, ['identificador'])].concat(cols(row, ['produto', 'direcional']));
    for (var i = 0; i < cands.length; i++) {
      var m = ('' + (cands[i] || '')).match(/BL\d+-\d+/);
      if (m) return m[0];
    }
    return '';
  }

  function parseBR(s) {
    if (!s) return 0;
    s = ('' + s).replace(/"/g, '').trim().replace(/[R$\s]/g, '');
    s = s.replace(/\./g, '').replace(',', '.');
    var v = parseFloat(s);
    return isFinite(v) ? v : 0;
  }

  /* =========================================================
     TITULO E SOL DA UNIDADE
     Mesma classificacao do site de produtos (assets/data.js), usando o
     registro completo do empreendimento em window.CITIES (config.js) -
     tipoRule, tipos (rotulos customizados) e solNascente por torre.
     Sem esse registro (config.js nao carregado, ou emp sem mapeamento),
     cai no fallback generico: só "2Q C/S" a partir do texto da planilha.
     ========================================================= */
  var SIM_ID_TO_CONFIG_ID = {
    gaia: 'village-gaia', park: 'village-park', botanico: 'reserva-direcional-jardim-botanico',
    ipiranga: 'direcional-conquista-clube-ipiranga', 'alta-vista': 'alta-vista-mangara',
    'cores-da-mata': 'cores-da-mata-mangara', 'casa-prado': 'casa-prado-residencial-riva',
    seleto: 'seleto-amoreiras', 'vila-da-mata': 'conquista-vila-da-mata'
  };
  var TIPO_LABEL_PADRAO = {
    '1q': 'Studio 1Q', '2q-meio': '2Q C/S - Meio', '2q-ponta': '2Q C/S - Ponta',
    'terreo-meio': 'Terreo C/S C/ AP - Meio', 'terreo-ponta': 'Terreo C/S C/ AP - Ponta'
  };
  var NASCENTE_FINAIS_PADRAO = [3, 4, 5, 6];

  function configEmpDe(emp) {
    var id = emp && SIM_ID_TO_CONFIG_ID[emp.id];
    if (!id || typeof window.findEmpreendimento !== 'function') return null;
    return window.findEmpreendimento(id);
  }

  function classificaTipo(cfg, tipoPlanta, final, andar, bl) {
    var t = ('' + (tipoPlanta || '')).toLowerCase();
    var regra = cfg && cfg.tipoRule;
    if (regra === 'seleto') {
      var pontaS = [1, 2, 7, 8].indexOf(final) >= 0;
      if (andar === 0) return pontaS ? 'terreo-ponta' : 'terreo-meio';
      return pontaS ? '2q-ponta' : '2q-meio';
    }
    if (regra === 'casa-prado') {
      if (andar === 0) return 'garden-ponta';
      if (andar >= 17) return 'cobertura';
      return ([1, 4].indexOf(final) >= 0) ? 'tipo-meio' : 'tipo-ponta';
    }
    if (regra === 'ipiranga') {
      var pontaI = [3, 4, 9, 10];
      if (andar >= 1) return pontaI.indexOf(final) >= 0 ? 'tipo-ponta' : 'tipo-meio';
      if (pontaI.indexOf(final) >= 0) return 'garden-ponta';
      var adaptado = (bl === 4) ? [1] : [1, 6, 7];
      return adaptado.indexOf(final) >= 0 ? 'garden-meio-adaptado' : 'garden-meio';
    }
    if (regra === 'village-park') {
      if (/pcd/i.test(tipoPlanta || '')) return 'tipo-ponta-pcd';
      if (andar >= 1) {
        if ([2, 3, 6, 7].indexOf(final) >= 0) return 'tipo-ponta';
        if (final === 8) return 'office-tipo-meio';
        return 'tipo-meio';
      }
      if (final === 8) return 'office-garden-meio';
      if ([4, 5].indexOf(final) >= 0) return 'garden-meio';
      return 'garden-ponta';
    }
    if (regra === 'jardim-botanico') {
      if (/pcd/i.test(tipoPlanta || '')) return 'tipo-meio-pcd';
      var pontaB = [2, 3, 6, 7];
      if (andar === 0) {
        if (pontaB.indexOf(final) >= 0) return 'garden-ponta';
        if (final === 8) return 'office-garden-meio';
        return 'garden-meio';
      }
      if (pontaB.indexOf(final) >= 0) return 'tipo-ponta';
      if (bl === 3) return (final === 8) ? 'office-tipo-meio' : 'tipo-meio';
      if (final === 4 || final === 8) return 'office-tipo-meio';
      return 'tipo-meio';
    }
    if (regra === 'village-gaia') {
      var pontaG = [2, 3, 6, 7];
      if (andar === 0) return pontaG.indexOf(final) >= 0 ? 'garden-ponta' : 'garden-meio';
      if (pontaG.indexOf(final) >= 0) return 'tipo-ponta';
      if (final === 8) return (andar <= 5) ? 'office-tipo-meio' : 'tipo-meio';
      return 'tipo-meio';
    }
    /* fallback generico: usa o texto da planilha (Tipo Planta/Area) */
    var pontaFinais = [2, 3, 6, 7];
    var isPonta = pontaFinais.indexOf(final) >= 0;
    if (t.indexOf('1q') >= 0 || t.indexOf('adapt') >= 0 || t.indexOf('studio') >= 0) return '1q';
    if (t.indexOf('terreo') >= 0 || t.indexOf('jardim') >= 0 || t.indexOf('garden') >= 0) {
      return isPonta ? 'terreo-ponta' : 'terreo-meio';
    }
    return isPonta ? '2q-ponta' : '2q-meio';
  }

  function rotuloTipo(cfg, tipo) {
    if (cfg && cfg.tipos) {
      for (var i = 0; i < cfg.tipos.length; i++) if (cfg.tipos[i].key === tipo) return cfg.tipos[i].label;
    }
    return TIPO_LABEL_PADRAO[tipo] || tipo;
  }

  function ehNascente(cfg, bl, final) {
    if (cfg && cfg.solNascente) {
      var lista = cfg.solNascente[bl] || cfg.solNascente['default'] || [];
      return lista.indexOf(final) >= 0;
    }
    return NASCENTE_FINAIS_PADRAO.indexOf(final) >= 0;
  }

  /* ---------- fetch com os mesmos fallbacks do site de produtos ---------- */
  function carregar() {
    if (estado === 'carregando' || estado === 'ok') return;

    try {
      var cache = sessionStorage.getItem(CACHE_KEY);
      if (cache) { linhas = JSON.parse(cache); estado = 'ok'; avisa(); return; }
    } catch (e) { /* sessionStorage indisponivel - segue para a rede */ }

    estado = 'carregando'; erroMsg = ''; avisa();

    var pronto = false;
    function ok(rows) {
      if (pronto) return; pronto = true;
      linhas = rows; estado = 'ok';
      try { sessionStorage.setItem(CACHE_KEY, JSON.stringify(rows)); } catch (e) { /* cota cheia */ }
      avisa();
    }
    function falha(msg) {
      if (pronto) return; pronto = true;
      estado = 'erro'; erroMsg = msg; avisa();
    }
    setTimeout(function () { falha('Tempo esgotado ao buscar a planilha.'); }, 20000);

    function tenta(url, proximo) {
      fetch(url)
        .then(function (r) { if (!r.ok) { proximo(); return; } return r.text(); })
        .then(function (text) {
          if (text === undefined) return;
          if (!text || text.trim().charAt(0) === '<') { proximo(); return; }
          var rows = parseCSV(text);
          if (!rows || !rows.length) { proximo(); return; }
          ok(rows);
        })
        .catch(function () { proximo(); });
    }

    var URL_CSV = window.SIM_SHEET_CSV_URL;
    tenta(URL_CSV, function () {
      tenta('https://corsproxy.io/?' + encodeURIComponent(URL_CSV), function () {
        tenta('https://api.allorigins.win/raw?url=' + encodeURIComponent(URL_CSV), function () {
          falha('Não foi possível acessar a planilha de unidades.');
        });
      });
    });
  }

  /* ---------- agrupamento por empreendimento ---------- */
  /* O bloco vem do proprio codigo da unidade (BL02-0804 -> BL02), e nao da
     coluna "Bloco/Etapa": alem de ser o que o corretor ve na tela, isso ja
     resolve as linhas agregadas (que trazem o cod. do produto no lugar do
     bloco) e descarta sozinho as vagas de garagem (VG-0010, sem prefixo BL). */
  function numBloco(codigo) { return parseInt(codigo.slice(2, codigo.indexOf('-')), 10); }

  /* valor exato da coluna pelo nome (com um fallback tolerante a espacos/caixa);
     os nomes batem com o cabecalho real da planilha, ja conferidos em producao */
  function valorExato(row, nome) {
    if (Object.prototype.hasOwnProperty.call(row, nome)) return row[nome];
    var alvo = nome.toLowerCase();
    for (var k in row) if (k.toLowerCase().trim() === alvo) return row[k];
    return '';
  }

  function porEmpreendimento(emp) {
    var vazio = { blocos: [], unidades: {}, total: 0, detalhes: {} };
    if (!emp || !linhas) return vazio;

    var querem = [normKey(emp.sheetName)];
    if (emp.sheetNamesExtra) {
      for (var e = 0; e < emp.sheetNamesExtra.length; e++) querem.push(normKey(emp.sheetNamesExtra[e]));
    }
    var cfg = configEmpDe(emp);

    var porBloco = {}, detalhes = {}, total = 0;
    for (var i = 0; i < linhas.length; i++) {
      var r = linhas[i];

      if (querem.indexOf(normKey(col(r, ['nome', 'empreendimento']))) < 0) continue;
      if (normKey(col(r, ['status', 'unidade'])) !== 'disponivel') continue;

      var codigo = codigoUnidade(r);
      if (!codigo) continue;                  /* vagas de garagem e afins */

      var n = numBloco(codigo);
      if (emp.torresVisiveis && emp.torresVisiveis.indexOf(n) < 0) continue;

      var chave = codigo.slice(0, codigo.indexOf('-'));   /* BL02 */
      if (!porBloco[chave]) porBloco[chave] = { n: n, lista: [] };
      if (porBloco[chave].lista.indexOf(codigo) < 0) { porBloco[chave].lista.push(codigo); total++; }

      /* valores da unidade - mesmas contas do site de produtos (assets/data.js) */
      var valorFinal  = parseBR(valorExato(r, 'Valor Final Com Kit'));
      var ba          = parseBR(valorExato(r, 'B.A. da Unidade'));
      var folgaCampG  = parseBR(valorExato(r, 'Folga Campanha G'));
      var folgaTabela = parseBR(valorExato(r, 'Folga de Tabela'));
      var avaliacao   = parseBR(valorExato(r, 'Valor de Avaliação Bancária'));
      var areaPriv    = Math.round(parseBR(valorExato(r, 'Área privativa total')));
      var vagasRaw    = valorExato(r, 'Quantidade de vagas');
      var vagas       = (vagasRaw === '' || vagasRaw == null) ? null : Math.round(parseBR(vagasRaw));
      var final       = parseInt(valorExato(r, 'Final unidade') || '0', 10);
      var andar       = parseInt(valorExato(r, 'Andar') || '0', 10);
      var tipoPlanta  = valorExato(r, 'Tipo Planta/Área') || '';

      var tabelaDireta = valorFinal - ba - folgaCampG;
      var associativo  = tabelaDireta - folgaTabela;
      var tipo = classificaTipo(cfg, tipoPlanta, final, andar, n);

      detalhes[codigo] = {
        tipoLabel: rotuloTipo(cfg, tipo),
        sol: ehNascente(cfg, n, final) ? 'Nascente' : 'Poente',
        areaPriv: areaPriv, vagas: vagas, avaliacao: avaliacao,
        tabelaDireta: tabelaDireta, associativo: associativo
      };
    }

    var blocos = Object.keys(porBloco).sort(function (a, b) { return porBloco[a].n - porBloco[b].n; });
    var unidades = {};
    for (var b = 0; b < blocos.length; b++) {
      unidades[blocos[b]] = porBloco[blocos[b]].lista.sort();
    }
    return {
      blocos: blocos.map(function (k) {
        return { id: k, label: 'Torre ' + porBloco[k].n, qtd: porBloco[k].lista.length };
      }),
      unidades: unidades,
      total: total,
      detalhes: detalhes
    };
  }

  return {
    carregar: carregar,
    porEmpreendimento: porEmpreendimento,
    aoMudar: function (fn) { ouvintes.push(fn); fn(estado, erroMsg); },
    estado: function () { return estado; },
    erro: function () { return erroMsg; },
    normKey: normKey
  };
})();

/* ============================================================
   COMBOBOX - lista flutuante com busca
   ------------------------------------------------------------
   var c = SimCombo(el, { placeholder, buscaPlaceholder, onChange });
   c.setOpcoes([{ value, label, grupo, sub }]);
   c.setValor(v)      define sem disparar onChange
   c.getValor()
   c.setDesabilitado(bool, motivo)
   c.setTextoLivre(bool)   vira input comum (fallback quando a planilha falha)
   ============================================================ */
window.SimCombo = function (el, opts) {
  opts = opts || {};
  var opcoes = [], valor = null, aberto = false, marcado = -1, filtradas = [];
  var desabilitado = false, textoLivre = false;

  el.classList.add('cbx');
  el.innerHTML =
    '<button type="button" class="cbx-btn" aria-haspopup="listbox" aria-expanded="false">' +
      '<span class="cbx-val"></span>' +
      '<svg class="cbx-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>' +
    '</button>' +
    '<input type="text" class="cbx-livre" style="display:none">' +
    '<div class="cbx-pop">' +
      '<div class="cbx-busca"><input type="text" autocomplete="off" spellcheck="false"></div>' +
      '<div class="cbx-lista" role="listbox"></div>' +
    '</div>';

  var btn    = el.querySelector('.cbx-btn');
  var rotulo = el.querySelector('.cbx-val');
  var livre  = el.querySelector('.cbx-livre');
  var pop    = el.querySelector('.cbx-pop');
  var busca  = el.querySelector('.cbx-busca input');
  var lista  = el.querySelector('.cbx-lista');

  busca.placeholder = opts.buscaPlaceholder || 'Buscar...';
  livre.placeholder = opts.placeholder || '';

  function achaOpcao(v) {
    for (var i = 0; i < opcoes.length; i++) if (opcoes[i].value === v) return opcoes[i];
    return null;
  }

  function pintaRotulo() {
    var o = achaOpcao(valor);
    rotulo.textContent = o ? o.label : (opts.placeholder || 'Selecione');
    rotulo.classList.toggle('ph', !o);
  }

  function desenhaLista() {
    var termo = window.SimUnidades.normKey(busca.value);
    filtradas = opcoes.filter(function (o) {
      if (!termo) return true;
      return window.SimUnidades.normKey(o.label + ' ' + (o.sub || '') + ' ' + (o.grupo || '')).indexOf(termo) >= 0;
    });

    if (!filtradas.length) {
      lista.innerHTML = '<div class="cbx-vazio">Nada encontrado</div>';
      marcado = -1;
      return;
    }

    var html = '', grupoAtual = null;
    for (var i = 0; i < filtradas.length; i++) {
      var o = filtradas[i];
      if (o.grupo && o.grupo !== grupoAtual) {
        grupoAtual = o.grupo;
        html += '<div class="cbx-grupo">' + o.grupo + '</div>';
      }
      html += '<div class="cbx-opt' + (o.value === valor ? ' sel' : '') + (i === marcado ? ' mk' : '') + '"' +
              ' role="option" data-i="' + i + '">' +
                '<span class="cbx-opt-lab">' + o.label + '</span>' +
                (o.sub ? '<span class="cbx-opt-sub">' + o.sub + '</span>' : '') +
              '</div>';
    }
    lista.innerHTML = html;
  }

  function marca(i) {
    if (!filtradas.length) return;
    marcado = Math.max(0, Math.min(filtradas.length - 1, i));
    var itens = lista.querySelectorAll('.cbx-opt');
    for (var k = 0; k < itens.length; k++) itens[k].classList.toggle('mk', +itens[k].getAttribute('data-i') === marcado);
    var alvo = lista.querySelector('.cbx-opt.mk');
    if (alvo) alvo.scrollIntoView({ block: 'nearest' });
  }

  function abre() {
    if (desabilitado || textoLivre) return;
    aberto = true;
    el.classList.add('open');
    btn.setAttribute('aria-expanded', 'true');
    busca.value = '';
    marcado = -1;
    desenhaLista();
    /* deixa marcado o item ja escolhido, para o teclado comecar dali */
    for (var i = 0; i < filtradas.length; i++) if (filtradas[i].value === valor) { marca(i); break; }
    busca.focus();
  }

  function fecha() {
    aberto = false;
    el.classList.remove('open');
    btn.setAttribute('aria-expanded', 'false');
  }

  function escolhe(i) {
    var o = filtradas[i];
    if (!o) return;
    valor = o.value;
    pintaRotulo();
    fecha();
    btn.focus();
    if (opts.onChange) opts.onChange(valor, o);
  }

  btn.addEventListener('click', function () { aberto ? fecha() : abre(); });
  busca.addEventListener('input', function () { marcado = -1; desenhaLista(); });

  lista.addEventListener('click', function (ev) {
    var o = ev.target.closest('.cbx-opt');
    if (o) escolhe(+o.getAttribute('data-i'));
  });
  lista.addEventListener('mousemove', function (ev) {
    var o = ev.target.closest('.cbx-opt');
    if (o) marca(+o.getAttribute('data-i'));
  });

  busca.addEventListener('keydown', function (ev) {
    if (ev.key === 'ArrowDown')      { ev.preventDefault(); marca(marcado + 1); }
    else if (ev.key === 'ArrowUp')   { ev.preventDefault(); marca(marcado - 1); }
    else if (ev.key === 'Enter')     { ev.preventDefault(); escolhe(marcado < 0 ? 0 : marcado); }
    else if (ev.key === 'Escape')    { ev.preventDefault(); fecha(); btn.focus(); }
  });

  btn.addEventListener('keydown', function (ev) {
    if (ev.key === 'ArrowDown' || ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); abre(); }
  });

  document.addEventListener('click', function (ev) {
    if (aberto && !el.contains(ev.target)) fecha();
  });

  livre.addEventListener('input', function () {
    valor = this.value;
    if (opts.onChange) opts.onChange(valor, null);
  });

  pintaRotulo();

  return {
    setOpcoes: function (novas) {
      opcoes = novas || [];
      if (valor && !achaOpcao(valor)) valor = null;
      pintaRotulo();
      if (aberto) desenhaLista();
    },
    setValor: function (v) {
      valor = v || null;
      pintaRotulo();
      if (textoLivre) livre.value = v || '';
    },
    getValor: function () { return valor; },
    setDesabilitado: function (b, motivo) {
      desabilitado = !!b;
      btn.disabled = !!b;
      livre.disabled = !!b;
      el.classList.toggle('off', !!b);
      if (b) { fecha(); if (motivo) { rotulo.textContent = motivo; rotulo.classList.add('ph'); } }
      else pintaRotulo();
    },
    setTextoLivre: function (b) {
      textoLivre = !!b;
      btn.style.display = b ? 'none' : '';
      livre.style.display = b ? '' : 'none';
      if (b) { fecha(); livre.value = valor || ''; }
    }
  };
};

/* ============================================================
   RICH TEXT (editor Quill) -> jsPDF
   ------------------------------------------------------------
   SimRichPdf.render(doc, html, {
     x, largura, y, topo, fundo, fonte
   }) -> novo y
   ============================================================ */
window.SimRichPdf = (function () {

  var TAM = { h1: 13, h2: 11.5, h3: 10, p: 8.5 };

  function corDe(str) {
    if (!str) return null;
    var m = str.match(/^#?([0-9a-f]{6})$/i);
    if (m) return [parseInt(m[1].slice(0,2),16), parseInt(m[1].slice(2,4),16), parseInt(m[1].slice(4,6),16)];
    m = str.match(/rgba?\((\d+)[,\s]+(\d+)[,\s]+(\d+)/i);
    if (m) return [+m[1], +m[2], +m[3]];
    return null;
  }

  /* junta os trechos de texto de um bloco, cada um com seu estilo */
  function runsDe(no, herda) {
    var runs = [];
    (function anda(n, est) {
      for (var i = 0; i < n.childNodes.length; i++) {
        var f = n.childNodes[i];
        if (f.nodeType === 3) {
          if (f.nodeValue) runs.push({ texto: f.nodeValue, est: est });
        } else if (f.nodeType === 1) {
          var t = f.tagName.toLowerCase();
          if (t === 'br') { runs.push({ quebra: true, est: est }); continue; }
          var novo = {
            bold: est.bold || t === 'strong' || t === 'b',
            italic: est.italic || t === 'em' || t === 'i',
            underline: est.underline || t === 'u',
            strike: est.strike || t === 's',
            cor: corDe(f.style && f.style.color) || est.cor
          };
          anda(f, novo);
        }
      }
    })(no, herda || {});
    return runs;
  }

  function estiloFonte(e) {
    if (e.bold && e.italic) return 'bolditalic';
    if (e.bold) return 'bold';
    if (e.italic) return 'italic';
    return 'normal';
  }

  function render(doc, html, o) {
    o = o || {};
    var x0     = o.x || 18;
    var larg   = o.largura || 174;
    var y      = o.y || 18;
    var topo   = o.topo || 18;
    var fundo  = o.fundo || 282;
    var fonte  = o.fonte || 'helvetica';
    var corPad = o.cor || [114, 122, 125];

    var caixa = document.createElement('div');
    caixa.innerHTML = html || '';

    function novaPagina() { doc.addPage(); y = topo; }
    function cabe(h) { if (y + h > fundo) novaPagina(); }

    var contadorOL = 0;

    function desenhaBloco(el, tag) {
      var tamanho = TAM[tag] || TAM.p;
      var alturaLinha = tamanho * 0.42 + 1.4;
      var indent = 0;
      var marcador = '';

      var cls = el.className || '';
      var mIndent = cls.match(/ql-indent-(\d+)/);
      if (mIndent) indent += (+mIndent[1]) * 5;

      if (tag === 'li') {
        indent += 4;
        /* o Quill 2 poe bullets e numeradas dentro do mesmo <ol> e separa as
           duas pelo data-list; a tag do pai so vale para HTML colado de fora */
        var dl = el.getAttribute('data-list');
        var ordenada = dl ? (dl === 'ordered')
                          : !!(el.parentNode && el.parentNode.tagName.toLowerCase() === 'ol');
        if (ordenada) { contadorOL++; marcador = contadorOL + '.'; }
        else { contadorOL = 0; marcador = '\u2022'; }
      } else {
        contadorOL = 0;
      }

      var alinha = 'left';
      if (cls.indexOf('ql-align-center') >= 0) alinha = 'center';
      else if (cls.indexOf('ql-align-right') >= 0) alinha = 'right';

      /* imagens ficam em bloco proprio */
      var imgs = el.querySelectorAll ? el.querySelectorAll('img') : [];
      for (var im = 0; im < imgs.length; im++) desenhaImagem(imgs[im]);

      /* titulo e negrito por natureza - o Quill nao usa <strong> neles */
      var runs = runsDe(el, tag.charAt(0) === 'h' ? { bold: true } : {});
      var xIni = x0 + indent;
      var largUtil = larg - indent;

      /* quebra manual em linhas, preservando o estilo de cada trecho */
      var linhas = [[]], usado = 0;
      for (var r = 0; r < runs.length; r++) {
        var run = runs[r];
        if (run.quebra) { linhas.push([]); usado = 0; continue; }
        doc.setFont(fonte, estiloFonte(run.est));
        doc.setFontSize(tamanho);
        var partes = run.texto.split(/(\s+)/);
        for (var p = 0; p < partes.length; p++) {
          if (!partes[p]) continue;
          var w = doc.getTextWidth(partes[p]);
          if (usado + w > largUtil && usado > 0) {
            if (/^\s+$/.test(partes[p])) continue;   /* nao inicia linha com espaco */
            linhas.push([]); usado = 0;
          }
          linhas[linhas.length - 1].push({ texto: partes[p], est: run.est, w: w });
          usado += w;
        }
      }

      for (var l = 0; l < linhas.length; l++) {
        var pedacos = linhas[l];
        if (!pedacos.length && linhas.length > 1) { y += alturaLinha; continue; }
        cabe(alturaLinha);

        var total = 0;
        for (var t = 0; t < pedacos.length; t++) total += pedacos[t].w;
        var x = xIni;
        if (alinha === 'center') x = xIni + (largUtil - total) / 2;
        else if (alinha === 'right') x = xIni + largUtil - total;

        if (marcador && l === 0) {
          doc.setFont(fonte, 'normal'); doc.setFontSize(tamanho);
          doc.setTextColor(corPad[0], corPad[1], corPad[2]);
          doc.text(marcador, xIni - 4, y);
        }

        for (var c = 0; c < pedacos.length; c++) {
          var pe = pedacos[c];
          doc.setFont(fonte, estiloFonte(pe.est));
          doc.setFontSize(tamanho);
          var cor = pe.est.cor || (tag.charAt(0) === 'h' ? [58, 64, 67] : corPad);
          doc.setTextColor(cor[0], cor[1], cor[2]);
          doc.text(pe.texto, x, y);
          if (pe.est.underline) doc.line(x, y + 0.7, x + pe.w, y + 0.7);
          if (pe.est.strike)    doc.line(x, y - tamanho * 0.11, x + pe.w, y - tamanho * 0.11);
          x += pe.w;
        }
        y += alturaLinha;
      }
      y += tag.charAt(0) === 'h' ? 1.6 : 0.6;
    }

    function desenhaImagem(img) {
      var src = img.getAttribute('src') || '';
      if (src.indexOf('data:') !== 0) return;    /* so imagens embutidas */
      var w = img.naturalWidth || img.width || 0;
      var h = img.naturalHeight || img.height || 0;
      if (!w || !h) return;

      var lw = Math.min(larg, larg * 0.85);
      var lh = lw * h / w;
      var maxH = fundo - topo;
      if (lh > maxH) { lh = maxH; lw = lh * w / h; }

      cabe(lh + 2);
      var fmt = src.indexOf('image/png') >= 0 ? 'PNG' : 'JPEG';
      try { doc.addImage(src, fmt, x0, y, lw, lh); } catch (e) { return; }
      y += lh + 3;
    }

    var blocos = caixa.children;
    for (var i = 0; i < blocos.length; i++) {
      var b = blocos[i];
      var tag = b.tagName.toLowerCase();
      if (tag === 'ul' || tag === 'ol') {
        contadorOL = 0;
        for (var j = 0; j < b.children.length; j++) desenhaBloco(b.children[j], 'li');
        contadorOL = 0;
      } else if (tag === 'img') {
        desenhaImagem(b);
      } else {
        desenhaBloco(b, TAM[tag] ? tag : 'p');
      }
    }
    return y;
  }

  /* texto puro, para nome de arquivo / checagem de "esta vazio" */
  function texto(html) {
    var d = document.createElement('div');
    d.innerHTML = html || '';
    return (d.textContent || '').replace(/\u00a0/g, ' ').trim();
  }

  return { render: render, texto: texto };
})();

/* ============================================================
   MOTOR DE DADOS - Site Produtos SPI
   Reaproveita a logica do portal original, mas filtrando pela
   coluna "Nome do Empreendimento".
   ============================================================ */

var units = [];              // unidades do empreendimento atual (apos filtro)
var activeFilter = 'todos';
var activeSol = 'todos';
var activeTorre = 'todos';
var activeVaga = 'todos';    // 'todos' | 'com' (vagas > 0) | 'sem' (vagas = 0)
var activePremio = 'com';    // 'com' = Com Premio (padrao) | 'sem' = Sem Premio
var viewMode = 'cards';      // 'cards' (padrao) | 'list'
var NASCENTE_FINAIS = [3, 4, 5, 6];

var AREA_MAP = { '1q':48, '2q-meio':48, '2q-ponta':46, 'terreo-meio':55, 'terreo-ponta':66 };
var TIPO_LABEL = {
  '1q':'Studio 1Q', '2q-meio':'2Q C/S - Meio', '2q-ponta':'2Q C/S - Ponta',
  'terreo-meio':'Terreo C/S C/ AP - Meio', 'terreo-ponta':'Terreo C/S C/ AP - Ponta'
};

/* ---------- helpers ---------- */
function blocoNum(bl) { var m = ('' + (bl || '')).match(/\d+/); return m ? parseInt(m[0], 10) : 1; }
// Nascente pode depender do bloco (via emp.solNascente); senao usa o padrao global
function unitNascente(u) {
  var emp = window.CURRENT_EMP;
  if (emp && emp.solNascente) {
    var list = emp.solNascente[blocoNum(u.bl)] || emp.solNascente['default'] || [];
    return list.indexOf(u.f) >= 0;
  }
  return NASCENTE_FINAIS.indexOf(u.f) >= 0;
}
function getSol(u) { return unitNascente(u) ? 'Nascente' : 'Poente'; }
// Quantidade de vagas (coluna da planilha) so e exibida/filtrada nos produtos de Ribeirao Preto
function showVagasQtd() {
  var emp = window.CURRENT_EMP;
  return !!(emp && emp._cityId === 'ribeirao-preto');
}
var VAGA_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
  '<path d="M5 11l1.6-4.4A2 2 0 0 1 8.5 5h7a2 2 0 0 1 1.9 1.6L19 11"></path>' +
  '<rect x="3" y="11" width="18" height="6" rx="2"></rect>' +
  '<circle cx="7.5" cy="17.5" r="1.4"></circle><circle cx="16.5" cy="17.5" r="1.4"></circle></svg>';
function vagasBadgeHtml(u) {
  if (!showVagasQtd() || u.vagas == null) return '';
  var lbl = u.vagas === 1 ? '1 vaga' : u.vagas + ' vagas';
  return '<span class="u-vagas' + (u.vagas > 0 ? '' : ' none') + '" title="Vagas de garagem">' + VAGA_SVG + lbl + '</span>';
}
function getSolIcon(u) { return unitNascente(u) ? '&#9728;' : '&#9790;'; }
function fmt(v) { return v.toLocaleString('pt-BR', { style:'currency', currency:'BRL', maximumFractionDigits:0 }); }

function parseBR(s) {
  if (!s) return 0;
  s = ('' + s).replace(/"/g, '').trim();
  s = s.replace(/[R$\s]/g, '');
  s = s.replace(/\./g, '').replace(',', '.');
  return parseFloat(s) || 0;
}
function normKey(s) {
  return ('' + (s || '')).toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]/g, '');
}
function wordsOf(s) {
  return ('' + (s || '')).toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .split(/[^a-z0-9]+/).filter(function (w) { return w.length > 0; });
}
function findCol(row, candidates) {
  var normCandidates = candidates.map(normKey);
  for (var key in row) {
    var keyWords = wordsOf(key), all = true;
    for (var i = 0; i < normCandidates.length; i++)
      if (keyWords.indexOf(normCandidates[i]) === -1) { all = false; break; }
    if (all) return row[key];
  }
  for (var key2 in row) {
    var nk = normKey(key2), all2 = true;
    for (var j = 0; j < normCandidates.length; j++)
      if (nk.indexOf(normCandidates[j]) === -1) { all2 = false; break; }
    if (all2) return row[key2];
  }
  return '';
}
// tenta varios grupos de candidatos (OR); dentro do grupo todas as palavras precisam bater (AND)
function findFirst(row, groups) {
  for (var g = 0; g < groups.length; g++) {
    var v = findCol(row, groups[g]);
    if (v !== '' && v != null) return v;
  }
  return '';
}
function parseTipo(tipoPlanta, final) {
  var t = ('' + (tipoPlanta || '')).toLowerCase();
  var pontaFinais = [2, 3, 6, 7];
  var isPonta = pontaFinais.indexOf(parseInt(final, 10)) >= 0;
  if (t.indexOf('1q') >= 0 || t.indexOf('adapt') >= 0 || t.indexOf('studio') >= 0) return '1q';
  if (t.indexOf('terreo') >= 0 || t.indexOf('jardim') >= 0 || t.indexOf('garden') >= 0)
    return isPonta ? 'terreo-ponta' : 'terreo-meio';
  return isPonta ? '2q-ponta' : '2q-meio';
}
// classificacao por empreendimento (Seleto usa finais + andar; demais usam parseTipo)
function classifyTipo(emp, tipoPlanta, final, andar, bl) {
  if (emp && emp.tipoRule === 'seleto') {
    var ponta = [1, 2, 7, 8].indexOf(final) >= 0;
    if (andar === 0) return ponta ? 'terreo-ponta' : 'terreo-meio';
    return ponta ? '2q-ponta' : '2q-meio';
  }
  if (emp && emp.tipoRule === 'casa-prado') {
    if (andar === 0) return 'garden-ponta';           // andar 0 (qualquer final)
    if (andar >= 17) return 'cobertura';              // andar 17 (qualquer final)
    return ([1, 4].indexOf(final) >= 0) ? 'tipo-meio' : 'tipo-ponta'; // andar 1-16
  }
  if (emp && emp.tipoRule === 'ipiranga') {
    var pontaF = [3, 4, 9, 10];
    if (andar >= 1) {                                 // Tipo (andar 1+)
      return pontaF.indexOf(final) >= 0 ? 'tipo-ponta' : 'tipo-meio';
    }
    // andar 0 = Garden
    if (pontaF.indexOf(final) >= 0) return 'garden-ponta';
    // Garden Meio x Adaptado depende da torre (bloco)
    var torre = blocoNum(bl);
    var adaptado = (torre === 4) ? [1] : [1, 6, 7];
    return adaptado.indexOf(final) >= 0 ? 'garden-meio-adaptado' : 'garden-meio';
  }
  if (emp && emp.tipoRule === 'village-park') {
    // PCD e marcado na planilha (coluna Tipo Planta/Area); sao todos Final 7
    if (/pcd/i.test(tipoPlanta || '')) return 'tipo-ponta-pcd';
    if (andar >= 1) {                                 // Tipo (andar 1+)
      if ([2, 3, 6, 7].indexOf(final) >= 0) return 'tipo-ponta';   // 3QCS Tipo Ponta
      if (final === 8) return 'office-tipo-meio';                  // 2QCS Office Tipo Meio
      return 'tipo-meio';                                          // finais 1,4,5
    }
    // andar 0 = Garden
    if (final === 8) return 'office-garden-meio';                  // 1Q Office Garden Meio
    if ([4, 5].indexOf(final) >= 0) return 'garden-meio';          // 2QCS Garden Meio
    return 'garden-ponta';                                         // finais 2,3,6
  }
  if (emp && emp.tipoRule === 'jardim-botanico') {
    // PCD e marcado na planilha (coluna Tipo Planta/Area) e tem prioridade
    if (/pcd/i.test(tipoPlanta || '')) return 'tipo-meio-pcd';
    var pontaB = [2, 3, 6, 7];
    var torreB = blocoNum(bl);
    if (andar === 0) {                                // Garden
      if (pontaB.indexOf(final) >= 0) return 'garden-ponta';   // 2,3,6,7
      if (final === 8) return 'office-garden-meio';            // 1Q Office Garden Meio
      return 'garden-meio';                                    // T1/T2 f5; T3 f4,f5
    }
    // andar >= 1 (Tipo)
    if (pontaB.indexOf(final) >= 0) return 'tipo-ponta';       // 2,3,6,7
    if (torreB === 3) {
      if (final === 8) return 'office-tipo-meio';              // T3 f8
      return 'tipo-meio';                                      // T3 f1,f4,f5
    }
    // Torres 1 e 2
    if (final === 4 || final === 8) return 'office-tipo-meio'; // T1/T2 f4,f8
    return 'tipo-meio';                                        // T1/T2 f1,f5
  }
  if (emp && emp.tipoRule === 'village-gaia') {
    var pontaG = [2, 3, 6, 7];
    if (andar === 0) {                                // Garden
      return pontaG.indexOf(final) >= 0 ? 'garden-ponta' : 'garden-meio';
    }
    // andar >= 1 (Tipo)
    if (pontaG.indexOf(final) >= 0) return 'tipo-ponta';           // 2QCS Tipo Ponta
    if (final === 8) return (andar <= 5) ? 'office-tipo-meio' : 'tipo-meio'; // Office 1-5, Tipo Meio 6+
    return 'tipo-meio';                                            // finais 1,4,5
  }
  return parseTipo(tipoPlanta, final);
}
function tipoLabelFor(emp, tipo) {
  if (emp && emp.tipos) {
    for (var i = 0; i < emp.tipos.length; i++)
      if (emp.tipos[i].key === tipo) return emp.tipos[i].label;
  }
  return TIPO_LABEL[tipo] || tipo;
}

/* ---------- CSV ---------- */
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

/* Converte linhas -> unidades, filtrando pelo empreendimento */
function rowsToUnits(rows, empSheetName) {
  var result = [];
  // nomes aceitos: o do empreendimento + eventuais nomes agregados (sheetNamesExtra)
  var wantNorms = [normKey(empSheetName)];
  var cur = window.CURRENT_EMP;
  if (cur && cur.sheetNamesExtra && normKey(cur.sheetName) === normKey(empSheetName)) {
    for (var e = 0; e < cur.sheetNamesExtra.length; e++) wantNorms.push(normKey(cur.sheetNamesExtra[e]));
  }
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i];

    // filtro por empreendimento (aceita nomes agregados)
    var empVal = findCol(r, wordsOf(window.EMP_COLUMN));
    if (!empVal) empVal = findCol(r, ['nome', 'empreendimento']);
    if (wantNorms.indexOf(normKey(empVal)) < 0) continue;
    var isExtra = normKey(empVal) !== normKey(empSheetName); // veio de um nome agregado

    var produto = findFirst(r, [['produto'], ['direcional']]);
    var apMatch = produto ? produto.match(/BL\d+-(\d+)/) : null;

    var final = parseInt(findFirst(r, [['final'], ['unidade']]) || '0', 10);
    var andar = parseInt(findFirst(r, [['andar']]) || '0', 10);
    var bl    = findFirst(r, [['bloco'], ['etapa'], ['torre']]) || 'BL-01';
    // sobrescreve o bloco das unidades agregadas (informado manualmente no config, por final+andar)
    if (isExtra && cur && cur.blocoOverrides) {
      for (var bo = 0; bo < cur.blocoOverrides.length; bo++) {
        var ov = cur.blocoOverrides[bo];
        if (ov.final === final && ov.andar === andar) { bl = ov.bl; break; }
      }
    }
    var tipoPlanta = findFirst(r, [['tipo', 'planta'], ['tipo'], ['planta']]) || '';

    // vagas de garagem nao entram na listagem de unidades
    if (tipoPlanta.toLowerCase().indexOf('vaga') >= 0) continue;

    // empreendimentos com venda restrita a algumas torres (ex.: Ipiranga vendendo so T1/T3)
    if (window.CURRENT_EMP && window.CURRENT_EMP.torresVisiveis &&
        window.CURRENT_EMP.torresVisiveis.indexOf(blocoNum(bl)) === -1) continue;

    var valorFinal   = parseBR(findFirst(r, [['valor', 'final', 'com', 'kit'], ['valor', 'final', 'kit'], ['valor', 'final']]));
    var ba           = parseBR(findFirst(r, [['ba', 'unidade'], ['b', 'a', 'da', 'unidade'], ['ba'], ['b', 'a']]));
    var folgaCampG   = parseBR(findFirst(r, [['folga', 'campanha', 'g'], ['folga', 'campanha']]));
    var folgaTabela  = parseBR(findFirst(r, [['folga', 'de', 'tabela'], ['folga', 'tabela']]));
    var folgaVoltaCx = parseBR(findFirst(r, [['folga', 'volta', 'caixa'], ['folga', 'volta']]));
    // Bonus Adimplencia (= B.A. da Unidade + Folga Promocional): exclusivo dos
    // empreendimentos de Ribeirao Preto, substitui o "ba" no calculo abaixo
    // (a Folga Promocional ja esta embutida nesse valor, nao e subtraida de novo).
    var isRibeiraoPreto = !!(window.CURRENT_EMP && window.CURRENT_EMP._cityId === 'ribeirao-preto');
    if (isRibeiraoPreto) {
      var bonusAdimplencia = parseBR(findFirst(r, [['bonus', 'adimplencia']]));
      if (bonusAdimplencia > 0) ba = bonusAdimplencia;
    }

    // Valor Tabela Direta = Valor Final Com Kit - B.A. da Unidade (Bonus Adimplencia em RP) - Folga Campanha "G"
    var tabelaDireta = valorFinal - ba - folgaCampG;
    // Valor Associativo/Investidor = Tabela Direta - Folga de Tabela
    var associativo  = tabelaDireta - folgaTabela;

    if (tabelaDireta <= 0) continue;

    var apNum, apStr;
    if (apMatch) { apNum = parseInt(apMatch[1], 10); apStr = apMatch[1]; }
    else { apNum = i; apStr = String(i); }

    var tipo = classifyTipo(window.CURRENT_EMP, tipoPlanta, final, andar, bl);
    var avaliacao = parseBR(findFirst(r, [
      ['valor', 'de', 'avaliacao', 'bancaria'],
      ['valor', 'avaliacao', 'bancaria'],
      ['avaliacao', 'bancaria'],
      ['avaliacao']
    ]));
    // Area privativa direto da planilha ("Area privativa total"), arredondada para inteiro
    var areaPriv = Math.round(parseBR(findFirst(r, [['area', 'privativa', 'total'], ['area', 'privativa']])));
    // Quantidade de vagas: null quando a coluna nao existe na planilha (nao exibe nem filtra)
    var vagasRaw = findFirst(r, [['quantidade', 'de', 'vagas'], ['quantidade', 'vagas'], ['qtd', 'vagas'], ['numero', 'vagas']]);
    var vagas = (vagasRaw === '' || vagasRaw == null) ? null : Math.round(parseBR(vagasRaw));

    result.push({
      ap: apStr, num: apNum, bl: bl, f: final, andar: andar,
      tipo: tipo, tipoLabel: tipoLabelFor(window.CURRENT_EMP, tipo),
      area: areaPriv > 0 ? areaPriv : (AREA_MAP[tipo] || 48),
      tabelaDireta: tabelaDireta, associativo: associativo,
      folgaTabela: folgaTabela, folgaVoltaCx: folgaVoltaCx,
      avaliacao: avaliacao, vagas: vagas
    });
  }
  return result;
}

/* ---------- filtros de UI (dropdowns em linha) ---------- */
function ddSelect(groupSelector, valId, btn) {
  var opts = document.querySelectorAll(groupSelector);
  for (var i = 0; i < opts.length; i++) opts[i].classList.remove('on');
  btn.classList.add('on');
  var val = document.getElementById(valId);
  if (val) val.textContent = btn.querySelector('span').textContent;
  var fdd = btn.closest('.fdd');
  if (fdd) fdd.classList.remove('open');
}
function setFilter(f, btn) {
  activeFilter = f;
  ddSelect('[id^="tipo-opt-"]', 'tipo-val', btn);
  renderUnits();
}
function setSol(sol, btn) {
  activeSol = sol;
  ddSelect('[id^="sol-opt-"]', 'sol-val', btn);
  renderUnits();
}
function setTorre(torre, btn) {
  activeTorre = torre;
  ddSelect('[id^="torre-opt-"]', 'torre-val', btn);
  renderUnits();
}
function setVaga(v, btn) {
  activeVaga = v;
  ddSelect('[id^="vaga-opt-"]', 'vaga-val', btn);
  renderUnits();
}
function setPremio(p, btn) {
  activePremio = p;
  ddSelect('[id^="premio-opt-"]', 'premio-val', btn);
  renderUnits();
}
function setSortOpt(v, btn) {
  var sortEl = document.getElementById('sort');
  if (sortEl) sortEl.value = v;
  ddSelect('[id^="sort-opt-"]', 'sort-val', btn);
  renderUnits();
}
function clearTipo() {
  var opt = document.getElementById('tipo-opt-todos');
  if (opt) setFilter('todos', opt);
}
function clearSol() {
  var opt = document.getElementById('sol-opt-todos');
  if (opt) setSol('todos', opt);
}
function clearPremio() {
  var opt = document.getElementById('premio-opt-com');
  if (opt) setPremio('com', opt);
}
function clearTorre() {
  var opt = document.getElementById('torre-opt-todos');
  if (opt) setTorre('todos', opt);
}
function clearVaga() {
  var opt = document.getElementById('vaga-opt-todos');
  if (opt) setVaga('todos', opt);
}

/* Mostra o dropdown de Premio apenas se ao menos uma unidade tiver
   "Folga Volta ao Caixa" > 0. Reavaliado a cada atualizacao da planilha. */
function updatePremioVisibility() {
  var row = document.getElementById('premio-row');
  if (!row) return;
  var hasPremio = false;
  for (var i = 0; i < units.length; i++) {
    if ((units[i].folgaVoltaCx || 0) > 0) { hasPremio = true; break; }
  }
  row.style.display = hasPremio ? '' : 'none';
  if (!hasPremio) clearPremio();       // filtro oculto: garante o padrao "Com Premio"
}

/* Mostra o dropdown de Vaga apenas se a planilha trouxe a coluna
   "Quantidade de vagas" para as unidades carregadas. */
function updateVagaVisibility() {
  var row = document.getElementById('vaga-row');
  if (!row) return;
  var hasVagas = false;
  for (var i = 0; i < units.length; i++) {
    if (units[i].vagas != null) { hasVagas = true; break; }
  }
  row.style.display = hasVagas ? '' : 'none';
  if (!hasVagas) clearVaga();          // filtro oculto: garante o padrao "Todas"
}

/* "Sem Premio" subtrai a Folga Volta ao Caixa dos valores exibidos */
function premioAdj(u)      { return activePremio === 'sem' ? (u.folgaVoltaCx || 0) : 0; }
function tabelaDiretaOf(u) { return u.tabelaDireta - premioAdj(u); }
function associativoOf(u)  { return u.associativo - premioAdj(u); }

/* ---------- render ---------- */
function renderUnits() {
  var grid = document.getElementById('units-grid');
  var plantaBox = document.getElementById('planta-destaque');
  var sortEl = document.getElementById('sort');
  var sortVal = sortEl ? sortEl.value : 'num-asc';

  if (plantaBox) {
    var allPlantas = document.querySelectorAll('.planta-card');
    for (var p = 0; p < allPlantas.length; p++) allPlantas[p].style.display = 'none';
    plantaBox.style.display = 'none';
    if (activeFilter !== 'todos') {
      for (var pd = 0; pd < allPlantas.length; pd++) {
        if (allPlantas[pd].getAttribute('data-tipo') === activeFilter) {
          allPlantas[pd].style.display = 'block';
          plantaBox.style.display = 'block';
        }
      }
    }
  }

  var list = [];
  for (var i = 0; i < units.length; i++) {
    var u = units[i];
    if (activeFilter !== 'todos' && activeFilter !== u.tipo) continue;
    if (activeSol !== 'todos') {
      var nasc = unitNascente(u);
      if (activeSol === 'nascente' && !nasc) continue;
      if (activeSol === 'poente' && nasc) continue;
    }
    if (activeTorre !== 'todos') {
      if (activeTorre !== String(blocoNum(u.bl))) continue;
    }
    if (activeVaga !== 'todos') {
      if (u.vagas == null) continue;                       // sem dado na planilha
      if (activeVaga === 'com' && u.vagas <= 0) continue;
      if (activeVaga === 'sem' && u.vagas > 0) continue;
    }
    list.push(u);
  }

  list.sort(function (a, b) {
    if (sortVal === 'num-asc') {
      var tA = blocoNum(a.bl), tB = blocoNum(b.bl);   // ordena pela torre (numerico), nao pelo texto do bloco
      if (tA !== tB) return tA - tB;
      if (a.andar !== b.andar) return a.andar - b.andar;
      return a.f - b.f;
    }
    if (sortVal === 'venda-asc')  return tabelaDiretaOf(a) - tabelaDiretaOf(b);
    if (sortVal === 'venda-desc') return tabelaDiretaOf(b) - tabelaDiretaOf(a);
    return 0;
  });

  var cnt = document.getElementById('count-label');
  if (cnt) cnt.textContent = list.length;

  if (!list.length) {
    grid.innerHTML = '<div class="empty"><div class="empty-icon">&#128269;</div><p>Nenhuma unidade para esse filtro. Clique em "Atualizar planilha" para carregar os dados.</p></div>';
    return;
  }

  grid.classList.toggle('list-view', viewMode === 'list');
  var buildUnit = viewMode === 'list' ? unitRowHtml : unitCardHtml;
  var html = '';
  for (var j = 0; j < list.length; j++) html += buildUnit(list[j]);
  grid.innerHTML = html;
}

/* dados comuns exibidos tanto no card quanto na linha da lista */
function unitDisplayData(u) {
  var hideSol = window.CURRENT_EMP && window.CURRENT_EMP.hideSol;
  var andarLabel = u.andar === 0 ? 'Terreo' : u.andar + '<sup>o</sup> andar';
  var sol = getSol(u), solIcon = getSolIcon(u);
  var solColor = (sol === 'Nascente') ? '#C9771A' : '#5A7FA8';
  var solBg = (sol === 'Nascente') ? '#FFF5E6' : '#EBF2FA';
  var solBorder = (sol === 'Nascente') ? '#F5DFB8' : '#C5D8EE';
  return {
    hideSol: hideSol, andarLabel: andarLabel, sol: sol, solIcon: solIcon,
    solColor: solColor, solBg: solBg, solBorder: solBorder,
    vagasBadge: vagasBadgeHtml(u),
    vTabela: tabelaDiretaOf(u), vAssoc: associativoOf(u)
  };
}

function unitCardHtml(u) {
  var d = unitDisplayData(u);
  var html = '<div class="u-card">';
  html += '<div class="u-top"><div class="u-top-info">';
  html += '<div class="u-tipo">' + u.tipoLabel + '</div>';
  html += '<div class="u-ap">' + u.bl + ' &middot; ' + d.andarLabel + ' &middot; Final ' + u.f + '</div>';
  html += '</div><div class="u-top-tags"><span class="u-badge-disp">Disponivel</span>' + d.vagasBadge + '</div></div>';
  html += '<hr class="u-hr">';
  html += '<div class="u-price-row">';
  html += '<div><div class="u-price-lbl">Valor Tabela Direta</div><div class="u-price">' + fmt(d.vTabela) + '</div></div>';
  if (u.avaliacao && u.avaliacao > 0)
    html += '<div class="u-avaliacao"><div class="u-price-lbl">Valor de Avaliacao</div><div class="u-price u-price-sm">' + fmt(u.avaliacao) + '</div></div>';
  html += '</div>';
  html += '<div class="u-meta">';
  html += '<div class="u-meta-box"' + (d.hideSol ? ' style="grid-column:1/-1"' : '') + '><div class="u-meta-k">Area privativa</div><div class="u-meta-v">' + u.area + ' m&sup2;</div></div>';
  if (!d.hideSol) {
    html += '<div class="u-meta-box" style="background:' + d.solBg + ';border:1px solid ' + d.solBorder + '">';
    html += '<div class="u-meta-k" style="color:' + d.solColor + '">Sol</div>';
    html += '<div class="u-meta-v" style="color:' + d.solColor + '">' + d.solIcon + ' ' + d.sol + '</div></div>';
  }
  html += '</div>';
  html += '<div class="u-desc"><span class="u-desc-lbl">Valor Associativo/Investidor</span><span class="u-desc-val">' + fmt(d.vAssoc) + ' (Desconto de ' + fmt(u.folgaTabela) + ')</span></div>';
  html += '</div>';
  return html;
}

function unitRowHtml(u) {
  var d = unitDisplayData(u);
  var html = '<div class="u-row">';
  html += '<div class="u-row-id">';
  html += '<span class="u-badge-disp">Disponivel</span>';
  html += '<div class="u-row-tipo-line"><div class="u-tipo">' + u.tipoLabel + '</div>' + d.vagasBadge + '</div>';
  html += '<div class="u-ap">' + u.bl + ' &middot; ' + d.andarLabel + ' &middot; Final ' + u.f + '</div>';
  html += '</div>';
  html += '<div class="u-row-stats">';
  html += '<div class="u-row-stat"><div class="u-price-lbl">Valor Tabela Direta</div><div class="u-price">' + fmt(d.vTabela) + '</div></div>';
  if (u.avaliacao && u.avaliacao > 0)
    html += '<div class="u-row-stat"><div class="u-price-lbl">Valor de Avaliacao</div><div class="u-price u-price-sm">' + fmt(u.avaliacao) + '</div></div>';
  html += '<div class="u-row-stat"><div class="u-meta-k">Area privativa</div><div class="u-meta-v">' + u.area + ' m&sup2;</div></div>';
  if (!d.hideSol) {
    html += '<div class="u-row-stat"><div class="u-meta-k" style="color:' + d.solColor + '">Sol</div><div class="u-meta-v" style="color:' + d.solColor + '">' + d.solIcon + ' ' + d.sol + '</div></div>';
  }
  html += '</div>';
  html += '<div class="u-row-desc"><span class="u-desc-lbl">Valor Associativo/Investidor</span><span class="u-desc-val">' + fmt(d.vAssoc) + '</span><span class="u-desc-off">(Desconto de ' + fmt(u.folgaTabela) + ')</span></div>';
  html += '<div class="u-row-chevron" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg></div>';
  html += '</div>';
  return html;
}

function setView(mode, btn) {
  viewMode = mode;
  document.querySelectorAll('.view-btn').forEach(function (b) { b.classList.remove('on'); });
  btn.classList.add('on');
  renderUnits();
}

/* ---------- tabs + zoom ---------- */
function switchTab(id, btn) {
  var secs = document.querySelectorAll('.section');
  for (var i = 0; i < secs.length; i++) secs[i].classList.remove('active');
  var tabs = document.querySelectorAll('.nav-tab');
  for (var k = 0; k < tabs.length; k++) tabs[k].classList.remove('active');
  document.getElementById('tab-' + id).classList.add('active');
  btn.classList.add('active');
}
function initZoom() {
  var zoomables = document.querySelectorAll('.zoom-box');
  for (var i = 0; i < zoomables.length; i++) (function (box) {
    var img = box.querySelector('.zoom-img');
    if (!img) return;
    box.addEventListener('mousemove', function (e) {
      var rect = box.getBoundingClientRect();
      var xPct = ((e.clientX - rect.left) / rect.width) * 100;
      var yPct = ((e.clientY - rect.top) / rect.height) * 100;
      img.style.transformOrigin = xPct + '% ' + yPct + '%';
    });
  })(zoomables[i]);
}

/* ---------- fetch da planilha ---------- */
function doUpdate() {
  var btn    = document.getElementById('btn-update');
  var status = document.getElementById('update-status');
  var emp = window.CURRENT_EMP;
  btn.disabled = true; btn.classList.add('loading');
  status.className = 'update-status';
  status.textContent = 'Buscando dados...';
  var luEl2 = document.getElementById('last-update'); if (luEl2) luEl2.textContent = '';

  var finished = false;
  function finish(ok, msg) {
    if (finished) return; finished = true;
    status.className = ok ? 'update-status ok' : 'update-status err';
    status.textContent = ok ? msg : ('Erro: ' + msg);
    btn.disabled = false; btn.classList.remove('loading');
  }
  setTimeout(function () {
    if (!finished) finish(false, 'Tempo esgotado. Verifique a conexão ou o link da planilha.');
  }, 15000);

  function processCSV(text) {
    var rows = parseCSV(text);
    if (!rows || rows.length === 0) { finish(false, 'Planilha vazia ou formato inesperado.'); return; }
    var newUnits = rowsToUnits(rows, emp.sheetName);
    if (newUnits.length === 0) {
      var sampleHeaders = rows.length ? Object.keys(rows[0]).join(' | ') : 'nenhum';
      finish(false, '0 unidades para "' + emp.sheetName + '" (de ' + rows.length + ' linhas). Colunas: ' + sampleHeaders);
      return;
    }
    units = newUnits;
    updatePremioVisibility();
    updateVagaVisibility();
    renderUnits();
    var now = new Date();
    var hm = now.getHours() + ':' + (now.getMinutes() < 10 ? '0' : '') + now.getMinutes();
    var luEl = document.getElementById('last-update'); if (luEl) luEl.textContent = 'Atualizado as ' + hm;
    finish(true, newUnits.length + ' unidades carregadas');
  }
  function tryUrl(url, nextFn) {
    fetch(url)
      .then(function (r) { if (!r.ok) { nextFn(); return; } return r.text(); })
      .then(function (text) {
        if (text === undefined) return;
        if (!text || text.trim().charAt(0) === '<') { nextFn(); return; }
        processCSV(text);
      })
      .catch(function () { nextFn(); });
  }
  var CSV_URL = window.SHEET_CSV_URL;
  tryUrl(CSV_URL, function () {
    tryUrl('https://corsproxy.io/?' + encodeURIComponent(CSV_URL), function () {
      tryUrl('https://api.allorigins.win/raw?url=' + encodeURIComponent(CSV_URL), function () {
        finish(false, 'Não foi possível acessar a planilha após 3 tentativas.');
      });
    });
  });
}

/* ============================================================
   MOTOR DE DADOS - Site Produtos SPI
   Reaproveita a logica do portal original, mas filtrando pela
   coluna "Nome do Empreendimento".
   ============================================================ */

var units = [];              // unidades do empreendimento atual (apos filtro)
var activeFilter = 'todos';
var activeSol = 'todos';
var activeTorre = 'todos';
var activePremio = 'com';    // 'com' = Com Premio (padrao) | 'sem' = Sem Premio
var NASCENTE_FINAIS = [3, 4, 5, 6];

var AREA_MAP = { '1q':48, '2q-meio':48, '2q-ponta':46, 'terreo-meio':55, 'terreo-ponta':66 };
var TIPO_LABEL = {
  '1q':'Studio 1Q', '2q-meio':'2Q C/S - Meio', '2q-ponta':'2Q C/S - Ponta',
  'terreo-meio':'Terreo C/S C/ AP - Meio', 'terreo-ponta':'Terreo C/S C/ AP - Ponta'
};

/* ---------- helpers ---------- */
function getSol(f) { return (NASCENTE_FINAIS.indexOf(f) >= 0) ? 'Nascente' : 'Poente'; }
function getSolIcon(f) { return (NASCENTE_FINAIS.indexOf(f) >= 0) ? '&#9728;' : '&#9790;'; }
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
  var wantNorm = normKey(empSheetName);
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i];

    // filtro por empreendimento
    var empVal = findCol(r, wordsOf(window.EMP_COLUMN));
    if (!empVal) empVal = findCol(r, ['nome', 'empreendimento']);
    if (normKey(empVal) !== wantNorm) continue;

    var produto = findFirst(r, [['produto'], ['direcional']]);
    var apMatch = produto ? produto.match(/BL\d+-(\d+)/) : null;

    var final = parseInt(findFirst(r, [['final'], ['unidade']]) || '0', 10);
    var andar = parseInt(findFirst(r, [['andar']]) || '0', 10);
    var bl    = findFirst(r, [['bloco'], ['etapa'], ['torre']]) || 'BL-01';
    var tipoPlanta = findFirst(r, [['tipo', 'planta'], ['tipo'], ['planta']]) || '';

    // vagas de garagem nao entram na listagem de unidades
    if (tipoPlanta.toLowerCase().indexOf('vaga') >= 0) continue;

    var valorFinal   = parseBR(findFirst(r, [['valor', 'final', 'com', 'kit'], ['valor', 'final', 'kit'], ['valor', 'final']]));
    var ba           = parseBR(findFirst(r, [['ba', 'unidade'], ['b', 'a', 'da', 'unidade'], ['ba'], ['b', 'a']]));
    var folgaCampG   = parseBR(findFirst(r, [['folga', 'campanha', 'g'], ['folga', 'campanha']]));
    var folgaTabela  = parseBR(findFirst(r, [['folga', 'de', 'tabela'], ['folga', 'tabela']]));
    var folgaVoltaCx = parseBR(findFirst(r, [['folga', 'volta', 'caixa'], ['folga', 'volta']]));

    // Valor Tabela Direta = Valor Final Com Kit - B.A. da Unidade - Folga Campanha "G"
    var tabelaDireta = valorFinal - ba - folgaCampG;
    // Valor Associativo/Investidor = Tabela Direta - Folga de Tabela
    var associativo  = tabelaDireta - folgaTabela;

    if (tabelaDireta <= 0) continue;

    var apNum, apStr;
    if (apMatch) { apNum = parseInt(apMatch[1], 10); apStr = apMatch[1]; }
    else { apNum = i; apStr = String(i); }

    var tipo = parseTipo(tipoPlanta, final);
    var avaliacao = parseBR(findFirst(r, [
      ['valor', 'de', 'avaliacao', 'bancaria'],
      ['valor', 'avaliacao', 'bancaria'],
      ['avaliacao', 'bancaria'],
      ['avaliacao']
    ]));

    result.push({
      ap: apStr, num: apNum, bl: bl, f: final, andar: andar,
      tipo: tipo, tipoLabel: TIPO_LABEL[tipo] || tipo,
      area: AREA_MAP[tipo] || 48,
      tabelaDireta: tabelaDireta, associativo: associativo,
      folgaTabela: folgaTabela, folgaVoltaCx: folgaVoltaCx,
      avaliacao: avaliacao
    });
  }
  return result;
}

/* ---------- filtros de UI ---------- */
function setFilter(f, btn) {
  activeFilter = f;
  var excludeIds = ['sol-btn-todos','sol-btn-nascente','sol-btn-poente','torre-btn-todos','torre-btn-1','torre-btn-2'];
  var btns = document.querySelectorAll('#tab-unidades .filter-row:first-child .fbtn');
  for (var i = 0; i < btns.length; i++)
    if (excludeIds.indexOf(btns[i].id) === -1) btns[i].classList.remove('on');
  btn.classList.add('on');
  renderUnits();
}
function setSol(sol, btn) {
  activeSol = sol;
  ['sol-btn-todos','sol-btn-nascente','sol-btn-poente'].forEach(function (id) {
    var el = document.getElementById(id); if (el) el.classList.remove('on');
  });
  btn.classList.add('on');
  renderUnits();
}
function setTorre(torre, btn) {
  activeTorre = torre;
  ['torre-btn-todos','torre-btn-1','torre-btn-2'].forEach(function (id) {
    var el = document.getElementById(id); if (el) el.classList.remove('on');
  });
  btn.classList.add('on');
  renderUnits();
}
function setPremio(p, btn) {
  activePremio = p;
  ['premio-btn-com','premio-btn-sem'].forEach(function (id) {
    var el = document.getElementById(id); if (el) el.classList.remove('on');
  });
  btn.classList.add('on');
  renderUnits();
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
      var isNascente = NASCENTE_FINAIS.indexOf(u.f) >= 0;
      if (activeSol === 'nascente' && !isNascente) continue;
      if (activeSol === 'poente' && isNascente) continue;
    }
    if (activeTorre !== 'todos') {
      var blStr = (u.bl || '').toString();
      var torreNum = blStr.match(/2/) ? '2' : '1';
      if (activeTorre !== torreNum) continue;
    }
    list.push(u);
  }

  list.sort(function (a, b) {
    if (sortVal === 'num-asc') {
      var blA = (a.bl || '').toString(), blB = (b.bl || '').toString();
      if (blA !== blB) return blA < blB ? -1 : 1;
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

  var html = '';
  for (var j = 0; j < list.length; j++) {
    var u = list[j];
    var andarLabel = u.andar === 0 ? 'Terreo' : u.andar + '<sup>o</sup> andar';
    var sol = getSol(u.f), solIcon = getSolIcon(u.f);
    var solColor = (sol === 'Nascente') ? '#C9771A' : '#5A7FA8';
    var solBg = (sol === 'Nascente') ? '#FFF5E6' : '#EBF2FA';
    var solBorder = (sol === 'Nascente') ? '#F5DFB8' : '#C5D8EE';
    var vTabela = tabelaDiretaOf(u);
    var vAssoc  = associativoOf(u);
    html += '<div class="u-card">';
    html += '<div class="u-top"><div class="u-top-info">';
    html += '<div class="u-tipo">' + u.tipoLabel + '</div>';
    html += '<div class="u-ap">' + u.bl + ' &middot; ' + andarLabel + ' &middot; Final ' + u.f + '</div>';
    html += '</div><span class="u-badge-disp">Disponivel</span></div>';
    html += '<hr class="u-hr">';
    html += '<div class="u-price-row">';
    html += '<div><div class="u-price-lbl">Valor Tabela Direta</div><div class="u-price">' + fmt(vTabela) + '</div></div>';
    if (u.avaliacao && u.avaliacao > 0)
      html += '<div class="u-avaliacao"><div class="u-price-lbl">Valor de Avaliacao</div><div class="u-price u-price-sm">' + fmt(u.avaliacao) + '</div></div>';
    html += '</div>';
    html += '<div class="u-meta">';
    html += '<div class="u-meta-box"><div class="u-meta-k">Area privativa</div><div class="u-meta-v">' + u.area + ' m&sup2;</div></div>';
    html += '<div class="u-meta-box" style="background:' + solBg + ';border:1px solid ' + solBorder + '">';
    html += '<div class="u-meta-k" style="color:' + solColor + '">Sol</div>';
    html += '<div class="u-meta-v" style="color:' + solColor + '">' + solIcon + ' ' + sol + '</div></div>';
    html += '</div>';
    html += '<div class="u-desc"><span class="u-desc-lbl">Valor Associativo/Investidor</span><span class="u-desc-val">' + fmt(vAssoc) + ' (Desconto de ' + fmt(u.folgaTabela) + ')</span></div>';
    html += '</div>';
  }
  grid.innerHTML = html;
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

/* ============================================================
   MATCH DE UNIDADES - tela
   Formulario -> SimUnidades (estoque ao vivo) -> Match.buscar
   -> lista por empreendimento -> associativo / PDF.
   ============================================================ */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var EMPS = window.SIM_EMPS;
  var POLITICAS = window.MatchProSoluto.POLITICAS;
  var ultimo = null;          /* { cliente, hoje, resultado } */
  var marcadas = {};          /* codigo|empId -> linha */

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function brl(n) {
    return (isFinite(n) ? n : 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
  function pct(f) { return ((f || 0) * 100).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'; }
  function hoje() { var d = new Date(); return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }

  /* ---------- formulario ---------- */
  function cidades() {
    var vistas = [];
    EMPS.forEach(function (e) { if (vistas.indexOf(e.cidade) < 0) vistas.push(e.cidade); });
    return vistas;
  }
  function preencheCidades() {
    $('f-cidade').innerHTML = cidades().map(function (c) { return '<option>' + esc(c) + '</option>'; }).join('');
    preencheEmps();
  }
  function preencheEmps() {
    var c = $('f-cidade').value;
    $('f-emp').innerHTML = '<option value="">Todos</option>' + EMPS.filter(function (e) { return e.cidade === c; })
      .map(function (e) { return '<option value="' + esc(e.id) + '">' + esc(e.nome) + '</option>'; }).join('');
  }
  function preenchePoliticas() {
    $('f-pol').innerHTML = window.Match.ORDEM_POLITICAS.map(function (id) {
      var p = window.MatchProSoluto.politicaPorId(id);
      return '<option value="' + id + '"' + (id === 'aco' ? ' selected' : '') + '>' + esc(p.nome) + '</option>';
    }).join('');
  }
  function lerCliente() {
    var nasc = $('f-nasc').value ? new Date($('f-nasc').value + 'T00:00:00') : null;
    return {
      renda: window.Match.numero($('f-renda').value),
      nascimento: nasc,
      fgts: document.querySelector('input[name=fgts]:checked').value === 'S',
      possuiImovel: document.querySelector('input[name=imovel]:checked').value === 'S'
    };
  }
  function erro(msg) { var el = $('mt-erro'); el.textContent = msg || ''; el.hidden = !msg; }

  /* ---------- estoque ---------- */
  function estoque(cidade) {
    return EMPS.filter(function (e) { return e.cidade === cidade; }).map(function (emp) {
      var u = window.SimUnidades.porEmpreendimento(emp), unidades = [];
      u.blocos.forEach(function (b) {
        (u.unidades[b.id] || []).forEach(function (cod) {
          var d = u.detalhes[cod] || {};
          unidades.push({ codigo: cod, torre: parseInt(b.id.replace(/\D/g, ''), 10), tipoLabel: d.tipoLabel,
            areaPriv: d.areaPriv, avaliacao: d.avaliacao, associativo: d.associativo });
        });
      });
      return { emp: emp, unidades: unidades };
    });
  }

  /* ---------- busca ---------- */
  function buscar(politicaId) {
    var cliente = lerCliente(), cidade = $('f-cidade').value, h = hoje();
    var msg = window.Match.validarCliente(cliente, cidade, h);
    erro(msg);
    if (msg) { $('mt-resultado').hidden = true; return; }
    if (politicaId) $('f-pol').value = politicaId;

    var est = window.SimUnidades.estado();
    if (est !== 'ok') {
      status(est === 'erro' ? 'erro' : 'carregando');
      pendente = true;
      return;
    }
    var resultado = window.Match.buscar({ cliente: cliente, cidade: cidade, empId: $('f-emp').value,
      politicaId: $('f-pol').value, hoje: h, estoque: estoque(cidade) });
    ultimo = { cliente: cliente, hoje: h, resultado: resultado };
    marcadas = {};
    render(window.Match.resumoCliente(cliente, cidade, h), resultado);
  }

  var pendente = false;
  function status(est) {
    var el = $('mt-status');
    if (est === 'carregando') { el.innerHTML = '<strong>Buscando as unidades disponíveis...</strong>'; el.hidden = false; }
    else if (est === 'erro') {
      el.innerHTML = '<strong>Não foi possível carregar as unidades.</strong> ' + esc(window.SimUnidades.erro()) +
        ' <button type="button" class="mt-btn mt-btn-sec" id="mt-retry">Tentar novamente</button>';
      el.hidden = false;
      $('mt-retry').onclick = function () { location.reload(); };
    } else { el.hidden = true; }
  }

  /* ---------- resultado ---------- */
  function render(resumo, r) {
    $('mt-resumo').innerHTML =
      '<div><span>Enquadramento</span><b>' + esc(resumo.faixa) + '</b></div>' +
      '<div><span>Juros CAIXA</span><b>' + resumo.jurosNominal.toLocaleString('pt-BR') + '% a.a.</b></div>' +
      '<div><span>Prazo CAIXA</span><b>' + resumo.prazo + ' meses</b></div>' +
      '<div><span>Financiamento até</span><b>' + brl(resumo.financiamentoMax) + '</b></div>' +
      '<div><span>Subsídio estimado</span><b>' + brl(resumo.subsidio) + '</b></div>';

    var pol = window.MatchProSoluto.politicaPorId($('f-pol').value).nome;
    $('mt-contagem').textContent = r.total === 1 ? '1 unidade cabe na política ' + pol
                                                 : r.total + ' unidades cabem na política ' + pol;
    var html = '';
    if (!r.total) {
      html = '<p class="notice"><strong>Nenhuma unidade cabe na política ' + esc(pol) + '.</strong> ' +
        (r.sugestao ? (r.sugestao.qtd + (r.sugestao.qtd === 1 ? ' unidade cabe' : ' unidades cabem') +
          ' na política ' + esc(r.sugestao.nome) + '. <button type="button" class="mt-btn mt-btn-sec" id="mt-sug">Ver na política ' +
          esc(r.sugestao.nome) + '</button>') : 'Nenhuma política aprova as unidades desse recorte.') + '</p>';
    }
    r.grupos.forEach(function (g) {
      html += '<section class="mt-grupo"><h2>' + esc(g.emp.nome) + ' <small>· ' + g.linhas.length + '</small></h2>';
      g.linhas.forEach(function (l) {
        var chave = l.empId + '|' + l.codigo;
        html += '<article class="mt-un">' +
          '<input type="checkbox" data-k="' + esc(chave) + '" aria-label="Incluir ' + esc(l.codigo) + ' no PDF">' +
          '<div><div class="mt-un-cod">' + esc(l.codigo) + '</div>' +
          '<div class="mt-un-sub">Torre ' + l.torre + ' · ' + l.andar + 'º andar · final ' + l.final + ' · ' +
          esc(l.tipoLabel || '') + (l.areaPriv ? ' · ' + l.areaPriv + ' m²' : '') + '</div>' +
          (l.travaF3 ? '<div class="mt-selo">Simulada na Faixa 3: valor travado em R$ 400 mil no PCV</div>' : '') +
          '</div>' +
          '<a href="' + esc(window.Match.urlAssociativo(l, ultimo.cliente, ultimo.hoje)) + '">Abrir no associativo →</a>' +
          '<div class="mt-un-nums">' +
          '<div><span>Valor</span><b>' + brl(l.venda) + '</b></div>' +
          '<div><span>Financiamento</span><b>' + brl(l.financiamento) + '</b></div>' +
          '<div><span>Subsídio</span><b>' + brl(l.subsidio) + '</b></div>' +
          '<div><span>Ato</span><b>' + brl(l.ato) + '</b></div>' +
          '<div><span>Pro Soluto (' + l.carne + ')</span><b>' + brl(l.parcelaPS) + ' × ' + l.prazoPS + '</b></div>' +
          '<div><span>Parcela CAIXA' + (l.faixa === 'SBPE' ? ' (SBPE)' : '') + '</span><b>' + brl(l.parcelaFin) + '</b></div>' +
          '<div><span>Comprometimento</span><b>' + pct(l.crTotal) + '</b></div>' +
          '</div></article>';
      });
      html += '</section>';
    });
    $('mt-grupos').innerHTML = html;

    var d = r.descartadas, partes = [];
    if (d.semAvaliacao) partes.push(d.semAvaliacao + ' sem valor de avaliação na planilha');
    if (d.foraEnquadramento) partes.push(d.foraEnquadramento + ' fora do enquadramento da renda');
    $('mt-rodape').textContent = partes.length ? 'Ficaram de fora: ' + partes.join(' · ') + '.' : '';

    $('mt-resultado').hidden = false;
    atualizaPdf();
    if ($('mt-sug')) $('mt-sug').onclick = function () { buscar(r.sugestao.politicaId); };
  }

  function linhaPorChave(k) {
    var achada = null;
    ultimo.resultado.grupos.forEach(function (g) {
      g.linhas.forEach(function (l) { if (l.empId + '|' + l.codigo === k) achada = l; });
    });
    return achada;
  }
  function atualizaPdf() {
    var n = Object.keys(marcadas).length;
    $('mt-pdf').textContent = 'Gerar PDF (' + n + ')';
    $('mt-pdf').disabled = !n;
  }

  /* ---------- PDF (spec secao 7) ---------- */
  function gerarPdf() {
    if (!window.jspdf || !window.jspdf.jsPDF) { alert('A biblioteca de PDF ainda está carregando. Tente de novo em alguns segundos.'); return; }
    var nome = prompt('Nome do cliente (opcional):', '') || '';
    var doc = new window.jspdf.jsPDF({ unit: 'mm', format: 'a4' });
    var W = doc.internal.pageSize.getWidth(), M = 14;
    doc.setFont('helvetica', 'bold'); doc.setFontSize(15); doc.setTextColor(228, 3, 43);
    doc.text('Grupo Direcional', M, 18);
    doc.setFontSize(11); doc.setTextColor(58, 64, 67);
    doc.text('Unidades sugeridas' + (nome ? ' para ' + nome : ''), M, 26);
    doc.setFont('helvetica', 'normal'); doc.setFontSize(8.5); doc.setTextColor(106, 114, 117);
    doc.text('Gerado em ' + hoje().toLocaleDateString('pt-BR'), M, 31);

    var linhas = Object.keys(marcadas).map(function (k) { return window.Match.linhaPdf(marcadas[k]); });
    doc.autoTable({
      startY: 36, margin: { left: M, right: M },
      head: [['Empreendimento / unidade', 'Valor', 'Financiamento', 'Subsídio', 'Ato', 'Pro Soluto', 'Parcela CAIXA']],
      body: linhas.map(function (l) {
        return [l.empNome + '\n' + l.codigo + ' · ' + (l.tipoLabel || '') + (l.areaPriv ? ' · ' + l.areaPriv + ' m²' : ''),
          brl(l.venda), brl(l.financiamento), brl(l.subsidio), brl(l.ato),
          brl(l.parcelaPS) + ' × ' + l.prazoPS + (l.carne === 'escalonado' ? '\n(escalonado)' : ''), brl(l.parcelaFin)];
      }),
      styles: { fontSize: 7.5, cellPadding: 1.8, textColor: [58, 64, 67] },
      headStyles: { fillColor: [228, 3, 43], textColor: 255 },
      /* valores em uma linha so: a coluna da unidade absorve a quebra */
      columnStyles: { 0: { cellWidth: 44 }, 1: { halign: 'right' }, 2: { halign: 'right' }, 3: { halign: 'right' },
                      4: { halign: 'right' }, 5: { halign: 'right' }, 6: { halign: 'right' } }
    });
    var total = doc.internal.getNumberOfPages();
    for (var p = 1; p <= total; p++) {
      doc.setPage(p);
      var H = doc.internal.pageSize.getHeight();
      doc.setFontSize(7); doc.setTextColor(114, 122, 125);
      doc.text('Simulação aproximada, sujeita à análise de crédito da CAIXA e à aprovação da Direcional.', M, H - 8);
      doc.text('Página ' + p + ' de ' + total, W - M, H - 8, { align: 'right' });
    }
    doc.save('unidades-' + (nome ? nome.replace(/\s+/g, '-').toLowerCase() : 'cliente') + '.pdf');
  }

  /* ---------- eventos ---------- */
  $('f-cidade').addEventListener('change', preencheEmps);
  $('f-renda').addEventListener('blur', function () {
    var v = window.Match.numero(this.value); this.value = v ? brl(v) : '';
  });
  $('mt-form').addEventListener('submit', function (ev) { ev.preventDefault(); buscar(); });
  $('mt-grupos').addEventListener('change', function (ev) {
    var k = ev.target.getAttribute && ev.target.getAttribute('data-k');
    if (!k) return;
    if (ev.target.checked) marcadas[k] = linhaPorChave(k); else delete marcadas[k];
    atualizaPdf();
  });
  $('mt-pdf').addEventListener('click', gerarPdf);

  preencheCidades();
  preenchePoliticas();
  window.SimUnidades.aoMudar(function (est) {
    if (est === 'ok') { status('ok'); if (pendente) { pendente = false; buscar(); } }
    else if (est === 'erro' && pendente) status('erro');
  });
  window.SimUnidades.carregar();
})();

/* ============================================================
   SIMULADOR DE FINANCIAMENTO - desenho do PDF (A4, uma folha)
   ------------------------------------------------------------
   Recebe as linhas prontas de Financiamento.dadosPdf() e desenha
   com jsPDF + autotable (carregados por CDN nas paginas).
   Layout: quadro "PDF da simulacao" do canvas
   (docs/design/simulador-financiamento/fonte/PDF.dc.html).
   ============================================================ */
window.FinanciamentoPdf = (function () {
  'use strict';

  var VERMELHO = [228, 3, 43], VERDE = [30, 142, 74], GRAFITE = [58, 64, 67], TITULO = [43, 48, 51],
      CINZA = [92, 100, 103], LINHA = [231, 233, 234], FUNDO = [250, 251, 251], AZUL = [37, 99, 168];
  var logo = null;

  /* logo transparente em PNG, carregado uma vez (mesma ideia do PDF do associativo) */
  function carregaLogo() {
    if (logo) return Promise.resolve(logo);
    return new Promise(function (ok) {
      var img = new Image();
      img.onload = function () {
        try {
          var cv = document.createElement('canvas');
          cv.width = img.naturalWidth; cv.height = img.naturalHeight;
          cv.getContext('2d').drawImage(img, 0, 0);
          logo = { data: cv.toDataURL('image/png'), w: img.naturalWidth, h: img.naturalHeight };
        } catch (e) { logo = null; }
        ok(logo);
      };
      img.onerror = function () { ok(null); };
      img.src = 'assets/img/logo-direcional-header.png';
    });
  }

  function cor(doc, c) { doc.setTextColor(c[0], c[1], c[2]); }
  function rotulo(doc, txt, x, y) {
    doc.setFont('helvetica', 'normal'); doc.setFontSize(7); cor(doc, CINZA);
    doc.text(txt.toUpperCase(), x, y, { charSpace: 0.2 });
  }
  function valor(doc, txt, x, y, tam, c) {
    doc.setFont('helvetica', 'bold'); doc.setFontSize(tam || 10); cor(doc, c || TITULO);
    doc.text(txt, x, y);
  }
  function passo(doc, txt, x, y) {
    doc.setFillColor(VERMELHO[0], VERMELHO[1], VERMELHO[2]);
    doc.rect(x, y - 1.6, 6, 0.6, 'F');
    doc.setFont('helvetica', 'bold'); doc.setFontSize(7.5); cor(doc, VERMELHO);
    doc.text(txt.toUpperCase(), x + 8, y, { charSpace: 0.3 });
  }

  function tabelaChaveValor(doc, linhas, x, y, w) {
    doc.autoTable({
      startY: y, margin: { left: x }, tableWidth: w, theme: 'plain', body: linhas,
      styles: { font: 'helvetica', fontSize: 8.5, cellPadding: { top: 1.6, bottom: 1.6, left: 0, right: 0 }, textColor: GRAFITE, lineColor: LINHA, lineWidth: { top: 0.2 } },
      columnStyles: { 0: { textColor: CINZA }, 1: { halign: 'right', fontStyle: 'bold', textColor: TITULO } }
    });
    return doc.lastAutoTable.finalY;
  }

  function miniGrafico(doc, serie, x, y, w, h) {
    var lo = 250, hi = 950;
    var py = function (v) { return y + (hi - Math.max(lo, Math.min(hi, v))) / (hi - lo) * h; };
    doc.setFont('helvetica', 'normal'); doc.setFontSize(7); cor(doc, CINZA);
    [300, 600, 900].forEach(function (v) {
      doc.setDrawColor(LINHA[0], LINHA[1], LINHA[2]); doc.setLineWidth(0.2);
      doc.line(x + 9, py(v), x + w, py(v));
      doc.text(String(v), x, py(v) + 1);
    });
    var todos = (serie.PRICE || []).concat(serie.SAC || []);
    var max = Math.max.apply(null, todos.concat([0]));
    if (max > hi) { hi = Math.ceil(max / 100) * 100 + 100; lo = Math.max(0, hi - 1400); }
    [['SAC', AZUL], ['PRICE', VERMELHO]].forEach(function (s) {
      var pts = serie[s[0]] || [];
      if (pts.length < 2) return;
      doc.setDrawColor(s[1][0], s[1][1], s[1][2]); doc.setLineWidth(0.5);
      var passoX = (w - 9) / (pts.length - 1);
      for (var i = 1; i < pts.length; i++) doc.line(x + 9 + (i - 1) * passoX, py(pts[i - 1]), x + 9 + i * passoX, py(pts[i]));
    });
    doc.text('hoje', x + 9, y + h + 4); doc.text('fim do prazo', x + w, y + h + 4, { align: 'right' });
  }

  function gerar(p) {
    if (!window.jspdf || !window.jspdf.jsPDF) {
      alert('A biblioteca de PDF ainda está carregando. Tente de novo em alguns segundos.');
      return Promise.resolve();
    }
    return carregaLogo().then(function (lg) {
      var doc = new window.jspdf.jsPDF({ unit: 'mm', format: 'a4' });
      var M = 14, W = 210, R = W - M;

      /* cabecalho */
      if (lg) doc.addImage(lg.data, 'PNG', M, 12, 9 * lg.w / lg.h, 9);
      doc.setFont('helvetica', 'bold'); doc.setFontSize(15); cor(doc, TITULO);
      doc.text('Simulação de financiamento', R, 17.5, { align: 'right' });
      doc.setFont('helvetica', 'normal'); doc.setFontSize(8); cor(doc, CINZA);
      doc.text('Emitida em ' + p.emissao + ' · Portal do Corretor', R, 22.5, { align: 'right' });
      doc.setDrawColor(LINHA[0], LINHA[1], LINHA[2]); doc.setLineWidth(0.3); doc.line(M, 27, R, 27);

      /* cliente e imovel */
      var col = (R - M) / 4;
      [['Cliente', p.cliente || '—', ''], ['Corretor', p.corretor || '—', ''],
       ['Imóvel', p.imovel.nome, p.imovel.detalhe], ['Valor de avaliação', p.imovel.avaliacao, p.imovel.cidade]]
        .forEach(function (c, i) {
          var x = M + i * col;
          rotulo(doc, c[0], x, 33);
          valor(doc, doc.splitTextToSize(c[1], col - 3)[0], x, 38, 9.5);
          if (c[2]) { doc.setFont('helvetica', 'normal'); doc.setFontSize(8); cor(doc, CINZA); doc.text(doc.splitTextToSize(c[2], col - 3)[0], x, 42); }
        });

      /* bloco principal */
      var by = 47;
      doc.setFillColor(FUNDO[0], FUNDO[1], FUNDO[2]); doc.setDrawColor(LINHA[0], LINHA[1], LINHA[2]);
      doc.roundedRect(M, by, R - M, 40, 3, 3, 'FD');
      rotulo(doc, 'Valor financiado', M + 5, by + 7);
      valor(doc, p.principal.financiado, M + 5, by + 16, 21);
      doc.setFont('helvetica', 'normal'); doc.setFontSize(7.5); cor(doc, CINZA);
      doc.text(p.principal.resumo, M + 5, by + 21);
      [['1ª parcela', p.principal.primeira, p.principal.pctRenda, TITULO],
       ['Subsídio', p.principal.subsidio || '—', p.principal.subsidio ? 'desconto FGTS' : 'sem subsídio', p.principal.subsidio ? VERDE : CINZA],
       ['Entrada mínima', p.principal.entrada, 'a negociar', TITULO]]
        .forEach(function (c, i) {
          var x = M + 100 + i * 28;
          rotulo(doc, c[0], x, by + 9);
          valor(doc, c[1], x, by + 15, 10.5, c[3]);
          doc.setFont('helvetica', 'normal'); doc.setFontSize(7.5); cor(doc, CINZA); doc.text(c[2], x, by + 19.5);
        });
      var bx = M + 5, bw = R - M - 10, bY = by + 27, total = p.barra.fin + p.barra.sub + p.barra.ent || 1;
      [[p.barra.fin, VERMELHO], [p.barra.sub, VERDE], [p.barra.ent, GRAFITE]].reduce(function (x, s) {
        var w = bw * s[0] / total;
        if (w > 0.4) { doc.setFillColor(s[1][0], s[1][1], s[1][2]); doc.rect(x, bY, Math.max(0, w - 0.5), 3, 'F'); }
        return x + w;
      }, bx);
      doc.setFont('helvetica', 'normal'); doc.setFontSize(7.5);
      [['Financiamento', VERMELHO, p.barra.fin], ['Subsídio', VERDE, p.barra.sub], ['Entrada', GRAFITE, p.barra.ent]].reduce(function (x, s) {
        if (s[2] <= 0) return x;
        doc.setFillColor(s[1][0], s[1][1], s[1][2]); doc.rect(x, bY + 6, 2.4, 2.4, 'F');
        cor(doc, GRAFITE); var t = s[0] + ' ' + Math.round(s[2]) + '%'; doc.text(t, x + 3.6, bY + 8.1);
        return x + 8 + doc.getTextWidth(t);
      }, bx);

      /* condicoes e dados do cliente */
      var ty = by + 50, meia = (R - M - 10) / 2;
      passo(doc, 'Condições', M, ty);
      passo(doc, 'Dados do cliente', M + meia + 10, ty);
      var y1 = tabelaChaveValor(doc, p.condicoes, M, ty + 3, meia);
      var y2 = tabelaChaveValor(doc, p.dadosCliente, M + meia + 10, ty + 3, meia);

      /* seguradoras */
      var sy = Math.max(y1, y2) + 9;
      passo(doc, 'Parcela por seguradora', M, sy);
      doc.autoTable({
        startY: sy + 3, margin: { left: M, right: M }, theme: 'plain',
        head: [['Seguradora', '1ª parcela', 'Última parcela']],
        body: p.seguradoras.map(function (s) { return [s.nome + (s.escolhida ? '  (escolhida)' : ''), s.primeira, s.ultima]; }),
        styles: { font: 'helvetica', fontSize: 8.5, cellPadding: { top: 1.8, bottom: 1.8, left: 0, right: 0 }, textColor: GRAFITE, lineColor: LINHA, lineWidth: { bottom: 0.2 } },
        headStyles: { fontStyle: 'bold', textColor: CINZA, fontSize: 7.5 },
        columnStyles: { 1: { halign: 'right', fontStyle: 'bold' }, 2: { halign: 'right' } },
        didParseCell: function (d) { if (d.section === 'head' && d.column.index > 0) d.cell.styles.halign = 'right';
          if (d.section === 'body' && p.seguradoras[d.row.index].escolhida) d.cell.styles.fontStyle = 'bold'; }
      });

      /* PRICE x SAC */
      var cy = doc.lastAutoTable.finalY + 9;
      passo(doc, 'PRICE ou SAC', M, cy);
      doc.autoTable({
        startY: cy + 3, margin: { left: M }, tableWidth: 104, theme: 'plain',
        head: [['Comparação', 'PRICE', 'SAC']], body: p.comparacao,
        styles: { font: 'helvetica', fontSize: 8.5, cellPadding: { top: 1.8, bottom: 1.8, left: 0, right: 0 }, textColor: GRAFITE, lineColor: LINHA, lineWidth: { bottom: 0.2 } },
        headStyles: { fontStyle: 'bold', textColor: CINZA, fontSize: 7.5 },
        columnStyles: { 1: { halign: 'right', fontStyle: 'bold' }, 2: { halign: 'right', fontStyle: 'bold' } },
        didParseCell: function (d) { if (d.section === 'head' && d.column.index > 0) d.cell.styles.halign = 'right'; }
      });
      doc.setFont('helvetica', 'normal'); doc.setFontSize(7.5); cor(doc, CINZA);
      doc.text('Parcela ao longo do prazo', M + 116, cy + 5);
      doc.setFillColor(VERMELHO[0], VERMELHO[1], VERMELHO[2]); doc.rect(M + 152, cy + 3.6, 4, 0.8, 'F'); doc.text('PRICE', M + 157, cy + 5);
      doc.setFillColor(AZUL[0], AZUL[1], AZUL[2]); doc.rect(M + 168, cy + 3.6, 4, 0.8, 'F'); doc.text('SAC', M + 173, cy + 5);
      miniGrafico(doc, p.serie, M + 116, cy + 9, R - M - 116, 26);

      /* rodape */
      doc.setDrawColor(LINHA[0], LINHA[1], LINHA[2]); doc.setLineWidth(0.3); doc.line(M, 276, R, 276);
      doc.setFont('helvetica', 'normal'); doc.setFontSize(7.5); cor(doc, CINZA);
      doc.text(doc.splitTextToSize(p.aviso, 140), M, 281);
      doc.setFont('helvetica', 'bold'); cor(doc, GRAFITE); doc.text('Grupo Direcional', R, 281, { align: 'right' });

      doc.save(p.arquivo);
    });
  }

  return { gerar: gerar };
})();

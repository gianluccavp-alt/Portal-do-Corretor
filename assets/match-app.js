/* ============================================================
   MATCH DE UNIDADES - tela
   Abertura -> 6 perguntas em linha do tempo -> revelacao -> resultado.
   As regras do fluxo ficam em match-fluxo.js; as de negocio em match.js.
   ============================================================ */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var EMPS = window.SIM_EMPS;
  var M = window.Match, F = window.MatchFluxo;
  var ETAPAS = F.ETAPAS;
  var ROTULOS = { onde: 'Onde', renda: 'Renda bruta', ato: 'Ato', nascimento: 'Nascimento',
    perfil: 'Perfil do cliente', politica: 'Política' };
  var TELAS = ['abertura', 'perguntas', 'revelacao', 'resultado'];
  var CHECK = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.6" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';

  var estado = { tela: 'abertura', etapa: 0, r: F.respostasIniciais(''), resultado: null,
    ordem: 'parcela', aberta: '', marcadas: {} };
  var iniciado = false;   /* depois da carga inicial, toda troca de tela move o foco */

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function brl(n) {
    return (isFinite(n) ? n : 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
  function pct(f) { return ((f || 0) * 100).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'; }
  function hoje() { var d = new Date(); return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }
  function modelo(id) { return $(id).content.cloneNode(true); }
  function cada(lista, fn) { Array.prototype.forEach.call(lista, fn); }
  function nomePolitica(id) { return window.MatchProSoluto.politicaPorId(id).nome; }
  function ctx() { return { emps: EMPS, nomePolitica: nomePolitica, hoje: hoje() }; }

  function cidades() {
    var vistas = [];
    EMPS.forEach(function (e) { if (vistas.indexOf(e.cidade) < 0) vistas.push(e.cidade); });
    return vistas;
  }
  /* so os digitos, em reais inteiros, formatado como 4.200 */
  function moeda(input) {
    var dig = input.value.replace(/\D/g, '').slice(0, 9);
    var n = dig ? M.numero(dig) : 0;
    input.value = dig ? n.toLocaleString('pt-BR') : '';
    return { n: n, vazio: !dig };
  }
  function idade(nasc, em) {
    var a = em.getFullYear() - nasc.getFullYear();
    if (em.getMonth() < nasc.getMonth() || (em.getMonth() === nasc.getMonth() && em.getDate() < nasc.getDate())) a--;
    return a;
  }

  /* ---------- navegacao ---------- */
  function irPara(tela, etapa, empilhar) {
    estado.tela = tela;
    if (typeof etapa === 'number') estado.etapa = Math.max(0, Math.min(ETAPAS.length - 1, etapa));
    TELAS.forEach(function (t) { $('mt-' + t).hidden = t !== tela; });
    document.body.classList.toggle('mt-em-fluxo', tela !== 'abertura');
    erro('');
    if (tela === 'perguntas') {
      var n = estado.etapa;
      $('mt-passo').textContent = 'Passo ' + (n + 1) + ' de ' + ETAPAS.length;
      $('mt-progresso').style.width = Math.round(n / ETAPAS.length * 100) + '%';
      $('mt-progresso').setAttribute('aria-valuenow', String(n));
      $('mt-progresso').setAttribute('aria-valuetext', 'Passo ' + (n + 1) + ' de ' + ETAPAS.length);
      $('mt-continuar').firstChild.nodeValue = ETAPAS[n] === 'politica' ? 'Encontrar unidades' : 'Continuar';
      desenhaTrilha();
      desenhaEtapa();
    }
    if (empilhar) history.pushState({ tela: tela, etapa: estado.etapa }, '');
    if (iniciado) {
      window.scrollTo(0, 0);
      var alvo = tela === 'perguntas' ? $('mt-etapa').querySelector('.mt-etapa-tit')
        : tela === 'revelacao' ? $('mt-rev-titulo') : tela === 'resultado' ? $('mt-res-titulo') : $('mt-comecar');
      if (alvo) alvo.focus({ preventScroll: true });
    }
  }

  function erro(msg) { var el = $('mt-erro'); el.textContent = msg || ''; el.hidden = !msg; }

  /* ---------- trilha ---------- */
  function desenhaTrilha() {
    var base = modelo('tpl-trilha').querySelectorAll('li'), ol = $('mt-trilha'), c = ctx();
    ol.innerHTML = '';
    ETAPAS.concat(['resultado']).forEach(function (e, k) {
      var li;
      if (k < estado.etapa) {
        var val = F.resumoEtapa(e, estado.r, c);
        li = base[0].cloneNode(true);
        li.querySelector('.mt-tl-rot').textContent = ROTULOS[e];
        li.querySelector('.mt-tl-val').textContent = val;
        var btn = li.querySelector('.mt-tl-btn');
        btn.setAttribute('aria-label', 'Editar ' + ROTULOS[e] + ': ' + val);
        btn.addEventListener('click', function () { irPara('perguntas', k, true); });
      } else if (k === estado.etapa) {
        li = base[1].cloneNode(true);
        li.querySelector('.mt-tl-val').textContent = ROTULOS[e];
      } else {
        li = base[2].cloneNode(true);
        li.querySelector('.mt-tl-rot').textContent = e === 'resultado' ? 'Resultado' : ROTULOS[e];
      }
      ol.appendChild(li);
    });
  }

  /* ---------- etapas ---------- */
  function desenhaEtapa() {
    var etapa = ETAPAS[estado.etapa], box = $('mt-etapa');
    box.innerHTML = '';
    box.appendChild(modelo('tpl-' + etapa));
    ({ onde: etapaOnde, renda: etapaRenda, ato: etapaAto, nascimento: etapaNascimento,
       perfil: etapaPerfil, politica: etapaPolitica })[etapa](box);
  }

  function marca(el, ligado, classe) {
    el.classList.toggle(classe, ligado);
    el.setAttribute('aria-pressed', String(ligado));
  }

  function etapaOnde(box) {
    var r = estado.r, pills = box.querySelector('[data-campo=cidade]'), opts = box.querySelector('[data-campo=empId]');
    cidades().forEach(function (cid) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'pill'; b.textContent = cid;
      marca(b, cid === r.cidade, 'pill-on');
      b.addEventListener('click', function () {
        r.cidade = cid; r.empId = '';
        cada(pills.children, function (p) { marca(p, p === b, 'pill-on'); });
        desenhaEmps(opts);
        erro('');
      });
      pills.appendChild(b);
    });
    desenhaEmps(opts);
  }

  function desenhaEmps(opts) {
    var r = estado.r;
    opts.innerHTML = '';
    if (!r.cidade) return;
    var lista = [{ id: '', nome: 'Todos os empreendimentos', sub: 'Busca em ' + r.cidade }]
      .concat(EMPS.filter(function (e) { return e.cidade === r.cidade; }).map(function (e) {
        return { id: e.id, nome: e.nome, sub: e.cidade, foto: F.fotoDe(e) };
      }));
    lista.forEach(function (o) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'opt';
      b.innerHTML = (o.foto ? '<img class="opt-foto" src="' + esc(o.foto) + '" alt="" width="48" height="48">'
          : '<span class="opt-ic"><img class="mt-ic3d" src="assets/img/icones-3d/pino.svg" alt="" width="34" height="34"></span>') +
        '<span class="opt-txt"><span class="opt-nome">' + esc(o.nome) + '</span><span class="opt-sub">' + esc(o.sub) + '</span></span>' +
        '<span class="radio">' + CHECK + '</span>';
      var img = b.querySelector('.opt-foto');
      if (img) img.addEventListener('error', function () {
        var ic = document.createElement('span');
        ic.className = 'opt-ic';
        ic.innerHTML = '<img class="mt-ic3d" src="assets/img/icones-3d/predio.svg" alt="" width="34" height="34">';
        img.parentNode.replaceChild(ic, img);
      });
      marca(b, o.id === r.empId, 'opt-on');
      b.addEventListener('click', function () {
        r.empId = o.id;
        cada(opts.children, function (x) { marca(x, x === b, 'opt-on'); });
      });
      opts.appendChild(b);
    });
  }

  function campoErro(input, ligado) {
    var lab = input.closest('.field');
    if (lab) lab.classList.toggle('field-erro', ligado);
    if (ligado) input.setAttribute('aria-invalid', 'true'); else input.removeAttribute('aria-invalid');
  }

  function etapaRenda(box) {
    var input = box.querySelector('[data-campo=renda]');
    input.value = estado.r.renda ? estado.r.renda.toLocaleString('pt-BR') : '';
    input.addEventListener('input', function () {
      estado.r.renda = moeda(input).n;
      campoErro(input, false); erro('');
    });
  }

  function etapaAto(box) {
    var r = estado.r, padrao = box.querySelector('[data-opcao=padrao]'), outro = box.querySelector('[data-opcao=outro]');
    var campo = box.querySelector('.mt-ato-campo'), input = box.querySelector('[data-campo=ato]');
    var sub = F.textoAtoPadrao(r.empId);
    box.querySelector('.mt-ato-padrao-sub').textContent = sub.charAt(0).toUpperCase() + sub.slice(1);
    function mostra(ehOutro) {
      marca(padrao, !ehOutro, 'opt-on');
      marca(outro, ehOutro, 'opt-on');
      campo.hidden = !ehOutro;
    }
    if (r.ato !== null && r.ato >= 0) input.value = r.ato.toLocaleString('pt-BR');
    mostra(r.ato !== null);
    padrao.addEventListener('click', function () { r.ato = null; mostra(false); campoErro(input, false); erro(''); });
    outro.addEventListener('click', function () {
      r.ato = /\d/.test(input.value) ? M.numero(input.value) : NaN;
      mostra(true);
      input.focus();
    });
    input.addEventListener('input', function () {
      var v = moeda(input);
      r.ato = v.vazio ? NaN : v.n;
      campoErro(input, false); erro('');
    });
  }

  function etapaNascimento(box) {
    var r = estado.r, campos = ['dia', 'mes', 'ano'], tam = { dia: 2, mes: 2, ano: 4 };
    var pill = box.querySelector('.mt-idade');
    function atualizaIdade() {
      var nasc = F.dataNascimento(r.dia, r.mes, r.ano), h = hoje();
      var ok = nasc && nasc.getTime() <= h.getTime();
      pill.hidden = !ok;
      if (ok) pill.querySelector('.mt-idade-txt').textContent = idade(nasc, h) + ' anos';
    }
    campos.forEach(function (c, i) {
      var input = box.querySelector('[data-campo=' + c + ']');
      input.value = r[c];
      /* colar a data inteira (14/03/1993 ou 14031993) preenche os tres campos */
      input.addEventListener('paste', function (ev) {
        var dig = ((ev.clipboardData || window.clipboardData).getData('text') || '').replace(/\D/g, '');
        if (dig.length !== 8) return;
        ev.preventDefault();
        campos.forEach(function (k, j) {
          var el = box.querySelector('[data-campo=' + k + ']');
          el.value = dig.slice([0, 2, 4][j], [2, 4, 8][j]);
          r[k] = el.value;
          campoErro(el, false);
        });
        erro('');
        atualizaIdade();
        box.querySelector('[data-campo=ano]').focus();
      });
      input.addEventListener('input', function () {
        input.value = input.value.replace(/\D/g, '').slice(0, tam[c]);
        r[c] = input.value;
        cada(box.querySelectorAll('.mt-data input'), function (x) { campoErro(x, false); });
        erro('');
        atualizaIdade();
        if (input.value.length === tam[c] && campos[i + 1]) {
          var prox = box.querySelector('[data-campo=' + campos[i + 1] + ']');
          prox.focus(); prox.select();
        }
      });
    });
    atualizaIdade();
  }

  function etapaPerfil(box) {
    var r = estado.r, tiles = box.querySelectorAll('.tile'), aviso = box.querySelector('.mt-aviso-dep');
    function atualiza() {
      var vis = F.perguntasPerfil(r);
      cada(tiles, function (t) {
        var c = t.getAttribute('data-campo'), on = r[c] === true;
        t.hidden = vis.indexOf(c) < 0;
        t.classList.toggle('tile-on', on);
        t.setAttribute('aria-checked', String(on));
      });
      aviso.hidden = !(vis.indexOf('fatorSocial') >= 0 && r.fatorSocial !== true);
    }
    cada(tiles, function (t) {
      t.addEventListener('click', function () {
        var c = t.getAttribute('data-campo');
        r[c] = r[c] !== true;
        atualiza();
      });
    });
    atualiza();
  }

  function etapaPolitica(box) {
    var r = estado.r, pols = box.querySelector('[data-campo=politicaId]');
    M.ORDEM_POLITICAS.forEach(function (id) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'pol';
      b.setAttribute('aria-label', 'Política ' + nomePolitica(id));
      b.innerHTML = '<img src="assets/img/ranking/' + esc(id) + '.png" alt="" width="120" height="120">' +
        '<span class="pol-check" aria-hidden="true">✓</span>';
      marca(b, id === r.politicaId, 'pol-on');
      b.addEventListener('click', function () {
        r.politicaId = id;
        cada(pols.children, function (x) { marca(x, x === b, 'pol-on'); });
      });
      pols.appendChild(b);
    });
  }

  /* campo que recebe o foco quando a etapa nao passa */
  function campoDoErro(etapa) {
    var box = $('mt-etapa');
    if (etapa === 'onde') return box.querySelector('.pill');
    if (etapa === 'renda') return box.querySelector('[data-campo=renda]');
    if (etapa === 'ato') return box.querySelector('[data-campo=ato]');
    if (etapa === 'nascimento') {
      var r = estado.r;
      var vazio = ['dia', 'mes', 'ano'].filter(function (c) { return !r[c]; })[0];
      return box.querySelector('[data-campo=' + (vazio || 'dia') + ']');
    }
    return null;
  }

  function continuar() {
    var etapa = ETAPAS[estado.etapa];
    var msg = F.validarEtapa(etapa, estado.r, hoje());
    if (msg) {
      erro(msg);
      var campo = campoDoErro(etapa);
      if (campo) {
        if (campo.tagName === 'INPUT') {
          if (etapa === 'nascimento') cada($('mt-etapa').querySelectorAll('.mt-data input'), function (x) { campoErro(x, true); });
          else campoErro(campo, true);
        }
        campo.focus();
      }
      return;
    }
    if (etapa === 'politica') { buscar(estado.r.politicaId); return; }
    irPara('perguntas', estado.etapa + 1, true);
  }

  function voltar() {
    if (estado.etapa === 0) irPara('abertura', 0, true);
    else irPara('perguntas', estado.etapa - 1, true);
  }

  /* ---------- estoque ---------- */
  function estoque(cidade) {
    return EMPS.filter(function (e) { return e.cidade === cidade; }).map(function (emp) {
      var u = window.SimUnidades.porEmpreendimento(emp), unidades = [];
      u.blocos.forEach(function (b) {
        (u.unidades[b.id] || []).forEach(function (cod) {
          var d = u.detalhes[cod] || {};
          unidades.push({ codigo: cod, torre: parseInt(b.id.replace(/\D/g, ''), 10), tipoLabel: d.tipoLabel,
            areaPriv: d.areaPriv, avaliacao: d.avaliacao,
            /* spec 4.2: valor associativo SEM premio (sem a Folga Volta ao Caixa) */
            associativo: d.associativoSemPremio });
        });
      });
      return { emp: emp, unidades: unidades };
    });
  }

  /* ---------- busca (Task 4 completa: revelacao + resultado) ---------- */
  var pendente = false;
  function buscar(politicaId) {
    if (politicaId) estado.r.politicaId = politicaId;
    irPara('revelacao', null, true);
  }

  /* estado da planilha ao vivo: 'carregando' | 'erro' | 'ok' */
  function status(est) {
    var rev = $('mt-revelacao');
    if (!rev) return;
    rev.classList.toggle('mt-buscando', est === 'carregando');
    rev.classList.toggle('mt-rev-erro', est === 'erro');
  }

  /* ---------- PDF (spec secao 7) ---------- */
  function gerarPdf() {
    if (!window.jspdf || !window.jspdf.jsPDF) { alert('A biblioteca de PDF ainda está carregando. Tente de novo em alguns segundos.'); return; }
    var nome = prompt('Nome do cliente (opcional):', '') || '';
    var doc = new window.jspdf.jsPDF({ unit: 'mm', format: 'a4' });
    var W = doc.internal.pageSize.getWidth(), Mg = 14;
    doc.setFont('helvetica', 'bold'); doc.setFontSize(15); doc.setTextColor(228, 3, 43);
    doc.text('Grupo Direcional', Mg, 18);
    doc.setFontSize(11); doc.setTextColor(58, 64, 67);
    doc.text('Unidades sugeridas' + (nome ? ' para ' + nome : ''), Mg, 26);
    doc.setFont('helvetica', 'normal'); doc.setFontSize(8.5); doc.setTextColor(106, 114, 117);
    doc.text('Gerado em ' + hoje().toLocaleDateString('pt-BR'), Mg, 31);

    var linhas = Object.keys(estado.marcadas).map(function (k) { return M.linhaPdf(estado.marcadas[k]); });
    doc.autoTable({
      startY: 36, margin: { left: Mg, right: Mg },
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
      doc.text('Simulação aproximada, sujeita à análise de crédito da CAIXA e à aprovação da Direcional.', Mg, H - 8);
      doc.text('Página ' + p + ' de ' + total, W - Mg, H - 8, { align: 'right' });
    }
    doc.save('unidades-' + (nome ? nome.replace(/\s+/g, '-').toLowerCase() : 'cliente') + '.pdf');
  }

  /* ---------- eventos ---------- */
  $('mt-comecar').addEventListener('click', function () { irPara('perguntas', 0, true); });
  $('mt-continuar').addEventListener('click', continuar);
  $('mt-voltar').addEventListener('click', voltar);
  $('mt-sair').addEventListener('click', function () { irPara('abertura', null, true); });
  $('mt-rev-voltar').addEventListener('click', function () { irPara('perguntas', ETAPAS.length - 1, true); });
  /* Enter avanca; em botoes e links o Enter ja clica */
  $('mt-perguntas').addEventListener('keydown', function (ev) {
    if (ev.key !== 'Enter' || ev.isComposing || ev.defaultPrevented) return;
    if (ev.target.closest && ev.target.closest('button, a')) return;
    ev.preventDefault();
    continuar();
  });
  window.addEventListener('popstate', function (ev) {
    var s = ev.state || { tela: 'abertura', etapa: 0 };
    irPara(TELAS.indexOf(s.tela) >= 0 ? s.tela : 'abertura', s.etapa, false);
  });

  history.replaceState({ tela: 'abertura', etapa: 0 }, '');
  irPara('abertura', 0, false);
  iniciado = true;

  window.SimUnidades.aoMudar(function (est) {
    if (est === 'ok') { status('ok'); if (pendente) { pendente = false; buscar(); } }
    else if (est === 'erro' && pendente) status('erro');
  });
  window.SimUnidades.carregar();

})();

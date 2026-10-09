/* ============================================================
   VISITAS DA RECEPCAO - interface de /visitas-recepcao-adm
   ------------------------------------------------------------
   Tela de senha + dashboard. Busca os ultimos 30 dias uma vez e
   filtra no navegador. Regras em assets/visitas.js.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md (secao 6)
   ============================================================ */
(function () {
  'use strict';

  var V = window.Visitas;
  var CHAVE_SESSAO = 'visitas.adm.senha';
  var ALTURA_BARRA = 190;
  var PERIODOS = [['hoje', 'Hoje'], ['7', '7 dias'], ['30', '30 dias']];
  var NOME_PERIODO = { hoje: 'Hoje', '7': 'Últimos 7 dias', '30': 'Últimos 30 dias' };
  var EMPS = V.listaEmpreendimentos(window.CITIES || []);
  var CIDADES = ['Todas'].concat((window.CITIES || []).map(function (c) { return c.name; }));
  var estado = { senha: '', todas: [], periodo: '7', cidade: 'Todas', emp: 'Todos', carregadoEm: null, hoje: V.dataLocalIso(new Date()) };
  var api = window.VisitasAPI.criar({
    url: window.VISITAS_APPS_SCRIPT_URL || '',
    senha: function () { return estado.senha; }
  });

  function $(id) { return document.getElementById(id); }
  function el(tag, cls, texto) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }
  function pct(q, t) { return (t ? Math.round(q / t * 100) : 0) + '%'; }
  function lerSessao() { try { return sessionStorage.getItem(CHAVE_SESSAO) || ''; } catch (e) { return ''; } }
  function gravarSessao(s) {
    try { if (s) sessionStorage.setItem(CHAVE_SESSAO, s); else sessionStorage.removeItem(CHAVE_SESSAO); } catch (e) { /* ignora */ }
  }

  /* ---------- senha / sessao (spec 6.1) ---------- */
  function mostrarGate(msg) {
    $('app').hidden = true;
    $('gate').hidden = false;
    $('gate-demo').hidden = !api.demo;
    $('gate-erro').textContent = msg || '';
    $('gate-erro').hidden = !msg;
    $('gate-senha').setAttribute('aria-invalid', msg ? 'true' : 'false');
    $('gate-senha').value = '';
    $('gate-entrar').disabled = false;
    $('gate-entrar').textContent = 'Entrar';
    $('gate-senha').focus();
  }
  function mostrarApp() {
    $('gate').hidden = true;
    $('app').hidden = false;
    $('aviso-demo').hidden = !api.demo;
  }
  function sair(msg) {
    gravarSessao('');
    estado.senha = '';
    estado.todas = [];
    mostrarGate(msg);
  }

  /* ---------- dados ---------- */
  function buscar() {
    estado.hoje = V.dataLocalIso(new Date());
    $('atualizar').disabled = true;
    return api.chamar('listar', { de: V.somarDias(estado.hoje, -29), ate: estado.hoje }).then(function (r) {
      estado.todas = (r.visitas || []).filter(function (v) { return V.TIPOS[v.tipo]; });
      estado.carregadoEm = new Date();
      $('aviso-erro').hidden = true;
      render();
    }).finally(function () { $('atualizar').disabled = false; });
  }
  var MSG_ERRO = 'Erro na planilha de visitas. Avise o comercial.';
  function tratarErro(f) {
    if (f && f.codigo === 'senha') { sair('Senha incorreta.'); return; }
    $('aviso-erro-txt').textContent = (f && f.mensagem) || MSG_ERRO;
    $('aviso-erro').hidden = false;
  }
  function entrar(ev) {
    ev.preventDefault();
    var s = $('gate-senha').value;
    if (!s) { mostrarGate('Digite a senha.'); return; }
    $('gate-entrar').disabled = true;
    $('gate-entrar').textContent = 'Entrando…';
    estado.senha = s;
    buscar().then(function () {
      gravarSessao(s);
      mostrarApp();
    }, function (f) {
      estado.senha = '';
      mostrarGate(f && f.codigo === 'senha' ? 'Senha incorreta.' : (f && f.mensagem) || MSG_ERRO);
    });
  }

  /* ---------- filtros ---------- */
  function montarChips(caixa, itens, aoEscolher) {
    itens.forEach(function (it) {
      var b = el('button', 'fchip', it[1]);
      b.type = 'button';
      b.setAttribute('data-v', it[0]);
      b.setAttribute('aria-pressed', 'false');
      b.addEventListener('click', function () { aoEscolher(it[0]); });
      caixa.appendChild(b);
    });
  }
  function marcarChips(caixa, valor) {
    Array.prototype.forEach.call(caixa.children, function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-v') === valor ? 'true' : 'false');
    });
  }
  function montarSelectEmp() {
    var sel = $('f-emp');
    sel.textContent = '';
    var todos = el('option', '', 'Todos os empreendimentos');
    todos.value = 'Todos';
    sel.appendChild(todos);
    EMPS.forEach(function (e) {
      if (estado.cidade !== 'Todas' && e.cidade !== estado.cidade) return;
      var o = el('option', '', e.nome);
      o.value = e.nome;
      sel.appendChild(o);
    });
    sel.value = estado.emp;
  }
  function filtroAtual() {
    var iv = V.intervalo(estado.periodo, estado.hoje);
    return {
      iv: iv,
      visitas: V.filtrar(estado.todas, { de: iv.de, ate: iv.ate, cidade: estado.cidade, empreendimento: estado.emp }),
      lista: EMPS.filter(function (e) {
        return (estado.cidade === 'Todas' || e.cidade === estado.cidade) && (estado.emp === 'Todos' || e.nome === estado.emp);
      })
    };
  }

  /* ---------- render (spec 6.2) ---------- */
  function render() {
    marcarChips($('periodos'), estado.periodo);
    marcarChips($('cidades'), estado.cidade);
    var f = filtroAtual(), iv = f.iv, t = V.totaisPorTipo(f.visitas);
    var rotulo = estado.periodo === 'hoje'
      ? 'Hoje, ' + V.dataCurta(iv.ate)
      : NOME_PERIODO[estado.periodo] + ' · ' + V.dataCurta(iv.de) + ' a ' + V.dataCurta(iv.ate);

    $('k-total').textContent = t.total;
    $('k-total-lab').textContent = rotulo;
    $('t-emps-lab').textContent = rotulo;
    V.ORDEM_TIPOS.forEach(function (k) {
      $('k-' + k).textContent = t[k];
      $('k-' + k + '-pct').textContent = pct(t[k], t.total) + ' do total';
      $('o-' + k).style.width = (t.total ? t[k] / t.total * 100 : 0) + '%';
      $('ol-' + k).textContent = pct(t[k], t.total) + ' · ' + t[k];
    });
    $('k-media').textContent = (t.total / iv.dias).toFixed(1).replace('.', ',');
    $('k-media-lab').textContent = estado.periodo === 'hoje' ? 'dia em andamento' : 'em ' + iv.dias + ' dias';

    renderGrafico(f.visitas, iv);
    renderRanking(V.rankingImobiliarias(f.visitas, 5));
    renderTabelaEmps(V.porEmpreendimento(f.visitas, f.lista));
    renderRecentes(V.recentes(f.visitas, 8));
    $('atualizado-em').textContent = estado.carregadoEm ? 'Atualizado às ' + V.horaLocal(estado.carregadoEm) : '';
  }

  function renderGrafico(visitas, iv) {
    var porHora = estado.periodo === 'hoje';
    var cols = porHora ? V.porHora(visitas, 8, 20) : V.porDia(visitas, iv.de, iv.ate);
    var max = Math.max.apply(null, cols.map(function (c) { return c.total; }).concat([1]));
    var g = $('grafico'), r = $('grafico-rotulos');
    var titulo = porHora ? 'Visitas por horário · hoje' : 'Visitas por dia';
    $('grafico-titulo').textContent = titulo;
    g.setAttribute('aria-label', titulo + ': ' + visitas.length + ' visitas');
    g.textContent = '';
    r.textContent = '';
    cols.forEach(function (c, i) {
      var nome = porHora ? c.hora + 'h' : V.rotuloDia(c.data);
      var rotulo = porHora ? c.hora + 'h'
        : iv.dias <= 7 ? V.rotuloDia(c.data)
          : (cols.length - 1 - i) % 5 === 0 ? V.dataCurta(c.data) : '';
      var col = el('div', 'col');
      col.title = nome + ' · ' + c.total + ' visitas (' + c.esp + ' espontâneas, ' + c.house + ' house, ' + c.imob + ' imobiliária)';
      col.appendChild(el('span', 'col-val num', (porHora || iv.dias <= 7) && c.total ? String(c.total) : ''));
      var pilha = el('div', 'pilha');
      ['imob', 'house', 'esp'].forEach(function (k) {
        var s = el('div');
        s.style.height = Math.round(c[k] / max * ALTURA_BARRA) + 'px';
        s.style.background = V.TIPOS[k].cor;
        pilha.appendChild(s);
      });
      col.appendChild(pilha);
      g.appendChild(col);
      r.appendChild(el('span', 'rot num', rotulo));
    });
    $('grafico-area').hidden = visitas.length === 0;
    $('grafico-vazio').hidden = visitas.length > 0;
  }

  function renderRanking(lista) {
    var ol = $('ranking');
    ol.textContent = '';
    if (!lista.length) { ol.appendChild(el('li', 'dica', 'Nenhuma visita de imobiliária no período.')); return; }
    var max = lista[0].qtd;
    lista.forEach(function (it) {
      var li = el('li');
      var topo = el('div', 'leg-linha');
      topo.appendChild(el('span', '', it.nome));
      topo.appendChild(el('strong', 'num', String(it.qtd)));
      var trilho = el('div', 'rank-trilho');
      var barra = el('div');
      barra.style.width = (it.qtd / max * 100) + '%';
      trilho.appendChild(barra);
      li.appendChild(topo);
      li.appendChild(trilho);
      ol.appendChild(li);
    });
  }

  function celula(tr, texto, cls) { var td = el('td', cls, texto); tr.appendChild(td); return td; }

  function renderTabelaEmps(linhas) {
    var tb = $('tab-emps');
    tb.textContent = '';
    linhas.forEach(function (l) {
      var tr = el('tr');
      celula(tr, l.nome, 'forte');
      celula(tr, l.cidade, 'suave');
      celula(tr, String(l.total), 'dir forte num');
      celula(tr, String(l.esp), 'dir num');
      celula(tr, String(l.house), 'dir num');
      celula(tr, String(l.imob), 'dir num');
      var td = celula(tr, '');
      var mix = el('div', 'mix mix-p');
      V.ORDEM_TIPOS.forEach(function (k) {
        var s = el('div');
        s.style.width = (l.total ? l[k] / l.total * 100 : 0) + '%';
        s.style.background = V.TIPOS[k].cor;
        mix.appendChild(s);
      });
      td.appendChild(mix);
      tb.appendChild(tr);
    });
  }

  function renderRecentes(lista) {
    var tb = $('tab-recentes');
    tb.textContent = '';
    lista.forEach(function (v) {
      var tr = el('tr');
      celula(tr, V.dataCurta(v.data), 'num');
      celula(tr, v.hora, 'forte num');
      celula(tr, v.empreendimento);
      var td = celula(tr, '');
      var badge = el('span', 'badge');
      var ponto = el('span', 'ponto');
      ponto.style.background = V.TIPOS[v.tipo].cor;
      badge.appendChild(ponto);
      badge.appendChild(document.createTextNode(V.TIPOS[v.tipo].nome));
      td.appendChild(badge);
      celula(tr, V.detalhe(v), 'suave');
      tb.appendChild(tr);
    });
    $('sem-recentes').hidden = lista.length > 0;
  }

  function exportar() {
    var f = filtroAtual();
    var blob = new Blob([V.gerarCSV(f.visitas)], { type: 'text/csv;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = V.nomeArquivoCSV(f.iv.de, f.iv.ate);
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  /* ---------- inicio ---------- */
  function iniciar() {
    montarChips($('periodos'), PERIODOS, function (v) { estado.periodo = v; render(); });
    montarChips($('cidades'), CIDADES.map(function (c) { return [c, c]; }), function (v) {
      estado.cidade = v;
      estado.emp = 'Todos';
      montarSelectEmp();
      render();
    });
    montarSelectEmp();
    $('f-emp').addEventListener('change', function () { estado.emp = $('f-emp').value; render(); });
    $('gate-form').addEventListener('submit', entrar);
    $('atualizar').addEventListener('click', function () { buscar().catch(tratarErro); });
    $('aviso-erro-tentar').addEventListener('click', function () { buscar().catch(tratarErro); });
    $('exportar').addEventListener('click', exportar);
    $('sair').addEventListener('click', function () { sair(); });

    var salva = lerSessao();
    if (salva) {
      estado.senha = salva;
      mostrarApp();
      render();
      buscar().catch(tratarErro);
    } else {
      mostrarGate();
    }
  }

  iniciar();
})();

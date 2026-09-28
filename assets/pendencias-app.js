/* ============================================================
   PENDENCIAS DE VENDAS - interface
   ------------------------------------------------------------
   Estado + DOM da pagina /pendencias-vendas. Toda regra de negocio
   fica em assets/pendencias.js (window.Pendencias); aqui so se le o
   estado e se desenha. Texto vindo da planilha entra SEMPRE por
   textContent.
   ============================================================ */
(function () {
  'use strict';

  var P = window.Pendencias;
  var URL_API = window.PENDENCIAS_APPS_SCRIPT_URL || '';
  var MODO_DEMO = !URL_API || /[?&]demo=1(&|$)/.test(window.location.search);
  var CHAVE_SESSAO = 'pendencias_senha';
  var TIMEOUT_PADRAO = 60000;
  var TIMEOUT_ATUALIZAR = 360000;
  var MSG_SENHA = 'Senha incorreta. Confira maiúsculas e tente de novo.';
  var ROTULOS_ORDEM = {
    antigas: 'as mais antigas primeiro',
    recentes: 'as mais recentes primeiro',
    valor: 'as de maior valor primeiro',
    pendencias: 'as com mais pendências primeiro'
  };

  var estado = {
    senha: '',
    vendas: [],
    filtros: P.filtrosPadrao(),
    ordem: 'antigas',
    salesforceAtualizadoEm: null,
    atualizando: false,
    aberta: null
  };

  /* ---------- utilitarios de DOM ---------- */
  function $(id) { return document.getElementById(id); }
  function el(tag, classe, texto) {
    var e = document.createElement(tag);
    if (classe) e.className = classe;
    if (texto !== undefined && texto !== null) e.textContent = texto;
    return e;
  }
  var ICONES = {
    relogio: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    nota: '<path d="M4 5h16v10l-5 5H4z"/><path d="M15 20v-5h5"/>',
    seta: '<path d="m9 6 6 6-6 6"/>',
    x: '<path d="M18 6 6 18M6 6l12 12"/>',
    alerta: '<path d="M12 7v6M12 17h.01"/>',
    check: '<path d="M20 6 9 17l-5-5"/>'
  };
  /* icones sao strings fixas deste arquivo, nunca dado da planilha */
  function icone(nome, tam) {
    var s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    var t = String(tam || 14);
    s.setAttribute('width', t);
    s.setAttribute('height', t);
    s.setAttribute('viewBox', '0 0 24 24');
    s.setAttribute('fill', 'none');
    s.setAttribute('stroke', 'currentColor');
    s.setAttribute('stroke-width', '2');
    s.setAttribute('stroke-linecap', 'round');
    s.setAttribute('stroke-linejoin', 'round');
    s.setAttribute('aria-hidden', 'true');
    s.innerHTML = ICONES[nome];
    return s;
  }
  function plural(n, um, varios) { return n + ' ' + (n === 1 ? um : varios); }

  /* ---------- API (spec 4.1) ---------- */
  function falha(codigo, mensagem) { return { codigo: codigo, mensagem: mensagem }; }

  function chamar(acao, params, timeout) {
    if (MODO_DEMO) return chamarDemo(acao, params || {});
    var corpo = Object.assign({ senha: estado.senha, acao: acao }, params || {});
    var ctrl = new AbortController();
    var timer = setTimeout(function () { ctrl.abort(); }, timeout || TIMEOUT_PADRAO);
    /* text/plain evita o preflight de CORS; o Apps Script le e.postData.contents */
    return fetch(URL_API, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(corpo),
      signal: ctrl.signal
    }).then(function (r) { return r.text(); }, function () {
      throw falha('rede', 'A planilha não respondeu. Verifique a conexão e tente de novo.');
    }).then(function (texto) {
      var json;
      try { json = JSON.parse(texto); } catch (e) { throw falha('formato', 'O Web App não respondeu no formato esperado.'); }
      if (!json.ok) throw falha(json.erro || 'interno', json.mensagem || 'Erro no Web App.');
      return json;
    }).finally(function () { clearTimeout(timer); });
  }

  /* modo demonstracao: dados ficticios, grava so na memoria da aba */
  var demoVendas = null;
  function copia(x) { return JSON.parse(JSON.stringify(x)); }
  function chamarDemo(acao, p) {
    var carga = demoVendas ? Promise.resolve() : fetch('tests/fixtures/vendas.json')
      .then(function (r) { return r.json(); })
      .then(function (v) { demoVendas = v; });
    return carga.then(function () {
      return new Promise(function (ok) { setTimeout(ok, acao === 'atualizar' ? 1500 : 350); });
    }).then(function () {
      if (acao === 'listar' || acao === 'atualizar') {
        return { ok: true, vendas: copia(demoVendas), salesforceAtualizadoEm: new Date().toISOString() };
      }
      var v = demoVendas.filter(function (x) { return x.id === p.id; })[0];
      if (!v) throw falha('nao_encontrada', 'Essa venda não está mais no relatório.');
      if (acao === 'cancelar') v.cancelada = true;
      if (acao === 'reativar') v.cancelada = false;
      if (acao === 'editar') { v.observacao = String(p.observacao || '').trim(); v.retorno = String(p.retorno || '').trim(); }
      return { ok: true, venda: copia(v) };
    });
  }

  /* ---------- senha / sessao (spec 3) ---------- */
  function gateCarregando(sim) {
    var b = $('gate-entrar');
    b.disabled = sim;
    b.textContent = sim ? 'Entrando…' : 'Entrar';
  }
  function gateErro(msg) {
    $('gate-erro').hidden = !msg;
    $('gate-erro-txt').textContent = msg || '';
    $('gate-senha').setAttribute('aria-invalid', msg ? 'true' : 'false');
  }
  function mostrarGate(msg) {
    $('app').hidden = true;
    $('gate').hidden = false;
    $('gate-demo').hidden = !MODO_DEMO;
    gateCarregando(false);
    gateErro(msg);
    $('gate-senha').value = '';
    $('gate-senha').focus();
  }
  function mostrarApp() {
    $('gate').hidden = true;
    $('app').hidden = false;
    $('aviso-demo').hidden = !MODO_DEMO;
  }
  function fecharDialogos() {
    ['dlg-cancelar', 'folha-filtros', 'painel'].forEach(function (id) {
      var d = $(id);
      if (d.open) d.close();
    });
  }
  function sair(msg) {
    try { sessionStorage.removeItem(CHAVE_SESSAO); } catch (e) { /* ignora */ }
    estado.senha = '';
    estado.vendas = [];
    fecharDialogos();
    mostrarGate(msg);
  }

  function iniciarGate() {
    $('gate-form').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var senha = $('gate-senha').value;
      if (!senha) { $('gate-senha').focus(); return; }
      estado.senha = senha;
      gateCarregando(true);
      gateErro('');
      chamar('listar').then(function (res) {
        try { sessionStorage.setItem(CHAVE_SESSAO, senha); } catch (e) { /* ignora */ }
        mostrarApp();
        receberLista(res);
      }).catch(function (f) {
        estado.senha = '';
        gateCarregando(false);
        gateErro(f.codigo === 'senha' ? MSG_SENHA : f.mensagem);
        $('gate-senha').select();
      });
    });
    $('gate-olho').addEventListener('click', function () {
      var campo = $('gate-senha');
      var mostrar = campo.type === 'password';
      campo.type = mostrar ? 'text' : 'password';
      this.setAttribute('aria-pressed', mostrar ? 'true' : 'false');
      this.setAttribute('aria-label', mostrar ? 'Ocultar senha' : 'Mostrar senha');
    });
  }

  /* ---------- carga ---------- */
  function mostrarEstadoLista(qual) {
    $('carregando').hidden = qual !== 'carregando';
    $('erro-lista').hidden = qual !== 'erro';
    $('conteudo-lista').hidden = qual !== 'ok';
  }
  function carregar() {
    mostrarEstadoLista('carregando');
    chamar('listar').then(receberLista).catch(function (f) {
      if (f.codigo === 'senha') { sair(MSG_SENHA); return; }
      $('erro-lista-txt').textContent = f.mensagem;
      mostrarEstadoLista('erro');
    });
  }
  function receberLista(res) {
    estado.vendas = res.vendas || [];
    estado.salesforceAtualizadoEm = res.salesforceAtualizadoEm || null;
    preencherOpcoes();
    renderCabecalho();
    mostrarEstadoLista('ok');
    render();
    /* painel aberto durante um "Atualizar": troca pela versao nova da venda */
    if (estado.aberta) {
      var fresca = vendaPorId(estado.aberta.id);
      if (fresca) { var sujo = painelSujo(); estado.aberta = fresca; preencherPainel(fresca, !sujo); }
      else fecharPainel(true);
    }
  }
  function vendaPorId(id) {
    return estado.vendas.filter(function (v) { return v.id === id; })[0] || null;
  }
  function substituirVenda(venda) {
    for (var i = 0; i < estado.vendas.length; i++) {
      if (estado.vendas[i].id === venda.id) { estado.vendas[i] = venda; break; }
    }
    render();
  }
  function renderCabecalho() {
    $('hdr-atualizacao').textContent = P.formatarAtualizacao(estado.salesforceAtualizadoEm, new Date());
    $('hdr-dot').hidden = !estado.salesforceAtualizadoEm;
  }

  /* ---------- filtros ---------- */
  function preencherSelect(sel, opcoes, rotuloTodos) {
    var atual = sel.value;
    sel.textContent = '';
    sel.appendChild(new Option(rotuloTodos, ''));
    opcoes.forEach(function (o) { sel.appendChild(new Option(o.rotulo, o.valor)); });
    sel.value = opcoes.some(function (o) { return o.valor === atual; }) ? atual : '';
  }
  function faseMarcada(fase) {
    return estado.filtros.fases.some(function (x) { return P.normalizar(x) === P.normalizar(fase); });
  }
  function preencherOpcoes() {
    var o = P.opcoesDeFiltro(estado.vendas);
    preencherSelect($('f-emp'), o.empreendimentos.map(function (e) { return { valor: e, rotulo: e }; }), 'Todos');
    preencherSelect($('f-eq'), o.equipes, 'Todas');
    estado.filtros.empreendimento = $('f-emp').value;
    estado.filtros.equipe = $('f-eq').value;
    var lista = $('f-fase-lista');
    lista.textContent = '';
    o.fases.forEach(function (fase) {
      var rotulo = el('label', 'multi-op');
      var cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.value = fase;
      cb.checked = faseMarcada(fase);
      cb.addEventListener('change', lerFases);
      rotulo.appendChild(cb);
      rotulo.appendChild(el('span', null, fase));
      lista.appendChild(rotulo);
    });
    atualizarResumoFases();
  }
  function lerFases() {
    estado.filtros.fases = Array.prototype.filter.call($('f-fase-lista').querySelectorAll('input'), function (c) {
      return c.checked;
    }).map(function (c) { return c.value; });
    atualizarResumoFases();
    render();
  }
  function atualizarResumoFases() {
    var f = estado.filtros.fases;
    var txt;
    if (!f.length) txt = 'Todas as fases';
    else if (P.mesmasFases(f, P.FASES_PADRAO)) txt = f.length + ' fases (padrão)';
    else if (f.length === 1) txt = f[0];
    else txt = f.length + ' fases';
    $('f-fase-resumo-txt').textContent = txt;
  }
  function ligarSelect(id, campo) {
    $(id).addEventListener('change', function () { estado.filtros[campo] = this.value; render(); });
  }
  function limparFiltros() {
    estado.filtros = P.filtrosPadrao();
    $('f-busca').value = '';
    $('f-emp').value = '';
    $('f-eq').value = '';
    $('f-per').value = 'todo';
    $('f-de').value = '';
    $('f-ate').value = '';
    $('intervalo').hidden = true;
    $('f-rank').value = '';
    $('f-tipo').value = 'todas';
    $('f-canceladas').checked = false;
    Array.prototype.forEach.call($('f-fase-lista').querySelectorAll('input'), function (c) { c.checked = faseMarcada(c.value); });
    atualizarResumoFases();
    render();
  }
  function iniciarFiltros() {
    var timer;
    $('f-busca').addEventListener('input', function () {
      var valor = this.value;
      clearTimeout(timer);
      timer = setTimeout(function () { estado.filtros.busca = valor; render(); }, 150);
    });
    ligarSelect('f-emp', 'empreendimento');
    ligarSelect('f-eq', 'equipe');
    ligarSelect('f-rank', 'ranking');
    ligarSelect('f-tipo', 'tipo');
    ligarSelect('f-de', 'de');
    ligarSelect('f-ate', 'ate');
    $('f-per').addEventListener('change', function () {
      estado.filtros.periodo = this.value;
      $('intervalo').hidden = this.value !== 'intervalo';
      render();
    });
    $('f-ord').addEventListener('change', function () { estado.ordem = this.value; render(); });
    $('f-canceladas').addEventListener('change', function () { estado.filtros.mostrarCanceladas = this.checked; render(); });
    $('limpar-filtros').addEventListener('click', limparFiltros);
    $('vazio-limpar').addEventListener('click', limparFiltros);
    Array.prototype.forEach.call(document.querySelectorAll('[data-pendencia]'), function (b) {
      b.addEventListener('click', function () { estado.filtros.pendencia = b.getAttribute('data-pendencia'); render(); });
    });
    document.addEventListener('click', function (ev) {
      var d = $('f-fase');
      if (d.open && !d.contains(ev.target)) d.open = false;
    });
  }

  /* ---------- render ---------- */
  function marcarAtivos() {
    var f = estado.filtros;
    $('f-emp').classList.toggle('ativo', !!f.empreendimento);
    $('f-eq').classList.toggle('ativo', !!f.equipe);
    $('f-fase-resumo').classList.toggle('ativo', f.fases.length > 0);
    $('f-per').classList.toggle('ativo', f.periodo !== 'todo');
    $('f-rank').classList.toggle('ativo', !!f.ranking);
    $('f-tipo').classList.toggle('ativo', f.tipo !== 'todas');
  }
  function renderKpis(k) {
    var f = estado.filtros;
    $('kpi-total').textContent = k.total;
    $('kpi-total-sub').textContent = plural(k.canceladasOcultas, 'cancelada', 'canceladas') +
      (f.mostrarCanceladas ? ' na lista' : (k.canceladasOcultas === 1 ? ' oculta' : ' ocultas'));
    $('kpi-ac').textContent = k.ac;
    $('kpi-ac-sub').textContent = plural(k.acReprovadas, 'reprovada', 'reprovadas') + ' · ' + k.acOutras + ' em análise ou não enviadas';
    $('kpi-fid').textContent = k.fid;
    $('kpi-fid-sub').textContent = k.fidPct + '% das vendas';
    $('kpi-ato').textContent = k.ato;
    $('kpi-pcv').textContent = k.pcv;
    $('kpi-vgv').textContent = P.formatarMi(k.vgv);
    $('chip-n-todas').textContent = k.total;
    $('chip-n-ac').textContent = k.ac;
    $('chip-n-fid').textContent = k.fid;
    $('chip-n-ato').textContent = k.ato;
    $('chip-n-pcv').textContent = k.pcv;
    $('canceladas-n').textContent = '(' + k.canceladasOcultas + ')';
    Array.prototype.forEach.call(document.querySelectorAll('.fchip[data-pendencia]'), function (b) {
      var on = b.getAttribute('data-pendencia') === f.pendencia;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    Array.prototype.forEach.call(document.querySelectorAll('.kpi[data-pendencia]'), function (b) {
      var on = f.pendencia !== 'todas' && b.getAttribute('data-pendencia') === f.pendencia;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }
  function chipsPendencia(v) {
    var box = el('span', 'chips');
    var itens = P.derivarPendencias(v);
    if (!itens.length) box.appendChild(el('span', 'chip c-ok', 'Nada pendente'));
    itens.forEach(function (p) { box.appendChild(el('span', 'chip c-' + p.estilo, p.rotulo)); });
    return box;
  }
  function diasDaVenda(v, hoje) {
    var dias = P.diasEmAberto(v.dataVenda, hoje);
    return { texto: P.textoDias(dias), alerta: dias !== null && dias >= P.DIAS_ALERTA };
  }
  function linhaTabela(v, hoje) {
    var tr = el('tr', v.cancelada ? 'cancelada' : '');
    tr.setAttribute('data-abrir', v.id);

    var td1 = el('td');
    td1.appendChild(el('div', 'num', v.dataVenda || '—'));
    var d = diasDaVenda(v, hoje);
    var dias = el('div', 'dias' + (d.alerta ? ' alerta' : ''));
    dias.appendChild(icone('relogio', 13));
    dias.appendChild(document.createTextNode(d.texto));
    td1.appendChild(dias);

    var td2 = el('td');
    td2.appendChild(el('div', 'nome', P.titleCase(v.cliente)));
    var meta = el('div', 'meta');
    meta.appendChild(el('span', 'num', v.id));
    if (v.vendaFacilitada) meta.appendChild(el('span', 'chip c-neu chip-p', 'Facilitada'));
    if (v.cancelada) meta.appendChild(el('span', 'chip c-err chip-p', 'Cancelada'));
    td2.appendChild(meta);
    var nota = P.notaDaLinha(v);
    if (nota) {
      var n = el('div', 'nota');
      n.title = nota;
      n.appendChild(icone('nota', 13));
      n.appendChild(el('span', 'ell', nota));
      td2.appendChild(n);
    }

    var td3 = el('td');
    td3.appendChild(el('div', null, v.empreendimento || '—'));
    if (v.identificador) td3.appendChild(el('div', 'sub num', 'Unidade ' + v.identificador));

    var td4 = el('td', 'equipe', P.formatarEquipe(v.imobiliaria));
    var td5 = el('td');
    td5.appendChild(chipsPendencia(v));
    var ac = P.statusAcBadge(v);
    var td6 = el('td');
    td6.appendChild(el('span', 'chip c-' + ac.estilo, ac.rotulo));
    var td7 = el('td', 'valor num', P.formatarValor(v.valorReal, false));
    var td8 = el('td', 'abrir');
    var b = el('button', 'btn btn-i btn-fantasma');
    b.type = 'button';
    b.setAttribute('aria-label', 'Abrir venda ' + v.id);
    b.appendChild(icone('seta', 18));
    td8.appendChild(b);

    [td1, td2, td3, td4, td5, td6, td7, td8].forEach(function (td) { tr.appendChild(td); });
    return tr;
  }
  function cartao(v, hoje) {
    var c = el('button', 'vc' + (v.cancelada ? ' cancelada' : ''));
    c.type = 'button';
    c.setAttribute('data-abrir', v.id);
    var topo = el('span', 'vc-topo');
    var id = el('span', 'vc-id');
    id.appendChild(el('span', 'nome', P.titleCase(v.cliente)));
    id.appendChild(el('span', 'sub num', [v.id, v.empreendimento, v.identificador].filter(Boolean).join(' · ')));
    topo.appendChild(id);
    topo.appendChild(icone('seta', 18));
    c.appendChild(topo);
    var chips = chipsPendencia(v);
    if (v.cancelada) chips.insertBefore(el('span', 'chip c-err', 'Cancelada'), chips.firstChild);
    c.appendChild(chips);
    var nota = P.notaDaLinha(v);
    if (nota) c.appendChild(el('span', 'vc-nota ell', nota));
    var rodape = el('span', 'vc-rodape');
    var quando = el('span', 'num');
    var d = diasDaVenda(v, hoje);
    if (v.dataVenda) {
      quando.appendChild(el('span', 'sub', v.dataVenda.slice(0, 5) + ' · '));
      quando.appendChild(el('span', d.alerta ? 'alerta' : '', d.texto));
    } else {
      quando.appendChild(el('span', 'sub', 'Sem data da venda'));
    }
    rodape.appendChild(quando);
    rodape.appendChild(el('span', 'num valor', P.formatarValor(v.valorReal, false)));
    c.appendChild(rodape);
    return c;
  }
  function render() {
    var hoje = new Date();
    var f = estado.filtros;
    renderKpis(P.calcularKpis(estado.vendas, f, hoje));
    marcarAtivos();
    var n = P.contarFiltrosAtivos(f);
    $('btn-filtros-txt').textContent = n ? 'Filtros · ' + n : 'Filtros';
    $('btn-filtros').classList.toggle('ativo', n > 0);

    var lista = P.ordenar(P.aplicarFiltros(estado.vendas, f, hoje), estado.ordem);
    $('contagem').textContent = plural(lista.length, 'venda', 'vendas');
    $('contagem-ordem').textContent = ' · ' + ROTULOS_ORDEM[estado.ordem];
    var corpo = $('tabela-corpo');
    var cartoes = $('cartoes');
    corpo.textContent = '';
    cartoes.textContent = '';
    lista.forEach(function (v) {
      corpo.appendChild(linhaTabela(v, hoje));
      cartoes.appendChild(cartao(v, hoje));
    });
    $('vazio').hidden = lista.length > 0;
    $('lista').hidden = lista.length === 0;
  }

  /* ---------- avisos (toast) ----------
     popover="manual": entra na top layer DEPOIS do dialogo modal aberto,
     entao aparece por cima dele. Sem suporte a popover, so a classe. */
  var toastTimer;
  function esconderToast() {
    var t = $('toast');
    t.classList.remove('visivel');
    if (t.hidePopover && t.matches(':popover-open')) t.hidePopover();
  }
  function toast(msg, opcoes) {
    opcoes = opcoes || {};
    var t = $('toast');
    esconderToast();
    t.textContent = '';
    t.className = 'toast' + (opcoes.erro ? ' erro' : '');
    t.appendChild(icone(opcoes.erro ? 'alerta' : 'check', 18));
    t.appendChild(el('span', null, msg));
    if (opcoes.acao) {
      var b = el('button', 'toast-acao', opcoes.acao.rotulo);
      b.type = 'button';
      b.addEventListener('click', function () { esconderToast(); opcoes.acao.fn(); });
      t.appendChild(b);
    }
    t.classList.add('visivel');
    if (t.showPopover) t.showPopover();
    clearTimeout(toastTimer);
    toastTimer = setTimeout(esconderToast, opcoes.acao ? 8000 : 5000);
  }

  function tratarFalhaAcao(f) {
    if (f.codigo === 'senha') { sair(MSG_SENHA); return; }
    if (f.codigo === 'nao_encontrada') {
      toast(f.mensagem || 'Essa venda não está mais no relatório.', { erro: true });
      fecharPainel(true);
      carregar();
      return;
    }
    toast(f.mensagem || 'Não deu para salvar. Tente de novo.', { erro: true });
  }
  function exigirLivre() {
    if (!estado.atualizando) return true;
    toast('Aguarde a atualização do Salesforce terminar.', { erro: true });
    return false;
  }

  /* ---------- painel de detalhe (spec 6) ---------- */
  function painelSujo() {
    var v = estado.aberta;
    if (!v) return false;
    return $('dt-obs').value !== (v.observacao || '') || $('dt-ret').value !== (v.retorno || '');
  }
  function atualizarBotoesPainel() {
    var sujo = painelSujo();
    $('dt-salvar').disabled = !sujo || estado.atualizando;
    $('dt-descartar').disabled = !sujo;
    $('dt-cancelar').disabled = estado.atualizando;
  }
  function preencherPainel(v, resetarCampos) {
    var hoje = new Date();
    $('dt-op').textContent = v.id;
    $('dt-nome').textContent = P.titleCase(v.cliente);
    $('dt-sub').textContent = [
      v.empreendimento, v.identificador ? 'Unidade ' + v.identificador : '', P.formatarEquipe(v.imobiliaria)
    ].filter(Boolean).join(' · ');
    var tags = $('dt-tags');
    tags.textContent = '';
    [v.fase, v.vendaFacilitada ? 'Venda facilitada' : 'Venda comercial', v.ranking ? 'Ranking ' + P.rankingRotulo(v.ranking) : '']
      .filter(Boolean)
      .forEach(function (t) { tags.appendChild(el('span', 'chip c-neu', t)); });
    if (v.cancelada) tags.appendChild(el('span', 'chip c-err', 'Cancelada'));

    $('dt-data').textContent = v.dataVenda || '—';
    var d = diasDaVenda(v, hoje);
    $('dt-dias').textContent = d.texto;
    $('dt-dias-cel').classList.toggle('alerta', d.alerta);
    $('dt-valor').textContent = P.formatarValor(v.valorReal, true);
    $('dt-fid').textContent = String(v.fid || '').trim() || '—';

    var itens = P.checklist(v);
    var faltam = itens.filter(function (i) { return !i.ok; }).length;
    $('dt-faltam').textContent = faltam ? faltam + ' de ' + itens.length + ' itens pendentes' : 'Nada pendente';
    var ul = $('dt-checklist');
    ul.textContent = '';
    itens.forEach(function (it) {
      var li = el('li', 'ck' + (it.ok ? ' ok' : ''));
      var bola = el('span', 'ci ci-' + it.estilo);
      bola.appendChild(icone(it.ok ? 'check' : (it.estilo === 'err' ? 'x' : 'alerta'), 14));
      var txt = el('div');
      txt.appendChild(el('div', 'ck-t', it.titulo));
      txt.appendChild(el('div', 'sub', it.detalhe));
      li.appendChild(bola);
      li.appendChild(txt);
      ul.appendChild(li);
    });

    $('dt-just').textContent = P.justificativaExibida(v.justificativa);
    if (resetarCampos) {
      $('dt-obs').value = v.observacao || '';
      $('dt-ret').value = v.retorno || '';
    }
    $('dt-cancelar-txt').textContent = v.cancelada ? 'Reativar venda' : 'Marcar como cancelada';
    $('dt-cancelar').classList.toggle('btn-d', !v.cancelada);
    atualizarBotoesPainel();
  }
  function abrirPainel(id) {
    var v = vendaPorId(id);
    if (!v) return;
    estado.aberta = v;
    preencherPainel(v, true);
    if (!$('painel').open) $('painel').showModal();
  }
  function fecharPainel(forcar) {
    var d = $('painel');
    if (!d.open) return true;
    if (!forcar && painelSujo() && !window.confirm('Descartar as alterações em Observação e Retorno?')) return false;
    d.close();
    return true;
  }
  /* devolve o foco para a linha/cartao visivel da venda que estava aberta */
  function focarOrigem(id) {
    var alvos = document.querySelectorAll('[data-abrir]');
    for (var i = 0; i < alvos.length; i++) {
      var a = alvos[i];
      if (a.getAttribute('data-abrir') !== id || a.offsetParent === null) continue;
      (a.tagName === 'TR' ? a.querySelector('button') : a).focus();
      return;
    }
  }

  function salvar() {
    if (!exigirLivre()) return;
    var v = estado.aberta;
    var b = $('dt-salvar');
    b.disabled = true;
    b.textContent = 'Salvando…';
    chamar('editar', { id: v.id, observacao: $('dt-obs').value, retorno: $('dt-ret').value })
      .then(function (res) {
        estado.aberta = res.venda;
        substituirVenda(res.venda);
        preencherPainel(res.venda, true);
        toast('Alterações salvas na planilha');
      })
      .catch(tratarFalhaAcao)
      .then(function () { b.textContent = 'Salvar alterações'; atualizarBotoesPainel(); });
  }

  function mudarCancelamento(id, acao) {
    var b = $('dt-cancelar');
    if (estado.aberta && estado.aberta.id === id) b.disabled = true;
    return chamar(acao, { id: id }).then(function (res) {
      substituirVenda(res.venda);
      if (estado.aberta && estado.aberta.id === id) {
        estado.aberta = res.venda;
        preencherPainel(res.venda, false);
      }
      if (acao === 'cancelar') {
        fecharPainel(true);
        toast('Venda ' + id + ' cancelada', {
          acao: { rotulo: 'Desfazer', fn: function () { mudarCancelamento(id, 'reativar'); } }
        });
      } else {
        toast('Venda ' + id + ' reativada');
      }
    }).catch(tratarFalhaAcao).then(function () { atualizarBotoesPainel(); });
  }
  function clicarCancelar() {
    if (!exigirLivre()) return;
    var v = estado.aberta;
    if (v.cancelada) { mudarCancelamento(v.id, 'reativar'); return; }
    if (painelSujo()) {
      toast('Salve ou descarte as alterações antes de cancelar a venda.', { erro: true });
      return;
    }
    $('cx-nome').textContent = P.titleCase(v.cliente);
    $('cx-meta').textContent = [v.id, v.empreendimento, v.identificador].filter(Boolean).join(' · ');
    $('cx-valor').textContent = P.formatarValor(v.valorReal, false);
    $('dlg-cancelar').showModal();
  }

  function copiarOp() {
    var id = estado.aberta && estado.aberta.id;
    if (!id) return;
    var p = navigator.clipboard ? navigator.clipboard.writeText(id) : Promise.reject();
    p.then(function () { toast('OP ' + id + ' copiada'); }, function () { toast('Não deu para copiar. OP: ' + id, { erro: true }); });
  }

  /* ---------- atualizar do Salesforce (spec 4.4) ---------- */
  function atualizarSalesforce() {
    if (estado.atualizando) return;
    estado.atualizando = true;
    var b = $('btn-atualizar');
    b.disabled = true;
    $('btn-atualizar-txt').textContent = 'Atualizando…';
    $('faixa-atualizando').hidden = false;
    atualizarBotoesPainel();
    chamar('atualizar', null, TIMEOUT_ATUALIZAR)
      .then(function (res) { receberLista(res); toast('Relatório atualizado do Salesforce'); })
      .catch(function (f) {
        if (f.codigo === 'rede') f.mensagem = 'A atualização não terminou a tempo. Rode "Atualizar Relatório" pelo menu Salesforce da planilha.';
        tratarFalhaAcao(f);
      })
      .then(function () {
        estado.atualizando = false;
        b.disabled = false;
        $('btn-atualizar-txt').textContent = 'Atualizar do Salesforce';
        $('faixa-atualizando').hidden = true;
        atualizarBotoesPainel();
      });
  }

  function iniciarPainel() {
    function abrirPorClique(ev) {
      var alvo = ev.target.closest('[data-abrir]');
      if (alvo) abrirPainel(alvo.getAttribute('data-abrir'));
    }
    $('tabela-corpo').addEventListener('click', abrirPorClique);
    $('cartoes').addEventListener('click', abrirPorClique);

    var painel = $('painel');
    painel.addEventListener('cancel', function (ev) { ev.preventDefault(); fecharPainel(false); });
    painel.addEventListener('click', function (ev) { if (ev.target === painel) fecharPainel(false); });
    painel.addEventListener('close', function () {
      var id = estado.aberta && estado.aberta.id;
      estado.aberta = null;
      if (id) focarOrigem(id);
    });
    $('dt-fechar').addEventListener('click', function () { fecharPainel(false); });
    $('dt-obs').addEventListener('input', atualizarBotoesPainel);
    $('dt-ret').addEventListener('input', atualizarBotoesPainel);
    $('dt-descartar').addEventListener('click', function () { preencherPainel(estado.aberta, true); });
    $('dt-salvar').addEventListener('click', salvar);
    $('dt-cancelar').addEventListener('click', clicarCancelar);
    $('dt-copiar').addEventListener('click', copiarOp);

    $('cx-voltar').addEventListener('click', function () { $('dlg-cancelar').close(); });
    $('cx-confirmar').addEventListener('click', function () {
      $('dlg-cancelar').close();
      if (estado.aberta) mudarCancelamento(estado.aberta.id, 'cancelar');
    });
    $('btn-atualizar').addEventListener('click', atualizarSalesforce);
  }

  /* ---------- filtros no celular (folha inferior) ----------
     Os MESMOS elementos de filtro mudam de lugar: vao para a folha ao abrir
     e voltam para o card ao fechar (nada duplicado, nada a sincronizar). */
  function abrirFolhaFiltros() {
    var corpo = $('folha-corpo');
    corpo.appendChild($('filtros-grid'));
    corpo.appendChild($('filtros-extra'));
    $('folha-filtros').showModal();
  }
  function devolverFiltros() {
    $('filtros-topo').insertBefore($('filtros-grid'), $('btn-filtros'));
    $('filtros-pend').appendChild($('filtros-extra'));
  }
  function iniciarFolhaFiltros() {
    var folha = $('folha-filtros');
    $('btn-filtros').addEventListener('click', abrirFolhaFiltros);
    $('folha-fechar').addEventListener('click', function () { folha.close(); });
    $('folha-aplicar').addEventListener('click', function () { folha.close(); });
    folha.addEventListener('click', function (ev) { if (ev.target === folha) folha.close(); });
    folha.addEventListener('close', devolverFiltros);
  }

  /* ---------- inicio ---------- */
  function iniciar() {
    iniciarGate();
    iniciarFiltros();
    iniciarPainel();
    iniciarFolhaFiltros();
    $('btn-sair').addEventListener('click', function () { sair(); });
    $('erro-lista-tentar').addEventListener('click', carregar);
    var salva = null;
    try { salva = sessionStorage.getItem(CHAVE_SESSAO); } catch (e) { /* ignora */ }
    if (salva) { estado.senha = salva; mostrarApp(); carregar(); }
    else mostrarGate();
  }
  iniciar();
})();

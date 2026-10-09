/* ============================================================
   VISITAS DA RECEPCAO - interface de /visitas-recepcao
   ------------------------------------------------------------
   Lancamento publico de visitas no stand + contador do dia.
   Regras em assets/visitas.js; API em assets/visitas-api.js.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md (secao 5)
   ============================================================ */
(function () {
  'use strict';

  var V = window.Visitas;
  var api = window.VisitasAPI.criar({ url: window.VISITAS_APPS_SCRIPT_URL || '' });
  var EMPS = V.listaEmpreendimentos(window.CITIES || []);
  var CHAVE_EMP = 'visitas.emp';
  var CHAVE_TOKENS = 'visitas.tokens';
  var INTERVALO_DIA = 60000;
  var TEXTO_BOTAO = {
    empreendimento: 'Escolha o empreendimento',
    data: 'Informe a data',
    hora: 'Informe o horário',
    tipo: 'Escolha o tipo de visita',
    imobiliaria: 'Informe a imobiliária'
  };
  var CAMPO_ID = { empreendimento: 'emp', data: 'data', hora: 'hora', imobiliaria: 'imob' };
  var estado = { tipo: null, enviando: false, ultimo: null, timerFaixa: null, seqDia: 0 };

  function $(id) { return document.getElementById(id); }
  function hoje() { return V.dataLocalIso(new Date()); }
  function lerLS(chave, padrao) {
    try { var v = localStorage.getItem(chave); return v === null ? padrao : JSON.parse(v); } catch (e) { return padrao; }
  }
  function gravarLS(chave, valor) {
    try { localStorage.setItem(chave, JSON.stringify(valor)); } catch (e) { /* ignora */ }
  }

  /* ---------- tokens de exclusao (spec 4.3): so os de hoje ---------- */
  function lerTokens() {
    var t = lerLS(CHAVE_TOKENS, {}) || {}, h = hoje(), limpo = {};
    Object.keys(t).forEach(function (id) { if (t[id] && t[id].data === h) limpo[id] = t[id]; });
    return limpo;
  }
  function guardarToken(id, token) { var t = lerTokens(); t[id] = { token: token, data: hoje() }; gravarLS(CHAVE_TOKENS, t); }
  function esquecerToken(id) { var t = lerTokens(); delete t[id]; gravarLS(CHAVE_TOKENS, t); }

  /* ---------- formulario ---------- */
  function montarEmpreendimentos() {
    var sel = $('emp');
    (window.CITIES || []).forEach(function (c) {
      var grupo = document.createElement('optgroup');
      grupo.label = c.name;
      (c.empreendimentos || []).forEach(function (e) {
        var o = document.createElement('option');
        o.value = e.nome;
        o.textContent = e.nome;
        grupo.appendChild(o);
      });
      sel.appendChild(grupo);
    });
    var salvo = lerLS(CHAVE_EMP, null);
    if (salvo && EMPS.some(function (e) { return e.nome === salvo; })) sel.value = salvo;
  }

  function lerForm() {
    return {
      empreendimento: $('emp').value, data: $('data').value, hora: $('hora').value, tipo: estado.tipo,
      corretorHouse: $('corretor-house').value, imobiliaria: $('imob').value, corretorImob: $('corretor-imob').value
    };
  }

  function marcarInvalido(campo) {
    ['emp', 'data', 'hora', 'imob'].forEach(function (id) {
      $(id).setAttribute('aria-invalid', CAMPO_ID[campo] === id ? 'true' : 'false');
    });
  }

  function atualizarBotao() {
    var f = V.validarFormulario(lerForm());
    $('registrar').disabled = estado.enviando || !f.ok;
    $('registrar-txt').textContent = estado.enviando ? 'Registrando…' : f.ok ? 'Registrar visita' : TEXTO_BOTAO[f.faltando];
  }

  function escolherTipo(tipo) {
    estado.tipo = tipo;
    Array.prototype.forEach.call(document.querySelectorAll('.tipo'), function (b) {
      b.setAttribute('aria-checked', b.getAttribute('data-tipo') === tipo ? 'true' : 'false');
    });
    $('extra-house').hidden = tipo !== 'house';
    $('extra-imob').hidden = tipo !== 'imob';
    atualizarBotao();
  }

  function limparTipo() {
    $('corretor-house').value = '';
    $('imob').value = '';
    $('corretor-imob').value = '';
    escolherTipo(null);
  }

  /* ---------- faixa de retorno (spec 5.2) ---------- */
  function mostrarFaixa(tipo, titulo, texto, comDesfazer) {
    clearTimeout(estado.timerFaixa);
    $('faixa').className = 'faixa ' + tipo;
    $('faixa-ico-ok').style.display = tipo === 'ok' ? '' : 'none';
    $('faixa-ico-err').style.display = tipo === 'ok' ? 'none' : '';
    $('faixa-titulo').textContent = titulo;
    $('faixa-texto').textContent = texto;
    $('faixa-desfazer').hidden = !comDesfazer;
    $('faixa').hidden = false;
    if (tipo === 'ok') estado.timerFaixa = setTimeout(esconderFaixa, 8000);
  }
  function esconderFaixa() {
    clearTimeout(estado.timerFaixa);
    $('faixa').hidden = true;
    estado.ultimo = null;
  }

  /* ---------- acoes ---------- */
  function registrar() {
    var dados = lerForm();
    if (estado.enviando || !V.validarFormulario(dados).ok) return;
    estado.enviando = true;
    atualizarBotao();
    marcarInvalido(null);
    api.chamar('registrar', dados).then(function (r) {
      guardarToken(r.visita.id, r.token);
      mostrarFaixa('ok', 'Visita registrada',
        [r.visita.hora, V.TIPOS[r.visita.tipo].nome, r.visita.empreendimento].join(' · '), true);
      estado.ultimo = r.visita;
      limparTipo();
      $('hora').value = V.horaLocal(new Date());
      carregarDia();
    }, function (f) {
      marcarInvalido(f.campo);
      mostrarFaixa('err', 'A visita não foi registrada', f.mensagem, false);
    }).then(function () {
      estado.enviando = false;
      atualizarBotao();
    });
  }

  function excluir(id) {
    var t = lerTokens()[id];
    if (!t) return Promise.resolve();
    return api.chamar('excluir', { id: id, token: t.token }).then(function () {
      esquecerToken(id);
    }, function (f) {
      mostrarFaixa('err', 'Não foi possível excluir este lançamento',
        f.codigo === 'nao_encontrada' ? 'Ele pode já ter sido excluído.' : f.mensagem, false);
    }).then(carregarDia);
  }

  function desfazer() {
    var v = estado.ultimo;
    if (!v) return;
    esconderFaixa();
    excluir(v.id);
  }

  /* ---------- contador do dia (spec 5.3) ---------- */
  function carregarDia() {
    var emp = $('emp').value, data = $('data').value;
    if (!emp || !data) return;
    var seq = ++estado.seqDia;
    api.chamar('dia', { empreendimento: emp, data: data }).then(function (r) {
      if (seq !== estado.seqDia) return;
      var visitas = (r.visitas || []).filter(function (v) { return V.TIPOS[v.tipo]; });
      renderContador(visitas, emp, data);
      renderSugestoes(r.sugestoesImob || []);
      $('cont-erro').hidden = true;
    }, function (f) {
      if (seq !== estado.seqDia) return;
      $('cont-erro').textContent = f.mensagem;
      $('cont-erro').hidden = false;
    });
  }

  function renderContador(visitas, emp, data) {
    var t = V.totaisPorTipo(visitas), eHoje = data === hoje();
    $('cont-titulo').textContent = (eHoje ? 'Visitas hoje · ' : 'Visitas em ') + V.dataCurta(data);
    $('cont-emp').textContent = emp;
    $('cont-total').textContent = t.total;
    $('cont-total-lab').textContent = t.total === 1 ? 'visita registrada' : 'visitas registradas';
    V.ORDEM_TIPOS.forEach(function (k) {
      $('q-' + k).textContent = t[k];
      $('b-' + k).style.width = (t.total ? Math.round(t[k] / t.total * 100) : 0) + '%';
    });
    var tokens = lerTokens(), ul = $('ultimos');
    ul.textContent = '';
    V.recentes(visitas, 6).forEach(function (v) { ul.appendChild(itemLista(v, !!tokens[v.id])); });
    $('vazio').textContent = eHoje ? 'Nenhuma visita registrada hoje neste stand.' : 'Nenhuma visita registrada neste dia.';
    $('vazio').hidden = visitas.length > 0;
  }

  function el(tag, cls, texto) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }

  function iconeLixeira() {
    var ns = 'http://www.w3.org/2000/svg', s = document.createElementNS(ns, 'svg');
    [['width', '18'], ['height', '18'], ['viewBox', '0 0 24 24'], ['fill', 'none'], ['stroke', 'currentColor'],
      ['stroke-width', '1.8'], ['stroke-linecap', 'round'], ['stroke-linejoin', 'round'], ['aria-hidden', 'true']]
      .forEach(function (a) { s.setAttribute(a[0], a[1]); });
    var p = document.createElementNS(ns, 'path');
    p.setAttribute('d', 'M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3');
    s.appendChild(p);
    return s;
  }

  function itemLista(v, podeExcluir) {
    var li = el('li');
    var txt = el('span', 'lista-txt');
    var tipo = el('span', 'lista-tipo');
    var ponto = el('span', 'ponto');
    ponto.style.background = V.TIPOS[v.tipo].cor;
    tipo.appendChild(ponto);
    tipo.appendChild(document.createTextNode(V.TIPOS[v.tipo].nome));
    txt.appendChild(tipo);
    txt.appendChild(el('span', 'lista-det', V.detalhe(v)));
    li.appendChild(el('span', 'lista-hora num', v.hora));
    li.appendChild(txt);
    if (podeExcluir) {
      var b = el('button', 'btn btn-i');
      b.type = 'button';
      b.setAttribute('aria-label', 'Excluir lançamento das ' + v.hora);
      b.appendChild(iconeLixeira());
      b.addEventListener('click', function () {
        if (!window.confirm('Excluir o lançamento das ' + v.hora + ' (' + V.TIPOS[v.tipo].nome + ')?')) return;
        b.disabled = true;
        if (estado.ultimo && estado.ultimo.id === v.id) esconderFaixa();
        excluir(v.id);
      });
      li.appendChild(b);
    }
    return li;
  }

  function renderSugestoes(nomes) {
    var dl = $('lista-imob');
    dl.textContent = '';
    nomes.forEach(function (n) { var o = document.createElement('option'); o.value = n; dl.appendChild(o); });
  }

  /* ---------- inicio ---------- */
  function iniciar() {
    montarEmpreendimentos();
    $('data').value = hoje();
    $('data').max = hoje();
    $('data').min = V.somarDias(hoje(), -7);
    $('hora').value = V.horaLocal(new Date());
    $('aviso-demo').hidden = !api.demo;

    Array.prototype.forEach.call(document.querySelectorAll('.tipo'), function (b) {
      b.addEventListener('click', function () { escolherTipo(b.getAttribute('data-tipo')); });
    });
    $('agora').addEventListener('click', function () { $('hora').value = V.horaLocal(new Date()); atualizarBotao(); });
    $('emp').addEventListener('change', function () {
      gravarLS(CHAVE_EMP, $('emp').value);
      esconderFaixa();
      carregarDia();
      atualizarBotao();
    });
    $('data').addEventListener('change', function () { carregarDia(); atualizarBotao(); });
    ['hora', 'imob', 'corretor-house', 'corretor-imob'].forEach(function (id) {
      $(id).addEventListener('input', atualizarBotao);
    });
    $('registrar').addEventListener('click', registrar);
    $('faixa-desfazer').addEventListener('click', desfazer);
    /* soma lancamentos de outro aparelho no mesmo stand */
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'visible') carregarDia();
    });
    setInterval(function () { if (document.visibilityState === 'visible') carregarDia(); }, INTERVALO_DIA);

    escolherTipo(null);
    carregarDia();
  }

  iniciar();
})();

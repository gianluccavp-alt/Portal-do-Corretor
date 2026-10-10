/* ============================================================
   VISITAS DA RECEPCAO - interface de /visitas-recepcao
   ------------------------------------------------------------
   Stand (Passo 1), cards que abrem o popup de cadastro (Passo 2)
   e contador do dia. Regras em assets/visitas.js; API em
   assets/visitas-api.js.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md (secoes 5 e 13)
   ============================================================ */
(function () {
  'use strict';

  var V = window.Visitas;
  var api = window.VisitasAPI.criar({ url: window.VISITAS_APPS_SCRIPT_URL || '' });
  var EMPS = V.listaEmpreendimentos(window.CITIES || []);
  var CHAVE_EMP = 'visitas.emp';
  var CHAVE_TOKENS = 'visitas.tokens';
  var INTERVALO_DIA = 60000;
  var TITULO_TIPO = { esp: 'Espontânea', house: 'Agendada · Corretor house', imob: 'Imobiliária parceira' };
  var ROTULO_CORRETOR = { esp: 'Corretor que atendeu', house: 'Corretor house que agendou', imob: 'Corretor da imobiliária' };
  /* campo da API -> id do input no popup */
  var CAMPOS = {
    cliente: 'f-cliente', cpf: 'f-cpf', telefone: 'f-telefone', data: 'f-data',
    hora: 'f-hora', imobiliaria: 'f-imob', corretor: 'f-corretor'
  };
  var estado = { tipo: null, enviando: false, ultimo: null, timerFaixa: null, seqDia: 0, hojeAplicado: '' };

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

  /* ---------- stand ---------- */
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

  /* ---------- popup (spec 13.1) ---------- */
  function limparErro(id) {
    $(id).setAttribute('aria-invalid', 'false');
    $('e-' + id).textContent = '';
    $('e-' + id).hidden = true;
  }
  function limparErros() {
    Object.keys(CAMPOS).forEach(function (c) { limparErro(CAMPOS[c]); });
    $('p-erro').hidden = true;
  }
  function mostrarErro(campo, msg) {
    var id = CAMPOS[campo];
    if (!id) return false;
    $(id).setAttribute('aria-invalid', 'true');
    $('e-' + id).textContent = msg;
    $('e-' + id).hidden = false;
    return true;
  }
  function atualizarBotao() {
    $('p-registrar').disabled = estado.enviando;
    /* enviando: nao deixa fechar o popup nem perder a resposta */
    $('p-cancelar').disabled = estado.enviando;
    $('p-fechar').disabled = estado.enviando;
    $('p-registrar-txt').textContent = estado.enviando ? 'Registrando…' : 'Registrar visita';
  }
  function aplicarLimitesData(h) {
    $('f-data').max = h;
    $('f-data').min = V.somarDias(h, -7);
  }

  function abrirPopup(tipo) {
    if (estado.enviando) return;
    estado.tipo = tipo;
    $('p-tipo').textContent = TITULO_TIPO[tipo];
    $('p-ponto').style.background = V.TIPOS[tipo].cor;
    $('p-emp').textContent = $('emp').value;
    $('rot-corretor').textContent = ROTULO_CORRETOR[tipo];
    $('bloco-imob').hidden = tipo !== 'imob';
    ['f-cliente', 'f-cpf', 'f-telefone', 'f-imob', 'f-corretor', 'f-gerente'].forEach(function (id) { $(id).value = ''; });
    var h = hoje();
    aplicarLimitesData(h);
    $('f-data').value = h;
    $('f-hora').value = V.horaLocal(new Date());
    limparErros();
    atualizarBotao();
    $('popup').showModal();
    $('f-cliente').focus();
  }
  function fecharPopup() {
    if (estado.enviando) return;
    if ($('popup').open) $('popup').close();
  }

  function lerPopup() {
    return {
      empreendimento: $('emp').value, tipo: estado.tipo,
      cliente: $('f-cliente').value, cpf: $('f-cpf').value, telefone: $('f-telefone').value,
      data: $('f-data').value, hora: $('f-hora').value,
      imobiliaria: estado.tipo === 'imob' ? $('f-imob').value : '',
      corretor: $('f-corretor').value, gerente: $('f-gerente').value
    };
  }

  function registrar(ev) {
    if (ev) ev.preventDefault();
    if (estado.enviando) return;
    var dados = lerPopup();
    var r = V.validarVisita(dados);
    limparErros();
    if (!r.ok) {
      Object.keys(r.erros).forEach(function (c) {
        /* campo sem input no popup (ex: empreendimento) vai para a mensagem geral */
        if (!mostrarErro(c, r.erros[c])) { $('p-erro').textContent = r.erros[c]; $('p-erro').hidden = false; }
      });
      if (CAMPOS[r.primeiro]) $(CAMPOS[r.primeiro]).focus();
      return;
    }
    estado.enviando = true;
    atualizarBotao();
    api.chamar('registrar', dados).then(function (resp) {
      guardarToken(resp.visita.id, resp.token);
      estado.enviando = false;
      atualizarBotao();
      fecharPopup();
      var texto = [resp.visita.hora, V.TIPOS[resp.visita.tipo].nome, resp.visita.primeiroNome].join(' · ');
      if (resp.cpfRepetido) {
        mostrarFaixa('aviso', 'Visita registrada. Atenção: este CPF já tinha visita hoje neste stand.', texto, true);
      } else {
        mostrarFaixa('ok', 'Visita registrada', texto, true);
      }
      estado.ultimo = resp.visita;
      carregarDia();
    }, function (f) {
      if (f.codigo === 'invalido' && mostrarErro(f.campo, f.mensagem)) {
        $(CAMPOS[f.campo]).focus();
      } else {
        $('p-erro').textContent = f.mensagem;
        $('p-erro').hidden = false;
      }
    }).then(function () {
      estado.enviando = false;
      atualizarBotao();
    });
  }

  /* ---------- faixa de retorno (spec 5.2 e 13.1) ---------- */
  function mostrarFaixa(tipo, titulo, texto, comDesfazer) {
    clearTimeout(estado.timerFaixa);
    $('faixa').className = 'faixa ' + tipo;
    $('faixa-ico-ok').style.display = tipo === 'ok' ? '' : 'none';
    $('faixa-ico-err').style.display = tipo === 'ok' ? 'none' : '';
    $('faixa-titulo').textContent = titulo;
    $('faixa-texto').textContent = texto;
    $('faixa-desfazer').hidden = !comDesfazer;
    $('faixa').hidden = false;
    /* no celular a faixa fica no topo: traz para a tela */
    try { $('faixa').scrollIntoView({ block: 'nearest', behavior: 'smooth' }); } catch (e) { /* navegador antigo */ }
    if (tipo === 'ok') estado.timerFaixa = setTimeout(esconderFaixa, 8000);
  }
  function esconderFaixa() {
    clearTimeout(estado.timerFaixa);
    $('faixa').hidden = true;
    estado.ultimo = null;
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
    var emp = $('emp').value, data = hoje();
    if (!emp) return;
    var seq = ++estado.seqDia;
    api.chamar('dia', { empreendimento: emp, data: data }).then(function (r) {
      if (seq !== estado.seqDia) return;
      var visitas = (r.visitas || []).filter(function (v) { return V.TIPOS[v.tipo]; });
      renderContador(visitas, emp, data);
      renderSugestoes(r.sugestoes || {});
      $('cont-erro').hidden = true;
    }, function (f) {
      if (seq !== estado.seqDia) return;
      $('cont-erro').textContent = f.mensagem;
      $('cont-erro').hidden = false;
    });
  }

  function renderContador(visitas, emp, data) {
    var t = V.totaisPorTipo(visitas);
    $('cont-titulo').textContent = 'Visitas hoje · ' + V.dataCurta(data);
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
    $('vazio').textContent = 'Nenhuma visita registrada hoje neste stand.';
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
    tipo.appendChild(document.createTextNode((v.primeiroNome ? v.primeiroNome + ' · ' : '') + V.TIPOS[v.tipo].nome));
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

  function preencherLista(id, nomes) {
    var dl = $(id);
    dl.textContent = '';
    (nomes || []).forEach(function (n) { var o = document.createElement('option'); o.value = n; dl.appendChild(o); });
  }
  function renderSugestoes(s) {
    preencherLista('lista-imob', s.imobiliarias);
    preencherLista('lista-corretor', s.corretores);
    preencherLista('lista-gerente', s.gerentes);
  }

  /* ---------- virada do dia ---------- */
  /* tablet aberto de um dia pro outro: popup aberto nao pode gravar na data antiga */
  function checarVirada() {
    if (document.visibilityState !== 'visible') return;
    var h = hoje();
    if (estado.hojeAplicado && h !== estado.hojeAplicado && $('popup').open) {
      aplicarLimitesData(h);
      if ($('f-data').value === estado.hojeAplicado) {
        $('f-data').value = h;
        $('f-hora').value = V.horaLocal(new Date());
      }
    }
    estado.hojeAplicado = h;
    carregarDia();
  }

  /* ---------- inicio ---------- */
  function iniciar() {
    montarEmpreendimentos();
    estado.hojeAplicado = hoje();
    $('aviso-demo').hidden = !api.demo;

    Array.prototype.forEach.call(document.querySelectorAll('.tipo'), function (b) {
      b.addEventListener('click', function () { abrirPopup(b.getAttribute('data-tipo')); });
    });
    $('emp').addEventListener('change', function () {
      gravarLS(CHAVE_EMP, $('emp').value);
      esconderFaixa();
      carregarDia();
    });
    $('p-form').addEventListener('submit', registrar);
    $('p-cancelar').addEventListener('click', fecharPopup);
    $('p-fechar').addEventListener('click', fecharPopup);
    $('popup').addEventListener('cancel', function (ev) { if (estado.enviando) ev.preventDefault(); });
    $('popup').addEventListener('close', function () { estado.tipo = null; });
    $('f-agora').addEventListener('click', function () { $('f-hora').value = V.horaLocal(new Date()); limparErro('f-hora'); });
    $('f-cpf').addEventListener('input', function () { $('f-cpf').value = V.mascaraCpf($('f-cpf').value); });
    $('f-telefone').addEventListener('input', function () { $('f-telefone').value = V.mascaraTelefone($('f-telefone').value); });
    /* campo corrigido deixa de ficar marcado como invalido */
    Object.keys(CAMPOS).forEach(function (c) {
      var id = CAMPOS[c];
      $(id).addEventListener('input', function () { limparErro(id); });
      $(id).addEventListener('change', function () { limparErro(id); });
    });
    $('faixa-desfazer').addEventListener('click', desfazer);
    /* soma lancamentos de outro aparelho no mesmo stand */
    document.addEventListener('visibilitychange', checarVirada);
    setInterval(checarVirada, INTERVALO_DIA);

    carregarDia();
  }

  iniciar();
})();

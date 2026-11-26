/* ============================================================
   SELETOR - lista suspensa com o desenho do portal
   ------------------------------------------------------------
   Veste um <select> comum: ele continua no HTML (escondido) como fonte
   do valor e dispara "change" quando o usuario escolhe. Com o atributo
   "multiple" vira escolha multipla com caixas de marcar.
   Depois de trocar opcoes ou valor por codigo, chame .atualizar().
   Texto das opcoes entra sempre por textContent.
   ============================================================ */
(function (raiz) {
  'use strict';

  var BUSCA_A_PARTIR_DE = 10;
  var aberto = null;
  var SETA = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>';

  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt !== undefined) e.textContent = txt;
    return e;
  }
  function semAcento(s) { return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }

  function criar(select, opcoes) {
    opcoes = opcoes || {};
    var multi = select.multiple;
    var id = select.id;

    var caixa = el('div', 'sel');
    var botao = el('button', 'sel-botao');
    botao.type = 'button';
    botao.id = id + '-botao';
    botao.setAttribute('aria-haspopup', 'listbox');
    botao.setAttribute('aria-expanded', 'false');
    var valor = el('span', 'sel-valor');
    valor.id = id + '-valor';
    botao.appendChild(valor);
    botao.insertAdjacentHTML('beforeend', SETA);

    var painel = el('div', 'sel-painel');
    painel.hidden = true;
    var busca = el('input', 'inp sel-busca');
    busca.type = 'search';
    busca.placeholder = 'Buscar…';
    busca.setAttribute('aria-label', 'Buscar opção');
    busca.autocomplete = 'off';
    var lista = el('div', 'sel-lista');
    lista.setAttribute('role', 'listbox');
    lista.id = id + '-lista';
    if (multi) lista.setAttribute('aria-multiselectable', 'true');
    botao.setAttribute('aria-controls', lista.id);
    var nada = el('p', 'sel-nada', 'Nada encontrado.');
    var limpar = el('button', 'sel-limpar', 'Limpar seleção');
    limpar.type = 'button';
    painel.appendChild(busca);
    painel.appendChild(lista);
    painel.appendChild(nada);
    if (multi) painel.appendChild(limpar);

    select.parentNode.insertBefore(caixa, select);
    caixa.appendChild(botao);
    caixa.appendChild(painel);
    caixa.appendChild(select);
    select.hidden = true;
    select.tabIndex = -1;

    var rotulo = document.querySelector('label[for="' + id + '"]');
    if (rotulo) {
      rotulo.id = rotulo.id || id + '-rotulo';
      rotulo.htmlFor = botao.id;
      botao.setAttribute('aria-labelledby', rotulo.id + ' ' + valor.id);
      lista.setAttribute('aria-labelledby', rotulo.id);
    }

    function marcadas() {
      return Array.prototype.filter.call(select.options, function (o) { return o.selected; });
    }
    function textoBotao() {
      var m = marcadas();
      if (!multi) return m.length ? m[0].textContent : '';
      if (!m.length) return opcoes.vazio || 'Todas';
      return m.length === 1 ? m[0].textContent : m.length + ' ' + (opcoes.varias || 'selecionadas');
    }
    function pintarValor() {
      valor.textContent = textoBotao();
      botao.title = multi ? marcadas().map(function (o) { return o.textContent; }).join(', ') : valor.textContent;
    }
    function itens() {
      return Array.prototype.filter.call(lista.children, function (i) { return !i.hidden; });
    }
    function montarLista() {
      /* quem ouve o change pode refazer as opcoes: mantem rolagem e foco */
      var rolagem = lista.scrollTop;
      var focado = Array.prototype.indexOf.call(lista.children, document.activeElement);
      var chave = focado >= 0 ? lista.children[focado].dataset.v : null;
      lista.textContent = '';
      Array.prototype.forEach.call(select.options, function (o, i) {
        var item = el('div', 'sel-item');
        item.setAttribute('role', 'option');
        item.setAttribute('aria-selected', o.selected ? 'true' : 'false');
        item.tabIndex = -1;
        item.dataset.i = i;
        item.dataset.v = o.value;
        var marca = el('span', multi ? 'sel-caixa' : 'sel-marca');
        marca.setAttribute('aria-hidden', 'true');
        item.appendChild(marca);
        item.appendChild(el('span', null, o.textContent));
        lista.appendChild(item);
      });
      filtrar();
      lista.scrollTop = rolagem;
      if (chave !== null) {
        var volta = Array.prototype.filter.call(lista.children, function (i) { return i.dataset.v === chave; })[0];
        if (volta) volta.focus({ preventScroll: true });
      }
    }
    function filtrar() {
      var q = semAcento(busca.value.trim());
      Array.prototype.forEach.call(lista.children, function (i) {
        i.hidden = !!q && semAcento(i.textContent).indexOf(q) < 0;
      });
      nada.hidden = itens().length > 0;
    }
    function sincronizarMarcas() {
      Array.prototype.forEach.call(lista.children, function (i) {
        i.setAttribute('aria-selected', select.options[i.dataset.i].selected ? 'true' : 'false');
      });
      limpar.disabled = !marcadas().length;
      pintarValor();
    }
    function avisar() { select.dispatchEvent(new Event('change', { bubbles: true })); }

    function escolher(item) {
      var o = select.options[item.dataset.i];
      if (multi) {
        o.selected = !o.selected;
        avisar();
        sincronizarMarcas(); /* quem ouve o change pode ter ajustado a selecao */
        return;
      }
      var mudou = !o.selected;
      o.selected = true;
      fechar(true);
      pintarValor();
      if (mudou) avisar();
    }

    function abrir() {
      if (aberto) aberto.fechar(false);
      busca.value = '';
      busca.hidden = select.options.length <= BUSCA_A_PARTIR_DE;
      montarLista();
      limpar.disabled = !marcadas().length;
      painel.hidden = false;
      botao.setAttribute('aria-expanded', 'true');
      painel.classList.remove('a-direita');
      if (painel.getBoundingClientRect().right > document.documentElement.clientWidth - 8) painel.classList.add('a-direita');
      aberto = controle;
      var atual = lista.querySelector('[aria-selected="true"]') || lista.firstElementChild;
      if (!busca.hidden) busca.focus();
      else if (atual) atual.focus();
    }
    function fechar(devolverFoco) {
      if (painel.hidden) return;
      painel.hidden = true;
      botao.setAttribute('aria-expanded', 'false');
      if (aberto === controle) aberto = null;
      if (devolverFoco) botao.focus();
    }

    botao.addEventListener('click', function () { if (painel.hidden) abrir(); else fechar(false); });
    botao.addEventListener('keydown', function (ev) {
      if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') { ev.preventDefault(); abrir(); }
    });
    lista.addEventListener('click', function (ev) {
      var item = ev.target.closest('.sel-item');
      if (item) { if (multi) item.focus({ preventScroll: true }); escolher(item); }
    });
    painel.addEventListener('keydown', function (ev) {
      var vis = itens();
      var i = vis.indexOf(document.activeElement);
      if (ev.key === 'Escape') { ev.preventDefault(); fechar(true); return; }
      if (ev.key === 'ArrowDown') { ev.preventDefault(); if (vis.length) vis[Math.min(i + 1, vis.length - 1)].focus(); }
      else if (ev.key === 'ArrowUp') { ev.preventDefault(); if (vis.length) vis[Math.max(i - 1, 0)].focus(); }
      else if (ev.key === 'Home' && i >= 0) { ev.preventDefault(); vis[0].focus(); }
      else if (ev.key === 'End' && i >= 0) { ev.preventDefault(); vis[vis.length - 1].focus(); }
      else if ((ev.key === 'Enter' || ev.key === ' ') && i >= 0) { ev.preventDefault(); escolher(vis[i]); }
      else if (ev.key === 'Enter' && ev.target === busca) { ev.preventDefault(); if (vis.length) escolher(vis[0]); }
    });
    caixa.addEventListener('focusout', function (ev) {
      if (ev.relatedTarget && !caixa.contains(ev.relatedTarget)) fechar(false);
    });
    busca.addEventListener('input', filtrar);
    limpar.addEventListener('click', function () {
      Array.prototype.forEach.call(select.options, function (o) { o.selected = false; });
      avisar();
      sincronizarMarcas();
    });

    var controle = {
      caixa: caixa,
      fechar: fechar,
      atualizar: function () {
        if (!painel.hidden) { montarLista(); limpar.disabled = !marcadas().length; }
        pintarValor();
      }
    };
    pintarValor();
    return controle;
  }

  /* clique fora fecha (o Safari nao da foco em botao clicado, o focusout nao basta) */
  document.addEventListener('pointerdown', function (ev) {
    if (aberto && !aberto.caixa.contains(ev.target)) aberto.fechar(false);
  });

  raiz.Seletor = { criar: criar };
})(window);

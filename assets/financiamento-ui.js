/* ============================================================
   SIMULADOR DE FINANCIAMENTO - pecas de interface compartilhadas
   ------------------------------------------------------------
   Usado pela tela dedicada (financiamento-app.js) e pelo popup
   dos associativos (financiamento-popup.js).
   - morph: atualiza o HTML reaproveitando os nos, sem piscar.
   - data-moeda: mascara de moeda em tempo real nos inputs.
   - enterAvanca: quando o Enter deve seguir para o proximo passo.
   - miniPopup: popup pequeno com formulario.
   ============================================================ */
window.FinanciamentoUI = (function () {
  'use strict';

  var X = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"></path></svg>';

  function movimentoReduzido() { return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); }

  function suavizar(el) {
    if (!el || !el.animate || movimentoReduzido()) return;
    el.animate([{ opacity: 0.25 }, { opacity: 1 }], { duration: 280, easing: 'ease-out' });
  }

  function mesmoTipo(a, b) { return a.nodeType === b.nodeType && a.nodeName === b.nodeName; }

  function sincronizaAtributos(a, b) {
    Array.prototype.slice.call(a.attributes).forEach(function (at) { if (!b.hasAttribute(at.name)) a.removeAttribute(at.name); });
    Array.prototype.forEach.call(b.attributes, function (at) { if (a.getAttribute(at.name) !== at.value) a.setAttribute(at.name, at.value); });
  }

  function sincronizaNo(a, b, suave) {
    if (a.nodeType === 3) {
      if (a.nodeValue !== b.nodeValue) { a.nodeValue = b.nodeValue; if (suave) suavizar(a.parentNode); }
      return;
    }
    if (a.nodeType !== 1) return;
    sincronizaAtributos(a, b);
    /* o valor digitado nao vive no atributo: so atualiza fora do campo em uso */
    if (a.tagName === 'INPUT' && a !== document.activeElement) a.value = b.getAttribute('value') || '';
    sincronizaFilhos(a, b, suave);
  }

  function sincronizaFilhos(a, b, suave) {
    var x = a.firstChild, y = b.firstChild;
    while (y) {
      var proxY = y.nextSibling;
      if (!x) a.appendChild(y);
      else {
        var proxX = x.nextSibling;
        if (mesmoTipo(x, y)) sincronizaNo(x, y, suave); else a.replaceChild(y, x);
        x = proxX;
      }
      y = proxY;
    }
    while (x) { var resto = x.nextSibling; a.removeChild(x); x = resto; }
  }

  /* troca o conteudo de alvo por html mantendo os elementos que continuam iguais:
     transicoes de CSS rodam, imagens nao recarregam, foco e animacoes nao reiniciam.
     opts.suave: texto que mudou entra com um fade curto. */
  function morph(alvo, html, opts) {
    var t = document.createElement('template');
    t.innerHTML = html;
    sincronizaFilhos(alvo, t.content, !!(opts && opts.suave));
  }

  /* Enter em botao de opcao ainda nao marcada ou em link faz a acao dele; no resto, avanca */
  function enterAvanca(el) {
    if (!el || !el.closest) return true;
    var b = el.closest('a,button');
    if (!b) return true;
    return b.getAttribute('role') === 'switch' || b.matches('[aria-checked="true"],[aria-pressed="true"],[aria-selected="true"]');
  }

  /* roda antes dos ouvintes das telas, que ja leem o valor formatado */
  document.addEventListener('input', function (ev) {
    var el = ev.target;
    if (!el.matches || !el.matches('input[data-moeda]')) return;
    var t = window.Financiamento.mascaraMoeda(el.value);
    if (t !== el.value) el.value = t;
  }, true);

  /* colar "510000" ou "510.000,00" e valor em reais, nao em centavos */
  document.addEventListener('paste', function (ev) {
    var el = ev.target;
    if (!el.matches || !el.matches('input[data-moeda]') || !ev.clipboardData) return;
    var v = window.Match.numero(ev.clipboardData.getData('text'));
    ev.preventDefault();
    el.value = v > 0 ? window.Financiamento.mascaraMoeda(v.toFixed(2)) : '';
    el.dispatchEvent(new Event('input', { bubbles: true }));
  });

  /* o = { titulo, desc, corpo, confirmar, extra, foco, aoConfirmar(raiz) -> mensagem de erro ou nada, aoExtra() } */
  function miniPopup(o) {
    var origem = document.activeElement;
    var veu = document.createElement('div');
    veu.className = 'fz-veu';
    veu.setAttribute('data-fz-tema', 'claro');
    veu.innerHTML = '<form class="fz-mini" role="dialog" aria-modal="true" aria-labelledby="fz-mini-t" novalidate>' +
      '<div class="fz-mini-cab"><h2 id="fz-mini-t">' + o.titulo + '</h2><button type="button" class="fz-x" data-mini="fechar" aria-label="Fechar">' + X + '</button></div>' +
      (o.desc ? '<p class="fz-mini-d">' + o.desc + '</p>' : '') + o.corpo +
      '<p class="fz-erro" id="fz-mini-e" role="alert" hidden></p>' +
      '<div class="fz-mini-rod">' + (o.extra ? '<button type="button" class="fz-ghost fz-mini-extra" data-mini="extra">' + o.extra + '</button>' : '') +
      '<button type="button" class="fz-ghost" data-mini="fechar">Cancelar</button><button type="submit" class="fz-pri">' + o.confirmar + '</button></div></form>';
    document.body.appendChild(veu);
    var form = veu.querySelector('form');

    function fechar() {
      if (veu.classList.contains('fz-saindo')) return;
      document.removeEventListener('keydown', teclas, true);
      veu.classList.add('fz-saindo');
      setTimeout(function () { veu.remove(); }, 160);
      if (origem && origem.focus && document.body.contains(origem)) origem.focus();
    }
    function teclas(ev) {
      if (ev.key === 'Escape') { ev.preventDefault(); ev.stopPropagation(); fechar(); return; }
      if (ev.key !== 'Tab') return;
      var f = Array.prototype.filter.call(form.querySelectorAll('button,input'), function (n) { return !n.disabled && n.offsetParent !== null; });
      var i = f.indexOf(document.activeElement);
      if (ev.shiftKey && i <= 0) { ev.preventDefault(); f[f.length - 1].focus(); }
      else if (!ev.shiftKey && i === f.length - 1) { ev.preventDefault(); f[0].focus(); }
    }
    document.addEventListener('keydown', teclas, true);
    veu.addEventListener('mousedown', function (ev) { if (ev.target === veu) fechar(); });
    form.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-mini]');
      if (!b) return;
      if (b.getAttribute('data-mini') === 'extra' && o.aoExtra) o.aoExtra();
      fechar();
    });
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var msg = o.aoConfirmar(form), e = form.querySelector('#fz-mini-e');
      if (msg) { e.textContent = msg; e.hidden = false; return; }
      fechar();
    });
    var alvo = o.foco ? form.querySelector(o.foco) : form.querySelector('input');
    if (alvo) alvo.focus();
  }

  return { morph: morph, enterAvanca: enterAvanca, miniPopup: miniPopup };
})();

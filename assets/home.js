/* Regras da home (Home V2).
   Funcoes puras, sem DOM: o controlador da pagina (home-app.js) so monta
   os elementos e chama estas funcoes para o texto e o HTML dos cards. */
(function (raiz) {
  'use strict';

  var CHAVE_ABERTURA = 'pc-abertura-vista';

  var SETA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>';
  var ICONE_FOTO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2.5"></rect><circle cx="8.5" cy="9.5" r="1.6"></circle><path d="M3.5 17l4.8-4.4a2 2 0 012.7 0l3 2.8m0 0l2-1.8a2 2 0 012.7 0l1.8 1.6"></path></svg>';

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function rotuloEmpreendimentos(n) {
    return n + (n === 1 ? ' empreendimento' : ' empreendimentos');
  }

  function cardCidadeHTML(city) {
    var total = (city.empreendimentos || []).length;
    var foto = '';
    if (city.foto) {
      var f = esc(city.foto);
      var f640 = esc(city.foto.replace(/\.webp$/, '@640.webp'));
      foto = '<img class="city-photo" src="' + f + '"' +
        ' srcset="' + f640 + ' 640w, ' + f + ' 1200w"' +
        ' sizes="(max-width: 900px) 100vw, 410px"' +
        ' width="1200" height="800" decoding="async" alt="" onerror="this.remove()">';
    }
    return foto +
      '<span class="city-chip">' +
        '<img src="assets/img/icones-3d/predio.svg" width="20" height="20" alt="">' +
        '<strong>' + total + '</strong> <span>' + (total === 1 ? 'empreendimento' : 'empreendimentos') + '</span>' +
      '</span>' +
      '<span class="city-body">' +
        '<span class="city-text">' +
          '<span class="city-name">' + esc(city.name) + '</span>' +
          '<span class="city-uf">' + esc(city.uf) + '</span>' +
        '</span>' +
        '<span class="city-go">' + SETA + '</span>' +
      '</span>';
  }

  function thumb(emp) {
    if (!emp.heroImg) {
      return '<span class="emp-thumb"><span class="emp-thumb-ph">' + ICONE_FOTO +
             '<span>Imagens em breve</span></span></span>';
    }
    var base = esc('assets/img/cards/' + emp.id);
    return '<span class="emp-thumb">' +
      '<img src="' + base + '.webp"' +
      ' srcset="' + base + '@480.webp 480w, ' + base + '@640.webp 640w, ' + base + '.webp 960w"' +
      ' sizes="(max-width: 560px) 84vw, (max-width: 1000px) 46vw, 300px"' +
      ' width="960" height="720" loading="lazy" decoding="async" alt=""' +
      ' onerror="this.onerror=null;this.removeAttribute(\'srcset\');this.src=\'' + esc(emp.heroImg) + '\'">' +
      '</span>';
  }

  function cardEmpreendimentoHTML(emp) {
    var nome = esc(emp.cardNome || emp.nome);
    if (emp.comingSoon) {
      return {
        tag: 'div', className: 'emp-card emp-card-soon', href: null,
        html: thumb(emp) + '<span class="emp-body"><span class="emp-name">' + nome + '</span>' +
          '<span class="emp-soon-tag">Em breve</span></span>'
      };
    }
    return {
      tag: 'a', className: 'emp-card', href: 'empreendimento.html?e=' + encodeURIComponent(emp.id),
      html: thumb(emp) + '<span class="emp-body"><span class="emp-name">' + nome + '</span>' +
        '<span class="emp-go">' + SETA + '</span></span>'
    };
  }

  /* A abertura aparece uma vez por aba. Sem storage (aba anonima, bloqueio),
     aparece sempre: melhor repetir a animacao que esconder a pagina. */
  function deveMostrarAbertura(storage) {
    if (!storage) return true;
    try {
      if (storage.getItem(CHAVE_ABERTURA)) return false;
    } catch (e) {
      return true;
    }
    try { storage.setItem(CHAVE_ABERTURA, '1'); } catch (e) { /* segue mostrando */ }
    return true;
  }

  function indiceSlide(scrollLeft, passo, total) {
    if (!(passo > 0) || total < 1) return 0;
    return Math.min(total - 1, Math.max(0, Math.round(scrollLeft / passo)));
  }

  var api = { esc: esc, rotuloEmpreendimentos: rotuloEmpreendimentos, cardCidadeHTML: cardCidadeHTML,
    cardEmpreendimentoHTML: cardEmpreendimentoHTML, deveMostrarAbertura: deveMostrarAbertura,
    indiceSlide: indiceSlide, SETA: SETA };

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.Home = api;
})(this);

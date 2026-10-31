/* Menu mobile da navbar (home e em-breve): o botão abre a folha com os
   links; fecha com o botão, com Esc, clicando fora ou escolhendo um link. */
(function () {
  'use strict';

  var btn   = document.getElementById('menu-btn');
  var folha = document.getElementById('menu-folha');
  var fundo = document.getElementById('menu-fundo');
  if (!btn || !folha) return;

  function definir(aberto) {
    folha.hidden = !aberto;
    if (fundo) fundo.hidden = !aberto;
    btn.setAttribute('aria-expanded', String(aberto));
    btn.setAttribute('aria-label', aberto ? 'Fechar menu' : 'Abrir menu');
    btn.classList.toggle('is-aberto', aberto);
  }

  btn.addEventListener('click', function () { definir(folha.hidden); });
  if (fundo) fundo.addEventListener('click', function () { definir(false); });
  folha.addEventListener('click', function (e) {
    if (e.target.closest('a')) definir(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !folha.hidden) {
      definir(false);
      btn.focus();
    }
  });
})();

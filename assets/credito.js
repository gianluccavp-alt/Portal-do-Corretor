/* Credito discreto no fim de todas as paginas. Fica em um unico lugar: editar aqui vale para o site todo. */
(function () {
  if (document.getElementById('credito-dev')) return;
  var st = document.createElement('style');
  st.textContent =
    '.credito-dev{margin:0;padding:14px 16px 18px;text-align:center;font:400 11px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif;letter-spacing:.01em;color:inherit;opacity:.38}' +
    '.credito-dev a{color:inherit;text-decoration:none}' +
    '.credito-dev a:hover,.credito-dev a:focus-visible{text-decoration:underline;opacity:1}' +
    '.credito-dev.fixo{position:fixed;right:10px;bottom:2px;z-index:1;padding:0;text-align:right;color:#fff;opacity:.45;pointer-events:none;text-shadow:0 1px 2px rgba(0,0,0,.5)}' +
    '.credito-dev.fixo a{pointer-events:auto}' +
    '@media(max-width:767px){body:has(.mtabbar) .credito-dev{padding-bottom:96px}}' +
    '@media print{.credito-dev{display:none}}';
  document.head.appendChild(st);
  var p = document.createElement('p');
  p.id = 'credito-dev';
  p.className = 'credito-dev' + (document.querySelector('.mq-rodape') ? ' fixo' : '');
  p.innerHTML = 'Desenvolvido por <a href="https://www.instagram.com/gabrielhanieri" target="_blank" rel="noopener">@gabrielhanieri</a>';
  document.body.appendChild(p);
})();

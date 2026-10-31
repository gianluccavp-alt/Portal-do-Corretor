/* Controlador da home: desenha cidades, abre os empreendimentos da cidade
   escolhida e cuida do carrossel. Texto e HTML dos cards vem de home.js. */
(function () {
  'use strict';

  var Home = window.Home;
  var cityGrid   = document.getElementById('city-grid');
  var empSection = document.getElementById('emp-section');
  var empGrid    = document.getElementById('emp-grid');
  var empTitle   = document.getElementById('emp-title');
  var empCount   = document.getElementById('emp-count');
  var empNav     = document.getElementById('emp-nav');
  var btnPrev    = document.getElementById('emp-prev');
  var btnNext    = document.getElementById('emp-next');
  var empDots    = document.getElementById('emp-dots');

  var reduceMotion = window.matchMedia
    ? window.matchMedia('(prefers-reduced-motion: reduce)')
    : { matches: false };

  function scrollBehavior() { return reduceMotion.matches ? 'auto' : 'smooth'; }

  function notice(title, body) {
    return '<div class="notice"><strong>' + Home.esc(title) + '</strong>' + Home.esc(body) + '</div>';
  }

  /* ---------- Cidades ---------- */
  var CITIES = Array.isArray(window.CITIES) ? window.CITIES : [];

  if (!CITIES.length) {
    cityGrid.innerHTML = notice(
      'Não foi possível carregar as cidades',
      'A lista de empreendimentos não chegou. Recarregue a página; se continuar assim, avise o time comercial.'
    );
  }

  CITIES.forEach(function (city, idx) {
    var btn = document.createElement('button');
    btn.className = 'city-card';
    btn.type = 'button';
    btn.setAttribute('aria-pressed', 'false');
    btn.setAttribute('aria-controls', 'emp-section');
    btn.innerHTML = Home.cardCidadeHTML(city);
    btn.addEventListener('click', function () { selectCity(idx, btn); });
    cityGrid.appendChild(btn);
  });

  /* ---------- Empreendimentos da cidade ---------- */
  function selectCity(idx, btn) {
    document.querySelectorAll('.city-card').forEach(function (c) {
      var on = c === btn;
      c.setAttribute('aria-pressed', String(on));
      c.classList.toggle('is-on', on);
    });

    var city = CITIES[idx];
    var emps = city.empreendimentos || [];
    empTitle.textContent = 'Empreendimentos em ' + city.name;
    empCount.textContent = Home.rotuloEmpreendimentos(emps.length);
    empGrid.innerHTML = '';
    empGrid.scrollLeft = 0;
    empDots.innerHTML = '';

    if (!emps.length) {
      empNav.hidden = true;
      empGrid.style.gridAutoColumns = '100%';
      empGrid.innerHTML = notice(
        'Nenhum empreendimento em ' + city.name,
        'Esta cidade ainda não tem produto publicado no portal.'
      );
      mostrarSecao();
      return;
    }

    emps.forEach(function (emp) {
      var card = Home.cardEmpreendimentoHTML(emp);
      var el = document.createElement(card.tag);
      el.className = card.className;
      if (card.href) el.href = card.href;
      else el.setAttribute('aria-disabled', 'true');
      el.innerHTML = card.html;
      empGrid.appendChild(el);
      empDots.appendChild(document.createElement('span'));
    });

    mostrarSecao();
    fitColumns();
    updateNav();
    desenharBolinhas();
  }

  function mostrarSecao() {
    empSection.classList.remove('home-hidden');
    empSection.scrollIntoView({ behavior: scrollBehavior(), block: 'start' });
  }

  /* ---------- Controles do carrossel ---------- */
  function gapPx() {
    return parseFloat(getComputedStyle(empGrid).columnGap) || 0;
  }

  function overflows() {
    return empGrid.scrollWidth - empGrid.clientWidth > 4;
  }

  /* Quando tudo cabe na largura, as colunas se esticam para preencher a faixa —
     mas nunca ficam mais largas que o tamanho padrão de um card do breakpoint. */
  function fitColumns() {
    empGrid.style.gridAutoColumns = '';
    var first = empGrid.firstElementChild;
    if (!first || !first.classList.contains('emp-card')) return;
    if (overflows()) return;

    var gap = gapPx();
    var baseW = first.getBoundingClientRect().width;
    var fits = Math.floor((empGrid.clientWidth + gap) / (baseW + gap)) || 1;
    var cols = Math.max(empGrid.children.length, fits);
    empGrid.style.gridAutoColumns =
      'calc((100% - ' + (cols - 1) + ' * ' + gap + 'px) / ' + cols + ')';
  }

  function updateNav() {
    if (!overflows()) { empNav.hidden = true; return; }
    empNav.hidden = false;
    var max = empGrid.scrollWidth - empGrid.clientWidth;
    btnPrev.disabled = empGrid.scrollLeft <= 2;
    btnNext.disabled = empGrid.scrollLeft >= max - 2;
  }

  function step() {
    var card = empGrid.firstElementChild;
    if (!card) return empGrid.clientWidth;
    return card.getBoundingClientRect().width + gapPx();
  }

  /* Bolinhas de posição (só aparecem no celular, via CSS). */
  function desenharBolinhas() {
    var dots = empDots.children;
    var atual = Home.indiceSlide(empGrid.scrollLeft, step(), dots.length);
    for (var i = 0; i < dots.length; i++) dots[i].classList.toggle('is-on', i === atual);
  }

  btnPrev.addEventListener('click', function () {
    empGrid.scrollBy({ left: -step(), behavior: scrollBehavior() });
  });
  btnNext.addEventListener('click', function () {
    empGrid.scrollBy({ left: step(), behavior: scrollBehavior() });
  });
  empGrid.addEventListener('scroll', function () { updateNav(); desenharBolinhas(); }, { passive: true });
  window.addEventListener('resize', function () { fitColumns(); updateNav(); desenharBolinhas(); });
})();

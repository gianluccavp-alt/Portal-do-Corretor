/* ============================================================
   MAQUETE 3D - aplicacao
   ------------------------------------------------------------
   Orquestra planilha -> Maquete (regras puras) -> Cena (Three.js)
   -> DOM. Usa os globais de config.js, data.js e maquete.js.
   Regra-mae: a tela e espelho da planilha. Sem dados, nada aparece
   como disponivel e nenhum valor e exibido.
   ============================================================ */
import { criarCena } from './maquete-cena.js';

const M = window.Maquete;
const TIMEOUT_PLANILHA = 15000;
const PESO_MODELO = 0.8;

const STATUS_TXT = {
  disponivel: 'Disponível', reservada: 'Reservada', vendida: 'Vendida',
  fora: 'Fora de venda', 'sem-dados': 'Sem dados'
};
const CAMERA_TXT = { geral: 'Vista geral', frente: 'Frente', fundos: 'Fundos', lazer: 'Lazer', portaria: 'Portaria' };

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (ch) => (
  { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
const pad2 = (n) => String(n).padStart(2, '0');

/* ---------- entrada ---------- */
const empId = new URLSearchParams(location.search).get('e');
const emp = empId ? window.findEmpreendimento(empId) : null;
const voltar = emp ? 'empreendimento.html?e=' + encodeURIComponent(emp.id) : 'index.html';
$('maquete-voltar').href = voltar;
$('maquete-erro-link').href = voltar;

function erroFatal(msg) {
  $('maquete-erro-msg').textContent = msg;
  $('maquete-erro').hidden = false;
  $('maquete-carregando').classList.add('fim');
}

if (!emp || !emp.maquete) erroFatal('Maquete 3D não disponível para este empreendimento');
else if (!window.WebGL2RenderingContext) erroFatal('Seu navegador não suporta a maquete 3D');
else iniciar(emp);

async function iniciar(emp) {
  /* data.js le CURRENT_EMP (cidade, regra de tipo, promocionais) */
  window.CURRENT_EMP = emp;
  document.title = 'Maquete 3D · ' + emp.nome + ' · Portal do Corretor';
  $('mq-nome').textContent = emp.nome;
  $('mq-carregando-nome').textContent = emp.nome;

  const cfg = emp.maquete;
  /* area de lazer: fotos do book (galeria do empreendimento), sem fachada/torre */
  const fotosLazer = ((emp.galeria && emp.galeria.items) || [])
    .filter((it) => it.img && !/^(fachada|torre)$/i.test(it.title || ''));
  const gcfg = Object.assign({ solNascente: emp.solNascente, torresVenda: emp.torresVisiveis || null }, cfg.grade);
  const ANDAR_MAX = gcfg.andares - 1;

  const st = {
    grade: M.montarGrade(gcfg, null),
    dados: false,
    modo: 'cores',
    sel: null,
    vista: false,
    visiveis: null,
    filtros: { soDisponiveis: false, tipos: [], sol: '', andarMin: 0, andarMax: ANDAR_MAX }
  };
  let cena = null;

  /* ---------- planilha (com timeout) ---------- */
  function carregarPlanilha() {
    return new Promise((ok) => {
      let feito = false;
      const fim = (v) => { if (!feito) { feito = true; clearTimeout(timer); ok(v); } };
      const timer = setTimeout(() => { console.warn('[maquete] planilha passou de 15 s'); fim(null); }, TIMEOUT_PLANILHA);
      try {
        window.fetchSheetCsv((texto) => {
          try {
            const rows = window.parseCSV(texto);
            const us = rows ? window.rowsToUnits(rows, emp.sheetName, { todosStatus: true }) : [];
            if (!us.length) console.warn('[maquete] planilha sem linhas para', emp.sheetName);
            fim(us.length ? us : null);
          } catch (e) {
            console.error('[maquete] erro lendo a planilha', e);
            fim(null);
          }
        }, (msg) => { console.warn('[maquete] planilha:', msg); fim(null); });
      } catch (e) {
        console.error('[maquete] erro buscando a planilha', e);
        fim(null);
      }
    });
  }

  function aplicarDados(units) {
    st.grade = M.montarGrade(gcfg, units);
    st.dados = !!units;
    if (units && st.grade.ignoradas) console.info('[maquete] linhas fora da grade ignoradas:', st.grade.ignoradas);
    $('mq-aviso').hidden = st.dados;
  }

  /* promocionais (so Ribeirao Preto): preenche PROMO_SET como loadPromocionais, sem renderUnits */
  function carregarPromocionais() {
    if (!window.showPromoFilter || !window.showPromoFilter()) return;
    window.fetchPromocionais((data) => {
      window.PROMO_SET = new Set((data.identificadores || []).map((s) => String(s).trim()));
      if (st.sel !== null) renderPainel();
    }, () => { /* sem lista: valores normais */ });
  }

  /* ---------- carga: modelo (80%) + planilha (20%) ---------- */
  const barra = $('maquete-progresso');
  let pModelo = 0;
  let pPlanilha = 0;
  const progresso = () => { barra.style.width = Math.round((pModelo * PESO_MODELO + pPlanilha * (1 - PESO_MODELO)) * 100) + '%'; };

  montarControles();
  carregarPromocionais();

  const pDados = carregarPlanilha().then((u) => { pPlanilha = 1; progresso(); return u; });
  let units;
  try {
    [cena, units] = await Promise.all([
      criarCena($('maquete-cena'), cfg, {
        onProgresso: (p) => { pModelo = p; progresso(); },
        onHover: aoPassar,
        onClick: aoClicar,
        onSelecao: posicionarSelecao,
        onRumo: girarBussola
      }),
      pDados
    ]);
  } catch (e) {
    console.error('[maquete]', e);
    erroFatal(/webgl/i.test(String(e && e.message)) ? 'Seu navegador não suporta a maquete 3D'
      : 'Não foi possível carregar a maquete 3D');
    return;
  }
  aplicarDados(units);
  atualizar();
  $('maquete-carregando').classList.add('fim');

  /* ---------- estado -> cena + DOM ---------- */
  /* a noite as disponiveis ja sao as unicas acesas: "So disponiveis" nao muda nada e some */
  function soDispAplica() { return st.modo !== 'noite'; }

  function filtroAtivo() {
    const f = st.filtros;
    return (f.soDisponiveis && soDispAplica()) || f.tipos.length > 0 || !!f.sol || f.andarMin > 0 || f.andarMax < ANDAR_MAX;
  }

  function atualizar() {
    $('mq-f-disp').hidden = !soDispAplica();
    const f = soDispAplica() ? st.filtros : Object.assign({}, st.filtros, { soDisponiveis: false });
    st.visiveis = filtroAtivo() ? M.filtrar(st.grade, f, gcfg) : null;
    if (cena) cena.pintar(M.estados(st.grade), st.visiveis, st.modo);
    renderResumo();
    renderLegenda();
    renderContagemFiltro();
    /* com os dados novos a unidade aberta pode ter virado "fora" (torre sem linhas): fecha */
    if (st.sel !== null && st.grade.celulas[st.sel].estado === 'fora') fecharPainel();
    if (st.sel !== null) renderPainel();
  }

  function renderResumo() {
    const el = $('mq-resumo');
    if (!st.dados) { el.textContent = 'Disponibilidade não carregada'; return; }
    const r = M.resumo(st.grade);
    el.innerHTML = '<b class="mq-resumo-disp">' + r.disponiveis + '</b> ' +
      (r.disponiveis === 1 ? 'unidade disponível' : 'unidades disponíveis');
  }

  function renderLegenda() {
    const itens = st.modo === 'noite'
      ? [['acesa', 'Disponível'], ['res', 'Reservada'], ['apagada', 'Vendida'], ['fora', 'Fora de venda']]
      : [['disp', 'Disponível'], ['res', 'Reservada'], ['vend', 'Vendida'], ['fora', 'Fora de venda']];
    $('mq-legenda').innerHTML = itens.map(([c, t]) => '<span><i class="mq-dot ' + c + '"></i>' + t + '</span>').join('');
  }

  function renderContagemFiltro() {
    const n = (st.filtros.soDisponiveis && soDispAplica() ? 1 : 0) + (st.filtros.tipos.length ? 1 : 0) + (st.filtros.sol ? 1 : 0) +
      (st.filtros.andarMin > 0 || st.filtros.andarMax < ANDAR_MAX ? 1 : 0);
    const badge = $('mq-filtros-n');
    badge.hidden = !n;
    badge.textContent = n;
    const cont = $('mq-f-cont');
    if (!st.visiveis) { cont.textContent = 'Sem filtro ativo'; return; }
    let disp = 0;
    st.visiveis.forEach((i) => { if (st.grade.celulas[i].estado === 'disponivel') disp++; });
    cont.textContent = disp + (disp === 1 ? ' disponível' : ' disponíveis') + ' no filtro';
  }

  /* ---------- dados de exibicao de uma celula ---------- */
  function info(idx) {
    const c = st.grade.celulas[idx];
    /* vendida nao tem linha na planilha: tipologia vem da mesma regra (classifyTipo) */
    const tipo = c.u ? c.u.tipo : window.classifyTipo(emp, '', c.final, c.andar, 'BL-' + pad2(c.torre));
    const tipoLabel = c.u ? c.u.tipoLabel : window.tipoLabelFor(emp, tipo);
    return { c, tipo, tipoLabel, numero: pad2(c.andar) + pad2(c.final) };
  }

  /* ---------- hover ---------- */
  function aoPassar(idx, x, y) {
    const tip = $('mq-tip');
    const c = idx == null ? null : st.grade.celulas[idx];
    if (!c || c.estado === 'inexistente') { tip.hidden = true; return; }
    let txt;
    if (c.estado === 'fora') {
      txt = 'Torre ' + c.torre + ' · Fora de venda';
      const canvas = $('maquete-cena').querySelector('canvas');
      if (canvas) canvas.style.cursor = 'default'; // nao clicavel
    } else {
      const i = info(idx);
      txt = 'T' + c.torre + ' · ' + i.numero + ' · ' + i.tipoLabel + ' · ' + STATUS_TXT[c.estado];
    }
    tip.dataset.estado = c.estado;
    $('mq-tip-txt').textContent = txt;
    tip.hidden = false;
    const w = tip.offsetWidth;
    const h = tip.offsetHeight;
    let left = x + 16;
    let top = y + 18;
    if (left + w > window.innerWidth - 8) left = x - w - 12;
    if (top + h > window.innerHeight - 8) top = y - h - 12;
    tip.style.transform = 'translate(' + Math.max(8, left) + 'px,' + Math.max(8, top) + 'px)';
  }

  /* ---------- badge da selecionada + bussola (posicoes vindas da cena) ---------- */
  function posicionarSelecao(p) {
    const b = $('mq-sel');
    if (!p || st.sel === null) { b.hidden = true; return; }
    b.hidden = false;
    const x = Math.round(p.x - b.offsetWidth / 2);
    const y = Math.round(p.y - b.offsetHeight - 10);
    b.style.transform = 'translate(' + x + 'px,' + y + 'px)';
  }

  function girarBussola(graus) {
    $('mq-bussola-disco').style.transform = 'rotate(' + (-graus) + 'deg)';
  }

  /* ---------- imagem ampliada (na propria pagina): planta ou galeria da area de lazer ---------- */
  let focoAntesPlanta = null;
  let galeria = null; // { itens, i } quando a galeria esta aberta
  function mostrarImagem(src, titulo, alt, sub) {
    $('mq-planta-img').src = src;
    $('mq-planta-img').alt = alt;
    $('mq-planta-titulo').textContent = titulo;
    $('mq-planta-sub').textContent = sub || '';
    $('mq-planta-sub').hidden = !sub;
  }
  function abrirModal() {
    focoAntesPlanta = document.activeElement;
    $('mq-planta-modal').hidden = false;
    $('mq-planta-fechar').focus();
  }
  function ajustarGaleria(com) {
    ['mq-gal-ant', 'mq-gal-prox', 'mq-planta-cont'].forEach((id) => { $(id).hidden = !com; });
  }
  function abrirPlanta(src, titulo) {
    galeria = null;
    ajustarGaleria(false);
    mostrarImagem(src, titulo, 'Planta ' + titulo);
    abrirModal();
  }
  function fotoGaleria(i) {
    const n = galeria.itens.length;
    galeria.i = (i + n) % n;
    const it = galeria.itens[galeria.i];
    mostrarImagem(it.img, it.title, it.title + (it.sub ? ' · ' + it.sub : ''), it.sub);
    $('mq-planta-cont').textContent = (galeria.i + 1) + ' / ' + n;
    /* pre-carrega a proxima para a troca ser instantanea */
    new Image().src = galeria.itens[(galeria.i + 1) % n].img;
  }
  function abrirLazer() {
    if (!fotosLazer.length) return;
    galeria = { itens: fotosLazer, i: 0 };
    ajustarGaleria(true);
    fotoGaleria(0);
    abrirModal();
  }
  function fecharPlanta() {
    if ($('mq-planta-modal').hidden) return false;
    $('mq-planta-modal').hidden = true;
    galeria = null;
    if (focoAntesPlanta && focoAntesPlanta.focus) focoAntesPlanta.focus();
    return true;
  }

  /* ---------- selecao ---------- */
  function aoClicar(idx) {
    if (idx == null) { fecharPainel(); return; }
    const c = st.grade.celulas[idx];
    if (!c || c.estado === 'fora' || c.estado === 'inexistente') return;
    abrir(idx);
  }

  function abrir(idx) {
    st.sel = idx;
    st.vista = false;
    $('mq-tip').hidden = true;
    if (cena) { cena.destacar(idx); cena.focarUnidade(idx); }
    const i = info(idx);
    $('mq-sel-txt').textContent = 'T' + i.c.torre + ' ' + i.numero + ' · ' + M.posicaoLabel(i.tipo);
    renderPainel();
    $('mq-painel').hidden = false;
    document.body.classList.add('painel-aberto');
  }

  function fecharPainel() {
    if (st.sel === null) return;
    st.sel = null;
    if (cena) cena.destacar(null);
    $('mq-sel').hidden = true;
    $('mq-painel').hidden = true;
    document.body.classList.remove('painel-aberto');
  }

  function renderPainel() {
    const { c, tipo, tipoLabel, numero } = info(st.sel);
    const andarTxt = c.andar === 0 ? 'Térreo/Garden' : c.andar + 'º andar';
    const manha = M.nascente(gcfg, c.torre, c.final);
    const planta = (emp.plantas || []).find((p) => p.tipo === tipo);
    const disp = c.estado === 'disponivel' && c.u;
    const promo = disp && window.isPromo(c.u);

    let h = '<div class="mq-p-cab">' +
      '<span class="mq-eyebrow">Torre ' + c.torre + ' · Final ' + pad2(c.final) + '</span>' +
      '<h2>Unidade ' + numero + '</h2>' +
      '<p class="mq-p-tipo">' + esc(tipoLabel) + '</p>' +
      '<div class="mq-p-tags"><span class="mq-pill ' + c.estado + '">' + STATUS_TXT[c.estado] + '</span>' +
      (promo ? '<span class="mq-pill promo">Promocional</span>' : '') + '</div></div>';

    if (planta) {
      h += '<button type="button" class="mq-planta" data-acao="planta" data-src="' + esc(planta.img) + '" data-titulo="' +
        esc(planta.title || tipoLabel) + '">' +
        '<img src="' + esc(planta.img) + '" alt="Planta ' + esc(planta.title || tipoLabel) + '" loading="lazy">' +
        '<span>' + esc(planta.title || tipoLabel) + '<em>Ampliar</em></span></button>';
    }

    h += '<div class="mq-p-meta">' +
      '<div><span class="mq-lab">Andar</span><b>' + andarTxt + '</b></div>' +
      '<div><span class="mq-lab">Posição</span><b>' + M.posicaoLabel(tipo) + '</b></div>' +
      '<div class="' + (manha ? 'sol-manha' : 'sol-tarde') + '"><span class="mq-lab">Sol</span><b>' +
        (manha ? 'Sol da manhã' : 'Sol da tarde') + '</b></div>' +
      (c.u && c.u.area ? '<div><span class="mq-lab">Área privativa</span><b>' + esc(c.u.area) + ' m²</b></div>' : '') +
      '</div>' +
      '<button type="button" class="mq-btn mq-btn-ghost mq-vista" data-acao="vista">' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>' +
      (st.vista ? 'Ver o prédio de fora' : 'Vista desta unidade') + '</button>';

    if (disp) {
      const sims = M.urlsSimuladores(cfg.simId, c.codigo);
      h += '<div class="mq-p-sec">' +
        '<div class="mq-valor-dest"><span class="mq-lab">Associativo/Investidor</span><b>' + esc(window.fmt(window.associativoOf(c.u))) + '</b></div>' +
        '<div class="mq-valor-sec"><span class="mq-lab">Tabela Direta</span><b>' + esc(window.fmt(window.tabelaDiretaOf(c.u))) + '</b></div>' +
        (promo ? '<p class="mq-promo-nota">Unidade promocional: não pode ser vendida com Prêmio.</p>' : '') +
        '<div class="mq-simular">' +
        '<a class="mq-btn" href="' + esc(sims.associativo) + '" target="_blank" rel="noopener">Simular Associativo</a>' +
        '<a class="mq-btn mq-btn-ghost" href="' + esc(sims.tabelaDireta) + '" target="_blank" rel="noopener">Simular Tabela Direta</a>' +
        '</div></div>';
    } else if (c.estado === 'sem-dados') {
      h += '<div class="mq-p-sec"><p class="mq-p-aviso">Disponibilidade não carregada. Tente de novo para ver status e valores.</p></div>';
    }

    $('mq-painel-corpo').innerHTML = h;
    const ant = M.vizinhaDisponivel(st.grade, st.sel, -1, st.visiveis);
    const prox = M.vizinhaDisponivel(st.grade, st.sel, 1, st.visiveis);
    $('mq-ant').disabled = ant === null;
    $('mq-prox').disabled = prox === null;
  }

  function navegar(dir) {
    if (st.sel === null) return;
    const i = M.vizinhaDisponivel(st.grade, st.sel, dir, st.visiveis);
    if (i !== null) abrir(i);
  }

  /* ---------- busca ---------- */
  function buscar(texto) {
    const msg = $('mq-busca-msg');
    const avisar = (t) => { msg.textContent = t; msg.hidden = false; };
    if (!texto.trim()) { msg.hidden = true; return; }
    const b = M.interpretarBusca(texto);
    let idx = -1;
    let hint = null;
    if (b) {
      if (b.torre !== null) idx = M.indice(gcfg, b.torre, b.andar, b.final);
      else {
        /* sem torre: primeira torre a venda que tenha essa unidade */
        const torres = st.grade.torresAVenda.length ? st.grade.torresAVenda : gcfg.torres;
        const achadas = [];
        for (const t of torres) {
          const i = M.indice(gcfg, t, b.andar, b.final);
          if (i !== -1 && !/^(fora|inexistente)$/.test(st.grade.celulas[i].estado)) achadas.push({ t, i });
        }
        if (achadas.length) { idx = achadas[0].i; hint = achadas; }
        else {
          for (const t of torres) {
            const i = M.indice(gcfg, t, b.andar, b.final);
            if (i !== -1 && st.grade.celulas[i].estado !== 'inexistente') { idx = i; break; }
          }
        }
      }
    }
    if (idx === -1 || st.grade.celulas[idx].estado === 'inexistente') { avisar('Unidade não encontrada'); return; }
    if (st.grade.celulas[idx].estado === 'fora') { avisar('Torre fora de venda'); return; }
    if (hint && hint.length > 1) {
      avisar('Mostrando Torre ' + hint[0].t + ' · também existe na ' +
        hint.slice(1).map((x) => 'Torre ' + x.t).join(', '));
    } else msg.hidden = true;
    abrir(idx);
  }

  /* ---------- controles (montados antes da cena existir) ---------- */
  function montarControles() {
    /* modo */
    document.querySelectorAll('.mq-modo button').forEach((b) => {
      b.addEventListener('click', () => {
        st.modo = b.dataset.modo;
        document.body.dataset.modo = st.modo;
        document.querySelectorAll('.mq-modo button').forEach((o) => o.setAttribute('aria-pressed', String(o === b)));
        atualizar();
      });
    });

    /* cameras */
    const nav = $('mq-cameras');
    Object.keys(cfg.cameras || {}).forEach((nome) => {
      const m = /^torre-(\d+)$/.exec(nome);
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = m ? 'Torre ' + m[1] : (CAMERA_TXT[nome] || nome);
      b.addEventListener('click', () => irParaCamera(nome));
      nav.appendChild(b);
      if (nome === 'lazer' && cfg.ambientes && cfg.ambientes.length) montarMenuLazer(b);
    });

    function irParaCamera(nome) {
      st.vista = false;
      if (cena) cena.irPara(nome);
      if (st.sel !== null) renderPainel();
    }

    /* menu do botao Lazer: abre ao passar o mouse (ou focar/tocar) e leva a camera ate cada ambiente.
       Fica fora da barra de cameras porque ela rola na horizontal no celular e cortaria o menu. */
    function montarMenuLazer(botao) {
      const menu = document.createElement('div');
      menu.id = 'mq-ambientes';
      menu.className = 'mq-card mq-ambientes';
      menu.setAttribute('role', 'menu');
      menu.setAttribute('aria-label', 'Ambientes de lazer');
      menu.hidden = true;
      cfg.ambientes.forEach((a) => {
        const it = document.createElement('button');
        it.type = 'button';
        it.setAttribute('role', 'menuitem');
        it.textContent = a.nome;
        it.addEventListener('click', () => { irParaCamera(a.id); fechar(); });
        menu.appendChild(it);
      });
      document.body.appendChild(menu);
      botao.setAttribute('aria-haspopup', 'menu');
      botao.setAttribute('aria-expanded', 'false');
      botao.setAttribute('aria-controls', menu.id);

      let timer = null;
      function posicionar() {
        const r = botao.getBoundingClientRect();
        const w = menu.offsetWidth;
        menu.style.left = Math.max(8, Math.min(window.innerWidth - w - 8, r.left + r.width / 2 - w / 2)) + 'px';
        menu.style.bottom = (window.innerHeight - r.top + 10) + 'px';
      }
      function abrir() {
        clearTimeout(timer);
        menu.hidden = false;
        posicionar();
        botao.setAttribute('aria-expanded', 'true');
      }
      function fechar() {
        clearTimeout(timer);
        menu.hidden = true;
        botao.setAttribute('aria-expanded', 'false');
      }
      /* folga para o mouse atravessar o vao entre o botao e o menu */
      const fecharDepois = () => { clearTimeout(timer); timer = setTimeout(fechar, 220); };
      let toque = false;
      botao.addEventListener('pointerdown', (e) => { toque = e.pointerType === 'touch'; });
      botao.addEventListener('pointerenter', (e) => { if (e.pointerType !== 'touch') abrir(); });
      botao.addEventListener('pointerleave', (e) => { if (e.pointerType !== 'touch') fecharDepois(); });
      menu.addEventListener('pointerenter', () => clearTimeout(timer));
      menu.addEventListener('pointerleave', (e) => { if (e.pointerType !== 'touch') fecharDepois(); });
      /* sem hover (toque): o toque no botao alterna o menu; o clique tambem leva a visao geral do lazer */
      botao.addEventListener('click', () => { if (toque && !menu.hidden) fechar(); else abrir(); });
      botao.addEventListener('focus', () => { if (botao.matches(':focus-visible')) abrir(); });
      [botao, menu].forEach((el) => el.addEventListener('focusout', (e) => {
        if (!menu.contains(e.relatedTarget) && e.relatedTarget !== botao) fecharDepois();
      }));
      document.addEventListener('keydown', (e) => {
        if (e.key !== 'Escape' || menu.hidden) return;
        const dentro = menu.contains(document.activeElement);
        fechar();
        if (dentro) botao.focus();
      });
      document.addEventListener('pointerdown', (e) => {
        if (!menu.hidden && !menu.contains(e.target) && !botao.contains(e.target)) fechar();
      });
      window.addEventListener('resize', () => { if (!menu.hidden) posicionar(); });
    }

    /* busca */
    const input = $('mq-busca-input');
    $('mq-busca').addEventListener('submit', (e) => { e.preventDefault(); buscar(input.value); });
    input.addEventListener('input', () => { if (!input.value) $('mq-busca-msg').hidden = true; });

    /* filtros */
    const btnF = $('mq-filtros-btn');
    btnF.addEventListener('click', () => {
      const abrirF = $('mq-filtros').hidden;
      $('mq-filtros').hidden = !abrirF;
      btnF.setAttribute('aria-expanded', String(abrirF));
    });
    const fDisp = $('mq-f-disp');
    fDisp.addEventListener('click', () => {
      st.filtros.soDisponiveis = !st.filtros.soDisponiveis;
      fDisp.setAttribute('aria-pressed', String(st.filtros.soDisponiveis));
      atualizar();
    });
    const tiposBox = $('mq-f-tipos');
    (emp.tipos || []).forEach((t) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'mq-chip';
      b.setAttribute('aria-pressed', 'false');
      b.textContent = t.label;
      b.addEventListener('click', () => {
        const lista = st.filtros.tipos;
        const pos = lista.indexOf(t.key);
        if (pos >= 0) lista.splice(pos, 1); else lista.push(t.key);
        b.setAttribute('aria-pressed', String(pos < 0));
        atualizar();
      });
      tiposBox.appendChild(b);
    });
    /* sol: nascente e poente sao exclusivos; clicar no ativo desliga */
    const solBox = $('mq-f-sol');
    const solBtns = solBox.querySelectorAll('.mq-chip');
    const marcarSol = () => solBtns.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.sol === st.filtros.sol)));
    solBtns.forEach((b) => b.addEventListener('click', () => {
      st.filtros.sol = st.filtros.sol === b.dataset.sol ? '' : b.dataset.sol;
      marcarSol();
      atualizar();
    }));
    const sMin = $('mq-f-min');
    const sMax = $('mq-f-max');
    for (let a = 0; a <= ANDAR_MAX; a++) {
      const txt = a === 0 ? 'Térreo' : a + 'º';
      sMin.add(new Option(txt, a));
      sMax.add(new Option(txt, a));
    }
    sMin.value = '0';
    sMax.value = String(ANDAR_MAX);
    const aoMudarAndar = (origem) => {
      let lo = parseInt(sMin.value, 10);
      let hi = parseInt(sMax.value, 10);
      if (lo > hi) { if (origem === sMin) hi = lo; else lo = hi; }
      sMin.value = String(lo);
      sMax.value = String(hi);
      st.filtros.andarMin = lo;
      st.filtros.andarMax = hi;
      atualizar();
    };
    sMin.addEventListener('change', () => aoMudarAndar(sMin));
    sMax.addEventListener('change', () => aoMudarAndar(sMax));
    $('mq-f-limpar').addEventListener('click', () => {
      st.filtros = { soDisponiveis: false, tipos: [], sol: '', andarMin: 0, andarMax: ANDAR_MAX };
      fDisp.setAttribute('aria-pressed', 'false');
      marcarSol();
      tiposBox.querySelectorAll('.mq-chip').forEach((b) => b.setAttribute('aria-pressed', 'false'));
      sMin.value = '0';
      sMax.value = String(ANDAR_MAX);
      atualizar();
    });

    /* aviso: tentar de novo */
    const btnAviso = $('mq-aviso-btn');
    btnAviso.addEventListener('click', async () => {
      btnAviso.disabled = true;
      btnAviso.textContent = 'Carregando…';
      const u = await carregarPlanilha();
      btnAviso.disabled = false;
      btnAviso.textContent = 'Tentar de novo';
      aplicarDados(u);
      atualizar();
    });

    /* painel */
    $('mq-painel-fechar').addEventListener('click', fecharPainel);
    $('mq-ant').addEventListener('click', () => navegar(-1));
    $('mq-prox').addEventListener('click', () => navegar(1));
    $('mq-planta-fechar').addEventListener('click', fecharPlanta);
    $('mq-gal-ant').addEventListener('click', () => galeria && fotoGaleria(galeria.i - 1));
    $('mq-gal-prox').addEventListener('click', () => galeria && fotoGaleria(galeria.i + 1));
    $('mq-lazer').hidden = !fotosLazer.length;
    $('mq-lazer').addEventListener('click', abrirLazer);
    /* celular: arrastar para o lado troca a foto */
    let toqueX = null;
    const foto = document.querySelector('.mq-modal-foto');
    foto.addEventListener('touchstart', (e) => { toqueX = e.touches[0].clientX; }, { passive: true });
    foto.addEventListener('touchend', (e) => {
      if (!galeria || toqueX === null) return;
      const dx = e.changedTouches[0].clientX - toqueX;
      toqueX = null;
      if (Math.abs(dx) > 40) fotoGaleria(galeria.i + (dx > 0 ? -1 : 1));
    });
    $('mq-planta-modal').addEventListener('click', (e) => { if (e.target === e.currentTarget) fecharPlanta(); });
    $('mq-painel-corpo').addEventListener('click', (e) => {
      const pl = e.target.closest('[data-acao="planta"]');
      if (pl) { abrirPlanta(pl.dataset.src, pl.dataset.titulo); return; }
      const b = e.target.closest('[data-acao="vista"]');
      if (!b || st.sel === null || !cena) return;
      st.vista = !st.vista;
      if (st.vista) cena.vistaDaUnidade(st.sel); else cena.focarUnidade(st.sel);
      renderPainel();
    });

    /* teclado: Esc fecha, setas navegam (fora de campos) */
    document.addEventListener('keydown', (e) => {
      const campo = /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName);
      if (galeria && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
        fotoGaleria(galeria.i + (e.key === 'ArrowLeft' ? -1 : 1));
        return;
      }
      if (e.key === 'Escape') {
        if (fecharPlanta()) return;
        if (campo) { e.target.blur(); return; }
        if (!$('mq-filtros').hidden) { btnF.click(); return; }
        fecharPainel();
      } else if (!campo && st.sel !== null && $('mq-planta-modal').hidden && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
        navegar(e.key === 'ArrowLeft' ? -1 : 1);
      }
    });
  }
}

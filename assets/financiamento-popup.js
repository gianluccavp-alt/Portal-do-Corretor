/* ============================================================
   SIMULADOR DE FINANCIAMENTO - popup dos associativos
   ------------------------------------------------------------
   window.FinanciamentoPopup.abrir(opts)           popup em passos
   window.FinanciamentoPopup.ligarAssociativo(cfg)  botao no passo Cliente
   Regras em assets/financiamento.js; PDF em assets/financiamento-pdf.js.
   Visual: docs/design/simulador-financiamento/fonte (Modal, Assoc*, A-*, B-*).
   Spec §6: docs/superpowers/specs/2026-11-07-simulador-financiamento-design.md
   ============================================================ */
window.FinanciamentoPopup = (function () {
  'use strict';

  var F = window.Financiamento, UI = window.FinanciamentoUI;
  var ICONE = function (n, t, alt) {
    return '<img class="fz-ico" src="assets/img/icones-3d/' + n + '.svg" width="' + t + '" height="' + t + '" alt="' + (alt || '') + '">';
  };
  var SETA = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>';
  var VOLTA = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"></path></svg>';
  var CHECK = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"></path></svg>';
  var BAIXAR = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"></path></svg>';
  var COPIAR = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="3"></rect><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"></path></svg>';
  var X = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"></path></svg>';
  var CIDADES = ['Ribeirão Preto', 'Campinas', 'Sorocaba'];
  var TITULOS = { 1: 'Passo 1 de 3 · Cliente', 2: 'Passo 2 de 3 · Perfil', 3: 'Passo 3 de 3 · Condições', resultado: 'Resultado' };
  var ORDEM = [1, 2, 3, 'resultado'];
  var CAMPOS_PASSO = { 1: ['renda', 'nascimento', 'valor', 'cidade'], 2: [], 3: [] };

  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function num(t) { return window.Match ? window.Match.numero(t) : parseFloat(String(t).replace(/\./g, '').replace(',', '.')) || 0; }
  function semRs(n) { return F.brl(n).replace('R$ ', ''); }
  function inteiro(n) { return 'R$ ' + semRs(Math.round(n)).replace(/,\d+$/, ''); }
  function pct(v) { return v.toFixed(2).replace('.', ',') + '%'; }
  function dataTxt(d) { return d ? ('0' + d.getDate()).slice(-2) + '/' + ('0' + (d.getMonth() + 1)).slice(-2) + '/' + d.getFullYear() : ''; }
  function celular() { return !!(window.matchMedia && window.matchMedia('(max-width:860px)').matches); }
  function focaveis(el) {
    return Array.prototype.filter.call(el.querySelectorAll('button,input,a[href],[tabindex]:not([tabindex="-1"])'),
      function (n) { return !n.disabled && n.offsetParent !== null; });
  }
  function resumoDe(sim) {
    var r = sim.r;
    return F.programa(r) + ' · ' + pct(r.jurosNominal) + ' a.a. · ' + r.prazo + ' meses · ' + r.sistema;
  }

  var aberto = null;   /* um popup por vez */

  /* opts = { tema, contexto, respostas, seg, etapa, aoCopiar(valores, registro), aoFechar } */
  function abrir(opts) {
    if (aberto) aberto.fechar();
    var ctx = opts.contexto || {};
    var hoje = new Date();
    var temAvaliacao = ctx.avaliacao > 0;
    var st = {
      etapa: opts.etapa === 'resultado' ? 'resultado' : 1,
      resp: Object.assign({}, F.RESP_PADRAO, opts.respostas || {}),
      imovel: {
        cidade: CIDADES.indexOf(ctx.cidade) >= 0 ? ctx.cidade : '', avaliacao: temAvaliacao ? ctx.avaliacao : 0,
        venda: ctx.venda > 0 ? ctx.venda : 0, ato: ctx.ato > 0 ? ctx.ato : 0,
        empId: ctx.empId || null, empNome: ctx.empNome || '', unidade: ctx.unidade || '', unidadeRotulo: ctx.unidadeRotulo || ''
      },
      seg: opts.seg || null, erros: {}, nascTxt: ''
    };
    if (!(st.resp.renda > 0) && ctx.renda > 0) st.resp.renda = ctx.renda;
    st.nascTxt = dataTxt(st.resp.nascimento);
    /* resultado so abre com respostas e imovel validos; senao comeca no passo 1 */
    if (st.etapa === 'resultado' && F.validar(st.resp, st.imovel, hoje).length) st.etapa = 1;
    var origem = document.activeElement;

    var veu = document.createElement('div');
    veu.className = 'fz-veu';
    veu.setAttribute('data-fz-tema', opts.tema === 'black' ? 'black' : 'claro');
    veu.innerHTML =
      '<div class="fz-pop' + (celular() ? ' fz-folha' : '') + '" role="dialog" aria-modal="true" aria-labelledby="fz-tit">' +
        '<div class="fz-pega" aria-hidden="true"></div>' +
        '<header class="fz-cab"><div class="fz-cab-l">' + ICONE('calculadora', 46) +
          '<div class="fz-cab-t"><h2 id="fz-tit">Simular financiamento</h2><p class="fz-cab-s"></p></div>' +
          '<button type="button" class="fz-x" data-acao="fechar" aria-label="Fechar">' + X + '</button></div>' +
          '<div class="fz-prog"><div class="fz-prog-b"></div><span class="fz-prog-t"></span></div></header>' +
        '<div class="fz-corpo"></div><footer class="fz-rod"></footer></div>';
    document.body.appendChild(veu);
    var pop = veu.querySelector('.fz-pop'), corpo = veu.querySelector('.fz-corpo'), rod = veu.querySelector('.fz-rod');
    var overflowAntes = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';

    function subtitulo() {
      var im = st.imovel;
      if (im.empNome && im.avaliacao > 0) return [im.empNome, im.unidadeRotulo, 'avaliação ' + inteiro(im.avaliacao)].filter(Boolean).join(' · ');
      if (im.empNome) return [im.empNome, im.unidadeRotulo].filter(Boolean).join(' · ');
      return 'Informe o imóvel no primeiro passo';
    }

    function simAtual() { return F.simular(st.resp, st.imovel, hoje); }
    function segEscolhida(sim) {
      var ok = sim.r.seguradoras.some(function (s) { return s.codigo === st.seg; });
      return ok ? st.seg : sim.segPadrao;
    }

    /* ---------- passos ---------- */
    function erroDe(campo) { return st.erros[campo] ? '<p class="fz-erro" id="fz-e-' + campo + '">' + esc(st.erros[campo]) + '</p>' : ''; }
    function previa() {
      if (!(st.resp.renda > 0) || !(st.imovel.avaliacao > 0) || !st.imovel.cidade || !st.resp.nascimento) return '';
      var s = simAtual();
      if (s.erro) return '<div class="fz-pilulas"><span class="fz-pil fz-pil-alerta">' + esc(s.mensagem) + '</span></div>';
      return '<div class="fz-pilulas"><span class="fz-pil fz-pil-ok">' + CHECK + esc(F.programa(s.r)) + '</span>' +
        '<span class="fz-pil">' + pct(s.r.jurosNominal) + ' a.a.</span><span class="fz-pil">Prazo de ' + s.r.prazo + ' meses</span>' +
        '<span class="fz-pil">Parcela de até ' + inteiro(s.parcelaMax) + '</span></div>';
    }
    function passo1() {
      var h = '';
      if (temAvaliacao) h += '<div class="fz-nota">' + SETA + '<span>Já trouxemos do simulador o imóvel, o valor de avaliação e a renda. Confira e complete.</span></div>';
      else h += '<div class="fz-nota">' + SETA + '<span>' + (st.imovel.empNome ? 'Essa unidade está sem valor de avaliação na planilha. ' : 'Nenhuma unidade escolhida no simulador. ') + 'Informe a cidade e o valor de avaliação.</span></div>';
      h += '<h3 class="fz-h3">Renda e idade do cliente</h3><div class="fz-grade">';
      if (!temAvaliacao) {
        h += '<div class="fz-campo fz-campo-largo"><span class="fz-lab" id="fz-l-cidade">Cidade do imóvel</span><div class="fz-pills" role="radiogroup" aria-labelledby="fz-l-cidade">' +
          CIDADES.map(function (c) { var on = st.imovel.cidade === c; return '<button type="button" role="radio" aria-checked="' + on + '" class="fz-pill' + (on ? ' fz-pill-on' : '') + '" data-acao="cidade" data-v="' + esc(c) + '" data-foco="cidade-' + esc(c) + '">' + esc(c) + '</button>'; }).join('') +
          '</div>' + erroDe('cidade') + '</div>' +
          '<div class="fz-campo"><label class="fz-lab" for="fz-valor">Valor de avaliação</label><div class="fz-input' + (st.erros.valor ? ' fz-input-erro' : '') + '"><span class="fz-pre">R$</span><input id="fz-valor" data-campo="valor" data-moeda inputmode="numeric" autocomplete="off" value="' + (st.imovel.avaliacao > 0 ? semRs(st.imovel.avaliacao) : '') + '" placeholder="0,00"' + (st.erros.valor ? ' aria-invalid="true" aria-describedby="fz-e-valor"' : '') + '></div>' + erroDe('valor') + '</div>';
      }
      h += '<div class="fz-campo"><label class="fz-lab" for="fz-renda">Renda familiar bruta' + (ctx.renda > 0 && st.resp.renda === ctx.renda ? '<span class="fz-do">do simulador</span>' : '') + '</label>' +
        '<div class="fz-input' + (st.erros.renda ? ' fz-input-erro' : '') + '"><span class="fz-pre">R$</span><input id="fz-renda" data-campo="renda" data-moeda inputmode="numeric" autocomplete="off" value="' + (st.resp.renda > 0 ? semRs(st.resp.renda) : '') + '" placeholder="0,00"' + (st.erros.renda ? ' aria-invalid="true" aria-describedby="fz-e-renda"' : '') + '></div>' + erroDe('renda') + '</div>';
      var idade = st.resp.nascimento ? F.idadeAnos(st.resp.nascimento, hoje) : null;
      h += '<div class="fz-campo"><label class="fz-lab" for="fz-nasc">Nascimento do comprador mais velho</label>' +
        '<div class="fz-input' + (st.erros.nascimento ? ' fz-input-erro' : '') + '"><input id="fz-nasc" data-campo="nascimento" inputmode="numeric" autocomplete="off" maxlength="10" placeholder="dd/mm/aaaa" value="' + esc(st.nascTxt) + '"' + (st.erros.nascimento ? ' aria-invalid="true" aria-describedby="fz-e-nascimento"' : '') + '>' +
        '<span class="fz-idade">' + (idade != null && idade >= 0 ? idade + ' anos' : '') + '</span></div>' + erroDe('nascimento') + '</div></div>';
      h += '<div class="fz-previa" aria-live="polite">' + previa() + '</div>';
      return h;
    }
    function passo2() {
      var tiles = [
        ['fgts', 'maleta', '3 anos de FGTS', 'Somando todos os períodos'],
        ['possuiImovel', 'chave', 'Já tem imóvel na cidade', 'Se sim, vai para o SBPE']
      ];
      if (F.mostraPerguntasSubsidio(st.resp.renda, st.resp.possuiImovel)) {
        tiles.push(['fatorSocial', 'pessoas', 'Mais de um comprador ou dependente', 'Sem isso, 30% do subsídio']);
        tiles.push(['subsidioAnterior', 'presente', 'Já recebeu subsídio', 'Do FGTS ou da União']);
      }
      return '<h3 class="fz-h3">O que vale para o cliente?</h3><p class="fz-p">Muda o programa, os juros e o subsídio. Toque para ligar ou desligar.</p>' +
        '<div class="fz-tiles">' + tiles.map(function (t) {
          var on = st.resp[t[0]] === true || (t[0] === 'fgts' && st.resp.fgts !== false);
          return '<button type="button" role="switch" aria-checked="' + on + '" class="fz-tile' + (on ? ' fz-tile-on' : '') + '" data-acao="tog" data-v="' + t[0] + '" data-foco="tog-' + t[0] + '">' +
            '<span class="fz-tile-top">' + ICONE(t[1], 50) + '<span class="fz-sw' + (on ? ' fz-sw-on' : '') + '"></span></span>' +
            '<span><span class="fz-tile-t">' + t[2] + '</span><span class="fz-tile-d">' + t[3] + '</span></span></button>';
        }).join('') + '</div>';
    }
    function passo3() {
      var base = Object.assign({}, st.resp, { prazo: null });
      var maxSim = F.simular(base, st.imovel, hoje);
      var maximo = maxSim.erro ? 420 : maxSim.r.prazo;
      var opcoes = [null].concat([360, 300, 240].filter(function (p) { return p < maximo; }));
      if (st.resp.prazo != null && opcoes.indexOf(st.resp.prazo) < 0) st.resp.prazo = null;
      var comp = F.comparar(st.resp, st.imovel, hoje);
      var card = function (id, desc) {
        var s = comp[id], on = st.resp.sistema === id, seg, fin, parc;
        if (s.erro) { fin = '—'; parc = '—'; }
        else {
          seg = s.r.seguradoras.filter(function (x) { return x.codigo === s.segPadrao; })[0];
          fin = inteiro(s.r.valorFinanciamento);
          parc = id === 'SAC' ? inteiro(seg.primeira) + ' → ' + semRs(Math.round(seg.ultima)).replace(/,\d+$/, '') : inteiro(seg.primeira);
        }
        return '<button type="button" role="radio" aria-checked="' + on + '" class="fz-opt' + (on ? ' fz-opt-on' : '') + '" data-acao="sis" data-v="' + id + '" data-foco="sis-' + id + '">' +
          '<span class="fz-opt-t"><span class="fz-radio">' + CHECK + '</span>' + id + '</span><span class="fz-opt-d">' + desc + '</span>' +
          '<span class="fz-opt-n"><span><span class="fz-k">Financia</span><b>' + fin + '</b></span><span><span class="fz-k">Parcela</span><b>' + parc + '</b></span></span></button>';
      };
      return '<h3 class="fz-h3">Como o cliente quer pagar?</h3>' +
        '<div class="fz-opts" role="radiogroup" aria-label="Sistema de amortização">' + card('PRICE', 'Parcela parecida o prazo todo') + card('SAC', 'Parcela que cai com o tempo') + '</div>' +
        '<span class="fz-lab" id="fz-l-prazo">Prazo</span><div class="fz-pills" role="radiogroup" aria-labelledby="fz-l-prazo">' +
        opcoes.map(function (p) {
          var on = st.resp.prazo === p, rot = p == null ? 'Máximo · ' + maximo + ' meses' : p + ' meses';
          return '<button type="button" role="radio" aria-checked="' + on + '" class="fz-pill' + (on ? ' fz-pill-on' : '') + '" data-acao="prazo" data-v="' + (p == null ? '' : p) + '" data-foco="prazo-' + p + '">' + rot + '</button>';
        }).join('') + '</div>';
    }
    function resultado() {
      var s = simAtual();
      if (s.erro) {
        return '<div class="fz-aviso" role="alert">' + ICONE('alvo', 44) + '<div><h3 class="fz-h3">Não deu para simular</h3><p class="fz-p">' + esc(s.mensagem) + '</p>' +
          '<button type="button" class="fz-lnk" data-acao="editar">Editar respostas</button></div></div>';
      }
      var r = s.r, seg = segEscolhida(s), segObj = r.seguradoras.filter(function (x) { return x.codigo === seg; })[0];
      var base = st.imovel.avaliacao;
      var pf = r.valorFinanciamento / base * 100, ps = r.subsidio / base * 100;
      var v = F.valoresCopia(s, seg, st.resp.renda);
      var segp = function (id) { var on = r.sistema === id; return '<button type="button" role="tab" aria-selected="' + on + '" class="fz-seg' + (on ? ' fz-seg-on' : '') + '" data-acao="sis" data-v="' + id + '" data-foco="rsis-' + id + '">' + id + '</button>'; };
      return '<div class="fz-res">' +
        '<div class="fz-res-a"><div class="fz-hero">' +
          '<div class="fz-hero-top"><span class="fz-ok">' + CHECK + 'Financia até</span><div class="fz-segw" role="tablist" aria-label="Sistema">' + segp('PRICE') + segp('SAC') + '</div></div>' +
          '<div class="fz-valor">' + F.brl(r.valorFinanciamento) + '</div>' +
          '<div class="fz-hero-s">' + esc(resumoDe(s)) + '</div>' +
          (s.limitado ? '<div class="fz-hero-s">A CAIXA aprova até ' + F.brl(s.capacidade) + ' para esta renda; o valor do imóvel não pede mais que isso.</div>' : '') +
          '<div class="fz-barra"><span class="fz-b-fin" style="width:' + pf.toFixed(2) + '%"></span>' + (r.subsidio > 0 ? '<span class="fz-b-sub" style="width:' + ps.toFixed(2) + '%"></span>' : '') + '<span class="fz-b-ent"></span></div>' +
          '<div class="fz-mini"><div><span class="fz-k"><i class="fz-dot fz-dot-fin"></i>1ª parcela</span><b>' + F.brl(segObj.primeira) + '</b></div>' +
          '<div><span class="fz-k"><i class="fz-dot fz-dot-sub"></i>Subsídio</span><b class="fz-verde">' + (r.subsidio > 0 ? inteiro(r.subsidio) : '—') + '</b></div>' +
          '<div><span class="fz-k"><i class="fz-dot fz-dot-ent"></i>Entrada</span><b>' + inteiro(s.entrada) + '</b></div></div></div>' +
          '<div class="fz-segs"><div class="fz-segs-t">' + ICONE('escudo', 28) + '<b>Seguradora</b><span>· 1ª parcela</span></div><div role="radiogroup" aria-label="Seguradora">' +
          F.seguradorasOrdenadas(r.seguradoras).map(function (x) {
            var on = x.codigo === seg, nome = x.nome.toLowerCase().replace(/(^|\s)\S/g, function (c) { return c.toUpperCase(); }).replace('Habitacional ', '');
            return '<button type="button" role="radio" aria-checked="' + on + '" class="fz-row' + (on ? ' fz-row-on' : '') + '" data-acao="seg" data-v="' + x.codigo + '" data-foco="seg-' + x.codigo + '"><span class="fz-radio">' + CHECK + '</span><span class="fz-row-n">' + esc(nome) + '</span><b>' + F.brl(x.primeira) + '</b></button>';
          }).join('') + '</div></div></div>' +
        '<div class="fz-res-b"><b class="fz-vai-t">Vai para o simulador</b><span class="fz-vai-s">Passo 2 · Cliente</span>' +
          [['Renda do cliente', F.brl(v.renda), ''], ['Valor do financiamento', F.brl(v.financiado), (st.imovel.venda > 0 ? (v.financiado / st.imovel.venda * 100).toFixed(2).replace('.', ',') + '% do imóvel' : '')],
           ['Subsídio', F.brl(v.subsidio), ''], ['Parcela do financiamento', F.brl(v.parcFin), segObj.nome.toLowerCase().replace(/(^|\s)\S/g, function (c) { return c.toUpperCase(); })]]
            .map(function (l) { return '<div class="fz-vai"><span>' + l[0] + '</span><span><b>' + l[1] + '</b>' + (l[2] ? '<small>' + esc(l[2]) + '</small>' : '') + '</span></div>'; }).join('') +
        '</div></div>';
    }

    var desenhada = null;   /* passo que esta na tela */
    function render() {
      var foco = document.activeElement && pop.contains(document.activeElement) ? document.activeElement.getAttribute('data-foco') || document.activeElement.id : null;
      var idx = ORDEM.indexOf(st.etapa);
      veu.querySelector('.fz-cab-s').textContent = subtitulo();
      UI.morph(veu.querySelector('.fz-prog-b'), ORDEM.map(function (k, i) { return '<span class="' + (i <= idx ? 'fz-on' : '') + '"></span>'; }).join(''));
      veu.querySelector('.fz-prog-t').textContent = TITULOS[st.etapa];
      var html = st.etapa === 1 ? passo1() : st.etapa === 2 ? passo2() : st.etapa === 3 ? passo3() : resultado();
      /* mesmo passo: atualiza no lugar, sem piscar */
      if (desenhada === st.etapa) UI.morph(corpo, html, { suave: true }); else corpo.innerHTML = html;
      desenhada = st.etapa;
      if (st.etapa === 'resultado') {
        var erro = simAtual().erro;
        var folha = pop.classList.contains('fz-folha');
        UI.morph(rod, '<button type="button" class="fz-ghost' + (folha ? ' fz-so-ico' : '') + '" data-acao="voltar" aria-label="Voltar e editar as respostas">' + VOLTA + (folha ? '' : 'Voltar') + '</button>' +
          '<span class="fz-rod-dir"><button type="button" class="fz-sec" data-acao="pdf"' + (erro ? ' disabled' : '') + '>' + BAIXAR + (folha ? 'PDF' : 'Baixar PDF') + '</button>' +
          '<button type="button" class="fz-pri" data-acao="copiar"' + (erro ? ' disabled' : '') + '>' + COPIAR + (folha ? 'Copiar' : 'Copiar para o simulador') + '</button></span>');
      } else {
        UI.morph(rod, '<button type="button" class="fz-ghost" data-acao="voltar">' + VOLTA + (idx === 0 ? 'Cancelar' : 'Voltar') + '</button>' +
          '<button type="button" class="fz-pri" data-acao="avancar">' + (st.etapa === 3 ? 'Ver resultado' : 'Continuar') + SETA + '</button>');
      }
      if (foco) {
        var alvo = pop.querySelector('[data-foco="' + foco + '"]') || document.getElementById(foco);
        if (alvo) alvo.focus();
      }
    }

    function validarPasso() {
      var campos = CAMPOS_PASSO[st.etapa] || [];
      var lista = F.validar(st.resp, st.imovel, hoje).filter(function (e) { return campos.indexOf(e.campo) >= 0; });
      st.erros = {};
      lista.forEach(function (e) { st.erros[e.campo] = e.mensagem; });
      return lista;
    }

    function avancar() {
      if (st.etapa === 1) {
        var lista = validarPasso();
        if (lista.length) {
          render();
          /* primeiro campo com erro na ordem da tela */
          var el = st.erros.cidade && !st.imovel.cidade ? pop.querySelector('[data-acao="cidade"]') : pop.querySelector('[aria-invalid="true"]');
          if (el) el.focus();
          return;
        }
      }
      var i = ORDEM.indexOf(st.etapa);
      st.etapa = ORDEM[Math.min(ORDEM.length - 1, i + 1)];
      render();
      corpo.scrollTop = 0;
      var f = focaveis(corpo)[0] || pop.querySelector('[data-acao="avancar"],[data-acao="copiar"]');
      if (f) f.focus();
    }

    function fechar() {
      if (!veu.parentNode) return;
      document.removeEventListener('keydown', teclas, true);
      veu.parentNode.removeChild(veu);
      document.documentElement.style.overflow = overflowAntes;
      aberto = null;
      if (origem && origem.focus && document.body.contains(origem)) origem.focus();
      if (typeof opts.aoFechar === 'function') opts.aoFechar();
    }

    function copiar() {
      var s = simAtual();
      if (s.erro) return;
      var seg = segEscolhida(s);
      var valores = F.valoresCopia(s, seg, st.resp.renda);
      var registro = { resp: Object.assign({}, st.resp), seg: seg, imovel: Object.assign({}, st.imovel), resumo: resumoDe(s) };
      fechar();
      if (typeof opts.aoCopiar === 'function') opts.aoCopiar(valores, registro);
    }

    function pdf() {
      var s = simAtual();
      if (s.erro || !window.FinanciamentoPdf) return;
      var comp = F.comparar(st.resp, st.imovel, hoje);
      window.FinanciamentoPdf.gerar(F.dadosPdf({ comp: comp, sistema: st.resp.sistema, imovel: st.imovel, resp: st.resp,
        seg: segEscolhida(s), pessoas: { cliente: ctx.cliente || '', corretor: ctx.corretor || '' }, hoje: hoje }));
    }

    pop.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-acao]');
      if (!b || b.disabled) return;
      var a = b.getAttribute('data-acao'), v = b.getAttribute('data-v');
      if (a === 'fechar') fechar();
      else if (a === 'voltar') { if (ORDEM.indexOf(st.etapa) === 0) fechar(); else { st.etapa = ORDEM[ORDEM.indexOf(st.etapa) - 1]; st.erros = {}; render(); } }
      else if (a === 'avancar') avancar();
      else if (a === 'editar') { st.etapa = 1; render(); }
      else if (a === 'cidade') { st.imovel.cidade = v; delete st.erros.cidade; render(); }
      else if (a === 'tog') { st.resp[v] = v === 'fgts' ? st.resp.fgts === false : st.resp[v] !== true; render(); }
      else if (a === 'sis') { st.resp.sistema = v; render(); }
      else if (a === 'prazo') { st.resp.prazo = v ? +v : null; render(); }
      else if (a === 'seg') { st.seg = v; render(); }
      else if (a === 'copiar') copiar();
      else if (a === 'pdf') pdf();
    });
    veu.addEventListener('mousedown', function (ev) { if (ev.target === veu) fechar(); });

    pop.addEventListener('input', function (ev) {
      var c = ev.target.getAttribute('data-campo');
      if (!c) return;
      if (c === 'renda') st.resp.renda = num(ev.target.value);
      else if (c === 'valor') st.imovel.avaliacao = num(ev.target.value);
      else if (c === 'nascimento') {
        var d = ev.target.value.replace(/\D/g, '').slice(0, 8);
        var t = d.length > 4 ? d.slice(0, 2) + '/' + d.slice(2, 4) + '/' + d.slice(4) : d.length > 2 ? d.slice(0, 2) + '/' + d.slice(2) : d;
        if (t !== ev.target.value) ev.target.value = t;
        st.nascTxt = t;
        st.resp.nascimento = F.lerData(t);
        var idade = st.resp.nascimento ? F.idadeAnos(st.resp.nascimento, hoje) : null;
        pop.querySelector('.fz-idade').textContent = idade != null && idade >= 0 ? idade + ' anos' : '';
      }
      if (st.erros[c]) {
        delete st.erros[c];
        var caixa = ev.target.closest('.fz-input'); if (caixa) caixa.classList.remove('fz-input-erro');
        var msg = document.getElementById('fz-e-' + c); if (msg) msg.parentNode.removeChild(msg);
        ev.target.removeAttribute('aria-invalid');
      }
      var pv = pop.querySelector('.fz-previa'); if (pv) pv.innerHTML = previa();
    });

    function teclas(ev) {
      if (ev.key === 'Escape') { ev.preventDefault(); fechar(); return; }
      if (ev.key === 'Enter' && st.etapa !== 'resultado' && !ev.repeat && UI.enterAvanca(ev.target)) { ev.preventDefault(); avancar(); return; }
      if (ev.key === 'Tab') {
        var f = focaveis(pop);
        if (!f.length) return;
        var i = f.indexOf(document.activeElement);
        if (ev.shiftKey && (i <= 0)) { ev.preventDefault(); f[f.length - 1].focus(); }
        else if (!ev.shiftKey && i === f.length - 1) { ev.preventDefault(); f[0].focus(); }
      }
    }
    document.addEventListener('keydown', teclas, true);

    render();
    var inicial = st.etapa === 1 ? (document.getElementById(!(st.resp.renda > 0) ? 'fz-renda' : !temAvaliacao ? 'fz-valor' : 'fz-nasc')) : pop.querySelector('[data-acao="copiar"]');
    if (inicial) inicial.focus();

    aberto = { fechar: fechar };
    return aberto;
  }

  /* ---------- botao no passo Cliente do associativo (spec §6.1 e §6.4) ---------- */
  var CALC = '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="3" width="14" height="18" rx="3"></rect><path d="M8 7h8M8.5 12h.01M12 12h.01M15.5 12h.01M8.5 16h.01M12 16h.01M15.5 16h.01"></path></svg>';
  var ALERTA = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l9.5 17h-19z"></path><path d="M12 10v4M12 17h.01"></path></svg>';

  function imovelDe(ctx) {
    return { cidade: ctx.cidade || '', avaliacao: ctx.avaliacao > 0 ? ctx.avaliacao : 0, venda: ctx.venda > 0 ? ctx.venda : 0,
             ato: ctx.ato > 0 ? ctx.ato : 0, empId: ctx.empId || null, empNome: ctx.empNome || '',
             unidade: ctx.unidade || '', unidadeRotulo: ctx.unidadeRotulo || '' };
  }

  /* cfg = { tema, slot, contexto(), ler(), aplicar(valores), campos:{ renda, financiado, subsidio, parcFin } } */
  function ligarAssociativo(cfg) {
    var tema = cfg.tema === 'black' ? 'black' : 'claro';
    var slot = cfg.slot;
    var area = slot.closest('.card') || slot;          /* campos marcados herdam as cores do tema */
    area.setAttribute('data-fz-tema', tema);
    var st = { registro: null, retrato: null, anteriores: null, marcados: {}, velha: false, toast: null, timer: null };

    /* o que o corretor muda: empreendimento, unidade e o Valor do imovel digitado (valorImovel).
       A venda derivada da planilha pode mudar sozinha (promocionais carregam depois) e nao conta.
       completo = tirado com a planilha carregada (avaliacao conhecida). */
    function retratoDe(ctx) {
      return { empId: ctx.empId || null, unidade: ctx.unidade || '', venda: ctx.venda > 0 ? ctx.venda : 0,
               valorImovel: ctx.valorImovel > 0 ? ctx.valorImovel : 0, completo: ctx.avaliacao > 0 };
    }
    function mudou(antes, agora) {
      if (agora.empId !== antes.empId || agora.unidade !== antes.unidade) return true;
      if (agora.valorImovel === antes.valorImovel) return false;
      /* sem valor digitado na copia, a simulacao usou a venda da planilha: so avisa se o digitado for diferente dela */
      var ref = antes.valorImovel > 0 ? antes.valorImovel : antes.venda;
      return !(agora.valorImovel > 0) || Math.abs(agora.valorImovel - ref) > 1;
    }

    function alvos(campo) {
      var el = document.getElementById(cfg.campos[campo]);
      if (!el) return [];
      var par = el.closest('.pair');
      return par ? [par] : [el];
    }
    function marca(campo, on) {
      alvos(campo).forEach(function (n) { n.classList.toggle('fz-campo-sim', on); });
      var lab = document.querySelector('label[for="' + cfg.campos[campo] + '"]');
      if (!lab) return;
      var tag = lab.querySelector('.fz-tag');
      if (on && !tag) { tag = document.createElement('span'); tag.className = 'fz-tag'; tag.textContent = 'simulação'; lab.appendChild(tag); }
      if (!on && tag) tag.parentNode.removeChild(tag);
    }
    function marcaTodos(on) {
      Object.keys(cfg.campos).forEach(function (c) { st.marcados[c] = on; marca(c, on); });
    }

    function tiraToast() {
      clearTimeout(st.timer);
      if (st.toast && st.toast.parentNode) st.toast.parentNode.removeChild(st.toast);
      st.toast = null;
    }
    function mostraToast() {
      tiraToast();
      var t = document.createElement('div');
      t.className = 'fz-toast'; t.setAttribute('role', 'status'); t.setAttribute('data-fz-tema', tema);
      t.innerHTML = '<span class="fz-toast-ok">' + CHECK + '</span><span>4 campos preenchidos com a simulação</span><button type="button" data-fz="desfazer">Desfazer</button>';
      t.addEventListener('click', function (ev) { if (ev.target.closest('[data-fz="desfazer"]')) desfazer(); });
      document.body.appendChild(t);
      st.toast = t;
      st.timer = setTimeout(tiraToast, 6000);
    }

    function desenhaBotao() {
      slot.innerHTML = '<div class="fz-cta"><span class="fz-cta-ico">' + ICONE('calculadora', 54) + '</span>' +
        '<span class="fz-cta-txt"><b>Ainda sem a simulação da CAIXA?</b><span>Calcule financiamento, subsídio e parcela aqui e preencha estes campos com um clique.</span></span>' +
        '<button type="button" class="fz-cta-btn" data-fz="abrir">' + CALC + 'Simular financiamento</button></div>';
    }
    function desenhaFaixa() {
      if (st.velha) {
        slot.innerHTML = '<div class="fz-faixa fz-faixa-velha" role="status"><span class="fz-faixa-ico">' + ALERTA + '</span>' +
          '<span class="fz-faixa-txt"><b>A unidade mudou depois da simulação</b><span>Os valores continuam nos campos. Refaça para atualizar com a unidade nova.</span></span>' +
          '<button type="button" class="fz-faixa-lnk fz-faixa-pri" data-fz="refazer">Refazer</button></div>';
        return;
      }
      slot.innerHTML = '<div class="fz-faixa" role="status"><span class="fz-faixa-ico">' + CHECK + '</span>' +
        '<span class="fz-faixa-txt"><b>Financiamento simulado' + (st.registro.resumo ? ' · ' + esc(st.registro.resumo) : '') + '</b>' +
        '<span>Os campos em verde vieram da simulação. Editar um deles tira a marca.</span></span>' +
        '<button type="button" class="fz-faixa-lnk" data-fz="ver">Ver simulação</button>' +
        '<button type="button" class="fz-faixa-lnk" data-fz="pdf">' + BAIXAR + 'PDF</button></div>';
    }

    function aoCopiar(valores, registro) {
      var ctx = cfg.contexto();
      st.anteriores = cfg.ler();
      st.retrato = retratoDe(ctx);
      st.registro = registro;
      st.velha = false;
      cfg.aplicar(valores);
      marcaTodos(true);
      desenhaFaixa();
      mostraToast();
      var ver = slot.querySelector('[data-fz="ver"]'); if (ver) ver.focus();
    }
    function desfazer() {
      tiraToast();
      if (st.anteriores) cfg.aplicar(st.anteriores);
      marcaTodos(false);
      st.registro = null; st.anteriores = null; st.velha = false;
      desenhaBotao();
    }
    function abrirPopup(extra) {
      abrir(Object.assign({ tema: tema, contexto: cfg.contexto(), aoCopiar: aoCopiar }, extra || {}));
    }
    function pdf() {
      var ctx = cfg.contexto(), reg = st.registro;
      var im = reg.imovel && reg.imovel.avaliacao > 0 ? reg.imovel : imovelDe(ctx);
      if (!(im.avaliacao > 0) || !window.FinanciamentoPdf) return;
      var hoje = new Date(), comp = F.comparar(reg.resp, im, hoje);
      if (comp[reg.resp.sistema].erro) return;
      window.FinanciamentoPdf.gerar(F.dadosPdf({ comp: comp, sistema: reg.resp.sistema, imovel: im, resp: reg.resp, seg: reg.seg,
        pessoas: { cliente: ctx.cliente || '', corretor: ctx.corretor || '' }, hoje: hoje }));
    }

    slot.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-fz]');
      if (!b) return;
      var a = b.getAttribute('data-fz');
      if (a === 'abrir') abrirPopup();
      else if (a === 'ver') {
        var c = cfg.contexto(), im = st.registro.imovel;
        if (!(c.avaliacao > 0) && im && im.avaliacao > 0) c = Object.assign({}, c, { avaliacao: im.avaliacao, cidade: im.cidade || c.cidade });
        abrir({ tema: tema, contexto: c, aoCopiar: aoCopiar, respostas: st.registro.resp, seg: st.registro.seg, etapa: 'resultado' });
      }
      else if (a === 'refazer') abrirPopup({ respostas: st.registro.resp, seg: st.registro.seg, etapa: 1 });
      else if (a === 'pdf') pdf();
    });

    /* editar um campo copiado tira a marca so dele */
    Object.keys(cfg.campos).forEach(function (c) {
      [cfg.campos[c], cfg.campos[c] + '-p'].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.addEventListener('input', function () { if (st.marcados[c]) { st.marcados[c] = false; marca(c, false); } });
      });
    });

    desenhaBotao();
    var controle = {
      /* chamado no fim do render() do associativo */
      atualizar: function () {
        if (!st.registro) return;
        var ctx = cfg.contexto();
        if (!st.registro.resumo && ctx.avaliacao > 0) {
          var s = F.simular(st.registro.resp, imovelDe(ctx), new Date());
          if (!s.erro) { st.registro.resumo = resumoDe(s); if (!st.velha) desenhaFaixa(); }
        }
        if (st.velha) return;
        var r = retratoDe(ctx);
        /* retrato tirado com a planilha ainda carregando (chegada pela URL): adota o primeiro contexto completo */
        if (!st.retrato.completo && r.completo && r.empId === st.retrato.empId && r.unidade === st.retrato.unidade) { st.retrato = r; return; }
        /* sem valor digitado, a venda de referencia acompanha a planilha (promocionais, recarga) */
        if (!(st.retrato.valorImovel > 0) && !(r.valorImovel > 0) && r.empId === st.retrato.empId && r.unidade === st.retrato.unidade) st.retrato.venda = r.venda;
        if (mudou(st.retrato, r)) {
          st.velha = true;
          desenhaFaixa();
        }
      },
      limpar: function () {
        tiraToast();
        marcaTodos(false);
        st.registro = null; st.anteriores = null; st.velha = false;
        desenhaBotao();
      },
      /* chegada pela URL com origem=financiamento: marcas e faixa, sem toast nem Desfazer */
      restaurar: function (dados) {
        var ctx = cfg.contexto();
        st.registro = { resp: dados.resp, seg: dados.seg, imovel: imovelDe(ctx), resumo: '' };
        st.retrato = retratoDe(ctx);
        st.anteriores = null; st.velha = false;
        marcaTodos(true);
        desenhaFaixa();
      }
    };
    /* o associativo nao chama render() quando a planilha chega; depois dos ouvintes dele, confere de novo */
    if (window.SimUnidades && window.SimUnidades.aoMudar) {
      window.SimUnidades.aoMudar(function () { setTimeout(controle.atualizar, 0); });
    }
    return controle;
  }

  return { abrir: abrir, ligarAssociativo: ligarAssociativo };
})();

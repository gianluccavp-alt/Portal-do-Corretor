/* ============================================================
   SIMULADOR DE FINANCIAMENTO - tela dedicada /simulador-financiamento
   ------------------------------------------------------------
   Passos (Imovel, Renda, Idade, Perfil, Condicoes) e resultado.
   Regras: assets/financiamento.js. PDF: assets/financiamento-pdf.js.
   Visual: docs/design/simulador-financiamento/fonte (Desktop-*, Main, M*).
   Spec §7: docs/superpowers/specs/2026-11-07-simulador-financiamento-design.md
   ============================================================ */
(function () {
  'use strict';

  var F = window.Financiamento;
  var $ = function (id) { return document.getElementById(id); };
  var CHAVE = 'fz-ultima';
  var CIDADES = ['Ribeirão Preto', 'Campinas', 'Sorocaba'];
  var FOTOS = { gaia: 'village-gaia', park: 'village-park', botanico: 'reserva-direcional-jardim-botanico',
    ipiranga: 'direcional-conquista-clube-ipiranga', 'alta-vista': 'alta-vista-mangara', 'cores-da-mata': 'cores-da-mata-mangara',
    'casa-prado': 'casa-prado-residencial-riva', seleto: 'seleto-amoreiras', 'vila-da-mata': 'conquista-vila-da-mata' };
  var ROTULOS = { 1: 'Imóvel', 2: 'Renda', 3: 'Idade', 4: 'Perfil do cliente', 5: 'Condições', 6: 'Resultado' };
  var SETA = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>';
  var VOLTA = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"></path></svg>';
  var CHECK = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"></path></svg>';
  var CHEV = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"></path></svg>';

  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function num(t) { return window.Match ? window.Match.numero(t) : 0; }
  function semRs(n) { return F.brl(n).replace('R$ ', ''); }
  function inteiro(n) { return 'R$ ' + semRs(Math.round(n)).replace(/,\d+$/, ''); }
  function pct(v) { return v.toFixed(2).replace('.', ',') + '%'; }
  function dataTxt(d) { return d ? ('0' + d.getDate()).slice(-2) + '/' + ('0' + (d.getMonth() + 1)).slice(-2) + '/' + d.getFullYear() : ''; }
  function celular() { return !!(window.matchMedia && window.matchMedia('(max-width:860px)').matches); }
  function icone(n, t) { return '<img class="fz-ico" src="assets/img/icones-3d/' + n + '.svg" width="' + t + '" height="' + t + '" alt="">'; }
  var HOJE = new Date();

  /* ---------- estado ---------- */
  function novo() {
    return { etapa: 1, abertura: true, modo: 'portal', cidade: 'Ribeirão Preto', empId: null, blocoId: null, unidade: '',
             avaliacaoDigitada: 0, resp: Object.assign({}, F.RESP_PADRAO), seg: null, erros: {}, nascTxt: '', menos: false };
  }
  var st = novo();

  function salvar() {
    try {
      var c = Object.assign({}, st, { erros: {}, abertura: false });
      c.resp = Object.assign({}, st.resp, { nascimento: st.resp.nascimento ? st.resp.nascimento.toISOString() : null });
      sessionStorage.setItem(CHAVE, JSON.stringify(c));
    } catch (e) { /* sem sessionStorage */ }
  }
  function ultima() {
    try {
      var c = JSON.parse(sessionStorage.getItem(CHAVE) || 'null');
      if (!c || !c.resp) return null;
      c.resp.nascimento = c.resp.nascimento ? new Date(c.resp.nascimento) : null;
      return c;
    } catch (e) { return null; }
  }

  /* ---------- imovel a partir do estado ---------- */
  function emps() { return (window.SIM_EMPS || []).filter(function (e) { return e.cidade === st.cidade; }); }
  function empAtual() { return (window.SIM_EMPS || []).filter(function (e) { return e.id === st.empId; })[0] || null; }
  function planilhaOk() { return window.SimUnidades && SimUnidades.estado() === 'ok'; }
  function unidadesDe(e) { return e && planilhaOk() ? SimUnidades.porEmpreendimento(e) : { blocos: [], unidades: {}, detalhes: {}, total: 0 }; }
  function detalhe() { var e = empAtual(); return e && st.unidade ? unidadesDe(e).detalhes[st.unidade] || null : null; }
  function imovel() {
    if (st.modo === 'portal') {
      var e = empAtual(), d = detalhe();
      return { cidade: st.cidade, avaliacao: d && d.avaliacao > 0 ? d.avaliacao : st.avaliacaoDigitada,
               venda: d && d.associativoSemPremio > 0 ? d.associativoSemPremio : 0, ato: 0,
               empId: e ? e.id : null, empNome: e ? e.nome : '', unidade: st.unidade, unidadeRotulo: st.unidade };
    }
    return { cidade: st.cidade, avaliacao: st.avaliacaoDigitada, venda: 0, ato: 0, empId: null, empNome: '', unidade: '', unidadeRotulo: '' };
  }
  function semAvaliacaoNaPlanilha() { var d = detalhe(); return st.modo === 'portal' && st.unidade && !(d && d.avaliacao > 0); }

  /* ---------- validacao por passo ---------- */
  function errosDoPasso() {
    var im = imovel(), out = {};
    var lista = F.validar(st.resp, im, HOJE);
    var pega = function (campo) { lista.forEach(function (e) { if (e.campo === campo) out[campo] = e.mensagem; }); };
    if (st.etapa === 1) {
      if (st.modo === 'portal' && !st.empId) out.unidade = 'Escolha o empreendimento.';
      else if (st.modo === 'portal' && !st.unidade && planilhaOk()) out.unidade = 'Escolha a torre e a unidade.';
      if (st.modo === 'valor' || semAvaliacaoNaPlanilha() || !planilhaOk()) pega('valor');
      pega('cidade');
    } else if (st.etapa === 2) pega('renda');
    else if (st.etapa === 3) pega('nascimento');
    return out;
  }

  /* ---------- pecas ---------- */
  function erroDe(c) { return st.erros[c] ? '<p class="fz-erro" id="fzp-e-' + c + '">' + esc(st.erros[c]) + '</p>' : ''; }
  function attrsErro(c) { return st.erros[c] ? ' aria-invalid="true" aria-describedby="fzp-e-' + c + '"' : ''; }
  function cabecalho(n, titulo, desc, ico) {
    return '<div class="fzp-q-cab"><div><p class="fzp-olho">Passo ' + n + ' · ' + ROTULOS[n] + '</p><h2 class="fzp-q-t" id="fzp-q-t">' + titulo + '</h2>' +
      '<p class="fzp-q-p">' + desc + '</p></div>' + (ico ? '<span class="fzp-q-ico">' + icone(ico, 96) + '</span>' : '') + '</div>';
  }
  function pilulas(acao, itens, atual) {
    return itens.map(function (it) {
      var on = it[0] === atual;
      return '<button type="button" role="radio" aria-checked="' + on + '" class="fz-pill' + (on ? ' fz-pill-on' : '') + '" data-a="' + acao + '" data-v="' + esc(it[0] == null ? '' : it[0]) + '">' + esc(it[1]) + '</button>';
    }).join('');
  }

  function passo1() {
    var h = cabecalho(1, 'Qual imóvel o cliente quer?', 'Escolha a unidade e o valor de avaliação vem da planilha. Sem unidade? Digite o valor.', null);
    h += '<div class="fzp-linha"><div class="fz-segw fzp-segw" role="tablist" aria-label="Como informar o imóvel">' +
      ['portal', 'valor'].map(function (m) { var on = st.modo === m; return '<button type="button" role="tab" aria-selected="' + on + '" class="fz-seg' + (on ? ' fz-seg-on' : '') + '" data-a="modo" data-v="' + m + '">' + (m === 'portal' ? 'Unidade do portal' : 'Digitar valor') + '</button>'; }).join('') + '</div></div>';
    h += '<p class="fz-lab" id="fzp-l-cid">Cidade</p><div class="fz-pills" role="radiogroup" aria-labelledby="fzp-l-cid">' + pilulas('cidade', CIDADES.map(function (c) { return [c, c]; }), st.cidade) + '</div>' + erroDe('cidade');
    if (st.modo === 'portal') {
      if (!planilhaOk()) {
        h += '<div class="fz-nota fzp-mt">' + (window.SimUnidades && SimUnidades.estado() === 'erro'
          ? 'Não foi possível carregar a planilha agora. Use "Digitar valor".' : 'Carregando as unidades da planilha…') + '</div>';
      } else {
        h += '<div class="fzp-emps">' + emps().map(function (e) {
          var on = e.id === st.empId, f = FOTOS[e.id];
          return '<button type="button" class="fzp-emp' + (on ? ' fzp-emp-on' : '') + '" aria-pressed="' + on + '" data-a="emp" data-v="' + esc(e.id) + '">' +
            '<span class="fzp-emp-img">' + (f ? '<img src="assets/img/cards/' + f + '.webp" alt="" loading="lazy">' : icone('predio', 64)) + (on ? '<span class="fzp-emp-ok">' + CHECK + '</span>' : '') + '</span>' +
            '<span class="fzp-emp-n">' + esc(e.nome) + '</span><span class="fzp-emp-c">' + esc(e.cidade) + '</span></button>';
        }).join('') + '</div>';
        var e = empAtual();
        if (e) {
          var u = unidadesDe(e), lista = st.blocoId ? (u.unidades[st.blocoId] || []) : [];
          h += '<div class="fzp-grade2 fzp-mt">' +
            '<div><label class="fz-lab" for="fzp-bloco">Torre</label><span class="fzp-sel">' +
            '<select id="fzp-bloco" data-c="bloco"><option value="">Escolha a torre</option>' + u.blocos.map(function (b) { return '<option value="' + esc(b.id) + '"' + (b.id === st.blocoId ? ' selected' : '') + '>' + esc(b.label) + ' · ' + b.qtd + ' un.</option>'; }).join('') + '</select>' + CHEV + '</span></div>' +
            '<div><label class="fz-lab" for="fzp-un">Unidade</label><span class="fzp-sel">' +
            '<select id="fzp-un" data-c="unidade"' + (st.blocoId ? '' : ' disabled') + attrsErro('unidade') + '><option value="">' + (st.blocoId ? 'Escolha a unidade' : 'Escolha a torre primeiro') + '</option>' +
            lista.map(function (x) { var d = u.detalhes[x]; return '<option value="' + esc(x) + '"' + (x === st.unidade ? ' selected' : '') + '>' + esc(x) + (d && d.tipoLabel ? ' · ' + esc(d.tipoLabel) : '') + '</option>'; }).join('') +
            '</select>' + CHEV + '</span>' + erroDe('unidade') + '</div></div>';
          var d = detalhe();
          if (d && d.avaliacao > 0) {
            h += '<div class="fzp-aval"><span><span class="fzp-aval-k">Valor de avaliação</span><b>' + F.brl(d.avaliacao) + '</b></span><span class="fzp-aval-tag">Da planilha</span></div>';
          }
        } else h += erroDe('unidade');
      }
    }
    if (st.modo === 'valor' || semAvaliacaoNaPlanilha() || (st.modo === 'portal' && window.SimUnidades && SimUnidades.estado() === 'erro')) {
      h += '<div class="fzp-mt"><label class="fz-lab" for="fzp-valor">Valor de avaliação do imóvel' + (semAvaliacaoNaPlanilha() ? '<span class="fz-do" style="color:var(--fz-warn)">sem avaliação na planilha</span>' : '') + '</label>' +
        '<div class="fz-input fzp-input-g' + (st.erros.valor ? ' fz-input-erro' : '') + '"><span class="fz-pre">R$</span><input id="fzp-valor" data-c="valor" inputmode="decimal" autocomplete="off" placeholder="0,00" value="' + (st.avaliacaoDigitada > 0 ? semRs(st.avaliacaoDigitada) : '') + '"' + attrsErro('valor') + '></div>' + erroDe('valor') +
        '<p class="fzp-dica">É o valor que a CAIXA considera. Sem a avaliação em mãos, use o valor de venda.</p></div>';
    }
    return h;
  }
  function passo2() {
    return cabecalho(2, 'Qual a renda da família?', 'Some a renda bruta de todos os compradores. Ela define faixa, juros e o teto da parcela.', 'carteira') +
      '<label class="fz-lab" for="fzp-renda">Renda bruta familiar</label>' +
      '<div class="fz-input fzp-input-g' + (st.erros.renda ? ' fz-input-erro' : '') + '"><span class="fz-pre">R$</span><input id="fzp-renda" data-c="renda" inputmode="decimal" autocomplete="off" placeholder="0,00" value="' + (st.resp.renda > 0 ? semRs(st.resp.renda) : '') + '"' + attrsErro('renda') + '><span class="fz-pre">/mês</span></div>' + erroDe('renda') +
      '<p class="fzp-dica">Acima de R$ 13.000, ou se o cliente já tem imóvel na cidade, a conta muda para o SBPE.</p>';
  }
  function passo3() {
    var idade = st.resp.nascimento ? F.idadeAnos(st.resp.nascimento, HOJE) : null;
    var s = st.resp.nascimento ? F.simular(Object.assign({}, st.resp, { prazo: null }), imovel(), HOJE) : null;
    return cabecalho(3, 'Quando nasceu o comprador mais velho?', 'A idade define o prazo e o valor do seguro.', 'calendario') +
      '<label class="fz-lab" for="fzp-nasc">Data de nascimento</label>' +
      '<div class="fz-input fzp-input-g' + (st.erros.nascimento ? ' fz-input-erro' : '') + '"><input id="fzp-nasc" data-c="nascimento" inputmode="numeric" autocomplete="off" maxlength="10" placeholder="dd/mm/aaaa" value="' + esc(st.nascTxt) + '"' + attrsErro('nascimento') + '><span class="fz-idade" id="fzp-idade">' + (idade != null && idade >= 0 ? idade + ' anos' : '') + '</span></div>' + erroDe('nascimento') +
      '<div class="fzp-prazo-info" id="fzp-prazo-info">' + prazoInfo(s, idade) + '</div>' +
      '<p class="fzp-dica">Com mais de 70 anos e 6 meses a CAIXA não financia. Perto disso, o prazo encurta.</p>';
  }
  function prazoInfo(s, idade) {
    if (!s || idade == null || idade < 18) return '';
    if (s.erro) return '<div class="fz-pil fz-pil-alerta">' + esc(s.mensagem) + '</div>';
    return '<span class="fzp-idade-box"><b>' + idade + '</b><small>anos</small></span><span><b>Prazo de até ' + s.r.prazo + ' meses</b><small>' +
      (s.r.prazo >= 420 ? '35 anos, o máximo da CAIXA' : Math.floor(s.r.prazo / 12) + ' anos e ' + (s.r.prazo % 12) + ' meses') + '</small></span>';
  }
  function passo4() {
    var tiles = [['fgts', 'maleta', '3 anos de FGTS', 'Somando todos os períodos'], ['possuiImovel', 'chave', 'Já tem imóvel na cidade', 'Se sim, a conta vai para o SBPE']];
    if (F.mostraPerguntasSubsidio(st.resp.renda, st.resp.possuiImovel)) {
      tiles.push(['fatorSocial', 'pessoas', 'Mais de um comprador ou dependente', 'Sem isso, só 30% do subsídio']);
      tiles.push(['subsidioAnterior', 'presente', 'Já recebeu subsídio', 'Do FGTS ou da União']);
    }
    return cabecalho(4, 'O que vale para o cliente?', 'Essas respostas mudam o programa, os juros e o subsídio. Clique para ligar ou desligar.', null) +
      '<div class="fz-tiles fzp-tiles">' + tiles.map(function (t, i) {
        var on = t[0] === 'fgts' ? st.resp.fgts !== false : st.resp[t[0]] === true;
        return '<button type="button" role="switch" aria-checked="' + on + '" class="fz-tile' + (on ? ' fz-tile-on' : '') + '" data-a="tog" data-v="' + t[0] + '">' +
          '<span class="fz-tile-top"><span class="fzp-flutua" style="animation-delay:-' + (i * 1.1) + 's">' + icone(t[1], 76) + '</span><span class="fz-sw' + (on ? ' fz-sw-on' : '') + '"></span></span>' +
          '<span><span class="fz-tile-t">' + t[2] + '</span><span class="fz-tile-d">' + t[3] + '</span></span></button>';
      }).join('') + '</div>';
  }
  function linha(serie, cor) {
    if (!serie.length) return '';
    var max = 950, min = 250, w = 300, hh = 52;
    var pts = serie.map(function (v, i) { return (4 + i * (w - 8) / (serie.length - 1)).toFixed(1) + ',' + (4 + (max - Math.max(min, Math.min(max, v))) / (max - min) * hh).toFixed(1); }).join(' ');
    return '<svg viewBox="0 0 300 64" width="100%" height="64" aria-hidden="true" class="fzp-spark"><line x1="0" y1="60" x2="300" y2="60" stroke="var(--fz-line)"></line><polyline points="' + pts + '" fill="none" stroke="' + cor + '" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></polyline></svg>';
  }
  function passo5() {
    var im = imovel();
    var maxSim = F.simular(Object.assign({}, st.resp, { prazo: null, financiarAte: null }), im, HOJE);
    var maximo = maxSim.erro ? 420 : maxSim.r.prazo;
    var opcoes = [[null, 'Máximo · ' + maximo + ' meses']].concat([360, 300, 240].filter(function (p) { return p < maximo; }).map(function (p) { return [p, p + ' meses']; }));
    if (st.resp.prazo != null && !opcoes.some(function (o) { return o[0] === st.resp.prazo; })) st.resp.prazo = null;
    var comp = F.comparar(st.resp, im, HOJE);
    var cartao = function (id, desc) {
      var s = comp[id], on = st.resp.sistema === id, c = '', serie = [];
      if (!s.erro) {
        var seg = s.r.seguradoras.filter(function (x) { return x.codigo === s.segPadrao; })[0];
        serie = F.serieAnual(MotorCaixa.cronograma(s.motorIn, s.r, s.segPadrao));
        c = '<span class="fzp-opt-n"><span><span class="fz-k">Financia</span><b>' + inteiro(s.r.valorFinanciamento) + '</b></span>' +
          '<span><span class="fz-k">' + (id === 'SAC' ? '1ª → última' : '1ª parcela') + '</span><b>' + (id === 'SAC' ? inteiro(seg.primeira) + ' → ' + semRs(Math.round(seg.ultima)).replace(/,\d+$/, '') : inteiro(seg.primeira)) + '</b></span>' +
          '<span><span class="fz-k">Entrada</span><b>' + inteiro(s.entrada) + '</b></span></span>';
      } else c = '<span class="fz-pil fz-pil-alerta">' + esc(s.mensagem) + '</span>';
      var tag = id === 'PRICE' && !comp.PRICE.erro && !comp.SAC.erro && comp.PRICE.r.valorFinanciamento > comp.SAC.r.valorFinanciamento ? '<span class="fzp-tag-ok">Financia mais</span>' : '';
      return '<button type="button" role="radio" aria-checked="' + on + '" class="fz-opt fzp-opt' + (on ? ' fz-opt-on' : '') + '" data-a="sis" data-v="' + id + '">' +
        '<span class="fz-opt-t"><span class="fz-radio">' + CHECK + '</span>' + id + tag + '</span><span class="fz-opt-d">' + desc + '</span>' +
        linha(serie, id === 'PRICE' ? '#E4032B' : '#2563A8') + c + '</button>';
    };
    return cabecalho(5, 'Como o cliente quer pagar?', 'Os dois sistemas com os números deste cliente. Dá para trocar depois, no resultado.', 'calculadora') +
      '<div class="fz-opts fzp-opts" role="radiogroup" aria-label="Sistema de amortização">' + cartao('PRICE', 'Parcela parecida do começo ao fim.') + cartao('SAC', 'Parcela que cai todo mês. Financia menos, então a entrada sobe.') + '</div>' +
      '<div class="fzp-linha fzp-mt"><div><p class="fz-lab" id="fzp-l-prazo">Prazo</p><div class="fz-pills" role="radiogroup" aria-labelledby="fzp-l-prazo">' + pilulas('prazo', opcoes, st.resp.prazo) + '</div></div>' +
      '<div class="fzp-menos"><button type="button" role="switch" aria-checked="' + st.menos + '" class="fzp-menos-btn" data-a="menos"><span><b>Financiar menos que o máximo</b><small>Opcional · o resto vira entrada</small></span><span class="fz-sw' + (st.menos ? ' fz-sw-on' : '') + '"></span></button>' +
      (st.menos ? '<div class="fz-input fzp-input-m"><span class="fz-pre">R$</span><input id="fzp-menos" data-c="financiarAte" inputmode="decimal" autocomplete="off" placeholder="valor a financiar" aria-label="Valor que quer financiar" value="' + (st.resp.financiarAte > 0 ? semRs(st.resp.financiarAte) : '') + '"></div>' : '') +
      '</div></div>';
  }

  /* ---------- resumo das respostas (trilha e pilulas do celular) ---------- */
  function respostas() {
    var im = imovel(), idade = st.resp.nascimento ? F.idadeAnos(st.resp.nascimento, HOJE) : null;
    var perfil = [st.resp.fgts !== false ? 'FGTS 3 anos' : 'Sem FGTS'];
    if (st.resp.possuiImovel) perfil.push('tem imóvel');
    if (F.mostraPerguntasSubsidio(st.resp.renda, st.resp.possuiImovel)) perfil.push(st.resp.fatorSocial ? 'com dependente' : 'sem dependente');
    return {
      1: im.empNome ? im.empNome + (im.unidade ? ' · ' + im.unidade : '') : (im.avaliacao > 0 ? 'Imóvel de ' + inteiro(im.avaliacao) : ''),
      2: st.resp.renda > 0 ? F.brl(st.resp.renda).replace(/,00$/, '') + '/mês' : '',
      3: idade != null ? dataTxt(st.resp.nascimento) + ' · ' + idade + ' anos' : '',
      4: perfil.join(' · '),
      5: st.resp.sistema + ' · ' + (st.resp.prazo ? st.resp.prazo + ' meses' : 'prazo máximo')
    };
  }
  function trilha() {
    var r = respostas();
    $('fzp-trilha').innerHTML = [1, 2, 3, 4, 5, 6].map(function (k) {
      var estado = k < st.etapa ? 'feito' : k === st.etapa ? 'agora' : 'depois';
      if (estado === 'feito') {
        return '<li class="fzp-tl fzp-tl-feito"><button type="button" data-a="ir" data-v="' + k + '" aria-label="Editar ' + ROTULOS[k] + '">' +
          '<span class="fzp-tl-m"><span class="fzp-tl-ok">' + CHECK + '</span><span class="fzp-tl-l"></span></span>' +
          '<span class="fzp-tl-t"><small>' + ROTULOS[k] + '</small><b>' + esc(r[k]) + '</b></span><span class="fzp-tl-ed">Editar</span></button></li>';
      }
      if (estado === 'agora') {
        return '<li class="fzp-tl fzp-tl-agora" aria-current="step"><span class="fzp-tl-m"><span class="fzp-tl-now"></span><span class="fzp-tl-l fzp-tl-tr"></span></span>' +
          '<span class="fzp-tl-t"><small>Agora</small><b>' + ROTULOS[k] + '</b></span></li>';
      }
      return '<li class="fzp-tl fzp-tl-depois"><span class="fzp-tl-m"><span class="fzp-tl-o"></span>' + (k < 6 ? '<span class="fzp-tl-l fzp-tl-tr"></span>' : '') + '</span><span class="fzp-tl-t"><b>' + ROTULOS[k] + '</b></span></li>';
    }).join('');
    $('fzp-contador').textContent = Math.min(st.etapa, 5) + ' de 5';
  }
  function pilulasCelular() {
    var r = respostas(), itens = [];
    for (var k = 1; k < Math.min(st.etapa, 6); k++) if (r[k]) itens.push('<button type="button" class="fzp-chip" data-a="ir" data-v="' + k + '" aria-label="Editar ' + ROTULOS[k] + '">' + CHECK + esc(r[k]) + '</button>');
    return itens.length ? '<div class="fzp-chiprow">' + itens.join('') + '</div>' : '';
  }
  function previa() {
    var im = imovel(), box = $('fzp-previa');
    var pronto = st.resp.renda > 0 && im.avaliacao > 0 && CIDADES.indexOf(im.cidade) >= 0;
    if (!pronto) {
      box.className = 'fzp-previa fzp-previa-vazia';
      box.innerHTML = icone('alvo', 48) + '<div><b>Prévia ao vivo</b><span>Faixa, juros e parcela aparecem aqui conforme você responde.</span></div>';
      return;
    }
    var linhas;
    if (st.resp.nascimento) {
      var s = F.simular(st.resp, im, HOJE);
      if (s.erro) { box.className = 'fzp-previa fzp-previa-vazia'; box.innerHTML = '<div><b>Prévia ao vivo</b><span>' + esc(s.mensagem) + '</span></div>'; return; }
      linhas = [['Programa', F.programa(s.r)], ['Juros', pct(s.r.jurosNominal) + ' a.a.'], ['Prazo', s.r.prazo + ' meses'], ['Subsídio', s.r.subsidio > 0 ? inteiro(s.r.subsidio) : '—']];
      box.dataset.parcela = F.brl(s.parcelaMax);
    } else {
      var cid = MotorCaixa.CIDADES[MotorCaixa.MUNICIPIO_POR_CIDADE[im.cidade]];
      var sbpe = st.resp.possuiImovel || st.resp.renda > 13000;
      var enq = sbpe ? { faixa: 'SBPE', jn: 10.92 } : MotorCaixa.enquadrar(st.resp.renda, im.avaliacao, cid, st.resp.fgts !== false);
      if (!enq) { box.className = 'fzp-previa fzp-previa-vazia'; box.innerHTML = '<div><b>Prévia ao vivo</b><span>' + esc(F.mensagemErro('Fora do enquadramento MCMV')) + '</span></div>'; return; }
      linhas = [['Programa', enq.faixa === 'SBPE' ? 'SBPE' : 'MCMV · ' + enq.faixa], ['Juros', pct(enq.jn) + ' a.a.'], ['Prazo', 'falta a idade'], ['Subsídio', enq.subsidio ? 'pode ter' : '—']];
      box.dataset.parcela = F.brl((sbpe && st.resp.sistema !== 'SAC' ? 0.25 : 0.30) * st.resp.renda);
    }
    box.className = 'fzp-previa';
    box.innerHTML = '<p class="fzp-previa-t"><span class="fzp-vivo"></span>Prévia ao vivo</p><div class="fzp-previa-g">' +
      linhas.map(function (l) { return '<div><small>' + l[0] + '</small><b' + (l[0] === 'Subsídio' && l[1] !== '—' ? ' class="fzp-verde"' : '') + '>' + esc(l[1]) + '</b></div>'; }).join('') +
      '</div><div class="fzp-previa-p"><small>Parcela de até</small><b>' + box.dataset.parcela + '</b></div>';
  }

  /* ---------- render ---------- */
  function rodape() {
    var ultimoPasso = st.etapa === 5;
    return '<div class="fzp-rod"><button type="button" class="fz-ghost" data-a="voltar"' + (st.etapa === 1 ? ' hidden' : '') + '>' + VOLTA + 'Voltar</button>' +
      '<span class="fzp-rod-dir"><span class="fzp-enter">Pressione <kbd>Enter</kbd> para ' + (ultimoPasso ? 'ver o resultado' : 'continuar') + '</span>' +
      '<button type="button" class="fz-pri" data-a="avancar">' + (ultimoPasso ? 'Ver resultado' : 'Continuar') + SETA + '</button></span></div>';
  }
  function render(focarCampo) {
    document.body.dataset.etapa = st.etapa;
    document.body.classList.toggle('fzp-com-abertura', st.abertura && st.etapa === 1);
    $('fzp-passo').textContent = st.etapa <= 5 ? 'Passo ' + st.etapa + ' de 5' : 'Resultado';
    $('fzp-barra').style.width = (Math.min(st.etapa, 6) / 6 * 100) + '%';
    var rep = $('fzp-repetir'); if (rep) rep.hidden = !ultima();
    trilha();
    previa();
    var corpo = st.etapa === 1 ? passo1() : st.etapa === 2 ? passo2() : st.etapa === 3 ? passo3() : st.etapa === 4 ? passo4() : st.etapa === 5 ? passo5() : '';
    $('fzp-pergunta').innerHTML = st.etapa <= 5 ? pilulasCelular() + '<div class="fzp-q fzp-entra">' + corpo + '</div>' + rodape() : '';
    if (window.FinanciamentoResultado && st.etapa === 6) window.FinanciamentoResultado.render(st, imovel(), HOJE);
    else { var res = $('fzp-resultado'); if (res) { res.hidden = true; res.innerHTML = ''; } }
    if (focarCampo) {
      var el = $('fzp-pergunta').querySelector('[aria-invalid="true"]') || $('fzp-pergunta').querySelector('input:not([disabled]),select:not([disabled])');
      if (el) el.focus();
    }
  }

  function avancar() {
    if (st.etapa > 5) return;
    st.erros = errosDoPasso();
    if (Object.keys(st.erros).length) { render(true); return; }
    st.etapa += 1;
    salvar();
    render(false);
    window.scrollTo({ top: celular() || st.etapa === 6 ? 0 : (document.getElementById('fzp-palco').offsetTop - 16), behavior: 'smooth' });
    var f = $('fzp-pergunta').querySelector('input,select,button.fz-tile,button.fz-opt');
    if (f && st.etapa !== 4 && st.etapa !== 5) f.focus();
  }
  function voltar() {
    if (st.etapa === 1) { st.abertura = true; render(false); window.scrollTo(0, 0); return; }
    st.erros = {}; st.etapa -= 1; render(false);
  }
  function irPara(k) { st.erros = {}; st.etapa = k; render(true); }

  /* expostos para o resultado (assets/financiamento-app.js, Task 10) */
  window.FinanciamentoApp = {
    estado: function () { return st; }, imovel: imovel, render: render, irPara: irPara, salvar: salvar,
    novo: function () { var cidade = st.cidade; st = novo(); st.cidade = cidade; st.abertura = false; render(true); window.scrollTo(0, 0); }
  };

  /* ---------- eventos ---------- */
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-a]');
    if (!b || b.disabled) return;
    var a = b.getAttribute('data-a'), v = b.getAttribute('data-v');
    if (a === 'comecar') { st.abertura = false; render(true); window.scrollTo(0, 0); }
    else if (a === 'repetir') { var u = ultima(); if (u) { st = Object.assign(novo(), u, { abertura: false, erros: {} }); st.nascTxt = dataTxt(st.resp.nascimento); render(false); } }
    else if (a === 'voltar') voltar();
    else if (a === 'avancar') avancar();
    else if (a === 'ir') irPara(+v);
    else if (a === 'modo') { st.modo = v; st.erros = {}; render(false); }
    else if (a === 'cidade') { if (st.cidade !== v) { st.cidade = v; st.empId = null; st.blocoId = null; st.unidade = ''; } delete st.erros.cidade; render(false); }
    else if (a === 'emp') { if (st.empId !== v) { st.empId = v; st.blocoId = null; st.unidade = ''; var u2 = unidadesDe(empAtual()); if (u2.blocos.length === 1) st.blocoId = u2.blocos[0].id; } delete st.erros.unidade; render(false); }
    else if (a === 'tog') { st.resp[v] = v === 'fgts' ? st.resp.fgts === false : st.resp[v] !== true; render(false); salvar(); }
    else if (a === 'sis') { st.resp.sistema = v; render(false); salvar(); }
    else if (a === 'prazo') { st.resp.prazo = v ? +v : null; render(false); salvar(); }
    else if (a === 'menos') { st.menos = !st.menos; if (!st.menos) st.resp.financiarAte = null; render(false); if (st.menos) { var m = $('fzp-menos'); if (m) m.focus(); } }
  });
  document.addEventListener('change', function (ev) {
    var c = ev.target.getAttribute && ev.target.getAttribute('data-c');
    if (c === 'bloco') { st.blocoId = ev.target.value || null; st.unidade = ''; render(false); var un = $('fzp-un'); if (un && !un.disabled) un.focus(); }
    else if (c === 'unidade') { st.unidade = ev.target.value; delete st.erros.unidade; render(false); }
    else if (c === 'financiarAte') { render(false); salvar(); }
  });
  document.addEventListener('input', function (ev) {
    var c = ev.target.getAttribute && ev.target.getAttribute('data-c');
    if (!c) return;
    if (c === 'renda') st.resp.renda = num(ev.target.value);
    else if (c === 'valor') st.avaliacaoDigitada = num(ev.target.value);
    else if (c === 'financiarAte') st.resp.financiarAte = num(ev.target.value) || null;
    else if (c === 'nascimento') {
      var d = ev.target.value.replace(/\D/g, '').slice(0, 8);
      var t = d.length > 4 ? d.slice(0, 2) + '/' + d.slice(2, 4) + '/' + d.slice(4) : d.length > 2 ? d.slice(0, 2) + '/' + d.slice(2) : d;
      if (t !== ev.target.value) ev.target.value = t;
      st.nascTxt = t; st.resp.nascimento = F.lerData(t);
      var idade = st.resp.nascimento ? F.idadeAnos(st.resp.nascimento, HOJE) : null;
      $('fzp-idade').textContent = idade != null && idade >= 0 ? idade + ' anos' : '';
      var s = st.resp.nascimento ? F.simular(Object.assign({}, st.resp, { prazo: null }), imovel(), HOJE) : null;
      $('fzp-prazo-info').innerHTML = prazoInfo(s, idade);
    } else return;
    if (st.erros[c === 'financiarAte' ? '' : c]) {
      delete st.erros[c];
      var caixa = ev.target.closest('.fz-input'); if (caixa) caixa.classList.remove('fz-input-erro');
      var msg = $('fzp-e-' + c); if (msg) msg.parentNode.removeChild(msg);
      ev.target.removeAttribute('aria-invalid');
    }
    previa();
  });
  document.addEventListener('focusout', function (ev) {
    var c = ev.target.getAttribute && ev.target.getAttribute('data-c');
    if (c === 'renda' && st.resp.renda > 0) ev.target.value = semRs(st.resp.renda);
    if (c === 'valor' && st.avaliacaoDigitada > 0) ev.target.value = semRs(st.avaliacaoDigitada);
    if (c === 'renda' || c === 'valor' || c === 'nascimento') salvar();
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Enter' && st.etapa <= 5 && !st.abertura && ev.target.tagName === 'INPUT') { ev.preventDefault(); avancar(); }
  });

  /* ---------- planilha ---------- */
  if (window.SimUnidades) {
    SimUnidades.aoMudar(function () {
      if (SimUnidades.estado() === 'erro' && st.modo === 'portal' && !st.empId) st.modo = 'valor';
      if (st.etapa <= 1 || st.etapa === 6) render(false);
      else previa();
    });
    SimUnidades.carregar();
  }
  render(false);
})();

/* ============================================================
   RESULTADO da tela dedicada (spec §7; quadros Desktop-Resultado e M6-Resultado)
   ============================================================ */
window.FinanciamentoResultado = (function () {
  'use strict';
  var F = window.Financiamento;
  var CHAVE_CORRETOR = 'mt-corretor';   /* o mesmo do Match */
  var CORES = { PRICE: '#E4032B', SAC: '#2563A8' };
  var CHECK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"></path></svg>';
  var SETA = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg>';
  var BAIXAR = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"></path></svg>';
  var LAPIS = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16v4z"></path></svg>';
  var NOVA = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12a8 8 0 1 0 2.4-5.7M4 4v4h4"></path></svg>';
  var ctx = null;   /* { st, im, hoje, comp, series } da ultima renderizacao */

  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function pct(v) { return v.toFixed(2).replace('.', ',') + '%'; }
  function inteiro(n) { return F.brl(Math.round(n)).replace(/,\d+$/, ''); }
  function mil(n) { return 'R$ ' + Math.round(n / 1000).toLocaleString('pt-BR') + ' mil'; }
  function lerLS(k) { try { return localStorage.getItem(k) || ''; } catch (e) { return ''; } }
  function gravarLS(k, v) { try { if (v) localStorage.setItem(k, v); else localStorage.removeItem(k); } catch (e) { /* sem localStorage */ } }
  function segDe(s, cod) { return s.r.seguradoras.filter(function (x) { return x.codigo === cod; })[0] || s.r.seguradoras.filter(function (x) { return x.codigo === s.segPadrao; })[0]; }
  function nomeSeg(n) { return n.toLowerCase().replace(/(^|\s)\S/g, function (c) { return c.toUpperCase(); }); }
  function totalPago(cron) { return cron.reduce(function (t, x) { return t + x.encargo; }, 0); }

  function grafico(series, idade0) {
    var todos = series.PRICE.concat(series.SAC);
    if (!todos.length) return '';
    var lo = 250, hi = Math.max(950, Math.ceil(Math.max.apply(null, todos) / 100) * 100 + 50);
    lo = Math.max(0, Math.min(lo, Math.floor(Math.min.apply(null, todos) / 100) * 100 - 50));
    var L = 56, T = 12, W = 620, H = 190, n = Math.max(series.PRICE.length, series.SAC.length);
    var x = function (i) { return L + i * W / (n - 1); }, y = function (v) { return T + (hi - v) / (hi - lo) * H; };
    var grade = [], passo = (hi - lo) > 900 ? 500 : 300;
    for (var g = Math.ceil(lo / passo) * passo; g <= hi; g += passo) grade.push(g);
    var linha = function (k) { return series[k].length ? '<polyline class="fzr-draw" points="' + series[k].map(function (v, i) { return x(i).toFixed(1) + ',' + y(v).toFixed(1); }).join(' ') + '" fill="none" stroke="' + CORES[k] + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></polyline>' : ''; };
    var rotX = []; for (var i = 0; i < n; i++) rotX.push('<text x="' + x(i).toFixed(1) + '" y="' + (T + H + 22) + '" text-anchor="middle">' + (i === 0 ? 'hoje' : i === n - 1 ? 'fim' : (i * 5) + ' anos') + '</text>');
    return '<svg class="fzr-svg" viewBox="0 0 700 236" role="img" aria-label="Parcela ao longo do prazo em PRICE e SAC">' +
      '<g font-family="DM Sans, sans-serif" font-size="12" fill="#727A7D">' +
      grade.map(function (v) { return '<line x1="' + L + '" y1="' + y(v).toFixed(1) + '" x2="690" y2="' + y(v).toFixed(1) + '" stroke="#EEF0F1"></line><text x="0" y="' + (y(v) + 4).toFixed(1) + '">' + inteiro(v) + '</text>'; }).join('') +
      rotX.join('') + '</g>' + linha('SAC') + linha('PRICE') +
      '<g class="fzr-cursor" opacity="0"><line class="fzr-cur-l" y1="' + T + '" y2="' + (T + H) + '" stroke="#3A4043" stroke-opacity=".35" stroke-dasharray="3 4"></line>' +
      '<circle class="fzr-cur-p" r="5" fill="#E4032B" stroke="#fff" stroke-width="2"></circle><circle class="fzr-cur-s" r="5" fill="#2563A8" stroke="#fff" stroke-width="2"></circle>' +
      '<g class="fzr-cur-box"><rect width="176" height="78" rx="12" fill="#2B3033"></rect><text class="fzr-cur-t" x="14" y="22" font-size="12" fill="#B4BCC0" font-family="DM Sans, sans-serif"></text>' +
      '<circle cx="18" cy="41" r="4" fill="#FF6B7E"></circle><text x="28" y="45" font-size="13" fill="#fff" font-family="DM Sans, sans-serif">PRICE</text><text class="fzr-cur-vp" x="162" y="45" font-size="13" font-weight="700" fill="#fff" text-anchor="end" font-family="DM Sans, sans-serif"></text>' +
      '<circle cx="18" cy="62" r="4" fill="#7FB0E8"></circle><text x="28" y="66" font-size="13" fill="#fff" font-family="DM Sans, sans-serif">SAC</text><text class="fzr-cur-vs" x="162" y="66" font-size="13" font-weight="700" fill="#fff" text-anchor="end" font-family="DM Sans, sans-serif"></text></g></g>' +
      '<rect class="fzr-hit" x="' + L + '" y="0" width="' + W + '" height="' + (T + H) + '" fill="transparent"></rect></svg>' +
      '<span hidden class="fzr-meta" data-l="' + L + '" data-w="' + W + '" data-t="' + T + '" data-h="' + H + '" data-lo="' + lo + '" data-hi="' + hi + '" data-n="' + n + '" data-idade="' + idade0 + '"></span>';
  }

  function ligaCursor(box) {
    var svg = box.querySelector('.fzr-svg'), meta = box.querySelector('.fzr-meta');
    if (!svg || !meta) return;
    var L = +meta.dataset.l, W = +meta.dataset.w, T = +meta.dataset.t, H = +meta.dataset.h, lo = +meta.dataset.lo, hi = +meta.dataset.hi, n = +meta.dataset.n, idade0 = +meta.dataset.idade;
    var y = function (v) { return T + (hi - v) / (hi - lo) * H; };
    var cur = svg.querySelector('.fzr-cursor');
    function mostra(i) {
      var P = ctx.series.PRICE[i], S = ctx.series.SAC[i], xx = L + i * W / (n - 1);
      cur.setAttribute('opacity', '1');
      svg.querySelector('.fzr-cur-l').setAttribute('x1', xx); svg.querySelector('.fzr-cur-l').setAttribute('x2', xx);
      var cp = svg.querySelector('.fzr-cur-p'), cs = svg.querySelector('.fzr-cur-s');
      if (P != null) { cp.setAttribute('cx', xx); cp.setAttribute('cy', y(P)); cp.style.display = ''; } else cp.style.display = 'none';
      if (S != null) { cs.setAttribute('cx', xx); cs.setAttribute('cy', y(S)); cs.style.display = ''; } else cs.style.display = 'none';
      var anos = i === n - 1 ? Math.round(ctx.prazo / 12) : i * 5;
      svg.querySelector('.fzr-cur-t').textContent = (i === 0 ? 'Hoje' : 'Daqui a ' + anos + ' anos') + ' · ' + (idade0 + anos) + ' anos';
      svg.querySelector('.fzr-cur-vp').textContent = P != null ? inteiro(P) : '—';
      svg.querySelector('.fzr-cur-vs').textContent = S != null ? inteiro(S) : '—';
      var bx = xx + 14 + 176 > 690 ? xx - 190 : xx + 14;
      svg.querySelector('.fzr-cur-box').setAttribute('transform', 'translate(' + bx + ',' + (T + 26) + ')');
    }
    svg.addEventListener('mousemove', function (ev) {
      var r = svg.getBoundingClientRect(), px = (ev.clientX - r.left) / r.width * 700;
      mostra(Math.max(0, Math.min(n - 1, Math.round((px - L) / (W / (n - 1))))));
    });
    svg.addEventListener('mouseleave', function () { cur.setAttribute('opacity', '0'); });
  }

  function render(st, im, hoje) {
    var box = document.getElementById('fzp-resultado');
    box.hidden = false;
    var comp = F.comparar(st.resp, im, hoje), s = comp[st.resp.sistema];
    if (s.erro) {
      ctx = { st: st, im: im, hoje: hoje, comp: comp, series: { PRICE: [], SAC: [] }, prazo: 0, erro: true };
      box.innerHTML = '<div class="fzr-in"><div class="fzr-erro fzp-entra"><img class="fz-ico" src="assets/img/icones-3d/alvo.svg" width="64" height="64" alt="">' +
        '<div><h1 class="fzr-erro-t">Não deu para simular</h1><p>' + esc(s.mensagem) + '</p><button type="button" class="fz-pri" data-r="editar">' + LAPIS + 'Editar respostas</button></div></div></div>';
      return;
    }
    var cod = segDe(s, st.seg).codigo; st.seg = cod;
    var r = s.r, seg = segDe(s, cod), outro = st.resp.sistema === 'PRICE' ? 'SAC' : 'PRICE';
    var cronos = {}, series = { PRICE: [], SAC: [] };
    ['PRICE', 'SAC'].forEach(function (k) {
      if (comp[k].erro) return;
      cronos[k] = MotorCaixa.cronograma(comp[k].motorIn, comp[k].r, segDe(comp[k], cod).codigo);
      series[k] = F.serieAnual(cronos[k]);
    });
    var idade0 = F.idadeAnos(st.resp.nascimento, hoje);
    ctx = { st: st, im: im, hoje: hoje, comp: comp, series: series, prazo: r.prazo };
    var base = s.baseEntrada === 'venda' ? im.venda : im.avaliacao;
    var pf = r.valorFinanciamento / base * 100, ps = r.subsidio / base * 100, pe = Math.max(0, s.entrada) / base * 100;
    var pctRenda = Math.round(seg.primeira / st.resp.renda * 100);
    var segp = function (k) { var on = st.resp.sistema === k; return '<button type="button" role="tab" aria-selected="' + on + '" class="fz-seg' + (on ? ' fz-seg-on' : '') + '" data-r="sis" data-v="' + k + '">' + k + '</button>'; };
    var cel = function (k, f) { return comp[k].erro ? '—' : f(comp[k]); };
    var lugar = im.empNome ? im.empNome + (im.unidade ? ' · ' + im.unidade : '') : 'Imóvel de ' + inteiro(im.avaliacao) + ' em ' + im.cidade;
    var respostas = [['Renda', F.brl(st.resp.renda)], ['Nascimento', ('0' + st.resp.nascimento.getDate()).slice(-2) + '/' + ('0' + (st.resp.nascimento.getMonth() + 1)).slice(-2) + '/' + st.resp.nascimento.getFullYear()],
      ['FGTS 3 anos', st.resp.fgts !== false ? 'Sim' : 'Não'], ['Imóvel na cidade', st.resp.possuiImovel ? 'Sim' : 'Não']];
    if (F.mostraPerguntasSubsidio(st.resp.renda, st.resp.possuiImovel)) respostas.push(['Dependente', st.resp.fatorSocial ? 'Sim' : 'Não'], ['Subsídio anterior', st.resp.subsidioAnterior ? 'Sim' : 'Não']);

    box.innerHTML = '<div class="fzr-in">' +
      '<div class="fzr-topo fzp-entra"><div><p class="fzr-ok">' + CHECK + 'Simulação pronta</p>' +
        '<h1 class="fzr-t">Financia até <span>' + F.brl(r.valorFinanciamento) + '</span></h1>' +
        '<p class="fzr-sub">' + esc(lugar) + ' · renda de ' + F.brl(st.resp.renda).replace(/,00$/, '') + '/mês · ' + idade0 + ' anos</p>' +
        (s.limitado ? '<p class="fzr-limite">A CAIXA aprova até ' + F.brl(s.capacidade) + ' para esta renda; o valor do imóvel não pede mais que isso.</p>' : '') + '</div>' +
        '<div class="fzr-acoes"><button type="button" class="fz-sec" data-r="editar">' + LAPIS + 'Editar respostas</button>' +
        '<button type="button" class="fz-sec" data-r="pdf">' + BAIXAR + 'Baixar PDF</button>' +
        '<button type="button" class="fz-pri" data-r="levar">Levar ao associativo' + SETA + '</button></div></div>' +
      '<div class="fzr-kpis fzp-entra">' +
        '<div class="fzr-kpi"><small>Enquadramento</small><b>' + esc(F.programa(r)) + '</b></div>' +
        '<div class="fzr-kpi"><small>Juros CAIXA</small><b>' + pct(r.jurosNominal) + ' a.a.</b><small>efetivo ' + pct(r.jurosEfetivo) + '</small></div>' +
        '<div class="fzr-kpi"><small>Prazo</small><b>' + r.prazo + ' meses</b><small>' + (r.prazo % 12 ? Math.floor(r.prazo / 12) + ' anos e ' + (r.prazo % 12) + ' meses' : (r.prazo / 12) + ' anos') + '</small></div>' +
        (r.subsidio > 0 ? '<div class="fzr-kpi fzr-kpi-ok"><small>Subsídio</small><b>' + F.brl(r.subsidio) + '</b><small>' + (st.resp.fatorSocial ? 'com dependente' : 'só o comprador') + '</small></div>'
          : '<div class="fzr-kpi"><small>Subsídio</small><b>—</b><small>' + (r.faixa === 'SBPE' ? 'SBPE não tem subsídio' : 'sem direito nesta faixa') + '</small></div>') +
        '<div class="fzr-kpi"><small>Taxa de administração</small><b>' + F.brl(r.taxaAdm) + '</b><small>por mês</small></div></div>' +
      '<div class="fzr-grade"><div class="fzr-principal">' +
        '<article class="fzr-card fzr-card-g fzp-entra"><div class="fzr-card-cab"><h2>Como fecham os ' + inteiro(base) + '</h2><div class="fz-segw" role="tablist" aria-label="Sistema de amortização">' + segp('PRICE') + segp('SAC') + '</div></div>' +
          '<div class="fzr-barra"><span style="width:' + pf.toFixed(2) + '%" class="fzr-b-fin"></span>' + (r.subsidio > 0 ? '<span style="width:' + ps.toFixed(2) + '%" class="fzr-b-sub"></span>' : '') + '<span class="fzr-b-ent"></span></div>' +
          '<div class="fzr-leg"><div><small><i class="fzr-d fzr-d-fin"></i>Financiamento · ' + Math.round(pf) + '%</small><b>' + F.brl(r.valorFinanciamento) + '</b></div>' +
          (r.subsidio > 0 ? '<div><small><i class="fzr-d fzr-d-sub"></i>Subsídio · ' + Math.round(ps) + '%</small><b class="fzr-verde">' + F.brl(r.subsidio) + '</b></div>' : '') +
          '<div><small><i class="fzr-d fzr-d-ent"></i>Entrada mínima · ' + Math.round(pe) + '%</small><b>' + F.brl(s.entrada) + '</b></div></div>' +
          '<div class="fzr-parcelas"><div class="fzr-parc"><div class="fzr-parc-l"><div><small>1ª parcela</small><b>' + F.brl(seg.primeira) + '</b></div><div class="fzr-dir"><small>da renda</small><b class="fzr-verde">' + pctRenda + '%</b></div></div>' +
            '<div class="fzr-trilho"><span style="width:' + Math.min(100, pctRenda / (r.comprometimento * 100) * 100).toFixed(1) + '%"></span></div><p>Parcela máxima da CAIXA: ' + Math.round(r.comprometimento * 100) + '% da renda (' + F.brl(s.parcelaMax) + ').</p></div>' +
          '<div class="fzr-parc"><small>Última parcela</small><b>' + F.brl(seg.ultima) + '</b><p>Sem o seguro de danos físicos, que zera no último mês.</p></div></div></article>' +
        '<article class="fzr-card fzp-entra"><div class="fzr-card-cab"><div><h2>Parcela ao longo do prazo</h2><p>Encargo com seguros, ' + esc(nomeSeg(seg.nome)) + ' · estimativa</p></div>' +
          '<div class="fzr-legenda"><span><i style="background:#E4032B"></i>PRICE</span><span><i style="background:#2563A8"></i>SAC</span></div></div>' +
          '<div class="fzr-graf"><div class="fzr-graf-svg">' + grafico(series, idade0) + '</div>' +
          '<table class="fzr-tab"><thead><tr><th scope="col"><span class="fzr-sr">Item</span></th><th scope="col">PRICE</th><th scope="col">SAC</th></tr></thead><tbody>' +
          '<tr><td>Financia</td><td>' + cel('PRICE', function (c) { return inteiro(c.r.valorFinanciamento); }) + '</td><td>' + cel('SAC', function (c) { return inteiro(c.r.valorFinanciamento); }) + '</td></tr>' +
          '<tr><td>Entrada</td><td>' + cel('PRICE', function (c) { return inteiro(c.entrada); }) + '</td><td>' + cel('SAC', function (c) { return inteiro(c.entrada); }) + '</td></tr>' +
          '<tr><td>1ª parcela</td><td>' + cel('PRICE', function (c) { return inteiro(segDe(c, cod).primeira); }) + '</td><td>' + cel('SAC', function (c) { return inteiro(segDe(c, cod).primeira); }) + '</td></tr>' +
          '<tr><td>Última</td><td>' + cel('PRICE', function (c) { return inteiro(segDe(c, cod).ultima); }) + '</td><td>' + cel('SAC', function (c) { return inteiro(segDe(c, cod).ultima); }) + '</td></tr>' +
          '<tr><td>Total pago*</td><td>' + (cronos.PRICE ? mil(totalPago(cronos.PRICE)) : '—') + '</td><td>' + (cronos.SAC ? mil(totalPago(cronos.SAC)) : '—') + '</td></tr>' +
          '</tbody></table></div><p class="fzr-nota">* Soma das parcelas com seguros no prazo todo. No PRICE o seguro de vida sobe com a idade, por isso a parcela pode crescer com o tempo.</p></article>' +
        '<article class="fzr-card fzp-entra"><div class="fzr-card-cab fzr-cab-ico"><img class="fz-ico" src="assets/img/icones-3d/escudo.svg" width="48" height="48" alt=""><div><h2>Seguradora</h2><p>A escolhida vai para o PDF e para o associativo</p></div></div>' +
          '<div class="fzr-segs" role="radiogroup" aria-label="Seguradora"><div class="fzr-seg-h"><span></span><span>Seguradora</span><span>1ª parcela</span><span>Última</span></div>' +
          r.seguradoras.map(function (x) {
            var on = x.codigo === cod, maior = x.codigo === s.segPadrao;
            var menor = r.seguradoras.every(function (y) { return y.primeira >= x.primeira; });
            return '<button type="button" role="radio" aria-checked="' + on + '" class="fzr-seg' + (on ? ' fzr-seg-on' : '') + '" data-r="seg" data-v="' + x.codigo + '"><span class="fz-radio">' + CHECK + '</span>' +
              '<span><b>' + esc(nomeSeg(x.nome)) + '</b>' + (maior ? '<small>Maior parcela · é a que limita o financiamento</small>' : menor ? '<small class="fzr-verde2">Menor parcela</small>' : '') + '</span>' +
              '<span class="fzr-num">' + F.brl(x.primeira) + '</span><span class="fzr-num fzr-cinza">' + F.brl(x.ultima) + '</span></button>';
          }).join('') + '</div></article></div>' +
      '<aside class="fzr-lado">' +
        '<div class="fzr-prox"><img class="fz-ico" src="assets/img/icones-3d/calculadora.svg" width="88" height="88" alt=""><p class="fzr-prox-o">Próximo passo</p><h3>Monte o fluxo no associativo</h3><p>Renda, financiamento, subsídio e parcela já entram preenchidos.</p><button type="button" data-r="levar">Abrir no associativo →</button></div>' +
        '<div class="fzr-card fzr-pdf"><h3>PDF para o cliente</h3><label class="fz-lab" for="fzr-cli">Nome do cliente <span class="fzr-cinza">opcional</span></label><input id="fzr-cli" class="fzr-in-txt" autocomplete="off" value="' + esc(st.cliente || '') + '">' +
          '<label class="fz-lab" for="fzr-cor">Corretor <span class="fzr-cinza">opcional</span></label><input id="fzr-cor" class="fzr-in-txt" autocomplete="off" value="' + esc(lerLS(CHAVE_CORRETOR)) + '">' +
          '<button type="button" class="fz-sec fzr-pdf-btn" data-r="pdf">' + BAIXAR + 'Baixar PDF</button></div>' +
        '<div class="fzr-card"><div class="fzr-cab-ico"><img class="fz-ico" src="assets/img/icones-3d/alvo.svg" width="48" height="48" alt=""><h3>Como chegamos aqui</h3></div><ul class="fzr-lista">' +
          '<li>Parcela de até ' + Math.round(r.comprometimento * 100) + '% da renda: ' + F.brl(s.parcelaMax) + '.</li>' +
          '<li>Financiamento de até ' + Math.round(r.cota * 100) + '% do imóvel' + (r.valorFinanciamento < r.cota * s.motorIn.valor - 1 ? '. Aqui a parcela limitou antes.' : '.') + '</li>' +
          '<li>Prazo pela idade: ' + r.prazo + ' meses aos ' + idade0 + ' anos.</li>' +
          (r.subsidio > 0 ? '<li>Subsídio pela renda, pela cidade' + (st.resp.fatorSocial ? ' e por ter dependente.' : '.') + '</li>' : '') +
          (s.trava ? '<li>Imóvel avaliado acima de R$ 400 mil e vendido abaixo disso: a CAIXA simula em R$ 400 mil.</li>' : '') + '</ul></div>' +
        '<div class="fzr-card"><h3>Respostas</h3><dl class="fzr-resp">' + respostas.map(function (x) { return '<dt>' + x[0] + '</dt><dd>' + esc(x[1]) + '</dd>'; }).join('') + '</dl>' +
          '<button type="button" class="fzr-lnk" data-r="nova">' + NOVA + 'Nova simulação</button></div>' +
        '<p class="fzr-aviso">Estimativa do motor calibrado no Simulador Habitacional CAIXA. Sujeita à análise de crédito da CAIXA e à aprovação da Direcional.</p></aside></div>' +
      '<div class="fzr-rod-cel"><button type="button" class="fz-sec" data-r="pdf">' + BAIXAR + 'PDF</button><button type="button" class="fz-pri" data-r="levar">Levar ao associativo' + SETA + '</button></div>' +
      '</div>';
    ligaCursor(box);
  }

  function pdf() {
    var st = ctx.st, cli = document.getElementById('fzr-cli'), cor = document.getElementById('fzr-cor');
    st.cliente = cli ? cli.value.trim() : '';
    var corretor = cor ? cor.value.trim() : lerLS(CHAVE_CORRETOR);
    gravarLS(CHAVE_CORRETOR, corretor);
    if (!window.FinanciamentoPdf) return;
    window.FinanciamentoPdf.gerar(F.dadosPdf({ comp: ctx.comp, sistema: st.resp.sistema, imovel: ctx.im, resp: st.resp, seg: st.seg,
      pessoas: { cliente: st.cliente, corretor: corretor }, hoje: ctx.hoje }));
  }

  function levar() {
    var st = ctx.st, s = ctx.comp[st.resp.sistema], d = F.destinos(ctx.im);
    var url = function (dest) { return F.urlAssociativo(dest, ctx.im, st.resp, s, st.seg, ctx.hoje); };
    if (d.length === 1) { location.href = url(d[0]); return; }
    var veu = document.createElement('div');
    veu.className = 'fz-veu'; veu.setAttribute('data-fz-tema', 'claro');
    veu.innerHTML = '<div class="fzr-escolha" role="dialog" aria-modal="true" aria-labelledby="fzr-esc-t"><h2 id="fzr-esc-t">Para qual simulador?</h2>' +
      '<p>A unidade é de ' + esc(ctx.im.cidade) + ', onde vale a condição Black Friday.</p>' +
      '<a class="fz-sec" href="' + esc(url('normal')) + '">Associativo</a><a class="fz-pri" href="' + esc(url('blackfriday')) + '">Associativo Black Friday</a>' +
      '<button type="button" class="fz-ghost" data-fecha>Cancelar</button></div>';
    var fecha = function () { document.removeEventListener('keydown', tecla, true); veu.remove(); };
    var tecla = function (ev) { if (ev.key === 'Escape') fecha(); };
    veu.addEventListener('click', function (ev) { if (ev.target === veu || ev.target.closest('[data-fecha]')) fecha(); });
    document.addEventListener('keydown', tecla, true);
    document.body.appendChild(veu);
    veu.querySelector('.fz-pri').focus();
  }

  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-r]');
    if (!b || !ctx) return;
    var a = b.getAttribute('data-r'), App = window.FinanciamentoApp;
    if (a === 'editar') App.irPara(ctx.erro ? 1 : 5);
    else if (a === 'sis') { ctx.st.resp.sistema = b.getAttribute('data-v'); App.salvar(); App.render(false); }
    else if (a === 'seg') { ctx.st.seg = b.getAttribute('data-v'); App.salvar(); App.render(false); }
    else if (a === 'pdf') pdf();
    else if (a === 'levar') levar();
    else if (a === 'nova') App.novo();
  });

  return { render: render };
})();

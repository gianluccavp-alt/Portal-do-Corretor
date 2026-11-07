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

/* ============================================================
   MATCH DE UNIDADES - tela
   Abertura -> 6 perguntas em linha do tempo -> revelacao -> resultado.
   As regras do fluxo ficam em match-fluxo.js; as de negocio em match.js.
   ============================================================ */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var EMPS = window.SIM_EMPS;
  var M = window.Match, F = window.MatchFluxo;
  var ETAPAS = F.ETAPAS;
  var ROTULOS = { onde: 'Onde', renda: 'Renda bruta', ato: 'Ato', nascimento: 'Nascimento',
    perfil: 'Perfil do cliente', politica: 'Política' };
  var TELAS = ['abertura', 'perguntas', 'revelacao', 'resultado'];
  var CHECK = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.6" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';

  /* filtro: empreendimento visto no resultado ('' = todos); e so visao, nao muda r.empId */
  var estado = { tela: 'abertura', etapa: 0, r: F.respostasIniciais(''), resultado: null,
    filtro: '', aberta: '', marcadas: {} };
  var iniciado = false;   /* depois da carga inicial, toda troca de tela move o foco */

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function hoje() { var d = new Date(); return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }
  function modelo(id) { return $(id).content.cloneNode(true); }
  function cada(lista, fn) { Array.prototype.forEach.call(lista, fn); }
  function nomePolitica(id) { return window.MatchProSoluto.politicaPorId(id).nome; }
  function ctx() { return { emps: EMPS, nomePolitica: nomePolitica, hoje: hoje() }; }

  function cidades() {
    var vistas = [];
    EMPS.forEach(function (e) { if (vistas.indexOf(e.cidade) < 0) vistas.push(e.cidade); });
    return vistas;
  }
  /* reais inteiros (centavos depois da virgula sao ignorados), formatado como 4.200 */
  function moeda(input) {
    var antes = input.value.slice(0, input.selectionStart == null ? input.value.length : input.selectionStart);
    var digAntes = antes.split(',')[0].replace(/\D/g, '').length;
    var n = F.reaisDigitados(input.value);
    var dig = String(n).slice(0, 9);
    n = dig === '0' ? 0 : parseInt(dig, 10);
    var vazio = !/\d/.test(input.value.split(',')[0]);
    var texto = vazio ? '' : n.toLocaleString('pt-BR');
    if (input.value !== texto) {
      input.value = texto;
      if (document.activeElement === input && input.setSelectionRange) {
        var pos = 0, vistos = 0;
        while (pos < texto.length && vistos < digAntes) { if (/\d/.test(texto.charAt(pos))) vistos++; pos++; }
        input.setSelectionRange(pos, pos);
      }
    }
    return { n: n, vazio: vazio };
  }
  function idade(nasc, em) {
    var a = em.getFullYear() - nasc.getFullYear();
    if (em.getMonth() < nasc.getMonth() || (em.getMonth() === nasc.getMonth() && em.getDate() < nasc.getDate())) a--;
    return a;
  }

  /* ---------- navegacao ---------- */
  function irPara(tela, etapa, empilhar) {
    estado.tela = tela;
    if (typeof etapa === 'number') estado.etapa = Math.max(0, Math.min(ETAPAS.length - 1, etapa));
    TELAS.forEach(function (t) { $('mt-' + t).hidden = t !== tela; });
    document.body.classList.toggle('mt-em-fluxo', tela !== 'abertura');
    erro('');
    if (tela === 'abertura') atualizaRepetir();
    if (tela === 'perguntas') {
      var n = estado.etapa;
      $('mt-passo').textContent = 'Passo ' + (n + 1) + ' de ' + ETAPAS.length;
      $('mt-progresso').style.width = Math.round(n / ETAPAS.length * 100) + '%';
      $('mt-progresso').setAttribute('aria-valuenow', String(n));
      $('mt-progresso').setAttribute('aria-valuetext', 'Passo ' + (n + 1) + ' de ' + ETAPAS.length);
      $('mt-continuar').firstChild.nodeValue = ETAPAS[n] === 'politica' ? 'Encontrar unidades' : 'Continuar';
      desenhaTrilha();
      desenhaEtapa();
    }
    if (empilhar) history.pushState({ tela: tela, etapa: estado.etapa }, '');
    if (iniciado) {
      window.scrollTo(0, 0);
      var alvo = tela === 'perguntas' ? $('mt-etapa').querySelector('.mt-etapa-tit')
        : tela === 'revelacao' ? $('mt-rev-titulo') : tela === 'resultado' ? $('mt-res-titulo') : $('mt-comecar');
      if (alvo) alvo.focus({ preventScroll: true });
    }
  }

  /* ---------- repetir a ultima busca ---------- */
  var CHAVES = Object.keys(F.respostasIniciais(''));
  function ultimaBusca() {
    var r;
    try {
      var bruto = sessionStorage.getItem('mt-ultima');
      if (!bruto) return null;
      r = JSON.parse(bruto);
      if (!r || typeof r !== 'object') return null;
      for (var i = 0; i < CHAVES.length; i++) if (!(CHAVES[i] in r)) return null;
      if (cidades().indexOf(r.cidade) < 0) return null;
      for (var k = 0; k < ETAPAS.length - 1; k++) if (F.validarEtapa(ETAPAS[k], r, hoje())) return null;
    } catch (e) { return null; }
    return r;
  }
  function atualizaRepetir() { $('mt-repetir').hidden = !ultimaBusca(); }
  function repetir() {
    var r = ultimaBusca();
    if (!r) { atualizaRepetir(); return; }
    estado.r = r;
    estado.resultado = null; estado.busca = null;
    irPara('perguntas', ETAPAS.length - 1, true);
  }

  function erro(msg) { var el = $('mt-erro'); el.textContent = msg || ''; el.hidden = !msg; }

  /* ---------- trilha ---------- */
  function desenhaTrilha() {
    var base = modelo('tpl-trilha').querySelectorAll('li'), ol = $('mt-trilha'), c = ctx();
    ol.innerHTML = '';
    ETAPAS.concat(['resultado']).forEach(function (e, k) {
      var li;
      if (k < estado.etapa) {
        var val = F.resumoEtapa(e, estado.r, c);
        li = base[0].cloneNode(true);
        li.querySelector('.mt-tl-rot').textContent = ROTULOS[e];
        li.querySelector('.mt-tl-val').textContent = val;
        var btn = li.querySelector('.mt-tl-btn');
        btn.setAttribute('aria-label', 'Editar ' + ROTULOS[e] + ': ' + val);
        btn.addEventListener('click', function () { irPara('perguntas', k, true); });
      } else if (k === estado.etapa) {
        li = base[1].cloneNode(true);
        li.querySelector('.mt-tl-val').textContent = ROTULOS[e];
      } else {
        li = base[2].cloneNode(true);
        li.querySelector('.mt-tl-rot').textContent = e === 'resultado' ? 'Resultado' : ROTULOS[e];
      }
      ol.appendChild(li);
    });
  }

  /* ---------- etapas ---------- */
  function desenhaEtapa() {
    var etapa = ETAPAS[estado.etapa], box = $('mt-etapa');
    box.innerHTML = '';
    box.appendChild(modelo('tpl-' + etapa));
    ({ onde: etapaOnde, renda: etapaRenda, ato: etapaAto, nascimento: etapaNascimento,
       perfil: etapaPerfil, politica: etapaPolitica })[etapa](box);
  }

  function marca(el, ligado, classe) {
    el.classList.toggle(classe, ligado);
    el.setAttribute('aria-pressed', String(ligado));
  }

  function etapaOnde(box) {
    var r = estado.r, pills = box.querySelector('[data-campo=cidade]'), opts = box.querySelector('[data-campo=empId]');
    cidades().forEach(function (cid) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'pill'; b.textContent = cid;
      marca(b, cid === r.cidade, 'pill-on');
      b.addEventListener('click', function () {
        r.cidade = cid; r.empId = '';
        cada(pills.children, function (p) { marca(p, p === b, 'pill-on'); });
        desenhaEmps(opts);
        erro('');
      });
      pills.appendChild(b);
    });
    desenhaEmps(opts);
  }

  function desenhaEmps(opts) {
    var r = estado.r;
    opts.innerHTML = '';
    if (!r.cidade) return;
    var lista = [{ id: '', nome: 'Todos os empreendimentos', sub: 'Busca em ' + r.cidade }]
      .concat(EMPS.filter(function (e) { return e.cidade === r.cidade; }).map(function (e) {
        return { id: e.id, nome: e.nome, sub: e.cidade, foto: F.fotoDe(e) };
      }));
    lista.forEach(function (o) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'opt';
      b.innerHTML = (o.foto ? '<img class="opt-foto" src="' + esc(o.foto) + '" alt="" width="48" height="48">'
          : '<span class="opt-ic"><img class="mt-ic3d" src="assets/img/icones-3d/pino.svg" alt="" width="34" height="34"></span>') +
        '<span class="opt-txt"><span class="opt-nome">' + esc(o.nome) + '</span><span class="opt-sub">' + esc(o.sub) + '</span></span>' +
        '<span class="radio">' + CHECK + '</span>';
      var img = b.querySelector('.opt-foto');
      if (img) img.addEventListener('error', function () {
        var ic = document.createElement('span');
        ic.className = 'opt-ic';
        ic.innerHTML = '<img class="mt-ic3d" src="assets/img/icones-3d/predio.svg" alt="" width="34" height="34">';
        img.parentNode.replaceChild(ic, img);
      });
      marca(b, o.id === r.empId, 'opt-on');
      b.addEventListener('click', function () {
        r.empId = o.id;
        cada(opts.children, function (x) { marca(x, x === b, 'opt-on'); });
      });
      opts.appendChild(b);
    });
  }

  function campoErro(input, ligado) {
    var lab = input.closest('.field');
    if (lab) lab.classList.toggle('field-erro', ligado);
    if (ligado) input.setAttribute('aria-invalid', 'true'); else input.removeAttribute('aria-invalid');
  }

  function etapaRenda(box) {
    var input = box.querySelector('[data-campo=renda]');
    input.value = estado.r.renda ? estado.r.renda.toLocaleString('pt-BR') : '';
    input.addEventListener('input', function () {
      estado.r.renda = moeda(input).n;
      campoErro(input, false); erro('');
    });
  }

  function etapaAto(box) {
    var r = estado.r, padrao = box.querySelector('[data-opcao=padrao]'), outro = box.querySelector('[data-opcao=outro]');
    var campo = box.querySelector('.mt-ato-campo'), input = box.querySelector('[data-campo=ato]');
    var sub = F.textoAtoPadrao(r.empId);
    box.querySelector('.mt-ato-padrao-sub').textContent = sub.charAt(0).toUpperCase() + sub.slice(1);
    function mostra(ehOutro) {
      marca(padrao, !ehOutro, 'opt-on');
      marca(outro, ehOutro, 'opt-on');
      campo.hidden = !ehOutro;
    }
    if (r.ato !== null && r.ato >= 0) input.value = r.ato.toLocaleString('pt-BR');
    mostra(r.ato !== null);
    padrao.addEventListener('click', function () { r.ato = null; mostra(false); campoErro(input, false); erro(''); });
    outro.addEventListener('click', function () {
      r.ato = /\d/.test(input.value) ? M.numero(input.value) : NaN;
      mostra(true);
      input.focus();
    });
    input.addEventListener('input', function () {
      var v = moeda(input);
      r.ato = v.vazio ? NaN : v.n;
      campoErro(input, false); erro('');
    });
  }

  function etapaNascimento(box) {
    var r = estado.r, campos = ['dia', 'mes', 'ano'], tam = { dia: 2, mes: 2, ano: 4 };
    var pill = box.querySelector('.mt-idade');
    function atualizaIdade() {
      var nasc = F.dataNascimento(r.dia, r.mes, r.ano), h = hoje();
      var ok = nasc && nasc.getTime() <= h.getTime();
      pill.hidden = !ok;
      if (ok) pill.querySelector('.mt-idade-txt').textContent = idade(nasc, h) + ' anos';
    }
    campos.forEach(function (c, i) {
      var input = box.querySelector('[data-campo=' + c + ']');
      input.value = r[c];
      /* colar a data inteira (14/03/1993 ou 14031993) preenche os tres campos */
      input.addEventListener('paste', function (ev) {
        var dig = ((ev.clipboardData || window.clipboardData).getData('text') || '').replace(/\D/g, '');
        if (dig.length !== 8) return;
        ev.preventDefault();
        campos.forEach(function (k, j) {
          var el = box.querySelector('[data-campo=' + k + ']');
          el.value = dig.slice([0, 2, 4][j], [2, 4, 8][j]);
          r[k] = el.value;
          campoErro(el, false);
        });
        erro('');
        atualizaIdade();
        box.querySelector('[data-campo=ano]').focus();
      });
      input.addEventListener('input', function () {
        input.value = input.value.replace(/\D/g, '').slice(0, tam[c]);
        r[c] = input.value;
        cada(box.querySelectorAll('.mt-data input'), function (x) { campoErro(x, false); });
        erro('');
        atualizaIdade();
        if (input.value.length === tam[c] && campos[i + 1]) {
          var prox = box.querySelector('[data-campo=' + campos[i + 1] + ']');
          prox.focus(); prox.select();
        }
      });
    });
    atualizaIdade();
  }

  function etapaPerfil(box) {
    var r = estado.r, tiles = box.querySelectorAll('.tile'), aviso = box.querySelector('.mt-aviso-dep');
    function atualiza() {
      var vis = F.perguntasPerfil(r);
      cada(tiles, function (t) {
        var c = t.getAttribute('data-campo'), on = r[c] === true;
        t.hidden = vis.indexOf(c) < 0;
        t.classList.toggle('tile-on', on);
        t.setAttribute('aria-checked', String(on));
      });
      aviso.hidden = !(vis.indexOf('fatorSocial') >= 0 && r.fatorSocial !== true);
    }
    cada(tiles, function (t) {
      t.addEventListener('click', function () {
        var c = t.getAttribute('data-campo');
        r[c] = r[c] !== true;
        atualiza();
      });
    });
    atualiza();
  }

  function etapaPolitica(box) {
    var r = estado.r, pols = box.querySelector('[data-campo=politicaId]');
    M.ORDEM_POLITICAS.forEach(function (id) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'pol';
      b.setAttribute('aria-label', 'Política ' + nomePolitica(id));
      b.innerHTML = '<img src="assets/img/ranking/' + esc(id) + '.png" alt="" width="120" height="120">' +
        '<span class="pol-check" aria-hidden="true">✓</span>';
      marca(b, id === r.politicaId, 'pol-on');
      b.addEventListener('click', function () {
        r.politicaId = id;
        cada(pols.children, function (x) { marca(x, x === b, 'pol-on'); });
      });
      pols.appendChild(b);
    });
  }

  /* campo que recebe o foco quando a etapa nao passa */
  function campoDoErro(etapa) {
    var box = $('mt-etapa');
    if (etapa === 'onde') return box.querySelector('.pill');
    if (etapa === 'renda') return box.querySelector('[data-campo=renda]');
    if (etapa === 'ato') return box.querySelector('[data-campo=ato]');
    if (etapa === 'nascimento') {
      var r = estado.r;
      var vazio = ['dia', 'mes', 'ano'].filter(function (c) { return !r[c]; })[0];
      return box.querySelector('[data-campo=' + (vazio || 'dia') + ']');
    }
    return null;
  }

  function continuar() {
    var etapa = ETAPAS[estado.etapa];
    var msg = F.validarEtapa(etapa, estado.r, hoje());
    if (msg) {
      erro(msg);
      var campo = campoDoErro(etapa);
      if (campo) {
        if (campo.tagName === 'INPUT') {
          if (etapa === 'nascimento') cada($('mt-etapa').querySelectorAll('.mt-data input'), function (x) { campoErro(x, true); });
          else campoErro(campo, true);
        }
        campo.focus();
      }
      return;
    }
    if (etapa === 'politica') { buscar(estado.r.politicaId); return; }
    irPara('perguntas', estado.etapa + 1, true);
  }

  function voltar() {
    if (estado.etapa === 0) irPara('abertura', 0, true);
    else irPara('perguntas', estado.etapa - 1, true);
  }

  /* ---------- estoque ---------- */
  function estoque(cidade) {
    return EMPS.filter(function (e) { return e.cidade === cidade; }).map(function (emp) {
      var u = window.SimUnidades.porEmpreendimento(emp), unidades = [];
      u.blocos.forEach(function (b) {
        (u.unidades[b.id] || []).forEach(function (cod) {
          var d = u.detalhes[cod] || {};
          unidades.push({ codigo: cod, torre: parseInt(b.id.replace(/\D/g, ''), 10), tipoLabel: d.tipoLabel,
            areaPriv: d.areaPriv, avaliacao: d.avaliacao,
            /* spec 4.2: valor associativo SEM premio (sem a Folga Volta ao Caixa);
               unidade promocional ja vem com o Valor Comercial Minimo */
            associativo: d.associativoSemPremio, promocional: !!d.promocional, valorFinal: d.valorFinal });
        });
      });
      return { emp: emp, unidades: unidades };
    });
  }

  /* ---------- busca e revelacao ---------- */
  var SETA = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  var POR_PAGINA = 6;              /* linhas de "Outras" antes do "Ver mais" */
  var SELO_F3 = 'Simulada na Faixa 3: valor travado em R$ 400 mil no PCV';
  var pendente = false;            /* busca esperando a planilha */
  var anim = { seq: 0, raf: 0, timers: [] };

  /* sem arredondamento: reais com centavos (R$ 312.800,00) e % com 2 casas (47,57%) */
  function dinheiro(n) { return F.dinheiro(n); }
  function pctRenda(cr) {
    return ((cr || 0) * 100).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%';
  }
  /* compara o valor exibido (2 casas): 30,00% ainda e verde */
  function acimaDoIdeal(cr) { return Math.round((cr || 0) * 10000) > 3000; }
  /* juros como o motor entrega, so com virgula: 7,66% a.a. */
  function jurosNum(j) { return String(j).replace('.', ','); }
  function juros(j) { return jurosNum(j) + '% a.a.'; }
  function plural(n, um, varios) { return n + ' ' + (n === 1 ? um : varios); }
  function dois(n) { return (n < 10 ? '0' : '') + n; }
  function reduzido() { return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); }
  function empDe(id) { return EMPS.filter(function (e) { return e.id === id; })[0] || null; }
  function recorte(r) { var e = r.empId && empDe(r.empId); return e ? e.nome : r.cidade; }
  function chaveDe(l) { return l.empId + '|' + l.codigo; }
  function apto(l) { return 'Apto ' + (l.andar > 0 ? l.andar + dois(l.final) : dois(l.final)); }
  function andarFinal(l) { return (l.andar > 0 ? l.andar + 'º andar' : 'Térreo') + ' · final ' + dois(l.final); }
  function tipoArea(l) { return [l.tipoLabel, l.areaPriv ? l.areaPriv + '\u00a0m²' : ''].filter(Boolean).join(' · '); }
  /* nome unico da unidade para leitores de tela (o mesmo apto existe em varias torres) */
  function nomeUn(l) { return apto(l) + ', Torre ' + l.torre + (estado.filtro ? '' : ', ' + l.empNome); }
  function editarPerfil() { irPara('perguntas', ETAPAS.indexOf('perfil'), true); }

  function botao(classe, html, fn) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = classe; b.innerHTML = html;
    b.addEventListener('click', fn);
    return b;
  }

  /* um contador por vez: nova busca (ou navegacao) cancela o anterior */
  function cancelaAnimacao() {
    anim.seq++;
    if (anim.raf) cancelAnimationFrame(anim.raf);
    anim.timers.forEach(clearTimeout);
    anim.raf = 0; anim.timers = [];
    $('mt-revelacao').classList.remove('mt-revelado');
  }

  function revEstado(classe) {
    var rev = $('mt-revelacao');
    ['mt-buscando', 'mt-revelado', 'mt-rev-erro'].forEach(function (c) { rev.classList.toggle(c, c === classe); });
  }

  /* resultado que corresponde as respostas atuais (voltar e mudar algo o invalida) */
  function resultadoValido() {
    return !!(estado.resultado && estado.busca && estado.busca.respostas === JSON.stringify(estado.r));
  }

  /* substituir: troca a entrada do historico (nova politica dentro da propria revelacao) */
  function buscar(politicaId, substituir) {
    if (politicaId) estado.r.politicaId = politicaId;
    cancelaAnimacao();
    estado.resultado = null; estado.busca = null;
    mostraBuscando();
    if (substituir) history.replaceState({ tela: 'revelacao', etapa: estado.etapa }, '');
    irPara('revelacao', null, !substituir);
    if (window.SimUnidades.estado() === 'ok') { pendente = false; calcula(); return; }
    pendente = true;
    window.SimUnidades.carregar();   /* depois de um erro tenta de novo; carregando: so espera */
  }

  function mostraBuscando() {
    revEstado('mt-buscando');
    $('mt-rev-titulo').textContent = 'Buscando as unidades…';
    $('mt-rev-sub').textContent = '';
    $('mt-rev-resumo').innerHTML = '';
    $('mt-rev-acao').innerHTML = '';
    $('mt-contagem').textContent = '0';
  }

  function mostraErro(msg) {
    cancelaAnimacao();
    revEstado('mt-rev-erro');
    $('mt-rev-titulo').textContent = 'Não foi possível carregar as unidades';
    $('mt-rev-sub').textContent = msg || window.SimUnidades.erro() || 'Confira a conexão e tente de novo.';
    $('mt-rev-resumo').innerHTML = '';
    var acao = $('mt-rev-acao');
    acao.innerHTML = '';
    acao.appendChild(botao('btn-pri', 'Tentar novamente', function () { buscar(null, true); }));
  }

  function calcula() {
    var r = estado.r, h = hoje(), c = F.cliente(r), res, porEmp;
    try {
      res = M.buscar({ cliente: c, cidade: r.cidade, empId: r.empId, politicaId: r.politicaId, hoje: h, estoque: estoque(r.cidade) });
      porEmp = porEmpreendimento(res, c, h);
    } catch (e) {
      mostraErro('Não foi possível cruzar as unidades com a planilha. Tente de novo.');
      return;
    }
    estado.resultado = res;
    estado.busca = { cliente: c, hoje: h, resumo: M.resumoCliente(c, r.cidade, h), porEmp: porEmp,
      respostas: JSON.stringify(r) };
    estado.filtro = r.empId;
    estado.marcadas = {}; estado.aberta = ''; estado.mostrar = POR_PAGINA;
    try { sessionStorage.setItem('mt-ultima', JSON.stringify(r)); } catch (e) { /* sem sessionStorage */ }
    revela(!reduzido());
  }

  /* a lista de promocionais chega por um fetch separado, depois da planilha: quando ela
     (ou qualquer nova carga) avisa, a busca ja feita e refeita para nunca ficar com valor velho */
  function recalcula() {
    if (!resultadoValido()) return;
    var r = estado.r, b = estado.busca, res, porEmp;
    try {
      res = M.buscar({ cliente: b.cliente, cidade: r.cidade, empId: r.empId, politicaId: r.politicaId, hoje: b.hoje, estoque: estoque(r.cidade) });
      porEmp = porEmpreendimento(res, b.cliente, b.hoje);
    } catch (e) { return; }
    var antes = estado.resultado.total, porChave = {}, marcadas = {};
    Object.keys(porEmp).forEach(function (id) { porEmp[id].linhas.forEach(function (l) { porChave[chaveDe(l)] = l; }); });
    Object.keys(estado.marcadas).forEach(function (k) { if (porChave[k]) marcadas[k] = porChave[k]; });
    if (estado.aberta && !porChave[estado.aberta]) estado.aberta = '';
    estado.resultado = res; b.porEmp = porEmp; estado.marcadas = marcadas;
    if (estado.tela === 'resultado') desenhaResultado();
    else if (estado.tela === 'revelacao' && res.total !== antes) revela(false);
  }

  /* filtro do resultado: a busca de cada empreendimento da cidade, feita uma vez (sem animacao).
     O empreendimento da propria busca reaproveita o resultado da revelacao: os numeros batem. */
  function porEmpreendimento(res, c, h) {
    var r = estado.r, est = estoque(r.cidade), out = {};
    EMPS.filter(function (e) { return e.cidade === r.cidade; }).forEach(function (e) {
      var x = r.empId === e.id ? res
        : M.buscar({ cliente: c, cidade: r.cidade, empId: e.id, politicaId: r.politicaId, hoje: h, estoque: est });
      out[e.id] = { linhas: F.achatar(x), descartadas: x.descartadas };
    });
    return out;
  }
  /* o que o filtro atual mostra: linhas e descartes do empreendimento (ou da cidade toda) */
  function vista() {
    var p = estado.busca.porEmp, ids = estado.filtro ? [estado.filtro] : Object.keys(p);
    var v = { linhas: [], descartadas: { semAvaliacao: 0, foraEnquadramento: 0 } };
    ids.forEach(function (id) {
      if (!p[id]) return;
      v.linhas = v.linhas.concat(p[id].linhas);
      v.descartadas.semAvaliacao += p[id].descartadas.semAvaliacao;
      v.descartadas.foraEnquadramento += p[id].descartadas.foraEnquadramento;
    });
    return v;
  }

  function revela(animar) {
    var res = estado.resultado, s = estado.busca.resumo, r = estado.r, total = res.total;
    var pol = nomePolitica(r.politicaId), rev = $('mt-revelacao');
    cancelaAnimacao();
    revEstado(null);
    $('mt-rev-titulo').textContent = total
      ? 'O cliente cabe em ' + plural(total, 'unidade', 'unidades')
      : 'Nenhuma unidade cabe na política ' + pol;
    $('mt-rev-sub').textContent = recorte(r) + ' · Política ' + pol;
    $('mt-rev-resumo').innerHTML = [['Enquadramento', s.faixa || '-'],
      s.subsidio > 0 ? ['Subsídio estimado', dinheiro(s.subsidio), 'mt-verde'] : ['Subsídio estimado', 'Sem subsídio'],
      ['Financiamento até', dinheiro(s.financiamentoMax)]].map(function (x) {
      return '<div class="rev-linha"><span>' + esc(x[0]) + '</span><b' + (x[2] ? ' class="' + x[2] + '"' : '') + '>' +
        esc(x[1]) + '</b></div>';
    }).join('');

    var acao = $('mt-rev-acao');
    acao.innerHTML = '';
    if (total) {
      acao.appendChild(botao('btn-pri sheen', esc(total === 1 ? 'Ver a unidade' : 'Ver as ' + total + ' unidades') + SETA,
        function () { desenhaResultado(); irPara('resultado', null, true); }));
    } else if (res.sugestao) {
      var sug = res.sugestao;
      acao.appendChild(botao('btn-pri', esc('Ver na política ' + sug.nome + ' (' + sug.qtd + ')'),
        function () { buscar(sug.politicaId, true); }));
      acao.appendChild(botao('btn-sec', 'Editar perfil', editarPerfil));
    } else {
      var nota = document.createElement('p');
      nota.className = 'mt-nota';
      nota.textContent = 'Nenhuma política aprova as unidades desse recorte.';
      acao.appendChild(nota);
      acao.appendChild(botao('btn-pri', 'Editar perfil', editarPerfil));
    }

    if (animar) {
      void rev.offsetWidth;          /* reinicia as animacoes de CSS */
      rev.classList.add('mt-revelado');
      conta(total);
    } else {
      $('mt-contagem').textContent = String(total);
    }
  }

  /* anel em 1,7s (CSS); o numero entra aos 1,85s e conta ate o total */
  function conta(total) {
    var el = $('mt-contagem'), seq = anim.seq;
    el.textContent = '0';
    if (!total) return;
    anim.timers.push(setTimeout(function () {
      var ini = null;
      function passo(t) {
        if (seq !== anim.seq) return;
        if (ini === null) ini = t;
        var p = Math.min(1, (t - ini) / 1300);
        el.textContent = String(Math.round((1 - Math.pow(1 - p, 3)) * total));
        anim.raf = p < 1 ? requestAnimationFrame(passo) : 0;
      }
      if (seq === anim.seq) anim.raf = requestAnimationFrame(passo);
    }, 1900));
  }

  /* ---------- detalhes da simulacao CAIXA (revelacao e resultado, mesmo sem unidades) ---------- */
  function bonito(nome) {
    return String(nome).toLowerCase().replace(/(^|\s)\S/g, function (c) { return c.toUpperCase(); });
  }
  function pct(f) { return String(Math.round(f * 1000) / 10).replace('.', ',') + '%'; }
  function abrirDetalhes(origem) {
    var s = estado.busca.resumo, c = estado.busca.cliente, r = estado.r, hoje = estado.busca.hoje;
    var dlg = $('mt-dlg-det');
    function grupo(tit, linhas, nota) {
      return '<div class="det-grupo"><h3 class="det-tit">' + esc(tit) + '</h3><div class="det-lista">' + linhas.map(function (x) {
        return '<div class="det-lin"><span>' + esc(x[0]) + '</span><b' + (x[2] ? ' class="' + x[2] + '"' : '') + '>' + esc(x[1]) + '</b></div>';
      }).join('') + '</div>' + (nota ? '<p class="det-nota">' + esc(nota) + '</p>' : '') + '</div>';
    }
    function sn(v) { return v ? 'Sim' : 'Não'; }
    var cli = [['Renda bruta', dinheiro(r.renda) + '/mês'],
      ['Idade', c.nascimento ? idade(c.nascimento, hoje) + ' anos' : '-'],
      ['3 anos de FGTS', sn(c.fgts !== false)], ['Possui imóvel na cidade', sn(c.possuiImovel === true)]];
    if (M.temSubsidio(r.renda, c.possuiImovel)) {
      cli.push(['Mais de um comprador ou dependente', sn(c.fatorSocial === true)]);
      cli.push(['Já recebeu subsídio', sn(c.subsidioAnterior === true)]);
    }
    var enq = [['Enquadramento', s.faixa || '-'], ['Juros nominal', juros(s.jurosNominal)],
      ['Juros efetivo', jurosNum(s.jurosEfetivo) + '% a.a.'],
      ['Prazo', s.prazo + ' meses (' + Math.round(s.prazo / 12 * 10) / 10 + ' anos)'],
      ['Sistema', s.sistema === 'SAC' ? 'SAC (parcelas decrescentes)' : 'Price (parcelas fixas)'],
      ['Taxa de administração', s.taxaAdm > 0 ? dinheiro(s.taxaAdm) + '/mês' : 'Sem taxa']];
    var res = [['Financiamento até', dinheiro(s.financiamentoMax)],
      s.subsidio > 0 ? ['Subsídio estimado', dinheiro(s.subsidio), 'mt-verde'] : ['Subsídio estimado', 'Sem subsídio'],
      ['Parcela máxima (' + pct(s.comprometimento) + ' da renda)', dinheiro(s.parcelaMax)],
      ['Financia até ' + pct(s.cota) + ' do imóvel', 'Valor de referência ' + dinheiro(s.valorReferencia)]];
    var seg = s.seguradoras.map(function (x) {
      return [bonito(x.nome), dinheiro(x.primeira) + (x.ultima !== x.primeira ? ' → ' + dinheiro(x.ultima) : '')];
    });
    $('mt-det-corpo').innerHTML = grupo('Cliente', cli) + grupo('Enquadramento CAIXA', enq) +
      grupo('Resultado', res, 'Calculado para um imóvel de ' + dinheiro(s.valorReferencia) + ', o teto da faixa. Cada unidade é recalculada com o próprio valor de avaliação.') +
      grupo('Parcela por seguradora (1ª → última)', seg, 'Já com taxa de administração e seguros, no financiamento máximo.');
    $('mt-det-corpo').scrollTop = 0;
    dlg._origem = origem || null;
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    $('mt-det-fechar').focus();
  }

  /* ---------- resultado ---------- */
  function desenhaResultado() {
    var b = estado.busca, s = b.resumo, r = estado.r, v = vista();
    $('mt-res-titulo').textContent = F.textoContagem(v.linhas.length);
    $('mt-res-sub').textContent = recorte({ cidade: r.cidade, empId: estado.filtro }) + ' · ' + nomePolitica(r.politicaId) +
      ' · ' + dinheiro(r.renda) + '/mês';
    $('mt-chips').innerHTML = [['Enquadramento', s.faixa || '-'], (s.subsidio > 0 ? ['Subsídio', dinheiro(s.subsidio), 'mt-verde'] : ['Subsídio', 'Sem subsídio']),
      ['Financ. até', dinheiro(s.financiamentoMax)], ['Juros CAIXA', juros(s.jurosNominal)],
      ['Prazo', s.prazo + ' meses']].map(function (c) {
      return '<div class="chip"><span class="chip-rot">' + esc(c[0]) + '</span><b class="chip-val' + (c[2] ? ' ' + c[2] : '') + '">' +
        esc(c[1]) + '</b></div>';
    }).join('');
    $('mt-chips').insertAdjacentHTML('beforeend', '<button type="button" class="chip chip-det" id="mt-chip-det" ' +
      'aria-haspopup="dialog"><span class="chip-rot">Simulação CAIXA</span><b class="chip-val">Detalhes →</b></button>');
    $('mt-chip-det').addEventListener('click', function () { abrirDetalhes(this); });
    var vazio = $('mt-vazio');
    vazio.hidden = v.linhas.length > 0;
    vazio.textContent = 'Nenhuma unidade deste empreendimento cabe na política ' + nomePolitica(r.politicaId) + '.';
    desenhaFiltro();
    desenhaDestaque(F.melhorMatch(v.linhas));
    desenhaOutras();
    desenhaLateral();
  }

  function preenche(box, valores) {
    cada(box.querySelectorAll('[data-v]'), function (el) {
      var v = valores[el.getAttribute('data-v')];
      if (v != null) el.textContent = v;
    });
  }

  /* pill curto do design ("Cai na Faixa 3"); o texto longo fica no title e em "Como chegamos aqui" */
  function selos(l) {
    if (l.travaF3) return [['Cai na Faixa 3', SELO_F3]];
    var sf = M.seloFaixa(l, estado.busca.resumo.faixa);
    return sf ? [['Cai na ' + l.faixa, sf]] : [];
  }
  function poeSelos(box, l) {
    var lista = selos(l).map(function (t) { return ['selo', t[0], t[1]]; });
    if (l.promocional) lista.unshift(['selo selo-promo', 'Promocional']);
    lista.forEach(function (x) {
      var s = document.createElement('span');
      s.className = x[0]; s.textContent = x[1];
      if (x[2]) s.title = x[2];
      box.appendChild(s);
    });
  }

  function linkAssoc(a, l, rotulo) {
    var b = estado.busca;
    a.href = M.urlAssociativo(l, b.cliente, b.hoje);
    a.setAttribute('aria-label', rotulo + ' (abre em nova aba)');
  }

  function desenhaDestaque(l) {
    var art = $('mt-destaque');
    art.innerHTML = '';
    art.hidden = !l;
    if (!l) return;
    art.appendChild(modelo('tpl-destaque'));
    var emp = empDe(l.empId), img = art.querySelector('.dest-foto img');
    img.addEventListener('error', function () {
      img.classList.add('dest-foto-ic');
      img.src = 'assets/img/icones-3d/predio.svg';
    }, { once: true });
    if (emp) img.src = F.fotoDe(emp);
    else { img.classList.add('dest-foto-ic'); img.src = 'assets/img/icones-3d/predio.svg'; }
    art.querySelector('.dest-sobre').textContent = l.empNome + ' · Torre ' + l.torre;
    art.querySelector('.dest-cod').textContent = apto(l);
    art.querySelector('.dest-tipo').textContent = tipoArea(l);
    art.querySelector('.dest-andar').textContent = andarFinal(l);
    poeSelos(art.querySelector('.dest-selos'), l);
    art.querySelector('.dest-mensal-val').textContent = dinheiro(F.mensal(l));
    var acima = acimaDoIdeal(l.crTotal), cr = art.querySelector('.dest-cr-val'), fill = art.querySelector('.barra-cr-fill');
    cr.textContent = pctRenda(l.crTotal);
    cr.classList.toggle('mt-ambar', acima);
    fill.style.width = Math.min(100, Math.max(0, l.crTotal * 100)) + '%';
    fill.classList.toggle('mt-ambar', acima);
    preenche(art, { valor: dinheiro(l.venda), fin: dinheiro(l.financiamento), subsidio: dinheiro(l.subsidio),
      ato: dinheiro(l.ato), ps: F.textoPS(l), parcela: dinheiro(l.parcelaFin) });
    linkAssoc(art.querySelector('.dest-assoc'), l, 'Abrir ' + nomeUn(l) + ' no associativo');
    ligaPdf(art.querySelector('.btn-pdf'), l);
  }

  /* filtro por empreendimento: "Todos" + cada empreendimento da cidade, com foto e quantas unidades cabem */
  function desenhaFiltro() {
    var box = $('mt-filtro'), p = estado.busca.porEmp, r = estado.r;
    var todos = Object.keys(p).reduce(function (t, id) { return t + p[id].linhas.length; }, 0);
    var lista = [{ id: '', nome: 'Todos', qtd: todos }].concat(EMPS.filter(function (e) {
      return e.cidade === r.cidade && p[e.id];
    }).map(function (e) { return { id: e.id, nome: e.nome, qtd: p[e.id].linhas.length, foto: F.fotoDe(e) }; }));
    var rolagem = box.scrollLeft;   /* refazer os chips zera a rolagem horizontal da fileira (celular) */
    box.innerHTML = '';
    lista.forEach(function (o) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'fil' + (o.qtd ? '' : ' fil-zero');
      b.title = o.nome;
      b.setAttribute('aria-label', o.nome + ', ' + plural(o.qtd, 'unidade', 'unidades'));
      b.innerHTML = (o.foto ? '<img class="opt-foto" src="' + esc(o.foto) + '" alt="" width="48" height="48">'
          : '<span class="opt-ic"><img class="mt-ic3d" src="assets/img/icones-3d/pino.svg" alt="" width="34" height="34"></span>') +
        '<span class="fil-txt"><span class="fil-nome">' + esc(o.nome) + '</span><span class="fil-qtd">' +
        esc(plural(o.qtd, 'unidade', 'unidades')) + '</span></span>';
      var img = b.querySelector('.opt-foto');
      if (img) img.addEventListener('error', function () {
        var ic = document.createElement('span');
        ic.className = 'opt-ic';
        ic.innerHTML = '<img class="mt-ic3d" src="assets/img/icones-3d/predio.svg" alt="" width="34" height="34">';
        img.parentNode.replaceChild(ic, img);
      });
      marca(b, o.id === estado.filtro, 'fil-on');
      b.addEventListener('click', function () {
        if (estado.filtro === o.id) return;
        estado.filtro = o.id; estado.aberta = ''; estado.mostrar = POR_PAGINA;
        /* o filtro fica abaixo do melhor match: se o cartao some ou muda de altura, a pagina
           acompanha para o filtro nao sair debaixo do dedo */
        var antes = box.getBoundingClientRect().top;
        desenhaResultado();
        window.scrollBy(0, box.getBoundingClientRect().top - antes);
        var novo = $('mt-filtro').children[lista.indexOf(o)];
        if (novo) novo.focus({ preventScroll: true });
      });
      box.appendChild(b);
    });
    /* devolve a rolagem e garante o chip escolhido visivel, sem mexer na rolagem vertical */
    box.scrollLeft = rolagem;
    var on = box.querySelector('.fil-on');
    if (on && box.scrollWidth > box.clientWidth) {
      var pad = 20, esq = on.offsetLeft - box.offsetLeft, dir = esq + on.offsetWidth;
      if (esq - pad < box.scrollLeft) box.scrollLeft = esq - pad;
      else if (dir + pad > box.scrollLeft + box.clientWidth) box.scrollLeft = dir + pad - box.clientWidth;
    }
  }

  /* ordem fixa: menor parcela */
  function outrasOrdenadas() {
    var linhas = vista().linhas, melhor = F.melhorMatch(linhas);
    return F.ordenar(linhas.filter(function (l) { return l !== melhor; }), 'parcela');
  }

  function desenhaOutras() {
    var outras = outrasOrdenadas(), n = outras.length, box = $('mt-outras'), tela = $('mt-resultado');
    var vis = outras.slice(0, estado.mostrar);
    $('mt-outras-tit').textContent = n === 1 ? 'Outra unidade' : 'Outras ' + n + ' unidades';
    tela.querySelector('.mt-outras-cab').hidden = !n;
    tela.querySelector('.mt-tabela').hidden = !n;
    box.innerHTML = '';
    vis.forEach(function (l) { box.appendChild(linha(l)); });
    var resto = n - vis.length, mais = $('mt-mais');
    mais.hidden = resto <= 0;
    mais.textContent = 'Ver mais ' + plural(resto, 'unidade', 'unidades');
    sincronizaPdf();
  }

  function linha(l) {
    var row = modelo('tpl-linha').querySelector('.row'), k = chaveDe(l), todos = !estado.filtro;
    var acima = acimaDoIdeal(l.crTotal), sub = andarFinal(l) + (tipoArea(l) ? ' · ' + tipoArea(l) : '');
    row.setAttribute('data-chave', k);
    cada(row.querySelectorAll('.row-cod'), function (el) {
      el.textContent = apto(l) + ' ';
      var sm = document.createElement('small');
      sm.textContent = '· ' + (todos ? l.empNome + ' · ' : '') + 'Torre ' + l.torre;
      el.appendChild(sm);
    });
    cada(row.querySelectorAll('.row-sub'), function (el) { el.textContent = sub; poeSelos(el.parentNode, l); });
    cada(row.querySelectorAll('.row-mes-val'), function (el) { el.textContent = dinheiro(F.mensal(l)); });
    cada(row.querySelectorAll('.row-cr'), function (el) {
      el.textContent = pctRenda(l.crTotal) + (el.closest('.row-dk') ? ' da renda' : '');
      el.classList.toggle('mt-ambar', acima);
    });
    preenche(row, { valor: dinheiro(l.venda), fin: dinheiro(l.financiamento), subsidio: dinheiro(l.subsidio), ps: F.textoPS(l) });
    linkAssoc(row.querySelector('.row-assoc'), l, 'Abrir ' + nomeUn(l) + ' no associativo');
    linkAssoc(row.querySelector('.go'), l, 'Abrir ' + nomeUn(l) + ' no associativo');
    ligaPdf(row.querySelector('.row-det .btn-pdf'), l);
    ligaPdf(row.querySelector('.cb'), l);

    var abrir = row.querySelector('.row-abrir'), det = row.querySelector('.row-det');
    det.id = 'mt-det-' + k.replace(/[^A-Za-z0-9_-]/g, '-');
    abrir.setAttribute('aria-controls', det.id);
    abrir.setAttribute('aria-expanded', String(estado.aberta === k));
    det.hidden = estado.aberta !== k;
    abrir.addEventListener('click', function () {
      estado.aberta = estado.aberta === k ? '' : k;
      cada($('mt-outras').querySelectorAll('.row'), function (x) {
        var on = x.getAttribute('data-chave') === estado.aberta;
        x.querySelector('.row-abrir').setAttribute('aria-expanded', String(on));
        x.querySelector('.row-det').hidden = !on;
      });
    });
    return row;
  }

  /* "Como chegamos aqui": a simulacao em frases curtas, com os numeros desta busca.
     Sem jargao: nada de folga, VCM, C.R. ou avaliacao bancaria. */
  function frasesSimulacao() {
    var b = estado.busca, s = b.resumo, r = estado.r, v = vista(), d = v.descartadas, fora = [];
    var pol = window.MatchProSoluto.politicaPorId(r.politicaId);
    var anos = b.cliente.nascimento ? idade(b.cliente.nascimento, b.hoje) : null;
    var itens = ['Com renda de ' + dinheiro(r.renda) + (anos !== null ? ' e ' + anos + ' anos' : '') +
      ', a CAIXA financia até ' + dinheiro(s.financiamentoMax) + ' em ' + s.prazo + ' meses, com juros de ' +
      jurosNum(s.jurosNominal) + '% ao ano' + (s.faixa ? ' (' + s.faixa + ')' : '') + '.'];
    itens.push(s.subsidio > 0 ? 'Subsídio estimado de ' + dinheiro(s.subsidio) + '.'
      : r.possuiImovel ? 'Sem subsídio: o cliente já tem imóvel na cidade.' : 'Sem subsídio para esta renda.');
    itens.push('O valor de cada unidade é o associativo da tabela de hoje. Unidades promocionais já entram com o preço promocional.');
    var ato = r.ato !== null ? 'ato de ' + dinheiro(r.ato)
      : estado.filtro ? 'ato padrão de ' + dinheiro(M.atoDe(estado.filtro)) : 'ato padrão de cada empreendimento';
    itens.push('Somamos financiamento, subsídio e ' + ato + '. O que falta vira Pro Soluto, pago em até ' + pol.prazo + ' parcelas.');
    itens.push('Só aparecem unidades em que o Pro Soluto e a parcela total cabem nos limites da política ' + pol.nome + '.');
    if (d.foraEnquadramento) fora.push(d.foraEnquadramento + ' fora do enquadramento da renda');
    if (d.semAvaliacao) fora.push(d.semAvaliacao + ' sem valor de avaliação');
    if (fora.length) itens.push('Ficaram de fora: ' + fora.join(' · ') + '.');
    /* selos curtos da lista, explicados em linguagem simples */
    if (v.linhas.some(function (l) { return l.travaF3; }))
      itens.push('Unidades marcadas com "Cai na Faixa 3" foram simuladas com o valor limitado a R$ 400 mil no financiamento da CAIXA.');
    var outras = {};
    v.linhas.forEach(function (l) { if (M.seloFaixa(l, s.faixa)) outras[l.faixa] = l.jurosNominal; });
    Object.keys(outras).forEach(function (f) {
      itens.push('Unidades marcadas com "Cai na ' + f + '" ficam na ' + f + ' da CAIXA pelo valor do imóvel, com juros de ' +
        jurosNum(outras[f]) + '% ao ano.');
    });
    return itens;
  }

  function desenhaLateral() {
    var box = $('mt-lateral'), res = estado.resultado;
    box.innerHTML = '';
    box.appendChild(modelo('tpl-lateral'));
    box.querySelector('.lado-card').open = !!(window.matchMedia && window.matchMedia('(min-width:1024px)').matches);
    box.querySelector('.lado-lista').innerHTML = frasesSimulacao().map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('');
    var mais = box.querySelector('.lado-mais'), sug = estado.filtro === estado.r.empId ? res.sugestao : null;
    mais.hidden = !sug;
    if (!sug) return;
    mais.querySelector('.lado-mais-tit').textContent = 'Na política ' + sug.nome + ', cabem ' + plural(sug.qtd, 'unidade', 'unidades');
    var btn = mais.querySelector('.lado-mais-btn');
    btn.textContent = 'Ver na ' + sug.nome + ' →';
    btn.setAttribute('aria-label', 'Ver na política ' + sug.nome);
    btn.addEventListener('click', function () { buscar(sug.politicaId); });
  }

  /* ---------- marcadas para o PDF (chave empId|codigo) ---------- */
  function ligaPdf(el, l) {
    var k = chaveDe(l);
    el.setAttribute('data-pdf', k);
    el.setAttribute('aria-label', 'Incluir ' + nomeUn(l) + ' no PDF');
    el.addEventListener('click', function () {
      if (estado.marcadas[k]) delete estado.marcadas[k];
      else estado.marcadas[k] = l;
      sincronizaPdf();
    });
  }

  /* os dois controles de cada linha (cartao do celular e tabela) e o do destaque andam juntos */
  function sincronizaPdf() {
    cada($('mt-resultado').querySelectorAll('[data-pdf]'), function (el) {
      var on = !!estado.marcadas[el.getAttribute('data-pdf')];
      el.setAttribute(el.getAttribute('role') === 'checkbox' ? 'aria-checked' : 'aria-pressed', String(on));
    });
    var n = Object.keys(estado.marcadas).length;
    $('mt-pdf-qtd').textContent = plural(n, 'unidade', 'unidades');
    $('mt-pdf').disabled = n === 0;
  }

  /* ---------- PDF (spec secao 7) ---------- */
  var AVISO_PDF = 'A biblioteca de PDF ainda está carregando. Tente de novo em alguns segundos.';
  var AVISO_ESTIMATIVA = 'Valores estimados. Sujeitos à análise de crédito da CAIXA e à aprovação da Direcional.';
  var RODAPE_PDF = 'Simulação aproximada, sujeita à análise de crédito da CAIXA e à aprovação da Direcional.';
  var CHAVE_CORRETOR = 'mt-corretor';

  /* logo do PDF: mesma carga via canvas do simulador associativo */
  var logoPdf = null;
  (function () {
    var img = new Image();
    img.onload = function () {
      var cv = document.createElement('canvas');
      cv.width = img.naturalWidth; cv.height = img.naturalHeight;
      cv.getContext('2d').drawImage(img, 0, 0);
      try { logoPdf = { data: cv.toDataURL('image/jpeg', 0.92), w: img.naturalWidth, h: img.naturalHeight }; }
      catch (e) { logoPdf = null; }
    };
    img.src = 'assets/img/logo-direcional.jpg';
  })();

  function pdfPronto() {
    return !!(window.jspdf && window.jspdf.jsPDF && window.jspdf.jsPDF.API && typeof window.jspdf.jsPDF.API.autoTable === 'function');
  }
  function slug(t) {
    return String(t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  }
  function lerCorretor() { try { return localStorage.getItem(CHAVE_CORRETOR) || ''; } catch (e) { return ''; } }
  function gravarCorretor(v) {
    try { if (v) localStorage.setItem(CHAVE_CORRETOR, v); else localStorage.removeItem(CHAVE_CORRETOR); } catch (e) { /* sem localStorage */ }
  }

  /* abre o popup; sem <dialog> (navegador antigo) gera direto, sem nomes */
  function abrirPdf() {
    if (!pdfPronto()) { alert(AVISO_PDF); return; }
    var dlg = $('mt-dlg-pdf');
    if (typeof dlg.showModal !== 'function') { montaPdf('', ''); return; }
    $('mt-dlg-cliente').value = '';
    $('mt-dlg-corretor').value = lerCorretor();
    dlg.showModal();
    $('mt-dlg-cliente').focus();
  }

  function montaPdf(cliente, corretor) {
    if (!pdfPronto()) { alert(AVISO_PDF); return; }
    var doc = new window.jspdf.jsPDF({ unit: 'mm', format: 'a4' });
    var b = estado.busca, s = b.resumo, r = estado.r;
    var W = doc.internal.pageSize.getWidth(), Mg = 14, y = 12;
    var CINZA = [114, 122, 125], TINTA = [58, 64, 67];

    if (logoPdf) {
      var lw = 38, lh = lw * logoPdf.h / logoPdf.w;
      doc.addImage(logoPdf.data, 'JPEG', (W - lw) / 2, y, lw, lh);
      y += lh + 6;
    } else { y += 4; }
    doc.setFont('helvetica', 'bold'); doc.setFontSize(14); doc.setTextColor(TINTA[0], TINTA[1], TINTA[2]);
    doc.text('Unidades sugeridas', W / 2, y, { align: 'center' }); y += 5;
    doc.setFont('helvetica', 'normal'); doc.setFontSize(10); doc.setTextColor(CINZA[0], CINZA[1], CINZA[2]);
    /* cabecalho: o empreendimento das unidades marcadas (podem vir de filtros diferentes) */
    var empsPdf = Object.keys(estado.marcadas).map(function (k) { return estado.marcadas[k].empId; })
      .filter(function (id, i, a) { return a.indexOf(id) === i; });
    var emp = empsPdf.length === 1 && empDe(empsPdf[0]);
    doc.text(emp ? emp.nome + '  ·  ' + emp.cidade : r.cidade + '  ·  todos os empreendimentos', W / 2, y, { align: 'center' });
    y += 7;

    var anos = b.cliente.nascimento ? idade(b.cliente.nascimento, b.hoje) : null;
    function rotulo(largura) { return { cellWidth: largura, fontStyle: 'bold', textColor: CINZA }; }
    doc.autoTable({
      startY: y, theme: 'plain', margin: { left: Mg, right: Mg },
      body: [['Cliente', cliente || '-', 'Corretor', corretor || '-'],
             ['Renda informada', r.renda > 0 ? dinheiro(r.renda) : '-', 'Idade', anos !== null ? anos + ' anos' : '-']],
      styles: { fontSize: 8.5, cellPadding: 1.4, textColor: TINTA },
      columnStyles: { 0: rotulo(34), 1: { cellWidth: 54 },
                      2: rotulo(40), 3: { cellWidth: 'auto' } }
    });
    y = doc.lastAutoTable.finalY + 5;

    doc.setFont('helvetica', 'bold'); doc.setFontSize(9); doc.setTextColor(TINTA[0], TINTA[1], TINTA[2]);
    doc.text('Condições CAIXA', Mg, y); y += 1.5;
    doc.autoTable({
      startY: y, theme: 'plain', margin: { left: Mg, right: Mg },
      body: [['Enquadramento', s.faixa || '-', 'Taxa de juros', juros(s.jurosNominal)],
             ['Prazo', s.prazo + ' meses', 'Financiamento até', dinheiro(s.financiamentoMax)]],
      styles: { fontSize: 8.5, cellPadding: 1.4, textColor: TINTA },
      columnStyles: { 0: rotulo(34), 1: { cellWidth: 54 },
                      2: rotulo(40), 3: { cellWidth: 'auto' } }
    });
    y = doc.lastAutoTable.finalY + 2.5;
    doc.setFont('helvetica', 'normal'); doc.setFontSize(6.8); doc.setTextColor(138, 146, 149);
    doc.text(AVISO_ESTIMATIVA, Mg + 1.4, y); y += 5;

    var linhas = Object.keys(estado.marcadas).map(function (k) { return M.linhaPdf(estado.marcadas[k]); });
    /* A4 retrato: 182 mm uteis (helvetica 7pt: "R$ 999.999,99" = 16,1 mm + 2,8 de margem interna). Unidade abreviada (30 mm); a coluna Subsidio so entra
       quando alguma unidade do PDF tem subsidio. Larguras fixas: nenhum valor quebra linha. */
    var comSub = linhas.some(function (l) { return l.subsidio > 0; });
    var COLS = [
      ['Unidade', 30, null],
      ['Valor do imóvel', 19.5, function (l) { return dinheiro(l.valorImovel); }],
      ['Desconto', 18, function (l) { return l.desconto > 0 ? dinheiro(l.desconto) : '-'; }],
      ['Valor com desconto', 19.5, function (l) { return dinheiro(l.venda); }],
      ['Financiamento', 19.5, function (l) { return dinheiro(l.financiamento); }],
      ['Subsídio', 18, function (l) { return l.subsidio > 0 ? dinheiro(l.subsidio) : '-'; }],
      ['Ato', 17.5, function (l) { return dinheiro(l.ato); }],
      ['Pro Soluto', 22, function (l) { return F.textoPS(l) + (l.parcelaPS > 0 && l.carne === 'escalonado' ? '\n(escalonado)' : ''); }],
      ['Parcela CAIXA', 18, function (l) { return dinheiro(l.parcelaFin); }]
    ].filter(function (c) { return comSub || c[0] !== 'Subsídio'; });
    /* sem a coluna de subsidio, a sobra (18 mm) e repartida entre as colunas de valor */
    var sobra = W - 2 * Mg - COLS.reduce(function (t, c) { return t + c[1]; }, 0), nVal = COLS.length - 1;
    var colStyles = {};
    COLS.forEach(function (c, i) {
      colStyles[i] = i === 0 ? { cellWidth: c[1] }
        : { cellWidth: c[1] + sobra / nVal, halign: 'right', overflow: 'visible' };
    });
    var FONTE = 7, PAD = 1.4;
    /* celula da unidade: ate 3 linhas curtas (nome em negrito, codigo · area, selo) desenhadas a mao */
    function unidadeLinhas(l) {
      doc.setFont('helvetica', 'bold'); doc.setFontSize(FONTE);
      var nome = doc.splitTextToSize(l.empNome || '', COLS[0][1] - 2 * PAD);
      var cod = l.codigo + (l.areaPriv ? ' · ' + l.areaPriv + ' m²' : '');
      return { nome: nome, cod: cod, promo: l.promocional };
    }
    var celUn = linhas.map(unidadeLinhas);
    doc.autoTable({
      startY: y, margin: { left: Mg, right: Mg, bottom: 22 }, theme: 'grid',
      head: [COLS.map(function (c) { return c[0]; })],
      body: linhas.map(function (l, i) {
        var u = celUn[i];
        /* texto so para medir a altura; o desenho real vem em didDrawCell */
        return [u.nome.concat([u.cod]).concat(u.promo ? ['Condição especial'] : []).join('\n')]
          .concat(COLS.slice(1).map(function (c) { return c[2](l); }));
      }),
      styles: { font: 'helvetica', fontSize: FONTE, cellPadding: PAD, textColor: TINTA, lineColor: [231, 233, 234], valign: 'middle' },
      headStyles: { fillColor: [228, 3, 43], textColor: 255, fontStyle: 'bold', fontSize: 6.8, halign: 'center' },
      alternateRowStyles: { fillColor: [250, 251, 251] },
      columnStyles: colStyles,
      willDrawCell: function (d) {
        if (d.section === 'body' && d.column.index === 0) d.cell.text = [];
      },
      didDrawCell: function (d) {
        if (d.section !== 'body' || d.column.index !== 0 || !celUn[d.row.index]) return;
        var u = celUn[d.row.index], x = d.cell.x + PAD, alt = FONTE * 0.3528 * 1.15;
        var linhasCel = u.nome.length + 1 + (u.promo ? 1 : 0);
        var yy = d.cell.y + (d.cell.height - linhasCel * alt) / 2 + alt * 0.8;
        doc.setFontSize(FONTE); doc.setTextColor(TINTA[0], TINTA[1], TINTA[2]);
        doc.setFont('helvetica', 'bold');
        u.nome.forEach(function (t) { doc.text(t, x, yy); yy += alt; });
        doc.setFont('helvetica', 'normal'); doc.setTextColor(CINZA[0], CINZA[1], CINZA[2]);
        doc.text(u.cod, x, yy); yy += alt;
        if (u.promo) {
          doc.setFont('helvetica', 'bold'); doc.setFontSize(6.5); doc.setTextColor(181, 114, 0);
          doc.text('Condição especial', x, yy);
        }
      }
    });

    var total = doc.internal.getNumberOfPages(), gerado = hoje().toLocaleDateString('pt-BR');
    for (var p = 1; p <= total; p++) {
      doc.setPage(p);
      var H = doc.internal.pageSize.getHeight();
      doc.setDrawColor(231, 233, 234); doc.setLineWidth(0.2); doc.line(Mg, H - 14, W - Mg, H - 14);
      doc.setFont('helvetica', 'normal'); doc.setFontSize(6.5); doc.setTextColor(CINZA[0], CINZA[1], CINZA[2]);
      doc.text(RODAPE_PDF, Mg, H - 10);
      doc.text('Gerado em ' + gerado + '  ·  Página ' + p + ' de ' + total, Mg, H - 6.5);
    }
    doc.save('unidades-' + (slug(cliente) || 'cliente') + '.pdf');
  }

  /* ---------- eventos ---------- */
  $('mt-comecar').addEventListener('click', function () {
    estado.r = F.respostasIniciais('');
    estado.resultado = null; estado.busca = null; estado.marcadas = {};
    irPara('perguntas', 0, true);
  });
  $('mt-repetir').addEventListener('click', repetir);
  $('mt-continuar').addEventListener('click', continuar);
  $('mt-voltar').addEventListener('click', voltar);
  $('mt-sair').addEventListener('click', function () { irPara('abertura', null, true); });
  $('mt-rev-voltar').addEventListener('click', function () { irPara('perguntas', ETAPAS.length - 1, true); });
  $('mt-editar').addEventListener('click', editarPerfil);
  $('mt-res-voltar').addEventListener('click', editarPerfil);
  $('mt-pdf').addEventListener('click', abrirPdf);
  $('mt-rev-detalhes').addEventListener('click', function () { abrirDetalhes(this); });
  $('mt-det-fechar').addEventListener('click', function () { $('mt-dlg-det').close(); });
  $('mt-dlg-det').addEventListener('close', function () { if (this._origem && this._origem.focus) this._origem.focus(); });
  /* clique no fundo escuro fecha */
  $('mt-dlg-det').addEventListener('click', function (ev) { if (ev.target === this) this.close(); });
  $('mt-dlg-form').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var cliente = $('mt-dlg-cliente').value.trim(), corretor = $('mt-dlg-corretor').value.trim();
    gravarCorretor(corretor);
    $('mt-dlg-pdf').close();
    montaPdf(cliente, corretor);
  });
  $('mt-dlg-cancelar').addEventListener('click', function () { $('mt-dlg-pdf').close(); });
  /* Esc (cancel) fecha sem gerar; ao fechar, o foco volta ao "Gerar PDF" */
  $('mt-dlg-pdf').addEventListener('close', function () { $('mt-pdf').focus(); });
  $('mt-mais').addEventListener('click', function () {
    var box = $('mt-outras'), de = box.children.length;
    estado.mostrar = Infinity;
    desenhaOutras();
    /* o foco vai para a primeira linha nova (o botao "Ver mais" some) */
    var row = box.children[de];
    if (!row) return;
    var alvo = row.querySelector('.row-abrir');
    if (!alvo || !alvo.offsetParent) alvo = row.querySelector('.cb');
    if (alvo) alvo.focus();
  });
  /* Enter avanca (como "Continuar", com validacao) em toda etapa: nos campos, cartoes, pilulas, tiles,
     politicas, titulo e corpo da etapa; Espaco segue alternando a selecao. Voltar, Sair, trilha, o proprio
     Continuar (clique nativo) e links ficam com o Enter nativo. Tecla segurada (repeat) nao pula etapas. */
  document.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Enter' || ev.isComposing || ev.defaultPrevented || estado.tela !== 'perguntas') return;
    var alvo = ev.target, tela = $('mt-perguntas');
    if (!alvo || !(tela.contains(alvo) || alvo === document.body || alvo === document.documentElement)) return;
    if (ev.repeat) { ev.preventDefault(); return; }   /* segurado: nunca pula etapas, nem nas exclusoes */
    if (alvo.closest && alvo.closest('#mt-voltar, #mt-sair, .mt-tl-btn, #mt-continuar, a')) return;
    ev.preventDefault();
    continuar();
  });
  window.addEventListener('popstate', function (ev) {
    var s = ev.state || { tela: 'abertura', etapa: 0 };
    var tela = TELAS.indexOf(s.tela) >= 0 ? s.tela : 'abertura';
    cancelaAnimacao();
    /* sem resultado (ou de respostas que mudaram): nada de tela vazia, volta para a politica */
    if ((tela === 'revelacao' || tela === 'resultado') && !resultadoValido()) {
      pendente = false;
      history.replaceState({ tela: 'perguntas', etapa: ETAPAS.length - 1 }, '');
      irPara('perguntas', ETAPAS.length - 1, false);
      return;
    }
    if (tela === 'revelacao') revela(false);
    if (tela === 'resultado') desenhaResultado();
    irPara(tela, s.etapa, false);
  });

  $('mt-revelacao').querySelector('.mt-anel-msg').firstChild.nodeValue = 'Buscando as unidades';
  /* o titulo (aria-live) ja diz o total; o numero animado nao e lido */
  $('mt-contagem').parentNode.setAttribute('aria-hidden', 'true');

  history.replaceState({ tela: 'abertura', etapa: 0 }, '');
  irPara('abertura', 0, false);
  iniciado = true;

  /* uma assinatura so para a vida da pagina */
  window.SimUnidades.aoMudar(function (est) {
    if (!pendente) { if (est === 'ok') recalcula(); return; }
    if (estado.tela !== 'revelacao') { pendente = false; return; }
    if (est === 'ok') { pendente = false; calcula(); }
    else if (est === 'erro') { pendente = false; mostraErro(); }
  });
  window.SimUnidades.carregar();

})();

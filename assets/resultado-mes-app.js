/* ============================================================
   RESULTADO DO MES - tela (/resultado-mes)
   ------------------------------------------------------------
   Senha conferida no Apps Script (docs/apps-script-resultado-mes.gs).
   Texto vindo da planilha entra SEMPRE por textContent, nunca innerHTML.
   Modo demonstracao (so localhost, com ?demo): le
   dados-locais/resultado-mes.json, que fica fora do git.
   ============================================================ */
(function () {
  'use strict';

  var R = window.ResultadoMes;
  var URL_API = window.RESULTADO_MES_APPS_SCRIPT_URL || '';
  var LOCAL = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);
  var MODO_DEMO = LOCAL && (/[?&]demo\b/.test(location.search) || !URL_API);
  var CHAVE_SESSAO = 'resultado_mes_senha';
  var MSG_SENHA = 'Senha incorreta. Confira maiúsculas e tente de novo.';
  var TIMEOUT = 60000;
  var PAGINA_OPS_LONGO = 300; // trimestre e ano: o resto sai no botao "Ver todas"
  var PAGINA_IMOB = 8;
  var FUSO = 'America/Sao_Paulo';
  var MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

  var estado = {
    senha: '',
    mes: mesAtual(),
    meses: [],
    cache: {},
    todas: [],   // todas as vendas do mes
    vendas: [],  // depois dos filtros gerais
    resumo: null,
    geral: { emp: '', cidade: '', canal: '' }, // mantidos ao trocar de mes
    filtro: filtroVazio(),
    verOps: Infinity,
    verImob: PAGINA_IMOB
  };

  function filtroVazio() { return { tipo: '', conf: '', pend: [], imob: '', busca: '' }; }
  var seletores = {};
  var PERIODOS = { mes: 'mês', tri: 'trimestre', ano: 'ano' };
  function tipoAtual() { return R.tipoPeriodo(estado.mes); }
  function noTexto() { return 'no ' + PERIODOS[tipoAtual()]; }
  function paginaOps() { return tipoAtual() === 'mes' ? Infinity : PAGINA_OPS_LONGO; }
  var ASSINATURA = {
    assinado: { cls: 't-ok', txt: 'Assinado' },
    aguardando: { cls: 't-sem', txt: 'Aguardando' },
    cancelado: { cls: 't-err', txt: 'Cancelado' },
    nao_assinado: { cls: 't-err', txt: 'Não assinado' },
    sem_envio: { cls: 't-err', txt: 'Não enviado' }
  };
  var CANAIS = { house: 'House', canal: 'Canal Imob' };

  function $(id) { return document.getElementById(id); }
  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt !== undefined && txt !== null) e.textContent = txt;
    return e;
  }

  /* ---------- formatos ---------- */
  function mesAtual() {
    var p = new Intl.DateTimeFormat('en-CA', { timeZone: FUSO, year: 'numeric', month: '2-digit' }).formatToParts(new Date());
    var a = '', m = '';
    p.forEach(function (x) { if (x.type === 'year') a = x.value; if (x.type === 'month') m = x.value; });
    return a + '-' + m;
  }
  /* '2026-11', '2026-T4' ou '2026' por extenso */
  function nomePeriodo(p, capital) {
    var tipo = R.tipoPeriodo(p);
    if (tipo === 'ano') return p;
    var ano = p.slice(0, 4);
    if (tipo === 'tri') return p.slice(6) + 'º trimestre' + (capital ? ' de ' : ' ') + ano;
    var n = MESES[Number(p.slice(5, 7)) - 1] || p;
    if (capital) n = n.charAt(0).toUpperCase() + n.slice(1);
    return n + (capital ? ' de ' : ' ') + ano;
  }
  var fmtInt = new Intl.NumberFormat('pt-BR');
  var fmtReal = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });
  function mi(v) {
    if (Math.abs(v) >= 1e6) return 'R$ ' + (v / 1e6).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' mi';
    if (Math.abs(v) >= 1e3) return 'R$ ' + (v / 1e3).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' mil';
    return fmtReal.format(v);
  }
  function dm(iso) { return iso ? iso.slice(8, 10) + '/' + iso.slice(5, 7) : ''; }
  function plural(n, um, varios) { return fmtInt.format(n) + ' ' + (n === 1 ? um : varios); }
  var SIGLAS = ['SPI', 'PJ', 'LTDA', 'ME', 'EIRELI', 'RP'];
  var MINUSCULAS = ['de', 'da', 'do', 'das', 'dos', 'e'];
  function titulo(s) {
    if (s !== s.toUpperCase()) return s;
    return s.toLowerCase().replace(/[^\s·–-]+/g, function (w, i) {
      if (SIGLAS.indexOf(w.toUpperCase()) >= 0) return w.toUpperCase();
      if (i > 0 && MINUSCULAS.indexOf(w) >= 0) return w;
      return w.charAt(0).toUpperCase() + w.slice(1);
    });
  }
  function limparImob(s) {
    return titulo(s.replace(/^DIRECIONAL VENDAS SPI\s*[–-]\s*/i, 'Vendas SPI · ')
      .replace(/^SPI\s*-\s*CANAL IMOB PJ\s*[–-]\s*/i, 'Canal Imob PJ · ')
      .replace(/^RIVA VENDAS SPI\s*[–-]\s*/i, 'Riva Vendas SPI · '))
      .replace(/^(.+? · )(.*)$/, function (_, a, b) { return a + titulo(b); });
  }

  /* ---------- API ---------- */
  function falha(codigo, mensagem) { return { codigo: codigo, mensagem: mensagem }; }

  function chamar(mes) {
    if (MODO_DEMO) return chamarDemo(mes);
    var ctrl = new AbortController();
    var timer = setTimeout(function () { ctrl.abort(); }, TIMEOUT);
    /* text/plain evita o preflight de CORS; o Apps Script le e.postData.contents */
    return fetch(URL_API, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify({ senha: estado.senha, acao: 'mes', mes: mes }),
      signal: ctrl.signal
    }).then(function (r) { return r.text(); }, function () {
      throw falha('rede', 'A planilha não respondeu. Verifique a conexão e tente de novo.');
    }).then(function (texto) {
      var json;
      try { json = JSON.parse(texto); } catch (e) { throw falha('formato', 'O Web App não respondeu no formato esperado.'); }
      if (!json.ok) throw falha(json.erro || 'interno', json.mensagem || 'Erro no Web App.');
      /* o Web App antigo ignora trimestre/ano e devolve o mes atual */
      if (json.mes !== mes && R.tipoPeriodo(mes) !== 'mes') throw falha('versao', 'O filtro por trimestre e ano precisa da versão nova do Web App no Apps Script.');
      return json;
    }).finally(function () { clearTimeout(timer); });
  }

  var demo = null;
  function chamarDemo(mes) {
    var carga = demo ? Promise.resolve(demo) : fetch('dados-locais/resultado-mes.json')
      .then(function (r) {
        if (!r.ok) throw falha('demo', 'Arquivo dados-locais/resultado-mes.json não encontrado.');
        return r.json();
      }).then(function (j) { demo = j; return j; });
    return carga.then(function (d) {
      var meses = {};
      var d4 = d.abas.filter(function (a) { return a.aba === 'Envios D4Sign'; })[0] || null;
      var abas = d.abas.filter(function (a) { return a !== d4; }).map(function (a) {
        var iV = a.cabecalho.indexOf('Data da venda');
        var iC = a.cabecalho.indexOf('Data Confirmação Venda 2.0');
        return {
          aba: a.aba, cabecalho: a.cabecalho,
          linhas: a.linhas.filter(function (l) {
            var mv = R.dataIso(l[iV]).slice(0, 7), mc = R.dataIso(l[iC]).slice(0, 7);
            if (mc || mv) meses[mc || mv] = true;
            return R.noPeriodo(mv, mes) || R.noPeriodo(mc, mes);
          })
        };
      });
      return { ok: true, mes: mes, meses: Object.keys(meses).sort().reverse(), atualizadoEm: d.atualizadoEm, intervaloMinutos: 30, abas: abas, d4sign: d4 };
    });
  }

  /* ---------- senha ---------- */
  function gateCarregando(sim) {
    $('gate-entrar').disabled = sim;
    $('gate-entrar').textContent = sim ? 'Entrando…' : 'Entrar';
  }
  function gateErro(msg) {
    $('gate-erro').hidden = !msg;
    $('gate-erro-txt').textContent = msg || '';
    $('gate-senha').setAttribute('aria-invalid', msg ? 'true' : 'false');
  }
  function mostrarGate(msg) {
    $('app').hidden = true;
    $('gate').hidden = false;
    $('gate-demo').hidden = !MODO_DEMO;
    gateCarregando(false);
    gateErro(msg);
    $('gate-senha').value = '';
    $('gate-senha').focus();
  }
  function mostrarApp() {
    $('gate').hidden = true;
    $('app').hidden = false;
    $('aviso-demo').hidden = !MODO_DEMO;
  }
  function sair(msg) {
    try { sessionStorage.removeItem(CHAVE_SESSAO); } catch (e) { /* ignora */ }
    estado.senha = '';
    estado.cache = {};
    estado.geral = { emp: '', cidade: '', canal: '' };
    mostrarGate(msg);
  }
  function iniciarGate() {
    $('gate-form').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var senha = $('gate-senha').value;
      if (!senha) { $('gate-senha').focus(); return; }
      estado.senha = senha;
      gateCarregando(true);
      gateErro('');
      chamar(estado.mes).then(function (res) {
        try { sessionStorage.setItem(CHAVE_SESSAO, senha); } catch (e) { /* ignora */ }
        mostrarApp();
        receber(res);
      }).catch(function (f) {
        estado.senha = '';
        gateCarregando(false);
        gateErro(f.codigo === 'senha' ? MSG_SENHA : f.mensagem);
        $('gate-senha').select();
      });
    });
    $('gate-olho').addEventListener('click', function () {
      var c = $('gate-senha');
      var mostrar = c.type === 'password';
      c.type = mostrar ? 'text' : 'password';
      this.setAttribute('aria-pressed', mostrar ? 'true' : 'false');
      this.setAttribute('aria-label', mostrar ? 'Ocultar senha' : 'Mostrar senha');
    });
    $('sair').addEventListener('click', function () { sair(''); });
  }

  /* ---------- carga ---------- */
  function mostrarEstado(qual) {
    $('carregando').hidden = qual !== 'carregando';
    $('erro').hidden = qual !== 'erro';
    $('painel').hidden = qual !== 'ok';
  }
  var pedidoAtual = 0; // resposta atrasada de um periodo anterior e ignorada
  function carregar(mes) {
    estado.mes = mes;
    if (estado.cache[mes]) { pedidoAtual++; receber(estado.cache[mes]); return; }
    if ($('painel').hidden) mostrarEstado('carregando');
    else $('conteudo').classList.add('carregando');
    desenharPeriodo();
    var pedido = ++pedidoAtual;
    chamar(mes).then(function (res) {
      if (pedido === pedidoAtual) receber(res);
    }).catch(function (f) {
      if (pedido !== pedidoAtual) return;
      $('conteudo').classList.remove('carregando');
      if (f.codigo === 'senha') { sair(MSG_SENHA); return; }
      $('erro-txt').textContent = f.mensagem;
      mostrarEstado('erro');
    });
  }
  function receber(res) {
    estado.cache[res.mes] = res;
    estado.mes = res.mes;
    if (res.meses && res.meses.length) estado.meses = res.meses.filter(function (m) { return m >= '2015-01'; });
    estado.todas = R.vendasDoMes(res.abas, res.mes, res.d4sign);
    estado.filtro = filtroVazio();
    estado.verImob = PAGINA_IMOB;
    $('busca').value = '';
    $('conteudo').classList.remove('carregando');
    desenharTopo(res);
    aplicarGeral();
    mostrarEstado('ok');
  }

  /* ---------- filtros gerais ---------- */
  function aplicarGeral() {
    preencherGerais();
    estado.vendas = R.filtrarGeral(estado.todas, estado.geral);
    estado.resumo = R.resumo(estado.vendas);
    estado.verOps = paginaOps();
    estado.verImob = PAGINA_IMOB;
    desenharResumo();
    desenharMatriz();
    desenharPendencias();
    desenharEmpreendimentos();
    desenharImobiliarias();
    preencherSelects();
    desenharOps();
  }

  function encher(sel, todos, valores, rotulo) {
    sel.textContent = '';
    var o = el('option', null, todos); o.value = ''; sel.appendChild(o);
    valores.forEach(function (v) { var op = el('option', null, rotulo ? rotulo(v) : v); op.value = v; sel.appendChild(op); });
  }

  function unicos(lista, campo) {
    var m = {};
    lista.forEach(function (v) { if (v[campo]) m[v[campo]] = true; });
    return Object.keys(m).sort(function (a, b) { return a.localeCompare(b, 'pt-BR'); });
  }

  /* o que esta escolhido continua na lista mesmo sem venda no mes */
  function preencherGerais() {
    var g = estado.geral;
    function com(lista, atual) { return atual && lista.indexOf(atual) < 0 ? lista.concat(atual) : lista; }
    var daCidade = estado.todas.filter(function (v) { return !g.cidade || v.cidade === g.cidade; });
    encher($('g-emp'), 'Todos os empreendimentos', com(unicos(daCidade, 'emp'), g.emp));
    var cidades = com(unicos(estado.todas, 'cidade'), g.cidade);
    cidades.sort(function (a, b) { return (a === 'Outras') - (b === 'Outras') || a.localeCompare(b, 'pt-BR'); });
    encher($('g-cidade'), 'Todas as cidades', cidades);
    $('g-emp').value = g.emp;
    $('g-cidade').value = g.cidade;
    $('g-canal').value = g.canal;
    seletores['g-emp'].atualizar();
    seletores['g-cidade'].atualizar();
    seletores['g-canal'].atualizar();
    $('g-limpar').disabled = !g.emp && !g.cidade && !g.canal;
  }

  /* ---------- topo ---------- */
  /* meses com venda (o atual sempre entra) */
  function mesesDisponiveis() {
    var lista = estado.meses.slice();
    if (lista.indexOf(mesAtual()) < 0) lista.push(mesAtual());
    return lista;
  }
  /* periodos de um tipo que tem venda, do mais antigo para o mais novo */
  function periodos(tipo) {
    var m = {};
    mesesDisponiveis().forEach(function (x) { m[R.periodoDe(x, tipo)] = true; });
    if (tipo === tipoAtual()) m[estado.mes] = true;
    return Object.keys(m).sort();
  }

  function desenharPeriodo() {
    var tipo = tipoAtual();
    Array.prototype.forEach.call(document.querySelectorAll('.per-tipo'), function (e) { e.textContent = PERIODOS[tipo]; });
    /* no trimestre o proprio nome ja diz o que e: "Vendas do 4º trimestre 2026" */
    $('per-titulo').textContent = tipo === 'tri' ? '' : PERIODOS[tipo];
    $('mes-nome').textContent = nomePeriodo(estado.mes);
    $('per-valor').textContent = nomePeriodo(estado.mes, true);
    var lista = periodos(tipo);
    var i = lista.indexOf(estado.mes);
    $('per-ant').disabled = i <= 0;
    $('per-prox').disabled = i >= lista.length - 1;
  }

  /* o painel navega por ano e tipo sem carregar nada ate o clique na opcao */
  var vista = { tipo: 'mes', ano: '' };
  function anos() { return periodos('ano'); }

  function desenharPainelPeriodo() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-per]'), function (b) {
      b.setAttribute('aria-pressed', b.dataset.per === vista.tipo ? 'true' : 'false');
    });
    var porAno = vista.tipo === 'ano';
    $('per-ano').hidden = porAno;
    $('per-ano-txt').textContent = vista.ano;
    var lista = anos();
    $('per-ano-ant').disabled = vista.ano <= lista[0];
    $('per-ano-prox').disabled = vista.ano >= lista[lista.length - 1];

    var temVenda = {};
    periodos(vista.tipo).forEach(function (p) { temVenda[p] = true; });
    var opcoes = porAno
      ? lista.slice().reverse().map(function (a) { return { valor: a, txt: a }; })
      : vista.tipo === 'tri'
        ? ['jan a mar', 'abr a jun', 'jul a set', 'out a dez'].map(function (d, i) { return { valor: vista.ano + '-T' + (i + 1), txt: (i + 1) + 'º tri', sub: d }; })
        : MESES.map(function (n, i) { return { valor: vista.ano + '-' + String(i + 1).padStart(2, '0'), txt: n.charAt(0).toUpperCase() + n.slice(1, 3) }; });
    var grade = $('per-grade');
    grade.textContent = '';
    grade.classList.toggle('duas-col', vista.tipo === 'tri');
    opcoes.forEach(function (o) {
      var b = el('button', 'per-op num', o.txt);
      b.type = 'button';
      if (o.sub) b.appendChild(el('small', null, o.sub));
      b.disabled = !temVenda[o.valor];
      b.setAttribute('aria-pressed', o.valor === estado.mes ? 'true' : 'false');
      b.setAttribute('aria-label', nomePeriodo(o.valor, true));
      b.addEventListener('click', function () { fecharPeriodo(true); carregar(o.valor); });
      grade.appendChild(b);
    });
  }

  function abrirPeriodo() {
    vista = { tipo: tipoAtual(), ano: estado.mes.slice(0, 4) };
    desenharPainelPeriodo();
    $('per-painel').hidden = false;
    $('per-botao').setAttribute('aria-expanded', 'true');
    var atual = $('per-grade').querySelector('[aria-pressed="true"]');
    if (atual) atual.focus();
  }
  function fecharPeriodo(devolverFoco) {
    if ($('per-painel').hidden) return;
    $('per-painel').hidden = true;
    $('per-botao').setAttribute('aria-expanded', 'false');
    if (devolverFoco) $('per-botao').focus();
  }

  function andarPeriodo(passo) {
    var lista = periodos(tipoAtual());
    var alvo = lista[lista.indexOf(estado.mes) + passo];
    if (alvo) carregar(alvo);
  }

  function iniciarPeriodo() {
    $('per-botao').addEventListener('click', function () { if ($('per-painel').hidden) abrirPeriodo(); else fecharPeriodo(false); });
    $('per-ant').addEventListener('click', function () { andarPeriodo(-1); });
    $('per-prox').addEventListener('click', function () { andarPeriodo(1); });
    Array.prototype.forEach.call(document.querySelectorAll('[data-per]'), function (b) {
      b.addEventListener('click', function () { vista.tipo = b.dataset.per; desenharPainelPeriodo(); });
    });
    $('per-ano-ant').addEventListener('click', function () { vista.ano = String(Number(vista.ano) - 1); desenharPainelPeriodo(); });
    $('per-ano-prox').addEventListener('click', function () { vista.ano = String(Number(vista.ano) + 1); desenharPainelPeriodo(); });
    $('per').addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && !$('per-painel').hidden) { ev.preventDefault(); fecharPeriodo(true); }
    });
    /* composedPath: a opcao clicada pode ja ter saido da tela quando o evento sobe */
    document.addEventListener('click', function (ev) {
      if (ev.composedPath().indexOf($('per')) < 0) fecharPeriodo(false);
    });
  }

  function desenharTopo(res) {
    desenharPeriodo();

    var txt = 'Sem data de atualização';
    var velho = true;
    var a = res.atualizadoEm || '';
    var m = a.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})/);
    if (m) {
      var quando = new Date(m[1] + '-' + m[2] + '-' + m[3] + 'T' + m[4] + ':' + m[5] + ':00-03:00');
      var min = (Date.now() - quando.getTime()) / 60000;
      var intervalo = res.intervaloMinutos || 30;
      velho = min > intervalo * 2.5;
      var hoje = new Intl.DateTimeFormat('en-CA', { timeZone: FUSO }).format(new Date()) === m[1] + '-' + m[2] + '-' + m[3];
      if (hoje) {
        var prox = new Date(quando.getTime() + intervalo * 60000);
        var hp = new Intl.DateTimeFormat('pt-BR', { timeZone: FUSO, hour: '2-digit', minute: '2-digit' }).format(prox);
        txt = 'Atualizado às ' + m[4] + ':' + m[5] + (velho ? '' : ' · próxima às ' + hp);
      } else {
        txt = 'Atualizado em ' + m[3] + '/' + m[2] + ' às ' + m[4] + ':' + m[5];
      }
    }
    $('atualizacao').textContent = txt;
    $('dot').classList.toggle('velho', velho);
  }

  /* ---------- resumo ---------- */
  function desenharResumo() {
    var m = estado.resumo.matriz;
    function detalhe(c) {
      return c.n ? plural(c.n, 'venda', 'vendas') + ' · ticket médio ' + mi(c.vgv / c.n) : 'Nenhuma venda';
    }
    [['com', m.comercial.total], ['fac', m.facilitada.total], ['vgv', m.total.total]].forEach(function (x) {
      $('s-' + x[0]).textContent = mi(x[1].vgv);
      $('s-' + x[0] + '-d').textContent = detalhe(x[1]);
    });
  }

  function desenharMatriz() {
    var m = estado.resumo.matriz;
    Array.prototype.forEach.call(document.querySelectorAll('#matriz .cel'), function (b) {
      var linha = m[b.dataset.tipo || 'total'];
      var c = linha[b.dataset.conf || 'total'];
      b.textContent = '';
      b.appendChild(el('span', 'cel-n num', fmtInt.format(c.n)));
      b.appendChild(el('span', 'cel-v num', mi(c.vgv)));
      var rot = (b.dataset.tipo ? (b.dataset.tipo === 'comercial' ? 'Comerciais' : 'Facilitadas') : 'Todas') +
        (b.dataset.conf === 'ok' ? ' confirmadas' : b.dataset.conf === 'sem' ? ' sem confirmação' : '');
      b.setAttribute('aria-label', rot + ': ' + c.n + ' vendas, ' + mi(c.vgv) + '. Filtrar lista.');
    });
  }

  function desenharPendencias() {
    var p = estado.resumo.pendencias;
    $('pend-sub').textContent = !p.total
      ? 'Nenhuma venda para conferir.'
      : 'Assinatura, FID e sinal nas ' + plural(p.total, 'venda', 'vendas') + '. Uma venda pode ter mais de uma pendência.' +
        (p.temD4 ? '' : ' Assinatura indisponível: dados do D4Sign ainda não chegaram.');
    var itens = [
      { id: 'assinatura', titulo: 'Sem assinatura', desc: 'Cliente ainda não assinou o PCV', n: p.assinatura, off: !p.temD4 },
      { id: 'fid', titulo: 'FID pendente', desc: 'Venda sem número de FID', n: p.fid },
      { id: 'sinal', titulo: 'Sinal pendente', desc: 'Sem boleto/PIX nem cartão pago', n: p.sinal },
      { id: 'nenhuma', titulo: 'Sem pendência', desc: 'Assinada, com FID e sinal pago', n: p.semPendencia, off: !p.temD4 }
    ];
    var lista = $('pend-lista');
    lista.textContent = '';
    itens.forEach(function (i) {
      var b = el('button', 'pend-l' + (i.id === 'nenhuma' ? ' pend-ok' : ''));
      b.type = 'button';
      b.disabled = !!i.off || !i.n;
      var t = el('span', 'pend-t');
      t.appendChild(el('b', null, i.titulo));
      t.appendChild(el('span', null, i.desc));
      b.appendChild(t);
      b.appendChild(el('span', 'pend-n num', i.off ? '–' : fmtInt.format(i.n)));
      var barra = el('span', 'pend-barra');
      barra.setAttribute('aria-hidden', 'true');
      var cheio = el('i');
      cheio.style.width = (!i.off && p.total ? i.n / p.total * 100 : 0) + '%';
      barra.appendChild(cheio);
      b.appendChild(barra);
      b.addEventListener('click', function () {
        estado.filtro = filtroVazio();
        estado.filtro.pend = [i.id];
        $('busca').value = '';
        reiniciarOps();
        $('ops').scrollIntoView({ block: 'start' });
      });
      lista.appendChild(b);
    });
  }

  function desenharEmpreendimentos() {
    var lista = $('emp-lista');
    lista.textContent = '';
    var g = estado.resumo.empreendimentos;
    if (!g.length) { lista.appendChild(el('p', 'vazio', 'Nenhuma venda ' + noTexto() + '.')); return; }
    var max = g[0].n;
    g.forEach(function (e) {
      var l = el('div', 'emp-l');
      l.appendChild(el('span', null, e.nome)).style.fontWeight = '500';
      var trilho = el('div', 'emp-barra');
      var bar = trilho.appendChild(el('div', 'emp-barra'));
      bar.style.width = (e.n / max * 100) + '%';
      bar.style.minWidth = '48px';
      [['com', e.comerciais, 'comerciais'], ['fac', e.facilitadas, 'facilitadas']].forEach(function (x) {
        if (!x[1]) return;
        var seg = el('div', 'emp-seg ' + x[0]);
        seg.style.flexGrow = x[1];
        seg.title = x[1] + ' ' + x[2];
        seg.appendChild(el('b', 'num', fmtInt.format(x[1])));
        seg.appendChild(el('i'));
        bar.appendChild(seg);
      });
      trilho.setAttribute('role', 'img');
      trilho.setAttribute('aria-label', e.comerciais + ' comerciais e ' + e.facilitadas + ' facilitadas');
      l.appendChild(trilho);
      l.appendChild(el('span', 'num r', fmtInt.format(e.n))).style.fontWeight = '700';
      var conf = l.appendChild(el('span', 'num r conf', e.confirmadas + ' confirm.'));
      conf.style.cssText = 'font-size:.78rem;color:var(--slate)';
      l.appendChild(el('span', 'num r', mi(e.vgv))).style.fontSize = '.82rem';
      lista.appendChild(l);
    });
  }

  function desenharImobiliarias() {
    var g = estado.resumo.imobiliarias;
    var corpo = $('imob-corpo');
    corpo.textContent = '';
    g.slice(0, estado.verImob).forEach(function (x, i) {
      var tr = el('tr');
      tr.appendChild(el('td', 'num fraco', i + 1));
      tr.appendChild(el('td', null, limparImob(x.nome))).style.fontWeight = '500';
      tr.appendChild(el('td', 'num r', x.comerciais));
      tr.appendChild(el('td', 'num r', x.facilitadas));
      tr.appendChild(el('td', 'num r', x.confirmadas));
      tr.appendChild(el('td', 'num r', x.n)).style.fontWeight = '700';
      tr.appendChild(el('td', 'num r nw', mi(x.vgv)));
      corpo.appendChild(tr);
    });
    $('imob-sub').textContent = g.length > PAGINA_IMOB && estado.verImob < g.length
      ? 'Top ' + PAGINA_IMOB + ' de ' + g.length + ' por quantidade'
      : plural(g.length, 'imobiliária/equipe', 'imobiliárias/equipes');
    var mais = $('imob-mais');
    mais.hidden = g.length <= PAGINA_IMOB;
    mais.textContent = estado.verImob < g.length ? 'Ver todas as ' + g.length : 'Mostrar só o top ' + PAGINA_IMOB;
  }

  /* ---------- lista de OPs ---------- */
  function preencherSelects() {
    var imobs = estado.resumo.imobiliarias.map(function (e) { return e.nome; }).sort();
    if (imobs.indexOf(estado.filtro.imob) < 0) estado.filtro.imob = '';
    encher($('f-imob'), 'Todas as equipes', imobs, limparImob);
    $('f-imob').value = estado.filtro.imob;
    seletores['f-imob'].atualizar();
  }

  function filtradas() {
    var f = estado.filtro;
    var b = f.busca.trim().toLowerCase();
    return estado.vendas.filter(function (v) {
      if (f.tipo && v.tipo !== f.tipo) return false;
      if (f.conf === 'ok' && !v.confirmada) return false;
      if (f.conf === 'sem' && v.confirmada) return false;
      if (!R.temAlguma(v, f.pend)) return false;
      if (f.imob && v.imob !== f.imob) return false;
      if (b && [v.op, v.cliente, v.unidade, v.emp, v.imob, v.corretor, v.fase, v.fid].join(' ').toLowerCase().indexOf(b) < 0) return false;
      return true;
    });
  }

  function desenharFiltros() {
    var f = estado.filtro;
    Array.prototype.forEach.call(document.querySelectorAll('[data-seg]'), function (c) {
      c.setAttribute('aria-pressed', f[c.dataset.seg] === c.dataset.v ? 'true' : 'false');
    });
    Array.prototype.forEach.call($('f-pend').options, function (o) { o.selected = f.pend.indexOf(o.value) >= 0; });
    $('f-imob').value = f.imob;
    seletores['f-pend'].atualizar();
    seletores['f-imob'].atualizar();
    $('f-limpar').disabled = !f.tipo && !f.conf && !f.pend.length && !f.imob && !f.busca;
  }

  function tag(cls, txt) { return el('span', 'tag ' + cls, txt); }

  function desenharOps() {
    desenharFiltros();
    var lista = filtradas();
    var corpo = $('ops-corpo');
    corpo.textContent = '';
    lista.slice(0, estado.verOps).forEach(function (v) {
      var tr = el('tr');
      var td = el('td', 'num nw');
      td.appendChild(el('div', null, dm(v.dataConta))).style.fontWeight = '700';
      td.appendChild(el('div', 'fraco', v.pelaConfirmacao ? 'Confirmação 2.0' : 'Data da venda'));
      tr.appendChild(td);

      td = el('td', 'op-cli');
      td.appendChild(el('div', 'num nw', v.op)).style.fontWeight = '700';
      if (v.cliente) td.appendChild(el('div', 'cli', titulo(v.cliente)));
      tr.appendChild(td);

      td = el('td');
      td.appendChild(el('div', 'nw', v.unidade)).style.fontWeight = '500';
      td.appendChild(el('div', 'fraco un-emp', v.emp));
      tr.appendChild(td);

      td = el('td');
      td.appendChild(v.tipo === 'comercial' ? tag('t-com', 'Comercial') : tag('t-fac', 'Facilitada'));
      if (v.virouComercial) td.appendChild(el('div', 'fraco nw', 'era facilitada')).style.marginTop = '.25rem';
      tr.appendChild(td);

      tr.appendChild(el('td', null, v.fase));

      td = el('td');
      td.appendChild(v.confirmada ? tag('t-ok', 'Confirmada ' + dm(v.conf)) : tag('t-sem', 'Pendente'));
      tr.appendChild(td);

      td = el('td');
      var fid = td.appendChild(v.fidOk ? tag('t-ok', 'Aprovado') : tag('t-sem', 'Pendente'));
      if (v.fidOk) fid.title = 'FID ' + v.fid;
      tr.appendChild(td);

      td = el('td');
      var a = ASSINATURA[v.assinatura];
      if (!a) td.appendChild(el('span', 'fraco', '–'));
      else td.appendChild(tag(a.cls, a.txt));
      tr.appendChild(td);

      td = el('td');
      var sinal = td.appendChild(v.sinalPago ? tag('t-ok', 'Pago') : tag('t-sem', 'Pendente'));
      if (v.sinalPago) sinal.title = v.boleto && v.cartao ? 'Boleto/PIX e cartão' : v.boleto ? 'Boleto/PIX' : 'Cartão';
      tr.appendChild(td);

      td = el('td');
      td.appendChild(el('div', null, limparImob(v.imob))).style.fontSize = '.8rem';
      td.appendChild(el('div', 'fraco', titulo(v.corretor)));
      tr.appendChild(td);

      tr.appendChild(el('td', 'num r nw', fmtReal.format(v.valor))).style.fontWeight = '700';
      corpo.appendChild(tr);
    });
    $('ops-vazio').hidden = lista.length > 0;
    var total = estado.vendas.length;
    $('ops-sub').textContent = lista.length === total
      ? plural(total, 'venda', 'vendas') + ' ' + noTexto()
      : plural(lista.length, 'venda', 'vendas') + ' de ' + fmtInt.format(total) + ' · ' + mi(lista.reduce(function (s, v) { return s + v.valor; }, 0));
    var mais = $('ops-mais');
    mais.hidden = lista.length <= estado.verOps;
    mais.textContent = 'Ver todas as ' + plural(lista.length, 'venda', 'vendas');
    $('exportar').disabled = !lista.length;
  }

  function exportar() {
    var cols = ['Data', 'Conta por', 'OP', 'Cliente', 'Unidade', 'Empreendimento', 'Cidade', 'Tipo', 'Era facilitada', 'Fase',
      'Data da venda', 'Data Confirmação 2.0', 'FID', 'Número do FID', 'Assinatura (D4Sign)', 'Boleto/PIX pago', 'Cartão pago', 'Imobiliária', 'House/Canal Imob', 'Corretor', 'Valor'];
    /* celula que comeca com = + - @ vira formula no Excel: prefixa com ' */
    function q(v) { var s = String(v === undefined || v === null ? '' : v); if (/^[=+\-@\t\r]/.test(s)) s = "'" + s; return /[";\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }
    function br(iso) { return iso ? iso.slice(8, 10) + '/' + iso.slice(5, 7) + '/' + iso.slice(0, 4) : ''; }
    var linhas = filtradas().map(function (v) {
      return [br(v.dataConta), v.pelaConfirmacao ? 'Confirmação 2.0' : 'Data da venda', v.op, v.cliente, v.unidade, v.emp, v.cidade,
        v.tipo === 'comercial' ? 'Comercial' : 'Facilitada', v.virouComercial ? 'Sim' : 'Não', v.fase, br(v.venda), br(v.conf),
        v.fidOk ? 'Aprovado' : 'Pendente', v.fid, ASSINATURA[v.assinatura] ? ASSINATURA[v.assinatura].txt : '',
        v.boleto ? 'Sim' : 'Não', v.cartao ? 'Sim' : 'Não', v.imob, CANAIS[v.canal] || '', v.corretor,
        v.valor.toFixed(2).replace('.', ',')].map(q).join(';');
    });
    var csv = '﻿' + [cols.join(';')].concat(linhas).join('\r\n');
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    a.download = 'vendas-' + estado.mes + '.csv';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  function reiniciarOps() { estado.verOps = paginaOps(); desenharOps(); }

  function iniciarControles() {
    ['g-emp', 'g-cidade', 'g-canal', 'f-imob'].forEach(function (id) { seletores[id] = window.Seletor.criar($(id)); });
    seletores['f-pend'] = window.Seletor.criar($('f-pend'), { vazio: 'Todas as situações' });
    iniciarPeriodo();
    $('tentar').addEventListener('click', function () { carregar(estado.mes); });

    Array.prototype.forEach.call(document.querySelectorAll('#matriz .cel'), function (b) {
      b.addEventListener('click', function () {
        estado.filtro.tipo = b.dataset.tipo;
        estado.filtro.conf = b.dataset.conf;
        estado.filtro.pend = [];
        reiniciarOps();
        $('ops').scrollIntoView({ block: 'start' });
      });
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-seg]'), function (c) {
      c.addEventListener('click', function () {
        estado.filtro[c.dataset.seg] = c.dataset.v;
        reiniciarOps();
      });
    });
    $('f-pend').addEventListener('change', function () {
      var antes = estado.filtro.pend;
      var marcadas = Array.prototype.filter.call(this.options, function (o) { return o.selected; }).map(function (o) { return o.value; });
      /* "Sem pendencia" nao combina com as outras: vale a que foi marcada por ultimo */
      if (marcadas.indexOf('nenhuma') >= 0 && marcadas.length > 1) {
        marcadas = antes.indexOf('nenhuma') < 0 ? ['nenhuma'] : marcadas.filter(function (x) { return x !== 'nenhuma'; });
      }
      estado.filtro.pend = marcadas;
      reiniciarOps();
    });
    $('f-imob').addEventListener('change', function () { estado.filtro.imob = this.value; reiniciarOps(); });
    $('f-limpar').addEventListener('click', function () {
      estado.filtro = filtroVazio();
      $('busca').value = '';
      reiniciarOps();
    });
    $('g-emp').addEventListener('change', function () { estado.geral.emp = this.value; aplicarGeral(); });
    $('g-cidade').addEventListener('change', function () {
      var cidade = this.value;
      estado.geral.cidade = cidade;
      if (cidade && estado.geral.emp && R.cidadeDe(estado.geral.emp) !== cidade) estado.geral.emp = '';
      aplicarGeral();
    });
    $('g-canal').addEventListener('change', function () { estado.geral.canal = this.value; aplicarGeral(); });
    $('g-limpar').addEventListener('click', function () { estado.geral = { emp: '', cidade: '', canal: '' }; aplicarGeral(); });
    var t;
    $('busca').addEventListener('input', function () {
      var v = this.value;
      clearTimeout(t);
      t = setTimeout(function () { estado.filtro.busca = v; reiniciarOps(); }, 150);
    });
    $('ops-mais').addEventListener('click', function () { estado.verOps = Infinity; desenharOps(); });
    $('imob-mais').addEventListener('click', function () {
      estado.verImob = estado.verImob < estado.resumo.imobiliarias.length ? Infinity : PAGINA_IMOB;
      desenharImobiliarias();
    });
    $('exportar').addEventListener('click', exportar);
  }

  iniciarGate();
  iniciarControles();
  var salva = null;
  try { salva = sessionStorage.getItem(CHAVE_SESSAO); } catch (e) { /* ignora */ }
  if (salva) { estado.senha = salva; mostrarApp(); carregar(estado.mes); }
  else mostrarGate('');
})();

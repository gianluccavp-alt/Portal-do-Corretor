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
  var PAGINA_OPS = Infinity; // mostra a lista inteira
  var PAGINA_IMOB = 8;
  var FUSO = 'America/Sao_Paulo';
  var MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

  var estado = {
    senha: '',
    mes: mesAtual(),
    meses: [],
    cache: {},
    vendas: [],
    resumo: null,
    filtro: { tipo: '', conf: '', emp: '', imob: '', busca: '' },
    verOps: PAGINA_OPS,
    verImob: PAGINA_IMOB
  };

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
  function nomeMes(ym, capital) {
    var p = ym.split('-');
    var n = MESES[Number(p[1]) - 1] || ym;
    if (capital) n = n.charAt(0).toUpperCase() + n.slice(1);
    return n + (capital ? ' de ' : ' ') + p[0];
  }
  function somaMes(ym, d) {
    var p = ym.split('-').map(Number);
    var t = p[0] * 12 + (p[1] - 1) + d;
    return Math.floor(t / 12) + '-' + String(t % 12 + 1).padStart(2, '0');
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
      var abas = d.abas.map(function (a) {
        var iV = a.cabecalho.indexOf('Data da venda');
        var iC = a.cabecalho.indexOf('Data Confirmação Venda 2.0');
        return {
          aba: a.aba, cabecalho: a.cabecalho,
          linhas: a.linhas.filter(function (l) {
            var mv = R.dataIso(l[iV]).slice(0, 7), mc = R.dataIso(l[iC]).slice(0, 7);
            if (mc || mv) meses[mc || mv] = true;
            return mv === mes || mc === mes;
          })
        };
      });
      return { ok: true, mes: mes, meses: Object.keys(meses).sort().reverse(), atualizadoEm: d.atualizadoEm, intervaloMinutos: 30, abas: abas };
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
  function carregar(mes) {
    estado.mes = mes;
    if (estado.cache[mes]) { receber(estado.cache[mes]); return; }
    if ($('painel').hidden) mostrarEstado('carregando');
    else $('conteudo').classList.add('carregando');
    $('mes-nome').textContent = nomeMes(mes);
    chamar(mes).then(receber).catch(function (f) {
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
    estado.vendas = R.vendasDoMes(res.abas, res.mes);
    estado.resumo = R.resumo(estado.vendas);
    estado.filtro = { tipo: '', conf: '', emp: '', imob: '', busca: '' };
    estado.verOps = PAGINA_OPS;
    estado.verImob = PAGINA_IMOB;
    $('busca').value = '';
    $('conteudo').classList.remove('carregando');
    desenharTopo(res);
    desenharResumo();
    desenharMatriz();
    desenharSinal();
    desenharEmpreendimentos();
    desenharImobiliarias();
    preencherSelects();
    desenharOps();
    mostrarEstado('ok');
  }

  /* ---------- topo ---------- */
  function desenharTopo(res) {
    $('mes-nome').textContent = nomeMes(estado.mes);
    var sel = $('mes');
    var lista = estado.meses.slice();
    var atual = mesAtual();
    if (lista.indexOf(atual) < 0) lista.unshift(atual);
    if (lista.indexOf(estado.mes) < 0) lista.push(estado.mes);
    lista.sort().reverse();
    sel.textContent = '';
    lista.forEach(function (m) {
      var o = el('option', null, nomeMes(m, true));
      o.value = m;
      if (m === estado.mes) o.selected = true;
      sel.appendChild(o);
    });
    var i = lista.indexOf(estado.mes);
    $('mes-ant').disabled = i >= lista.length - 1;
    $('mes-prox').disabled = i <= 0;

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
    var r = estado.resumo;
    $('s-vgv').textContent = mi(r.total.vgv);
    $('s-vgv-d').textContent = r.total.n ? 'Ticket médio ' + mi(r.ticket) : 'Nenhuma venda no mês';
    $('s-vgv-n').textContent = r.total.n ? 'Em ' + plural(r.total.n, 'venda', 'vendas') : '';
    $('s-total').textContent = fmtInt.format(r.total.n);
    $('s-oficial').textContent = fmtInt.format(r.oficial.n);
    $('s-pend').textContent = fmtInt.format(r.pendentes.n);
    $('s-pend-d').textContent = mi(r.pendentes.vgv) + ' · contam pela data da venda';
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

  function desenharSinal() {
    var s = estado.resumo.sinal;
    $('sinal-sub').textContent = s.total
      ? 'As ' + plural(s.total, 'venda', 'vendas') + ' sem Data Confirmação 2.0, pelo que falta para confirmar.'
      : 'Todas as vendas do mês já têm Data Confirmação 2.0.';
    var itens = [
      { cor: '#1E8E4A', titulo: 'PCV assinado e sinal pago', desc: 'Só falta o sistema confirmar', n: s.pcvESinal },
      { cor: '#3A4043', titulo: 'PCV assinado, sinal em aberto', desc: 'Cobrar boleto/PIX ou cartão', n: s.soPcv },
      { cor: '#9AA1A4', titulo: 'Sinal pago, PCV sem assinatura', desc: 'Cobrar assinatura do contrato', n: s.soSinal },
      { cor: '#F2B544', titulo: 'Nem PCV nem sinal', desc: 'Maior risco de não confirmar no mês', n: s.nenhum }
    ];
    var bar = $('sinal-bar');
    bar.textContent = '';
    bar.setAttribute('aria-label', itens.map(function (i) { return i.n + ' ' + i.titulo; }).join(', '));
    var lista = $('sinal-lista');
    lista.textContent = '';
    itens.forEach(function (i) {
      if (s.total) {
        var seg = el('span');
        seg.style.width = (i.n / s.total * 100) + '%';
        seg.style.background = i.cor;
        bar.appendChild(seg);
      }
      var l = el('div', 'sinal-l');
      var sw = el('span', 'sw');
      sw.style.background = i.cor;
      sw.setAttribute('aria-hidden', 'true');
      var t = el('div', 'sinal-t');
      t.appendChild(el('b', null, i.titulo));
      t.appendChild(el('span', null, i.desc));
      l.appendChild(sw);
      l.appendChild(t);
      l.appendChild(el('span', 'num', fmtInt.format(i.n))).style.cssText = 'font-weight:700;font-size:1.05rem';
      lista.appendChild(l);
    });
  }

  function desenharEmpreendimentos() {
    var lista = $('emp-lista');
    lista.textContent = '';
    var g = estado.resumo.empreendimentos;
    if (!g.length) { lista.appendChild(el('p', 'vazio', 'Nenhuma venda no mês.')); return; }
    var max = g[0].n;
    g.forEach(function (e) {
      var l = el('div', 'emp-l');
      l.appendChild(el('span', null, e.nome)).style.fontWeight = '500';
      var bar = el('div', 'bar');
      var c = el('span'); c.style.width = (e.comerciais / max * 100) + '%'; c.style.background = '#3A4043';
      var f = el('span'); f.style.width = (e.facilitadas / max * 100) + '%'; f.style.background = '#B9BEC0';
      bar.appendChild(c); bar.appendChild(f);
      bar.setAttribute('aria-hidden', 'true');
      l.appendChild(bar);
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
    function encher(sel, todos, valores, rotulo) {
      sel.textContent = '';
      var o = el('option', null, todos); o.value = ''; sel.appendChild(o);
      valores.forEach(function (v) { var op = el('option', null, rotulo ? rotulo(v) : v); op.value = v; sel.appendChild(op); });
    }
    var emps = estado.resumo.empreendimentos.map(function (e) { return e.nome; }).sort();
    var imobs = estado.resumo.imobiliarias.map(function (e) { return e.nome; }).sort();
    encher($('f-emp'), 'Todos os empreendimentos', emps);
    encher($('f-imob'), 'Todas as imobiliárias', imobs, limparImob);
  }

  function filtradas() {
    var f = estado.filtro;
    var b = f.busca.trim().toLowerCase();
    return estado.vendas.filter(function (v) {
      if (f.tipo && v.tipo !== f.tipo) return false;
      if (f.conf === 'ok' && !v.confirmada) return false;
      if (f.conf === 'sem' && v.confirmada) return false;
      if (f.emp && v.emp !== f.emp) return false;
      if (f.imob && v.imob !== f.imob) return false;
      if (b && [v.op, v.unidade, v.emp, v.imob, v.corretor, v.fase].join(' ').toLowerCase().indexOf(b) < 0) return false;
      return true;
    });
  }

  function desenharChips() {
    var f = estado.filtro;
    Array.prototype.forEach.call(document.querySelectorAll('[data-chip]'), function (c) {
      var k = c.dataset.chip;
      var on = k === 'todas' ? !f.tipo && !f.conf : (k === f.tipo || k === f.conf);
      c.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    $('f-emp').value = f.emp;
    $('f-imob').value = f.imob;
  }

  function tag(cls, txt) { return el('span', 'tag ' + cls, txt); }

  function desenharOps() {
    desenharChips();
    var lista = filtradas();
    var corpo = $('ops-corpo');
    corpo.textContent = '';
    lista.slice(0, estado.verOps).forEach(function (v) {
      var tr = el('tr');
      var td = el('td', 'num nw');
      td.appendChild(el('div', null, dm(v.dataConta))).style.fontWeight = '700';
      td.appendChild(el('div', 'fraco', v.pelaConfirmacao ? 'Confirmação 2.0' : 'Data da venda'));
      tr.appendChild(td);

      tr.appendChild(el('td', 'num nw', v.op)).style.fontWeight = '500';

      td = el('td');
      td.appendChild(el('div', 'nw', v.unidade)).style.fontWeight = '500';
      td.appendChild(el('div', 'fraco nw', v.emp));
      tr.appendChild(td);

      td = el('td');
      td.appendChild(v.tipo === 'comercial' ? tag('t-com', 'Comercial') : tag('t-fac', 'Facilitada'));
      if (v.virouComercial) td.appendChild(el('div', 'fraco nw', 'era facilitada')).style.marginTop = '.25rem';
      tr.appendChild(td);

      tr.appendChild(el('td', 'nw', v.fase));

      td = el('td');
      td.appendChild(v.confirmada ? tag('t-ok', 'Confirmada ' + dm(v.conf)) : tag('t-sem', 'Pendente'));
      tr.appendChild(td);

      var pcv = tr.appendChild(el('td', 'num nw', v.pcv ? 'Assinado ' + dm(v.pcv) : 'Não assinado'));
      if (!v.pcv) pcv.style.color = 'var(--slate)';

      var sinal = v.boleto && v.cartao ? 'Boleto/PIX e cartão' : v.boleto ? 'Boleto/PIX' : v.cartao ? 'Cartão' : 'Não pago';
      var tdS = tr.appendChild(el('td', 'nw', sinal));
      tdS.style.color = v.sinalPago ? 'var(--ok)' : 'var(--slate)';

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
      ? plural(total, 'venda', 'vendas') + ' no mês'
      : plural(lista.length, 'venda', 'vendas') + ' de ' + fmtInt.format(total) + ' · ' + mi(lista.reduce(function (s, v) { return s + v.valor; }, 0));
    var mais = $('ops-mais');
    mais.hidden = lista.length <= estado.verOps;
    mais.textContent = 'Ver todas as ' + plural(lista.length, 'venda', 'vendas');
    $('exportar').disabled = !lista.length;
  }

  function exportar() {
    var cols = ['Data que conta', 'Conta por', 'OP', 'Unidade', 'Empreendimento', 'Tipo', 'Era facilitada', 'Fase',
      'Data da venda', 'Data Confirmação 2.0', 'PCV assinado', 'Boleto/PIX pago', 'Cartão pago', 'Imobiliária', 'Corretor', 'Valor'];
    /* celula que comeca com = + - @ vira formula no Excel: prefixa com ' */
    function q(v) { var s = String(v === undefined || v === null ? '' : v); if (/^[=+\-@\t\r]/.test(s)) s = "'" + s; return /[";\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }
    function br(iso) { return iso ? iso.slice(8, 10) + '/' + iso.slice(5, 7) + '/' + iso.slice(0, 4) : ''; }
    var linhas = filtradas().map(function (v) {
      return [br(v.dataConta), v.pelaConfirmacao ? 'Confirmação 2.0' : 'Data da venda', v.op, v.unidade, v.emp,
        v.tipo === 'comercial' ? 'Comercial' : 'Facilitada', v.virouComercial ? 'Sim' : 'Não', v.fase, br(v.venda), br(v.conf),
        br(v.pcv), v.boleto ? 'Sim' : 'Não', v.cartao ? 'Sim' : 'Não', v.imob, v.corretor,
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

  function reiniciarOps() { estado.verOps = PAGINA_OPS; desenharOps(); }

  function iniciarControles() {
    $('mes').addEventListener('change', function () { carregar(this.value); });
    $('mes-ant').addEventListener('click', function () {
      var s = $('mes'); if (s.selectedIndex < s.options.length - 1) carregar(s.options[s.selectedIndex + 1].value);
    });
    $('mes-prox').addEventListener('click', function () {
      var s = $('mes'); if (s.selectedIndex > 0) carregar(s.options[s.selectedIndex - 1].value);
    });
    $('tentar').addEventListener('click', function () { carregar(estado.mes); });

    Array.prototype.forEach.call(document.querySelectorAll('#matriz .cel'), function (b) {
      b.addEventListener('click', function () {
        estado.filtro.tipo = b.dataset.tipo;
        estado.filtro.conf = b.dataset.conf;
        reiniciarOps();
        $('ops').scrollIntoView({ block: 'start' });
      });
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-chip]'), function (c) {
      c.addEventListener('click', function () {
        var k = c.dataset.chip, f = estado.filtro;
        if (k === 'todas') { f.tipo = ''; f.conf = ''; }
        else if (k === 'comercial' || k === 'facilitada') f.tipo = f.tipo === k ? '' : k;
        else f.conf = f.conf === k ? '' : k;
        reiniciarOps();
      });
    });
    $('f-emp').addEventListener('change', function () { estado.filtro.emp = this.value; reiniciarOps(); });
    $('f-imob').addEventListener('change', function () { estado.filtro.imob = this.value; reiniciarOps(); });
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

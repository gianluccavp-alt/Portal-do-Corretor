/* ============================================================
   VISITAS DA RECEPCAO - interface de /visitas-recepcao-adm
   ------------------------------------------------------------
   Tela de senha + dashboard. Busca os ultimos 30 dias uma vez e
   filtra no navegador. Regras em assets/visitas.js.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md (secao 6)
   ============================================================ */
(function () {
  'use strict';

  var V = window.Visitas;
  var CHAVE_SESSAO = 'visitas.adm.senha';
  var ALTURA_BARRA = 190;
  var PERIODOS = [['hoje', 'Hoje'], ['7', '7 dias'], ['30', '30 dias']];
  var NOME_PERIODO = { hoje: 'Hoje', '7': 'Últimos 7 dias', '30': 'Últimos 30 dias' };
  var EMPS = V.empreendimentosVisitas(window.CITIES || []);
  var PDVS_FILTRO = [['Todos', 'Todos']].concat(V.PDVS.map(function (p) { return [p, p]; }));
  var estado = { senha: '', todas: [], contas: [], senhaTemp: null, aba: 'visitas', periodo: '7', pdv: 'Todos', emp: 'Todos', carregadoEm: null, hoje: V.dataLocalIso(new Date()) };
  var api = window.VisitasAPI.criar({
    url: window.VISITAS_APPS_SCRIPT_URL || '',
    senha: function () { return estado.senha; }
  });

  function $(id) { return document.getElementById(id); }
  function el(tag, cls, texto) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }
  function pct(q, t) { return (t ? Math.round(q / t * 100) : 0) + '%'; }
  function lerSessao() { try { return sessionStorage.getItem(CHAVE_SESSAO) || ''; } catch (e) { return ''; } }
  function gravarSessao(s) {
    try { if (s) sessionStorage.setItem(CHAVE_SESSAO, s); else sessionStorage.removeItem(CHAVE_SESSAO); } catch (e) { /* ignora */ }
  }

  /* ---------- senha / sessao (spec 6.1) ---------- */
  function mostrarGate(msg) {
    $('app').hidden = true;
    $('gate').hidden = false;
    $('gate-demo').hidden = !api.demo;
    $('gate-erro').textContent = msg || '';
    $('gate-erro').hidden = !msg;
    $('gate-senha').setAttribute('aria-invalid', msg ? 'true' : 'false');
    $('gate-senha').value = '';
    $('gate-entrar').disabled = false;
    $('gate-entrar').textContent = 'Entrar';
    $('gate-senha').focus();
  }
  function mostrarApp() {
    $('gate').hidden = true;
    $('app').hidden = false;
    $('aviso-demo').hidden = !api.demo;
  }
  function sair(msg) {
    gravarSessao('');
    estado.senha = '';
    estado.todas = [];
    estado.contas = [];
    estado.senhaTemp = null;
    mostrarAba('visitas');
    mostrarGate(msg);
  }

  /* ---------- dados ---------- */
  function buscar() {
    estado.hoje = V.dataLocalIso(new Date());
    $('atualizar').disabled = true;
    return api.chamar('listar', { de: V.somarDias(estado.hoje, -29), ate: estado.hoje }).then(function (r) {
      estado.todas = (r.visitas || []).filter(function (v) { return V.TIPOS[v.tipo]; });
      estado.carregadoEm = new Date();
      $('aviso-erro').hidden = true;
      render();
    }).finally(function () { $('atualizar').disabled = false; });
  }
  var MSG_ERRO = 'Erro na planilha de visitas. Avise o comercial.';
  function tratarErro(f) {
    if (f && f.codigo === 'senha') { sair('Senha incorreta.'); return; }
    $('aviso-erro-txt').textContent = (f && f.mensagem) || MSG_ERRO;
    $('aviso-erro').hidden = false;
  }
  function entrar(ev) {
    ev.preventDefault();
    var s = $('gate-senha').value;
    if (!s) { mostrarGate('Digite a senha.'); return; }
    $('gate-entrar').disabled = true;
    $('gate-entrar').textContent = 'Entrando…';
    estado.senha = s;
    buscar().then(function () {
      gravarSessao(s);
      mostrarApp();
      carregarContas().catch(tratarErro);
    }, function (f) {
      estado.senha = '';
      mostrarGate(f && f.codigo === 'senha' ? 'Senha incorreta.' : (f && f.mensagem) || MSG_ERRO);
    });
  }

  /* ---------- filtros ---------- */
  function montarChips(caixa, itens, aoEscolher) {
    itens.forEach(function (it) {
      var b = el('button', 'fchip', it[1]);
      b.type = 'button';
      b.setAttribute('data-v', it[0]);
      b.setAttribute('aria-pressed', 'false');
      b.addEventListener('click', function () { aoEscolher(it[0]); });
      caixa.appendChild(b);
    });
  }
  function marcarChips(caixa, valor) {
    Array.prototype.forEach.call(caixa.children, function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-v') === valor ? 'true' : 'false');
    });
  }
  function montarSelectEmp() {
    var sel = $('f-emp');
    sel.textContent = '';
    var todos = el('option', '', 'Todos os empreendimentos');
    todos.value = 'Todos';
    sel.appendChild(todos);
    EMPS.forEach(function (e) {
      var o = el('option', '', e.nome);
      o.value = e.nome;
      sel.appendChild(o);
    });
    sel.value = estado.emp;
  }
  function filtroAtual() {
    var iv = V.intervalo(estado.periodo, estado.hoje);
    return {
      iv: iv,
      visitas: V.filtrar(estado.todas, { de: iv.de, ate: iv.ate, pdv: estado.pdv, empreendimento: estado.emp }),
      lista: EMPS.filter(function (e) { return estado.emp === 'Todos' || e.nome === estado.emp; })
    };
  }

  /* ---------- render (spec 6.2) ---------- */
  function render() {
    marcarChips($('periodos'), estado.periodo);
    marcarChips($('pdvs'), estado.pdv);
    var f = filtroAtual(), iv = f.iv, t = V.totaisPorTipo(f.visitas);
    var rotulo = estado.periodo === 'hoje'
      ? 'Hoje, ' + V.dataCurta(iv.ate)
      : NOME_PERIODO[estado.periodo] + ' · ' + V.dataCurta(iv.de) + ' a ' + V.dataCurta(iv.ate);

    $('k-total').textContent = t.total;
    $('k-total-lab').textContent = rotulo;
    $('t-emps-lab').textContent = rotulo;
    V.ORDEM_TIPOS.forEach(function (k) {
      $('k-' + k).textContent = t[k];
      $('k-' + k + '-pct').textContent = pct(t[k], t.total) + ' do total';
      $('o-' + k).style.width = (t.total ? t[k] / t.total * 100 : 0) + '%';
      $('ol-' + k).textContent = pct(t[k], t.total) + ' · ' + t[k];
    });
    $('k-media').textContent = (t.total / iv.dias).toFixed(1).replace('.', ',');
    $('k-media-lab').textContent = estado.periodo === 'hoje' ? 'dia em andamento' : 'em ' + iv.dias + ' dias';

    renderGrafico(f.visitas, iv);
    renderRanking(V.rankingImobiliarias(f.visitas, 5));
    renderTabelaEmps(V.porEmpreendimento(f.visitas, f.lista));
    renderRecentes(V.recentes(f.visitas, 8));
    $('atualizado-em').textContent = estado.carregadoEm ? 'Atualizado às ' + V.horaLocal(estado.carregadoEm) : '';
  }

  function renderGrafico(visitas, iv) {
    var porHora = estado.periodo === 'hoje';
    var cols = porHora ? V.porHora(visitas, 8, 20) : V.porDia(visitas, iv.de, iv.ate);
    var max = Math.max.apply(null, cols.map(function (c) { return c.total; }).concat([1]));
    var g = $('grafico'), r = $('grafico-rotulos');
    var titulo = porHora ? 'Visitas por horário · hoje' : 'Visitas por dia';
    $('grafico-titulo').textContent = titulo;
    g.setAttribute('aria-label', titulo + ': ' + visitas.length + ' visitas');
    g.textContent = '';
    r.textContent = '';
    cols.forEach(function (c, i) {
      var nome = porHora ? c.hora + 'h' : V.rotuloDia(c.data);
      var rotulo = porHora ? c.hora + 'h'
        : iv.dias <= 7 ? V.rotuloDia(c.data)
          : (cols.length - 1 - i) % 5 === 0 ? V.dataCurta(c.data) : '';
      var col = el('div', 'col');
      col.title = nome + ' · ' + c.total + ' visitas (' + c.esp + ' espontâneas, ' + c.house + ' house, ' + c.imob + ' imobiliária)';
      col.appendChild(el('span', 'col-val num', (porHora || iv.dias <= 7) && c.total ? String(c.total) : ''));
      var pilha = el('div', 'pilha');
      ['imob', 'house', 'esp'].forEach(function (k) {
        var s = el('div');
        s.style.height = Math.round(c[k] / max * ALTURA_BARRA) + 'px';
        s.style.background = V.TIPOS[k].cor;
        pilha.appendChild(s);
      });
      col.appendChild(pilha);
      g.appendChild(col);
      r.appendChild(el('span', 'rot num', rotulo));
    });
    $('grafico-area').hidden = visitas.length === 0;
    $('grafico-vazio').hidden = visitas.length > 0;
  }

  function renderRanking(lista) {
    var ol = $('ranking');
    ol.textContent = '';
    if (!lista.length) { ol.appendChild(el('li', 'dica', 'Nenhuma visita de imobiliária no período.')); return; }
    var max = lista[0].qtd;
    lista.forEach(function (it) {
      var li = el('li');
      var topo = el('div', 'leg-linha');
      topo.appendChild(el('span', '', it.nome));
      topo.appendChild(el('strong', 'num', String(it.qtd)));
      var trilho = el('div', 'rank-trilho');
      var barra = el('div');
      barra.style.width = (it.qtd / max * 100) + '%';
      trilho.appendChild(barra);
      li.appendChild(topo);
      li.appendChild(trilho);
      ol.appendChild(li);
    });
  }

  function celula(tr, texto, cls) { var td = el('td', cls, texto); tr.appendChild(td); return td; }

  function renderTabelaEmps(linhas) {
    var tb = $('tab-emps');
    tb.textContent = '';
    linhas.forEach(function (l) {
      var tr = el('tr');
      celula(tr, l.nome, 'forte');
      celula(tr, l.cidade, 'suave');
      celula(tr, String(l.total), 'dir forte num');
      celula(tr, String(l.esp), 'dir num');
      celula(tr, String(l.house), 'dir num');
      celula(tr, String(l.imob), 'dir num');
      var td = celula(tr, '');
      var mix = el('div', 'mix mix-p');
      V.ORDEM_TIPOS.forEach(function (k) {
        var s = el('div');
        s.style.width = (l.total ? l[k] / l.total * 100 : 0) + '%';
        s.style.background = V.TIPOS[k].cor;
        mix.appendChild(s);
      });
      td.appendChild(mix);
      tb.appendChild(tr);
    });
  }

  function renderRecentes(lista) {
    var tb = $('tab-recentes');
    tb.textContent = '';
    lista.forEach(function (v) {
      var tr = el('tr');
      celula(tr, V.dataCurta(v.data), 'num');
      celula(tr, v.hora, 'forte num');
      celula(tr, v.pdv || '—');
      celula(tr, v.cliente, 'forte');
      celula(tr, V.formatarCpf(v.cpf), 'num');
      celula(tr, V.formatarTelefone(v.telefone), 'num');
      celula(tr, v.empreendimento);
      var td = celula(tr, '');
      var badge = el('span', 'badge');
      var ponto = el('span', 'ponto');
      ponto.style.background = V.TIPOS[v.tipo].cor;
      badge.appendChild(ponto);
      badge.appendChild(document.createTextNode(V.TIPOS[v.tipo].nome));
      td.appendChild(badge);
      celula(tr, v.imobiliaria || '—', 'suave');
      celula(tr, v.corretor || '—');
      celula(tr, v.gerente || '—', 'suave');
      celula(tr, v.lancadoPor || '—', 'suave');
      tb.appendChild(tr);
    });
    $('sem-recentes').hidden = lista.length > 0;
  }

  function exportar() {
    var f = filtroAtual();
    var blob = new Blob([V.gerarCSV(f.visitas)], { type: 'text/csv;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = V.nomeArquivoCSV(f.iv.de, f.iv.ate);
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  /* ---------- abas (spec 14.6) ---------- */
  function mostrarAba(aba) {
    estado.aba = aba;
    $('aba-visitas').hidden = aba !== 'visitas';
    $('aba-recep').hidden = aba !== 'recep';
    $('aba-btn-visitas').setAttribute('aria-current', aba === 'visitas' ? 'page' : 'false');
    $('aba-btn-recep').setAttribute('aria-current', aba === 'recep' ? 'page' : 'false');
    estado.senhaTemp = null;
    $('faixa-senha').hidden = true;
    if (aba === 'recep' && estado.senha) carregarContas().catch(tratarErro);
  }

  /* ---------- recepcionistas (spec 14.6) ---------- */
  function curtoBr(s) {
    var m = /^(\d{2})\/(\d{2})\/\d{4} (\d{2}:\d{2})/.exec(String(s || ''));
    return m ? m[1] + '/' + m[2] + ' ' + m[3] : '—';
  }
  function carregarContas() {
    $('atualizar-contas').disabled = true;
    return api.chamar('contas', {}).then(function (r) {
      estado.contas = r.contas || [];
      $('aviso-erro').hidden = true;
      renderContas();
    }).finally(function () { $('atualizar-contas').disabled = false; });
  }
  function acaoConta(acao, c, pergunta, btn) {
    if (pergunta && !window.confirm(pergunta)) return;
    estado.senhaTemp = null;
    $('faixa-senha').hidden = true;
    var botoes = btn && btn.parentNode ? btn.parentNode.querySelectorAll('button') : [];
    var travar = function (v) { Array.prototype.forEach.call(botoes, function (b) { b.disabled = v; }); };
    travar(true);
    api.chamar(acao, { usuario: c.usuario }).then(function (r) {
      if (acao === 'redefinirSenha') estado.senhaTemp = { nome: c.nome, valor: r.senhaTemporaria };
      return carregarContas().catch(tratarErro);
    }, function (f) {
      tratarErro(f);
      /* estado pode ter mudado no servidor: recarrega a lista */
      if (!(f && f.codigo === 'senha')) return carregarContas().catch(tratarErro);
    }).then(function () { travar(false); });
  }
  function botao(texto, cls, fn) {
    var b = el('button', cls, texto);
    b.type = 'button';
    b.addEventListener('click', function () { fn(b); });
    return b;
  }
  function renderContas() {
    var pend = estado.contas.filter(function (c) { return c.situacao === 'pendente'; });
    var outras = estado.contas.filter(function (c) { return c.situacao !== 'pendente'; });
    $('selo-pendentes').textContent = String(pend.length);
    $('selo-pendentes').hidden = pend.length === 0;
    $('bloco-pendentes').hidden = pend.length === 0;
    var ul = $('lista-pendentes');
    ul.textContent = '';
    pend.forEach(function (c) {
      var li = el('li');
      var txt = el('div', 'pend-txt');
      txt.appendChild(el('strong', '', c.nome));
      txt.appendChild(el('span', 'dica', c.usuario + ' · cadastro em ' + curtoBr(c.criadoEm)));
      li.appendChild(txt);
      li.appendChild(botao('Recusar', 'btn', function (b) { acaoConta('recusar', c, 'Recusar o cadastro de ' + c.nome + '?', b); }));
      li.appendChild(botao('Aprovar', 'btn btn-p', function (b) { acaoConta('aprovar', c, null, b); }));
      ul.appendChild(li);
    });
    var tb = $('tab-contas');
    tb.textContent = '';
    outras.forEach(function (c) {
      var tr = el('tr');
      celula(tr, c.nome, 'forte');
      celula(tr, c.usuario, 'suave');
      var td = celula(tr, '');
      td.appendChild(el('span', 'badge ' + (c.situacao === 'ativa' ? 'badge-ok' : 'badge-off'), c.situacao === 'ativa' ? 'Ativa' : 'Desativada'));
      if (c.temporaria) td.appendChild(el('span', 'badge badge-temp', 'Senha temporária'));
      celula(tr, String(c.visitas30 || 0), 'dir num');
      celula(tr, curtoBr(c.ultimoAcesso), 'suave');
      var acoes = celula(tr, '', 'dir acoes-conta');
      acoes.appendChild(botao('Redefinir senha', 'btn', function (b) {
        acaoConta('redefinirSenha', c, 'Gerar uma senha temporária para ' + c.nome + '? A senha atual deixa de funcionar.', b);
      }));
      if (c.situacao === 'ativa') {
        acoes.appendChild(botao('Desativar', 'btn', function (b) { acaoConta('desativar', c, 'Desativar o acesso de ' + c.nome + '?', b); }));
      } else {
        acoes.appendChild(botao('Reativar', 'btn', function (b) { acaoConta('reativar', c, null, b); }));
      }
      tb.appendChild(tr);
    });
    $('sem-contas').hidden = outras.length > 0;
    $('faixa-senha').hidden = !estado.senhaTemp;
    if (estado.senhaTemp) {
      $('senha-nome').textContent = estado.senhaTemp.nome;
      $('senha-temp').textContent = estado.senhaTemp.valor;
    }
  }

  /* ---------- inicio ---------- */
  function iniciar() {
    montarChips($('periodos'), PERIODOS, function (v) { estado.periodo = v; render(); });
    montarChips($('pdvs'), PDVS_FILTRO, function (v) { estado.pdv = v; render(); });
    montarSelectEmp();
    $('f-emp').addEventListener('change', function () { estado.emp = $('f-emp').value; render(); });
    $('gate-form').addEventListener('submit', entrar);
    $('atualizar').addEventListener('click', function () { buscar().catch(tratarErro); });
    $('aviso-erro-tentar').addEventListener('click', function () {
      (estado.aba === 'recep' ? carregarContas() : buscar()).catch(tratarErro);
    });
    $('exportar').addEventListener('click', exportar);
    $('sair').addEventListener('click', function () { sair(); });
    $('aba-btn-visitas').addEventListener('click', function () { mostrarAba('visitas'); });
    $('aba-btn-recep').addEventListener('click', function () { mostrarAba('recep'); });
    $('atualizar-contas').addEventListener('click', function () { carregarContas().catch(tratarErro); });

    var salva = lerSessao();
    if (salva) {
      estado.senha = salva;
      mostrarApp();
      render();
      buscar().catch(tratarErro);
      carregarContas().catch(tratarErro);
    } else {
      mostrarGate();
    }
  }

  iniciar();
})();

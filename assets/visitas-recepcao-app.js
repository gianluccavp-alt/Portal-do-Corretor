/* ============================================================
   VISITAS DA RECEPCAO - interface de /visitas-recepcao
   ------------------------------------------------------------
   Acesso (entrar, criar conta, trocar senha temporaria), PDV
   (Passo 1), cards que abrem o popup de cadastro (Passo 2) e
   contador do dia por PDV. Regras em assets/visitas.js; API em
   assets/visitas-api.js.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md (secoes 13 e 14)
   ============================================================ */
(function () {
  'use strict';

  var V = window.Visitas;
  var CHAVE_SESSAO = 'visitas.sessao';
  var CHAVE_PDV = 'visitas.pdv';
  var CHAVES_ANTIGAS = ['visitas.emp', 'visitas.tokens'];
  var INTERVALO_DIA = 60000;
  var MSG_SESSAO = 'Sua sessão terminou. Entre de novo.';
  var EMPS = V.empreendimentosVisitas(window.CITIES || []);
  var TITULO_TIPO = { esp: 'Espontânea', house: 'Agendada · Corretor house', imob: 'Imobiliária parceira' };
  var ROTULO_CORRETOR = { esp: 'Corretor que atendeu', house: 'Corretor house que agendou', imob: 'Corretor da imobiliária' };
  var SUB = {
    acesso: 'Acesso exclusivo das recepcionistas dos stands.',
    app: 'Escolha o PDV e toque no tipo de visita para registrar o cliente.'
  };
  /* campo da API -> id do input */
  var CAMPOS = {
    empreendimento: 'f-emp', cliente: 'f-cliente', cpf: 'f-cpf', telefone: 'f-telefone', data: 'f-data',
    hora: 'f-hora', imobiliaria: 'f-imob', corretor: 'f-corretor'
  };
  var CAMPOS_CADASTRO = { nome: 'c-nome', usuario: 'c-usuario', senha: 'c-senha', confirmacao: 'c-confirmacao' };
  var TELAS = ['entrar', 'cadastro', 'enviado', 'troca'];
  var FOCO_TELA = { entrar: 'a-usuario', cadastro: 'c-nome', enviado: 'enviado-voltar', troca: 'n-senha' };
  var estado = {
    sessao: null, pdv: '', tipo: null, enviando: false, ultimo: null, timerFaixa: null, seqDia: 0, hojeAplicado: ''
  };
  var api = window.VisitasAPI.criar({
    url: window.VISITAS_APPS_SCRIPT_URL || '',
    sessao: function () { return estado.sessao ? estado.sessao.token : ''; }
  });

  function $(id) { return document.getElementById(id); }
  function hoje() { return V.dataLocalIso(new Date()); }
  function lerLS(chave, padrao) {
    try { var v = localStorage.getItem(chave); return v === null ? padrao : JSON.parse(v); } catch (e) { return padrao; }
  }
  function gravarLS(chave, valor) {
    try { localStorage.setItem(chave, JSON.stringify(valor)); } catch (e) { /* ignora */ }
  }
  function apagarLS(chave) {
    try { localStorage.removeItem(chave); } catch (e) { /* ignora */ }
  }
  function cada(seletor, fn) { Array.prototype.forEach.call(document.querySelectorAll(seletor), fn); }

  /* ---------- erros de campo ---------- */
  function limparErro(id) {
    $(id).setAttribute('aria-invalid', 'false');
    $('e-' + id).textContent = '';
    $('e-' + id).hidden = true;
  }
  function marcarErro(id, msg) {
    $(id).setAttribute('aria-invalid', 'true');
    $('e-' + id).textContent = msg;
    $('e-' + id).hidden = false;
  }
  function ocupado(id, sim, texto) {
    $(id).disabled = sim;
    $(id).textContent = texto;
  }

  /* ---------- sessao (spec 14.2) ---------- */
  function guardarSessao(r) {
    estado.sessao = { token: r.sessao, expira: r.expira, nome: r.nome, usuario: r.usuario, trocar: !!r.trocarSenha };
    gravarLS(CHAVE_SESSAO, estado.sessao);
  }
  function encerrar(msg) {
    estado.sessao = null;
    estado.enviando = false;
    apagarLS(CHAVE_SESSAO);
    if ($('popup').open) $('popup').close();
    esconderFaixa();
    mostrarAcesso('entrar', msg ? { tipo: 'err', texto: msg } : null);
  }
  /* qualquer 'sessao' do servidor volta para o login */
  function tratarSessao(f) {
    if (f && f.codigo === 'sessao') { encerrar(MSG_SESSAO); return true; }
    return false;
  }

  /* ---------- telas de acesso ---------- */
  function mostrarMsg(msg) {
    $('a-msg').className = 'msg ' + (msg ? msg.tipo : '');
    $('a-msg').textContent = msg ? msg.texto : '';
    $('a-msg').hidden = !msg;
  }
  function mostrarAcesso(tela, msg) {
    $('app').hidden = true;
    $('hero-user').hidden = true;
    $('acesso').hidden = false;
    $('acesso-demo').hidden = !api.demo;
    $('hero-sub').textContent = SUB.acesso;
    TELAS.forEach(function (t) { $('t-' + t).hidden = t !== tela; });
    mostrarMsg(msg || null);
    $(FOCO_TELA[tela]).focus();
  }
  function mostrarApp() {
    $('acesso').hidden = true;
    $('app').hidden = false;
    $('hero-user').hidden = false;
    $('hero-sub').textContent = SUB.app;
    $('ola').textContent = V.primeiroNome(estado.sessao.nome) || estado.sessao.usuario;
    $('aviso-demo').hidden = !api.demo;
    estado.hojeAplicado = hoje();
    renderPdv();
    carregarDia();
  }

  function entrar(ev) {
    ev.preventDefault();
    var usuario = V.normalizarUsuario($('a-usuario').value), senha = $('a-senha').value;
    if (!usuario || !senha) { mostrarMsg({ tipo: 'err', texto: 'Informe usuário e senha.' }); return; }
    ocupado('a-entrar', true, 'Entrando…');
    api.chamar('entrar', { usuario: usuario, senha: senha }).then(function (r) {
      $('a-senha').value = '';
      guardarSessao(r);
      if (r.trocarSenha) mostrarAcesso('troca'); else mostrarApp();
    }, function (f) {
      $('a-senha').value = '';
      mostrarMsg({ tipo: f.codigo === 'pendente' ? 'aviso' : 'err', texto: f.mensagem });
      $('a-senha').focus();
    }).then(function () { ocupado('a-entrar', false, 'Entrar'); });
  }

  function cadastrar(ev) {
    ev.preventDefault();
    var d = { nome: $('c-nome').value, usuario: $('c-usuario').value, senha: $('c-senha').value, confirmacao: $('c-confirmacao').value };
    var r = V.validarCadastro(d);
    Object.keys(CAMPOS_CADASTRO).forEach(function (c) { limparErro(CAMPOS_CADASTRO[c]); });
    $('c-erro').hidden = true;
    if (!r.ok) {
      Object.keys(r.erros).forEach(function (c) { marcarErro(CAMPOS_CADASTRO[c], r.erros[c]); });
      $(CAMPOS_CADASTRO[r.primeiro]).focus();
      return;
    }
    var usuario = V.normalizarUsuario(d.usuario);
    ocupado('c-enviar', true, 'Enviando…');
    api.chamar('cadastrar', { nome: d.nome, usuario: usuario, senha: d.senha }).then(function () {
      ['c-nome', 'c-usuario', 'c-senha', 'c-confirmacao'].forEach(function (id) { $(id).value = ''; });
      $('enviado-usuario').textContent = usuario;
      mostrarAcesso('enviado');
    }, function (f) {
      var id = f.codigo === 'invalido' && CAMPOS_CADASTRO[f.campo];
      if (id) { marcarErro(id, f.mensagem); $(id).focus(); return; }
      $('c-erro').textContent = f.mensagem;
      $('c-erro').hidden = false;
    }).then(function () { ocupado('c-enviar', false, 'Enviar cadastro'); });
  }

  function trocarSenha(ev) {
    ev.preventDefault();
    var nova = $('n-senha').value, conf = $('n-confirmacao').value;
    limparErro('n-senha');
    limparErro('n-confirmacao');
    $('n-erro').hidden = true;
    var msg = V.validarSenha(nova, estado.sessao ? estado.sessao.usuario : '');
    if (msg) { marcarErro('n-senha', msg); $('n-senha').focus(); return; }
    if (nova !== conf) { marcarErro('n-confirmacao', 'As senhas não conferem.'); $('n-confirmacao').focus(); return; }
    ocupado('n-salvar', true, 'Salvando…');
    api.chamar('trocarSenha', { novaSenha: nova }).then(function (r) {
      $('n-senha').value = '';
      $('n-confirmacao').value = '';
      guardarSessao(r);
      mostrarApp();
    }, function (f) {
      if (tratarSessao(f)) return;
      if (f.codigo === 'invalido') { marcarErro('n-senha', f.mensagem); $('n-senha').focus(); return; }
      $('n-erro').textContent = f.mensagem;
      $('n-erro').hidden = false;
    }).then(function () { ocupado('n-salvar', false, 'Salvar e continuar'); });
  }

  /* ---------- PDV (spec 14.3) ---------- */
  function renderPdv() {
    cada('.pdv', function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-pdv') === estado.pdv ? 'true' : 'false'); });
    cada('.tipo', function (b) { b.disabled = !estado.pdv; });
    $('tipo-dica').textContent = estado.pdv ? 'Toque no tipo para abrir o cadastro da visita.' : 'Escolha o PDV primeiro.';
  }
  function escolherPdv(pdv) {
    if (estado.enviando || pdv === estado.pdv) return;
    estado.pdv = pdv;
    gravarLS(CHAVE_PDV, pdv);
    esconderFaixa();
    renderPdv();
    carregarDia();
  }
  function montarEmpreendimentos() {
    var sel = $('f-emp');
    var vazio = document.createElement('option');
    vazio.value = '';
    vazio.textContent = 'Selecione';
    sel.appendChild(vazio);
    EMPS.forEach(function (e) {
      var o = document.createElement('option');
      o.value = e.nome;
      o.textContent = e.nome;
      sel.appendChild(o);
    });
  }

  /* ---------- popup (spec 13.1 e 14.3) ---------- */
  function limparErros() {
    Object.keys(CAMPOS).forEach(function (c) { limparErro(CAMPOS[c]); });
    $('p-erro').hidden = true;
  }
  function mostrarErro(campo, msg) {
    if (!CAMPOS[campo]) return false;
    marcarErro(CAMPOS[campo], msg);
    return true;
  }
  function atualizarBotao() {
    $('p-registrar').disabled = estado.enviando;
    /* enviando: nao deixa fechar o popup nem perder a resposta */
    $('p-cancelar').disabled = estado.enviando;
    $('p-fechar').disabled = estado.enviando;
    $('p-registrar-txt').textContent = estado.enviando ? 'Registrando…' : 'Registrar visita';
  }
  function aplicarLimitesData(h) {
    $('f-data').max = h;
    $('f-data').min = V.somarDias(h, -7);
  }

  function abrirPopup(tipo) {
    if (estado.enviando || !estado.pdv) return;
    estado.tipo = tipo;
    $('p-tipo').textContent = TITULO_TIPO[tipo];
    $('p-ponto').style.background = V.TIPOS[tipo].cor;
    $('p-pdv').textContent = 'PDV ' + estado.pdv;
    $('rot-corretor').textContent = ROTULO_CORRETOR[tipo];
    $('bloco-imob').hidden = tipo !== 'imob';
    ['f-emp', 'f-cliente', 'f-cpf', 'f-telefone', 'f-imob', 'f-corretor', 'f-gerente'].forEach(function (id) { $(id).value = ''; });
    var h = hoje();
    aplicarLimitesData(h);
    $('f-data').value = h;
    $('f-hora').value = V.horaLocal(new Date());
    limparErros();
    atualizarBotao();
    $('popup').showModal();
    $('f-emp').focus();
  }
  function fecharPopup() {
    if (estado.enviando) return;
    if ($('popup').open) $('popup').close();
  }

  function lerPopup() {
    return {
      pdv: estado.pdv, empreendimento: $('f-emp').value, tipo: estado.tipo,
      cliente: $('f-cliente').value, cpf: $('f-cpf').value, telefone: $('f-telefone').value,
      data: $('f-data').value, hora: $('f-hora').value,
      imobiliaria: estado.tipo === 'imob' ? $('f-imob').value : '',
      corretor: $('f-corretor').value, gerente: $('f-gerente').value
    };
  }

  function registrar(ev) {
    if (ev) ev.preventDefault();
    if (estado.enviando) return;
    var dados = lerPopup();
    var r = V.validarVisita(dados);
    limparErros();
    if (!r.ok) {
      Object.keys(r.erros).forEach(function (c) {
        /* campo sem input no popup (ex: pdv) vai para a mensagem geral */
        if (!mostrarErro(c, r.erros[c])) { $('p-erro').textContent = r.erros[c]; $('p-erro').hidden = false; }
      });
      if (CAMPOS[r.primeiro]) $(CAMPOS[r.primeiro]).focus();
      return;
    }
    estado.enviando = true;
    atualizarBotao();
    api.chamar('registrar', dados).then(function (resp) {
      estado.enviando = false;
      atualizarBotao();
      fecharPopup();
      var texto = [resp.visita.hora, V.TIPOS[resp.visita.tipo].nome, resp.visita.primeiroNome].join(' · ');
      if (resp.cpfRepetido) {
        mostrarFaixa('aviso', 'Visita registrada. Atenção: este CPF já tinha visita hoje neste PDV.', texto, true);
      } else {
        mostrarFaixa('ok', 'Visita registrada', texto, true);
      }
      estado.ultimo = resp.visita;
      carregarDia();
    }, function (f) {
      if (tratarSessao(f)) return;
      if (f.codigo === 'invalido' && mostrarErro(f.campo, f.mensagem)) {
        $(CAMPOS[f.campo]).focus();
      } else {
        $('p-erro').textContent = f.mensagem;
        $('p-erro').hidden = false;
      }
    }).then(function () {
      estado.enviando = false;
      if ($('popup').open) atualizarBotao();
    });
  }

  /* ---------- faixa de retorno (spec 5.2 e 13.1) ---------- */
  function mostrarFaixa(tipo, titulo, texto, comDesfazer) {
    clearTimeout(estado.timerFaixa);
    $('faixa').className = 'faixa ' + tipo;
    $('faixa-ico-ok').style.display = tipo === 'ok' ? '' : 'none';
    $('faixa-ico-err').style.display = tipo === 'ok' ? 'none' : '';
    $('faixa-titulo').textContent = titulo;
    $('faixa-texto').textContent = texto;
    $('faixa-desfazer').hidden = !comDesfazer;
    $('faixa').hidden = false;
    /* no celular a faixa fica no topo: traz para a tela */
    try { $('faixa').scrollIntoView({ block: 'nearest', behavior: 'smooth' }); } catch (e) { /* navegador antigo */ }
    if (tipo === 'ok') estado.timerFaixa = setTimeout(esconderFaixa, 8000);
  }
  function esconderFaixa() {
    clearTimeout(estado.timerFaixa);
    $('faixa').hidden = true;
    estado.ultimo = null;
  }

  /* spec 14.3: so a propria visita, registrada hoje (o servidor confere) */
  function excluir(id) {
    return api.chamar('excluir', { id: id }).then(null, function (f) {
      if (tratarSessao(f)) return;
      mostrarFaixa('err', 'Não foi possível excluir este lançamento',
        f.codigo === 'nao_encontrada' ? 'Ele pode já ter sido excluído.' : f.mensagem, false);
    }).then(function () { if (estado.sessao) carregarDia(); });
  }
  function desfazer() {
    var v = estado.ultimo;
    if (!v) return;
    esconderFaixa();
    excluir(v.id);
  }

  /* ---------- contador do dia por PDV (spec 5.3 e 14.3) ---------- */
  function carregarDia() {
    if (!estado.sessao || !estado.pdv) { renderContador([], estado.pdv, hoje()); return; }
    var pdv = estado.pdv, data = hoje();
    var seq = ++estado.seqDia;
    api.chamar('dia', { pdv: pdv, data: data }).then(function (r) {
      if (seq !== estado.seqDia) return;
      var visitas = (r.visitas || []).filter(function (v) { return V.TIPOS[v.tipo]; });
      renderContador(visitas, pdv, data);
      renderSugestoes(r.sugestoes || {});
      $('cont-erro').hidden = true;
    }, function (f) {
      if (seq !== estado.seqDia || tratarSessao(f)) return;
      $('cont-erro').textContent = f.mensagem;
      $('cont-erro').hidden = false;
    });
  }

  function renderContador(visitas, pdv, data) {
    var t = V.totaisPorTipo(visitas);
    $('cont-titulo').textContent = 'Visitas hoje · ' + V.dataCurta(data);
    $('cont-emp').textContent = pdv ? 'PDV ' + pdv : 'Escolha o PDV';
    $('cont-total').textContent = t.total;
    $('cont-total-lab').textContent = t.total === 1 ? 'visita registrada' : 'visitas registradas';
    V.ORDEM_TIPOS.forEach(function (k) {
      $('q-' + k).textContent = t[k];
      $('b-' + k).style.width = (t.total ? Math.round(t[k] / t.total * 100) : 0) + '%';
    });
    var ul = $('ultimos');
    ul.textContent = '';
    V.recentes(visitas, 6).forEach(function (v) { ul.appendChild(itemLista(v, !!v.minha)); });
    $('vazio').textContent = pdv ? 'Nenhuma visita registrada hoje neste PDV.' : 'Escolha o PDV para ver as visitas do dia.';
    $('vazio').hidden = visitas.length > 0;
  }

  function el(tag, cls, texto) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }

  function iconeLixeira() {
    var ns = 'http://www.w3.org/2000/svg', s = document.createElementNS(ns, 'svg');
    [['width', '18'], ['height', '18'], ['viewBox', '0 0 24 24'], ['fill', 'none'], ['stroke', 'currentColor'],
      ['stroke-width', '1.8'], ['stroke-linecap', 'round'], ['stroke-linejoin', 'round'], ['aria-hidden', 'true']]
      .forEach(function (a) { s.setAttribute(a[0], a[1]); });
    var p = document.createElementNS(ns, 'path');
    p.setAttribute('d', 'M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3');
    s.appendChild(p);
    return s;
  }

  function itemLista(v, podeExcluir) {
    var li = el('li');
    var txt = el('span', 'lista-txt');
    var tipo = el('span', 'lista-tipo');
    var ponto = el('span', 'ponto');
    ponto.style.background = V.TIPOS[v.tipo].cor;
    tipo.appendChild(ponto);
    tipo.appendChild(document.createTextNode((v.primeiroNome ? v.primeiroNome + ' · ' : '') + V.TIPOS[v.tipo].nome));
    txt.appendChild(tipo);
    txt.appendChild(el('span', 'lista-det', (v.empreendimento ? v.empreendimento + ' · ' : '') + V.detalhe(v)));
    li.appendChild(el('span', 'lista-hora num', v.hora));
    li.appendChild(txt);
    if (podeExcluir) {
      var b = el('button', 'btn btn-i');
      b.type = 'button';
      b.setAttribute('aria-label', 'Excluir lançamento das ' + v.hora);
      b.appendChild(iconeLixeira());
      b.addEventListener('click', function () {
        if (!window.confirm('Excluir o lançamento das ' + v.hora + ' (' + V.TIPOS[v.tipo].nome + ')?')) return;
        b.disabled = true;
        if (estado.ultimo && estado.ultimo.id === v.id) esconderFaixa();
        excluir(v.id);
      });
      li.appendChild(b);
    }
    return li;
  }

  function preencherLista(id, nomes) {
    var dl = $(id);
    dl.textContent = '';
    (nomes || []).forEach(function (n) { var o = document.createElement('option'); o.value = n; dl.appendChild(o); });
  }
  function renderSugestoes(s) {
    preencherLista('lista-imob', s.imobiliarias);
    preencherLista('lista-corretor', s.corretores);
    preencherLista('lista-gerente', s.gerentes);
  }

  /* ---------- virada do dia e fim da sessao ---------- */
  /* tablet aberto de um dia pro outro: a sessao acaba a meia-noite */
  function checarVirada() {
    if (document.visibilityState !== 'visible' || !estado.sessao) return;
    if (!V.sessaoValida(estado.sessao, Date.now())) { encerrar(MSG_SESSAO); return; }
    var h = hoje();
    if (estado.hojeAplicado && h !== estado.hojeAplicado && $('popup').open) {
      aplicarLimitesData(h);
      if ($('f-data').value === estado.hojeAplicado) {
        $('f-data').value = h;
        $('f-hora').value = V.horaLocal(new Date());
      }
    }
    estado.hojeAplicado = h;
    if (!$('app').hidden) carregarDia();
  }

  /* ---------- inicio ---------- */
  function iniciar() {
    CHAVES_ANTIGAS.forEach(apagarLS);
    montarEmpreendimentos();
    var pdv = lerLS(CHAVE_PDV, '');
    estado.pdv = V.PDVS.indexOf(pdv) >= 0 ? pdv : '';

    $('t-entrar').addEventListener('submit', entrar);
    $('t-cadastro').addEventListener('submit', cadastrar);
    $('t-troca').addEventListener('submit', trocarSenha);
    $('a-ir-cadastro').addEventListener('click', function () { mostrarAcesso('cadastro'); });
    $('c-ir-entrar').addEventListener('click', function () { mostrarAcesso('entrar'); });
    $('enviado-voltar').addEventListener('click', function () { mostrarAcesso('entrar'); });
    $('c-usuario').addEventListener('change', function () { $('c-usuario').value = V.normalizarUsuario($('c-usuario').value); });
    ['c-nome', 'c-usuario', 'c-senha', 'c-confirmacao', 'n-senha', 'n-confirmacao'].forEach(function (id) {
      $(id).addEventListener('input', function () { limparErro(id); });
    });
    $('sair').addEventListener('click', function () { if (!estado.enviando) encerrar(); });

    cada('.pdv', function (b) { b.addEventListener('click', function () { escolherPdv(b.getAttribute('data-pdv')); }); });
    cada('.tipo', function (b) { b.addEventListener('click', function () { abrirPopup(b.getAttribute('data-tipo')); }); });
    $('p-form').addEventListener('submit', registrar);
    $('p-cancelar').addEventListener('click', fecharPopup);
    $('p-fechar').addEventListener('click', fecharPopup);
    $('popup').addEventListener('cancel', function (ev) { if (estado.enviando) ev.preventDefault(); });
    $('popup').addEventListener('close', function () { estado.tipo = null; });
    $('f-agora').addEventListener('click', function () { $('f-hora').value = V.horaLocal(new Date()); limparErro('f-hora'); });
    $('f-cpf').addEventListener('input', function () { $('f-cpf').value = V.mascaraCpf($('f-cpf').value); });
    $('f-telefone').addEventListener('input', function () { $('f-telefone').value = V.mascaraTelefone($('f-telefone').value); });
    /* campo corrigido deixa de ficar marcado como invalido */
    Object.keys(CAMPOS).forEach(function (c) {
      var id = CAMPOS[c];
      $(id).addEventListener('input', function () { limparErro(id); });
      $(id).addEventListener('change', function () { limparErro(id); });
    });
    $('faixa-desfazer').addEventListener('click', desfazer);
    /* soma lancamentos de outro aparelho no mesmo PDV */
    document.addEventListener('visibilitychange', checarVirada);
    setInterval(checarVirada, INTERVALO_DIA);

    var s = lerLS(CHAVE_SESSAO, null);
    if (V.sessaoValida(s, Date.now())) {
      estado.sessao = s;
      if (s.trocar) mostrarAcesso('troca'); else mostrarApp();
    } else {
      apagarLS(CHAVE_SESSAO);
      mostrarAcesso('entrar');
    }
  }

  iniciar();
})();

/* ============================================================
   VISITAS DA RECEPCAO - cliente do Web App
   ------------------------------------------------------------
   POST text/plain (sem preflight de CORS) para o Web App de
   docs/apps-script-visitas.gs. Sem URL configurada (ou com ?demo=1)
   entra em modo demonstracao: tudo fica na memoria da aba.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md
   ============================================================ */
(function (raiz) {
  'use strict';

  var V = raiz.Visitas;
  var TIMEOUT = 20000;
  var MSG_PLANILHA = 'Erro na planilha de visitas. Avise o comercial.';
  var MENSAGENS = {
    rede: 'Sem conexão. Tente de novo.',
    ocupado: 'Muitos lançamentos ao mesmo tempo, tente de novo.',
    coluna: MSG_PLANILHA,
    interno: MSG_PLANILHA,
    formato: MSG_PLANILHA,
    sessao: 'Sua sessão terminou. Entre de novo.'
  };

  function falha(codigo, mensagem, campo) {
    return { codigo: codigo, mensagem: MENSAGENS[codigo] || mensagem || MSG_PLANILHA, campo: campo || null };
  }
  function copia(x) { return JSON.parse(JSON.stringify(x)); }
  function pad(n) { return (n < 10 ? '0' : '') + n; }

  /* ---------- modo demonstracao (spec 14.7) ---------- */
  var IMOBS_DEMO = ['Imobiliária Exemplo A', 'Imobiliária Exemplo B', 'Imobiliária Exemplo C', 'Imobiliária Exemplo D'];
  var CORRETORES_DEMO = ['Corretor Exemplo 1', 'Corretor Exemplo 2', 'Corretor Exemplo 3'];
  var GERENTES_DEMO = ['Gerente Exemplo 1', 'Gerente Exemplo 2'];
  var CLIENTES_DEMO = [
    ['Cliente Exemplo Ana', '52998224725', '19998765432'],
    ['Cliente Exemplo Bruno', '11144477735', '1932458890'],
    ['Cliente Exemplo Carla', '12345678909', '16998112233'],
    ['Cliente Exemplo Diego', '98765432100', '15998765432']
  ];
  var CONTAS_DEMO = [
    { usuario: 'recep.um', nome: 'Recepcionista Exemplo Um', situacao: 'ativa', temporaria: false, criadoEm: '01/09/2026 09:00:00', ultimoAcesso: '' },
    { usuario: 'recep.dois', nome: 'Recepcionista Exemplo Dois', situacao: 'ativa', temporaria: false, criadoEm: '02/09/2026 09:00:00', ultimoAcesso: '' },
    { usuario: 'troca.demo', nome: 'Recepcionista Exemplo Três', situacao: 'ativa', temporaria: true, criadoEm: '03/09/2026 09:00:00', ultimoAcesso: '' },
    { usuario: 'desativada.demo', nome: 'Recepcionista Exemplo Quatro', situacao: 'desativada', temporaria: false, criadoEm: '04/09/2026 09:00:00', ultimoAcesso: '' },
    { usuario: 'pendente.demo', nome: 'Recepcionista Exemplo Cinco', situacao: 'pendente', temporaria: false, criadoEm: '10/10/2026 09:12:00', ultimoAcesso: '' }
  ];
  var LANCADORES_DEMO = ['recep.um', 'recep.dois'];
  var memoria = null;
  var contas = null;

  function rnd(a, b, c) {
    var x = Math.sin(a * 127.1 + b * 311.7 + c * 74.7) * 43758.5453;
    return x - Math.floor(x);
  }
  function escolher(lista, r) { return lista[Math.floor(r * lista.length)]; }
  function agoraBr() {
    var d = new Date();
    return pad(d.getDate()) + '/' + pad(d.getMonth() + 1) + '/' + d.getFullYear() + ' ' + V.horaLocal(d) + ':00';
  }
  function fimDoDia() { var d = new Date(); d.setHours(24, 0, 0, 0); return d.getTime(); }
  function gerarDemo(hoje, emps) {
    var out = [], seq = 0;
    for (var d = 0; d < 30; d++) {
      var data = V.somarDias(hoje, -d);
      emps.forEach(function (e, ei) {
        var n = Math.floor(rnd(ei, d, 1) * 7);
        for (var k = 0; k < n; k++) {
          var r = rnd(ei, d, 10 + k);
          var tipo = r < 0.4 ? 'esp' : r < 0.65 ? 'house' : 'imob';
          var min = 8 * 60 + Math.floor(rnd(ei, d, 30 + k) * 11 * 60);
          var cli = escolher(CLIENTES_DEMO, rnd(ei, d, 70 + k));
          seq++;
          out.push({
            id: 'D' + seq, data: data, hora: pad(Math.floor(min / 60)) + ':' + pad(min % 60),
            pdv: escolher(V.PDVS, rnd(ei, d, 150 + k)),
            empreendimento: e.nome, cidade: e.cidade, tipo: tipo,
            cliente: cli[0], cpf: cli[1], telefone: cli[2],
            imobiliaria: tipo === 'imob' ? escolher(IMOBS_DEMO, rnd(ei, d, 50 + k)) : '',
            corretor: escolher(CORRETORES_DEMO, rnd(ei, d, 90 + k)),
            gerente: rnd(ei, d, 110 + k) < 0.6 ? escolher(GERENTES_DEMO, rnd(ei, d, 130 + k)) : '',
            lancadoPor: escolher(LANCADORES_DEMO, rnd(ei, d, 170 + k))
          });
        }
      });
    }
    return out;
  }
  function memoriaDemo() {
    if (!memoria) memoria = gerarDemo(V.dataLocalIso(new Date()), V.empreendimentosVisitas(raiz.CITIES || []));
    if (!contas) contas = copia(CONTAS_DEMO);
    return memoria;
  }
  function contaDemo(usuario) { return contas.filter(function (c) { return c.usuario === usuario; })[0] || null; }
  function sessaoDemo(token, permitirTemporaria) {
    var m = /^demo\.(.+)$/.exec(token || ''), c = m && contaDemo(m[1]);
    if (!c || c.situacao !== 'ativa' || (c.temporaria && !permitirTemporaria)) throw falha('sessao');
    return c;
  }
  function resultadoSessao(c) {
    return { ok: true, sessao: 'demo.' + c.usuario, expira: fimDoDia(), nome: c.nome, usuario: c.usuario, trocarSenha: !!c.temporaria };
  }
  function contaAdm(usuario, de) {
    var c = contaDemo(V.normalizarUsuario(usuario));
    if (!c || (de && c.situacao !== de)) throw falha('nao_encontrada', 'Recepcionista não encontrada.');
    return c;
  }
  function senhaTempDemo() {
    var a = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789', s = '';
    for (var i = 0; i < 9; i++) { if (i === 3 || i === 6) s += '-'; s += a.charAt(Math.floor(Math.random() * a.length)); }
    return s;
  }

  function chamarDemo(acao, p, token) {
    var lista = memoriaDemo();
    return new Promise(function (ok) { setTimeout(ok, 300); }).then(function () {
      var c, usuario;
      if (acao === 'entrar') {
        usuario = V.normalizarUsuario(p.usuario);
        if (!V.usuarioValido(usuario) || String(p.senha || '').length < 8) throw falha('credenciais', 'Usuário ou senha incorretos.');
        c = contaDemo(usuario);
        if (!c) { c = { usuario: usuario, nome: 'Recepcionista ' + usuario, situacao: 'ativa', temporaria: false, criadoEm: agoraBr(), ultimoAcesso: '' }; contas.push(c); }
        if (c.situacao === 'pendente') throw falha('pendente', 'Seu cadastro está aguardando aprovação do comercial.');
        if (c.situacao !== 'ativa') throw falha('desativada', 'Seu acesso foi desativado. Fale com o comercial.');
        c.ultimoAcesso = agoraBr();
        return resultadoSessao(c);
      }
      if (acao === 'cadastrar') {
        var vc = V.validarCadastro({ nome: p.nome, usuario: p.usuario, senha: p.senha, confirmacao: p.senha });
        if (!vc.ok) throw falha('invalido', vc.erros[vc.primeiro], vc.primeiro);
        usuario = V.normalizarUsuario(p.usuario);
        if (contaDemo(usuario)) throw falha('invalido', 'Esse usuário já existe.', 'usuario');
        contas.push({ usuario: usuario, nome: V.normalizarTexto(p.nome), situacao: 'pendente', temporaria: false, criadoEm: agoraBr(), ultimoAcesso: '' });
        return { ok: true };
      }
      if (acao === 'trocarSenha') {
        c = sessaoDemo(token, true);
        var msg = V.validarSenha(p.novaSenha, c.usuario);
        if (msg) throw falha('invalido', msg, 'novaSenha');
        c.temporaria = false;
        return resultadoSessao(c);
      }
      if (acao === 'registrar') {
        c = sessaoDemo(token, false);
        var f = V.validarVisita(p);
        if (!f.ok) throw falha('invalido', f.erros[f.primeiro], f.primeiro);
        var emp = V.empreendimentosVisitas(raiz.CITIES || []).filter(function (e) { return e.nome === p.empreendimento; })[0];
        if (!emp) throw falha('invalido', 'Escolha o empreendimento.', 'empreendimento');
        var v = {
          id: 'D' + Date.now(), data: p.data, hora: p.hora, pdv: p.pdv, empreendimento: emp.nome, cidade: emp.cidade, tipo: p.tipo,
          cliente: V.normalizarTexto(p.cliente), cpf: V.soDigitos(p.cpf), telefone: V.soDigitos(p.telefone),
          imobiliaria: p.tipo === 'imob' ? V.normalizarTexto(p.imobiliaria) : '',
          corretor: V.normalizarTexto(p.corretor), gerente: V.normalizarTexto(p.gerente), lancadoPor: c.usuario,
          registradoEm: V.dataLocalIso(new Date())
        };
        var repetido = lista.some(function (x) { return x.cpf === v.cpf && x.pdv === v.pdv && x.data === v.data; });
        lista.push(v);
        return { ok: true, visita: V.resumirVisita(v, c.usuario), cpfRepetido: repetido };
      }
      if (acao === 'dia') {
        c = sessaoDemo(token, false);
        return {
          ok: true,
          visitas: lista.filter(function (v) { return v.pdv === p.pdv && v.data === p.data; })
            .map(function (v) { return V.resumirVisita(v, c.usuario); }),
          sugestoes: { imobiliarias: IMOBS_DEMO.slice(), corretores: CORRETORES_DEMO.slice(), gerentes: GERENTES_DEMO.slice() }
        };
      }
      if (acao === 'excluir') {
        c = sessaoDemo(token, false);
        var hoje = V.dataLocalIso(new Date());
        for (var i = 0; i < lista.length; i++) {
          if (lista[i].id === p.id && lista[i].lancadoPor === c.usuario && lista[i].registradoEm === hoje) {
            lista.splice(i, 1);
            return { ok: true, id: p.id };
          }
        }
        throw falha('nao_encontrada', 'Não foi possível excluir este lançamento.');
      }
      /* acoes do comercial: no demo qualquer senha vale */
      if (acao === 'listar') {
        return {
          ok: true,
          visitas: copia(V.filtrar(lista, { de: p.de, ate: p.ate })).map(function (v) {
            var dono = contaDemo(v.lancadoPor);
            v.lancadoPor = dono ? dono.nome : v.lancadoPor;
            delete v.registradoEm;
            return v;
          })
        };
      }
      if (acao === 'contas') {
        var desde = V.somarDias(V.dataLocalIso(new Date()), -29);
        return {
          ok: true,
          contas: contas.map(function (x) {
            var n = lista.filter(function (v) { return v.lancadoPor === x.usuario && v.data >= desde; }).length;
            return { usuario: x.usuario, nome: x.nome, situacao: x.situacao, temporaria: x.temporaria, criadoEm: x.criadoEm, ultimoAcesso: x.ultimoAcesso, visitas30: n };
          })
        };
      }
      if (acao === 'aprovar') { c = contaAdm(p.usuario, 'pendente'); c.situacao = 'ativa'; return { ok: true, usuario: c.usuario, situacao: c.situacao }; }
      if (acao === 'recusar') {
        c = contaAdm(p.usuario, 'pendente');
        contas.splice(contas.indexOf(c), 1);
        return { ok: true, usuario: c.usuario, situacao: 'recusada' };
      }
      if (acao === 'desativar') { c = contaAdm(p.usuario, 'ativa'); c.situacao = 'desativada'; return { ok: true, usuario: c.usuario, situacao: c.situacao }; }
      if (acao === 'reativar') { c = contaAdm(p.usuario, 'desativada'); c.situacao = 'ativa'; return { ok: true, usuario: c.usuario, situacao: c.situacao }; }
      if (acao === 'redefinirSenha') {
        c = contaAdm(p.usuario);
        if (c.situacao === 'pendente') throw falha('nao_encontrada', 'Recepcionista não encontrada.');
        c.temporaria = true;
        return { ok: true, usuario: c.usuario, senhaTemporaria: senhaTempDemo() };
      }
      throw falha('interno');
    });
  }

  /* ---------- Web App (spec 4.1) ---------- */
  function criar(opcoes) {
    var url = opcoes.url || '';
    var busca = raiz.location ? raiz.location.search : '';
    var demo = !url || /[?&]demo=1(&|$)/.test(busca);
    var senha = opcoes.senha || function () { return ''; };
    var sessao = opcoes.sessao || function () { return ''; };

    function chamar(acao, params) {
      if (demo) return chamarDemo(acao, params || {}, sessao());
      var corpo = Object.assign({ acao: acao }, params || {});
      var s = senha();
      if (s) corpo.senha = s;
      var t = sessao();
      if (t) corpo.sessao = t;
      var ctrl = new AbortController();
      var timer = setTimeout(function () { ctrl.abort(); }, TIMEOUT);
      return fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify(corpo),
        signal: ctrl.signal
      }).then(function (r) { return r.text(); }, function () {
        throw falha('rede');
      }).then(function (texto) {
        var json;
        try { json = JSON.parse(texto); } catch (e) { throw falha('formato'); }
        if (!json || typeof json !== 'object') throw falha('formato');
        if (!json.ok) throw falha(json.erro || 'interno', json.mensagem, json.campo);
        return json;
      }).catch(function (e) {
        if (e && e.codigo) throw e;
        throw falha('rede');
      }).finally(function () { clearTimeout(timer); });
    }

    return { chamar: chamar, demo: demo };
  }

  raiz.VisitasAPI = { criar: criar };
})(this);

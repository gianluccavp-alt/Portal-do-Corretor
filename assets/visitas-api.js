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
    formato: MSG_PLANILHA
  };

  function falha(codigo, mensagem, campo) {
    return { codigo: codigo, mensagem: MENSAGENS[codigo] || mensagem || MSG_PLANILHA, campo: campo || null };
  }
  function copia(x) { return JSON.parse(JSON.stringify(x)); }
  function pad(n) { return (n < 10 ? '0' : '') + n; }

  /* ---------- modo demonstracao ---------- */
  var IMOBS_DEMO = ['Imobiliária Exemplo A', 'Imobiliária Exemplo B', 'Imobiliária Exemplo C', 'Imobiliária Exemplo D'];
  var CORRETORES_DEMO = ['Corretor Exemplo 1', 'Corretor Exemplo 2', 'Corretor Exemplo 3'];
  var GERENTES_DEMO = ['Gerente Exemplo 1', 'Gerente Exemplo 2'];
  var CLIENTES_DEMO = [
    ['Cliente Exemplo Ana', '52998224725', '19998765432'],
    ['Cliente Exemplo Bruno', '11144477735', '1932458890'],
    ['Cliente Exemplo Carla', '12345678909', '16998112233'],
    ['Cliente Exemplo Diego', '98765432100', '15998765432']
  ];
  var memoria = null;
  var tokensDemo = {};

  function rnd(a, b, c) {
    var x = Math.sin(a * 127.1 + b * 311.7 + c * 74.7) * 43758.5453;
    return x - Math.floor(x);
  }
  function escolher(lista, r) { return lista[Math.floor(r * lista.length)]; }
  function gerarDemo(hoje, emps) {
    var out = [], seq = 0;
    for (var d = 0; d < 30; d++) {
      var data = V.somarDias(hoje, -d);
      emps.forEach(function (e, ei) {
        var n = Math.floor(rnd(ei, d, 1) * 6);
        for (var k = 0; k < n; k++) {
          var r = rnd(ei, d, 10 + k);
          var tipo = r < 0.4 ? 'esp' : r < 0.65 ? 'house' : 'imob';
          var min = 8 * 60 + Math.floor(rnd(ei, d, 30 + k) * 11 * 60);
          var cli = escolher(CLIENTES_DEMO, rnd(ei, d, 70 + k));
          seq++;
          out.push({
            id: 'D' + seq, data: data, hora: pad(Math.floor(min / 60)) + ':' + pad(min % 60),
            empreendimento: e.nome, cidade: e.cidade, tipo: tipo,
            cliente: cli[0], cpf: cli[1], telefone: cli[2],
            imobiliaria: tipo === 'imob' ? escolher(IMOBS_DEMO, rnd(ei, d, 50 + k)) : '',
            corretor: escolher(CORRETORES_DEMO, rnd(ei, d, 90 + k)),
            gerente: rnd(ei, d, 110 + k) < 0.6 ? escolher(GERENTES_DEMO, rnd(ei, d, 130 + k)) : ''
          });
        }
      });
    }
    return out;
  }
  function memoriaDemo() {
    if (!memoria) memoria = gerarDemo(V.dataLocalIso(new Date()), V.listaEmpreendimentos(raiz.CITIES || []));
    return memoria;
  }

  function chamarDemo(acao, p) {
    var lista = memoriaDemo();
    return new Promise(function (ok) { setTimeout(ok, 300); }).then(function () {
      if (acao === 'registrar') {
        var f = V.validarVisita(p);
        if (!f.ok) throw falha('invalido', f.erros[f.primeiro], f.primeiro);
        var emp = V.listaEmpreendimentos(raiz.CITIES || []).filter(function (e) { return e.nome === p.empreendimento; })[0];
        var v = {
          id: 'D' + Date.now(), data: p.data, hora: p.hora, empreendimento: p.empreendimento,
          cidade: emp ? emp.cidade : '', tipo: p.tipo,
          cliente: V.normalizarTexto(p.cliente), cpf: V.soDigitos(p.cpf), telefone: V.soDigitos(p.telefone),
          imobiliaria: p.tipo === 'imob' ? V.normalizarTexto(p.imobiliaria) : '',
          corretor: V.normalizarTexto(p.corretor), gerente: V.normalizarTexto(p.gerente)
        };
        var repetido = lista.some(function (x) { return x.cpf === v.cpf && x.empreendimento === v.empreendimento && x.data === v.data; });
        var token = 'demo-' + Math.random().toString(36).slice(2);
        lista.push(v);
        tokensDemo[v.id] = token;
        return { ok: true, visita: V.resumirVisita(v), token: token, cpfRepetido: repetido };
      }
      if (acao === 'dia') {
        return {
          ok: true,
          visitas: lista.filter(function (v) { return v.empreendimento === p.empreendimento && v.data === p.data; })
            .map(V.resumirVisita),
          sugestoes: { imobiliarias: IMOBS_DEMO.slice(), corretores: CORRETORES_DEMO.slice(), gerentes: GERENTES_DEMO.slice() }
        };
      }
      if (acao === 'excluir') {
        for (var i = 0; i < lista.length; i++) {
          if (lista[i].id === p.id && tokensDemo[p.id] && tokensDemo[p.id] === p.token) {
            lista.splice(i, 1);
            delete tokensDemo[p.id];
            return { ok: true, id: p.id };
          }
        }
        throw falha('nao_encontrada', 'Não foi possível excluir este lançamento.');
      }
      if (acao === 'listar') return { ok: true, visitas: copia(V.filtrar(lista, { de: p.de, ate: p.ate })) };
      throw falha('interno');
    });
  }

  /* ---------- Web App (spec 4.1) ---------- */
  function criar(opcoes) {
    var url = opcoes.url || '';
    var busca = raiz.location ? raiz.location.search : '';
    var demo = !url || /[?&]demo=1(&|$)/.test(busca);
    var senha = opcoes.senha || function () { return ''; };

    function chamar(acao, params) {
      if (demo) return chamarDemo(acao, params || {});
      var corpo = Object.assign({ acao: acao }, params || {});
      var s = senha();
      if (s) corpo.senha = s;
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

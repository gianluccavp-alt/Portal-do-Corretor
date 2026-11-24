/* ============================================================
   RESULTADO DO MES - regras de negocio (sem DOM)
   ------------------------------------------------------------
   Cruza as abas VENDAS SPI XIMENES (historico) e VENDAS SPI 2.0
   XIMENES (confirmadas do mes) e monta os numeros da pagina
   /resultado-mes. Regras combinadas com o comercial em 2026-11-24:
   - Mes da venda: com Data Confirmacao 2.0 -> mes dela;
     sem ela -> mes da Data da venda.
   - Fases: de Proposta Aprovada em diante. Ficam fora as etapas
     anteriores (atendimento, visita, elaboracao) e as perdidas.
   - Venda com check comercial E facilitada comecou facilitada e
     virou comercial: conta como COMERCIAL.
   - Resultado oficial (regra de hoje): comerciais em Contrato
     comunicado ou Fechado e ganho + facilitadas confirmadas.
   Funciona no navegador (window.ResultadoMes) e no Node (testes).
   ============================================================ */
(function (raiz) {
  'use strict';

  var COLUNAS = {
    venda: 'Data da venda',
    fase: 'Fase',
    unidade: 'Identificador',
    emp: 'Empreendimento',
    nome: 'Nome da oportunidade',
    imob: 'Imobiliária',
    corretor: 'Contato Corretor Proprietario',
    pcv: 'Cliente assinou PCV',
    conf: 'Data Confirmação Venda 2.0',
    boleto: 'Boleto/PIX Pago',
    cartao: 'Cartão Pago',
    valor: 'Valor Real de Venda',
    ranking: 'Ranking',
    comercial: 'Venda Comercial?',
    facilitada: 'Venda facilitada',
    origem: 'Origem da Conta'
  };

  var FASES_ANTES = ['em atendimento', 'visita agendada', 'visita realizada', 'em elaboração', 'em elaboracao', 'em análise', 'em analise', 'proposta reprovada'];
  var FASES_OFICIAIS_COMERCIAL = ['contrato comunicado', 'fechado e ganho'];

  function texto(v) { return v === null || v === undefined ? '' : String(v).trim(); }
  function sim(v) {
    if (v === true) return true;
    var t = texto(v).toLowerCase();
    return t === 'true' || t === 'sim' || t === 'verdadeiro' || t === '1';
  }
  function numero(v) {
    if (typeof v === 'number') return v;
    var t = texto(v).replace(/[^\d,.-]/g, '');
    if (t.indexOf(',') >= 0) t = t.replace(/\./g, '').replace(',', '.');
    var n = Number(t);
    return isFinite(n) ? n : 0;
  }
  /* aceita '2026-11-23', '2026-11-23T10:00' e '23/11/2026' */
  function dataIso(v) {
    var t = texto(v);
    var m = t.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (m) return m[1] + '-' + m[2] + '-' + m[3];
    m = t.match(/^(\d{2})\/(\d{2})\/(\d{4})/);
    if (m) return m[3] + '-' + m[2] + '-' + m[1];
    return '';
  }

  function faseConta(fase) {
    var f = texto(fase).toLowerCase();
    if (!f) return false;
    if (FASES_ANTES.indexOf(f) >= 0) return false;
    if (/perdid|reprovad|cancelad|distrat/.test(f)) return false;
    return true;
  }

  function chaveOp(nome, unidade, emp) {
    var m = texto(nome).match(/OP-\d+/i);
    return m ? m[0].toUpperCase() : [texto(unidade), texto(emp), texto(nome)].join('|');
  }

  /* linha crua (array) + cabecalho -> objeto com os campos usados */
  function lerLinha(cab, linha) {
    var o = {};
    Object.keys(COLUNAS).forEach(function (k) {
      var i = cab.indexOf(COLUNAS[k]);
      o[k] = i >= 0 ? linha[i] : '';
    });
    var conf = dataIso(o.conf);
    var venda = dataIso(o.venda);
    var comercial = sim(o.comercial);
    var facilitada = sim(o.facilitada);
    var op = texto(o.nome).match(/OP-\d+/i);
    return {
      chave: chaveOp(o.nome, o.unidade, o.emp),
      op: op ? op[0].toUpperCase() : texto(o.nome),
      venda: venda,
      conf: conf,
      fase: texto(o.fase),
      unidade: texto(o.unidade),
      emp: texto(o.emp),
      imob: texto(o.imob),
      corretor: texto(o.corretor),
      pcv: dataIso(o.pcv),
      boleto: sim(o.boleto),
      cartao: sim(o.cartao),
      valor: numero(o.valor),
      ranking: texto(o.ranking),
      origem: texto(o.origem),
      tipo: comercial || !facilitada ? 'comercial' : 'facilitada',
      virouComercial: comercial && facilitada
    };
  }

  /* Junta as duas abas pela OP. O relatorio principal pode repetir a mesma OP
     (uma linha por contrato); fica uma so. A aba 2.0 completa a data de
     confirmacao quando o principal ainda nao tem e traz OPs que faltarem. */
  function cruzar(abas) {
    var porChave = {};
    var ordem = [];
    (abas || []).forEach(function (aba, idx) {
      var cab = (aba.cabecalho || []).map(texto);
      (aba.linhas || []).forEach(function (linha) {
        var v = lerLinha(cab, linha);
        var atual = porChave[v.chave];
        if (!atual) { porChave[v.chave] = v; ordem.push(v.chave); return; }
        if (!atual.conf && v.conf) atual.conf = v.conf;
        if (!atual.pcv && v.pcv) atual.pcv = v.pcv;
        if (v.boleto) atual.boleto = true;
        if (v.cartao) atual.cartao = true;
        if (idx === 0 && !atual.valor && v.valor) atual.valor = v.valor;
      });
    });
    return ordem.map(function (k) { return porChave[k]; });
  }

  function classificar(v) {
    v.mesConta = (v.conf || v.venda).slice(0, 7);
    v.dataConta = v.conf || v.venda;
    v.pelaConfirmacao = !!v.conf;
    v.confirmada = !!v.conf;
    v.sinalPago = v.boleto || v.cartao;
    v.oficial = v.tipo === 'comercial'
      ? FASES_OFICIAIS_COMERCIAL.indexOf(v.fase.toLowerCase()) >= 0
      : v.confirmada;
    return v;
  }

  function vendasDoMes(abas, mes) {
    return cruzar(abas)
      .filter(function (v) { return faseConta(v.fase); })
      .map(classificar)
      .filter(function (v) { return v.mesConta === mes; })
      .sort(function (a, b) { return b.dataConta.localeCompare(a.dataConta) || a.op.localeCompare(b.op); });
  }

  function soma(lista) {
    return { n: lista.length, vgv: lista.reduce(function (s, v) { return s + v.valor; }, 0) };
  }

  function agrupar(vendas, campo) {
    var mapa = {};
    vendas.forEach(function (v) {
      var k = v[campo] || '(sem ' + (campo === 'emp' ? 'empreendimento' : 'imobiliária') + ')';
      var g = mapa[k] || (mapa[k] = { nome: k, n: 0, comerciais: 0, facilitadas: 0, confirmadas: 0, vgv: 0 });
      g.n++;
      g[v.tipo === 'comercial' ? 'comerciais' : 'facilitadas']++;
      if (v.confirmada) g.confirmadas++;
      g.vgv += v.valor;
    });
    return Object.keys(mapa).map(function (k) { return mapa[k]; })
      .sort(function (a, b) { return b.n - a.n || b.vgv - a.vgv; });
  }

  function resumo(vendas) {
    function f(tipo, conf) {
      return soma(vendas.filter(function (v) {
        return (tipo === null || v.tipo === tipo) && (conf === null || v.confirmada === conf);
      }));
    }
    var pendentes = vendas.filter(function (v) { return !v.confirmada; });
    var total = soma(vendas);
    return {
      total: total,
      ticket: total.n ? total.vgv / total.n : 0,
      oficial: soma(vendas.filter(function (v) { return v.oficial; })),
      pendentes: soma(pendentes),
      matriz: {
        comercial: { ok: f('comercial', true), sem: f('comercial', false), total: f('comercial', null) },
        facilitada: { ok: f('facilitada', true), sem: f('facilitada', false), total: f('facilitada', null) },
        total: { ok: f(null, true), sem: f(null, false), total: total }
      },
      sinal: {
        pcvESinal: pendentes.filter(function (v) { return v.pcv && v.sinalPago; }).length,
        soPcv: pendentes.filter(function (v) { return v.pcv && !v.sinalPago; }).length,
        soSinal: pendentes.filter(function (v) { return !v.pcv && v.sinalPago; }).length,
        nenhum: pendentes.filter(function (v) { return !v.pcv && !v.sinalPago; }).length,
        total: pendentes.length
      },
      empreendimentos: agrupar(vendas, 'emp'),
      imobiliarias: agrupar(vendas, 'imob')
    };
  }

  var api = {
    COLUNAS: COLUNAS,
    faseConta: faseConta,
    chaveOp: chaveOp,
    lerLinha: lerLinha,
    cruzar: cruzar,
    classificar: classificar,
    vendasDoMes: vendasDoMes,
    resumo: resumo,
    dataIso: dataIso
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.ResultadoMes = api;
})(typeof window !== 'undefined' ? window : this);

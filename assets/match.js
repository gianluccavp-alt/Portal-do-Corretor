/* ============================================================
   MATCH DE UNIDADES - regras de negocio
   ------------------------------------------------------------
   Funcoes puras (sem DOM, sem rede). Cruza o cliente com as
   unidades disponiveis usando o motor CAIXA e a copia do
   Pro Soluto. Usado por /match-unidades via window.Match e
   pelos testes (node --test tests/*.test.js).
   Spec: docs/superpowers/specs/2026-10-15-match-unidades-design.md
   ============================================================ */
(function (raiz) {
  'use strict';

  var Motor = typeof module !== 'undefined' && module.exports ? require('./motor-caixa.js') : raiz.MotorCaixa;
  var PS = typeof module !== 'undefined' && module.exports ? require('./match-prosoluto.js') : raiz.MatchProSoluto;

  var ATO_PADRAO = 2500;
  var ATO_POR_EMP = { ipiranga: 1500 };
  /* da politica mais baixa para a mais alta (POLITICAS vem do Diamante para o Aco) */
  var ORDEM_POLITICAS = ['aco', 'bronze', 'prata', 'ouro', 'diamante'];

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function iso(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function r2(v) { return Math.round(v * 100) / 100; }

  /* mesmo parser do associativo (num()) */
  function numero(str) {
    if (typeof str === 'number') return str;
    var s = (str || '').toString().replace(/[^\d.,-]/g, '');
    if (!s) return 0;
    var temVirg = s.indexOf(',') >= 0, temPonto = s.indexOf('.') >= 0;
    if (temVirg) { s = s.replace(/\./g, '').replace(',', '.'); }
    else if (temPonto) {
      var partes = s.split('.');
      if (partes.length > 2 || (partes.length === 2 && partes[1].length === 3)) s = partes.join('');
    }
    var v = parseFloat(s);
    return isFinite(v) ? v : 0;
  }

  function atoDe(empId) { return ATO_POR_EMP[empId] || ATO_PADRAO; }
  /* ato informado pelo corretor (0 vale); vazio usa o padrao do empreendimento */
  function atoCliente(cliente, empId) {
    return typeof cliente.ato === 'number' && cliente.ato >= 0 ? r2(cliente.ato) : atoDe(empId);
  }

  function idadeAnos(nasc, em) {
    var a = em.getFullYear() - nasc.getFullYear();
    if (em.getMonth() < nasc.getMonth() || (em.getMonth() === nasc.getMonth() && em.getDate() < nasc.getDate())) a--;
    return a;
  }

  /* valor de referencia para o resumo: o teto da faixa da renda */
  /* spec 4.5: possui imovel ou renda acima do MCMV -> SBPE */
  function ehSbpe(cliente) { return cliente.possuiImovel === true || cliente.renda > 13000; }

  /* spec 4.6: avaliacao > 400 mil vendida abaixo de 400 mil para renda de Faixa 3:
     o PCV trava o imovel em 400 mil e a CAIXA simula na Faixa 3 */
  var TETO_F3 = 400000, RENDA_MAX_F3 = 9600;
  function travaFaixa3(cliente, un) {
    return !ehSbpe(cliente) && cliente.renda <= RENDA_MAX_F3 && un.avaliacao > TETO_F3 && un.associativo < TETO_F3;
  }

  function valorReferencia(renda, municipio, sbpe) {
    if (sbpe) return 600000;
    if (renda <= 5000) return Motor.CIDADES[municipio].tetoF12;
    if (renda <= 9600) return 400000;
    return 600000;
  }

  /* renda que pode ter subsidio (Faixas 1 e 2 ate R$ 4.000, sem imovel na cidade):
     so nesse caso o formulario pergunta dependente e subsidio anterior */
  var RENDA_MAX_SUBSIDIO = 4000;
  function temSubsidio(renda, possuiImovel) { return renda > 0 && renda <= RENDA_MAX_SUBSIDIO && possuiImovel !== true; }

  function simulaCaixa(cliente, municipio, valor, hoje, tetoFinanciamento) {
    return Motor.simular({ renda: cliente.renda, valor: valor, nascimento: cliente.nascimento,
      municipio: municipio, fgts: cliente.fgts !== false, possuiImovel: cliente.possuiImovel === true,
      fatorSocial: cliente.fatorSocial === true, subsidioAnterior: cliente.subsidioAnterior === true,
      sistema: 'PRICE', hoje: hoje, valorFinanciamento: tetoFinanciamento });
  }

  function validarCliente(cliente, cidade, hoje) {
    if (!(cliente.renda > 0)) return 'Informe a renda bruta do cliente.';
    if (typeof cliente.ato === 'number' && !(cliente.ato >= 0)) return 'Informe um ato válido ou deixe em branco.';
    if (!cliente.nascimento || !isFinite(cliente.nascimento.getTime())) return 'Informe a data de nascimento do cliente.';
    if (temSubsidio(cliente.renda, cliente.possuiImovel) && cliente.fatorSocial == null)
      return 'Informe se há mais de um comprador ou dependente: muda o subsídio.';
    var municipio = Motor.MUNICIPIO_POR_CIDADE[cidade];
    if (!municipio) return 'Escolha a cidade.';
    var r = simulaCaixa(cliente, municipio, valorReferencia(cliente.renda, municipio, ehSbpe(cliente)), hoje);
    if (r.erro) return /70 anos/.test(r.erro)
      ? 'Cliente acima de 70 anos e 6 meses: fora do limite de idade da CAIXA.'
      : 'Fora das regras da CAIXA: ' + r.erro + '.';
    return null;
  }

  function resumoCliente(cliente, cidade, hoje) {
    var municipio = Motor.MUNICIPIO_POR_CIDADE[cidade];
    var ref = valorReferencia(cliente.renda, municipio, ehSbpe(cliente));
    var r = simulaCaixa(cliente, municipio, ref, hoje);
    return { faixa: r.faixa, jurosNominal: r.jurosNominal, prazo: r.prazo,
             financiamentoMax: r.valorFinanciamento, subsidio: r.subsidio,
             /* detalhes da simulacao CAIXA (tela "Detalhes"), calculados no valor de referencia da faixa */
             jurosEfetivo: r.jurosEfetivo, taxaAdm: r.taxaAdm, sistema: r.sistema, produto: r.produto,
             comprometimento: r.comprometimento, cota: r.cota, valorReferencia: ref,
             parcelaMax: r2(r.comprometimento * cliente.renda), seguradoras: r.seguradoras };
  }

  function avaliarUnidade(cliente, emp, un, politicaId, hoje) {
    if (!(un.avaliacao > 0) || !(un.associativo > 0)) return { status: 'sem-avaliacao' };
    var municipio = Motor.MUNICIPIO_POR_CIDADE[emp.cidade];
    var trava = travaFaixa3(cliente, un);
    var valorCaixa = trava ? TETO_F3 : un.avaliacao;
    var cx = simulaCaixa(cliente, municipio, valorCaixa, hoje);
    if (cx.erro) return { status: 'fora-enquadramento' };

    var ato = atoCliente(cliente, emp.id);
    var venda = un.associativo;
    var subsidio = cx.subsidio;
    /* Review Focus 1: banco + subsidio + ato nao podem passar da venda */
    var financiamento = Math.max(0, Math.min(cx.valorFinanciamento, r2(venda - subsidio - ato)));
    /* financiamento menor que a capacidade: a parcela CAIXA e a do valor financiado de fato */
    if (financiamento < cx.valorFinanciamento) cx = simulaCaixa(cliente, municipio, valorCaixa, hoje, financiamento);
    var parcelaFin = Math.max.apply(null, cx.seguradoras.map(function (s) { return s.primeira; }));

    var pol = PS.politicaPorId(politicaId);
    var dataVenda = iso(hoje);
    var e = {
      emp: { id: emp.id, nome: emp.nome, inicioObra: emp.inicioObra, entrega: PS.entregaDe(emp, un.torre), parcMin: emp.parcMin },
      politica: pol, dataVenda: dataVenda, dataVenc1: PS.sugereVenc1(dataVenda), dataAto: dataVenda,
      prazo: pol.prazo, valor: venda, financiado: financiamento, subsidio: subsidio, ato: ato,
      renda: cliente.renda, parcFin: parcelaFin
    };
    var c = PS.calcular(e);
    /* carne abaixo da parcela minima do produto: encurta o prazo,
       como o associativo orienta ("Reduza o prazo") */
    while (c.pronto && c.saldoCorrigido > 0.01 && c.linear.parcela < emp.parcMin && e.prazo > 1) {
      e.prazo--;
      c = PS.calcular(e);
    }
    var ap = PS.aprovacao(c, e);
    if (!ap.linear && !ap.escalonado) return { status: 'politica' };

    var carne = ap.linear ? 'linear' : 'escalonado';
    var num = un.codigo.slice(un.codigo.indexOf('-') + 1);   /* "0804" */
    return {
      status: 'ok',
      linha: {
        empId: emp.id, empNome: emp.nome, codigo: un.codigo, torre: un.torre,
        andar: parseInt(num.slice(0, num.length - 2), 10), final: parseInt(num.slice(-2), 10),
        tipoLabel: un.tipoLabel, areaPriv: un.areaPriv,
        venda: venda, financiamento: financiamento, subsidio: subsidio, ato: ato,
        saldoPS: Math.max(0, r2(c.preSaldo)), carne: carne,
        parcelaPS: carne === 'linear' ? c.linear.parcela : r2(c.escalonado.faixas[0].parcela),
        prazoPS: e.prazo, parcelaFin: parcelaFin,
        crTotal: carne === 'linear' ? c.crLinear : c.crEscal,
        jurosNominal: cx.jurosNominal, prazoFin: cx.prazo, politicaId: pol.id,
        faixa: cx.faixa, travaF3: trava,
        /* so repasse: a venda ja chega com o valor promocional (associativoSemPremio) */
        promocional: un.promocional === true,
        /* so repasse: "Valor Final Com Kit" da planilha (valor cheio do imovel, so para o PDF) */
        valorFinal: un.valorFinal
      }
    };
  }

  function contaNaPolitica(cliente, alvo, politicaId, hoje) {
    var n = 0;
    alvo.forEach(function (g) {
      g.unidades.forEach(function (un) {
        if (avaliarUnidade(cliente, g.emp, un, politicaId, hoje).status === 'ok') n++;
      });
    });
    return n;
  }

  function buscar(o) {
    var alvo = o.estoque.filter(function (g) {
      return g.emp.cidade === o.cidade && (!o.empId || g.emp.id === o.empId);
    });
    var grupos = [], total = 0, desc = { semAvaliacao: 0, foraEnquadramento: 0 };
    alvo.forEach(function (g) {
      var linhas = [];
      g.unidades.forEach(function (un) {
        var r = avaliarUnidade(o.cliente, g.emp, un, o.politicaId, o.hoje);
        if (r.status === 'ok') linhas.push(r.linha);
        else if (r.status === 'sem-avaliacao') desc.semAvaliacao++;
        else if (r.status === 'fora-enquadramento') desc.foraEnquadramento++;
      });
      linhas.sort(function (a, b) { return a.parcelaPS - b.parcelaPS || (a.codigo < b.codigo ? -1 : 1); });
      if (linhas.length) { grupos.push({ emp: g.emp, linhas: linhas }); total += linhas.length; }
    });

    var sugestao = null;
    if (!total) {
      var acima = ORDEM_POLITICAS.slice(ORDEM_POLITICAS.indexOf(o.politicaId) + 1);
      for (var i = 0; i < acima.length && !sugestao; i++) {
        var qtd = contaNaPolitica(o.cliente, alvo, acima[i], o.hoje);
        if (qtd) sugestao = { politicaId: acima[i], nome: PS.politicaPorId(acima[i]).nome, qtd: qtd };
      }
    }
    return { grupos: grupos, total: total, descartadas: desc, sugestao: sugestao };
  }

  /* selo do cartao quando a unidade cai em faixa diferente da do resumo do cliente
     (ex.: renda de Faixa 3 em unidade vendida acima de 400 mil -> Faixa 4).
     A trava da Faixa 3 ja tem selo proprio. */
  function seloFaixa(l, faixaResumo) {
    if (l.travaF3 || !l.faixa || l.faixa === faixaResumo) return null;
    return 'Enquadrada na ' + l.faixa + ' (' + String(l.jurosNominal).replace('.', ',') + '% a.a.)';
  }

  /* valor do imovel = Valor Final Com Kit (ausente ou abaixo da venda: usa a venda);
     desconto = total agregado ate o valor com desconto (a venda simulada) */
  function linhaPdf(l) {
    var valorImovel = Math.max(l.valorFinal || 0, l.venda);
    return { valorImovel: valorImovel, desconto: r2(valorImovel - l.venda), empNome: l.empNome, codigo: l.codigo, tipoLabel: l.tipoLabel, areaPriv: l.areaPriv,
             venda: l.venda, financiamento: l.financiamento, subsidio: l.subsidio, ato: l.ato,
             parcelaPS: l.parcelaPS, prazoPS: l.prazoPS, carne: l.carne, parcelaFin: l.parcelaFin,
             promocional: l.promocional === true };
  }

  function urlAssociativo(l, cliente, hoje) {
    var p = {
      emp: l.empId, unidade: l.codigo, politica: l.politicaId,
      renda: cliente.renda, idade: idadeAnos(cliente.nascimento, hoje), valor: l.venda,
      fin: l.financiamento, sub: l.subsidio, parcFin: l.parcelaFin, ato: l.ato, prazo: l.prazoPS
    };
    var q = Object.keys(p).map(function (k) { return k + '=' + encodeURIComponent(p[k]); }).join('&');
    return 'simulador-associativo.html?' + q;
  }

  var api = {
    numero: numero, temSubsidio: temSubsidio, atoDe: atoDe, atoCliente: atoCliente, seloFaixa: seloFaixa, validarCliente: validarCliente, resumoCliente: resumoCliente,
    avaliarUnidade: avaliarUnidade, buscar: buscar, linhaPdf: linhaPdf, urlAssociativo: urlAssociativo,
    ORDEM_POLITICAS: ORDEM_POLITICAS
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.Match = api;
})(this);

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
   Regras de 2026-11-25:
   - Assinatura vem do relatorio D4Sign SPI (envios de PCV), cruzado
     pela OP: o envio NAO cancelado mais recente decide. Assinado =
     Finalizado OU "Cliente assinou?" marcado, mesmo faltando as outras
     assinaturas. So cancelados = cancelado; nenhum envio = sem envio.
     Venda anterior ao primeiro envio do relatorio (18/09/2025) sem
     envio usa o campo "Cliente assinou PCV" dos relatorios de venda:
     com data = assinado; vazio = nao assinado.
   - Periodo: mes ('2026-11'), trimestre ('2026-T4') ou ano ('2026').
     Varios meses escolhidos (2026-11-26) = '2026-09+2026-11': soma tudo.
   - FID preenchido (numero) = aprovado; vazio = pendente.
   - Pendencias (assinatura, FID, sinal) olham todas as vendas do mes,
     com ou sem Data Confirmacao 2.0.
   - Imobiliaria: "CANAL IMOB" = Canal Imob; "VENDAS SPI" (Direcional e
     Riva) = House. O resto so aparece em "Todas".
   - Cidade vem do empreendimento (o relatorio nao traz cidade).
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
    origem: 'Origem da Conta',
    fid: 'FID'
  };

  var D4_INICIO = '2025-09-18';

  var COLUNAS_D4 = {
    op: 'Envio D4Sign: Oportunidade',
    status: 'Envio D4Sign: Status',
    cliente: 'Envio D4Sign: Cliente assinou?',
    criado: 'Envio D4Sign: Data de criação'
  };

  var CIDADES = {
    'Alta Vista Mangará': 'Campinas',
    'Cores da Mata Mangará': 'Campinas',
    'Parque Alto Mangará': 'Campinas',
    'Casa Prado Residencial Riva': 'Campinas',
    'Seleto Amoreiras': 'Campinas',
    'Village Park': 'Ribeirão Preto',
    'Village Gaia': 'Ribeirão Preto',
    'Reserva Direcional Jardim Botânico': 'Ribeirão Preto',
    'Direcional Conquista Clube Ipiranga': 'Ribeirão Preto',
    'Conquista Vila da Mata': 'Sorocaba'
  };

  var FASES_ANTES = ['em atendimento', 'visita agendada', 'visita realizada', 'em elaboração', 'em elaboracao', 'em análise', 'em analise', 'proposta reprovada'];

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

  function nomeCliente(nome) {
    var m = texto(nome).match(/Cliente:\s*(.+)$/i);
    return m ? m[1].trim() : '';
  }

  function cidadeDe(emp) { return CIDADES[texto(emp)] || 'Outras'; }

  function canalDe(imob) {
    var t = texto(imob).toUpperCase();
    if (t.indexOf('CANAL IMOB') >= 0) return 'canal';
    if (t.indexOf('VENDAS SPI') >= 0) return 'house';
    return '';
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
      cliente: nomeCliente(o.nome),
      fid: texto(o.fid),
      fidOk: !!texto(o.fid),
      assinatura: '',
      cidade: cidadeDe(o.emp),
      canal: canalDe(o.imob),
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
        if (!atual.fid && v.fid) { atual.fid = v.fid; atual.fidOk = true; }
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
    return v;
  }

  /* aba "Envios D4Sign" -> { 'OP-1': 'assinado' | 'aguardando' | 'cancelado' } */
  function lerD4sign(aba) {
    var cab = (aba.cabecalho || []).map(texto);
    var idx = {};
    Object.keys(COLUNAS_D4).forEach(function (k) { idx[k] = cab.indexOf(COLUNAS_D4[k]); });
    var porOp = {};
    (aba.linhas || []).forEach(function (l) {
      var m = texto(l[idx.op]).match(/OP-\d+/i);
      if (!m) return;
      var k = m[0].toUpperCase();
      (porOp[k] || (porOp[k] = [])).push({
        status: texto(l[idx.status]).toLowerCase(),
        cliente: sim(l[idx.cliente]),
        criado: texto(l[idx.criado])
      });
    });
    var saida = {};
    Object.keys(porOp).forEach(function (k) {
      var vivos = porOp[k].filter(function (e) { return e.status !== 'cancelado'; })
        /* mais recente primeiro; na mesma data, o Finalizado vale */
        .sort(function (a, b) {
          return dataIso(b.criado).localeCompare(dataIso(a.criado)) ||
            (b.status === 'finalizado') - (a.status === 'finalizado');
        });
      var e = vivos[0];
      if (!e) saida[k] = 'cancelado';
      else saida[k] = e.status === 'finalizado' || e.cliente ? 'assinado' : 'aguardando';
    });
    return saida;
  }

  function tipoPeriodo(p) {
    if (p.indexOf('+') >= 0) return 'multi';
    if (/^\d{4}$/.test(p)) return 'ano';
    return /^\d{4}-T[1-4]$/.test(p) ? 'tri' : 'mes';
  }
  /* periodo do tipo pedido que contem o mes 'yyyy-MM' */
  function periodoDe(mes, tipo) {
    if (tipo === 'ano') return mes.slice(0, 4);
    if (tipo === 'tri') return mes.slice(0, 4) + '-T' + Math.ceil(Number(mes.slice(5, 7)) / 3);
    return mes;
  }
  function noPeriodo(mes, p) {
    if (!mes) return false;
    if (tipoPeriodo(p) === 'multi') return p.split('+').indexOf(mes) >= 0;
    return periodoDe(mes, tipoPeriodo(p)) === p;
  }

  /* Junta as respostas de varios meses ANTES das regras: a OP que vier em duas
     respostas e unificada pelo cruzar, como no trimestre. Se um mes vier sem
     D4Sign, a assinatura fica desconhecida (nunca "Nao enviado" por engano). */
  function juntarRespostas(respostas, periodo) {
    function juntar(tabelas) {
      var porNome = {};
      var saida = [];
      tabelas.forEach(function (t) {
        var chave = JSON.stringify([t.aba || '', t.cabecalho]);
        var alvo = porNome[chave];
        if (!alvo) {
          alvo = porNome[chave] = { aba: t.aba, cabecalho: t.cabecalho, linhas: [] };
          saida.push(alvo);
        }
        alvo.linhas = alvo.linhas.concat(t.linhas || []);
      });
      return saida;
    }
    /* a aba principal de todos os meses vem antes da aba 2.0 */
    var abas = [];
    respostas.forEach(function (r) {
      (r.abas || []).forEach(function (a, i) { (abas[i] || (abas[i] = [])).push(a); });
    });
    var temD4 = respostas.every(function (r) { return r.d4sign && r.d4sign.linhas; });
    return {
      ok: true,
      mes: periodo,
      meses: respostas[0].meses,
      atualizadoEm: respostas.map(function (r) { return r.atualizadoEm || ''; }).sort()[0],
      intervaloMinutos: respostas[0].intervaloMinutos,
      abas: abas.reduce(function (lista, grupo) { return lista.concat(juntar(grupo)); }, []),
      d4sign: temD4 ? juntar(respostas.map(function (r) { return { cabecalho: r.d4sign.cabecalho, linhas: r.d4sign.linhas }; }))[0] : null
    };
  }

  /* d4sign ausente (Web App antigo): assinatura fica '' (desconhecida) */
  function vendasDoMes(abas, mes, d4sign) {
    var envios = d4sign && d4sign.linhas ? lerD4sign(d4sign) : null;
    return cruzar(abas)
      .filter(function (v) { return faseConta(v.fase); })
      .map(classificar)
      .filter(function (v) { return noPeriodo(v.mesConta, mes); })
      .map(function (v) {
        if (!envios) return v;
        var e = envios[v.op];
        if (e) v.assinatura = e;
        else if (v.venda && v.venda < D4_INICIO) v.assinatura = v.pcv ? 'assinado' : 'nao_assinado';
        else v.assinatura = 'sem_envio';
        return v;
      })
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

  function temPendencia(v, qual) {
    if (qual === 'assinatura') return !!v.assinatura && v.assinatura !== 'assinado';
    if (qual === 'fid') return !v.fidOk;
    if (qual === 'sinal') return !v.sinalPago;
    return v.assinatura === 'assinado' && v.fidOk && v.sinalPago;
  }

  /* filtro com varias marcadas: basta ter uma delas; nenhuma marcada = todas */
  function temAlguma(v, quais) {
    return !quais.length || quais.some(function (q) { return temPendencia(v, q); });
  }

  /* filtros do topo: valem para a pagina inteira */
  function filtrarGeral(vendas, g) {
    return vendas.filter(function (v) {
      return (!g.emps.length || g.emps.indexOf(v.emp) >= 0) && (!g.cidade || v.cidade === g.cidade) && (!g.canal || v.canal === g.canal);
    });
  }

  function resumo(vendas) {
    function f(tipo, conf) {
      return soma(vendas.filter(function (v) {
        return (tipo === null || v.tipo === tipo) && (conf === null || v.confirmada === conf);
      }));
    }
    function pend(qual) { return vendas.filter(function (v) { return temPendencia(v, qual); }).length; }
    var total = soma(vendas);
    var temD4 = vendas.some(function (v) { return !!v.assinatura; });
    return {
      total: total,
      matriz: {
        comercial: { ok: f('comercial', true), sem: f('comercial', false), total: f('comercial', null) },
        facilitada: { ok: f('facilitada', true), sem: f('facilitada', false), total: f('facilitada', null) },
        total: { ok: f(null, true), sem: f(null, false), total: total }
      },
      pendencias: {
        temD4: temD4,
        total: total.n,
        assinatura: pend('assinatura'),
        fid: pend('fid'),
        sinal: pend('sinal'),
        semPendencia: pend('nenhuma')
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
    lerD4sign: lerD4sign,
    temPendencia: temPendencia,
    temAlguma: temAlguma,
    tipoPeriodo: tipoPeriodo,
    periodoDe: periodoDe,
    noPeriodo: noPeriodo,
    juntarRespostas: juntarRespostas,
    filtrarGeral: filtrarGeral,
    canalDe: canalDe,
    cidadeDe: cidadeDe,
    dataIso: dataIso
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.ResultadoMes = api;
})(typeof window !== 'undefined' ? window : this);

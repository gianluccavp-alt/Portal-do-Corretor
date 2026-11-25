/**
 * Vendas SPI XIMENES: Salesforce -> Google Sheets.
 * Tambem copia o relatorio D4Sign SPI para a aba "Envios D4Sign".
 *
 * Roda DENTRO da planilha (Extensoes > Apps Script) e, a cada 30 minutos, copia
 * dois relatorios do Salesforce para duas abas:
 *   - aba "VENDAS SPI XIMENES"      <- relatorio VENDAS SPI XIMENES
 *   - aba "VENDAS SPI 2.0 XIMENES"  <- relatorio VENDAS SPI 2.0 XIMENES
 * Nenhuma regra do relatorio e reescrita aqui: o Salesforce roda o relatorio
 * (filtros, colunas, logica) e este script so traz o resultado.
 *
 * LIMITE DE 2.000 LINHAS: a API de relatorios entrega no maximo 2.000 linhas por
 * execucao. Quando o relatorio e maior, o script roda o mesmo relatorio por
 * intervalos de "Data de criacao" (campo nunca vazio) e junta os pedacos. Os
 * intervalos usados ficam guardados e sao reaproveitados nas proximas rodadas
 * (cerca de 19 execucoes de relatorio por atualizacao com o D4Sign, em vez de 40+).
 * ATENCAO: o Salesforce limita a 500 execucoes de relatorio POR HORA para a
 * empresa inteira. Cada atualizacao gasta ~19, entao a 30 min sao ~38 por hora.
 * Antes de baixar o intervalo, veja se sobra folga (erro 403 = limite atingido).
 *
 * INSTALACAO (uma vez):
 *  1. Extensoes > Apps Script. Cole este arquivo no Codigo.gs.
 *  2. Configuracoes do projeto (engrenagem):
 *       - Fuso horario: (GMT-03:00) America/Sao_Paulo
 *       - Propriedades do script > Adicionar propriedade (4):
 *           SF_HOST      https://direcional.my.salesforce.com
 *           SF_USERNAME  seu usuario do Salesforce
 *           SF_PASSWORD  sua senha do Salesforce
 *           SF_TOKEN     seu token de seguranca (o do e-mail)
 *  3. Escolha a funcao testarLogin e clique em Executar (autorize quando pedir).
 *  4. Execute atualizarAgora (primeira carga; leva ~1 minuto).
 *  5. Execute instalarGatilho (liga a atualizacao automatica).
 *
 * SEGREDOS: usuario, senha e token ficam so nas Propriedades do script, nunca no
 * codigo. Quem tem acesso de EDITOR a esta planilha consegue abrir o script e
 * ver essas propriedades, entao compartilhe como editor so com quem pode.
 * Se trocar a senha do Salesforce, atualize SF_PASSWORD e SF_TOKEN (o token muda).
 */

var CONFIG = {
  planilhaId: '1WGgOMdVP_FMTjXgNpi5dodX44YNH-dqv4Cb5yglb0l4', // RELATORIO VENDAS 2.0
  relatorios: [
    { aba: 'VENDAS SPI XIMENES', id: '00OU600000OaAcYMAV' },
    { aba: 'VENDAS SPI 2.0 XIMENES', id: '00OU600000O7OxRMAV' },
    // relatorio D4Sign SPI: tabular, sem Data de criacao da OP; divide pelo filtro de data do proprio relatorio
    { aba: 'Envios D4Sign', id: '00OU600000NJLYHMA5', d4sign: true, particao: 'filtroDeData' }
  ],
  apiVersao: 'v62.0',
  fuso: 'America/Sao_Paulo',
  intervaloMinutos: 30,        // 1, 5, 10, 15 ou 30
  horario: { inicio: 7, fim: 22 }, // so atualiza entre 7h e 22h (horario de Sao Paulo)
  limiteApi: 2000,
  margem: 1800,                // pedaco com mais que isso e dividido ao meio
  campoParticao: 'Opportunity.CreatedDate',
  paralelo: 8,                 // execucoes simultaneas (o Salesforce aceita ate 20)
  colunasMoeda: ['Valor Real de Venda'],
  tentativas: 3
};

/* ============================ PONTOS DE ENTRADA ============================ */

/** Gatilho automatico. Respeita o horario comercial. */
function atualizarVendas() { executar_(false); }

/** Botao manual: atualiza agora, em qualquer horario. */
function atualizarAgora() { executar_(true); }

/** Confere usuario, senha e token sem mexer na planilha. */
function testarLogin() {
  var sessao = sfLogin_();
  Logger.log('Login OK. Sessao de ' + sessao.length + ' caracteres.');
}

/** Liga a atualizacao automatica (apaga gatilhos antigos desta funcao antes). */
function instalarGatilho() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'atualizarVendas') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('atualizarVendas').timeBased().everyMinutes(CONFIG.intervaloMinutos).create();
  Logger.log('Gatilho criado: a cada ' + CONFIG.intervaloMinutos + ' minutos, entre ' +
    CONFIG.horario.inicio + 'h e ' + CONFIG.horario.fim + 'h.');
}

/** Desliga a atualizacao automatica. */
function removerGatilho() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'atualizarVendas') ScriptApp.deleteTrigger(t);
  });
}

/** Mostra quando foi a ultima atualizacao e o ultimo erro (se houver). */
function statusAtualizacao() {
  var p = PropertiesService.getScriptProperties();
  Logger.log('Ultima atualizacao: ' + (p.getProperty('ULTIMA_ATUALIZACAO') || 'nunca') +
    ' | Ultimo erro: ' + (p.getProperty('ULTIMO_ERRO') || 'nenhum'));
}

/* ============================== ORQUESTRACAO =============================== */

function executar_(forcar) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(2000)) return; // ja tem uma atualizacao rodando
  var props = PropertiesService.getScriptProperties();
  try {
    if (!forcar && !dentroDoHorario_()) return;
    if (Session.getScriptTimeZone() !== CONFIG.fuso) {
      throw new Error('Fuso horario do projeto e ' + Session.getScriptTimeZone() +
        '. Ajuste em Configuracoes do projeto para ' + CONFIG.fuso + ' (senao as datas saem erradas).');
    }
    var inicio = Date.now();
    // Puxa TUDO antes de gravar qualquer aba: se algo falhar, a planilha fica como estava.
    var resultados = CONFIG.relatorios.map(function (r) {
      var dados = puxarComTentativas_(r);
      dados.aba = r.aba;
      return dados;
    });
    resultados.forEach(gravarAba_);
    props.setProperty('ULTIMA_ATUALIZACAO', Utilities.formatDate(new Date(), CONFIG.fuso, 'yyyy-MM-dd HH:mm:ss'));
    props.deleteProperty('ULTIMO_ERRO');
    Logger.log(resultados.map(function (d) { return d.aba + ': ' + d.rows.length + ' linhas'; }).join(' | ') +
      ' em ' + Math.round((Date.now() - inicio) / 1000) + 's');
  } catch (e) {
    props.setProperty('ULTIMO_ERRO', Utilities.formatDate(new Date(), CONFIG.fuso, 'yyyy-MM-dd HH:mm:ss') + ' ' + e.message);
    throw e;
  } finally {
    lock.releaseLock();
  }
}

function dentroDoHorario_() {
  var h = Number(Utilities.formatDate(new Date(), CONFIG.fuso, 'H'));
  return h >= CONFIG.horario.inicio && h < CONFIG.horario.fim;
}

/** Se o relatorio mudar no meio da puxada (venda nova), a contagem nao fecha: tenta de novo. */
function puxarComTentativas_(rel) {
  var ultimoErro;
  for (var i = 0; i < CONFIG.tentativas; i++) {
    try { return puxarRelatorio_(rel); } catch (e) {
      ultimoErro = e;
      if (!/CONTAGEM/.test(e.message)) throw e;
      Utilities.sleep(2000);
    }
  }
  throw ultimoErro;
}

/* ============================ RELATORIO ANALYTICS ========================== */

function puxarRelatorio_(rel) {
  var desc = sfFetchAll_([{ path: '/analytics/reports/' + rel.id + '/describe' }])[0];
  var meta = desc.reportMetadata;

  // 1 execucao barata (sem detalhes) so para saber o total de linhas.
  var esperado = total_(rodar_(rel.id, meta, false));

  var linhas;
  if (esperado <= CONFIG.limiteApi) {
    var unico = rodar_(rel.id, meta, true);
    if (!unico.allData) throw new Error('CONTAGEM: relatorio ' + rel.aba + ' veio cortado com ' + esperado + ' linhas.');
    linhas = achatar_(desc, unico);
  } else {
    linhas = porParticoes_(rel, desc);
  }
  if (linhas.rows.length !== esperado) {
    throw new Error('CONTAGEM: ' + rel.aba + ' veio com ' + linhas.rows.length + ' linhas e o Salesforce informa ' + esperado + '.');
  }
  return linhas;
}

function rodar_(id, meta, detalhes) {
  return sfFetchAll_([corpoRelatorio_(id, meta, detalhes)])[0];
}

function corpoRelatorio_(id, meta, detalhes) {
  return { path: '/analytics/reports/' + id + '?includeDetails=' + detalhes, body: { reportMetadata: meta } };
}

function total_(resultado) {
  var ag = resultado.factMap['T!T'].aggregates;
  return Number(String(ag[ag.length - 1].value).replace(/\./g, ''));
}

/** Divide o relatorio por intervalos de data de criacao ate cada um caber em 2.000 linhas. */
function porParticoes_(rel, desc) {
  var pedaco = rel.particao === 'filtroDeData' ? comPeriodo_ : comPedaco_;
  var chave = 'PARTICOES_' + rel.id;
  var props = PropertiesService.getScriptProperties();
  var salvas = props.getProperty(chave);
  var fila = salvas ? JSON.parse(salvas) : [['2010-01-01', '2100-01-01']];
  var usadas = [], formato = null, todas = [], profundidade = 0;

  while (fila.length) {
    if (++profundidade > 14) throw new Error('Particionamento de ' + rel.aba + ' nao convergiu.');
    var pedidos = fila.map(function (r) { return corpoRelatorio_(rel.id, pedaco(desc.reportMetadata, r[0], r[1]), true); });
    var respostas = sfFetchAll_(pedidos);
    var proxima = [];
    respostas.forEach(function (j, i) {
      var r = fila[i];
      if (j.allData) {
        var a = achatar_(desc, j);
        formato = formato || a;
        for (var k = 0; k < a.rows.length; k++) todas.push(a.rows[k]);
        usadas.push(r);
      } else {
        var m = meio_(r[0], r[1]);
        proxima.push([r[0], m], [m, r[1]]);
      }
    });
    fila = proxima;
  }
  props.setProperty(chave, JSON.stringify(usadas));
  formato = formato || achatar_(desc, { factMap: {} });
  return { headers: formato.headers, types: formato.types, rows: todas };
}

/** Copia a configuracao do relatorio e acrescenta [ini, fim) na data de criacao, preservando a logica booleana. */
function comPedaco_(metaOriginal, ini, fim) {
  var m = JSON.parse(JSON.stringify(metaOriginal));
  var n = m.reportFilters.length;
  m.reportFilters.push(
    { column: CONFIG.campoParticao, filterType: 'fieldValue', isRunPageEditable: false, operator: 'greaterOrEqual', value: ini },
    { column: CONFIG.campoParticao, filterType: 'fieldValue', isRunPageEditable: false, operator: 'lessThan', value: fim }
  );
  var base = m.reportBooleanFilter;
  if (!base) { var nums = []; for (var i = 1; i <= n; i++) nums.push(i); base = nums.join(' AND '); }
  m.reportBooleanFilter = '(' + base + ') AND ' + (n + 1) + ' AND ' + (n + 2);
  return m;
}

/** Mesmo intervalo [ini, fim), usando o filtro de data padrao do relatorio (as duas pontas dele sao inclusivas). */
function comPeriodo_(metaOriginal, ini, fim) {
  var m = JSON.parse(JSON.stringify(metaOriginal));
  m.standardDateFilter = { column: m.standardDateFilter.column, durationValue: 'CUSTOM', startDate: ini, endDate: isoDeDias_(diasDesde1970_(fim) - 1) };
  return m;
}

function diasDesde1970_(iso) { return Math.floor(Date.parse(iso + 'T00:00:00Z') / 86400000); }
function isoDeDias_(d) { return new Date(d * 86400000).toISOString().slice(0, 10); }

function meio_(ini, fim) {
  var a = diasDesde1970_(ini);
  var b = Math.min(diasDesde1970_(fim), Math.floor(Date.now() / 86400000) + 2); // intervalo aberto no futuro: divide ate hoje
  var m = Math.floor((a + b) / 2);
  if (m <= a || m >= diasDesde1970_(fim)) throw new Error('Intervalo de um unico dia (' + ini + ') ainda passa de 2.000 linhas.');
  return isoDeDias_(m);
}

/** Transforma o resultado do Salesforce em cabecalhos, tipos e linhas com valores puros. */
function achatar_(desc, resultado) {
  var info = desc.reportExtendedMetadata.detailColumnInfo;
  var cols = desc.reportMetadata.detailColumns;
  var rows = [];
  Object.keys(resultado.factMap).forEach(function (chave) {
    // relatorio tabular guarda as linhas em T!T; nos agrupados, T!T e so o total
    if (chave === 'T!T' && desc.reportMetadata.reportFormat !== 'TABULAR') return;
    (resultado.factMap[chave].rows || []).forEach(function (linha) {
      rows.push(linha.dataCells.map(function (c, i) {
        var tipo = info[cols[i]].dataType, v = c.value;
        if (v === null || v === undefined) return '';
        if (typeof v === 'number' || typeof v === 'boolean') return v;
        if (typeof v === 'object' && v.amount !== undefined) return v.amount;
        if (tipo === 'date' || tipo === 'datetime') return v;
        return c.label !== undefined ? c.label : v;
      }));
    });
  });
  return {
    headers: cols.map(function (c) { return info[c].label; }),
    types: cols.map(function (c) { return info[c].dataType; }),
    rows: rows
  };
}

/* ================================ SALESFORCE =============================== */

function sfBase_() {
  var host = PropertiesService.getScriptProperties().getProperty('SF_HOST');
  if (!host) throw new Error('Falta a propriedade do script SF_HOST.');
  return host.replace(/\/$/, '') + '/services/data/' + CONFIG.apiVersao;
}

function sfLogin_() {
  var p = PropertiesService.getScriptProperties();
  var host = (p.getProperty('SF_HOST') || '').replace(/\/$/, '');
  var user = p.getProperty('SF_USERNAME'), senha = p.getProperty('SF_PASSWORD'), token = p.getProperty('SF_TOKEN');
  if (!host || !user || !senha || !token) {
    throw new Error('Faltam propriedades do script: SF_HOST, SF_USERNAME, SF_PASSWORD e SF_TOKEN.');
  }
  var esc = function (s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');
  };
  var xml = '<?xml version="1.0" encoding="utf-8"?>' +
    '<env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">' +
    '<env:Body><n1:login xmlns:n1="urn:partner.soap.sforce.com"><n1:username>' + esc(user) + '</n1:username>' +
    '<n1:password>' + esc(senha + token) + '</n1:password></n1:login></env:Body></env:Envelope>';
  var r = UrlFetchApp.fetch(host + '/services/Soap/u/' + CONFIG.apiVersao.replace('v', ''), {
    method: 'post', contentType: 'text/xml; charset=UTF-8', headers: { SOAPAction: 'login' }, payload: xml, muteHttpExceptions: true
  });
  var txt = r.getContentText();
  var m = txt.match(/<sessionId>([^<]+)<\/sessionId>/);
  if (!m) {
    var f = txt.match(/<faultstring>([^<]*)<\/faultstring>/);
    throw new Error('Login no Salesforce falhou: ' + (f ? f[1] : 'HTTP ' + r.getResponseCode()));
  }
  CacheService.getScriptCache().put('SF_SESSAO', m[1], 1500); // 25 minutos
  return m[1];
}

function sfSessao_() { return CacheService.getScriptCache().get('SF_SESSAO') || sfLogin_(); }

/** Executa uma lista de chamadas (em lotes paralelos) e devolve os JSON na mesma ordem. */
function sfFetchAll_(itens) {
  var sessao = sfSessao_(), saida = [];
  for (var i = 0; i < itens.length; i += CONFIG.paralelo) {
    var lote = itens.slice(i, i + CONFIG.paralelo);
    var respostas = sfEnviar_(lote, sessao);
    var expirou = respostas.some(function (r) { return r.getResponseCode() === 401; });
    if (expirou) { sessao = sfLogin_(); respostas = sfEnviar_(lote, sessao); }
    respostas.forEach(function (r) {
      var cod = r.getResponseCode(), txt = r.getContentText();
      if (cod >= 400) {
        var dica = /500 relat/.test(txt) ? ' (limite de 500 relatorios por hora da empresa)' : '';
        throw new Error('Salesforce ' + cod + dica + ': ' + txt.slice(0, 300));
      }
      saida.push(JSON.parse(txt));
    });
  }
  return saida;
}

function sfEnviar_(lote, sessao) {
  var base = sfBase_();
  return UrlFetchApp.fetchAll(lote.map(function (it) {
    var req = { url: base + it.path, method: it.body ? 'post' : 'get', headers: { Authorization: 'Bearer ' + sessao }, muteHttpExceptions: true };
    if (it.body) { req.contentType = 'application/json'; req.payload = JSON.stringify(it.body); }
    return req;
  }));
}

/* ============================== GOOGLE SHEETS ============================== */

function gravarAba_(dados) {
  var ss = SpreadsheetApp.openById(CONFIG.planilhaId); // funciona com o script dentro da planilha ou solto
  var sh = ss.getSheetByName(dados.aba) || ss.insertSheet(dados.aba);
  var n = dados.rows.length, c = dados.headers.length;

  var valores = [dados.headers];
  for (var i = 0; i < n; i++) valores.push(converterLinha_(dados.rows[i], dados.types));

  if (sh.getMaxRows() < n + 1) sh.insertRowsAfter(sh.getMaxRows(), n + 1 - sh.getMaxRows());
  if (sh.getMaxColumns() < c) sh.insertColumnsAfter(sh.getMaxColumns(), c - sh.getMaxColumns());

  sh.getRange(1, 1, n + 1, c).setValues(valores);

  var ultima = sh.getLastRow();
  if (ultima > n + 1) sh.getRange(n + 2, 1, ultima - n - 1, sh.getMaxColumns()).clearContent();
  if (sh.getMaxColumns() > c) sh.getRange(1, c + 1, Math.max(n + 1, ultima), sh.getMaxColumns() - c).clearContent();

  // formatos
  dados.types.forEach(function (tipo, j) {
    var fmt = null;
    if (tipo === 'date') fmt = 'dd/MM/yyyy';
    else if (tipo === 'datetime') fmt = 'dd/MM/yyyy HH:mm';
    else if (CONFIG.colunasMoeda.indexOf(dados.headers[j]) >= 0) fmt = '#,##0.00';
    if (fmt && n > 0) sh.getRange(2, j + 1, n, 1).setNumberFormat(fmt);
  });
  sh.getRange(1, 1, 1, c).setFontWeight('bold').setBackground('#1F3864').setFontColor('#FFFFFF');
  sh.setFrozenRows(1);
  sh.getRange(1, 1).setNote('Atualizado em ' + Utilities.formatDate(new Date(), CONFIG.fuso, 'dd/MM/yyyy HH:mm') +
    ' a partir do relatorio do Salesforce. Nao edite estas celulas: a proxima atualizacao sobrescreve.');
}

function converterLinha_(linha, tipos) {
  return linha.map(function (v, j) {
    if (v === '' || v === null || v === undefined) return '';
    if (tipos[j] === 'date' && typeof v === 'string') {
      var p = v.split('-');
      return new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2])); // meia-noite no fuso do projeto
    }
    if (tipos[j] === 'datetime' && typeof v === 'string') return new Date(v);
    return v;
  });
}

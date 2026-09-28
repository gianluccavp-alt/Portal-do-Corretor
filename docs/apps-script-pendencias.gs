/* ============================================================
   PENDENCIAS DE VENDAS - Google Apps Script Web App
   ------------------------------------------------------------
   Backend da pagina /pendencias-vendas do Portal do Corretor.
   Le a aba RELATORIO e grava Observacao/Retorno e o cancelamento
   (fonte vermelha + tachada) direto nela. A pagina NAO le o CSV
   da planilha: tudo passa por aqui, com a senha conferida no
   servidor. Spec: docs/superpowers/specs/2026-09-28-pendencias-vendas-design.md

   ---------- COMO PUBLICAR (uma vez) ----------
   1. Abra a planilha > Extensoes > Apps Script (o MESMO projeto que
      tem atualizarRelatorioSalesforce()).
   2. Arquivos > "+" > Script > nome "Pendencias" > cole este arquivo.
   3. No arquivo do relatorio, dentro de atualizarRelatorioSalesforce(),
      logo ANTES da ultima linha
        Logger.log("RELATÓRIO atualizado com sucesso usando DATABASE, DATABASE 2 e OP X AC.");
      adicione:
        PropertiesService.getScriptProperties()
          .setProperty('PENDENCIAS_ULTIMA_ATUALIZACAO', new Date().toISOString());
   4. Selecione a funcao configurarSenhaPendencias > Executar (autorize).
   5. Selecione testePendencias > Executar > confira o log.
   6. Implantar > Nova implantacao > Tipo: App da Web
        Executar como: Eu
        Quem tem acesso: Qualquer pessoa
   7. Copie a URL que termina em /exec e cole em
      window.PENDENCIAS_APPS_SCRIPT_URL (assets/config.js).

   Mudou o codigo depois? Implantar > Gerenciar implantacoes > editar >
   Nova versao (a URL /exec continua a mesma).
   Trocar a senha: edite configurarSenhaPendencias e rode de novo
   (nao precisa reimplantar nem mexer no site).
   ============================================================ */

var PEND_ABA = 'RELATÓRIO';
var PEND_LINHA_CABECALHO = 3;
var PEND_PROP_SENHA = 'PENDENCIAS_SENHA';
var PEND_PROP_ATUALIZACAO = 'PENDENCIAS_ULTIMA_ATUALIZACAO';
var PEND_VERMELHOS = ['#ff0000', '#f00', 'red', '#cc0000', '#990000', '#b00000'];
var PEND_OBRIGATORIAS = ['ID', 'Observação', 'Retorno'];
var PEND_MAX_TEXTO = 5000;

function configurarSenhaPendencias() {
  PropertiesService.getScriptProperties().setProperty(PEND_PROP_SENHA, 'Comercial123');
  Logger.log('Senha da pagina /pendencias-vendas configurada.');
}

function PendFalha(codigo, mensagem) { this.codigo = codigo; this.message = mensagem; }

function doGet() {
  return pendJson_({ ok: false, erro: 'interno', mensagem: 'Use POST.' });
}

function doPost(e) {
  var resposta;
  try {
    var req = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    resposta = pendRoteador_(req);
  } catch (err) {
    resposta = err instanceof PendFalha
      ? { ok: false, erro: err.codigo, mensagem: err.message }
      : { ok: false, erro: 'interno', mensagem: String((err && err.message) || err) };
  }
  return pendJson_(resposta);
}

function pendJson_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function pendRoteador_(req) {
  var senha = PropertiesService.getScriptProperties().getProperty(PEND_PROP_SENHA);
  if (!senha || req.senha !== senha) throw new PendFalha('senha', 'Senha incorreta.');
  switch (req.acao) {
    case 'listar': return pendListar_();
    case 'cancelar': return pendComLock_(function () { return pendPintar_(req.id, true); });
    case 'reativar': return pendComLock_(function () { return pendPintar_(req.id, false); });
    case 'editar': return pendComLock_(function () { return pendEditar_(req.id, req.observacao, req.retorno); });
    case 'atualizar': return pendComLock_(function () { atualizarRelatorioSalesforce(); return pendListar_(); });
    default: throw new PendFalha('interno', 'Ação desconhecida: ' + req.acao);
  }
}

/* O atualizarRelatorioSalesforce() insere linhas e reordena a aba: toda
   gravacao localiza a linha pelo ID dentro do lock, logo antes de gravar. */
function pendComLock_(fn) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) throw new PendFalha('ocupado', 'Tem uma atualização em andamento, tente em instantes.');
  try { return fn(); } finally { lock.releaseLock(); }
}

function pendNormalizar_(v) {
  if (v === null || v === undefined) return '';
  return String(v).trim().toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
}

function pendLerAba_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var aba = ss.getSheetByName(PEND_ABA);
  if (!aba) throw new PendFalha('coluna', 'A aba "' + PEND_ABA + '" não foi encontrada.');
  var ultimaLinha = aba.getLastRow();
  var ultimaColuna = aba.getLastColumn();
  var cabecalho = aba.getRange(PEND_LINHA_CABECALHO, 1, 1, ultimaColuna).getValues()[0]
    .map(function (c) { return String(c).trim(); });
  var indice = {};
  cabecalho.forEach(function (nome, i) { if (nome && !(nome in indice)) indice[nome] = i; });
  PEND_OBRIGATORIAS.forEach(function (nome) {
    if (!(nome in indice)) throw new PendFalha('coluna', 'Coluna "' + nome + '" não encontrada no ' + PEND_ABA + '.');
  });
  /* colunas de dados = todas menos as auxiliares "__ORDEM_..." do script */
  var colunasDados = [];
  cabecalho.forEach(function (nome, i) { if (nome.indexOf('__') !== 0) colunasDados.push(i); });
  var n = Math.max(ultimaLinha - PEND_LINHA_CABECALHO, 0);
  var faixa = n ? aba.getRange(PEND_LINHA_CABECALHO + 1, 1, n, ultimaColuna) : null;
  return {
    aba: aba,
    fuso: ss.getSpreadsheetTimeZone(),
    indice: indice,
    colunasDados: colunasDados,
    ultimaColunaDados: colunasDados.length ? colunasDados[colunasDados.length - 1] + 1 : ultimaColuna,
    n: n,
    valores: faixa ? faixa.getValues() : [],
    exibidos: faixa ? faixa.getDisplayValues() : [],
    cores: faixa ? faixa.getFontColors() : [],
    linhasFonte: faixa ? faixa.getFontLines() : []
  };
}

function pendNumero_(bruto, exibido) {
  if (typeof bruto === 'number') return bruto;
  var s = String(exibido || bruto || '').replace(/[^\d,.-]/g, '');
  if (!s) return null;
  var n = Number(s.replace(/\./g, '').replace(',', '.'));
  return isNaN(n) ? null : n;
}

function pendVendaDaLinha_(t, i) {
  var bruto = t.valores[i];
  var exibido = t.exibidos[i];
  function col(nome) { return nome in t.indice ? t.indice[nome] : -1; }
  function texto(nome) { var c = col(nome); return c < 0 ? '' : String(exibido[c]).trim(); }
  function data(nome) {
    var c = col(nome);
    if (c < 0) return '';
    var v = bruto[c];
    if (Object.prototype.toString.call(v) === '[object Date]' && !isNaN(v)) {
      var comHora = v.getHours() || v.getMinutes();
      return Utilities.formatDate(v, t.fuso, comHora ? 'dd/MM/yyyy HH:mm' : 'dd/MM/yyyy');
    }
    return String(exibido[c]).trim();
  }
  function sim(nome) {
    var c = col(nome);
    if (c < 0) return false;
    if (bruto[c] === true) return true;
    var s = pendNormalizar_(exibido[c]);
    return s === 'sim' || s === 'verdadeiro' || s === 'true';
  }
  var cancelada = false;
  for (var k = 0; k < t.colunasDados.length && !cancelada; k++) {
    var j = t.colunasDados[k];
    var cor = String(t.cores[i][j] || '').toLowerCase();
    var linha = String(t.linhasFonte[i][j] || '').toLowerCase();
    if (PEND_VERMELHOS.indexOf(cor) !== -1 || linha === 'line-through') cancelada = true;
  }
  var cValor = col('Valor Real de Venda');
  return {
    id: texto('ID'),
    cliente: texto('Cliente'),
    dataVenda: data('Data da venda'),
    fase: texto('Fase'),
    imobiliaria: texto('Imobiliária'),
    empreendimento: texto('Empreendimento'),
    identificador: texto('Identificador'),
    vendaFacilitada: sim('Venda facilitada'),
    fid: texto('FID'),
    pcvAssinadoEm: data('Cliente assinou PCV'),
    boletoPago: sim('Boleto/PIX Pago'),
    cartaoPago: sim('Cartão Pago'),
    valorReal: cValor < 0 ? null : pendNumero_(bruto[cValor], exibido[cValor]),
    ranking: texto('Ranking'),
    justificativa: texto('Justificativa'),
    statusAC: texto('Status AC'),
    observacao: texto('Observação'),
    retorno: texto('Retorno'),
    cancelada: cancelada
  };
}

function pendListar_() {
  var t = pendLerAba_();
  var cId = t.indice['ID'];
  var vendas = [];
  for (var i = 0; i < t.n; i++) {
    if (!String(t.exibidos[i][cId]).trim()) continue;
    vendas.push(pendVendaDaLinha_(t, i));
  }
  return {
    ok: true,
    vendas: vendas,
    salesforceAtualizadoEm: PropertiesService.getScriptProperties().getProperty(PEND_PROP_ATUALIZACAO) || null
  };
}

function pendAcharLinha_(t, id) {
  var alvo = String(id || '').trim();
  var cId = t.indice['ID'];
  if (alvo) {
    for (var i = 0; i < t.n; i++) if (String(t.exibidos[i][cId]).trim() === alvo) return i;
  }
  throw new PendFalha('nao_encontrada', 'Essa venda não está mais no relatório.');
}

function pendPintar_(id, cancelar) {
  var t = pendLerAba_();
  var i = pendAcharLinha_(t, id);
  var linha = PEND_LINHA_CABECALHO + 1 + i;
  t.aba.getRange(linha, 1, 1, t.ultimaColunaDados)
    .setFontColor(cancelar ? '#ff0000' : '#000000')
    .setFontLine(cancelar ? 'line-through' : 'none');
  if ('__ORDEM_CANCELADA' in t.indice) {
    t.aba.getRange(linha, t.indice['__ORDEM_CANCELADA'] + 1).setValue(cancelar ? 1 : 0);
  }
  var venda = pendVendaDaLinha_(t, i);
  venda.cancelada = cancelar;
  return { ok: true, venda: venda };
}

/* texto livre nunca vira formula na planilha */
function pendTextoSeguro_(v) {
  var s = String(v === null || v === undefined ? '' : v).slice(0, PEND_MAX_TEXTO);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

function pendEditar_(id, observacao, retorno) {
  var t = pendLerAba_();
  var i = pendAcharLinha_(t, id);
  var linha = PEND_LINHA_CABECALHO + 1 + i;
  var obs = pendTextoSeguro_(observacao);
  var ret = pendTextoSeguro_(retorno);
  t.aba.getRange(linha, t.indice['Observação'] + 1).setValue(obs);
  t.aba.getRange(linha, t.indice['Retorno'] + 1).setValue(ret);
  var venda = pendVendaDaLinha_(t, i);
  venda.observacao = String(observacao || '').slice(0, PEND_MAX_TEXTO).trim();
  venda.retorno = String(retorno || '').slice(0, PEND_MAX_TEXTO).trim();
  return { ok: true, venda: venda };
}

/* Rode no editor antes de implantar: confere colunas e contagens. */
function testePendencias() {
  var r = pendListar_();
  var porFase = {};
  var canceladas = 0;
  r.vendas.forEach(function (v) {
    porFase[v.fase] = (porFase[v.fase] || 0) + 1;
    if (v.cancelada) canceladas++;
  });
  Logger.log('Vendas: %s | canceladas: %s', r.vendas.length, canceladas);
  Logger.log('Por fase: %s', JSON.stringify(porFase));
  Logger.log('Colunas encontradas: %s', JSON.stringify(Object.keys(pendLerAba_().indice)));
  Logger.log('Salesforce atualizado em: %s', r.salesforceAtualizadoEm);
  Logger.log('Exemplo: %s', JSON.stringify(r.vendas[0]));
}

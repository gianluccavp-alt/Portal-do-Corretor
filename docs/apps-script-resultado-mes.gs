/* ============================================================
   RESULTADO DO MES - Google Apps Script Web App
   ------------------------------------------------------------
   Backend da pagina /resultado-mes do Portal do Corretor.
   Fica no MESMO projeto do script que copia os relatorios do Salesforce
   (docs/apps-script-vendas-salesforce.gs) e usa o CONFIG de la.
   Le as abas "VENDAS SPI XIMENES" e "VENDAS SPI 2.0 XIMENES" e devolve so
   as linhas do mes pedido. A senha e conferida AQUI, no servidor: sem ela
   nenhum dado sai da planilha.

   ---------- COMO PUBLICAR (uma vez) ----------
   1. No editor do Apps Script: Arquivos > "+" > Script > nome "ResultadoMes"
      > cole este arquivo > salvar.
   2. Em configurarSenhaResultado, troque COLOQUE_A_SENHA_AQUI pela senha,
      Executar, e apague a senha do codigo de novo.
   3. Selecione testeResultado > Executar > confira o log.
   4. Implantar > Nova implantacao > Tipo: App da Web
        Executar como: Eu
        Quem tem acesso: Qualquer pessoa
   5. Copie a URL que termina em /exec e cole em
      window.RESULTADO_MES_APPS_SCRIPT_URL (assets/config.js).

   Mudou o codigo depois? Implantar > Gerenciar implantacoes > editar >
   Nova versao (a URL /exec continua a mesma).
   Trocar a senha: edite configurarSenhaResultado e rode de novo.
   ============================================================ */

var RES_PROP_SENHA = 'RESULTADO_MES_SENHA';
var RES_CACHE_MIN = 10;

/* O repositorio e PUBLICO: a senha real NAO fica aqui. No editor do Apps
   Script, troque o texto abaixo pela senha, rode uma vez e apague de novo
   (ela fica guardada nas Propriedades do script). */
function configurarSenhaResultado() {
  PropertiesService.getScriptProperties().setProperty(RES_PROP_SENHA, 'COLOQUE_A_SENHA_AQUI');
  Logger.log('Senha da pagina /resultado-mes configurada.');
}

function testeResultado() {
  var mes = Utilities.formatDate(new Date(), CONFIG.fuso, 'yyyy-MM');
  var r = resMes_(mes);
  Logger.log('Mes ' + mes + ': ' + r.abas.map(function (a) { return a.aba + ' ' + a.linhas.length + ' linhas'; }).join(' | ') +
    ' | meses disponiveis: ' + r.meses.length + ' | atualizado: ' + r.atualizadoEm);
}

function ResFalha(codigo, mensagem) { this.codigo = codigo; this.message = mensagem; }

function doPost(e) {
  var resposta;
  try {
    var req = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var senha = PropertiesService.getScriptProperties().getProperty(RES_PROP_SENHA);
    if (!senha || req.senha !== senha) throw new ResFalha('senha', 'Senha incorreta.');
    if (req.acao !== 'mes') throw new ResFalha('interno', 'Acao desconhecida.');
    var mes = String(req.mes || '');
    if (!/^\d{4}-\d{2}$/.test(mes)) mes = Utilities.formatDate(new Date(), CONFIG.fuso, 'yyyy-MM');
    resposta = resMesComCache_(mes);
    resposta.ok = true;
  } catch (err) {
    resposta = err instanceof ResFalha
      ? { ok: false, erro: err.codigo, mensagem: err.message }
      : { ok: false, erro: 'interno', mensagem: String((err && err.message) || err) };
  }
  return ContentService.createTextOutput(JSON.stringify(resposta)).setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return ContentService.createTextOutput(JSON.stringify({ ok: false, erro: 'interno', mensagem: 'Use POST.' }))
    .setMimeType(ContentService.MimeType.JSON);
}

/* A chave do cache muda a cada atualizacao do Salesforce: depois de uma carga
   nova, a proxima consulta ja le a planilha de novo. */
function resMesComCache_(mes) {
  var versao = PropertiesService.getScriptProperties().getProperty('ULTIMA_ATUALIZACAO') || '';
  var chave = 'RES_' + mes + '_' + versao.replace(/\D/g, '');
  var cache = CacheService.getScriptCache();
  var salvo = cache.get(chave);
  if (salvo) return JSON.parse(salvo);
  var r = resMes_(mes);
  var texto = JSON.stringify(r);
  if (texto.length < 95000) cache.put(chave, texto, RES_CACHE_MIN * 60);
  return r;
}

function resMes_(mes) {
  var planilha = SpreadsheetApp.openById(CONFIG.planilhaId);
  var meses = {};
  var abas = CONFIG.relatorios.map(function (rel) {
    var sh = planilha.getSheetByName(rel.aba);
    if (!sh || sh.getLastRow() < 2) return { aba: rel.aba, cabecalho: [], linhas: [] };
    var valores = sh.getDataRange().getValues();
    var cab = valores[0].map(String);
    var iVenda = cab.indexOf('Data da venda');
    var iConf = cab.indexOf('Data Confirmação Venda 2.0');
    if (iVenda < 0 || iConf < 0) throw new ResFalha('interno', 'Aba ' + rel.aba + ' sem as colunas de data.');
    var linhas = [];
    for (var i = 1; i < valores.length; i++) {
      var bruta = valores[i];
      var mVenda = resMesDe_(bruta[iVenda]);
      var mConf = resMesDe_(bruta[iConf]);
      var mesConta = mConf || mVenda;
      if (mesConta) meses[mesConta] = true;
      // devolve tudo que PODE contar no mes; a regra final e aplicada na pagina.
      // So formata as linhas do mes: formatar a planilha toda leva ~30 s.
      if (mVenda === mes || mConf === mes) linhas.push(bruta.map(resCelula_));
    }
    return { aba: rel.aba, cabecalho: cab, linhas: linhas };
  });
  return {
    mes: mes,
    meses: Object.keys(meses).filter(function (m) { return /^\d{4}-\d{2}$/.test(m); }).sort().reverse(),
    atualizadoEm: PropertiesService.getScriptProperties().getProperty('ULTIMA_ATUALIZACAO') || '',
    intervaloMinutos: CONFIG.intervaloMinutos,
    abas: abas
  };
}

/* 'yyyy-MM' de uma celula de data (o fuso do projeto e o de Sao Paulo) */
function resMesDe_(v) {
  if (v instanceof Date) return v.getFullYear() + '-' + ('0' + (v.getMonth() + 1)).slice(-2);
  var m = String(v || '').match(/^(\d{4})-(\d{2})/);
  return m ? m[1] + '-' + m[2] : '';
}

function resCelula_(v) {
  if (v instanceof Date) {
    var temHora = v.getHours() || v.getMinutes() || v.getSeconds();
    return Utilities.formatDate(v, CONFIG.fuso, temHora ? "yyyy-MM-dd'T'HH:mm" : 'yyyy-MM-dd');
  }
  return v;
}

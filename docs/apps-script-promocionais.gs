/* ============================================================
   PROMOCIONAIS - Google Apps Script Web App
   ------------------------------------------------------------
   Grava a lista de unidades marcadas como promocionais na pagina
   /promocionais do Portal do Corretor numa aba da propria planilha
   ("Promocionais"), em vez de PropertiesService - assim o dado fica
   auditavel/editavel na planilha, e o site le essa aba via CSV
   publicado (nao depende deste Web App para leitura).

   Este script cuida SO da escrita (doPost). O doGet fica so como
   fallback/debug manual - o site e a pagina /promocionais leem via
   CSV publicado (assets/config.js -> PROMO_CSV_URL).

   ---------- COMO PUBLICAR (uma vez) ----------
   1. Acesse https://script.google.com  ->  Novo projeto
   2. Apague o conteudo e cole este arquivo inteiro
   3. Troque SENHA pelo mesmo valor de window.PROMO_SENHA (assets/config.js)
   4. Confira SHEET_ID (e o mesmo ID que aparece em SHEET_CSV_URL, em
      assets/config.js)
   5. Implantar  ->  Nova implantacao
        Tipo: App da Web
        Executar como: Eu
        Quem tem acesso: Qualquer pessoa
   6. Copie a URL que termina em /exec
   7. Cole em window.PROMO_APPS_SCRIPT_URL (assets/config.js) e faca deploy

   Ao mudar a SENHA ou o codigo depois, use "Gerenciar implantacoes"
   -> editar -> Nova versao (a URL /exec continua a mesma).

   ---------- PUBLICAR A ABA COMO CSV (leitura) ----------
   Na planilha: Arquivo > Compartilhar > Publicar na Web > selecionar a aba
   "Promocionais" > formato CSV > Publicar > marcar "Republicar
   automaticamente quando alteracoes forem feitas". Cole a URL gerada em
   window.PROMO_CSV_URL (assets/config.js).
   ============================================================ */

var SENHA    = '3815Comercial!';   // == window.PROMO_SENHA
var SHEET_ID = '1hXgz1AbzYeaP2xLbM5Vj9wcM-0CWd98FG4PY5ZusJac'; // == ID em SHEET_CSV_URL
var ABA      = 'Promocionais';
var CABECALHO = ['Empreendimento', 'Identificador', 'ValorAssociativoNoMomento', 'ValorTabelaDiretaNoMomento', 'AtualizadoEm'];

function _json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// Pega a aba "Promocionais", criando com o cabecalho se ainda nao existir.
function _aba() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName(ABA);
  if (!sh) {
    sh = ss.insertSheet(ABA);
    sh.appendRow(CABECALHO);
  }
  return sh;
}

// GET: fallback/debug manual (o site le via CSV publicado, nao por aqui).
function doGet() {
  var sh = _aba();
  var vals = sh.getDataRange().getValues();
  var unidades = [];
  for (var i = 1; i < vals.length; i++) {
    var r = vals[i];
    if (!r[1]) continue;
    unidades.push({
      emp: r[0], identificador: r[1],
      associativo: r[2], tabelaDireta: r[3], atualizadoEm: r[4]
    });
  }
  return _json({ unidades: unidades });
}

// POST protegido por senha: substitui a aba inteira pelas unidades enviadas.
// Corpo esperado (string JSON):
//   { senha, unidades: [{ emp, identificador, associativo, tabelaDireta }] }
function doPost(e) {
  var body;
  try { body = JSON.parse(e.postData.contents); } catch (err) { body = {}; }

  if (body.senha !== SENHA) {
    return _json({ ok: false, erro: 'senha' });
  }

  var unidades = Array.isArray(body.unidades) ? body.unidades : [];
  var agora = new Date().toISOString();

  var linhas = unidades
    .map(function (u) {
      return [
        ('' + (u.emp || '')).trim(),
        ('' + (u.identificador || '')).trim(),
        Number(u.associativo) || 0,
        Number(u.tabelaDireta) || 0,
        agora
      ];
    })
    .filter(function (r) { return r[0] && r[1]; });

  var sh = _aba();
  var ultimaLinha = sh.getLastRow();
  if (ultimaLinha > 1) sh.getRange(2, 1, ultimaLinha - 1, CABECALHO.length).clearContent();
  if (linhas.length > 0) sh.getRange(2, 1, linhas.length, CABECALHO.length).setValues(linhas);

  return _json({ ok: true, total: linhas.length, atualizadoEm: agora });
}

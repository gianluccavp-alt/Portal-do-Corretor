/* ============================================================
   PROMOCIONAIS - Google Apps Script Web App
   ------------------------------------------------------------
   Guarda a lista de "Identificador" das unidades marcadas como
   promocionais na pagina /promocionais do Portal do Corretor.

   NAO usa banco de dados: a lista vive em PropertiesService
   (armazenamento chave-valor embutido no Apps Script).

   ---------- COMO PUBLICAR (uma vez) ----------
   1. Acesse https://script.google.com  ->  Novo projeto
   2. Apague o conteudo e cole este arquivo inteiro
   3. Troque SENHA pelo mesmo valor de window.PROMO_SENHA (assets/config.js)
   4. Implantar  ->  Nova implantacao
        Tipo: App da Web
        Executar como: Eu
        Quem tem acesso: Qualquer pessoa
   5. Copie a URL que termina em /exec
   6. Cole em window.PROMO_APPS_SCRIPT_URL (assets/config.js) e faca deploy

   Ao mudar a SENHA ou o codigo depois, use "Gerenciar implantacoes"
   -> editar -> Nova versao (a URL /exec continua a mesma).
   ============================================================ */

var SENHA = '3815Comercial!';         // == window.PROMO_SENHA
var KEY   = 'promocionais_ribeirao';   // chave no PropertiesService

function _ler() {
  var raw = PropertiesService.getScriptProperties().getProperty(KEY);
  return raw ? JSON.parse(raw) : { identificadores: [], atualizadoEm: null, por: null };
}

function _json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// GET publico: devolve a lista atual. Chamado pelo site e pela pagina /promocionais.
function doGet() {
  return _json(_ler());
}

// POST protegido por senha: substitui a lista inteira pelos identificadores enviados.
// Corpo esperado (string JSON): { senha, identificadores: [...], por }
function doPost(e) {
  var body;
  try { body = JSON.parse(e.postData.contents); } catch (err) { body = {}; }

  if (body.senha !== SENHA) {
    return _json({ ok: false, erro: 'senha' });
  }

  var ids = (body.identificadores || [])
    .map(function (s) { return ('' + s).trim(); })
    .filter(function (s) { return s.length > 0; });

  // dedup preservando ordem
  var vistos = {}, unicos = [];
  for (var i = 0; i < ids.length; i++) {
    if (!vistos[ids[i]]) { vistos[ids[i]] = 1; unicos.push(ids[i]); }
  }

  var data = {
    identificadores: unicos,
    atualizadoEm: new Date().toISOString(),
    por: ('' + (body.por || '')).slice(0, 60)
  };
  PropertiesService.getScriptProperties().setProperty(KEY, JSON.stringify(data));
  return _json({ ok: true, total: unicos.length, atualizadoEm: data.atualizadoEm });
}

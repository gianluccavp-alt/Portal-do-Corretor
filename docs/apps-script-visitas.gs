/* ============================================================
   VISITAS DA RECEPCAO - Google Apps Script Web App
   ------------------------------------------------------------
   Backend de /visitas-recepcao (publica) e /visitas-recepcao-adm
   (com senha). Grava e le a aba VISITAS da planilha de visitas.
   Spec: docs/superpowers/specs/2026-10-09-visitas-recepcao-design.md

   ---------- COMO PUBLICAR (uma vez) ----------
   1. Abra a planilha de visitas > Extensoes > Apps Script.
   2. Cole este arquivo inteiro no Codigo.gs (ou num arquivo "Visitas").
   3. SO NO EDITOR (nunca no repositorio): troque
        var VIS_SENHA_INICIAL = '';
      por a senha do dashboard (minimo de 12 caracteres), selecione configurarSenhaVisitas >
      Executar (autorize) e depois volte a linha para ''.
   4. Se ja existir uma aba VISITAS da versao anterior (v1), apague ou renomeie antes: a v2 cria a aba nova com o cabecalho certo.
   5. Selecione testeVisitas > Executar > confira o log.
   6. Implantar > Nova implantacao > Tipo: App da Web
        Executar como: Eu
        Quem tem acesso: Qualquer pessoa
   7. Copie a URL que termina em /exec e cole em
      window.VISITAS_APPS_SCRIPT_URL no assets/config.js.
   Ao alterar o codigo: Implantar > Gerenciar implantacoes > editar >
   Nova versao (a URL /exec continua a mesma).

   ---------- EMPREENDIMENTOS ----------
   VISITAS_EMPREENDIMENTOS precisa ter os mesmos nomes de
   window.CITIES no assets/config.js. O teste
   tests/visitas-gs.test.js falha se as listas divergirem.
   ============================================================ */

var VIS_ABA = 'VISITAS';
var VIS_FUSO = 'America/Sao_Paulo';
var VIS_PROP_SENHA = 'VISITAS_SENHA';
var VIS_SENHA_INICIAL = '';
var VIS_MAX_TEXTO = 80;
var VIS_MAX_SUGESTOES = 200;
var VIS_DIAS_SUGESTOES = 90;
var VIS_DIAS_RETROATIVOS = 7;
var VIS_MAX_DIAS_LISTAR = 92;
var VIS_TIPOS = { esp: 'Espontânea', house: 'Corretor house', imob: 'Imobiliária' };
var VIS_COLUNAS = ['ID', 'Registrado em', 'Data', 'Horário', 'Empreendimento', 'Cidade', 'Tipo',
  'Nome do cliente', 'CPF', 'Telefone', 'Imobiliária', 'Corretor', 'Gerente de vendas', 'Excluída', 'Token'];
var VIS_MIN_SENHA = 12;
var VISITAS_EMPREENDIMENTOS = [
  { nome: 'Alta Vista Mangará', cidade: 'Campinas' },
  { nome: 'Cores da Mata Mangará', cidade: 'Campinas' },
  { nome: 'Casa Prado Residencial Riva', cidade: 'Campinas' },
  { nome: 'Seleto Amoreiras', cidade: 'Campinas' },
  { nome: 'Universo - Parque Alphaville', cidade: 'Campinas' },
  { nome: 'Village Park', cidade: 'Ribeirão Preto' },
  { nome: 'Village Gaia', cidade: 'Ribeirão Preto' },
  { nome: 'Reserva Direcional Jardim Botânico', cidade: 'Ribeirão Preto' },
  { nome: 'Direcional Conquista Clube Ipiranga', cidade: 'Ribeirão Preto' },
  { nome: 'Conquista Vila da Mata', cidade: 'Sorocaba' }
];

function configurarSenhaVisitas() {
  if (!VIS_SENHA_INICIAL) throw new Error('Preencha VIS_SENHA_INICIAL so no editor antes de executar.');
  /* spec 13.5: o dashboard guarda dado pessoal, a senha precisa ser forte */
  if (String(VIS_SENHA_INICIAL).trim().length < VIS_MIN_SENHA) throw new Error('A senha precisa ter pelo menos ' + VIS_MIN_SENHA + ' caracteres.');
  if (/^comercial123$/i.test(String(VIS_SENHA_INICIAL).trim())) throw new Error('Essa senha e conhecida e fraca demais: escolha outra.');
  PropertiesService.getScriptProperties().setProperty(VIS_PROP_SENHA, VIS_SENHA_INICIAL);
  Logger.log('Senha do /visitas-recepcao-adm configurada. Volte VIS_SENHA_INICIAL para \'\'.');
}

function VisFalha(codigo, mensagem, campo) {
  this.codigo = codigo;
  this.message = mensagem;
  this.campo = campo || null;
}

/* ---------- HTTP ---------- */
function doGet() {
  return visJson_({ ok: false, erro: 'interno', mensagem: 'Use POST.' });
}

function doPost(e) {
  var resposta;
  try {
    var req = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    resposta = visRoteador_(req);
    resposta.ok = true;
  } catch (err) {
    resposta = err instanceof VisFalha
      ? { ok: false, erro: err.codigo, mensagem: err.message, campo: err.campo }
      : { ok: false, erro: 'interno', mensagem: 'Erro interno.' };
    if (!(err instanceof VisFalha)) Logger.log('visitas: ' + String((err && err.name) || 'Error') + (err && err.stack ? '\n' + err.stack : ''));
  }
  return visJson_(resposta);
}

function visJson_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function visRoteador_(req) {
  switch (req.acao) {
    case 'registrar': return visRegistrar_(req);
    case 'dia': return visDia_(req);
    case 'excluir': return visExcluir_(req);
    case 'listar': visConferirSenha_(req.senha); return visListar_(req);
    default: throw new VisFalha('interno', 'Ação desconhecida.');
  }
}

function visConferirSenha_(enviada) {
  var senha = PropertiesService.getScriptProperties().getProperty(VIS_PROP_SENHA);
  if (!senha) throw new VisFalha('interno', 'Senha do dashboard não configurada. Rode configurarSenhaVisitas().');
  if (enviada !== senha) throw new VisFalha('senha', 'Senha incorreta.');
}

function visComLock_(fn) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) throw new VisFalha('ocupado', 'Muitos lançamentos ao mesmo tempo, tente de novo.');
  try { return fn(); } finally { lock.releaseLock(); }
}

/* ---------- helpers puros (testados em tests/visitas-gs.test.js) ---------- */
function visPad_(n) { return (n < 10 ? '0' : '') + n; }
function visIsoParaMs_(iso) { var p = iso.split('-'); return Date.UTC(+p[0], +p[1] - 1, +p[2]); }
function visMsParaIso_(ms) {
  var d = new Date(ms);
  return d.getUTCFullYear() + '-' + visPad_(d.getUTCMonth() + 1) + '-' + visPad_(d.getUTCDate());
}
function visSomarDias_(iso, n) { return visMsParaIso_(visIsoParaMs_(iso) + n * 86400000); }
function visDiasEntre_(de, ate) { return Math.round((visIsoParaMs_(ate) - visIsoParaMs_(de)) / 86400000) + 1; }
function visDataValida_(iso) {
  return /^\d{4}-\d{2}-\d{2}$/.test(iso) && visMsParaIso_(visIsoParaMs_(iso)) === iso;
}
function visIsoParaBr_(iso) { var p = iso.split('-'); return p[2] + '/' + p[1] + '/' + p[0]; }
function visBrParaIso_(br) {
  var m = /^(\d{2})\/(\d{2})\/(\d{4})/.exec(String(br || '').trim());
  return m ? m[3] + '-' + m[2] + '-' + m[1] : '';
}
function visTexto_(s) {
  if (s === null || s === undefined) return '';
  return String(s).replace(/\s+/g, ' ').trim().slice(0, VIS_MAX_TEXTO);
}
function visChave_(s) { return visTexto_(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
function visNeutralizar_(s) {
  var t = String(s === null || s === undefined ? '' : s);
  return /^[=+\-@\t\r]/.test(t) ? "'" + t : t;
}
function visEmpreendimento_(nome) {
  var n = visTexto_(nome);
  for (var i = 0; i < VISITAS_EMPREENDIMENTOS.length; i++) {
    if (VISITAS_EMPREENDIMENTOS[i].nome === n) return VISITAS_EMPREENDIMENTOS[i];
  }
  return null;
}
function visCodigoTipo_(nome) {
  var n = String(nome || '').trim();
  for (var k in VIS_TIPOS) if (VIS_TIPOS.hasOwnProperty(k) && VIS_TIPOS[k] === n) return k;
  return '';
}
function visDigitos_(s) { return String(s === null || s === undefined ? '' : s).replace(/\D/g, ''); }
/* spec 13.1: mesmas regras de assets/visitas.js (paridade testada) */
function visCpfValido_(s) {
  var d = visDigitos_(s);
  if (d.length !== 11 || /^(\d)\1{10}$/.test(d)) return false;
  for (var t = 9; t < 11; t++) {
    var soma = 0;
    for (var i = 0; i < t; i++) soma += Number(d.charAt(i)) * (t + 1 - i);
    if (((soma * 10) % 11) % 10 !== Number(d.charAt(t))) return false;
  }
  return true;
}
function visTelefoneValido_(s) {
  var d = visDigitos_(s);
  return (d.length === 10 || d.length === 11) && Number(d.slice(0, 2)) >= 11;
}
function visPrimeiroNome_(s) { return visTexto_(s).split(' ')[0] || ''; }

/* spec 4.2 + 13.3: o servidor e a autoridade */
function visValidar_(req, hoje, agoraMin) {
  var emp = visEmpreendimento_(req.empreendimento);
  if (!emp) throw new VisFalha('invalido', 'Empreendimento desconhecido.', 'empreendimento');
  var tipo = String(req.tipo || '');
  if (!VIS_TIPOS.hasOwnProperty(tipo)) throw new VisFalha('invalido', 'Tipo de visita inválido.', 'tipo');
  var data = String(req.data || '');
  if (!visDataValida_(data) || data > hoje || data < visSomarDias_(hoje, -VIS_DIAS_RETROATIVOS)) {
    throw new VisFalha('invalido', 'A data precisa estar entre hoje e 7 dias atrás.', 'data');
  }
  var hora = String(req.hora || '');
  var m = /^([01]\d|2[0-3]):([0-5]\d)$/.exec(hora);
  if (!m) throw new VisFalha('invalido', 'Horário inválido.', 'hora');
  if (data === hoje && (+m[1]) * 60 + (+m[2]) > agoraMin + 5) {
    throw new VisFalha('invalido', 'O horário não pode estar no futuro.', 'hora');
  }
  var cliente = visTexto_(req.cliente);
  if (!cliente) throw new VisFalha('invalido', 'Informe o nome do cliente.', 'cliente');
  if (!visCpfValido_(req.cpf)) throw new VisFalha('invalido', 'CPF inválido. Confira os números.', 'cpf');
  if (!visTelefoneValido_(req.telefone)) throw new VisFalha('invalido', 'Telefone com DDD, 10 ou 11 números.', 'telefone');
  var imobiliaria = tipo === 'imob' ? visTexto_(req.imobiliaria) : '';
  if (tipo === 'imob' && !imobiliaria) throw new VisFalha('invalido', 'Informe a imobiliária.', 'imobiliaria');
  var corretor = visTexto_(req.corretor);
  if (!corretor) throw new VisFalha('invalido', 'Informe o nome do corretor.', 'corretor');
  return {
    empreendimento: emp.nome, cidade: emp.cidade, data: data, hora: hora, tipo: tipo,
    cliente: cliente, cpf: visDigitos_(req.cpf), telefone: visDigitos_(req.telefone),
    imobiliaria: imobiliaria, corretor: corretor, gerente: visTexto_(req.gerente)
  };
}

function visAtiva_(l, ix) { return String(l[ix['Excluída']]).trim() !== '1'; }

function visDeLinha_(l, ix) {
  return {
    id: String(l[ix['ID']]),
    data: visBrParaIso_(l[ix['Data']]),
    hora: String(l[ix['Horário']]).trim(),
    empreendimento: String(l[ix['Empreendimento']]),
    cidade: String(l[ix['Cidade']]),
    tipo: visCodigoTipo_(l[ix['Tipo']]),
    cliente: String(l[ix['Nome do cliente']]),
    cpf: visDigitos_(l[ix['CPF']]),
    telefone: visDigitos_(l[ix['Telefone']]),
    imobiliaria: String(l[ix['Imobiliária']]),
    corretor: String(l[ix['Corretor']]),
    gerente: String(l[ix['Gerente de vendas']])
  };
}

/* spec 13.3: so isto sai nas respostas publicas */
function visResumo_(v) {
  return {
    id: v.id, data: v.data, hora: v.hora, empreendimento: v.empreendimento, tipo: v.tipo,
    primeiroNome: visPrimeiroNome_(v.cliente), imobiliaria: v.imobiliaria || '', corretor: v.corretor || ''
  };
}

/* mesmo CPF, mesmo stand e mesma data, entre as linhas ativas */
function visCpfRepetido_(linhas, ix, v) {
  for (var i = 0; i < linhas.length; i++) {
    var l = linhas[i];
    if (!visAtiva_(l, ix)) continue;
    if (visDigitos_(l[ix['CPF']]) === v.cpf && String(l[ix['Empreendimento']]) === v.empreendimento &&
        visBrParaIso_(l[ix['Data']]) === v.data) return true;
  }
  return false;
}

/* nomes distintos (sem caixa/acento), grafia mais frequente, ordem alfabetica */
function visSugestoes_(linhas, ix, desde, coluna) {
  var grupos = Object.create(null), ordem = [];
  linhas.forEach(function (l) {
    if (!visAtiva_(l, ix)) return;
    if (visBrParaIso_(l[ix['Registrado em']]) < desde) return;
    var nome = visTexto_(l[ix[coluna]]), k = visChave_(nome);
    if (!k) return;
    if (!grupos[k]) { grupos[k] = Object.create(null); ordem.push(k); }
    grupos[k][nome] = (grupos[k][nome] || 0) + 1;
  });
  return ordem.map(function (k) {
    var g = grupos[k], melhor = null;
    Object.keys(g).forEach(function (n) { if (melhor === null || g[n] > g[melhor]) melhor = n; });
    return melhor;
  }).sort(function (a, b) { return a.localeCompare(b, 'pt-BR'); }).slice(0, VIS_MAX_SUGESTOES);
}

/* ---------- planilha ---------- */
function visAba_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var aba = ss.getSheetByName(VIS_ABA) || ss.insertSheet(VIS_ABA);
  if (aba.getLastRow() === 0) {
    aba.getRange(1, 1, 1, VIS_COLUNAS.length).setValues([VIS_COLUNAS]).setFontWeight('bold');
    aba.setFrozenRows(1);
  }
  return aba;
}

function visCabecalho_(aba) {
  var largura = aba.getLastColumn();
  var cab = aba.getRange(1, 1, 1, largura).getDisplayValues()[0].map(function (c) { return String(c).trim(); });
  var ix = {};
  cab.forEach(function (n, i) { if (n && !(n in ix)) ix[n] = i; });
  VIS_COLUNAS.forEach(function (n) {
    if (!(n in ix)) throw new VisFalha('coluna', 'Coluna "' + n + '" não encontrada na aba ' + VIS_ABA + '.');
  });
  return { indice: ix, largura: largura };
}

function visLer_() {
  var aba = visAba_();
  var cab = visCabecalho_(aba);
  var n = Math.max(aba.getLastRow() - 1, 0);
  return {
    aba: aba,
    indice: cab.indice,
    largura: cab.largura,
    linhas: n ? aba.getRange(2, 1, n, cab.largura).getDisplayValues() : []
  };
}

function visHoje_() { return Utilities.formatDate(new Date(), VIS_FUSO, 'yyyy-MM-dd'); }

function visHash_(texto) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, texto, Utilities.Charset.UTF_8)
    .map(function (b) { return ('0' + (b & 0xff).toString(16)).slice(-2); }).join('');
}

/* ---------- acoes ---------- */
function visRegistrar_(req) {
  var agora = new Date();
  var hoje = Utilities.formatDate(agora, VIS_FUSO, 'yyyy-MM-dd');
  var hm = Utilities.formatDate(agora, VIS_FUSO, 'HH:mm').split(':');
  var v = visValidar_(req, hoje, (+hm[0]) * 60 + (+hm[1]));
  var token = Utilities.getUuid();
  v.id = 'V' + agora.getTime() + Utilities.getUuid().slice(0, 4).toUpperCase();
  var valores = {
    'ID': v.id,
    'Registrado em': Utilities.formatDate(agora, VIS_FUSO, 'dd/MM/yyyy HH:mm:ss'),
    'Data': visIsoParaBr_(v.data),
    'Horário': v.hora,
    'Empreendimento': v.empreendimento,
    'Cidade': v.cidade,
    'Tipo': VIS_TIPOS[v.tipo],
    'Nome do cliente': v.cliente,
    'CPF': v.cpf,
    'Telefone': v.telefone,
    'Imobiliária': v.imobiliaria,
    'Corretor': v.corretor,
    'Gerente de vendas': v.gerente,
    'Excluída': '0',
    'Token': visHash_(token)
  };
  var repetido = visComLock_(function () {
    var t = visLer_();
    var achou = visCpfRepetido_(t.linhas, t.indice, v);
    var linha = [];
    for (var i = 0; i < t.largura; i++) linha.push('');
    Object.keys(valores).forEach(function (nome) { linha[t.indice[nome]] = visNeutralizar_(valores[nome]); });
    /* formato texto: a planilha nao converte data/hora/CPF e mantem o valor exato */
    var faixa = t.aba.getRange(t.aba.getLastRow() + 1, 1, 1, t.largura);
    faixa.setNumberFormat('@');
    faixa.setValues([linha]);
    return achou;
  });
  return { visita: visResumo_(v), token: token, cpfRepetido: repetido };
}

function visDia_(req) {
  var emp = visEmpreendimento_(req.empreendimento);
  if (!emp) throw new VisFalha('invalido', 'Empreendimento desconhecido.', 'empreendimento');
  var data = String(req.data || '');
  if (!visDataValida_(data)) throw new VisFalha('invalido', 'Data inválida.', 'data');
  var t = visLer_(), ix = t.indice, visitas = [];
  t.linhas.forEach(function (l) {
    if (!visAtiva_(l, ix)) return;
    var v = visDeLinha_(l, ix);
    if (v.empreendimento === emp.nome && v.data === data) visitas.push(visResumo_(v));
  });
  var desde = visSomarDias_(visHoje_(), -VIS_DIAS_SUGESTOES);
  return {
    visitas: visitas,
    sugestoes: {
      imobiliarias: visSugestoes_(t.linhas, ix, desde, 'Imobiliária'),
      corretores: visSugestoes_(t.linhas, ix, desde, 'Corretor'),
      gerentes: visSugestoes_(t.linhas, ix, desde, 'Gerente de vendas')
    }
  };
}

/* spec 4.3: so exclui com o token do proprio navegador e no mesmo dia */
function visExcluir_(req) {
  var id = String(req.id || ''), token = String(req.token || '');
  var hoje = visHoje_();
  return visComLock_(function () {
    var t = visLer_(), ix = t.indice;
    for (var i = 0; i < t.linhas.length; i++) {
      var l = t.linhas[i];
      if (String(l[ix['ID']]) !== id) continue;
      var valido = token && String(l[ix['Token']]) === visHash_(token) &&
        visBrParaIso_(l[ix['Registrado em']]) === hoje;
      if (!valido) break;
      t.aba.getRange(i + 2, ix['Excluída'] + 1).setValue('1');
      return { id: id };
    }
    throw new VisFalha('nao_encontrada', 'Não foi possível excluir este lançamento.');
  });
}

function visListar_(req) {
  var de = String(req.de || ''), ate = String(req.ate || '');
  if (!visDataValida_(de) || !visDataValida_(ate) || de > ate || visDiasEntre_(de, ate) > VIS_MAX_DIAS_LISTAR) {
    throw new VisFalha('invalido', 'Período inválido (máximo de 92 dias).', 'periodo');
  }
  var t = visLer_(), ix = t.indice, visitas = [];
  t.linhas.forEach(function (l) {
    if (!visAtiva_(l, ix)) return;
    var v = visDeLinha_(l, ix);
    if (v.data >= de && v.data <= ate) visitas.push(v);
  });
  return { visitas: visitas };
}

/* ---------- conferencia manual (spec 4.6) ---------- */
function testeVisitas() {
  var hoje = visHoje_();
  var r = visRegistrar_({
    empreendimento: VISITAS_EMPREENDIMENTOS[0].nome, data: hoje,
    hora: Utilities.formatDate(new Date(), VIS_FUSO, 'HH:mm'), tipo: 'imob', imobiliaria: 'TESTE - pode ignorar',
    cliente: 'TESTE - pode ignorar', cpf: '52998224725', telefone: '19999999999', corretor: 'TESTE', gerente: ''
  });
  Logger.log('registrar: ' + JSON.stringify(r.visita) + ' cpfRepetido=' + r.cpfRepetido);
  var d = visDia_({ empreendimento: VISITAS_EMPREENDIMENTOS[0].nome, data: hoje });
  Logger.log('dia: ' + d.visitas.length + ' visita(s); sugestoes: ' + d.sugestoes.imobiliarias.length + ' imob, ' +
    d.sugestoes.corretores.length + ' corretor, ' + d.sugestoes.gerentes.length + ' gerente');
  Logger.log('excluir: ' + JSON.stringify(visExcluir_({ id: r.visita.id, token: r.token })));
  Logger.log('listar: ' + visListar_({ de: hoje, ate: hoje }).visitas.length + ' visita(s) ativas hoje');
}

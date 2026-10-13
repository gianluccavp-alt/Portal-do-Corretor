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
   4. Se ja existir uma aba VISITAS de uma versao anterior, apague ou renomeie antes: a v3 cria as abas VISITAS e RECEPCIONISTAS com o cabecalho certo.
   5. Selecione testeVisitas > Executar > confira o log (cria e apaga uma conta de teste).
   6. Implantar > Nova implantacao > Tipo: App da Web
        Executar como: Eu
        Quem tem acesso: Qualquer pessoa
   7. Copie a URL que termina em /exec e cole em
      window.VISITAS_APPS_SCRIPT_URL no assets/config.js.
   Ao alterar o codigo: Implantar > Gerenciar implantacoes > editar >
   Nova versao (a URL /exec continua a mesma).

   ---------- EMPREENDIMENTOS E PDVS ----------
   VISITAS_EMPREENDIMENTOS tem so os de Ribeirao Preto do
   window.CITIES (assets/config.js) e VISITAS_PDVS precisa bater com
   PDVS de assets/visitas.js. O teste tests/visitas-gs.test.js falha
   se as listas divergirem.

   ---------- CONTAS ----------
   As recepcionistas se cadastram em /visitas-recepcao e o comercial
   aprova em /visitas-recepcao-adm. A senha fica so como hash (aba
   RECEPCIONISTAS) e a sessao vale ate a meia-noite. O segredo da
   sessao (Script Property VISITAS_SEGREDO) e criado sozinho; apagar
   essa propriedade derruba todas as sessoes.
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
var VIS_COLUNAS = ['ID', 'Registrado em', 'Data', 'Horário', 'PDV', 'Empreendimento', 'Cidade', 'Tipo',
  'Nome do cliente', 'CPF', 'Telefone', 'Imobiliária', 'Corretor', 'Gerente de vendas', 'Lançado por', 'Excluída'];
var VIS_MIN_SENHA = 12;
/* ---------- contas das recepcionistas (spec 14) ---------- */
var VIS_ABA_CONTAS = 'RECEPCIONISTAS';
var VIS_COLUNAS_CONTAS = ['Usuário', 'Nome', 'Situação', 'Hash', 'Sal', 'Temporária', 'Criado em', 'Aprovado em', 'Último acesso'];
var VIS_PROP_SEGREDO = 'VISITAS_SEGREDO';
var VIS_ITERACOES = 1000;
var VIS_MAX_FALHAS = 5;
var VIS_BLOQUEIO_S = 900;
var VIS_MAX_PENDENTES = 20;
var VIS_FUSO_MS = 3 * 3600000; /* Brasilia, -03:00 fixo (sem horario de verao desde 2019) */
var VIS_MSG_SESSAO = 'Sua sessão terminou. Entre de novo.';
/* sem 0/O/o, 1/l/I */
var VIS_TEMP_ALFABETO = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789';
var VISITAS_PDVS = ['Zona Sul RP', 'Centro RP'];
/* spec 14.1: por enquanto so Ribeirao Preto */
var VISITAS_EMPREENDIMENTOS = [
  { nome: 'Village Park', cidade: 'Ribeirão Preto' },
  { nome: 'Village Gaia', cidade: 'Ribeirão Preto' },
  { nome: 'Reserva Direcional Jardim Botânico', cidade: 'Ribeirão Preto' },
  { nome: 'Direcional Conquista Clube Ipiranga', cidade: 'Ribeirão Preto' }
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
    if (!(err instanceof VisFalha)) Logger.log('visitas: ' + String((err && err.name) || 'Error') + '\n' + visStackSemMensagem_(err && err.stack));
  }
  return visJson_(resposta);
}

/* so as linhas "at ..." do stack: a primeira linha do V8 repete a mensagem,
   que pode trazer trecho da entrada (CPF, telefone) */
function visStackSemMensagem_(stack) {
  return String(stack || '').split('\n').filter(function (l) { return /^\s*at\s/.test(l); }).join('\n');
}

function visJson_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function visRoteador_(req) {
  switch (req.acao) {
    case 'entrar': return visEntrar_(req);
    case 'cadastrar': return visCadastrar_(req);
    case 'trocarSenha': return visTrocarSenha_(req);
    case 'registrar': return visRegistrar_(req, visSessao_(req, false));
    case 'dia': return visDia_(req, visSessao_(req, false));
    case 'excluir': return visExcluir_(req, visSessao_(req, false));
  }
  /* daqui para baixo: so com a senha do dashboard */
  visConferirSenha_(req.senha);
  switch (req.acao) {
    case 'listar': return visListar_(req);
    case 'contas': return visContas_();
    case 'aprovar': return visMudarSituacao_(req, 'pendente', 'ativa');
    case 'recusar': return visRecusar_(req);
    case 'desativar': return visMudarSituacao_(req, 'ativa', 'desativada');
    case 'reativar': return visMudarSituacao_(req, 'desativada', 'ativa');
    case 'redefinirSenha': return visRedefinirSenha_(req);
    default: throw new VisFalha('interno', 'Ação desconhecida.');
  }
}

function visConferirSenha_(enviada) {
  var senha = PropertiesService.getScriptProperties().getProperty(VIS_PROP_SENHA);
  if (!senha) throw new VisFalha('interno', 'Senha do dashboard não configurada. Rode configurarSenhaVisitas().');
  if (!visIguais_(String(enviada === null || enviada === undefined ? '' : enviada), senha)) throw new VisFalha('senha', 'Senha incorreta.');
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
  var pdv = String(req.pdv || '');
  if (VISITAS_PDVS.indexOf(pdv) < 0) throw new VisFalha('invalido', 'Escolha o PDV.', 'pdv');
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
    pdv: pdv, empreendimento: emp.nome, cidade: emp.cidade, data: data, hora: hora, tipo: tipo,
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
    pdv: String(l[ix['PDV']]),
    empreendimento: String(l[ix['Empreendimento']]),
    cidade: String(l[ix['Cidade']]),
    tipo: visCodigoTipo_(l[ix['Tipo']]),
    cliente: String(l[ix['Nome do cliente']]),
    cpf: visDigitos_(l[ix['CPF']]),
    telefone: visDigitos_(l[ix['Telefone']]),
    imobiliaria: String(l[ix['Imobiliária']]),
    corretor: String(l[ix['Corretor']]),
    gerente: String(l[ix['Gerente de vendas']]),
    lancadoPor: String(l[ix['Lançado por']]).trim()
  };
}

/* spec 14.5: so isto sai nas respostas da recepcao; o usuario de quem lancou nao sai */
function visResumo_(v, usuario) {
  return {
    id: v.id, data: v.data, hora: v.hora, pdv: v.pdv || '', empreendimento: v.empreendimento, tipo: v.tipo,
    primeiroNome: visPrimeiroNome_(v.cliente), imobiliaria: v.imobiliaria || '', corretor: v.corretor || '',
    minha: !!usuario && v.lancadoPor === usuario
  };
}

/* mesmo CPF, mesmo PDV e mesma data, entre as linhas ativas */
function visCpfRepetido_(linhas, ix, v) {
  for (var i = 0; i < linhas.length; i++) {
    var l = linhas[i];
    if (!visAtiva_(l, ix)) continue;
    if (visDigitos_(l[ix['CPF']]) === v.cpf && String(l[ix['PDV']]) === v.pdv &&
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

/* spec 14.3: exclui so a propria visita, registrada hoje */
function visPodeExcluir_(l, ix, id, usuario, hoje) {
  return !!usuario && String(l[ix['ID']]) === id && visAtiva_(l, ix) &&
    String(l[ix['Lançado por']]).trim() === usuario && visBrParaIso_(l[ix['Registrado em']]) === hoje;
}
function visContarPorUsuario_(linhas, ix, desde) {
  var qtd = Object.create(null);
  linhas.forEach(function (l) {
    if (!visAtiva_(l, ix) || visBrParaIso_(l[ix['Data']]) < desde) return;
    var u = String(l[ix['Lançado por']]).trim();
    if (u) qtd[u] = (qtd[u] || 0) + 1;
  });
  return qtd;
}
function visNomesPorUsuario_(t) {
  var nomes = Object.create(null);
  t.linhas.forEach(function (l) { var c = visContaDeLinha_(l, t.indice); if (c.usuario) nomes[c.usuario] = c.nome; });
  return nomes;
}

/* ---------- planilha ---------- */
function visGarantirAba_(nome, colunas) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var aba = ss.getSheetByName(nome) || ss.insertSheet(nome);
  if (aba.getLastRow() === 0) {
    aba.getRange(1, 1, 1, colunas.length).setValues([colunas]).setFontWeight('bold');
    aba.setFrozenRows(1);
  }
  return aba;
}

function visCabecalho_(aba, colunas, nome) {
  var largura = aba.getLastColumn();
  var cab = aba.getRange(1, 1, 1, largura).getDisplayValues()[0].map(function (c) { return String(c).trim(); });
  var ix = {};
  cab.forEach(function (n, i) { if (n && !(n in ix)) ix[n] = i; });
  colunas.forEach(function (n) {
    if (!(n in ix)) throw new VisFalha('coluna', 'Coluna "' + n + '" não encontrada na aba ' + nome + '.');
  });
  return { indice: ix, largura: largura };
}

function visLerAba_(nome, colunas) {
  var aba = visGarantirAba_(nome, colunas);
  var cab = visCabecalho_(aba, colunas, nome);
  var n = Math.max(aba.getLastRow() - 1, 0);
  return {
    aba: aba,
    indice: cab.indice,
    largura: cab.largura,
    linhas: n ? aba.getRange(2, 1, n, cab.largura).getDisplayValues() : []
  };
}
function visLer_() { return visLerAba_(VIS_ABA, VIS_COLUNAS); }
function visLerContas_() { return visLerAba_(VIS_ABA_CONTAS, VIS_COLUNAS_CONTAS); }

/* formato texto: a planilha nao converte data/hora/CPF e mantem o valor exato */
function visAnexar_(t, valores) {
  var linha = [];
  for (var i = 0; i < t.largura; i++) linha.push('');
  Object.keys(valores).forEach(function (nome) { linha[t.indice[nome]] = visNeutralizar_(valores[nome]); });
  var faixa = t.aba.getRange(t.aba.getLastRow() + 1, 1, 1, t.largura);
  faixa.setNumberFormat('@');
  faixa.setValues([linha]);
}
function visAtualizarLinha_(t, i, valores) {
  Object.keys(valores).forEach(function (nome) {
    t.aba.getRange(i + 2, t.indice[nome] + 1).setNumberFormat('@').setValue(visNeutralizar_(valores[nome]));
  });
}
function visAcharConta_(t, usuario) {
  for (var i = 0; i < t.linhas.length; i++) {
    if (String(t.linhas[i][t.indice['Usuário']]).trim() === usuario) return { i: i, conta: visContaDeLinha_(t.linhas[i], t.indice) };
  }
  return null;
}
function visAgoraBr_() { return Utilities.formatDate(new Date(), VIS_FUSO, 'dd/MM/yyyy HH:mm:ss'); }
/* gerado na primeira vez; nunca sai do servidor */
function visSegredo_() {
  var props = PropertiesService.getScriptProperties();
  var s = props.getProperty(VIS_PROP_SEGREDO);
  if (!s) {
    s = Utilities.getUuid() + Utilities.getUuid();
    props.setProperty(VIS_PROP_SEGREDO, s);
  }
  return s;
}

function visHoje_() { return Utilities.formatDate(new Date(), VIS_FUSO, 'yyyy-MM-dd'); }

function visHash_(texto) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, texto, Utilities.Charset.UTF_8)
    .map(function (b) { return ('0' + (b & 0xff).toString(16)).slice(-2); }).join('');
}

/* ---------- contas e sessao: helpers puros (spec 14.5) ---------- */
function visNormUsuario_(s) { return String(s === null || s === undefined ? '' : s).trim().toLowerCase(); }
function visUsuarioValido_(s) { return /^[a-z0-9][a-z0-9._-]{2,29}$/.test(String(s === null || s === undefined ? '' : s)); }
/* mesmas regras e mensagens de assets/visitas.js (paridade testada) */
function visValidarSenha_(senha, usuario) {
  var s = String(senha === null || senha === undefined ? '' : senha);
  if (s.length < 8 || s.length > 72) return 'A senha precisa ter de 8 a 72 caracteres.';
  if (s.toLowerCase() === visNormUsuario_(usuario)) return 'A senha não pode ser igual ao usuário.';
  return '';
}
function visValidarCadastro_(req) {
  var nome = visTexto_(req.nome);
  if (!nome) throw new VisFalha('invalido', 'Informe seu nome completo.', 'nome');
  var usuario = visNormUsuario_(req.usuario);
  if (!visUsuarioValido_(usuario)) throw new VisFalha('invalido', 'Use de 3 a 30 letras minúsculas, números, ponto, hífen ou sublinhado.', 'usuario');
  var msg = visValidarSenha_(req.senha, usuario);
  if (msg) throw new VisFalha('invalido', msg, 'senha');
  return { nome: nome, usuario: usuario, senha: String(req.senha) };
}
/* sem bcrypt no Apps Script: SHA-256 iterado encarece tentativas se a planilha vazar */
function visHashSenha_(senha, sal) {
  var h = visHash_(String(sal) + String(senha));
  for (var i = 1; i < VIS_ITERACOES; i++) h = visHash_(h + sal);
  return h;
}
function visExpiraMeiaNoite_(agoraMs) {
  var dia = Math.floor((agoraMs - VIS_FUSO_MS) / 86400000);
  return (dia + 1) * 86400000 + VIS_FUSO_MS;
}
/* o comeco do hash entra na assinatura: trocar a senha derruba as sessoes abertas */
function visAssinar_(usuario, expira, hash, segredo) {
  return Utilities.base64EncodeWebSafe(
    Utilities.computeHmacSha256Signature(usuario + '.' + expira + '.' + String(hash).slice(0, 12), segredo));
}
function visCriarToken_(usuario, hash, agoraMs, segredo) {
  var expira = visExpiraMeiaNoite_(agoraMs);
  return { token: usuario + '.' + expira + '.' + visAssinar_(usuario, expira, hash, segredo), expira: expira };
}
/* o usuario pode ter ponto: le de tras para frente */
function visLerToken_(token) {
  var partes = String(token === null || token === undefined ? '' : token).split('.');
  if (partes.length < 3) return null;
  var assinatura = partes.pop(), expira = partes.pop(), usuario = partes.join('.');
  if (!assinatura || !/^\d{1,15}$/.test(expira) || !visUsuarioValido_(usuario)) return null;
  return { usuario: usuario, expira: Number(expira), assinatura: assinatura };
}
/* tempo nao depende de onde esta a primeira diferenca */
function visIguais_(a, b) {
  a = String(a); b = String(b);
  var dif = a.length ^ b.length;
  for (var i = 0; i < Math.max(a.length, b.length); i++) dif |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return dif === 0;
}
function visConferirToken_(token, conta, agoraMs, segredo) {
  var p = visLerToken_(token);
  if (!p || !conta || p.usuario !== conta.usuario || agoraMs >= p.expira) return false;
  return visIguais_(p.assinatura, visAssinar_(p.usuario, p.expira, conta.hash, segredo));
}
function visSessaoOk_(token, conta, agoraMs, segredo, permitirTemporaria) {
  if (!conta || conta.situacao !== 'ativa' || (conta.temporaria && !permitirTemporaria)) return false;
  return visConferirToken_(token, conta, agoraMs, segredo);
}
function visSenhaTemporaria_(bytes) {
  var s = '';
  for (var i = 0; i < 9; i++) {
    if (i === 3 || i === 6) s += '-';
    s += VIS_TEMP_ALFABETO.charAt(bytes[i] % VIS_TEMP_ALFABETO.length);
  }
  return s;
}
function visContaDeLinha_(l, ix) {
  return {
    usuario: String(l[ix['Usuário']]).trim(),
    nome: String(l[ix['Nome']]),
    situacao: String(l[ix['Situação']]).trim(),
    hash: String(l[ix['Hash']]).trim(),
    sal: String(l[ix['Sal']]).trim(),
    temporaria: String(l[ix['Temporária']]).trim() === 'sim',
    criadoEm: String(l[ix['Criado em']]),
    aprovadoEm: String(l[ix['Aprovado em']]),
    ultimoAcesso: String(l[ix['Último acesso']])
  };
}
/* o que o dashboard ve de cada conta: nunca hash nem sal */
function visContaPublica_(c, visitas30) {
  return {
    usuario: c.usuario, nome: c.nome, situacao: c.situacao, temporaria: c.temporaria,
    criadoEm: c.criadoEm, ultimoAcesso: c.ultimoAcesso, visitas30: visitas30 || 0
  };
}
function visContarPendentes_(linhas, ix) {
  return linhas.filter(function (l) { return String(l[ix['Situação']]).trim() === 'pendente'; }).length;
}
/* tentativas erradas por usuario, no CacheService */
function visChaveFalhas_(usuario) { return 'vis.falhas.' + usuario; }
function visBloqueado_(cache, usuario) { return Number(cache.get(visChaveFalhas_(usuario)) || 0) >= VIS_MAX_FALHAS; }
function visRegistrarFalha_(cache, usuario) {
  var n = Number(cache.get(visChaveFalhas_(usuario)) || 0) + 1;
  cache.put(visChaveFalhas_(usuario), String(n), VIS_BLOQUEIO_S);
  return n;
}
function visLimparFalhas_(cache, usuario) { cache.remove(visChaveFalhas_(usuario)); }

/* ---------- acoes ---------- */
function visRegistrar_(req, conta) {
  var agora = new Date();
  var hoje = Utilities.formatDate(agora, VIS_FUSO, 'yyyy-MM-dd');
  var hm = Utilities.formatDate(agora, VIS_FUSO, 'HH:mm').split(':');
  var v = visValidar_(req, hoje, (+hm[0]) * 60 + (+hm[1]));
  v.id = 'V' + agora.getTime() + Utilities.getUuid().slice(0, 4).toUpperCase();
  v.lancadoPor = conta.usuario;
  var valores = {
    'ID': v.id,
    'Registrado em': Utilities.formatDate(agora, VIS_FUSO, 'dd/MM/yyyy HH:mm:ss'),
    'Data': visIsoParaBr_(v.data),
    'Horário': v.hora,
    'PDV': v.pdv,
    'Empreendimento': v.empreendimento,
    'Cidade': v.cidade,
    'Tipo': VIS_TIPOS[v.tipo],
    'Nome do cliente': v.cliente,
    'CPF': v.cpf,
    'Telefone': v.telefone,
    'Imobiliária': v.imobiliaria,
    'Corretor': v.corretor,
    'Gerente de vendas': v.gerente,
    'Lançado por': conta.usuario,
    'Excluída': '0'
  };
  var repetido = visComLock_(function () {
    var t = visLer_();
    var achou = visCpfRepetido_(t.linhas, t.indice, v);
    visAnexar_(t, valores);
    return achou;
  });
  return { visita: visResumo_(v, conta.usuario), cpfRepetido: repetido };
}

function visDia_(req, conta) {
  var pdv = String(req.pdv || '');
  if (VISITAS_PDVS.indexOf(pdv) < 0) throw new VisFalha('invalido', 'Escolha o PDV.', 'pdv');
  var data = String(req.data || '');
  if (!visDataValida_(data)) throw new VisFalha('invalido', 'Data inválida.', 'data');
  var t = visLer_(), ix = t.indice, visitas = [];
  t.linhas.forEach(function (l) {
    if (!visAtiva_(l, ix)) return;
    var v = visDeLinha_(l, ix);
    if (v.pdv === pdv && v.data === data) visitas.push(visResumo_(v, conta.usuario));
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

/* spec 14.3: mesma resposta para id inexistente, de outra pessoa ou de outro dia */
function visExcluir_(req, conta) {
  var id = String(req.id || '');
  var hoje = visHoje_();
  return visComLock_(function () {
    var t = visLer_(), ix = t.indice;
    for (var i = 0; i < t.linhas.length; i++) {
      if (String(t.linhas[i][ix['ID']]) !== id) continue;
      if (!visPodeExcluir_(t.linhas[i], ix, id, conta.usuario, hoje)) break;
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
  var nomes = visNomesPorUsuario_(visLerContas_());
  var t = visLer_(), ix = t.indice, visitas = [];
  t.linhas.forEach(function (l) {
    if (!visAtiva_(l, ix)) return;
    var v = visDeLinha_(l, ix);
    if (v.data < de || v.data > ate) return;
    v.lancadoPor = nomes[v.lancadoPor] || v.lancadoPor;
    visitas.push(v);
  });
  return { visitas: visitas };
}

/* ---------- contas (spec 14.2 e 14.5) ---------- */
function visResultadoSessao_(conta, hash) {
  var tk = visCriarToken_(conta.usuario, hash, Date.now(), visSegredo_());
  return { sessao: tk.token, expira: tk.expira, nome: conta.nome, usuario: conta.usuario, trocarSenha: !!conta.temporaria };
}

function visSessao_(req, permitirTemporaria) {
  var p = visLerToken_(req.sessao);
  if (!p) throw new VisFalha('sessao', VIS_MSG_SESSAO);
  var a = visAcharConta_(visLerContas_(), p.usuario);
  if (!a || !visSessaoOk_(String(req.sessao), a.conta, Date.now(), visSegredo_(), permitirTemporaria)) {
    throw new VisFalha('sessao', VIS_MSG_SESSAO);
  }
  return a.conta;
}

function visEntrar_(req) {
  var usuario = visNormUsuario_(req.usuario), senha = String(req.senha === null || req.senha === undefined ? '' : req.senha);
  var falhou = function () { throw new VisFalha('credenciais', 'Usuário ou senha incorretos.'); };
  if (!visUsuarioValido_(usuario)) { visHashSenha_(senha, 'sem-conta'); falhou(); }
  var cache = CacheService.getScriptCache();
  if (visBloqueado_(cache, usuario)) throw new VisFalha('bloqueado', 'Muitas tentativas. Tente de novo em 15 minutos.');
  var a = visAcharConta_(visLerContas_(), usuario);
  /* conta inexistente tambem calcula o hash: mesma demora */
  var hash = visHashSenha_(senha, a ? a.conta.sal : 'sem-conta');
  if (!a || !visIguais_(hash, a.conta.hash)) {
    if (visRegistrarFalha_(cache, usuario) >= VIS_MAX_FALHAS) {
      throw new VisFalha('bloqueado', 'Muitas tentativas. Tente de novo em 15 minutos.');
    }
    falhou();
  }
  visLimparFalhas_(cache, usuario);
  if (a.conta.situacao === 'pendente') throw new VisFalha('pendente', 'Seu cadastro está aguardando aprovação do comercial.');
  if (a.conta.situacao !== 'ativa') throw new VisFalha('desativada', 'Seu acesso foi desativado. Fale com o comercial.');
  visComLock_(function () {
    var t = visLerContas_(), achou = visAcharConta_(t, usuario);
    if (achou) visAtualizarLinha_(t, achou.i, { 'Último acesso': visAgoraBr_() });
  });
  return visResultadoSessao_(a.conta, a.conta.hash);
}

function visCadastrar_(req) {
  var d = visValidarCadastro_(req);
  var sal = Utilities.getUuid(), hash = visHashSenha_(d.senha, sal);
  return visComLock_(function () {
    var t = visLerContas_();
    if (visAcharConta_(t, d.usuario)) throw new VisFalha('invalido', 'Esse usuário já existe.', 'usuario');
    if (visContarPendentes_(t.linhas, t.indice) >= VIS_MAX_PENDENTES) {
      throw new VisFalha('limite', 'Muitos cadastros aguardando aprovação. Fale com o comercial.');
    }
    visAnexar_(t, {
      'Usuário': d.usuario, 'Nome': d.nome, 'Situação': 'pendente', 'Hash': hash, 'Sal': sal,
      'Temporária': 'não', 'Criado em': visAgoraBr_(), 'Aprovado em': '', 'Último acesso': ''
    });
    return { ok: true };
  });
}

function visTrocarSenha_(req) {
  var conta = visSessao_(req, true);
  var nova = String(req.novaSenha === null || req.novaSenha === undefined ? '' : req.novaSenha);
  var msg = visValidarSenha_(nova, conta.usuario);
  if (msg) throw new VisFalha('invalido', msg, 'novaSenha');
  if (visIguais_(visHashSenha_(nova, conta.sal), conta.hash)) {
    throw new VisFalha('invalido', 'A nova senha precisa ser diferente da atual.', 'novaSenha');
  }
  var sal = Utilities.getUuid(), hash = visHashSenha_(nova, sal);
  visComLock_(function () {
    var t = visLerContas_(), a = visAcharConta_(t, conta.usuario);
    if (!a) throw new VisFalha('sessao', VIS_MSG_SESSAO);
    visAtualizarLinha_(t, a.i, { 'Hash': hash, 'Sal': sal, 'Temporária': 'não' });
  });
  conta.temporaria = false;
  return visResultadoSessao_(conta, hash);
}

/* ---------- acoes do comercial sobre as contas (spec 14.5) ---------- */
function visNaoEncontrada_() { return new VisFalha('nao_encontrada', 'Recepcionista não encontrada.'); }

function visContas_() {
  var t = visLerContas_(), v = visLer_();
  var qtd = visContarPorUsuario_(v.linhas, v.indice, visSomarDias_(visHoje_(), -29));
  return {
    contas: t.linhas.map(function (l) {
      var c = visContaDeLinha_(l, t.indice);
      return visContaPublica_(c, qtd[c.usuario] || 0);
    })
  };
}

function visMudarSituacao_(req, de, para) {
  var usuario = visNormUsuario_(req.usuario);
  return visComLock_(function () {
    var t = visLerContas_(), a = visAcharConta_(t, usuario);
    if (!a || a.conta.situacao !== de) throw visNaoEncontrada_();
    var valores = { 'Situação': para };
    if (de === 'pendente') valores['Aprovado em'] = visAgoraBr_();
    visAtualizarLinha_(t, a.i, valores);
    if (para === 'ativa') visLimparFalhas_(CacheService.getScriptCache(), usuario);
    return { usuario: usuario, situacao: para };
  });
}

function visRecusar_(req) {
  var usuario = visNormUsuario_(req.usuario);
  return visComLock_(function () {
    var t = visLerContas_(), a = visAcharConta_(t, usuario);
    if (!a || a.conta.situacao !== 'pendente') throw visNaoEncontrada_();
    t.aba.deleteRow(a.i + 2);
    return { usuario: usuario, situacao: 'recusada' };
  });
}

function visRedefinirSenha_(req) {
  var usuario = visNormUsuario_(req.usuario);
  var bytes = [];
  for (var i = 0; i < 9; i++) bytes.push(parseInt(Utilities.getUuid().slice(0, 2), 16));
  var temp = visSenhaTemporaria_(bytes), sal = Utilities.getUuid(), hash = visHashSenha_(temp, sal);
  return visComLock_(function () {
    var t = visLerContas_(), a = visAcharConta_(t, usuario);
    if (!a || a.conta.situacao === 'pendente') throw visNaoEncontrada_();
    visAtualizarLinha_(t, a.i, { 'Hash': hash, 'Sal': sal, 'Temporária': 'sim' });
    visLimparFalhas_(CacheService.getScriptCache(), usuario);
    return { usuario: usuario, senhaTemporaria: temp };
  });
}

/* ---------- conferencia manual (spec 14.5) ---------- */
function testeVisitas() {
  var usuario = 'teste.visitas', senha = 'teste-' + Utilities.getUuid().slice(0, 8), sal = Utilities.getUuid();
  var hash = visHashSenha_(senha, sal);
  visComLock_(function () {
    var t = visLerContas_();
    if (visAcharConta_(t, usuario)) throw new Error('Ja existe a conta ' + usuario + ': apague a linha na aba ' + VIS_ABA_CONTAS + '.');
    visAnexar_(t, {
      'Usuário': usuario, 'Nome': 'TESTE - pode ignorar', 'Situação': 'ativa', 'Hash': hash, 'Sal': sal,
      'Temporária': 'não', 'Criado em': visAgoraBr_(), 'Aprovado em': visAgoraBr_(), 'Último acesso': ''
    });
  });
  try {
    var s = visEntrar_({ usuario: usuario, senha: senha });
    Logger.log('entrar: ok, sessao ate ' + new Date(s.expira));
    var conta = visSessao_({ sessao: s.sessao }, false);
    var hoje = visHoje_();
    var r = visRegistrar_({
      pdv: VISITAS_PDVS[0], empreendimento: VISITAS_EMPREENDIMENTOS[0].nome, data: hoje,
      hora: Utilities.formatDate(new Date(), VIS_FUSO, 'HH:mm'), tipo: 'imob', imobiliaria: 'TESTE - pode ignorar',
      cliente: 'TESTE - pode ignorar', cpf: '52998224725', telefone: '19999999999', corretor: 'TESTE', gerente: ''
    }, conta);
    Logger.log('registrar: ' + JSON.stringify(r.visita) + ' cpfRepetido=' + r.cpfRepetido);
    var d = visDia_({ pdv: VISITAS_PDVS[0], data: hoje }, conta);
    Logger.log('dia: ' + d.visitas.length + ' visita(s) no PDV ' + VISITAS_PDVS[0]);
    Logger.log('excluir: ' + JSON.stringify(visExcluir_({ id: r.visita.id }, conta)));
    Logger.log('listar: ' + visListar_({ de: hoje, ate: hoje }).visitas.length + ' visita(s) ativas hoje');
    Logger.log('contas: ' + visContas_().contas.length + ' conta(s)');
  } finally {
    visComLock_(function () {
      var t = visLerContas_(), a = visAcharConta_(t, usuario);
      if (a) t.aba.deleteRow(a.i + 2);
    });
    Logger.log('conta de teste apagada');
  }
}

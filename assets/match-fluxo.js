/* Regras do fluxo em linha do tempo do Match de Unidades.
   Funcoes puras, sem DOM: o controller da pagina so chama estas regras.
   As regras de negocio (CAIXA, subsidio, Pro Soluto) ficam em match.js. */
(function (raiz) {
  'use strict';

  var Match = typeof module !== 'undefined' && module.exports ? require('./match.js') : raiz.Match;

  var ETAPAS = ['onde', 'renda', 'ato', 'nascimento', 'perfil', 'politica'];

  function respostasIniciais(cidade) {
    return { cidade: cidade, empId: '', renda: 0, ato: null, dia: '', mes: '', ano: '', fgts: true,
      possuiImovel: false, fatorSocial: false, subsidioAnterior: false, politicaId: 'aco' };
  }

  /* data real (dia/mes/ano de 4 digitos) ou null */
  function dataNascimento(dia, mes, ano) {
    var d = parseInt(dia, 10), m = parseInt(mes, 10), a = parseInt(ano, 10);
    if (!(d > 0) || !(m > 0) || String(ano).length !== 4 || !(a > 0)) return null;
    var dt = new Date(a, m - 1, d);
    if (dt.getFullYear() !== a || dt.getMonth() !== m - 1 || dt.getDate() !== d) return null;
    return dt;
  }

  function perguntasPerfil(r) {
    var p = ['fgts', 'possuiImovel'];
    if (Match.temSubsidio(r.renda, r.possuiImovel)) p.push('fatorSocial', 'subsidioAnterior');
    return p;
  }

  function cliente(r) {
    var sub = Match.temSubsidio(r.renda, r.possuiImovel);
    return { renda: r.renda, ato: r.ato, nascimento: dataNascimento(r.dia, r.mes, r.ano), fgts: r.fgts,
      possuiImovel: r.possuiImovel, fatorSocial: sub && r.fatorSocial === true,
      subsidioAnterior: sub && r.subsidioAnterior === true };
  }

  function validarEtapa(etapa, r, hoje) {
    if (etapa === 'onde') return r.cidade ? null : 'Escolha a cidade.';
    if (etapa === 'renda') return r.renda > 0 ? null : 'Informe a renda bruta do cliente.';
    if (etapa === 'ato') return r.ato !== null && !(r.ato >= 0) ? 'Informe um ato válido ou use o padrão.' : null;
    if (etapa === 'nascimento') {
      var nasc = dataNascimento(r.dia, r.mes, r.ano);
      if (!nasc) return 'Confira a data de nascimento.';
      if (nasc.getTime() > hoje.getTime()) return 'A data de nascimento está no futuro.';
      var msg = Match.validarCliente(cliente(r), r.cidade, hoje);
      /* as demais mensagens dizem respeito a etapas seguintes */
      return msg && /70 anos|Fora das regras/.test(msg) ? msg : null;
    }
    return null;
  }

  function dinheiro(n) { return 'R$ ' + Math.round(n).toLocaleString('pt-BR'); }
  function dois(n) { return (n < 10 ? '0' : '') + n; }

  function idadeAnos(nasc, em) {
    var a = em.getFullYear() - nasc.getFullYear();
    if (em.getMonth() < nasc.getMonth() || (em.getMonth() === nasc.getMonth() && em.getDate() < nasc.getDate())) a--;
    return a;
  }

  function textoAtoPadrao(empId) {
    return empId ? dinheiro(Match.atoDe(empId)) : 'o padrão de cada empreendimento';
  }

  function resumoEtapa(etapa, r, ctx) {
    if (etapa === 'onde') {
      if (!r.empId) return r.cidade + ' · todos';
      var achado = (ctx.emps || []).filter(function (e) { return e.id === r.empId; })[0];
      return achado ? achado.nome : r.empId;
    }
    if (etapa === 'renda') return dinheiro(r.renda) + '/mês';
    if (etapa === 'ato') {
      if (r.ato !== null) return dinheiro(r.ato);
      return r.empId ? 'Padrão · ' + textoAtoPadrao(r.empId) : 'Padrão de cada empreendimento';
    }
    if (etapa === 'nascimento') {
      var nasc = dataNascimento(r.dia, r.mes, r.ano);
      if (!nasc) return '';
      return dois(nasc.getDate()) + '/' + dois(nasc.getMonth() + 1) + '/' + nasc.getFullYear() +
        ' · ' + idadeAnos(nasc, ctx.hoje) + ' anos';
    }
    if (etapa === 'perfil') {
      var p = [r.fgts ? 'FGTS 3 anos' : 'Sem FGTS', r.possuiImovel ? 'Tem imóvel' : 'Sem imóvel'];
      if (Match.temSubsidio(r.renda, r.possuiImovel)) {
        p.push(r.fatorSocial ? 'Com dependente' : 'Sem dependente');
        if (r.subsidioAnterior) p.push('Já teve subsídio');
      }
      return p.join(' · ');
    }
    if (etapa === 'politica') return ctx.nomePolitica(r.politicaId);
    return '';
  }

  function mensal(l) { return l.parcelaFin + l.parcelaPS; }

  function ordenar(linhas, criterio) {
    var chaves = {
      parcela: function (l) { return [mensal(l), l.crTotal]; },
      cr: function (l) { return [l.crTotal, mensal(l)]; },
      andar: function (l) { return [-l.andar, mensal(l)]; }
    };
    var chave = chaves[criterio] || chaves.parcela;
    return linhas.slice().sort(function (a, b) {
      var ka = chave(a), kb = chave(b);
      for (var i = 0; i < ka.length; i++) if (ka[i] !== kb[i]) return ka[i] - kb[i];
      return a.codigo < b.codigo ? -1 : a.codigo > b.codigo ? 1 : 0;
    });
  }

  function melhorMatch(linhas) { return linhas.length ? ordenar(linhas, 'parcela')[0] : null; }

  function achatar(resultado) {
    var out = [];
    resultado.grupos.forEach(function (g) { g.linhas.forEach(function (l) { out.push(l); }); });
    return out;
  }

  function textoPS(l) { return l.parcelaPS > 0 ? dinheiro(l.parcelaPS) + ' × ' + l.prazoPS : 'Sem Pro Soluto'; }

  function textoContagem(total) { return total === 1 ? '1 unidade cabe' : total + ' unidades cabem'; }

  function fotoDe(emp) {
    var slug = emp.sheetName.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
    return 'assets/img/cards/' + slug + '@480.webp';
  }

  /* reais inteiros digitados: tudo antes da primeira virgula, so digitos */
  function reaisDigitados(str) {
    var dig = String(str == null ? '' : str).split(',')[0].replace(/\D/g, '');
    return dig ? parseInt(dig, 10) : 0;
  }

  var api = { reaisDigitados: reaisDigitados, ETAPAS: ETAPAS, respostasIniciais: respostasIniciais, dataNascimento: dataNascimento,
    perguntasPerfil: perguntasPerfil, cliente: cliente, validarEtapa: validarEtapa, resumoEtapa: resumoEtapa,
    textoAtoPadrao: textoAtoPadrao, mensal: mensal, melhorMatch: melhorMatch, ordenar: ordenar,
    achatar: achatar, textoPS: textoPS, textoContagem: textoContagem, fotoDe: fotoDe };

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.MatchFluxo = api;
})(this);

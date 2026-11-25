#!/usr/bin/env node
/* Puxa relatorios do Salesforce pela API de Analytics, SEM o limite de 2.000 linhas.
 *
 * A API devolve no maximo 2.000 linhas por execucao. Quando o relatorio e maior,
 * este script roda o MESMO relatorio varias vezes, cada uma com um intervalo de
 * "Data de criacao" da oportunidade (campo que nunca e vazio), dividindo ao meio
 * ate cada pedaco caber. As regras do relatorio (filtros, logica, colunas) sao as
 * do proprio Salesforce, nada e reescrito aqui.
 *
 * Uso:  node scripts/salesforce-relatorios.mjs [arquivo-saida.json]
 * Le as credenciais do .env (SALESFORCE_INSTANCE_URL, SALESFORCE_SESSION_ID).
 * Para renovar a sessao: ./scripts/salesforce-login.sh
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const RELATORIOS = [
  { aba: 'VENDAS SPI XIMENES', id: '00OU600000OaAcYMAV' },
  { aba: 'VENDAS SPI 2.0 XIMENES', id: '00OU600000O7OxRMAV' },
  { aba: 'Envios D4Sign', id: '00OU600000NJLYHMA5', d4sign: true, particao: 'filtroDeData' },
];

const LIMITE_API = 2000;
const MARGEM = 1800; // so busca detalhes de um pedaco se ele tiver ate isso
const CAMPO_PARTICAO = 'Opportunity.CreatedDate';

function lerEnv(arquivo) {
  const env = {};
  for (const l of fs.readFileSync(arquivo, 'utf8').split('\n')) {
    const m = l.match(/^([A-Z0-9_]+)=(.*)$/);
    if (m) env[m[1]] = m[2];
  }
  return env;
}

export function criarCliente(env) {
  const base = `${env.SALESFORCE_INSTANCE_URL.replace(/\/$/, '')}/services/data/${env.SALESFORCE_API_VERSION || 'v62.0'}`;
  const headers = { Authorization: `Bearer ${env.SALESFORCE_SESSION_ID}`, 'Content-Type': 'application/json' };
  let execucoes = 0;
  async function chamar(caminho, init = {}) {
    const r = await fetch(base + caminho, { ...init, headers });
    const j = await r.json();
    if (r.status === 401) throw new Error('Sessao do Salesforce expirada. Rode ./scripts/salesforce-login.sh');
    if (!r.ok) throw new Error(`Salesforce ${r.status}: ${JSON.stringify(j).slice(0, 400)}`);
    return j;
  }
  return {
    descrever: (id) => chamar(`/analytics/reports/${id}/describe`),
    async executar(id, metadata, detalhes) {
      execucoes++;
      return chamar(`/analytics/reports/${id}?includeDetails=${detalhes}`, {
        method: 'POST',
        body: JSON.stringify({ reportMetadata: metadata }),
      });
    },
    get execucoes() { return execucoes; },
  };
}

const total = (j) => Number(String(j.factMap['T!T'].aggregates.at(-1).value).replace(/\./g, ''));

const iso = (d) => d.toISOString().slice(0, 10);
const meio = (a, b) => new Date(Math.floor((a.getTime() + b.getTime()) / 2 / 86400000) * 86400000);

function comPedaco(desc, ini, fim) {
  // intervalo [ini, fim) na data de criacao, preservando a logica booleana original
  const m = structuredClone(desc.reportMetadata);
  const n = m.reportFilters.length;
  m.reportFilters.push(
    { column: CAMPO_PARTICAO, filterType: 'fieldValue', isRunPageEditable: false, operator: 'greaterOrEqual', value: iso(ini) },
    { column: CAMPO_PARTICAO, filterType: 'fieldValue', isRunPageEditable: false, operator: 'lessThan', value: iso(fim) },
  );
  const base = m.reportBooleanFilter || Array.from({ length: n }, (_, i) => i + 1).join(' AND ');
  m.reportBooleanFilter = `(${base}) AND ${n + 1} AND ${n + 2}`;
  return m;
}

// mesmo [ini, fim), pelo filtro de data do proprio relatorio (pontas inclusivas)
function comPeriodo(desc, ini, fim) {
  const m = structuredClone(desc.reportMetadata);
  m.standardDateFilter = { column: m.standardDateFilter.column, durationValue: 'CUSTOM', startDate: iso(ini), endDate: iso(new Date(fim.getTime() - 86400000)) };
  return m;
}

function achatar(desc, resultado) {
  const info = desc.reportExtendedMetadata.detailColumnInfo;
  const cols = desc.reportMetadata.detailColumns;
  const rows = [];
  for (const [chave, fato] of Object.entries(resultado.factMap)) {
    // tabular guarda as linhas em T!T; nos agrupados, T!T e so o total
    if (chave === 'T!T' && desc.reportMetadata.reportFormat !== 'TABULAR') continue;
    for (const linha of fato.rows || []) {
      rows.push(linha.dataCells.map((c, i) => {
        const tipo = info[cols[i]].dataType, v = c.value;
        if (v === null || v === undefined) return '';
        if (typeof v === 'number' || typeof v === 'boolean') return v;
        if (typeof v === 'object' && 'amount' in v) return v.amount;
        if (tipo === 'date' || tipo === 'datetime') return v;
        return c.label ?? v;
      }));
    }
  }
  return {
    headers: cols.map((c) => info[c].label),
    types: cols.map((c) => info[c].dataType),
    rows,
  };
}

export async function puxarRelatorio(sf, id, log = () => {}, particao = '') {
  const dividir = particao === 'filtroDeData' ? comPeriodo : comPedaco;
  const desc = await sf.descrever(id);
  const nome = desc.reportMetadata.name;
  const completo = await sf.executar(id, desc.reportMetadata, true);
  const esperado = total(completo);
  if (completo.allData) {
    const r = achatar(desc, completo);
    return { nome, ...r, esperado, pedacos: 1 };
  }
  log(`  ${nome}: ${esperado} linhas, API entrega ${LIMITE_API}. Dividindo por data de criacao...`);
  const linhas = [];
  let pedacos = 0, formato;
  async function pedaco(ini, fim) {
    const m = dividir(desc, ini, fim);
    const n = total(await sf.executar(id, m, false));
    if (n === 0) return;
    if (n > MARGEM && fim - ini > 86400000) {
      const c = meio(ini, fim);
      await pedaco(ini, c);
      await pedaco(c, fim);
      return;
    }
    const j = await sf.executar(id, m, true);
    if (!j.allData) throw new Error(`Pedaco ${iso(ini)}..${iso(fim)} ainda cortado (${n} linhas em um unico dia)`);
    const r = achatar(desc, j);
    formato ??= r;
    linhas.push(...r.rows);
    pedacos++;
  }
  const hoje = new Date();
  await pedaco(new Date(Date.UTC(2010, 0, 1)), new Date(Date.UTC(hoje.getUTCFullYear(), hoje.getUTCMonth(), hoje.getUTCDate() + 2)));
  return { nome, headers: formato.headers, types: formato.types, rows: linhas, esperado, pedacos };
}

export async function puxarTodos(sf, log = () => {}) {
  const saida = [];
  for (const { aba, id, particao } of RELATORIOS) {
    const r = await puxarRelatorio(sf, id, log, particao);
    if (r.rows.length !== r.esperado) {
      throw new Error(`${aba}: veio ${r.rows.length} linhas, o Salesforce informa ${r.esperado}. Nao vou gravar dados incompletos.`);
    }
    saida.push({ aba, id, ...r });
  }
  return saida;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  const sf = criarCliente(lerEnv(path.join(raiz, '.env')));
  const t0 = Date.now();
  const dados = await puxarTodos(sf, console.log);
  for (const d of dados) console.log(`${d.aba}: ${d.rows.length} linhas (esperado ${d.esperado}) em ${d.pedacos} execucao(oes) com detalhes`);
  console.log(`${sf.execucoes} execucoes de relatorio no total, ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  const saida = process.argv[2];
  if (saida) {
    fs.writeFileSync(saida, JSON.stringify({ atualizadoEm: new Date().toISOString(), relatorios: dados }));
    console.log('gravado em', saida);
  }
}

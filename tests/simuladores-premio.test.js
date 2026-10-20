const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

/* Carrega assets/simuladores.js num sandbox com a planilha ja no cache da sessao
   (o SimUnidades le o cache antes de ir a rede). */
function carregaUnidades(linhas) {
  const store = { 'sim-unidades-csv-v1': JSON.stringify(linhas) };
  const ctx = {
    window: {},
    sessionStorage: { getItem: (k) => store[k] || null, setItem: () => {} },
    localStorage: { getItem: () => null },
    fetch: () => Promise.reject(new Error('sem rede no teste'))
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 'assets', 'simuladores.js'), 'utf8'), ctx);
  ctx.window.SimUnidades.carregar();
  return ctx.window;
}

const linha = (id, extra) => Object.assign({
  'Nome do Empreendimento': 'Reserva Direcional Jardim Botânico',
  'Status da Unidade': 'Disponível',
  'Identificador': id,
  'Valor Final Com Kit': '420.000,00',
  'B.A. da Unidade': '10.000,00',
  'Folga Campanha G': '0,00',
  'Folga de Tabela': '8.434,34',
  'Valor Comercial Mínimo': '0,00',
  'Valor de Avaliação Bancária': '412.800,00',
  'Área privativa total': '50,00',
  'Final unidade': '6',
  'Andar': '10',
  'Tipo Planta/Área': '2Q C/S'
}, extra || {});

test('associativoSemPremio = associativo − Folga Volta ao Caixa (mesmo "Sem Prêmio" do site de produtos)', () => {
  const w = carregaUnidades([
    linha('BL03-1006', { 'Folga Volta ao Caixa': '4.165,66' }),
    linha('BL03-1007', { 'Folga Volta ao Caixa': '0,00' }),
    linha('BL03-1008')
  ]);
  const u = w.SimUnidades.porEmpreendimento(w.SIM_EMP_POR_ID('botanico'));
  assert.equal(u.total, 3);
  const d = u.detalhes;
  assert.equal(d['BL03-1006'].associativo.toFixed(2), '401565.66', 'associativo com prêmio continua igual');
  assert.equal(d['BL03-1006'].associativoSemPremio.toFixed(2), '397400.00');
  assert.equal(d['BL03-1007'].associativoSemPremio.toFixed(2), '401565.66', 'sem folga: os dois valores são iguais');
  assert.equal(d['BL03-1008'].associativoSemPremio.toFixed(2), '401565.66', 'coluna ausente conta como zero');
});

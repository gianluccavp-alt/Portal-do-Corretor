const test = require('node:test');
const assert = require('node:assert/strict');
const V = require('../assets/visitas.js');
const FIX = require('./fixtures/visitas.json');

const ids = (lista) => lista.map((v) => v.id);
const semData = ({ esp, house, imob, total }) => ({ esp, house, imob, total });
const CABECALHO_CSV = 'Data;Horário;PDV;Empreendimento;Tipo;Cliente;CPF;Telefone;Imobiliária;Corretor;Gerente de vendas;Lançado por';

test('filtrar por período, PDV e empreendimento', () => {
  assert.equal(V.filtrar(FIX, {}).length, 8);
  assert.equal(V.filtrar(FIX, { pdv: 'Todos', empreendimento: 'Todos' }).length, 8);
  assert.deepEqual(ids(V.filtrar(FIX, { pdv: 'Zona Sul RP' })), ['V1', 'V2', 'V5', 'V6', 'V8']);
  assert.deepEqual(ids(V.filtrar(FIX, { pdv: 'Centro RP' })), ['V3', 'V4', 'V7']);
  assert.deepEqual(ids(V.filtrar(FIX, { de: '2026-10-09' })), ['V6', 'V7', 'V8']);
  assert.deepEqual(ids(V.filtrar(FIX, { empreendimento: 'Village Park', ate: '2026-10-07' })), ['V3']);
});

test('totaisPorTipo', () => {
  assert.deepEqual(V.totaisPorTipo(FIX), { esp: 2, house: 2, imob: 4, total: 8 });
  assert.deepEqual(V.totaisPorTipo([]), { esp: 0, house: 0, imob: 0, total: 0 });
  assert.deepEqual(V.totaisPorTipo([{ tipo: 'total' }, { tipo: '' }]), { esp: 0, house: 0, imob: 0, total: 0 });
});

test('porDia inclui dias sem visita', () => {
  const dias = V.porDia(FIX, '2026-10-06', '2026-10-09');
  assert.deepEqual(dias.map((d) => d.data), ['2026-10-06', '2026-10-07', '2026-10-08', '2026-10-09']);
  assert.deepEqual(semData(dias[0]), { esp: 0, house: 0, imob: 0, total: 0 });
  assert.deepEqual(semData(dias[1]), { esp: 1, house: 1, imob: 1, total: 3 });
  assert.deepEqual(semData(dias[2]), { esp: 0, house: 0, imob: 2, total: 2 });
  assert.deepEqual(semData(dias[3]), { esp: 1, house: 1, imob: 1, total: 3 });
});

test('porHora joga visitas fora da faixa para as pontas', () => {
  const horas = V.porHora(FIX, 8, 20);
  assert.equal(horas.length, 13);
  assert.equal(horas[0].hora, 8);
  assert.deepEqual(semData(horas[0]), { esp: 0, house: 0, imob: 1, total: 1 }); /* V4 07:45 */
  assert.equal(horas[1].total, 1); /* V1 09:10 */
  assert.equal(horas[3].total, 2); /* V6 e V7 11h */
  assert.deepEqual(semData(horas[12]), { esp: 0, house: 1, imob: 0, total: 1 }); /* V3 21:30 */
  const soma = horas.reduce((a, h) => a + h.total, 0);
  assert.equal(soma, 8);
});

test('porEmpreendimento mostra zerados e ordena por total', () => {
  const lista = [
    { nome: 'Seleto Amoreiras', cidade: 'Campinas' },
    { nome: 'Village Park', cidade: 'Ribeirão Preto' },
    { nome: 'Alta Vista Mangará', cidade: 'Campinas' },
    { nome: 'Conquista Vila da Mata', cidade: 'Sorocaba' }
  ];
  const linhas = V.porEmpreendimento(FIX, lista);
  assert.deepEqual(linhas.map((l) => [l.nome, l.total]), [
    ['Alta Vista Mangará', 5], ['Village Park', 2], ['Conquista Vila da Mata', 1], ['Seleto Amoreiras', 0]
  ]);
  assert.deepEqual(semData(linhas[0]), { esp: 1, house: 1, imob: 3, total: 5 });
  assert.equal(linhas[0].cidade, 'Campinas');
});

test('rankingImobiliarias agrupa sem caixa e sem acento e usa a grafia mais comum', () => {
  assert.deepEqual(V.rankingImobiliarias(FIX, 5), [
    { nome: 'Imobiliária Ápice', qtd: 3 },
    { nome: 'Imóveis Beta', qtd: 1 }
  ]);
  assert.equal(V.rankingImobiliarias(FIX, 1).length, 1);
});

test('recentes ordena por data e hora, mais novo primeiro', () => {
  assert.deepEqual(ids(V.recentes(FIX, 3)), ['V8', 'V7', 'V6']);
  assert.deepEqual(ids(V.ordenarPorTempo(FIX, false)).slice(0, 2), ['V1', 'V2']);
  assert.equal(FIX[0].id, 'V1'); /* nao muta a entrada */
});

test('gerarCSV: BOM, separador ;, ordem cronológica, aspas, neutralização, PDV e lançado por', () => {
  const visitas = [
    { data: '2026-10-09', hora: '11:50', pdv: 'Centro RP', empreendimento: 'Village Gaia', cidade: 'Ribeirão Preto', tipo: 'esp', cliente: 'Ana Lima', cpf: '52998224725', telefone: '15998765432', imobiliaria: '', corretor: 'Rui', gerente: '', lancadoPor: 'Recepcionista Um' },
    { data: '2026-10-08', hora: '14:00', pdv: 'Zona Sul RP', empreendimento: 'Village Park', cidade: 'Ribeirão Preto', tipo: 'imob', cliente: '=HYPERLINK("x")', cpf: '11144477735', telefone: '1932458890', imobiliaria: 'Imob; Centro', corretor: 'Bia', gerente: 'Gil', lancadoPor: 'Recepcionista Dois' }
  ];
  const esperado = '\uFEFF' + CABECALHO_CSV + '\r\n' +
    '08/10/2026;14:00;Zona Sul RP;Village Park;Imobiliária;"\'=HYPERLINK(""x"")";111.444.777-35;(19) 3245-8890;"Imob; Centro";Bia;Gil;Recepcionista Dois\r\n' +
    '09/10/2026;11:50;Centro RP;Village Gaia;Espontânea;Ana Lima;529.982.247-25;(15) 99876-5432;;Rui;;Recepcionista Um\r\n';
  assert.equal(V.gerarCSV(visitas), esperado);
});

test('gerarCSV vazio tem só o cabeçalho', () => {
  assert.equal(V.gerarCSV([]), '\uFEFF' + CABECALHO_CSV + '\r\n');
});

test('nomeArquivoCSV', () => {
  assert.equal(V.nomeArquivoCSV('2026-10-03', '2026-10-09'), 'visitas-2026-10-03-a-2026-10-09.csv');
});

test('nomes que coincidem com chaves de Object.prototype nao quebram nem poluem', () => {
  const nomes = ['constructor', 'Constructor', '__proto__'];
  const visitas = nomes.map((n, i) => ({
    id: 'P' + i, data: '2026-10-09', hora: '10:00', empreendimento: n, cidade: 'Campinas', tipo: 'imob', imobiliaria: n
  }));
  const rank = V.rankingImobiliarias(visitas, 10);
  assert.equal(rank.reduce((s, r) => s + r.qtd, 0), 3);
  assert.equal(rank.find((r) => r.nome.toLowerCase() === 'constructor').qtd, 2);
  assert.equal(rank.find((r) => r.nome === '__proto__').qtd, 1);
  const emp = V.porEmpreendimento(visitas, nomes.map((n) => ({ nome: n, cidade: 'X' })));
  assert.equal(emp.find((l) => l.nome === 'constructor').total, 1);
  assert.equal(emp.find((l) => l.nome === '__proto__').total, 1);
  const dias = V.porDia([{ data: 'constructor', tipo: 'imob' }], '2026-10-09', '2026-10-09');
  assert.equal(dias[0].total, 0);
  assert.equal(({}).qtd, undefined);
  assert.equal(({}).total, undefined);
});

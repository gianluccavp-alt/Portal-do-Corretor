/* ============================================================
   MAQUETE 3D - modelo provisorio (gerado em codigo)
   ------------------------------------------------------------
   Segue o mesmo contrato do .glb definitivo:
   - malha "unidades" com atributo de vertice "_unit" (float) =
     Maquete.indice(torre, andar, final) da unidade dona do vertice
   - malhas "torre-1", "torre-2", "torre-3" (corpo) e "terreno"
   - metros, Y para cima, origem no centro do terreno
   Proporcoes aproximadas da implantacao do Village Gaia: torres
   em fila (da esquerda para a direita: Torre 3, 2, 1), corpo
   alongado no eixo Z, 2 finais por face.
   ============================================================ */
import * as THREE from 'three';

const PE_DIREITO = 2.9;          // altura de cada andar
const LARGURA = 18;              // corpo da torre no eixo X
const COMPRIMENTO = 42;          // corpo da torre no eixo Z
const ESPACAMENTO = 57;          // distancia entre os centros das torres
const AFASTAMENTO = 0.06;        // vidro levemente para fora da fachada
const MARGEM_H = 0.9;            // folga lateral de cada unidade na fachada
const PEITORIL = 0.55;           // folga inferior do vidro
const VERGA = 0.45;              // folga superior do vidro

/* Posicao de cada final na planta (vista de cima, norte = -Z):
   face norte: 03 a esquerda, 02 a direita; face sul: 06 e 07;
   lateral oeste: 04 (metade norte) e 05; lateral leste: 01 e 08.
   n = normal da face; de/ate = trecho da face em fracao (0..1),
   medido da esquerda para a direita de quem olha a face de fora. */
const FACES = {
  3: { n: [0, 0, -1], de: 0.5, ate: 1 },
  2: { n: [0, 0, -1], de: 0, ate: 0.5 },
  6: { n: [0, 0, 1], de: 0, ate: 0.5 },
  7: { n: [0, 0, 1], de: 0.5, ate: 1 },
  4: { n: [-1, 0, 0], de: 0, ate: 0.5 },
  5: { n: [-1, 0, 0], de: 0.5, ate: 1 },
  1: { n: [1, 0, 0], de: 0.5, ate: 1 },
  8: { n: [1, 0, 0], de: 0, ate: 0.5 }
};

const CORES = {
  corpo: '#E7E2D9',
  cobertura: '#B9B3A8',
  terreo: '#CFC8BC',
  terreno: '#7E9A5C',
  calcada: '#C9C5BC',
  entorno: '#6F8A52',
  copa: '#4F7140',
  tronco: '#6B5440'
};

/* centro X de cada torre na ordem de cfg.torres (Torre 1 a direita) */
export function centroTorreX(grade, torre) {
  const i = grade.torres.indexOf(torre);
  const n = grade.torres.length;
  return ((n - 1) / 2 - i) * ESPACAMENTO;
}

function quadsDasUnidades(grade) {
  const indice = window.Maquete.indice;
  const pos = [];
  const nor = [];
  const uni = [];
  const idx = [];
  const up = new THREE.Vector3(0, 1, 0);
  const n = new THREE.Vector3();
  const t = new THREE.Vector3();
  const c = new THREE.Vector3();
  const cantos = [[-1, -1], [1, -1], [1, 1], [-1, 1]];

  grade.torres.forEach((torre) => {
    const cx = centroTorreX(grade, torre);
    for (let andar = 0; andar < grade.andares; andar++) {
      for (let final = 1; final <= grade.finais; final++) {
        const f = FACES[final];
        if (!f) continue; // layout provisorio so conhece 8 finais
        n.fromArray(f.n);
        t.crossVectors(up, n); // direita de quem olha a face de fora
        const larguraFace = Math.abs(n.x) > 0 ? COMPRIMENTO : LARGURA;
        const meia = Math.abs(n.x) > 0 ? LARGURA / 2 : COMPRIMENTO / 2;
        const meio = ((f.de + f.ate) / 2 - 0.5) * larguraFace;
        const hw = ((f.ate - f.de) * larguraFace) / 2 - MARGEM_H;
        const y0 = andar * PE_DIREITO + PEITORIL;
        const y1 = (andar + 1) * PE_DIREITO - VERGA;
        const hh = (y1 - y0) / 2;
        c.set(cx, y0 + hh, 0).addScaledVector(n, meia + AFASTAMENTO).addScaledVector(t, meio);

        const u = indice(grade, torre, andar, final);
        const base = pos.length / 3;
        cantos.forEach(([sx, sy]) => {
          pos.push(c.x + t.x * hw * sx, c.y + hh * sy, c.z + t.z * hw * sx);
          nor.push(n.x, n.y, n.z);
          uni.push(u);
        });
        idx.push(base, base + 1, base + 2, base, base + 2, base + 3);
      }
    }
  });

  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('_unit', new THREE.Float32BufferAttribute(uni, 1));
  g.setIndex(idx);
  return g;
}

function criarTorre(grade, torre, mats) {
  const altura = grade.andares * PE_DIREITO;
  const cx = centroTorreX(grade, torre);
  const torreGrupo = new THREE.Group();

  const corpo = new THREE.Mesh(new THREE.BoxGeometry(LARGURA, altura, COMPRIMENTO), mats.corpo);
  corpo.name = 'torre-' + torre;
  corpo.position.set(cx, altura / 2, 0);
  corpo.castShadow = true;
  corpo.receiveShadow = true;
  torreGrupo.add(corpo);

  /* platibanda + caixa d'agua: so silhueta */
  const plat = new THREE.Mesh(new THREE.BoxGeometry(LARGURA + 0.6, 1.2, COMPRIMENTO + 0.6), mats.cobertura);
  plat.position.set(cx, altura + 0.6, 0);
  plat.castShadow = true;
  torreGrupo.add(plat);
  const caixa = new THREE.Mesh(new THREE.BoxGeometry(8, 3.2, 10), mats.cobertura);
  caixa.position.set(cx, altura + 1.6 + 1.6, 0);
  caixa.castShadow = true;
  torreGrupo.add(caixa);

  /* base (garden) um pouco maior que o corpo */
  const base = new THREE.Mesh(new THREE.BoxGeometry(LARGURA + 6, 0.4, COMPRIMENTO + 6), mats.calcada);
  base.position.set(cx, 0.2, 0);
  base.receiveShadow = true;
  torreGrupo.add(base);
  return torreGrupo;
}

function criarArvores(grade, mat) {
  const n = grade.torres.length;
  const meiaLargura = ((n - 1) / 2) * ESPACAMENTO + 60;
  const pontos = [];
  /* fileiras de arvores nos corredores entre torres e na borda sul */
  for (let i = 0; i < n - 1; i++) {
    const x = ((n - 1) / 2 - i - 0.5) * ESPACAMENTO;
    for (let z = -36; z <= 36; z += 12) pontos.push([x - 7, z], [x + 7, z + 6]);
  }
  for (let x = -meiaLargura + 10; x <= meiaLargura - 10; x += 16) pontos.push([x, 62]);
  for (let x = -meiaLargura + 10; x <= meiaLargura - 10; x += 22) pontos.push([x + 5, -66]);

  const copaGeo = new THREE.IcosahedronGeometry(2.6, 0);
  const copas = new THREE.InstancedMesh(copaGeo, mat.copa, pontos.length);
  const troncos = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.25, 0.3, 2.4, 6), mat.tronco, pontos.length);
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();
  const s = new THREE.Vector3();
  const p = new THREE.Vector3();
  pontos.forEach(([x, z], i) => {
    const esc = 0.8 + ((i * 37) % 10) / 20;
    s.set(esc, esc * 1.15, esc);
    p.set(x, 2.4 + 2.2 * esc, z);
    q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), i * 1.7);
    copas.setMatrixAt(i, m.compose(p, q, s));
    s.set(1, 1, 1);
    p.set(x, 1.2, z);
    troncos.setMatrixAt(i, m.compose(p, q, s));
  });
  copas.castShadow = true;
  troncos.castShadow = true;
  const g = new THREE.Group();
  g.name = 'arvores';
  g.add(copas, troncos);
  return g;
}

export function criarModeloProvisorio(grade) {
  const mats = {
    corpo: new THREE.MeshStandardMaterial({ color: CORES.corpo, roughness: 0.85 }),
    cobertura: new THREE.MeshStandardMaterial({ color: CORES.cobertura, roughness: 0.9 }),
    calcada: new THREE.MeshStandardMaterial({ color: CORES.calcada, roughness: 0.95 }),
    terreno: new THREE.MeshStandardMaterial({ color: CORES.terreno, roughness: 1 }),
    entorno: new THREE.MeshStandardMaterial({ color: CORES.entorno, roughness: 1 }),
    copa: new THREE.MeshStandardMaterial({ color: CORES.copa, roughness: 0.9, flatShading: true }),
    tronco: new THREE.MeshStandardMaterial({ color: CORES.tronco, roughness: 1 }),
    unidades: new THREE.MeshStandardMaterial({ color: '#ffffff' }) // trocado pela cena
  };

  const grupo = new THREE.Group();
  grupo.name = 'maquete-provisoria';

  const n = grade.torres.length;
  const largTerreno = (n - 1) * ESPACAMENTO + 120;
  const terreno = new THREE.Mesh(new THREE.PlaneGeometry(largTerreno, 150), mats.terreno);
  terreno.name = 'terreno';
  terreno.rotation.x = -Math.PI / 2;
  terreno.receiveShadow = true;
  grupo.add(terreno);

  const entorno = new THREE.Mesh(new THREE.PlaneGeometry(2400, 2400), mats.entorno);
  entorno.name = 'entorno';
  entorno.rotation.x = -Math.PI / 2;
  entorno.position.y = -0.05;
  entorno.receiveShadow = true;
  grupo.add(entorno);

  grade.torres.forEach((t) => grupo.add(criarTorre(grade, t, mats)));
  grupo.add(criarArvores(grade, mats));

  const unidades = new THREE.Mesh(quadsDasUnidades(grade), mats.unidades);
  unidades.name = 'unidades';
  unidades.receiveShadow = true;
  grupo.add(unidades);

  return grupo;
}

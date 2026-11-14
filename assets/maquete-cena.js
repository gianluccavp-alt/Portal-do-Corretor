/* ============================================================
   MAQUETE 3D - cena Three.js
   ------------------------------------------------------------
   criarCena(container, cfg, ev) -> Promise<Cena>
     cfg = emp.maquete ({ modelo, grade, cameras, ... })
     ev  = { onProgresso(p 0..1), onHover(idx|null, x, y), onClick(idx|null) }
   Cena = { pintar(estados, visiveis, modo), destacar(idx|null),
            focarUnidade(idx), irPara(nomeCamera), vistaDaUnidade(idx),
            dispose() }
   ev tambem aceita onSelecao({x, y}|null) - ponto da tela acima da unidade
   selecionada (badge) - e onRumo(graus) - azimute da camera (0 = olhando
   para o norte, 90 = para o leste), para a bussola.

   Pintura: um unico DataTexture (1 texel por idx) lido no shader
   pelo atributo de vertice "_unit" da malha "unidades" (sem um
   material por unidade). Texel = rgb da cor + a = forca do emissivo.

   Qualidade de render: pixel ratio ate 2 (cai em movimento se a GPU nao acompanhar), ACES Filmic, anisotropia maxima nas
   texturas do modelo, luz de ambiente por PMREM (ceu procedural do
   modo) para reflexos suaves, sombra PCF suave ajustada ao terreno e
   renderizada so quando a luz muda (o modelo e estatico).
   ============================================================ */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { criarModeloProvisorio } from './maquete-provisoria.js';

const DRACO_PATH = 'https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/draco/gltf/';
const DUR_ANIM = 800;
/* norte padrao da cena (Gaia): a face +x das torres (finais 1, 2, 7 e 8) e a do nascente, entao leste = +x
   e norte = -z (glTF Y-up). Cada empreendimento pode trocar por cfg.norte = [x, z] (direcao em Three). */
const NORTE_PADRAO = [0, -1];
/* afastamento do fundo da varanda ate o plano da fachada (Gaia: 1,1 m de loggia) + folga; cfg.ateFachada troca */
const ATE_FACHADA_PADRAO = 1.13;

/* cor e forca do emissivo por estado, em cada modo */
/* env*: ceu (PMREM) refletido nos materiais lisos (vidro, guarda-corpo, agua, unidades); envInt = forca.
   A luz difusa de ceu fica com a hemisferica: env em todo o modelo custava ~2x o tempo de GPU. */
const MODOS = {
  noite: {
    ceuTopo: '#050913', ceuBase: '#1c2541', nevoa: '#1c2541', nuvens: 0,
    envTopo: '#1a2440', envHorizonte: '#3a4a74', envChao: '#0b0e15', envInt: 0.6,
    hemiCeu: '#66789f', hemiChao: '#12151c', hemi: 1.15,
    sol: '#a9bcff', solInt: 0.5, exposicao: 1.15, emissivo: 1.6, sombra: false,
    corSel: '#3DDC84', luzJanelas: 1.15, luzInterna: 0.5, luzAcesa: 3.2, luzTela: 1.1, luzAgua: 0.55, luzChao: 1,
    estados: {
      disponivel: ['#FFC872', 1],
      reservada: ['#D9323F', 0.55],
      vendida: ['#232a38', 0],
      fora: ['#323846', 0],
      'sem-dados': ['#323846', 0]
    },
    esmaecido: ['#161b25', 0], misturaEsmaecido: 1
  },
  cores: {
    ceuTopo: '#3F7FCB', ceuBase: '#DCEAF4', nevoa: '#DCEAF4', nuvens: 1,
    envTopo: '#6f9fd6', envHorizonte: '#eef3f7', envChao: '#8f9a7c', envInt: 1.0,
    /* fachadas na sombra nao podem virar preto (modelo real e grafite): ceu (env) + hemi */
    hemiCeu: '#dfeaf7', hemiChao: '#a3a892', hemi: 1.5,
    sol: '#fff1dc', solInt: 4.5, exposicao: 0.9, emissivo: 0.35, sombra: true,
    corSel: '#FFD23F', luzJanelas: 0, luzInterna: 0.16, luzAcesa: 0, luzTela: 0.35, luzAgua: 0, luzChao: 0,
    estados: {
      disponivel: ['#2FA866', 0.5],
      reservada: ['#D9323F', 0.35],
      vendida: ['#8D9197', 0],
      fora: ['#C7CBD0', 0],
      'sem-dados': ['#C7CBD0', 0]
    },
    esmaecido: ['#D3D6DA', 0], misturaEsmaecido: 0.8
  }
};

function criarCeu() {
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false, toneMapped: false,
    uniforms: { topo: { value: new THREE.Color() }, base: { value: new THREE.Color() }, nuvens: { value: 0 } },
    vertexShader: `varying vec3 vDir;
      void main() { vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    /* nuvens: ruido fractal projetado num plano alto. So o ceu paga esse custo, e so nos pixels de ceu */
    fragmentShader: `uniform vec3 topo; uniform vec3 base; uniform float nuvens; varying vec3 vDir;
      float h21(vec2 p) { p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
      float vn(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
        return mix(mix(h21(i), h21(i + vec2(1, 0)), f.x), mix(h21(i + vec2(0, 1)), h21(i + vec2(1, 1)), f.x), f.y); }
      float fbm(vec2 p) { float v = 0.0, a = 0.5; for (int k = 0; k < 5; k++) { v += a * vn(p); p = p * 2.03 + 7.1; a *= 0.5; } return v; }
      void main() {
        vec3 d = normalize(vDir);
        float h = smoothstep(-0.02, 0.55, d.y);
        vec3 c = mix(base, topo, h);
        if (nuvens > 0.0 && d.y > 0.0) {
          vec2 p = d.xz / (d.y + 0.14) * 1.5;
          float n = fbm(p);
          float mass = smoothstep(0.50, 0.74, n);
          float somb = smoothstep(0.50, 0.92, fbm(p + vec2(0.13, 0.09)));
          vec3 corN = mix(vec3(1.0), vec3(0.66, 0.71, 0.79), somb * 0.75);
          c = mix(c, corN, mass * smoothstep(0.015, 0.14, d.y) * 0.93 * nuvens);
        }
        gl_FragColor = vec4(c, 1.0);
      #include <colorspace_fragment>
      }`
  });
  const ceu = new THREE.Mesh(new THREE.SphereGeometry(1500, 32, 16), mat);
  ceu.name = 'ceu';
  ceu.renderOrder = -1;
  return ceu;
}

/* mapa de ambiente (PMREM) a partir de um ceu procedural: luz de ceu suave + reflexos */
function criarAmbiente(renderer, m) {
  const cena = new THREE.Scene();
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false,
    uniforms: {
      topo: { value: new THREE.Color(m.envTopo) },
      horiz: { value: new THREE.Color(m.envHorizonte) },
      chao: { value: new THREE.Color(m.envChao) }
    },
    vertexShader: `varying vec3 vDir;
      void main() { vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `uniform vec3 topo; uniform vec3 horiz; uniform vec3 chao; varying vec3 vDir;
      void main() {
        float y = vDir.y;
        vec3 c = y > 0.0 ? mix(horiz, topo, pow(smoothstep(0.0, 0.7, y), 0.8)) : mix(horiz, chao, smoothstep(0.0, 0.12, -y));
        gl_FragColor = vec4(c, 1.0);
      }`
  });
  cena.add(new THREE.Mesh(new THREE.SphereGeometry(10, 48, 24), mat));
  const pmrem = new THREE.PMREMGenerator(renderer);
  const rt = pmrem.fromScene(cena, 0.02);
  pmrem.dispose();
  mat.dispose();
  cena.children[0].geometry.dispose();
  return rt;
}

/* nitidez das texturas do modelo: anisotropia maxima + mipmaps + espaco de cor correto */
const MAPAS_COR = ['map', 'emissiveMap'];
const MAPAS_DADOS = ['normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'bumpMap'];
function afinarTexturas(modelo, aniso) {
  const vistas = new Set();
  modelo.traverse((o) => {
    if (!o.isMesh) return;
    (Array.isArray(o.material) ? o.material : [o.material]).forEach((mt) => {
      if (!mt) return;
      [...MAPAS_COR, ...MAPAS_DADOS].forEach((k) => {
        const t = mt[k];
        if (!t || vistas.has(t)) return;
        vistas.add(t);
        t.anisotropy = aniso;
        t.generateMipmaps = true;
        t.minFilter = THREE.LinearMipmapLinearFilter;
        t.magFilter = THREE.LinearFilter;
        if (MAPAS_COR.includes(k)) t.colorSpace = THREE.SRGBColorSpace;
        t.needsUpdate = true;
      });
    });
  });
}

/* recortes (folhas, guarda-corpos, alambrado): borda suave com MSAA, sem serrilhado nem halo;
   sombras de contato so escurecem o que esta embaixo */
function ajustarRecortes(modelo) {
  const vistos = new Set();
  modelo.traverse((o) => {
    if (!o.isMesh) return;
    (Array.isArray(o.material) ? o.material : [o.material]).forEach((mt) => {
      if (!mt || vistos.has(mt)) return;
      vistos.add(mt);
      if (mt.alphaTest > 0) {
        mt.alphaToCoverage = true;
        mt.alphaTest = 0.35;
      }
      /* folhagem: o verso do cartao recebe a mesma luz da frente (sem riscos escuros nas copas) */
      if (/^(folha_|fronde|touceira|flores_)/.test(mt.name || '')) {
        mt.onBeforeCompile = (shader) => {
          shader.fragmentShader = shader.fragmentShader.replace('#include <normal_fragment_begin>',
            THREE.ShaderChunk.normal_fragment_begin.replace(/gl_FrontFacing \? 1\.0 : - 1\.0/, '1.0'));
        };
        mt.customProgramCacheKey = () => 'folhagem';
        mt.needsUpdate = true;
      }
      if (/^sombra_contato/.test(mt.name || '')) {
        mt.depthWrite = false;
        mt.polygonOffset = true;
        mt.polygonOffsetFactor = -1;
        mt.polygonOffsetUnits = -1;
        mt.vertexColors = false;
      }
    });
    if (/^vegetacao|^sombra/.test(o.name)) o.renderOrder = 1;
  });
}

/* material compartilhado da malha "unidades": cor por texel do DataTexture */
function criarMaterialUnidades(tex, uni) {
  const mat = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 0.22, metalness: 0.15 });
  mat.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, uni, { uEstados: { value: tex } });
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nattribute float _unit;\nvarying float vUnit;')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nvUnit = _unit;');
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>
        varying float vUnit;
        uniform sampler2D uEstados;
        uniform float uSel;
        uniform float uHover;
        uniform float uEmissivo;
        uniform float uPulso;
        uniform vec3 uCorSel;`)
      .replace('#include <color_fragment>', `#include <color_fragment>
        /* detalhe do modelo (porta/caixilho em cinza, se houver map) modula a cor do estado */
        vec3 detalhe = diffuseColor.rgb;
        vec4 est = texelFetch(uEstados, ivec2(int(vUnit + 0.5), 0), 0);
        vec3 emissUn = est.rgb * est.a * uEmissivo * detalhe;
        diffuseColor.rgb = est.rgb * detalhe;
        if (abs(vUnit - uSel) < 0.5) {
          diffuseColor.rgb = uCorSel * detalhe;
          emissUn = uCorSel * (0.55 + 0.45 * uPulso) * detalhe;
        } else if (abs(vUnit - uHover) < 0.5) {
          diffuseColor.rgb = mix(diffuseColor.rgb, vec3(1.0), 0.45);
          emissUn += vec3(0.22);
        }`)
      .replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\ntotalEmissiveRadiance += emissUn;');
  };
  mat.customProgramCacheKey = () => 'maquete-unidades';
  return mat;
}

async function carregarGLB(url, onProgresso) {
  const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
  const { DRACOLoader } = await import('three/addons/loaders/DRACOLoader.js');
  const draco = new DRACOLoader().setDecoderPath(DRACO_PATH);
  const loader = new GLTFLoader().setDRACOLoader(draco);
  try {
    const gltf = await new Promise((ok, falha) => loader.load(url, ok, (e) => {
      if (e.lengthComputable && e.total) onProgresso(Math.min(0.99, e.loaded / e.total));
    }, falha));
    return gltf.scene;
  } finally {
    draco.dispose();
  }
}

/* malhas que formam "unidades" (no glTF pode virar Group com varias primitivas) */
function malhasDeUnidades(modelo) {
  const raiz = modelo.getObjectByName('unidades');
  if (!raiz) throw new Error('Modelo sem a malha "unidades"');
  const lista = [];
  raiz.traverse((o) => { if (o.isMesh) lista.push(o); });
  lista.forEach((m) => {
    const g = m.geometry;
    /* o GLTFLoader expoe "_UNIT" como "_unit"; aceita os dois */
    if (!g.getAttribute('_unit') && g.getAttribute('_UNIT')) g.setAttribute('_unit', g.getAttribute('_UNIT'));
    if (!g.getAttribute('_unit')) throw new Error('Malha "unidades" sem o atributo _unit');
    if (!g.getAttribute('normal')) g.computeVertexNormals();
  });
  return lista;
}

/* centro e normal media de cada unidade, em coordenadas de mundo */
function mapearUnidades(malhas, total) {
  const soma = new Float32Array(total * 3);
  const norm = new Float32Array(total * 3);
  const min = new Float32Array(total * 3).fill(Infinity);
  const max = new Float32Array(total * 3).fill(-Infinity);
  const cont = new Uint32Array(total);
  const v = new THREE.Vector3();
  const n = new THREE.Vector3();
  malhas.forEach((m) => {
    m.updateWorldMatrix(true, false);
    const nm = new THREE.Matrix3().getNormalMatrix(m.matrixWorld);
    const p = m.geometry.getAttribute('position');
    const no = m.geometry.getAttribute('normal');
    const un = m.geometry.getAttribute('_unit');
    for (let i = 0; i < p.count; i++) {
      const u = Math.round(un.getX(i));
      if (u < 0 || u >= total) continue;
      v.fromBufferAttribute(p, i).applyMatrix4(m.matrixWorld);
      n.fromBufferAttribute(no, i).applyMatrix3(nm);
      soma[u * 3] += v.x; soma[u * 3 + 1] += v.y; soma[u * 3 + 2] += v.z;
      for (let k = 0; k < 3; k++) {
        const c = v.getComponent(k);
        if (c < min[u * 3 + k]) min[u * 3 + k] = c;
        if (c > max[u * 3 + k]) max[u * 3 + k] = c;
      }
      norm[u * 3] += n.x; norm[u * 3 + 1] += n.y; norm[u * 3 + 2] += n.z;
      cont[u]++;
    }
  });
  return (idx) => {
    if (!(idx >= 0 && idx < total) || !cont[idx]) return null;
    const c = new THREE.Vector3(soma[idx * 3], soma[idx * 3 + 1], soma[idx * 3 + 2]).divideScalar(cont[idx]);
    const nn = new THREE.Vector3(norm[idx * 3], 0, norm[idx * 3 + 2]);
    if (nn.lengthSq() < 1e-6) nn.set(0, 0, 1);
    const caixa = new THREE.Box3(new THREE.Vector3().fromArray(min, idx * 3), new THREE.Vector3().fromArray(max, idx * 3));
    return { centro: c, normal: nn.normalize(), caixa };
  };
}

function suavizar(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

export async function criarCena(container, cfg, ev = {}) {
  const onProgresso = ev.onProgresso || (() => {});
  const onHover = ev.onHover || (() => {});
  const onClick = ev.onClick || (() => {});
  const extras = { onSelecao: ev.onSelecao || (() => {}), onRumo: ev.onRumo || (() => {}) };
  const grade = cfg.grade;
  const total = grade.torres.length * grade.andares * grade.finais;

  /* ---------- renderer (lanca erro se nao houver WebGL2) ---------- */
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; // contraste e cores de estado mais vivas que o AgX
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.shadowMap.autoUpdate = false; // cena estatica: sombra so e refeita quando a luz muda
  renderer.domElement.style.display = 'block';
  renderer.domElement.style.touchAction = 'none';
  container.appendChild(renderer.domElement);

  try {
    return await montar(renderer, container, cfg, grade, total, onProgresso, onHover, onClick, extras);
  } catch (e) {
    renderer.dispose();
    renderer.forceContextLoss();
    renderer.domElement.remove();
    throw e;
  }
}

async function montar(renderer, container, cfg, grade, total, onProgresso, onHover, onClick, extras) {
  const nn = cfg.norte || NORTE_PADRAO;
  const NORTE = new THREE.Vector3(nn[0], 0, nn[1]).normalize();
  const ATE_FACHADA = cfg.ateFachada || ATE_FACHADA_PADRAO;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.4, 4000);
  const ceu = criarCeu();
  scene.add(ceu);
  scene.fog = new THREE.Fog('#000000', 320, 950);

  const hemi = new THREE.HemisphereLight();
  scene.add(hemi);
  const sol = new THREE.DirectionalLight();
  const SOL_DIR = new THREE.Vector3(170, 200, 40).normalize(); // do leste (manha): ilumina as varandas +x
  sol.position.copy(SOL_DIR).multiplyScalar(300);
  sol.castShadow = true;
  const maxTex = renderer.capabilities.maxTextureSize || 4096;
  const tamSombra = Math.min(4096, maxTex);
  sol.shadow.mapSize.set(tamSombra, tamSombra);
  Object.assign(sol.shadow.camera, { left: -170, right: 170, top: 170, bottom: -170, near: 10, far: 600 });
  sol.shadow.bias = -0.0002;
  sol.shadow.normalBias = 0.35;
  sol.shadow.radius = 3;
  scene.add(sol);
  scene.add(sol.target);

  /* luz de ambiente por modo (PMREM do ceu procedural) */
  const ambientes = {};
  Object.keys(MODOS).forEach((k) => { ambientes[k] = criarAmbiente(renderer, MODOS[k]); });

  /* ---------- texture de estados + uniforms compartilhados ---------- */
  const dados = new Float32Array(total * 4);
  const tex = new THREE.DataTexture(dados, total, 1, THREE.RGBAFormat, THREE.FloatType);
  tex.minFilter = THREE.NearestFilter;
  tex.magFilter = THREE.NearestFilter;
  tex.needsUpdate = true;
  const uni = {
    uSel: { value: -1 }, uHover: { value: -1 }, uEmissivo: { value: 1 }, uPulso: { value: 0 },
    uCorSel: { value: new THREE.Color(MODOS.noite.corSel) }
  };
  const matUnidades = criarMaterialUnidades(tex, uni);

  /* camera de sombra justa no terreno + torres (sem a moldura de entorno): mais texels por metro */
  function ajustarSombra(raiz) {
    const caixa = new THREE.Box3();
    raiz.children.forEach((o) => { if (!/^entorno/.test(o.name)) caixa.expandByObject(o); });
    if (caixa.isEmpty()) return;
    const esfera = caixa.getBoundingSphere(new THREE.Sphere());
    const r = Math.max(20, esfera.radius * 1.02);
    sol.target.position.copy(esfera.center);
    sol.position.copy(esfera.center).addScaledVector(SOL_DIR, r + 60);
    Object.assign(sol.shadow.camera, { left: -r, right: r, top: r, bottom: -r, near: 1, far: 2 * r + 120 });
    sol.shadow.camera.updateProjectionMatrix();
    sol.target.updateMatrixWorld();
    renderer.shadowMap.needsUpdate = true;
  }

  /* ---------- modelo ---------- */
  let modelo;
  if (typeof cfg.modelo === 'string' && cfg.modelo) {
    modelo = await carregarGLB(cfg.modelo, onProgresso);
    modelo.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  } else {
    modelo = criarModeloProvisorio(grade);
  }
  scene.add(modelo);
  afinarTexturas(modelo, renderer.capabilities.getMaxAnisotropy());
  ajustarRecortes(modelo);
  /* materiais lisos que ganham reflexo do ceu (o resto e reboco/chao fosco: so luz difusa) */
  const LISOS = /vidro|guarda|agua|veneziana|unidade|inox|espelho|carro_|cromo/i;
  const matsReflexo = new Set([matUnidades]);
  /* janelas de dormitorio (parte de vidro) e banheiro: emissao do modelo, acesa so a noite */
  const matsJanela = new Set();
  modelo.traverse((o) => {
    if (!o.isMesh) return;
    (Array.isArray(o.material) ? o.material : [o.material]).forEach((mt) => {
      if (mt && mt.isMeshStandardMaterial && LISOS.test(mt.name || '')) matsReflexo.add(mt);
      if (mt && mt.emissiveMap && /janela/i.test(mt.name || '')) matsJanela.add(mt);
    });
  });
  /* luzes do lazer a noite. Ambientes sem teto: paredes, pisos e moveis recebem brilho quente proprio
     (sai a custo zero de GPU, sem uma luz real por sala). luz_*: fontes acesas; tela: TV e geladeira;
     agua e pastilha: piscina iluminada; luz_chao: poca de luz somada, invisivel de dia. */
  const luzes = { interno: new Set(), acesa: new Set(), tela: new Set(), agua: new Set(), chao: new Set() };
  modelo.traverse((o) => {
    if (!o.isMesh) return;
    let raiz = o;
    while (raiz.parent && raiz.parent !== modelo) raiz = raiz.parent;
    const mt = o.material;
    const nome = (mt && mt.name) || '';
    if (/^(vidro_lazer|agua|sombra_contato|luz_chao|marcas)/.test(nome)) o.castShadow = false;
    if (!mt || !mt.isMeshStandardMaterial) return;
    if (/^luz_chao/.test(nome)) {
      mt.transparent = true;
      mt.blending = THREE.AdditiveBlending;
      mt.depthWrite = false;
      mt.vertexColors = false;
      mt.polygonOffset = true;
      mt.polygonOffsetFactor = -2;
      mt.polygonOffsetUnits = -2;
      /* so a textura, sem iluminacao: emissivo puro */
      mt.color.set('#000000');
      mt.emissive.set('#ffffff');
      mt.emissiveMap = mt.map;
      luzes.chao.add(mt);
      o.renderOrder = 2;
    } else if (/^luz_/.test(nome)) {
      mt.emissive.copy(mt.color);
      /* com textura (letreiro/logo), a emissao segue a imagem em vez de acender o recorte inteiro de uma cor */
      if (mt.map) mt.emissiveMap = mt.map;
      luzes.acesa.add(mt);
    } else if (/^tela/.test(nome)) {
      mt.emissive.set('#ffffff');
      mt.emissiveMap = mt.map;
      luzes.tela.add(mt);
    } else if (/^(agua|pastilha)/.test(nome)) {
      mt.emissive.set(nome.startsWith('agua') ? '#28a7a2' : '#3a8f8c');
      if (mt.map) mt.emissiveMap = mt.map;
      luzes.agua.add(mt);
    } else if (/^(int_|piso_|carpete|ripado|placa)/.test(nome) || raiz.name === 'moveis') {
      if (/^(metal|cromo|inox|espelho|vidro)/.test(nome)) return;
      mt.emissive.copy(mt.color).multiply(new THREE.Color('#ffd9a8'));
      if (mt.map) mt.emissiveMap = mt.map;
      luzes.interno.add(mt);
    }
  });
  ajustarSombra(modelo);
  const malhasUn = malhasDeUnidades(modelo);
  malhasUn.forEach((m) => {
    /* aproveita a textura de detalhe da malha (porta/caixilho) no material da cena */
    if (!matUnidades.map && m.material && m.material.map) {
      matUnidades.map = m.material.map;
      matUnidades.needsUpdate = true;
    }
    m.material = matUnidades;
    m.castShadow = false;
  });
  const setUn = new Set(malhasUn);
  /* alvos do picking: so o que pode tapar uma unidade (torres). Chao, entorno, arvores e
     guarda-corpos (vazados) ficam de fora - tambem deixa o raycast barato */
  const SEM_PICK = /^(terreno|entorno|guarda-corpo|lazer|moveis|vegetacao|carros|torre-\d-det)/;
  const alvosPick = [];
  modelo.traverse((o) => {
    if (!o.isMesh) return;
    for (let p = o; p && p !== modelo; p = p.parent) if (SEM_PICK.test(p.name)) return;
    alvosPick.push(o);
  });
  const unidadeInfo = mapearUnidades(malhasUn, total);
  onProgresso(1);

  /* ---------- camera + controles ---------- */
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 6;
  controls.maxDistance = 340;
  controls.maxPolarAngle = Math.PI / 2 - 0.06;
  controls.screenSpacePanning = false;

  const cam0 = (cfg.cameras && cfg.cameras.geral) || { pos: [120, 105, 185], alvo: [0, 22, 0] };
  camera.position.fromArray(cam0.pos);
  controls.target.fromArray(cam0.alvo);
  controls.update();

  let anim = null;
  let sujo = true;
  const pedirRender = () => { sujo = true; };
  controls.addEventListener('change', pedirRender);
  controls.addEventListener('start', () => { anim = null; });

  function animarPara(pos, alvo) {
    anim = {
      t0: performance.now(),
      dePos: camera.position.clone(), deAlvo: controls.target.clone(),
      paraPos: pos.clone(), paraAlvo: alvo.clone()
    };
    pedirRender();
  }

  /* ---------- contorno da unidade selecionada (varanda inteira, no plano da fachada) ---------- */
  const contorno = new Line2(new LineGeometry(), new LineMaterial({
    color: MODOS.noite.corSel, linewidth: 3, transparent: true, opacity: 0.95, depthWrite: false
  }));
  contorno.visible = false;
  contorno.renderOrder = 2;
  scene.add(contorno);
  const ancoraSel = new THREE.Vector3(); // topo do contorno: onde a badge aparece
  let vendoDeDentro = false;

  /* cfg.contornos (opcional): fachada de cada unidade em planta, por torre e final ({ pe_direito, torres: { t: { f:
     [[x, z], ...] } } }). Com ela o contorno segue a parede (recuos, blocos salientes, testa) do piso ao teto do
     andar, em vez do retangulo no plano da varanda. Gerado pelo script do modelo (Ipiranga: ipiranga-contornos.json). */
  let contornos = null;
  if (cfg.contornos) {
    fetch(cfg.contornos).then((r) => (r.ok ? r.json() : null)).then((j) => { contornos = j; })
      .catch((e) => console.warn('[maquete] contornos:', e));
  }

  function contornoDaFachada(idx) {
    if (!contornos) return null;
    const f = (idx % grade.finais) + 1;
    const resto = Math.floor(idx / grade.finais);
    const andar = resto % grade.andares;
    const t = grade.torres[Math.floor(resto / grade.andares)];
    const planta = contornos.torres[String(t)] && contornos.torres[String(t)][String(f)];
    if (!planta || planta.length < 2) return null;
    const pd = contornos.pe_direito;
    const y0 = andar * pd + (andar ? 0.02 : 0.1);
    const y1 = (andar + 1) * pd - 0.02;
    const base = planta.map(([x, z]) => new THREE.Vector3(x, y0, z));
    const topo = planta.map(([x, z]) => new THREE.Vector3(x, y1, z)).reverse();
    const pts = base.concat(topo, [base[0]]);
    /* badge: no topo, sobre o meio do trecho de fachada */
    const meio = planta[Math.floor((planta.length - 1) / 2)];
    const prox = planta[Math.floor((planta.length - 1) / 2) + 1] || meio;
    const ancora = new THREE.Vector3((meio[0] + prox[0]) / 2, y1, (meio[1] + prox[1]) / 2);
    return { pts, ancora };
  }

  function montarContorno(idx) {
    const info = unidadeInfo(idx);
    if (!info) { contorno.visible = false; return; }
    const fach = contornoDaFachada(idx);
    if (fach) {
      contorno.geometry.dispose();
      contorno.geometry = new LineGeometry().setPositions(fach.pts.flatMap((v) => v.toArray()));
      contorno.computeLineDistances();
      ancoraSel.copy(fach.ancora);
      contorno.visible = !vendoDeDentro;
      return;
    }
    const n = info.normal;
    const t = new THREE.Vector3(0, 1, 0).cross(n).normalize(); // horizontal no plano da fachada
    const tam = info.caixa.getSize(new THREE.Vector3());
    const meia = Math.abs(tam.dot(t)) / 2 + 0.1;              // quad tem 10 cm de folga de cada lado
    const base = info.caixa.min.y - 0.5;                       // laje + peitoril abaixo do quad
    const topo = info.caixa.max.y;
    const c = info.centro.clone().addScaledVector(n, ATE_FACHADA);
    const p = (s, y) => c.clone().addScaledVector(t, s).setY(y);
    const pts = [p(-meia, base), p(meia, base), p(meia, topo), p(-meia, topo), p(-meia, base)];
    contorno.geometry.dispose();
    contorno.geometry = new LineGeometry().setPositions(pts.flatMap((v) => v.toArray()));
    contorno.computeLineDistances();
    ancoraSel.copy(c).setY(topo);
    contorno.visible = !vendoDeDentro;
  }

  const projetado = new THREE.Vector3();
  function avisarSelecao() {
    if (uni.uSel.value < 0 || vendoDeDentro) { extras.onSelecao(null); return; }
    projetado.copy(ancoraSel).project(camera);
    if (projetado.z > 1 || Math.abs(projetado.x) > 1.2 || Math.abs(projetado.y) > 1.2) { extras.onSelecao(null); return; }
    const r = el.getBoundingClientRect();
    extras.onSelecao({ x: r.left + (projetado.x + 1) / 2 * r.width, y: r.top + (1 - projetado.y) / 2 * r.height });
  }

  const frente = new THREE.Vector3();
  let rumoAnterior = null;
  function avisarRumo() {
    camera.getWorldDirection(frente);
    frente.y = 0;
    if (frente.lengthSq() < 1e-6) return;
    frente.normalize();
    /* 0 = olhando para o norte, cresce no sentido horario (leste = 90) */
    const leste = new THREE.Vector3().crossVectors(NORTE, new THREE.Vector3(0, 1, 0)); // +x
    const g = Math.round(THREE.MathUtils.radToDeg(Math.atan2(frente.dot(leste), frente.dot(NORTE))));
    if (g !== rumoAnterior) { rumoAnterior = g; extras.onRumo(g); }
  }

  /* ---------- modo (noite/cores) ---------- */
  let modoAtual = null;
  function aplicarModo(modo) {
    if (modo === modoAtual) return;
    modoAtual = modo;
    const m = MODOS[modo];
    ceu.material.uniforms.topo.value.set(m.ceuTopo);
    ceu.material.uniforms.base.value.set(m.ceuBase);
    ceu.material.uniforms.nuvens.value = m.nuvens;
    scene.fog.color.set(m.nevoa);
    hemi.color.set(m.hemiCeu);
    hemi.groundColor.set(m.hemiChao);
    hemi.intensity = m.hemi;
    sol.color.set(m.sol);
    sol.intensity = m.solInt;
    sol.castShadow = m.sombra;
    renderer.shadowMap.needsUpdate = true;
    matsReflexo.forEach((mt) => {
      if (!mt.envMap) mt.needsUpdate = true;
      mt.envMap = ambientes[modo].texture;
      mt.envMapIntensity = m.envInt;
    });
    renderer.toneMappingExposure = m.exposicao;
    uni.uEmissivo.value = m.emissivo;
    uni.uCorSel.value.set(m.corSel);
    matsJanela.forEach((mt) => { mt.emissive.set('#ffffff'); mt.emissiveIntensity = m.luzJanelas; });
    luzes.interno.forEach((mt) => { mt.emissiveIntensity = m.luzInterna; });
    luzes.acesa.forEach((mt) => { mt.emissiveIntensity = m.luzAcesa; });
    luzes.tela.forEach((mt) => { mt.emissiveIntensity = m.luzTela; });
    luzes.agua.forEach((mt) => { mt.emissiveIntensity = m.luzAgua; });
    luzes.chao.forEach((mt) => { mt.visible = m.luzChao > 0; mt.emissiveIntensity = m.luzChao; });
    contorno.material.color.set(m.corSel);
  }

  const semRealce = new Uint8Array(total); // unidades 'fora' nao clareiam no hover
  const cor = new THREE.Color();
  const corEsm = new THREE.Color();
  function pintar(estados, visiveis, modo) {
    const m = MODOS[modo] ? modo : 'noite';
    aplicarModo(m);
    const tab = MODOS[m];
    corEsm.set(tab.esmaecido[0]);
    for (let i = 0; i < total; i++) {
      semRealce[i] = estados[i] === 'fora' || estados[i] === 'inexistente' ? 1 : 0;
      const par = tab.estados[estados[i]] || tab.estados['sem-dados'];
      cor.set(par[0]);
      let forca = par[1];
      if (visiveis && !visiveis.has(i)) {
        cor.lerp(corEsm, tab.misturaEsmaecido);
        forca = 0;
      }
      dados[i * 4] = cor.r; dados[i * 4 + 1] = cor.g; dados[i * 4 + 2] = cor.b; dados[i * 4 + 3] = forca;
    }
    tex.needsUpdate = true;
    pedirRender();
  }

  function destacar(idx) {
    uni.uSel.value = idx == null ? -1 : idx;
    vendoDeDentro = false;
    if (idx == null) contorno.visible = false; else montarContorno(idx);
    avisarSelecao();
    pedirRender();
  }

  function focarUnidade(idx) {
    const info = unidadeInfo(idx);
    if (!info) return;
    const pos = info.centro.clone().addScaledVector(info.normal, 42);
    pos.y = Math.max(4, info.centro.y + 10);
    vendoDeDentro = false;
    contorno.visible = uni.uSel.value === idx;
    animarPara(pos, info.centro);
  }

  function vistaDaUnidade(idx) {
    const info = unidadeInfo(idx);
    if (!info) return;
    const pos = info.centro.clone().addScaledVector(info.normal, 1.2);
    pos.y = info.centro.y + 0.2;
    const alvo = info.centro.clone().addScaledVector(info.normal, 60);
    alvo.y = Math.max(0.5, info.centro.y - 6); // olha levemente para baixo, nunca abaixo do chao
    vendoDeDentro = true;                       // de dentro da varanda nao ha contorno nem badge
    contorno.visible = false;
    animarPara(pos, alvo);
  }

  function irPara(nome) {
    /* cameras da barra ou ambientes do menu Lazer */
    const c = (cfg.cameras && cfg.cameras[nome]) || (cfg.ambientes || []).find((a) => a.id === nome);
    if (!c) { console.warn('[maquete] camera desconhecida:', nome); return; }
    animarPara(new THREE.Vector3().fromArray(c.pos), new THREE.Vector3().fromArray(c.alvo));
  }

  /* ---------- picking (hover/clique) ---------- */
  const ray = new THREE.Raycaster();
  const ponteiro = new THREE.Vector2();
  const el = renderer.domElement;

  function pick(clientX, clientY) {
    const r = el.getBoundingClientRect();
    ponteiro.set(((clientX - r.left) / r.width) * 2 - 1, -((clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ponteiro, camera);
    const hits = ray.intersectObjects(alvosPick, false);
    for (const h of hits) {
      if (!h.object.visible) continue;
      if (!setUn.has(h.object) || !h.face) return null; // algo na frente da unidade
      const u = Math.round(h.object.geometry.getAttribute('_unit').getX(h.face.a));
      return u >= 0 && u < total ? u : null;
    }
    return null;
  }

  let hoverPend = null;
  let hoverIdx = null;
  let ultimoMouse = null; // ultima posicao do mouse sobre o canvas
  let baixo = null;

  function onMove(e) {
    if (e.pointerType !== 'mouse') return;
    ultimoMouse = { x: e.clientX, y: e.clientY };
    hoverPend = ultimoMouse;
  }
  function onLeave() {
    hoverPend = null;
    ultimoMouse = null;
    if (hoverIdx !== null) {
      hoverIdx = null;
      uni.uHover.value = -1;
      pedirRender();
      onHover(null, 0, 0);
    }
  }
  const ativos = new Set();
  function onDown(e) {
    ativos.add(e.pointerId);
    /* botao direito/meio ou segundo dedo (pinca) nao viram clique */
    if (e.button !== 0 || ativos.size > 1) { baixo = null; return; }
    baixo = { id: e.pointerId, x: e.clientX, y: e.clientY, t: performance.now() };
  }
  function onCancel(e) {
    ativos.delete(e.pointerId);
    if (baixo && baixo.id === e.pointerId) baixo = null;
  }
  function onUp(e) {
    ativos.delete(e.pointerId);
    if (!baixo || baixo.id !== e.pointerId) return;
    const dx = e.clientX - baixo.x;
    const dy = e.clientY - baixo.y;
    const curto = performance.now() - baixo.t < 600;
    baixo = null;
    if (dx * dx + dy * dy > 36 || !curto) return; // foi arrasto, nao clique
    onClick(pick(e.clientX, e.clientY));
  }
  el.addEventListener('pointermove', onMove);
  el.addEventListener('pointerleave', onLeave);
  el.addEventListener('pointerdown', onDown);
  el.addEventListener('pointerup', onUp);
  el.addEventListener('pointercancel', onCancel);

  function processarHover() {
    if (!hoverPend) return;
    const { x, y } = hoverPend;
    hoverPend = null;
    const idx = pick(x, y);
    const mudou = idx !== hoverIdx;
    if (mudou) {
      hoverIdx = idx;
      uni.uHover.value = idx == null || semRealce[idx] ? -1 : idx;
      el.style.cursor = idx == null ? '' : 'pointer';
      pedirRender();
    }
    /* com unidade: avisa a cada movimento (etiqueta acompanha o mouse) */
    if (idx !== null || mudou) onHover(idx, x, y);
  }

  /* ---------- tamanho ---------- */
  function redimensionar() {
    const w = container.clientWidth || 1;
    const h = container.clientHeight || 1;
    renderer.setSize(w, h, false);
    el.style.width = '100%';
    el.style.height = '100%';
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    contorno.material.resolution.set(w, h);
    pedirRender();
  }
  const ro = new ResizeObserver(redimensionar);
  ro.observe(container);
  redimensionar();

  /* ---------- resolucao adaptativa: parado sempre nitido; em movimento, se a GPU nao acompanha,
     desce a resolucao ate ficar fluido e volta ao maximo quando a camera para ---------- */
  const RATIO_MAX = Math.min(window.devicePixelRatio || 1, 2);
  const RATIO_MIN = Math.min(1, RATIO_MAX);
  let ratioAtual = RATIO_MAX;
  let ratioMov = RATIO_MAX;
  let tUltimoMov = 0;
  let tQuadroAnt = 0;
  let somaDt = 0;
  let nDt = 0;
  function usarRatio(r) {
    if (r === ratioAtual) return;
    ratioAtual = r;
    renderer.setPixelRatio(r);
    redimensionar();
  }
  function adaptarResolucao(agora, emMovimento) {
    if (emMovimento) {
      usarRatio(ratioMov);
      /* intervalo entre quadros seguidos em movimento; pausas nao contam */
      if (tUltimoMov && agora - tUltimoMov < 100) { somaDt += agora - tQuadroAnt; nDt++; }
      tUltimoMov = agora;
      tQuadroAnt = agora;
      if (nDt >= 24) {
        const media = somaDt / nDt;
        somaDt = 0; nDt = 0;
        if (media > 25 && ratioMov > RATIO_MIN) ratioMov = Math.max(RATIO_MIN, ratioMov * 0.8);
      }
    } else if (ratioAtual !== RATIO_MAX && agora - tUltimoMov > 300) {
      usarRatio(RATIO_MAX);
    }
  }

  /* ---------- loop (so renderiza quando algo muda) ---------- */
  let rodando = true;
  function quadro(agora) {
    if (!rodando) return;
    requestAnimationFrame(quadro);
    let camMudou = false;
    if (anim) {
      const t = Math.min(1, (agora - anim.t0) / DUR_ANIM);
      const k = suavizar(t);
      camera.position.lerpVectors(anim.dePos, anim.paraPos, k);
      controls.target.lerpVectors(anim.deAlvo, anim.paraAlvo, k);
      if (t >= 1) anim = null;
      sujo = true;
      camMudou = true;
    }
    if (controls.update()) { sujo = true; camMudou = true; }
    if (controls.target.y < 0) { controls.target.y = 0; camMudou = true; sujo = true; }
    /* camera andou com o mouse parado: refaz o picking para a etiqueta nao ficar velha */
    if (camMudou && ultimoMouse) hoverPend = ultimoMouse;
    processarHover();
    adaptarResolucao(agora, camMudou);
    if (uni.uSel.value >= 0) {
      uni.uPulso.value = 0.5 + 0.5 * Math.sin(agora / 260);
      sujo = true;
    }
    if (sujo) {
      sujo = false;
      renderer.render(scene, camera);
      if (uni.uSel.value >= 0) avisarSelecao();
      if (camMudou || rumoAnterior === null) avisarRumo();
    }
  }

  pintar(new Array(total).fill('sem-dados'), null, 'cores');
  requestAnimationFrame(quadro);

  function dispose() {
    rodando = false;
    ro.disconnect();
    el.removeEventListener('pointermove', onMove);
    el.removeEventListener('pointerleave', onLeave);
    el.removeEventListener('pointerdown', onDown);
    el.removeEventListener('pointerup', onUp);
    el.removeEventListener('pointercancel', onCancel);
    controls.dispose();
    scene.traverse((o) => {
      if (o.geometry) o.geometry.dispose();
      const mats = Array.isArray(o.material) ? o.material : o.material ? [o.material] : [];
      mats.forEach((m) => {
        Object.values(m).forEach((v) => { if (v && v.isTexture) v.dispose(); });
        m.dispose();
      });
    });
    tex.dispose();
    Object.values(ambientes).forEach((rt) => rt.dispose());
    renderer.dispose();
    el.remove();
  }

  return { pintar, destacar, focarUnidade, irPara, vistaDaUnidade, dispose };
}

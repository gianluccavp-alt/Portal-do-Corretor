/* ============================================================
   MAQUETE 3D - cena Three.js
   ------------------------------------------------------------
   criarCena(container, cfg, ev) -> Promise<Cena>
     cfg = emp.maquete ({ modelo, grade, cameras, ... })
     ev  = { onProgresso(p 0..1), onHover(idx|null, x, y), onClick(idx|null) }
   Cena = { pintar(estados, visiveis, modo), destacar(idx|null),
            focarUnidade(idx), irPara(nomeCamera), vistaDaUnidade(idx),
            dispose() }

   Pintura: um unico DataTexture (1 texel por idx) lido no shader
   pelo atributo de vertice "_unit" da malha "unidades" (sem um
   material por unidade). Texel = rgb da cor + a = forca do emissivo.
   ============================================================ */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { criarModeloProvisorio } from './maquete-provisoria.js';

const DRACO_PATH = 'https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/draco/gltf/';
const DUR_ANIM = 800;
const VERMELHO = '#E4032B';

/* cor e forca do emissivo por estado, em cada modo */
const MODOS = {
  noite: {
    ceuTopo: '#050913', ceuBase: '#1c2541', nevoa: '#1c2541',
    hemiCeu: '#5a6c9c', hemiChao: '#10131a', hemi: 0.55,
    sol: '#a9bcff', solInt: 0.45, exposicao: 1.0, emissivo: 1.15, sombra: false,
    estados: {
      disponivel: ['#FFC872', 1],
      reservada: ['#232a38', 0],
      vendida: ['#232a38', 0],
      fora: ['#323846', 0],
      'sem-dados': ['#323846', 0]
    },
    esmaecido: ['#161b25', 0], misturaEsmaecido: 1
  },
  cores: {
    ceuTopo: '#7FA9D9', ceuBase: '#E8EEF3', nevoa: '#E8EEF3',
    hemiCeu: '#dfeaf7', hemiChao: '#6d7a5a', hemi: 1.1,
    sol: '#fff1dc', solInt: 2.4, exposicao: 1.0, emissivo: 0.35, sombra: true,
    estados: {
      disponivel: ['#2FA866', 0.5],
      reservada: ['#F2A93B', 0.4],
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
    uniforms: { topo: { value: new THREE.Color() }, base: { value: new THREE.Color() } },
    vertexShader: `varying vec3 vDir;
      void main() { vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `uniform vec3 topo; uniform vec3 base; varying vec3 vDir;
      void main() { float h = smoothstep(-0.02, 0.55, vDir.y); gl_FragColor = vec4(mix(base, topo, h), 1.0);
      #include <colorspace_fragment>
      }`
  });
  const ceu = new THREE.Mesh(new THREE.SphereGeometry(1500, 32, 16), mat);
  ceu.name = 'ceu';
  ceu.renderOrder = -1;
  return ceu;
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
        vec4 est = texelFetch(uEstados, ivec2(int(vUnit + 0.5), 0), 0);
        vec3 emissUn = est.rgb * est.a * uEmissivo;
        diffuseColor.rgb = est.rgb;
        if (abs(vUnit - uSel) < 0.5) {
          diffuseColor.rgb = uCorSel;
          emissUn = uCorSel * (0.55 + 0.45 * uPulso);
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
      norm[u * 3] += n.x; norm[u * 3 + 1] += n.y; norm[u * 3 + 2] += n.z;
      cont[u]++;
    }
  });
  return (idx) => {
    if (!(idx >= 0 && idx < total) || !cont[idx]) return null;
    const c = new THREE.Vector3(soma[idx * 3], soma[idx * 3 + 1], soma[idx * 3 + 2]).divideScalar(cont[idx]);
    const nn = new THREE.Vector3(norm[idx * 3], 0, norm[idx * 3 + 2]);
    if (nn.lengthSq() < 1e-6) nn.set(0, 0, 1);
    return { centro: c, normal: nn.normalize() };
  };
}

function suavizar(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

export async function criarCena(container, cfg, ev = {}) {
  const onProgresso = ev.onProgresso || (() => {});
  const onHover = ev.onHover || (() => {});
  const onClick = ev.onClick || (() => {});
  const grade = cfg.grade;
  const total = grade.torres.length * grade.andares * grade.finais;

  /* ---------- renderer (lanca erro se nao houver WebGL2) ---------- */
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.style.display = 'block';
  renderer.domElement.style.touchAction = 'none';
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.5, 4000);
  const ceu = criarCeu();
  scene.add(ceu);
  scene.fog = new THREE.Fog('#000000', 320, 950);

  const hemi = new THREE.HemisphereLight();
  scene.add(hemi);
  const sol = new THREE.DirectionalLight();
  sol.position.set(-140, 210, 120);
  sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048);
  Object.assign(sol.shadow.camera, { left: -170, right: 170, top: 170, bottom: -170, near: 10, far: 600 });
  sol.shadow.bias = -0.0004;
  sol.shadow.normalBias = 0.6;
  scene.add(sol);

  /* ---------- texture de estados + uniforms compartilhados ---------- */
  const dados = new Float32Array(total * 4);
  const tex = new THREE.DataTexture(dados, total, 1, THREE.RGBAFormat, THREE.FloatType);
  tex.minFilter = THREE.NearestFilter;
  tex.magFilter = THREE.NearestFilter;
  tex.needsUpdate = true;
  const uni = {
    uSel: { value: -1 }, uHover: { value: -1 }, uEmissivo: { value: 1 }, uPulso: { value: 0 },
    uCorSel: { value: new THREE.Color(VERMELHO) }
  };
  const matUnidades = criarMaterialUnidades(tex, uni);

  /* ---------- modelo ---------- */
  let modelo;
  if (typeof cfg.modelo === 'string' && cfg.modelo) {
    modelo = await carregarGLB(cfg.modelo, onProgresso);
    modelo.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  } else {
    modelo = criarModeloProvisorio(grade);
  }
  scene.add(modelo);
  const malhasUn = malhasDeUnidades(modelo);
  malhasUn.forEach((m) => { m.material = matUnidades; m.castShadow = false; });
  const setUn = new Set(malhasUn);
  const unidadeInfo = mapearUnidades(malhasUn, total);
  onProgresso(1);

  /* ---------- camera + controles ---------- */
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 18;
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

  /* ---------- modo (noite/cores) ---------- */
  let modoAtual = null;
  function aplicarModo(modo) {
    if (modo === modoAtual) return;
    modoAtual = modo;
    const m = MODOS[modo];
    ceu.material.uniforms.topo.value.set(m.ceuTopo);
    ceu.material.uniforms.base.value.set(m.ceuBase);
    scene.fog.color.set(m.nevoa);
    hemi.color.set(m.hemiCeu);
    hemi.groundColor.set(m.hemiChao);
    hemi.intensity = m.hemi;
    sol.color.set(m.sol);
    sol.intensity = m.solInt;
    sol.castShadow = m.sombra;
    renderer.toneMappingExposure = m.exposicao;
    uni.uEmissivo.value = m.emissivo;
  }

  const cor = new THREE.Color();
  const corEsm = new THREE.Color();
  function pintar(estados, visiveis, modo) {
    const m = MODOS[modo] ? modo : 'noite';
    aplicarModo(m);
    const tab = MODOS[m];
    corEsm.set(tab.esmaecido[0]);
    for (let i = 0; i < total; i++) {
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
    pedirRender();
  }

  function focarUnidade(idx) {
    const info = unidadeInfo(idx);
    if (!info) return;
    const pos = info.centro.clone().addScaledVector(info.normal, 42);
    pos.y = Math.max(4, info.centro.y + 10);
    animarPara(pos, info.centro);
  }

  function vistaDaUnidade(idx) {
    const info = unidadeInfo(idx);
    if (!info) return;
    const pos = info.centro.clone().addScaledVector(info.normal, 1.2);
    pos.y = info.centro.y + 0.2;
    const alvo = info.centro.clone().addScaledVector(info.normal, 60);
    alvo.y = info.centro.y - 6; // olha levemente para baixo (respeita maxPolarAngle)
    animarPara(pos, alvo);
  }

  function irPara(nome) {
    const c = cfg.cameras && cfg.cameras[nome];
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
    const hits = ray.intersectObject(modelo, true);
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
  let baixo = null;

  function onMove(e) {
    if (e.pointerType !== 'mouse') return;
    hoverPend = { x: e.clientX, y: e.clientY };
  }
  function onLeave() {
    hoverPend = null;
    if (hoverIdx !== null) {
      hoverIdx = null;
      uni.uHover.value = -1;
      pedirRender();
      onHover(null, 0, 0);
    }
  }
  function onDown(e) { baixo = { x: e.clientX, y: e.clientY, t: performance.now() }; }
  function onUp(e) {
    if (!baixo) return;
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

  function processarHover() {
    if (!hoverPend) return;
    const { x, y } = hoverPend;
    hoverPend = null;
    const idx = pick(x, y);
    const mudou = idx !== hoverIdx;
    if (mudou) {
      hoverIdx = idx;
      uni.uHover.value = idx == null ? -1 : idx;
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
    pedirRender();
  }
  const ro = new ResizeObserver(redimensionar);
  ro.observe(container);
  redimensionar();

  /* ---------- loop (so renderiza quando algo muda) ---------- */
  let rodando = true;
  function quadro(agora) {
    if (!rodando) return;
    requestAnimationFrame(quadro);
    if (anim) {
      const t = Math.min(1, (agora - anim.t0) / DUR_ANIM);
      const k = suavizar(t);
      camera.position.lerpVectors(anim.dePos, anim.paraPos, k);
      controls.target.lerpVectors(anim.deAlvo, anim.paraAlvo, k);
      if (t >= 1) anim = null;
      sujo = true;
    }
    if (controls.update()) sujo = true;
    processarHover();
    if (uni.uSel.value >= 0) {
      uni.uPulso.value = 0.5 + 0.5 * Math.sin(agora / 260);
      sujo = true;
    }
    if (sujo) {
      sujo = false;
      renderer.render(scene, camera);
    }
  }

  pintar(new Array(total).fill('sem-dados'), null, 'noite');
  requestAnimationFrame(quadro);

  function dispose() {
    rodando = false;
    ro.disconnect();
    el.removeEventListener('pointermove', onMove);
    el.removeEventListener('pointerleave', onLeave);
    el.removeEventListener('pointerdown', onDown);
    el.removeEventListener('pointerup', onUp);
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
    renderer.dispose();
    el.remove();
  }

  return { pintar, destacar, focarUnidade, irPara, vistaDaUnidade, dispose };
}

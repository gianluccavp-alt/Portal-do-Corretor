/* ============================================================
   MAQUETE 3D - apartamento decorado (passeio em primeira pessoa)
   ------------------------------------------------------------
   carregarApto(ctx, cfg, onProgresso) -> Promise<Apto>
   Apto = { entrar(unidade, ev), sair(), quadro(agora), irPara(id), ativo, ... }

   O apartamento e colocado na posicao real da unidade (torre + andar),
   entao a sacada e as janelas mostram a maquete de verdade naquela
   altura. A torre e aberta no volume da unidade por planos de corte.
   Luz: lightmaps calculados no Blender (uv1); a luz de cena nao atua
   nos materiais internos, que so recebem o reflexo do proprio ambiente.
   Gerador: assets/3d/village-gaia/apto/scripts/
   ============================================================ */
import * as THREE from 'three';
import { Reflector } from 'three/addons/objects/Reflector.js';

const VEL_ANDAR = 1.75;      // m/s
const VEL_RAPIDO = 3.0;
const ACEL = 9;              // resposta do movimento (1/s)
const SENS_MOUSE = 0.0021;
const SENS_TOQUE = 0.0042;
const FOV = 68;
const PITCH_MAX = 1.35;

const TECLAS = {
  ArrowUp: 'f', KeyW: 'f', ArrowDown: 't', KeyS: 't',
  ArrowLeft: 'e', KeyA: 'e', ArrowRight: 'd', KeyD: 'd',
  ShiftLeft: 'r', ShiftRight: 'r'
};

/* interno: so o lightmap ilumina; a luz da cena (sol, hemisferica) nao entra e o reflexo do ambiente
   e apagado onde o lightmap e escuro */
function patchInterno(mat) {
  mat.onBeforeCompile = (s) => {
    s.fragmentShader = s.fragmentShader
      .replace('#include <lights_fragment_maps>', 'irradiance = vec3(0.0);\n#include <lights_fragment_maps>')
      .replace('#include <lights_fragment_end>', `irradiance *= vec3(0.94, 0.985, 1.07);   /* lampadas menos amarelas, como nas fotos do decorado */
        iblIrradiance = vec3(0.0);
        radiance *= clamp(dot(lightMapIrradiance, vec3(0.333)) * 0.55, 0.0, 1.0);
        #include <lights_fragment_end>
        reflectedLight.directDiffuse = vec3(0.0);
        reflectedLight.directSpecular = vec3(0.0);`);
  };
  mat.customProgramCacheKey = () => 'apto-interno';
}

/* partes finas sem lightmap (caixilhos, rodapes, hastes, cortinas): luz neutra e constante, igual a de um
   ambiente iluminado, sem o sol atravessar as paredes nem o azul do ceu */
function patchFino(mat) {
  mat.onBeforeCompile = (s) => {
    s.fragmentShader = s.fragmentShader
      .replace('#include <lights_fragment_maps>', 'irradiance = vec3(2.45, 2.38, 2.26);\n#include <lights_fragment_maps>')
      .replace('#include <lights_fragment_end>', `iblIrradiance = vec3(0.0);
        #include <lights_fragment_end>
        reflectedLight.directDiffuse = vec3(0.0);
        reflectedLight.directSpecular = vec3(0.0);`);
  };
  mat.customProgramCacheKey = () => 'apto-fino';
}

function carregarTextura(url) {
  return new Promise((ok, falha) => new THREE.TextureLoader().load(url, ok, undefined, falha));
}

export async function carregarApto(ctx, cfg, onProgresso) {
  const { renderer, scene, camera, controls, carregarGLB, usarRatio, ratioMax, sol, solDirPadrao } = ctx;
  const base = cfg.pasta;
  const v = cfg.versao ? '?v=' + cfg.versao : '';
  const dados = await fetch(base + cfg.arquivo + '.json' + v).then((r) => {
    if (!r.ok) throw new Error('apto: json ' + r.status);
    return r.json();
  });
  let pGlb = 0;
  let pTex = 0;
  const avisar = () => onProgresso(Math.min(0.99, pGlb * 0.8 + pTex * 0.2));
  const [raiz, lmArq, lmMov] = await Promise.all([
    carregarGLB(base + cfg.arquivo + '.glb' + v, (p) => { pGlb = p; avisar(); }),
    carregarTextura(base + dados.lm_arq + v).then((t) => { pTex += 0.5; avisar(); return t; }),
    carregarTextura(base + dados.lm_mov + v).then((t) => { pTex += 0.5; avisar(); return t; })
  ]);
  const aniso = renderer.capabilities.getMaxAnisotropy();
  [lmArq, lmMov].forEach((t) => {
    t.channel = 1;
    t.flipY = false;                       // TEXCOORD_1 do glTF ja vem com v invertido
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = Math.min(4, aniso);
    t.needsUpdate = true;
  });
  const INT_LUZ = dados.lm_escala * Math.PI * (cfg.exposicaoInterna || 1);

  /* ---------- materiais ---------- */
  const internos = [];
  const clones = new Map();
  raiz.traverse((o) => {
    if (!o.isMesh) return;
    let cam = o;
    while (cam.parent && cam.parent !== raiz) cam = cam.parent;
    const camada = cam.name.replace('apto_', '');
    o.castShadow = false;
    o.receiveShadow = false;
    const mt0 = o.material;
    const chave = camada + '|' + mt0.uuid;
    let mt = clones.get(chave);
    if (!mt) {
      mt = mt0.clone();
      clones.set(chave, mt);
      ['map'].forEach((k) => { if (mt[k]) { mt[k].anisotropy = aniso; mt[k].colorSpace = THREE.SRGBColorSpace; mt[k].needsUpdate = true; } });
      if (camada === 'arq' || camada === 'mov') {
        mt.lightMap = camada === 'arq' ? lmArq : lmMov;
        mt.lightMapIntensity = INT_LUZ;
        mt.side = THREE.FrontSide;
        patchInterno(mt);
        internos.push(mt);
      } else if (camada === 'vidro') {
        mt.transparent = true;
        mt.depthWrite = false;
        mt.side = THREE.DoubleSide;
        if (/canelado/.test(mt.name)) {
          mt.opacity = 0.2;
          mt.emissive.set('#ffcf96');
          mt.emissiveIntensity = 0.22;
          if (mt.map) { mt.map.wrapS = THREE.RepeatWrapping; }
        } else {
          mt.opacity = 0.09;
        }
        internos.push(mt);
      } else if (camada === 'folha') {
        mt.alphaTest = 0.4;
        mt.alphaToCoverage = true;
        mt.transparent = false;
        mt.side = THREE.DoubleSide;
        mt.color.multiplyScalar(0.8);
      } else if (camada === 'ext') {
        if (/cortina/.test(mt.name)) mt.side = THREE.DoubleSide;
        patchFino(mt);
        internos.push(mt);                 // metais finos (torneiras, puxadores) refletem o ambiente
      }
    }
    o.material = mt;
    if ((camada === 'arq' || camada === 'mov') && !o.geometry.getAttribute('uv1')) {
      const a = o.geometry.getAttribute('_lightuv') || o.geometry.getAttribute('texcoord_1');
      if (a) o.geometry.setAttribute('uv1', a);
    }
  });
  const grupo = new THREE.Group();
  grupo.name = 'apto';
  grupo.add(raiz);
  grupo.visible = false;
  scene.add(grupo);

  /* ---------- espelhos reais: so atualizam quando o visitante esta no ambiente deles ---------- */
  const espelhos = dados.espelhos.map((e, i) => {
    /* pontos em coordenadas do apto (x, y, z) num plano x constante, voltados para -x */
    const pts2 = e.pts.map((p) => new THREE.Vector2(-p[1], p[2]));
    const geo = new THREE.ShapeGeometry(new THREE.Shape(pts2));
    const m = new Reflector(geo, {
      textureWidth: 1024, textureHeight: 1024, clipBias: 0.002, multisample: 4, color: 0xf2f2f2
    });
    m.rotation.y = -Math.PI / 2;
    m.position.set(e.pts[0][0], 0, 0);
    m.name = 'espelho-' + i;
    const ys = e.pts.map((p) => p[1]);
    const yM = (Math.min(...ys) + Math.max(...ys)) / 2;
    const zona = yM < 4.76 ? [2.2, 0, 6.2, 4.76] : yM < 7.26 ? [3.3, 4.8, 5.6, 7.26] : [3.3, 7.3, 5.6, 9.75];
    const atualizar = m.onBeforeRender;
    let pronto = false;
    m.onBeforeRender = function (r, sc, cam) {
      if (pronto && !this.userData.liberado) return;
      pronto = true;
      atualizar.call(this, r, sc, cam);
    };
    m.userData.zona = zona;
    raiz.add(m);
    return m;
  });

  /* ---------- estado do passeio ---------- */
  const st = {
    ativo: false, x: 0, y: 0, yaw: 0, pitch: 0, vx: 0, vy: 0,
    origem: new THREE.Vector3(), teclas: new Set(), ultimoT: 0, sala: null, somaDt: 0, nDt: 0, ratio: ratioMax
  };
  let ev = {};
  let salvo = null;
  const el = renderer.domElement;
  const OLHO = dados.olho;
  const RAIO = dados.raio;
  const BL = dados.blocos;

  function colidir(x, y) {
    for (let k = 0; k < 3; k++) {
      let mexeu = false;
      for (let i = 0; i < BL.length; i++) {
        const b = BL[i];
        if (x < b[0] - RAIO || x > b[2] + RAIO || y < b[1] - RAIO || y > b[3] + RAIO) continue;
        const nx = Math.max(b[0], Math.min(x, b[2]));
        const ny = Math.max(b[1], Math.min(y, b[3]));
        const dx = x - nx;
        const dy = y - ny;
        const d2 = dx * dx + dy * dy;
        if (d2 >= RAIO * RAIO) continue;
        if (d2 > 1e-9) {
          const d = Math.sqrt(d2);
          x = nx + dx / d * RAIO;
          y = ny + dy / d * RAIO;
        } else {
          /* centro dentro do bloco: sai pelo lado mais proximo */
          const lados = [x - b[0], b[2] - x, y - b[1], b[3] - y];
          const m = lados.indexOf(Math.min(...lados));
          if (m === 0) x = b[0] - RAIO; else if (m === 1) x = b[2] + RAIO; else if (m === 2) y = b[1] - RAIO; else y = b[3] + RAIO;
        }
        mexeu = true;
      }
      if (!mexeu) break;
    }
    return [x, y];
  }

  function salaEm(x, y) {
    /* a primeira caixa que contem o ponto; entrada, cozinha e sala antes de jantar */
    const a = dados.ambientes.find((r) => x >= r.caixa[0] && x <= r.caixa[2] && y >= r.caixa[1] && y <= r.caixa[3]);
    return a || null;
  }

  function aplicarCamera() {
    camera.position.set(st.origem.x + st.x, st.origem.y + OLHO, st.origem.z - st.y);
    camera.rotation.set(st.pitch, st.yaw, 0, 'YXZ');
    camera.updateMatrixWorld();
  }

  /* direcao no quadro do apto (x, y) -> yaw da camera: olhar para (dx, dy) */
  function olhar(dx, dy) {
    /* no mundo: x = x, z = -y. A camera olha para -z quando yaw = 0, isto e, para +y do apto */
    st.yaw = Math.atan2(-dx, dy);
    st.pitch = -0.04;
  }

  function irPara(id) {
    const a = dados.ambientes.find((r) => r.id === id);
    if (!a) return;
    st.x = a.pos[0];
    st.y = a.pos[1];
    st.vx = st.vy = 0;
    olhar(a.olha[0], a.olha[1]);
    aplicarCamera();
    atualizarSala(true);
  }

  function atualizarSala(forca) {
    const a = salaEm(st.x, st.y);
    const id = a ? a.id : st.sala;
    if (id !== st.sala || forca) {
      st.sala = id;
      if (ev.onAmbiente) ev.onAmbiente(a);
    }
  }

  /* ---------- entrada: mouse e teclado ---------- */
  let arrasto = null;
  const travado = () => document.pointerLockElement === el;

  function onMouseMove(e) {
    if (!st.ativo || !travado()) return;
    st.yaw -= e.movementX * SENS_MOUSE;
    st.pitch = Math.max(-PITCH_MAX, Math.min(PITCH_MAX, st.pitch - e.movementY * SENS_MOUSE));
  }
  function onPointerDown(e) {
    if (!st.ativo) return;
    if (e.pointerType === 'mouse' && e.button === 0 && !travado() && ev.travarAoClicar !== false) {
      const p = el.requestPointerLock && el.requestPointerLock();
      if (p && p.catch) p.catch(() => {});
    }
    if (!travado()) arrasto = { id: e.pointerId, x: e.clientX, y: e.clientY, s: e.pointerType === 'mouse' ? SENS_MOUSE * 1.6 : SENS_TOQUE };
  }
  function onPointerMove(e) {
    if (!arrasto || e.pointerId !== arrasto.id || travado()) return;
    if (ev.onInteragiu) ev.onInteragiu();
    st.yaw -= (e.clientX - arrasto.x) * arrasto.s;
    st.pitch = Math.max(-PITCH_MAX, Math.min(PITCH_MAX, st.pitch - (e.clientY - arrasto.y) * arrasto.s));
    arrasto.x = e.clientX;
    arrasto.y = e.clientY;
  }
  function onPointerUp(e) { if (arrasto && e.pointerId === arrasto.id) arrasto = null; }
  function onLock() { if (st.ativo && ev.onTrava) ev.onTrava(travado()); }
  function onLockErro() { if (st.ativo && ev.onTravaFalhou) ev.onTravaFalhou(); }
  function onKey(e) {
    if (!st.ativo) return;
    const a = TECLAS[e.code];
    if (a) {
      e.preventDefault();
      e.stopPropagation();
      if (e.type === 'keydown') {
        st.teclas.add(a);
        if (ev.onInteragiu) ev.onInteragiu();
      } else st.teclas.delete(a);
    } else if (e.code === 'Escape' && e.type === 'keydown') {
      /* com o mouse preso, o navegador usa o Esc para soltar; solto, Esc sai do apartamento */
      e.stopPropagation();
      if (!travado() && ev.onEsc) ev.onEsc();
    }
  }
  function onBlur() { st.teclas.clear(); }
  function ligar() {
    document.addEventListener('mousemove', onMouseMove);
    el.addEventListener('pointerdown', onPointerDown);
    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp);
    window.addEventListener('pointercancel', onPointerUp);
    document.addEventListener('pointerlockchange', onLock);
    document.addEventListener('pointerlockerror', onLockErro);
    /* em captura: as setas nao chegam aos atalhos da maquete */
    window.addEventListener('keydown', onKey, true);
    window.addEventListener('keyup', onKey, true);
    window.addEventListener('blur', onBlur);
  }
  function desligar() {
    document.removeEventListener('mousemove', onMouseMove);
    el.removeEventListener('pointerdown', onPointerDown);
    window.removeEventListener('pointermove', onPointerMove);
    window.removeEventListener('pointerup', onPointerUp);
    window.removeEventListener('pointercancel', onPointerUp);
    document.removeEventListener('pointerlockchange', onLock);
    document.removeEventListener('pointerlockerror', onLockErro);
    window.removeEventListener('keydown', onKey, true);
    window.removeEventListener('keyup', onKey, true);
    window.removeEventListener('blur', onBlur);
  }

  /* ---------- corte na torre: some so o volume desta unidade ---------- */
  const matsTorre = new Set();
  ctx.modelo.traverse((o) => {
    if (!o.isMesh) return;
    let r = o;
    while (r.parent && r.parent !== ctx.modelo) r = r.parent;
    if (/^(torre-|guarda-corpo|unidades)/.test(r.name)) {
      (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => { if (m) matsTorre.add(m); });
    }
  });
  function cortarTorre(o, andarY) {
    const x0 = o.x - 0.04; const x1 = o.x + 6.19;
    const z0 = o.z - 9.83; const z1 = o.z + 0.03;
    const y0 = andarY - 0.16; const y1 = andarY + 2.92;
    const planos = [
      new THREE.Plane(new THREE.Vector3(1, 0, 0), -x1), new THREE.Plane(new THREE.Vector3(-1, 0, 0), x0),
      new THREE.Plane(new THREE.Vector3(0, 1, 0), -y1), new THREE.Plane(new THREE.Vector3(0, -1, 0), y0),
      new THREE.Plane(new THREE.Vector3(0, 0, 1), -z1), new THREE.Plane(new THREE.Vector3(0, 0, -1), z0)
    ];
    renderer.localClippingEnabled = true;
    matsTorre.forEach((m) => { m.clippingPlanes = planos; m.clipIntersection = true; m.needsUpdate = true; });
  }
  function fecharTorre() {
    matsTorre.forEach((m) => { m.clippingPlanes = null; m.clipIntersection = false; m.needsUpdate = true; });
    renderer.localClippingEnabled = false;
  }

  /* ---------- reflexo do proprio ambiente, capturado uma vez por entrada ---------- */
  let envRT = null;
  function capturarAmbiente() {
    const rt = new THREE.WebGLCubeRenderTarget(256, { type: THREE.HalfFloatType, generateMipmaps: true, minFilter: THREE.LinearMipmapLinearFilter });
    const cub = new THREE.CubeCamera(0.05, 1500, rt);
    cub.position.set(st.origem.x + 3.6, st.origem.y + 1.3, st.origem.z - 2.9);
    espelhos.forEach((m) => { m.visible = false; });
    internos.forEach((m) => { m.envMap = null; });
    cub.update(renderer, scene);
    const pm = new THREE.PMREMGenerator(renderer);
    const novo = pm.fromCubemap(rt.texture);
    pm.dispose();
    rt.dispose();
    if (envRT) envRT.dispose();
    envRT = novo;
    internos.forEach((m) => {
      m.envMap = novo.texture;
      m.envMapIntensity = /vidro/.test(m.name) ? 1.0 : 0.85;
      m.needsUpdate = true;
    });
    espelhos.forEach((m) => { m.visible = true; });
  }

  /* ---------- entrar / sair ---------- */
  function entrar(unidade, callbacks) {
    ev = callbacks || {};
    const o = new THREE.Vector3(unidade.cx + dados.torre_x_para_apto, unidade.andar * cfg.peDireito, -(unidade.cy + dados.torre_y_para_apto));
    st.origem.copy(o);
    grupo.position.copy(o);
    grupo.visible = true;
    grupo.updateMatrixWorld(true);
    salvo = {
      fov: camera.fov, near: camera.near, far: camera.far,
      pos: camera.position.clone(), alvo: controls.target.clone(), solPos: sol.position.clone(), solAlvo: sol.target.position.clone()
    };
    controls.enabled = false;
    camera.fov = FOV;
    camera.near = 0.06;
    camera.far = 1800;
    camera.updateProjectionMatrix();
    /* sol da tarde, o mesmo usado no calculo da luz do apartamento */
    const d = new THREE.Vector3(dados.sol[0], dados.sol[2], -dados.sol[1]).normalize();
    const alcance = salvo.solPos.distanceTo(salvo.solAlvo);
    sol.position.copy(sol.target.position).addScaledVector(d, alcance);
    renderer.shadowMap.needsUpdate = true;
    cortarTorre(o, o.y);
    st.ratio = Math.min(ratioMax, 1.5);
    usarRatio(st.ratio);
    st.ativo = true;
    st.teclas.clear();
    st.sala = null;
    st.ultimoT = performance.now();
    ligar();
    /* fica no primeiro ambiente da lista (entrada) */
    irPara(dados.ambientes[0].id);
    capturarAmbiente();
    aplicarCamera();
  }

  function sair() {
    if (!st.ativo) return;
    st.ativo = false;
    desligar();
    arrasto = null;
    if (travado() && document.exitPointerLock) document.exitPointerLock();
    grupo.visible = false;
    fecharTorre();
    camera.fov = salvo.fov;
    camera.near = salvo.near;
    camera.far = salvo.far;
    camera.updateProjectionMatrix();
    camera.rotation.set(0, 0, 0, 'XYZ');
    camera.position.copy(salvo.pos);
    controls.target.copy(salvo.alvo);
    controls.enabled = true;
    controls.update();
    sol.position.copy(salvo.solPos);
    renderer.shadowMap.needsUpdate = true;
    usarRatio(ratioMax);
    st.ratio = ratioMax;
  }

  function adaptar(dt) {
    st.somaDt += dt;
    st.nDt++;
    if (st.nDt < 30) return;
    const media = st.somaDt / st.nDt;
    st.somaDt = 0;
    st.nDt = 0;
    if (media > 0.03 && st.ratio > 1) {
      st.ratio = Math.max(1, st.ratio * 0.85);
      usarRatio(st.ratio);
    }
  }

  /* um quadro do passeio: movimento + render */
  function quadro(agora) {
    const dt = Math.min(0.1, (agora - st.ultimoT) / 1000);
    st.ultimoT = agora;
    const t = st.teclas;
    const frente = (t.has('f') ? 1 : 0) - (t.has('t') ? 1 : 0);
    const lado = (t.has('d') ? 1 : 0) - (t.has('e') ? 1 : 0);
    const vMax = t.has('r') ? VEL_RAPIDO : VEL_ANDAR;
    /* yaw 0 olha para +y do apto; direita = +x */
    const sa = Math.sin(st.yaw);
    const ca = Math.cos(st.yaw);
    let dx = -sa * frente + ca * lado;
    let dy = ca * frente + sa * lado;
    const n = Math.hypot(dx, dy);
    if (n > 1) { dx /= n; dy /= n; }
    const k = 1 - Math.exp(-ACEL * dt);
    st.vx += (dx * vMax - st.vx) * k;
    st.vy += (dy * vMax - st.vy) * k;
    if (Math.abs(st.vx) + Math.abs(st.vy) > 0.001) {
      /* passos curtos: nao atravessa parede fina em quadro lento */
      const passos = Math.max(1, Math.ceil(Math.hypot(st.vx, st.vy) * dt / (RAIO * 0.5)));
      for (let i = 0; i < passos; i++) {
        const [nx, ny] = colidir(st.x + st.vx * dt / passos, st.y + st.vy * dt / passos);
        st.x = nx;
        st.y = ny;
      }
      atualizarSala(false);
    }
    aplicarCamera();
    espelhos.forEach((m) => {
      const z = m.userData.zona;
      m.userData.liberado = st.x >= z[0] && st.x <= z[2] && st.y >= z[1] && st.y <= z[3];
    });
    adaptar(dt);
    renderer.render(scene, camera);
  }

  /* botoes na tela (toque) */
  function tecla(acao, baixo) { if (baixo) st.teclas.add(acao); else st.teclas.delete(acao); }

  onProgresso(1);
  return {
    entrar, sair, quadro, irPara, tecla, ambientes: dados.ambientes,
    get ativo() { return st.ativo; }
  };
}

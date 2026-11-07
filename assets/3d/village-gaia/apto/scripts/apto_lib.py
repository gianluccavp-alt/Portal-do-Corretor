# apto_lib.py -- primitivas do gerador do apartamento (executado por apto_final05.py, dentro do Blender).
# Coordenadas do apartamento em metros, Z para cima. Cada primitiva acumula em uma camada:
#   arq (arquitetura, lightmap proprio)   mov (moveis, lightmap proprio)
#   vidro (transparente, sem lightmap)    luz (emissores, sem lightmap)   folha (recortes, sem lightmap)
#   ext (partes finas ao ar livre: luz de cena, sem lightmap)
import bpy, math, os
from contextlib import contextmanager
import numpy as np

CAMADAS = ('arq', 'mov', 'vidro', 'luz', 'folha', 'ext')
UV = {}          # material -> (m por repeticao, trocar u/v)
MATS = {}
BLOCOS = []      # colisao: [x0, y0, x1, y1] em coordenadas do apartamento
FINO = 0.016     # tubos e hastes mais finos que isso nao gastam lightmap (luz de cena)


class Camada:
    def __init__(self, nome):
        self.nome = nome
        self.v, self.f, self.fm, self.fs, self.fuv = [], [], [], [], []
        self.mats, self.idx = [], {}

    def m(self, nome):
        if nome not in MATS:
            raise KeyError('material desconhecido: ' + nome)
        if nome not in self.idx:
            self.idx[nome] = len(self.mats)
            self.mats.append(nome)
        return self.idx[nome]


C = {n: Camada(n) for n in CAMADAS}
_tx, _ty, _tz, _a = 0.0, 0.0, 0.0, 0.0


@contextmanager
def em(x=0.0, y=0.0, z=0.0, giro=0.0):
    """Posiciona o que vier dentro: translada (no sistema atual) e gira em Z (graus)."""
    global _tx, _ty, _tz, _a
    velho = (_tx, _ty, _tz, _a)
    ca, sa = math.cos(_a), math.sin(_a)
    _tx, _ty, _tz = _tx + ca * x - sa * y, _ty + sa * x + ca * y, _tz + z
    _a += math.radians(giro)
    try:
        yield
    finally:
        _tx, _ty, _tz, _a = velho


def pt(x, y, z):
    ca, sa = math.cos(_a), math.sin(_a)
    return (_tx + ca * x - sa * y, _ty + sa * x + ca * y, _tz + z)


def malha(vs, fs, mat, L='mov', suave=False, uvs=None):
    """vs: pontos locais; fs: faces (indices). uvs: uv por vertice (senao, projecao de caixa no fim)."""
    c = C[L]
    base = len(c.v)
    c.v.extend(pt(*p) for p in vs)
    mi = c.m(mat)
    for f in fs:
        c.f.append(tuple(i + base for i in f))
        c.fm.append(mi)
        c.fs.append(suave)
        c.fuv.append(None if uvs is None else [uvs[i] for i in f])


def bloco(x0, x1, y0, y1):
    a, b = pt(x0, y0, 0), pt(x1, y1, 0)
    c_, d = pt(x0, y1, 0), pt(x1, y0, 0)
    xs, ys = [p[0] for p in (a, b, c_, d)], [p[1] for p in (a, b, c_, d)]
    BLOCOS.append([round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)])


def caixa(x0, x1, y0, y1, z0, z1, mat, L='mov', bev=0.0, sem=''):
    """Caixa com chanfro opcional (bev). sem: faces omitidas, ex. 'b' (fundo), 't' (topo)."""
    if x0 > x1: x0, x1 = x1, x0
    if y0 > y1: y0, y1 = y1, y0
    if z0 > z1: z0, z1 = z1, z0
    if bev <= 0:
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        faces = {'b': (3, 2, 1, 0), 't': (4, 5, 6, 7), 'f': (0, 1, 5, 4), 'r': (1, 2, 6, 5), 'k': (2, 3, 7, 6), 'l': (3, 0, 4, 7)}
        # vertices proprios por face: normais retas
        for k, f in faces.items():
            if k in sem:
                continue
            malha([v[i] for i in f], [(0, 1, 2, 3)], mat, L)
        return
    e = min(bev, (x1 - x0) / 2.01, (y1 - y0) / 2.01, (z1 - z0) / 2.01)
    def P(sx, sy, sz, ix, iy, iz):
        return (x1 - ix * e if sx else x0 + ix * e, y1 - iy * e if sy else y0 + iy * e, z1 - iz * e if sz else z0 + iz * e)
    def Q(pts):
        malha(pts, [tuple(range(len(pts)))], mat, L)
    if 't' not in sem: Q([P(0, 0, 1, 1, 1, 0), P(1, 0, 1, 1, 1, 0), P(1, 1, 1, 1, 1, 0), P(0, 1, 1, 1, 1, 0)])
    if 'b' not in sem: Q([P(0, 1, 0, 1, 1, 0), P(1, 1, 0, 1, 1, 0), P(1, 0, 0, 1, 1, 0), P(0, 0, 0, 1, 1, 0)])
    if 'f' not in sem: Q([P(0, 0, 0, 1, 0, 1), P(1, 0, 0, 1, 0, 1), P(1, 0, 1, 1, 0, 1), P(0, 0, 1, 1, 0, 1)])
    if 'k' not in sem: Q([P(1, 1, 0, 1, 0, 1), P(0, 1, 0, 1, 0, 1), P(0, 1, 1, 1, 0, 1), P(1, 1, 1, 1, 0, 1)])
    if 'r' not in sem: Q([P(1, 0, 0, 0, 1, 1), P(1, 1, 0, 0, 1, 1), P(1, 1, 1, 0, 1, 1), P(1, 0, 1, 0, 1, 1)])
    if 'l' not in sem: Q([P(0, 1, 0, 0, 1, 1), P(0, 0, 0, 0, 1, 1), P(0, 0, 1, 0, 1, 1), P(0, 1, 1, 0, 1, 1)])
    # chanfros das 12 arestas e 8 cantos
    for sx in (0, 1):
        for sy in (0, 1):
            a, b, c_, d = P(sx, sy, 0, 1, 0, 1), P(sx, sy, 0, 0, 1, 1), P(sx, sy, 1, 0, 1, 1), P(sx, sy, 1, 1, 0, 1)
            Q([b, a, d, c_] if sx == sy else [a, b, c_, d])
    for sy in (0, 1):
        for sz in (0, 1):
            a, b, c_, d = P(0, sy, sz, 1, 0, 1), P(1, sy, sz, 1, 0, 1), P(1, sy, sz, 1, 1, 0), P(0, sy, sz, 1, 1, 0)
            Q([a, b, c_, d] if sy != sz else [d, c_, b, a])
    for sx in (0, 1):
        for sz in (0, 1):
            a, b, c_, d = P(sx, 0, sz, 0, 1, 1), P(sx, 1, sz, 0, 1, 1), P(sx, 1, sz, 1, 1, 0), P(sx, 0, sz, 1, 1, 0)
            Q([a, b, c_, d] if sx == sz else [d, c_, b, a])
    for sx in (0, 1):
        for sy in (0, 1):
            for sz in (0, 1):
                a, b, c_ = P(sx, sy, sz, 0, 1, 1), P(sx, sy, sz, 1, 0, 1), P(sx, sy, sz, 1, 1, 0)
                Q([a, b, c_] if (sx + sy + sz) % 2 == 1 else [c_, b, a])


def cil(x, y, r, z0, z1, mat, L='mov', seg=32, r2=None, tampa=True, base=False, suave=True):
    r2 = r if r2 is None else r2
    if L == 'mov' and max(r, r2) <= FINO:
        L = 'ext'
    vs, fs = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        vs.append((x + r * math.cos(a), y + r * math.sin(a), z0))
        vs.append((x + r2 * math.cos(a), y + r2 * math.sin(a), z1))
    for i in range(seg):
        j = (i + 1) % seg
        fs.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    malha(vs, fs, mat, L, suave=suave)
    if tampa:
        malha([(x + r2 * math.cos(2 * math.pi * i / seg), y + r2 * math.sin(2 * math.pi * i / seg), z1) for i in range(seg)],
              [tuple(range(seg))], mat, L)
    if base:
        malha([(x + r * math.cos(-2 * math.pi * i / seg), y + r * math.sin(-2 * math.pi * i / seg), z0) for i in range(seg)],
              [tuple(range(seg))], mat, L)


def macio(cx, cy, cz, rx, ry, rz, mat, L='mov', e1=0.35, e2=0.35, seg=28, aneis=14, ruido=0.0, giro=0.0, seed=1, inc=0.0):
    """Superelipsoide (almofadas, colchoes, estofados). e menor = mais quadrado. inc: inclina em torno do eixo x local."""
    rng = np.random.default_rng(seed)
    fase = rng.uniform(0, 6.28, 6)
    ca, sa = math.cos(math.radians(giro)), math.sin(math.radians(giro))
    ci, si = math.cos(math.radians(inc)), math.sin(math.radians(inc))
    def sp(c, e):
        return math.copysign(abs(c) ** e, c)
    vs = []
    for j in range(aneis + 1):
        phi = -math.pi / 2 + math.pi * j / aneis
        for i in range(seg):
            th = 2 * math.pi * i / seg
            x = rx * sp(math.cos(phi), e1) * sp(math.cos(th), e2)
            y = ry * sp(math.cos(phi), e1) * sp(math.sin(th), e2)
            z = rz * sp(math.sin(phi), e1)
            if ruido:
                k = 1 + ruido * (math.sin(th * 2 + fase[0] + phi * 3) * 0.6 + math.sin(th * 3 + fase[1] - phi * 2) * 0.4 +
                                 0.5 * math.sin(th * 5 + fase[2] + phi * 5) * (z / max(rz, 1e-6)))
                z *= k
            y, z = y * ci - z * si, y * si + z * ci
            vs.append((cx + ca * x - sa * y, cy + sa * x + ca * y, cz + z))
    fs = []
    for j in range(aneis):
        for i in range(seg):
            a, b = j * seg + i, j * seg + (i + 1) % seg
            c_, d = (j + 1) * seg + (i + 1) % seg, (j + 1) * seg + i
            fs.append((a, b, c_, d))
    malha(vs, fs, mat, L, suave=True)


def tubo(pts, r, mat, L='mov', seg=10, fechado=False, ry=None, tampa=True):
    """Tubo por uma polilinha 3D. ry: secao eliptica (r no plano horizontal, ry na vertical do quadro)."""
    ry = r if ry is None else ry
    if L == 'mov' and max(r, ry) <= FINO:
        L = 'ext'
    pts = [np.array(p, float) for p in pts]
    n = len(pts)
    vs, fs = [], []
    for k, p in enumerate(pts):
        if fechado:
            t = pts[(k + 1) % n] - pts[(k - 1) % n]
        else:
            t = pts[min(k + 1, n - 1)] - pts[max(k - 1, 0)]
        t = t / (np.linalg.norm(t) + 1e-9)
        up = np.array([0, 0, 1.0]) if abs(t[2]) < 0.95 else np.array([1.0, 0, 0])
        a = np.cross(t, up); a /= np.linalg.norm(a) + 1e-9
        b = np.cross(a, t)
        for i in range(seg):
            q = 2 * math.pi * i / seg
            vs.append(tuple(p + a * (r * math.cos(q)) + b * (ry * math.sin(q))))
    lim = n if fechado else n - 1
    for k in range(lim):
        kk = (k + 1) % n
        for i in range(seg):
            j = (i + 1) % seg
            fs.append((k * seg + j, k * seg + i, kk * seg + i, kk * seg + j))
    malha(vs, fs, mat, L, suave=True)
    if tampa and not fechado:
        malha(vs[:seg], [tuple(range(seg))], mat, L)
        malha(vs[-seg:], [tuple(reversed(range(seg)))], mat, L)


def extruda(poly, z0, z1, mat, L='mov', lados_suaves=True, topo=None, sem_base=True):
    """Poligono 2D (anti-horario) extrudado em Z."""
    n = len(poly)
    vs = [(p[0], p[1], z0) for p in poly] + [(p[0], p[1], z1) for p in poly]
    fs = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    malha(vs, fs, mat, L, suave=lados_suaves)
    malha([(p[0], p[1], z1) for p in poly], [tuple(range(n))], topo or mat, L)
    if not sem_base:
        malha([(p[0], p[1], z0) for p in reversed(poly)], [tuple(range(n))], mat, L)


def arredondado(x0, x1, y0, y1, r, passos=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(passos + 1):
            a = math.radians(a0 + 90 * i / passos)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def imagem(p0, p1, p2, p3, mat, L='mov', uv=((0, 0), (1, 0), (1, 1), (0, 1))):
    """Quad com a imagem inteira: p0 base-esq, p1 base-dir, p2 topo-dir, p3 topo-esq (visto de frente)."""
    malha([p0, p1, p2, p3], [(0, 1, 2, 3)], mat, L, uvs=list(uv))


def disco(x, y, z, r, mat, L='mov', seg=48, uv_disco=False):
    vs = [(x + r * math.cos(2 * math.pi * i / seg), y + r * math.sin(2 * math.pi * i / seg), z) for i in range(seg)]
    uvs = [(0.5 + 0.5 * math.cos(2 * math.pi * i / seg), 0.5 + 0.5 * math.sin(2 * math.pi * i / seg)) for i in range(seg)] if uv_disco else None
    malha(vs, [tuple(range(seg))], mat, L, uvs=uvs)


# ------------------------------------------------------------------ materiais
TEX_APTO = None
TEX_GAIA = None
_imgs = {}


def _img(nome):
    if nome in _imgs:
        return _imgs[nome]
    p = os.path.join(TEX_APTO, nome)
    if not os.path.exists(p):
        p = os.path.join(TEX_GAIA, nome)
    im = bpy.data.images.load(p)
    im.pack()
    _imgs[nome] = im
    return im


def srgb(hx):
    hx = hx.lstrip('#')
    c = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def mat(nome, cor='#ffffff', rough=0.8, metal=0.0, img=None, tint=False, uv=None, troca=False, emite=0.0, alfa=None,
        recorte=False, duplo=False, spec=0.5):
    """cor sRGB. img + tint: imagem multiplicada pela cor. uv: metros por repeticao (projecao de caixa)."""
    rgb = srgb(cor)
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    p = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if p is None:
        nt.nodes.clear()
        p = nt.nodes.new('ShaderNodeBsdfPrincipled')
        sai = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(p.outputs['BSDF'], sai.inputs['Surface'])
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    p.inputs['Base Color'].default_value = (*rgb, 1)
    if 'Specular IOR Level' in p.inputs:
        p.inputs['Specular IOR Level'].default_value = spec
    if img:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = _img(img)
        if tint:
            mx = nt.nodes.new('ShaderNodeMix')
            mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
            mx.inputs['Factor'].default_value = 1.0
            nt.links.new(t.outputs['Color'], mx.inputs['A'])
            mx.inputs['B'].default_value = (*rgb, 1)
            nt.links.new(mx.outputs['Result'], p.inputs['Base Color'])
        else:
            nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
        if recorte:
            nt.links.new(t.outputs['Alpha'], p.inputs['Alpha'])
            m.surface_render_method = 'DITHERED'
            m.blend_method = 'CLIP'
            m.alpha_threshold = 0.4
    if emite:
        p.inputs['Emission Color'].default_value = (*rgb, 1)
        p.inputs['Emission Strength'].default_value = emite
    if alfa is not None:
        p.inputs['Alpha'].default_value = alfa
        m.blend_method = 'BLEND'
    m.use_backface_culling = not duplo
    MATS[nome] = m
    if uv:
        UV[nome] = (uv, troca)
    return m


# ------------------------------------------------------------------ fechamento das camadas em objetos
def objeto(nome_cam):
    c = C[nome_cam]
    if not c.f:
        return None
    me = bpy.data.meshes.new('apto_' + nome_cam)
    me.from_pydata(c.v, [], c.f)
    me.update()
    for n in c.mats:
        me.materials.append(MATS[n])
    me.polygons.foreach_set('material_index', c.fm)
    me.polygons.foreach_set('use_smooth', c.fs)
    uvl = me.uv_layers.new(name='UVMap')
    dados = uvl.data
    v = me.vertices
    k = 0
    for i, pol in enumerate(me.polygons):
        ex = c.fuv[i]
        nome_m = c.mats[c.fm[i]]
        esc, troca = UV.get(nome_m, (1.0, False))
        n_ = pol.normal
        ax = max(range(3), key=lambda q: abs(n_[q]))
        for j, li in enumerate(pol.loop_indices):
            if ex is not None:
                dados[li].uv = ex[j]
                continue
            co = v[me.loops[li].vertex_index].co
            if ax == 2:
                u, w = co.x, co.y
            elif ax == 0:
                u, w = co.y, co.z
            else:
                u, w = co.x, co.z
            if troca:
                u, w = w, u
            dados[li].uv = (u / esc, w / esc)
    me.update()
    ob = bpy.data.objects.new('apto_' + nome_cam, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob

# comum.py -- registro planta<->cena e construtor de malhas (executado dentro do Blender)
# Planta = TIF FyrStudio (10000 x 7039 px). 13,04 px/m. Torres do Gaia casam com a planta:
# para cima na planta = +x da cena; para a direita = -y.
import bpy, math, random, os, json
import numpy as np

PXM = 13.04
def P(px, py):
    return (31.9 - (py - 1510) / PXM, 19.7 - (px - 7187) / PXM)
def Ps(l):
    return [P(*p) for p in l]

def colecao(nome='mundo'):
    c = bpy.data.collections.get(nome)
    if not c:
        c = bpy.data.collections.new(nome)
        bpy.context.scene.collection.children.link(c)
    return c

def limpar(prefixo='mundo'):
    for o in list(bpy.data.objects):
        if o.name.startswith(prefixo):
            bpy.data.objects.remove(o, do_unlink=True)
    for me in list(bpy.data.meshes):
        if me.users == 0 and me.name.startswith(prefixo):
            bpy.data.meshes.remove(me)

class Malha:
    """Acumula quads/tris com UV por canto. Sombreamento plano (sem normais custom)."""
    def __init__(self, nome, mat):
        self.nome, self.mat, self.v, self.f, self.uv = nome, mat, [], [], []
    def face(self, cos, uvs):
        k = len(self.v)
        self.v += cos
        self.f.append(tuple(range(k, k + len(cos))))
        self.uv += uvs
    def objeto(self, liso=False):
        if not self.f:
            return None
        me = bpy.data.meshes.new(self.nome)
        me.from_pydata(self.v, [], self.f)
        me.update()
        uvl = me.uv_layers.new(name='UVMap')
        idx = np.zeros(len(me.loops), np.int32)
        me.loops.foreach_get('vertex_index', idx)
        uv = np.array(self.uv, np.float32)[idx]
        uvl.data.foreach_set('uv', uv.ravel())
        me.materials.append(self.mat)
        if liso:
            me.shade_smooth()
        ob = bpy.data.objects.new(self.nome, me)
        colecao().objects.link(ob)
        return ob

def material(nome, cor=(1, 1, 1), rug=0.9, img=None, emis=None, alpha=None, recriar=True):
    m = bpy.data.materials.get(nome)
    if m and recriar:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(b.outputs['BSDF'], nt.nodes.new('ShaderNodeOutputMaterial').inputs['Surface'])
    b.inputs['Base Color'].default_value = (*cor, 1)
    b.inputs['Roughness'].default_value = rug
    b.inputs['Metallic'].default_value = 0
    def tex(path, cs='sRGB'):
        nome_i = os.path.basename(path)
        im = bpy.data.images.get(nome_i)
        if im:
            im.reload()
        else:
            im = bpy.data.images.load(path)
        im.colorspace_settings.name = cs
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = im
        return n
    if img:
        n = tex(img)
        nt.links.new(n.outputs['Color'], b.inputs['Base Color'])
        if alpha == 'BLEND':
            nt.links.new(n.outputs['Alpha'], b.inputs['Alpha'])
    if emis:
        n = tex(emis)
        nt.links.new(n.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = 1.0
    if alpha == 'BLEND':
        m.blend_method = 'BLEND'
    return m

def suaviza(pts, passo=5.0):
    """Catmull-Rom denso (metros)."""
    p = [np.array(a, float) for a in pts]
    if len(p) == 2:
        L = np.linalg.norm(p[1] - p[0])
        n = max(1, int(L / (passo * 6)))
        return [tuple(p[0] + (p[1] - p[0]) * i / n) for i in range(n + 1)]
    q = [2 * p[0] - p[1]] + p + [2 * p[-1] - p[-2]]
    out = []
    for i in range(1, len(q) - 2):
        a, b, c, d = q[i - 1], q[i], q[i + 1], q[i + 2]
        n = max(2, int(np.linalg.norm(c - b) / passo))
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (3 * b - a - 3 * c + d) * t ** 3)))
    out.append(tuple(p[-1]))
    return out

def normais(pts):
    a = np.array(pts)
    d = np.gradient(a, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    return np.stack([-d[:, 1], d[:, 0]], axis=1)

def fita(m, pts, larg, z, desloc=0.0, uv_esc=None, pular=None):
    """faixa horizontal ao longo de pts. uv_esc: UV de mundo (asfalto casa nas juncoes)."""
    a, n = np.array(pts), normais(pts)
    e = a + n * (desloc + larg / 2)
    d = a + n * (desloc - larg / 2)
    for i in range(len(a) - 1):
        if pular is not None and (pular(a[i] + n[i] * desloc) or pular(a[i + 1] + n[i + 1] * desloc)):
            continue
        cos = [(*d[i], z), (*d[i + 1], z), (*e[i + 1], z), (*e[i], z)]
        if uv_esc:
            uvs = [(c[0] * uv_esc, c[1] * uv_esc) for c in cos]
        else:
            uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        m.face(cos, uvs)

def guia(m, pts, desloc, z0, z1, larg=0.22, pular=None):
    """meio-fio: topo + face voltada para a rua, UV fixo (cor solida)."""
    a, n = np.array(pts), normais(pts)
    lado = 1 if desloc >= 0 else -1
    for i in range(len(a) - 1):
        p0, p1 = a[i] + n[i] * desloc, a[i + 1] + n[i + 1] * desloc
        if pular is not None and (pular(p0) or pular(p1)):
            continue
        q0, q1 = p0 + n[i] * lado * larg, p1 + n[i + 1] * lado * larg
        uv = [(0.5, 0.5)] * 4
        if lado > 0:
            m.face([(*p0, z0), (*p1, z0), (*p1, z1), (*p0, z1)], uv)
            m.face([(*p0, z1), (*p1, z1), (*q1, z1), (*q0, z1)], uv)
        else:
            m.face([(*p1, z0), (*p0, z0), (*p0, z1), (*p1, z1)], uv)
            m.face([(*p1, z1), (*p0, z1), (*q0, z1), (*q1, z1)], uv)

def tracejado(m, pts, larg, z, cheio=3.0, vazio=4.0, desloc=0.0):
    """faixa pintada tracejada ao longo de pts."""
    a = np.array(pts); n = normais(pts)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(a, axis=0), axis=1))])
    t = 0.0
    while t + cheio < s[-1]:
        ini, fim = t, t + cheio
        pp = []
        for u in np.arange(ini, fim + 0.01, max(0.5, cheio / 2)):
            i = min(np.searchsorted(s, u) , len(a) - 1)
            i0 = max(i - 1, 0)
            f = 0 if s[i] == s[i0] else (u - s[i0]) / (s[i] - s[i0])
            pp.append(a[i0] + (a[i] - a[i0]) * f + n[i] * desloc)
        if len(pp) >= 2:
            fita(m, [tuple(x) for x in pp], larg, z, uv_esc=None)
        t += cheio + vazio

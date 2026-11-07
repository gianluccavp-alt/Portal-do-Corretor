# gaia_geo.py -- utilitarios de geometria do gerador (roda dentro do Blender; executado por gaia_modelo.py).
# Geo acumula faces com material, UV, normal e cor por vertice (sombra de oclusao falsa) e vira um objeto
# com normais proprias. Coordenadas em metros, Z para cima. `em()` empilha transformacoes (posicao + giro em Z),
# para montar um movel em coordenadas locais e posicionar na planta.
import bpy, math, json, os
from contextlib import contextmanager
import numpy as np

S_PX = 0.0998
def X(px):
    return (px - 1184.0) * S_PX
def Y(py):
    return (879.5 - py) * S_PX

# escala de textura por material (metros por repeticao: u, v); ausente = (1, 1)
UVESC = {}


def _normal(cos):
    a, b, c = np.array(cos[0], float), np.array(cos[1], float), np.array(cos[2], float)
    n = np.cross(b - a, c - a)
    if np.dot(n, n) < 1e-18 and len(cos) > 3:
        n = np.cross(c - a, np.array(cos[3], float) - a)
    l = math.sqrt(float(np.dot(n, n))) or 1.0
    return tuple(n / l)


class Geo:
    def __init__(self, nome, ao=True):
        self.nome, self.ao = nome, ao
        self.v, self.fi, self.uv, self.n, self.c, self.fm, self.mats = [], [], [], [], [], [], []
        self.idx = {}
        self.tx, self.ty, self.tz, self.ca, self.sa, self.k = 0.0, 0.0, 0.0, 1.0, 0.0, 1.0

    @contextmanager
    def em(self, x=0.0, y=0.0, z=0.0, giro=0.0, esc=1.0):
        velho = (self.tx, self.ty, self.tz, self.ca, self.sa, self.k)
        px, py = self._p(x, y)
        a = math.radians(giro)
        ca, sa = math.cos(a), math.sin(a)
        self.tx, self.ty, self.tz = px, py, self.tz + z * self.k
        self.ca, self.sa = velho[3] * ca - velho[4] * sa, velho[4] * ca + velho[3] * sa
        self.k *= esc
        try:
            yield self
        finally:
            self.tx, self.ty, self.tz, self.ca, self.sa, self.k = velho

    def _p(self, x, y):
        return (self.tx + self.k * (self.ca * x - self.sa * y), self.ty + self.k * (self.sa * x + self.ca * y))

    def _m(self, nome):
        i = self.idx.get(nome)
        if i is None:
            i = len(self.mats)
            self.mats.append(nome)
            self.idx[nome] = i
        return i

    def face(self, cos, mat, uvs=None, nrm=None, cor=None):
        """cos locais (sentido anti-horario visto de fora). uvs: por vertice; nrm: lista por vertice."""
        if nrm is None:
            nf = _normal(cos)
            nrm = [nf] * len(cos)
        if uvs is None:
            su, sv = UVESC.get(mat, (1.0, 1.0))
            nf = nrm[0]
            ax = max(range(3), key=lambda i: abs(nf[i]))
            if ax == 2:
                uvs = [(c[0] / su, c[1] / sv) for c in cos]
            elif ax == 0:
                uvs = [(c[1] / su, c[2] / sv) for c in cos]
            else:
                uvs = [(c[0] / su, c[2] / sv) for c in cos]
        ca, sa, k = self.ca, self.sa, self.k
        tx, ty, tz = self.tx, self.ty, self.tz
        base = len(self.v)
        for j, c in enumerate(cos):
            x = tx + k * (ca * c[0] - sa * c[1])
            y = ty + k * (sa * c[0] + ca * c[1])
            z = tz + k * c[2]
            self.v.append((x, y, z))
            nx, ny, nz = nrm[j]
            self.n.append((ca * nx - sa * ny, sa * nx + ca * ny, nz))
            if cor is not None:
                self.c.append(cor[j] if isinstance(cor, list) else cor)
            elif self.ao:
                if nz > 0.7:
                    v_ = 1.0
                elif nz < -0.7:
                    v_ = 0.72
                else:
                    v_ = 0.66 + 0.34 * min(1.0, max(0.0, z) / 0.9)
                self.c.append(v_)
            else:
                self.c.append(1.0)
        self.uv.extend(uvs)
        self.fi.append((base, len(cos)))
        self.fm.append(self._m(mat))

    # -------------------------------------------------------------- primitivas
    def quad(self, a, b, c, d, mat, **kw):
        self.face([a, b, c, d], mat, **kw)

    def piso(self, x0, x1, y0, y1, z, mat, **kw):
        self.face([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], mat, **kw)

    def caixa(self, x0, x1, y0, y1, z0, z1, mat, topo=None, lados=None, fundo=None, sem_fundo=True, sem=''):
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        l = lados or mat
        self.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], topo or mat)
        if 's' not in sem: self.face([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], l)
        if 'l' not in sem: self.face([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], l)
        if 'n' not in sem: self.face([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], l)
        if 'o' not in sem: self.face([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], l)
        if not sem_fundo or fundo:
            self.face([(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)], fundo or mat)

    def cil(self, x, y, r, z0, z1, mat, seg=12, r2=None, tampa=True, base=False, topo=None):
        r2 = r if r2 is None else r2
        su, sv = UVESC.get(mat, (1.0, 1.0))
        cc = [(math.cos(2 * math.pi * i / seg), math.sin(2 * math.pi * i / seg)) for i in range(seg + 1)]
        inc = (r - r2) / max(1e-6, z1 - z0)
        nz = inc / math.sqrt(1 + inc * inc)
        nh = 1 / math.sqrt(1 + inc * inc)
        for i in range(seg):
            (c0, s0), (c1, s1) = cc[i], cc[i + 1]
            u0, u1 = i / seg * (2 * math.pi * r) / su, (i + 1) / seg * (2 * math.pi * r) / su
            self.face([(x + r * c0, y + r * s0, z0), (x + r * c1, y + r * s1, z0), (x + r2 * c1, y + r2 * s1, z1), (x + r2 * c0, y + r2 * s0, z1)], mat,
                      uvs=[(u0, z0 / sv), (u1, z0 / sv), (u1, z1 / sv), (u0, z1 / sv)],
                      nrm=[(c0 * nh, s0 * nh, nz), (c1 * nh, s1 * nh, nz), (c1 * nh, s1 * nh, nz), (c0 * nh, s0 * nh, nz)])
        if tampa and r2 > 1e-4:
            self.face([(x + r2 * c, y + r2 * s, z1) for c, s in cc[:-1]], topo or mat)
        if base:
            self.face([(x + r * c, y + r * s, z0) for c, s in reversed(cc[:-1])], mat)

    def elipsoide(self, x, y, z, rx, ry, rz, mat, seg=12, aneis=8, exp=1.0, zmin=-1.0):
        """Esfera/superelipsoide (exp < 1 deixa mais quadrado, bom para almofada e puff)."""
        def sg(v, e):
            return math.copysign(abs(v) ** e, v)
        pts = []
        lat0 = math.asin(max(-1.0, zmin))
        for j in range(aneis + 1):
            lat = lat0 + (math.pi / 2 - lat0) * j / aneis
            lin = []
            for i in range(seg + 1):
                lon = 2 * math.pi * i / seg
                cl, sl, co, so = math.cos(lat), math.sin(lat), math.cos(lon), math.sin(lon)
                p = (rx * sg(cl, exp) * sg(co, exp), ry * sg(cl, exp) * sg(so, exp), rz * sg(sl, exp))
                nn = np.array((cl * co / rx, cl * so / ry, sl / rz))
                nn = nn / (np.linalg.norm(nn) or 1)
                lin.append(((x + p[0], y + p[1], z + p[2]), tuple(nn), (i / seg, j / aneis)))
            pts.append(lin)
        for j in range(aneis):
            for i in range(seg):
                a, b, c, d = pts[j][i], pts[j][i + 1], pts[j + 1][i + 1], pts[j + 1][i]
                self.face([a[0], b[0], c[0], d[0]], mat, uvs=[a[2], b[2], c[2], d[2]], nrm=[a[1], b[1], c[1], d[1]])

    def tubo(self, pts, r, mat, seg=6, tampa=False):
        """Tubo por uma polilinha 3D (quadro de cadeira, escorregador, corrimao)."""
        pts = [np.array(p, float) for p in pts]
        ds = [pts[1] - pts[0]] + [pts[i + 1] - pts[i - 1] for i in range(1, len(pts) - 1)] + [pts[-1] - pts[-2]]
        ds = [d / (np.linalg.norm(d) or 1) for d in ds]
        ref = np.array((0, 0, 1.0)) if abs(ds[0][2]) < 0.9 else np.array((1.0, 0, 0))
        u = np.cross(ds[0], ref); u /= np.linalg.norm(u) or 1
        aneis = []
        for p, d in zip(pts, ds):
            u = u - d * np.dot(u, d)
            u /= np.linalg.norm(u) or 1
            w = np.cross(d, u)
            lin = []
            for i in range(seg + 1):
                a = 2 * math.pi * i / seg
                nn = u * math.cos(a) + w * math.sin(a)
                lin.append((tuple(p + nn * r), tuple(nn)))
            aneis.append(lin)
        comp = 0.0
        sv = UVESC.get(mat, (1.0, 1.0))[1]
        for k in range(len(aneis) - 1):
            prox = comp + float(np.linalg.norm(pts[k + 1] - pts[k])) / sv
            for i in range(seg):
                a, b, c, d = aneis[k][i], aneis[k][i + 1], aneis[k + 1][i + 1], aneis[k + 1][i]
                self.face([a[0], b[0], c[0], d[0]], mat, nrm=[a[1], b[1], c[1], d[1]],
                          uvs=[(i / seg, comp), ((i + 1) / seg, comp), ((i + 1) / seg, prox), (i / seg, prox)])
            comp = prox

    def prisma(self, poly, z0, z1, mat, topo=None, nivel_lados=True):
        """Extruda um poligono convexo (ou estrelado no primeiro ponto), anti-horario."""
        self.face([(p[0], p[1], z1) for p in poly], topo or mat)
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            self.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], mat)

    def caixa_red(self, x0, x1, y0, y1, z0, z1, r, mat, topo=None, passos=3):
        """Caixa de cantos arredondados, com normais laterais suaves."""
        poly = []
        for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
            for k in range(passos + 1):
                a = math.radians(a0 + 90 * k / passos)
                poly.append((cx + r * math.cos(a), cy + r * math.sin(a), math.cos(a), math.sin(a)))
        self.face([(p[0], p[1], z1) for p in poly], topo or mat)
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            self.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], mat,
                      nrm=[(a[2], a[3], 0), (b[2], b[3], 0), (b[2], b[3], 0), (a[2], a[3], 0)])

    def painel(self, x0, y0, x1, y1, z0, z1, mat, rect, cor=1.0):
        """Quad vertical de (x0,y0) a (x1,y1), com a face visivel a direita desse sentido, e um retangulo do atlas."""
        u0, v0, u1, v1 = rect
        self.face([(x0, y0, z0), (x1, y1, z0), (x1, y1, z1), (x0, y0, z1)], mat,
                  uvs=[(u0, v0), (u1, v0), (u1, v1), (u0, v1)], cor=cor)

    def tapete(self, x0, x1, y0, y1, z, mat, rect, gira=False, cor=1.0):
        """Quad horizontal com um retangulo do atlas (gira=True roda a imagem 90 graus)."""
        u0, v0, u1, v1 = rect
        uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        if gira:
            uvs = uvs[1:] + uvs[:1]
        self.face([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], mat, uvs=uvs, cor=cor)

    def sombra(self, x0, x1, y0, y1, z=0.012, forca=0.55, disco=False):
        """Mancha de sombra de contato sob um movel (quad com alfa, sem escrever profundidade)."""
        r = MARCAS['sombra_disco' if disco else 'sombra_ret']
        self.tapete(x0, x1, y0, y1, z, 'sombra_contato', r, cor=forca)

    def poligono(self, pts, z, mat):
        """Poligono simples qualquer no plano z (corte de orelhas), anti-horario ou horario."""
        for tri in orelhas(pts):
            self.face([(p[0], p[1], z) for p in tri], mat)

    # -------------------------------------------------------------- saida
    def objeto(self):
        me = bpy.data.meshes.new(self.nome)
        nv = len(self.v)
        me.vertices.add(nv)
        me.vertices.foreach_set('co', np.array(self.v, np.float32).ravel())
        ini = np.array([f[0] for f in self.fi], np.int32)
        tot = np.array([f[1] for f in self.fi], np.int32)
        me.loops.add(nv)
        me.loops.foreach_set('vertex_index', np.arange(nv, dtype=np.int32))
        me.polygons.add(len(self.fi))
        me.polygons.foreach_set('loop_start', ini)
        me.update(calc_edges=True)
        uvl = me.uv_layers.new(name='UVMap')
        uvl.data.foreach_set('uv', np.array(self.uv, np.float32).ravel())
        for nome in self.mats:
            me.materials.append(MATS[nome])
        me.polygons.foreach_set('material_index', np.array(self.fm, np.int32))
        col = me.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
        cc = np.array(self.c, np.float32)
        rgba = np.stack([cc, cc, cc, np.ones_like(cc)], 1)
        col.data.foreach_set('color', rgba.ravel())
        me.color_attributes.active_color = col
        me.update()
        me.shade_smooth()
        me.normals_split_custom_set(np.array(self.n, np.float32).tolist())
        ob = bpy.data.objects.new(self.nome, me)
        bpy.context.scene.collection.objects.link(ob)
        return ob


def orelhas(pts):
    """Triangulacao por corte de orelhas (poligono simples sem furos)."""
    P_ = [tuple(p[:2]) for p in pts]
    ar = sum(P_[i][0] * P_[(i + 1) % len(P_)][1] - P_[(i + 1) % len(P_)][0] * P_[i][1] for i in range(len(P_)))
    if ar < 0:
        P_.reverse()
    def conv(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 1e-9
    def dentro(p, a, b, c):
        return (conv(a, b, p) and conv(b, c, p) and conv(c, a, p))
    out, idx = [], list(range(len(P_)))
    guarda = 0
    while len(idx) > 3 and guarda < 10000:
        guarda += 1
        for i in range(len(idx)):
            ia, ib, ic = idx[i - 1], idx[i], idx[(i + 1) % len(idx)]
            a, b, c = P_[ia], P_[ib], P_[ic]
            if not conv(a, b, c):
                continue
            if any(dentro(P_[j], a, b, c) for j in idx if j not in (ia, ib, ic)):
                continue
            out.append((a, b, c))
            idx.pop(i)
            break
        else:
            break
    if len(idx) == 3:
        out.append(tuple(P_[j] for j in idx))
    return out

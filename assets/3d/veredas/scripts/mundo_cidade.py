# mundo_cidade.py -- anel de cidade: chao, casas, predios, arvores, massas do Park/Novus e postes
RND = random.Random(21)
CENTRO = np.array((-60.0, 220.0))
RAIZ = AQUI

def dentro(pt, poli):
    x, y = pt; c = False; n = len(poli)
    for i in range(n):
        x0, y0 = poli[i]; x1, y1 = poli[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0 + 1e-12) + x0:
            c = not c
    return c
_CORE = Ps(CONTORNO)
def no_core(p):
    return dentro(p, _CORE) or (-120 < p[0] < 150 and -60 < p[1] < 60)

class Grade:
    """ocupacao em celulas de 6 m"""
    def __init__(self):
        self.s = set()
    def livre(self, x, y, r=1):
        i, j = int(x // 6), int(y // 6)
        return all((a, b) not in self.s for a in range(i - r, i + r + 1) for b in range(j - r, j + r + 1))
    def marca(self, x, y, r=1):
        i, j = int(x // 6), int(y // 6)
        for a in range(i - r, i + r + 1):
            for b in range(j - r, j + r + 1):
                self.s.add((a, b))
GRADE = Grade()
QUINTAIS = []

# ---------- construcoes
UV_TEL = lambda i: ((i + 0.5) / 8, 0.5)
def parede(m, a, b, z0, z1, u0, u1, v0, v1):
    m.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])

def casa(mp, mt, cx, cy, w, d, ang, pav, cor=None, tel=None):
    """casa w x d com telhado de 2 aguas; w ao longo de ang"""
    c, s = math.cos(ang), math.sin(ang)
    def q(a, b): return (cx + a * c - b * s, cy + a * s + b * c)
    A, B, C, D = q(-w / 2, -d / 2), q(w / 2, -d / 2), q(w / 2, d / 2), q(-w / 2, d / 2)
    h = 3.0 * pav
    faixa = RND.randrange(4) if cor is None else cor  # 4 cores, 2 linhas cada
    v0 = 1 - (faixa * 2 + pav) / 8
    v1 = v0 + pav / 8
    for (a, b, comp) in ((A, B, w), (B, C, d), (C, D, w), (D, A, d)):
        n = max(1, min(8, round(comp / 3)))
        parede(mp, a, b, 0, h, 0, n / 8, v0, v1)
    t = UV_TEL(RND.choice((0, 2, 4, 4, 6, 6, 7, 3)) if tel is None else tel)
    alt = h + d * 0.22
    E, F = q(-w / 2, 0), q(w / 2, 0)
    p = lambda v, z: (v[0], v[1], z)
    mt.face([p(A, h), p(B, h), p(F, alt), p(E, alt)], [t] * 4)
    mt.face([p(C, h), p(D, h), p(E, alt), p(F, alt)], [t] * 4)
    mt.face([p(B, h), p(C, h), p(F, alt)], [t] * 3)
    mt.face([p(D, h), p(A, h), p(E, alt)], [t] * 3)

def predio_poli(mp, mt, pts, pav, col=None, h_pav=3.0, tel=5):
    """extrusao do contorno, fachada de janelas por pedacos de ate 12 m"""
    pts = list(pts)
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2
    if area < 0:
        pts = pts[::-1]
    col = RND.randrange(4) if col is None else col
    z1 = pav * h_pav
    for i in range(len(pts)):
        a, b = np.array(pts[i]), np.array(pts[(i + 1) % len(pts)])
        L = np.linalg.norm(b - a)
        nseg = max(1, int(math.ceil(L / 12)))
        for k in range(nseg):
            p0, p1 = a + (b - a) * k / nseg, a + (b - a) * (k + 1) / nseg
            cel = max(1, min(4, round(L / nseg / 3)))
            u0 = col * 0.25
            parede(mp, tuple(p0), tuple(p1), 0, z1, u0, u0 + cel / 16, 0, pav / 16)
    t = UV_TEL(tel)
    mt.face([(x, y, z1) for x, y in pts], [t] * len(pts))

def caixa(mp, mt, x0, y0, x1, y1, pav, col=None, h_pav=2.9, tel=5, base=0):
    predio_poli(mp, mt, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], pav, col, h_pav, tel)

def caixa_px(mp, mt, a, b, pav, col=None):
    (x0, y0), (x1, y1) = P(*a), P(*b)
    caixa(mp, mt, min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), pav, col)

def obb(pts):
    """retangulo minimo: centro, lados e angulo"""
    a = np.array(pts, float)
    melhor = None
    for i in range(len(a) - 1):
        d = a[i + 1] - a[i]
        ang = math.atan2(d[1], d[0])
        c, s = math.cos(-ang), math.sin(-ang)
        r = np.stack([a[:, 0] * c - a[:, 1] * s, a[:, 0] * s + a[:, 1] * c], 1)
        lo, hi = r.min(0), r.max(0)
        A = (hi - lo).prod()
        if melhor is None or A < melhor[0]:
            m_ = (lo + hi) / 2
            cc, ss = math.cos(ang), math.sin(ang)
            melhor = (A, m_[0] * cc - m_[1] * ss, m_[0] * ss + m_[1] * cc, hi[0] - lo[0], hi[1] - lo[1], ang)
    return melhor

def area_poli(p):
    return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2

# ---------- arvore: icosfera (mesma para todas), indexada e lisa
_ICO_V, _ICO_F = None, None
def _ico():
    global _ICO_V, _ICO_F
    if _ICO_V is None:
        t = (1 + 5 ** 0.5) / 2
        v = np.array([(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)], float)
        _ICO_V = v / np.linalg.norm(v[0])
        _ICO_F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    return _ICO_V, _ICO_F

class MalhaLisa(Malha):
    def blob(self, c, r, ez, u):
        v, f = _ico()
        k = len(self.v)
        ruid = [1 + RND.uniform(-0.14, 0.14) for _ in range(12)]
        for i, p in enumerate(v):
            self.v.append((c[0] + p[0] * r * ruid[i], c[1] + p[1] * r * ruid[i], c[2] + p[2] * r * ez * ruid[i]))
            self.uv.append((u, 0.5 + p[2] * 0.48))
        for a, b, cc in f:
            self.f.append((k + a, k + b, k + cc))

def arvore(m, x, y, rad, col, blobs=2):
    u = (col + 0.5) / 8
    h = rad * 0.9 + 1.2
    m.blob((x, y, h + rad * 0.5), rad, 0.82, u)
    for _ in range(blobs - 1):
        ang = RND.uniform(0, 6.28)
        m.blob((x + math.cos(ang) * rad * 0.55, y + math.sin(ang) * rad * 0.55, h + rad * RND.uniform(0.2, 0.7)), rad * RND.uniform(0.55, 0.8), 0.8, u)

# ---------- arvores ricas (mesma tecnica do Gaia: miolo escuro + cartoes de folha), so perto do lote
class MalhaRica:
    def __init__(self, nome):
        self.nome, self.v, self.f, self.uv, self.fm, self.n, self.c, self.mats = nome, [], [], [], [], [], [], []
    def mi(self, nome):
        m = bpy.data.materials[nome]
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)
    def face(self, cos, uvs, mname, nrms, cols):
        k = len(self.v)
        self.v += [tuple(map(float, c)) for c in cos]
        self.f.append(tuple(range(k, k + len(cos))))
        self.uv += uvs; self.n += [tuple(map(float, n)) for n in nrms]; self.c += cols
        self.fm.append(self.mi(mname))
    def objeto(self):
        me = bpy.data.meshes.new(self.nome)
        me.from_pydata(self.v, [], self.f)
        me.update()
        idx = np.zeros(len(me.loops), np.int32)
        me.loops.foreach_get('vertex_index', idx)
        me.uv_layers.new(name='UVMap').data.foreach_set('uv', np.array(self.uv, np.float32)[idx].ravel())
        me.polygons.foreach_set('material_index', self.fm)
        col = me.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
        cc = np.concatenate([np.array(self.c, np.float32), np.ones((len(self.c), 1), np.float32)], axis=1)
        col.data.foreach_set('color', cc[idx].ravel())
        me.color_attributes.active_color = col
        me.shade_smooth()
        me.normals_split_custom_set([self.n[i] for i in idx])
        for m in self.mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(self.nome, me)
        colecao().objects.link(ob)

def _un(v):
    return v / (np.linalg.norm(v) + 1e-9)
def _ao(p, c, rad, ez):
    alt = np.clip((p[2] - (c[2] - rad * ez)) / (2 * rad * ez), 0, 1)
    fora = np.clip(np.linalg.norm((p - c) / np.array([rad, rad, rad * ez])), 0, 1)
    k = 0.42 + 0.38 * alt + 0.20 * fora
    return (k, k, k)
def copa_rica(m, c, rad, ez, esp, cartoes=20):
    c = np.array(c, float); esc = np.array([rad, rad, rad * ez])
    vs, fs = _ico()
    pts = [c + p * esc * 0.72 * (1 + RND.uniform(-0.12, 0.12)) for p in vs]
    for idx in fs:
        cos = [pts[i] for i in idx]
        m.face(cos, [(0, 0)] * 3, 'miolo_' + esp, [_un((p - c) / esc) for p in cos], [_ao(p, c, rad, ez) for p in cos])
    for _ in range(cartoes):
        while True:
            d = _un(np.array([RND.gauss(0, 1), RND.gauss(0, 1), RND.gauss(0, 1)]))
            if d[2] > -0.55:
                break
        p0 = c + d * esc * RND.uniform(0.62, 0.98)
        s = rad * RND.uniform(0.55, 0.80)
        n = _un(d + np.array([RND.gauss(0, 0.6), RND.gauss(0, 0.6), RND.gauss(0, 0.6)]))
        t = _un(np.cross(n, (0, 0, 1)) if abs(n[2]) < 0.95 else np.cross(n, (1, 0, 0)))
        bt = np.cross(n, t)
        cos = [p0 - t * s - bt * s, p0 + t * s - bt * s, p0 + t * s + bt * s, p0 - t * s + bt * s]
        nrm = [_un(0.75 * _un((q - c) / esc) + 0.25 * n) for q in cos]
        m.face(cos, [(0, 0), (1, 0), (1, 1), (0, 1)], 'folha_' + esp, nrm, [_ao(q, c, rad, ez) for q in cos])
def tronco_rico(m, x, y, h, r):
    for k in range(5):
        a0, a1 = 2 * math.pi * k / 5, 2 * math.pi * (k + 1) / 5
        cos = [(x + r * math.cos(a0), y + r * math.sin(a0), -0.3), (x + r * math.cos(a1), y + r * math.sin(a1), -0.3), (x + r * 0.6 * math.cos(a1), y + r * 0.6 * math.sin(a1), h), (x + r * 0.6 * math.cos(a0), y + r * 0.6 * math.sin(a0), h)]
        m.face(cos, [(0, 0), (1, 0), (1, 1), (0, 1)], 'tronco', [(math.cos(a0), math.sin(a0), 0), (math.cos(a1), math.sin(a1), 0), (math.cos(a1), math.sin(a1), 0), (math.cos(a0), math.sin(a0), 0)], [(0.7, 0.7, 0.7)] * 4)
PERTO = 300.0  # metros do centro do Gaia

# ---------- montagem
def montar_cidade(M, eixos):
    T = os.path.join(RAIZ, 'tex')
    o = json.load(open(os.path.join(RAIZ, 'osm_cena.json')))
    mPar = Malha('mundo-casas-paredes', material('janela_casas', (1, 1, 1), 0.9, img=os.path.join(T, 'casas.jpg'), emis=os.path.join(T, 'casas_luz.jpg')))
    mTel = Malha('mundo-telhados', material('mundo_telhados', (1, 1, 1), 0.95, img=os.path.join(T, 'telhados.png')))
    mPre = Malha('mundo-predios', material('janela_predios', (1, 1, 1), 0.85, img=os.path.join(T, 'predios.jpg'), emis=os.path.join(T, 'predios_luz.jpg')))
    mArv = MalhaLisa('mundo-arvores', material('mundo_copas', (1, 1, 1), 0.95, img=os.path.join(T, 'copas.png')))
    est = {}
    # chao do anel
    L = 4200
    anel = Malha('mundo-anel', material('janela_anel', (1, 1, 1), 1.0, img=os.path.join(T, 'anel.jpg'), emis=os.path.join(T, 'anel_luz.jpg')))
    anel.face([(-L, -L, -0.6), (L, -L, -0.6), (L, L, -0.6), (-L, L, -0.6)], [(0, 0), (1, 0), (1, 1), (0, 1)])
    anel.objeto()
    # ruas principais do OSM em 3D perto do complexo + bloqueio na grade
    LARG = {'motorway': 12, 'trunk': 12, 'primary': 12, 'secondary': 10, 'tertiary': 8, 'motorway_link': 6, 'trunk_link': 6, 'primary_link': 6, 'secondary_link': 6, 'tertiary_link': 6}
    for r in o['ruas']:
        pts = r['p']
        w = {'residential': 7, 'living_street': 6, 'unclassified': 7, 'service': 4}.get(r['c'], LARG.get(r['c'], 6))
        for a, b in zip(pts, pts[1:]):
            d = math.hypot(b[0] - a[0], b[1] - a[1])
            for t in np.arange(0, d + 1, 4):
                GRADE.marca(a[0] + (b[0] - a[0]) * t / max(d, 1e-6), a[1] + (b[1] - a[1]) * t / max(d, 1e-6), 0 if w < 8 else 1)
        if r['c'] in LARG and r.get('j') is None:
            dmed = min(np.linalg.norm(np.array(q) - CENTRO) for q in pts)
            if dmed < 2600:
                tudo = r['c'].startswith(('motorway', 'trunk'))
                trecho = []
                for q in pts + [None]:
                    if q is not None and (tudo or not no_core(q)):
                        trecho.append(tuple(q))
                    else:
                        if len(trecho) >= 2:
                            fita(M['asfalto'], trecho, w, -0.2, uv_esc=0.09)
                        trecho = []
    # predios do OSM
    nc = np_ = 0
    for b in o['predios']:
        p = [tuple(q) for q in b['p']]
        if len(p) < 4:
            continue
        cx, cy = np.mean(p, axis=0)
        d = np.linalg.norm(np.array((cx, cy)) - CENTRO)
        if d > 3600 or no_core((cx, cy)):
            continue
        a = area_poli(p)
        tipo = b.get('t') or 'yes'
        GRADE.marca(cx, cy, 1 if a < 800 else 3)
        niv = None
        try:
            niv = int(float(b['n'])) if b.get('n') else None
        except ValueError:
            pass
        if niv is None and tipo in ('yes', 'house', 'residential', 'detached') and a < 300:
            if d > 2500:
                continue
            _, ox, oy, w, h, ang = obb(p)
            if w < h:
                w, h = h, w; ang += math.pi / 2
            casa(mPar, mTel, ox, oy, max(w, 4), max(h, 4), ang, RND.choice((1, 1, 1, 2)))
            nc += 1
        else:
            if niv is None:
                if tipo in ('industrial', 'warehouse', 'retail', 'commercial', 'supermarket') or a > 1500:
                    niv = 3
                elif tipo == 'apartments':
                    niv = RND.randint(5, 18)
                else:
                    niv = RND.choice((2, 2, 3, 4, 6, 8)) if a < 1000 else 3
            predio_poli(mPre, mTel, p, niv, tel=RND.choice((3, 4, 5, 7)))
            np_ += 1
    est['osm_casas'], est['osm_predios'] = nc, np_
    # casas procedurais ao longo das ruas locais
    res = [e['p'] for e in o['solo'] if e['u'] == 'res' and len(e['p']) > 2]
    bres = [(min(q[0] for q in p), min(q[1] for q in p), max(q[0] for q in p), max(q[1] for q in p)) for p in res]
    def em_res(x, y):
        for p, bb in zip(res, bres):
            if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] and dentro((x, y), p):
                return True
        return False
    proc = 0
    for r in o['ruas']:
        if r['c'] not in ('residential', 'living_street', 'unclassified', 'service'):
            continue
        pts = r['p']
        for a, b in zip(pts, pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]; L2 = math.hypot(dx, dy)
            if L2 < 6:
                continue
            nx, ny = -dy / L2, dx / L2
            ang = math.atan2(dy, dx)
            for t in np.arange(6, L2, 12.5):
                for lado in (-1, 1):
                    x, y = a[0] + dx * t / L2 + nx * lado * 11.5, a[1] + dy * t / L2 + ny * lado * 11.5
                    d = math.hypot(x - CENTRO[0], y - CENTRO[1])
                    if d > 2000 or RND.random() > 1.05 - d / 2700:
                        continue
                    if not GRADE.livre(x, y, 0) or no_core((x, y)):
                        continue
                    if r['c'] == 'service' and not em_res(x, y):
                        continue
                    GRADE.marca(x, y, 0)
                    casa(mPar, mTel, x, y, RND.uniform(8, 11), RND.uniform(8, 10), ang, RND.choice((1, 1, 2)))
                    proc += 1
                    if d < 1400 and RND.random() < 0.16:  # arvore de quintal, so onde ha casa
                        QUINTAIS.append((x + nx * lado * 9, y + ny * lado * 9))
    est['casas_proc'] = proc
    # torres: 5 perto da rotatoria (fotos aereas) + skyline a noroeste
    def RU(r_, u):  # metros: direita/cima da planta a partir da rotatoria esquerda
        return (-141.95 + u, 514.2 - r_)
    torres = 0
    for r_, u, pav in ((-260, -20, 28), (-292, 34, 26), (-420, 12, 24), (-438, 74, 24), (-560, -40, 22), (-330, 190, 20), (-690, 120, 18)):
        x, y = RU(r_, u)
        predio_poli(mPre, mTel, [(x - 13, y - 9), (x + 13, y - 9), (x + 13, y + 9), (x - 13, y + 9)], pav, RND.choice((0, 1, 3)))
        GRADE.marca(x, y, 3); torres += 1
    A = math.radians(20.76)
    def EN(e, n):  # metros leste/norte do OSM para a cena
        e -= 100; n += 60
        return (e * math.sin(A) + n * math.cos(A) - 141.95, 514.2 - (e * math.cos(A) - n * math.sin(A)))
    for grupo, (e0, e1, n0, n1), qtd, (p0, p1) in (('centro', (-2900, -300, 900, 2900), 95, (12, 30)), ('nordeste', (1300, 2900, 2000, 3100), 22, (10, 22)), ('leste', (2200, 3200, -500, 400), 12, (6, 14))):
        for _ in range(qtd):
            for tent in range(12):
                x, y = EN(RND.uniform(e0, e1), RND.uniform(n0, n1))
                if GRADE.livre(x, y, 3):
                    break
            w, h = RND.uniform(16, 26), RND.uniform(14, 20)
            predio_poli(mPre, mTel, [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], RND.randint(p0, p1))
            GRADE.marca(x, y, 3); torres += 1
    est['torres'] = torres
    # Best Center (galpao comercial com cobertura azul), perto da rotatoria esquerda
    x, y = RU(-170, 210)
    caixa(mPre, mTel, x - 28, y - 55, x + 28, y + 55, 3, 0, 3.0, 4)
    mAzul = Malha('mundo-best-azul', material('mundo_azul', (0.09, 0.27, 0.55), 0.6))
    for k in range(5):
        y0 = y - 50 + k * 21
        cos = [(x - 34, y0, 5.2), (x - 28, y0, 7), (x - 28, y0 + 17, 7), (x - 34, y0 + 17, 5.2)]
        mAzul.face(cos, [(0, 0)] * 4)
    mAzul.objeto()
    # massas do Village Park (16 pav.) e Village Novus (5 pav.): baixa fidelidade
    for a, b in (((2582, 4713), (2778, 4890)), ((2625, 4890), (2735, 5100)), ((2582, 5100), (2778, 5279)),
                 ((3715, 4725), (3915, 4905)), ((3760, 4905), (3870, 5125)), ((3715, 5125), (3915, 5305)),
                 ((2935, 5385), (3110, 5580)), ((3110, 5425), (3300, 5540)), ((3300, 5385), (3475, 5580))):
        caixa_px(mPre, mTel, a, b, 16, 0)
    for x0, x1, linhas in ((4480, 5300, (5040, 5345, 5650, 5960)), (5690, 6470, (5040, 5540, 5835, 6160))):
        for yy in linhas:
            caixa_px(mPre, mTel, (x0, yy - 78), (x1, yy + 78), 5, 1)
    # arvores: copas desenhadas na planta, avenidas e matas do OSM
    arv = 0
    mRica = MalhaRica('mundo-arvores-perto')
    for px_, py_, k in json.load(open(os.path.join(RAIZ, 'arvores_planta.json'))):
        x, y = P(px_ + RND.uniform(-12, 12), py_ + RND.uniform(-12, 12))
        if math.hypot(x, y) < PERTO:
            esp = {'r': 'ipe_rosa', 'a': 'ipe_amarelo'}.get(k) or RND.choice(('verde', 'verde', 'verde_clara', 'verde_escura'))
            rad = RND.uniform(2.6, 3.8) if k == 'v' else RND.uniform(1.8, 2.4)
            cz = rad * 1.5 + RND.uniform(0.8, 1.6)
            tronco_rico(mRica, x, y, cz, 0.16 + 0.03 * rad)
            copa_rica(mRica, (x, y, cz), rad, 0.82, esp)
            arv += 1
            continue
        if k == 'r':
            arvore(mArv, x, y, RND.uniform(2.2, 3.0), 6, 2)
        elif k == 'a':
            arvore(mArv, x, y, RND.uniform(1.8, 2.5), 7, 1)
        else:
            arvore(mArv, x, y, RND.uniform(2.3, 3.6), RND.randrange(6), 2)
        arv += 1
    for e in o['solo']:
        if e['u'] != 'mata' or len(e['p']) < 3:
            continue
        p = e['p']
        xs, ys = [q[0] for q in p], [q[1] for q in p]
        if math.hypot(np.mean(xs) - CENTRO[0], np.mean(ys) - CENTRO[1]) > 2400:
            continue
        A_ = area_poli(p)
        for _ in range(min(260, int(A_ / 500))):
            x, y = RND.uniform(min(xs), max(xs)), RND.uniform(min(ys), max(ys))
            if dentro((x, y), p):
                arvore(mArv, x, y, RND.uniform(3.5, 6.5), RND.randrange(5), 1); arv += 1
    for f in o['fileiras']:
        for a, b in zip(f, f[1:]):
            d = math.hypot(b[0] - a[0], b[1] - a[1])
            for t in np.arange(0, d, 9):
                arvore(mArv, a[0] + (b[0] - a[0]) * t / max(d, 1), a[1] + (b[1] - a[1]) * t / max(d, 1), RND.uniform(3, 5), RND.randrange(5), 1); arv += 1
    # no meio das casas (quintais) ate 1,5 km
    for qx, qy in QUINTAIS:
        arvore(mArv, qx, qy, RND.uniform(2.2, 3.8), RND.randrange(5), 1); arv += 1
    est['arvores'] = arv
    # postes: eixo das ruas (dos dois lados), a cada 32 m + rotatorias + lote do Gaia
    mPos = Malha('mundo-postes', material('mundo_poste', (0.38, 0.39, 0.40), 0.6))
    mLam = Malha('mundo-lampadas', material('janela_lampada', (0.85, 0.85, 0.8), 0.5, emis=os.path.join(T, 'lampada.png')))
    mChao = Malha('mundo-luz-chao', material('luz_chao', (1, 1, 1), 1.0, img=os.path.join(T, 'luz_radial.png'), alpha='BLEND'))
    mHalo = Malha('mundo-luz-halo', material('luz_halo', (1, 1, 1), 1.0, img=os.path.join(T, 'luz_radial.png'), alpha='BLEND'))
    def poste(x, y, dx, dy, alt=8.0, z0=0.0, raio=11.0):
        w = 0.09
        for (a, b) in (((x - w, y - w), (x + w, y - w)), ((x + w, y - w), (x + w, y + w)), ((x + w, y + w), (x - w, y + w)), ((x - w, y + w), (x - w, y - w))):
            parede(mPos, a, b, z0, alt, 0, 0, 0, 0)
        hx, hy = x + dx * 1.6, y + dy * 1.6
        nx, ny = -dy * 0.06, dx * 0.06
        mPos.face([(x + nx, y + ny, alt), (hx + nx, hy + ny, alt), (hx - nx, hy - ny, alt), (x - nx, y - ny, alt)], [(0, 0)] * 4)
        mLam.face([(hx - 0.3, hy - 0.2, alt - 0.05), (hx + 0.3, hy - 0.2, alt - 0.05), (hx + 0.3, hy + 0.2, alt - 0.05), (hx - 0.3, hy + 0.2, alt - 0.05)], [(0.5, 0.5)] * 4)
        mLam.face([(hx - 0.3, hy - 0.2, alt - 0.05), (hx - 0.3, hy + 0.2, alt - 0.05), (hx + 0.3, hy + 0.2, alt - 0.05), (hx + 0.3, hy - 0.2, alt - 0.05)], [(0.5, 0.5)] * 4)
        cz = 0.14
        cx, cy = hx + dx * 1.5, hy + dy * 1.5
        mChao.face([(cx - raio, cy - raio, cz), (cx + raio, cy - raio, cz), (cx + raio, cy + raio, cz), (cx - raio, cy + raio, cz)], [(0, 0), (1, 0), (1, 1), (0, 1)])
        s = 2.2
        for (ux, uy) in ((1, 0), (0, 1)):
            mHalo.face([(hx - ux * s, hy - uy * s, alt - s), (hx + ux * s, hy + uy * s, alt - s), (hx + ux * s, hy + uy * s, alt + s), (hx - ux * s, hy - uy * s, alt + s)], [(0, 0), (1, 0), (1, 1), (0, 1)])
    np2 = 0
    LADOS = {'av-norte': (9.0, -1), 'av-sul': (10.0, 1), 'rua-gaia': (9.2, 0), 'rua-01': (10.0, 0), 'alca': (9.0, 0), 'prolong-o': (12.0, 1), 'prolong-l': (12.0, -1), 'rua-baixo': (7.5, 0)}
    for k, (w, ld) in LADOS.items():
        a = np.array(eixos[k]); n = normais(eixos[k])
        s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(a, axis=0), axis=1))])
        ladovez = 1
        for t in np.arange(10, s[-1], 34):
            i = int(np.searchsorted(s, t)); i = min(i, len(a) - 1)
            lado = ld if ld else ladovez
            ladovez = -ladovez
            x, y = a[i] + n[i] * lado * (w / 2 + 0.9)
            poste(x, y, *(-n[i] * lado)); np2 += 1
    for c, ri, re in ROTAT:
        cc = np.array(P(*c)); ri /= PXM
        for j in range(8):
            t = j * math.pi / 4
            v = np.array((math.cos(t), math.sin(t)))
            x, y = cc + v * (ri - 1.0)
            poste(x, y, *v, alt=9.0, raio=13); np2 += 1
    # entrada do Gaia: o asfalto do lote rompe a calcada ate a rua
    mPatch = M['asfalto']
    cos = [(127.2, -51.0, 0.06), (130.7, -51.0, 0.06), (130.7, -41.0, 0.06), (127.2, -41.0, 0.06)]
    mPatch.face(cos, [(q[0] * 0.09, q[1] * 0.09) for q in cos])
    # lote do Gaia: canteiros centrais e perimetro (px do render de cima -> metros)
    def G(u, v): return (6.7 + (u - 750) * 0.1733, -2 - (v - 400) * 0.1733)
    ng = 0
    for u in (290, 480, 625, 830, 975):
        for v in (140, 300, 470, 560):
            x, y = G(u, v)
            poste(x, y, 0, -1 if v > 300 else 1, alt=6.5, raio=12); ng += 1
    for u in (130, 400, 700, 1000, 1260):
        x, y = G(u, 648)
        poste(x, y, 0, 1, alt=6.5, raio=12); ng += 1
    for v in (180, 420, 560):
        x, y = G(62, v)
        poste(x, y, 1, 0, alt=6.5, raio=12); ng += 1
    for u, v in ((1310, 260), (1420, 300), (1420, 460), (1420, 620), (1250, 350), (1120, 560)):
        x, y = G(u, v)
        poste(x, y, -1, 0, alt=6.5, raio=12); ng += 1
    est['postes'], est['postes_gaia'] = np2, ng
    for m in (mPar, mTel, mPre, mPos, mLam, mChao, mHalo):
        m.objeto()
    mArv.objeto(liso=True)
    mRica.objeto()
    est['faces_perto'] = len(mRica.f)
    est['faces'] = {m.nome: len(m.f) for m in (mPar, mTel, mPre, mArv, mPos, mChao)}
    return est

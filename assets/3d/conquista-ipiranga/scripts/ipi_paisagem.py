# ipi_paisagem.py -- ipes, arvores, palmeiras e carros (especies e carro vindos do gerador do Gaia).
# Posicoes: ipi_planta.py (IPES detectados pela cor, ARVORES, PALMEIRAS, CARROS). Executado por ipi_modelo.py.

ESPECIES = {
    'verde': ('#4c7631', 'folhas2.png'), 'verde_clara': ('#6f9440', 'folhas2.png'), 'verde_escura': ('#335a2a', 'folhas2.png'),
    'ipe_rosa': ('#c0508f', 'flores.png'), 'ipe_amarelo': ('#e8bf2f', 'flores.png'), 'branca': ('#e9eadf', 'flores.png'),
    'laranja': ('#d98a26', 'flores.png'), 'roxa': ('#8c5aa0', 'flores.png'), 'oliva': ('#8d9a3e', 'folhas2.png'),
}


def materiais_paisagem():
    mat('tronco', '#5b4a3a', 0.95)
    mat('tronco_palmeira', '#ffffff', 0.95, img='tronco_palmeira.jpg', uv=(1.0, 2.0))
    for nome, (cor, img) in ESPECIES.items():
        mat('miolo_' + nome, tuple(c * 0.5 for c in srgb(cor)), 0.95)
        mat('folha_' + nome, cor, 0.8, img=img, tint=True, recorte=True, img_mean=0.8)
    mat('fronde', '#5f8739', 0.7, img='fronde.png', tint=True, recorte=True, img_mean=0.82)
    mat('touceira_verde', '#4e7a35', 0.85, img='touceira.png', tint=True, recorte=True, img_mean=0.75)
    mat('touceira_vermelha', '#9c2130', 0.85, img='touceira.png', tint=True, recorte=True, img_mean=0.75)
    mat('touceira_roxa', '#6b4a7a', 0.85, img='touceira.png', tint=True, recorte=True, img_mean=0.75)
    mat('touceira_clara', '#88a44e', 0.85, img='touceira.png', tint=True, recorte=True, img_mean=0.75)
    mat('flores_laranja', '#e0802c', 0.8, img='flores.png', tint=True, recorte=True, img_mean=0.8)
    mat('terra', '#3e3226', 1.0)
    for nome, cor in CORES_CARRO.items():
        mat('carro_' + nome, cor, 0.28, metal=0.55)
    mat('carro_vidro', '#16202a', 0.08, metal=0.3)
    mat('pneu', '#17181a', 0.9)
    mat('farol', '#f1efe6', 0.2)
    mat('lanterna', '#8c1a1e', 0.3)
    mat('roda', '#9a9da2', 0.35, metal=0.6)


CORES_CARRO = {'branco': '#e6e6e4', 'prata': '#a9acb0', 'grafite': '#3d4045', 'azul': '#23426f', 'vermelho': '#8e1f22', 'verde': '#27412f'}


def _u(v):
    n = np.linalg.norm(v)
    return v / (n or 1)


def _copa(g, rnd, c, rad, ez, esp, cartoes=70):
    """Copa de lobos irregulares: miolo escuro + cartoes com normal para fora (luz de volume)."""
    c = np.array(c, float)
    lobos = []
    n_l = rnd.randint(4, 7)
    for i in range(n_l):
        d = np.array([rnd.gauss(0, 1), rnd.gauss(0, 1), abs(rnd.gauss(0, 0.7)) - 0.15])
        d = _u(d)
        lobos.append((c + d * np.array([rad, rad, rad * ez]) * rnd.uniform(0.38, 0.62), rad * rnd.uniform(0.48, 0.68)))
    miolo = 'miolo_' + esp
    for p, r in lobos[:3]:
        g.elipsoide(p[0], p[1], p[2], r * 0.72, r * 0.72, r * 0.62, miolo, seg=7, aneis=4, exp=1.0)
    fol = 'folha_' + esp
    for k in range(cartoes):
        p, r = lobos[k % n_l]
        d = np.array([rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0.25, 1)])
        d = _u(d)
        centro = p + d * r * rnd.uniform(0.55, 1.0)
        s = r * rnd.uniform(0.55, 0.85)
        nn = _u(d + np.array([rnd.gauss(0, 0.6), rnd.gauss(0, 0.6), rnd.gauss(0, 0.6)]))
        t = _u(np.cross(nn, (0, 0, 1))) if abs(nn[2]) < 0.95 else _u(np.cross(nn, (1, 0, 0)))
        b = np.cross(nn, t)
        a = rnd.uniform(0, 6.283)
        t, b = t * math.cos(a) + b * math.sin(a), -t * math.sin(a) + b * math.cos(a)
        cos = [centro - t * s - b * s, centro + t * s - b * s, centro + t * s + b * s, centro - t * s + b * s]
        nrm = [tuple(_u(0.8 * _u(q - c) + 0.2 * nn)) for q in cos]
        ao = []
        for q in cos:
            alt = max(0.0, min(1.0, (q[2] - (c[2] - rad * ez)) / (2 * rad * ez)))
            ao.append(0.50 + 0.50 * alt)
        g.face([tuple(q) for q in cos], fol, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], nrm=nrm, cor=ao)


def _galho(g, a, b, r0, r1):
    g.tubo([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2 + 0.05), b], (r0 + r1) / 2, 'tronco', seg=5)


def arvore(g, rnd, x, y, esp, escala=1.0):
    if esp.startswith('ipe') or esp == 'branca':
        fuste = rnd.uniform(2.0, 2.6) * escala; rad = rnd.uniform(1.5, 2.0) * escala; ez = 0.72
    else:
        fuste = rnd.uniform(1.9, 2.5) * escala; rad = rnd.uniform(1.4, 1.9) * escala; ez = 0.85
    cz = fuste + rad * ez * 0.7
    inc = (rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05))
    topo = (x + inc[0] * cz, y + inc[1] * cz, cz)
    g.cil(x, y, 0.13 * (0.7 + 0.3 * escala), 0, fuste, 'tronco', seg=7, r2=0.08, tampa=False)
    b0 = (x + inc[0] * fuste, y + inc[1] * fuste, fuste)
    for k in range(4):
        a = rnd.uniform(0, 6.283)
        fim = (b0[0] + math.cos(a) * rad * 0.55, b0[1] + math.sin(a) * rad * 0.55, b0[2] + rnd.uniform(0.7, 1.4) * escala)
        _galho(g, b0, fim, 0.07, 0.03)
    _copa(g, rnd, topo, rad, ez, esp, cartoes=int(66 + 14 * escala))


def palmeira(g, rnd, x, y, escala=1.0):
    h = rnd.uniform(6.2, 8.4) * escala
    inc = (rnd.uniform(-0.04, 0.04), rnd.uniform(-0.04, 0.04))
    r0, r1 = 0.22 * escala, 0.14 * escala
    pts = [(x + inc[0] * h * t, y + inc[1] * h * t, h * t) for t in (0, 0.25, 0.5, 0.75, 1.0)]
    g.tubo(pts, (r0 + r1) / 2, 'tronco_palmeira', seg=9)
    top = np.array(pts[-1])
    g.elipsoide(top[0], top[1], top[2] + 0.05, 0.2 * escala, 0.2 * escala, 0.38 * escala, 'tronco_palmeira', seg=7, aneis=4)
    n = 17
    a0 = rnd.uniform(0, 6.28)
    for k in range(n):
        a = a0 + k * 2.399963  # angulo de ouro: coroa cheia sem cara de carrossel
        cam = k / n
        Lf = rnd.uniform(2.3, 2.9) * escala * (0.82 + 0.3 * cam)
        sobe = (1.4 - 1.3 * cam) * rnd.uniform(0.8, 1.2) * escala
        cai = (0.7 + 1.5 * cam) * rnd.uniform(0.85, 1.15) * escala
        d = np.array([math.cos(a), math.sin(a), 0.0]); s = np.array([-d[1], d[0], 0.0])
        w = rnd.uniform(0.46, 0.58) * escala
        segs = 6
        lin = []
        for i in range(segs + 1):
            t = i / segs
            cc = top + d * Lf * t + np.array([0, 0, sobe * t - cai * t * t + 0.12])
            lin.append((cc - s * w - np.array([0, 0, 0.16 * w]), cc + s * w - np.array([0, 0, 0.16 * w]), t))
        tom = rnd.uniform(0.72, 1.0)
        for i in range(segs):
            a_, b_, ta = lin[i]; d_, c_, tb = lin[i + 1]
            nn = _u(np.cross(b_ - a_, d_ - a_))
            if nn[2] < 0:
                nn = -nn
            g.face([tuple(a_), tuple(b_), tuple(c_), tuple(d_)], 'fronde', uvs=[(ta, 0), (ta, 1), (tb, 1), (tb, 0)],
                   nrm=[tuple(_u(nn + np.array([0, 0, 0.5])))] * 4, cor=[tom * (0.82 + 0.18 * ta)] * 2 + [tom * (0.82 + 0.18 * tb)] * 2)


def canteiro(g, rnd, x0, x1, y0, y1, esp='touceira_verde', alt=0.55, passo=0.62, solo=True):
    """Canteiro retangular (metros): solo escuro + touceiras em cartoes cruzados."""
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    if solo:
        g.piso(x0, x1, y0, y1, 0.16, 'terra')
    xx = x0 + passo / 2
    while xx < x1:
        yy = y0 + passo / 2
        while yy < y1:
            px = xx + rnd.uniform(-0.15, 0.15); py = yy + rnd.uniform(-0.15, 0.15)
            h_ = alt * rnd.uniform(0.75, 1.2)
            w_ = passo * rnd.uniform(0.62, 0.85)
            a = rnd.uniform(0, 3.14)
            for da in (0, 1.57):
                ca, sa = math.cos(a + da) * w_, math.sin(a + da) * w_
                k = rnd.uniform(0.78, 1.0)
                g.face([(px - ca, py - sa, 0.14), (px + ca, py + sa, 0.14), (px + ca, py + sa, 0.14 + h_), (px - ca, py - sa, 0.14 + h_)], esp,
                       uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], nrm=[(0, 0, 1)] * 4, cor=[0.55 * k, 0.55 * k, k, k])
            yy += passo
        xx += passo


def arbusto(g, rnd, x, y, r, esp='verde'):
    g.elipsoide(x, y, r * 0.7, r * 0.72, r * 0.72, r * 0.6, 'miolo_' + esp, seg=7, aneis=3, zmin=-0.2)
    for k in range(int(14 + 10 * r)):
        d = _u(np.array([rnd.gauss(0, 1), rnd.gauss(0, 1), abs(rnd.gauss(0.4, 0.7))]))
        c = np.array((x, y, r * 0.7)) + d * r * rnd.uniform(0.55, 0.98)
        s = r * rnd.uniform(0.32, 0.5)
        t = _u(np.cross(d, (0.2, 0.3, 1)))
        b = np.cross(d, t)
        cos = [c - t * s - b * s, c + t * s - b * s, c + t * s + b * s, c - t * s + b * s]
        nrm = [tuple(_u(d + np.array([0, 0, 0.4])))] * 4
        ao = [0.55 + 0.45 * min(1.0, max(0.0, q[2] / (r * 1.5))) for q in cos]
        g.face([tuple(q) for q in cos], 'folha_' + esp, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], nrm=nrm, cor=ao)


# ------------------------------------------------------------------ paisagem (posicoes medidas na implantacao)
def paisagem(g):
    rnd = random.Random(21)
    for px, py, esp in PL.ARVORES:
        arvore(g, rnd, X(px) + rnd.uniform(-0.2, 0.2), Y(py) + rnd.uniform(-0.2, 0.2), esp, rnd.uniform(0.85, 1.15))
    for px, py in PL.IPES:      # ipes de flor rosa-arroxeada, como na implantacao e na perspectiva
        arvore(g, rnd, X(px), Y(py), 'ipe_rosa' if rnd.random() < 0.7 else 'roxa', rnd.uniform(0.8, 1.0))
    for px, py in PL.PALMEIRAS:
        palmeira(g, rnd, X(px), Y(py), rnd.uniform(0.85, 1.05))


# ------------------------------------------------------------------ carros
def carro(g, cor, suv=False):
    """Carro em coordenadas locais: eixo x, frente em +x, chao em z=0."""
    c = 'carro_' + cor
    L_, W_ = (2.25, 0.92) if suv else (2.15, 0.88)
    hb, hc, ht = (0.92, 1.0, 1.62) if suv else (0.8, 0.86, 1.42)
    z0 = 0.22
    # carroceria: perfil lateral extrudado
    per = [(-L_, z0 + 0.06), (-L_ + 0.12, z0), (L_ - 0.12, z0), (L_, z0 + 0.1), (L_ + 0.02, hb - 0.22), (L_ - 0.12, hb - 0.08), (1.25, hc - 0.02), (1.0, hc),
           (-L_ + 0.22, hc), (-L_ + 0.02, hb - 0.08), (-L_ - 0.02, hb - 0.3)]
    for s in (-1, 1):
        cos = [(p[0], s * W_, p[1]) for p in (per if s < 0 else per[::-1])]
        g.face(cos, c, uvs=[(0, 0)] * len(cos), nrm=[(0, s, 0)] * len(cos))
    n = len(per)
    for i in range(n):
        a, b = per[i], per[(i + 1) % n]
        if i == 0:
            continue
        cos = [(a[0], W_, a[1]), (a[0], -W_, a[1]), (b[0], -W_, b[1]), (b[0], W_, b[1])]
        g.face(cos[::-1] if _normal(cos)[2] < -0.1 else cos, c)
    # habitaculo: vidro com teto
    ti = 0.82 * W_
    tp = [(1.0, hc), (0.2, ht), (-1.25, ht - 0.03), (-1.8, hc)]
    for s in (-1, 1):
        cos = [(p[0], s * (W_ if p[1] == hc else ti), p[1]) for p in (tp[::-1] if s > 0 else tp)]
        cos = cos if _normal(cos)[1] * s > 0 else cos[::-1]
        g.face(cos, 'carro_vidro', uvs=[(0, 0)] * 4)
    g.face([(1.0, -W_ * 0.96, hc), (1.0, W_ * 0.96, hc), (0.2, ti, ht), (0.2, -ti, ht)], 'carro_vidro', uvs=[(0, 0)] * 4)
    g.face([(-1.8, W_ * 0.96, hc), (-1.8, -W_ * 0.96, hc), (-1.25, -ti, ht - 0.03), (-1.25, ti, ht - 0.03)], 'carro_vidro', uvs=[(0, 0)] * 4)
    g.face([(0.2, -ti, ht + 0.012), (0.2, ti, ht + 0.012), (-1.25, ti, ht - 0.018), (-1.25, -ti, ht - 0.018)], c, uvs=[(0, 0)] * 4)
    for s in (-1, 1):   # soleira e arcos escuros: tiram o aspecto de caixa
        g.caixa(-L_ + 0.1, L_ - 0.1, s * W_ - 0.012, s * W_ + 0.012, z0, z0 + 0.14, 'pneu')
    # colunas, farois, lanternas
    for s in (-1, 1):
        y_ = s * (W_ - 0.02)
        g.caixa(-0.5, -0.4, min(y_, y_ * 0.92), max(y_, y_ * 0.92), hc, ht - 0.02, c)
        g.caixa(L_ - 0.02, L_ + 0.01, s * 0.55, s * 0.85, hb - 0.32, hb - 0.2, 'farol')
        g.caixa(-L_ - 0.01, -L_ + 0.02, s * 0.55, s * 0.85, hb - 0.3, hb - 0.16, 'lanterna')
    for ex in (1.35, -1.35):
        for s in (-1, 1):
            # rodas: eixo em y
            yc = s * (W_ - 0.1)
            seg = 12
            r = 0.33
            for i in range(seg):
                a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
                g.face([(ex + r * math.cos(a0), yc - 0.11, r + r * math.sin(a0)), (ex + r * math.cos(a1), yc - 0.11, r + r * math.sin(a1)),
                        (ex + r * math.cos(a1), yc + 0.11, r + r * math.sin(a1)), (ex + r * math.cos(a0), yc + 0.11, r + r * math.sin(a0))][::-1],
                       'pneu', uvs=[(0, 0)] * 4)
            yf = yc + s * 0.112
            pts = [(ex + 0.3 * math.cos(2 * math.pi * i / seg), yf, r + 0.3 * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
            g.face(pts[::-1] if s > 0 else pts, 'pneu', uvs=[(0, 0)] * seg)
            pts = [(ex + 0.19 * math.cos(2 * math.pi * i / seg), yf + s * 0.005, r + 0.19 * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
            g.face(pts[::-1] if s > 0 else pts, 'roda', uvs=[(0, 0)] * seg)



def carros(g):
    rnd = random.Random(5)
    nomes = ['branco', 'prata', 'prata', 'grafite', 'grafite', 'azul', 'branco', 'vermelho', 'verde']
    for px, py, giro in PL.CARROS:
        ang = giro + (180 if rnd.random() < 0.5 else 0)
        with g.em(X(px), Y(py), 0.03, ang):
            carro(g, rnd.choice(nomes), rnd.random() < 0.45)

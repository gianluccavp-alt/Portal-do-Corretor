# gaia_lazer.py -- edificios e areas externas do lazer, sem teto nos ambientes fechados (como em 26-lazer.jpg).
# Medidas: gaia_planta.py (px). Mobiliario: gaia_moveis.py. Executado por gaia_modelo.py dentro do Blender.

Z_PISO = 0.16          # piso acabado do lazer
H_PAREDE = 3.0         # corte das paredes
E_PAREDE = 0.14
Z_AGUA = 0.10


def RM(r):
    """retangulo em px -> (x0, x1, y0, y1) em metros, com y0 < y1"""
    return X(r[0]), X(r[2]), Y(r[3]), Y(r[1])


def materiais_lazer():
    P_ = 'porcelanato.jpg'
    mat('deck', '#d6d0c5', 0.55, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('piso_int', '#d9d4ca', 0.35, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('piso_cinza', '#b9b6af', 0.4, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('piso_madeira', '#ffffff', 0.45, img='madeira_piso.jpg', uv=3.0)
    mat('carpete', '#7d786c', 0.97, img='emborrachado.jpg', tint=True, uv=1.5)
    mat('pastilha', '#ffffff', 0.25, img='pastilha.jpg', uv=1.6)
    mat('agua', '#3fb4b0', 0.04, blend=0.42, nrm='agua_normal.jpg', nrm_str=0.5, metal=0.0, uv=4.0)
    mat('borda_piscina', '#cfcabc', 0.6)
    mat('paver_bege', '#b6aca0', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    mat('paver_escuro', '#6d6c6c', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    E_ = dict(img='emborrachado.jpg', tint=True, uv=1.5)
    mat('ep_amarelo', '#e4b42c', 0.85, **E_)
    mat('ep_azul', '#2f86c8', 0.85, **E_)
    mat('ep_azul_escuro', '#1f58a6', 0.85, **E_)
    mat('quadra_azul', '#2f5c98', 0.7, **E_)
    mat('quadra_cinza', '#5f6065', 0.7, **E_)
    mat('quadra_borda', '#47494d', 0.8, **E_)
    # paredes internas (prefixo int_: a pagina acende a noite)
    for nome, cor in (('branco', '#e8e3d9'), ('areia', '#cfba9c'), ('laranja', '#c9632b'), ('grafite', '#39454c'), ('azulpub', '#3f5b6c'),
                      ('terracota', '#b4503a'), ('cinza', '#a3a5a6'), ('creme', '#efe6d3'), ('rosa', '#c98476'), ('escuro', '#3a3b3e')):
        mat('int_' + nome, cor, 0.85)
    mat('parede_corte', '#d9d6cf', 0.9)
    mat('rodape', '#b5b1a8', 0.7)
    mat('vidro_lazer', '#c6d8e0', 0.05, blend=0.12, metal=0.1)
    mat('caixilho_ext', '#e9e7e1', 0.45)
    mat('porta_veneziana', '#e7e6e1', 0.6, img='ripado.jpg', tint=True, img_mean=0.82, uv=(0.5, 3.0))
    mat('ferro_escuro', '#2a2d30', 0.55, metal=0.35)
    mat('ferro_verde', '#2d4538', 0.55, metal=0.3)
    mat('alambrado', '#2f4a3b', 0.6, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.5, 0.5))
    mat('gradil_preto', '#26282b', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('gradil_branco', '#e9e7e2', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('reboco_marrom', '#847566', 0.92, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('atlas', '#ffffff', 0.5, img='atlas_lazer.jpg')
    mat('placa_gaia', '#ffffff', 0.6, img='placa_gaia.jpg')
    mat('tela', '#ffffff', 0.25, img='atlas_lazer.jpg')
    mat('luz_poste', '#fff1cc', 0.4)
    mat('luz_chao', '#ffffff', 1.0, img='luz_radial.jpg')
    mat('rede_gol', '#f2f2ee', 0.7, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.25, 0.25))


def _caixa_piso(g, rects, z, mat_topo, lados='meio_fio'):
    for x0, x1, y0, y1 in rects:
        g.caixa(x0, x1, y0, y1, 0, z, mat_topo, lados=lados)


def parede(g, a, b, ext, inte, aberturas=(), z0=Z_PISO, z1=H_PAREDE + Z_PISO, e=E_PAREDE, ini_ext=0.0, fim_ext=0.0):
    """Parede de a para b; a ESQUERDA do sentido a->b e o lado de dentro (percorra a sala no anti-horario).
    aberturas: (s0, s1, zb, zt, tipo, nfolhas) medidos a partir de a. tipo: janela | porta_vidro | vao | veneziana"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L_ = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))
    def bloco(u0, u1, za, zb):
        if u1 - u0 < 1e-4 or zb - za < 1e-4:
            return
        g.face([(u0, 0, za), (u1, 0, za), (u1, 0, zb), (u0, 0, zb)], ext)
        g.face([(u1, e, za), (u0, e, za), (u0, e, zb), (u1, e, zb)], inte)
        if zb >= z1 - 1e-4:
            g.face([(u0, 0, zb), (u1, 0, zb), (u1, e, zb), (u0, e, zb)], 'parede_corte')
        else:
            g.face([(u0, 0, zb), (u1, 0, zb), (u1, e, zb), (u0, e, zb)], 'caixilho_ext')
        if za > z0 + 1e-4:
            g.face([(u0, e, za), (u1, e, za), (u1, 0, za), (u0, 0, za)], 'caixilho_ext')
    with g.em(a[0], a[1], 0, ang):
        cur = -ini_ext
        for s0, s1, zb, zt, tipo, n in sorted(aberturas):
            bloco(cur, s0, z0, z1)
            bloco(s0, s1, z0, zb)
            bloco(s0, s1, zt, z1)
            # ombreiras
            g.face([(s0, 0, zb), (s0, e, zb), (s0, e, zt), (s0, 0, zt)], 'caixilho_ext')
            g.face([(s1, e, zb), (s1, 0, zb), (s1, 0, zt), (s1, e, zt)], 'caixilho_ext')
            if tipo in ('janela', 'porta_vidro'):
                ym = e / 2
                f = 0.035
                g.caixa(s0, s1, ym - f, ym + f, zb, zb + 0.05, 'caixilho_ext')
                g.caixa(s0, s1, ym - f, ym + f, zt - 0.05, zt, 'caixilho_ext')
                for k in range(n + 1):
                    u = s0 + (s1 - s0) * k / n
                    g.caixa(u - 0.025, u + 0.025, ym - f, ym + f, zb, zt, 'caixilho_ext')
                g.face([(s0, ym, zb), (s1, ym, zb), (s1, ym, zt), (s0, ym, zt)], 'vidro_lazer', cor=1.0)
                g.face([(s1, ym, zb), (s0, ym, zb), (s0, ym, zt), (s1, ym, zt)], 'vidro_lazer', cor=1.0)
            elif tipo == 'veneziana':
                g.caixa(s0, s1, e / 2 - 0.02, e / 2 + 0.02, zb, zt, 'porta_veneziana')
            cur = s1
        bloco(cur, L_ + fim_ext, z0, z1)
        # rodape interno
        g.caixa(-ini_ext + e, L_ + fim_ext - e, e, e + 0.012, z0, z0 + 0.08, 'rodape', sem='s')


def sala(g, r, piso, paredes, z=Z_PISO):
    """Sala retangular (metros x0,x1,y0,y1). paredes = dict lado -> (ext, int, aberturas). Lados: s l n o (anti-horario)."""
    x0, x1, y0, y1 = r
    g.piso(x0, x1, y0, y1, z + 0.003, piso)
    seq = {'s': ((x0, y0), (x1, y0)), 'l': ((x1, y0), (x1, y1)), 'n': ((x1, y1), (x0, y1)), 'o': ((x0, y1), (x0, y0))}
    for lado, cfg in paredes.items():
        a, b = seq[lado]
        ext, inte, ab = cfg
        parede(g, a, b, ext, inte, ab)


EXT = 'parede_externa'


def janela(s, l=1.5, n=2):
    return (s, s + l, Z_PISO + 0.9, Z_PISO + 2.2, 'janela', n)


def porta_vidro(s, l=2.0, n=2):
    return (s, s + l, Z_PISO, Z_PISO + 2.35, 'porta_vidro', n)


def veneziana(s, l=0.9):
    return (s, s + l, Z_PISO, Z_PISO + 2.15, 'veneziana', 1)


# ------------------------------------------------------------------ pisos externos
def pisos_lazer(g):
    # circulacao de paver cinza
    m = _mascara(PL.CIRCULACAO)
    # tira o que tem piso proprio
    for r in (PL.DECK, PL.PLAYGROUND, PL.CHURRASCO_LAJE, PL.QUADRA_LAJE, PL.GOURMET,
              (PL.BLOCO_X[0], PL.ACADEMIA_Y[0], PL.BLOCO_X[1], 1090), PL.APOIO, PL.GUARITA):
        m[int(r[1]):int(r[3]), int(r[0]):int(r[2])] = False
    for r in _decompor(m):
        g.caixa(X(r[0]), X(r[2]), Y(r[3]), Y(r[1]), 0, Z_PISO - 0.005, 'paver', lados='meio_fio')
    # contrastes de paver escuro, como nos caminhos do corte do book
    for r in ((1890, 925, 1925, 950), (1860, 985, 1900, 1005), (1908, 985, 1930, 1010), (1990, 1095, 2030, 1110), (2115, 1140, 2132, 1175), (2160, 885, 2172, 955),
              (2226, 985, 2228, 990)):
        g.piso(X(r[0]), X(r[2]), Y(r[3]), Y(r[1]), Z_PISO + 0.002, 'paver_escuro')
    # lajes tematicas
    for r, mt in ((PL.CHURRASCO_LAJE, 'paver_bege'), (PL.PRACA14, 'paver'), (PL.CROSSFIT, 'paver_bege'), (PL.LOUNGE_TEEN, 'paver'),
                  (PL.PRACA_JOGOS, 'paver'), (PL.BICICLETARIO, 'paver'), ((2115, 1128, 2185, 1190), 'paver')):
        g.caixa(X(r[0]), X(r[2]), Y(r[3]), Y(r[1]), 0, Z_PISO, mt, lados='meio_fio')
    # solo (passeio) da faixa inferior do lazer
    g.caixa(X(2103), X(2190), Y(1200), Y(1190), 0, Z_PISO, 'paver', lados='meio_fio')


def piscinas(g):
    """Deck de porcelanato com a piscina adulto + deck molhado + infantil, com profundidade real."""
    m = _mascara([PL.DECK])
    for r in (PL.PISCINA, PL.PISCINA_MOLHADO, PL.PISCINA_INFANTIL):
        m[int(r[1]):int(r[3]), int(r[0]):int(r[2])] = False
    for r in _decompor(m):
        g.caixa(X(r[0]), X(r[2]), Y(r[3]), Y(r[1]), 0, Z_PISO, 'deck', lados='meio_fio')
    def parede_bacia(a, b, fundo, topo=Z_PISO):
        # de a para b com a agua a esquerda
        L_ = math.hypot(b[0] - a[0], b[1] - a[1])
        g.face([(a[0], a[1], fundo), (b[0], b[1], fundo), (b[0], b[1], topo), (a[0], a[1], topo)], 'pastilha',
               uvs=[(0, fundo / 1.6), (L_ / 1.6, fundo / 1.6), (L_ / 1.6, topo / 1.6), (0, topo / 1.6)], cor=0.8)
    Fp, Fm, Fi = -1.05, -0.12, -0.30
    # adulto
    x0, x1, y0, y1 = RM(PL.PISCINA)
    g.piso(x0, x1, y0, y1, Fp, 'pastilha', cor=0.72)
    mx0, mx1, my0, my1 = RM(PL.PISCINA_MOLHADO)
    # molhado encostado no lado sul da piscina: parede sul da adulto so fora do trecho do molhado
    parede_bacia((x0, y0), (mx0, y0), Fp)
    parede_bacia((mx1, y0), (x1, y0), Fp)
    parede_bacia((mx0, y0), (mx1, y0), Fp, Fm)      # degrau para o molhado
    parede_bacia((x1, y0), (x1, y1), Fp)
    parede_bacia((x1, y1), (x0, y1), Fp)
    parede_bacia((x0, y1), (x0, y0), Fp)
    # molhado
    g.piso(mx0, mx1, my0, my1, Fm, 'pastilha', cor=0.95)
    parede_bacia((mx0, my0), (mx1, my0), Fm)
    parede_bacia((mx1, my0), (mx1, my1), Fm)
    parede_bacia((mx0, my1), (mx0, my0), Fm)
    # infantil
    ix0, ix1, iy0, iy1 = RM(PL.PISCINA_INFANTIL)
    g.piso(ix0, ix1, iy0, iy1, Fi, 'pastilha', cor=0.9)
    for a, b in (((ix0, iy0), (ix1, iy0)), ((ix1, iy0), (ix1, iy1)), ((ix1, iy1), (ix0, iy1)), ((ix0, iy1), (ix0, iy0))):
        parede_bacia(a, b, Fi)
    # espelho d'agua (superficie unica nos retangulos)
    for r in (PL.PISCINA, PL.PISCINA_MOLHADO, PL.PISCINA_INFANTIL):
        a, b, c, d = RM(r)
        g.piso(a, b, c, d, Z_AGUA, 'agua', cor=1.0)
    # borda de pedra em volta das bacias (fina, acima do deck)
    bd = 0.22
    def borda_ret(r, sul=True):
        a, b, c, d = RM(r)
        g.caixa(a - bd, b + bd, d, d + bd, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
        if sul:
            g.caixa(a - bd, b + bd, c - bd, c, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
        g.caixa(a - bd, a, c, d, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
        g.caixa(b, b + bd, c, d, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
    borda_ret(PL.PISCINA_INFANTIL)
    a, b, c, d = RM(PL.PISCINA)
    g.caixa(a - bd, b + bd, d, d + bd, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
    g.caixa(a - bd, a, c - bd, d, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
    g.caixa(b, b + bd, c - bd, d, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
    g.caixa(a - bd, mx0, c - bd, c, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
    g.caixa(mx1, b + bd, c - bd, c, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
    g.caixa(mx0 - bd, mx0, my0 - bd, c, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
    g.caixa(mx1, mx1 + bd, my0 - bd, c, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
    g.caixa(mx0 - bd, mx1 + bd, my0 - bd, my0, Z_PISO, Z_PISO + 0.02, 'borda_piscina')
    # guarda-corpo branco: lados oeste, norte e sul do deck
    x0, x1, y0, y1 = RM(PL.DECK)
    gradil(g, (x0, y0), (x0, y1), 1.25, 'gradil_branco', 'caixilho_ext', Z_PISO, passo=1.4)
    gradil(g, (x0, y1), (x1, y1), 1.25, 'gradil_branco', 'caixilho_ext', Z_PISO, passo=1.4)
    gradil(g, (x1, y1), (x1, Y(735)), 1.25, 'gradil_branco', 'caixilho_ext', Z_PISO, passo=1.4)


def gradil(g, a, b, h, mt, poste, z=0.0, passo=2.0, mureta=0.0):
    """Gradil de painel recortado com postes. mureta: base macica de altura dada."""
    L_ = math.hypot(b[0] - a[0], b[1] - a[1])
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    with g.em(a[0], a[1], 0, ang):
        z0 = z + mureta
        if mureta:
            g.caixa(0, L_, -0.06, 0.06, z, z0, 'parede_externa', sem='ol')
        su, sv = UVESC.get(mt, (1, 1))
        g.face([(0, 0, z0), (L_, 0, z0), (L_, 0, z0 + h), (0, 0, z0 + h)], mt,
               uvs=[(0, 0), (L_ / su, 0), (L_ / su, 1), (0, 1)], cor=1.0, nrm=[(0, 0, 1)] * 4)
        g.caixa(0, L_, -0.018, 0.018, z0 + h - 0.03, z0 + h + 0.015, poste)
        g.caixa(0, L_, -0.018, 0.018, z0, z0 + 0.03, poste)
        k = 0.0
        while k <= L_ + 1e-3:
            g.caixa(k - 0.03, k + 0.03, -0.03, 0.03, z, z0 + h + 0.03, poste)
            k += passo


def alambrado_quadra(g):
    x0, x1, y0, y1 = RM(PL.QUADRA_LAJE)
    h = 4.2
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        L_ = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        with g.em(a[0], a[1], 0, ang):
            g.face([(0, 0, 0.2), (L_, 0, 0.2), (L_, 0, h), (0, 0, h)], 'alambrado',
                   uvs=[(0, 0.4), (L_ / 0.5, 0.4), (L_ / 0.5, h / 0.5), (0, h / 0.5)], cor=1.0, nrm=[(0, 0, 1)] * 4)
            g.caixa(0, L_, -0.03, 0.03, h - 0.05, h, 'ferro_verde')
            g.caixa(0, L_, -0.025, 0.025, 2.0, 2.05, 'ferro_verde')
            g.caixa(0, L_, -0.03, 0.03, 0.14, 0.32, 'ferro_verde')
            n = max(2, round(L_ / 2.8))
            for k in range(n + 1):
                u = L_ * k / n
                g.caixa(u - 0.04, u + 0.04, -0.04, 0.04, 0, h + 0.03, 'ferro_verde')
                if k < n:   # travamento em X como em 08-quadra
                    u2 = L_ * (k + 1) / n
                    g.tubo([(u, 0, 2.03), (u2, 0, h - 0.05)], 0.018, 'ferro_verde', seg=4)


def _linha_seg(g, a, b, w, z, mt='faixa'):
    segmento(g, a, b, w, z, mt)


def _arco(g, c, r, a0, a1, w, z, n=24, mt='faixa'):
    pts = [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
    for p, q in zip(pts[:-1], pts[1:]):
        segmento(g, p, q, w, z, mt)


def quadra(g):
    """Quadra poliesportiva (implantacao + 08-quadra): azul com garrafoes cinza, linhas brancas, tabelas e traves."""
    x0, x1, y0, y1 = RM(PL.QUADRA_LAJE)
    g.caixa(x0, x1, y0, y1, 0, Z_PISO, 'quadra_borda', lados='meio_fio')
    a, b, c, d = RM(PL.QUADRA)
    z = Z_PISO + 0.004
    g.piso(a, b, c, d, z, 'quadra_azul')
    # dois retangulos cinza
    ax0, ax1 = X(2190), X(2242)
    g.piso(ax0, ax1, Y(725), Y(708), z + 0.002, 'quadra_cinza')
    g.piso(ax0, ax1, Y(800), Y(783), z + 0.002, 'quadra_cinza')
    zl = z + 0.005
    cx, cy = (a + b) / 2, (c + d) / 2
    W_ = 0.05
    for p, q in (((a, c), (b, c)), ((b, c), (b, d)), ((b, d), (a, d)), ((a, d), (a, c)), ((a, cy), (b, cy))):
        segmento(g, p, q, W_, zl)
    _arco(g, (cx, cy), 1.2, 0, 360, W_, zl, n=32)
    # garrafoes e arcos de 3 pontos nas duas pontas
    for s, yb in ((1, d), (-1, c)):
        _arco(g, (cx, yb - s * 1.6), 0.9, 0, 360, W_, zl, n=24)
        for p, q in (((cx - 1.0, yb), (cx - 1.0, yb - s * 1.6)), ((cx + 1.0, yb), (cx + 1.0, yb - s * 1.6)), ((cx - 1.0, yb - s * 1.6), (cx + 1.0, yb - s * 1.6))):
            segmento(g, p, q, W_, zl)
        a0, a1 = (180, 360) if s > 0 else (0, 180)
        _arco(g, (cx, yb), 3.0, a0, a1, W_, zl, n=28)
        # trave de futsal com rede + tabela de basquete
        yf = yb + s * 0.25
        for ex in (-1.0, 1.0):
            g.cil(cx + ex, yf, 0.04, Z_PISO, Z_PISO + 2.0, 'faixa', seg=8, tampa=False)
        g.tubo([(cx - 1.0, yf, Z_PISO + 2.0), (cx + 1.0, yf, Z_PISO + 2.0)], 0.04, 'faixa', seg=8)
        with g.em(cx, yf, 0):
            g.face([(-1.0, 0, Z_PISO), (1.0, 0, Z_PISO), (1.0, 0, Z_PISO + 2.0), (-1.0, 0, Z_PISO + 2.0)], 'rede_gol',
                   uvs=[(0, 0), (8, 0), (8, 8), (0, 8)], cor=1.0, nrm=[(0, 0, 1)] * 4)
        yt = yf + s * 0.35
        g.cil(cx, yt, 0.06, Z_PISO, Z_PISO + 3.3, 'faixa', seg=8)
        g.tubo([(cx, yt, Z_PISO + 3.2), (cx, yb - s * 0.2, Z_PISO + 3.2)], 0.035, 'faixa', seg=6)
        g.caixa(cx - 0.75, cx + 0.75, yb - s * 0.22 - 0.015, yb - s * 0.22 + 0.015, Z_PISO + 2.75, Z_PISO + 3.55, 'caixilho_ext')
        ya = yb - s * 0.45
        _arco3d(g, (cx, ya), 0.22, Z_PISO + 3.05, 'int_laranja')
    alambrado_quadra(g)
    # portao lateral
    g.caixa(x0 - 0.03, x0 + 0.03, Y(760) - 0.6, Y(760) + 0.6, Z_PISO, 2.2, 'ferro_verde')


def _arco3d(g, c, r, z, mt, n=14):
    pts = [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n), z) for k in range(n + 1)]
    g.tubo(pts, 0.012, mt, seg=4)


def pergola(g, r, h=2.75, passo=0.5, sentido='x', pilares=None, mt='ferro_escuro', viga=0.12, ripa=0.05):
    """Pergola metalica: pilares nos cantos, 2 vigas, ripas transversais."""
    x0, x1, y0, y1 = r
    z = Z_PISO + h
    for (px, py) in (pilares or ((x0, y0), (x1, y0), (x1, y1), (x0, y1))):
        g.caixa(px - 0.05, px + 0.05, py - 0.05, py + 0.05, Z_PISO, z, mt)
    if sentido == 'x':
        for yy in (y0, y1):
            g.caixa(x0 - 0.08, x1 + 0.08, yy - 0.04, yy + 0.04, z - viga, z, mt)
        p = x0
        while p <= x1 + 1e-3:
            g.caixa(p - ripa / 2, p + ripa / 2, y0 - 0.1, y1 + 0.1, z, z + 0.1, mt)
            p += passo
    else:
        for xx in (x0, x1):
            g.caixa(xx - 0.04, xx + 0.04, y0 - 0.08, y1 + 0.08, z - viga, z, mt)
        p = y0
        while p <= y1 + 1e-3:
            g.caixa(x0 - 0.1, x1 + 0.1, p - ripa / 2, p + ripa / 2, z, z + 0.1, mt)
            p += passo


def grelha(g, r, h=2.75, passo=0.75, mt='ferro_escuro'):
    """Pergola em grelha (como sobre o crossfit e a lateral do salao): duas direcoes de ripas."""
    x0, x1, y0, y1 = r
    z = Z_PISO + h
    for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        g.caixa(px - 0.05, px + 0.05, py - 0.05, py + 0.05, Z_PISO, z, mt)
    p = x0
    while p <= x1 + 1e-3:
        g.caixa(p - 0.03, p + 0.03, y0 - 0.05, y1 + 0.05, z - 0.1, z, mt)
        p += passo
    p = y0
    while p <= y1 + 1e-3:
        g.caixa(x0 - 0.05, x1 + 0.05, p - 0.03, p + 0.03, z, z + 0.08, mt)
        p += passo


# ------------------------------------------------------------------ edificios
def bloco_principal(g):
    """Academia, pub, brinquedoteca e salao de festas + servico (fita de 8,3 m de largura)."""
    bx0, bx1 = X(PL.BLOCO_X[0]), X(PL.BLOCO_X[1])
    ya0, ya1 = Y(PL.ACADEMIA_Y[1]), Y(PL.ACADEMIA_Y[0])
    yp0, yp1 = Y(PL.PUB_Y[1]), Y(PL.PUB_Y[0])
    yb0, yb1 = Y(PL.BRINQ_Y[1]), Y(PL.BRINQ_Y[0])
    ys0, ys1 = Y(PL.SALAO_Y[1]), Y(PL.SALAO_Y[0])
    fim = Y(1090)
    # academia: parede leste laranja (TV + 2 portas), norte grafite (espelho), piso madeira
    sala(g, (bx0, bx1, ya0, ya1), 'piso_madeira', {
        'n': (EXT, 'int_grafite', [janela(5.6, 1.6)]),
        'l': (EXT, 'int_laranja', [porta_vidro(1.0, 2.0), porta_vidro(5.2, 2.0)]),
        'o': (EXT, 'int_branco', [porta_vidro(1.0, 2.4, 3), porta_vidro(5.0, 2.4, 3)]),
    })
    # pub: azul petroleo, piso claro
    sala(g, (bx0, bx1, yp0, yp1), 'piso_int', {
        'n': (EXT, 'int_azulpub', []),
        'l': (EXT, 'int_azulpub', [janela(1.2, 1.8, 3)]),
        'o': (EXT, 'int_azulpub', [porta_vidro(0.9, 2.2, 2)]),
    })
    # brinquedoteca: creme com mural, piso madeira
    sala(g, (bx0, bx1, yb0, yb1), 'piso_madeira', {
        'n': (EXT, 'int_creme', []),
        'l': (EXT, 'int_creme', [porta_vidro(1.0, 1.9, 3)]),
        'o': (EXT, 'int_creme', [porta_vidro(1.0, 2.0, 2)]),
    })
    # salao: areia, janelas altas, acesso pela pergola leste
    sala(g, (bx0, bx1, Y(1090), ys1), 'piso_int', {
        'n': (EXT, 'int_areia', []),
        'l': (EXT, 'int_areia', [porta_vidro(4.8, 2.6, 3), porta_vidro(8.2, 2.0, 2)]),
        's': (EXT, 'int_cinza', [janela(1.0, 1.2, 1), veneziana(5.8), veneziana(7.0)]),
        'o': (EXT, 'int_areia', [porta_vidro(1.8, 2.4, 3), porta_vidro(5.4, 2.4, 3), janela(9.6, 1.4, 2)]),
    })
    # servico do salao (copa + 2 WC + deposito), sem telhado, paredes internas
    sx0, sx1, sy0, sy1 = RM(PL.SERVICO)
    with g.em(0, 0):
        parede(g, (sx0, sy1), (sx0, sy0), 'int_cinza', 'int_branco', [veneziana(1.2)])
        parede(g, (sx1, sy1), (sx0, sy1), 'int_areia', 'int_branco', [])
        xm = (sx0 + sx1) / 2 + 0.3
        ym = (sy0 + sy1) / 2
        parede(g, (xm, sy0), (xm, sy1), 'int_branco', 'int_branco', [veneziana(0.5), veneziana(2.7)], e=0.1)
        parede(g, (sx1, ym), (xm, ym), 'int_branco', 'int_branco', [], e=0.1)
        parede(g, (xm, ym), (sx0, ym), 'int_branco', 'int_branco', [], e=0.1)
    # guia colorida na lateral do salao (blocos do book)
    for k, cor in enumerate(('ep_azul', 'ep_amarelo', 'ep_azul_escuro')):
        g.caixa(X(2157), X(2160), Y(1062 + k * 7), Y(1056 + k * 7), 0, 0.22, cor)


def churrasqueira(g):
    x0, x1, y0, y1 = RM(PL.CHURRASCO)
    xm = X(2096)
    sala(g, (xm, x1, y0, y1), 'piso_int', {
        'n': (EXT, 'int_terracota', []),
        'o': (EXT, 'int_areia', []),
    })
    sala(g, (x0, xm, y0, y1), 'piso_cinza', {
        's': (EXT, 'int_branco', [veneziana(1.0)]),
        'n': (EXT, 'int_branco', []),
        'o': (EXT, 'int_branco', [janela(1.0, 1.2, 1)]),
    })
    # parede terracota com pilar ate a pergola
    g.caixa(x1 - 0.2, x1, y0 - 0.2, y0, Z_PISO, Z_PISO + 3.0, EXT, topo='parede_corte')
    px0, px1, py0, py1 = RM(PL.PERGOLA_CHURRASCO)
    pergola(g, (x1, px1, Y(740), py1), 2.7, 0.55, 'x', mt='ferro_verde')
    pergola(g, (x0, px1, py0, Y(740)), 2.7, 0.55, 'y', mt='ferro_verde')


def gourmet(g):
    """Varanda gourmet (08): salao aberto ao norte, cozinha ao sul e WC sem teto."""
    x0, x1, y0, y1 = RM(PL.GOURMET)
    g.caixa(x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 0.3, 0, Z_PISO, 'piso_int', lados='meio_fio')
    # paredes (lado norte aberto, com 2 pilares claros)
    parede(g, (x0, y0), (x1, y0), EXT, 'int_cinza', [janela(1.4, 1.4, 2)])
    parede(g, (x1, y0), (x1, y1), EXT, 'int_cinza', [veneziana(0.6), janela(3.8, 1.5, 2)])
    parede(g, (x0, y1 - 3.2), (x0, y0), EXT, 'int_areia', [janela(0.8, 1.4, 2)])
    for px, py in ((x0, y1), (x1, y1), (x0, y1 - 3.2)):
        g.caixa(px - 0.15, px + 0.15, py - 0.15, py + 0.15, Z_PISO, Z_PISO + H_PAREDE, 'caixilho_ext', topo='parede_corte')
    # WC (canto sudeste) e cozinha
    wx0, wx1, wy0, wy1 = RM((1897, 1070, 1915, 1104))
    parede(g, (wx0, wy1), (wx0, wy0), 'int_cinza', 'int_branco', [veneziana(0.4)], e=0.1)
    parede(g, (wx1, wy1), (wx0, wy1), 'int_cinza', 'int_branco', [], e=0.1)
    ym = (wy0 + wy1) / 2
    parede(g, (wx1, ym), (wx0, ym), 'int_branco', 'int_branco', [], e=0.08)
    # parede de fundo grafite-azul da cozinha
    parede(g, (x0 + 0.14, wy1), (wx0, wy1), 'int_cinza', 'int_cinza', [], e=0.1)


def vestiarios(g):
    x0, x1, y0, y1 = RM(PL.VESTIARIOS)
    z = Z_PISO
    g.caixa(x0, x1, y0, y1, z, z + 2.9, EXT, topo='telha')
    g.caixa(x0 - 0.12, x1 + 0.12, y0 - 0.12, y1 + 0.12, z + 2.9, z + 3.05, 'pingadeira', topo='telha')
    for u in (0.9, 2.4):
        g.caixa(x0 + u, x0 + u + 0.9, y1, y1 + 0.03, z, z + 2.15, 'porta_veneziana')
    for u in (4.2, 5.2):
        g.caixa(x0 + u, x0 + u + 0.5, y1, y1 + 0.03, z + 1.7, z + 2.4, 'caixilho_ext')


def edificio_fechado(g, r, topo='telha', portas=()):
    x0, x1, y0, y1 = RM(r)
    z = 0.0
    g.caixa(x0, x1, y0, y1, z, z + 3.2, EXT, topo=topo)
    g.caixa(x0 - 0.15, x1 + 0.15, y0 - 0.15, y1 + 0.15, z + 3.2, z + 3.42, 'pingadeira', topo=topo)
    for lado, u, l, zb, zt, mt in portas:
        if lado == 'o':
            g.caixa(x0 - 0.03, x0, y0 + u, y0 + u + l, zb, zt, mt)
        elif lado == 's':
            g.caixa(x0 + u, x0 + u + l, y0 - 0.03, y0, zb, zt, mt)
        elif lado == 'n':
            g.caixa(x0 + u, x0 + u + l, y1, y1 + 0.03, zb, zt, mt)
        elif lado == 'l':
            g.caixa(x1, x1 + 0.03, y0 + u, y0 + u + l, zb, zt, mt)


def portaria(g):
    """Guarita e delivery (01, 02), portico de veiculos, gradil e portoes, como em 01-fachada.jpg."""
    x0, x1, y0, y1 = RM(PL.GUARITA)
    Mt = 'reboco_marrom'
    g.caixa(x0, x1, y0, y1, 0, Z_PISO, 'paver', lados='meio_fio')
    # delivery sem teto (para ver as prateleiras) e guarita com teto
    dx0, dx1, dy0, dy1 = RM(PL.DELIVERY)
    parede(g, (dx0, dy1), (dx0, dy0), Mt, 'int_escuro', [])
    parede(g, (dx1, dy1), (dx0, dy1), Mt, 'int_escuro', [janela(0.4, 1.3, 2)])
    parede(g, (dx0, dy0), (dx1, dy0), 'int_escuro', 'int_escuro', [])
    parede(g, (dx1, dy0), (dx1, dy1), 'int_escuro', 'int_escuro', [veneziana(0.6)])
    g.piso(dx0, dx1, dy0, dy1, Z_PISO + 0.004, 'piso_cinza')
    gx0 = dx1
    g.caixa(gx0, x1, y0, y1, Z_PISO, Z_PISO + 3.0, Mt, topo='telha')
    g.caixa(gx0 - 0.1, x1 + 0.25, y0 - 0.25, y1 + 0.1, Z_PISO + 3.0, Z_PISO + 3.2, 'pingadeira', topo='telha')
    # visor da guarita
    g.caixa(x1, x1 + 0.03, y0 + 0.8, y0 + 2.8, Z_PISO + 1.0, Z_PISO + 2.2, 'vidro_porta')
    for k in range(3):
        g.caixa(x1, x1 + 0.05, y0 + 0.8 + k, y0 + 0.86 + k, Z_PISO + 1.0, Z_PISO + 2.2, 'ferragem')
    # pergolas de pedestre
    for r in (PL.PERGOLA_GUARITA_N, PL.PERGOLA_GUARITA_S):
        a, b, c, d = RM(r)
        pergola(g, (a, b, c, d), 2.75, 0.42, 'y', mt='ferro_escuro')
    # portico de veiculos: dois pilares largos e laje com ripado por baixo
    a, b, c, d = RM(PL.PORTICO)
    pz = 5.2
    for yp in (c, d):
        for xp in (a, b):
            g.caixa(xp - 0.28, xp + 0.28, yp - 0.28, yp + 0.28, 0, pz, Mt, topo='parede_corte')
    g.caixa(a - 0.3, b + 0.3, c - 0.3, d + 0.3, pz, pz + 0.42, Mt, topo='telha')
    p = c
    while p <= d:
        g.caixa(a, b, p - 0.05, p + 0.05, pz - 0.3, pz, 'ferro_escuro')
        p += 0.65
    # fita de LED no ripado do portico e arandelas da guarita (acesas a noite)
    g.caixa(a, b, (c + d) / 2 - 0.03, (c + d) / 2 + 0.03, pz - 0.34, pz - 0.3, 'luz_poste', fundo='luz_poste', sem_fundo=False)
    for yy in (y0 + 0.5, y1 - 0.5):
        g.caixa(x1 + 0.01, x1 + 0.06, yy - 0.07, yy + 0.07, Z_PISO + 2.1, Z_PISO + 2.4, 'luz_poste')
    # portoes: dois vaos, gradil escuro deslizante
    ya_ = Y(1186)
    gradil(g, (a, ya_), (b, ya_), 2.4, 'gradil_preto', 'ferro_escuro', 0.02, passo=1.6)
    ym = Y(1272)
    gradil(g, (a, ym), (b, ym), 2.4, 'gradil_preto', 'ferro_escuro', 0.02, passo=1.6)
    # gradil de frente e fundo do lazer
    gx = X(PL.GRADIL_X)
    gradil(g, (gx, Y(642)), (gx, Y(1120)), 1.9, 'gradil_preto', 'ferro_escuro', 0.0, passo=2.4, mureta=0.25)
    gradil(g, (gx, Y(1120)), (X(2228), Y(1120)), 1.9, 'gradil_preto', 'ferro_escuro', 0.0, passo=2.4, mureta=0.25)
    # pedestres: portao entre guarita e rua
    gradil(g, (X(2228), Y(1138)), (X(2272), Y(1138)), 2.0, 'gradil_preto', 'ferro_escuro', 0.0, passo=2.0)
    # totem do empreendimento
    tx_, ty_ = X(2298), Y(1140)
    g.caixa(tx_ - 0.12, tx_ + 0.12, ty_ - 0.65, ty_ + 0.65, 0.14, 2.3, 'parede_externa', topo='parede_corte')
    g.painel(tx_ + 0.122, ty_ - 0.55, tx_ + 0.122, ty_ + 0.55, 0.4, 2.2, 'placa_gaia', (0, 0, 1, 1))


def piso_playground(g):
    z = Z_PISO
    x0, x1, y0, y1 = RM(PL.PLAYGROUND)
    g.caixa(x0, x1, y0, y1, 0, z - 0.01, 'ep_azul', lados='meio_fio')
    blocos = [
        (1958, 906, 2008, 966, 'ep_amarelo'), (2008, 906, 2038, 966, 'ep_azul'), (2038, 906, 2056, 966, 'ep_amarelo'),
        (1958, 966, 2056, 1012, 'ep_azul'), (1958, 1012, 1996, 1048, 'ep_amarelo'), (1996, 1012, 2026, 1048, 'ep_azul'),
        (2026, 1012, 2056, 1048, 'ep_amarelo'), (1958, 1048, 2000, 1078, 'ep_amarelo'), (2000, 1048, 2056, 1078, 'ep_azul_escuro'),
    ]
    for a, b, c, d, mt in blocos:
        g.piso(X(a), X(c), Y(d), Y(b), z + 0.002, mt)


def pet_place(g):
    x0, x1, y0, y1 = RM(PL.PET)
    gradil(g, (x0, y0), (x1, y0), 1.3, 'alambrado', 'ferro_verde', 0.0, passo=2.0)
    gradil(g, (x1, y0), (x1, y1), 1.3, 'alambrado', 'ferro_verde', 0.0, passo=2.0)
    gradil(g, (x1, y1), (x0, y1), 1.3, 'alambrado', 'ferro_verde', 0.0, passo=2.0)
    gradil(g, (x0, y1), (x0, y0), 1.3, 'alambrado', 'ferro_verde', 0.0, passo=2.0)


def lazer(g):
    # chao sob o lazer: laje por bloco
    pisos_lazer(g)
    piscinas(g)
    quadra(g)
    piso_playground(g)
    bloco_principal(g)
    churrasqueira(g)
    gourmet(g)
    vestiarios(g)
    edificio_fechado(g, PL.APOIO, portas=(('o', 1.5, 0.95, 0.0, 2.2, 'porta_veneziana'), ('s', 1.6, 1.8, 0.95, 2.3, 'vidro_porta'), ('s', 4.2, 1.8, 0.95, 2.3, 'vidro_porta')))
    portaria(g)
    pet_place(g)
    # pergolas soltas
    x0, x1, y0, y1 = RM(PL.PERGOLA_CROSSFIT)
    grelha(g, (x0, x1, y0, y1), 3.0, 0.7)
    x0, x1, y0, y1 = RM(PL.PERGOLA_SALAO)
    grelha(g, (x0, x1, y0, y1), 2.75, 0.7)
    # postes do patio e balizadores do lazer (acesos a noite)
    postes_e_balizadores(g)


def _poste(g, x, y, z0=0.14, h=4.6):
    g.cil(x, y, 0.05, z0, z0 + h, 'ferro_escuro', seg=8, tampa=False)
    g.caixa(x - 0.2, x + 0.2, y - 0.07, y + 0.07, z0 + h, z0 + h + 0.09, 'ferro_escuro', fundo='luz_poste')


def _balizador(g, x, y, z0=Z_PISO, h=0.7):
    g.cil(x, y, 0.045, z0, z0 + h, 'ferro_escuro', seg=8)
    g.cil(x, y, 0.05, z0 + h - 0.1, z0 + h - 0.02, 'luz_poste', seg=8, tampa=False)


POSTES_PATIO = [(455, 500), (455, 800), (455, 1090), (630, 560), (630, 850), (630, 1130), (1055, 560), (1055, 830), (1055, 1100),
                (1231, 560), (1231, 850), (1231, 1130), (1642, 520), (1642, 830), (1642, 1100), (1820, 560), (1820, 830), (1820, 1100),
                (220, 560), (220, 800), (305, 955), (810, 1050), (1425, 1000), (640, 1345), (1000, 1345), (1400, 1345), (1800, 1345), (60, 700), (60, 950),
                (2322, 720), (2334, 840), (2346, 960), (2362, 1090), (2402, 1320)]
BALIZADORES = [(1850, 700), (1850, 780), (1850, 860), (2048, 700), (2048, 770), (2048, 840), (2062, 800), (2062, 860), (2062, 930), (2062, 1000), (2062, 1070),
               (2165, 800), (2165, 880), (2165, 950), (2165, 1020), (1950, 890), (1950, 960), (1950, 1030), (1950, 1100), (1858, 1010), (1920, 1010), (1860, 1110),
               (1990, 1120), (2040, 1120), (2120, 1120), (2190, 1120), (2230, 1000), (2180, 1045), (2240, 1120), (2290, 1125),
               (2232, 1150), (2262, 1158), (2292, 1166), (2322, 1152), (2110, 1196), (2150, 1196), (2200, 1192), (2245, 1192)]


def postes_e_balizadores(g):
    def poca(x, y, r, z):
        g.face([(x - r, y - r, z), (x + r, y - r, z), (x + r, y + r, z), (x - r, y + r, z)], 'luz_chao', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], cor=1.0)
    for px, py in POSTES_PATIO:
        _poste(g, X(px), Y(py))
        poca(X(px), Y(py), 6.5, 0.18)
    for px, py in BALIZADORES:
        _balizador(g, X(px), Y(py))
        poca(X(px), Y(py), 1.9, Z_PISO + 0.02)

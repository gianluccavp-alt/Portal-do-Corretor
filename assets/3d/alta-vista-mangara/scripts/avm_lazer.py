# avm_lazer.py -- lazer e apoio do Alta Vista Mangara. Etapa 2: ambientes SEM TETO (paredes cortadas a 3 m, como
# no Gaia e no Village Park) para ver os moveis de cima; piso do lazer desenhado a mao a partir da vista de cima
# do book (perspectiva VOO); piscina em L com deck molhado; portaria com marquise (perspectiva GUA), pet place,
# bike sharing, abrigo de lixo, casa de bombas e os 5 reservatorios.
# Medidas: avm_planta.py (px). Mobiliario: avm_moveis.py (pecas) e avm_ambientes.py (posicoes).
# Executado por avm_modelo.py dentro do Blender.

Z_QUADRA = 0.20        # piso da quadra de areia e do playground
Z_DECK = 0.30          # deck da piscina acima do passeio (0,14)
Z_PISO = 0.16          # piso acabado dos ambientes (moveis apoiam aqui)
Z_MADEIRA = 0.22       # decks de madeira
H_PAREDE = 3.0         # corte das paredes dos ambientes sem teto
E_PAREDE = 0.14
EXT = 'parede_externa'


def RM(r):
    """retangulo em px -> (x0, x1, y0, y1) em metros, com y0 < y1"""
    return X(r[0]), X(r[2]), Y(r[3]), Y(r[1])


def materiais_lazer():
    P_ = 'porcelanato.jpg'
    mat('deck', '#ddd6c8', 0.55, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('piso_int', '#e3ddd1', 0.35, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('piso_cinza', '#b9b6af', 0.4, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('piso_madeira', '#ffffff', 0.45, img='madeira_piso.jpg', uv=3.0)
    mat('deck_madeira', '#a8794f', 0.75, img='ripado.jpg', tint=True, img_mean=0.82, uv=(1.2, 1.2))
    mat('pastilha', '#ffffff', 0.25, img='pastilha.jpg', uv=1.6)
    mat('agua', '#3fb4b0', 0.04, blend=0.42, nrm='agua_normal.jpg', nrm_str=0.5, metal=0.0, uv=4.0)
    mat('borda_piscina', '#d8d2c4', 0.6)
    mat('paver_bege', '#b6aca0', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    E_ = dict(img='emborrachado.jpg', tint=True, uv=1.5)
    mat('ep_vermelho', '#c2463a', 0.85, **E_)
    mat('ep_azul', '#2f86c8', 0.85, **E_)
    mat('ep_azul_claro', '#62a9d8', 0.85, **E_)
    mat('ep_verde', '#4f9a52', 0.85, **E_)
    mat('ep_laranja', '#d9783a', 0.85, **E_)
    mat('areia', '#dcc7a0', 0.97, img='concreto.jpg', tint=True, uv=2.0)
    mat('alambrado', '#2f4a3b', 0.6, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.5, 0.5))
    mat('gradil_claro', '#e4e3df', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('gradil_preto', '#26282b', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('ferro_escuro', '#2a2d30', 0.55, metal=0.35)
    # paredes internas (prefixo int_: a pagina acende a noite)
    for nome, cor in (('branco', '#ece7dd'), ('bege', '#d9cbb4'), ('terracota', '#b4503a'), ('grafite', '#4a4d52'),
                      ('cinza', '#a9aaab'), ('creme', '#efe6d3'), ('laranja', '#c8642f')):
        mat('int_' + nome, cor, 0.85)
    mat('parede_corte', '#d9d6cf', 0.9)
    mat('rodape', '#b5b1a8', 0.7)
    mat('vidro_lazer', '#c6d8e0', 0.05, blend=0.12, metal=0.1)
    mat('caixilho_ext', '#2e3033', 0.45)
    mat('porta_veneziana', '#e7e6e1', 0.6, img='ripado.jpg', tint=True, img_mean=0.82, uv=(0.5, 3.0))
    mat('reboco_grafite', '#4f5156', 0.92, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('reboco_azul', '#2c3e66', 0.92, img='reboco_fino.jpg', tint=True, img_mean=0.88, uv=TILE)
    mat('reboco_laranja', '#c9793c', 0.92, img='reboco_fino.jpg', tint=True, img_mean=0.88, uv=TILE)
    mat('portico_madeira', '#8a5c3a', 0.7, img='ripado.jpg', tint=True, img_mean=0.82, uv=(0.6, 0.6))
    mat('rede', '#f2f2ee', 0.7, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.25, 0.25))
    mat('grama_pet', '#5f8a3e', 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=3.0)
    mat('atlas', '#ffffff', 0.5, img='atlas_lazer.jpg')
    mat('tela', '#ffffff', 0.25, img='atlas_lazer.jpg')
    mat('luz_poste', '#fff1cc', 0.4)
    mat('luz_chao', '#ffffff', 1.0, img='luz_radial.jpg')


# ------------------------------------------------------------------ utilitarios
def _mascara(rects, ref):
    x0, y0, x1, y1 = ref
    m = np.zeros((y1 - y0, x1 - x0), bool)
    for r in rects:
        m[max(0, int(r[1]) - y0):max(0, int(r[3]) - y0), max(0, int(r[0]) - x0):max(0, int(r[2]) - x0)] = True
    return m


def _decompor(m, ref):
    x0, y0 = ref[0], ref[1]
    out, abertos = [], {}
    for y in range(m.shape[0] + 1):
        corr = set()
        if y < m.shape[0] and m[y].any():
            d = np.diff(np.concatenate([[0], m[y].astype(np.int8), [0]]))
            corr = set(zip(np.nonzero(d == 1)[0].tolist(), np.nonzero(d == -1)[0].tolist()))
        for c in list(abertos):
            if c not in corr:
                out.append((x0 + c[0], y0 + abertos.pop(c), x0 + c[1], y0 + y))
        for c in corr:
            abertos.setdefault(c, y)
    return out


def _caixa_ref(rects):
    return (min(int(r[0]) for r in rects), min(int(r[1]) for r in rects),
            max(int(r[2]) for r in rects) + 1, max(int(r[3]) for r in rects) + 1)


def _uniao(rects, menos=()):
    ref = _caixa_ref(list(rects) + list(menos))
    m = _mascara(rects, ref)
    if menos:
        m &= ~_mascara(menos, ref)
    return _decompor(m, ref)


def _menos(r, buracos):
    return _uniao([r], buracos)


def _laje(g, rects_px, z, mt, menos=()):
    """Laje levantada (uniao de retangulos, sem faces coplanares sobrepostas) com lateral de meio-fio."""
    for r in _uniao(rects_px, menos):
        x0, x1, y0, y1 = RM(r)
        g.caixa(x0, x1, y0, y1, 0, z, mt, lados='meio_fio')


def _cerca(g, x0, x1, y0, y1, h, mat='alambrado', passo=2.5, z=Z_QUADRA, lados='slno'):
    """Cerca em volta de um retangulo (m): tela com recorte e postes."""
    segs = {'s': ((x0, y0), (x1, y0)), 'l': ((x1, y0), (x1, y1)), 'n': ((x1, y1), (x0, y1)), 'o': ((x0, y1), (x0, y0))}
    for k in lados:
        a, b = segs[k]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        g.painel(a[0], a[1], b[0], b[1], z, z + h, mat, (0, 0, L / 0.5 / 4, h / 0.5 / 4))
        g.painel(b[0], b[1], a[0], a[1], z, z + h, mat, (0, 0, L / 0.5 / 4, h / 0.5 / 4))
        n = max(1, round(L / passo))
        for i in range(n + 1):
            t = i / n
            g.cil(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 0.035, z, z + h + 0.05, 'ferro_escuro', seg=6)


# ------------------------------------------------------------------ paredes sem teto (mesmo desenho do Gaia)
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
        g.caixa(-ini_ext + e, L_ + fim_ext - e, e, e + 0.012, z0, z0 + 0.08, 'rodape', sem='s')


def sala(g, r, piso, paredes, z=Z_PISO):
    """Sala retangular (metros x0,x1,y0,y1). paredes = dict lado -> (ext, int, aberturas). Lados: s l n o (anti-horario).
    Aqui 'n' e o lado de cima da implantacao (y maior)."""
    x0, x1, y0, y1 = r
    g.piso(x0, x1, y0, y1, z + 0.003, piso)
    seq = {'s': ((x0, y0), (x1, y0)), 'l': ((x1, y0), (x1, y1)), 'n': ((x1, y1), (x0, y1)), 'o': ((x0, y1), (x0, y0))}
    for lado, cfg in paredes.items():
        a, b = seq[lado]
        ext, inte, ab = cfg
        parede(g, a, b, ext, inte, ab)


def janela(s, l=1.5, n=2):
    return (s, s + l, Z_PISO + 0.9, Z_PISO + 2.2, 'janela', n)


def janelao(s, l=2.0, n=2):
    return (s, s + l, Z_PISO + 0.12, Z_PISO + 2.45, 'janela', n)


def porta_vidro(s, l=2.0, n=2):
    return (s, s + l, Z_PISO, Z_PISO + 2.35, 'porta_vidro', n)


def veneziana(s, l=0.9):
    return (s, s + l, Z_PISO, Z_PISO + 2.15, 'veneziana', 1)


def vao(s, l=1.0):
    return (s, s + l, Z_PISO, Z_PISO + 2.3, 'vao', 1)


def pergola(g, r, h=2.75, passo=0.5, sentido='x', mt='ferro_escuro', z=Z_PISO, ripa='ferro_escuro'):
    """Pergola: pilares nos cantos, 2 vigas, ripas transversais."""
    x0, x1, y0, y1 = r
    zt = z + h
    for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        g.caixa(px - 0.06, px + 0.06, py - 0.06, py + 0.06, z, zt, mt)
    if sentido == 'x':
        for yy in (y0, y1):
            g.caixa(x0 - 0.08, x1 + 0.08, yy - 0.05, yy + 0.05, zt - 0.15, zt, mt)
        p = x0
        while p <= x1 + 1e-3:
            g.caixa(p - 0.03, p + 0.03, y0 - 0.12, y1 + 0.12, zt, zt + 0.12, ripa)
            p += passo
    else:
        for xx in (x0, x1):
            g.caixa(xx - 0.05, xx + 0.05, y0 - 0.08, y1 + 0.08, zt - 0.15, zt, mt)
        p = y0
        while p <= y1 + 1e-3:
            g.caixa(x0 - 0.12, x1 + 0.12, p - 0.03, p + 0.03, zt, zt + 0.12, ripa)
            p += passo


def poste(g, x, y, h=3.2, z=0.0, poca=3.2):
    """Poste baixo do jardim com globo aceso a noite e a poca de luz no chao (luz_chao, invisivel de dia)."""
    g.cil(x, y, 0.05, z, z + h, 'ferro_escuro', seg=8)
    g.elipsoide(x, y, z + h + 0.15, 0.17, 0.17, 0.17, 'luz_poste', seg=10, aneis=6)
    if poca:
        g.tapete(x - poca, x + poca, y - poca, y + poca, z + 0.17, 'luz_chao', (0, 0, 1, 1))


# ------------------------------------------------------------------ chao do lazer
def chao_lazer(g):
    """Grama ja vem do lote; aqui entram o paver da praca e da entrada do bloco, os decks e as cercas vivas."""
    _laje(g, [PL.PRACA, PL.PASSEIO_LAZER], Z_PASSEIO, 'paver_bege')
    _laje(g, [PL.LOUNGE_ACADEMIA], Z_PASSEIO, 'concreto')
    x0, x1, y0, y1 = RM(PL.DECK_GOURMET)
    g.caixa(x0, x1, y0, y1, 0, Z_MADEIRA, 'deck_madeira', lados='meio_fio')
    # pisantes do wine lounge (placas de concreto na grama)
    wx0, wx1, wy0, wy1 = RM(PL.WINE_LOUNGE)
    for i in range(4):
        for j in range(2):
            px, py = wx0 + 0.6 + i * 0.9, wy1 - 2.3 - j * 0.9
            g.caixa(px, px + 0.7, py, py + 0.7, 0, 0.05, 'concreto')


# ------------------------------------------------------------------ piscina em L
def _paredes_tanque(g, rects_px, z_fundo, z_top):
    """Paredes internas do tanque so onde a borda encosta no deck (pedacos cobertos por outro tanque ficam de fora)."""
    ref = _caixa_ref(rects_px)
    ref = (ref[0] - 2, ref[1] - 2, ref[2] + 2, ref[3] + 2)
    m = _mascara(rects_px, ref)
    ox, oy = ref[0], ref[1]
    H, W = m.shape
    # bordas horizontais (topo e base de cada linha de pixels) e verticais, juntadas em corridas
    for y in range(H + 1):
        acima = m[y - 1] if y > 0 else np.zeros(W, bool)
        abaixo = m[y] if y < H else np.zeros(W, bool)
        for borda, sinal in ((acima & ~abaixo, -1), (abaixo & ~acima, 1)):
            d = np.diff(np.concatenate([[0], borda.astype(np.int8), [0]]))
            for s0, s1 in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
                yy = Y(oy + y)
                xa, xb = X(ox + s0), X(ox + s1)
                q = [(xa, yy, z_fundo), (xb, yy, z_fundo), (xb, yy, z_top), (xa, yy, z_top)]
                g.face(q if sinal > 0 else q[::-1], 'pastilha')
    for x in range(W + 1):
        esq = m[:, x - 1] if x > 0 else np.zeros(H, bool)
        dir_ = m[:, x] if x < W else np.zeros(H, bool)
        for borda, sinal in ((esq & ~dir_, -1), (dir_ & ~esq, 1)):
            d = np.diff(np.concatenate([[0], borda.astype(np.int8), [0]]))
            for s0, s1 in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
                xx = X(ox + x)
                ya, yb = Y(oy + s0), Y(oy + s1)
                q = [(xx, ya, z_fundo), (xx, yb, z_fundo), (xx, yb, z_top), (xx, ya, z_top)]
                g.face(q if sinal > 0 else q[::-1], 'pastilha')


def piscinas(g):
    z = Z_DECK
    tanques = PL.PISCINA + [PL.PISCINA_INFANTIL]
    for r in _menos(PL.PISCINA_DECK, tanques):
        x0, x1, y0, y1 = RM(r)
        g.caixa(x0, x1, y0, y1, 0, z, 'deck', lados='meio_fio')
    for r in PL.PISCINA:
        x0, x1, y0, y1 = RM(r)
        raso = (r == PL.DECK_MOLHADO)
        g.piso(x0, x1, y0, y1, (z - 0.10) if raso else 0.16, 'pastilha')
        g.piso(x0, x1, y0, y1, z - 0.06, 'agua')
    x0, x1, y0, y1 = RM(PL.PISCINA_INFANTIL)
    g.piso(x0, x1, y0, y1, 0.18, 'pastilha')
    g.piso(x0, x1, y0, y1, z - 0.06, 'agua')
    _paredes_tanque(g, PL.PISCINA, 0.16, z)
    _paredes_tanque(g, [PL.PISCINA_INFANTIL], 0.18, z)
    # degrau entre o deck molhado e a raia funda
    dx0, dx1, dy0, dy1 = RM(PL.DECK_MOLHADO)
    g.face([(dx1, dy1, 0.16), (dx1, dy0, 0.16), (dx1, dy0, z - 0.10), (dx1, dy1, z - 0.10)], 'pastilha')
    # borda de pedra em volta dos tanques
    for r in tanques:
        a0, a1, b0, b1 = RM(r)
        e = 0.22
        for (u0, u1, v0, v1) in ((a0 - e, a1 + e, b1, b1 + e), (a0 - e, a1 + e, b0 - e, b0), (a0 - e, a0, b0, b1), (a1, a1 + e, b0, b1)):
            for rr in _uniao([(int(round(PL.ORIGEM_PX[0] + u0 / S_PX)), int(round(PL.ORIGEM_PX[1] - v1 / S_PX)),
                               int(round(PL.ORIGEM_PX[0] + u1 / S_PX)), int(round(PL.ORIGEM_PX[1] - v0 / S_PX)))], tanques):
                c0, c1, d0, d1 = RM(rr)
                g.caixa(c0, c1, d0, d1, z, z + 0.03, 'borda_piscina')
    # escada inox na raia funda e gradil em volta do deck (aberto na entrada, a oeste)
    ex, ey = X(PL.PISCINA[0][0]) + 0.35, Y(1720)
    for dy in (-0.3, 0.3):
        g.tubo([(ex - 0.1, ey + dy, z - 0.9), (ex, ey + dy, z + 0.6), (ex - 0.45, ey + dy, z + 0.75), (ex - 0.55, ey + dy, z)],
               0.022, 'inox', seg=6)
    x0, x1, y0, y1 = RM(PL.PISCINA_DECK)
    _cerca(g, x0, x1, y0, y1, 1.2, mat='gradil_claro', passo=2.4, z=Z_DECK, lados='sln')
    _cerca(g, x0, x0, Y(1620), y1, 1.2, mat='gradil_claro', passo=2.4, z=Z_DECK, lados='o')
    _cerca(g, x0, x0, y0, Y(1660), 1.2, mat='gradil_claro', passo=2.4, z=Z_DECK, lados='o')


# ------------------------------------------------------------------ bloco do salao, academia e WCs (sem teto)
def bloco_salao(g):
    bx0, bx1, by0, by1 = RM(PL.EDIF_SALAO)
    g.caixa(bx0 - 0.3, bx1 + 0.3, by0 - 0.3, by1 + 0.3, 0, Z_PISO, 'piso_cinza', lados='meio_fio')
    ax0, ax1 = X(PL.ACADEMIA_X[0]), X(PL.ACADEMIA_X[1])
    sx0, sx1 = X(PL.SALAO_X[0]), X(PL.SALAO_X[1])
    wx0, wx1 = X(PL.WC_X[0]), X(PL.WC_X[1])
    # academia (ACA): grafite, piso de madeira com pista laranja, vidro para o passeio e porta para o lounge
    sala(g, (ax0, ax1, by0, by1), 'piso_madeira', {
        'n': (EXT, 'int_grafite', [janelao(0.6, 3.0, 3)]),
        'o': (EXT, 'int_grafite', [janela(2.2, 2.6, 2)]),
        's': (EXT, 'int_grafite', [porta_vidro(1.0, 2.0, 2)]),
    })
    # salao de festas (SFE): bege, janeloes do piso ao teto nos dois lados
    sala(g, (sx0, sx1, by0, by1), 'piso_int', {
        'n': (EXT, 'int_bege', [janelao(0.6, 2.4, 2), porta_vidro(3.6, 2.2, 2)]),
        's': (EXT, 'int_bege', [janelao(0.5, 2.6, 2), porta_vidro(3.6, 2.4, 2)]),
        'o': (EXT, 'int_bege', []),
    })
    # copa (norte, aberta para o salao) e dois WCs (sul)
    yc = Y(1562)
    xm = X(2269)
    sala(g, (wx0, wx1, by0, by1), 'piso_int', {
        'n': (EXT, 'int_branco', [janela(1.2, 1.2, 1)]),
        'l': (EXT, 'int_branco', [janela(0.8, 0.8, 1), janela(4.6, 0.8, 1)]),
        's': (EXT, 'int_branco', [veneziana(0.5, 0.8), veneziana(2.2, 0.8)]),
    })
    parede(g, (wx0, by0), (wx0, yc), 'int_bege', 'int_branco', [], e=0.1)
    parede(g, (wx1, yc), (wx0, yc), 'int_branco', 'int_branco', [veneziana(0.4, 0.8), veneziana(2.2, 0.8)], e=0.1)
    parede(g, (xm, by0), (xm, yc), 'int_branco', 'int_branco', [], e=0.08)


# ------------------------------------------------------------------ churrasqueira (sem teto) e lounge com pergola
def churrasqueira(g):
    cx0, cx1, cy0, cy1 = RM(PL.CHURRASQUEIRA)
    g.caixa(cx0 - 0.25, cx1 + 0.25, cy0 - 0.25, cy1 + 0.25, 0, Z_PISO, 'piso_cinza', lados='meio_fio')
    xw = X(1722)
    ym = (cy0 + cy1) / 2
    sala(g, (cx0, cx1, cy0, cy1), 'piso_int', {
        'n': (EXT, 'int_cinza', [janela(1.0, 1.4, 2)]),
        'l': (EXT, 'int_branco', [veneziana(0.6, 0.8), veneziana(2.8, 0.8)]),
        's': (EXT, 'int_cinza', [janela(0.8, 1.6, 2)]),
        'o': (EXT, 'int_terracota', [vao(0.9, 2.6)]),
    })
    parede(g, (xw, cy0), (xw, cy1), 'int_cinza', 'int_branco', [veneziana(0.5, 0.8), veneziana(2.9, 0.8)], e=0.1)
    parede(g, (cx1, ym), (xw, ym), 'int_branco', 'int_branco', [], e=0.08)
    # lounge: deck de madeira sob pergolado de madeira com trepadeira
    lx0, lx1, ly0, ly1 = RM(PL.LOUNGE_CHURRASQUEIRA)
    g.caixa(lx0, lx1, ly0, ly1, 0, Z_MADEIRA, 'deck_madeira', lados='meio_fio')
    pergola(g, (lx0 + 0.15, lx1 - 0.05, ly0 + 0.15, ly1 - 0.15), h=2.7, passo=0.35, sentido='x', mt='ferro_escuro',
            z=Z_MADEIRA, ripa='portico_madeira')


# ------------------------------------------------------------------ quadra de areia e playground
def quadra_areia(g):
    x0, x1, y0, y1 = RM(PL.QUADRA_AREIA)
    g.caixa(x0, x1, y0, y1, 0, Z_QUADRA, 'areia', lados='meio_fio')
    zl = Z_QUADRA + 0.005
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = 3.6, 1.8
    w = 0.05
    for xa, xb, ya, yb in ((cx - hx, cx + hx, cy - hy, cy - hy + w), (cx - hx, cx + hx, cy + hy - w, cy + hy),
                           (cx - hx, cx - hx + w, cy - hy, cy + hy), (cx + hx - w, cx + hx, cy - hy, cy + hy)):
        g.piso(xa, xb, ya, yb, zl, 'ep_azul')
    for yy in (cy - hy - 0.4, cy + hy + 0.4):
        g.cil(cx, yy, 0.05, zl, zl + 2.45, 'ferro_escuro', seg=6)
    g.painel(cx, cy - hy - 0.4, cx, cy + hy + 0.4, zl + 1.55, zl + 2.4, 'rede', (0, 0, 5, 1))
    g.painel(cx, cy + hy + 0.4, cx, cy - hy - 0.4, zl + 1.55, zl + 2.4, 'rede', (0, 0, 5, 1))
    _cerca(g, x0 + 0.1, x1 - 0.1, y0 + 0.1, y1 - 0.1, 3.5)


def playground(g):
    x0, x1, y0, y1 = RM(PL.PLAYGROUND)
    g.caixa(x0, x1, y0, y1, 0, Z_QUADRA - 0.04, 'ep_vermelho', lados='meio_fio')
    # desenho de piso como na vista de cima: miolo azul com ilhas vermelha e azul-clara
    g.caixa_red(x0 + 0.5, x1 - 0.5, y0 + 0.5, y1 - 0.5, Z_QUADRA - 0.04, Z_QUADRA - 0.034, 1.2, 'ep_azul')
    g.caixa_red(x0 + 1.6, x1 - 1.0, y0 + 2.2, y1 - 1.2, Z_QUADRA - 0.034, Z_QUADRA - 0.03, 0.9, 'ep_azul_claro')
    g.caixa_red(x0 + 2.6, x1 - 1.8, y1 - 3.6, y1 - 1.6, Z_QUADRA - 0.03, Z_QUADRA - 0.026, 0.6, 'ep_vermelho')


# ------------------------------------------------------------------ apoio: portaria, lixo, pet, bike, bombas
def portaria(g):
    """Guarita (GUA): volume grafite com revestimento de madeira ripada na frente da Rua 2, vidro escuro para o
    portao de entrada e uma marquise plana longa que cobre a guarita e o portao; totem com o nome."""
    x0, x1, y0, y1 = RM(PL.PORTARIA)
    g.caixa(x0, x1, y0, y1, 0, 3.0, 'reboco_grafite', topo='cobertura')
    g.caixa(x1 - 0.02, x1 + 0.06, y0 + 0.3, y1 - 0.3, 0.1, 2.9, 'portico_madeira')
    # vidro da guarita (face norte, para a pista de entrada, e um trecho da face leste)
    g.caixa(x0 + 0.3, x1 - 0.3, y1 - 0.02, y1 + 0.04, 0.95, 2.55, 'vidro_porta')
    g.caixa(x0 + 0.3, x1 - 0.3, y1 + 0.02, y1 + 0.08, 0.9, 0.97, 'ferro_escuro')
    g.caixa(x0 - 0.04, x0 + 0.02, y0 + 1.0, y0 + 2.2, 0.12, 2.2, 'porta_servico')
    # marquise: laje plana fina sobre pilares metalicos esbeltos
    mx0, mx1, my0, my1 = RM(PL.MARQUISE_PORTARIA)
    g.caixa(mx0, mx1, my0, my1, 3.55, 3.8, 'reboco_grafite', topo='cobertura', fundo='varanda_forro', sem_fundo=False)
    for px in (mx0 + 0.3, mx1 - 0.3):
        g.caixa(px - 0.08, px + 0.08, my1 - 0.3 - 0.08, my1 - 0.3 + 0.08, 0, 3.55, 'ferro_escuro')
    for xx in (mx0 + 1.2, (mx0 + mx1) / 2, mx1 - 1.2):
        g.cil(xx, (my0 + my1) / 2 + 1.0, 0.12, 3.53, 3.55, 'luz_poste', seg=10, tampa=False, base=True)
    # totem com o nome do empreendimento (placa generica, sem logo)
    tx_, ty_ = X(PL.TOTEM[0]), Y(PL.TOTEM[1])
    g.caixa(tx_ - 0.35, tx_ + 0.35, ty_ - 0.18, ty_ + 0.18, Z_PASSEIO, Z_PASSEIO + 2.4, 'reboco_grafite', topo='cobertura')
    g.caixa(tx_ + 0.35, tx_ + 0.37, ty_ - 0.12, ty_ + 0.12, Z_PASSEIO + 1.2, Z_PASSEIO + 2.2, 'metal_ouro')


def apoio(g):
    # abrigo de lixo: volume fechado com portas venezianas
    x0, x1, y0, y1 = RM(PL.LIXO)
    g.caixa(x0, x1, y0, y1, 0, 2.6, 'parede_externa', topo='cobertura')
    g.caixa(x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 0.3, 2.6, 2.75, 'laje_borda', topo='cobertura', fundo='varanda_forro', sem_fundo=False)
    for yy in (y0 + 0.8, y0 + 2.6):
        g.caixa(x0 - 0.03, x0 + 0.01, yy, yy + 1.4, 0.05, 2.2, 'porta_veneziana')
    # casa de bombas
    x0, x1, y0, y1 = RM(PL.CASA_BOMBAS)
    g.caixa(x0, x1, y0, y1, 0, 2.5, 'parede_externa', topo='cobertura')
    g.caixa(x0 + 1.0, x0 + 2.0, y1, y1 + 0.03, 0.05, 2.1, 'porta_veneziana')
    # reservatorios (5 caixas azuis com tampa e escada)
    for cx, cy in PL.RESERVATORIOS:
        rr = PL.RAIO_RESERVATORIO_PX * S_PX
        X_, Y_ = X(cx), Y(cy)
        g.caixa(X_ - rr - 0.2, X_ + rr + 0.2, Y_ - rr - 0.2, Y_ + rr + 0.2, 0, 0.2, 'concreto', lados='meio_fio')
        g.cil(X_, Y_, rr, 0.2, 2.6, 'cisterna', seg=28, topo='cisterna')
        g.cil(X_, Y_, rr * 0.35, 2.6, 2.75, 'cisterna', seg=14)
        for k in range(8):
            a = 2 * math.pi * k / 8
            g.caixa(X_ + math.cos(a) * rr - 0.03, X_ + math.cos(a) * rr + 0.03, Y_ + math.sin(a) * rr - 0.03,
                    Y_ + math.sin(a) * rr + 0.03, 0.25, 2.55, 'cisterna')
    # bike sharing (BIC): piso, parede azul com o desenho da bicicleta e o porta-bicicletas preto
    x0, x1, y0, y1 = RM(PL.BIKE)
    g.caixa(x0, x1, y0, y1, 0, 0.14, 'concreto', lados='meio_fio')
    g.caixa(x0, x0 + 0.2, y0, y1, 0.14, 2.8, 'reboco_azul', topo='cobertura')
    # pet place (PET): grama, gradil preto, muro com faixa laranja e ducha
    x0, x1, y0, y1 = RM(PL.PET)
    g.caixa(x0, x1, y0, y1, 0, 0.05, 'grama_pet')
    _cerca(g, x0, x1, y0, y1, 1.4, mat='gradil_preto', passo=2.4, z=0.05, lados='slo')
    g.caixa(x0, x1, y1 - 0.2, y1, 0.05, 2.2, 'reboco_grafite', topo='cobertura')
    g.caixa(x0 + 0.6, x0 + 2.8, y1 - 0.205, y1 - 0.2, 0.05, 1.6, 'reboco_laranja')
    g.caixa(x0 + 0.8, x0 + 1.8, y1 - 0.75, y1 - 0.2, 0.05, 0.75, 'concreto', topo='azulejo')


def lazer(g):
    chao_lazer(g)
    piscinas(g)
    bloco_salao(g)
    churrasqueira(g)
    quadra_areia(g)
    playground(g)
    portaria(g)
    apoio(g)
    # postes do jardim (a noite acendem; de dia o globo e a poca nao aparecem)
    for px, py in ((1540, 1425), (1720, 1530), (1880, 1495), (2010, 1505), (2120, 1720), (2240, 1730),
                   (2325, 1470), (2325, 1790), (1620, 1525)):
        poste(g, X(px), Y(py))

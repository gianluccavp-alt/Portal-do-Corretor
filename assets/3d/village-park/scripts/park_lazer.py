# park_lazer.py -- lazer e apoio do Village Park. Etapa 2: ambientes fechados SEM TETO (paredes cortadas a 3 m,
# como no Gaia), para ver os moveis de cima; piso do lazer desenhado a mao (caminhos, decks, cercas vivas), sem a
# segmentacao por cor, que deixava manchas. Piscinas, quadras e entrada como na etapa 1.
# Medidas: park_planta.py (px) e FAQ. Mobiliario: park_moveis.py (pecas) e park_ambientes.py (posicoes).
# Executado por park_modelo.py dentro do Blender.

Z_QUADRA = 0.20        # piso das quadras e do playground
Z_DECK = 0.30          # deck da piscina acima do passeio (0,14)
Z_PISO = 0.16          # piso acabado dos ambientes (moveis apoiam aqui)
Z_MADEIRA = 0.22       # decks de madeira
H_PAREDE = 3.0         # corte das paredes dos ambientes sem teto
E_PAREDE = 0.14
H_EDIF = 3.4
EXT = 'parede_externa'


def RM(r):
    """retangulo em px -> (x0, x1, y0, y1) em metros, com y0 < y1"""
    return X(r[0]), X(r[2]), Y(r[3]), Y(r[1])


def materiais_lazer():
    P_ = 'porcelanato.jpg'
    mat('deck', '#d6d0c5', 0.55, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('piso_int', '#d9d4ca', 0.35, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('piso_cinza', '#b9b6af', 0.4, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('piso_madeira', '#ffffff', 0.45, img='madeira_piso.jpg', uv=3.0)
    mat('deck_madeira', '#a8794f', 0.75, img='ripado.jpg', tint=True, img_mean=0.82, uv=(1.2, 1.2))
    mat('pastilha', '#ffffff', 0.25, img='pastilha.jpg', uv=1.6)
    mat('agua', '#3fb4b0', 0.04, blend=0.42, nrm='agua_normal.jpg', nrm_str=0.5, metal=0.0, uv=4.0)
    mat('borda_piscina', '#cfcabc', 0.6)
    mat('paver_bege', '#b6aca0', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    mat('sebe', '#3e6a2c', 0.95, img='grama2.jpg', tint=True, img_mean=0.45, uv=1.2)
    E_ = dict(img='emborrachado.jpg', tint=True, uv=1.5)
    mat('quadra_terra', '#b45a33', 0.75, **E_)
    mat('quadra_verde', '#3f8a4f', 0.75, **E_)
    mat('quadra_borda', '#47494d', 0.8, **E_)
    mat('ep_vermelho', '#b8443a', 0.85, **E_)
    mat('ep_azul', '#2f86c8', 0.85, **E_)
    mat('ep_verde', '#4f9a52', 0.85, **E_)
    mat('ep_amarelo', '#e4b42c', 0.85, **E_)
    mat('ep_terracota', '#b5603a', 0.85, **E_)
    mat('areia', '#d9c9a6', 0.97, img='concreto.jpg', tint=True, uv=2.0)
    mat('alambrado', '#2f4a3b', 0.6, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.5, 0.5))
    mat('gradil_preto', '#26282b', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('ferro_escuro', '#2a2d30', 0.55, metal=0.35)
    # paredes internas (prefixo int_: a pagina acende a noite)
    for nome, cor in (('branco', '#e8e3d9'), ('areia', '#cfba9c'), ('terracota', '#b4503a'), ('grafite', '#39454c'),
                      ('verde', '#3f5f50'), ('tijolo', '#a5603f'), ('creme', '#efe6d3'), ('cinza', '#a3a5a6'),
                      ('menta', '#a9c4b4'), ('escuro', '#3a3b3e')):
        mat('int_' + nome, cor, 0.85)
    mat('parede_corte', '#d9d6cf', 0.9)
    mat('rodape', '#b5b1a8', 0.7)
    mat('vidro_lazer', '#c6d8e0', 0.05, blend=0.12, metal=0.1)
    mat('caixilho_ext', '#e9e7e1', 0.45)
    mat('porta_veneziana', '#e7e6e1', 0.6, img='ripado.jpg', tint=True, img_mean=0.82, uv=(0.5, 3.0))
    mat('reboco_grafite', '#55565c', 0.92, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('portico_madeira', '#7a5236', 0.7, img='madeira_fina.jpg', tint=True, img_mean=0.6, uv=1.5)
    mat('reboco_portaria', '#b4b3ae', 0.92, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.9, uv=1.6)
    mat('pergolado_grafite', '#2d2f33', 0.6, metal=0.3)
    mat('portao_grafite', '#3b3e42', 0.55, metal=0.3)
    mat('logo_park', '#ffffff', 0.6, img='logo_park.png', recorte=True)
    mat('logo_direcional', '#ffffff', 0.6, img='logo_direcional.png', recorte=True)
    mat('rede', '#f2f2ee', 0.7, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.25, 0.25))
    mat('atlas', '#ffffff', 0.5, img='atlas_lazer.jpg')
    mat('tela', '#ffffff', 0.25, img='atlas_lazer.jpg')
    mat('luz_poste', '#fff1cc', 0.4)
    mat('luz_chao', '#ffffff', 1.0, img='luz_radial.jpg')


# ------------------------------------------------------------------ utilitarios
def _mascara(rects, ref):
    """Retangulos px -> mascara booleana na janela ref (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = ref
    m = np.zeros((y1 - y0, x1 - x0), bool)
    for r in rects:
        m[max(0, int(r[1]) - y0):max(0, int(r[3]) - y0), max(0, int(r[0]) - x0):max(0, int(r[2]) - x0)] = True
    return m


def _decompor(m, ref):
    """Mascara -> retangulos px sem sobreposicao (varredura por linhas)."""
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


def porta_vidro(s, l=2.0, n=2):
    return (s, s + l, Z_PISO, Z_PISO + 2.35, 'porta_vidro', n)


def veneziana(s, l=0.9):
    return (s, s + l, Z_PISO, Z_PISO + 2.15, 'veneziana', 1)


def vao(s, l=1.0):
    return (s, s + l, Z_PISO, Z_PISO + 2.3, 'vao', 1)


def pergola(g, r, h=2.75, passo=0.5, sentido='x', mt='ferro_escuro', z=Z_PISO):
    """Pergola metalica: pilares nos cantos, 2 vigas, ripas transversais."""
    x0, x1, y0, y1 = r
    zt = z + h
    for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        g.caixa(px - 0.05, px + 0.05, py - 0.05, py + 0.05, z, zt, mt)
    if sentido == 'x':
        for yy in (y0, y1):
            g.caixa(x0 - 0.08, x1 + 0.08, yy - 0.04, yy + 0.04, zt - 0.12, zt, mt)
        p = x0
        while p <= x1 + 1e-3:
            g.caixa(p - 0.025, p + 0.025, y0 - 0.1, y1 + 0.1, zt, zt + 0.1, mt)
            p += passo
    else:
        for xx in (x0, x1):
            g.caixa(xx - 0.04, xx + 0.04, y0 - 0.08, y1 + 0.08, zt - 0.12, zt, mt)
        p = y0
        while p <= y1 + 1e-3:
            g.caixa(x0 - 0.1, x1 + 0.1, p - 0.025, p + 0.025, zt, zt + 0.1, mt)
            p += passo


# ------------------------------------------------------------------ chao do lazer (zonas a mao)
def chao_lazer(g):
    """Grama em toda a zona, caminhos levantados, cercas vivas e decks de madeira. A segmentacao (park_chao.json)
    nao entra nestas zonas (park_planta.ZONAS_A_MAO)."""
    for r in _uniao(PL.ZONAS_A_MAO):
        x0, x1, y0, y1 = RM(r)
        g.piso(x0, x1, y0, y1, 0.0, 'grama')
    # caminhos (o que cruza decks, lajes e o bloco fica por baixo deles)
    _laje(g, PL.CAMINHOS_LAZER, Z_PASSEIO, 'concreto', menos=[PL.BLOCO_LAZER, PL.DECK_CHURRASQUEIRA_T1] + PL.DECKS_SUL)
    _laje(g, PL.ENTRADAS_PISCINA, Z_PASSEIO, 'concreto')
    # cercas vivas: caixa verde com topo arredondado de folhas
    for r in PL.SEBES:
        x0, x1, y0, y1 = RM(r)
        g.caixa(x0, x1, y0, y1, 0, 0.95, 'sebe', topo='sebe')
    # decks de madeira com mesas (piquenique e apoio da quadra)
    for r in PL.DECKS_SUL + [PL.DECK_PIQUENIQUE]:
        x0, x1, y0, y1 = RM(r)
        g.caixa(x0, x1, y0, y1, 0, Z_MADEIRA, 'deck_madeira', lados='meio_fio')


# ------------------------------------------------------------------ piscinas, quadras, playground
def _piscina(g, rects_px, z_deck):
    """Tanque raso visualmente: fundo de pastilha, paredes internas e agua 6 cm abaixo do deck."""
    for r in rects_px:
        x0, x1, y0, y1 = RM(r)
        g.piso(x0, x1, y0, y1, 0.16, 'pastilha')
        g.piso(x0, x1, y0, y1, z_deck - 0.06, 'agua')
    m_px = {}
    for r in rects_px:
        for x in range(r[0], r[2]):
            for y in range(r[1], r[3]):
                m_px[(x, y)] = True
    for r in rects_px:
        x0, x1, y0, y1 = RM(r)
        lados = []
        if not m_px.get((r[0] - 1, (r[1] + r[3]) // 2)):
            lados.append([(x0, y1, 0.16), (x0, y0, 0.16), (x0, y0, z_deck), (x0, y1, z_deck)])
        if not m_px.get((r[2], (r[1] + r[3]) // 2)):
            lados.append([(x1, y0, 0.16), (x1, y1, 0.16), (x1, y1, z_deck), (x1, y0, z_deck)])
        if not m_px.get(((r[0] + r[2]) // 2, r[1] - 1)):
            lados.append([(x1, y1, 0.16), (x0, y1, 0.16), (x0, y1, z_deck), (x1, y1, z_deck)])
        if not m_px.get(((r[0] + r[2]) // 2, r[3])):
            lados.append([(x0, y0, 0.16), (x1, y0, 0.16), (x1, y0, z_deck), (x0, y0, z_deck)])
        for q in lados:
            g.face(q, 'pastilha')
            g.face(q[::-1], 'pastilha')


def _deck_com_piscinas(g, deck_px, piscinas_px, z=Z_DECK, mat_='deck'):
    for r in _menos(deck_px, piscinas_px):
        x0, x1, y0, y1 = RM(r)
        g.caixa(x0, x1, y0, y1, 0, z, mat_, lados='meio_fio')
    for r in piscinas_px:
        x0, x1, y0, y1 = RM(r)
        e = 0.25
        g.caixa(x0 - e, x1 + e, y1, y1 + e, z, z + 0.03, 'borda_piscina')
        g.caixa(x0 - e, x1 + e, y0 - e, y0, z, z + 0.03, 'borda_piscina')
    _piscina(g, piscinas_px, z)


def _quadra(g):
    x0, x1, y0, y1 = RM(PL.QUADRA_LAJE)
    g.caixa(x0, x1, y0, y1, 0, Z_QUADRA, 'quadra_verde', lados='meio_fio')
    q0, q1, r0, r1 = RM(PL.QUADRA)
    g.piso(q0, q1, r0, r1, Z_QUADRA + 0.004, 'quadra_terra')
    zl = Z_QUADRA + 0.008
    w = 0.06
    for xa, xb, ya, yb in ((q0, q1, r0, r0 + w), (q0, q1, r1 - w, r1), (q0, q0 + w, r0, r1), (q1 - w, q1, r0, r1)):
        g.piso(xa, xb, ya, yb, zl, 'faixa')
    xm = (q0 + q1) / 2
    g.piso(xm - w / 2, xm + w / 2, r0, r1, zl, 'faixa')
    ym = (r0 + r1) / 2
    for k in range(24):
        a0, a1 = 2 * math.pi * k / 24, 2 * math.pi * (k + 1) / 24
        p = [(xm + 1.8 * math.cos(a0), ym + 1.8 * math.sin(a0)), (xm + 1.8 * math.cos(a1), ym + 1.8 * math.sin(a1))]
        g.face([(p[0][0], p[0][1], zl), (p[1][0], p[1][1], zl), (xm + 1.74 * math.cos(a1), ym + 1.74 * math.sin(a1), zl),
                (xm + 1.74 * math.cos(a0), ym + 1.74 * math.sin(a0), zl)], 'faixa')
    for xx, s in ((q0, 1), (q1, -1)):
        for yy in (ym - 1.5, ym + 1.5):
            g.cil(xx, yy, 0.04, Z_QUADRA, Z_QUADRA + 2.0, 'faixa', seg=6)
        g.caixa(xx - 0.04, xx + 0.04, ym - 1.5, ym + 1.5, Z_QUADRA + 1.96, Z_QUADRA + 2.04, 'faixa')
        g.painel(xx - s * 0.6, ym - 1.5, xx - s * 0.6, ym + 1.5, Z_QUADRA, Z_QUADRA + 2.0, 'rede', (0, 0, 3, 2))
        # tabela de basquete atras do gol
        g.cil(xx - s * 0.9, ym, 0.06, Z_QUADRA, Z_QUADRA + 3.3, 'ferro_escuro', seg=8)
        g.caixa(xx - s * 0.9 - 0.03, xx - s * 0.9 + 0.03, ym - 0.9, ym + 0.9, Z_QUADRA + 2.75, Z_QUADRA + 3.8, 'faixa')
    _cerca(g, x0 + 0.1, x1 - 0.1, y0 + 0.1, y1 - 0.1, 4.0)


def _beach(g):
    x0, x1, y0, y1 = RM(PL.BEACH)
    g.caixa(x0, x1, y0, y1, 0, Z_QUADRA + 0.05, 'areia', lados='meio_fio')
    zl = Z_QUADRA + 0.055
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = 16.0 / 2, 8.0 / 2
    w = 0.05
    for xa, xb, ya, yb in ((cx - hx, cx + hx, cy - hy, cy - hy + w), (cx - hx, cx + hx, cy + hy - w, cy + hy),
                           (cx - hx, cx - hx + w, cy - hy, cy + hy), (cx + hx - w, cx + hx, cy - hy, cy + hy)):
        g.piso(xa, xb, ya, yb, zl, 'quadra_borda')
    g.piso(cx - w / 2, cx + w / 2, cy - hy, cy + hy, zl, 'quadra_borda')
    for yy in (cy - hy - 0.5, cy + hy + 0.5):
        g.cil(cx, yy, 0.05, zl, zl + 2.45, 'ferro_escuro', seg=6)
    g.painel(cx, cy - hy - 0.5, cx, cy + hy + 0.5, zl + 1.45, zl + 2.45, 'rede', (0, 0, 9, 1))
    g.painel(cx, cy + hy + 0.5, cx, cy - hy - 0.5, zl + 1.45, zl + 2.45, 'rede', (0, 0, 9, 1))
    _cerca(g, x0 + 0.1, x1 - 0.1, y0 + 0.1, y1 - 0.1, 4.0)


def _playground(g):
    x0, x1, y0, y1 = RM(PL.PLAYGROUND)
    g.caixa(x0, x1, y0, y1, 0, Z_QUADRA - 0.04, 'ep_vermelho', lados='meio_fio')
    e = 1.4      # pista vermelha em volta, miolo colorido (como 24-playground)
    for ya, yb, m in ((y0 + e, (y0 + y1) / 2, 'ep_azul'), ((y0 + y1) / 2, y1 - e, 'ep_verde')):
        g.piso(x0 + e, x1 - e, ya, yb, Z_QUADRA - 0.035, m)
    # faixas da pista
    xm = (x0 + x1) / 2
    for k in range(int((y1 - y0) / 1.6)):
        yy = y0 + 0.8 + k * 1.6
        g.piso(x0 + 0.62, x0 + 0.78, yy, yy + 0.7, Z_QUADRA - 0.032, 'faixa')


def _crossfit(g):
    x0, x1, y0, y1 = RM(PL.CROSSFIT)
    g.caixa(x0, x1, y0, y1, 0, Z_QUADRA - 0.04, 'ep_verde', lados='meio_fio')
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    for xa, xb, ya, yb in ((x0 + 1.0, xm - 1.5, ym, y1 - 1.0), (xm + 1.2, x1 - 1.0, y0 + 1.0, ym + 0.5)):
        g.piso(xa, xb, ya, yb, Z_QUADRA - 0.035, 'ep_terracota')


# ------------------------------------------------------------------ ambientes sem teto
def bloco_salas(g):
    """Salao de festas (com copa e WC), brinquedoteca, academia, pub, minimarket, beauty e cowork.
    Bloco de 34,1 x 8,3 m; a face norte (de cima na implantacao) da para o caminho e a quadra."""
    bx0, bx1, by0, by1 = RM(PL.BLOCO_LAZER)
    g.caixa(bx0 - 0.3, bx1 + 0.3, by0 - 0.3, by1 + 0.3, 0, Z_PISO, 'piso_cinza', lados='meio_fio')
    sx0, sx1 = X(PL.SALAO_X[0]), X(PL.SALAO_X[1])
    bq0, bq1 = X(PL.BRINQ_X[0]), X(PL.BRINQ_X[1])
    ac0, ac1 = X(PL.ACADEMIA_X[0]), X(PL.ACADEMIA_X[1])
    fx0, fxm, fx1 = X(PL.FIM_X[0]), X(PL.FIM_XM), X(PL.FIM_X[1])
    fym = Y(PL.FIM_YM)
    # salao de festas (13-salao-festas): areia com parede terracota, vidro para o caminho
    sala(g, (sx0, sx1, by0, by1), 'piso_int', {
        'n': (EXT, 'int_areia', [porta_vidro(1.2, 2.4, 3), janela(4.6, 2.2, 3), porta_vidro(8.2, 2.4, 3)]),
        'l': (EXT, 'int_terracota', []),
        's': (EXT, 'int_areia', [janela(6.0, 1.6, 2), janela(9.0, 1.6, 2)]),
        'o': (EXT, 'int_branco', [veneziana(1.0)]),
    })
    # WC do salao (2 sanitarios + copa de apoio), paredes internas
    wx0, wx1, wy0, wy1 = RM(PL.SALAO_WC)
    parede(g, (wx1, wy1), (wx0, wy1), 'int_branco', 'int_branco', [veneziana(1.6)], e=0.1)
    parede(g, (wx1, wy0), (wx1, wy1), 'int_branco', 'int_branco', [veneziana(0.6), veneziana(3.0)], e=0.1)
    ym = (wy0 + wy1) / 2
    parede(g, (wx0, ym), (wx1, ym), 'int_branco', 'int_branco', [], e=0.08)
    # brinquedoteca (19-brinquedoteca): creme e menta, piso de madeira
    sala(g, (bq0, bq1, by0, by1), 'piso_madeira', {
        'n': (EXT, 'int_creme', [porta_vidro(1.0, 2.2, 2)]),
        'l': (EXT, 'int_menta', []),
        's': (EXT, 'int_creme', [janela(1.2, 1.8, 2)]),
        'o': (EXT, 'int_menta', []),
    })
    # academia (14-academia): madeira na parte de cardio, emborrachado preto nos pesos
    sala(g, (ac0, ac1, by0, by1), 'piso_madeira', {
        'n': (EXT, 'int_grafite', [porta_vidro(1.2, 2.0, 2), janela(4.0, 3.0, 3)]),
        'l': (EXT, 'int_cinza', []),
        's': (EXT, 'int_grafite', [janela(1.5, 2.6, 3), janela(5.0, 2.0, 2)]),
        'o': (EXT, 'int_branco', []),
    })
    g.piso(X(1302), ac1, by0, by1, Z_PISO + 0.006, 'ep_preto')
    # pub de jogos (18-pub-jogos): grafite e tijolinho
    sala(g, (fx0, fxm, fym, by1), 'piso_cinza', {
        'n': (EXT, 'int_tijolo', [porta_vidro(1.0, 1.8, 2)]),
        'l': (EXT, 'int_grafite', []),
        's': (EXT, 'int_grafite', []),
        'o': (EXT, 'int_grafite', []),
    })
    # minimarket (21-minimarket): forro terracota vira faixa na parede
    sala(g, (fxm, fx1, fym, by1), 'piso_int', {
        'n': (EXT, 'int_branco', [porta_vidro(1.6, 1.8, 2)]),
        'l': (EXT, 'int_terracota', []),
        's': (EXT, 'int_branco', []),
        'o': (EXT, 'int_branco', []),
    })
    # beauty (06-beauty): branco com parede terracota
    sala(g, (fx0, fxm, by0, fym), 'piso_int', {
        'n': (EXT, 'int_branco', []),
        'l': (EXT, 'int_terracota', []),
        's': (EXT, 'int_branco', [porta_vidro(1.4, 1.6, 2)]),
        'o': (EXT, 'int_branco', [janela(1.0, 1.6, 2)]),
    })
    # cowork (10-cowork): verde escuro, fundo verde de gravacao
    sala(g, (fxm, fx1, by0, fym), 'piso_cinza', {
        'n': (EXT, 'int_verde', []),
        'l': (EXT, 'int_cinza', [janela(1.0, 1.8, 2)]),
        's': (EXT, 'int_verde', [porta_vidro(1.0, 1.6, 2)]),
        'o': (EXT, 'int_verde', []),
    })


def churrasqueira(g, r_edif, r_laje, decks):
    """Churrasqueira (09-churrasqueira): duas salas (norte e sul) com a churrasqueira de costas uma para a outra no
    meio, WC a oeste e pergola com jardim no canto noroeste. Laje de concreto e decks de madeira com mesas."""
    x0, x1, y0, y1 = RM(r_laje)
    g.caixa(x0, x1, y0, y1, 0, Z_PISO - 0.02, 'paver', lados='meio_fio')
    for r in decks:
        a0, a1, b0, b1 = RM(r)
        g.caixa(a0, a1, b0, b1, 0, Z_MADEIRA, 'deck_madeira', lados='meio_fio')
    ex0, ex1, ey0, ey1 = RM(r_edif)
    xw = ex0 + (ex1 - ex0) * 0.36          # WC e pergola a oeste
    yc0 = ey0 + (ey1 - ey0) * 0.35         # faixa das churrasqueiras entre as duas salas
    yc1 = ey0 + (ey1 - ey0) * 0.55
    # sala norte (aberta para a pergola a oeste)
    sala(g, (xw, ex1, yc1, ey1), 'piso_int', {
        'n': (EXT, 'int_verde', [janela(1.0, 1.6, 2)]),
        'l': (EXT, 'int_branco', [porta_vidro(0.6, 2.4, 3)]),
        's': (EXT, 'int_verde', []),
    })
    # sala sul (aberta para o deck sul)
    sala(g, (xw, ex1, ey0, yc0), 'piso_int', {
        'n': (EXT, 'int_verde', []),
        'l': (EXT, 'int_branco', [porta_vidro(0.6, 1.4, 2)]),
        'o': (EXT, 'int_branco', []),
    })
    # faixa das churrasqueiras (alvenaria) e WC
    g.caixa(xw, ex1, yc0, yc1, Z_PISO, Z_PISO + H_PAREDE, EXT, topo='parede_corte')
    sala(g, (ex0, xw, ey0, yc1), 'piso_cinza', {
        'n': (EXT, 'int_branco', [veneziana(0.4, 0.8)]),
        's': (EXT, 'int_branco', []),
        'o': (EXT, 'int_branco', [veneziana(0.5, 0.8), veneziana(2.3, 0.8)]),
    })
    parede(g, (ex0, (ey0 + yc1) / 2), (xw, (ey0 + yc1) / 2), 'int_branco', 'int_branco', [], e=0.08)
    # pergola com jardim no canto noroeste
    g.piso(ex0 + 0.2, xw - 0.2, yc1 + 0.2, ey1 - 0.2, Z_PISO + 0.002, 'terra')
    pergola(g, (ex0, xw, yc1, ey1), 2.8, 0.45, 'y', mt='ferro_escuro')


def club(g):
    """Village Club (15 a 17): deck com piscina e prainha, salao gourmet sem teto com WC e pergola."""
    _deck_com_piscinas(g, PL.CLUB_DECK, [PL.CLUB_PISCINA], z=0.32)
    x0, x1, y0, y1 = RM(PL.CLUB_DECK)
    _cerca(g, x0, x1, y0, y1, 1.6, mat='gradil_preto', passo=2.4, z=0.0)
    cx0, cx1, cy0, cy1 = RM(PL.CLUB_SALAO)
    zc = 0.32
    sala(g, (cx0, cx1, cy0, cy1), 'piso_int', {
        'n': (EXT, 'int_areia', [porta_vidro(1.0, 2.6, 3), porta_vidro(4.4, 2.6, 3)]),
        'l': (EXT, 'int_branco', [porta_vidro(1.0, 2.6, 3)]),
        's': (EXT, 'int_escuro', [janela(4.0, 2.0, 2)]),
        'o': (EXT, 'int_areia', []),
    }, z=zc)
    wx1 = cx0 + 3.4
    wy1 = cy0 + 1.9
    parede(g, (wx1, wy1), (cx0, wy1), 'int_branco', 'int_branco', [veneziana(1.2, 0.8)], z0=zc, z1=zc + H_PAREDE, e=0.1)
    parede(g, (wx1, cy0), (wx1, wy1), 'int_branco', 'int_branco', [], z0=zc, z1=zc + H_PAREDE, e=0.1)
    px0, px1, py0, py1 = RM(PL.CLUB_PERGOLA)
    pergola(g, (px0, px1, py0, py1), 2.8, 0.5, 'x', z=zc)


# ------------------------------------------------------------------ fechados com cobertura e entrada
def _edificio(g, r_px, h=H_EDIF, mat_='parede_externa', vidro=True, beiral=0.35):
    x0, x1, y0, y1 = RM(r_px)
    g.caixa(x0, x1, y0, y1, 0, h, mat_, topo='telha')
    g.caixa(x0 - beiral, x1 + beiral, y0 - beiral, y1 + beiral, h, h + 0.18, 'laje_borda', topo='telha', fundo='varanda_forro')
    if vidro:
        for (a, b) in (((x0, y0), (x1, y0)), ((x1, y1), (x0, y1))):
            L = abs(b[0] - a[0])
            n = max(1, int(L / 3.2))
            for k in range(n):
                u0 = a[0] + (b[0] - a[0]) * (k + 0.18) / n
                u1 = a[0] + (b[0] - a[0]) * (k + 0.82) / n
                yy = a[1] + (-0.012 if a[1] == y0 else 0.012)
                g.painel(u0, yy, u1, yy, 0.25, 2.5, 'vidro_porta', (0, 0, 1, 1))


def _vestiarios(g):
    x0, x1, y0, y1 = RM(PL.VESTIARIOS)
    z = Z_DECK
    g.caixa(x0, x1, y0, y1, z, z + 2.9, EXT, topo='telha')
    g.caixa(x0 - 0.12, x1 + 0.12, y0 - 0.12, y1 + 0.12, z + 2.9, z + 3.05, 'laje_borda', topo='telha', fundo='varanda_forro')
    for u in (1.2, 3.0, 4.8):
        g.caixa(x0 + u, x0 + u + 0.85, y1, y1 + 0.03, z, z + 2.1, 'porta_veneziana')


H_VIGA0, H_VIGA1 = 6.6, 7.4      # viga cinza dos porticos (perspectiva 03-portaria: portao ~2,4 m, painel ~7 m)
H_PERGOLA = 6.05                 # pergolado escuro pendurado sob a viga
H_PAINEL = 7.0


def _logo(g, xe, xd, y, zc, larg, alt, mat_):
    """Placa com alfa na face norte (+y), centrada em zc; xe = lado leste (esquerda de quem olha da rua)."""
    z0, z1 = zc - alt / 2, zc + alt / 2
    g.face([(xe, y, z0), (xd, y, z0), (xd, y, z1), (xe, y, z1)], mat_, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)],
           nrm=[(0, 1, 0)] * 4, cor=1.0)


def _pergolado(g, x0, x1, y0, y1, z, passo=0.5, ripa=0.08, alt=0.2):
    """Moldura escura com ripas no sentido y (frente-fundo), como no portico da perspectiva."""
    m = 'pergolado_grafite'
    g.caixa(x0, x1, y0, y0 + 0.14, z, z + alt + 0.06, m)
    g.caixa(x0, x1, y1 - 0.14, y1, z, z + alt + 0.06, m)
    g.caixa(x0, x0 + 0.14, y0, y1, z, z + alt + 0.06, m)
    g.caixa(x1 - 0.14, x1, y0, y1, z, z + alt + 0.06, m)
    n = max(2, int((x1 - x0) / passo))
    for k in range(1, n):
        xx = x0 + (x1 - x0) * k / n
        g.caixa(xx - ripa / 2, xx + ripa / 2, y0 + 0.14, y1 - 0.14, z + 0.04, z + alt, m)


def _portao_regua(g, xa, xb, y):
    """Portao de correr de reguas horizontais (grafite), com montantes."""
    m = 'portao_grafite'
    xa, xb = min(xa, xb), max(xa, xb)
    z = 0.12
    while z < 2.35:
        g.caixa(xa, xb, y - 0.025, y + 0.025, z, z + 0.1, m)
        z += 0.155
    n = max(2, int((xb - xa) / 2.4))
    for k in range(n + 1):
        xx = xa + (xb - xa) * k / n
        g.caixa(xx - 0.05, xx + 0.05, y - 0.04, y + 0.04, 0.05, 2.4, m)


def _portico(g, x_fora, x_ilha, yb, logo=None):
    """Um portico: painel de madeira com parede cinza atras na ponta de fora, pilar cinza na ilha, viga e pergolado."""
    lado = 1 if x_fora > x_ilha else -1                 # +1: portico leste (painel cresce para leste)
    xp0, xp1 = sorted((x_fora, x_fora + lado * 2.4))   # painel de madeira
    xw0, xw1 = sorted((x_fora - lado * 0.3, x_fora + lado * 3.3))   # parede cinza que continua a viga
    xi0, xi1 = sorted((x_ilha, x_ilha - lado * 0.6))   # pilar cinza junto a guarita
    C = 'reboco_portaria'
    g.caixa(xw0, xw1, yb - 0.55, yb - 0.2, 0, H_VIGA1, C)                       # parede (atras do painel)
    g.caixa(xp0, xp1, yb - 0.2, yb + 0.25, 0, H_PAINEL, 'portico_madeira', topo='portico_madeira')
    g.caixa(xi0, xi1, yb - 0.3, yb + 0.3, 0, H_VIGA1, C)                        # pilar da ilha
    va, vb = sorted((xi0 if lado > 0 else xi1, xw1 if lado > 0 else xw0))
    g.caixa(va, vb, yb - 0.3, yb + 0.3, H_VIGA0, H_VIGA1, C, fundo=C)           # viga
    pa, pb = sorted((xi1 if lado > 0 else xi0, xp0 if lado > 0 else xp1))
    _pergolado(g, pa + 0.1, pb - 0.1, yb - 1.7, yb + 1.7, H_PERGOLA)
    for xx in (pa + 1.2, (pa + pb) / 2, pb - 1.2):                                # tirantes ate a viga
        for s_ in (-1, 1):
            g.tubo([(xx, yb + s_ * 1.6, H_PERGOLA + 0.2), (xx, yb + s_ * 0.3, H_VIGA1 - 0.1)], 0.022, 'pergolado_grafite', seg=5)
    if logo:
        mat_, larg, alt, zc = logo
        xc = (xp0 + xp1) / 2
        xe, xd = xc + larg / 2, xc - larg / 2
        _logo(g, xe, xd, yb + 0.26, zc, larg, alt, mat_)


def _guarita(g):
    """Guarita de madeira com faixa de vidro, laje escura e pergolado em volta (perspectiva 03-portaria)."""
    x0, x1, y0, y1 = RM(PL.GUARITA)
    g.caixa(x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2, 0, 0.15, 'piso_cinza')
    g.caixa(x0, x1, y0, y1, 0.15, 0.95, 'portico_madeira')
    g.caixa(x0 + 0.04, x1 - 0.04, y0 + 0.04, y1 - 0.04, 0.95, 2.45, 'vidro_porta')
    for xx in (x0, x1 - 0.1):                                                    # montantes escuros
        for yy in (y0, y1 - 0.1):
            g.caixa(xx, xx + 0.1, yy, yy + 0.1, 0.95, 2.45, 'pergolado_grafite')
    for k in range(1, 4):
        xx = x0 + (x1 - x0) * k / 4
        g.caixa(xx - 0.03, xx + 0.03, y1 - 0.02, y1 + 0.01, 0.95, 2.45, 'pergolado_grafite')
    g.caixa(x0, x1, y0, y1, 2.45, 3.9, 'portico_madeira')
    g.caixa(x0 - 0.35, x1 + 0.35, y0 - 0.35, y1 + 0.35, 3.9, 4.1, 'pergolado_grafite')
    px0, px1, py0, py1 = RM(PL.PORTICO)
    _pergolado(g, px0 + 0.65, px1 - 0.65, py0, py1, 3.0, passo=0.45, alt=0.22)
    for xx in (px0 + 0.75, px1 - 0.87):                                          # pilaretes do pergolado
        for yy in (py0 + 0.05, py1 - 0.17):
            g.caixa(xx, xx + 0.12, yy, yy + 0.12, 0.0, 3.0, 'pergolado_grafite')


def _entrada(g):
    yb = Y(PL.VIGA_PORTICO_PY)
    xo, xio, xil, xl = (X(v) for v in PL.PORTARIA_X_PX)
    _portico(g, xl, xil, yb, logo=('logo_park', 2.0, 2.0 * 772 / 512, 4.4))       # leste: saida, logo do Village Park
    _portico(g, xo, xio, yb, logo=('logo_direcional', 1.5, 1.5 * 120 / 512, 4.6))  # oeste: entrada, Direcional
    _guarita(g)
    for r in PL.PORTOES:
        a0, a1, b0, b1 = RM(r)
        _portao_regua(g, a0, a1, yb - 0.75)
    for r, h in ((PL.LIXO, 2.8), (PL.APOIO, 3.0)):
        _edificio(g, r, h=h, vidro=(r is PL.APOIO))
    for cx, cy, rr in PL.RESERVATORIOS:
        g.cil(X(cx), Y(cy), rr * S_PX, 0, 7.5, 'parede_externa', seg=28, topo='cobertura')
        g.cil(X(cx), Y(cy), rr * S_PX + 0.08, 7.5, 7.7, 'laje_borda', seg=28, topo='cobertura')


def lazer(g):
    chao_lazer(g)
    _deck_com_piscinas(g, PL.DECK_PISCINA, PL.PISCINA + [PL.PISCINA_INFANTIL])
    # canteiros floridos: na borda norte do deck e a floreira dentro da piscina
    for r, z in ((PL.FLOREIRA_TOPO_PISCINA, Z_DECK), (PL.FLOREIRA_PISCINA, Z_DECK)):
        fx0, fx1, fy0, fy1 = RM(r)
        g.caixa(fx0 + 0.1, fx1 - 0.1, fy0 + 0.1, fy1 - 0.1, z, z + 0.45, 'borda_piscina', topo='terra')
    _vestiarios(g)
    _quadra(g)
    _beach(g)
    _playground(g)
    _crossfit(g)
    bx0, bx1, by0, by1 = RM(PL.BIKESHARE)
    g.caixa(bx0, bx1, by0, by1, 0, 0.2, 'ep_vermelho', lados='meio_fio')
    bloco_salas(g)
    churrasqueira(g, PL.CHURRASQUEIRA_T1, PL.DECK_CHURRASQUEIRA_T1, PL.DECKS_T1)
    churrasqueira(g, PL.CHURRASQUEIRA_T2, PL.DECK_CHURRASQUEIRA_T2, PL.DECKS_T2)
    club(g)
    x0, x1, y0, y1 = RM(PL.PET)
    _cerca(g, x0, x1, y0, y1, 1.2, mat='gradil_preto', passo=2.4, z=0.0)
    _entrada(g)

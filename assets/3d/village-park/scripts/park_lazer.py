# park_lazer.py -- lazer e apoio do Village Park. ETAPA 1: volumes simples nos lugares e medidas certos
# (piscinas com agua, quadras pintadas e cercadas, edificios do lazer fechados com cobertura, decks), mais a
# entrada (guarita, portico, portoes, deposito de lixo, apoio e reservatorios). Mobiliario e interiores: etapa 2.
# Medidas: park_planta.py (px) e FAQ. Executado por park_modelo.py dentro do Blender.

Z_DECK = 0.30          # deck da piscina acima do passeio (0,14)
Z_PISO = 0.20          # piso das quadras e do playground
H_EDIF = 3.4


def RM(r):
    """retangulo em px -> (x0, x1, y0, y1) em metros, com y0 < y1"""
    return X(r[0]), X(r[2]), Y(r[3]), Y(r[1])


def materiais_lazer():
    P_ = 'porcelanato.jpg'
    mat('deck', '#d6d0c5', 0.55, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('pastilha', '#ffffff', 0.25, img='pastilha.jpg', uv=1.6)
    mat('agua', '#3fb4b0', 0.04, blend=0.42, nrm='agua_normal.jpg', nrm_str=0.5, metal=0.0, uv=4.0)
    mat('borda_piscina', '#cfcabc', 0.6)
    mat('paver_bege', '#b6aca0', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    E_ = dict(img='emborrachado.jpg', tint=True, uv=1.5)
    mat('quadra_terra', '#b45a33', 0.75, **E_)
    mat('quadra_verde', '#3f8a4f', 0.75, **E_)
    mat('quadra_borda', '#47494d', 0.8, **E_)
    mat('ep_vermelho', '#b8443a', 0.85, **E_)
    mat('ep_azul', '#2f86c8', 0.85, **E_)
    mat('ep_verde', '#4f9a52', 0.85, **E_)
    mat('ep_amarelo', '#e4b42c', 0.85, **E_)
    mat('areia', '#d9c9a6', 0.97, img='concreto.jpg', tint=True, uv=2.0)
    mat('alambrado', '#2f4a3b', 0.6, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.5, 0.5))
    mat('gradil_preto', '#26282b', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('ferro_escuro', '#2a2d30', 0.55, metal=0.35)
    mat('vidro_lazer', '#4a5d68', 0.06, metal=0.15)
    mat('caixilho_ext', '#e9e7e1', 0.45)
    mat('reboco_grafite', '#55565c', 0.92, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('portico_madeira', '#7a5236', 0.7, img='madeira_fina.jpg', tint=True, img_mean=0.6, uv=1.5)
    mat('rede', '#f2f2ee', 0.7, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.25, 0.25))


def _menos(r, buracos):
    """Retangulo px menos buracos px -> retangulos px (grade de 1 px)."""
    x0, y0, x1, y1 = r
    m = np.ones((y1 - y0, x1 - x0), bool)
    for b in buracos:
        m[max(0, b[1] - y0):max(0, b[3] - y0), max(0, b[0] - x0):max(0, b[2] - x0)] = False
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


def _cerca(g, x0, x1, y0, y1, h, mat='alambrado', passo=2.5):
    """Cerca em volta de um retangulo (m): tela com recorte e postes."""
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        g.painel(a[0], a[1], b[0], b[1], Z_PISO, h, mat, (0, 0, L / 0.5 / 4, h / 0.5 / 4))
        g.painel(b[0], b[1], a[0], a[1], Z_PISO, h, mat, (0, 0, L / 0.5 / 4, h / 0.5 / 4))
        n = max(1, round(L / passo))
        for k in range(n + 1):
            t = k / n
            px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            g.cil(px, py, 0.035, 0, h + 0.05, 'ferro_escuro', seg=6)


def _piscina(g, rects_px, z_deck):
    """Tanque raso visualmente: fundo de pastilha, paredes internas e agua 6 cm abaixo do deck."""
    for r in rects_px:
        x0, x1, y0, y1 = RM(r)
        g.piso(x0, x1, y0, y1, 0.16, 'pastilha')
        g.piso(x0, x1, y0, y1, z_deck - 0.06, 'agua')
    # paredes internas so na divisa com o deck
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
        # borda de pedra em volta do tanque
        g.caixa(x0 - e, x1 + e, y1, y1 + e, z, z + 0.03, 'borda_piscina')
        g.caixa(x0 - e, x1 + e, y0 - e, y0, z, z + 0.03, 'borda_piscina')
    _piscina(g, piscinas_px, z)


def _edificio(g, r_px, h=H_EDIF, mat_='parede_externa', vidro=True, beiral=0.35):
    """Volume fechado com faixa de vidro nas fachadas e cobertura de telha com beiral (etapa 1)."""
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
                g.painel(u0, yy, u1, yy, 0.25, 2.5, 'vidro_lazer', (0, 0, 1, 1))


def _quadra(g):
    x0, x1, y0, y1 = RM(PL.QUADRA_LAJE)
    g.caixa(x0, x1, y0, y1, 0, Z_PISO, 'quadra_verde', lados='meio_fio')
    q0, q1, r0, r1 = RM(PL.QUADRA)
    g.piso(q0, q1, r0, r1, Z_PISO + 0.004, 'quadra_terra')
    zl = Z_PISO + 0.008
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
    # traves
    for xx, s in ((q0, 1), (q1, -1)):
        for yy in (ym - 1.5, ym + 1.5):
            g.cil(xx, yy, 0.04, Z_PISO, Z_PISO + 2.0, 'faixa', seg=6)
        g.caixa(xx - 0.04, xx + 0.04, ym - 1.5, ym + 1.5, Z_PISO + 1.96, Z_PISO + 2.04, 'faixa')
    _cerca(g, x0 + 0.1, x1 - 0.1, y0 + 0.1, y1 - 0.1, 4.0)


def _beach(g):
    x0, x1, y0, y1 = RM(PL.BEACH)
    g.caixa(x0, x1, y0, y1, 0, Z_PISO + 0.05, 'areia', lados='meio_fio')
    zl = Z_PISO + 0.055
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = 16.0 / 2, 8.0 / 2       # quadra de beach tennis / volei de praia dentro da areia
    w = 0.05
    for xa, xb, ya, yb in ((cx - hx, cx + hx, cy - hy, cy - hy + w), (cx - hx, cx + hx, cy + hy - w, cy + hy),
                           (cx - hx, cx - hx + w, cy - hy, cy + hy), (cx + hx - w, cx + hx, cy - hy, cy + hy)):
        g.piso(xa, xb, ya, yb, zl, 'quadra_borda')
    for yy in (cy - hy - 0.5, cy + hy + 0.5):
        g.cil(cx, yy, 0.05, zl, zl + 2.45, 'ferro_escuro', seg=6)
    g.painel(cx, cy - hy - 0.5, cx, cy + hy + 0.5, zl + 1.45, zl + 2.45, 'rede', (0, 0, 9, 1))
    g.painel(cx, cy + hy + 0.5, cx, cy - hy - 0.5, zl + 1.45, zl + 2.45, 'rede', (0, 0, 9, 1))
    _cerca(g, x0 + 0.1, x1 - 0.1, y0 + 0.1, y1 - 0.1, 4.0)


def _playground(g):
    x0, x1, y0, y1 = RM(PL.PLAYGROUND)
    g.caixa(x0, x1, y0, y1, 0, Z_PISO - 0.04, 'ep_vermelho', lados='meio_fio')
    e = 1.4      # pista vermelha em volta, miolo colorido
    xm = (x0 + x1) / 2
    for i, (ya, yb, m) in enumerate(((y0 + e, (y0 + y1) / 2, 'ep_azul'), ((y0 + y1) / 2, y1 - e, 'ep_verde'))):
        g.piso(x0 + e, x1 - e, ya, yb, Z_PISO - 0.035, m)
    # brinquedo principal: torres com telhado e escorregador (volume simples)
    for yy in ((y0 + y1) / 2 - 3.0, (y0 + y1) / 2 + 3.5):
        g.caixa(xm - 1.0, xm + 1.0, yy - 1.0, yy + 1.0, 1.2, 1.35, 'ep_amarelo')
        for dx in (-0.9, 0.9):
            for dy in (-0.9, 0.9):
                g.cil(xm + dx, yy + dy, 0.06, Z_PISO, 2.6, 'ep_azul', seg=6)
        g.prisma([(xm - 1.2, yy - 1.2), (xm + 1.2, yy - 1.2), (xm + 1.2, yy + 1.2), (xm - 1.2, yy + 1.2)], 2.6, 2.75, 'ep_verde')
    g.face([(xm + 1.0, (y0 + y1) / 2 - 3.6, 1.3), (xm + 3.2, (y0 + y1) / 2 - 3.6, Z_PISO + 0.1),
            (xm + 3.2, (y0 + y1) / 2 - 2.6, Z_PISO + 0.1), (xm + 1.0, (y0 + y1) / 2 - 2.6, 1.3)][::-1], 'ep_amarelo')


def _churrasqueira(g, deck_px, edif_px):
    x0, x1, y0, y1 = RM(deck_px)
    g.caixa(x0, x1, y0, y1, 0, 0.2, 'paver_bege', lados='meio_fio')
    _edificio(g, edif_px, h=3.0, vidro=False)


def _club(g):
    _deck_com_piscinas(g, PL.CLUB_DECK, [PL.CLUB_PISCINA], z=0.32)
    _edificio(g, PL.CLUB_SALAO, h=3.2)
    x0, x1, y0, y1 = RM(PL.CLUB_DECK)
    _cerca(g, x0, x1, y0, y1, 1.6, mat='gradil_preto', passo=2.4)


def _entrada(g):
    # guarita (vidro escuro em volta, cobertura plana grafite) sob o portico
    x0, x1, y0, y1 = RM(PL.GUARITA)
    g.caixa(x0, x1, y0, y1, 0, 0.9, 'portico_madeira')
    g.caixa(x0 + 0.05, x1 - 0.05, y0 + 0.05, y1 - 0.05, 0.9, 2.7, 'vidro_lazer')
    g.caixa(x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 0.3, 2.7, 3.0, 'reboco_grafite')
    # portico: dois quadros altos nas laterais das pistas com viga e cobertura (perspectiva da fachada)
    px0, px1, py0, py1 = RM(PL.PORTICO)
    for xa, xb in ((X(1030), X(1185)), (X(1275), X(1440))):
        g.caixa(xa, xa + 0.9, py0 + 1.0, py1 - 1.0, 0, 6.0, 'reboco_grafite')        # pilar
        g.caixa(xb - 0.6, xb, py0 + 1.0, py1 - 1.0, 0, 6.0, 'portico_madeira')
        g.caixa(xa, xb, py0 + 1.0, py1 - 1.0, 6.0, 6.8, 'reboco_grafite')
        g.caixa(xa + 0.9, xb - 0.6, py0 + 1.6, py1 - 1.6, 5.4, 5.55, 'ferro_escuro')
    for r in PL.PORTOES:
        a0, a1, b0, b1 = RM(r)
        ym = (b0 + b1) / 2
        g.painel(a0, ym, a1, ym, 0.05, 2.2, 'gradil_preto', (0, 0, (a1 - a0) / 2.4, 1))
        g.painel(a1, ym, a0, ym, 0.05, 2.2, 'gradil_preto', (0, 0, (a1 - a0) / 2.4, 1))
        g.caixa(a0, a1, ym - 0.05, ym + 0.05, 2.15, 2.25, 'ferro_escuro')
    for r, h in ((PL.LIXO, 2.8), (PL.APOIO, 3.0)):
        _edificio(g, r, h=h, vidro=(r is PL.APOIO))
    for cx, cy, rr in PL.RESERVATORIOS:
        g.cil(X(cx), Y(cy), rr * S_PX, 0, 7.5, 'parede_externa', seg=28, topo='cobertura')
        g.cil(X(cx), Y(cy), rr * S_PX + 0.08, 7.5, 7.7, 'laje_borda', seg=28, topo='cobertura')


def lazer(g):
    _deck_com_piscinas(g, PL.DECK_PISCINA, PL.PISCINA + [PL.PISCINA_INFANTIL])
    fx0, fx1, fy0, fy1 = RM(PL.FLOREIRA_PISCINA)
    g.caixa(fx0 + 0.1, fx1 - 0.1, fy0 + 0.1, fy1 - 0.1, Z_DECK, Z_DECK + 0.45, 'borda_piscina', topo='terra')
    x0, x1, y0, y1 = RM(PL.DECK_PISCINA)
    _cerca(g, x0, x1, y0, y1, 1.4, mat='gradil_preto', passo=2.4)
    _edificio(g, PL.VESTIARIOS, h=3.0, vidro=False)
    _quadra(g)
    _beach(g)
    _playground(g)
    bx0, bx1, by0, by1 = RM(PL.BIKESHARE)
    g.caixa(bx0, bx1, by0, by1, 0, 0.2, 'ep_vermelho', lados='meio_fio')
    _edificio(g, PL.BLOCO_LAZER, h=H_EDIF)
    _churrasqueira(g, PL.DECK_CHURRASQUEIRA_T1, PL.CHURRASQUEIRA_T1)
    _churrasqueira(g, PL.DECK_CHURRASQUEIRA_T2, PL.CHURRASQUEIRA_T2)
    _club(g)
    x0, x1, y0, y1 = RM(PL.PET)
    _cerca(g, x0, x1, y0, y1, 1.2, mat='gradil_preto', passo=2.4)
    _entrada(g)

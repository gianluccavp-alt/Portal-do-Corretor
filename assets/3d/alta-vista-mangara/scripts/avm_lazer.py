# avm_lazer.py -- lazer e apoio do Alta Vista Mangara. ETAPA 1: volumes simples nos lugares e medidas certos
# (piscina adulto com deck molhado e infantil, salao de festas e academia fechados, quadra de areia, playground,
# churrasqueira, praca, decks), mais o apoio (portaria, abrigo de lixo, pet place, casa de bombas, bike sharing e
# os 5 reservatorios). Mobiliario e interiores: etapa 2. Medidas: avm_planta.py (px). Executado por avm_modelo.py.

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
    mat('deck_madeira', '#9a6a45', 0.7, img='madeira_piso.jpg', tint=True, img_mean=0.6, uv=2.0)
    mat('grama_pet', '#5f8a3e', 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=3.0)


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


def _playground(g):
    x0, x1, y0, y1 = RM(PL.PLAYGROUND)
    g.caixa(x0, x1, y0, y1, 0, Z_PISO - 0.04, 'ep_vermelho', lados='meio_fio')
    e = 0.9      # pista vermelha em volta, miolo azul e verde
    g.piso(x0 + e, x1 - e, y0 + e, (y0 + y1) / 2, Z_PISO - 0.035, 'ep_azul')
    g.piso(x0 + e, x1 - e, (y0 + y1) / 2, y1 - e, Z_PISO - 0.035, 'ep_verde')
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    # brinquedo principal: torre com telhado e escorregador (volume simples)
    g.caixa(xm - 1.0, xm + 1.0, ym - 1.0, ym + 1.0, 1.2, 1.35, 'ep_amarelo')
    for dx in (-0.9, 0.9):
        for dy in (-0.9, 0.9):
            g.cil(xm + dx, ym + dy, 0.06, Z_PISO, 2.6, 'ep_azul', seg=6)
    g.prisma([(xm - 1.2, ym - 1.2), (xm + 1.2, ym - 1.2), (xm + 1.2, ym + 1.2), (xm - 1.2, ym + 1.2)], 2.6, 2.75, 'ep_verde')
    g.face([(xm + 1.0, ym - 0.5, 1.3), (xm + 2.8, ym - 0.5, Z_PISO + 0.1), (xm + 2.8, ym + 0.5, Z_PISO + 0.1),
            (xm + 1.0, ym + 0.5, 1.3)][::-1], 'ep_amarelo')


def _quadra_areia(g):
    x0, x1, y0, y1 = RM(PL.QUADRA_AREIA)
    g.caixa(x0, x1, y0, y1, 0, 0.18, 'areia', lados='meio_fio')
    xm = (x0 + x1) / 2
    for yy in (y0 + 0.3, y1 - 0.3):
        g.cil(xm, yy, 0.05, 0.18, 2.5, 'ferro_escuro', seg=6)
    g.painel(xm, y1 - 0.3, xm, y0 + 0.3, 1.5, 2.4, 'rede', (0, 0, (y1 - y0) / 1.0, 1))
    _cerca(g, x0 + 0.1, x1 - 0.1, y0 + 0.1, y1 - 0.1, 3.0)


def _salao(g):
    """Bloco do salao de festas (leste, com WCs) e da academia (oeste); decks da academia, gourmet e wine lounge."""
    _edificio(g, PL.EDIF_SALAO, h=H_EDIF)
    x0, x1, y0, y1 = RM(PL.DECK_GOURMET)
    g.caixa(x0, x1, y0, y1, 0, 0.2, 'deck_madeira', lados='meio_fio')
    # pergolado sobre o deck
    for k in range(int((x1 - x0) / 0.6)):
        xx = x0 + 0.3 + k * 0.6
        g.caixa(xx - 0.04, xx + 0.04, y0 + 0.2, y1, 2.75, 2.9, 'portico_madeira')
    for xx in (x0 + 0.2, x1 - 0.2):
        g.caixa(xx - 0.1, xx + 0.1, y0 + 0.2, y0 + 0.4, 0.2, 2.9, 'portico_madeira')


def _churrasqueira(g):
    _edificio(g, PL.CHURRASQUEIRA, h=3.0, vidro=False)
    x0, x1, y0, y1 = RM(PL.LOUNGE_CHURRASQUEIRA)
    g.caixa(x0, x1, y0, y1, 0, 0.2, 'deck_madeira', lados='meio_fio')
    x0, x1, y0, y1 = RM(PL.PIQUENIQUE)
    g.caixa(x0, x1, y0, y1, 0, 0.16, 'deck_madeira', lados='meio_fio')
    x0, x1, y0, y1 = RM(PL.PRACA)
    g.caixa(x0, x1, y0, y1, 0, 0.16, 'paver_bege', lados='meio_fio')


def _apoio(g):
    # portaria: guarita de vidro escuro com cobertura grafite
    x0, x1, y0, y1 = RM(PL.PORTARIA)
    g.caixa(x0, x1, y0, y1, 0, 0.9, 'parede_externa')
    g.caixa(x0 + 0.05, x1 - 0.05, y0 + 0.05, y1 - 0.05, 0.9, 2.8, 'vidro_lazer')
    g.caixa(x0 - 0.5, x1 + 0.5, y0 - 0.5, y1 + 0.5, 2.8, 3.1, 'reboco_grafite')
    _edificio(g, PL.LIXO, h=2.8, vidro=False)
    _edificio(g, PL.CASA_BOMBAS, h=2.6, vidro=False)
    x0, x1, y0, y1 = RM(PL.BIKE)
    g.caixa(x0, x1, y0, y1, 0, 0.16, 'concreto', lados='meio_fio')
    g.caixa(x0, x1, y0, y1, 2.4, 2.55, 'reboco_grafite')
    for xx in (x0 + 0.15, x1 - 0.15):
        for yy in (y0 + 0.15, y1 - 0.15):
            g.caixa(xx - 0.06, xx + 0.06, yy - 0.06, yy + 0.06, 0, 2.4, 'ferro_escuro')
    x0, x1, y0, y1 = RM(PL.PET)
    g.caixa(x0, x1, y0, y1, 0, 0.05, 'grama_pet')
    _cerca(g, x0, x1, y0, y1, 1.2, mat='gradil_preto', passo=2.4)
    for cx, cy in PL.RESERVATORIOS:
        rr = PL.RAIO_RESERVATORIO_PX * S_PX
        g.cil(X(cx), Y(cy), rr, 0, 2.6, 'cisterna', seg=24, topo='cisterna')
        g.cil(X(cx), Y(cy), 0.3, 2.6, 2.8, 'cisterna', seg=10)


def lazer(g):
    _deck_com_piscinas(g, PL.PISCINA_DECK, PL.PISCINA + [PL.PISCINA_INFANTIL])
    # deck molhado: lamina rasa na ponta norte da piscina adulto
    x0, x1, y0, y1 = RM(PL.DECK_MOLHADO)
    g.piso(x0, x1, y0, y1, Z_DECK - 0.10, 'pastilha')
    x0, x1, y0, y1 = RM(PL.PISCINA_DECK)
    _cerca(g, x0, x1, y0, y1, 1.3, mat='gradil_preto', passo=2.4)
    _salao(g)
    _playground(g)
    _quadra_areia(g)
    _churrasqueira(g)
    _apoio(g)

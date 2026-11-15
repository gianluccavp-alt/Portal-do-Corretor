# jbo_lazer.py -- lazer e apoio do Jardim Botanico em volumes (etapa 1), numerados como na implantacao da ficha:
# praca de convivencia (4), beach tennis (5), churrasqueira (6), quadra recreativa (7), salao de festas (8), espaco
# happy hour (9), playground (10), piscinas adulto e infantil com o solarium (11 a 13), fitness cross (14), academia
# (15), pet place (16), guarita (3), abrigo de lixo, cisterna e a cobertura das motos na entrada. Sem moveis (etapa 2),
# so o que da leitura de cima: espreguicadeiras, cabanas, guarda-sois, brinquedos e redes. Medidas: jbo_planta.py (px).
# Executado por jbo_modelo.py.

Z_DECK = 0.10          # solarium (concreto) acima do passeio
H_EDIF = 3.2


def materiais_lazer():
    mat('deck_madeira', '#b98a5e', 0.75, img='madeira_piso.jpg', tint=True, img_mean=0.6, uv=(2.0, 2.0))
    mat('pastilha', '#ffffff', 0.25, img='pastilha.jpg', uv=1.6)
    mat('agua', '#3fb4b0', 0.04, blend=0.42, nrm='agua_normal.jpg', nrm_str=0.5, metal=0.0, uv=4.0)
    mat('borda_piscina', '#d8d3c6', 0.6)
    E_ = dict(img='emborrachado.jpg', tint=True, uv=1.5)
    mat('ep_azul', '#3d7fc4', 0.85, **E_)
    mat('ep_azul_claro', '#8fc0e6', 0.85, **E_)
    mat('ep_cinza', '#9aa1a8', 0.85, **E_)
    mat('areia', '#e2cfaa', 0.98, img='concreto.jpg', tint=True, uv=2.0)
    mat('alambrado', '#2f5d3a', 0.6, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.5, 0.5))
    mat('rede', '#f2f2ee', 0.6, img='alambrado.png', tint=True, recorte=True, img_mean=1.0, uv=(0.25, 0.25))
    mat('gradil_preto', '#26282b', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('ferro_escuro', '#2a2d30', 0.55, metal=0.35)
    mat('ferro_verde', '#2b5e36', 0.55, metal=0.3)
    mat('vidro_cobertura', '#9fb6bf', 0.05, blend=0.45, double=True)
    mat('ripado_madeira', '#8a5f3e', 0.7, img='ripado.jpg', tint=True, img_mean=0.82, uv=(1.2, 1.2))
    mat('pergola_escura', '#2b2c2e', 0.6, metal=0.3)
    mat('telhado_laje', '#9a9893', 0.95)
    mat('piso_lazer', '#d8d2c6', 0.5, img='porcelanato.jpg', tint=True, img_mean=0.87, uv=3.0)
    mat('grama_pet', '#5f8a3e', 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=3.0)
    mat('brinquedo_azul', '#2f5fae', 0.5)
    mat('brinquedo_madeira', '#9a6a42', 0.7)
    mat('jardineira', '#3a5f2b', 0.95, img='grama2.jpg', tint=True, img_mean=1.0, uv=1.2)
    mat('ep_laranja', '#c4622d', 0.85, **E_)
    mat('ep_vermelho', '#d9473f', 0.85, **E_)
    mat('ep_verde', '#7aa63a', 0.85, **E_)
    mat('ep_verde_escuro', '#3f6a3a', 0.85, **E_)
    mat('quadra_azul', '#3f6fa6', 0.8, img='concreto.jpg', tint=True, uv=4.0)
    mat('solarium', '#a9a8a6', 0.85, img='paver.jpg', tint=True, img_mean=0.74, uv=1.6)
    mat('parede_lazer', '#8e9196', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('parede_guarita', '#6f7276', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('totem', '#e4e1da', 0.9, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.5, uv=TILE)
    mat('portico', '#3a3c40', 0.6, metal=0.2)
    mat('luz_portico', '#ffe2a8', 0.5)
    mat('madeira_escura', '#6e4a30', 0.7, img='madeira_fina.jpg', tint=True, img_mean=0.6, uv=(1.0, 1.0))
    mat('lona_branca', '#f1efe8', 0.9, img='tecido.jpg', tint=True, img_mean=0.8, uv=(1.0, 1.0), double=True)
    mat('lona_bege', '#c9a77c', 0.9, img='tecido.jpg', tint=True, img_mean=0.8, uv=(1.0, 1.0), double=True)
    mat('estofado', '#4a3a2e', 0.8)
    mat('flor_rosa', '#d58fb8', 0.85, img='touceira.png', tint=True, recorte=True, img_mean=0.75)
    mat('pneu_fitness', '#1b1c1e', 0.9)


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


def _cerca(g, x0, x1, y0, y1, h, mat='gradil_preto', passo=2.4, z0=0.0, poste='ferro_escuro', lados='snlo'):
    trechos = {'s': ((x0, y0), (x1, y0)), 'l': ((x1, y0), (x1, y1)), 'n': ((x1, y1), (x0, y1)), 'o': ((x0, y1), (x0, y0))}
    for a, b in (trechos[c] for c in lados):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        g.painel(a[0], a[1], b[0], b[1], z0, z0 + h, mat, (0, 0, L / 2.0, 1))
        g.painel(b[0], b[1], a[0], a[1], z0, z0 + h, mat, (0, 0, L / 2.0, 1))
        n = max(1, round(L / passo))
        for k in range(n + 1):
            t = k / n
            g.cil(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 0.035, z0, z0 + h + 0.05, poste, seg=6)


def _tanque(g, r, z_agua, fundo=0.04, borda=True):
    x0, x1, y0, y1 = RM(r)
    g.piso(x0, x1, y0, y1, fundo, 'pastilha')
    g.piso(x0, x1, y0, y1, z_agua, 'agua')
    for q in ([(x0, y1, fundo), (x0, y0, fundo), (x0, y0, Z_DECK), (x0, y1, Z_DECK)],
              [(x1, y0, fundo), (x1, y1, fundo), (x1, y1, Z_DECK), (x1, y0, Z_DECK)],
              [(x1, y1, fundo), (x0, y1, fundo), (x0, y1, Z_DECK), (x1, y1, Z_DECK)],
              [(x0, y0, fundo), (x1, y0, fundo), (x1, y0, Z_DECK), (x0, y0, Z_DECK)]):
        g.face(q[::-1], 'pastilha')
    if borda:
        e = 0.22
        g.caixa(x0 - e, x1 + e, y1, y1 + e, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x0 - e, x1 + e, y0 - e, y0, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x0 - e, x0, y0, y1, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x1, x1 + e, y0, y1, Z_DECK, Z_DECK + 0.03, 'borda_piscina')


def _edificio(g, r_px, h=H_EDIF, m='parede_externa', vidros=('s',), beiral=0.35):
    """Volume do lazer com laje plana e beiral; faces com vidro do piso a 2,4 m (pano a cada 3 m)."""
    x0, x1, y0, y1 = RM(r_px)
    g.caixa(x0, x1, y0, y1, 0, h, m, topo='telhado_laje')
    g.caixa(x0 - beiral, x1 + beiral, y0 - beiral, y1 + beiral, h, h + 0.18, 'laje_borda', topo='telhado_laje', fundo='forro', sem_fundo=False)
    for lado in vidros:
        if lado in 'sn':
            yy = y0 - 0.012 if lado == 's' else y1 + 0.012
            a, b = (x0, x1) if lado == 's' else (x1, x0)
        else:
            xx = x1 + 0.012 if lado == 'l' else x0 - 0.012
            a, b = (y0, y1) if lado == 'l' else (y1, y0)
        L = abs(b - a)
        n = max(1, int(L / 3.0))
        for k in range(n):
            u0 = a + (b - a) * (k + 0.08) / n
            u1 = a + (b - a) * (k + 0.92) / n
            if lado in 'sn':
                g.painel(u0, yy, u1, yy, 0.1, 2.4, 'vidro_lazer', (0, 0, 1, 1))
            else:
                g.painel(xx, u0, xx, u1, 0.1, 2.4, 'vidro_lazer', (0, 0, 1, 1))


def _pergolado(g, r_px, h, passo=0.45, ao_longo_x=True, m='pergola_escura', pilares=True, vidro=False):
    """Pergolado de vigas: pilares nos cantos (e a cada ~4 m), vigas de borda e ripas paralelas."""
    x0, x1, y0, y1 = RM(r_px)
    if pilares:
        nx = max(1, round((x1 - x0) / 4.0)); ny = max(1, round((y1 - y0) / 4.0))
        for i in range(nx + 1):
            for j in (0, ny):
                xx, yy = x0 + 0.1 + (x1 - x0 - 0.2) * i / nx, y0 + 0.1 + (y1 - y0 - 0.2) * j / max(1, ny)
                g.caixa(xx - 0.07, xx + 0.07, yy - 0.07, yy + 0.07, 0.05, h, m)
        for j in range(1, ny):
            for xx in (x0 + 0.1, x1 - 0.1):
                yy = y0 + 0.1 + (y1 - y0 - 0.2) * j / ny
                g.caixa(xx - 0.07, xx + 0.07, yy - 0.07, yy + 0.07, 0.05, h, m)
    e = 0.12
    g.caixa(x0, x1, y0, y0 + e, h, h + 0.22, m)
    g.caixa(x0, x1, y1 - e, y1, h, h + 0.22, m)
    g.caixa(x0, x0 + e, y0, y1, h, h + 0.22, m)
    g.caixa(x1 - e, x1, y0, y1, h, h + 0.22, m)
    if vidro:
        g.piso(x0, x1, y0, y1, h + 0.24, 'vidro_cobertura')
        g.face([(x0, y1, h + 0.235), (x1, y1, h + 0.235), (x1, y0, h + 0.235), (x0, y0, h + 0.235)], 'vidro_cobertura')
    if ao_longo_x:
        yy = y0 + passo
        while yy < y1 - 0.05:
            g.caixa(x0, x1, yy - 0.03, yy + 0.03, h + 0.04, h + 0.22, m); yy += passo
    else:
        xx = x0 + passo
        while xx < x1 - 0.05:
            g.caixa(xx - 0.03, xx + 0.03, y0, y1, h + 0.04, h + 0.22, m); xx += passo


def _edificio_telha(g, r_px, h=H_EDIF, m='parede_lazer', janelas=('s',), passo=3.2, cumeeira=False):
    """Volume do lazer com telha metalica de baixa inclinacao (implantacao e perspectiva aerea): platibanda baixa,
    telha clara por dentro e janelas de vidro em fita a cada ~3 m nas faces dadas."""
    x0, x1, y0, y1 = RM(r_px)
    g.caixa(x0, x1, y0, y1, 0.0, h, m, topo='telhado_laje')
    e = 0.15
    g.caixa(x0, x1, y0, y0 + e, h, h + 0.5, m, topo='pingadeira')
    g.caixa(x0, x1, y1 - e, y1, h, h + 0.5, m, topo='pingadeira')
    g.caixa(x0, x0 + e, y0, y1, h, h + 0.5, m, topo='pingadeira')
    g.caixa(x1 - e, x1, y0, y1, h, h + 0.5, m, topo='pingadeira')
    longo_x = (x1 - x0) >= (y1 - y0)
    if cumeeira:        # duas aguas com a cumeeira no meio do lado maior
        if longo_x:
            ym = (y0 + y1) / 2
            for a, b in ((y0 + e, ym), (y1 - e, ym)):
                _quad_cima(g, [(x0 + e, a, h + 0.05), (x1 - e, a, h + 0.05), (x1 - e, b, h + 0.42), (x0 + e, b, h + 0.42)], 'telha_metalica')
            g.caixa(x0 + e, x1 - e, ym - 0.08, ym + 0.08, h + 0.40, h + 0.47, 'telha_metalica')
        else:
            xm = (x0 + x1) / 2
            for a, b in ((x0 + e, xm), (x1 - e, xm)):
                _quad_cima(g, [(a, y0 + e, h + 0.05), (a, y1 - e, h + 0.05), (b, y1 - e, h + 0.42), (b, y0 + e, h + 0.42)], 'telha_metalica')
            g.caixa(xm - 0.08, xm + 0.08, y0 + e, y1 - e, h + 0.40, h + 0.47, 'telha_metalica')
    else:
        _quad_cima(g, [(x0 + e, y0 + e, h + 0.10), (x1 - e, y0 + e, h + 0.10), (x1 - e, y1 - e, h + 0.38), (x0 + e, y1 - e, h + 0.38)], 'telha_metalica')
    for lado in janelas:
        if lado in 'sn':
            yy = y0 - 0.012 if lado == 's' else y1 + 0.012
            a, b = (x0, x1) if lado == 's' else (x1, x0)
        else:
            xx = x1 + 0.012 if lado == 'l' else x0 - 0.012
            a, b = (y0, y1) if lado == 'l' else (y1, y0)
        L = abs(b - a)
        n = max(1, int(L / passo))
        for k in range(n):
            u0 = a + (b - a) * (k + 0.18) / n
            u1 = a + (b - a) * (k + 0.82) / n
            if lado in 'sn':
                g.painel(u0, yy, u1, yy, 1.0, 2.3, 'vidro_lazer', (0, 0, 1, 1))
            else:
                g.painel(xx, u0, xx, u1, 1.0, 2.3, 'vidro_lazer', (0, 0, 1, 1))


def _quad_cima(g, cs, mat, uvs=None):
    if _normal(cs)[2] < 0:
        cs = cs[::-1]
        if uvs is not None:
            uvs = uvs[::-1]
    g.face(cs, mat, uvs=uvs)


def _espreguicadeira(g, x, y, giro=90.0):
    with g.em(x, y, Z_DECK, giro):
        g.caixa(-0.95, 0.55, -0.32, 0.32, 0.18, 0.30, 'madeira_escura')
        _quad_cima(g, [(0.55, -0.32, 0.30), (0.95, -0.32, 0.72), (0.95, 0.32, 0.72), (0.55, 0.32, 0.30)], 'madeira_escura')
        g.caixa(-0.9, 0.5, -0.29, 0.29, 0.30, 0.36, 'estofado')
        for sx in (-0.85, 0.45):
            for sy in (-0.27, 0.27):
                g.caixa(sx - 0.03, sx + 0.03, sy - 0.03, sy + 0.03, 0.0, 0.18, 'madeira_escura')


def _cabana(g, r_px):
    """Cabana do solarium (perspectiva aerea): quadro de madeira, teto de lona branca e cortinas presas nos pilares,
    com um futon no meio."""
    x0, x1, y0, y1 = RM(r_px)
    h = 2.4
    for xx in (x0 + 0.06, x1 - 0.06):
        for yy in (y0 + 0.06, y1 - 0.06):
            g.caixa(xx - 0.06, xx + 0.06, yy - 0.06, yy + 0.06, Z_DECK, Z_DECK + h, 'madeira_escura')
            g.cil(xx + (0.18 if xx < (x0 + x1) / 2 else -0.18), yy + (0.18 if yy < (y0 + y1) / 2 else -0.18), 0.16,
                  Z_DECK + 0.05, Z_DECK + h - 0.1, 'lona_branca', seg=8, tampa=False)
    g.caixa(x0, x1, y0, y1, Z_DECK + h, Z_DECK + h + 0.12, 'madeira_escura', topo='lona_branca')
    g.caixa(x0 + 0.25, x1 - 0.25, y0 + 0.25, y1 - 0.25, Z_DECK, Z_DECK + 0.35, 'madeira_escura', topo='lona_branca')


def _guarda_sol(g, x, y, r=1.2, z0=Z_DECK):
    g.cil(x, y, 0.03, z0, z0 + 2.3, 'ferro_escuro', seg=6)
    n = 8
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        tri = [(x, y, z0 + 2.55), (x + r * math.cos(a0), y + r * math.sin(a0), z0 + 2.15),
               (x + r * math.cos(a1), y + r * math.sin(a1), z0 + 2.15)]
        _quad_cima(g, tri, 'lona_bege')


def _piscinas(g):
    """Solarium de concreto com a piscina adulto (14,9 x 5,0) e a infantil (5,0 x 2,9) recortadas, gradil preto em
    volta (perspectiva aerea), espreguicadeiras, duas cabanas, guarda-sois, palmeiras (paisagem) e a casa de maquinas."""
    for r in _menos(PL.DECK_PISCINA, [PL.PISCINA, PL.PISCINA_INFANTIL]):
        x0, x1, y0, y1 = RM(r)
        g.caixa(x0, x1, y0, y1, 0, Z_DECK, 'solarium', lados='meio_fio')
    _tanque(g, PL.PISCINA, Z_DECK - 0.06)
    _tanque(g, PL.PISCINA_INFANTIL, Z_DECK - 0.06)
    x0, x1, y0, y1 = RM(PL.DECK_PISCINA)
    _cerca(g, x0 + 0.1, x1 - 0.1, y0 + 0.1, y1 - 0.1, 1.2, 'gradil_preto', 2.4, z0=Z_DECK)
    for px, py in PL.ESPREGUICADEIRAS:
        _espreguicadeira(g, X(px), Y(py), giro=90.0)
    for r in PL.CABANAS:
        _cabana(g, r)
    for px, py, k in PL.GUARDA_SOIS:
        _guarda_sol(g, X(px), Y(py))
    for r in PL.CASA_MAQ:
        x0, x1, y0, y1 = RM(r)
        g.caixa(x0, x1, y0, y1, Z_DECK, 2.4, 'parede_externa', topo='telhado_laje')


def _playground(g):
    """Piso emborrachado em faixas diagonais (laranja, azul, verde e vermelho, perspectiva aerea), torre de madeira
    com telhado vermelho, escorregador e rede de escalada, casinha e gira-gira."""
    x0, x1, y0, y1 = RM(PL.PLAYGROUND)
    g.caixa(x0, x1, y0, y1, 0, 0.06, 'ep_laranja', lados='meio_fio')
    W, H = x1 - x0, y1 - y0
    for k, (m, a, b) in enumerate((('ep_vermelho', 0.30, 0.42), ('ep_azul', 0.42, 0.62), ('ep_verde', 0.62, 0.80))):
        # faixa diagonal: do canto de cima a esquerda para baixo a direita
        pts = [(x0 + W * a, y1), (x0 + W * b, y1), (x0 + W * (b + 0.25), y0), (x0 + W * (a + 0.25), y0)]
        pts = [(min(x1, max(x0, p[0])), p[1]) for p in pts]
        _quad_cima(g, [(p[0], p[1], 0.065) for p in pts], m)
    # torre com escorregador
    tx, ty = x0 + W * 0.22, y0 + H * 0.68
    for sx in (-0.7, 0.7):
        for sy in (-0.7, 0.7):
            g.caixa(tx + sx - 0.06, tx + sx + 0.06, ty + sy - 0.06, ty + sy + 0.06, 0.06, 2.7, 'brinquedo_madeira')
    g.caixa(tx - 0.75, tx + 0.75, ty - 0.75, ty + 0.75, 1.2, 1.3, 'brinquedo_madeira')
    g.prisma([(tx - 0.95, ty - 0.95), (tx + 0.95, ty - 0.95), (tx + 0.95, ty + 0.95), (tx - 0.95, ty + 0.95)], 2.7, 2.78, 'ep_vermelho')
    g.prisma([(tx - 0.95, ty - 0.95), (tx + 0.95, ty - 0.95), (tx, ty)], 2.78, 3.4, 'ep_vermelho')
    g.prisma([(tx + 0.95, ty + 0.95), (tx - 0.95, ty + 0.95), (tx, ty)], 2.78, 3.4, 'ep_vermelho')
    g.tubo([(tx + 0.75, ty, 1.25), (tx + 1.8, ty - 0.2, 0.9), (tx + 2.8, ty - 0.3, 0.35)], 0.28, 'ep_verde', seg=8)
    # casinha e gira-gira
    cx_, cy_ = x0 + W * 0.18, y0 + H * 0.25
    g.caixa(cx_ - 0.6, cx_ + 0.6, cy_ - 0.5, cy_ + 0.5, 0.06, 1.2, 'lona_branca')
    g.prisma([(cx_ - 0.7, cy_ - 0.6), (cx_ + 0.7, cy_ - 0.6), (cx_ + 0.7, cy_ + 0.6), (cx_ - 0.7, cy_ + 0.6)], 1.2, 1.35, 'ep_vermelho')
    gx, gy = x0 + W * 0.62, y0 + H * 0.42
    g.cil(gx, gy, 0.85, 0.06, 0.32, 'ep_vermelho', seg=16)
    g.cil(gx, gy, 0.05, 0.32, 0.9, 'ferro_escuro', seg=6)
    g.cil(gx, gy, 0.45, 0.9, 0.95, 'ep_verde', seg=12)


def _quadras(g):
    # quadra recreativa (7): piso azul com as linhas de basquete e futsal, alambrado e as tabelas
    x0, x1, y0, y1 = RM(PL.QUADRA)
    g.caixa(x0, x1, y0, y1, 0, 0.08, 'quadra_azul', lados='meio_fio')
    m = 0.6
    for xx in (x0 + m, x1 - m):
        g.piso(xx - 0.03, xx + 0.03, y0 + m, y1 - m, 0.085, 'faixa')
    for yy in (y0 + m, y1 - m, (y0 + y1) / 2):
        g.piso(x0 + m, x1 - m, yy - 0.03, yy + 0.03, 0.085, 'faixa')
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    n = 24
    for k in range(n):      # circulo central
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        r = 1.8
        g.face([(xm + r * math.cos(a0), ym + r * math.sin(a0), 0.086), (xm + (r - 0.06) * math.cos(a0), ym + (r - 0.06) * math.sin(a0), 0.086),
                (xm + (r - 0.06) * math.cos(a1), ym + (r - 0.06) * math.sin(a1), 0.086), (xm + r * math.cos(a1), ym + r * math.sin(a1), 0.086)][::-1], 'faixa')
    _cerca(g, x0, x1, y0, y1, 4.0, 'alambrado', 2.5, poste='ferro_verde')
    for yy, s in ((y0 + 0.8, 1), (y1 - 0.8, -1)):    # tabelas de basquete
        g.cil(xm, yy - s * 0.4, 0.06, 0.08, 3.3, 'ferro_escuro', seg=6)
        g.caixa(xm - 0.9, xm + 0.9, yy - 0.03, yy + 0.03, 2.9, 3.95, 'lona_branca')
    # beach tennis / volei de praia (5): areia, alambrado e rede no meio
    x0, x1, y0, y1 = RM(PL.BEACH)
    g.caixa(x0, x1, y0, y1, 0, 0.10, 'areia', lados='meio_fio')
    for xx in (x0 + 0.8, x1 - 0.8):
        g.piso(xx - 0.04, xx + 0.04, y0 + 0.9, y1 - 0.9, 0.105, 'pcd_azul')
    for yy in (y0 + 0.9, y1 - 0.9):
        g.piso(x0 + 0.8, x1 - 0.8, yy - 0.04, yy + 0.04, 0.105, 'pcd_azul')
    _cerca(g, x0, x1, y0, y1, 4.0, 'alambrado', 2.5, poste='ferro_verde')
    ym = (y0 + y1) / 2
    for xx in (x0 + 0.4, x1 - 0.4):
        g.cil(xx, ym, 0.04, 0.10, 2.5, 'ferro_escuro', seg=6)
    g.painel(x0 + 0.4, ym, x1 - 0.4, ym, 1.6, 2.4, 'rede', (0, 0, (x1 - x0) / 0.25, 3.2))
    g.painel(x1 - 0.4, ym, x0 + 0.4, ym, 1.6, 2.4, 'rede', (0, 0, (x1 - x0) / 0.25, 3.2))
    # churrasqueira (6): cobertura de telha sobre pilares no meio da faixa de paver laranja, bancada e mesas
    x0, x1, y0, y1 = RM(PL.CHURRASQUEIRA)
    for xx in (x0 + 0.15, x1 - 0.15):
        for k in range(4):
            yy = y0 + 0.15 + (y1 - y0 - 0.3) * k / 3
            g.caixa(xx - 0.1, xx + 0.1, yy - 0.1, yy + 0.1, 0.06, 2.9, 'pergola_escura')
    g.caixa(x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 0.3, 2.9, 3.05, 'laje_borda', topo='telha_metalica', fundo='forro', sem_fundo=False)
    g.caixa(x0 + 0.5, x1 - 0.5, y0 + 1.2, y0 + 1.8, 0.06, 0.95, 'parede_externa', topo='borda_piscina')
    g.caixa(x0 + 0.6, x0 + 1.4, y0 + 1.25, y0 + 1.75, 0.95, 2.4, 'parede_externa')
    for k in range(3):
        yy = y0 + 3.0 + k * (y1 - y0 - 4.5) / 2
        g.caixa((x0 + x1) / 2 - 0.45, (x0 + x1) / 2 + 0.45, yy - 0.9, yy + 0.9, 0.72, 0.78, 'madeira_escura')
        g.caixa((x0 + x1) / 2 - 0.05, (x0 + x1) / 2 + 0.05, yy - 0.7, yy + 0.7, 0.06, 0.72, 'madeira_escura')


def _praca(g):
    """Praca de convivencia (4): piso de concreto, sebe florida em volta (aberta nas entradas), canteiro com a arvore
    no meio e o pergolado com flores rosadas e bancos."""
    x0, x1, y0, y1 = RM(PL.PRACA)
    g.piso(x0, x1, y0, y1, 0.06, 'concreto')
    e = 0.8
    xm = (x0 + x1) / 2
    for a, b, c, d in ((x0, x1, y1 - e, y1), (x0, xm - 1.2, y0, y0 + e), (xm + 1.2, x1, y0, y0 + e),
                       (x0, x0 + e, y0, y1), (x1 - e, x1, y0, y1)):
        g.caixa(a, b, c, d, 0.06, 0.9, 'sebe')
    # canteiro central
    cx_, cy_ = X(12560), Y(790)
    g.caixa(cx_ - 1.6, cx_ + 1.6, cy_ - 1.6, cy_ + 1.6, 0.06, 0.45, 'meio_fio', topo='jardineira')
    _pergolado(g, PL.PERGOLA_PRACA, 2.8, passo=0.5, ao_longo_x=False, m='madeira_escura')
    px0, px1, py0, py1 = RM(PL.PERGOLA_PRACA)
    xx = px0 + 0.4
    while xx < px1 - 0.4:       # flores sobre o pergolado
        g.face([(xx - 0.35, py0 + 0.2, 3.04), (xx + 0.35, py0 + 0.2, 3.04), (xx + 0.35, py1 - 0.2, 3.04), (xx - 0.35, py1 - 0.2, 3.04)],
               'flor_rosa', uvs=[(0, 0), (1, 0), (1, 3), (0, 3)], nrm=[(0, 0, 1)] * 4)
        xx += 0.9
    for k in range(3):
        bx = px0 + 1.0 + k * (px1 - px0 - 2.0) / 2
        g.caixa(bx - 0.8, bx + 0.8, py0 + 0.6, py0 + 1.05, 0.06, 0.45, 'madeira_escura')


def _portaria(g):
    """Guarita (3) e o portico da entrada (perspectiva GUI_10_Portaria): guarita cinza com vidro, totem branco com o
    nome do condominio ao sul do acesso e o portico escuro com a fita de LED sobre os portoes."""
    x0, x1, y0, y1 = RM(PL.GUARITA)
    g.caixa(x0, x1, y0, y1, 0.0, 2.8, 'parede_guarita', topo='telhado_laje')
    g.caixa(x0 - 0.4, x1 + 0.4, y0 - 0.4, y1 + 0.4, 2.8, 3.0, 'laje_borda', topo='telhado_laje', fundo='forro', sem_fundo=False)
    g.face([(x1 + 0.012, y0 + 0.4, 1.0), (x1 + 0.012, y1 - 0.4, 1.0), (x1 + 0.012, y1 - 0.4, 2.4), (x1 + 0.012, y0 + 0.4, 2.4)], 'vidro_lazer')
    g.face([(x0 + 0.4, y0 - 0.012, 1.0), (x1 - 0.4, y0 - 0.012, 1.0), (x1 - 0.4, y0 - 0.012, 2.4), (x0 + 0.4, y0 - 0.012, 2.4)][::-1], 'vidro_lazer')
    # portico: totem ao sul do acesso, viga sobre os portoes ate a coluna junto a guarita
    xa, xb = X(12930), X(13040)
    ys, yn = Y(1300), Y(985)
    g.caixa(xa, xb, ys - 1.2, ys, 0.0, 6.0, 'totem', topo='laje_borda')
    g.caixa(xa + 0.6, xa + 0.95, yn - 0.2, yn + 0.25, 0.0, 5.4, 'portico')
    g.caixa(xa, xb, yn - 0.25, ys - 0.6, 5.0, 5.6, 'portico')
    g.caixa(xa + 0.05, xb - 0.05, yn - 0.2, ys - 0.65, 4.98, 5.0, 'luz_portico')


def _apoio(g):
    # academia (15) e salao de festas (8): volumes cinza com telha metalica
    _edificio_telha(g, PL.ACADEMIA, h=3.4, janelas=('l', 'o'), cumeeira=True)
    _edificio_telha(g, PL.SALAO, h=3.8, janelas=('n', 's'), cumeeira=True)
    # fitness cross (14): piso emborrachado, faixa de areia e o portico de barras
    x0, x1, y0, y1 = RM(PL.FITNESS)
    g.caixa(x0, x1, y0, y1, 0, 0.06, 'ep_verde_escuro', lados='meio_fio')
    g.piso(x0 + (x1 - x0) * 0.35, x0 + (x1 - x0) * 0.65, y0 + 0.5, y1 - 0.5, 0.065, 'areia')
    for k in range(3):
        yy = y0 + 2.0 + k * 3.0
        for xx in (x0 + 0.6, x1 - 0.6):
            g.caixa(xx - 0.05, xx + 0.05, yy - 0.05, yy + 0.05, 0.06, 2.4, 'ferro_escuro')
        g.tubo([(x0 + 0.6, yy, 2.35), (x1 - 0.6, yy, 2.35)], 0.025, 'ferro_escuro', seg=6)
    for k in range(3):
        g.cil(x0 + (x1 - x0) * 0.5, y1 - 1.2 - k * 1.3, 0.45, 0.06, 0.28, 'pneu_fitness', seg=12)
    # pet place (16)
    x0, x1, y0, y1 = RM(PL.PET)
    g.piso(x0, x1, y0, y1, 0.06, 'grama_pet')
    _cerca(g, x0, x1, y0, y1, 1.2, 'gradil_preto', 2.0)
    g.caixa(x0 + 0.6, x0 + 1.6, y0 + 0.8, y0 + 0.9, 0.0, 0.5, 'brinquedo_azul')
    # happy hour (9): piso de concreto, mesas e pergolado com cordao de luzes
    x0, x1, y0, y1 = RM(PL.HAPPY_HOUR)
    g.piso(x0, x1, y0, y1, 0.06, 'concreto')
    _pergolado(g, PL.HAPPY_HOUR, 2.8, passo=0.6, ao_longo_x=True, m='parede_externa')
    for k in range(2):
        yy = y0 + (y1 - y0) * (0.3 + 0.4 * k)
        g.caixa((x0 + x1) / 2 - 1.2, (x0 + x1) / 2 + 1.2, yy - 0.45, yy + 0.45, 0.74, 0.79, 'madeira_escura')
        g.caixa((x0 + x1) / 2 - 1.0, (x0 + x1) / 2 + 1.0, yy - 0.05, yy + 0.05, 0.06, 0.74, 'madeira_escura')
    # abrigo de lixo e gas, cisterna e caixa de medidores junto a entrada
    _edificio_telha(g, PL.LIXO, h=2.9, janelas=(), cumeeira=True)
    cx_, cy_, rr = PL.RESERVATORIO
    g.cil(X(cx_), Y(cy_), rr * S_PX, 0.0, 0.5, 'concreto', seg=32)
    g.cil(X(cx_), Y(cy_), rr * S_PX * 0.82, 0.5, 3.6, 'parede_externa', seg=32, topo='telhado_laje')
    x0, x1, y0, y1 = RM(PL.MEDIDORES)
    g.caixa(x0, x1, y0, y1, 0.0, 0.3, 'concreto')
    g.caixa(x0 + 0.5, x1 - 0.5, y0 + 0.5, y1 - 0.5, 0.3, 1.8, 'parede_externa', topo='telhado_laje')
    # cobertura metalica das motos ao lado da entrada (duas aguas na implantacao)
    x0, x1, y0, y1 = RM(PL.COBERTURA_SE)
    for xx in (x0 + 0.3, x1 - 0.3):
        for k in range(3):
            yy = y0 + 0.3 + (y1 - y0 - 0.6) * k / 2
            g.caixa(xx - 0.07, xx + 0.07, yy - 0.07, yy + 0.07, 0.02, 2.5, 'estrutura_escura')
    ym = (y0 + y1) / 2
    for a, b in ((y0, ym), (y1, ym)):
        _quad_cima(g, [(x0, a, 2.5), (x1, a, 2.5), (x1, b, 2.75), (x0, b, 2.75)], 'telha_metalica')
        g.face([(p[0], p[1], p[2] - 0.06) for p in [(x0, a, 2.5), (x1, a, 2.5), (x1, b, 2.75), (x0, b, 2.75)]][::-1]
               if a < b else [(p[0], p[1], p[2] - 0.06) for p in [(x0, a, 2.5), (x1, a, 2.5), (x1, b, 2.75), (x0, b, 2.75)]], 'telha_metalica')


def lazer(g):
    _piscinas(g)
    _playground(g)
    _quadras(g)
    _praca(g)
    _portaria(g)
    _apoio(g)

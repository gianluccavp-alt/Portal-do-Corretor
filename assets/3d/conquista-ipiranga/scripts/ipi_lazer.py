# ipi_lazer.py -- lazer e apoio do Conquista Clube Ipiranga. ETAPA 1: volumes simples nos lugares e medidas
# certos (solarium com piscina adulto 15,00 x 5,90 e infantil 4,75 x 3,20, vestiarios, fitness externo, playground,
# varanda gourmet com pergolado e o apoio administrativo, pet place, bicicletario), mais o apoio (guarita com
# delivery, casa de bombas, deposito de lixo e os 4 reservatorios). Mobiliario: etapa 2.
# Medidas: ipi_planta.py (px). Executado por ipi_modelo.py.

Z_DECK = 0.30          # solarium acima do passeio
Z_PISO = 0.12          # piso do playground e do fitness
H_EDIF = 3.0


def RM(r):
    """retangulo em px -> (x0, x1, y0, y1) em metros, com y0 < y1"""
    return X(r[0]), X(r[2]), Y(r[3]), Y(r[1])


def materiais_lazer():
    P_ = 'porcelanato.jpg'
    mat('deck', '#d9d3c8', 0.55, img=P_, tint=True, img_mean=0.87, uv=3.6)
    mat('pastilha', '#ffffff', 0.25, img='pastilha.jpg', uv=1.6)
    mat('agua', '#3fb4b0', 0.04, blend=0.42, nrm='agua_normal.jpg', nrm_str=0.5, metal=0.0, uv=4.0)
    mat('borda_piscina', '#cfcabc', 0.6)
    E_ = dict(img='emborrachado.jpg', tint=True, uv=1.5)
    mat('ep_grafite', '#3e4247', 0.85, **E_)
    mat('ep_azul', '#2f6fb8', 0.85, **E_)
    mat('ep_verde', '#4f9a52', 0.85, **E_)
    mat('ep_amarelo', '#e4b42c', 0.85, **E_)
    mat('ep_vermelho', '#c2453a', 0.85, **E_)
    mat('gradil_preto', '#26282b', 0.5, img='gradil.png', tint=True, recorte=True, img_mean=1.0, uv=(1.0, 1.0))
    mat('ferro_escuro', '#2a2d30', 0.55, metal=0.35)
    mat('vidro_lazer', '#4a5d68', 0.06, metal=0.15)
    mat('reboco_grafite', '#55565c', 0.92, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('pergola_madeira', '#7a5236', 0.7, img='madeira_fina.jpg', tint=True, img_mean=0.6, uv=1.5)
    mat('deck_grafite', '#6b6a68', 0.8, img=P_, tint=True, img_mean=0.87, uv=1.2)
    mat('grama_pet', '#5f8a3e', 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=3.0)
    mat('telhado_ripado', '#c9c6bf', 0.8, img='ripado.jpg', tint=True, img_mean=0.82, uv=(0.6, 0.6))


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


def _cerca(g, x0, x1, y0, y1, h, mat='gradil_preto', passo=2.4, z0=0.0):
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        g.painel(a[0], a[1], b[0], b[1], z0, z0 + h, mat, (0, 0, L / 2.0, 1))
        g.painel(b[0], b[1], a[0], a[1], z0, z0 + h, mat, (0, 0, L / 2.0, 1))
        n = max(1, round(L / passo))
        for k in range(n + 1):
            t = k / n
            g.cil(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 0.035, z0, z0 + h + 0.05, 'ferro_escuro', seg=6)


def _piscinas(g):
    """Solarium em deck com os tanques recortados: fundo de pastilha, paredes internas e agua 6 cm abaixo."""
    tanques = [PL.PISCINA, PL.PISCINA_INFANTIL]
    for r in _menos(PL.SOLARIUM, tanques):
        x0, x1, y0, y1 = RM(r)
        g.caixa(x0, x1, y0, y1, 0, Z_DECK, 'deck', lados='meio_fio')
    for r in tanques:
        x0, x1, y0, y1 = RM(r)
        g.piso(x0, x1, y0, y1, 0.04, 'pastilha')
        g.piso(x0, x1, y0, y1, Z_DECK - 0.06, 'agua')
        for q in ([(x0, y1, 0.04), (x0, y0, 0.04), (x0, y0, Z_DECK), (x0, y1, Z_DECK)],
                  [(x1, y0, 0.04), (x1, y1, 0.04), (x1, y1, Z_DECK), (x1, y0, Z_DECK)],
                  [(x1, y1, 0.04), (x0, y1, 0.04), (x0, y1, Z_DECK), (x1, y1, Z_DECK)],
                  [(x0, y0, 0.04), (x1, y0, 0.04), (x1, y0, Z_DECK), (x0, y0, Z_DECK)]):
            g.face(q[::-1], 'pastilha')
        e = 0.25
        g.caixa(x0 - e, x1 + e, y1, y1 + e, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x0 - e, x1 + e, y0 - e, y0, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x0 - e, x0, y0, y1, Z_DECK, Z_DECK + 0.03, 'borda_piscina')
        g.caixa(x1, x1 + e, y0, y1, Z_DECK, Z_DECK + 0.03, 'borda_piscina')


def _edificio(g, r_px, h=H_EDIF, mat_='parede_externa', vidro=True, beiral=0.3, telhado='telhado_ripado'):
    """Volume fechado com cobertura de telha metalica (ripado claro, como na implantacao) e beiral."""
    x0, x1, y0, y1 = RM(r_px)
    g.caixa(x0, x1, y0, y1, 0, h, mat_, topo=telhado)
    g.caixa(x0 - beiral, x1 + beiral, y0 - beiral, y1 + beiral, h, h + 0.16, 'laje_borda', topo=telhado, fundo='forro')
    if vidro:
        for (a, b) in (((x0, y0), (x1, y0)), ((x1, y1), (x0, y1))):
            L = abs(b[0] - a[0])
            n = max(1, int(L / 3.0))
            for k in range(n):
                u0 = a[0] + (b[0] - a[0]) * (k + 0.15) / n
                u1 = a[0] + (b[0] - a[0]) * (k + 0.85) / n
                yy = a[1] + (-0.012 if a[1] == y0 else 0.012)
                g.painel(u0, yy, u1, yy, 0.3, 2.4, 'vidro_lazer', (0, 0, 1, 1))


def _playground(g):
    x0, x1, y0, y1 = RM(PL.PLAYGROUND)
    g.caixa(x0, x1, y0, y1, 0, Z_PISO, 'ep_azul', lados='meio_fio')
    ym = (y0 + y1) / 2
    g.piso(x0 + 0.6, x1 - 0.6, ym - 2.6, ym + 0.4, Z_PISO + 0.004, 'ep_verde')
    g.piso(x0 + 0.6, x1 - 0.6, y1 - 3.0, y1 - 0.6, Z_PISO + 0.004, 'ep_verde')
    xm = (x0 + x1) / 2
    # brinquedo principal: torre com telhado amarelo e escorregador (volume simples)
    g.caixa(xm - 0.9, xm + 0.9, ym - 0.9, ym + 0.9, 1.2, 1.32, 'pergola_madeira')
    for dx in (-0.8, 0.8):
        for dy in (-0.8, 0.8):
            g.cil(xm + dx, ym + dy, 0.06, Z_PISO, 2.5, 'pergola_madeira', seg=6)
    g.prisma([(xm - 1.1, ym - 1.1), (xm + 1.1, ym - 1.1), (xm + 1.1, ym + 1.1), (xm - 1.1, ym + 1.1)], 2.5, 2.62, 'ep_amarelo')
    g.face([(xm - 0.4, ym - 0.9, 1.25), (xm - 0.4, ym - 3.0, Z_PISO + 0.1), (xm + 0.4, ym - 3.0, Z_PISO + 0.1),
            (xm + 0.4, ym - 0.9, 1.25)], 'ep_azul')
    _cerca(g, x0, x1, y0, y1, 1.1)


def _fitness(g):
    x0, x1, y0, y1 = RM(PL.FITNESS)
    g.caixa(x0, x1, y0, y1, 0, Z_PISO, 'ep_grafite', lados='meio_fio')
    for k in range(5):     # aparelhos de ginastica ao ar livre (volumes simples)
        xx = x0 + 1.2 + k * (x1 - x0 - 2.4) / 4
        yc = (y0 + y1) / 2
        g.cil(xx, yc, 0.07, Z_PISO, 1.6, 'ep_amarelo', seg=8)
        g.caixa(xx - 0.5, xx + 0.5, yc - 0.05, yc + 0.05, 1.5, 1.6, 'ep_amarelo')


def _gourmet(g):
    """Varanda gourmet: piso grafite com pergolado de madeira a oeste e o apoio administrativo a leste."""
    x0, x1, y0, y1 = RM(PL.GOURMET)
    g.caixa(x0, x1, y0, y1, 0, 0.15, 'deck_grafite', lados='meio_fio')
    g.caixa(x1 - 0.7, x1 - 0.1, y0 + 0.4, y1 - 0.4, 0.15, 1.05, 'reboco_grafite', topo='borda_piscina')   # bancada
    x0, x1, y0, y1 = RM(PL.PERGOLADO)
    g.caixa(x0, x1, y0, y1, 0, 0.15, 'deck_grafite', lados='meio_fio')
    for k in range(int((y1 - y0) / 0.55)):
        yy = y0 + 0.3 + k * 0.55
        g.caixa(x0 + 0.1, x1 - 0.1, yy - 0.04, yy + 0.04, 2.7, 2.85, 'pergola_madeira')
    for xx in (x0 + 0.2, x1 - 0.2):
        g.caixa(xx - 0.1, xx + 0.1, y0 + 0.1, y1 - 0.1, 2.55, 2.7, 'pergola_madeira')
        for yy in (y0 + 0.3, (y0 + y1) / 2, y1 - 0.3):
            g.caixa(xx - 0.1, xx + 0.1, yy - 0.1, yy + 0.1, 0.15, 2.7, 'pergola_madeira')
    _edificio(g, PL.APOIO, h=3.0)


def _pet(g):
    x0, x1, y0, y1 = RM(PL.PET)
    g.caixa(x0, x1, y0, y1, 0, 0.05, 'grama_pet')
    _cerca(g, x0, x1, y0, y1, 1.1)
    # tunel e obstaculos de agilidade
    g.cil(x0 + 6.0, (y0 + y1) / 2, 0.35, 0.05, 0.4, 'ep_azul', seg=10)
    for k in range(4):
        xx = x0 + 2 + k * 0.9
        g.cil(xx, y0 + 1.0, 0.03, 0.05, 0.6, 'ep_amarelo', seg=6)


def _bicicletario(g):
    (ax, ay), (bx, by) = PL.BICICLETARIO
    A, B = (X(ax), Y(ay)), (X(bx), Y(by))
    L = math.hypot(B[0] - A[0], B[1] - A[1])
    ang = math.degrees(math.atan2(B[1] - A[1], B[0] - A[0]))
    with g.em(A[0], A[1], 0.0, ang):
        n = int(L / 0.6)
        for k in range(n):
            xx = 0.3 + k * 0.6
            g.tubo([(xx, -0.35, Z_PASSEIO_LZ), (xx, -0.35, 0.75), (xx, 0.35, 0.75), (xx, 0.35, Z_PASSEIO_LZ)], 0.025, 'ferro_escuro', seg=5)


Z_PASSEIO_LZ = 0.06


def _apoio(g):
    # guarita com delivery: caixa taupe, frente de vidro voltada para a rua e laje plana com beiral (perspectiva do acesso)
    x0, x1, y0, y1 = RM(PL.GUARITA)
    g.caixa(x0, x1, y0, y1, 0, 2.8, 'parede_taupe')
    g.caixa(x1 - 0.02, x1 + 0.02, y0 + 0.6, y1 - 2.2, 1.0, 2.3, 'vidro_lazer')
    g.caixa(x1 - 0.02, x1 + 0.05, y0 + 0.5, y1 - 2.1, 0.95, 1.02, 'ferro_escuro')
    g.caixa(x0 - 0.6, x1 + 0.8, y0 - 0.6, y1 + 0.6, 2.8, 3.1, 'parede_externa', topo='cobertura', fundo='forro')
    _edificio(g, PL.CASA_BOMBAS, h=2.6, vidro=False)
    _edificio(g, PL.LIXO, h=2.6, vidro=False)
    for cx, cy in PL.RESERVATORIOS:
        rr = PL.RAIO_RESERVATORIO_PX * S_PX
        g.cil(X(cx), Y(cy), rr, 0.06, 2.4, 'cisterna', seg=24, topo='cisterna', r2=rr * 0.96)
        g.cil(X(cx), Y(cy), rr * 0.3, 2.4, 2.75, 'cisterna', seg=12, r2=rr * 0.12)
    for x0p, y0p, x1p, y1p in PL.SEBES:
        mx0, mx1, my0, my1 = X(x0p), X(x1p), Y(y1p), Y(y0p)
        g.caixa(mx0, mx1, my0, my1, 0.0, 0.7, 'sebe_flor' if x0p > 3000 else 'sebe')


def lazer(g):
    _piscinas(g)
    x0, x1, y0, y1 = RM(PL.SOLARIUM)
    _edificio(g, PL.VESTIARIO, h=2.8, vidro=False)
    _fitness(g)
    _playground(g)
    _gourmet(g)
    _pet(g)
    _bicicletario(g)
    _apoio(g)

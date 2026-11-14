# ipi_ambientes.py -- mobiliario de cada ambiente do lazer do Conquista Clube Ipiranga (pecas em ipi_moveis.py).
# Posicoes em px da implantacao (P), lidas na propria implantacao do Drive, que desenha o lazer visto de cima com
# os moveis; o estilo de cada peca segue as perspectivas da galeria (02 piscina, 03 fitness, 04 playground,
# 06 gourmet, 10 pet place, 11 bicicletario). Executado por ipi_modelo.py dentro do Blender (objeto 'moveis').


def PA(px, py):
    return X(px), Y(py)


def _em(g, px, py, z=None, giro=0.0, esc=1.0):
    x, y = PA(px, py)
    return g.em(x, y, Z_PISO if z is None else z, giro, esc)


def mesa_4(g, px, py, z, r=0.5, tampo='madeira', cad=None, perna='metal_preto', giro=45):
    """Mesa redonda com 4 cadeiras; cad() desenha uma cadeira com a frente em +x."""
    with _em(g, px, py, z, giro):
        g.sombra(-1.25, 1.25, -1.25, 1.25, 0.008, disco=True)
        mesa_redonda(g, r, 0.75, tampo, perna, larga=False)
        for a in (0, 90, 180, 270):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            with g.em(c * (r + 0.24), s * (r + 0.24), 0, a + 180):
                cad()
        utensilios(g, 0.2, 0.1, 0.75)


# ------------------------------------------------------------------ varanda gourmet (06) e pergolado
def gourmet_moveis(g):
    z = Z_GOURMET
    concha = lambda: cadeira_concha(g, 'plastico_preto', 'metal_preto')
    for px, py in ((1575, 1565), (1642, 1565), (1577, 1615), (1642, 1615)):
        mesa_4(g, px, py, z, 0.5, 'madeira', concha)
    # mesa comprida de madeira com as cadeiras verde oliva (perspectiva)
    xa, ya = PA(1584.5, 1670)
    with g.em(xa, ya, z, 90):
        g.sombra(-1.6, 1.6, -0.9, 0.9, 0.008)
        mesa_quadrada(g, 2.5, 0.95, 0.76, 'madeira', 'madeira')
        for k in range(4):
            x_ = -0.94 + k * 0.63
            for sy in (-1, 1):
                with g.em(x_, sy * 0.7, 0, -90 * sy):
                    cadeira_concha(g, 'plastico_oliva', 'plastico_oliva')
        for x_ in (-0.7, 0.0, 0.7):
            utensilios(g, x_, 0.18, 0.76)
            g.elipsoide(x_ + 0.25, 0.0, 0.8, 0.12, 0.12, 0.06, 'folha_verde', seg=8, aneis=3)
    # bancada de apoio com 4 banquetas
    x0, x1, y0, y1 = RM((1638, 1646, 1650, 1700))
    g.caixa(x0, x1, y0, y1, z, z + 1.0, 'reboco_grafite', topo='pedra_granito')
    for py in (1652, 1666, 1680, 1694):
        with _em(g, 1632, py, z):
            banqueta(g, 'madeira', 'metal_preto', 0.72)
    # cozinha na parede leste: geladeira inox, pia, cooktop e churrasqueira; prateleiras e TV
    xc = X(1690) - 0.02
    yA, yB = Y(1715), Y(1637)
    g.caixa(xc - 0.62, xc, yA + 1.1, yB, z, z + 0.9, 'madeira', topo='pedra_granito')        # armario e tampo
    g.caixa(xc - 0.6, xc, yB, yB + 0.75, z, z + 1.85, 'inox')                                   # geladeira
    g.painel(xc - 0.601, yB + 0.72, xc - 0.601, yB + 0.03, z + 0.05, z + 1.8, 'tela', ATL['geladeira_inox'])
    ys = Y(1660)
    g.caixa(xc - 0.5, xc - 0.12, ys - 0.3, ys + 0.3, z + 0.86, z + 0.905, 'inox')               # cuba
    g.tubo([(xc - 0.08, ys, z + 0.9), (xc - 0.08, ys, z + 1.2), (xc - 0.3, ys, z + 1.22)], 0.012, 'cromo', seg=5)
    yf = Y(1682)
    g.caixa(xc - 0.5, xc - 0.1, yf - 0.32, yf + 0.32, z + 0.9, z + 0.91, 'metal_preto')            # cooktop
    # churrasqueira de alvenaria grafite com coifa (canto sul)
    yq0, yq1 = yA, yA + 1.1
    g.caixa(xc - 0.75, xc, yq0, yq1, z, z + 0.95, 'reboco_grafite', topo='pedra_granito')
    g.caixa(xc - 0.7, xc, yq0 + 0.1, yq1 - 0.1, z + 0.95, z + 1.15, 'metal_preto')
    g.caixa(xc - 0.75, xc, yq0, yq1, z + 1.15, z + 2.9, 'reboco_grafite', sem='')
    g.caixa(xc - 0.76, xc - 0.74, yq0 + 0.15, yq1 - 0.15, z + 0.6, z + 1.1, 'metal_preto')
    for zz in (z + 1.55, z + 1.95):
        prateleira(g, xc - 0.28, xc, Y(1660) - 0.9, Y(1660) + 0.9, zz, 'madeira')
        for k in range(4):
            g.cil(xc - 0.14, Y(1660) - 0.6 + k * 0.4, 0.05, zz, zz + 0.16, ('ceramica', 'plastico_branco', 'madeira', 'vidro_escuro')[k], seg=8)
    tv(g, xc - 0.02, Y(1596), z + 1.65, 180, 1.1, 0.65, 'tv_show')
    g.caixa(xc - 0.45, xc, Y(1615), Y(1577), z, z + 0.6, 'madeira')                              # aparador
    for px, py in ((1553, 1545), (1553, 1703)):
        vaso_planta(g, X(px), Y(py), z, 0.26, 0.6, 1.4)
    # pergolado: mesas redondas com cadeiras de aluminio
    ext = lambda: cadeira_externa(g, 'tecido_escuro')
    for px, py in ((1492, 1545), (1518, 1585), (1492, 1630), (1518, 1675)):
        mesa_4(g, px, py, Z_PERGOLADO, 0.45, 'madeira_escura', ext, giro=0)


# ------------------------------------------------------------------ piscina (02)
def piscina_moveis(g):
    for py in (1582, 1610, 1637, 1666):
        with _em(g, 2121, py, Z_DECK, 0):
            g.sombra(-1.1, 1.1, -0.45, 0.45, 0.012)
            espreguicadeira(g)
    cad = lambda: cadeira_externa(g, 'tecido_areia', 'metal_champanhe')
    for px, py in ((2095, 1720), (2125, 1767), (2197, 1730), (2255, 1767)):
        mesa_4(g, px, py, Z_DECK, 0.45, 'plastico_cinza', cad, 'metal_champanhe', giro=30)
        with _em(g, px, py, Z_DECK):
            ombrelone(g, 1.25, 2.45)
    # ducha de inox no box ao lado do vestiario
    dx, dy = PA(2064, 1580)
    g.caixa(dx - 0.6, dx + 0.6, dy - 0.6, dy + 0.6, Z_DECK, Z_DECK + 0.03, 'piso_cinza')
    g.tubo([(dx, dy + 0.5, Z_DECK), (dx, dy + 0.5, Z_DECK + 2.25), (dx, dy + 0.15, Z_DECK + 2.3)], 0.025, 'inox', seg=6)
    g.cil(dx, dy + 0.12, 0.12, Z_DECK + 2.24, Z_DECK + 2.27, 'inox', seg=10)
    # bola na piscina infantil e boia na adulto
    bx, by = PA(2404, 1768)
    bola_praia(g, bx, by, Z_DECK - 0.22)
    bx, by = PA(2420, 1610)
    g.tubo([(bx + 0.4 * math.cos(2 * math.pi * k / 12), by + 0.4 * math.sin(2 * math.pi * k / 12), Z_DECK - 0.04) for k in range(13)],
           0.09, 'plastico_vermelho', seg=6)


# ------------------------------------------------------------------ fitness ao ar livre (03)
def fitness_moveis(g):
    z = Z_PISO
    with _em(g, 2262, 1511, z, 0):
        barra_fixa(g, 4, 1.25)
    with _em(g, 2290, 1532, z, 0):
        paralelas(g)
    with _em(g, 2208, 1519, z, 90):
        prancha_abdominal(g)
    for px, py, h, gi in ((2348, 1517, 0.5, 8), (2370, 1527, 0.6, -12), (2377, 1509, 0.45, 25)):
        with _em(g, px, py, z, gi):
            caixa_plyo(g, 0.6, 0.5, h)
    for k in range(3):
        x_, y_ = PA(2335 + k * 4, 1532)
        halter(g, x_, y_, z, 0.3, 0.07)


# ------------------------------------------------------------------ playground (04)
def playground_moveis(g):
    z = Z_PISO
    ax, ay = PA(1908, 1612)
    bx, by = PA(1912, 1672)
    # torre A (telhado amarelo em piramide) e torre B (mais baixa), postes laranja e guardas amarelas
    for (cx, cy, h, hp) in ((ax, ay, 1.45, 3.0), (bx, by, 1.15, 2.2)):
        for sx in (-1, 1):
            for sy in (-1, 1):
                g.caixa(cx + sx * 0.6 - 0.06, cx + sx * 0.6 + 0.06, cy + sy * 0.6 - 0.06, cy + sy * 0.6 + 0.06, z, z + hp, 'plastico_laranja')
        g.caixa(cx - 0.66, cx + 0.66, cy - 0.66, cy + 0.66, z + h - 0.06, z + h, 'plastico_marrom', sem_fundo=False)
        for sx in (-1, 1):
            g.caixa(cx + sx * 0.6 - 0.03, cx + sx * 0.6 + 0.03, cy - 0.55, cy + 0.55, z + h + 0.1, z + h + 0.75, 'plastico_amarelo')
    _telhado_cone(g, ax, ay, z + 3.0, 1.15, 0.85, 'plastico_amarelo', seg=4)
    # escorregador azul para leste, tunel verde entre as torres, rampa de escalada com pegas para leste da torre B
    _escorrega(g, (ax + 0.66, ay, z + 1.45), (ax + 3.1, ay, z + 0.3), 0.55, 'plastico_azulc')
    g.tubo([(ax, ay - 0.6, z + 1.85), (bx, by + 0.6, z + 1.55)], 0.42, 'plastico_verde', seg=14)
    g.face([(bx + 0.66, by - 0.5, z + 1.15), (bx + 0.66, by + 0.5, z + 1.15), (bx + 2.4, by + 0.5, z + 0.05), (bx + 2.4, by - 0.5, z + 0.05)],
           'pergola_madeira', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    g.face([(bx + 0.66, by + 0.5, z + 1.13), (bx + 0.66, by - 0.5, z + 1.13), (bx + 2.4, by - 0.5, z + 0.03), (bx + 2.4, by + 0.5, z + 0.03)],
           'pergola_madeira', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    for k, mt in enumerate(('plastico_amarelo', 'plastico_verde', 'plastico_vermelho', 'plastico_azulc', 'plastico_amarelo', 'plastico_laranja')):
        t = (k + 0.7) / 6.5
        g.caixa(bx + 0.66 + 1.74 * t - 0.06, bx + 0.66 + 1.74 * t + 0.06, by - 0.3 + 0.35 * (k % 2), by - 0.1 + 0.35 * (k % 2),
                z + 1.15 - 1.1 * t + 0.02, z + 1.15 - 1.1 * t + 0.07, mt)
    # escorregador cinza pequeno a oeste da torre B
    _escorrega(g, (bx - 0.66, by, z + 1.15), (bx - 2.4, by - 0.2, z + 0.28), 0.45, 'plastico_cinza')
    with _em(g, 1924, 1690, z):
        palmeira_play(g, 3.0)
    with _em(g, 1890, 1517, z, 0):
        banco_jardim(g, 1.8)


# ------------------------------------------------------------------ pet place (10)
def pet_moveis(g):
    z = 0.05
    with _em(g, 1588, 1025, z, 0):
        bambole_pet(g)
    a, b = PA(1618, 1013), PA(1647, 1040)
    for k in range(7):
        t = k / 6
        g.cil(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 0.022, z, z + 0.9, 'plastico_amarelo' if k % 2 else 'plastico_azul', seg=6)
    tunel_pet(g, [PA(px, py) for px, py in ((1610, 1062), (1618, 1066), (1626, 1068), (1634, 1069), (1642, 1068), (1650, 1065), (1657, 1059), (1662, 1052))], 0.3)
    x0, x1, y0, y1 = RM((1487, 1057, 1557, 1075))
    g.caixa(x0, x1, y0, y1, 0, 0.07, 'paver')
    with _em(g, 1537, 1071, 0.07, 0):
        banco_jardim(g, 1.4)


# ------------------------------------------------------------------ bicicletario (11)
def bike_moveis(g):
    (ax, ay), (bx, by) = PL.BICICLETARIO
    A, B = (X(ax), Y(ay)), (X(bx), Y(by))
    L = math.hypot(B[0] - A[0], B[1] - A[1])
    ang = math.degrees(math.atan2(B[1] - A[1], B[0] - A[0]))
    cores = ('plastico_preto', 'metal_preto', 'plastico_branco', 'plastico_vermelho', 'plastico_azul')
    with g.em(A[0], A[1], Z_PASSEIO_LZ, ang):
        n = int(L / 0.75)
        for k in range(n):
            xx = 0.4 + k * 0.75
            with g.em(xx, 0, 0, 90):
                paraciclo(g)
            if k % 3 != 1:
                with g.em(xx + 0.2, 0, 0, 90):
                    bicicleta(g, cores[k % len(cores)])


def moveis(g):
    gourmet_moveis(g)
    piscina_moveis(g)
    fitness_moveis(g)
    playground_moveis(g)
    pet_moveis(g)
    bike_moveis(g)

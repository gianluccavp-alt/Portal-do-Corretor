# avm_ambientes.py -- mobiliario de cada ambiente do lazer do Alta Vista Mangara (pecas em avm_moveis.py).
# Posicoes em px da implantacao (P), lidas na vista de cima do book (perspectiva VOO, ver avm_planta.py); o estilo
# de cada ambiente segue as perspectivas: ACA (academia), SFE (salao), CHU e PIQ (churrasqueira e piquenique),
# WIN (wine lounge), PIS (piscina), PLA (playground), QUA (quadra de areia), PET (pet place), BIC (bike sharing).
# Executado por avm_modelo.py dentro do Blender.


def P(px, py):
    return X(px), Y(py)


def _em(g, px, py, z=None, giro=0.0, esc=1.0):
    x, y = P(px, py)
    return g.em(x, y, Z_PISO if z is None else z, giro, esc)


def mesa_4(g, px, py, z=None, cad='estofada', r=0.5, tampo='madeira', giro=0.0, tec='tecido_bege'):
    """Mesa redonda com 4 cadeiras."""
    with _em(g, px, py, z, giro):
        g.sombra(-1.25, 1.25, -1.25, 1.25, 0.008, disco=True)
        mesa_redonda(g, r, 0.76, tampo, 'metal_ouro')
        for a in (45, 135, 225, 315):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            with g.em(c * (r + 0.26), s * (r + 0.26), 0, a + 180):
                if cad == 'estofada':
                    cadeira_estofada(g, tec, 'metal_ouro')
                else:
                    cadeira_concha(g, cad, 'metal_preto')
        utensilios(g, 0.2, 0.1, 0.76)


# ------------------------------------------------------------------ academia (ACA)
def academia_moveis(g):
    z = Z_PISO
    x0, x1 = X(PL.ACADEMIA_X[0]) + E_PAREDE, X(PL.ACADEMIA_X[1])
    y0, y1 = Y(PL.EDIF_SALAO[3]) + E_PAREDE, Y(PL.EDIF_SALAO[1]) - E_PAREDE
    # pista laranja de corrida no piso de madeira, com faixas brancas
    px0, px1 = X(2040), X(2054)
    g.piso(px0, px1, y0 + 0.2, y1 - 0.2, z + 0.008, 'ep_laranja')
    yy = y0 + 0.6
    while yy < y1 - 0.6:
        g.piso(px0 + 0.1, px1 - 0.1, yy, yy + 0.06, z + 0.011, 'faixa'); yy += 1.2
    # estacao funcional (crossover) encostada na parede oeste, rack de halteres e banco
    with _em(g, 2028, 1530, z + 0.006, 0):
        g.sombra(-1.1, 0.4, -1.1, 1.1, 0.01)
        estacao_cross(g)
    with _em(g, 2028, 1575, z + 0.006, 0):
        g.sombra(-0.35, 0.35, -0.75, 0.75, 0.01)
        rack_halteres(g)
    with _em(g, 2072, 1610, z, 90):
        g.sombra(-0.75, 0.75, -0.4, 0.4, 0.01)
        banco_supino(g)
    # tres esteiras viradas para o vidro norte e uma bike
    for py in (1523, 1550):
        with _em(g, 2084, py, z, 90):
            g.sombra(-1.1, 1.0, -0.55, 0.55, 0.01)
            esteira(g)
    with _em(g, 2084, 1578, z + 0.006, 90):
        g.sombra(-0.7, 0.7, -0.35, 0.35, 0.01)
        bike(g)
    for px, py in ((2062, 1590), (2066, 1596)):
        halter(g, X(px), Y(py), z + 0.006)
    g.elipsoide(X(2090), Y(1625), z + 0.32, 0.32, 0.32, 0.32, 'plastico_amarelo', seg=14, aneis=8)
    # espelho com LED e mural "workout" na parede do salao (lado da academia), TV no oeste
    g.painel(x1 - 0.015, y0 + 0.5, x1 - 0.015, y1 - 0.5, z + 0.45, z + 2.25, 'atlas', ATL['espelho_gym'])
    tv(g, x0 + 0.01, Y(1610), z + 1.7, 0, 1.0, 0.56, 'tv_treino')
    g.caixa(x0, x0 + 0.35, Y(1630), Y(1622), z, z + 1.1, 'inox')


# ------------------------------------------------------------------ salao de festas (SFE) e copa
def salao_moveis(g):
    z = Z_PISO
    for px, py in ((2119, 1528), (2161, 1528), (2205, 1528), (2119, 1608), (2160, 1608)):
        mesa_4(g, px, py)
    # banco-pufe laranja capitone no meio do salao
    with _em(g, 2150, 1569, z, 0):
        g.sombra(-1.3, 1.3, -0.6, 0.6, 0.01)
        g.caixa_red(-1.1, 1.1, -0.42, 0.42, 0.0, 0.42, 0.08, 'tecido_terracota', passos=2)
        g.caixa_red(0.3, 1.1, -0.42, 1.1, 0.0, 0.42, 0.08, 'tecido_terracota', passos=2)
    # ilha da copa com banquetas e o balcao de apoio
    g.caixa(X(2184), X(2199), Y(1615), Y(1567), z, z + 0.95, 'madeira_clara', topo='pedra_granito')
    for k in range(3):
        with _em(g, 2178, 1576 + k * 14, z, 0):
            banqueta(g, 'tecido_bege', 'metal_ouro', 0.66)
    # copa (norte do bloco dos WCs): bancada em L, geladeira inox, cooktop e prateleiras
    wx0, wx1 = X(PL.WC_X[0]) + 0.1, X(PL.WC_X[1]) - E_PAREDE
    yN = Y(PL.EDIF_SALAO[1]) - E_PAREDE
    g.caixa(wx0 + 0.9, wx1, yN - 0.62, yN, z, z + 0.9, 'madeira_clara', topo='pedra_granito')
    g.caixa(wx1 - 0.62, wx1, Y(1560) + 0.2, yN - 0.62, z, z + 0.9, 'madeira_clara', topo='pedra_granito')
    g.caixa(wx0, wx0 + 0.75, yN - 0.75, yN, z, z + 1.85, 'inox')
    g.painel(wx0 + 0.751, yN - 0.05, wx0 + 0.751, yN - 0.7, z + 0.02, z + 1.83, 'atlas', ATL['geladeira_inox'])
    prateleira(g, wx0 + 1.2, wx1 - 0.2, yN - 0.3, yN, z + 1.65, 'madeira')
    g.caixa(wx1 - 0.55, wx1 - 0.1, Y(1545), Y(1535), z + 0.9, z + 0.93, 'metal_preto')
    # WCs: vaso e bancada com cuba e espelho
    ys = (Y(PL.EDIF_SALAO[3]) + E_PAREDE + 0.6)
    for xa, xb in ((X(PL.WC_X[0]) + 0.1, X(2269)), (X(2269) + 0.08, X(PL.WC_X[1]) - E_PAREDE)):
        vaso_sanitario(g, (xa + xb) / 2 - 0.45, ys, z, 90)
        g.caixa((xa + xb) / 2 + 0.05, xb - 0.05, ys - 0.25, ys + 0.3, z, z + 0.85, 'plastico_branco', topo='pedra_granito')
    # cortinas de linho nos janeloes e plantas nos cantos
    for px in (2106, 2228):
        for yy in (Y(1505), Y(1630)):
            g.caixa(X(px) - 0.12, X(px) + 0.12, yy - 0.06, yy + 0.06, z, z + 2.7, 'tecido_bege')
    vaso_planta(g, X(2228) - 0.3, Y(1592), z, 0.26, 0.5, 1.5)
    vaso_planta(g, X(2106) + 0.3, Y(1570), z, 0.22, 0.45, 1.3)


# ------------------------------------------------------------------ churrasqueira (CHU) e lounge com pergola (PIQ)
def churrasqueira_moveis(g):
    z = Z_PISO
    cx0, cx1, cy0, cy1 = RM(PL.CHURRASQUEIRA)
    xw = X(1722)
    yN = cy1 - E_PAREDE
    # churrasqueira de alvenaria com coifa e bancada com cuba ao longo da parede norte
    g.caixa(xw - 1.25, xw - 0.06, yN - 0.62, yN, z, z + 0.9, 'int_branco', topo='pedra_granito')
    g.caixa(xw - 1.15, xw - 0.2, yN - 0.6, yN - 0.595, z + 0.95, z + 1.35, 'metal_preto')
    g.caixa(xw - 1.25, xw - 0.06, yN - 0.62, yN, z + 1.9, z + 2.6, 'int_branco')
    g.caixa(cx0 + 0.15, xw - 1.3, yN - 0.6, yN, z, z + 0.88, 'madeira_clara', topo='pedra_granito')
    g.caixa(cx0 + 0.15, cx0 + 0.85, yN - 0.75, yN, z, z + 1.85, 'inox')
    prateleira(g, cx0 + 1.0, xw - 1.4, yN - 0.25, yN, z + 1.7, 'madeira')
    # balcao com 3 banquetas pretas
    g.caixa(cx0 + 0.8, xw - 0.8, Y(1488), Y(1480), z, z + 1.0, 'madeira', topo='pedra_granito')
    for k in range(3):
        with _em(g, 1672 + k * 15, 1495, z, 90):
            banqueta(g, 'plastico_preto', 'metal_preto', 0.72)
    tv(g, cx0 + 0.15, Y(1500), z + 1.6, 0, 1.2, 0.68, 'tv_show')
    # WCs
    for yy in (cy0 + 0.6, (cy0 + cy1) / 2 + 0.6):
        vaso_sanitario(g, cx1 - E_PAREDE - 0.45, yy, z, 180)
    # lounge sob a pergola: duas mesas com cadeiras pretas
    for py in (1452, 1494):
        x_, y_ = P(1633, py)
        mesa_com_cadeiras(g, x_, y_, 0, 'externa', 0.8, z=Z_MADEIRA)
    # piquenique: duas mesas de madeira na grama e um ombrelone
    for px, py, giro in PL.MESAS_PIQUENIQUE:
        with _em(g, px, py, 0.0, giro):
            g.sombra(-1.2, 1.2, -1.0, 1.0, 0.01)
            mesa_piquenique(g)
            g.caixa(-0.5, 0.5, -0.38, 0.38, 0.765, 0.768, 'tecido_xadrez')
    with _em(g, 1592, 1452, 0.0):
        ombrelone(g, 1.0, 2.3)


# ------------------------------------------------------------------ decks e wine lounge (WIN)
def lounges_moveis(g):
    # lounge gourmet: deck de madeira com duas mesas pretas
    for px, py, giro in ((2128, 1662, 0), (2162, 1692, 15)):
        x_, y_ = P(px, py)
        mesa_com_cadeiras(g, x_, y_, giro, 'preta', 0.8, z=Z_MADEIRA)
    # wine lounge: poltronas azuis de fibra em volta do fogo de chao
    fx, fy = P(2258, 1680)
    g.cil(fx, fy, 0.5, 0.0, 0.34, 'pedra_granito', seg=18)
    g.cil(fx, fy, 0.36, 0.34, 0.36, 'luz_led', seg=18)
    for k, a in enumerate((20, 110, 200, 290)):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        with g.em(fx + c * 1.45, fy + s * 1.45, 0.0, a + 180):
            g.sombra(-0.5, 0.5, -0.5, 0.5, 0.01, disco=True)
            poltrona(g, 'tecido_azul', 'plastico_azul')
    # lounge academia: bancos de madeira e vasos
    for px in (2038, 2080):
        x_, y_ = P(px, 1650)
        g.caixa(x_ - 0.9, x_ + 0.9, y_ - 0.22, y_ + 0.22, Z_PASSEIO, Z_PASSEIO + 0.45, 'madeira')
    # praca de convivio: bancos sob as arvores
    for px, py in ((1830, 1485), (1915, 1485), (1990, 1430)):
        x_, y_ = P(px, py)
        g.caixa(x_ - 0.9, x_ + 0.9, y_ - 0.22, y_ + 0.22, Z_PASSEIO, Z_PASSEIO + 0.45, 'madeira')


# ------------------------------------------------------------------ piscina (PIS)
def piscina_moveis(g):
    # espreguicadeiras dentro do deck molhado (agua rasa) e no deck
    for py in (1486, 1510, 1534, 1559):
        with _em(g, 2414, py, Z_DECK - 0.10, 0):
            espreguicadeira(g)
    for py in (1594, 1621, 1648):
        with _em(g, 2362, py, Z_DECK, 0):
            g.sombra(-1.1, 1.1, -0.45, 0.45, 0.012)
            espreguicadeira(g)
    for py in (1508, 1562):
        with _em(g, 2354, py, Z_DECK):
            g.sombra(-1.3, 1.3, -1.3, 1.3, 0.012, disco=True)
            ombrelone(g, 1.15, 2.4)
        for dy in (-12, 12):
            with _em(g, 2343, py + dy, Z_DECK, 0):
                cadeira_externa(g)
    # boia e ducha
    bx, by = P(2492, 1495)
    g.cil(bx, by, 0.35, Z_DECK - 0.07, Z_DECK - 0.03, 'plastico_branco', seg=16)
    dx, dy = P(2340, 1730)
    g.tubo([(dx, dy, Z_DECK), (dx, dy, Z_DECK + 2.2), (dx + 0.3, dy, Z_DECK + 2.3)], 0.022, 'inox', seg=6)


# ------------------------------------------------------------------ playground (PLA)
def playground_moveis(g):
    z = Z_QUADRA - 0.026
    with _em(g, 1985, 1550, z, 90, 0.62):
        g.sombra(-4.5, 4.5, -2.5, 2.5, 0.012)
        brinquedo(g)
    # trenzinho colorido (vagoes) e dois balancos de mola
    for k, mt in enumerate(('plastico_amarelo', 'plastico_vermelho', 'plastico_azulc', 'plastico_verde')):
        x_, y_ = P(1935 + k * 9, 1602)
        g.caixa_red(x_ - 0.35, x_ + 0.35, y_ - 0.45, y_ + 0.45, z, z + 0.9, 0.08, mt, passos=2)
        for dx in (-0.25, 0.25):
            g.cil(x_ + dx, y_ - 0.47, 0.14, z, z + 0.28, 'plastico_preto', seg=10)
    for px, py, mt in ((1940, 1625, 'plastico_verde'), (1960, 1628, 'plastico_laranja')):
        with _em(g, px, py, z):
            g.cil(0, 0, 0.1, 0, 0.3, 'metal_preto', seg=8, tampa=False)
            g.elipsoide(0, 0, 0.42, 0.42, 0.14, 0.14, mt, seg=10, aneis=5, exp=0.7)


# ------------------------------------------------------------------ pet place (PET) e bike sharing (BIC)
def pet_moveis(g):
    x0, x1, y0, y1 = RM(PL.PET)
    zc = 0.05
    with g.em((x0 + x1) / 2 + 0.6, y0 + 1.0, zc, 0):
        g.face([(-0.7, -0.25, 0), (0.0, -0.25, 0.42), (0.0, 0.25, 0.42), (-0.7, 0.25, 0)], 'plastico_azulc', uvs=[(0, 0)] * 4)
        g.face([(0.0, -0.25, 0.42), (0.7, -0.25, 0), (0.7, 0.25, 0), (0.0, 0.25, 0.42)], 'plastico_azulc', uvs=[(0, 0)] * 4)
    for k in range(4):
        g.cil(x0 + 0.6 + k * 0.6, y0 + 0.5, 0.11, zc, zc + 0.32, 'plastico_laranja', seg=8, r2=0.02)
    g.caixa(x1 - 1.6, x1 - 0.2, y1 - 0.65, y1 - 0.25, zc, zc + 0.45, 'concreto')


def bike_moveis(g):
    x0, x1, y0, y1 = RM(PL.BIKE)
    z = 0.14
    xr = x0 + 1.2
    # porta-bicicletas: portico preto com as bicicletas penduradas pela roda e outras apoiadas no chao
    for yy in (y0 + 0.3, y1 - 0.3):
        g.caixa(xr - 0.05, xr + 0.05, yy - 0.05, yy + 0.05, z, z + 2.4, 'metal_preto')
    g.caixa(xr - 0.05, xr + 0.05, y0 + 0.3, y1 - 0.3, z + 2.35, z + 2.45, 'metal_preto')
    n = int((y1 - y0 - 0.8) / 0.75)
    for k in range(n):
        yy = y0 + 0.7 + k * 0.75
        with g.em(xr + 0.8, yy, z, 0):
            bicicleta(g, ('plastico_preto', 'plastico_branco', 'plastico_azul')[k % 3])


def moveis(g):
    academia_moveis(g)
    salao_moveis(g)
    churrasqueira_moveis(g)
    lounges_moveis(g)
    piscina_moveis(g)
    playground_moveis(g)
    pet_moveis(g)
    bike_moveis(g)


# ------------------------------------------------------------------ canteiros do lazer
def paisagem_lazer(g):
    rnd = random.Random(33)
    for r, esp in (((2192, 1724, 2245, 1742), 'touceira_roxa'), ((2250, 1730, 2306, 1752), 'touceira_roxa'),
                   ((2020, 1662, 2104, 1676), 'touceira_verde'), ((2310, 1470, 2328, 1600), 'touceira_verde'),
                   ((1612, 1520, 1754, 1534), 'touceira_verde'), ((2187, 1642, 2200, 1700), 'touceira_clara')):
        x0, x1, y0, y1 = RM(r)
        canteiro(g, rnd, x0, x1, y0, y1, esp, alt=0.55, passo=0.6)
    # plantas altas atras das poltronas do wine lounge (como na perspectiva WIN)
    for px, py in ((2200, 1650), (2300, 1648), (2305, 1700)):
        arbusto(g, rnd, X(px), Y(py), 0.75, 'verde_clara')

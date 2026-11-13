# park_ambientes.py -- posicoes do mobiliario de cada ambiente do lazer do Village Park (pecas em park_moveis.py)
# e as palmeiras/canteiros do lazer. Posicoes em px da implantacao (P), lidas nos desenhos dos moveis da propria
# implantacao; o estilo de cada sala segue as perspectivas da galeria (assets/img/village-park/galeria).
# Executado por park_modelo.py dentro do Blender.


def P(px, py):
    return X(px), Y(py)


def _em(g, px, py, z=None, giro=0.0, esc=1.0):
    x, y = P(px, py)
    return g.em(x, y, Z_PISO if z is None else z, giro, esc)


def mesa_4(g, px, py, z=None, cad='estofada', r=0.5, tampo='madeira', giro=0.0):
    """Mesa redonda com 4 cadeiras."""
    with _em(g, px, py, z, giro):
        g.sombra(-1.25, 1.25, -1.25, 1.25, 0.008, disco=True)
        mesa_redonda(g, r, 0.76, tampo, 'madeira')
        for a in (45, 135, 225, 315):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            with g.em(c * (r + 0.26), s * (r + 0.26), 0, a + 180):
                if cad == 'estofada':
                    cadeira_estofada(g)
                else:
                    cadeira_concha(g, cad, 'madeira_clara')
        utensilios(g, 0.2, 0.1, 0.76)


def mesa_longa(g, px, py, comp, z=None, giro=0.0, cad='estofada', n=3):
    """Mesa retangular de jantar (eixo x) com n cadeiras de cada lado."""
    with _em(g, px, py, z, giro):
        g.sombra(-comp / 2 - 0.5, comp / 2 + 0.5, -1.1, 1.1, 0.008)
        mesa_quadrada(g, comp, 0.95, 0.76, 'madeira', 'madeira_escura')
        for k in range(n):
            xx = -comp / 2 + comp * (k + 0.5) / n
            for s in (-1, 1):
                with g.em(xx, s * 0.72, 0, -90 * s):
                    if cad == 'estofada':
                        cadeira_estofada(g)
                    elif cad == 'banco':
                        pass
                    else:
                        cadeira_concha(g, cad, 'metal_preto')
        if cad == 'banco':
            for s in (-1, 1):
                g.caixa(-comp / 2 + 0.1, comp / 2 - 0.1, s * 0.75 - 0.18, s * 0.75 + 0.18, 0.42, 0.47, 'madeira')
                for xx in (-comp / 2 + 0.3, comp / 2 - 0.3):
                    g.caixa(xx - 0.03, xx + 0.03, s * 0.75 - 0.15, s * 0.75 + 0.15, 0, 0.42, 'metal_preto')
        utensilios(g, comp * 0.25, 0.15, 0.76)
        utensilios(g, -comp * 0.25, -0.15, 0.76)


# ------------------------------------------------------------------ bloco de salas
def salao_moveis(g):
    z = Z_PISO
    x0 = X(PL.SALAO_X[0]) + E_PAREDE
    yN = Y(PL.BLOCO_LAZER[1]) - E_PAREDE
    # copa: bancada na parede oeste, geladeira inox, ilha com banquetas
    g.caixa(x0, x0 + 0.62, Y(1326), yN - 0.8, z, z + 0.9, 'plastico_branco', topo='pedra_granito')
    g.caixa(x0, x0 + 0.72, yN - 0.78, yN, z, z + 1.85, 'inox')
    g.painel(x0 + 0.721, yN - 0.05, x0 + 0.721, yN - 0.74, z + 0.02, z + 1.83, 'atlas', ATL['geladeira_inox'])
    prateleira(g, x0, x0 + 0.3, Y(1322), Y(1300), z + 1.7, 'madeira')
    g.caixa(X(1071), X(1080), Y(1325), Y(1295), z, z + 0.92, 'madeira_clara', topo='pedra_granito')
    for k in range(3):
        with _em(g, 1085, 1300 + k * 9, z, 180):
            banqueta(g, 'tecido_bege', 'metal_preto', 0.68)
    # mesa comprida e mesas redondas (13-salao-festas)
    mesa_longa(g, 1110, 1309, 2.4, n=3)
    for px, py in ((1148, 1308), (1178, 1308), (1125, 1349), (1148, 1374), (1178, 1374)):
        mesa_4(g, px, py)
    # estar com sofa, tapete organico e TV na parede terracota
    xE = X(PL.SALAO_X[1]) - E_PAREDE
    with _em(g, 1193, 1347, z, 90):
        g.sombra(-1.4, 1.4, -0.55, 0.55, 0.01)
        sofa(g, 2.4, 0.85, 'tecido_bege')
    g.elipsoide(X(1180), Y(1347), z + 0.005, 1.25, 1.6, 0.01, 'tecido_escuro', seg=20, aneis=2, zmin=0.0)
    with _em(g, 1180, 1347, z):
        mesa_redonda(g, 0.42, 0.38, 'madeira_escura', 'madeira_escura')
        vaso_planta(g, 0, 0, 0.38, 0.07, 0.04, 0.3, folha='folha_verde_clara')
    for px, py in ((1172, 1338), (1172, 1357)):
        with _em(g, px, py, z, 0):
            poltrona(g, 'tecido_terracota', 'madeira_escura')
    tv(g, xE - 0.05, Y(1312), z + 1.6, 180, 1.3, 0.74, 'tv_show')
    g.caixa(xE - 0.45, xE, Y(1318), Y(1306), z + 0.5, z + 0.56, 'madeira')
    vaso_planta(g, xE - 0.4, yN - 0.4, z, 0.26, 0.5, 1.5)
    vaso_planta(g, X(1094) + 0.4, Y(1386) + 0.3, z, 0.22, 0.45, 1.3)
    # WC: 2 sanitarios e bancada com cuba
    wx0, wx1, wy0, wy1 = RM(PL.SALAO_WC)
    ym = (wy0 + wy1) / 2
    for by in (ym + 1.3, ym - 1.3):
        vaso_sanitario(g, wx0 + E_PAREDE + 0.5, by, z, 0)
        g.caixa(wx1 - 0.62, wx1 - 0.12, by - 0.5, by + 0.5, z, z + 0.85, 'plastico_branco', topo='pedra_granito')
        g.painel(wx1 - 0.105, by - 0.45, wx1 - 0.105, by + 0.45, z + 1.1, z + 1.9, 'espelho', (0, 0, 1, 1))


def brinq_moveis(g):
    z = Z_PISO
    x0, x1 = X(PL.BRINQ_X[0]) + E_PAREDE, X(PL.BRINQ_X[1]) - E_PAREDE
    y0, y1 = Y(PL.BLOCO_LAZER[3]) + E_PAREDE, Y(PL.BLOCO_LAZER[1]) - E_PAREDE
    tatame(g, x0 + 0.3, x1 - 0.3, Y(1335), Y(1300), z + 0.012)
    with _em(g, 1240, 1318, z, 200):
        g.sombra(-0.95, 0.95, -0.95, 0.95, 0.018)
        cabana(g)
    for px, py, tec in ((1212, 1306, 'tecido_terracota'), (1214, 1322, 'tecido_verde'), (1226, 1330, 'tecido_bege')):
        g.elipsoide(X(px), Y(py), z + 0.14, 0.42, 0.38, 0.13, tec, seg=10, aneis=4, exp=0.6)
    # mesinha com cadeirinhas (19-brinquedoteca)
    for px, py in ((1217, 1360), (1238, 1376)):
        with _em(g, px, py, z):
            g.sombra(-0.75, 0.75, -0.75, 0.75, 0.012, disco=True)
            mesa_redonda(g, 0.38, 0.5, 'plastico_branco', 'madeira_clara', larga=False)
            for k, mt in enumerate(('plastico_vermelho', 'plastico_amarelo', 'plastico_azulc', 'plastico_verde')):
                a = k * 90 + 30
                c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
                with g.em(c * 0.55, s * 0.55, 0, a + 180, 0.62):
                    cadeira_concha(g, mt, 'madeira_clara')
    # estante alta de madeira na parede leste, nichos baixos na oeste, mural e lousa
    g.caixa(x1 - 0.4, x1, Y(1350), Y(1338), z, z + 2.2, 'madeira_clara')
    for k in range(4):
        prateleira(g, x1 - 0.4, x1, Y(1350), Y(1338), z + 0.45 + k * 0.45, 'madeira')
    g.caixa(x0, x0 + 0.4, Y(1388), Y(1350), z, z + 0.62, 'plastico_branco', topo='madeira_clara')
    g.painel(x0 + 0.401, Y(1388) + 0.05, x0 + 0.401, Y(1350) - 0.05, z + 0.06, z + 0.58, 'atlas', ATL['produtos'])
    g.painel(x1 - 0.012, y0 + 0.2, x1 - 0.012, Y(1352), z + 1.0, z + 2.0, 'atlas', ATL['lousa'])
    g.painel(x0 + 0.012, Y(1345), x0 + 0.012, y1 - 0.2, z + 1.65, z + 2.95, 'atlas', ATL['mural_brinq'])
    tv(g, x0 + 0.01, Y(1318), z + 1.3, 0, 1.0, 0.56, 'tv_kids')
    vaso_planta(g, x1 - 0.35, y1 - 0.35, z, 0.22, 0.45, 1.3)


def academia_moveis(g):
    z = Z_PISO
    x0, x1 = X(PL.ACADEMIA_X[0]) + E_PAREDE, X(PL.ACADEMIA_X[1]) - E_PAREDE
    y0, y1 = Y(PL.BLOCO_LAZER[3]) + E_PAREDE, Y(PL.BLOCO_LAZER[1]) - E_PAREDE
    for py in (1347, 1364, 1381):
        with _em(g, 1272, py, z, 0):
            g.sombra(-1.1, 1.0, -0.55, 0.55, 0.01)
            esteira(g)
    for py in (1306, 1326):
        with _em(g, 1349, py, z + 0.006, 180):
            g.sombra(-0.7, 0.7, -0.35, 0.35, 0.01)
            bike(g)
    for py in (1312, 1324):
        with _em(g, 1272, py, z, 0):
            g.sombra(-0.75, 0.75, -0.4, 0.4, 0.01)
            banco_supino(g)
    with _em(g, 1312, 1294, z + 0.006, -90):
        g.sombra(-0.35, 0.35, -0.75, 0.75, 0.01)
        rack_halteres(g)
    with _em(g, 1345, 1352, z + 0.006, 180):
        g.sombra(-1.1, 0.4, -1.1, 1.1, 0.01)
        estacao_cross(g)
    g.piso(X(1307), X(1325), Y(1383), Y(1347), z + 0.012, 'ep_vermelho')
    g.elipsoide(X(1312), Y(1388), z + 0.32, 0.32, 0.32, 0.32, 'plastico_amarelo', seg=14, aneis=8)
    g.elipsoide(X(1316), Y(1318), z + 0.28, 0.27, 0.27, 0.27, 'tecido_bege', seg=14, aneis=8)
    for px, py in ((1320, 1340), (1300, 1336)):
        halter(g, X(px), Y(py), z + 0.006)
    # espelho com LED na parede oeste, mural no sul, TV no leste
    g.painel(x0 + 0.015, y0 + 0.6, x0 + 0.015, y1 - 0.6, z + 0.45, z + 2.25, 'atlas', ATL['espelho_gym'])
    g.painel(x1 - 1.2, y0 + 0.012, x0 + 4.0, y0 + 0.012, z + 1.75, z + 2.75, 'atlas', ATL['mural_gym'])
    tv(g, x1 - 0.05, Y(1330), z + 1.85, 180, 1.1, 0.62, 'tv_treino')
    g.caixa(x1 - 0.35, x1, y1 - 0.8, y1 - 0.45, z, z + 1.1, 'inox')


def pub_moveis(g):
    z = Z_PISO
    x0, x1 = X(PL.FIM_X[0]) + E_PAREDE, X(PL.FIM_XM) - E_PAREDE
    y0, y1 = Y(PL.FIM_YM) + E_PAREDE, Y(PL.BLOCO_LAZER[1]) - E_PAREDE
    with _em(g, 1389, 1316, z):
        g.sombra(-1.2, 1.2, -1.2, 1.2, 0.008, disco=True)
        mesa_redonda(g, 0.6, 0.76, 'tecido_verde_esc', 'madeira_preta')
        for a in (20, 110, 200, 290):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            with g.em(c * 0.88, s * 0.88, 0, a + 180):
                cadeira_concha(g, 'plastico_marrom', 'metal_preto', 'tecido_escuro')
    # sofa grafite na parede leste com puffs verdes (18-pub-jogos)
    with g.em(x1 - 0.43, (y0 + y1) / 2, z, 90):
        g.sombra(-1.3, 1.3, -0.55, 0.55, 0.01)
        sofa(g, 2.6, 0.85, 'tecido_escuro')
    for px, py in ((1400, 1300), (1402, 1332)):
        with _em(g, px, py, z):
            puff(g, 'tecido_verde_esc')
    # aparador com TV na parede oeste e placa do pub no norte
    g.caixa(x0, x0 + 0.45, y0 + 0.4, y1 - 0.8, z, z + 0.75, 'madeira_preta')
    tv(g, x0 + 0.02, (y0 + y1) / 2, z + 1.6, 0, 1.3, 0.74, 'tv_show')
    g.painel(x0 + 0.6, y1 - 0.012, x0 + 1.6, y1 - 0.012, z + 1.5, z + 2.3, 'atlas', ATL['placa_pub'])
    vaso_planta(g, x0 + 0.35, y1 - 0.4, z, 0.24, 0.45, 1.4)


def mercado_moveis(g):
    z = Z_PISO
    x0, x1 = X(PL.FIM_XM) + E_PAREDE, X(PL.FIM_X[1]) - E_PAREDE
    y0, y1 = Y(PL.FIM_YM) + E_PAREDE, Y(PL.BLOCO_LAZER[1]) - E_PAREDE
    estante_mercado(g, x0 + 0.3, x1 - 1.6, y0, y0 + 0.4, z, 'produtos', False)
    for k in range(2):
        yy = y0 + 0.4 + k * 0.78
        g.caixa(x1 - 0.7, x1, yy, yy + 0.72, z, z + 2.0, 'metal_preto')
        g.painel(x1 - 0.701, yy + 0.04, x1 - 0.701, yy + 0.68, z + 0.08, z + 1.92, 'atlas', ATL['geladeira'])
    with _em(g, 1438, 1318, z):
        g.sombra(-0.6, 0.6, -0.6, 0.6, 0.01, disco=True)
        mesa_redonda(g, 0.36, 1.05, 'madeira_clara', 'metal_preto', larga=False)
        for a in (0, 180):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            with g.em(c * 0.55, s * 0.55, 0):
                banqueta(g, 'madeira', 'metal_preto', 0.95)
    g.caixa(x0, x0 + 0.6, y1 - 1.6, y1 - 0.3, z, z + 0.95, 'madeira_clara', topo='pedra_granito')
    g.painel(x0 + 0.012, y0 + 0.6, x0 + 0.012, y1 - 1.8, z + 2.0, z + 2.6, 'atlas', ATL['placa_mercado'])


def beauty_moveis(g):
    z = Z_PISO
    x0, x1 = X(PL.FIM_X[0]) + E_PAREDE, X(PL.FIM_XM) - E_PAREDE
    y0, y1 = Y(PL.BLOCO_LAZER[3]) + E_PAREDE, Y(PL.FIM_YM) - E_PAREDE
    # bancada com 2 espelhos ovais iluminados (06-beauty) na parede norte
    g.caixa(x0 + 0.3, x0 + 2.4, y1 - 0.5, y1, z + 0.75, z + 0.8, 'plastico_branco')
    for k in range(2):
        xm = x0 + 0.8 + k * 1.1
        g.painel(xm - 0.3, y1 - 0.012, xm + 0.3, y1 - 0.012, z + 1.1, z + 2.1, 'espelho', (0, 0, 1, 1))
        g.caixa(xm - 0.34, xm + 0.34, y1 - 0.02, y1 - 0.01, z + 1.06, z + 2.14, 'luz_led')
        with g.em(xm, y1 - 0.85, z, 90):
            cadeira_beauty(g)
    with g.em(x1 - 0.55, (y0 + y1) / 2 - 0.2, z, 90):
        g.sombra(-1.1, 1.1, -0.5, 0.5, 0.01)
        maca(g)
    g.caixa(x0, x0 + 0.5, y0 + 0.3, y0 + 1.2, z, z + 0.85, 'plastico_branco', topo='pedra_granito')
    vaso_planta(g, x1 - 0.35, y1 - 0.35, z, 0.22, 0.45, 1.4)


def cowork_moveis(g):
    z = Z_PISO
    x0, x1 = X(PL.FIM_XM) + E_PAREDE, X(PL.FIM_X[1]) - E_PAREDE
    y0, y1 = Y(PL.BLOCO_LAZER[3]) + E_PAREDE, Y(PL.FIM_YM) - E_PAREDE
    # fundo verde de gravacao, tripe e ring light (10-cowork)
    g.caixa(x0 + 1.6, x1 - 0.1, y1 - 0.06, y1, z, z + 2.6, 'tela_verde')
    g.piso(x0 + 1.6, x1 - 0.1, y1 - 1.2, y1 - 0.06, z + 0.006, 'tela_verde')
    tx, ty = x0 + 2.6, y1 - 2.0
    for a in (90, 210, 330):
        g.tubo([(tx + 0.3 * math.cos(math.radians(a)), ty + 0.3 * math.sin(math.radians(a)), z), (tx, ty, z + 1.2)], 0.012, 'metal_preto', seg=4)
    g.tubo([(tx, ty, z + 1.2), (tx, ty, z + 1.55)], 0.015, 'metal_preto', seg=4)
    g.caixa(tx - 0.08, tx + 0.08, ty - 0.05, ty + 0.05, z + 1.55, z + 1.66, 'metal_preto')
    with g.em(x1 - 0.7, y1 - 1.9, z, 0):
        g.cil(0, 0, 0.012, 0, 1.6, 'metal_preto', seg=4)
        g.elipsoide(0, 0, 1.75, 0.25, 0.02, 0.25, 'luz_led', seg=14, aneis=3)
    # bancada de trabalho na parede oeste com 3 cadeiras verdes
    g.caixa(x0, x0 + 0.75, y0 + 0.3, y0 + 2.8, z + 0.72, z + 0.76, 'plastico_branco')
    for yy in (y0 + 0.4, y0 + 2.7):
        g.caixa(x0 + 0.05, x0 + 0.7, yy - 0.02, yy + 0.02, z, z + 0.72, 'metal_preto')
    for k in range(3):
        with g.em(x0 + 1.0, y0 + 0.75 + k * 0.8, z, 180):
            cadeira_concha(g, 'plastico_verde', 'metal_preto')
    g.painel(x0 + 0.012, y0 + 0.4, x0 + 0.012, y0 + 2.7, z + 1.2, z + 2.0, 'atlas', ATL['lousa'])
    for px, py in ((1462, 1385),):
        with _em(g, px, py, z):
            puff(g, 'tecido_terracota')


# ------------------------------------------------------------------ churrasqueiras, club, piscina
def churrasqueira_moveis(g, r_edif, decks):
    z = Z_PISO
    ex0, ex1, ey0, ey1 = RM(r_edif)
    xw = ex0 + (ex1 - ex0) * 0.36
    yc0 = ey0 + (ey1 - ey0) * 0.35
    yc1 = ey0 + (ey1 - ey0) * 0.55
    xm = (xw + ex1) / 2
    for yg, s in ((yc1, 1), (yc0, -1)):
        # churrasqueira de alvenaria com coifa, bancada com cuba e mesa comunitaria com bancos (09-churrasqueira)
        g.caixa(ex1 - 1.25, ex1 - E_PAREDE, yg + s * 0.0, yg + s * 0.62, z, z + 0.9, 'int_branco', topo='pedra_granito')
        g.caixa(ex1 - 1.15, ex1 - 0.25, yg + s * 0.6, yg + s * 0.605, z + 0.95, z + 1.35, 'metal_preto')
        g.caixa(ex1 - 1.1, ex1 - 0.3, yg + s * 0.605, yg + s * 0.61, z + 1.0, z + 1.12, 'luz_led')
        g.caixa(ex1 - 1.25, ex1 - E_PAREDE, yg + s * 0.0, yg + s * 0.62, z + 1.9, z + 2.6, 'int_branco')
        g.caixa(xw + E_PAREDE, ex1 - 1.3, yg, yg + s * 0.58, z, z + 0.88, 'madeira_clara', topo='pedra_granito')
        prateleira(g, xw + 0.3, ex1 - 1.5, min(yg, yg + s * 0.25), max(yg, yg + s * 0.25), z + 1.7, 'madeira')
        yt = yg + s * ((ey1 - yc1) if s > 0 else (yc0 - ey0)) * 0.58
        x_, y_ = xm, yt
        with g.em(x_, y_, z, 0):
            g.sombra(-1.6, 1.6, -1.1, 1.1, 0.008)
            mesa_quadrada(g, 2.3, 0.9, 0.76, 'madeira', 'metal_preto')
            for s2 in (-1, 1):
                g.caixa(-1.1, 1.1, s2 * 0.75 - 0.18, s2 * 0.75 + 0.18, 0.42, 0.47, 'madeira')
                for xx in (-0.85, 0.85):
                    g.caixa(xx - 0.03, xx + 0.03, s2 * 0.75 - 0.15, s2 * 0.75 + 0.15, 0, 0.42, 'metal_preto')
            utensilios(g, 0.5, 0.15, 0.76)
            utensilios(g, -0.5, -0.15, 0.76)
    # WC
    for yy in (ey0 + 0.5, yc1 - 0.5):
        vaso_sanitario(g, ex0 + E_PAREDE + 0.5, yy, z, 0)
    # mesas nos decks
    for r in decks:
        a0, a1, b0, b1 = RM(r)
        n = 2
        comprido_y = (b1 - b0) > (a1 - a0)
        for k in range(n):
            t = (k + 0.5) / n
            x_ = (a0 + a1) / 2 if comprido_y else a0 + (a1 - a0) * t
            y_ = b0 + (b1 - b0) * t if comprido_y else (b0 + b1) / 2
            mesa_com_cadeiras(g, x_, y_, 15 * k, 'externa', 0.8, z=Z_MADEIRA)


def piscina_moveis(g):
    z = Z_DECK
    for px in (1248, 1298, 1310, 1355, 1367, 1412):
        with _em(g, px, 1040, z, 90):
            g.sombra(-1.1, 1.1, -0.45, 0.45, 0.012)
            espreguicadeira(g)
    for px in (1277, 1337, 1390):
        with _em(g, px, 1040, z):
            g.sombra(-1.6, 1.6, -1.6, 1.6, 0.012, disco=True)
            ombrelone(g)
    for px in (1373, 1388, 1403):                       # na prainha
        with _em(g, px, 946, 0.17, -90):
            espreguicadeira(g)
    for px, giro in ((1198, -60), (1385, 240)):
        with _em(g, px, 993, z, giro):
            g.sombra(-1.05, 1.05, -1.05, 1.05, 0.012, disco=True)
            bangalo(g)
    # ducha
    dx, dy = P(1450, 975)
    g.tubo([(dx, dy, z), (dx, dy, z + 2.2), (dx + 0.3, dy, z + 2.3)], 0.022, 'inox', seg=6)
    g.caixa(dx - 0.5, dx + 0.5, dy - 0.5, dy + 0.5, z, z + 0.02, 'ep_preto')


def club_moveis(g):
    z = 0.32
    for px in (1740, 1785):
        with _em(g, px, 1562, z, -90):
            g.sombra(-1.05, 1.05, -1.05, 1.05, 0.012, disco=True)
            bangalo(g)
    fx, fy = P(1762, 1577)
    g.cil(fx, fy, 0.45, z, z + 0.32, 'pedra_granito', seg=16)
    g.cil(fx, fy, 0.32, z + 0.32, z + 0.34, 'luz_led', seg=16)
    for px in (1825, 1840, 1855):
        with _em(g, px, 1663, 0.19, 90):
            espreguicadeira(g)
    for px in (1700, 1722):
        with _em(g, px, 1556, z, -90):
            g.sombra(-1.1, 1.1, -0.45, 0.45, 0.012)
            espreguicadeira(g)
    # salao gourmet (16 e 17-village-club): ilha, mesa redonda com cadeiras verdes, sofa e TV
    cx0, cx1, cy0, cy1 = RM(PL.CLUB_SALAO)
    zi = z
    g.caixa(X(1697), X(1712), Y(1650), Y(1638), zi, zi + 0.92, 'madeira_escura', topo='pedra_granito')
    g.caixa(cx0 + E_PAREDE, cx0 + 3.4, cy1 - 0.75, cy1 - E_PAREDE, zi, zi + 0.9, 'int_escuro', topo='pedra_granito')
    g.caixa(cx0 + 3.4, cx0 + 4.1, cy1 - 0.85, cy1 - E_PAREDE, zi, zi + 1.85, 'inox')
    mesa_4(g, 1762, 1633, z=zi, cad='plastico_verde', r=0.62)
    with g.em(X(1742), cy0 + E_PAREDE + 0.45, zi, 0):
        g.sombra(-1.3, 1.3, -0.55, 0.55, 0.01)
        sofa(g, 2.2, 0.85, 'tecido_bege')
    tv(g, cx1 - E_PAREDE - 0.05, Y(1660), zi + 1.6, 180, 1.2, 0.68, 'tv_show')
    vaso_sanitario(g, cx0 + E_PAREDE + 0.5, cy0 + 0.9, zi, 0)


# ------------------------------------------------------------------ areas abertas
def playground_moveis(g):
    z = Z_QUADRA - 0.035
    with _em(g, 1016, 1035, z, 90):
        g.sombra(-4.5, 4.5, -2.5, 2.5, 0.012)
        brinquedo(g)
    with _em(g, 1060, 1160, z, 180):
        g.sombra(-0.95, 0.95, -0.95, 0.95, 0.012)
        casinha(g)
    for px, py, mt in ((1060, 960, 'plastico_laranja'), (1062, 985, 'plastico_vermelho')):
        with _em(g, px, py, z):
            g.cil(0, 0, 0.1, 0, 0.3, 'metal_preto', seg=8, tampa=False)
            g.elipsoide(0, 0, 0.42, 0.42, 0.14, 0.14, mt, seg=10, aneis=5, exp=0.7)
    # amarelinha de hexagonos
    for k, (dx, dy) in enumerate(((0, 0), (1.0, 0), (0.5, 0.85), (1.5, 0.85), (2.0, 0), (1.0, 1.7))):
        cx, cy = P(1010, 1135)
        mt = ('plastico_vermelho', 'plastico_amarelo', 'plastico_verde')[k % 3]
        g.cil(cx + dx, cy + dy, 0.45, z, z + 0.006, mt, seg=6)


def crossfit_moveis(g):
    z = Z_QUADRA - 0.035
    with _em(g, 1555, 1320, z, 90):
        g.sombra(-1.3, 1.3, -0.8, 0.8, 0.01)
        gaiola_cross(g)
    with _em(g, 1595, 1345, z, 0):
        gaiola_cross(g)
    for px, py in ((1520, 1300), (1528, 1300)):
        x_, y_ = P(px, py)
        g.caixa(x_ - 0.3, x_ + 0.3, y_ - 0.25, y_ + 0.25, z, z + 0.6, 'madeira')
    for px, py in ((1585, 1295), (1592, 1300)):
        x_, y_ = P(px, py)
        g.elipsoide(x_, y_, z + 0.12, 0.12, 0.12, 0.12, 'metal_preto', seg=8, aneis=5)


def pet_moveis(g):
    x0, x1, y0, y1 = RM(PL.PET)
    # circuito de agilidade (22-petplace): cones e barra, rampa, tunel
    for k, py in enumerate((1505, 1530, 1555)):
        cor = ('plastico_azulc', 'plastico_amarelo', 'plastico_vermelho')[k]
        px0, px1 = X(630), X(660)
        yy = Y(py)
        for xx in (px0, px1):
            g.cil(xx, yy, 0.12, 0, 0.4, cor, seg=8, r2=0.02)
        g.tubo([(px0, yy, 0.3), (px1, yy, 0.3)], 0.02, 'plastico_branco', seg=5)
    with _em(g, 700, 1600, 0.0, 20):
        g.tubo([(-0.9, 0, 0.32), (0.9, 0, 0.32)], 0.32, 'plastico_azulc', seg=10)
    with _em(g, 690, 1520, 0.0, -30):
        g.face([(-0.7, -0.25, 0), (0.0, -0.25, 0.42), (0.0, 0.25, 0.42), (-0.7, 0.25, 0)], 'plastico_laranja', uvs=[(0, 0)] * 4)
        g.face([(0.0, -0.25, 0.42), (0.7, -0.25, 0), (0.7, 0.25, 0), (0.0, 0.25, 0.42)], 'plastico_amarelo', uvs=[(0, 0)] * 4)
    for px in (720, 735):
        g.cil(X(px), Y(1505), 0.05, 0, 0.5, 'plastico_amarelo', seg=8)


def bikeshare_moveis(g):
    x0, x1, y0, y1 = RM(PL.BIKESHARE)
    n = int((y1 - y0 - 0.6) / 0.75)
    for k in range(n):
        yy = y0 + 0.6 + k * 0.75
        with g.em((x0 + x1) / 2 + 0.2, yy, 0.2, 0):
            bicicleta(g, ('plastico_vermelho', 'plastico_preto', 'plastico_azul')[k % 3])
        g.tubo([(x0 + 0.5, yy + 0.35, 0.2), (x0 + 0.5, yy + 0.35, 0.95), (x0 + 0.9, yy + 0.35, 0.95), (x0 + 0.9, yy + 0.35, 0.2)],
               0.025, 'inox', seg=5)


def decks_moveis(g):
    z = Z_MADEIRA
    for px, py in ((1092, 1248), (1160, 1248)):
        with _em(g, px, py, z, 0):
            g.sombra(-1.2, 1.2, -1.0, 1.0, 0.01)
            mesa_piquenique(g)
    with _em(g, 1495, 1069, z, 0):
        g.sombra(-1.2, 1.2, -1.0, 1.0, 0.01)
        mesa_piquenique(g)
    x_, y_ = P(1331, 1248)
    g.caixa(x_ - 0.25, x_ + 0.25, y_ - 0.9, y_ + 0.9, z, z + 0.45, 'madeira')


def moveis(g):
    salao_moveis(g)
    brinq_moveis(g)
    academia_moveis(g)
    pub_moveis(g)
    mercado_moveis(g)
    beauty_moveis(g)
    cowork_moveis(g)
    churrasqueira_moveis(g, PL.CHURRASQUEIRA_T1, PL.DECKS_T1)
    churrasqueira_moveis(g, PL.CHURRASQUEIRA_T2, PL.DECKS_T2)
    piscina_moveis(g)
    club_moveis(g)
    playground_moveis(g)
    crossfit_moveis(g)
    pet_moveis(g)
    bikeshare_moveis(g)
    decks_moveis(g)


# ------------------------------------------------------------------ palmeiras e canteiros do lazer
def paisagem_lazer(g):
    rnd = random.Random(33)
    for px, py in PL.PALMEIRAS:
        palmeira(g, rnd, X(px) + rnd.uniform(-0.15, 0.15), Y(py) + rnd.uniform(-0.15, 0.15), rnd.uniform(0.6, 0.78))
    # floreiras da piscina (amarelas no topo, folhagem na do meio)
    for r, esp in ((PL.FLOREIRA_TOPO_PISCINA, 'flores_laranja'), (PL.FLOREIRA_PISCINA, 'touceira_clara')):
        x0, x1, y0, y1 = RM(r)
        with g.em(0, 0, Z_DECK + 0.45 - 0.14):
            canteiro(g, rnd, x0 + 0.2, x1 - 0.2, y0 + 0.2, y1 - 0.2, esp, alt=0.5, passo=0.55, solo=False)
    # canteiros floridos entre a quadra e o bloco (roxo e verde, como na implantacao)
    for r, esp in (((1193, 1235, 1227, 1262), 'touceira_roxa'), ((1283, 1240, 1320, 1262), 'touceira_verde'),
                   ((1100, 1213, 1340, 1228), 'touceira_verde')):
        x0, x1, y0, y1 = RM(r)
        canteiro(g, rnd, x0, x1, y0, y1, esp, alt=0.55, passo=0.6, solo=False)

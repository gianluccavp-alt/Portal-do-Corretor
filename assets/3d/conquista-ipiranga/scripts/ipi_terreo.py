# ipi_terreo.py -- espacos de uso comum no terreo das torres, no lugar do final 12 (implantacao, legenda 03, 04,
# 14 e 16): T1 espaco happy hour, T2 coworking e espaco reels, T3 brinquedoteca, T4 mini market.
# A implantacao desenha cada sala vista de cima, mobiliada: um L entre div06 e g06 (do corredor ate o recuo do
# garden) mais o bloco saliente (b06..g06) ate a fachada. A frente do bloco e a lateral voltada para o recuo do hall
# sao de vidro (ipi_modelo._parede_terreo); aqui ficam piso, paredes internas, forro, spots e moveis, no objeto
# 'moveis' (a pagina acende a noite). Estilo de cada sala pelas perspectivas 05, 07, 08 e 09 da galeria.
#
# Quadro da sala: o quadrante -x -y da torre girado 180 graus, que e o mesmo que espelhar os dois eixos. Assim as
# medidas de Q valem com sinal positivo: x cresce do nucleo para a ponta, y do corredor para a fachada (+y = rua).
# Executado por ipi_modelo.py dentro do Blender.

ZF = 0.13                 # piso acabado (= piso do hall)
ZC = PD - 0.12            # forro
Y_CORR = 0.75             # parede do corredor central (implantacao: 16 px do eixo)
E_INT = 0.06


def materiais_terreo():
    for nome, cor in (('verde', '#9aa77e'), ('verde_kids', '#a9cf8f'), ('marinho', '#2c4466'), ('gelo', '#e2e3e1'),
                      ('creme', '#efe8d8')):
        mat('int_' + nome, cor, 0.85)
    mat('piso_terreo', '#dcd9d2', 0.35, img='porcelanato.jpg', tint=True, img_mean=0.87, uv=1.2)
    mat('piso_madeira_terreo', '#ffffff', 0.45, img='madeira_piso.jpg', uv=1.6)
    mat('vidro_lazer_sala', '#c6d8e0', 0.05, blend=0.14, metal=0.1)       # vidro_lazer*: a cena nao projeta sombra
    mat('rodape', '#b5b1a8', 0.7)
    mat('corda', '#c9a46e', 0.8)


def _sala():
    q = Q
    return q['g06'], q['b06'], q['div06'], Y_CORR, q['y_fundo'], q['y_fachada']


def casca(g, parede, fundo=None, piso='piso_terreo', forro='int_branco'):
    """Piso, paredes internas nas arestas sem vidro, rodape, forro e spots. Devolve as medidas da sala."""
    gx, bx, dx, yc, yF, yS = _sala()
    fundo = fundo or parede
    g.piso(gx, dx, yc, yF, ZF, piso)
    g.piso(gx, bx, yF, yS, ZF, piso)
    E = E_INT
    for (x0, x1, y0, y1, mt) in ((gx, dx, yc, yc + E, fundo), (dx - E, dx, yc, yF, parede), (bx, dx, yF - E, yF, parede),
                                 (bx - E, bx, yF, yS, parede), (gx, gx + E, yc, yF, parede)):
        g.caixa(x0, x1, y0, y1, ZF, ZC, mt)
        g.caixa(x0 - 0.01, x1 + 0.01, y0 - 0.01, y1 + 0.01, ZF, ZF + 0.08, 'rodape')
    g.caixa(gx, dx, yc, yF, ZC, ZC + 0.02, forro, sem_fundo=False)
    g.caixa(gx, bx, yF, yS, ZC, ZC + 0.02, forro, sem_fundo=False)
    for xx, yy in ((gx + 1.2, yc + 1.2), (gx + 3.0, yc + 1.2), ((bx + dx) / 2, yc + 1.4), (gx + 1.2, yF - 0.6),
                   ((bx + dx) / 2, yF - 1.2), ((gx + bx) / 2, (yF + yS) / 2)):
        g.caixa(xx - 0.15, xx + 0.15, yy - 0.15, yy + 0.15, ZC - 0.01, ZC, 'luz_led', sem_fundo=False)
    return gx, bx, dx, yc, yF, yS


# ------------------------------------------------------------------ T1 espaco happy hour (07)
def happy_hour(g):
    gx, bx, dx, yc, yF, yS = casca(g, 'int_branco', 'int_marinho')
    z = ZF
    # bancada da cozinha na parede do fundo (azul), com pia, prateleira e plantas
    g.caixa(gx + 0.1, gx + 2.4, yc + E_INT, yc + 0.65, z, z + 0.9, 'int_marinho', topo='pedra_granito')
    g.caixa(gx + 0.9, gx + 1.4, yc + 0.2, yc + 0.55, z + 0.88, z + 0.91, 'inox')
    g.tubo([(gx + 1.15, yc + 0.12, z + 0.9), (gx + 1.15, yc + 0.12, z + 1.2), (gx + 1.15, yc + 0.32, z + 1.22)], 0.012, 'cromo', seg=5)
    prateleira(g, gx + 0.2, gx + 2.3, yc + E_INT, yc + 0.32, z + 1.6, 'madeira')
    for k, mt in enumerate(('vidro_escuro', 'ceramica', 'madeira', 'plastico_branco', 'vidro_escuro')):
        g.cil(gx + 0.4 + k * 0.42, yc + 0.2, 0.05, z + 1.6, z + 1.8, mt, seg=8)
    vaso_planta(g, gx + 2.1, yc + 0.22, z + 1.6, 0.1, 0.14, 0.45)
    # balcao do bar em azul com tampo de granito e 3 banquetas pretas
    yb = 3.1
    g.caixa(gx + 0.15, gx + 2.2, yb - 0.3, yb + 0.25, z, z + 1.0, 'int_marinho')
    g.caixa(gx + 0.1, gx + 2.25, yb - 0.35, yb + 0.35, z + 1.0, z + 1.05, 'pedra_granito')
    for k in range(3):
        with g.em(gx + 0.55 + k * 0.6, yb + 0.7, z):
            banqueta(g, 'metal_preto', 'metal_preto', 0.75)
    utensilios(g, gx + 1.0, yb, z + 1.05)
    for k in range(3):                                   # pendentes de cupula preta sobre o balcao
        xx = gx + 0.55 + k * 0.6
        g.tubo([(xx, yb, ZC), (xx, yb, ZC - 0.75)], 0.004, 'fio_preto', seg=3)
        g.cil(xx, yb, 0.2, ZC - 0.95, ZC - 0.75, 'metal_preto', seg=12, r2=0.04, tampa=False)
        g.cil(xx, yb, 0.12, ZC - 0.955, ZC - 0.95, 'luz_led', seg=10, tampa=False, base=True)
    # mesas bistro de madeira com cadeiras de madeira e banquetas
    for xx, yy, n in ((dx - 1.6, 2.1, 2), (dx - 2.3, 3.6, 2), (dx - 0.85, 3.4, 2)):
        with g.em(xx, yy, z):
            g.sombra(-0.7, 0.7, -0.7, 0.7, 0.008, disco=True)
            mesa_redonda(g, 0.33, 0.75, 'madeira', 'metal_preto', larga=False)
            for a in range(n):
                ang = 30 + a * 180
                c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
                with g.em(c * 0.55, s * 0.55, 0, ang + 180):
                    cadeira_concha(g, 'madeira_escura', 'madeira_escura')
    with g.em(gx + 0.9, (yF + yS) / 2, z):                # mesa alta no bloco da frente
        mesa_redonda(g, 0.3, 1.02, 'madeira', 'metal_preto', larga=False)
        for a in (0, 180):
            with g.em(0.5 * math.cos(math.radians(a)), 0.5 * math.sin(math.radians(a)), 0):
                banqueta(g, 'metal_preto', 'metal_preto', 0.72)
    # sofa cinza encostado no recuo do garden e TV na parede da ponta
    with g.em((bx + dx) / 2, yF - 0.5, z, 180):
        g.sombra(-1.0, 1.0, -0.5, 0.5, 0.008)
        sofa(g, 1.8, 0.85, 'tecido_cinza', almofadas=False)
    tv(g, dx - E_INT - 0.02, 2.6, z + 1.6, 180, 1.1, 0.62, 'tv_show')
    g.caixa(bx - 0.45, bx - E_INT, yF + 0.1, yS - 0.4, z, z + 0.8, 'madeira')          # aparador
    vaso_planta(g, bx - 0.3, yS - 0.3, z, 0.18, 0.4, 1.0)


# ------------------------------------------------------------------ T2 coworking e espaco reels (09)
def coworking(g):
    gx, bx, dx, yc, yF, yS = casca(g, 'int_branco', 'int_verde')
    z = ZF
    g.caixa(dx - E_INT - 0.005, dx - E_INT, yc + 0.1, yF - 0.1, z + 0.08, ZC, 'int_verde')
    # bancada comprida de madeira na parede do nucleo com 4 cadeiras cantilever, notebooks e luminarias
    g.caixa(gx + E_INT, gx + 0.66, yc + 0.2, yF - 0.6, z + 0.73, z + 0.77, 'madeira', sem_fundo=False)
    for yy in (yc + 0.25, yF - 0.65):
        g.caixa(gx + E_INT, gx + 0.66, yy - 0.025, yy + 0.025, z, z + 0.73, 'metal_preto')
    for k in range(4):
        yy = yc + 0.65 + k * 0.8
        with g.em(gx + 1.05, yy, z, 180):
            cadeira_concha(g, 'plastico_preto', 'cromo')
        g.caixa(gx + 0.25, gx + 0.5, yy - 0.17, yy + 0.17, z + 0.77, z + 0.785, 'metal_preto')
        g.painel(gx + 0.25, yy - 0.16, gx + 0.25, yy + 0.16, z + 0.79, z + 1.0, 'tela', ATL['tv_podcast'])
    # espaco reels: mesa de podcast com 2 cadeiras, microfones, ring light, tapete e a cortina de cordas
    g.caixa(bx + 0.2, dx - 0.4, yc + 0.6, yc + 2.6, z, z + 0.01, 'tecido_cinza')
    xm, ym = (bx + dx) / 2 + 0.15, yc + 1.5
    with g.em(xm, ym, z, 90):
        mesa_quadrada(g, 1.2, 0.7, 0.75, 'madeira', 'metal_preto')
        for sy in (-1, 1):
            with g.em(0, sy * 0.65, 0, -90 * sy):
                cadeira_estofada(g, 'tecido_escuro', 'metal_preto')
            g.tubo([(0.0, sy * 0.2, 0.75), (0.0, sy * 0.2, 0.95), (0.0, sy * 0.3, 1.05)], 0.01, 'metal_preto', seg=4)
            g.elipsoide(0.0, sy * 0.32, 1.07, 0.03, 0.03, 0.05, 'metal_preto', seg=6, aneis=3)
    rx, ry = bx - 0.1, yc + 2.4
    for a in (90, 210, 330):
        g.tubo([(rx, ry, z + 1.0), (rx + 0.35 * math.cos(math.radians(a)), ry + 0.35 * math.sin(math.radians(a)), z)], 0.01, 'metal_preto', seg=4)
    g.tubo([(rx, ry, z + 1.0), (rx, ry, z + 1.55)], 0.012, 'metal_preto', seg=4)
    g.tubo([(rx + 0.16 * math.cos(2 * math.pi * k / 14), ry, z + 1.72 + 0.16 * math.sin(2 * math.pi * k / 14)) for k in range(15)], 0.018, 'luz_led', seg=4)
    xc = bx - 0.6
    for k in range(26):                                   # cortina de cordas separando o espaco reels
        yy = yc + 0.4 + k * 0.09
        g.tubo([(xc, yy, ZC), (xc + 0.02 * ((k % 3) - 1), yy, z + 0.02)], 0.008, 'corda', seg=3)
    g.caixa(xc - 0.03, xc + 0.03, yc + 0.35, yc + 0.4 + 26 * 0.09, ZC - 0.05, ZC, 'madeira')
    # poltrona de madeira, mesinha lateral, planta, quadro e relogio
    with g.em(dx - 0.6, yF - 0.75, z, 200):
        poltrona(g, 'tecido_terracota', 'madeira')
    with g.em(dx - 0.55, yF - 0.2, z):
        mesa_redonda(g, 0.25, 0.5, 'madeira', 'madeira', larga=False)
    vaso_planta(g, gx + 0.4, yF - 0.3, z, 0.2, 0.45, 1.2)
    g.painel(dx - E_INT - 0.012, yc + 3.4, dx - E_INT - 0.012, yc + 2.6, z + 1.3, z + 2.0, 'atlas', ATL['quadro'])
    g.cil(gx + 2.2, yc + E_INT + 0.01, 0.17, z + 1.9, z + 1.92, 'plastico_verde', seg=16)
    # balcao de cafe junto a fachada
    g.caixa(bx - 0.5, bx - E_INT, yF + 0.2, yS - 0.35, z, z + 0.95, 'madeira')
    g.caixa(bx - 0.4, bx - 0.15, yF + 0.5, yF + 0.8, z + 0.95, z + 1.25, 'metal_preto')


# ------------------------------------------------------------------ T3 brinquedoteca (05)
def brinquedoteca(g):
    gx, bx, dx, yc, yF, yS = casca(g, 'int_creme', piso='piso_madeira_terreo')
    z = ZF
    E = E_INT + 0.004
    for (x0, x1, y0, y1) in ((gx, dx, yc, yc + E), (dx - E, dx, yc, yF), (bx, dx, yF - E, yF), (bx - E, bx, yF, yS),
                             (gx, gx + E, yc, yF)):
        g.caixa(x0, x1, y0, y1, z + 0.08, z + 1.2, 'int_verde_kids')          # barrado verde (perspectiva)
    # painel de madeira em forma de casinha com a TV, na parede do fundo
    xt = gx + 2.6
    g.caixa(xt - 0.8, xt + 0.8, yc + E, yc + E + 0.04, z + 1.0, z + 2.0, 'madeira_clara')
    g.face([(xt - 0.85, yc + E + 0.041, z + 2.0), (xt + 0.85, yc + E + 0.041, z + 2.0), (xt, yc + E + 0.041, z + 2.45)][::-1], 'madeira_clara')
    tv(g, xt, yc + E + 0.05, z + 1.5, 90, 0.9, 0.52, 'tv_kids')
    g.caixa(xt - 0.9, xt + 0.9, yc + E, yc + 0.45, z + 0.85, z + 0.9, 'madeira_clara', sem_fundo=False)
    # caixotes de brinquedo, futon e almofadas no fundo
    for k, xx in enumerate((gx + 0.5, gx + 1.05)):
        g.caixa(xx - 0.25, xx + 0.25, yc + 0.15, yc + 0.55, z, z + 0.4, 'madeira_clara')
        g.cil(xx, yc + 0.35, 0.1, z + 0.4, z + 0.5, ('plastico_vermelho', 'plastico_azulc')[k], seg=8)
    g.caixa_red(gx + 3.4, gx + 4.6, yc + 0.15, yc + 0.85, z, z + 0.14, 0.05, 'plastico_laranja', passos=2)
    for k, mt in enumerate(('tecido_terracota', 'tecido_bege', 'tecido_verde')):
        g.elipsoide(gx + 3.6 + k * 0.4, yc + 0.25, z + 0.35, 0.18, 0.08, 0.18, mt, seg=8, aneis=4, exp=0.6)
    # tapete laranja redondo, cabana e brinquedos de chao
    rx, ry = dx - 1.6, 3.0
    g.cil(rx, ry, 1.0, z, z + 0.012, 'plastico_laranja', seg=28)
    with g.em(dx - 0.9, yF - 0.9, z + 0.012, 225):
        g.sombra(-0.95, 0.95, -0.95, 0.95, 0.018)
        cabana(g)
    for k, mt in enumerate(('plastico_amarelo', 'plastico_azulc', 'plastico_vermelho', 'plastico_verde')):
        g.caixa(rx - 0.4 + k * 0.22, rx - 0.3 + k * 0.22, ry - 0.2, ry - 0.1, z + 0.012, z + 0.11, mt)
    # mesinha branca com as cadeirinhas coloridas
    with g.em(gx + 1.9, 2.4, z, 0):
        g.sombra(-0.8, 0.8, -0.7, 0.7, 0.008)
        mesa_quadrada(g, 0.9, 0.6, 0.55, 'plastico_branco', 'madeira_clara')
        for k, (cx, cy, a, mt) in enumerate(((0.62, 0, 180, 'plastico_amarelo'), (-0.62, 0, 0, 'plastico_azulc'),
                                             (0.2, 0.5, -90, 'plastico_branco'), (-0.2, -0.5, 90, 'plastico_laranja'))):
            with g.em(cx, cy, 0, a, 0.7):
                cadeira_concha(g, mt, 'madeira_clara')
    # amarelinha no piso do bloco da frente, lousa de casinha e prateleiras
    cores = ('plastico_amarelo', 'plastico_azulc', 'plastico_vermelho', 'plastico_verde', 'plastico_laranja')
    for k in range(6):
        yy = yF + 0.15 + k * 0.3
        for j in ((0,) if k % 2 == 0 else (-1, 1)):
            xx = gx + 1.4 + j * 0.16
            g.caixa(xx - 0.14, xx + 0.14, yy, yy + 0.27, z, z + 0.004, cores[(k + j) % 5])
    g.painel(dx - E - 0.012, yc + 3.6, dx - E - 0.012, yc + 2.9, z + 0.3, z + 1.5, 'atlas', ATL['lousa'])
    for zz in (z + 1.45, z + 1.8):
        prateleira(g, bx + 0.3, bx + 1.1, yc + E, yc + 0.25, zz, 'madeira_clara')
    g.caixa(bx - 0.45, bx - E_INT, yF + 0.15, yS - 0.3, z, z + 0.45, 'plastico_azul', topo='madeira_clara')     # banco baú


# ------------------------------------------------------------------ T4 mini market (08)
def _carrinho(g):
    for k in range(5):
        zz = 0.55 + k * 0.08
        g.tubo([(-0.25, -0.18, zz), (0.25, -0.18, zz), (0.25, 0.18, zz), (-0.25, 0.18, zz), (-0.25, -0.18, zz)], 0.006, 'metal_preto', seg=4)
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.tubo([(sx * 0.22, sy * 0.16, 0.06), (sx * 0.25, sy * 0.18, 0.88)], 0.01, 'metal_preto', seg=4)
            g.cil(sx * 0.22, sy * 0.16, 0.035, 0.0, 0.07, 'plastico_preto', seg=6)
    g.caixa(-0.22, 0.22, -0.16, 0.16, 0.2, 0.22, 'metal_preto')
    g.tubo([(-0.3, -0.2, 0.95), (-0.3, 0.2, 0.95)], 0.015, 'plastico_preto', seg=6)


def mini_market(g):
    gx, bx, dx, yc, yF, yS = casca(g, 'int_gelo', 'int_creme')
    z = ZF
    # geladeiras pretas de porta de vidro na parede da ponta (frente para o nucleo)
    for k in range(3):
        yy = yc + 0.75 + k * 0.82
        g.caixa(dx - 0.7, dx - E_INT, yy - 0.39, yy + 0.39, z, z + 2.05, 'metal_preto')
        g.painel(dx - 0.701, yy + 0.37, dx - 0.701, yy - 0.37, z + 0.32, z + 1.98, 'tela', ATL['geladeira'])
    # prateleiras de madeira com mercadorias: parede do fundo (frente para a fachada) e parede do nucleo
    estante_mercado(g, gx + 1.0, dx - 1.0, yc + E_INT, yc + 0.4, z, 'produtos', False)
    with g.em(gx + E_INT + 0.2, (yc + yF) / 2 + 0.2, z, -90):
        estante_mercado(g, -1.5, 1.5, -0.2, 0.2, 0, 'produtos', False)
    g.painel((gx + dx) / 2 + 0.9, yc + E_INT + 0.004, (gx + dx) / 2 - 0.9, yc + E_INT + 0.004, ZC - 0.45, ZC - 0.1, 'atlas', ATL['placa_mercado'])
    # balcao baixo de produtos e o totem de autoatendimento no bloco da frente
    g.caixa(bx - 0.5, bx - E_INT, yF + 0.1, yS - 0.4, z, z + 0.9, 'madeira')
    g.painel(bx - 0.501, yS - 0.45, bx - 0.501, yF + 0.15, z + 0.1, z + 0.85, 'atlas', ATL['produtos'])
    g.caixa(gx + 0.3, gx + 0.7, yS - 0.9, yS - 0.55, z, z + 1.05, 'plastico_branco')
    g.painel(gx + 0.31, yS - 0.549, gx + 0.69, yS - 0.549, z + 1.0, z + 1.35, 'tela', ATL['menu'])
    with g.em((gx + dx) / 2 + 0.3, 3.3, z, 25):
        g.sombra(-0.35, 0.35, -0.3, 0.3, 0.008)
        _carrinho(g)


SALAS = {1: happy_hour, 2: coworking, 3: brinquedoteca, 4: mini_market}


def salas_terreo(g):
    for t, (cxp, cyp, ang) in sorted(PL.TORRES.items()):
        with g.em(X(cxp), Y(cyp), 0.0, -ang), g.em(0.0, 0.0, 0.0, 180.0):
            SALAS[t](g)

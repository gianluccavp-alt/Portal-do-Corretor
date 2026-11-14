# avm_terreo.py -- espacos de uso comum no terreo das torres do Alta Vista Mangara, no lugar dos finais 1 e 8.
# Implantacao (legenda): T1 = 23 brinquedoteca (lado -x do hall) e 24 mini market (faixa central);
# T2 = 21 coworking/espaco influencer e 22 espaco pilates, nas mesmas posicoes. O hall de entrada ocupa a
# saliencia (X_C..X_B1) entre as duas salas; o lado +x (lugar do final 1) e fechado.
# Coordenadas locais da torre (as do quadrante -x/-y de avm_modelo.quadrante), montadas dentro de g.em(torre).
# Estilo de cada sala pelas perspectivas da galeria (cowork, espaco-pilates, brinquedoteca, mini-mercado).
# Fachada de vidro: avm_modelo._terreo_loja. Interior (paredes int_*, piso, forro, moveis): objeto 'moveis', que a
# pagina acende a noite. Executado por avm_modelo.py dentro do Blender.

ZF = 0.15                 # piso acabado das salas do terreo
ZC = PD - 0.18            # forro (fundo da laje da varanda do 1o pavimento)
Y_FUNDO = -1.15           # parede do corredor central
E_INT = 0.07
# salas (x0, x1, y0 = vidro, y1 = fundo)
SALA_A = (-X_DIV0, -X_B1 - 0.12, -(Y_FACE - 0.08), Y_FUNDO)       # brinquedoteca / coworking
HALL = (-X_B1, -X_C, -(Y_BUMP - 0.04), Y_FUNDO)
SALA_B = (-X_C, -0.10, -(Y_FACE - 0.04), Y_FUNDO)                  # mini market / pilates


def materiais_terreo():
    for nome, cor in (('verde', '#8fa27a'), ('rosa', '#d6a394'), ('lilas', '#c9c7d8'), ('marinho', '#22385f'),
                      ('gelo', '#dfe0e0')):
        mat('int_' + nome, cor, 0.85)
    mat('piso_terreo', '#d9d6cf', 0.35, img='porcelanato.jpg', tint=True, img_mean=0.87, uv=1.2)
    mat('piso_madeira_terreo', '#ffffff', 0.45, img='madeira_piso.jpg', uv=1.6)


def _casca(g, sala, piso, fundo, esq, dir_, forro='int_branco'):
    """Piso, tres paredes internas (o lado y0 e o vidro), forro e trilho de spots."""
    x0, x1, y0, y1 = sala
    g.piso(x0, x1, y0, y1, ZF, piso)
    g.caixa(x0, x1, y1 - E_INT, y1, ZF, ZC, fundo)
    g.caixa(x0, x0 + E_INT, y0, y1 - E_INT, ZF, ZC, esq)
    g.caixa(x1 - E_INT, x1, y0, y1 - E_INT, ZF, ZC, dir_)
    for xa, xb, ya, yb in ((x0, x0 + E_INT, y0, y1), (x1 - E_INT, x1, y0, y1), (x0, x1, y1 - E_INT, y1)):
        g.caixa(xa, xb, ya, yb, ZF, ZF + 0.08, 'rodape')
    g.caixa(x0, x1, y0, y1, ZC - 0.02, ZC, forro, sem_fundo=False)
    # trilho preto com spots no meio da sala, ao longo da profundidade
    xm = (x0 + x1) / 2
    g.caixa(xm - 0.02, xm + 0.02, y0 + 0.5, y1 - 0.4, ZC - 0.06, ZC - 0.02, 'metal_preto', sem_fundo=False)
    yy = y0 + 0.8
    while yy < y1 - 0.5:
        g.cil(xm, yy, 0.045, ZC - 0.22, ZC - 0.06, 'metal_preto', seg=8, base=True)
        g.cil(xm, yy, 0.035, ZC - 0.225, ZC - 0.22, 'luz_led', seg=8, tampa=False, base=True)
        yy += 0.9
    return x0 + E_INT, x1 - E_INT, y0, y1 - E_INT


def _bola(g, x, y, z, r, mt):
    g.elipsoide(x, y, z + r, r, r, r, mt, seg=10, aneis=6)


# ------------------------------------------------------------------ 21 coworking (T2)
def coworking(g):
    x0, x1, y0, y1 = _casca(g, SALA_A, 'piso_terreo', 'int_grafite', 'int_gelo', 'int_verde')
    z = ZF
    # bancada de trabalho na parede do fundo, com notebooks e cadeiras
    g.caixa(x0 + 0.2, x1 - 0.9, y1 - 0.62, y1, z + 0.72, z + 0.76, 'madeira', sem_fundo=False)
    for xx in (x0 + 0.25, x1 - 0.95):
        g.caixa(xx, xx + 0.05, y1 - 0.6, y1, z, z + 0.72, 'metal_preto')
    for k in range(3):
        xx = x0 + 0.75 + k * 0.85
        with g.em(xx, y1 - 0.95, z, 90):
            cadeira_estofada(g, 'tecido_cinza', 'metal_preto')
        g.caixa(xx - 0.17, xx + 0.17, y1 - 0.45, y1 - 0.2, z + 0.76, z + 0.775, 'metal_preto')
        g.painel(xx - 0.16, y1 - 0.2, xx + 0.16, y1 - 0.2, z + 0.78, z + 0.99, 'tela', ATL['tv_podcast'])
    g.painel(x1 - 1.9, y1 - 0.012, x1 - 1.0, y1 - 0.012, z + 1.25, z + 2.0, 'atlas', ATL['quadro'])
    # estantes de madeira com ripado na parede da esquerda, cafeteira e plantas
    g.caixa(x0, x0 + 0.06, y0 + 1.6, y1 - 0.8, z, ZC, 'ripado_madeira')
    for k in range(3):
        prateleira(g, x0 + 0.06, x0 + 0.36, y0 + 1.7, y1 - 0.9, z + 0.55 + k * 0.6, 'madeira')
    g.caixa(x0 + 0.1, x0 + 0.32, y0 + 2.1, y0 + 2.4, z + 1.15, z + 1.45, 'plastico_branco')
    vaso_planta(g, x0 + 0.2, y1 - 1.3, z + 1.75, 0.1, 0.16, 0.5)
    vaso_planta(g, x0 + 0.35, y0 + 0.45, z, 0.22, 0.45, 1.3)
    # duas mesas redondas altas com pufes e um sofa bege encostado na parede verde
    for xx, yy in ((x0 + 1.25, y0 + 1.25), (x0 + 1.8, y0 + 2.6)):
        with g.em(xx, yy, z):
            g.sombra(-0.75, 0.75, -0.75, 0.75, 0.008, disco=True)
            mesa_redonda(g, 0.42, 0.76, 'madeira', 'metal_preto', larga=False)
            g.caixa(-0.15, 0.15, -0.1, 0.12, 0.76, 0.775, 'cromo')
            for a in (200, 20):
                with g.em(0.62 * math.cos(math.radians(a)), 0.62 * math.sin(math.radians(a)), 0):
                    puff(g, 'tecido_escuro', 0.22, 0.44)
    with g.em(x1 - 0.45, y0 + 1.8, z, 90):
        g.sombra(-0.9, 0.9, -0.5, 0.5, 0.008)
        sofa(g, 1.6, 0.85, 'tecido_bege', almofadas=False)
    # arandela preta na parede verde
    g.caixa(x1 - 0.02, x1, y0 + 1.8 - 0.03, y0 + 1.8 + 0.03, z + 1.6, z + 2.1, 'metal_preto')
    g.cil(x1 - 0.18, y0 + 1.8, 0.09, z + 1.55, z + 1.7, 'metal_preto', seg=10, r2=0.04)


# ------------------------------------------------------------------ 22 espaco pilates (T2)
def _reformer(g):
    """Reformer de madeira ao longo de y (cabeceira em +y)."""
    for sx in (-1, 1):
        g.caixa(sx * 0.33 - 0.05, sx * 0.33 + 0.05, -1.15, 1.15, 0.08, 0.36, 'madeira_clara')
    for yy in (-1.1, 1.1):
        g.caixa(-0.38, 0.38, yy - 0.05, yy + 0.05, 0.0, 0.38, 'madeira_clara')
    g.caixa_red(-0.3, 0.3, -0.2, 0.75, 0.36, 0.45, 0.04, 'ep_preto', passos=2)      # carro
    g.caixa(-0.3, 0.3, 0.85, 0.95, 0.36, 0.62, 'ep_preto')                          # ombreiras
    g.tubo([(-0.32, -0.95, 0.36), (-0.32, -0.95, 0.85), (0.32, -0.95, 0.85), (0.32, -0.95, 0.36)], 0.018, 'cromo', seg=6)
    for sx in (-1, 1):
        g.caixa(sx * 0.33 - 0.03, sx * 0.33 + 0.03, -1.12, -1.06, 0.38, 1.25, 'madeira_clara')


def _chair_pilates(g):
    g.caixa_red(-0.3, 0.3, -0.28, 0.28, 0.0, 0.55, 0.06, 'madeira_clara', passos=2)
    g.caixa_red(-0.31, 0.31, -0.29, 0.29, 0.55, 0.62, 0.03, 'ep_preto', passos=2)
    for sx in (-1, 1):
        g.tubo([(sx * 0.24, -0.26, 0.55), (sx * 0.24, -0.26, 1.15)], 0.015, 'cromo', seg=6)
        g.cil(sx * 0.24, -0.26, 0.03, 1.08, 1.2, 'ep_preto', seg=8)


def _barrel(g):
    g.caixa(-0.35, 0.35, -0.3, 0.3, 0.0, 0.62, 'madeira_clara')
    g.elipsoide(0, 0.05, 0.62, 0.34, 0.28, 0.32, 'ep_preto', seg=12, aneis=6, zmin=0.0)
    for k in range(6):
        yy = -0.45 - 0.0
        g.caixa(-0.32, 0.32, -0.75, -0.7, 0.12 + k * 0.17, 0.15 + k * 0.17, 'madeira_clara')
    for sx in (-1, 1):
        g.caixa(sx * 0.33 - 0.03, sx * 0.33 + 0.03, -0.76, -0.68, 0.0, 1.1, 'madeira_clara')


def pilates(g):
    x0, x1, y0, y1 = _casca(g, SALA_B, 'piso_madeira_terreo', 'int_verde', 'int_verde', 'int_gelo')
    z = ZF
    # espaldar e estante com bolas e kettlebells na parede do fundo
    for k, xa in enumerate((x0 + 0.25, x0 + 1.05)):
        for xx in (xa, xa + 0.7):
            g.caixa(xx - 0.03, xx + 0.03, y1 - 0.12, y1 - 0.04, z, z + 2.15, 'madeira_clara')
        r = 0
        while r < 13:
            g.cil(xa + 0.35, y1 - 0.08, 0.016, z + 0.15 + r * 0.155, z + 0.17 + r * 0.155, 'madeira_clara', seg=6)
            g.caixa(xa, xa + 0.7, y1 - 0.095, y1 - 0.065, z + 0.15 + r * 0.155, z + 0.175 + r * 0.155, 'madeira_clara')
            r += 1
    ex0 = x0 + 1.95
    g.caixa(ex0, x1 - 0.05, y1 - 0.38, y1, z, z + 0.05, 'madeira')
    for k in range(4):
        prateleira(g, ex0, x1 - 0.05, y1 - 0.38, y1, z + 0.5 + k * 0.5, 'madeira')
    for sx in (ex0, x1 - 0.08):
        g.caixa(sx, sx + 0.03, y1 - 0.38, y1, z, z + 2.05, 'madeira')
    for k in range(3):
        _bola(g, ex0 + 0.18 + k * 0.28, y1 - 0.2, z + 2.0, 0.12, 'plastico_preto')
        g.cil(ex0 + 0.18 + k * 0.28, y1 - 0.2, 0.07, z + 1.0, z + 1.18, 'metal_preto', seg=8)
        g.cil(ex0 + 0.2 + k * 0.28, y1 - 0.2, 0.06, z + 0.5, z + 0.56, 'inox', seg=10)
    # bolas suicas soltas
    _bola(g, x1 - 0.4, y1 - 0.75, z, 0.32, 'plastico_branco')
    _bola(g, x1 - 0.95, y1 - 0.6, z, 0.3, 'tecido_escuro')
    # espelho na parede da esquerda e quadros na da direita
    g.caixa(x0, x0 + 0.02, y0 + 0.6, y1 - 0.5, z + 0.25, z + 2.05, 'espelho', sem_fundo=False)
    g.painel(x1 - 0.012, y0 + 1.0, x1 - 0.012, y0 + 1.6, z + 1.2, z + 2.0, 'atlas', ATL['quadro'])
    # reformer, chair e ladder barrel
    with g.em((x0 + x1) / 2 - 0.15, y1 - 1.6, z, 90):
        g.sombra(-0.5, 0.5, -1.3, 1.3, 0.008)
        _reformer(g)
    with g.em(x0 + 0.7, y0 + 0.9, z, 160):
        g.sombra(-0.45, 0.45, -0.45, 0.45, 0.008)
        _chair_pilates(g)
    with g.em(x1 - 0.65, y0 + 2.6, z, 90):
        g.sombra(-0.5, 0.5, -0.9, 0.5, 0.008)
        _barrel(g)


# ------------------------------------------------------------------ 23 brinquedoteca (T1)
def brinquedoteca(g):
    x0, x1, y0, y1 = _casca(g, SALA_A, 'piso_madeira_terreo', 'int_lilas', 'int_lilas', 'int_rosa')
    z = ZF
    # parede do fundo meio rosa, mural da arvore e lousa em forma de casinha
    g.caixa((x0 + x1) / 2 + 0.3, x1, y1 - 0.012, y1, z + 0.08, ZC - 0.02, 'int_rosa')
    g.painel(x0 + 0.3, y1 - 0.013, x0 + 1.9, y1 - 0.013, z + 0.6, z + 2.2, 'atlas', ATL['mural_brinq'])
    g.painel(x0 + 2.0, y1 - 0.013, x0 + 2.8, y1 - 0.013, z + 0.35, z + 1.25, 'atlas', ATL['lousa'])
    # painel de madeira com TV e prateleira baixa na parede da esquerda
    g.caixa(x0, x0 + 0.05, y0 + 1.6, y1 - 0.4, z, z + 2.2, 'madeira_clara')
    tv(g, x0 + 0.06, y0 + 2.6, z + 1.45, 0, 0.95, 0.55, 'tv_kids')
    g.caixa(x0 + 0.05, x0 + 0.45, y0 + 1.7, y1 - 0.5, z + 0.75, z + 0.8, 'madeira_clara', sem_fundo=False)
    g.caixa(x0 + 0.05, x0 + 0.45, y0 + 1.7, y0 + 3.1, z, z + 0.4, 'plastico_branco', topo='madeira_clara')
    g.painel(x0 + 0.451, y0 + 3.05, x0 + 0.451, y0 + 1.75, z + 0.04, z + 0.38, 'atlas', ATL['produtos'])
    # cabana, mesinha com cadeirinhas e pufe laranja
    with g.em(x1 - 0.95, y1 - 0.95, z, 225):
        g.sombra(-0.95, 0.95, -0.95, 0.95, 0.018)
        cabana(g)
    with g.em((x0 + x1) / 2 - 0.1, y1 - 1.6, z):
        g.sombra(-0.7, 0.7, -0.7, 0.7, 0.012, disco=True)
        mesa_redonda(g, 0.36, 0.5, 'madeira_clara', 'madeira_clara', larga=False)
        for k in range(4):
            a = k * 90 + 45
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            with g.em(c * 0.5, s * 0.5, 0, a + 180, 0.6):
                cadeira_estofada(g, 'tecido_xadrez', 'madeira_clara')
    with g.em(x1 - 1.1, y0 + 2.0, z):
        puff(g, 'tecido_terracota', 0.38, 0.38)
    # piscina de bolinhas junto ao vidro
    bx0, bx1, by0, by1 = x0 + 0.3, x0 + 2.0, y0 + 0.25, y0 + 1.25
    g.caixa(bx0, bx1, by0, by1, z, z + 0.42, 'plastico_azulc', topo='plastico_azulc')
    g.caixa(bx0 + 0.08, bx1 - 0.08, by0 + 0.08, by1 - 0.08, z + 0.42, z + 0.43, 'plastico_azul')
    rnd = random.Random(23)
    cores = ('plastico_amarelo', 'plastico_branco', 'plastico_laranja', 'tecido_cinza')
    for k in range(70):
        xx = rnd.uniform(bx0 + 0.13, bx1 - 0.13)
        yy = rnd.uniform(by0 + 0.13, by1 - 0.13)
        g.elipsoide(xx, yy, z + 0.43 + rnd.uniform(0.0, 0.04), 0.045, 0.045, 0.045, cores[k % 4], seg=6, aneis=4)
    # almofadas de estrela (no piso, perto da cabana)
    for xx, yy in ((x1 - 1.9, y1 - 0.5), (x1 - 0.3, y1 - 2.0)):
        g.cil(xx, yy, 0.16, z, z + 0.05, 'plastico_amarelo', seg=5)


# ------------------------------------------------------------------ 24 mini market (T1)
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
    g.caixa(-0.18, 0.12, -0.12, 0.12, 0.58, 0.82, 'plastico_laranja')


def mini_market(g):
    x0, x1, y0, y1 = _casca(g, SALA_B, 'piso_terreo', 'int_marinho', 'int_gelo', 'int_gelo')
    z = ZF
    # forro marinho sobre as geladeiras (como na perspectiva) e lambri de madeira na parede da esquerda
    g.caixa(x0 + 1.4, x1, y0, y1, ZC - 0.025, ZC - 0.02, 'int_marinho', sem_fundo=False)
    g.caixa(x0, x0 + 0.04, y0, y1, z, ZC - 0.02, 'madeira_clara')
    # estantes: no fundo (frente para o vidro) e na parede da esquerda (frente para +x)
    estante_mercado(g, x0 + 0.1, x1 - 1.4, y1 - 0.36, y1, z, 'produtos', True)
    with g.em(x0 + 0.22, y0 + 2.2, z, 90):
        estante_mercado(g, -1.0, 1.0, -0.18, 0.18, 0, 'produtos', True)
    g.painel(x1 - 1.35, y1 - 0.004, x1 - 0.1, y1 - 0.004, z + 1.1, z + 1.9, 'atlas', ATL['placa_mercado'])
    # geladeiras pretas de porta de vidro na parede da direita (frente para -x)
    for k in range(2):
        yy = y0 + 1.25 + k * 0.78
        g.caixa(x1 - 0.68, x1, yy - 0.37, yy + 0.37, z, z + 2.05, 'metal_preto')
        g.painel(x1 - 0.681, yy + 0.35, x1 - 0.681, yy - 0.35, z + 0.32, z + 1.98, 'tela', ATL['geladeira'])
    # totem de autoatendimento junto ao vidro e carrinho
    g.caixa(x1 - 0.5, x1 - 0.1, y0 + 0.3, y0 + 0.65, z, z + 1.05, 'plastico_branco')
    g.painel(x1 - 0.48, y0 + 0.29, x1 - 0.12, y0 + 0.29, z + 1.0, z + 1.35, 'tela', ATL['menu'])
    with g.em((x0 + x1) / 2 - 0.2, y0 + 1.1, z, 30):
        g.sombra(-0.35, 0.35, -0.3, 0.3, 0.008)
        _carrinho(g)


# ------------------------------------------------------------------ hall de entrada
def hall(g):
    x0, x1, y0, y1 = _casca(g, HALL, 'piso_terreo', 'ripado_hall', 'int_branco', 'int_bege')
    z = ZF
    # caixas de correio na parede da direita, banco e planta
    g.caixa(x1 - 0.3, x1, y1 - 2.4, y1 - 0.6, z + 0.9, z + 1.9, 'madeira_clara')
    for k in range(5):
        g.caixa(x1 - 0.305, x1 - 0.3, y1 - 2.4, y1 - 0.6, z + 0.9 + k * 0.2, z + 0.91 + k * 0.2, 'metal_preto')
    g.caixa(x0, x0 + 0.42, y0 + 1.2, y0 + 2.6, z + 0.42, z + 0.47, 'madeira', sem_fundo=False)
    g.caixa(x0, x0 + 0.42, y0 + 1.2, y0 + 2.6, z, z + 0.42, 'int_grafite')
    vaso_planta(g, x0 + 0.3, y0 + 0.5, z, 0.24, 0.5, 1.4)
    g.painel(x0 + 0.012, y0 + 2.9, x0 + 0.012, y0 + 3.7, z + 1.2, z + 1.9, 'atlas', ATL['quadro'])


def salas_terreo(g):
    for t, (cxp, cyp) in sorted(PL.TORRES.items()):
        with g.em(X(cxp), Y(cyp), 0.0, 0.0):
            hall(g)
            if t == 1:
                brinquedoteca(g)
                mini_market(g)
            else:
                coworking(g)
                pilates(g)

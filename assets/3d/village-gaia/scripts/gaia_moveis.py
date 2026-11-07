# gaia_moveis.py -- mobiliario e equipamentos de cada ambiente, seguindo as perspectivas do book (galeria 04 a 25)
# e as posicoes da implantacao. Cada movel e montado em coordenadas locais (origem no centro, base em z=0).
# Sem marcas de terceiros: paineis, produtos e telas sao genericos (atlas em gaia_tex.py).


def materiais_moveis():
    M_ = dict(img='madeira_fina.jpg', tint=True, img_mean=0.8, uv=(0.9, 0.3))
    mat('madeira', '#b98c5c', 0.55, **M_)
    mat('madeira_clara', '#d3b288', 0.55, **M_)
    mat('madeira_escura', '#6b4a30', 0.55, **M_)
    mat('madeira_preta', '#242120', 0.5, **M_)
    mat('ripado_madeira', '#b89668', 0.6, img='ripado.jpg', tint=True, img_mean=0.82, uv=(0.5, 3.0))
    mat('ripado_claro', '#d8cdb9', 0.6, img='ripado.jpg', tint=True, img_mean=0.82, uv=(0.5, 3.0))
    T_ = dict(img='tecido.jpg', tint=True, img_mean=0.84, uv=0.25)
    for nome, cor in (('azul', '#2c4a7c'), ('cinza', '#a7a8a6'), ('terracota', '#b5532c'), ('bege', '#d9cfba'), ('verde', '#6d8a4c'), ('verde_esc', '#566b33'),
                      ('escuro', '#4b4a48'), ('xadrez', '#b56b78'), ('branco', '#ece8e0')):
        mat('tecido_' + nome, cor, 0.95, **T_)
    for nome, cor in (('preto', '#1d1e21'), ('azul', '#2f4d68'), ('branco', '#ececea'), ('vermelho', '#cf3a2c'), ('amarelo', '#f0b82f'), ('verde', '#3ea33e'),
                      ('azulc', '#3f7fd6'), ('laranja', '#e8752a'), ('marrom', '#7a4a2a')):
        mat('plastico_' + nome, cor, 0.38)
    mat('metal_preto', '#17181a', 0.42, metal=0.55)
    mat('metal_ouro', '#b89a5c', 0.3, metal=0.8)
    mat('inox', '#b9bdc1', 0.28, metal=0.85)
    mat('espelho', '#ccd6dc', 0.04, metal=1.0)
    mat('luz_led', '#ffe9c0', 0.5)
    mat('pedra_granito', '#c5bfb2', 0.35, img='emborrachado.jpg', tint=True, uv=0.7)
    mat('azulejo', '#ece7dc', 0.2, img='porcelanato.jpg', tint=True, img_mean=0.87, uv=0.9)
    mat('rattan', '#9b7a50', 0.8, img='ripado.jpg', tint=True, img_mean=0.82, uv=(0.2, 0.2))
    mat('ombrelone', '#e7dcc4', 0.85)
    mat('ep_preto', '#27282a', 0.9, img='emborrachado.jpg', tint=True, uv=1.0)
    mat('tela_verde', '#42b02f', 0.8)
    mat('truck_amarelo', '#dca226', 0.32, metal=0.3)
    mat('truck_branco', '#ece9df', 0.35)
    mat('cromo', '#d6d8da', 0.15, metal=0.95)
    mat('vidro_escuro', '#1f2830', 0.08, metal=0.3)
    mat('ceramica', '#b6a892', 0.8)


# ------------------------------------------------------------------ assentos e mesas
def _pernas(g, xs, ys, h, r, mt, seg=5, abre=0.0):
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.tubo([(sx * xs, sy * ys, h), (sx * (xs + abre), sy * (ys + abre), 0)], r, mt, seg=seg)


def cadeira_concha(g, cor='plastico_preto', perna='metal_preto', estofado=None):
    """Cadeira de refeicao: concha com encosto curvo (06-gourmet, 15-churrasqueira). Frente em +x."""
    _pernas(g, 0.19, 0.19, 0.44, 0.012, perna, abre=0.03)
    g.caixa_red(-0.22, 0.22, -0.22, 0.22, 0.44, 0.47, 0.07, cor, passos=2)
    if estofado:
        g.caixa_red(-0.19, 0.2, -0.19, 0.19, 0.47, 0.495, 0.06, estofado, passos=2)
    # encosto em arco
    arco = []
    for k in range(7):
        a = math.radians(115 + 130 * k / 6)
        arco.append((0.24 * math.cos(a) - 0.02, 0.24 * math.sin(a)))
    for i in range(6):
        (x0, y0), (x1, y1) = arco[i], arco[i + 1]
        for z0, z1, inc0, inc1 in ((0.47, 0.84, 0.0, -0.05),):
            n = _unit2((x0 + x1) / 2, (y0 + y1) / 2)
            g.face([(x1, y1, z0), (x0, y0, z0), (x0 + inc1, y0, z1), (x1 + inc1, y1, z1)], cor, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], nrm=[(n[0], n[1], 0)] * 4)
            g.face([(x0, y0, z0), (x1, y1, z0), (x1 + inc1, y1, z1), (x0 + inc1, y0, z1)], cor, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], nrm=[(-n[0], -n[1], 0)] * 4)
            g.face([(x0 + inc1, y0, z1), (x1 + inc1, y1, z1), (x1 + inc1 - 0.01, y1, z1 + 0.012), (x0 + inc1 - 0.01, y0, z1 + 0.012)], cor, uvs=[(0, 0)] * 4)


def _unit2(x, y):
    l = math.hypot(x, y) or 1
    return x / l, y / l


def cadeira_estofada(g, tec='tecido_cinza', perna='madeira_clara'):
    """Cadeira do salao: pes de madeira, assento e encosto estofados arredondados."""
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.tubo([(sx * 0.18, sy * 0.18, 0.44), (sx * 0.22, sy * 0.22, 0)], 0.018, perna, seg=6)
    g.elipsoide(0, 0, 0.47, 0.25, 0.25, 0.055, tec, seg=10, aneis=4, exp=0.55)
    g.tubo([(-0.2, -0.18, 0.46), (-0.26, -0.2, 0.86)], 0.016, perna, seg=5)
    g.tubo([(-0.2, 0.18, 0.46), (-0.26, 0.2, 0.86)], 0.016, perna, seg=5)
    g.elipsoide(-0.26, 0, 0.8, 0.05, 0.27, 0.13, tec, seg=10, aneis=4, exp=0.7)


def cadeira_externa(g):
    """Cadeira de varanda em aluminio com tela (05-foodtruck, 15-churrasqueira)."""
    M = 'metal_preto'
    for sy in (-1, 1):
        g.tubo([(0.22, sy * 0.22, 0), (0.22, sy * 0.22, 0.44), (-0.22, sy * 0.22, 0.44), (-0.28, sy * 0.22, 0.88)], 0.012, M, seg=4)
        g.tubo([(-0.22, sy * 0.22, 0), (-0.22, sy * 0.22, 0.44)], 0.012, M, seg=4)
    g.caixa(-0.22, 0.22, -0.22, 0.22, 0.42, 0.45, 'tecido_escuro')
    g.face([(-0.22, -0.22, 0.45), (-0.22, 0.22, 0.45), (-0.28, 0.22, 0.88), (-0.28, -0.22, 0.88)], 'tecido_escuro', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    g.face([(-0.22, 0.22, 0.45), (-0.22, -0.22, 0.45), (-0.28, -0.22, 0.88), (-0.28, 0.22, 0.88)], 'tecido_escuro', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])


def banqueta(g, assento='plastico_vermelho', perna='metal_preto', h=0.72):
    for a in (45, 135, 225, 315):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        g.tubo([(0.1 * c, 0.1 * s, h), (0.17 * c, 0.17 * s, 0)], 0.012, perna, seg=4)
    g.cil(0, 0, 0.17, h, h + 0.05, assento, seg=12)


def puff(g, tec='tecido_terracota', r=0.26, h=0.42):
    g.cil(0, 0, r, 0, h - 0.04, tec, seg=16, tampa=False)
    g.elipsoide(0, 0, h - 0.04, r, r, 0.05, tec, seg=16, aneis=3, zmin=0.0)


def mesa_quadrada(g, l=0.8, p=0.8, h=0.75, tampo='madeira', perna='metal_preto', central=False):
    g.caixa(-l / 2, l / 2, -p / 2, p / 2, h - 0.03, h, tampo)
    if central:
        g.cil(0, 0, 0.04, 0, h - 0.03, perna, seg=8, tampa=False)
        g.cil(0, 0, 0.26, 0, 0.02, perna, seg=14)
    else:
        for sx in (-1, 1):
            for sy in (-1, 1):
                g.caixa(sx * (l / 2 - 0.05) - 0.022, sx * (l / 2 - 0.05) + 0.022, sy * (p / 2 - 0.05) - 0.022, sy * (p / 2 - 0.05) + 0.022, 0, h - 0.03, perna)


def mesa_redonda(g, r=0.65, h=0.75, tampo='madeira', perna='madeira', larga=True):
    g.cil(0, 0, r, h - 0.03, h, tampo, seg=24)
    if larga:
        g.cil(0, 0, 0.2, 0, h - 0.03, perna, seg=12, r2=0.15, tampa=False)
    else:
        g.cil(0, 0, 0.035, 0, h - 0.03, perna, seg=8, tampa=False)
        g.cil(0, 0, 0.26, 0, 0.02, perna, seg=14)


def mesa_com_cadeiras(g, x, y, giro=0, tipo='preta', l=0.85):
    """Mesa com 4 cadeiras (px ja convertido)."""
    with g.em(x, y, Z_PISO, giro):
        g.sombra(-1.1, 1.1, -1.1, 1.1, 0.008, disco=True)
        if tipo == 'preta':
            mesa_quadrada(g, l, l, 0.75, 'madeira', 'metal_preto')
            cad = lambda: cadeira_concha(g, 'plastico_preto', 'metal_preto', 'madeira_escura')
        else:
            mesa_quadrada(g, l, l, 0.75, 'madeira_escura', 'metal_preto')
            cad = lambda: cadeira_externa(g)
        for a in (0, 90, 180, 270):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            with g.em(c * (l / 2 + 0.22), s * (l / 2 + 0.22), 0, a + 180):
                cad()
        utensilios(g, 0.18, 0.1, 0.75)


def utensilios(g, x, y, z):
    g.cil(x, y, 0.11, z, z + 0.012, 'plastico_branco', seg=12)
    g.cil(-x, -y, 0.11, z, z + 0.012, 'plastico_branco', seg=12)
    g.cil(x * 0.2, -y, 0.03, z, z + 0.16, 'vidro_escuro', seg=8, r2=0.022)


def sofa(g, c=2.0, p=0.85, tec='tecido_azul', almofadas=True):
    """Sofa com encosto em -y (frente em +y)."""
    h = 0.42
    g.caixa_red(-c / 2, c / 2, -p / 2, p / 2, 0.06, h, 0.07, tec, passos=2)
    g.caixa_red(-c / 2, c / 2, -p / 2, -p / 2 + 0.2, h, 0.78, 0.07, tec, passos=2)
    for s in (-1, 1):
        g.caixa_red(s * c / 2 - 0.1, s * c / 2 + 0.1, -p / 2, p / 2, 0.06, 0.6, 0.07, tec, passos=2)
    n = max(1, round((c - 0.3) / 0.8))
    w = (c - 0.28) / n
    for k in range(n):
        x = -c / 2 + 0.14 + w * (k + 0.5)
        g.elipsoide(x, 0.06, h + 0.04, w / 2 - 0.01, p / 2 - 0.13, 0.07, tec, seg=10, aneis=4, exp=0.45)
        g.elipsoide(x, -p / 2 + 0.3, h + 0.2, w / 2 - 0.01, 0.1, 0.18, tec, seg=10, aneis=4, exp=0.55)
        if almofadas and k % 2 == 0:
            g.elipsoide(x + 0.2, -p / 2 + 0.42, h + 0.2, 0.2, 0.06, 0.2, 'tecido_bege' if tec == 'tecido_azul' else 'tecido_terracota', seg=8, aneis=3, exp=0.6)


def poltrona(g, tec='tecido_terracota', pe='metal_preto'):
    """Poltrona concha baixa (beauty), frente em +x."""
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.tubo([(sx * 0.2, sy * 0.2, 0.28), (sx * 0.26, sy * 0.26, 0)], 0.012, pe, seg=4)
    g.elipsoide(0, 0, 0.42, 0.36, 0.36, 0.16, tec, seg=14, aneis=5, exp=0.8)
    arco = []
    for k in range(9):
        a = math.radians(110 + 140 * k / 8)
        arco.append((0.34 * math.cos(a), 0.34 * math.sin(a)))
    for i in range(8):
        g.tubo([(arco[i][0], arco[i][1], 0.58), (arco[i + 1][0], arco[i + 1][1], 0.58)], 0.09, tec, seg=6)
        g.caixa(arco[i][0] - 0.07, arco[i][0] + 0.07, arco[i][1] - 0.07, arco[i][1] + 0.07, 0.45, 0.72, tec)


def vaso_planta(g, x, y, z=Z_PISO, r=0.22, h=0.5, alt=1.1, mt='ceramica', folha='folha_verde'):
    g.cil(x, y, r * 0.8, z, z + h, mt, seg=12, r2=r)
    g.cil(x, y, r * 0.92, z + h - 0.02, z + h, 'terra', seg=12)
    n = 3
    for k in range(n):
        a = math.pi * k / n
        c, s = math.cos(a) * alt * 0.5, math.sin(a) * alt * 0.5
        z0 = z + h - 0.08
        g.face([(x - c, y - s, z0), (x + c, y + s, z0), (x + c, y + s, z0 + alt), (x - c, y - s, z0 + alt)], folha, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)], cor=0.82, nrm=[(0, 0, 1)] * 4)


def tv(g, x, y, z, giro, w, h, tela, base=True):
    """Televisor na parede, tela em +x local."""
    with g.em(x, y, z, giro):
        g.caixa(0, 0.04, -w / 2, w / 2, -h / 2, h / 2, 'metal_preto')
        g.painel(0.041, -w / 2 + 0.02, 0.041, w / 2 - 0.02, -h / 2 + 0.02, h / 2 - 0.02, 'tela', ATL[tela], cor=1.0)


def prateleira(g, x0, x1, y0, y1, z, mt='madeira', e=0.03):
    g.caixa(x0, x1, y0, y1, z - e, z, mt, sem_fundo=False)


# ------------------------------------------------------------------ academia (14-academia)
def esteira(g):
    """Frente em +x."""
    g.caixa_red(-0.9, 0.75, -0.4, 0.4, 0.0, 0.14, 0.05, 'plastico_preto', passos=2)
    g.caixa(-0.85, 0.7, -0.27, 0.27, 0.14, 0.15, 'ep_preto')
    for s in (-1, 1):
        g.tubo([(0.62, s * 0.34, 0.14), (0.75, s * 0.32, 1.15)], 0.03, 'metal_preto', seg=6)
        g.tubo([(0.75, s * 0.32, 1.0), (0.2, s * 0.36, 0.98)], 0.018, 'metal_preto', seg=6)
    g.caixa_red(0.68, 0.85, -0.36, 0.36, 1.12, 1.3, 0.04, 'plastico_preto', passos=2)
    g.painel(0.685, 0.28, 0.685, -0.28, 1.15, 1.27, 'tela', ATL['tv_treino'])


def bike(g):
    """Bicicleta ergometrica, frente em +x."""
    g.caixa_red(-0.1, 0.42, -0.1, 0.1, 0.05, 0.72, 0.08, 'plastico_preto', passos=2)
    for xx in (-0.45, 0.55):
        g.caixa(xx - 0.04, xx + 0.04, -0.26, 0.26, 0, 0.05, 'metal_preto')
    g.tubo([(-0.45, 0, 0.05), (-0.05, 0, 0.4), (-0.22, 0, 0.82)], 0.024, 'metal_preto', seg=6)
    g.elipsoide(-0.25, 0, 0.86, 0.14, 0.12, 0.04, 'tecido_escuro', seg=8, aneis=3, exp=0.7)
    g.tubo([(0.3, 0, 0.7), (0.42, 0, 1.12)], 0.022, 'metal_preto', seg=6)
    g.tubo([(0.3, -0.26, 1.15), (0.42, 0, 1.12), (0.3, 0.26, 1.15)], 0.016, 'plastico_preto', seg=5)
    g.caixa(0.4, 0.5, -0.11, 0.11, 1.1, 1.22, 'tela')


def banco_supino(g):
    g.caixa_red(-0.55, 0.55, -0.15, 0.15, 0.40, 0.47, 0.05, 'tecido_escuro', passos=2)
    for xx, w in ((-0.45, 0.28), (0.42, 0.28)):
        g.tubo([(xx, 0, 0.4), (xx, 0, 0.04)], 0.025, 'metal_preto', seg=5)
        g.caixa(xx - 0.04, xx + 0.04, -w, w, 0, 0.04, 'metal_preto')


def halter(g, x, y, z, comp=0.26, r=0.055, mt='metal_preto'):
    g.tubo([(x - comp / 2, y, z + r), (x + comp / 2, y, z + r)], 0.012, 'cromo', seg=4)
    for s in (-1, 1):
        g.elipsoide(x + s * comp / 2, y, z + r, r, r, r, mt, seg=8, aneis=4)


def rack_halteres(g):
    """Rack em A com 3 niveis, frente em +x."""
    for s in (-1, 1):
        g.tubo([(0.0, s * 0.55, 0), (0.0, s * 0.55, 1.05)], 0.02, 'metal_preto', seg=5)
        g.tubo([(-0.22, s * 0.55, 0), (0.0, s * 0.55, 1.05)], 0.018, 'metal_preto', seg=5)
        g.tubo([(0.22, s * 0.55, 0), (0.0, s * 0.55, 1.05)], 0.018, 'metal_preto', seg=5)
    for z, dx in ((0.34, 0.16), (0.62, 0.1), (0.88, 0.05)):
        g.caixa(dx - 0.07, dx + 0.07, -0.56, 0.56, z, z + 0.02, 'metal_preto')
        for k in range(5):
            halter(g, dx, -0.42 + k * 0.21, z + 0.02, comp=0.12, r=0.045)


def estacao_cross(g):
    """Estacao de cabos em triangulo (implantacao): frame com polia, frente em +x."""
    M = 'metal_preto'
    for s in (-1, 1):
        g.tubo([(0.0, s * 0.9, 0), (0.0, s * 0.9, 2.2)], 0.035, M, seg=6)
        g.tubo([(-0.7, s * 0.35, 0), (-0.7, s * 0.35, 2.2)], 0.035, M, seg=6)
        g.tubo([(0.0, s * 0.9, 2.2), (-0.7, s * 0.35, 2.2)], 0.03, M, seg=6)
        g.tubo([(0.0, s * 0.9, 0.04), (-0.7, s * 0.35, 0.04)], 0.03, M, seg=6)
        g.caixa(-0.8, -0.6, s * 0.35 - 0.08, s * 0.35 + 0.08, 0.2, 1.2, 'cromo')
    g.tubo([(-0.7, -0.35, 2.2), (-0.7, 0.35, 2.2)], 0.03, M, seg=6)
    g.tubo([(0.0, -0.9, 2.05), (0.0, 0.9, 2.05)], 0.02, 'cromo', seg=6)


def academia_moveis(g):
    x0, x1 = X(PL.BLOCO_X[0]), X(PL.BLOCO_X[1])
    yN = Y(PL.ACADEMIA_Y[0])
    yS = Y(PL.ACADEMIA_Y[1])
    z = Z_PISO
    with g.em(X(2134), Y(841), z, 0):
        g.sombra(-1.1, 1.0, -0.55, 0.55, 0.01)
        esteira(g)
    with g.em(X(2134), Y(853), z, 0):
        g.sombra(-1.1, 1.0, -0.55, 0.55, 0.01)
        esteira(g)
    for py in (810, 820):
        with g.em(X(2136), Y(py), z, 0):
            g.sombra(-0.7, 0.7, -0.35, 0.35, 0.01)
            bike(g)
    with g.em(X(2100), Y(835), z, 90):
        g.sombra(-0.75, 0.75, -0.4, 0.4, 0.01)
        banco_supino(g)
    with g.em(X(2112), Y(796), z, -90):
        g.sombra(-0.35, 0.35, -0.75, 0.75, 0.01)
        rack_halteres(g)
    for k, px in enumerate((2124, 2129.5)):
        g.elipsoide(X(px), Y(793.5), z + 0.27, 0.27, 0.27, 0.27, 'tecido_bege', seg=14, aneis=8)
    with g.em(X(2096), Y(866), z, 90):
        g.sombra(-1.1, 0.4, -1.1, 1.1, 0.01)
        estacao_cross(g)
    # espelho iluminado + mural na parede norte
    yp = yN - E_PAREDE - 0.02
    g.caixa(x0 + 0.62, x0 + 4.58, yp - 0.015, yp, z + 0.37, z + 2.33, 'metal_preto')
    g.painel(x0 + 0.7, yp - 0.017, x0 + 4.5, yp - 0.017, z + 0.45, z + 2.25, 'atlas', ATL['espelho_gym'])
    g.caixa(x0 + 0.6, x0 + 4.6, yp - 0.02, yp, z + 0.33, z + 0.37, 'luz_led')
    g.painel(x0 + 4.8, yp - 0.004, x0 + 7.9, yp - 0.004, z + 1.75, z + 2.75, 'atlas', ATL['mural_gym'])
    # TV na parede leste
    tv(g, x1 - E_PAREDE - 0.05, Y(832), z + 1.85, 180, 1.1, 0.62, 'tv_treino')
    # step, halteres soltos, kettlebell e bebedouro
    g.caixa_red(X(2082), X(2090), Y(846), Y(842), z, z + 0.12, 0.04, 'plastico_laranja', passos=2)
    halter(g, X(2085), Y(838), z)
    halter(g, X(2112), Y(848), z + 0.0)
    g.elipsoide(X(2110), Y(838), z + 0.09, 0.09, 0.09, 0.09, 'metal_preto', seg=8, aneis=5)
    g.caixa(x0 + 0.2, x0 + 0.55, yN - 1.3, yN - 0.95, z, z + 1.1, 'inox')
    g.caixa(x0 + 0.5, x0 + 2.0, Y(850), Y(842), z, z + 0.02, 'ep_preto')


# ------------------------------------------------------------------ pub de jogos (21-pub)
def sinuca(g):
    """Eixo longo em x. Tampo verde, moldura escura, pes macicos."""
    L_, W_, h = 1.25, 0.72, 0.8
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.caixa(sx * (L_ - 0.3) - 0.11, sx * (L_ - 0.3) + 0.11, sy * (W_ - 0.2) - 0.11, sy * (W_ - 0.2) + 0.11, 0, h - 0.12, 'madeira_preta')
    g.caixa(-L_, L_, -W_, W_, h - 0.14, h, 'madeira_preta')
    g.piso(-L_ + 0.1, L_ - 0.1, -W_ + 0.1, W_ - 0.1, h + 0.002, 'tecido_verde_esc')
    for sx in (-1, 0, 1):
        for sy in (-1, 1):
            g.cil(sx * (L_ - 0.11), sy * (W_ - 0.11), 0.05, h, h + 0.004, 'metal_preto', seg=8)
    bolas = [('plastico_vermelho', 0.3, 0.0), ('plastico_amarelo', 0.36, 0.05), ('plastico_azulc', 0.36, -0.05), ('plastico_laranja', 0.42, 0.1), ('plastico_verde', 0.42, 0.0),
             ('plastico_preto', 0.42, -0.1), ('plastico_branco', -0.55, 0.05)]
    for mt, x, y in bolas:
        g.elipsoide(x, y, h + 0.03, 0.03, 0.03, 0.03, mt, seg=8, aneis=4)
    g.tubo([(-0.9, -0.3, h + 0.02), (0.1, 0.2, h + 0.03)], 0.008, 'madeira', seg=4)


def pub_moveis(g):
    x0, x1 = X(PL.BLOCO_X[0]), X(PL.BLOCO_X[1])
    yN, yS = Y(PL.PUB_Y[0]), Y(PL.PUB_Y[1])
    z = Z_PISO
    with g.em(X(2134), Y(888), z, 0):
        g.sombra(-1.5, 1.5, -1.0, 1.0, 0.01)
        sinuca(g)
    # luminaria pendente de LED sobre a sinuca
    g.tubo([(X(2120), Y(888), z + 2.2), (X(2148), Y(888), z + 2.2)], 0.02, 'luz_led', seg=4)
    # sofa azul + mesa de xadrez com banquinhos
    with g.em(X(2084), Y(879), z, 180):
        g.sombra(-1.0, 1.0, -0.55, 0.55, 0.01)
        sofa(g, 1.7, 0.75, 'tecido_azul')
    with g.em(X(2082), Y(893), z):
        mesa_redonda(g, 0.36, 0.75, 'madeira', 'metal_preto', larga=False)
        g.caixa(-0.17, 0.17, -0.17, 0.17, 0.75, 0.78, 'tecido_escuro')
        for k in range(5):
            g.cil(-0.12 + k * 0.06, -0.08, 0.012, 0.78, 0.84, 'plastico_branco', seg=6)
            g.cil(-0.12 + k * 0.06, 0.08, 0.012, 0.78, 0.84, 'plastico_preto', seg=6)
    for dx, dy in ((-0.7, 0.3), (0.72, -0.1)):
        with g.em(X(2082) + dx, Y(893) + dy, z):
            puff(g, 'tecido_bege', 0.24, 0.42)
    # prateleira com jogos, frigobar e placa
    yp = yS + E_PAREDE + 0.02
    g.caixa(x0 + 1.2, x0 + 7.6, yS + 0.14, yS + 0.42, z + 1.34, z + 1.38, 'madeira_clara', sem_fundo=False)
    g.painel(x0 + 3.8, yS + 0.4, x0 + 1.4, yS + 0.4, z + 1.38, z + 1.68, 'atlas', ATL['produtos'])
    g.painel(x0 + 5.6, yp + 0.002, x0 + 2.0, yp + 0.002, z + 2.0, z + 2.5, 'atlas', ATL['placa_pub'])
    g.caixa(x0 + 4.6, x0 + 5.3, yS + 0.14, yS + 0.72, z, z + 0.9, 'metal_preto')
    g.painel(x0 + 5.25, yS + 0.725, x0 + 4.65, yS + 0.725, z + 0.06, z + 0.84, 'tela', ATL['geladeira'])
    vaso_planta(g, x0 + 3.4, yS + 0.3, z + 1.38, 0.1, 0.16, 0.42, folha='folha_verde_clara')
    # banquetas no balcao
    for k in range(3):
        with g.em(x0 + 6.0 + k * 0.5, yS + 0.72, z):
            banqueta(g, 'tecido_escuro', 'metal_preto', 0.62)


# ------------------------------------------------------------------ brinquedoteca (18-brinquedoteca)
def cabana(g):
    """Cabana (teepee) de tecido, 4 mastros, abertura em +x."""
    b, h = 0.72, 1.75
    topo = (0, 0, h)
    cantos = [(-b, -b), (b, -b), (b, b), (-b, b)]
    for i in range(4):
        a, c = cantos[i], cantos[(i + 1) % 4]
        if i == 0 or i == 2 or i == 3:
            g.face([(a[0], a[1], 0), (c[0], c[1], 0), topo], 'tecido_branco', uvs=[(0, 0), (1, 0), (0.5, 1)], cor=0.95)
    # abertura: duas abas
    g.face([(b, -b, 0), (b, -0.12, 0), topo], 'tecido_branco', uvs=[(0, 0), (1, 0), (0.5, 1)], cor=0.9)
    g.face([(b, 0.12, 0), (b, b, 0), topo], 'tecido_branco', uvs=[(0, 0), (1, 0), (0.5, 1)], cor=0.9)
    for a in cantos:
        g.tubo([(a[0] * 1.05, a[1] * 1.05, 0), (a[0] * -0.08, a[1] * -0.08, h + 0.18)], 0.018, 'madeira_clara', seg=4)
    g.caixa_red(-0.6, 0.65, -0.6, 0.6, 0, 0.1, 0.1, 'tecido_cinza', passos=2)
    g.elipsoide(0.2, 0.2, 0.2, 0.22, 0.2, 0.1, 'tecido_terracota', seg=8, aneis=3, exp=0.6)
    g.elipsoide(-0.1, -0.25, 0.2, 0.22, 0.2, 0.1, 'tecido_bege', seg=8, aneis=3, exp=0.6)


def tatame(g, x0, x1, y0, y1, z):
    """Tapete de EVA em placas de 50 cm alternando verdes."""
    cores = ('tecido_verde', 'tecido_verde_esc', 'tecido_bege')
    p = 0.56
    j = 0
    yy = y0
    while yy < y1 - 0.01:
        xx = x0
        i = 0
        while xx < x1 - 0.01:
            g.piso(xx, min(xx + p, x1), yy, min(yy + p, y1), z, cores[(i * 2 + j * 3 + (i * j)) % 3])
            xx += p
            i += 1
        yy += p
        j += 1


def brinq_moveis(g):
    x0, x1 = X(PL.BLOCO_X[0]), X(PL.BLOCO_X[1])
    yN, yS = Y(PL.BRINQ_Y[0]), Y(PL.BRINQ_Y[1])
    z = Z_PISO
    tatame(g, X(2100), x1 - 0.3, yS + 0.3, Y(931), z + 0.012)
    with g.em(X(2144), Y(950), z, 200):
        g.sombra(-0.95, 0.95, -0.95, 0.95, 0.018)
        cabana(g)
    # almofadoes
    for px, py, tec in ((2118, 948, 'tecido_terracota'), (2108, 940, 'tecido_escuro'), (2126, 938, 'tecido_escuro')):
        g.elipsoide(X(px), Y(py), z + 0.14, 0.42, 0.38, 0.13, tec, seg=10, aneis=4, exp=0.6)
    # caixa de brinquedos e mesinha com cadeirinhas
    g.caixa(X(2085), X(2098), Y(958), Y(950), z, z + 0.42, 'plastico_laranja', topo='plastico_amarelo')
    with g.em(X(2090), Y(930), z):
        g.sombra(-0.75, 0.75, -0.75, 0.75, 0.012, disco=True)
        mesa_redonda(g, 0.36, 0.5, 'plastico_branco', 'madeira_clara', larga=False)
        for k, mt in enumerate(('plastico_vermelho', 'plastico_amarelo', 'plastico_azulc', 'plastico_verde')):
            a = k * 90 + 30
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            with g.em(c * 0.55, s * 0.55, 0, a + 180, 0.62):
                cadeira_concha(g, mt, 'madeira_clara')
    # estantes ao longo da parede norte
    yp = yN - E_PAREDE
    for k, px in enumerate(range(2110, 2150, 12)):
        ex0, ex1 = X(px), X(px + 11)
        g.caixa(ex0, ex1, yp - 0.36, yp, z, z + 0.72, 'plastico_branco', topo='madeira_clara')
        g.painel(ex0 + 0.05, yp - 0.361, ex1 - 0.05, yp - 0.361, z + 0.08, z + 0.65, 'atlas', ATL['produtos'])
    # bancada baixa vermelha, TV e mural de copas
    g.caixa(X(2076), X(2108), yp - 0.42, yp, z + 0.34, z + 0.46, 'plastico_vermelho')
    tv(g, X(2092), yp - 0.01, z + 1.3, -90, 1.0, 0.56, 'tv_kids')
    g.painel(x1 - 0.15, yS + E_PAREDE + 0.012, x0 + 0.15, yS + E_PAREDE + 0.012, z + 1.65, z + 2.95, 'atlas', ATL['mural_brinq'])
    g.painel(x0 + 0.15, yp - 0.012, x1 - 0.15, yp - 0.012, z + 1.65, z + 2.95, 'atlas', ATL['mural_brinq'])


# ------------------------------------------------------------------ salao de festas (16-salao)
def mesa_jantar(g, x, y, n=5, r=0.72):
    with g.em(x, y, Z_PISO):
        g.sombra(-1.5, 1.5, -1.5, 1.5, 0.008, disco=True)
        mesa_redonda(g, r, 0.76, 'madeira', 'madeira')
        for k in range(n):
            a = 360 * k / n + 18
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            with g.em(c * (r + 0.28), s * (r + 0.28), 0, a + 180):
                cadeira_estofada(g)
            g.cil(c * (r - 0.2), s * (r - 0.2), 0.12, 0.76, 0.772, 'plastico_branco', seg=12)
        g.cil(0, 0, 0.09, 0.76, 0.9, 'ceramica', seg=10)
        vaso_planta(g, 0, 0, 0.9, 0.07, 0.02, 0.32, folha='folha_verde_clara')


def salao_moveis(g):
    x0, x1 = X(PL.BLOCO_X[0]), X(PL.BLOCO_X[1])
    yN = Y(PL.SALAO_Y[0])
    z = Z_PISO
    # sofa azul na parede norte e mesas baixas com puffs
    with g.em((x0 + x1) / 2 + 0.2, yN - E_PAREDE - 0.45, z, 0):
        g.sombra(-3.4, 3.4, -0.6, 0.6, 0.01)
        sofa(g, 6.0, 0.8, 'tecido_azul')
    for px, py in ((2098, 974), (2126, 974)):
        with g.em(X(px), Y(py), z):
            g.sombra(-0.75, 0.75, -0.75, 0.75, 0.01, disco=True)
            mesa_redonda(g, 0.46, 0.72, 'plastico_branco', 'metal_preto', larga=False)
            vaso_planta(g, 0, 0, 0.72, 0.06, 0.02, 0.22, folha='folha_verde_clara')
        for dx, dy in ((-0.72, 0.3), (0.72, 0.25), (0.05, -0.72)):
            with g.em(X(px) + dx, Y(py) + dy, z):
                puff(g, 'tecido_terracota')
    # 4 mesas redondas
    for px, py in ((2094, 996), (2131, 996), (2094, 1030), (2131, 1030)):
        mesa_jantar(g, X(px), Y(py))
    # parede leste: TV + ripado com LED; aparador
    xp = x1 - E_PAREDE
    yT = Y(1010)
    g.caixa(xp - 0.05, xp, yT - 1.5, yT + 1.5, z, z + 2.8, 'ripado_claro')
    g.caixa(xp - 0.06, xp - 0.05, yT - 1.45, yT - 1.42, z + 0.1, z + 2.7, 'luz_led')
    g.caixa(xp - 0.06, xp - 0.05, yT + 1.42, yT + 1.45, z + 0.1, z + 2.7, 'luz_led')
    tv(g, xp - 0.05, yT, z + 1.6, 180, 1.3, 0.74, 'tv_show')
    g.caixa(xp - 0.45, xp - 0.05, yT - 1.2, yT + 1.2, z + 0.5, z + 0.56, 'madeira')
    # cozinha: ilha com banquetas, bancada, geladeira inox, prateleira e pendentes
    ky = Y(1064)
    g.caixa(X(2083), X(2100), ky - 0.35, ky + 0.35, z, z + 0.92, 'madeira_clara', topo='pedra_granito')
    for k in range(3):
        with g.em(X(2085) + k * 0.65, ky + 0.62, z):
            banqueta(g, 'plastico_azul', 'metal_preto', 0.68)
    yS = Y(1090) + E_PAREDE
    g.caixa(x0 + E_PAREDE, X(2102), yS, yS + 0.6, z, z + 0.9, 'plastico_branco', topo='pedra_granito')
    g.caixa(X(2102) - 0.85, X(2102) - 0.05, yS + 0.0, yS + 0.72, z, z + 1.85, 'inox')
    g.painel(X(2102) - 0.06, yS + 0.721, X(2102) - 0.84, yS + 0.721, z + 0.02, z + 1.83, 'atlas', ATL['geladeira_inox'])
    prateleira(g, x0 + 0.5, x0 + 2.4, yS, yS + 0.26, z + 1.7, 'madeira')
    vaso_planta(g, x0 + 0.42 + 0.3, yN - 1.2, z, 0.26, 0.5, 1.5)
    # WCs do servico
    sx0, sx1, sy0, sy1 = RM(PL.SERVICO)
    xm = (sx0 + sx1) / 2 + 0.3
    ym = (sy0 + sy1) / 2
    for bx, by in ((sx1 - 0.9, sy1 - 0.5), (sx1 - 0.9, sy0 + 0.5)):
        vaso_sanitario(g, bx, by, z, 180)
    g.caixa(sx0 + 0.2, sx0 + 1.1, sy1 - 0.62, sy1 - 0.14, z, z + 0.82, 'plastico_branco', topo='pedra_granito')
    g.caixa(sx0 + 0.2, sx0 + 1.1, sy0 + 0.14, sy0 + 0.62, z, z + 0.82, 'plastico_branco', topo='pedra_granito')


def vaso_sanitario(g, x, y, z, giro=0):
    with g.em(x, y, z, giro):
        g.cil(-0.02, 0, 0.16, 0, 0.4, 'plastico_branco', seg=10, r2=0.2)
        g.caixa(-0.34, -0.14, -0.2, 0.2, 0, 0.78, 'plastico_branco')


# ------------------------------------------------------------------ churrasqueira (15-churrasqueira)
def churrasqueira_moveis(g):
    x0, x1, y0, y1 = RM(PL.CHURRASCO)
    xm = X(2096)
    z = Z_PISO
    yp = y1 - E_PAREDE
    # bancada de madeira com pedra, cuba, churrasqueira de alvenaria com fogo e prateleira
    g.caixa(xm + 0.2, x1 - 1.0, yp - 0.58, yp, z, z + 0.88, 'madeira_clara', topo='pedra_granito')
    g.cil(xm + 1.0, yp - 0.3, 0.015, z + 0.88, z + 1.1, 'cromo', seg=6)
    g.caixa(x1 - 1.0, x1 - 0.05, yp - 0.6, yp, z, z + 2.0, 'int_terracota')
    g.caixa(x1 - 0.86, x1 - 0.2, yp - 0.605, yp - 0.6, z + 0.7, z + 1.25, 'metal_preto')
    g.caixa(x1 - 0.82, x1 - 0.24, yp - 0.61, yp - 0.605, z + 0.74, z + 0.92, 'luz_led')
    prateleira(g, xm + 0.4, x1 - 1.2, yp - 0.24, yp, z + 1.7, 'madeira')
    vaso_planta(g, xm + 0.7, yp - 0.13, z + 1.7, 0.07, 0.12, 0.35, folha='folha_verde_clara')
    # mesa comunitaria alta com 3 cadeiras azuis e 1 banco
    tx, ty = X(2107), Y(725)
    with g.em(tx, ty, z):
        g.sombra(-1.4, 1.4, -0.9, 0.9, 0.012)
        g.caixa(-1.1, 1.1, -0.36, 0.36, 0.86, 0.9, 'madeira')
        for sx in (-1, 1):
            for sy in (-1, 1):
                g.caixa(sx * 1.02 - 0.025, sx * 1.02 + 0.025, sy * 0.3 - 0.025, sy * 0.3 + 0.025, 0, 0.86, 'metal_preto')
        for k in range(3):
            with g.em(-0.75 + k * 0.75, -0.58, 0.12, 90, 1.0):
                cadeira_concha(g, 'plastico_azul', 'metal_preto')
        g.caixa(-1.0, 1.0, 0.5, 0.78, 0.44, 0.48, 'madeira_clara')
        for sx in (-1, 1):
            g.caixa(sx * 0.88 - 0.02, sx * 0.88 + 0.02, 0.52, 0.76, 0, 0.44, 'metal_preto')
        utensilios(g, 0.5, 0.1, 0.9)
    # mesas sob a pergola
    for px, py in ((2141, 716), (2141, 746)):
        mesa_com_cadeiras(g, X(px), Y(py), 0, 'externa', 0.8)
    # vaso grande
    vaso_planta(g, x1 + 0.4, y0 - 0.45, z, 0.38, 1.05, 1.4)
    # WC do bloco
    bx0 = x0 + E_PAREDE
    vaso_sanitario(g, xm - 0.5, y1 - 0.55, z, 180)
    g.caixa(bx0, bx0 + 0.9, y0 + 0.14, y0 + 0.64, z, z + 0.82, 'plastico_branco', topo='pedra_granito')


# ------------------------------------------------------------------ varanda gourmet (06-gourmet)
def gourmet_moveis(g):
    x0, x1, y0, y1 = RM(PL.GOURMET)
    z = Z_PISO
    for px, py in ((1888, 1030), (1874, 1054), (1903, 1050)):
        mesa_com_cadeiras(g, X(px), Y(py), 0, 'preta')
    # cozinha: bancada alta com 3 banquetas vermelhas, churrasqueira, geladeira, TV
    yp = Y(1070) - 0.1
    g.caixa(X(1868), X(1897), yp + 0.1, yp + 0.55, z, z + 0.95, 'madeira', topo='pedra_granito')
    for k in range(3):
        with g.em(X(1872) + k * 0.8, yp + 0.8, z):
            banqueta(g, 'plastico_vermelho', 'metal_preto', 0.66)
    ys = y0 + E_PAREDE
    g.caixa(x0 + 0.2, X(1885), ys, ys + 0.58, z, z + 0.88, 'plastico_branco', topo='pedra_granito')
    g.caixa(X(1885), X(1897) - 0.05, ys, ys + 0.62, z, z + 1.1, 'int_cinza')
    g.caixa(X(1887), X(1895), ys + 0.625, ys + 0.63, z + 0.45, z + 1.0, 'metal_preto')
    g.caixa(X(1888), X(1894), ys + 0.63, ys + 0.635, z + 0.5, z + 0.68, 'luz_led')
    g.caixa(x0 + 0.2, x0 + 0.92, ys + 0.62, ys + 1.3, z, z + 1.8, 'inox')
    prateleira(g, x0 + 1.2, X(1885), ys, ys + 0.24, z + 1.6, 'madeira')
    tv(g, x0 + E_PAREDE + 0.01, Y(1048), z + 1.7, 0, 1.2, 0.68, 'tv_show')
    # aparador com louca sob a TV
    g.caixa(x0 + 0.15, x0 + 0.55, Y(1054), Y(1042), z + 0.75, z + 0.8, 'madeira')
    for k in range(2):
        g.caixa(x0 + 0.17, x0 + 0.21, Y(1054) + 0.05 + k * 1.05, Y(1054) + 0.08 + k * 1.05, z, z + 0.75, 'metal_preto')
    # WC
    wx0, wx1, wy0, wy1 = RM((1897, 1070, 1915, 1104))
    ym = (wy0 + wy1) / 2
    vaso_sanitario(g, wx1 - 0.5, wy1 - 0.6, z, 180)
    vaso_sanitario(g, wx1 - 0.5, wy0 + 0.6, z, 180)


# ------------------------------------------------------------------ ambientes no terreo das torres
def vitrine(g, x, y0, y1, z=0.12, h=2.75):
    """Fachada envidracada da sala, voltada para +x: dali se ve o interior."""
    g.face([(x, y0, z), (x, y1, z), (x, y1, z + h), (x, y0, z + h)], 'vidro_lazer', cor=1.0)
    L_ = y1 - y0
    n = max(2, round(L_ / 1.1))
    for k in range(n + 1):
        yy = y0 + L_ * k / n
        g.caixa(x - 0.03, x + 0.03, yy - 0.025, yy + 0.025, z, z + h, 'caixilho_ext')
    for zz in (z, z + 2.1, z + h - 0.03):
        g.caixa(x - 0.03, x + 0.03, y0, y1, zz, zz + 0.04, 'caixilho_ext')


def _sul_interno(g, x0, x1, y, z, h, mt):
    """Parede interna do lado sul: precisa olhar para +y."""
    g.face([(x1, y, z), (x0, y, z), (x0, y, z + h), (x1, y, z + h)], mt, uvs=[(0, 0)] * 4, nrm=[(0, 1, 0)] * 4)


def salas_torres(g):
    z = 0.12
    H_ = 2.78
    cx1, cy = TORRES['torre-1']
    cx2 = TORRES['torre-2'][0]
    cx3 = TORRES['torre-3'][0]

    def casca(cx, r, piso, s, n, o):
        x0, x1, y0, y1 = cx + r['x'][0], cx + r['x'][1], cy - r['y'][1], cy - r['y'][0]
        g.piso(x0, x1, y0, y1, z + 0.004, piso)
        _sul_interno(g, x0, x1, y0, z, H_, s)
        g.face([(x0, y1, z), (x1, y1, z), (x1, y1, z + H_), (x0, y1, z + H_)], n, uvs=[(0, 0)] * 4)
        g.face([(x0, y0, z), (x0, y1, z), (x0, y1, z + H_), (x0, y0, z + H_)], o, uvs=[(0, 0)] * 4)
        vitrine(g, x1, y0, y1, z)
        return x0, x1, y0, y1

    # --- Torre 1: spa + beauty
    x0, x1, y0, y1 = casca(cx1, SALA1, 'piso_cinza', 'int_terracota', 'int_areia', 'ripado_madeira')
    with g.em(x0 + 2.0, (y0 + y1) / 2, z + 0.01, 0):
        g.sombra(-1.2, 1.2, -0.6, 0.6, 0.008)
        maca(g)
    g.caixa(x0, x0 + 0.42, y0 + 0.6, y1 - 0.6, z + 0.78, z + 0.9, 'pedra_granito')
    g.elipsoide(x0 + 0.03, (y0 + y1) / 2, z + 1.65, 0.02, 0.5, 0.56, 'espelho', seg=20, aneis=8)
    g.elipsoide(x0 + 0.02, (y0 + y1) / 2, z + 1.65, 0.01, 0.56, 0.62, 'luz_led', seg=20, aneis=6)
    g.painel(x0 + 2.4, y0 + 0.01, x0 + 0.9, y0 + 0.01, z + 0.9, z + 2.5, 'atlas', ATL['quadro'])
    x0, x1, y0, y1 = casca(cx1, SALA2, 'piso_int', 'int_rosa', 'int_areia', 'ripado_claro')
    for k, py in enumerate((y0 + 1.05, y1 - 1.0)):
        with g.em(x0 + 1.45, py, z + 0.01, 180):
            cadeira_beauty(g)
        g.caixa(x0 + 0.03, x0 + 0.05, py - 0.34, py + 0.34, z + 0.75, z + 2.25, 'espelho', sem_fundo=False)
        g.caixa(x0 + 0.03, x0 + 0.04, py - 0.39, py + 0.39, z + 0.71, z + 0.75, 'luz_led')
        g.caixa(x0 + 0.03, x0 + 0.04, py - 0.39, py + 0.39, z + 2.25, z + 2.29, 'luz_led')
        g.caixa(x0, x0 + 0.4, py - 0.5, py + 0.5, z + 0.75, z + 0.79, 'madeira_clara', sem_fundo=False)
    with g.em(x1 - 1.0, y1 - 0.8, z + 0.01, 225):
        poltrona(g)
    g.caixa(x0 + 0.1, x0 + 0.6, (y0 + y1) / 2 - 0.28, (y0 + y1) / 2 + 0.28, z + 0.01, z + 0.9, 'plastico_branco')
    # --- Torre 2: mini market + lavanderia
    x0, x1, y0, y1 = casca(cx2, SALA1, 'piso_cinza', 'int_cinza', 'int_cinza', 'int_escuro')
    for k in range(3):
        yy = y0 + 0.5 + k * 0.82
        g.caixa(x0, x0 + 0.62, yy - 0.38, yy + 0.38, z, z + 2.0, 'metal_preto')
        g.painel(x0 + 0.625, yy - 0.36, x0 + 0.625, yy + 0.36, z + 0.15, z + 1.95, 'tela', ATL['geladeira'])
    estante_mercado(g, x0 + 1.0, x1 - 0.1, y1 - 0.34, y1, z, 'produtos', True)
    estante_mercado(g, x0 + 1.0, x1 - 0.1, y0, y0 + 0.34, z, 'produtos', False)
    g.painel(x0 + 1.0, y1 - 0.003, x0 + 3.2, y1 - 0.003, z + 2.2, z + 2.68, 'atlas', ATL['placa_mercado'])
    g.caixa(x0 + 2.0, x0 + 2.5, y0 + 1.1, y0 + 1.5, z, z + 0.4, 'plastico_verde')
    x0, x1, y0, y1 = casca(cx2, SALA2, 'piso_int', 'int_creme', 'int_grafite', 'int_creme')
    for k in range(3):
        xx = x0 + 0.1 + k * 0.72
        g.caixa(xx, xx + 0.68, y1 - 0.68, y1, z, z + 0.88, 'plastico_branco', topo='pedra_granito')
        g.painel(xx, y1 - 0.68 - 0.002, xx + 0.68, y1 - 0.68 - 0.002, z + 0.08, z + 0.8, 'atlas', ATL['lavadora'])
    g.caixa(x0, x1, y1 - 0.02, y1, z + 0.9, z + 1.7, 'azulejo', sem_fundo=False)
    g.caixa(x0 + 2.3, x1 - 0.1, y1 - 0.55, y1, z + 0.85, z + 0.9, 'madeira_clara', sem_fundo=False)
    prateleira(g, x0 + 0.1, x1 - 0.1, y1 - 0.28, y1, z + 1.9, 'madeira_clara')
    g.painel(x0 + 1.5, y1 - 0.005, x1 - 0.2, y1 - 0.005, z + 2.05, z + 2.7, 'atlas', ATL['placa_lavanderia'])
    for xx in (x1 - 0.9, x1 - 0.4):
        g.cil(xx, y1 - 0.9, 0.18, z, z + 0.48, 'rattan', seg=12, tampa=False)
    with g.em(x1 - 0.9, y0 + 0.9, z + 0.01, 120):
        poltrona(g, 'plastico_azul', 'metal_preto')
    # --- Torre 3: cinema + coworking
    x0, x1, y0, y1 = casca(cx3, SALA1, 'carpete', 'int_escuro', 'int_escuro', 'int_escuro')
    g.painel(x0 + 0.03, y0 + 0.25, x0 + 0.03, y1 - 0.25, z + 0.85, z + 2.25, 'tela', ATL['cinema'])
    g.caixa(x0, x0 + 0.08, y0 + 0.2, y1 - 0.2, z + 0.8, z + 0.85, 'metal_preto')
    g.caixa(x0, x0 + 0.24, y0 + 0.2, y1 - 0.2, z + 0.5, z + 0.54, 'madeira_escura')
    for dx, dy in ((1.5, 0.75), (1.55, 2.15), (2.95, 1.45)):
        g.elipsoide(x0 + dx, y0 + dy, z + 0.3, 0.68, 0.66, 0.42, 'tecido_escuro', seg=14, aneis=6, exp=0.82, zmin=-0.72)
    x0, x1, y0, y1 = casca(cx3, SALA2, 'piso_int', 'tela_verde', 'int_areia', 'int_areia')
    tv(g, x0 + 0.01, (y0 + y1) / 2 + 0.3, z + 1.45, 0, 1.0, 0.58, 'tv_podcast')
    with g.em(x0 + 1.2, (y0 + y1) / 2 + 0.3, z + 0.01):
        g.sombra(-0.9, 0.9, -0.9, 0.9, 0.008, disco=True)
        mesa_quadrada(g, 0.9, 0.7, 0.75, 'plastico_branco', 'madeira_clara')
        for a in (0, 180, 90, 270):
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            with g.em(c * 0.62, s * 0.62, 0, a + 180):
                cadeira_concha(g, 'plastico_azul', 'madeira_clara')
    g.caixa(x1 - 0.72, x1 - 0.12, y0 + 0.2, y1 - 0.2, z + 0.73, z + 0.77, 'int_escuro')
    for k in range(3):
        with g.em(x1 - 1.0, y0 + 0.75 + k * 0.95, z + 0.01, 0):
            cadeira_concha(g, 'plastico_branco', 'metal_preto')
    g.tubo([(x0 + 2.3, y0 + 0.5, z), (x0 + 2.3, y0 + 0.5, z + 1.75)], 0.012, 'metal_preto', seg=4)
    pts = [(x0 + 2.3 + 0.17 * math.cos(2 * math.pi * k / 14), y0 + 0.5, z + 1.75 + 0.17 * math.sin(2 * math.pi * k / 14)) for k in range(15)]
    g.tubo(pts, 0.012, 'luz_led', seg=4)


def maca(g):
    """Maca de massagem de madeira com prateleira, eixo x."""
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.caixa(sx * 0.9 - 0.04, sx * 0.9 + 0.04, sy * 0.3 - 0.04, sy * 0.3 + 0.04, 0, 0.72, 'madeira')
    g.caixa(-0.95, 0.95, -0.33, 0.33, 0.2, 0.24, 'madeira')
    g.caixa(-0.97, 0.97, -0.35, 0.35, 0.68, 0.74, 'madeira')
    g.caixa_red(-0.98, 0.98, -0.36, 0.36, 0.74, 0.84, 0.05, 'tecido_bege', passos=2)
    g.caixa(0.2, 0.55, -0.15, 0.15, 0.24, 0.42, 'rattan')
    g.elipsoide(-0.75, 0, 0.87, 0.14, 0.2, 0.05, 'tecido_branco', seg=8, aneis=3, exp=0.6)


def cadeira_beauty(g):
    """Cadeira de pedicure/cabelereiro: base rodizio, assento claro."""
    g.cil(0, 0, 0.26, 0, 0.03, 'cromo', seg=12)
    g.cil(0, 0, 0.035, 0.03, 0.42, 'cromo', seg=8, tampa=False)
    g.elipsoide(0, 0, 0.48, 0.28, 0.28, 0.08, 'tecido_branco', seg=12, aneis=4, exp=0.6)
    g.elipsoide(-0.24, 0, 0.72, 0.06, 0.28, 0.24, 'tecido_branco', seg=12, aneis=5, exp=0.75)


def estante_mercado(g, x0, x1, y0, y1, z, img, encostada_norte):
    for k in range(5):
        zz = z + 0.32 + k * 0.48
        g.caixa(x0, x1, y0, y1, zz - 0.03, zz, 'madeira', sem_fundo=False)
        if encostada_norte:      # frente para o sul (-y)
            g.painel(x0 + 0.03, y0 - 0.002, x1 - 0.03, y0 - 0.002, zz, zz + 0.32, 'atlas', ATL[img])
        else:
            g.painel(x1 - 0.03, y1 + 0.002, x0 + 0.03, y1 + 0.002, zz, zz + 0.32, 'atlas', ATL[img])
    n = 3
    for k in range(n + 1):
        xx = x0 + (x1 - x0) * k / n
        for yy in (y0 + 0.02, y1 - 0.02):
            g.caixa(xx - 0.012, xx + 0.012, yy - 0.012, yy + 0.012, z, z + 2.25, 'metal_preto')


# ------------------------------------------------------------------ delivery (25-delivery)
def delivery_moveis(g):
    x0, x1, y0, y1 = RM(PL.DELIVERY)
    z = Z_PISO
    px0, px1 = x0 + E_PAREDE, x1 - E_PAREDE
    for k in range(5):
        zz = z + 0.2 + k * 0.48
        g.caixa(px0, px0 + 0.4, y0 + 0.2, y1 - 0.2, zz - 0.03, zz, 'madeira', sem_fundo=False)
        g.painel(px0 + 0.4, y0 + 0.25, px0 + 0.4, y1 - 0.25, zz, zz + 0.32, 'atlas', ATL['caixas'])
    for yy in (y0 + 0.22, y1 - 0.22):
        for xx in (px0 + 0.03, px0 + 0.38):
            g.caixa(xx - 0.012, xx + 0.012, yy - 0.012, yy + 0.012, z, z + 2.35, 'metal_preto')


# ------------------------------------------------------------------ deck da piscina (04-piscina)
def espreguicadeira(g):
    """Eixo x, cabeceira em -x."""
    M = 'metal_ouro'
    for sy in (-1, 1):
        g.tubo([(0.95, sy * 0.34, 0.0), (0.9, sy * 0.34, 0.27), (-0.3, sy * 0.34, 0.27), (-1.0, sy * 0.34, 0.72)], 0.015, M, seg=4)
        g.tubo([(-0.3, sy * 0.34, 0.27), (-0.34, sy * 0.34, 0)], 0.015, M, seg=4)
    g.caixa_red(-0.3, 0.95, -0.33, 0.33, 0.28, 0.36, 0.04, 'tecido_bege', passos=2)
    g.face([(-0.3, -0.33, 0.36), (-0.3, 0.33, 0.36), (-1.0, 0.33, 0.8), (-1.0, -0.33, 0.8)][::-1], 'tecido_bege', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    g.face([(-0.3, -0.33, 0.36), (-0.3, 0.33, 0.36), (-1.0, 0.33, 0.8), (-1.0, -0.33, 0.8)], 'tecido_bege', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])


def ombrelone(g, r=1.45, h=2.5):
    """Ombrelone quadrado com base."""
    g.cil(0, 0, 0.28, 0, 0.05, 'metal_preto', seg=14)
    g.cil(0, 0, 0.025, 0.05, h + 0.25, 'madeira_clara', seg=8, tampa=False)
    topo = (0, 0, h + 0.25)
    cs = [(-r, -r), (r, -r), (r, r), (-r, r)]
    for i in range(4):
        a, b = cs[i], cs[(i + 1) % 4]
        g.face([(a[0], a[1], h - 0.15), (b[0], b[1], h - 0.15), topo], 'ombrelone', uvs=[(0, 0), (1, 0), (0.5, 1)], cor=[0.82, 0.82, 1.0])
        g.face([(b[0], b[1], h - 0.15), (a[0], a[1], h - 0.15), topo], 'ombrelone', uvs=[(0, 0), (1, 0), (0.5, 1)], cor=[0.72, 0.72, 0.88])
    g.tubo([(0, 0, h - 0.5), (-r * 0.8, 0, h - 0.17)], 0.008, 'madeira_clara', seg=3)
    g.tubo([(0, 0, h - 0.5), (r * 0.8, 0, h - 0.17)], 0.008, 'madeira_clara', seg=3)


def bangalo(g):
    """Daybed redondo de ratan com almofadas (04-piscina)."""
    g.cil(0, 0, 0.82, 0, 0.3, 'rattan', seg=20, r2=0.86)
    g.elipsoide(0, 0, 0.32, 0.8, 0.8, 0.09, 'tecido_branco', seg=20, aneis=4, exp=0.6)
    pts = [(0.86 * math.cos(math.radians(a)), 0.86 * math.sin(math.radians(a))) for a in range(60, 301, 20)]
    for p, q in zip(pts[:-1], pts[1:]):
        g.tubo([(p[0], p[1], 0.3), (p[0], p[1], 0.82)], 0.03, 'rattan', seg=4)
        g.tubo([(p[0], p[1], 0.82), (q[0], q[1], 0.82)], 0.05, 'rattan', seg=5)
        g.face([(q[0], q[1], 0.28), (p[0], p[1], 0.28), (p[0], p[1], 0.8), (q[0], q[1], 0.8)], 'rattan', uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    g.elipsoide(-0.3, 0.2, 0.52, 0.25, 0.1, 0.2, 'tecido_bege', seg=8, aneis=4, exp=0.6)
    g.elipsoide(-0.2, -0.3, 0.52, 0.25, 0.1, 0.2, 'tecido_azul', seg=8, aneis=4, exp=0.6)


def deck_moveis(g):
    z = Z_PISO
    for px, py in ((1931, 767), (1951, 767)):           # no deck molhado
        with g.em(X(px), Y(py), Z_AGUA - 0.08, 90):
            g.sombra(-1.1, 1.1, -0.45, 0.45, 0.012)
            espreguicadeira(g)
    for px, py in ((1880, 768), (1892, 768)):
        with g.em(X(px), Y(py), z, 90):
            g.sombra(-1.1, 1.1, -0.45, 0.45, 0.012)
            espreguicadeira(g)
    for px, py in ((2000, 790), (2016, 790)):
        with g.em(X(px), Y(py), z, 90):
            g.sombra(-1.1, 1.1, -0.45, 0.45, 0.012)
            espreguicadeira(g)
    for px, py in ((1885, 780), (1985, 790), (1945, 835)):
        with g.em(X(px), Y(py), z):
            g.sombra(-1.6, 1.6, -1.6, 1.6, 0.012, disco=True)
            ombrelone(g)
    # mesas com cadeiras sob o ombrelone
    for px, py in ((1985, 790), (1945, 835)):
        with g.em(X(px), Y(py), z):
            mesa_redonda(g, 0.42, 0.72, 'madeira_escura', 'metal_preto', larga=False)
            for a in (0, 90, 180, 270):
                c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
                with g.em(c * 0.6, s * 0.6, 0, a + 180):
                    cadeira_externa(g)
    for px, py in ((1896, 812), (1912, 812)):
        with g.em(X(px), Y(py), z, -60 if px < 1900 else 240):
            g.sombra(-1.05, 1.05, -1.05, 1.05, 0.012, disco=True)
            bangalo(g)
    # ducha
    dx, dy = X(2036), Y(735)
    g.tubo([(dx, dy, z), (dx, dy, z + 2.2), (dx + 0.3, dy, z + 2.3)], 0.022, 'inox', seg=6)
    g.caixa(dx - 0.5, dx + 0.5, dy - 0.5, dy + 0.5, z, z + 0.02, 'ep_preto')


# ------------------------------------------------------------------ playground (09-playground)
def _poste_play(g, x, y, h):
    g.caixa(x - 0.06, x + 0.06, y - 0.06, y + 0.06, 0, h, 'plastico_marrom')


def _escorrega(g, a, b, larg, mt, curva=0.25, n=8):
    """Calha de escorregador de a (alto) a b (baixo), com lateral."""
    ax, ay, az = a; bx, by, bz = b
    dx, dy = bx - ax, by - ay
    L_ = math.hypot(dx, dy) or 1
    nx, ny = -dy / L_ * larg / 2, dx / L_ * larg / 2
    pts = []
    for k in range(n + 1):
        t = k / n
        z = az + (bz - az) * (t ** 0.8) + curva * math.sin(math.pi * t) * -0.5
        pts.append((ax + dx * t, ay + dy * t, z))
    for p, q in zip(pts[:-1], pts[1:]):
        g.face([(p[0] - nx, p[1] - ny, p[2]), (q[0] - nx, q[1] - ny, q[2]), (q[0] + nx, q[1] + ny, q[2]), (p[0] + nx, p[1] + ny, p[2])], mt, uvs=[(0, 0)] * 4)
        g.face([(p[0] + nx, p[1] + ny, p[2]), (q[0] + nx, q[1] + ny, q[2]), (q[0] - nx, q[1] - ny, q[2]), (p[0] - nx, p[1] - ny, p[2])], mt, uvs=[(0, 0)] * 4)
        for s in (-1, 1):
            g.tubo([(p[0] + s * nx, p[1] + s * ny, p[2] + 0.14), (q[0] + s * nx, q[1] + s * ny, q[2] + 0.14)], 0.03, mt, seg=5)
            g.face([(p[0] + s * nx, p[1] + s * ny, p[2]), (q[0] + s * nx, q[1] + s * ny, q[2]), (q[0] + s * nx, q[1] + s * ny, q[2] + 0.14), (p[0] + s * nx, p[1] + s * ny, p[2] + 0.14)], mt, uvs=[(0, 0)] * 4)
            g.face([(q[0] + s * nx, q[1] + s * ny, q[2]), (p[0] + s * nx, p[1] + s * ny, p[2]), (p[0] + s * nx, p[1] + s * ny, p[2] + 0.14), (q[0] + s * nx, q[1] + s * ny, q[2] + 0.14)], mt, uvs=[(0, 0)] * 4)


def _telhado_cone(g, x, y, z, r, h, mt, seg=10):
    for i in range(seg):
        a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
        g.face([(x + r * math.cos(a0), y + r * math.sin(a0), z), (x + r * math.cos(a1), y + r * math.sin(a1), z), (x, y, z + h)], mt, uvs=[(0, 0), (1, 0), (0.5, 1)],
               nrm=[(math.cos(a0) * 0.7, math.sin(a0) * 0.7, 0.7), (math.cos(a1) * 0.7, math.sin(a1) * 0.7, 0.7), (0, 0, 1)])
        g.face([(x + r * math.cos(a1), y + r * math.sin(a1), z), (x + r * math.cos(a0), y + r * math.sin(a0), z), (x, y, z + h)], mt, uvs=[(0, 0), (1, 0), (0.5, 1)], cor=0.7)


def casinha(g):
    """Casinha de toras (09-playground), frente em +x."""
    for k in range(7):
        z = k * 0.18
        mt = 'plastico_laranja' if k % 2 else 'plastico_marrom'
        for s in (-1, 1):
            g.tubo([(-0.5, s * 0.5, z + 0.09), (0.5, s * 0.5, z + 0.09)], 0.09, mt, seg=6)
        g.tubo([(-0.5, -0.5, z + 0.09), (-0.5, 0.5, z + 0.09)], 0.09, mt, seg=6)
        if k > 3:
            g.tubo([(0.5, -0.5, z + 0.09), (0.5, 0.5, z + 0.09)], 0.09, mt, seg=6)
    for s in (-1, 1):
        g.tubo([(0.5, s * 0.5, 0), (0.5, s * 0.25, 0.75)], 0.09, 'plastico_laranja', seg=6)
    _telhado_cone(g, 0, 0, 1.25, 0.95, 0.55, 'plastico_verde', seg=4)


def brinquedo(g):
    """Torres de playground com escorregadores, tunel e escalada (09-playground). Eixo longo em x."""
    N1, N2 = 1.4, 1.5
    for (tx, h, cor) in ((-1.2, N1, 'plastico_azulc'), (1.2, N2, 'plastico_vermelho')):
        for sx in (-1, 1):
            for sy in (-1, 1):
                _poste_play(g, tx + sx * 0.6, sy * 0.6, 3.0)
        g.caixa(tx - 0.65, tx + 0.65, -0.65, 0.65, h - 0.06, h, 'plastico_marrom', sem_fundo=False)
        # guardas
        for sy in (-1, 1):
            g.caixa(tx - 0.58, tx + 0.58, sy * 0.6 - 0.03, sy * 0.6 + 0.03, h + 0.1, h + 0.8, cor)
    # telhados
    _telhado_cone(g, 1.2, 0, 3.0, 1.15, 0.7, 'plastico_verde')
    g.cil(-1.2, 0, 0.08, 3.0, 3.75, 'plastico_marrom', seg=8)
    for k in range(7):
        a = k * 6.283 / 7
        ca, sa = math.cos(a), math.sin(a)
        g.face([(-1.2, 0, 3.75), (-1.2 + ca * 0.95 - sa * 0.22, sa * 0.95 + ca * 0.22, 3.42), (-1.2 + ca * 0.95 + sa * 0.22, sa * 0.95 - ca * 0.22, 3.42)], 'plastico_verde', uvs=[(0, 0)] * 3)
        g.face([(-1.2, 0, 3.75), (-1.2 + ca * 0.95 + sa * 0.22, sa * 0.95 - ca * 0.22, 3.42), (-1.2 + ca * 0.95 - sa * 0.22, sa * 0.95 + ca * 0.22, 3.42)], 'plastico_verde', uvs=[(0, 0)] * 3, cor=0.7)
    # tunel amarelo entre as torres
    g.tubo([(-0.6, 0, 1.75), (-0.1, 0, 1.95), (0.1, 0, 1.95), (0.6, 0, 1.75)], 0.42, 'plastico_amarelo', seg=12)
    # escorregadores
    _escorrega(g, (1.85, 0, N2), (4.0, 0.2, 0.28), 0.55, 'plastico_verde')
    _escorrega(g, (-1.85, 0, N1), (-3.9, -0.1, 0.28), 0.55, 'plastico_vermelho')
    # parede de escalada azul com pegas
    g.caixa(0.75, 1.65, 0.65, 0.72, 0.0, 1.5, 'plastico_azulc')
    for k in range(9):
        g.elipsoide(0.82 + (k % 3) * 0.3, 0.74, 0.25 + (k // 3) * 0.45, 0.05, 0.03, 0.05, 'plastico_amarelo', seg=6, aneis=3)
    # escada com degraus
    for k in range(5):
        g.caixa(-1.1, -0.5, -0.65 - 0.8 + k * 0.17, -0.65 - 0.65 + k * 0.17, 0.22 + k * 0.28, 0.27 + k * 0.28, 'plastico_laranja', sem_fundo=False)
    for s in (-1.1, -0.5):
        g.tubo([(s, -1.45, 0.0), (s, -0.65, 1.4)], 0.03, 'plastico_marrom', seg=5)
    # caracol lateral (escorregador azul claro)
    _escorrega(g, (1.2, -0.65, 1.0), (1.2, -2.5, 0.25), 0.5, 'plastico_azulc')


def playground_moveis(g):
    z = Z_PISO
    with g.em(X(2004), Y(1000), z, 0):
        g.sombra(-4.5, 4.5, -2.5, 2.5, 0.012)
        brinquedo(g)
    with g.em(X(2030), Y(1062), z, 180):
        g.sombra(-0.95, 0.95, -0.95, 0.95, 0.012)
        casinha(g)
    # gira-gira de mola e brinquedos soltos do plano
    for px, py, mt in ((1970, 935, 'plastico_laranja'), (1980, 948, 'plastico_vermelho')):
        with g.em(X(px), Y(py), z):
            g.cil(0, 0, 0.1, 0, 0.3, 'metal_preto', seg=8, tampa=False)
            g.elipsoide(0, 0, 0.42, 0.42, 0.14, 0.14, mt, seg=10, aneis=5, exp=0.7)
            g.tubo([(0.2, -0.1, 0.5), (0.2, 0.1, 0.5)], 0.02, 'metal_preto', seg=4)
    g.elipsoide(X(2020), Y(960), z + 0.11, 0.11, 0.11, 0.11, 'plastico_laranja', seg=10, aneis=6)
    g.caixa(X(2028), X(2032), Y(958), Y(954), z, z + 0.3, 'plastico_vermelho', topo='plastico_amarelo')
    # bancos de concreto em volta (12-bikeshare)
    for x0, x1, y0, y1 in ((1970, 2008, 1088, 1092), (2030, 2055, 1088, 1092)):
        g.caixa(X(x0), X(x1), Y(y1), Y(y0), Z_PISO, Z_PISO + 0.45, 'quadra_azul', topo='quadra_borda')


# ------------------------------------------------------------------ crossfit e praca (07-crossfit)
def gaiola_cross(g):
    M = 'metal_preto'
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.tubo([(sx * 1.0, sy * 0.6, 0), (sx * 1.0, sy * 0.6, 2.5)], 0.04, M, seg=6)
    for sy in (-1, 1):
        g.tubo([(-1.0, sy * 0.6, 2.5), (1.0, sy * 0.6, 2.5)], 0.03, M, seg=6)
    for sx in (-1, 0, 1):
        g.tubo([(sx * 1.0, -0.6, 2.5), (sx * 1.0, 0.6, 2.5)], 0.03, M, seg=6)


def crossfit_moveis(g):
    z = Z_PISO
    x0, x1, y0, y1 = RM(PL.CROSSFIT)
    # pista azul com degraus (agilidade), pisada no paver
    a, b, c, d = RM(PL.PISTA_CROSSFIT)
    for xx in (a, b):
        g.piso(xx - 0.06, xx + 0.06, c, d, z + 0.004, 'ep_azul')
    p = c
    while p < d:
        g.piso(a, b, p - 0.05, p + 0.05, z + 0.004, 'ep_azul')
        p += 1.2
    with g.em(X(2240), Y(905), z, 90):
        g.piso(-2.2, 2.2, -1.2, 1.2, 0.006, 'ep_preto')
        g.sombra(-1.3, 1.3, -0.9, 0.9, 0.012)
        gaiola_cross(g)
    # colchonete, kettlebells, halteres azuis, caixotes de madeira, corda
    g.caixa(X(2222), X(2238), Y(942), Y(932), z, z + 0.05, 'ep_preto')
    for k, dx in enumerate((0, 0.32, 0.64)):
        px = X(2243) + dx
        g.elipsoide(px, Y(915), z + 0.13, 0.11, 0.11, 0.13, 'metal_preto', seg=8, aneis=5)
    for k in range(2):
        halter(g, X(2224) + k * 0.6, Y(925), z, comp=0.3, r=0.07, mt='plastico_azul')
    for px, py, l_ in ((2258, 925, 0.55), (2258, 936, 0.55)):
        g.caixa(X(px) - l_ / 2, X(px) + l_ / 2, Y(py) - l_ / 2, Y(py) + l_ / 2, z, z + l_, 'madeira_clara')
    pts = [(X(2222) + k * 0.25, Y(948) + 0.1 * math.sin(k * 1.2), z + 0.03) for k in range(14)]
    g.tubo(pts, 0.022, 'tecido_bege', seg=5)
    # bancos de concreto
    for px0, py0, px1, py1 in ((2164, 900, 2170, 920), (2164, 930, 2170, 950)):
        g.caixa(X(px0), X(px1), Y(py1), Y(py0), z, z + 0.45, 'pingadeira', topo='madeira')


# ------------------------------------------------------------------ pracas: jogos, piquenique, lounge, pet, bicicletario
def mesa_ping_pong(g):
    g.caixa(-1.37, 1.37, -0.76, 0.76, 0.74, 0.77, 'tecido_escuro')
    g.caixa(-0.01, 0.01, -0.85, 0.85, 0.77, 0.92, 'plastico_branco')
    for sx in (-1, 1):
        g.tubo([(sx * 0.9, -0.7, 0.74), (sx * 0.55, -0.7, 0), (sx * 0.55, 0.7, 0), (sx * 0.9, 0.7, 0.74)], 0.03, 'plastico_laranja', seg=5)
        g.tubo([(sx * 0.9, -0.7, 0.74), (sx * 0.9, 0.7, 0.74)], 0.03, 'plastico_laranja', seg=5)


def mesa_piquenique(g):
    """Mesa com bancos integrados, eixo x."""
    g.caixa(-1.0, 1.0, -0.38, 0.38, 0.72, 0.76, 'madeira')
    for s in (-1, 1):
        g.caixa(-1.0, 1.0, s * 0.72 - 0.15, s * 0.72 + 0.15, 0.42, 0.46, 'madeira')
    for xx in (-0.72, 0.72):
        g.tubo([(xx, -0.72, 0), (xx, 0.3, 0.72)], 0.035, 'madeira', seg=4)
        g.tubo([(xx, 0.72, 0), (xx, -0.3, 0.72)], 0.035, 'madeira', seg=4)
        g.caixa(xx - 0.03, xx + 0.03, -0.72, 0.72, 0.38, 0.42, 'madeira')


def bicicleta(g, cor='plastico_vermelho'):
    """Bicicleta eixo x."""
    for ex in (-0.5, 0.5):
        pts = [(ex + 0.33 * math.cos(2 * math.pi * k / 16), 0, 0.33 + 0.33 * math.sin(2 * math.pi * k / 16)) for k in range(17)]
        g.tubo(pts, 0.012, 'metal_preto', seg=4)
    for p, q in (((-0.5, 0, 0.33), (-0.1, 0, 0.35)), ((-0.1, 0, 0.35), (0.3, 0, 0.72)), ((-0.1, 0, 0.35), (-0.2, 0, 0.76)), ((-0.2, 0, 0.76), (0.3, 0, 0.72)),
                 ((-0.5, 0, 0.33), (-0.2, 0, 0.76)), ((0.5, 0, 0.33), (0.3, 0, 0.82))):
        g.tubo([p, q], 0.016, cor, seg=4)
    g.elipsoide(-0.22, 0, 0.8, 0.11, 0.05, 0.025, 'plastico_preto', seg=6, aneis=3)
    g.tubo([(0.3, -0.2, 0.86), (0.3, 0.2, 0.86)], 0.012, 'metal_preto', seg=4)


def bicicletario_moveis(g):
    x0, x1, y0, y1 = RM(PL.BICICLETARIO)
    z = Z_PISO
    n = 6
    for k in range(n):
        xx = x0 + 0.5 + k * (x1 - x0 - 1.0) / (n - 1)
        with g.em(xx, y0 + 1.5, z, 90):
            g.tubo([(-0.35, 0, 0), (-0.35, 0, 0.72), (0.35, 0, 0.72), (0.35, 0, 0)], 0.02, 'cromo', seg=5)
            if k % 2 == 0 or k == 3:
                with g.em(0.1, 0.12, 0):
                    bicicleta(g, ('plastico_vermelho', 'plastico_azulc', 'tecido_escuro', 'plastico_amarelo')[k % 4])


def lounge_moveis(g):
    z = Z_PISO
    x0, x1, y0, y1 = RM(PL.LOUNGE_TEEN)
    cx, cy = (x0 + x1) / 2 + 0.3, (y0 + y1) / 2 - 1.0
    with g.em(cx, cy, z):
        g.sombra(-1.8, 1.8, -1.8, 1.8, 0.012, disco=True)
        g.caixa(-0.5, 0.5, -0.5, 0.5, 0, 0.36, 'madeira')
    for dx, dy, giro in ((-1.3, 0.8, 200), (1.3, 0.8, -20), (-1.3, -0.9, 150), (1.3, -0.9, 30)):
        with g.em(cx + dx, cy + dy, z, giro):
            g.elipsoide(0, 0, 0.26, 0.48, 0.46, 0.26, 'tecido_bege', seg=12, aneis=5, exp=0.8, zmin=-0.9)
    # lounge teen do patio (T3 e T2): bicicletas e bancos
    for px, py in ((405, 985), (1026, 510)):
        for k in range(3):
            with g.em(X(px) + k * 0.65 - 0.65, Y(py), Z_PASSEIO, 90):
                bicicleta(g, ('plastico_vermelho', 'plastico_azulc', 'tecido_escuro')[k])
        g.caixa(X(px) - 0.9, X(px) + 0.9, Y(py) + 1.5, Y(py) + 1.9, Z_PASSEIO, Z_PASSEIO + 0.45, 'pingadeira', topo='madeira')


def pet_moveis(g):
    x0, x1, y0, y1 = RM(PL.PET)
    # circuito de agilidade (13-petplace): cones e barra, rampa, tunel
    for k, py in enumerate((1003, 1014, 1025)):
        cor = ('plastico_azulc', 'plastico_amarelo', 'plastico_vermelho')[k]
        px0, px1 = X(1000), X(1020)
        yy = Y(py)
        for xx in (px0, px1):
            g.cil(xx, yy, 0.12, 0, 0.4, cor, seg=8, r2=0.02)
        g.tubo([(px0, yy, 0.3), (px1, yy, 0.3)], 0.02, 'plastico_branco', seg=5)
    with g.em(X(1012), Y(1088), 0, 20):
        g.tubo([(-0.7, 0, 0.32), (0.7, 0, 0.32)], 0.32, 'plastico_azulc', seg=10)
    with g.em(X(1000), Y(1052), 0, -30):
        g.face([(-0.7, -0.25, 0), (0.0, -0.25, 0.42), (0.0, 0.25, 0.42), (-0.7, 0.25, 0)], 'plastico_laranja', uvs=[(0, 0)] * 4)
        g.face([(0.0, -0.25, 0.42), (0.7, -0.25, 0), (0.7, 0.25, 0), (0.0, 0.25, 0.42)], 'plastico_amarelo', uvs=[(0, 0)] * 4)
    # bancada de apoio em concreto com cuba, nichos e toalhas
    ax0, ax1 = X(1022), X(1036)
    ay = Y(980)
    g.caixa(ax0, ax1, ay - 1.2, ay + 1.2, Z_PASSEIO, Z_PASSEIO + 0.82, 'parede_corte', topo='pedra_granito')
    g.caixa(ax0, ax1, ay + 1.2, ay + 1.3, Z_PASSEIO, Z_PASSEIO + 1.3, 'parede_corte')


def foodtruck(g):
    """Van-food truck retro generica: frente em +x. Medidas ~4,7 x 2,0 x 2,6."""
    A, B = 'truck_amarelo', 'truck_branco'
    L_, W_ = 2.35, 1.0
    # chassi e parte inferior
    g.caixa_red(-L_, L_ - 0.5, -W_, W_, 0.42, 1.2, 0.12, A, passos=2)
    g.caixa_red(-L_, L_ - 0.65, -W_ * 0.98, W_ * 0.98, 1.2, 2.45, 0.14, B, topo=B, passos=2)
    g.caixa_red(-L_ + 0.05, L_ - 0.7, -W_ * 0.9, W_ * 0.9, 2.45, 2.55, 0.14, 'caixilho_ext', passos=2)
    # cabine e capo
    g.caixa_red(L_ - 1.1, L_ + 0.1, -W_ * 0.96, W_ * 0.96, 0.42, 1.28, 0.2, A, passos=3)
    g.face([(L_ - 0.1, -W_ * 0.88, 1.28), (L_ - 0.1, W_ * 0.88, 1.28), (L_ - 0.65, W_ * 0.86, 2.3), (L_ - 0.65, -W_ * 0.86, 2.3)], 'vidro_escuro', uvs=[(0, 0)] * 4)
    for s in (-1, 1):
        y_ = s * W_ * 0.975
        cos = [(L_ - 0.1, y_, 1.28), (L_ - 0.72, y_, 1.28), (L_ - 0.72, y_, 2.28), (L_ - 0.65, y_, 2.3)]
        g.face(cos if s > 0 else cos[::-1], 'vidro_escuro', uvs=[(0, 0)] * 4)
        g.caixa(L_ - 0.32, L_ + 0.05, s * 0.72, s * 0.9, 0.72, 0.88, 'farol')
        for ex in (1.35, -1.35):
            yc = s * (W_ - 0.05)
            r = 0.42
            seg = 14
            for i in range(seg):
                a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
                g.face([(ex + r * math.cos(a1), yc + 0.12, r + r * math.sin(a1)), (ex + r * math.cos(a0), yc + 0.12, r + r * math.sin(a0)),
                        (ex + r * math.cos(a0), yc - 0.12, r + r * math.sin(a0)), (ex + r * math.cos(a1), yc - 0.12, r + r * math.sin(a1))], 'pneu', uvs=[(0, 0)] * 4)
            yf = yc + s * 0.125
            pts = [(ex + 0.38 * math.cos(2 * math.pi * i / seg), yf, r + 0.38 * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
            g.face(pts[::-1] if s > 0 else pts, 'pneu', uvs=[(0, 0)] * seg)
            pts = [(ex + 0.24 * math.cos(2 * math.pi * i / seg), yf + s * 0.004, r + 0.24 * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
            g.face(pts[::-1] if s > 0 else pts, 'cromo', uvs=[(0, 0)] * seg)
    # para-choque e grade
    g.caixa_red(L_ + 0.04, L_ + 0.18, -W_, W_, 0.42, 0.58, 0.04, 'cromo', passos=2)
    for k in range(5):
        g.caixa(L_ + 0.1, L_ + 0.11, -0.45, 0.45, 0.62 + k * 0.06, 0.65 + k * 0.06, 'cromo')
    # janela de atendimento no lado +y (voltada para as mesas), toldo e balcao
    jy = W_ * 0.98 + 0.005
    g.painel(0.5, jy, -1.5, jy, 1.2, 2.2, 'tela', ATL['truck_janela'])
    g.caixa(-1.55, 0.55, W_ * 0.98, W_ * 0.98 + 0.28, 1.14, 1.2, 'madeira', sem_fundo=False)
    g.face([(-1.6, jy, 2.32), (0.6, jy, 2.32), (0.6, jy + 0.9, 2.1), (-1.6, jy + 0.9, 2.1)][::-1], 'ep_amarelo', uvs=[(0, 0)] * 4)
    g.face([(-1.6, jy, 2.32), (0.6, jy, 2.32), (0.6, jy + 0.9, 2.1), (-1.6, jy + 0.9, 2.1)], 'truck_amarelo', uvs=[(0, 0)] * 4)
    # lanterna traseira
    for s in (-1, 1):
        g.caixa(-L_ - 0.01, -L_ + 0.02, s * 0.6, s * 0.85, 0.75, 0.95, 'lanterna')


def foodtruck_moveis(g):
    x0, x1, y0, y1 = RM(PL.FOODTRUCK)
    cx, cy = (x0 + x1) / 2 + 0.05, (y0 + y1) / 2
    with g.em(cx, cy, Z_PISO - 0.14, 90 - 180):      # frente para o sul da planta; janela para o leste
        g.sombra(-2.6, 2.6, -1.3, 1.3, 0.16, forca=0.6)
        foodtruck(g)
    for px, py in PL.MESAS_FOODTRUCK:
        mesa_com_cadeiras(g, X(px) - 4.0, Y(py), 0, 'externa', 0.8)
    # lousa de menu
    with g.em(X(2132), Y(1165), Z_PISO, 0):
        g.painel(0, -0.3, 0, 0.3, 0.1, 1.15, 'atlas', ATL['menu'])
        g.tubo([(-0.2, -0.28, 0), (0.0, -0.28, 1.15)], 0.012, 'madeira', seg=3)
        g.tubo([(-0.2, 0.28, 0), (0.0, 0.28, 1.15)], 0.012, 'madeira', seg=3)
    # varal de lampadas da van ate a palmeira e o apoio
    a = (X(2127), Y(1148), 2.6)
    b = (X(2175), Y(1150), 3.2)
    pts = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t - 0.55 * math.sin(math.pi * t)) for t in np.linspace(0, 1, 15)]
    g.tubo(pts, 0.008, 'metal_preto', seg=3)
    for p in pts[1:-1]:
        g.elipsoide(p[0], p[1], p[2] - 0.05, 0.05, 0.05, 0.06, 'luz_led', seg=6, aneis=3)
    g.cil(b[0], b[1], 0.05, 0.14, 3.3, 'ferro_escuro', seg=6, tampa=False)
    g.cil(a[0] + 0.0, a[1] + 0.3, 0.04, 0.14, 2.7, 'ferro_escuro', seg=6, tampa=False)


def pracas_moveis(g):
    z = Z_PISO
    with g.em(X(1885), Y(946), z, 0):
        g.sombra(-1.75, 1.75, -1.1, 1.1, 0.012)
        mesa_ping_pong(g)
    for px, py, giro in ((1865, 898, 90), (1913, 898, 90), (1890, 880, 0)):
        with g.em(X(px), Y(py), 0.0, giro):
            g.sombra(-1.3, 1.3, -1.1, 1.1, 0.012)
            mesa_piquenique(g)
    # manta xadrez e bola no gramado
    g.tapete(X(1896), X(1912), Y(902), Y(892), 0.03, 'tecido_xadrez', (0, 0, 1, 1))
    g.elipsoide(X(1928), Y(958), z + 0.11, 0.11, 0.11, 0.11, 'plastico_branco', seg=10, aneis=6)


def moveis(g):
    academia_moveis(g)
    pub_moveis(g)
    brinq_moveis(g)
    salao_moveis(g)
    churrasqueira_moveis(g)
    gourmet_moveis(g)
    salas_torres(g)
    delivery_moveis(g)
    deck_moveis(g)
    playground_moveis(g)
    crossfit_moveis(g)
    bicicletario_moveis(g)
    lounge_moveis(g)
    pet_moveis(g)
    foodtruck_moveis(g)
    pracas_moveis(g)

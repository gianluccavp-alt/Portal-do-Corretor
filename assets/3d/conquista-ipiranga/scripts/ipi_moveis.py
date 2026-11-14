# ipi_moveis.py -- pecas de mobiliario e equipamentos (copiadas de alta-vista-mangara/scripts/avm_moveis.py, que
# vieram do Gaia), mais as pecas proprias do Ipiranga no fim (fitness ao ar livre, pet, paraciclo, pendente).
# Cada peca e montada em coordenadas locais (origem no centro, base em z=0). Posicoes em ipi_ambientes.py.

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
    # Ipiranga: cadeiras verde oliva da gourmet, tela bege das cadeiras da piscina, madeira de pinus do fitness
    mat('plastico_oliva', '#6c7a3a', 0.45)
    mat('plastico_cinza', '#c9c7c2', 0.4)
    mat('tecido_areia', '#cbbca0', 0.9, img='tecido.jpg', tint=True, img_mean=0.84, uv=0.25)
    mat('metal_champanhe', '#a49882', 0.35, metal=0.6)
    mat('pinus', '#c9a46e', 0.7, img='madeira_fina.jpg', tint=True, img_mean=0.8, uv=(0.9, 0.3))
    mat('eucalipto', '#7b5236', 0.75, img='madeira_fina.jpg', tint=True, img_mean=0.8, uv=(0.9, 0.3))
    mat('fio_preto', '#151515', 0.6)


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


def cadeira_externa(g, tec='tecido_escuro', M='metal_preto'):
    """Cadeira de varanda em aluminio com tela (05-foodtruck, 15-churrasqueira)."""
    for sy in (-1, 1):
        g.tubo([(0.22, sy * 0.22, 0), (0.22, sy * 0.22, 0.44), (-0.22, sy * 0.22, 0.44), (-0.28, sy * 0.22, 0.88)], 0.012, M, seg=4)
        g.tubo([(-0.22, sy * 0.22, 0), (-0.22, sy * 0.22, 0.44)], 0.012, M, seg=4)
    g.caixa(-0.22, 0.22, -0.22, 0.22, 0.42, 0.45, tec)
    g.face([(-0.22, -0.22, 0.45), (-0.22, 0.22, 0.45), (-0.28, 0.22, 0.88), (-0.28, -0.22, 0.88)], tec, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    g.face([(-0.22, 0.22, 0.45), (-0.22, -0.22, 0.45), (-0.28, -0.22, 0.88), (-0.28, 0.22, 0.88)], tec, uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])


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


def mesa_com_cadeiras(g, x, y, giro=0, tipo='preta', l=0.85, z=None):
    """Mesa com 4 cadeiras (metros)."""
    with g.em(x, y, Z_PISO if z is None else z, giro):
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


def vaso_sanitario(g, x, y, z, giro=0):
    with g.em(x, y, z, giro):
        g.cil(-0.02, 0, 0.16, 0, 0.4, 'plastico_branco', seg=10, r2=0.2)
        g.caixa(-0.34, -0.14, -0.2, 0.2, 0, 0.78, 'plastico_branco')


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


def gaiola_cross(g):
    M = 'metal_preto'
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.tubo([(sx * 1.0, sy * 0.6, 0), (sx * 1.0, sy * 0.6, 2.5)], 0.04, M, seg=6)
    for sy in (-1, 1):
        g.tubo([(-1.0, sy * 0.6, 2.5), (1.0, sy * 0.6, 2.5)], 0.03, M, seg=6)
    for sx in (-1, 0, 1):
        g.tubo([(sx * 1.0, -0.6, 2.5), (sx * 1.0, 0.6, 2.5)], 0.03, M, seg=6)


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



# ------------------------------------------------------------------ pecas do Ipiranga
def barra_fixa(g, n=3, vao=1.3, h=2.4):
    """Postes de eucalipto tratado com barras de ferro entre eles (perspectiva do fitness), alinhados em x."""
    for k in range(n):
        x = (k - (n - 1) / 2) * vao
        g.cil(x, 0, 0.09, 0, h - 0.25 * (k % 2), 'eucalipto', seg=10)
    for k in range(n - 1):
        x0 = (k - (n - 1) / 2) * vao
        zz = h - 0.4 - 0.25 * (k % 2)
        g.tubo([(x0 + 0.08, 0, zz), (x0 + vao - 0.08, 0, zz)], 0.018, 'ferro_escuro', seg=6)


def paralelas(g, comp=2.2, h=1.05):
    """Barras paralelas baixas (eixo x)."""
    for sy in (-0.28, 0.28):
        for sx in (-comp / 2 + 0.1, comp / 2 - 0.1):
            g.cil(sx, sy, 0.05, 0, h, 'eucalipto', seg=8)
        g.tubo([(-comp / 2, sy, h + 0.02), (comp / 2, sy, h + 0.02)], 0.022, 'ferro_escuro', seg=6)


def caixa_plyo(g, l=0.6, p=0.5, h=0.5):
    g.caixa(-l / 2, l / 2, -p / 2, p / 2, 0, h, 'pinus', sem_fundo=True)


def prancha_abdominal(g, comp=1.8):
    """Prancha inclinada de madeira com apoio dos pes (eixo x, alto em +x)."""
    g.face([(-comp / 2, -0.25, 0.12), (comp / 2, -0.25, 0.55), (comp / 2, 0.25, 0.55), (-comp / 2, 0.25, 0.12)], 'pinus',
           uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    g.face([(-comp / 2, 0.25, 0.10), (comp / 2, 0.25, 0.53), (comp / 2, -0.25, 0.53), (-comp / 2, -0.25, 0.10)], 'pinus',
           uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    g.caixa(comp / 2 - 0.1, comp / 2, -0.25, 0.25, 0, 0.55, 'eucalipto')
    g.caixa(-comp / 2, -comp / 2 + 0.1, -0.25, 0.25, 0, 0.12, 'eucalipto')
    g.tubo([(comp / 2 - 0.05, -0.22, 0.75), (comp / 2 - 0.05, 0.22, 0.75)], 0.03, 'tecido_escuro', seg=6)


def bambole_pet(g):
    """Argola de salto do pet place: dois postes amarelos e o aro azul e amarelo (eixo do salto em x)."""
    for sy in (-0.45, 0.45):
        g.cil(0, sy, 0.03, 0, 1.25, 'plastico_amarelo', seg=8)
        g.caixa(-0.18, 0.18, sy - 0.03, sy + 0.03, 0, 0.03, 'plastico_amarelo')
    g.tubo([(0, -0.45, 1.2), (0, 0.45, 1.2)], 0.025, 'plastico_amarelo', seg=6)
    n = 16
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        g.tubo([(0, 0.3 * math.cos(a0), 0.7 + 0.3 * math.sin(a0)), (0, 0.3 * math.cos(a1), 0.7 + 0.3 * math.sin(a1))], 0.05,
               'plastico_azul' if k % 4 < 2 else 'plastico_amarelo', seg=6)
    for sy in (-1, 1):
        g.tubo([(0, sy * 0.33, 0.7), (0, sy * 0.45, 0.7)], 0.012, 'plastico_amarelo', seg=4)


def tunel_pet(g, pts, r=0.32):
    """Tunel de agilidade em listras azul e amarela ao longo de pts (x, y) no chao."""
    for i, (p, q) in enumerate(zip(pts[:-1], pts[1:])):
        g.tubo([(p[0], p[1], r), (q[0], q[1], r)], r, 'plastico_azul' if i % 2 == 0 else 'plastico_amarelo', seg=12)


def paraciclo(g):
    """U invertido de inox (perspectiva do bicicletario), plano x z."""
    pts = [(-0.35, 0, 0)] + [(-0.35 + 0.35 * (1 - math.cos(math.pi * k / 8)), 0, 0.55 + 0.33 * math.sin(math.pi * k / 8)) for k in range(9)] + [(0.35, 0, 0)]
    g.tubo(pts, 0.024, 'inox', seg=6)


def pendente(g, x, y, zt, comp, r=0.05):
    """Lampada de filamento pendurada por um fio desde zt (perspectiva da gourmet)."""
    g.tubo([(x, y, zt), (x, y, zt - comp)], 0.004, 'fio_preto', seg=3)
    g.elipsoide(x, y, zt - comp - r, r * 0.8, r * 0.8, r, 'luz_led', seg=8, aneis=4)


def palmeira_play(g, h=2.6):
    """Coqueiro decorativo do playground: tronco marrom e folhas verdes de plastico."""
    g.cil(0, 0, 0.09, 0, h, 'plastico_marrom', seg=8, r2=0.07)
    for k in range(7):
        a = 2 * math.pi * k / 7
        c, s_ = math.cos(a), math.sin(a)
        g.face([(0, 0, h + 0.05), (c * 0.95 - s_ * 0.22, s_ * 0.95 + c * 0.22, h - 0.3), (c * 0.95 + s_ * 0.22, s_ * 0.95 - c * 0.22, h - 0.3)],
               'plastico_verde', uvs=[(0, 0)] * 3)
        g.face([(0, 0, h + 0.05), (c * 0.95 + s_ * 0.22, s_ * 0.95 - c * 0.22, h - 0.3), (c * 0.95 - s_ * 0.22, s_ * 0.95 + c * 0.22, h - 0.3)],
               'plastico_verde', uvs=[(0, 0)] * 3, cor=0.7)


def banco_jardim(g, comp=1.6):
    """Banco de concreto com assento de madeira (eixo x)."""
    for sx in (-comp / 2 + 0.2, comp / 2 - 0.2):
        g.caixa(sx - 0.08, sx + 0.08, -0.2, 0.2, 0, 0.4, 'concreto')
    g.caixa(-comp / 2, comp / 2, -0.22, 0.22, 0.4, 0.46, 'madeira')


def bola_praia(g, x, y, z, r=0.2):
    """Bola de praia: metade amarela, metade azul."""
    g.elipsoide(x, y, z + r, r, r, r, 'plastico_amarelo', seg=10, aneis=5)
    g.elipsoide(x, y, z + r + 0.004, r * 1.01, r * 0.4, r * 1.01, 'plastico_azulc', seg=10, aneis=5)

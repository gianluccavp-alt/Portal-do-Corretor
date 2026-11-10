# park_patio.py -- chao do condominio a partir de park_chao.json (segmentacao da implantacao por park_mapa.py):
# grama, asfalto com guia, passeios levantados com meio-fio, faixas pintadas, avenida e muros de divisa.
# Executado por park_modelo.py dentro do Blender.
import math

Z_GRAMA, Z_ASF, Z_LINHA, Z_PASSEIO = 0.0, 0.02, 0.045, 0.14
E_GUIA = 0.12

# avenida Luiz Octavio da Silva Whitaker (px): calcada do outro lado, pista, calcada do condominio
AV_CAL_N, AV_PISTA, AV_CAL_S = (177, 228), (228, 341), (341, 394)
AV_X = (30, 2570)


def _ret(g, r, z, mat):
    x0, y0, x1, y1 = r
    g.piso(X(x0), X(x1), Y(y1), Y(y0), z, mat)


def chao(g):
    for r in CHAO['grama']:
        _ret(g, r, Z_GRAMA, 'grama')
    for r in CHAO['asfalto']:
        _ret(g, r, Z_ASF, 'asfalto')
    for r in CHAO['passeio']:
        _ret(g, r, Z_PASSEIO, 'concreto')
    # meio-fio: lateral do passeio levantado
    for x0, y0, x1, y1, lado in CHAO['bordas_passeio']:
        if lado in 'ns':
            _face_y(g, Y(y0), X(x0), X(x1), 0.0, Z_PASSEIO, 'meio_fio', 1 if lado == 'n' else -1)
        else:
            _face_x(g, X(x0), Y(y0), Y(y1), 0.0, Z_PASSEIO, 'meio_fio', 1 if lado == 'l' else -1)
    # guia entre o asfalto e a grama (do lado da grama)
    for x0, y0, x1, y1, lado in CHAO['guias']:
        if lado == 'n':
            g.caixa(X(x0), X(x1), Y(y0), Y(y0) + E_GUIA, 0.0, Z_PASSEIO, 'meio_fio')
        elif lado == 's':
            g.caixa(X(x0), X(x1), Y(y0) - E_GUIA, Y(y0), 0.0, Z_PASSEIO, 'meio_fio')
        elif lado == 'o':
            g.caixa(X(x0) - E_GUIA, X(x0), Y(y1), Y(y0), 0.0, Z_PASSEIO, 'meio_fio')
        else:
            g.caixa(X(x0), X(x0) + E_GUIA, Y(y1), Y(y0), 0.0, Z_PASSEIO, 'meio_fio')
    # faixas pintadas (vagas, zebras, PCD)
    for r in CHAO['linhas']:
        _ret(g, r, Z_LINHA, 'faixa')


def avenida(g):
    """Prolonga a avenida para fora da imagem (a parte dentro dela ja vem da segmentacao) e pinta o eixo."""
    for xa, xb in ((-9000, AV_X[0]), (AV_X[1], 12000)):
        x0, x1 = X(xa), X(xb)
        g.piso(x0, x1, Y(AV_PISTA[1]), Y(AV_PISTA[0]), Z_ASF, 'asfalto')
        for a, b in (AV_CAL_N, AV_CAL_S):
            g.caixa(x0, x1, Y(b), Y(a), 0.0, Z_PASSEIO, 'concreto', lados='meio_fio')
    # eixo tracejado e bordas brancas
    yc = Y((AV_PISTA[0] + AV_PISTA[1]) / 2)
    xx = X(-1500)
    while xx < X(4200):
        g.piso(xx, xx + 3.0, yc - 0.07, yc + 0.07, Z_LINHA, 'faixa')
        xx += 7.0
    for yb in (Y(AV_PISTA[0]) - 0.35, Y(AV_PISTA[1]) + 0.35):
        g.piso(X(-1500), X(4200), yb - 0.06, yb + 0.06, Z_LINHA, 'faixa')


def _muro_seg(g, a, b, h, e, mat='muro_bloco', pilar=3.2):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ang = math.degrees(math.atan2(dy, dx))
    with g.em(a[0], a[1], 0, ang):
        g.caixa(0, L, -e / 2, e / 2, 0, h, mat, topo='pingadeira', sem='ol')
        k = 0.0
        while k <= L:
            g.caixa(k - 0.1, k + 0.1, -e / 2 - 0.03, e / 2 + 0.03, 0, h + 0.03, mat, topo='pingadeira')
            k += pilar


def _gradil_seg(g, a, b, h=2.1):
    """Gradil escuro (frente do condominio) sobre mureta, com pilares."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ang = math.degrees(math.atan2(dy, dx))
    with g.em(a[0], a[1], 0, ang):
        g.caixa(0, L, -0.08, 0.08, 0, 0.45, 'muro_bloco', topo='pingadeira')
        g.painel(0, 0.0, L, 0.0, 0.45, h, 'gradil_preto', (0, 0, L / 2.4, 1))
        g.painel(L, 0.0, 0, 0.0, 0.45, h, 'gradil_preto', (0, 0, L / 2.4, 1))
        k = 0.0
        while k <= L:
            g.caixa(k - 0.09, k + 0.09, -0.09, 0.09, 0, h + 0.05, 'ferragem')
            k += 2.4


def muros_perimetro(g):
    """Muro de bloco nas divisas laterais e de fundo; gradil na frente (avenida), aberto no acesso de veiculos."""
    p = [(X(x), Y(y)) for x, y in PL.TERRENO]       # NO, NE, SE, SO
    _muro_seg(g, p[1], p[2], 2.6, 0.16)
    _muro_seg(g, p[2], p[3], 2.6, 0.16)
    _muro_seg(g, p[3], p[0], 2.6, 0.16)
    yf = Y(PL.TERRENO[0][1])
    for xa, xb in PL.FRENTE_GRADIL:
        _gradil_seg(g, (X(xa), yf), (X(xb), yf))


def jardins_torres(g):
    """Muretas dos gardens do terreo: contorno, divisorias entre quintais e corredor do hall (planta local)."""
    mx, my = PL.GARDEN_MEIA
    dv = PL.GARDEN_DIV_Y
    h, e = 1.5, 0.14

    def mur(x0, x1, y0, y1):
        g.caixa(x0, x1, y0, y1, 0.0, h, 'muro_bloco', topo='pingadeira')

    for (cxp, cyp), giro in PL.TORRES.values():
        with g.em(X(cxp), Y(cyp), 0.0, giro):
            mur(-mx, mx, my - e, my)
            mur(-mx, mx, -my, -my + e)
            mur(mx - e, mx, -my, 1.2)                 # face +x: passagem para o lazer
            mur(mx - e, mx, 2.8, my)
            mur(-mx, -mx + e, -my, -0.9)              # face -x: corredor do hall
            mur(-mx, -mx + e, 0.9, my)
            for s in (1, -1):
                mur(s * X_FACE if s > 0 else -mx, mx if s > 0 else -X_FACE, dv - e / 2, dv + e / 2)
                mur(s * X_FACE if s > 0 else -mx, mx if s > 0 else -X_FACE, -dv - e / 2, -dv + e / 2)
                mur(-e / 2, e / 2, s * L2 if s > 0 else -my, my if s > 0 else -L2)
            mur(X_NOTCH, mx, -e / 2, e / 2)
            for yy in (-0.9, 0.9):
                mur(-mx, -X_NOTCH, yy - e / 2, yy + e / 2)

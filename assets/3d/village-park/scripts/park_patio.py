# park_patio.py -- chao do condominio a partir de park_chao.json (park_mapa.py, poligonos de park_chao_mao.py):
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


def _tri(g, t, z, mat):
    """Triangulo em px virado para cima (a imagem tem y para baixo: o sentido inverte ao passar para metros)."""
    p = [(X(t[0]), Y(t[1]), z), (X(t[2]), Y(t[3]), z), (X(t[4]), Y(t[5]), z)]
    if (p[1][0] - p[0][0]) * (p[2][1] - p[0][1]) - (p[1][1] - p[0][1]) * (p[2][0] - p[0][0]) < 0:
        p.reverse()
    g.face(p, mat)


def _parede(g, a, b, z0, z1, n, mat):
    """Face vertical de a a b (metros) voltada para a normal n (metros, no plano)."""
    cs = [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)]
    # normal de (b - a) x z: (dy, -dx)
    if (b[1] - a[1]) * n[0] - (b[0] - a[0]) * n[1] < 0:
        cs.reverse()
    g.face(cs, mat)


def _trecho(s):
    """[x0, y0, x1, y1, nx, ny] em px -> pontos e normal em metros."""
    a, b = (X(s[0]), Y(s[1])), (X(s[2]), Y(s[3]))
    return a, b, (s[4], -s[5])


def chao(g):
    for t in CHAO['tri_grama']:
        _tri(g, t, Z_GRAMA, 'grama')
    for t in CHAO['tri_asfalto']:
        _tri(g, t, Z_ASF, 'asfalto')
    for t in CHAO['tri_passeio']:
        _tri(g, t, Z_PASSEIO, 'concreto')
    for t in CHAO['tri_faixas']:
        _tri(g, t, Z_LINHA, 'faixa')
    # meio-fio: lateral do passeio levantado
    for s in CHAO['bordas_passeio']:
        a, b, n = _trecho(s)
        _parede(g, a, b, 0.0, Z_PASSEIO, n, 'meio_fio')
    # guia entre o asfalto e a grama, do lado da grama: topo, face para o asfalto e face para a grama
    for s in CHAO['guias']:
        a, b, n = _trecho(s)
        a2, b2 = (a[0] + n[0] * E_GUIA, a[1] + n[1] * E_GUIA), (b[0] + n[0] * E_GUIA, b[1] + n[1] * E_GUIA)
        topo = [(a[0], a[1], Z_PASSEIO), (b[0], b[1], Z_PASSEIO), (b2[0], b2[1], Z_PASSEIO), (a2[0], a2[1], Z_PASSEIO)]
        if (b[0] - a[0]) * (a2[1] - a[1]) - (b[1] - a[1]) * (a2[0] - a[0]) < 0:
            topo.reverse()
        g.face(topo, 'meio_fio')
        _parede(g, a, b, Z_ASF, Z_PASSEIO, (-n[0], -n[1]), 'meio_fio')
        _parede(g, a2, b2, 0.0, Z_PASSEIO, n, 'meio_fio')


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
    """Muretas dos gardens do terreo (planta local da torre), como as linhas finas da implantacao:
    contorno, divisorias entre quintais na divisa das varandas (Y_DIV, Y_BUMP0 e o eixo) e nenhum muro no
    trecho do hall e do final 1, que no terreo e jardim comum (a face -x fica aberta de -Y_DIV a Y_BUMP0)."""
    mx, my = PL.GARDEN_MEIA
    h, e = 1.5, 0.14

    def mur(x0, x1, y0, y1):
        g.caixa(x0, x1, y0, y1, 0.0, h, 'muro_bloco', topo='pingadeira')

    for (cxp, cyp), giro in PL.TORRES.values():
        with g.em(X(cxp), Y(cyp), 0.0, giro):
            mur(-mx, mx, my - e, my)                       # testas (07|06 e 02|03)
            mur(-mx, mx, -my, -my + e)
            mur(mx - e, mx, -my + e, my - e)               # face +x continua (finais 3 a 6)
            mur(-mx, -mx + e, Y_BUMP0, my - e)             # face -x: gardens 08 e 07
            mur(-mx, -mx + e, -my + e, -Y_DIV + e / 2)     # face -x: garden 02
            mur(-e / 2, e / 2, L2, my - e)                 # eixo entre as pontas
            mur(-e / 2, e / 2, -my + e, -L2)
            for yy in (Y_DIV, -Y_DIV):                     # ponta | meio, nas duas faces
                mur(X_FACE, mx - e, yy - e / 2, yy + e / 2)
                mur(-mx + e, -X_FACE, yy - e / 2, yy + e / 2)
            mur(X_NOTCH, mx - e, -e / 2, e / 2)            # 05 | 04
            mur(-mx + e, -X_BUMP, Y_BUMP0, Y_BUMP0 + e)    # fim do garden 08, junto ao hall

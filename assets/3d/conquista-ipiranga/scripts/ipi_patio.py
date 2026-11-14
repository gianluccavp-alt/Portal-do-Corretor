# ipi_patio.py -- chao do condominio a partir de ipi_planta.py: grama no lote, asfalto (poligonos sem
# sobreposicao), vagas de piso drenante, PcD e motos, faixas de pedestre, passeios de paver, pracas de concreto,
# ilhas, a Rua Itajuba com as calcadas e a rua lateral, e os muros (gradil na frente). Executado por ipi_modelo.py.
import math

Z_GRAMA, Z_ASF, Z_VAGA, Z_LINHA, Z_PASSEIO, Z_CALCADA = 0.0, 0.02, 0.03, 0.045, 0.06, 0.12


def P(p):
    return (X(p[0]), Y(p[1]))


def _poly(g, pts_px, z, mat):
    g.poligono([P(p) for p in pts_px], z, mat)


def _quad_cima(g, cs, mat, uvs=None):
    """Quad horizontal garantindo a normal para cima (inverte a ordem e os uvs se preciso)."""
    if _normal(cs)[2] < 0:
        cs = cs[::-1]
        if uvs is not None:
            uvs = uvs[::-1]
    g.face(cs, mat, uvs=uvs)


def _frame(a, b, d):
    """Referencial local de uma fileira: origem em a, x de a para b; devolve (giro, L, prof com sinal)."""
    A, B, D = P(a), P(b), P(d)
    ux, uy = B[0] - A[0], B[1] - A[1]
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    dx, dy = D[0] - A[0], D[1] - A[1]
    prof = -uy * dx + ux * dy           # componente de AD na normal esquerda de AB
    return A, math.degrees(math.atan2(uy, ux)), L, prof


def chao(g):
    _poly(g, PL.TERRENO, Z_GRAMA, 'grama')
    for pol in PL.ASFALTO:
        _poly(g, pol, Z_ASF, 'asfalto')
    for pol in PL.PASSEIOS:
        _poly(g, pol, Z_PASSEIO, 'paver')
    for pol in PL.PRACAS:
        _poly(g, pol, Z_PASSEIO, 'concreto')
    # calcada em curva da entrada (da Rua Itajuba ate a guarita)
    _poly(g, [(3590, 790), (3650, 790), (3650, 985), (3612, 985), (3570, 950), (3510, 1017), (3463, 1083),
              (3430, 1062), (3482, 1000), (3542, 934), (3574, 868), (3582, 820)], Z_CALCADA, 'concreto')
    # ilhas de canteiro com meio-fio
    for x0, y0, x1, y1 in PL.ILHAS:
        mx0, mx1, my0, my1 = X(x0), X(x1), Y(y1), Y(y0)
        g.caixa(mx0, mx1, my0, my1, 0.0, 0.15, 'meio_fio', topo='grama')
    # faixas de pedestre
    for x0, y0, x1, y1, ori in PL.ZEBRAS:
        mx0, mx1, my0, my1 = X(x0), X(x1), Y(y1), Y(y0)
        if ori == 'h':          # listras ao longo de x, empilhadas em y
            yy = my0 + 0.2
            while yy + 0.4 <= my1:
                g.piso(mx0, mx1, yy, yy + 0.4, Z_LINHA, 'faixa'); yy += 0.8
        else:
            xx = mx0 + 0.2
            while xx + 0.4 <= mx1:
                g.piso(xx, xx + 0.4, my0, my1, Z_LINHA, 'faixa'); xx += 0.8


def vagas(g):
    """Fileiras de vagas: piso drenante com uma repeticao da textura por vaga; PcD em concreto com o simbolo e a
    faixa zebrada de 1,20 m entre as duas vagas; motos em concreto com as divisorias brancas."""
    for cs, n, tipo in PL.VAGAS:
        a, b, c, d = cs
        A, giro, L, prof = _frame(a, b, d)
        s = 1 if prof > 0 else -1
        pr = abs(prof)
        with g.em(A[0], A[1], 0.0, giro):
            if tipo == 'carro':
                q = [(0, 0, Z_VAGA), (L, 0, Z_VAGA), (L, s * pr, Z_VAGA), (0, s * pr, Z_VAGA)]
                _quad_cima(g, q, 'vaga_drenante', uvs=[(0, 0), (n, 0), (n, 1), (0, 1)])
            elif tipo == 'pcd':
                q = [(0, 0, Z_VAGA), (L, 0, Z_VAGA), (L, s * pr, Z_VAGA), (0, s * pr, Z_VAGA)]
                _quad_cima(g, q, 'vaga_pcd')
                lv = (L - 1.2) / 2
                for x0 in (0.0, lv, lv + 1.2, L):
                    g.piso(x0 - 0.05, x0 + 0.05, min(0, s * pr) + 0.1, max(0, s * pr) - 0.1, Z_LINHA, 'faixa')
                xx = lv + 0.1                      # zebrado diagonal da faixa de circulacao
                k = 0.25
                yy0, yy1 = sorted((s * 0.3, s * (pr - 0.3)))
                while yy0 + 0.25 < yy1:
                    g.piso(lv + 0.12, lv + 1.08, yy0, yy0 + 0.13, Z_LINHA, 'faixa'); yy0 += 0.55
                r_ = MARCAS['pcd']
                for xc in (lv / 2, lv + 1.2 + lv / 2):
                    yc = s * pr * 0.55
                    g.tapete(xc - 0.75, xc + 0.75, yc - 0.75, yc + 0.75, Z_LINHA + 0.003, 'marcas', r_, gira=(s < 0))
            else:   # moto
                q = [(0, 0, Z_VAGA), (L, 0, Z_VAGA), (L, s * pr, Z_VAGA), (0, s * pr, Z_VAGA)]
                _quad_cima(g, q, 'concreto')
                for k in range(n + 1):
                    xx = L * k / n
                    g.piso(xx - 0.04, xx + 0.04, min(0, s * pr) + 0.05, max(0, s * pr) - 0.05, Z_LINHA, 'faixa')


def ruas(g):
    """Rua Itajuba (pista de ~10 m com a faixa dupla no eixo), calcadas e a rua lateral a leste."""
    x0, x1 = PL.RUA_X
    c0, c1 = PL.CALCADA_X
    yl0, yl1 = PL.RUA_LATERAL_Y
    ext0, ext1 = -1800, 3800              # px: a rua continua para fora da imagem
    g.piso(X(x0), X(x1), Y(ext1), Y(ext0), Z_ASF, 'asfalto')
    # calcada do lote (sem a curva e os acessos, que estao no terreno)
    for ya, yb in ((ext0, 790), (1360, ext1)):
        g.caixa(X(c0), X(c1), Y(yb), Y(ya), 0.0, Z_CALCADA, 'meio_fio', topo='concreto')
    # calcada oposta, interrompida pela rua lateral
    xo = x1 + PL.CALCADA_OPOSTA
    for ya, yb in ((ext0, yl0), (yl1, ext1)):
        g.caixa(X(x1), X(xo), Y(yb), Y(ya), 0.0, Z_CALCADA, 'meio_fio', topo='concreto')
    # rua lateral e as calcadas dela
    xl1 = x1 + 1400
    g.piso(X(x1), X(xl1), Y(yl1), Y(yl0), Z_ASF - 0.004, 'asfalto')
    for ya, yb in ((yl0 - 65, yl0), (yl1, yl1 + 65)):
        g.caixa(X(xo), X(xl1), Y(yb), Y(ya), 0.0, Z_CALCADA, 'meio_fio', topo='concreto')
    # faixa dupla no eixo e linhas de bordo
    xm = (x0 + x1) / 2
    for dx in (-5, 5):
        g.piso(X(xm + dx) - 0.06, X(xm + dx) + 0.06, Y(ext1), Y(ext0), Z_LINHA, 'faixa')
    for xx in (x0 + 8, x1 - 8):
        for ya, yb in ((ext0, yl0 - 5), (yl1 + 5, ext1)) if xx > xm else ((ext0, ext1),):
            g.piso(X(xx) - 0.05, X(xx) + 0.05, Y(yb), Y(ya), Z_LINHA, 'faixa')


def _muro_seg(g, a, b, h, e, mat='muro_liso', pilar=3.0):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ang = math.degrees(math.atan2(dy, dx))
    with g.em(a[0], a[1], 0, ang):
        g.caixa(0, L, -e / 2, e / 2, 0, h, mat, topo='pingadeira', sem='ol')
        k = 0.0
        while k <= L:
            g.caixa(k - 0.12, k + 0.12, -e / 2 - 0.03, e / 2 + 0.03, 0, h + 0.04, mat, topo='pingadeira')
            k += pilar


def _gradil_frente(g, a, b, hm=0.9, hg=1.3):
    """Mureta taupe com gradil preto por cima (frente na Rua Itajuba, como na perspectiva do acesso)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ang = math.degrees(math.atan2(dy, dx))
    with g.em(a[0], a[1], 0, ang):
        g.caixa(0, L, -0.1, 0.1, 0, hm, 'muro_base', topo='pingadeira')
        g.painel(0, 0.0, L, 0.0, hm, hm + hg, 'gradil_preto', (0, 0, L / 2.0, 1))
        g.painel(L, 0.0, 0, 0.0, hm, hm + hg, 'gradil_preto', (0, 0, L / 2.0, 1))
        g.caixa(0, L, -0.03, 0.03, hm + hg - 0.05, hm + hg, 'ferro_escuro')
        k = 0.0
        while k <= L:
            g.caixa(k - 0.04, k + 0.04, -0.04, 0.04, hm, hm + hg, 'ferro_escuro')
            k += 2.0


def _portao(g, a, b, h=2.2):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ang = math.degrees(math.atan2(dy, dx))
    with g.em(a[0], a[1], 0, ang):
        g.painel(0, 0.0, L, 0.0, 0.05, h, 'gradil_preto', (0, 0, L / 2.0, 1))
        g.painel(L, 0.0, 0, 0.0, 0.05, h, 'gradil_preto', (0, 0, L / 2.0, 1))
        g.caixa(0, L, -0.04, 0.04, h - 0.08, h, 'ferro_escuro')
        for k in (0.0, L):
            g.caixa(k - 0.15, k + 0.15, -0.15, 0.15, 0, h + 0.15, 'muro_base', topo='pingadeira')


def muros_perimetro(g):
    """Muro liso nas divisas com os vizinhos; na frente (Rua Itajuba) mureta com gradil, aberta entre a curva da
    calcada e a saida; portao de correr na linha da guarita."""
    t = PL.TERRENO
    n = len(t)
    ya, yb = PL.FRENTE_ABERTA_Y
    for i in range(n):
        a, b = t[i], t[(i + 1) % n]
        if a[0] == b[0] == 3590:
            y0, y1 = sorted((a[1], b[1]))
            if y0 < ya:
                _gradil_frente(g, P((3590, y0)), P((3590, ya)))
            if y1 > yb:
                _gradil_frente(g, P((3590, yb)), P((3590, y1)))
            continue
        _muro_seg(g, P(a), P(b), 2.4, 0.16)
    _portao(g, P(PL.PORTAO[0]), P(PL.PORTAO[1]))
    _portao(g, P(PL.PORTAO_PEDESTRE[0]), P(PL.PORTAO_PEDESTRE[1]))

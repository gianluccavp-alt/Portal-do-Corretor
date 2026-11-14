# cpr_patio.py -- chao do condominio a partir de cpr_planta.py: grama no lote, rua interna de asfalto, vagas
# descobertas (asfalto com faixas brancas, PcD com o simbolo e a zebra de 1,20 m, carro eletrico), passeios de paver,
# pracas de concreto, o edificio-garagem (terreo com as vagas, coberturas metalicas, nucleo de escada e a rampa que
# desce para o subsolo), muros (gradil na frente da avenida) e a Avenida Maria Emilia com a alca de embarque.
# Executado por cpr_modelo.py.
import math

Z_GRAMA, Z_ASF, Z_VAGA, Z_LINHA, Z_PASSEIO, Z_CALCADA = 0.0, 0.02, 0.025, 0.035, 0.06, 0.12
Z_DECK_G = 0.03                  # piso do terreo da garagem
H_COB = (2.55, 2.85)             # coberturas metalicas das vagas (beiral baixo e alto)


def materiais_patio():
    mat('grama', '#ffffff', 0.97, img='grama2.jpg', uv=6.0)
    mat('grama_garden', '#e9f0dc', 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=4.0)
    mat('entorno', (0.62, 0.62, 0.50), 0.97, img='grama2.jpg', tint=True, img_mean=1.0, uv=14.0)
    mat('asfalto', '#ffffff', 0.92, img='asfalto2.jpg', uv=8.0)
    mat('piso_garagem', '#8d8f92', 0.85, img='concreto.jpg', tint=True, uv=5.0)
    mat('concreto', '#cfccc4', 0.88, img='concreto.jpg', tint=True, uv=4.0)
    mat('paver', '#a3a19c', 0.9, img='paver.jpg', tint=True, img_mean=0.74, uv=2.4)
    mat('vaga_eletrica', '#9da7a0', 0.88, img='concreto.jpg', tint=True, uv=4.0)
    mat('meio_fio', '#c8c5bc', 0.9)
    mat('faixa', '#f0f0ea', 0.75)
    mat('faixa_amarela', '#e3b62c', 0.75)
    mat('pcd_azul', '#2f63b0', 0.8)
    mat('marcas', '#ffffff', 0.8, img='piso_marcas.png', recorte=True)
    mat('sombra_contato', '#ffffff', 1.0, img='piso_marcas.png', blend_img=True)
    mat('muro_liso', '#d6d2ca', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('muro_base', '#8d8a85', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('parede_externa', '#d9d5cd', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('garagem_parede', '#b9b6b0', 0.93, img='reboco_fino.jpg', tint=True, img_mean=0.88, nrm='reboco_fino_n.jpg', nrm_str=0.7, uv=TILE)
    mat('telha_metalica', '#c7c9cb', 0.6, img='ripado.jpg', tint=True, img_mean=0.82, uv=(0.9, 0.9), metal=0.2)
    mat('estrutura_escura', '#2c2e31', 0.55, metal=0.35)
    mat('rampa', '#8f9193', 0.85, img='concreto.jpg', tint=True, uv=3.0)
    mat('vao_escuro', '#1d1f22', 0.95)
    mat('sebe', '#5f8a45', 0.95, img='grama2.jpg', tint=True, img_mean=1.0, uv=1.5)


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
    """Referencial local de uma fileira: origem em a, x de a para b; devolve (A, giro, L, prof com sinal)."""
    A, Bp, D = P(a), P(b), P(d)
    ux, uy = Bp[0] - A[0], Bp[1] - A[1]
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    dx, dy = D[0] - A[0], D[1] - A[1]
    prof = -uy * dx + ux * dy
    return A, math.degrees(math.atan2(uy, ux)), L, prof


def RM(r):
    """retangulo em px -> (x0, x1, y0, y1) em metros, com y0 < y1"""
    return X(r[0]), X(r[2]), Y(r[3]), Y(r[1])


def chao(g):
    for pol in PL.GRAMA_LOTE:
        _poly(g, pol, Z_GRAMA, 'grama')
    for pol in PL.ASFALTO:
        _poly(g, pol, Z_ASF, 'asfalto')
    for pol in PL.PASSEIOS:
        _poly(g, pol, Z_PASSEIO, 'paver')
    for pol in PL.PRACAS:
        _poly(g, pol, Z_PASSEIO, 'concreto')
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
    # degraus da escada do passeio norte (so o desenho no piso: o lote e plano na maquete)
    x0, x1, y0, y1 = RM(PL.ESCADA)
    g.piso(x0, x1, y0, y1, Z_PASSEIO + 0.002, 'concreto')
    yy = y0 + 0.15
    while yy < y1:
        g.piso(x0, x1, yy, yy + 0.04, Z_PASSEIO + 0.004, 'meio_fio'); yy += 0.3


def _linhas(g, L, s, pr, n, z, mat='faixa', fundo=True):
    """Divisorias brancas de uma fileira (referencial local): n+1 linhas e a linha do fundo."""
    for k in range(n + 1):
        xx = L * k / n
        g.piso(xx - 0.05, xx + 0.05, min(0, s * pr), max(0, s * pr), z, mat)
    if fundo:
        y = s * (pr - 0.05)
        g.piso(0, L, min(y - 0.05, y + 0.05), max(y - 0.05, y + 0.05), z, mat)


def vagas(g):
    """Fileiras de vagas: no asfalto e no piso da garagem so as faixas brancas (como na implantacao); PcD com o
    simbolo e a zebra de 1,20 m entre as duas vagas; carro eletrico em concreto; motos com divisorias."""
    for cs, n, tipo in PL.VAGAS:
        a, b, c, d = cs
        A, giro, L, prof = _frame(a, b, d)
        s = 1 if prof > 0 else -1
        pr = abs(prof)
        zb = Z_DECK_G if tipo in ('deck', 'moto') else Z_ASF
        with g.em(A[0], A[1], 0.0, giro):
            if tipo in ('asf', 'pcd'):        # vagas descobertas: asfalto continuo com a rua
                _quad_cima(g, [(0, 0, Z_ASF), (L, 0, Z_ASF), (L, s * pr, Z_ASF), (0, s * pr, Z_ASF)], 'asfalto')
            if tipo in ('asf', 'deck'):
                _linhas(g, L, s, pr, n, zb + 0.006)
            elif tipo == 'eletrica':
                q = [(0, 0, Z_VAGA), (L, 0, Z_VAGA), (L, s * pr, Z_VAGA), (0, s * pr, Z_VAGA)]
                _quad_cima(g, q, 'vaga_eletrica')
                _linhas(g, L, s, pr, n, Z_LINHA)
            elif tipo == 'pcd':
                lv = (L - 1.2) / 2
                for x0 in (0.0, lv, lv + 1.2, L):
                    g.piso(x0 - 0.05, x0 + 0.05, min(0, s * pr) + 0.05, max(0, s * pr) - 0.05, Z_LINHA, 'faixa')
                yy0, yy1 = sorted((s * 0.3, s * (pr - 0.3)))
                while yy0 + 0.25 < yy1:
                    g.piso(lv + 0.12, lv + 1.08, yy0, yy0 + 0.13, Z_LINHA, 'faixa'); yy0 += 0.55
                r_ = MARCAS['pcd']
                for xc in (lv / 2, lv + 1.2 + lv / 2):
                    yc = s * pr * 0.55
                    g.piso(xc - 0.8, xc + 0.8, yc - 0.8, yc + 0.8, Z_LINHA - 0.004, 'pcd_azul')
                    g.tapete(xc - 0.75, xc + 0.75, yc - 0.75, yc + 0.75, Z_LINHA + 0.003, 'marcas', r_, gira=(s < 0))
            else:   # moto
                _linhas(g, L, s, pr, n, zb + 0.006, fundo=False)


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


def _gradil(g, a, b, hm=0.6, hg=1.6):
    """Mureta com gradil preto por cima (frente na avenida, "muros e/ou gradis" do FAQ)."""
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
    """Muro liso nas divisas com os vizinhos; na frente (avenida) mureta com gradil, aberta no acesso de veiculos;
    portoes (entrada e saida) recuados na linha da guarita."""
    t = PL.TERRENO
    n = len(t)
    ya, yb = PL.ENTRADA_Y
    for i in range(n):
        a, b = t[i], t[(i + 1) % n]
        if a[0] == b[0] == PL.FRENTE_X:
            y0, y1 = sorted((a[1], b[1]))
            _gradil(g, P((PL.FRENTE_X, y0)), P((PL.FRENTE_X, ya)))
            _gradil(g, P((PL.FRENTE_X, yb)), P((PL.FRENTE_X, y1)))
            continue
        _muro_seg(g, P(a), P(b), 2.4, 0.16)
    # portoes de correr (entrada e saida) e o fechamento entre eles e a divisa
    ym = (ya + yb) / 2
    _portao(g, P((PL.PORTAO_X, ya)), P((PL.PORTAO_X, ym - 2)))
    _portao(g, P((PL.PORTAO_X, ym + 2)), P((PL.PORTAO_X, yb)))


# ------------------------------------------------------------------ edificio-garagem
def _cobertura_vagas(g, r_px):
    """Cobertura metalica de uma agua sobre as vagas (perspectiva 058 e aerea 059): telha clara com rufo, vigas e
    pilares escuros a cada ~5 m nos dois lados maiores."""
    x0, x1, y0, y1 = RM(r_px)
    longo_x = (x1 - x0) >= (y1 - y0)
    zl, zh = H_COB
    e = 0.10
    if longo_x:
        cs = [(x0, y0, zl), (x1, y0, zl), (x1, y1, zh), (x0, y1, zh)]
    else:
        cs = [(x0, y0, zl), (x1, y0, zh), (x1, y1, zh), (x0, y1, zl)]
    g.face(cs, 'telha_metalica')
    g.face([(p[0], p[1], p[2] - e) for p in cs[::-1]], 'telha_metalica')
    # rufo em volta (espessura da telha)
    for i in range(4):
        a, b = cs[i], cs[(i + 1) % 4]
        q = [(a[0], a[1], a[2] - e), (b[0], b[1], b[2] - e), (b[0], b[1], b[2] + 0.02), (a[0], a[1], a[2] + 0.02)]
        if _normal(q)[0] * ((a[0] + b[0]) / 2 - (x0 + x1) / 2) + _normal(q)[1] * ((a[1] + b[1]) / 2 - (y0 + y1) / 2) < 0:
            q = [q[1], q[0], q[3], q[2]]
        g.face(q, 'telha_metalica')
    # pilares e vigas
    L = (x1 - x0) if longo_x else (y1 - y0)
    n = max(1, round(L / 5.0))
    for k in range(n + 1):
        t = k / n
        if longo_x:
            xx = x0 + 0.25 + (x1 - x0 - 0.5) * t
            for yy, zz in ((y0 + 0.3, zl), (y1 - 0.3, zh)):
                g.caixa(xx - 0.08, xx + 0.08, yy - 0.08, yy + 0.08, Z_DECK_G, zz - e, 'estrutura_escura')
            g.caixa(xx - 0.06, xx + 0.06, y0, y1, zl - e - 0.22, zl - e, 'estrutura_escura')
        else:
            yy = y0 + 0.25 + (y1 - y0 - 0.5) * t
            for xx, zz in ((x0 + 0.3, zl), (x1 - 0.3, zh)):
                g.caixa(xx - 0.08, xx + 0.08, yy - 0.08, yy + 0.08, Z_DECK_G, zz - e, 'estrutura_escura')
            g.caixa(x0, x1, yy - 0.06, yy + 0.06, zl - e - 0.22, zl - e, 'estrutura_escura')


def garagem(g):
    """Terreo do edificio-garagem: piso de concreto, mureta na borda, coberturas das vagas, nucleo de escada e
    elevador, faixa dos depositos, bike sharing e a rampa para o subsolo (a garagem do subsolo nao aparece)."""
    # piso, recortando a rampa
    _poly(g, PL.DECK, Z_DECK_G, 'piso_garagem')
    # mureta de 1,10 m nas bordas que dao para a grama (leste, diagonal, sul e oeste ate a passarela)
    for a, b in PL.DECK_MURETA:
        _muro_seg(g, P(a), P(b), 1.10, 0.15, 'garagem_parede', pilar=5.0)
    # faixa dos depositos (o espaco e entregue; a obra e do morador) e bike sharing
    for r in PL.DEPOSITOS:
        x0, x1, y0, y1 = RM(r)
        g.piso(x0, x1, y0, y1, Z_DECK_G + 0.004, 'concreto')
        g.piso(x0, x1, y0 - 0.05, y0 + 0.05, Z_DECK_G + 0.008, 'faixa_amarela')
    x0, x1, y0, y1 = RM(PL.BIKE)
    yy = y0 + 0.6
    while yy < y1 - 0.6:      # setas amarelas (chevrons)
        for s in (-1, 1):
            xm = (x0 + x1) / 2
            z = Z_DECK_G + 0.008
            _quad_cima(g, [(xm, yy + 0.35, z), (xm + s * 0.9, yy - 0.25, z), (xm + s * 0.9, yy - 0.05, z),
                           (xm, yy + 0.55, z)], 'faixa_amarela')
        yy += 1.3
    for r in PL.COBERTURAS:
        _cobertura_vagas(g, r)
    # nucleo de escada e elevador do subsolo
    x0, x1, y0, y1 = RM(PL.NUCLEO_GARAGEM)
    g.caixa(x0, x1, y0, y1, Z_DECK_G, 3.1, 'garagem_parede', topo='cobertura')
    g.caixa(x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2, 3.1, 3.25, 'laje_borda', topo='cobertura')
    g.face([(x1 + 0.012, y0 + 0.4, Z_DECK_G), (x1 + 0.012, y0 + 1.4, Z_DECK_G), (x1 + 0.012, y0 + 1.4, 2.1),
            (x1 + 0.012, y0 + 0.4, 2.1)], 'vidro_porta')
    # rampa que desce 3,0 m para o subsolo: piso inclinado, muretas e o vao escuro no fim
    a, b, c, d = [P(p) for p in PL.RAMPA]
    zf = -3.0
    _quad_cima(g, [(a[0], a[1], Z_DECK_G + 0.01), (b[0], b[1], Z_DECK_G + 0.01), (c[0], c[1], zf), (d[0], d[1], zf)], 'rampa')
    for p0, p1 in ((a, d), (b, c)):
        _muro_seg(g, p0, p1, 1.10, 0.15, 'garagem_parede', pilar=50.0)
        # parede do talude ate o piso da rampa
        g.face([(p0[0], p0[1], Z_DECK_G), (p1[0], p1[1], zf), (p1[0], p1[1], Z_DECK_G)], 'garagem_parede')
        g.face([(p0[0], p0[1], Z_DECK_G), (p1[0], p1[1], Z_DECK_G), (p1[0], p1[1], zf)], 'garagem_parede')
    g.face([(d[0], d[1], zf), (c[0], c[1], zf), (c[0], c[1], Z_DECK_G), (d[0], d[1], Z_DECK_G)], 'vao_escuro')
    g.face([(c[0], c[1], zf), (d[0], d[1], zf), (d[0], d[1], Z_DECK_G), (c[0], c[1], Z_DECK_G)], 'vao_escuro')


# ------------------------------------------------------------------ avenida (publica)
def _faixa_av(g, x0_top, x1_top, z, m, y0=-500, y1=1600, cortes=()):
    """Faixa longitudinal da avenida (bordos inclinados), de y0 a y1 px, interrompida nos cortes (ya, yb)."""
    k = PL.AV_INCL
    trechos, ya = [], y0
    for c0, c1 in sorted(cortes):
        trechos.append((ya, c0)); ya = c1
    trechos.append((ya, y1))
    for a, b in trechos:
        if b - a < 1:
            continue
        pts = [(x0_top - k * a, a), (x1_top - k * a, a), (x1_top - k * b, b), (x0_top - k * b, b)]
        g.poligono([P(p) for p in pts], z, m)


def ruas(g):
    """Avenida Maria Emilia Alves dos Santos de Angelis: duas pistas com canteiro central, faixa de grama, calcada
    e o jardim publico ate a divisa; a alca de embarque em frente ao lote contorna uma ilha com palmeiras."""
    _faixa_av(g, *PL.AV_PISTA_L, Z_ASF, 'asfalto')
    _faixa_av(g, *PL.AV_PISTA_O, Z_ASF, 'asfalto')
    _faixa_av(g, *PL.AV_CANTEIRO, 0.10, 'grama')
    _faixa_av(g, PL.AV_GRAMA[0], PL.AV_GRAMA[1], 0.08, 'grama', cortes=[(545, 1045)])
    _faixa_av(g, PL.AV_CALCADA[0], PL.AV_CALCADA[1], Z_CALCADA, 'concreto', cortes=[(560, 1030)])
    # jardim publico entre a calcada e a divisa (fora do lote), sem a alca
    k = PL.AV_INCL
    for a, b in ((-500, 545), (1045, 1600)):
        pts = [(PL.AV_CALCADA[1] - k * a, a), (PL.FRENTE_X, a), (PL.FRENTE_X, b), (PL.AV_CALCADA[1] - k * b, b)]
        g.poligono([P(p) for p in pts], 0.01, 'grama')
    # alca: asfalto e a ilha com meio-fio e grama
    _poly(g, PL.ALCA, Z_ASF + 0.004, 'asfalto')
    _poly(g, PL.ILHA, 0.15, 'grama')
    il = [P(p) for p in PL.ILHA]
    for i in range(len(il)):
        p0, p1 = il[i], il[(i + 1) % len(il)]
        q = [(p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), (p1[0], p1[1], 0.15), (p0[0], p0[1], 0.15)]
        cx = sum(p[0] for p in il) / len(il); cy = sum(p[1] for p in il) / len(il)
        if _normal(q)[0] * ((p0[0] + p1[0]) / 2 - cx) + _normal(q)[1] * ((p0[1] + p1[1]) / 2 - cy) < 0:
            q = [q[1], q[0], q[3], q[2]]
        g.face(q, 'meio_fio')
    # faixa tracejada entre as faixas de rolamento e linhas de bordo
    xm = (PL.AV_PISTA_L[0] + PL.AV_PISTA_L[1]) / 2
    y = -500
    while y < 1600:
        p0, p1 = (xm - k * y, y), (xm - k * (y + 50), y + 50)
        A, Bp = P(p0), P(p1)
        g.face([(A[0] - 0.06, A[1], Z_LINHA), (A[0] + 0.06, A[1], Z_LINHA), (Bp[0] + 0.06, Bp[1], Z_LINHA),
                (Bp[0] - 0.06, Bp[1], Z_LINHA)][::-1], 'faixa')
        y += 110

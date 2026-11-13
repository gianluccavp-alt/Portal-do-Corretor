# avm_patio.py -- chao do condominio a partir de avm_planta.py: grama no lote, asfalto (uniao limpa de
# retangulos), vagas e zebras pintadas, calcadas com meio-fio, ruas em volta, muros, portoes, gardens das torres e
# o edificio garagem (terreo coberto + deck com vagas e rampa). Executado por avm_modelo.py dentro do Blender.
import math

Z_GRAMA, Z_ASF, Z_LINHA, Z_PASSEIO = 0.0, 0.02, 0.045, 0.14
E_GUIA = 0.12
LARG_RUA = 12.0           # pista das tres ruas (m)
LARG_CALCADA_OPOSTA = 3.0


def _ret(g, r, z, mat):
    x0, y0, x1, y1 = r
    g.piso(X(x0), X(x1), Y(y1), Y(y0), z, mat)


def uniao(rects):
    """Retangulos px (podem se sobrepor) -> retangulos px sem sobreposicao (grade de 1 px, corridas por linha)."""
    x0 = min(r[0] for r in rects); y0 = min(r[1] for r in rects)
    x1 = max(r[2] for r in rects); y1 = max(r[3] for r in rects)
    m = np.zeros((int(y1 - y0), int(x1 - x0)), bool)
    for r in rects:
        m[int(r[1] - y0):int(r[3] - y0), int(r[0] - x0):int(r[2] - x0)] = True
    out, abertos = [], {}
    for y in range(m.shape[0] + 1):
        corr = set()
        if y < m.shape[0] and m[y].any():
            d = np.diff(np.concatenate([[0], m[y].astype(np.int8), [0]]))
            corr = set(zip(np.nonzero(d == 1)[0].tolist(), np.nonzero(d == -1)[0].tolist()))
        for c in list(abertos):
            if c not in corr:
                out.append((x0 + c[0], y0 + abertos.pop(c), x0 + c[1], y0 + y))
        for c in corr:
            abertos.setdefault(c, y)
    return out


def _offset(pts, d):
    """Polilinha (m) deslocada d metros para a esquerda do sentido de percurso, com juntas em meia-esquadria."""
    out = []
    n = len(pts)
    for i in range(n):
        if i == 0:
            dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
            l = math.hypot(dx, dy); nx, ny = -dy / l, dx / l
            out.append((pts[0][0] + nx * d, pts[0][1] + ny * d)); continue
        if i == n - 1:
            dx, dy = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
            l = math.hypot(dx, dy); nx, ny = -dy / l, dx / l
            out.append((pts[i][0] + nx * d, pts[i][1] + ny * d)); continue
        ax, ay = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
        bx, by = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
        la, lb = math.hypot(ax, ay), math.hypot(bx, by)
        n1 = (-ay / la, ax / la); n2 = (-by / lb, bx / lb)
        mx, my = n1[0] + n2[0], n1[1] + n2[1]
        lm = math.hypot(mx, my)
        mx, my = mx / lm, my / lm
        k = d / max(0.3, (mx * n1[0] + my * n1[1]))
        out.append((pts[i][0] + mx * k, pts[i][1] + my * k))
    return out


def _faixa(g, a, b, z, mat, lados=None):
    """Faixa entre duas polilinhas paralelas (mesmo numero de pontos), em quads."""
    for i in range(len(a) - 1):
        q = [(a[i][0], a[i][1], z), (a[i + 1][0], a[i + 1][1], z), (b[i + 1][0], b[i + 1][1], z), (b[i][0], b[i][1], z)]
        if _normal(q)[2] < 0:
            q = q[::-1]
        g.face(q, mat)


def chao(g):
    # grama no lote inteiro (dentro do muro)
    g.poligono([(X(x), Y(y)) for x, y in PL.TERRENO], Z_GRAMA, 'grama')
    # asfalto: uniao limpa dos retangulos
    for r in uniao(PL.ASFALTO):
        if r[2] > 2900:                         # acesso de veiculos: rebaixo da calcada em asfalto
            _ret(g, (max(r[0], 2900), r[1], r[2], r[3]), Z_PASSEIO + 0.006, 'asfalto')
            r = (r[0], r[1], 2900, r[3])
        if r[2] > r[0]:
            _ret(g, r, Z_ASF, 'asfalto')
    # calcada entre o muro e o meio-fio (oeste, avenida e leste), com meio-fio
    mf = [(X(x), Y(y)) for x, y in PL.MEIO_FIO]
    # muro do noroeste ao nordeste passando pelo sul: (330,398), (330,1000), ..., (2900,1700), (2900,398)
    t = PL.TERRENO
    sul = [t[0]] + t[:0:-1]                     # (330,398), (330,1000), ..., (2900,1700), (2900,398)
    muro = [(X(330), Y(330))] + [(X(x), Y(y)) for x, y in sul] + [(X(2900), Y(330))]
    g.poligono(mf + muro[::-1], Z_PASSEIO, 'concreto')
    for i in range(len(mf) - 1):
        a, b = mf[i], mf[i + 1]
        q = [(a[0], a[1], 0.0), (b[0], b[1], 0.0), (b[0], b[1], Z_PASSEIO), (a[0], a[1], Z_PASSEIO)]
        g.face(q, 'meio_fio')
        g.face(q[::-1], 'meio_fio')
    # vagas: faixas divisorias pintadas (no chao e no deck)
    for x0, y0, x1, y1, ori, lw, nivel in PL.VAGAS:
        z = (PL.DECK_Z + 0.03) if nivel == 'deck' else Z_LINHA
        mx0, mx1, my0, my1 = X(x0), X(x1), Y(y1), Y(y0)
        if ori == 'h':
            n = int((mx1 - mx0) / lw + 0.25)
            for k in range(n + 1):
                xx = mx0 + k * lw
                g.piso(xx - 0.05, xx + 0.05, my0 + 0.15, my1 - 0.15, z, 'faixa')
        else:
            n = int((my1 - my0) / lw + 0.25)
            for k in range(n + 1):
                yy = my1 - k * lw
                g.piso(mx0 + 0.15, mx1 - 0.15, yy - 0.05, yy + 0.05, z, 'faixa')
    for x0, y0, x1, y1, ori in PL.ZEBRAS:
        mx0, mx1, my0, my1 = X(x0), X(x1), Y(y1), Y(y0)
        if ori == 'v':       # listras ao longo de y (atravessa a rua que corre em x)
            xx = mx0
            while xx + 0.4 <= mx1:
                g.piso(xx, xx + 0.4, my0, my1, Z_LINHA, 'faixa'); xx += 0.8
        else:
            yy = my0
            while yy + 0.4 <= my1:
                g.piso(mx0, mx1, yy, yy + 0.4, Z_LINHA, 'faixa'); yy += 0.8


def ruas(g):
    """Pista em volta do lote (Rua Joao Francisco Lisboa, Av. Graca Aranha e Rua 2), calcada do outro lado e o
    prolongamento das ruas para fora da imagem."""
    mf = [(X(x), Y(y)) for x, y in PL.MEIO_FIO]
    mf = [(mf[0][0], mf[0][1] + 160.0)] + mf + [(mf[-1][0], mf[-1][1] + 160.0)]
    # o sentido de percurso (norte -> sul -> leste -> norte) deixa o lote a esquerda: a rua fica a direita (-d)
    fora = _offset(mf, -LARG_RUA)
    cal = _offset(mf, -LARG_RUA - LARG_CALCADA_OPOSTA)
    _faixa(g, mf, fora, Z_ASF, 'asfalto')
    _faixa(g, fora, cal, Z_PASSEIO, 'concreto')
    # eixo amarelo tracejado
    eixo = _offset(mf, -LARG_RUA / 2)
    for i in range(len(eixo) - 1):
        a, b = eixo[i], eixo[i + 1]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        with g.em(a[0], a[1], 0, ang):
            s = 0.0
            while s + 3.0 < L:
                g.piso(s, s + 3.0, -0.07, 0.07, Z_LINHA, 'faixa_amarela'); s += 7.0
    # Av. Graca Aranha continua a oeste (passa pela esquina da Joao Francisco Lisboa) e a leste da Rua 2
    d = (1.0, 0.324); l = math.hypot(*d); d = (d[0] / l, -d[1] / l)        # direcao da avenida em metros (x, y)
    nrm = (d[1], -d[0])                                                    # para fora do lote (sul)
    for p0, sent in (((X(500), Y(1283)), -1), ((X(2780), Y(2022)), 1)):
        for (o0, o1, z, m, t0) in ((0, LARG_RUA, Z_ASF - 0.006, 'asfalto', 6), (-3.0, 0, Z_PASSEIO, 'concreto', 32),
                                   (LARG_RUA, LARG_RUA + 3.0, Z_PASSEIO, 'concreto', 32)):
            a = (p0[0] + d[0] * t0 * sent, p0[1] + d[1] * t0 * sent)
            b = (p0[0] + d[0] * 900 * sent, p0[1] + d[1] * 900 * sent)
            q = [(a[0] + nrm[0] * o0, a[1] + nrm[1] * o0, z), (b[0] + nrm[0] * o0, b[1] + nrm[1] * o0, z),
                 (b[0] + nrm[0] * o1, b[1] + nrm[1] * o1, z), (a[0] + nrm[0] * o1, a[1] + nrm[1] * o1, z)]
            if _normal(q)[2] < 0:
                q = q[::-1]
            g.face(q, m)


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


def _gradil_seg(g, a, b, h=2.2):
    """Portao de gradil escuro com pilares."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ang = math.degrees(math.atan2(dy, dx))
    with g.em(a[0], a[1], 0, ang):
        g.painel(0, 0.0, L, 0.0, 0.05, h, 'gradil_preto', (0, 0, L / 2.4, 1))
        g.painel(L, 0.0, 0, 0.0, 0.05, h, 'gradil_preto', (0, 0, L / 2.4, 1))
        for k in (0.0, L):
            g.caixa(k - 0.15, k + 0.15, -0.15, 0.15, 0, h + 0.1, 'muro_liso', topo='pingadeira')


def muros_perimetro(g):
    """Muro liso em toda a divisa (FAQ: muros e/ou gradis); no leste fica aberto na entrada, portaria e saida."""
    p = [(X(x), Y(y)) for x, y in PL.TERRENO]
    ya, yb = PL.MURO_ABERTO_Y
    n = len(p)
    for i in range(n):
        a, b = PL.TERRENO[i], PL.TERRENO[(i + 1) % n]
        if a[0] == b[0] == 2900 and a[1] < ya < b[1]:     # lado leste: corta a abertura
            _muro_seg(g, p[i], (X(2900), Y(ya)), 2.6, 0.18)
            _muro_seg(g, (X(2900), Y(yb)), p[(i + 1) % n], 2.6, 0.18)
            continue
        _muro_seg(g, p[i], p[(i + 1) % n], 2.6, 0.18)
    for a, b in (PL.PORTAO_ENTRADA, PL.PORTAO_SAIDA):
        _gradil_seg(g, (X(a[0]), Y(a[1])), (X(b[0]), Y(b[1])))
    # muretas das vagas de acumulacao (curva da entrada) e canteiro da portaria
    g.caixa(X(2860), X(2905), Y(1545), Y(1535), 0, 1.0, 'muro_liso', topo='pingadeira')


def jardins_torres(g):
    """Gardens do terreo (muretas de 1,1 m a 1,50 m da fachada, com as divisorias entre as unidades) e sebes."""
    h, e = 1.1, 0.14
    yg = Y_FACE + 1.55

    def mur(x0, x1, y0, y1):
        g.caixa(x0, x1, y0, y1, 0.0, h, 'muro_bloco', topo='pingadeira')

    for cxp, cyp in PL.TORRES.values():
        with g.em(X(cxp), Y(cyp), 0.0, 0.0):
            # face +y: gardens dos finais 6, 5, 4 e 3 (contornando a saliencia do dormitorio do meio)
            for s in (1, -1):
                mur(s * X_B1 if s > 0 else -L2, L2 if s > 0 else -X_B1, yg, yg + e)
                mur(s * X_C if s > 0 else -X_B1, X_B1 if s > 0 else -X_C, Y_BUMP + 0.9, Y_BUMP + 0.9 + e)
                mur(s * X_C - e / 2, s * X_C + e / 2, Y_FACE, Y_BUMP + 0.9 + e)
                mur(s * X_B1 - e / 2, s * X_B1 + e / 2, yg, Y_BUMP + 0.9 + e)
                mur(-e / 2 + s * 9.5, e / 2 + s * 9.5, Y_FACE, yg + e)                     # divisa meio | ponta
                mur(s * L2 - e / 2, s * L2 + e / 2, Y_NOTCH, yg + e)                       # testa
                # face -y: so os finais de ponta (7 e 2) tem garden; no meio ficam o hall e o lazer
                mur(s * 9.5 if s > 0 else -L2, L2 if s > 0 else -9.5, -yg - e, -yg)
                mur(s * 9.5 - e / 2, s * 9.5 + e / 2, -yg - e, -Y_FACE)
                mur(s * L2 - e / 2, s * L2 + e / 2, -yg - e, -Y_NOTCH)
            mur(-e / 2, e / 2, Y_FACE, Y_BUMP + 0.9 + e)
            mur(-X_C, X_C, Y_BUMP + 0.9, Y_BUMP + 0.9 + e)
    for r in PL.SEBES:
        x0, y0, x1, y1 = r
        g.caixa(X(x0), X(x1), Y(y1), Y(y0), 0.0, 0.85, 'sebe')


# ------------------------------------------------------------------ edificio garagem
def garagem(g):
    """Faixa norte: terreo coberto (pilares, sem fechamento na frente) e o deck do 1o pavimento com vagas,
    mureta e o nucleo de escada; rampa do deck saindo da rua entre as torres."""
    x0, y0, x1, y1 = PL.DECK
    mx0, mx1, my0, my1 = X(x0), X(x1), Y(y1), Y(y0)
    z = PL.DECK_Z
    # laje do deck (rampa abre um vao na borda sul)
    rx0, ry0, rx1, ry1 = PL.RAMPA_DECK
    g.caixa(mx0, mx1, my0, my1, z - 0.35, z, 'garagem_parede', topo='asfalto_deck', fundo='garagem_teto', sem_fundo=False)
    # mureta do deck (fechada no norte e nas pontas, guarda-corpo baixo no sul; aberta na chegada da rampa)
    hm = 1.1
    g.caixa(mx0, mx1, my1 - 0.15, my1, z, z + hm, 'garagem_parede', topo='pingadeira')
    g.caixa(mx0, mx0 + 0.15, my0, my1, z, z + hm, 'garagem_parede', topo='pingadeira')
    g.caixa(mx1 - 0.15, mx1, my0 + 7.0, my1, z, z + hm, 'garagem_parede', topo='pingadeira')
    g.caixa(mx0, X(rx0), my0, my0 + 0.15, z, z + hm, 'garagem_parede', topo='pingadeira')
    g.caixa(X(rx1), mx1, my0, my0 + 0.15, z, z + hm, 'garagem_parede', topo='pingadeira')
    # pilares do terreo (malha de ~7,5 m) e a parede de fundo junto ao jardim norte
    g.caixa(mx0, mx1, my1 - 0.2, my1, 0, z - 0.35, 'garagem_parede')
    nx = int((mx1 - mx0) / 7.6)
    for i in range(nx + 1):
        xx = mx0 + 0.3 + (mx1 - mx0 - 0.6) * i / nx
        for yy in (my0 + 0.35, (my0 + my1) / 2):
            g.caixa(xx - 0.25, xx + 0.25, yy - 0.25, yy + 0.25, 0, z - 0.35, 'garagem_parede')
    # nucleo de escada (sobe ate o deck e passa um pavimento)
    ex0, ey0, ex1, ey1 = PL.ESCADA_DECK
    g.caixa(X(ex0), X(ex1), Y(ey1), Y(ey0), 0, z + 2.7, 'garagem_parede', topo='telha')
    g.caixa(X(ex0) - 0.3, X(ex1) + 0.3, Y(ey1) - 0.3, Y(ey0) + 0.3, z + 2.7, z + 2.85, 'laje_borda', topo='telha')
    g.caixa(X(ex0) + 1.4, X(ex0) + 2.4, Y(ey1) - 0.02, Y(ey1), z + 0.05, z + 2.15, 'porta_servico')
    # rampa: sobe do chao (y = ry1) ate o deck (y = ry0), com muretas laterais
    a, b = X(rx0), X(rx1)
    ya, yb = Y(ry1), Y(ry0)
    q = [(a, ya, Z_ASF), (b, ya, Z_ASF), (b, yb, z), (a, yb, z)]
    g.face(q, 'asfalto_deck')
    g.face([(a, ya, Z_ASF), (a, yb, z), (a, yb, 0), (a, ya, 0)][::-1], 'garagem_parede')
    for xx in (a, b - 0.15):
        g.face([(xx, ya, 0.0), (xx, yb, z - 0.35), (xx, yb, z + hm), (xx, ya, 0.9)], 'garagem_parede')
        g.face([(xx + 0.15, ya, 0.9), (xx + 0.15, yb, z + hm), (xx + 0.15, yb, z - 0.35), (xx + 0.15, ya, 0.0)], 'garagem_parede')
        g.face([(xx, ya, 0.9), (xx, yb, z + hm), (xx + 0.15, yb, z + hm), (xx + 0.15, ya, 0.9)], 'pingadeira')
    # seta e "07" pintados na pista do deck: faixa amarela no meio da pista
    yc = Y(596)
    xx = mx0 + 4
    while xx < mx1 - 4:
        g.piso(xx, xx + 3.0, yc - 0.06, yc + 0.06, z + 0.03, 'faixa_amarela'); xx += 7.0
